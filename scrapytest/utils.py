'''
SECOND DRAFT

from bs4 import BeautifulSoup, Comment

import re


########################################################################
# HTML Cleaning
########################################################################

def clean_html(html: str) -> str:
    """
    Remove non-visible HTML elements while preserving the
    meaningful page structure.
    """

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup([
        "script",
        "style",
        "noscript",
        "iframe",
        "svg",
        "canvas",
        "header",
        "footer",
        "nav",
        "form",
        "aside",
    ]):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(
        string=lambda text: isinstance(text, Comment)
    ):
        comment.extract()

    return str(soup)


########################################################################
# Visible Text
########################################################################

def extract_visible_text(html: str) -> str:
    """
    Convert cleaned HTML into plain text.
    """

    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text(
        separator="\n",
        strip=True,
    )

    # Remove duplicated blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    # Remove duplicated spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


########################################################################
# Chunking
########################################################################

def chunk_text(
    text: str,
    chunk_size: int = 2500,
    overlap: int = 250,
):
    """
    Split long text into overlapping chunks.

    This is useful because LLMs have limited context windows.
    """

    if len(text) <= chunk_size:
        return [text]

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(
            text[start:end]
        )

        start += chunk_size - overlap

    return chunks


########################################################################
# Simple Page Filter
########################################################################

def is_empty_page(text: str) -> bool:
    """
    Ignore pages that contain almost no useful information.
    """

    if not text:
        return True

    if len(text.split()) < 20:
        return True

    return False
'''

import re
from typing import List

# Approximate number of words per chunk.
# Feel free to adjust based on the model you use.
DEFAULT_CHUNK_SIZE = 900

# Number of overlapping words between chunks.
# Helps preserve context across chunk boundaries.
DEFAULT_OVERLAP = 100


def clean_text(text: str) -> str:
    """
    Clean webpage text before sending it to the LLM.
    """

    if not text:
        return ""

    # Normalize newlines
    text = text.replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove repeated spaces
    text = re.sub(r"[ ]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> List[str]:
    """
    Split long text into overlapping chunks.

    Uses words instead of characters to avoid cutting
    sentences in unnatural positions.
    """

    text = clean_text(text)

    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []

    start = 0

    while start < len(words):

        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


def merge_people(results):
    """
    Merge duplicate relationships extracted from
    multiple chunks of the SAME webpage.

    This does NOT merge across webpages.
    """

    merged = []

    seen = set()

    for person in results:

        key = (
            person.name,
            person.relationship.type,
            person.relationship.related_to,
            person.relationship.role,
            person.found_in_url,
        )

        if key in seen:
            continue

        seen.add(key)
        merged.append(person)

    return merged