# SOC Control Panel

A full stack web application for managing the SOC home lab.
Built with React frontend and Flask backend, providing a live
dashboard for monitoring and controlling all security components.

---

## Architecture

```text
Browser (React)          Lubuntu VM (Flask)
Port 3000                Port 5000
     │                        │
     │   GET /api/alerts       │
     │──────────────────────▶ │
     │                        │ reads alerts.json
     │   JSON response         │
     │◀────────────────────── │
     │                        │
     │   POST /api/block-ip    │
     │──────────────────────▶ │
     │                        │ runs iptables
     │   {"success": true}     │
     │◀────────────────────── │
```

---

## Backend — Flask API

Location: `backend/app.py`
Port: 5000

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/health | Check all data sources are reachable |
| GET | /api/alerts | Last 20 Wazuh alerts |
| GET | /api/incidents | All incidents from SQLite |
| GET | /api/blocked-ips | Current iptables DROP rules |
| POST | /api/block-ip | Add iptables DROP rule for an IP |
| POST | /api/unblock-ip | Remove iptables DROP rule |
| GET | /api/services/status | Status of all 4 services |
| POST | /api/services/control | Start, stop or restart a service |
| GET | /api/stats | Incident statistics and top IPs |

### Data Sources

| Data | Source |
|---|---|
| Alerts | /var/ossec/logs/alerts/alerts.json |
| Incidents | /home/agb/soar/incidents.db |
| Blocked IPs | iptables INPUT chain |
| Service status | systemctl |

---

## Frontend — React Dashboard

Location: `frontend/src/App.js`
Port: 3000

### Panels

| Panel | Data Source | Updates |
|---|---|---|
| Services | /api/services/status | Every 30 seconds |
| Attack Statistics | /api/stats | Every 30 seconds |
| Recent Incidents | /api/incidents | Every 30 seconds |
| Blocked IPs | /api/blocked-ips | Every 30 seconds |
| Recent Alerts | /api/alerts | Every 30 seconds |

---

## Running the Application

### Start the backend

```bash
cd app/backend
newgrp wazuh
python3 app.py
```

### Start the frontend

```bash
cd app/frontend
npm install
npm start
```

### Open in browser
http://localhost:3000
---

## Key Features

- Live data from all security components
- One click IP blocking and unblocking
- Real iptables firewall control from the browser
- Service start and stop from the UI
- Auto refreshes every 30 seconds
- Color coded severity levels
- Dark theme SOC interface
