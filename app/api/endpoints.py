from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.report_service import trigger_report_generation, get_report_status
import os

#  I have implemented fast api

app = FastAPI(title="LoopAI - Store Monitoring")

@app.post("/trigger_report")
def trigger_report():
    report_id = trigger_report_generation()
    return {"report_id": report_id}

@app.get("/get_report")
def get_report(report_id: str, db: Session = Depends(get_db)):
    result = get_report_status(report_id, db)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    if result["status"] == "Complete":
        file_path = result["file_path"]
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                media_type='text/csv',
                filename=f"store_report_{report_id}.csv"
            )
        else:
            raise HTTPException(status_code=404, detail="Report file not found")
    
    return {"status": result["status"]} 