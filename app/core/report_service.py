import uuid
import csv
import os
from datetime import datetime
from sqlalchemy.orm import Session
from .models import ReportStatus
from .database import SessionLocal
from .calculator import generate_report
import threading
import pandas as pd

def create_report_id() -> str:
    return str(uuid.uuid4())

def save_report_to_csv(report_data: list, file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    df = pd.DataFrame(report_data)
    df.to_csv(file_path, index=False)

def generate_report_async(report_id: str):
    session = SessionLocal()
    try:
        report_status = session.query(ReportStatus).filter(ReportStatus.report_id == report_id).first()
        if not report_status:
            return
        
        report_data = generate_report(session)
        
        file_path = f"reports/{report_id}.csv"
        save_report_to_csv(report_data, file_path)
        
        report_status.status = "Complete"
        report_status.completed_at = datetime.utcnow()
        report_status.file_path = file_path
        session.commit()
        
    except Exception as e:
        report_status = session.query(ReportStatus).filter(ReportStatus.report_id == report_id).first()
        if report_status:
            report_status.status = "Failed"
            session.commit()
        print(f"Report generation failed: {e}")
    finally:
        session.close()

def trigger_report_generation() -> str:
    report_id = create_report_id()
    
    session = SessionLocal()
    try:
        report_status = ReportStatus(
            report_id=report_id,
            status="Running"
        )
        session.add(report_status)
        session.commit()
        
        thread = threading.Thread(target=generate_report_async, args=(report_id,))
        thread.start()
        
        return report_id
    finally:
        session.close()

def get_report_status(report_id: str, session: Session) -> dict:
    report = session.query(ReportStatus).filter(ReportStatus.report_id == report_id).first()
    
    if not report:
        return {"error": "Report not found"}
    
    if report.status == "Complete":
        return {
            "status": "Complete",
            "file_path": report.file_path
        }
    elif report.status == "Running":
        return {"status": "Running"}
    else:
        return {"status": "Failed"} 