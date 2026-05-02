"""Generate Logfi Security Architecture Document — English, Professional PDF."""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register fonts
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))

# Colors
NAVY = HexColor('#0f172a')
SLATE = HexColor('#475569')
DARK = HexColor('#1e293b')
LIGHT_GRAY = HexColor('#f8fafc')
BORDER = HexColor('#e2e8f0')
WHITE = HexColor('#ffffff')
RED_BADGE = HexColor('#ef4444')

WIDTH, HEIGHT = A4
MARGIN = 2.5 * cm
CONTENT_WIDTH = WIDTH - 2 * MARGIN


class SecurityDoc:
    def __init__(self, filename):
        self.c = canvas.Canvas(filename, pagesize=A4)
        self.page_num = 0
        self.y = HEIGHT - MARGIN

    def new_page(self):
        if self.page_num > 0:
            self._footer()
            self.c.showPage()
        self.page_num += 1
        self.y = HEIGHT - MARGIN
        if self.page_num > 1:
            self.c.setStrokeColor(BORDER)
            self.c.setLineWidth(0.5)
            self.c.line(MARGIN, HEIGHT - 1.5 * cm, WIDTH - MARGIN, HEIGHT - 1.5 * cm)
            self.c.setFont('Arial', 7)
            self.c.setFillColor(SLATE)
            self.c.drawString(MARGIN, HEIGHT - 1.2 * cm, 'Logfi — Security Architecture & Information Security Document')
            self.c.drawRightString(WIDTH - MARGIN, HEIGHT - 1.2 * cm, f'v1.0 | {datetime.now().strftime("%B %Y")}')
            self.y = HEIGHT - 2.2 * cm

    def _footer(self):
        self.c.setStrokeColor(BORDER)
        self.c.setLineWidth(0.5)
        self.c.line(MARGIN, 1.5 * cm, WIDTH - MARGIN, 1.5 * cm)
        self.c.setFont('Arial', 7)
        self.c.setFillColor(SLATE)
        self.c.drawString(MARGIN, 1 * cm, f'Page {self.page_num}')
        self.c.setFillColor(RED_BADGE)
        self.c.drawRightString(WIDTH - MARGIN, 1 * cm, 'CONFIDENTIAL — Internal Use Only')

    def title_page(self):
        self.new_page()
        y = HEIGHT / 2 + 3 * cm

        # Logo
        self.c.setFillColor(NAVY)
        self.c.roundRect(WIDTH / 2 - 1.2 * cm, y, 2.4 * cm, 2.4 * cm, 8, fill=1, stroke=0)
        self.c.setFillColor(WHITE)
        self.c.setFont('ArialBold', 18)
        self.c.drawCentredString(WIDTH / 2, y + 0.8 * cm, 'Logfi')

        # Title
        y -= 1.5 * cm
        self.c.setFont('ArialBold', 26)
        self.c.setFillColor(NAVY)
        self.c.drawCentredString(WIDTH / 2, y, 'Security Architecture')
        y -= 0.9 * cm
        self.c.setFont('ArialBold', 26)
        self.c.drawCentredString(WIDTH / 2, y, '& Information Security')
        y -= 1.2 * cm
        self.c.setFont('Arial', 13)
        self.c.setFillColor(SLATE)
        self.c.drawCentredString(WIDTH / 2, y, 'Financial Management System for Construction & FM Projects')

        # Divider
        y -= 1.5 * cm
        self.c.setStrokeColor(BORDER)
        self.c.setLineWidth(0.5)
        self.c.line(WIDTH / 2 - 4 * cm, y, WIDTH / 2 + 4 * cm, y)

        # Meta
        y -= 1.2 * cm
        meta = [
            ('Version', '1.0'),
            ('Date', datetime.now().strftime('%d %B %Y')),
            ('Author', 'Bar Pesso — Logi Group'),
            ('Classification', 'Confidential — Internal Use Only'),
            ('Status', 'Pending InfoSec Approval'),
        ]
        for label, value in meta:
            self.c.setFont('ArialBold', 10)
            self.c.setFillColor(SLATE)
            self.c.drawRightString(WIDTH / 2 - 0.5 * cm, y, f'{label}:')
            self.c.setFont('Arial', 10)
            self.c.drawString(WIDTH / 2 + 0.5 * cm, y, value)
            y -= 0.6 * cm

    def h1(self, text):
        if self.y < 4 * cm:
            self.new_page()
        self.y -= 0.8 * cm
        self.c.setFont('ArialBold', 16)
        self.c.setFillColor(NAVY)
        self.c.drawString(MARGIN, self.y, text)
        self.y -= 0.8 * cm

    def h2(self, text):
        if self.y < 3 * cm:
            self.new_page()
        self.y -= 0.5 * cm
        self.c.setFont('ArialBold', 12)
        self.c.setFillColor(DARK)
        self.c.drawString(MARGIN, self.y, text)
        self.y -= 0.6 * cm

    def p(self, text):
        lines = self._wrap(text, 'Arial', 10, CONTENT_WIDTH)
        for line in lines:
            if self.y < 2.5 * cm:
                self.new_page()
            self.c.setFont('Arial', 10)
            self.c.setFillColor(SLATE)
            self.c.drawString(MARGIN, self.y, line)
            self.y -= 0.45 * cm

    def bullet(self, text):
        lines = self._wrap(text, 'Arial', 10, CONTENT_WIDTH - 1 * cm)
        first = True
        for line in lines:
            if self.y < 2.5 * cm:
                self.new_page()
            if first:
                self.c.setFont('Arial', 10)
                self.c.setFillColor(SLATE)
                self.c.drawString(MARGIN + 0.3 * cm, self.y, '\u2022')
                first = False
            self.c.setFont('Arial', 10)
            self.c.setFillColor(SLATE)
            self.c.drawString(MARGIN + 0.8 * cm, self.y, line)
            self.y -= 0.45 * cm

    def table(self, headers, rows):
        num_cols = len(headers)
        col_w = CONTENT_WIDTH / num_cols

        # Header row
        if self.y < 2.5 * cm:
            self.new_page()
        self.c.setFillColor(LIGHT_GRAY)
        self.c.rect(MARGIN, self.y - 0.15 * cm, CONTENT_WIDTH, 0.55 * cm, fill=1, stroke=0)
        self.c.setStrokeColor(BORDER)
        self.c.setLineWidth(0.3)
        self.c.line(MARGIN, self.y - 0.15 * cm, WIDTH - MARGIN, self.y - 0.15 * cm)
        for i, h in enumerate(headers):
            self.c.setFont('ArialBold', 9)
            self.c.setFillColor(DARK)
            self.c.drawString(MARGIN + i * col_w + 0.2 * cm, self.y, h)
        self.y -= 0.55 * cm

        # Data rows
        for row in rows:
            if self.y < 2.5 * cm:
                self.new_page()
            self.c.setStrokeColor(BORDER)
            self.c.setLineWidth(0.2)
            self.c.line(MARGIN, self.y - 0.15 * cm, WIDTH - MARGIN, self.y - 0.15 * cm)
            for i, cell in enumerate(row):
                self.c.setFont('Arial', 9)
                self.c.setFillColor(SLATE)
                self.c.drawString(MARGIN + i * col_w + 0.2 * cm, self.y, str(cell))
            self.y -= 0.5 * cm

        self.c.setStrokeColor(BORDER)
        self.c.line(MARGIN, self.y + 0.35 * cm, WIDTH - MARGIN, self.y + 0.35 * cm)
        self.y -= 0.2 * cm

    def space(self, v=0.3):
        self.y -= v * cm

    def _wrap(self, text, font, size, max_w):
        words = text.split()
        lines = []
        cur = []
        self.c.setFont(font, size)
        for w in words:
            test = ' '.join(cur + [w])
            if self.c.stringWidth(test, font, size) > max_w and cur:
                lines.append(' '.join(cur))
                cur = [w]
            else:
                cur.append(w)
        if cur:
            lines.append(' '.join(cur))
        return lines

    def save(self):
        self._footer()
        self.c.save()


