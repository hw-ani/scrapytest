
'''
from textwrap import dedent

SYSTEM_PROMPT = dedent("""
You are an information extraction system.

Your ONLY task is to extract explicit factual relationships from university webpages.

You MUST NOT summarize.

You MUST NOT infer information.

You MUST NOT guess.

If information is not explicitly written,
do not include it.

Return ONLY valid JSON.

The JSON MUST match the provided schema exactly.
""")


USER_PROMPT = dedent("""
Extract every PERSON explicitly mentioned in the webpage.

For EACH person extract ONLY the following relationship categories.

==========================================================
CATEGORY 1

Groups / Laboratories / Projects / Programs

Examples:

• Research Group
• Laboratory
• Project
• Sholarship programs (BK21, GKS, KINGS...)
• Laboratory resources (GPU Rental, AWS/Google Cloud sbscription, ...)
• Government-funded project
• Company collaboration (co-workers, colleagues, ...)
• Research Topic (Research papers in review, to appear or submitted)
• Research Conferences (IEEE, ACSAC, ...)
• Research Venues (IEEE, Springer, ...)

For every relationship include:

- entity name
- entity type
- person's role
- exact evidence sentence

Possible psychological targets:

- Authority
- Familiarity
- Trust
- Carelessness
- Urgent matters (financial support, ...)

==========================================================
CATEGORY 2

Waiting Events

Examples:

- Recruitment
- Graduate admission
- Internship
- Interview
- Registration
- Application period
- Deadline
- Seminar registration

Include:

- event name
- current status
- exact evidence

Possible psychological targets:

- Expectation
- Urgency

==========================================================
CATEGORY 3

Event Participation

Examples:

- Conference
- Workshop
- Competition
- Publication
- Seminar
- Symposium
- Hackathon
- Laboratory meeting / MT
- Get-together for dinner/coffee/drink

Include:

- event name
- person's role
- exact evidence

Possible psychological targets:

- Uncritical Acceptance

==========================================================

IMPORTANT

Extract ONLY relationships that are explicitly stated.

If no relationship exists,
return an empty list.

Never summarize the webpage.

Never explain your reasoning.

Return ONLY JSON.
""")


def build_prompt(page_text: str) -> str:
    """
    Build the final prompt sent to the LLM.
    """

    return f"""
{SYSTEM_PROMPT}

Webpage:

{page_text}

{USER_PROMPT}
"""
'''

from textwrap import dedent


SYSTEM_PROMPT = dedent("""
You are an information extraction system specialized in university websites.

Your ONLY task is to extract explicit factual relationships involving people.

You MUST NOT summarize.

You MUST NOT infer information.

You MUST NOT guess.

You MUST NOT combine multiple relationships into a single object.

If a person has three different relationships,
you MUST output three different objects.

Extract ONLY relationships explicitly supported by the webpage.

If there is no supporting evidence,
do not output the relationship.

Return ONLY valid JSON.

The JSON MUST follow exactly the schema requested.

Do NOT include markdown.

Do NOT include explanations.

Do NOT wrap the JSON inside ``` blocks.
""")


USER_PROMPT = dedent("""
Extract every PERSON explicitly mentioned in the webpage.

Ignore organizations that are not associated with a person.

Ignore relationships without a clearly identifiable person.

For EACH relationship, generate ONE independent object.

=========================================
CATEGORY 1

Relationship type:

groups_projects_programs

Extract ONLY explicit memberships, affiliations, collaborations or participation involving:

• Research Group
• Laboratory
• Research Center
• Project
• Scholarship Program (BK21, GKS, KINGS, ...)
• Laboratory Resources (GPU Rental, Cloud Resources, ...)
• Government-funded Project
• Company Collaboration
• Research Topic
• Research Grant
• Research Venue
• Journal
• Conference Organization
• Startup
• Institute

For each relationship extract:

- related_to
- role
- exact evidence sentence

Possible psychological targets:

- Authority
- Familiarity
- Trust
- Carelessness

=========================================
CATEGORY 2

Relationship type:

waiting_response_events

Extract ONLY events that indicate someone is waiting for a future response.

Examples:

• Recruitment
• Graduate Admission
• Internship
• Interview
• Registration
• Application Period
• Deadline
• Paper Under Review
• Paper Submitted
• Grant Proposal Submitted
• Conference Submission
• Student Recruitment

For each relationship extract:

- related_to
- role (if available)
- exact evidence sentence

Possible psychological targets:

- Expectation
- Urgency

=========================================
CATEGORY 3

Relationship type:

events_participation

Extract ONLY completed or ongoing participations.

Examples:

• Conference
• Workshop
• Competition
• Publication
• Symposium
• Seminar
• Hackathon
• Demonstration
• Invited Talk
• Laboratory Meeting
• Social Gathering (Dinner, Coffee, Drink)

For each relationship extract:

- related_to
- role
- exact evidence sentence

Possible psychological targets:

- Uncritical Acceptance

=========================================
For EACH extracted relationship return ONE object with EXACTLY this format:

{
    "name": "...",
    "relationship": {
        "type": "groups_projects_programs | waiting_response_events | events_participation",
        "related_to": "...",
        "role": "...",
        "evidence": "..."
    },
    "found_in_url": "__PAGE_URL__",
    "additional_info": {
        "position": "...",
        "department": "...",
        "email": "...",
        "organization": "..."
        ...
    }
}

If Professor Kim appears in BK21 and IEEE VR 2025,
return TWO objects.

Never merge multiple relationships into one object.

If a webpage contains no valid relationships, return:

{
    "people": []
}

Return ONLY JSON.
""")


def build_prompt(page_text: str, page_url: str) -> str:
    """
    Build the final prompt sent to the LLM.
    """

    prompt = USER_PROMPT.replace("__PAGE_URL__", page_url)

    return f"""
{SYSTEM_PROMPT}

WEBPAGE CONTENT

--------------------------------------------------

{page_text}

--------------------------------------------------

{prompt}
"""