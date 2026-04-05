import copy
import datetime as dt
from services.unified import load_form_data
from services.form_calculator import form_to_pnl, form_to_cashflow
from services.payment_terms import extract_shotef_days, _parse_month


def run_whatif(project_name, modifications):
    """Run What-If simulation on a project."""
    all_data = load_form_data()
    if project_name not in all_data:
        return None

    original_data = all_data[project_name]
    modified_data = copy.deepcopy(original_data)

    if 'revenue_change_pct' in modifications:
        pct = modifications['revenue_change_pct']
        orig_rev = modified_data.get('total_revenue', 0) or 0
        modified_data['total_revenue'] = round(orig_rev * (1 + pct / 100))

    if 'expense_change_pct' in modifications:
        pct = modifications['expense_change_pct']
        for cat in ['manpower', 'equipment', 'insurance', 'consultants', 'financing', 'other']:
            for line in modified_data.get(f'expense_lines_{cat}', []):
                if line.get('monthly_amount'):
                    line['monthly_amount'] = round(line['monthly_amount'] * (1 + pct / 100))
        for sub in modified_data.get('subcontractors', []):
            if sub.get('total_amount'):
                sub['total_amount'] = round(sub['total_amount'] * (1 + pct / 100))
            if sub.get('monthly_amount'):
                sub['monthly_amount'] = round(sub['monthly_amount'] * (1 + pct / 100))

    if 'extend_months' in modifications:
        ext = modifications['extend_months']
        end_date = modified_data.get('expected_end_date', '')
        if end_date:
            parts = end_date.split('-')
            if len(parts) >= 2:
                y, m = int(parts[0]), int(parts[1])
                m += ext
                while m > 12:
                    m -= 12
                    y += 1
                d = parts[2] if len(parts) >= 3 else '01'
                modified_data['expected_end_date'] = f"{y}-{m:02d}-{d}"

    if 'remove_subcontractor' in modifications:
        name = modifications['remove_subcontractor']
        modified_data['subcontractors'] = [
            s for s in modified_data.get('subcontractors', [])
            if s.get('name', '') != name
        ]

    original_pnl = form_to_pnl(original_data)
    simulated_pnl = form_to_pnl(modified_data)

    os_ = original_pnl['summary']
    ss = simulated_pnl['summary']

    return {
        'original': {'summary': os_, 'months': original_pnl['months']},
        'simulated': {'summary': ss, 'months': simulated_pnl['months']},
        'diff': {
            'revenue_change': round(ss['total_revenue'] - os_['total_revenue'], 2),
            'expense_change': round(ss['total_op_expenses'] - os_['total_op_expenses'], 2),
            'profit_change': round(ss['total_operating_profit'] - os_['total_operating_profit'], 2),
            'margin_change': round((ss['margin'] or 0) - (os_['margin'] or 0), 1),
        }
    }


