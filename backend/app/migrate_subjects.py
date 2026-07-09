"""One-off, idempotent data migration: rename subject slugs to numeric ids.

``subjects.id`` is a string PK referenced by ``concepts.subject_id`` (a real FK)
and ``tutor_sessions.subject_id`` (a plain string). A PK can't be renamed in
place while an FK points at it, so for each mapping we:

  1. create the new subject row (a copy of the old, with the numeric id),
  2. repoint ``concepts`` and ``tutor_sessions`` to the new id,
  3. delete the old subject row.

Idempotent: subjects already migrated (old id absent) are skipped. Run with
``python -m app.migrate_subjects`` (or ``make migrate-subjects``).
"""

import asyncio
import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.features.catalog.models import Concept, Subject
from app.features.tutor.models import TutorSession

logger = logging.getLogger("app.migrate_subjects")

# Old slug → new numeric id, in catalog order.
MAPPING: dict[str, str] = {
    "fractions": "1",
    "decimals": "2",
    "percentages": "3",
    "integers": "4",
    "geometry": "5",
    "ratios": "6",
}


async def migrate(db: AsyncSession) -> int:
    """Rename any still-slugged subjects. Returns the number renamed."""
    renamed = 0
    for old, new in MAPPING.items():
        old_subject = await db.get(Subject, old)
        if old_subject is None:
            continue  # already migrated (or never seeded)
        if await db.get(Subject, new) is None:
            db.add(
                Subject(
                    id=new,
                    name=old_subject.name,
                    glyph=old_subject.glyph,
                    tone=old_subject.tone,
                    description=old_subject.description,
                    meta=old_subject.meta,
                    status=old_subject.status,
                    is_new=old_subject.is_new,
                    position=old_subject.position,
                )
            )
            await db.flush()
        # Repoint children BEFORE deleting the old subject (the FK cascades).
        await db.execute(update(Concept).where(Concept.subject_id == old).values(subject_id=new))
        await db.execute(
            update(TutorSession).where(TutorSession.subject_id == old).values(subject_id=new)
        )
        await db.delete(old_subject)
        renamed += 1
    await db.commit()
    return renamed


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async with AsyncSessionLocal() as db:
        renamed = await migrate(db)
    await engine.dispose()
    logger.info("Subject-id migration complete (%d subjects renamed to numbers).", renamed)


if __name__ == "__main__":
    asyncio.run(main())
