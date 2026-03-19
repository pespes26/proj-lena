import os
import json
import shutil
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from data_loader import load_pnl, load_cashflow, load_dashboard_kpis, load_project_cashflow, PROJECTS, DATA_PATH

app = FastAPI(title="סנג'ר - P&L & Cash Flow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/projects")
def get_projects():
    return {"projects": list(PROJECTS.keys())}


@app.get("/api/pnl")
def get_pnl(project: str = Query(None)):
    try:
        if project and project not in PROJECTS:
            raise HTTPException(status_code=404, detail=f"פרויקט '{project}' לא נמצא")
        data = load_pnl(project)
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת נתוני P&L: {str(e)}")


@app.get("/api/pnl/summary")
def get_pnl_summary():
    try:
        data = load_pnl()
        return {"data": {name: info['summary'] for name, info in data.items()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת סיכום P&L: {str(e)}")


@app.get("/api/cashflow")
def get_cashflow():
    try:
        return {"data": load_cashflow()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת תזרים מזומנים: {str(e)}")


@app.get("/api/project-cashflow")
def get_project_cashflow(project: str = Query(...)):
    try:
        if project not in PROJECTS:
            raise HTTPException(status_code=404, detail=f"פרויקט '{project}' לא נמצא")
        data = load_project_cashflow(project)
        if not data:
            raise HTTPException(status_code=404, detail="אין נתוני תזרים לפרויקט")
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת תזרים פרויקט: {str(e)}")


@app.get("/api/dashboard")
def get_dashboard():
    try:
        return {"data": load_dashboard_kpis()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת נתוני דשבורד: {str(e)}")


@app.get("/api/data/status")
def get_data_status():
    try:
        exists = os.path.exists(DATA_PATH)
        if not exists:
            return {"exists": False}

        stat = os.stat(DATA_PATH)
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        size_kb = round(stat.st_size / 1024, 1)

        projects = list(PROJECTS.keys())
        project_count = len(projects)

        return {
            "exists": True,
            "filename": os.path.basename(DATA_PATH),
            "modified": modified,
            "size_kb": size_kb,
            "project_count": project_count,
            "projects": projects,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בבדיקת מצב הנתונים: {str(e)}")


@app.post("/api/data/upload")
async def upload_data(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="יש להעלות קובץ Excel בלבד (.xlsx)")

    try:
        backup_dir = os.path.join(os.path.dirname(DATA_PATH), 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        if os.path.exists(DATA_PATH):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"data_backup_{timestamp}.xlsx"
            shutil.copy2(DATA_PATH, os.path.join(backup_dir, backup_name))

        contents = await file.read()
        with open(DATA_PATH, 'wb') as f:
            f.write(contents)

        return {"message": "הקובץ הועלה בהצלחה", "filename": file.filename, "size_kb": round(len(contents) / 1024, 1)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בהעלאת הקובץ: {str(e)}")


@app.get("/api/data/backups")
def get_backups():
    try:
        backup_dir = os.path.join(os.path.dirname(DATA_PATH), 'backups')
        if not os.path.exists(backup_dir):
            return {"backups": []}

        backups = []
        for f in sorted(os.listdir(backup_dir), reverse=True):
            if f.endswith('.xlsx'):
                path = os.path.join(backup_dir, f)
                stat = os.stat(path)
                backups.append({
                    "filename": f,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size_kb": round(stat.st_size / 1024, 1),
                })
        return {"backups": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת גיבויים: {str(e)}")


# --- Reports ---

REPORTS_FILE = os.path.join(os.path.dirname(DATA_PATH), 'reports.json')


class ReportCreate(BaseModel):
    project: str
    month: Optional[int] = None
    type: str  # 'expense' | 'revenue' | 'note' | 'issue'
    title: str
    amount: Optional[float] = None
    description: Optional[str] = None


def _load_reports():
    if not os.path.exists(REPORTS_FILE):
        return []
    with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_reports(reports):
    with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)


@app.get("/api/reports")
def get_reports(project: str = Query(None)):
    try:
        reports = _load_reports()
        if project:
            reports = [r for r in reports if r['project'] == project]
        return {"reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת דיווחים: {str(e)}")


@app.post("/api/reports")
def create_report(report: ReportCreate):
    try:
        if report.project not in PROJECTS:
            raise HTTPException(status_code=404, detail=f"פרויקט '{report.project}' לא נמצא")

        reports = _load_reports()
        new_report = {
            "id": len(reports) + 1,
            "project": report.project,
            "month": report.month,
            "type": report.type,
            "title": report.title,
            "amount": report.amount,
            "description": report.description,
            "created_at": datetime.now().isoformat(),
        }
        reports.append(new_report)
        _save_reports(reports)
        return {"report": new_report, "message": "הדיווח נשמר בהצלחה"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בשמירת דיווח: {str(e)}")


# --- Project Form ---

PROJECTS_DATA_FILE = os.path.join(os.path.dirname(DATA_PATH), 'projects_data.json')


def _load_projects_data():
    if not os.path.exists(PROJECTS_DATA_FILE):
        return {}
    with open(PROJECTS_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_projects_data(data):
    with open(PROJECTS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.get("/api/project-form/{project}")
def get_project_form(project: str):
    try:
        all_data = _load_projects_data()
        return {"data": all_data.get(project, None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת נתוני פרויקט: {str(e)}")


@app.post("/api/project-form/{project}")
def save_project_form(project: str, form_data: dict):
    try:
        all_data = _load_projects_data()
        all_data[project] = form_data
        _save_projects_data(all_data)
        return {"message": "נתוני הפרויקט נשמרו בהצלחה"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בשמירת נתוני פרויקט: {str(e)}")


# --- Attendance ---

ATTENDANCE_FILE = os.path.join(os.path.dirname(DATA_PATH), 'attendance_data.json')


def _load_attendance():
    if not os.path.exists(ATTENDANCE_FILE):
        return None
    with open(ATTENDANCE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_attendance(data):
    with open(ATTENDANCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.post("/api/attendance/upload")
async def upload_attendance(file: UploadFile = File(...), hourly_rate: float = Query(50)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="יש להעלות קובץ Excel בלבד (.xlsx)")

    try:
        import pandas as pd
        from io import BytesIO

        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        # Normalize column names
        col_map = {}
        for col in df.columns:
            cl = str(col).strip()
            if 'עובד' in cl or 'שם' in cl: col_map[col] = 'employee'
            elif 'תאריך' in cl: col_map[col] = 'date'
            elif 'כניסה' in cl: col_map[col] = 'entry'
            elif 'יציאה' in cl: col_map[col] = 'exit'
            elif 'פרויקט' in cl or 'project' in cl.lower(): col_map[col] = 'project'
            elif 'שעות' in cl or 'hours' in cl.lower(): col_map[col] = 'hours'
        df = df.rename(columns=col_map)

        records = []
        for _, row in df.iterrows():
            emp = str(row.get('employee', '')).strip()
            proj = str(row.get('project', '')).strip()
            if not emp or not proj:
                continue

            hours = 0
            if 'hours' in row and pd.notna(row['hours']):
                hours = float(row['hours'])
            elif 'entry' in row and 'exit' in row and pd.notna(row['entry']) and pd.notna(row['exit']):
                try:
                    entry = pd.to_datetime(str(row['entry']))
                    exit_t = pd.to_datetime(str(row['exit']))
                    hours = round((exit_t - entry).total_seconds() / 3600, 2)
                except:
                    hours = 0

            date_str = ''
            if 'date' in row and pd.notna(row['date']):
                try:
                    date_str = pd.to_datetime(row['date']).strftime('%Y-%m-%d')
                except:
                    date_str = str(row['date'])

            records.append({
                'employee': emp,
                'date': date_str,
                'entry': str(row.get('entry', '')),
                'exit': str(row.get('exit', '')),
                'project': proj,
                'hours': round(hours, 2),
            })

        # Aggregate by project
        by_project = {}
        for r in records:
            p = r['project']
            if p not in by_project:
                by_project[p] = {'total_hours': 0, 'employees': set(), 'cost': 0}
            by_project[p]['total_hours'] += r['hours']
            by_project[p]['employees'].add(r['employee'])
        for p in by_project:
            by_project[p]['employees'] = len(by_project[p]['employees'])
            by_project[p]['total_hours'] = round(by_project[p]['total_hours'], 2)
            by_project[p]['cost'] = round(by_project[p]['total_hours'] * hourly_rate, 2)

        # Aggregate by employee
        by_employee = {}
        for r in records:
            e = r['employee']
            if e not in by_employee:
                by_employee[e] = {'total_hours': 0, 'projects': {}}
            by_employee[e]['total_hours'] += r['hours']
            by_employee[e]['projects'][r['project']] = round(
                by_employee[e]['projects'].get(r['project'], 0) + r['hours'], 2)
        for e in by_employee:
            by_employee[e]['total_hours'] = round(by_employee[e]['total_hours'], 2)

        result = {
            'uploaded_at': datetime.now().isoformat(),
            'filename': file.filename,
            'hourly_rate': hourly_rate,
            'record_count': len(records),
            'records': records,
            'by_project': by_project,
            'by_employee': by_employee,
        }
        _save_attendance(result)
        return {"message": f"קובץ נוכחות עובד בהצלחה — {len(records)} רשומות", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בעיבוד קובץ נוכחות: {str(e)}")


@app.get("/api/attendance")
def get_attendance():
    data = _load_attendance()
    if not data:
        return {"data": None}
    return {"data": data}


@app.get("/api/attendance/by-project")
def get_attendance_by_project(project: str = Query(...)):
    data = _load_attendance()
    if not data:
        return {"records": [], "summary": None}
    records = [r for r in data['records'] if r['project'] == project]
    summary = data['by_project'].get(project)
    return {"records": records, "summary": summary}
