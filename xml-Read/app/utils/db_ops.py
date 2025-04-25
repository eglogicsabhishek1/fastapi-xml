from sqlalchemy.orm import Session
from app.models import Job

def upsert_jobs_in_batches(jobs, session: Session, batch_size=1000):
    inserted = 0
    updated = 0

    all_guids = [job["guid"] for job in jobs if "guid" in job]
    existing = session.query(Job).filter(Job.guid.in_(all_guids)).all()
    existing_map = {job.guid: job for job in existing}

    to_insert = []
    to_update = []

    for job in jobs:
        guid = job["guid"]
        if guid in existing_map:
            db_job = existing_map[guid]
            changed = any(getattr(db_job, k) != job.get(k) for k in job if hasattr(db_job, k))
            if changed:
                job["id"] = db_job.id
                to_update.append(job)
        else:
            to_insert.append(job)

    if to_insert:
        session.bulk_insert_mappings(Job, to_insert)
        inserted = len(to_insert)

    if to_update:
        session.bulk_update_mappings(Job, to_update)
        updated = len(to_update)

    session.commit()
    return inserted, updated
