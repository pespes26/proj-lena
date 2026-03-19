import os
from openpyxl import load_workbook

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data.xlsx')

PROJECTS = {
    'מנרב סנטר': {'start_row': 6, 'end_row': 17, 'summary_row': 18},
    'קריית מנרב': {'start_row': 22, 'end_row': 33, 'summary_row': 34},
    'הדסה': {'start_row': 38, 'end_row': 49, 'summary_row': 50},
    'עמיגור באר שבע': {'start_row': 57, 'end_row': 68, 'summary_row': 69},
}

MONTH_TO_COL = {9: 5, 10: 7, 11: 9, 12: 11, 1: 13, 2: 15, 3: 17, 4: 19, 5: 21, 6: 23, 7: 25, 8: 27, 9: 29}

CASHFLOW_ROWS = {
    'קריית מנרב': 4,
    'מנרב סנטר': 5,
    'הדסה': 6,
    'עמיגור באר שבע': 7,
}

PROJECT_META = {
    'מנרב סנטר': {'manager': 'אתי', 'area': 'מסחרי פרטי', 'axis': 'FM', 'priority_id': 'P-1001'},
    'קריית מנרב': {'manager': 'אתי', 'area': 'מסחרי פרטי', 'axis': 'FM', 'priority_id': 'P-1002'},
    'הדסה': {'manager': 'אתי', 'area': 'מסחרי פרטי', 'axis': 'FM', 'priority_id': 'P-1003'},
    'עמיגור באר שבע': {'manager': 'אלון', 'area': 'פרוייקטים', 'axis': 'FM', 'priority_id': 'P-2001'},
}

# Monthly expense breakdown components per project (from Excel side columns)
EXPENSE_BREAKDOWN = {
    'מנרב סנטר': {
        'op_components': [
            {'name': 'ניקיון ותחזוקה', 'amount': 100},
        ],
        'salary_components': [
            {'name': 'שכר מנרב אחזקות', 'amount': 100},
            {'name': 'העמסת שכר עובד 1', 'amount': 16.67},
            {'name': 'העמסת שכר עובד 2', 'amount': 1.67},
        ],
    },
    'קריית מנרב': {
        'op_components': [
            {'name': 'ניקיון ותחזוקה', 'amount': 255},
            {'name': 'פער ספק ניקיון', 'amount': 45},
            {'name': 'הוצאות שוטפות', 'amount': 98.84},
        ],
        'salary_components': [
            {'name': 'שכר מנרב אחזקות', 'amount': 250},
            {'name': 'העמסת שכר עובד 1', 'amount': 16.67},
            {'name': 'העמסת שכר עובד 2', 'amount': 1.67},
        ],
    },
    'הדסה': {
        'op_components': [
            {'name': 'ניקיון ותחזוקה', 'amount': 100},
            {'name': 'הוצאות שוטפות', 'amount': 29.8},
        ],
        'salary_components': [
            {'name': 'שכר מנרב אחזקות', 'amount': 70},
            {'name': 'העמסת שכר עובד 1 (שליש)', 'amount': 16.67},
            {'name': 'העמסת שכר עובד 2', 'amount': 1.67},
        ],
    },
    'עמיגור באר שבע': {
        'op_components': [
            {'name': 'עבודות פנים', 'amount': None},
            {'name': 'עבודות חוץ', 'amount': None},
        ],
        'salary_components': [],
        'milestones': [
            {'name': 'פעימה 1', 'revenue': 70, 'expense': 0, 'month': 'פברואר'},
            {'name': 'פעימה 2', 'revenue': 150, 'expense': 0, 'month': 'פברואר'},
            {'name': 'פעימה 3', 'revenue': 450, 'expense': 540, 'month': 'מרץ'},
            {'name': 'פעימה 4', 'revenue': 336.36, 'expense': 302.73, 'month': 'מאי'},
        ],
    },
}


def _val(v):
    if v is None:
        return 0
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0


