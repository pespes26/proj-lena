import os
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, UploadFile, File, Depends
from config import CONTRACTS_DIR
from services.unified import load_form_data, save_form_data, import_excel_to_form
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/project-form/{project}")
def get_project_form(project: str):
    try:
        all_data = load_form_data()
        return {"data": all_data.get(project, None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת נתוני פרויקט: {str(e)}")


@router.post("/api/project-form/{project}")
def save_project_form(project: str, form_data: dict):
    try:
        all_data = load_form_data()
        form_data['last_updated'] = datetime.now().isoformat()
        if 'source' not in form_data:
            form_data['source'] = 'form'
        if 'status' not in form_data:
            form_data['status'] = 'active'
        all_data[project] = form_data
        save_form_data(all_data)
        return {"message": "נתוני הפרויקט נשמרו בהצלחה"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בשמירת נתוני פרויקט: {str(e)}")


@router.post("/api/project-form/{project}/upload-contract")
async def upload_contract(project: str, sub_index: int = Query(...), file: UploadFile = File(...)):
    try:
        contracts_dir = os.path.join(CONTRACTS_DIR, project)
        os.makedirs(contracts_dir, exist_ok=True)
        filename = f"sub_{sub_index}_{file.filename}"
        filepath = os.path.join(contracts_dir, filename)
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)

        all_data = load_form_data()
        if project in all_data and 'subcontractors' in all_data[project]:
            subs = all_data[project]['subcontractors']
            if 0 <= sub_index < len(subs):
                subs[sub_index]['contract_filename'] = file.filename
                save_form_data(all_data)
        return {"message": "חוזה הועלה בהצלחה", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בהעלאת חוזה: {str(e)}")


@router.post("/api/project-form/{project}/actuals")
def save_project_actuals(project: str, actuals_data: dict):
    try:
        all_data = load_form_data()
        if project not in all_data:
            raise HTTPException(status_code=404, detail=f"פרויקט '{project}' לא נמצא בנתוני הטופס")

        month = str(actuals_data.get('month', ''))
        if not month or int(month) < 1 or int(month) > 12:
            raise HTTPException(status_code=400, detail="חודש לא תקין")

        if 'actuals' not in all_data[project]:
            all_data[project]['actuals'] = {}

        all_data[project]['actuals'][month] = {
            'revenue': actuals_data.get('revenue', 0),
            'op_expenses': actuals_data.get('op_expenses', 0),
            'salary_expenses': actuals_data.get('salary_expenses', 0),
            'notes': actuals_data.get('notes', ''),
        }
        all_data[project]['last_updated'] = datetime.now().isoformat()
        save_form_data(all_data)
        return {"message": f"ביצוע בפועל לחודש {month} נשמר בהצלחה"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בשמירת ביצוע בפועל: {str(e)}")


@router.post("/api/import-excel-project/{project}")
def import_excel_project(project: str):
    try:
        result = import_excel_to_form(project)
        if not result:
            raise HTTPException(status_code=404, detail=f"פרויקט '{project}' לא נמצא ב-Excel")
        return {"message": f"פרויקט '{project}' יובא בהצלחה מ-Excel", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בייבוא פרויקט: {str(e)}")
