from fastapi import APIRouter, UploadFile, File, HTTPException,Depends
import os, time, psutil
from app.utils.sax_parser import parse_xml
from app.utils.parser import JobHandler
from app.utils.db_ops import upsert_jobs_in_batches
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/upload-xml")
def upload_xml(file: UploadFile = File(...), db: Session = Depends(get_db)): 
    if not file.filename.endswith(".xml"):
        raise HTTPException(status_code=400, detail="Invalid file format")

    # Save file
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Start performance tracking
    process = psutil.Process(os.getpid())
    start_time = time.time()
    start_mem = process.memory_info().rss
    start_disk = psutil.disk_io_counters().write_bytes

    # Parse XML
    handler = JobHandler()
    parse_xml(file_path, handler)

    # DB insert/update
    inserted, updated = upsert_jobs_in_batches(handler.jobs, db)

    # End performance tracking
    time_taken = time.time() - start_time
    end_mem = process.memory_info().rss
    end_disk = psutil.disk_io_counters().write_bytes

    os.remove(file_path)

    return {
        "inserted": inserted,
        "updated": updated,
        "time_taken": round(time_taken, 2),
        "memory_mb": round((end_mem - start_mem) / 1024 / 1024, 2),
        "disk_mb": round((end_disk - start_disk) / 1024 / 1024, 2),
    }
