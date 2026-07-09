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

def build_prompt(page_text: str, page_url: str) -> str:
    """
    Build the final prompt sent to the LLM.
    웹페이지 본문을 프롬프트 맨 끝에 배치하여 모델이 본문에 집중하도록 합니다.
    """
    return f"""\
Extract every PERSON explicitly mentioned in the provided webpage text. 
Ignore organizations that are not associated with a person.
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

OUTPUT SCHEMA:
Return ONLY JSON with this exact structure. Replace the `<...>` placeholders with actual data extracted from the text.
Do not use "Professor Kim" or "Virtual Reality Lab" unless they actually appear in the text.

{{
    "source_doc_id": "PLACEHOLDER",
    "source_url": "{page_url}",
    "facts": [
        {{
            "fact_id": "<Generate a e.g., fact_1 string, unique>",
            "subject": {{
                "surface_text": "<VERBATIM exact from of person text the words>",
                "type": "<OPEN Professor, Student descriptor, e.g., free-text>"
            }},
            "relationship": {{
                "type": "<MUST BE: OR events_participation groups_projects_programs waiting_response_events>",
                "role": "<OPEN Applicant, Author Director, e.g., role,>"
            }},
            "object": {{
                "surface_text": "<VERBATIM entity exact from of related text the words>",
                "type": "<OPEN Conference Group, Research descriptor, e.g., free-text>"
            }},
            "assertion": "<MUST BE: OR asserted reported speculative>",
            "evidence": "<Exact fact from justifying sentence short source text the this>",
            "additional_info": {{}}
        }}
    ]
}}

If a webpage contains no valid relationships, return an empty list for facts:
{{
    "source_doc_id": "PLACEHOLDER",
    "source_url": "{page_url}",
    "facts": []
}}

=========================================
WEBPAGE CONTENT TO PROCESS:
--------------------------------------------------
{page_text}
--------------------------------------------------
"""