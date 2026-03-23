import calendar
from datetime import date, timedelta


def extract_shotef_days(term_type):
    """Extract X days from שוטף+X term type string."""
    if not term_type:
        return 0
    if 'שוטף+90' in term_type:
        return 90
    if 'שוטף+75' in term_type:
        return 75
    if 'שוטף+60' in term_type:
        return 60
    if 'שוטף+45' in term_type:
        return 45
    if 'שוטף+30' in term_type:
        return 30
    if 'שוטף+0' in term_type or term_type == 'שוטף':
        return 0
    return 0


def shotef_payment_month(invoice_month, invoice_year, x_days):
    """Calculate which month payment lands in for שוטף+X.

    Logic:
    1. Go to end of invoice month (ignore exact invoice day)
    2. Add X days
    3. Return (month, year) of payment date
    """
    last_day = calendar.monthrange(invoice_year, invoice_month)[1]
    end_of_month = date(invoice_year, invoice_month, last_day)
    payment_date = end_of_month + timedelta(days=x_days)
    return payment_date.month, payment_date.year


def calc_revenue_for_month(form_data, target_cal_month):
    """Calculate revenue arriving in a specific calendar month based on payment terms.

    - מקדמה (advance): all at project start month
    - מזומן (cash): spread evenly across project duration
    - שוטף+X: invoices issued monthly, payment = end of invoice month + X days
    """
    total_revenue = form_data.get('total_revenue', 0) or 0
    if not total_revenue:
        return 0

    payment_terms = form_data.get('revenue_payment_terms', [])
    if not payment_terms:
        payment_terms = [{'type': 'מזומן', 'percent': 100}]

    start_date = form_data.get('start_date', '')
    end_date = form_data.get('expected_end_date', '')
    start_month = _parse_month(start_date, 1)
    start_year = _parse_year(start_date, 2026)
    end_month = _parse_month(end_date, 12)

    project_months = max(1, end_month - start_month + 1)

    total = 0
    for term in payment_terms:
        term_pct = term.get('percent', 0) or 0
        if not term_pct:
            continue
        term_amount = total_revenue * term_pct / 100
        term_type = term.get('type', '')

        if term_type == 'מקדמה':
            # Advance: all at project start month
            if target_cal_month == start_month:
                total += round(term_amount)

        elif term_type == 'פעימות תשלום':
            # Milestones handled separately
            pass

        else:
            # שוטף+X: invoice issued at project END, payment = end of end_month + X days
            x_days = extract_shotef_days(term_type)
            inv_year = start_year if end_month >= start_month else start_year + 1
            pay_month, _pay_year = shotef_payment_month(end_month, inv_year, x_days)
            if pay_month == target_cal_month:
                total += round(term_amount)

    return total


def _parse_month(date_str, default):
    """Extract month number from yyyy-mm-dd string."""
    if not date_str:
        return default
    parts = date_str.split('-')
    if len(parts) >= 2:
        try:
            return int(parts[1])
        except ValueError:
            return default
    return default


def _parse_year(date_str, default):
    """Extract year from yyyy-mm-dd string."""
    if not date_str:
        return default
    parts = date_str.split('-')
    if len(parts) >= 1:
        try:
            return int(parts[0])
        except ValueError:
            return default
    return default
