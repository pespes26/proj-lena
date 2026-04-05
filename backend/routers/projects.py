from fastapi import APIRouter, Query, HTTPException, Depends
from services.unified import load_unified_projects
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


def _filter_projects(unified, user):
    """Filter projects based on user role. project_manager sees only their projects."""
    if user['role'] != 'project_manager':
        return unified
    manager = user.get('linked_manager', '')
    if not manager:
        return {}
    return {name: data for name, data in unified.items()
            if data['pnl'].get('meta', {}).get('manager', '') == manager}


@router.get("/api/projects")
def get_projects(user: dict = Depends(get_current_user)):
    unified = _filter_projects(load_unified_projects(), user)
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
def get_pnl(project: str = Query(None), user: dict = Depends(get_current_user)):
    try:
        unified = _filter_projects(load_unified_projects(), user)
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
def get_pnl_summary(user: dict = Depends(get_current_user)):
    try:
        unified = _filter_projects(load_unified_projects(), user)
        return {"data": {name: data['pnl']['summary'] for name, data in unified.items()}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת סיכום P&L: {str(e)}")
