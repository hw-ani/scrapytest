from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class SubjectDef(BaseModel):
    surface_text: str
    type: str

class RelationshipDef(BaseModel):
    type: Literal[
        "groups_projects_programs",
        "waiting_response_events",
        "events_participation"
    ]
    role: str

class ObjectDef(BaseModel):
    surface_text: str
    type: str

class Fact(BaseModel):
    fact_id: str
    subject: SubjectDef
    relationship: RelationshipDef
    object: ObjectDef
    assertion: Literal["asserted", "reported", "speculative"]
    evidence: str
    additional_info: Optional[Dict[str, Any]] = None

class ExtractionResponse(BaseModel):
    source_doc_id: str = "PLACEHOLDER"
    source_url: str = ""
    facts: List[Fact] = Field(default_factory=list)