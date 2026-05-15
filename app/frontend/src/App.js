import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [services, setServices] = useState([]);
  const [stats, setStats] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [blockedIps, setBlockedIps] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [lastUpdated, setLastUpdated] = useState('');

  function fetchData() {
    fetch('/api/services/status')
      .then(res => res.json())
      .then(data => setServices(data.services));

    fetch('/api/stats')
      .then(res => res.json())
      .then(data => setStats(data));

    fetch('/api/incidents')
      .then(res => res.json())
      .then(data => setIncidents(data.incidents));

    fetch('/api/blocked-ips')
      .then(res => res.json())
      .then(data => setBlockedIps(data.blocked_ips));

    fetch('/api/alerts')
      .then(res => res.json())
      .then(data => setAlerts(data.alerts));

    setLastUpdated(new Date().toLocaleTimeString());
  }

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  function blockIp(ip) {
    fetch('/api/block-ip', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ip: ip})
    }).then(() => fetchData());
  }

  function unblockIp(ip) {
    fetch('/api/unblock-ip', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ip: ip})
    }).then(() => fetchData());
  }

  return (
    <div>
      <div className="header">
        <h1>SOC Home Lab</h1>
        <p>Security Operations Control Panel</p>
        <p style={{color: '#3fb950', fontSize: '12px', marginTop: '5px'}}>
          ● Last updated: {lastUpdated}
        </p>
      </div>

      <div className="dashboard">

        <div className="panel">
          <h2>Services</h2>
          {services.map(service => (
            <div className="service-item" key={service.name}>
              <span>{service.name}</span>
              <span className={
                service.status === 'active' ? 'status-active' : 'status-inactive'
              }>
                {service.status === 'active' ? '● ACTIVE' : '● STOPPED'}
              </span>
            </div>
          ))}
        </div>

        <div className="panel">
          <h2>Attack Statistics</h2>
          {stats && (
            <div>
              <div className="service-item">
                <span>Total Incidents</span>
                <span style={{color: '#58a6ff'}}>{stats.total_incidents}</span>
              </div>
              {stats.by_severity.map(s => (
                <div className="service-item" key={s.severity}>
                  <span>{s.severity.toUpperCase()}</span>
                  <span className={
                    s.severity === 'high' ? 'status-inactive' : 'status-active'
                  }>{s.count}</span>
                </div>
              ))}
              <h2 style={{marginTop: '15px'}}>Top Attacking IPs</h2>
              {stats.top_ips.map(ip => (
                <div className="service-item" key={ip.src_ip}>
                  <span>{ip.src_ip}</span>
                  <span style={{color: '#f85149'}}>{ip.hits} hits</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <h2>Recent Incidents</h2>
          {incidents.slice(0, 8).map(inc => (
            <div className="service-item" key={inc.id}>
              <span style={{fontSize: '12px', maxWidth: '70%'}}>
                {inc.description}
              </span>
              <span className={
                inc.level >= 10 ? 'status-inactive' : 'status-active'
              }>L{inc.level}</span>
            </div>
          ))}
        </div>

        <div className="panel">
          <h2>Blocked IPs</h2>
          {blockedIps.length === 0 && (
            <div style={{color: '#8b949e', fontSize: '14px'}}>
              No IPs currently blocked
            </div>
          )}
          {blockedIps.map(item => (
            <div className="service-item" key={item.ip}>
              <span>{item.ip}</span>
              <button
                onClick={() => unblockIp(item.ip)}
                style={{
                  background: '#f85149',
                  color: 'white',
                  border: 'none',
                  padding: '4px 10px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontFamily: 'monospace'
                }}>
                UNBLOCK
              </button>
            </div>
          ))}
          <div style={{marginTop: '15px'}}>
            <button
              onClick={() => blockIp('192.168.56.40')}
              style={{
                background: '#21262d',
                color: '#f85149',
                border: '1px solid #f85149',
                padding: '6px 14px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontFamily: 'monospace'
              }}>
              BLOCK KALI (192.168.56.40)
            </button>
          </div>
        </div>

        <div className="panel">
          <h2>Recent Alerts</h2>
          {alerts.slice(-10).reverse().map((alert, index) => (
            <div className="service-item" key={index}>
              <span style={{fontSize: '12px', maxWidth: '75%'}}>
                {alert.rule?.description || 'Unknown alert'}
              </span>
              <span className={
                alert.rule?.level >= 10 ? 'status-inactive' : 'status-active'
              }>
                L{alert.rule?.level}
              </span>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

export default App;
