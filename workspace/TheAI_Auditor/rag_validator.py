from pydantic import BaseModel, Field, AfterValidator, field_validator
from typing import List, Optional, Dict, Any, Annotated
from datetime import datetime, timezone
import re

def check_for_injection_patterns(v: str) -> str:
    """2026 standard check for indirect prompt injection patterns."""
    forbidden_patterns = [r"ignore previous instructions", r"system override", r"bypass security"]
    for pattern in forbidden_patterns:
        if re.search(pattern, v, re.IGNORECASE):
            raise ValueError(f"Adversarial pattern detected: {pattern}")
    return v

# Using Annotated for Pydantic v3 compliance
SecureContent = Annotated[str, AfterValidator(check_for_injection_patterns)]

class RetrievalChunk(BaseModel):
    chunk_id: str
    content: SecureContent
    source_metadata: Dict[str, Any]
    relevance_score: float = Field(..., ge=0.7) # Reject low-relevance noise per Forensic Spec

class ForensicHeader(BaseModel):
    red_team_baseline_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    audit_trail_id: Optional[str] = None

class ValidatedRAGInput(BaseModel):
    query: str
    context: List[RetrievalChunk]
    forensic_header: ForensicHeader

# Integration Examples for 2026 Vector DBs
def map_pinecone_v3(match: Any) -> RetrievalChunk:
    """Maps Pinecone v3+ ScoredVector to RetrievalChunk."""
    return RetrievalChunk(
        chunk_id=match.id,
        content=match.metadata.get("text", ""),
        source_metadata=match.metadata,
        relevance_score=match.score
    )

def map_weaviate_v4(obj: Any) -> RetrievalChunk:
    """Maps Weaviate v4 Collection object to RetrievalChunk."""
    return RetrievalChunk(
        chunk_id=str(obj.uuid),
        content=obj.properties.get("content", ""),
        source_metadata=obj.properties,
        relevance_score=obj.metadata.score if obj.metadata else 0.0
    )

def map_milvus_3_0(res: Dict[str, Any]) -> RetrievalChunk:
    """Maps Milvus 3.0 SearchResult to RetrievalChunk."""
    return RetrievalChunk(
        chunk_id=str(res.get("id")),
        content=res.get("entity", {}).get("text", ""),
        source_metadata=res.get("entity", {}),
        relevance_score=res.get("distance", 0.0)
    )