def generate():
    out = os.path.join(os.path.dirname(__file__), 'Logfi_Security_Architecture.pdf')
    d = SecurityDoc(out)

    # TITLE PAGE
    d.title_page()

    # TOC
    d.new_page()
    d.h1('Table of Contents')
    for item in [
        '1. System Overview',
        '2. Technical Architecture',
        '3. Authentication & Authorization',
        '4. Data Storage & Encryption',
        '5. Network & Communication Security',
        '6. Access Control Matrix',
        '7. Google Cloud Platform (GCP) Services',
        '8. AI & Machine Learning Components',
        '9. Risk Assessment & Mitigation',
        '10. Regulatory Compliance',
        '11. Recommendations for Approval',
    ]:
        d.bullet(item)

    # 1. OVERVIEW
    d.new_page()
    d.h1('1. System Overview')
    d.p('Logfi is an internal financial management system built for Logi Group / Manrav IFM. The system manages the financial aspects of construction, maintenance and facility management (FM) projects — including P&L reports, cash flow analysis, subcontractor management, payment terms, and risk analysis.')
    d.space()
    d.h2('Data Types')
    d.bullet('Project financials: revenue, expenses, payment terms, P&L, cash flow')
    d.bullet('Supplier data: name, contact details, contract amounts, payment terms')
    d.bullet('Salary costs: monthly amounts per project (not individual employee salaries)')
    d.bullet('Financial reports: P&L, cash flow, risk scoring, variance analysis')
    d.bullet('User accounts: name, email, role, authentication credentials')
    d.space()
    d.h2('System Users')
    d.table(
        ['Role', 'Count', 'Access Level'],
        [
            ['System Admin (CEO)', '1', 'Full access including user management'],
            ['Economist', '1', 'Full access except user management'],
            ['Viewer', '1-3', 'Read-only access to all data'],
            ['Project Manager', '3', 'Read-only access to own projects only'],
        ]
    )

    # 2. ARCHITECTURE
    d.new_page()
    d.h1('2. Technical Architecture')
    d.h2('System Components')
    d.table(
        ['Component', 'Technology', 'Purpose'],
        [
            ['Frontend', 'Vue 3 + Tailwind CSS', 'Single Page Application (SPA)'],
            ['Backend', 'FastAPI (Python)', 'REST API + business logic'],
            ['Database', 'Google Firestore', 'NoSQL document database'],
            ['Authentication', 'Firebase Authentication', 'User auth + 2FA (TOTP)'],
            ['Hosting', 'GCP Cloud Run', 'Serverless container platform'],
            ['AI Chatbot', 'Google Gemini API', 'Financial analysis assistant'],
        ]
    )
    d.space()
    d.h2('Data Flow')
    d.p('Browser (Vue SPA) --[HTTPS]--> Cloud Run (FastAPI) --[gRPC]--> Firestore')
    d.p('Browser --[HTTPS]--> Firebase Auth --[JWT token]--> Cloud Run (verify)')
    d.p('Cloud Run --[HTTPS]--> Gemini API (summary data only, no PII)')

    # 3. AUTH
    d.new_page()
    d.h1('3. Authentication & Authorization')
    d.h2('Authentication')
    d.bullet('Firebase Authentication with email + password')
    d.bullet('Two-Factor Authentication (2FA) via Google Authenticator (TOTP)')
    d.bullet('JWT tokens issued by Firebase, verified server-side with Firebase Admin SDK')
    d.bullet('Token expiry: 60 minutes, auto-refreshed by Firebase SDK')
    d.bullet('Passwords stored exclusively in Firebase (hashed, never in application code)')
    d.bullet('Clock skew tolerance: 30 seconds for token verification')
    d.space()
    d.h2('Authorization')
    d.bullet('4 permission levels: admin, economist, viewer, project_manager')
    d.bullet('Every API request requires valid JWT token — verified server-side')
    d.bullet('Project managers can only access projects assigned to them (linked_manager)')
    d.bullet('Authorization enforced on backend — cannot be bypassed from client')
    d.bullet('CORS restricted to application domain only')

    # 4. DATA STORAGE
    d.h1('4. Data Storage & Encryption')
    d.bullet('All data stored in Google Firestore (NoSQL)')
    d.bullet('Encryption at rest: AES-256, managed by Google (default)')
    d.bullet('No direct Firestore access from browser — all access through backend API')
    d.bullet('Service Account with minimal permissions (principle of least privilege)')
    d.bullet('Service Account keys excluded from Git (.gitignore)')
    d.bullet('Sensitive credentials (API keys, passwords) stored in environment variables')
    d.space()
    d.h2('Data Classification')
    d.table(
        ['Data Type', 'Sensitivity', 'Storage', 'Protection'],
        [
            ['Project financials', 'High', 'Firestore', 'AES-256 at rest + HTTPS'],
            ['Supplier details', 'Medium', 'Firestore', 'AES-256 at rest + HTTPS'],
            ['Salary costs', 'High', 'Firestore', 'AES-256 at rest + role-based access'],
            ['User passwords', 'Critical', 'Firebase Auth', 'bcrypt hash (never stored in app)'],
            ['API keys', 'Critical', 'Env vars / .env', 'gitignored, GCP Secret Manager'],
        ]
    )

    # 5. NETWORK
    d.new_page()
    d.h1('5. Network & Communication Security')
    d.bullet('All traffic encrypted via HTTPS/TLS — no HTTP endpoints')
    d.bullet('Cloud Run provides automatic SSL certificate (managed by Google)')
    d.bullet('CORS policy restricts API access to authorized domain only')
    d.bullet('Firebase Auth tokens transmitted in Authorization: Bearer header')
    d.bullet('No sensitive data stored in cookies or localStorage (except Firebase session)')
    d.bullet('No external API receives personally identifiable information (PII)')

    # 6. ACCESS MATRIX
    d.h1('6. Access Control Matrix')
    d.table(
        ['Action', 'Admin', 'Economist', 'Viewer', 'Project Mgr'],
        [
            ['View all projects', 'Yes', 'Yes', 'Yes', 'Own only'],
            ['Create project', 'Yes', 'Yes', 'No', 'No'],
            ['Edit project', 'Yes', 'Yes', 'No', 'No'],
            ['Update actuals', 'Yes', 'Yes', 'No', 'Own only'],
            ['Manage users', 'Yes', 'No', 'No', 'No'],
            ['AI Chatbot', 'All data', 'All data', 'Read-only', 'Own projects'],
            ['Export PDF', 'Yes', 'Yes', 'Yes', 'Own only'],
            ['View dashboard', 'Executive', 'Operational', 'Operational', 'My Projects'],
        ]
    )

    # 7. GCP
    d.new_page()
    d.h1('7. Google Cloud Platform (GCP) Services')
    d.h2('Services Used')
    d.table(
        ['Service', 'Purpose', 'Region'],
        [
            ['Cloud Run', 'Application server (serverless)', 'us-central1'],
            ['Firestore', 'Document database', 'us-east1'],
            ['Firebase Auth', 'User authentication + 2FA', 'Global'],
            ['Cloud Build', 'Docker image builds', 'us-central1'],
        ]
    )
    d.space()
    d.h2('GCP Security Controls')
    d.bullet('GCP Project ID: minlog-491211')
    d.bullet('Billing account with budget alerts configured')
    d.bullet('IAM: Service Account with minimal permissions only')
    d.bullet('No public access to Firestore — backend Service Account only')
    d.bullet('Cloud Run: Application-level authentication (Firebase JWT)')
    d.bullet('Docker images built via Cloud Build (no local builds in production)')
    d.space()
    d.h2('GCP Certifications')
    d.bullet('SOC 1, SOC 2, SOC 3')
    d.bullet('ISO 27001 — Information Security Management')
    d.bullet('ISO 27017 — Cloud Security')
    d.bullet('ISO 27018 — PII Protection in Cloud')

    # 8. AI
    d.h1('8. AI & Machine Learning Components')
    d.p('The system includes a financial analysis chatbot powered by Google Gemini API.')
    d.space()
    d.h2('AI Data Policy')
    d.bullet('Chatbot receives only project summaries (name, revenue, expenses, margin)')
    d.bullet('No salary data, supplier PII, or personal information sent to AI')
    d.bullet('Gemini API: data not used for model training (per Google policy)')
    d.bullet('Planned: migration to Vertex AI (data stays within GCP project)')
    d.bullet('Financial calculations (What-If, Risk Score) run in Python — no AI involved')
    d.bullet('AI responses are advisory only — no automated financial decisions')

    # 9. RISKS
    d.new_page()
    d.h1('9. Risk Assessment & Mitigation')
    d.table(
        ['Risk', 'Severity', 'Mitigation'],
        [
            ['Password breach', 'Critical', 'Firebase Auth + 2FA + bcrypt'],
            ['Unauthorized access', 'High', 'JWT + RBAC + server-side enforcement'],
            ['Data leak', 'High', 'Encryption at rest + HTTPS + CORS'],
            ['API key exposure', 'Medium', '.env + .gitignore + Secret Manager'],
            ['AI hallucination', 'Low', 'Grounded prompts + temperature 0.25'],
            ['DDoS attack', 'Low', 'Cloud Run auto-scaling + Google infra'],
            ['SQL injection', 'None', 'Firestore NoSQL (no SQL queries)'],
            ['XSS', 'Low', 'Vue.js auto-escaping + no v-html on user input'],
        ]
    )

    # 10. COMPLIANCE
    d.h1('10. Regulatory Compliance')
    d.p('Google Cloud Platform meets the following standards:')
    d.bullet('SOC 1, SOC 2, SOC 3 — Service Organization Controls')
    d.bullet('ISO 27001 — Information Security Management System')
    d.bullet('ISO 27017 — Cloud-Specific Information Security')
    d.bullet('ISO 27018 — Protection of PII in Public Cloud')
    d.bullet('GDPR compliance available (Data Processing Agreement)')
    d.bullet('Google Cloud DPA available upon request')

    # 11. RECOMMENDATIONS
    d.new_page()
    d.h1('11. Recommendations for Approval')
    d.p('The following steps are recommended before production deployment:')
    d.space()
    d.bullet('1. Architecture review — review of this document by Information Security Officer')
    d.bullet('2. Password policy — define minimum length, complexity, expiration')
    d.bullet('3. Mandatory 2FA — enforce for all users (currently optional)')
    d.bullet('4. GCP budget alerts — configure alerts for unexpected spending')
    d.bullet('5. Audit logging — track sensitive operations (user creation, data exports)')
    d.bullet('6. Code review — verify no credential exposure in source code')
    d.bullet('7. Penetration test — optional, recommended for production')
    d.bullet('8. Backup & recovery — define RPO/RTO and test procedures')
    d.bullet('9. Google DPA — sign Data Processing Agreement with Google')
    d.bullet('10. Final approval — Information Security Officer sign-off')

    d.space(1)
    d.h2('Contact')
    d.p('For questions or clarifications:')
    d.bullet('Bar Pesso — System Developer')
    d.bullet('bar@logigroup.co')

    d.space(1.5)
    d.p('Information Security Officer Signature: _______________________________')
    d.space(0.5)
    d.p('Date: _______________________________')

    d.save()
    print(f'PDF created: {out}')


if __name__ == '__main__':
    generate()
