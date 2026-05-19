import datetime as dt
from config import EXPENSE_CATEGORIES, MONTH_LABELS, CAL_MONTHS
from services.payment_terms import calc_revenue_for_month, _parse_month, _parse_year, shotef_payment_month, extract_shotef_days


def _calc_line_month_range(line):
    """Extract month range from an expense line, using dates if available, else month numbers."""
    line_sd = line.get('start_date', '')
    line_ed = line.get('end_date', '')
    if line_sd or line_ed:
        return _parse_month(line_sd, 1), _parse_month(line_ed, 12)
    return line.get('start_month', 1), line.get('end_month', 12)


def _expense_payment_month(work_month, work_year, payment_terms_str):
    """Calculate when an expense is actually PAID based on payment terms.

    - מקדמה: paid at project start
    - מזומן / empty: paid in the work month itself
    - שוטף+X: end of work month + X days
    """
    if not payment_terms_str or payment_terms_str in ('מזומן', 'מקדמה'):
        return work_month
    x_days = extract_shotef_days(payment_terms_str)
    if x_days == 0:
        return work_month
    pay_m, _pay_y = shotef_payment_month(work_month, work_year, x_days)
    return pay_m


def _calc_subcontractor_for_month(sub, target_month, base_year, project_start_month):
    """Calculate subcontractor expense paid in a given month.

    Subcontractor has:
    - total_amount OR monthly_amount (backward compat): total commitment
    - payment_terms: array [{type, percent}] OR string (backward compat)
    - start_date, end_date: when work happens
    """
    # Get total amount (support both total_amount and legacy monthly_amount)
    total_amount = sub.get('total_amount', 0) or 0
    if not total_amount:
        # Legacy: monthly_amount was actually used as total in old data
        total_amount = sub.get('monthly_amount', 0) or 0
    if not total_amount:
        return 0

    sub_sm = _parse_month(sub.get('start_date', ''), 1)
    sub_em = _parse_month(sub.get('end_date', ''), 12)

    payment_terms = sub.get('payment_terms', '')

    # New format: payment_terms is an array [{type, percent}, ...]
    if isinstance(payment_terms, list) and len(payment_terms) > 0:
        total = 0
        for term in payment_terms:
            term_pct = term.get('percent', 0) or 0
            if not term_pct:
                continue
            term_amount = total_amount * term_pct / 100
            term_type = term.get('type', '')

            if term_type == 'מקדמה':
                # Advance: paid at subcontractor start
                if target_month == sub_sm:
                    total += round(term_amount)
            elif term_type == 'מזומן':
                # Cash: spread evenly across work period
                work_months = max(1, sub_em - sub_sm + 1)
                monthly = term_amount / work_months
                if sub_sm <= target_month <= sub_em:
                    total += round(monthly)
            else:
                # שוטף+X: payment at end of work + delay
                x_days = extract_shotef_days(term_type)
                pay_m, _pay_y = shotef_payment_month(sub_em, base_year, x_days)
                if target_month == pay_m:
                    total += round(term_amount)
        return total

    # Legacy format: payment_terms is a single string, monthly_amount per month
    elif isinstance(payment_terms, str):
        monthly_amount = sub.get('monthly_amount', 0) or 0
        if not monthly_amount:
            return 0
        for work_m in range(sub_sm, sub_em + 1):
            work_year = base_year if work_m >= project_start_month else base_year + 1
            pay_m = _expense_payment_month(work_m, work_year, payment_terms)
            if pay_m == target_month:
                return monthly_amount
        return 0

    return 0


def _calc_expenses_for_month(form_data, target_month):
    """Calculate total operational expenses PAID in a given month, respecting payment terms."""
    op_expenses = 0

    start_date = form_data.get('start_date', '')
    base_year = _parse_year(start_date, 2026)
    project_start_month = _parse_month(start_date, 1)

    # Expense lines (suppliers)
    for cat in EXPENSE_CATEGORIES:
        for line in form_data.get(f'expense_lines_{cat}', []):
            line_sm, line_em = _calc_line_month_range(line)
            line_payment_terms = line.get('payment_terms', '')
            monthly_amount = line.get('monthly_amount', 0) or 0
            if not monthly_amount:
                continue

            for work_m in range(line_sm, line_em + 1):
                work_year = base_year if work_m >= project_start_month else base_year + 1
                pay_m = _expense_payment_month(work_m, work_year, line_payment_terms)
                if pay_m == target_month:
                    op_expenses += monthly_amount

    # Subcontractors
    for sub in form_data.get('subcontractors', []):
        op_expenses += _calc_subcontractor_for_month(sub, target_month, base_year, project_start_month)

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
            'is_actual': bool(has_actual) and m <= current_month,
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

    axis = form_data.get('axis', '')
    area = form_data.get('area', '')
    meta = {
        'manager': form_data.get('manager', ''),
        'area': area,
        'axis': axis,
        'axis_area': f"{axis} - {area}" if axis and area else axis or area,
        'priority_id': form_data.get('priority_id', ''),
        'start_month': _parse_month(form_data.get('start_date', ''), 1),
        'end_month': _parse_month(form_data.get('expected_end_date', ''), 12),
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
