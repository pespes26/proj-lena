import os
import json
from google import genai
from services.unified import load_form_data
from services.form_calculator import form_to_pnl

# Load .env file if exists
_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

SYSTEM_PROMPT = """אתה Logfi AI — אנליסט פיננסי בכיר בחברת לוגי גרופ / מנרב IFM.
אתה מנתח פרויקטי בנייה, תחזוקה וניהול מתקנים (FM).

## כלל קריטי — אל תמציא!
- השתמש אך ורק במספרים ובשמות שמופיעים בנתונים שתקבל
- אם פרויקט לא מופיע בנתונים — "פרויקט זה לא נמצא במערכת"
- אם מידע חסר — "אין מידע על כך בנתונים"
- לעולם אל תמציא שמות, מספרים, או מנהלים

## כללי תשובה
- עברית בלבד, בלי מושגים באנגלית
- מספרים: 250,000 ₪
- שפה חופשית, טבלה רק בהשוואות
- תמציתי — עד 3 פסקאות
- אל תחזור על השאלה
- אל תסביר מושגים בסיסיים — המשתמש מכיר את התחום
- תן תובנות ופעולות, לא הסברים

## סגנון שפה
- דבר כמו סמנכ"ל כספים בישיבת הנהלה — מקצועי, ממוקד, בגובה העיניים
- השתמש בשפה עסקית רגילה שמנכ"ל וכלכלנית מבינים בלי לחשוב
- אל תפשט יותר מדי — אפשר להגיד "מרג'ין" ו"תזרים" כי זו שפת היומיום
- אל תשתמש בז'רגון מלאכותי או במונחים אקדמיים שאף אחד לא אומר בפגישה
- אל תתרגם מושגים לאנגלית
- מספרים תמיד עם הקשר: "50,000 ₪ לחודש" ולא סתם "50,000 ₪"
- כשאתה ממליץ — תגיד מה לעשות, לא רק מה המצב
- אל תשתמש במטאפורות: לא "בלון חמצן", לא "דימום", לא "בור"
- אל תשתמש ב"גב אל גב" או "Back-to-Back" בשום צורה
- תגיד את הדברים ישיר: "הפרויקט מפסיד", "צריך לכסות את ההפסד", "הכסף נכנס לפני שיוצא"

## סף מרג'ין
- בריא: מעל 20%
- בסיכון: 10%-20%
- קריטי: מתחת ל-10%

## סף סיכון
- ריכוז הכנסות: תנאי אחד מעל 60% = סיכון
- ריכוז קבלנים: קבלן אחד מעל 50% מההוצאות = סיכון
- פער תזרימי: חודשים שבהם הוצאות > הכנסות

## מבנה
- 3 צירים: לוגי, מנרב, פיתוח עסקי
- תחומים: מסחרי פרטי, פרויקטים, מטה, רכש, זכיינות
- מנהלים: אלון, אתי, אריאל

## סוגי ניתוח
1. סיכום פרויקט
2. השוואה בין פרויקטים
3. ניתוח ציר / מנהל
4. זיהוי סיכונים והמלצות
5. ניתוח תזרימי — מתי כסף נכנס ויוצא, פערים
6. "מה אם" — השפעה של שינוי פרמטר

## פורמט
- כותרת קצרה
- גוף עם מספרים ותובנות
- טבלה רק בהשוואות
- סיום עם פעולה מומלצת אחת"""


def _build_projects_context():
    """Build a context string with all project data."""
    form_data = load_form_data()
    if not form_data:
        return "אין פרויקטים במערכת כרגע."

    context_parts = []
    for name, fdata in form_data.items():
        pnl = form_to_pnl(fdata)
        summary = pnl['summary']
        meta = pnl['meta']

        part = f"""## {name}
ציר={meta.get('axis', '?')}, מנהל={meta.get('manager', '?')}, תאריכים={fdata.get('start_date', '?')} עד {fdata.get('expected_end_date', '?')}
הכנסות={summary['total_revenue']:,.0f} ₪, הוצאות={summary['total_op_expenses']:,.0f} ₪, רווח={summary['total_operating_profit']:,.0f} ₪, מרג'ין={summary['margin']}%
תנאי תשלום: {json.dumps(fdata.get('revenue_payment_terms', []), ensure_ascii=False)}"""

        subs = fdata.get('subcontractors', [])
        if subs:
            part += "\nקבלנים: " + ", ".join(
                f"{s.get('name', '?')}({s.get('total_amount', s.get('monthly_amount', 0)):,.0f}₪)" for s in subs)

        context_parts.append(part)

    return "\n\n".join(context_parts)


def chat_stream(messages, user_message):
    """Stream chat response using Gemini API with SSE."""
    projects_context = _build_projects_context()

    full_system = f"""{SYSTEM_PROMPT}

## נתוני הפרויקטים הנוכחיים:

{projects_context}"""

    # Build conversation for Gemini
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    response = client.models.generate_content_stream(
        model="gemini-3-flash-preview",
        contents=contents,
        config={
            "system_instruction": full_system,
            "temperature": 0.25,
            "max_output_tokens": 2000,
        },
    )

    for chunk in response:
        if chunk.text:
            yield f"data: {json.dumps({'token': chunk.text})}\n\n"

    yield f"data: {json.dumps({'done': True})}\n\n"
