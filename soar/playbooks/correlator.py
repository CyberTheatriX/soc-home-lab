#!/usr/bin/env python3
"""
Playbook 2 — Correlation Engine
Detects same IP appearing across multiple sources
"""

import logging
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

log = logging.getLogger(__name__)

# In-memory store: {ip: {source: timestamp}}
ip_activity = {}


def check_correlation(ip, source, alert_data):
    """Check if same IP has been seen across multiple sources."""
    now = datetime.utcnow()
    window = timedelta(seconds=config.CORRELATION_WINDOW)

    # Initialize IP entry if first time seeing it
    if ip not in ip_activity:
        ip_activity[ip] = {}

    # Record this source and timestamp
    ip_activity[ip][source] = now

    # Clean up old entries outside the window
    ip_activity[ip] = {
        src: ts for src, ts in ip_activity[ip].items()
        if now - ts <= window
    }

    # Check how many sources this IP has appeared in
    sources_seen = list(ip_activity[ip].keys())

    # Correlation: Suricata + Cowrie = attack chain confirmed
    if "suricata" in sources_seen and "cowrie" in sources_seen:
        fire_correlation_alert(ip, sources_seen, alert_data)

    # Correlation: Three or more sources = coordinated attack
    if len(sources_seen) >= 3:
        fire_coordinated_alert(ip, sources_seen, alert_data)


def fire_correlation_alert(ip, sources, alert_data):
    """Fire a critical correlation alert."""
    log.critical(
        f"CORRELATION ALERT | IP: {ip} | "
        f"Seen in: {', '.join(sources)} | "
        f"Suricata scan → Cowrie intrusion - ATTACK CHAIN CONFIRMED"
    )


def fire_coordinated_alert(ip, sources, alert_data):
    """Fire alert for coordinated multi-source attack."""
    log.critical(
        f"COORDINATED ATTACK | IP: {ip} | "
        f"Active across {len(sources)} sources: {', '.join(sources)} | "
        f"Full-spectrum attack detected"
    )
