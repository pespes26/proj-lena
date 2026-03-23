import datetime as dt
from config import PROJECTS, PROJECT_META, EXPENSE_BREAKDOWN, PROJECTS_DATA_FILE
from storage import load_json, save_json
from services.excel_reader import load_pnl, load_cashflow
from services.form_calculator import form_to_pnl, form_to_cashflow


def load_form_data():
    return load_json(PROJECTS_DATA_FILE, {})


def save_form_data(data):
    save_json(PROJECTS_DATA_FILE, data)


def load_unified_projects():
    """Load all projects from both Excel and form. Form data takes priority."""
    form_data = load_form_data()

    result = {}

    for name, fdata in form_data.items():
        if name not in result:
            result[name] = {
                'pnl': form_to_pnl(fdata),
                'source': fdata.get('source', 'form'),
                'status': fdata.get('status', 'active'),
                'last_updated': fdata.get('last_updated', ''),
            }

    return result


def load_unified_dashboard():
    """Dashboard KPIs from all projects (unified)."""
    unified = load_unified_projects()

    total_revenue = 0
    total_expenses = 0
    total_op_profit = 0
    project_summaries = {}

    for name, data in unified.items():
        s = data['pnl']['summary']
        total_revenue += s.get('total_revenue', 0)
        total_expenses += s.get('total_op_expenses', 0) + s.get('total_salary_expenses', 0)
        total_op_profit += s.get('total_operating_profit', 0)
        project_summaries[name] = {
            **s,
            'meta': data['pnl'].get('meta', {}),
            'source': data['source'],
            'status': data['status'],
        }

    margin = round((total_op_profit / total_revenue) * 100, 1) if total_revenue > 0 else None

    try:
        cf = load_cashflow()
        cash_position = cf['cumulative'][-1]['value'] if cf['cumulative'] else 0
    except Exception:
        cash_position = 0

    return {
        'total_revenue': round(total_revenue, 2),
        'total_expenses': round(total_expenses, 2),
        'total_operating_profit': round(total_op_profit, 2),
        'margin': margin,
        'cash_position': round(cash_position, 2),
        'project_summaries': project_summaries,
    }


def import_excel_to_form(project_name):
    """Import an Excel project into form data structure."""
    if project_name not in PROJECTS:
        return None

    pnl = load_pnl(project_name)
    project_pnl = pnl[project_name]
    meta = PROJECT_META.get(project_name, {})
    breakdown = EXPENSE_BREAKDOWN.get(project_name, {})

    total_rev = project_pnl['summary']['total_revenue']
    revenue_forecast = {}
    for m_data in project_pnl['months']:
        m = m_data['month']
        revenue_forecast[str(m)] = round(m_data['revenue'] / total_rev * 100, 1) if total_rev > 0 else 0

    expense_lines_other = []
    for comp in breakdown.get('op_components', []):
        if comp.get('amount'):
            expense_lines_other.append({
                'name': comp['name'], 'monthly_amount': comp['amount'],
                'start_month': 1, 'end_month': 12,
            })

    expense_lines_manpower = []
    for comp in breakdown.get('salary_components', []):
        if comp.get('amount'):
            expense_lines_manpower.append({
                'name': comp['name'], 'monthly_amount': comp['amount'],
                'start_month': 1, 'end_month': 12,
            })

    actuals = {}
    for m_data in project_pnl['months']:
        m = m_data['month']
        actuals[str(m)] = {
            'revenue': m_data['revenue'],
            'op_expenses': m_data['op_expenses'],
            'salary_expenses': m_data['salary_expenses'],
            'notes': m_data.get('notes', ''),
        }

    form_data = {
        'project_name': project_name,
        'priority_id': meta.get('priority_id', ''),
        'start_date': '',
        'description': 'פרויקט מיובא מ-Excel',
        'manager': meta.get('manager', ''),
        'client': '',
        'area': meta.get('area', ''),
        'axis': meta.get('axis', ''),
        'total_revenue': total_rev,
        'revenue_payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
        'revenue_forecast': revenue_forecast,
        'total_budget': project_pnl['summary']['total_op_expenses'] + project_pnl['summary']['total_salary_expenses'],
        'subcontractors': [],
        'expense_lines_manpower': expense_lines_manpower,
        'expense_lines_equipment': [],
        'expense_lines_insurance': [],
        'expense_lines_consultants': [],
        'expense_lines_financing': [],
        'expense_lines_other': expense_lines_other,
        'actuals': actuals,
        'status': 'active',
        'source': 'excel-import',
        'last_updated': dt.datetime.now().isoformat(),
    }

    all_data = load_form_data()
    all_data[project_name] = form_data
    save_form_data(all_data)

    return form_data
