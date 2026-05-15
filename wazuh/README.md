# Wazuh SIEM Configuration

Custom Wazuh rules and configuration for the SOC home lab.
Wazuh acts as the central correlation engine ingesting logs
from all security components.

---

## Log Sources Configured

| Source | Format | Path |
|---|---|---|
| Suricata IDS | JSON | /var/log/suricata/eve-wazuh.json |
| Cowrie Honeypot | JSON | /home/cowrie/cowrie/var/log/cowrie/cowrie.json |
| Apache Web Server | Apache | /var/log/apache2/access.log |
| Authentication | journald | auth |
| Package Manager | syslog | /var/log/dpkg.log |

---

## Custom Cowrie Detection Rules

File: `cowrie_rules.xml`

| Rule ID | Level | Description |
|---|---|---|
| 100200 | 3 | Any Cowrie honeypot event |
| 100201 | 6 | New connection to honeypot |
| 100202 | 6 | Failed login attempt on honeypot |
| 100203 | 10 | Successful login to honeypot |
| 100204 | 8 | Command executed inside honeypot |
| 100205 | 12 | File download attempt in honeypot |
| 100206 | 10 | Brute force detected on honeypot |
| 100210 | 12 | Correlation — IP in Suricata + Cowrie |
| 100211 | 14 | Critical — active attacker confirmed |

---

## Alert Severity Scale

Wazuh uses levels 1 to 15:

```text
Level 1  - 3  → Informational
Level 4  - 7  → Low severity
Level 8  - 9  → Medium severity  (SOAR logs incident)
Level 10 - 13 → High severity    (SOAR blocks IP)
Level 14 - 15 → Critical         (immediate response)
```

---

## Why Custom Rules?

Wazuh does not have built in rules for Cowrie honeypot events.
The custom rules in cowrie_rules.xml decode the Cowrie JSON format
and map each event type to an appropriate severity level.

A successful honeypot login is level 10 because any attacker who
successfully authenticates to our honeypot is an active threat
that must be blocked immediately.

A file download attempt is level 12 because it indicates the
attacker is attempting to install malware or tools — a serious
escalation in the attack chain.

---

## Wazuh Dashboard

A custom SOC dashboard was built in Wazuh with 5 panels:

- Alert Timeline
- Top Attacking IPs
- Alerts by Source
- Alert Severity Breakdown
- Recent High Severity Alerts
