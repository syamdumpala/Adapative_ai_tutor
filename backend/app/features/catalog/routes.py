"""HTTP routes for the content catalog: subjects and concepts (topics).

Reads are open to any authenticated account; writes require a teacher.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.query import ListParams, Page, list_params
from app.features.auth.dependencies import get_current_user, require_teacher
from app.features.auth.models import Student
from app.features.catalog import service
from app.features.catalog.schemas import (
    ConceptCreate,
    ConceptOut,
    ConceptUpdate,
    SubjectCreate,
    SubjectDetailOut,
    SubjectOut,
    SubjectUpdate,
)

router = APIRouter(tags=["catalog"])


# ---- Subjects ----------------------------------------------------------------


@router.get("/subjects", response_model=Page[SubjectOut])
async def list_subjects(
    params: ListParams = Depends(list_params),
    status: str | None = Query(None, description="Filter by status (active|draft)"),
    is_new: bool | None = Query(None, description="Filter to newly added subjects"),
    current: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Subject catalog with search (`q` over name/description), sorting and paging.

    `progress` is the requesting student's completion fraction for each subject.
    """
    return await service.list_subjects(db, current.id, params, status=status, is_new=is_new)


@router.get("/subjects/{subject_id}", response_model=SubjectDetailOut)
async def get_subject(
    subject_id: str,
    current: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.get_subject(db, current.id, subject_id)
    except service.SubjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject not found") from None


@router.post("/subjects", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
async def create_subject(
    payload: SubjectCreate,
    _teacher: Student = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.create_subject(db, payload)
    except service.DuplicateError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "A subject with this id already exists"
        ) from None


@router.patch("/subjects/{subject_id}", response_model=SubjectOut)
async def update_subject(
    subject_id: str,
    payload: SubjectUpdate,
    _teacher: Student = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.update_subject(db, subject_id, payload)
    except service.SubjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject not found") from None


# ---- Concepts / topics -------------------------------------------------------


@router.get("/topics", response_model=Page[ConceptOut])
async def list_topics(
    params: ListParams = Depends(list_params),
    subject_id: str | None = Query(None, description="Filter to one subject"),
    difficulty_band: str | None = Query(None, description="Filter by difficulty (easy|med|hard)"),
    current: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List of concepts/topics with search (`q` over name/short/long), filters and paging."""
    return await service.list_concepts(
        db, params, subject_id=subject_id, difficulty_band=difficulty_band
    )


@router.get("/topics/{concept_id}", response_model=ConceptOut)
async def get_topic(
    concept_id: str,
    current: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.get_concept(db, concept_id)
    except service.ConceptNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found") from None


@router.post("/topics", response_model=ConceptOut, status_code=status.HTTP_201_CREATED)
async def create_topic(
    payload: ConceptCreate,
    _teacher: Student = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.create_concept(db, payload)
    except service.DuplicateError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "A topic with this id already exists"
        ) from None
    except service.SubjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject not found") from None


@router.patch("/topics/{concept_id}", response_model=ConceptOut)
async def update_topic(
    concept_id: str,
    payload: ConceptUpdate,
    _teacher: Student = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.update_concept(db, concept_id, payload)
    except service.ConceptNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found") from None
