from sqlalchemy import Column, String, DateTime, Integer, Time, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class StoreStatus(Base):
    __tablename__ = "store_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    timestamp_utc = Column(DateTime, nullable=False, index=True)

class BusinessHours(Base):
    __tablename__ = "business_hours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)
    start_time_local = Column(Time, nullable=False)
    end_time_local = Column(Time, nullable=False)

class StoreTimezone(Base):
    __tablename__ = "store_timezones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String, nullable=False, unique=True, index=True)
    timezone_str = Column(String, nullable=False)

class ReportStatus(Base):
    __tablename__ = "report_status"
    
    report_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    file_path = Column(String, nullable=True) 