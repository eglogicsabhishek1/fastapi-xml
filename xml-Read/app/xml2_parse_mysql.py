import os
import time
import psutil
import xml.sax
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Database Setup ---
Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    guid = Column(String(255)) 
    reference = Column(String(255)) 
    url = Column(String(255))
    title = Column(String(255))
    country = Column(String(100))
    state = Column(String(100))
    city = Column(String(100))
    date_updated = Column(String(100))
    cpc = Column(String(100))
    currency = Column(String(50))
    company = Column(String(255))
    date_expired = Column(String(100))
    jobtype = Column(String(100))
    salary_min = Column(String(100))
    salary_max = Column(String(100))
    salary_currency = Column(String(50))
    salary_rate = Column(String(50))
    description = Column(String(1000))

# --- MySQL Connection Setup ---
DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/xml_db"
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(engine)

# --- FastAPI App ---
app = FastAPI()

# --- FilePath Input Model ---
class FilePathRequest(BaseModel):
    path: str

# --- XML Parsing Handler ---
class JobHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.current_element = ""
        self.current_job = {}
        self.current_data = []
        self.in_job = False
        self.jobs = []

    def startElement(self, name, attrs):
        if name == "job":
            self.in_job = True
            self.current_job = {}
        self.current_element = name
        self.current_data = []

    def characters(self, content):
        if self.in_job:
            self.current_data.append(content)

    def endElement(self, name):
        if self.in_job:
            data = ''.join(self.current_data).strip()
            if name != "job":
                self.current_job[name] = data
            else:
                self.jobs.append(self.current_job)
                self.in_job = False
        self.current_element = ""

# --- Insert Jobs into MySQL in Batches with Flush ---
def insert_jobs_in_batches(jobs, session, batch_size=1000):
    objects = []
    for job in jobs:
        obj = Job(
            guid=job.get("guid"),
            reference=job.get("referencenumber"),
            url=job.get("url"),
            title=job.get("title"),
            country=job.get("country"),
            state=job.get("state"),
            city=job.get("city"),
            date_updated=job.get("date_updated"),
            cpc=job.get("cpc"),
            currency=job.get("currency"),
            company=job.get("company"),
            date_expired=job.get("date_expired"),
            jobtype=job.get("jobtype"),
            salary_min=job.get("min"),
            salary_max=job.get("max"),
            salary_currency=job.get("currency"),
            salary_rate=job.get("rate"),
            description=job.get("description"),
        )
        objects.append(obj)

        if len(objects) >= batch_size:
            session.bulk_save_objects(objects)
            session.commit()
            session.flush()  # Ensure data is fully pushed to the DB
            objects = []

    if objects:
        session.bulk_save_objects(objects)
        session.commit()
        session.flush()  # Final flush

# --- Hardcoded Path to XML ---
HARD_CODED_FILE_PATH = "2Mdata.xml"

# --- Endpoint: Process XML File ---
@app.get("/process-xml/")
def read_xml_from_path():
    session = Session()

    initial_cpu = psutil.cpu_percent()
    initial_memory = psutil.virtual_memory().percent
    initial_disk = psutil.disk_usage('/').percent
    start_time = time.time()

    file_path = HARD_CODED_FILE_PATH
    if not os.path.exists(file_path):
        return JSONResponse(status_code=400, content={"message": "File path not found."})

    parser = xml.sax.make_parser()
    handler = JobHandler()
    parser.setContentHandler(handler)
    parser.parse(file_path)

    insert_jobs_in_batches(handler.jobs, session)

    elapsed_time = time.time() - start_time
    total_inserted = len(handler.jobs)

    final_cpu = psutil.cpu_percent()
    final_memory = psutil.virtual_memory().percent
    final_disk = psutil.disk_usage('/').percent

    session.close()

    return JSONResponse(content={
        "message": "File processed successfully.",
        "total_records": total_inserted,
        "time_taken_sec": round(elapsed_time, 2),
        "avg_speed_records_per_sec": round(total_inserted / elapsed_time, 2) if elapsed_time else 0,
        "initial_cpu_usage": initial_cpu,
        "final_cpu_usage": final_cpu,
        "initial_memory_usage": initial_memory,
        "final_memory_usage": final_memory,
        "initial_disk_usage": initial_disk,
        "final_disk_usage": final_disk,
    })

# --- Endpoint: Get Job by ID ---
@app.get("/job/{job_id}")
def get_job_by_id(job_id: int):
    session = Session()
    job = session.query(Job).filter(Job.id == job_id).first()
    session.close()

    if job is None:
        return JSONResponse(status_code=404, content={"message": "Job not found."})

    return {
        "id": job.id,
        "guid": job.guid,
        "reference": job.reference,
        "url": job.url,
        "title": job.title,
        "country": job.country,
        "state": job.state,
        "city": job.city,
        "date_updated": job.date_updated,
        "cpc": job.cpc,
        "currency": job.currency,
        "company": job.company,
        "date_expired": job.date_expired,
        "jobtype": job.jobtype,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency,
        "salary_rate": job.salary_rate,
        "description": job.description
    }
