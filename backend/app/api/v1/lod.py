# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
LOD Community API Router
Provides endpoints for managing Linked Open Data contributions
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import os
import json

router = APIRouter(prefix="/lod", tags=["LOD Community"])


# =============================================================================
# ENUMS & MODELS
# =============================================================================

class DatasetStatus(str, Enum):
    PENDING = "pending"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"


class DatasetFormat(str, Enum):
    TURTLE = "turtle"
    JSON_LD = "json-ld"
    RDF_XML = "rdf-xml"
    N_TRIPLES = "n-triples"


class License(str, Enum):
    CC_BY_4 = "CC-BY 4.0"
    CC_BY_SA_4 = "CC-BY-SA 4.0"
    CC0_1 = "CC0 1.0"
    ODBL = "ODbL"
    MIT = "MIT"


class ContributorBadge(str, Enum):
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    CONTRIBUTOR = "contributor"


# =============================================================================
# SCHEMAS
# =============================================================================

class DatasetMetadata(BaseModel):
    id: str
    name: str
    description: str
    namespace: str
    triples: int = 0
    contributor_id: str
    contributor_name: str
    license: License
    status: DatasetStatus = DatasetStatus.PENDING
    downloads: int = 0
    stars: int = 0
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    formats: List[DatasetFormat] = [DatasetFormat.TURTLE]
    linked_datasets: List[str] = []
    sparql_endpoint: Optional[str] = None
    void_description: Optional[str] = None


class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    namespace: str = Field(..., pattern=r'^https?://')
    license: License
    tags: List[str] = []
    linked_datasets: List[str] = []


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    linked_datasets: Optional[List[str]] = None


