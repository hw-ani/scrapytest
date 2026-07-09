from textwrap import dedent

SYSTEM_PROMPT = dedent("""\
You are an information extraction system specialized in university websites.
Your ONLY task is to extract explicit factual relationships involving people.
You MUST NOT summarize. You MUST NOT infer information. You MUST NOT guess.
You MUST NOT combine multiple relationships into a single object.
If there is no supporting evidence, do not output the relationship.

Return ONLY valid JSON. The JSON MUST follow exactly the schema requested.
Do NOT include markdown. Do NOT include explanations. Do NOT wrap the JSON inside ``` blocks.
""")

USER_PROMPT = dedent("""\
Extract every PERSON explicitly mentioned in the webpage. Ignore organizations that are not associated with a person.
Ignore relationships without a clearly identifiable person.
For EACH relationship, generate ONE independent fact object.

=========================================
RELATIONSHIP CATEGORIES (relationship.type MUST be one of these exactly):

1. groups_projects_programs
Extract ONLY explicit memberships, affiliations, collaborations or participation involving: 
Research Group, Laboratory, Research Center, Project, Scholarship Program, Government-funded Project, Company Collaboration, etc.

2. waiting_response_events
Extract ONLY events that indicate someone is waiting for a future response. Examples: 
Recruitment, Graduate Admission, Internship, Interview, Registration, Application Period, Deadline, Paper Under Review, etc.

3. events_participation
Extract ONLY completed or ongoing participations. Examples: 
Conference, Workshop, Competition, Publication, Symposium, Seminar, Invited Talk, Social Gathering, etc.
=========================================

For EACH extracted relationship, return ONE object inside the "facts" array with EXACTLY this format:

{
    "source_doc_id": "PLACEHOLDER",
    "source_url": "__PAGE_URL__",
    "facts": [
        {
            "fact_id": "fact_1",
            "subject": {
                "surface_text": "Professor Kim",
                "type": "Professor"
            },
            "relationship": {
                "type": "groups_projects_programs", 
                "role": "Director"
            },
            "object": {
                "surface_text": "Virtual Reality Lab",
                "type": "Research Group"
            },
            "assertion": "asserted",
            "evidence": "Professor Kim directs the Virtual Reality Lab.",
            "additional_info": {}
        }
    ]
}

RULES FOR FIELDS:
- "relationship.type": MUST BE EXACTLY ONE OF "groups_projects_programs", "waiting_response_events", or "events_participation". Do not write anything else.
- "assertion": MUST BE EXACTLY ONE OF "asserted", "reported", or "speculative". Do not write anything else.

If Professor Kim appears in BK21 and IEEE VR 2025, output TWO separate fact objects inside the "facts" list.
Never merge multiple relationships into one fact object.

If a webpage contains no valid relationships, return:
{
    "source_doc_id": "PLACEHOLDER",
    "source_url": "__PAGE_URL__",
    "facts": []
}

Return ONLY JSON.
""")

def build_prompt(page_text: str, page_url: str) -> str:
    """
    Build the final prompt sent to the LLM.
    """
    prompt = USER_PROMPT.replace("__PAGE_URL__", page_url)
    
    return f"""\
{SYSTEM_PROMPT}

WEBPAGE CONTENT
--------------------------------------------------
{page_text}
--------------------------------------------------

{prompt}
"""