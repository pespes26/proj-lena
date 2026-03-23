import datetime as dt
from config import EXPENSE_CATEGORIES, MONTH_LABELS, CAL_MONTHS
from services.payment_terms import calc_revenue_for_month, _parse_month


def _calc_line_month_range(line):
    """Extract month range from an expense line, using dates if available, else month numbers."""
    line_sd = line.get('start_date', '')
    line_ed = line.get('end_date', '')
    if line_sd or line_ed:
        return _parse_month(line_sd, 1), _parse_month(line_ed, 12)
    return line.get('start_month', 1), line.get('end_month', 12)


def _calc_expenses_for_month(form_data, m):
    """Calculate total operational expenses for a given month."""
    op_expenses = 0

    for cat in EXPENSE_CATEGORIES:
        for line in form_data.get(f'expense_lines_{cat}', []):
            line_sm, line_em = _calc_line_month_range(line)
            if line_sm <= m <= line_em:
                op_expenses += line.get('monthly_amount', 0) or 0

    for sub in form_data.get('subcontractors', []):
        sub_sm = _parse_month(sub.get('start_date', ''), 1)
        sub_em = _parse_month(sub.get('end_date', ''), 12)
        if sub_sm <= m <= sub_em:
            op_expenses += sub.get('monthly_amount', 0) or 0

    return op_expenses


def form_to_pnl(form_data, current_month=None):
    """Convert form data to P&L format. Uses actuals for past months, forecast for future."""
    if current_month is None:
        current_month = dt.datetime.now().month

    actuals = form_data.get('actuals', {})
    months = []

    for m in range(1, 13):
        actual = actuals.get(str(m), {})
        has_actual = actual and (actual.get('revenue', 0) > 0 or actual.get('op_expenses', 0) > 0)

        if has_actual and m <= current_month:
            revenue = actual.get('revenue', 0)
            op_expenses = actual.get('op_expenses', 0)
            salary_expenses = actual.get('salary_expenses', 0)
        else:
            revenue = calc_revenue_for_month(form_data, m)
            op_expenses = _calc_expenses_for_month(form_data, m)
            salary_expenses = 0

        operating_profit = revenue - op_expenses - salary_expenses
        margin = round((operating_profit / revenue) * 100, 1) if revenue > 0 else None

        months.append({
            'month': m,
            'revenue': round(revenue, 2),
            'op_expenses': round(op_expenses, 2),
            'gross_profit': round(revenue - op_expenses, 2),
            'salary_expenses': round(salary_expenses, 2),
            'operating_profit': round(operating_profit, 2),
            'margin': margin,
            'margin_alert': margin is not None and margin < 20,
            'notes': actual.get('notes', ''),
            'is_actual': has_actual and m <= current_month,
        })

    total_rev = sum(m['revenue'] for m in months)
    total_op = sum(m['op_expenses'] for m in months)
    total_sal = sum(m['salary_expenses'] for m in months)
    total_profit = total_rev - total_op - total_sal

    summary = {
        'total_revenue': round(total_rev, 2),
        'total_op_expenses': round(total_op, 2),
        'total_gross_profit': round(total_rev - total_op, 2),
        'total_salary_expenses': round(total_sal, 2),
        'total_operating_profit': round(total_profit, 2),
        'margin': round((total_profit / total_rev) * 100, 1) if total_rev > 0 else None,
    }

    meta = {
        'manager': form_data.get('manager', ''),
        'area': form_data.get('area', ''),
        'axis': form_data.get('axis', ''),
        'priority_id': form_data.get('priority_id', ''),
    }

    return {'months': months, 'summary': summary, 'meta': meta, 'expense_breakdown': {}}


def form_to_cashflow(form_data):
    """Compute cashflow from form data including payment term delays."""
    actuals = form_data.get('actuals', {})
    data = []
    cumulative = 0

    for ci, cal_m in enumerate(CAL_MONTHS):
        actual = actuals.get(str(cal_m), {})
        has_actual = actual and (actual.get('revenue', 0) > 0 or actual.get('op_expenses', 0) > 0)

        if has_actual:
            rev = actual.get('revenue', 0)
            exp = actual.get('op_expenses', 0) + actual.get('salary_expenses', 0)
        else:
            rev = calc_revenue_for_month(form_data, cal_m)
            exp = _calc_expenses_for_month(form_data, cal_m)

        net = rev - exp
        cumulative += net
        data.append({
            'month': MONTH_LABELS[ci],
            'expenses': round(exp, 2),
            'revenue': round(rev, 2),
            'net': round(net, 2),
            'cumulative': round(cumulative, 2),
        })

    return {'month_labels': MONTH_LABELS, 'data': data}
