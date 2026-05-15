#!/usr/bin/env python3
"""
Playbook 3 — Incident Logger
Logs high severity alerts to SQLite database
"""

import sqlite3
import logging
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

log = logging.getLogger(__name__)


def init_db():
    """Create incidents table if it doesn't exist."""
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT,
            src_ip      TEXT,
            level       INTEGER,
            rule_id     TEXT,
            description TEXT,
            source      TEXT,
            groups      TEXT,
            full_log    TEXT,
            created_at  TEXT
        )
    ''')
    conn.commit()
    conn.close()
    log.info("Incident database initialized")


def log_incident(alert_data, source):
    """Write a high severity incident to the database."""
    try:
        init_db()
        conn = sqlite3.connect(config.DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO incidents
            (timestamp, src_ip, level, rule_id, description,
             source, groups, full_log, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert_data["timestamp"],
            alert_data["src_ip"],
            alert_data["level"],
            alert_data["rule_id"],
            alert_data["description"],
            source,
            json.dumps(alert_data["groups"]),
            alert_data["full_log"],
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
        log.info(
            f"Incident logged | IP: {alert_data['src_ip']} | "
            f"Level: {alert_data['level']} | {alert_data['description']}"
        )
    except Exception as e:
        log.error(f"Failed to log incident: {e}")
