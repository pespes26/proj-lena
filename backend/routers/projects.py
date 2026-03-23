from fastapi import APIRouter, Query, HTTPException, Depends
from services.unified import load_unified_projects
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/api/projects")
def get_projects():
    unified = load_unified_projects()
    projects = []
    for name, data in unified.items():
        meta = data['pnl'].get('meta', {})
        projects.append({
            'name': name,
            'status': data.get('status', 'active'),
            'source': data.get('source', 'excel'),
            'last_updated': data.get('last_updated', ''),
            'manager': meta.get('manager', ''),
            'priority_id': meta.get('priority_id', ''),
        })
    return {"projects": [p['name'] for p in projects], "projects_detail": projects}


@router.get("/api/pnl")
def get_pnl(project: str = Query(None)):
    try:
        unified = load_unified_projects()
        if project:
            if project not in unified:
                raise HTTPException(status_code=404, detail=f"פרויקט '{project}' לא נמצא")
            return {"data": {project: unified[project]['pnl']}}
        return {"data": {name: data['pnl'] for name, data in unified.items()}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת נתוני P&L: {str(e)}")


@router.get("/api/pnl/summary")
def get_pnl_summary():
    try:
        unified = load_unified_projects()
        return {"data": {name: data['pnl']['summary'] for name, data in unified.items()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת סיכום P&L: {str(e)}")
