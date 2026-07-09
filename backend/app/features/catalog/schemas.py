"""Request/response schemas for the content catalog (subjects + concepts)."""

from typing import Literal

from pydantic import BaseModel, Field

Tone = Literal["green", "violet", "amber", "coral"]
Difficulty = Literal["easy", "med", "hard"]


class ConceptOut(BaseModel):
    id: str
    subject_id: str
    name: str
    glyph: str
    tone: str
    short: str
    long: str
    difficulty_band: str
    position: int


class SubjectOut(BaseModel):
    id: str
    name: str
    glyph: str
    tone: str
    desc: str
    meta: str
    status: str
    is_new: bool
    position: int
    # Per-student completion fraction (0..1); 0 for teachers / fresh students.
    progress: float = 0.0


class SubjectDetailOut(SubjectOut):
    concepts: list[ConceptOut] = []


class SubjectCreate(BaseModel):
    id: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=128)
    glyph: str = Field(default="", max_length=16)
    tone: Tone = "green"
    desc: str = Field(default="", max_length=255)
    meta: str = Field(default="", max_length=64)
    status: Literal["active", "draft"] = "active"
    is_new: bool = False
    position: int = 0


class SubjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    glyph: str | None = Field(default=None, max_length=16)
    tone: Tone | None = None
    desc: str | None = Field(default=None, max_length=255)
    meta: str | None = Field(default=None, max_length=64)
    status: Literal["active", "draft"] | None = None
    is_new: bool | None = None
    position: int | None = None


class ConceptCreate(BaseModel):
    id: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9_-]+$")
    subject_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    glyph: str = Field(default="", max_length=16)
    tone: Tone = "green"
    short: str = Field(default="", max_length=255)
    long: str = Field(default="", max_length=4000)
    difficulty_band: Difficulty = "med"
    position: int = 0


class ConceptUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    glyph: str | None = Field(default=None, max_length=16)
    tone: Tone | None = None
    short: str | None = Field(default=None, max_length=255)
    long: str | None = Field(default=None, max_length=4000)
    difficulty_band: Difficulty | None = None
    position: int | None = None
