from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from storage import load_reports_firestore, save_report_firestore
from services.unified import load_form_data
from auth import get_current_user, require_editor

router = APIRouter(dependencies=[Depends(get_current_user)])


class ReportCreate(BaseModel):
    project: str
    month: Optional[int] = None
    type: str
    title: str
    amount: Optional[float] = None
    description: Optional[str] = None


@router.get("/api/reports")
def get_reports(project: str = Query(None)):
    try:
        reports = load_reports_firestore()
        if project:
            reports = [r for r in reports if r.get('project') == project]
        return {"reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת דיווחים: {str(e)}")


@router.post("/api/reports", dependencies=[Depends(require_editor)])
def create_report(report: ReportCreate):
    try:
        all_projects = list(load_form_data().keys())
        if report.project not in all_projects:
            raise HTTPException(status_code=404, detail=f"פרויקט '{report.project}' לא נמצא")

        new_report = {
            "project": report.project,
            "month": report.month,
            "type": report.type,
            "title": report.title,
            "amount": report.amount,
            "description": report.description,
            "created_at": datetime.now().isoformat(),
        }
        save_report_firestore(new_report)
        return {"report": new_report, "message": "הדיווח נשמר בהצלחה"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בשמירת דיווח: {str(e)}")
