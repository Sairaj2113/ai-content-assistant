from typing import Annotated

from pydantic import BaseModel, StringConstraints

# Whitespace is stripped before the length checks, so "   " fails min_length.
EntryText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)
]


class EntryCreate(BaseModel):
    text: EntryText


class EntrySummary(BaseModel):
    """One row in the list view."""

    id: int
    summary: str
    tags: list[str]
    created_at: str
    preview: str


class Entry(BaseModel):
    """A full entry."""

    id: int
    text: str
    summary: str
    tags: list[str]
    created_at: str
