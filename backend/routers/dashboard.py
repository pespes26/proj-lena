from fastapi import APIRouter, HTTPException, Depends
from services.unified import load_unified_dashboard, load_unified_projects
from services.form_calculator import form_to_pnl
from services.unified import load_form_data
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


def _filtered_dashboard(user):
    """Build dashboard data, filtering for project_manager."""
    if user['role'] != 'project_manager':
        return load_unified_dashboard()

    # For project_manager: build custom dashboard with only their projects
    manager = user.get('linked_manager', '')
    form_data = load_form_data()

    total_revenue = 0
    total_expenses = 0
    total_op_profit = 0
    project_summaries = {}

    for name, fdata in form_data.items():
        if fdata.get('manager', '') != manager:
            continue
        pnl = form_to_pnl(fdata)
        s = pnl['summary']
        total_revenue += s.get('total_revenue', 0)
        total_expenses += s.get('total_op_expenses', 0) + s.get('total_salary_expenses', 0)
        total_op_profit += s.get('total_operating_profit', 0)
        project_summaries[name] = {
            **s,
            'meta': pnl.get('meta', {}),
            'source': 'form',
            'status': fdata.get('status', 'active'),
        }

    margin = round((total_op_profit / total_revenue) * 100, 1) if total_revenue > 0 else None

    return {
        'total_revenue': round(total_revenue, 2),
        'total_expenses': round(total_expenses, 2),
        'total_operating_profit': round(total_op_profit, 2),
        'margin': margin,
        'cash_position': 0,
        'project_summaries': project_summaries,
    }


@router.get("/api/dashboard")
def get_dashboard(user: dict = Depends(get_current_user)):
    try:
        return {"data": _filtered_dashboard(user)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בטעינת נתוני דשבורד: {str(e)}")
