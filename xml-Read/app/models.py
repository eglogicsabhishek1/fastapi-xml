from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    guid = Column(String(255), unique=True, index=True)
    reference = Column(String(255))
    url = Column(String(1024))
    title = Column(String(255))
    country = Column(String(255))
    state = Column(String(255))
    city = Column(String(255))
    date_updated = Column(DateTime)
    cpc = Column(String(255))
    currency = Column(String(255))
    company = Column(String(255))
    date_expired = Column(DateTime)
    jobtype = Column(String(255))
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10))
    salary_rate = Column(String(50))
    description = Column(Text)