def load_pnl(project_name=None):
    wb = load_workbook(DATA_PATH, data_only=True)
    ws = wb['פרוייקטים מנרב IFM']
    result = {}

    targets = {project_name: PROJECTS[project_name]} if project_name else PROJECTS

    for name, info in targets.items():
        months = []
        for r in range(info['start_row'], info['end_row'] + 1):
            month_num = ws.cell(row=r, column=2).value
            revenue = _val(ws.cell(row=r, column=3).value)
            op_expenses = _val(ws.cell(row=r, column=4).value)
            gross_profit = _val(ws.cell(row=r, column=5).value)
            salary_expenses = _val(ws.cell(row=r, column=6).value)
            operating_profit = _val(ws.cell(row=r, column=7).value)
            notes = ws.cell(row=r, column=8).value or ''

            margin = round((operating_profit / revenue) * 100, 1) if revenue > 0 else None

            months.append({
                'month': int(month_num) if month_num else 0,
                'revenue': round(revenue, 2),
                'op_expenses': round(op_expenses, 2),
                'gross_profit': round(gross_profit, 2),
                'salary_expenses': round(salary_expenses, 2),
                'operating_profit': round(operating_profit, 2),
                'margin': margin,
                'margin_alert': margin is not None and margin < 20,
                'notes': str(notes),
            })

        sr = info['summary_row']
        summary = {
            'total_revenue': round(_val(ws.cell(row=sr, column=3).value), 2),
            'total_op_expenses': round(_val(ws.cell(row=sr, column=4).value), 2),
            'total_gross_profit': round(_val(ws.cell(row=sr, column=5).value), 2),
            'total_salary_expenses': round(_val(ws.cell(row=sr, column=6).value), 2),
            'total_operating_profit': round(_val(ws.cell(row=sr, column=7).value), 2),
        }
        total_rev = summary['total_revenue']
        summary['margin'] = round((summary['total_operating_profit'] / total_rev) * 100, 1) if total_rev > 0 else None

        meta = PROJECT_META.get(name, {})
        expense_breakdown = EXPENSE_BREAKDOWN.get(name, {})
        result[name] = {'months': months, 'summary': summary, 'meta': meta, 'expense_breakdown': expense_breakdown}

    wb.close()
    return result


def load_project_cashflow(project_name):
    wb = load_workbook(DATA_PATH, data_only=True)
    ws = wb['ריכוז']
    row_num = CASHFLOW_ROWS.get(project_name)
    if not row_num:
        wb.close()
        return None

    month_labels = ['9/2025', '10/2025', '11/2025', '12/2025',
                    '1/2026', '2/2026', '3/2026', '4/2026', '5/2026',
                    '6/2026', '7/2026', '8/2026', '9/2026']
    col_map = [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]

    data = []
    cumulative = 0
    for ci, col in enumerate(col_map):
        exp = _val(ws.cell(row=row_num, column=col).value)
        rev = _val(ws.cell(row=row_num, column=col + 1).value)
        net = rev - exp
        cumulative += net
        data.append({
            'month': month_labels[ci],
            'expenses': round(exp, 2),
            'revenue': round(rev, 2),
            'net': round(net, 2),
            'cumulative': round(cumulative, 2),
        })

    wb.close()
    return {'month_labels': month_labels, 'data': data}


def load_cashflow():
    wb = load_workbook(DATA_PATH, data_only=True)
    ws = wb['ריכוז']

    month_labels = ['9/2025', '10/2025', '11/2025', '12/2025',
                    '1/2026', '2/2026', '3/2026', '4/2026', '5/2026',
                    '6/2026', '7/2026', '8/2026', '9/2026']
    month_keys = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    # Column mapping: expense col, revenue col = col, col+1
    col_map = [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]

    projects = {}
    for pname, row_num in CASHFLOW_ROWS.items():
        data = []
        for ci, col in enumerate(col_map):
            exp = _val(ws.cell(row=row_num, column=col).value)
            rev = _val(ws.cell(row=row_num, column=col + 1).value)
            data.append({
                'month': month_labels[ci],
                'expenses': round(exp, 2),
                'revenue': round(rev, 2),
                'profit': round(rev - exp, 2),
            })
        projects[pname] = data

    # Totals row (12)
    totals_row = 12
    totals = []
    for ci, col in enumerate(col_map):
        exp = _val(ws.cell(row=totals_row, column=col).value)
        rev = _val(ws.cell(row=totals_row, column=col + 1).value)
        totals.append({
            'month': month_labels[ci],
            'expenses': round(exp, 2),
            'revenue': round(rev, 2),
        })

    # Monthly net (row 14)
    monthly_net = []
    for ci, col in enumerate(col_map):
        v = _val(ws.cell(row=14, column=col).value)
        monthly_net.append({'month': month_labels[ci], 'value': round(v, 2)})

    # Cumulative (row 15)
    cumulative = []
    for ci, col in enumerate(col_map):
        v = _val(ws.cell(row=15, column=col).value)
        cumulative.append({'month': month_labels[ci], 'value': round(v, 2)})

    wb.close()
    return {
        'month_labels': month_labels,
        'projects': projects,
        'totals': totals,
        'monthly_net': monthly_net,
        'cumulative': cumulative,
    }


def load_dashboard_kpis():
    pnl = load_pnl()
    total_revenue = sum(p['summary']['total_revenue'] for p in pnl.values())
    total_expenses = sum(p['summary']['total_op_expenses'] + p['summary']['total_salary_expenses'] for p in pnl.values())
    total_op_profit = sum(p['summary']['total_operating_profit'] for p in pnl.values())
    margin = round((total_op_profit / total_revenue) * 100, 1) if total_revenue > 0 else None

    cf = load_cashflow()
    cash_position = cf['cumulative'][-1]['value'] if cf['cumulative'] else 0

    return {
        'total_revenue': round(total_revenue, 2),
        'total_expenses': round(total_expenses, 2),
        'total_operating_profit': round(total_op_profit, 2),
        'margin': margin,
        'cash_position': round(cash_position, 2),
        'project_summaries': {name: data['summary'] for name, data in pnl.items()},
    }
