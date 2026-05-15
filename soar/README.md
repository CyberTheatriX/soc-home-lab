# SOAR Engine

A custom Security Orchestration, Automation and Response engine
built from scratch in Python 3.12. Monitors Wazuh alerts in real
time and automatically responds to threats.

---

## What it does

- Tails Wazuh alerts.json continuously for new alerts
- Auto blocks attacking IPs via iptables on level 10+ alerts
- Detects cross source correlation — same IP appearing in both
  Suricata and Cowrie within 5 minutes
- Logs all incidents to SQLite database for audit trail
- Whitelist support to protect trusted IPs from being blocked

---

## File Structure

```text
soar/
├── main.py              # Entry point, tails alerts and dispatches playbooks
├── config.py            # All settings in one place
├── requirements.txt     # Python dependencies
└── playbooks/
    ├── ip_blocker.py    # Blocks IPs via iptables
    ├── correlator.py    # Cross source correlation engine
    └── incident_logger.py # Writes incidents to SQLite
```

---

## Configuration

All settings live in config.py:

| Setting | Default | Description |
|---|---|---|
| MIN_LEVEL_BLOCK | 10 | Alert level that triggers IP block |
| MIN_LEVEL_INCIDENT | 8 | Alert level that triggers incident log |
| CORRELATION_WINDOW | 300 | Seconds to look back for correlation |
| WHITELIST | 127.0.0.1, 192.168.56.1 | IPs never blocked |

---

## How it works

```text
Wazuh writes alert to alerts.json
          │
          ▼
main.py reads the new alert
          │
          ▼
Is level >= 10?
    │           │
   YES          NO
    │           │
    ▼           ▼
ip_blocker   skip block
blocks IP
    │
    ▼
correlator checks — did this IP
appear in both Suricata + Cowrie
within last 5 minutes?
    │
    ▼
incident_logger writes to SQLite
```

---

## Playbooks

### ip_blocker.py
Runs `iptables -I INPUT -s <ip> -j DROP` to block the attacking IP
at the firewall level. Also calls netfilter-persistent to make the
block survive a reboot.

### correlator.py
Queries the SQLite database looking for the same source IP appearing
in alerts from both Suricata and Cowrie within the correlation window.
If found, raises a level 12 correlation alert — meaning the attacker
was detected by two independent systems.

### incident_logger.py
Writes every level 8+ alert to the incidents SQLite database with
timestamp, source IP, severity level, description, source system,
and the full raw log for forensic reference.

---

## Running the SOAR

```bash
cd ~/soar
python3 main.py
```

Or as a systemd service which starts automatically on boot:

```bash
sudo systemctl start soar
sudo systemctl status soar
```
