#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Sync PostgreSQL data → GraphDB (Apache Jena Fuseki)
Chuyển đổi relational data thành RDF triples
Chạy: python scripts/sync_to_graphdb.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.postgres import SessionLocal
from app.models.report import Report, ReportCategory
from app.models.user import User
from app.models.geographic import AdministrativeBoundary, Street
from app.models.facility import PublicFacility
import requests
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from datetime import datetime

# Fuseki endpoint
FUSEKI_URL = os.getenv("FUSEKI_URL", "http://localhost:3030")
DATASET = "citylens"

# Namespaces
CITYLENS = Namespace("http://citylens.io/ontology#")
RESOURCE = Namespace("http://citylens.io/resource/")


def create_rdf_graph():
    """Create RDF graph với namespaces"""
    g = Graph()
    g.bind("citylens", CITYLENS)
    g.bind("resource", RESOURCE)
    g.bind("xsd", XSD)
    return g


def sync_reports():
    """Sync reports từ PostgreSQL → RDF triples"""
    db: Session = SessionLocal()
    g = create_rdf_graph()
    
    reports = db.query(Report).limit(100).all()  # Limit for demo
    
    for report in reports:
        # Create report URI
        report_uri = RESOURCE[f"report/{report.id}"]
        
        # Type
        g.add((report_uri, RDF.type, CITYLENS.Report))
        
        # Basic properties
        g.add((report_uri, CITYLENS.reportTitle, Literal(report.title)))
        g.add((report_uri, CITYLENS.reportDescription, Literal(report.description or "")))
        g.add((report_uri, CITYLENS.reportStatus, Literal(report.status.value)))
        g.add((report_uri, CITYLENS.reportPriority, Literal(report.priority.value)))
        g.add((report_uri, CITYLENS.upvoteCount, Literal(report.upvotes, datatype=XSD.integer)))
        g.add((report_uri, CITYLENS.createdAt, Literal(report.created_at, datatype=XSD.dateTime)))
        
        # Location (extract lat/lon from PostGIS)
        if report.location:
            # Simplified - in production use PostGIS ST_AsText
            # Example: POINT(105.8542 21.0285)
            coords = str(report.location).replace("SRID=4326;POINT(", "").replace(")", "")
            try:
                lon, lat = coords.split()
                g.add((report_uri, CITYLENS.latitude, Literal(float(lat), datatype=XSD.float)))
                g.add((report_uri, CITYLENS.longitude, Literal(float(lon), datatype=XSD.float)))
            except:
                pass
        
        # Relations
        if report.user_id:
            user_uri = RESOURCE[f"citizen/{report.user_id}"]
            g.add((report_uri, CITYLENS.reportedBy, user_uri))
        
        if report.district_id:
            district_uri = RESOURCE[f"district/{report.district_id}"]
            g.add((report_uri, CITYLENS.locatedIn, district_uri))
        
        if report.related_facility_id:
            facility_uri = RESOURCE[f"facility/{report.related_facility_id}"]
            g.add((report_uri, CITYLENS.relatedToFacility, facility_uri))
        
        if report.related_street_id:
            street_uri = RESOURCE[f"street/{report.related_street_id}"]
            g.add((report_uri, CITYLENS.relatedToStreet, street_uri))
    
    print(f"✓ Synced {len(reports)} reports → {len(g)} triples")
    db.close()
    
    return g


def sync_districts():
    """Sync administrative boundaries → RDF"""
    db: Session = SessionLocal()
    g = create_rdf_graph()
    
    districts = db.query(AdministrativeBoundary).filter(
        AdministrativeBoundary.admin_level == 6  # Districts only
    ).all()
    
    for district in districts:
        district_uri = RESOURCE[f"district/{district.id}"]
        
        g.add((district_uri, RDF.type, CITYLENS.AdministrativeBoundary))
        g.add((district_uri, RDFS.label, Literal(district.name)))
        g.add((district_uri, CITYLENS.adminLevel, Literal(6, datatype=XSD.integer)))
        
        if district.population:
            g.add((district_uri, CITYLENS.population, Literal(district.population, datatype=XSD.integer)))
    
    print(f"✓ Synced {len(districts)} districts → {len(g)} triples")
    db.close()
    
    return g


def upload_to_fuseki(graph: Graph):
    """Upload RDF graph to Fuseki"""
    try:
        # Serialize to Turtle format
        ttl_data = graph.serialize(format='turtle')
        
        # POST to Fuseki
        url = f"{FUSEKI_URL}/{DATASET}/data"
        headers = {"Content-Type": "text/turtle"}
        
        response = requests.post(url, data=ttl_data, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"Uploaded {len(graph)} triples to Fuseki")
        return True
    except requests.exceptions.ConnectionError:
        print("Cannot connect to Fuseki. Is it running?")
        print(f"   Start Fuseki: docker run -p 3030:3030 stain/jena-fuseki")
        return False
    except Exception as e:
        print(f"Error uploading to Fuseki: {e}")
        return False


if __name__ == "__main__":
    print("Syncing PostgreSQL → GraphDB...\n")
    
    print("1. Syncing districts...")
    g_districts = sync_districts()
    
    print("\n2. Syncing reports...")
    g_reports = sync_reports()
    
    # Combine graphs
    combined = create_rdf_graph()
    combined += g_districts
    combined += g_reports
    
    print(f"\nTotal: {len(combined)} RDF triples")
    
    print("\n3. Uploading to Fuseki...")
    success = upload_to_fuseki(combined)
    
    if success:
        print("\nSync completed!")
        print(f"   Query endpoint: {FUSEKI_URL}/{DATASET}/sparql")
        print("\n   Example SPARQL query:")
        print("   SELECT * WHERE { ?s a citylens:Report } LIMIT 10")
    else:
        print("\nFuseki upload failed. RDF graph generated but not uploaded.")
        print("   You can save it manually:")
        print("   with open('citylens.ttl', 'w') as f:")
        print("       f.write(combined.serialize(format='turtle'))")
