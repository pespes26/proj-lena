from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, UploadFile, File, Depends
from config import ATTENDANCE_FILE
from storage import load_json, save_json
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/api/attendance/upload")
async def upload_attendance(file: UploadFile = File(...), hourly_rate: float = Query(50)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="יש להעלות קובץ Excel בלבד (.xlsx)")

    try:
        import pandas as pd
        from io import BytesIO

        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

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
        save_json(ATTENDANCE_FILE, result)
        return {"message": f"קובץ נוכחות עובד בהצלחה — {len(records)} רשומות", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בעיבוד קובץ נוכחות: {str(e)}")


@router.get("/api/attendance")
def get_attendance():
    data = load_json(ATTENDANCE_FILE, None)
    if not data:
        return {"data": None}
    return {"data": data}


@router.get("/api/attendance/by-project")
def get_attendance_by_project(project: str = Query(...)):
    data = load_json(ATTENDANCE_FILE, None)
    if not data:
        return {"records": [], "summary": None}
    records = [r for r in data['records'] if r['project'] == project]
    summary = data['by_project'].get(project)
    return {"records": records, "summary": summary}
