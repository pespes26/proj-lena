import os
import shutil
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from config import DATA_PATH, PROJECTS, BACKUP_DIR
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/data/status")
def get_data_status():
    try:
        exists = os.path.exists(DATA_PATH)
        if not exists:
            return {"exists": False}

        stat = os.stat(DATA_PATH)
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        size_kb = round(stat.st_size / 1024, 1)
        projects = list(PROJECTS.keys())

        return {
            "exists": True,
            "filename": os.path.basename(DATA_PATH),
            "modified": modified,
            "size_kb": size_kb,
            "project_count": len(projects),
            "projects": projects,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בבדיקת מצב הנתונים: {str(e)}")


@router.post("/api/data/upload")
async def upload_data(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="יש להעלות קובץ Excel בלבד (.xlsx)")

    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)

        if os.path.exists(DATA_PATH):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"data_backup_{timestamp}.xlsx"
            shutil.copy2(DATA_PATH, os.path.join(BACKUP_DIR, backup_name))

        contents = await file.read()
        with open(DATA_PATH, 'wb') as f:
            f.write(contents)

        return {"message": "הקובץ הועלה בהצלחה", "filename": file.filename, "size_kb": round(len(contents) / 1024, 1)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בהעלאת הקובץ: {str(e)}")


@router.get("/api/data/backups")
def get_backups():
    try:
        if not os.path.exists(BACKUP_DIR):
            return {"backups": []}

        backups = []
        for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
            if f.endswith('.xlsx'):
                path = os.path.join(BACKUP_DIR, f)
                stat = os.stat(path)
                backups.append({
                    "filename": f,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size_kb": round(stat.st_size / 1024, 1),
                })
        return {"backups": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת גיבויים: {str(e)}")
