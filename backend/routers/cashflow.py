from fastapi import APIRouter, Query, HTTPException, Depends
from config import MONTH_LABELS
from services.form_calculator import form_to_cashflow
from services.unified import load_form_data
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


def _get_form_projects(user):
    """Get form projects filtered by user role."""
    form_projects = load_form_data()
    if user['role'] == 'project_manager':
        manager = user.get('linked_manager', '')
        return {name: fdata for name, fdata in form_projects.items()
                if fdata.get('manager', '') == manager}
    return form_projects


@router.get("/api/cashflow")
def get_cashflow(user: dict = Depends(get_current_user)):
    """Unified cashflow from all form-based projects."""
    try:
        form_projects = _get_form_projects(user)
        if not form_projects:
            return {"data": _empty_cashflow()}

        all_projects = {}
        for name, fdata in form_projects.items():
            cf = form_to_cashflow(fdata)
            all_projects[name] = cf['data']

        num_months = len(MONTH_LABELS)
        totals = []
        monthly_net = []
        cumulative = []
        cum = 0

        for i in range(num_months):
            total_rev = 0
            total_exp = 0
            for pname, pdata in all_projects.items():
                if i < len(pdata):
                    total_rev += pdata[i].get('revenue', 0)
                    total_exp += pdata[i].get('expenses', 0)
            net = total_rev - total_exp
            cum += net
            totals.append({'month': MONTH_LABELS[i], 'revenue': round(total_rev, 2), 'expenses': round(total_exp, 2)})
            monthly_net.append({'month': MONTH_LABELS[i], 'value': round(net, 2)})
            cumulative.append({'month': MONTH_LABELS[i], 'value': round(cum, 2)})

        projects_out = {}
        for pname, pdata in all_projects.items():
            projects_out[pname] = [{
                'month': entry['month'],
                'revenue': entry['revenue'],
                'expenses': entry['expenses'],
                'profit': round(entry['revenue'] - entry['expenses'], 2),
            } for entry in pdata]

        return {"data": {
            'month_labels': MONTH_LABELS,
            'projects': projects_out,
            'totals': totals,
            'monthly_net': monthly_net,
            'cumulative': cumulative,
        }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת תזרים מזומנים: {str(e)}")


@router.get("/api/project-cashflow")
def get_project_cashflow(project: str = Query(...), user: dict = Depends(get_current_user)):
    try:
        form_projects = _get_form_projects(user)
        if project in form_projects:
            return {"data": form_to_cashflow(form_projects[project])}
        raise HTTPException(status_code=404, detail=f"פרויקט '{project}' לא נמצא")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת תזרים פרויקט: {str(e)}")


def _empty_cashflow():
    return {
        'month_labels': MONTH_LABELS,
        'projects': {},
        'totals': [{'month': m, 'revenue': 0, 'expenses': 0} for m in MONTH_LABELS],
        'monthly_net': [{'month': m, 'value': 0} for m in MONTH_LABELS],
        'cumulative': [{'month': m, 'value': 0} for m in MONTH_LABELS],
    }
