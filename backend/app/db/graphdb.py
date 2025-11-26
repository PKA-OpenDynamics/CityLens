# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Kết nối GraphDB và SPARQL queries
"""

from typing import List, Dict, Any
from SPARQLWrapper import SPARQLWrapper, JSON
from app.core.config import settings


class GraphDBClient:
    """Client để tương tác với GraphDB"""
    
    def __init__(self):
        self.endpoint = f"{settings.GRAPHDB_URL}/repositories/{settings.GRAPHDB_REPOSITORY}"
        self.sparql = SPARQLWrapper(self.endpoint)
        self.sparql.setReturnFormat(JSON)
    
    def query(self, query_string: str) -> List[Dict[str, Any]]:
        """Thực hiện SPARQL query"""
        self.sparql.setQuery(query_string)
        try:
            results = self.sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            print(f"GraphDB query error: {e}")
            return []
    
    def insert(self, triples: str) -> bool:
        """Chèn RDF triples vào GraphDB"""
        query = f"""
        INSERT DATA {{
            {triples}
        }}
        """
        try:
            self.sparql.setQuery(query)
            self.sparql.method = "POST"
            self.sparql.query()
            return True
        except Exception as e:
            print(f"GraphDB insert error: {e}")
            return False


graphdb_client = GraphDBClient()
