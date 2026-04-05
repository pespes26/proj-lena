import os
import json
from auth import db


# --- Legacy JSON (for local dev fallback) ---

def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- Firestore: Projects ---

def load_projects_firestore():
    """Load all projects from Firestore. Returns dict {name: data}."""
    result = {}
    docs = db.collection('projects').stream()
    for doc in docs:
        result[doc.id] = doc.to_dict()
    return result


def save_project_firestore(name, data):
    """Save a single project to Firestore."""
    db.collection('projects').document(name).set(data)


def save_all_projects_firestore(data):
    """Save all projects to Firestore (batch)."""
    batch = db.batch()
    for name, project_data in data.items():
        ref = db.collection('projects').document(name)
        batch.set(ref, project_data)
    batch.commit()


def delete_project_firestore(name):
    """Delete a project from Firestore."""
    db.collection('projects').document(name).delete()


# --- Firestore: Reports ---

def load_reports_firestore():
    """Load all reports from Firestore. Returns list."""
    docs = db.collection('reports').order_by('created_at').stream()
    reports = []
    for doc in docs:
        r = doc.to_dict()
        r['_doc_id'] = doc.id
        reports.append(r)
    return reports


def save_report_firestore(report):
    """Add a single report to Firestore."""
    db.collection('reports').add(report)