class Contributor(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    organization: Optional[str] = None
    avatar_url: Optional[str] = None
    datasets_count: int = 0
    total_triples: int = 0
    total_stars: int = 0
    badge: ContributorBadge = ContributorBadge.CONTRIBUTOR
    joined_at: datetime


class CommunityStats(BaseModel):
    total_datasets: int
    total_triples: int
    total_contributors: int
    total_downloads: int
    pending_reviews: int
    approved_datasets: int
    this_month_contributions: int
    top_tags: List[dict]


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    triple_count: int = 0
    entity_types: List[dict] = []
    namespaces: List[str] = []
    has_external_links: bool = False
    five_star_score: int = 0


class DownloadOptions(BaseModel):
    format: DatasetFormat = DatasetFormat.TURTLE
    include_metadata: bool = True
    include_void: bool = False


# =============================================================================
# IN-MEMORY STORAGE (Replace with database in production)
# =============================================================================

datasets_db: dict[str, DatasetMetadata] = {}
contributors_db: dict[str, Contributor] = {}

# Initialize with sample data
def init_sample_data():
    # Sample contributors
    contributors_db["citylens-team"] = Contributor(
        id="citylens-team",
        name="CityLens Team",
        organization="PKA OpenDynamics",
        datasets_count=4,
        total_triples=450,
        total_stars=150,
        badge=ContributorBadge.GOLD,
        joined_at=datetime(2025, 1, 1)
    )
    
    # Sample datasets
    datasets_db["citylens-weather"] = DatasetMetadata(
        id="citylens-weather",
        name="Hanoi Weather Observations",
        description="Real-time weather data for Hanoi districts using SOSA/SSN ontology",
        namespace="https://citylens.vn/data/weather/",
        triples=63,
        contributor_id="citylens-team",
        contributor_name="CityLens Team",
        license=License.CC_BY_4,
        status=DatasetStatus.APPROVED,
        downloads=1250,
        stars=45,
        created_at=datetime(2025, 1, 15),
        updated_at=datetime(2025, 12, 10),
        tags=["weather", "hanoi", "sosa", "iot"],
        formats=[DatasetFormat.TURTLE, DatasetFormat.JSON_LD],
        linked_datasets=["citylens-places", "citylens-airquality"],
        sparql_endpoint="http://localhost:7200/citylens-weather/sparql"
    )

init_sample_data()


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/datasets", response_model=List[DatasetMetadata])
async def list_datasets(
    status: Optional[DatasetStatus] = None,
    tag: Optional[str] = None,
    format: Optional[DatasetFormat] = None,
    contributor_id: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("updated_at", enum=["updated_at", "stars", "downloads", "triples"]),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List all datasets with filtering and pagination.
    """
    datasets = list(datasets_db.values())
    
    # Filter
    if status:
        datasets = [d for d in datasets if d.status == status]
    if tag:
        datasets = [d for d in datasets if tag.lower() in [t.lower() for t in d.tags]]
    if format:
        datasets = [d for d in datasets if format in d.formats]
    if contributor_id:
        datasets = [d for d in datasets if d.contributor_id == contributor_id]
    if search:
        search_lower = search.lower()
        datasets = [d for d in datasets if 
            search_lower in d.name.lower() or 
            search_lower in d.description.lower() or
            any(search_lower in t.lower() for t in d.tags)]
    
    # Sort
    sort_key = lambda x: getattr(x, sort_by)
    datasets.sort(key=sort_key, reverse=True)
    
    # Paginate
    return datasets[offset:offset + limit]


@router.get("/datasets/{dataset_id}", response_model=DatasetMetadata)
async def get_dataset(dataset_id: str):
    """
    Get detailed information about a specific dataset.
    """
    if dataset_id not in datasets_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return datasets_db[dataset_id]


@router.post("/datasets", response_model=DatasetMetadata)
async def create_dataset(
    dataset: DatasetCreate,
    contributor_id: str = "anonymous"
):
    """
    Submit a new dataset for review.
    """
    import uuid
    
    dataset_id = str(uuid.uuid4())[:8]
    
    # Get contributor info
    contributor_name = contributors_db.get(contributor_id, Contributor(
        id=contributor_id,
        name="Anonymous",
        joined_at=datetime.now()
    )).name
    
    new_dataset = DatasetMetadata(
        id=dataset_id,
        name=dataset.name,
        description=dataset.description,
        namespace=dataset.namespace,
        license=dataset.license,
        tags=dataset.tags,
        linked_datasets=dataset.linked_datasets,
        contributor_id=contributor_id,
        contributor_name=contributor_name,
        status=DatasetStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    datasets_db[dataset_id] = new_dataset
    return new_dataset


@router.post("/datasets/{dataset_id}/upload")
async def upload_dataset_file(
    dataset_id: str,
    file: UploadFile = File(...),
    format: DatasetFormat = Form(DatasetFormat.TURTLE)
):
    """
    Upload RDF data file for a dataset.
    """
    if dataset_id not in datasets_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Validate file extension
    valid_extensions = {
        DatasetFormat.TURTLE: [".ttl", ".turtle"],
        DatasetFormat.JSON_LD: [".jsonld", ".json"],
        DatasetFormat.RDF_XML: [".rdf", ".xml"],
        DatasetFormat.N_TRIPLES: [".nt", ".ntriples"]
    }
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in valid_extensions.get(format, []):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file extension for format {format}"
        )
    
    # Read and validate content
    content = await file.read()
    
    # TODO: Implement actual RDF validation
    # For now, just store the file
    
    upload_dir = f"uploads/lod/{dataset_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/data{file_ext}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update dataset metadata
    datasets_db[dataset_id].updated_at = datetime.now()
    if format not in datasets_db[dataset_id].formats:
        datasets_db[dataset_id].formats.append(format)
    
    return {
        "message": "File uploaded successfully",
        "file_path": file_path,
        "size_bytes": len(content)
    }


@router.post("/datasets/{dataset_id}/validate", response_model=ValidationResult)
async def validate_dataset(dataset_id: str):
    """
    Validate a dataset's RDF content and structure.
    """
    if dataset_id not in datasets_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # TODO: Implement actual RDF validation using rdflib
    # This is a mock response
    
    return ValidationResult(
        is_valid=True,
        errors=[],
        warnings=["Consider adding owl:sameAs links to external datasets"],
        triple_count=63,
        entity_types=[
            {"type": "sosa:Observation", "count": 8},
            {"type": "fiware:WeatherObserved", "count": 5}
        ],
        namespaces=[
            "https://citylens.vn/data/",
            "http://www.w3.org/ns/sosa/",
            "https://uri.fiware.org/ns/data-models#"
        ],
        has_external_links=True,
        five_star_score=4
    )


@router.get("/datasets/{dataset_id}/download")
async def download_dataset(
    dataset_id: str,
    format: DatasetFormat = Query(DatasetFormat.TURTLE),
    include_metadata: bool = Query(True)
):
    """
    Download dataset in specified format.
    """
    if dataset_id not in datasets_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = datasets_db[dataset_id]
    
    # Increment download count
    dataset.downloads += 1
    
    # TODO: Implement actual file conversion and serving
    # For now, return mock response
    
    return {
        "dataset_id": dataset_id,
        "format": format,
        "download_url": f"/api/v1/lod/files/{dataset_id}.{format.value}",
        "expires_at": datetime.now().isoformat()
    }


@router.post("/datasets/{dataset_id}/star")
async def star_dataset(dataset_id: str, user_id: str = "anonymous"):
    """
    Star/favorite a dataset.
    """
    if dataset_id not in datasets_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    datasets_db[dataset_id].stars += 1
    return {"stars": datasets_db[dataset_id].stars}


# =============================================================================
# CONTRIBUTORS
# =============================================================================

@router.get("/contributors", response_model=List[Contributor])
async def list_contributors(
    badge: Optional[ContributorBadge] = None,
    sort_by: str = Query("total_stars", enum=["total_stars", "datasets_count", "joined_at"]),
    limit: int = Query(20, ge=1, le=100)
):
    """
    List all contributors with their statistics.
    """
    contributors = list(contributors_db.values())
    
    if badge:
        contributors = [c for c in contributors if c.badge == badge]
    
    sort_key = lambda x: getattr(x, sort_by)
    contributors.sort(key=sort_key, reverse=True)
    
    return contributors[:limit]


@router.get("/contributors/{contributor_id}", response_model=Contributor)
async def get_contributor(contributor_id: str):
    """
    Get contributor profile and statistics.
    """
    if contributor_id not in contributors_db:
        raise HTTPException(status_code=404, detail="Contributor not found")
    return contributors_db[contributor_id]


@router.get("/contributors/{contributor_id}/datasets", response_model=List[DatasetMetadata])
async def get_contributor_datasets(contributor_id: str):
    """
    Get all datasets by a specific contributor.
    """
    return [d for d in datasets_db.values() if d.contributor_id == contributor_id]


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats", response_model=CommunityStats)
async def get_community_stats():
    """
    Get overall community statistics.
    """
    datasets = list(datasets_db.values())
    
    # Count tags
    tag_counts: dict[str, int] = {}
    for d in datasets:
        for tag in d.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    top_tags = sorted(
        [{"tag": k, "count": v} for k, v in tag_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:10]
    
    return CommunityStats(
        total_datasets=len(datasets),
        total_triples=sum(d.triples for d in datasets),
        total_contributors=len(contributors_db),
        total_downloads=sum(d.downloads for d in datasets),
        pending_reviews=sum(1 for d in datasets if d.status == DatasetStatus.PENDING),
        approved_datasets=sum(1 for d in datasets if d.status == DatasetStatus.APPROVED),
        this_month_contributions=sum(
            1 for d in datasets 
            if d.created_at.month == datetime.now().month
        ),
        top_tags=top_tags
    )


# =============================================================================
# ADMIN ENDPOINTS (Protected)
# =============================================================================

@router.patch("/admin/datasets/{dataset_id}/status")
async def update_dataset_status(
    dataset_id: str,
    status: DatasetStatus,
    review_notes: Optional[str] = None
):
    """
    Update dataset status (admin only).
    """
    if dataset_id not in datasets_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    datasets_db[dataset_id].status = status
    datasets_db[dataset_id].updated_at = datetime.now()
    
    return {
        "message": f"Dataset status updated to {status}",
        "dataset_id": dataset_id
    }


@router.delete("/admin/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """
    Delete a dataset (admin only).
    """
    if dataset_id not in datasets_db:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    del datasets_db[dataset_id]
    return {"message": "Dataset deleted successfully"}
