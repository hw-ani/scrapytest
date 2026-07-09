# models.py

'''
FIRST DRAFT
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Mention(BaseModel):
    mention_id: str = Field(description="Unique identifier for this mention")
    type: Literal[
        "Person",
        "ResearchGroup",
        "Project",
        "Program",
        "Event",
        "Organization",
    ]
    surface_text: str = Field(description="Exact text found on the webpage")


class Relationship(BaseModel):
    person_mention: str = Field(description="mention_id of the person")
    context_mention: str = Field(description="mention_id of the related entity")

    relationship_type: Literal[
        "GROUP_MEMBERSHIP",
        "PROJECT_MEMBERSHIP",
        "PROGRAM_MEMBERSHIP",
        "WAITING_EVENT",
        "EVENT_PARTICIPATION",
    ]

    role: Optional[str] = None

    extracted_evidence: str = Field(
        description="Exact sentence supporting this relationship"
    )


class ResponseModel(BaseModel):
    document_id: str

    source_url: str

    mentions: List[Mention]

    participations: List[Relationship]
'''

'''
SECOND DRAFT
from typing import List, Optional
from pydantic import BaseModel, Field


########################################################################
# Base Relationship
########################################################################

class Relationship(BaseModel):
    """
    Generic relationship between a person and an entity.
    """

    name: str = Field(
        description="Name of the entity."
    )

    type: str = Field(
        description="Research Group, Laboratory, Project, Program, Conference, Workshop, etc."
    )

    role: Optional[str] = Field(
        default=None,
        description="Role of the person in this relationship."
    )

    evidence: str = Field(
        description="Exact sentence or paragraph supporting this extraction."
    )

    source_url: Optional[str] = Field(
        default=None,
        description="URL where the relationship was found."
    )

    confidence: Optional[float] = Field(
        default=None,
        description="Confidence between 0 and 1."
    )


########################################################################
# Waiting Event
########################################################################

class WaitingEvent(BaseModel):

    name: str = Field(
        description="Name of the event."
    )

    status: Optional[str] = Field(
        default=None,
        description="Open, Recruiting, Upcoming, Waiting, etc."
    )

    evidence: str

    source_url: Optional[str] = None

    confidence: Optional[float] = None


########################################################################
# Event Participation
########################################################################

class EventParticipation(BaseModel):

    event: str = Field(
        description="Conference, Workshop, Competition, Publication, etc."
    )

    role: Optional[str] = Field(
        default=None,
        description="Presenter, Organizer, Participant..."
    )

    evidence: str

    source_url: Optional[str] = None

    confidence: Optional[float] = None


########################################################################
# Relationships for ONE person
########################################################################

class PersonRelationships(BaseModel):

    groups_projects_programs: List[Relationship] = Field(
        default_factory=list,
        description=(
            "Groups, laboratories, projects, scholarships, "
            "research topics, companies, collaborations."
        )
    )

    waiting_events: List[WaitingEvent] = Field(
        default_factory=list
    )

    event_participation: List[EventParticipation] = Field(
        default_factory=list
    )


########################################################################
# Person
########################################################################

class Person(BaseModel):

    person: str = Field(
        description="Full name of the person."
    )

    relationships: PersonRelationships


########################################################################
# Response returned by the LLM
########################################################################

class ResponseModel(BaseModel):

    people: List[Person] = Field(
        default_factory=list,
        description="All people explicitly mentioned on this webpage."
    )
'''

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# -------------------------
# Relationship
# -------------------------

class Relationship(BaseModel):
    type: Literal[
        "groups_projects_programs",
        "waiting_response_events",
        "events_participation",
    ] = Field(
        description="One of the three supported relationship types."
    )

    related_to: str = Field(
        description="Name of the related project, group, program or event."
    )

    role: Optional[str] = Field(
        default=None,
        description="Role of the person in this relationship."
    )

    evidence: str = Field(
        description="Exact sentence or short paragraph supporting this relationship."
    )


# -------------------------
# Additional Information
# -------------------------

class AdditionalInfo(BaseModel):

    position: Optional[str] = None

    department: Optional[str] = None

    email: Optional[str] = None

    organization: Optional[str] = None


# -------------------------
# One extracted relationship
# -------------------------

class PersonRelationship(BaseModel):

    name: str = Field(
        description="Full name of the person."
    )

    relationship: Relationship

    found_in_url: str = Field(
        description="URL where the relationship was found."
    )

    additional_info: AdditionalInfo


# -------------------------
# LLM Response
# -------------------------

class ExtractionResponse(BaseModel):

    people: List[PersonRelationship]