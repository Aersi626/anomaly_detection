# db_logger.py

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "anomalies.db"

# Initialize database and table if not exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anomaly_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            anomaly_score REAL,
            is_anomaly INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Insert a batch of anomaly records
def log_anomalies(scores, flags):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    for score, flag in zip(scores, flags):
        cursor.execute(
            "INSERT INTO anomaly_log (timestamp, anomaly_score, is_anomaly) VALUES (?, ?, ?)",
            (now, float(score), int(flag))
        )
    conn.commit()
    conn.close()

# Read from the log for dashboard display
def read_anomalies(limit=100):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM anomaly_log ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df