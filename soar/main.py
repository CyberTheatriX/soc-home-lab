#!/usr/bin/env python3
"""
SOAR Main Engine
Tails Wazuh alerts.json and dispatches playbooks
"""

import json
import time
import os
import sys
import logging
from datetime import datetime

# Add soar directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from playbooks.ip_blocker import block_ip
from playbooks.correlator import check_correlation
from playbooks.incident_logger import log_incident

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SOAR] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(config.SOAR_LOG),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def extract_alert_data(alert):
    """Extract key fields from a Wazuh alert."""
    return {
        "timestamp":   alert.get("timestamp", ""),
        "level":       alert.get("rule", {}).get("level", 0),
        "rule_id":     alert.get("rule", {}).get("id", ""),
        "description": alert.get("rule", {}).get("description", ""),
        "groups":      alert.get("rule", {}).get("groups", []),
        "src_ip":      alert.get("data", {}).get("src_ip", None),
        "location":    alert.get("location", ""),
        "full_log":    alert.get("full_log", ""),
    }


def identify_source(groups):
    """Identify which log source generated this alert."""
    if "suricata" in groups:
        return "suricata"
    if "cowrie" in groups or "honeypot" in groups:
        return "cowrie"
    if "web" in groups or "accesslog" in groups:
        return "apache2"
    if "authentication_failed" in groups or "pam" in groups:
        return "auth"
    return "system"


def process_alert(alert_data):
    """Process a single alert and trigger appropriate playbooks."""
    level   = alert_data["level"]
    src_ip  = alert_data["src_ip"]
    source  = identify_source(alert_data["groups"])
    desc    = alert_data["description"]

    log.info(f"Alert | Level:{level} | Source:{source} | IP:{src_ip} | {desc}")

    # Skip if no source IP
    if not src_ip:
        return

    # Skip whitelisted IPs
    if src_ip in config.WHITELIST:
        log.info(f"Skipping whitelisted IP: {src_ip}")
        return

    # Playbook 1 — Block IP
    if level >= config.MIN_LEVEL_BLOCK:
        block_ip(src_ip, reason=desc, source=source)

    # Playbook 2 — Correlation check
    check_correlation(src_ip, source, alert_data)

    # Playbook 3 — Log incident
    if level >= config.MIN_LEVEL_INCIDENT:
        log_incident(alert_data, source)


def tail_alerts(filepath):
    """Continuously tail the Wazuh alerts file."""
    log.info(f"Starting SOAR engine - watching {filepath}")

    # Wait for file to exist
    while not os.path.exists(filepath):
        log.warning(f"Waiting for {filepath} to exist...")
        time.sleep(5)

    with open(filepath, "r") as f:
        # Move to end of file
        f.seek(0, 2)
        log.info("SOAR engine ready - listening for alerts...")

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            line = line.strip()
            if not line:
                continue
            try:
                alert = json.loads(line)
                alert_data = extract_alert_data(alert)
                process_alert(alert_data)
            except json.JSONDecodeError:
                log.warning(f"Could not parse alert line: {line[:100]}")
            except Exception as e:
                log.error(f"Error processing alert: {e}")


if __name__ == "__main__":
    tail_alerts(config.ALERTS_FILE)
