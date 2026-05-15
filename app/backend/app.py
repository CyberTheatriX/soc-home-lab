import json
import sqlite3
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/health")
def health():
    return {"status": "SOC panel is alive!"}

@app.route("/api/alerts")
def get_alerts():
    alerts = []
    
    try:
        with open("/var/ossec/logs/alerts/alerts.json", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    alerts.append(json.loads(line))
    except FileNotFoundError:
        return {"error": "alerts file not found"}

    return {"total": len(alerts), "alerts": alerts[-20:]}

@app.route("/api/incidents")
def get_incidents():
    incidents = []
    
    try:
        conn = sqlite3.connect("/home/agb/soar/incidents.db")
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM incidents ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        incidents = [dict(row) for row in rows]
        conn.close()
    except Exception as e:
        return {"error": str(e)}
    
    return {"total": len(incidents), "incidents": incidents}

@app.route("/api/blocked-ips")
def get_blocked_ips():
    try:
        result = subprocess.run(
            ["sudo", "iptables", "-L", "INPUT", "-n", "--line-numbers"],
            capture_output=True,
            text=True
        )
        lines = result.stdout.splitlines()
        blocked = []
        for line in lines:
            if "DROP" in line:
                parts = line.split()
                blocked.append({
                    "rule_num": parts[0],
                    "ip": parts[4],
                })
        return {"total": len(blocked), "blocked_ips": blocked}
    except Exception as e:
        return {"error": str(e)}

@app.route("/api/services/status")
def services_status():
    services = ["suricata", "cowrie", "wazuh-manager", "soar"]
    result = []

    for service in services:
        status = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True,
            text=True
        )
        result.append({
            "name": service,
            "status": status.stdout.strip()
        })

    return {"services": result}

@app.route("/api/block-ip", methods=["POST"])
def block_ip():
    data = request.get_json()
    ip = data.get("ip")

    if not ip:
        return jsonify({"error": "no IP provided"}), 400

    subprocess.run(
        ["sudo", "iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"]
    )

    return jsonify({"success": True, "message": f"{ip} has been blocked"})


@app.route("/api/unblock-ip", methods=["POST"])
def unblock_ip():
    data = request.get_json()
    ip = data.get("ip")

    if not ip:
        return jsonify({"error": "no IP provided"}), 400

    subprocess.run(
        ["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"]
    )

    return jsonify({"success": True, "message": f"{ip} has been unblocked"})

@app.route("/api/services/control", methods=["POST"])
def services_control():
    data = request.get_json()
    service = data.get("service")
    action = data.get("action")

    allowed_services = ["suricata", "cowrie", "wazuh-manager", "soar"]
    allowed_actions = ["start", "stop", "restart"]

    if service not in allowed_services:
        return jsonify({"error": f"unknown service: {service}"}), 400

    if action not in allowed_actions:
        return jsonify({"error": f"unknown action: {action}"}), 400

    subprocess.run(["sudo", "systemctl", action, service])

    return jsonify({"success": True, "service": service, "action": action})

@app.route("/api/stats")
def get_stats():
    try:
        conn = sqlite3.connect("/home/agb/soar/incidents.db")
        conn.row_factory = sqlite3.Row

        total = conn.execute(
            "SELECT COUNT(*) as count FROM incidents"
        ).fetchone()["count"]

        top_ips = conn.execute(
            """SELECT src_ip, COUNT(*) as hits 
               FROM incidents 
               GROUP BY src_ip 
               ORDER BY hits DESC 
               LIMIT 5"""
        ).fetchall()

        by_level = conn.execute(
            """SELECT 
                 CASE
                   WHEN level >= 10 THEN 'high'
                   WHEN level >= 8  THEN 'medium'
                   ELSE 'low'
                 END as severity,
                 COUNT(*) as count
               FROM incidents
               GROUP BY severity"""
        ).fetchall()

        conn.close()

        return jsonify({
            "total_incidents": total,
            "top_ips": [dict(row) for row in top_ips],
            "by_severity": [dict(row) for row in by_level]
        })
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
