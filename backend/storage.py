import os
import json
from auth import db, DEV_MODE
from config import PROJECTS_DATA_FILE, REPORTS_FILE


# --- JSON helpers ---

def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _firestore_unavailable():
    """True when Firebase project is gone or DEV_MODE is active without Firestore."""
    return False  # will be set to True on first Firestore failure


_firestore_down = False  # cached flag — once down, stay on JSON


# --- Firestore: Projects ---

def load_projects_firestore():
    """Load all projects from Firestore, fall back to JSON on failure."""
    global _firestore_down
    if not _firestore_down:
        try:
            result = {}
            docs = db.collection('projects').stream()
            for doc in docs:
                result[doc.id] = doc.to_dict()
            return result
        except Exception as e:
            print(f"[STORAGE] Firestore unavailable, falling back to JSON: {e}")
            _firestore_down = True
    return load_json(PROJECTS_DATA_FILE, {})


def save_project_firestore(name, data):
    """Save a single project to Firestore or JSON fallback."""
    global _firestore_down
    if not _firestore_down:
        try:
            db.collection('projects').document(name).set(data)
            # Also mirror to JSON
            all_data = load_json(PROJECTS_DATA_FILE, {})
            all_data[name] = data
            save_json(PROJECTS_DATA_FILE, all_data)
            return
        except Exception as e:
            print(f"[STORAGE] Firestore write failed, using JSON: {e}")
            _firestore_down = True
    all_data = load_json(PROJECTS_DATA_FILE, {})
    all_data[name] = data
    save_json(PROJECTS_DATA_FILE, all_data)


def save_all_projects_firestore(data):
    """Save all projects to Firestore or JSON fallback."""
    global _firestore_down
    if not _firestore_down:
        try:
            batch = db.batch()
            for name, project_data in data.items():
                ref = db.collection('projects').document(name)
                batch.set(ref, project_data)
            batch.commit()
            save_json(PROJECTS_DATA_FILE, data)
            return
        except Exception as e:
            print(f"[STORAGE] Firestore batch write failed, using JSON: {e}")
            _firestore_down = True
    save_json(PROJECTS_DATA_FILE, data)


def delete_project_firestore(name):
    """Delete a project from Firestore or JSON fallback."""
    global _firestore_down
    if not _firestore_down:
        try:
            db.collection('projects').document(name).delete()
        except Exception as e:
            print(f"[STORAGE] Firestore delete failed, using JSON: {e}")
            _firestore_down = True
    all_data = load_json(PROJECTS_DATA_FILE, {})
    all_data.pop(name, None)
    save_json(PROJECTS_DATA_FILE, all_data)


# --- Firestore: Reports ---

def load_reports_firestore():
    """Load all reports from Firestore, fall back to JSON on failure."""
    global _firestore_down
    if not _firestore_down:
        try:
            docs = db.collection('reports').order_by('created_at').stream()
            reports = []
            for doc in docs:
                r = doc.to_dict()
                r['_doc_id'] = doc.id
                reports.append(r)
            return reports
        except Exception as e:
            print(f"[STORAGE] Firestore reports unavailable, falling back to JSON: {e}")
            _firestore_down = True
    data = load_json(REPORTS_FILE, [])
    # REPORTS_FILE may be a list or a dict with 'reports' key
    if isinstance(data, dict):
        return data.get('reports', [])
    return data


def save_report_firestore(report):
    """Add a single report to Firestore or JSON fallback."""
    global _firestore_down
    if not _firestore_down:
        try:
            db.collection('reports').add(report)
            # Mirror to JSON
            reports = load_reports_firestore()
            reports.append(report)
            save_json(REPORTS_FILE, reports)
            return
        except Exception as e:
            print(f"[STORAGE] Firestore report save failed, using JSON: {e}")
            _firestore_down = True
    reports = load_json(REPORTS_FILE, [])
    if isinstance(reports, dict):
        reports = reports.get('reports', [])
    reports.append(report)
    save_json(REPORTS_FILE, reports)