def calc_risk_score(project_name):
    """Calculate risk score 0-100."""
    all_data = load_form_data()
    if project_name not in all_data:
        return None

    fdata = all_data[project_name]
    pnl = form_to_pnl(fdata)
    summary = pnl['summary']
    factors = []

    # Factor 1: Margin risk (0-20)
    margin = summary.get('margin') or 0
    if margin >= 25:
        score1 = 0
    elif margin >= 20:
        score1 = 5
    elif margin >= 10:
        score1 = 12
    elif margin >= 0:
        score1 = 16
    else:
        score1 = 20
    factors.append({'name': 'margin_risk', 'label': 'סיכון מרג\'ין', 'score': score1,
                    'detail': f'מרג\'ין: {margin}%'})

    # Factor 2: Revenue concentration (0-20)
    terms = fdata.get('revenue_payment_terms', [])
    max_pct = max((t.get('percent', 0) for t in terms), default=0) if terms else 100
    if max_pct >= 80:
        score2 = 18
    elif max_pct >= 60:
        score2 = 12
    elif max_pct >= 40:
        score2 = 6
    else:
        score2 = 0
    factors.append({'name': 'revenue_concentration', 'label': 'ריכוז הכנסות', 'score': score2,
                    'detail': f'תנאי תשלום מקסימלי: {max_pct}%'})

    # Factor 3: Subcontractor concentration (0-20)
    subs = fdata.get('subcontractors', [])
    total_sub = sum(s.get('total_amount', s.get('monthly_amount', 0)) or 0 for s in subs)
    max_sub = max((s.get('total_amount', s.get('monthly_amount', 0)) or 0 for s in subs), default=0)
    sub_pct = (max_sub / total_sub * 100) if total_sub > 0 else 0
    if sub_pct >= 70:
        score3 = 16
    elif sub_pct >= 50:
        score3 = 10
    elif sub_pct >= 30:
        score3 = 4
    else:
        score3 = 0
    factors.append({'name': 'sub_concentration', 'label': 'ריכוז קבלנים', 'score': score3,
                    'detail': f'קבלן מרכזי: {sub_pct:.0f}% מההוצאות'})

    # Factor 4: Payment exposure (0-20)
    avg_days = 0
    if terms:
        total_weighted = 0
        for t in terms:
            days = extract_shotef_days(t.get('type', ''))
            total_weighted += days * (t.get('percent', 0) / 100)
        avg_days = total_weighted
    if avg_days >= 75:
        score4 = 18
    elif avg_days >= 45:
        score4 = 12
    elif avg_days >= 30:
        score4 = 6
    else:
        score4 = 0
    factors.append({'name': 'payment_exposure', 'label': 'חשיפת תשלום', 'score': score4,
                    'detail': f'ממוצע שוטף: {avg_days:.0f} ימים'})

    # Factor 5: Cash gap (0-20)
    cf = form_to_cashflow(fdata)
    negative_months = sum(1 for d in cf['data'] if d.get('cumulative', 0) < 0)
    if negative_months >= 4:
        score5 = 20
    elif negative_months >= 2:
        score5 = 12
    elif negative_months >= 1:
        score5 = 6
    else:
        score5 = 0
    factors.append({'name': 'cash_gap', 'label': 'פער תזרימי', 'score': score5,
                    'detail': f'{negative_months} חודשים שליליים'})

    total = sum(f['score'] for f in factors)
    if total <= 25:
        level = 'low'
    elif total <= 50:
        level = 'medium'
    elif total <= 75:
        level = 'high'
    else:
        level = 'critical'

    return {'score': total, 'level': level, 'factors': factors}


def calc_all_risk_scores():
    all_data = load_form_data()
    return {name: calc_risk_score(name) for name in all_data}


def calc_budget_vs_actual(project_name):
    all_data = load_form_data()
    if project_name not in all_data:
        return None

    fdata = all_data[project_name]
    pnl = form_to_pnl(fdata)
    actuals = fdata.get('actuals', {})

    months = []
    for m_data in pnl['months']:
        m = m_data['month']
        actual = actuals.get(str(m), {})
        months.append({
            'month': m,
            'planned_revenue': m_data['revenue'],
            'planned_expenses': m_data['op_expenses'],
            'actual_revenue': actual.get('revenue', 0),
            'actual_expenses': actual.get('op_expenses', 0),
            'revenue_variance': round(actual.get('revenue', 0) - m_data['revenue'], 2) if actual else None,
            'expense_variance': round(actual.get('op_expenses', 0) - m_data['op_expenses'], 2) if actual else None,
            'has_actual': bool(actual),
        })

    total_planned_rev = pnl['summary']['total_revenue']
    total_actual_rev = sum(actuals.get(str(m), {}).get('revenue', 0) for m in range(1, 13))
    total_planned_exp = pnl['summary']['total_op_expenses']
    total_actual_exp = sum(actuals.get(str(m), {}).get('op_expenses', 0) for m in range(1, 13))

    start_m = _parse_month(fdata.get('start_date', ''), 1)
    end_m = _parse_month(fdata.get('expected_end_date', ''), 12)
    current_m = dt.datetime.now().month
    total_months = max(1, end_m - start_m + 1)
    elapsed = max(0, min(current_m - start_m + 1, total_months))
    completion_pct = round(elapsed / total_months * 100)
    burn_pct = round(total_actual_exp / total_planned_exp * 100) if total_planned_exp > 0 else 0

    return {
        'months': months,
        'total_planned_revenue': total_planned_rev,
        'total_actual_revenue': total_actual_rev,
        'total_planned_expenses': total_planned_exp,
        'total_actual_expenses': total_actual_exp,
        'completion_pct': completion_pct,
        'burn_rate_pct': burn_pct,
        'on_track': burn_pct <= completion_pct + 10,
    }
