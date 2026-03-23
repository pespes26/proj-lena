from fastapi import APIRouter, Query, HTTPException, Depends
from config import PROJECTS
from services.excel_reader import load_cashflow, load_project_cashflow
from services.form_calculator import form_to_cashflow
from services.unified import load_form_data
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/cashflow")
def get_cashflow():
    try:
        return {"data": load_cashflow()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת תזרים מזומנים: {str(e)}")


@router.get("/api/project-cashflow")
def get_project_cashflow(project: str = Query(...)):
    try:
        form_projects = load_form_data()
        if project in form_projects:
            return {"data": form_to_cashflow(form_projects[project])}
        if project in PROJECTS:
            data = load_project_cashflow(project)
            if data:
                return {"data": data}
        raise HTTPException(status_code=404, detail=f"פרויקט '{project}' לא נמצא")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת תזרים פרויקט: {str(e)}")
