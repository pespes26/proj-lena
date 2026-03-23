import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data.xlsx')
PROJECTS_DATA_FILE = os.path.join(BASE_DIR, 'projects_data.json')
REPORTS_FILE = os.path.join(BASE_DIR, 'reports.json')
ATTENDANCE_FILE = os.path.join(BASE_DIR, 'attendance_data.json')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
CONTRACTS_DIR = os.path.join(BASE_DIR, 'contracts')
USERS_FILE = os.path.join(BASE_DIR, 'users.json')

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

EXPENSE_BREAKDOWN = {
    'מנרב סנטר': {
        'op_components': [{'name': 'ניקיון ותחזוקה', 'amount': 100}],
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

MONTH_LABELS = ['9/2025', '10/2025', '11/2025', '12/2025',
                '1/2026', '2/2026', '3/2026', '4/2026', '5/2026',
                '6/2026', '7/2026', '8/2026', '9/2026']

CAL_MONTHS = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]

COL_MAP = [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]

EXPENSE_CATEGORIES = ['manpower', 'equipment', 'insurance', 'consultants', 'financing', 'other']
