"""Create 10 realistic test projects in Firestore."""
import datetime as dt
from storage import save_project_firestore

NOW = dt.datetime.now().isoformat()

def empty_actuals():
    return {str(i): {'revenue': 0, 'op_expenses': 0, 'salary_expenses': 0, 'notes': ''} for i in range(1, 13)}

def actuals_with_data(months_data):
    a = empty_actuals()
    for m, data in months_data.items():
        a[str(m)] = data
    return a

PROJECTS = [
    # 1. מגדלי חיפה — לוגי, מסחרי פרטי, אלון, ~25% margin
    {
        'project_name': 'מגדלי חיפה',
        'priority_id': 'P-2001',
        'start_date': '2026-01-15',
        'expected_end_date': '2026-08-30',
        'manager': 'אלון',
        'client': 'מגדלי חיפה בע"מ',
        'description': 'ניהול ותחזוקת מגדלי משרדים וחניונים בחיפה',
        'axis': 'לוגי',
        'area': 'מסחרי פרטי',
        'status': 'active',
        'total_revenue': 2500000,
        'revenue_payment_terms': [
            {'type': 'מקדמה', 'percent': 20},
            {'type': 'שוטף+30', 'percent': 50},
            {'type': 'שוטף+60', 'percent': 30},
        ],
        'subcontractors': [
            {'name': 'אורי חשמל', 'total_amount': 280000, 'start_date': '2026-02-01', 'end_date': '2026-07-31',
             'payment_terms': [{'type': 'מקדמה', 'percent': 15}, {'type': 'שוטף+30', 'percent': 85}],
             'contact_name': 'אורי כהן', 'contact_phone': '050-1111111', 'business_id': '515000001'},
            {'name': 'גל אינסטלציה', 'total_amount': 195000, 'start_date': '2026-02-15', 'end_date': '2026-06-30',
             'payment_terms': [{'type': 'שוטף+45', 'percent': 100}],
             'contact_name': 'גל לוי', 'contact_phone': '052-2222222', 'business_id': '515000002'},
            {'name': 'דני איטום', 'total_amount': 120000, 'start_date': '2026-03-01', 'end_date': '2026-05-31',
             'payment_terms': [{'type': 'מקדמה', 'percent': 30}, {'type': 'שוטף+60', 'percent': 70}],
             'contact_name': 'דני אברהם', 'contact_phone': '054-3333333', 'business_id': '515000003'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל אתר', 'monthly_amount': 22000, 'start_date': '2026-01-15', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל פרויקט', 'monthly_amount': 18000, 'start_date': '2026-01-15', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
            {'name': 'עובדי שטח (4)', 'monthly_amount': 48000, 'start_date': '2026-02-01', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל בטיחות', 'monthly_amount': 8000, 'start_date': '2026-02-01', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'שכירת עגורן', 'monthly_amount': 35000, 'start_date': '2026-02-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+30'},
            {'name': 'פיגומים', 'monthly_amount': 12000, 'start_date': '2026-03-01', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+30'},
            {'name': 'ציוד בדיקות', 'monthly_amount': 3500, 'start_date': '2026-01-15', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח קבלנים', 'monthly_amount': 45000, 'start_date': '2026-08-30', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
            {'name': 'ביטוח צד ג', 'monthly_amount': 18000, 'start_date': '2026-08-30', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [
            {'name': 'יועץ קונסטרוקציה', 'monthly_amount': 15000, 'start_date': '2026-01-15', 'end_date': '2026-03-31', 'payment_terms': 'שוטף+30'},
            {'name': 'יועץ בטיחות', 'monthly_amount': 6000, 'start_date': '2026-02-01', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_financing': [
            {'name': 'ערבות בנקאית', 'monthly_amount': 5000, 'start_date': '2026-01-15', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_other': [
            {'name': 'הסעות עובדים', 'monthly_amount': 4500, 'start_date': '2026-02-01', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
            {'name': 'משרד שטח', 'monthly_amount': 3000, 'start_date': '2026-01-15', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
            {'name': 'ניקיון אתר', 'monthly_amount': 2500, 'start_date': '2026-02-01', 'end_date': '2026-08-30', 'payment_terms': 'שוטף+0'},
        ],
        'actuals': actuals_with_data({
            1: {'revenue': 500000, 'op_expenses': 85000, 'salary_expenses': 0, 'notes': 'קבלת מקדמה'},
            2: {'revenue': 0, 'op_expenses': 195000, 'salary_expenses': 0, 'notes': 'תחילת עבודות'},
            3: {'revenue': 0, 'op_expenses': 210000, 'salary_expenses': 0, 'notes': 'עבודות איטום'},
        }),
    },

    # 2. קניון הנגב — לוגי, פרוייקטים, אתי, ~30% margin
    {
        'project_name': 'קניון הנגב',
        'priority_id': 'P-2002',
        'start_date': '2026-02-01',
        'expected_end_date': '2026-06-30',
        'manager': 'אתי',
        'client': 'קניון הנגב ניהול',
        'description': 'שיפוץ והרחבת קניון הנגב באר שבע',
        'axis': 'לוגי',
        'area': 'פרוייקטים',
        'status': 'active',
        'total_revenue': 800000,
        'revenue_payment_terms': [
            {'type': 'מקדמה', 'percent': 30},
            {'type': 'שוטף+30', 'percent': 70},
        ],
        'subcontractors': [
            {'name': 'משה ריצוף', 'total_amount': 85000, 'start_date': '2026-03-01', 'end_date': '2026-05-31',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'משה דוד', 'contact_phone': '050-4444444', 'business_id': '515000004'},
            {'name': 'יוסי צבע', 'total_amount': 55000, 'start_date': '2026-04-01', 'end_date': '2026-06-15',
             'payment_terms': [{'type': 'מקדמה', 'percent': 20}, {'type': 'שוטף+30', 'percent': 80}],
             'contact_name': 'יוסי חן', 'contact_phone': '052-5555555', 'business_id': '515000005'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל פרויקט', 'monthly_amount': 16000, 'start_date': '2026-02-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+0'},
            {'name': 'צוות אחזקה (3)', 'monthly_amount': 36000, 'start_date': '2026-02-15', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'ציוד ניקיון תעשייתי', 'monthly_amount': 4000, 'start_date': '2026-02-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+30'},
            {'name': 'שכירת מלגזה', 'monthly_amount': 6000, 'start_date': '2026-03-01', 'end_date': '2026-05-31', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח מבנה', 'monthly_amount': 15000, 'start_date': '2026-06-30', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [
            {'name': 'מודד', 'monthly_amount': 8000, 'start_date': '2026-02-01', 'end_date': '2026-02-28', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_financing': [],
        'expense_lines_other': [
            {'name': 'שילוט זמני', 'monthly_amount': 2000, 'start_date': '2026-02-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+0'},
            {'name': 'אבטחת אתר', 'monthly_amount': 5000, 'start_date': '2026-02-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+0'},
        ],
        'actuals': actuals_with_data({
            2: {'revenue': 240000, 'op_expenses': 42000, 'salary_expenses': 0, 'notes': 'קבלת מקדמה'},
            3: {'revenue': 0, 'op_expenses': 78000, 'salary_expenses': 0, 'notes': 'תחילת ריצוף'},
        }),
    },

    # 3. מתחם הרצליה — מנרב, מסחרי פרטי, אריאל, ~18% margin (risk)
    {
        'project_name': 'מתחם הרצליה',
        'priority_id': 'P-3001',
        'start_date': '2026-03-01',
        'expected_end_date': '2026-09-30',
        'manager': 'אריאל',
        'client': 'הרצליה נדל"ן',
        'description': 'בניית מתחם מסחרי חדש בהרצליה פיתוח',
        'axis': 'מנרב',
        'area': 'מסחרי פרטי',
        'status': 'active',
        'total_revenue': 1500000,
        'revenue_payment_terms': [
            {'type': 'מקדמה', 'percent': 10},
            {'type': 'שוטף+60', 'percent': 60},
            {'type': 'שוטף+90', 'percent': 30},
        ],
        'subcontractors': [
            {'name': 'רון בנייה', 'total_amount': 350000, 'start_date': '2026-03-15', 'end_date': '2026-08-31',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'רון אשכנזי', 'contact_phone': '050-6666666', 'business_id': '515000006'},
            {'name': 'שלמה מיזוג', 'total_amount': 220000, 'start_date': '2026-05-01', 'end_date': '2026-09-15',
             'payment_terms': [{'type': 'מקדמה', 'percent': 10}, {'type': 'שוטף+45', 'percent': 90}],
             'contact_name': 'שלמה עזרא', 'contact_phone': '054-7777777', 'business_id': '515000007'},
            {'name': 'אבי חשמל תעשייתי', 'total_amount': 180000, 'start_date': '2026-04-01', 'end_date': '2026-08-31',
             'payment_terms': [{'type': 'שוטף+60', 'percent': 100}],
             'contact_name': 'אבי מזרחי', 'contact_phone': '052-8888888', 'business_id': '515000008'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל אתר בכיר', 'monthly_amount': 25000, 'start_date': '2026-03-01', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל פרויקט', 'monthly_amount': 20000, 'start_date': '2026-03-01', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
            {'name': 'עובדי שטח (6)', 'monthly_amount': 72000, 'start_date': '2026-03-15', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל בטיחות', 'monthly_amount': 10000, 'start_date': '2026-03-01', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'שכירת עגורן צריח', 'monthly_amount': 45000, 'start_date': '2026-04-01', 'end_date': '2026-08-31', 'payment_terms': 'שוטף+30'},
            {'name': 'משאבת בטון', 'monthly_amount': 15000, 'start_date': '2026-04-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+30'},
            {'name': 'מחפרון', 'monthly_amount': 8000, 'start_date': '2026-03-01', 'end_date': '2026-05-31', 'payment_terms': 'שוטף+30'},
            {'name': 'גנרטור', 'monthly_amount': 3500, 'start_date': '2026-03-01', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח קבלנים', 'monthly_amount': 35000, 'start_date': '2026-09-30', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
            {'name': 'ביטוח צד ג', 'monthly_amount': 12000, 'start_date': '2026-09-30', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
            {'name': 'ביטוח עובדים', 'monthly_amount': 8000, 'start_date': '2026-09-30', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [
            {'name': 'יועץ קונסטרוקציה', 'monthly_amount': 18000, 'start_date': '2026-03-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+30'},
            {'name': 'יועץ חשמל', 'monthly_amount': 8000, 'start_date': '2026-04-01', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+30'},
            {'name': 'שמאי', 'monthly_amount': 12000, 'start_date': '2026-03-01', 'end_date': '2026-03-31', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_financing': [
            {'name': 'ערבות ביצוע', 'monthly_amount': 8000, 'start_date': '2026-03-01', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
            {'name': 'עמלת אשראי', 'monthly_amount': 3000, 'start_date': '2026-03-01', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_other': [
            {'name': 'הסעות', 'monthly_amount': 6000, 'start_date': '2026-03-15', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
            {'name': 'משרד שטח', 'monthly_amount': 4500, 'start_date': '2026-03-01', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
            {'name': 'ניקיון', 'monthly_amount': 3000, 'start_date': '2026-03-15', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
            {'name': 'שילוט ובטיחות', 'monthly_amount': 2000, 'start_date': '2026-03-01', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+0'},
        ],
        'actuals': actuals_with_data({
            3: {'revenue': 150000, 'op_expenses': 145000, 'salary_expenses': 0, 'notes': 'מקדמה + תחילת עבודות'},
        }),
    },

    # 4. בית חולים שיבא — מנרב, פרוייקטים, אלון, ~22% margin
    {
        'project_name': 'בית חולים שיבא',
        'priority_id': 'P-3002',
        'start_date': '2026-01-01',
        'expected_end_date': '2026-12-31',
        'manager': 'אלון',
        'client': 'שיבא תל השומר',
        'description': 'תחזוקה שנתית של מערכות מבנה בבית חולים שיבא',
        'axis': 'מנרב',
        'area': 'פרוייקטים',
        'status': 'active',
        'total_revenue': 3200000,
        'revenue_payment_terms': [
            {'type': 'שוטף+30', 'percent': 100},
        ],
        'subcontractors': [
            {'name': 'טכנו מעליות', 'total_amount': 420000, 'start_date': '2026-01-01', 'end_date': '2026-12-31',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'חיים טכנו', 'contact_phone': '050-9999999', 'business_id': '515000009'},
            {'name': 'מגן אש', 'total_amount': 280000, 'start_date': '2026-01-01', 'end_date': '2026-12-31',
             'payment_terms': [{'type': 'שוטף+45', 'percent': 100}],
             'contact_name': 'יעקב מגן', 'contact_phone': '052-1010101', 'business_id': '515000010'},
            {'name': 'קלין ניקיון רפואי', 'total_amount': 360000, 'start_date': '2026-01-01', 'end_date': '2026-12-31',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'רחל קלין', 'contact_phone': '054-1111112', 'business_id': '515000011'},
            {'name': 'חום קור מיזוג', 'total_amount': 310000, 'start_date': '2026-03-01', 'end_date': '2026-11-30',
             'payment_terms': [{'type': 'מקדמה', 'percent': 10}, {'type': 'שוטף+60', 'percent': 90}],
             'contact_name': 'עמוס חום', 'contact_phone': '050-1212121', 'business_id': '515000012'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל פרויקט בכיר', 'monthly_amount': 28000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
            {'name': 'צוות אחזקה (8)', 'monthly_amount': 96000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל בטיחות', 'monthly_amount': 12000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'ציוד בדיקות חשמל', 'monthly_amount': 5000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+30'},
            {'name': 'ציוד אינסטלציה', 'monthly_amount': 4000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח קבלנים', 'monthly_amount': 65000, 'start_date': '2026-12-31', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
            {'name': 'ביטוח עובדים', 'monthly_amount': 25000, 'start_date': '2026-12-31', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [
            {'name': 'יועץ בטיחות אש', 'monthly_amount': 7000, 'start_date': '2026-01-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_financing': [
            {'name': 'ערבות בנקאית', 'monthly_amount': 8000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_other': [
            {'name': 'הסעות עובדים', 'monthly_amount': 6000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
            {'name': 'ביגוד ואמצעי מיגון', 'monthly_amount': 3500, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
        ],
        'actuals': actuals_with_data({
            1: {'revenue': 0, 'op_expenses': 225000, 'salary_expenses': 0, 'notes': 'תחילת שנה, תשלום ינואר'},
            2: {'revenue': 260000, 'op_expenses': 230000, 'salary_expenses': 0, 'notes': 'תשלום ינואר נכנס'},
            3: {'revenue': 265000, 'op_expenses': 235000, 'salary_expenses': 0, 'notes': 'שגרה'},
        }),
    },

    # 5. משרדי רמת גן — מנרב, מטה, אתי, ~35% margin
    {
        'project_name': 'משרדי רמת גן',
        'priority_id': 'P-3003',
        'start_date': '2026-04-01',
        'expected_end_date': '2026-07-31',
        'manager': 'אתי',
        'client': 'בורסת רמת גן',
        'description': 'שיפוץ משרדי הבורסה לניירות ערך ברמת גן',
        'axis': 'מנרב',
        'area': 'מטה',
        'status': 'active',
        'total_revenue': 450000,
        'revenue_payment_terms': [
            {'type': 'מקדמה', 'percent': 40},
            {'type': 'שוטף+0', 'percent': 60},
        ],
        'subcontractors': [
            {'name': 'ניר גבס', 'total_amount': 45000, 'start_date': '2026-04-15', 'end_date': '2026-06-15',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'ניר שטרן', 'contact_phone': '050-1313131', 'business_id': '515000013'},
            {'name': 'זוהר צביעה', 'total_amount': 32000, 'start_date': '2026-05-01', 'end_date': '2026-07-15',
             'payment_terms': [{'type': 'מקדמה', 'percent': 25}, {'type': 'שוטף+30', 'percent': 75}],
             'contact_name': 'זוהר בן דוד', 'contact_phone': '052-1414141', 'business_id': '515000014'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל פרויקט', 'monthly_amount': 15000, 'start_date': '2026-04-01', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+0'},
            {'name': 'צוות שטח (2)', 'monthly_amount': 24000, 'start_date': '2026-04-15', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'ציוד שיפוצים', 'monthly_amount': 5000, 'start_date': '2026-04-01', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח מבנה', 'monthly_amount': 10000, 'start_date': '2026-07-31', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [],
        'expense_lines_financing': [],
        'expense_lines_other': [
            {'name': 'ניקיון', 'monthly_amount': 2500, 'start_date': '2026-04-01', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+0'},
        ],
        'actuals': empty_actuals(),
    },

    # 6. פארק תעשייה נתניה — פיתוח עסקי, רכש, אריאל, ~15% margin (risk)
    {
        'project_name': 'פארק תעשייה נתניה',
        'priority_id': 'P-4001',
        'start_date': '2026-02-15',
        'expected_end_date': '2026-10-31',
        'manager': 'אריאל',
        'client': 'עיריית נתניה',
        'description': 'הקמת תשתיות בפארק תעשייה חדש בנתניה',
        'axis': 'פיתוח עסקי',
        'area': 'רכש',
        'status': 'active',
        'total_revenue': 1800000,
        'revenue_payment_terms': [
            {'type': 'שוטף+60', 'percent': 70},
            {'type': 'שוטף+90', 'percent': 30},
        ],
        'subcontractors': [
            {'name': 'כביש זהב', 'total_amount': 420000, 'start_date': '2026-03-01', 'end_date': '2026-09-30',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'דוד כביש', 'contact_phone': '050-1515151', 'business_id': '515000015'},
            {'name': 'תשתיות מים', 'total_amount': 310000, 'start_date': '2026-03-15', 'end_date': '2026-08-31',
             'payment_terms': [{'type': 'מקדמה', 'percent': 15}, {'type': 'שוטף+45', 'percent': 85}],
             'contact_name': 'אמיר מים', 'contact_phone': '054-1616161', 'business_id': '515000016'},
            {'name': 'חשמל תעשייתי פלוס', 'total_amount': 275000, 'start_date': '2026-04-01', 'end_date': '2026-10-15',
             'payment_terms': [{'type': 'שוטף+60', 'percent': 100}],
             'contact_name': 'יגאל חשמל', 'contact_phone': '052-1717171', 'business_id': '515000017'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל אתר', 'monthly_amount': 22000, 'start_date': '2026-02-15', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל פרויקט', 'monthly_amount': 18000, 'start_date': '2026-02-15', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
            {'name': 'עובדי שטח (5)', 'monthly_amount': 55000, 'start_date': '2026-03-01', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'מחפרון כבד', 'monthly_amount': 18000, 'start_date': '2026-03-01', 'end_date': '2026-08-31', 'payment_terms': 'שוטף+30'},
            {'name': 'מערבל בטון', 'monthly_amount': 8000, 'start_date': '2026-03-15', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+30'},
            {'name': 'גנרטור תעשייתי', 'monthly_amount': 5000, 'start_date': '2026-02-15', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח קבלנים', 'monthly_amount': 40000, 'start_date': '2026-10-31', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
            {'name': 'ביטוח צד ג', 'monthly_amount': 15000, 'start_date': '2026-10-31', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [
            {'name': 'יועץ סביבתי', 'monthly_amount': 12000, 'start_date': '2026-02-15', 'end_date': '2026-04-30', 'payment_terms': 'שוטף+30'},
            {'name': 'מודד מוסמך', 'monthly_amount': 10000, 'start_date': '2026-02-15', 'end_date': '2026-03-31', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_financing': [
            {'name': 'ערבות ביצוע', 'monthly_amount': 12000, 'start_date': '2026-02-15', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
            {'name': 'ערבות בנקאית', 'monthly_amount': 6000, 'start_date': '2026-02-15', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_other': [
            {'name': 'הסעות', 'monthly_amount': 5000, 'start_date': '2026-03-01', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
            {'name': 'אבטחה', 'monthly_amount': 7000, 'start_date': '2026-02-15', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
        ],
        'actuals': actuals_with_data({
            2: {'revenue': 0, 'op_expenses': 68000, 'salary_expenses': 0, 'notes': 'הוצאות ראשונות'},
            3: {'revenue': 0, 'op_expenses': 185000, 'salary_expenses': 0, 'notes': 'עבודות תשתית'},
        }),
    },

    # 7. מלון אילת — פיתוח עסקי, זכיינות, אלון, ~28% margin
    {
        'project_name': 'מלון אילת',
        'priority_id': 'P-4002',
        'start_date': '2026-01-01',
        'expected_end_date': '2026-12-31',
        'manager': 'אלון',
        'client': 'רשת מלונות ים סוף',
        'description': 'ניהול ותחזוקה שנתית של מלון 5 כוכבים באילת',
        'axis': 'פיתוח עסקי',
        'area': 'זכיינות',
        'status': 'active',
        'total_revenue': 5000000,
        'revenue_payment_terms': [
            {'type': 'מקדמה', 'percent': 15},
            {'type': 'שוטף+30', 'percent': 85},
        ],
        'subcontractors': [
            {'name': 'טופ ניקיון', 'total_amount': 650000, 'start_date': '2026-01-01', 'end_date': '2026-12-31',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'מיכל טופ', 'contact_phone': '050-1818181', 'business_id': '515000018'},
            {'name': 'גינון ונוף', 'total_amount': 280000, 'start_date': '2026-02-01', 'end_date': '2026-11-30',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'עמי גינון', 'contact_phone': '052-1919191', 'business_id': '515000019'},
            {'name': 'בריכות ספא', 'total_amount': 320000, 'start_date': '2026-03-01', 'end_date': '2026-10-31',
             'payment_terms': [{'type': 'מקדמה', 'percent': 20}, {'type': 'שוטף+45', 'percent': 80}],
             'contact_name': 'תמר ספא', 'contact_phone': '054-2020202', 'business_id': '515000020'},
            {'name': 'חום קור אילת', 'total_amount': 450000, 'start_date': '2026-01-01', 'end_date': '2026-12-31',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'ברק קור', 'contact_phone': '050-2121212', 'business_id': '515000021'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל פרויקט בכיר', 'monthly_amount': 30000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
            {'name': 'צוות אחזקה (10)', 'monthly_amount': 120000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל בטיחות', 'monthly_amount': 12000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'ציוד אחזקה כללי', 'monthly_amount': 8000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+30'},
            {'name': 'ציוד בריכה', 'monthly_amount': 5000, 'start_date': '2026-03-01', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח מקיף', 'monthly_amount': 85000, 'start_date': '2026-12-31', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [
            {'name': 'יועץ בטיחות אש', 'monthly_amount': 6000, 'start_date': '2026-01-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_financing': [
            {'name': 'ערבות בנקאית', 'monthly_amount': 15000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_other': [
            {'name': 'הסעות עובדים', 'monthly_amount': 8000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
            {'name': 'ביגוד', 'monthly_amount': 3000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+0'},
            {'name': 'חומרי ניקוי', 'monthly_amount': 4000, 'start_date': '2026-01-01', 'end_date': '2026-12-31', 'payment_terms': 'שוטף+30'},
        ],
        'actuals': actuals_with_data({
            1: {'revenue': 750000, 'op_expenses': 285000, 'salary_expenses': 0, 'notes': 'מקדמה + ינואר'},
            2: {'revenue': 350000, 'op_expenses': 295000, 'salary_expenses': 0, 'notes': 'שגרה'},
            3: {'revenue': 355000, 'op_expenses': 310000, 'salary_expenses': 0, 'notes': 'תחילת עונת בריכות'},
        }),
    },

    # 8. תחנת רכבת לוד — לוגי, פרוייקטים, אתי, ~8% margin (critical)
    {
        'project_name': 'תחנת רכבת לוד',
        'priority_id': 'P-2003',
        'start_date': '2026-05-01',
        'expected_end_date': '2026-11-30',
        'manager': 'אתי',
        'client': 'רכבת ישראל',
        'description': 'שיפוץ ושדרוג תחנת רכבת לוד',
        'axis': 'לוגי',
        'area': 'פרוייקטים',
        'status': 'active',
        'total_revenue': 950000,
        'revenue_payment_terms': [
            {'type': 'שוטף+90', 'percent': 100},
        ],
        'subcontractors': [
            {'name': 'פלדות הדרום', 'total_amount': 280000, 'start_date': '2026-05-15', 'end_date': '2026-10-31',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'אייל פלדה', 'contact_phone': '050-2222233', 'business_id': '515000022'},
            {'name': 'חשמל רכבות', 'total_amount': 195000, 'start_date': '2026-06-01', 'end_date': '2026-11-15',
             'payment_terms': [{'type': 'שוטף+45', 'percent': 100}],
             'contact_name': 'נועם חשמל', 'contact_phone': '052-2323232', 'business_id': '515000023'},
            {'name': 'ריצוף תעשייתי', 'total_amount': 120000, 'start_date': '2026-07-01', 'end_date': '2026-10-31',
             'payment_terms': [{'type': 'מקדמה', 'percent': 10}, {'type': 'שוטף+60', 'percent': 90}],
             'contact_name': 'עידו ריצוף', 'contact_phone': '054-2424242', 'business_id': '515000024'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל אתר', 'monthly_amount': 20000, 'start_date': '2026-05-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'עובדי שטח (4)', 'monthly_amount': 44000, 'start_date': '2026-05-15', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל בטיחות', 'monthly_amount': 10000, 'start_date': '2026-05-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'פיגומים כבדים', 'monthly_amount': 15000, 'start_date': '2026-05-15', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+30'},
            {'name': 'ציוד ריתוך', 'monthly_amount': 4000, 'start_date': '2026-06-01', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח קבלנים', 'monthly_amount': 25000, 'start_date': '2026-11-30', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'ביטוח עובדים', 'monthly_amount': 10000, 'start_date': '2026-11-30', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [
            {'name': 'יועץ תנועה', 'monthly_amount': 15000, 'start_date': '2026-05-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_financing': [
            {'name': 'ערבות ביצוע', 'monthly_amount': 7000, 'start_date': '2026-05-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_other': [
            {'name': 'אבטחה', 'monthly_amount': 8000, 'start_date': '2026-05-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'הסעות', 'monthly_amount': 4000, 'start_date': '2026-05-15', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
        ],
        'actuals': empty_actuals(),
    },

    # 9. קאנטרי כפר סבא — מנרב, מסחרי פרטי, אריאל, ~40% margin
    {
        'project_name': 'קאנטרי כפר סבא',
        'priority_id': 'P-3004',
        'start_date': '2026-06-01',
        'expected_end_date': '2026-10-31',
        'manager': 'אריאל',
        'client': 'קאנטרי כפר סבא',
        'description': 'שדרוג מתקני ספורט ובריכות בקאנטרי כפר סבא',
        'axis': 'מנרב',
        'area': 'מסחרי פרטי',
        'status': 'active',
        'total_revenue': 600000,
        'revenue_payment_terms': [
            {'type': 'מקדמה', 'percent': 50},
            {'type': 'שוטף+30', 'percent': 50},
        ],
        'subcontractors': [
            {'name': 'בריכות ישראל', 'total_amount': 85000, 'start_date': '2026-06-15', 'end_date': '2026-09-30',
             'payment_terms': [{'type': 'מקדמה', 'percent': 30}, {'type': 'שוטף+30', 'percent': 70}],
             'contact_name': 'יובל בריכות', 'contact_phone': '050-2525252', 'business_id': '515000025'},
            {'name': 'דשא סינטטי פלוס', 'total_amount': 65000, 'start_date': '2026-07-01', 'end_date': '2026-09-15',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'תומר דשא', 'contact_phone': '052-2626262', 'business_id': '515000026'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל פרויקט', 'monthly_amount': 14000, 'start_date': '2026-06-01', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
            {'name': 'צוות שטח (2)', 'monthly_amount': 22000, 'start_date': '2026-06-15', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'ציוד בריכות', 'monthly_amount': 6000, 'start_date': '2026-06-15', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח מבנה', 'monthly_amount': 12000, 'start_date': '2026-10-31', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [
            {'name': 'יועץ בטיחות', 'monthly_amount': 5000, 'start_date': '2026-06-01', 'end_date': '2026-06-30', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_financing': [],
        'expense_lines_other': [
            {'name': 'ניקיון', 'monthly_amount': 3000, 'start_date': '2026-06-01', 'end_date': '2026-10-31', 'payment_terms': 'שוטף+0'},
        ],
        'actuals': empty_actuals(),
    },

    # 10. מרכז לוגיסטי אשדוד — פיתוח עסקי, פרוייקטים, אלון, ~20% margin
    {
        'project_name': 'מרכז לוגיסטי אשדוד',
        'priority_id': 'P-4003',
        'start_date': '2026-03-01',
        'expected_end_date': '2026-11-30',
        'manager': 'אלון',
        'client': 'נמל אשדוד בע"מ',
        'description': 'הקמת מרכז לוגיסטי חדש בסמוך לנמל אשדוד',
        'axis': 'פיתוח עסקי',
        'area': 'פרוייקטים',
        'status': 'active',
        'total_revenue': 2100000,
        'revenue_payment_terms': [
            {'type': 'מקדמה', 'percent': 10},
            {'type': 'שוטף+45', 'percent': 50},
            {'type': 'שוטף+75', 'percent': 40},
        ],
        'subcontractors': [
            {'name': 'בטון הדרום', 'total_amount': 380000, 'start_date': '2026-03-15', 'end_date': '2026-09-30',
             'payment_terms': [{'type': 'שוטף+30', 'percent': 100}],
             'contact_name': 'שמעון בטון', 'contact_phone': '050-2727272', 'business_id': '515000027'},
            {'name': 'פלדות הנגב', 'total_amount': 290000, 'start_date': '2026-04-01', 'end_date': '2026-10-31',
             'payment_terms': [{'type': 'מקדמה', 'percent': 10}, {'type': 'שוטף+45', 'percent': 90}],
             'contact_name': 'עמית פלדה', 'contact_phone': '052-2828282', 'business_id': '515000028'},
            {'name': 'חשמל תעשייתי דרום', 'total_amount': 215000, 'start_date': '2026-05-01', 'end_date': '2026-11-15',
             'payment_terms': [{'type': 'שוטף+60', 'percent': 100}],
             'contact_name': 'מוטי חשמל', 'contact_phone': '054-2929292', 'business_id': '515000029'},
        ],
        'expense_lines_manpower': [
            {'name': 'מנהל אתר', 'monthly_amount': 24000, 'start_date': '2026-03-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל פרויקט', 'monthly_amount': 20000, 'start_date': '2026-03-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'עובדי שטח (5)', 'monthly_amount': 55000, 'start_date': '2026-03-15', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'מנהל בטיחות', 'monthly_amount': 10000, 'start_date': '2026-03-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_equipment': [
            {'name': 'שכירת עגורן', 'monthly_amount': 30000, 'start_date': '2026-04-01', 'end_date': '2026-09-30', 'payment_terms': 'שוטף+30'},
            {'name': 'מחפרון', 'monthly_amount': 12000, 'start_date': '2026-03-01', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+30'},
            {'name': 'משאבת בטון', 'monthly_amount': 10000, 'start_date': '2026-04-01', 'end_date': '2026-07-31', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_insurance': [
            {'name': 'ביטוח קבלנים', 'monthly_amount': 50000, 'start_date': '2026-11-30', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'ביטוח צד ג', 'monthly_amount': 18000, 'start_date': '2026-11-30', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_consultants': [
            {'name': 'יועץ קרקע', 'monthly_amount': 15000, 'start_date': '2026-03-01', 'end_date': '2026-04-30', 'payment_terms': 'שוטף+30'},
            {'name': 'יועץ תנועה', 'monthly_amount': 10000, 'start_date': '2026-03-01', 'end_date': '2026-05-31', 'payment_terms': 'שוטף+30'},
            {'name': 'שמאי', 'monthly_amount': 8000, 'start_date': '2026-03-01', 'end_date': '2026-03-31', 'payment_terms': 'שוטף+30'},
        ],
        'expense_lines_financing': [
            {'name': 'ערבות בנקאית', 'monthly_amount': 10000, 'start_date': '2026-03-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'ערבות ביצוע', 'monthly_amount': 8000, 'start_date': '2026-03-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
        ],
        'expense_lines_other': [
            {'name': 'הסעות', 'monthly_amount': 6000, 'start_date': '2026-03-15', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'משרד שטח', 'monthly_amount': 4000, 'start_date': '2026-03-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
            {'name': 'אבטחה', 'monthly_amount': 6500, 'start_date': '2026-03-01', 'end_date': '2026-11-30', 'payment_terms': 'שוטף+0'},
        ],
        'actuals': actuals_with_data({
            3: {'revenue': 210000, 'op_expenses': 175000, 'salary_expenses': 0, 'notes': 'מקדמה + תחילת עבודות'},
        }),
    },
]

if __name__ == '__main__':
    for p in PROJECTS:
        name = p['project_name']
        p['payment_milestones'] = p.get('payment_milestones', [])
        p['revenue_forecast'] = p.get('revenue_forecast', {str(i): 0 for i in range(1, 13)})
        p['total_budget'] = 0
        p['default_expense_payment_terms'] = p.get('default_expense_payment_terms', 'שוטף+30')
        p['company_id'] = ''
        p['is_recurring'] = False
        p['source'] = 'form'
        p['last_updated'] = NOW
        if 'actuals' not in p:
            p['actuals'] = empty_actuals()

        save_project_firestore(name, p)
        print(f'Created: {name}')

    print(f'\nDone! Created {len(PROJECTS)} projects.')
