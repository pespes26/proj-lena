import os
import json
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


# --- Projects (JSON) ---

def load_projects_firestore():
    return load_json(PROJECTS_DATA_FILE, {})


def save_project_firestore(name, data):
    all_data = load_json(PROJECTS_DATA_FILE, {})
    all_data[name] = data
    save_json(PROJECTS_DATA_FILE, all_data)


def save_all_projects_firestore(data):
    save_json(PROJECTS_DATA_FILE, data)


def delete_project_firestore(name):
    all_data = load_json(PROJECTS_DATA_FILE, {})
    all_data.pop(name, None)
    save_json(PROJECTS_DATA_FILE, all_data)


# --- Reports (JSON) ---

def load_reports_firestore():
    data = load_json(REPORTS_FILE, [])
    if isinstance(data, dict):
        return data.get('reports', [])
    return data


def save_report_firestore(report):
    reports = load_json(REPORTS_FILE, [])
    if isinstance(reports, dict):
        reports = reports.get('reports', [])
    reports.append(report)
    save_json(REPORTS_FILE, reports)
