"""Business logic for the content catalog: subjects and concepts (topics).

List endpoints share the pagination/search/sort helpers in ``app.core.query``;
this module adds the resource-specific filters and per-student ``progress``.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.query import ListParams, Page, apply_search, apply_sort, paginate
from app.features.catalog.models import Concept, Subject
from app.features.catalog.schemas import (
    ConceptCreate,
    ConceptOut,
    ConceptUpdate,
    SubjectCreate,
    SubjectDetailOut,
    SubjectOut,
    SubjectUpdate,
)
from app.features.tutor.models import StudentConceptState

_SUBJECT_SORTS = {
    "position": Subject.position,
    "name": Subject.name,
    "created_at": Subject.created_at,
}
_CONCEPT_SORTS = {
    "position": Concept.position,
    "name": Concept.name,
    "difficulty_band": Concept.difficulty_band,
    "created_at": Concept.created_at,
}


class SubjectNotFoundError(Exception):
    pass


class ConceptNotFoundError(Exception):
    pass


class DuplicateError(Exception):
    pass


async def _subject_progress(db: AsyncSession, student_id: int) -> dict[str, float]:
    """Average per-concept mastery per subject for one student (0..1)."""
    stmt = (
        select(Concept.subject_id, func.avg(StudentConceptState.mastery))
        .join(StudentConceptState, StudentConceptState.concept_id == Concept.id)
        .where(StudentConceptState.student_id == student_id)
        .group_by(Concept.subject_id)
    )
    rows = (await db.execute(stmt)).all()
    return {subject_id: round(float(avg or 0.0), 3) for subject_id, avg in rows}


def _to_subject_out(subject: Subject, progress: float) -> SubjectOut:
    return SubjectOut(
        id=subject.id,
        name=subject.name,
        glyph=subject.glyph,
        tone=subject.tone,
        desc=subject.description,
        meta=subject.meta,
        status=subject.status,
        is_new=subject.is_new,
        position=subject.position,
        progress=progress,
    )


async def list_subjects(
    db: AsyncSession,
    student_id: int,
    params: ListParams,
    status: str | None = None,
    is_new: bool | None = None,
) -> Page[SubjectOut]:
    stmt = select(Subject)
    if status is not None:
        stmt = stmt.where(Subject.status == status)
    if is_new is not None:
        stmt = stmt.where(Subject.is_new == is_new)
    stmt = apply_search(stmt, [Subject.name, Subject.description], params.q)
    stmt = apply_sort(stmt, params.sort, _SUBJECT_SORTS, Subject.position.asc())
    rows, total = await paginate(db, stmt, params.limit, params.offset)
    progress = await _subject_progress(db, student_id)
    items = [_to_subject_out(s, progress.get(s.id, 0.0)) for s in rows]
    return Page.build(items, total, params.limit, params.offset)


def _to_concept_out(concept: Concept) -> ConceptOut:
    return ConceptOut(
        id=concept.id,
        subject_id=concept.subject_id,
        name=concept.name,
        glyph=concept.glyph,
        tone=concept.tone,
        short=concept.short,
        long=concept.long,
        difficulty_band=concept.difficulty_band,
        position=concept.position,
    )


async def get_subject(db: AsyncSession, student_id: int, subject_id: str) -> SubjectDetailOut:
    subject = await db.get(Subject, subject_id)
    if subject is None:
        raise SubjectNotFoundError
    progress = await _subject_progress(db, student_id)
    concepts = (
        (
            await db.execute(
                select(Concept)
                .where(Concept.subject_id == subject_id)
                .order_by(Concept.position.asc())
            )
        )
        .scalars()
        .all()
    )
    base = _to_subject_out(subject, progress.get(subject_id, 0.0))
    return SubjectDetailOut(**base.model_dump(), concepts=[_to_concept_out(c) for c in concepts])


async def list_concepts(
    db: AsyncSession,
    params: ListParams,
    subject_id: str | None = None,
    difficulty_band: str | None = None,
) -> Page[ConceptOut]:
    stmt = select(Concept)
    if subject_id is not None:
        stmt = stmt.where(Concept.subject_id == subject_id)
    if difficulty_band is not None:
        stmt = stmt.where(Concept.difficulty_band == difficulty_band)
    stmt = apply_search(stmt, [Concept.name, Concept.short, Concept.long], params.q)
    stmt = apply_sort(stmt, params.sort, _CONCEPT_SORTS, Concept.position.asc())
    rows, total = await paginate(db, stmt, params.limit, params.offset)
    return Page.build([_to_concept_out(c) for c in rows], total, params.limit, params.offset)


async def get_concept(db: AsyncSession, concept_id: str) -> ConceptOut:
    concept = await db.get(Concept, concept_id)
    if concept is None:
        raise ConceptNotFoundError
    return _to_concept_out(concept)


async def create_subject(db: AsyncSession, payload: SubjectCreate) -> SubjectOut:
    if await db.get(Subject, payload.id) is not None:
        raise DuplicateError
    subject = Subject(
        id=payload.id,
        name=payload.name,
        glyph=payload.glyph,
        tone=payload.tone,
        description=payload.desc,
        meta=payload.meta,
        status=payload.status,
        is_new=payload.is_new,
        position=payload.position,
    )
    db.add(subject)
    await db.commit()
    await db.refresh(subject)
    return _to_subject_out(subject, 0.0)


async def update_subject(db: AsyncSession, subject_id: str, payload: SubjectUpdate) -> SubjectOut:
    subject = await db.get(Subject, subject_id)
    if subject is None:
        raise SubjectNotFoundError
    data = payload.model_dump(exclude_unset=True)
    if "desc" in data:
        subject.description = data.pop("desc")
    for field, value in data.items():
        setattr(subject, field, value)
    await db.commit()
    await db.refresh(subject)
    return _to_subject_out(subject, 0.0)


async def create_concept(db: AsyncSession, payload: ConceptCreate) -> ConceptOut:
    if await db.get(Concept, payload.id) is not None:
        raise DuplicateError
    if await db.get(Subject, payload.subject_id) is None:
        raise SubjectNotFoundError
    concept = Concept(**payload.model_dump())
    db.add(concept)
    await db.commit()
    await db.refresh(concept)
    return _to_concept_out(concept)


async def update_concept(db: AsyncSession, concept_id: str, payload: ConceptUpdate) -> ConceptOut:
    concept = await db.get(Concept, concept_id)
    if concept is None:
        raise ConceptNotFoundError
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(concept, field, value)
    await db.commit()
    await db.refresh(concept)
    return _to_concept_out(concept)
