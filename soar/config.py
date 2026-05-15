# SOAR Configuration
# ==================

# Wazuh alerts file
ALERTS_FILE = "/var/ossec/logs/alerts/alerts.json"

# Minimum alert level to trigger SOAR actions
MIN_LEVEL_BLOCK = 10        # Block IP at this level
MIN_LEVEL_INCIDENT = 8     # Log incident at this level
MIN_LEVEL_CRITICAL = 14    # Correlation critical alert

# AbuseIPDB API key (we'll add this later)
ABUSEIPDB_API_KEY = "YOUR_API_KEY_HERE"

# Correlation window in seconds
CORRELATION_WINDOW = 300   # 5 minutes

# IPs to never block (whitelist)
WHITELIST = [
    "127.0.0.1",
    "192.168.56.1",   # your host machine
    "192.168.56.12",  # Lubuntu VM itself
]

# Incident database path
DB_PATH = "/home/agb/soar/incidents.db"

# Log file for SOAR actions
SOAR_LOG = "/home/agb/soar/soar.log"
