SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employees(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS reports(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    employee_id INTEGER,
    report_date TEXT NOT NULL,
    report_time TEXT,
    employee_code TEXT,
    employee_name TEXT,
    category TEXT,
    volante TEXT,
    comments TEXT,
    photos_count INTEGER DEFAULT 0,
    app_version TEXT,
    app_version_code INTEGER,
    format_version TEXT,
    created_at_device TEXT,
    imported_at TEXT NOT NULL,
    pdf_name TEXT NOT NULL,
    pdf_sha256 TEXT NOT NULL UNIQUE,
    json_sha256 TEXT NOT NULL,
    compliance_pct REAL DEFAULT 0,
    total_answers INTEGER DEFAULT 0,
    total_ok INTEGER DEFAULT 0,
    total_no INTEGER DEFAULT 0,
    total_change INTEGER DEFAULT 0,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS answers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    cumple INTEGER NOT NULL DEFAULT 0,
    cambio INTEGER NOT NULL DEFAULT 0,
    display_order INTEGER,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evidence(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL UNIQUE,
    pdf_blob BLOB NOT NULL,
    encrypted_payload_blob BLOB NOT NULL,
    decrypted_json TEXT NOT NULL,
    pdf_size INTEGER NOT NULL,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS questions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL UNIQUE,
    category TEXT,
    active INTEGER DEFAULT 1,
    display_order INTEGER
);

CREATE TABLE IF NOT EXISTS license(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    install_date TEXT NOT NULL,
    expires_date TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'TRIAL',
    license_key TEXT
);

CREATE TABLE IF NOT EXISTS app_config(
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_reports_project_date ON reports(project_id, report_date);
CREATE INDEX IF NOT EXISTS idx_reports_employee ON reports(employee_code);
CREATE INDEX IF NOT EXISTS idx_answers_question ON answers(question);
CREATE INDEX IF NOT EXISTS idx_answers_response ON answers(response);
"""
