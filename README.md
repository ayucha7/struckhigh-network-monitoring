<p align="center">
  <img src="static/assets/logo-struckhigh.png" alt="Struckhigh" height="60" />
</p>

<h1 align="center">NetWatch — Network Monitoring Tool</h1>
<p align="center">
  <strong>Real-time local network intelligence, built by <a href="https://struckhigh.co.in">Struckhigh Solutions</a></strong>
</p>

<p align="center">
  <a href="https://ayucha7.github.io/struckhigh-network-monitoring/"><img src="https://img.shields.io/badge/🚀_Live_Demo-Visit_Now-e8552d?style=for-the-badge" /></a>
</p>

<p align="center">
  <a href="https://struckhigh.co.in"><img src="https://img.shields.io/badge/Struckhigh-Website-e8552d?style=for-the-badge&logo=google-chrome&logoColor=white" /></a>
  <a href="https://instagram.com/struckhigh"><img src="https://img.shields.io/badge/Struckhigh-Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" /></a>
  <a href="https://www.linkedin.com/company/struckhigh/"><img src="https://img.shields.io/badge/Struckhigh-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge" />
</p>

---

## 🚀 Live Demo

**[▶ Try the interactive demo →](https://ayucha7.github.io/struckhigh-network-monitoring/)**

The demo runs entirely in your browser with simulated sample data — no installation needed. It showcases all features: live traffic chart, connections table, interfaces, ports, and dark/light theme toggle.

---

## What is NetWatch?

**NetWatch** is a lightweight, zero-config network monitoring dashboard that runs entirely on your local machine. It gives you instant visibility into:

- 📈 **Live upload & download speeds** — real-time bandwidth graph with 60-second rolling window
- 🔗 **Active connections** — every TCP/UDP socket with process info, status badges
- 🖧 **Network interfaces** — all adapters with IPs, MTU, speed, and per-interface traffic
- 🔒 **Port usage** — listening and active ports shown as color-coded pills
- 🌗 **Dark / Light mode** — toggle with one click, persists across sessions

No cloud. No accounts. No data leaves your machine.

> *"Think Bigger. Design Smarter."* — Struckhigh Solutions

---

## Features at a Glance

| Feature | Description |
|---------|-------------|
| **Real-time chart** | Upload (green) and download (pink) bandwidth plotted with smooth interpolation |
| **20+ connections** | Full table with protocol, family, local/remote address, status, PID, process |
| **Interface cards** | en0, lo0, utun0, awdl0 — each with up/down status, MTU, addresses, traffic |
| **Port pills** | 9 listening ports (sshd, nginx, postgres, redis, mysql, etc.) + active ports |
| **Theme toggle** | Clearly visible button in the top bar — switches everything including the chart |
| **Logo filter** | Struckhigh logo adapts via CSS `filter` — inverted in dark, original in light |
| **Demo mode** | `DEMO=1` flag shows sample data without exposing real system info |
| **macOS fallback** | Auto-detects when `psutil` needs root, falls back to `lsof` parsing |
| **Struckhigh branded** | Logo, colors, tagline, social links throughout |

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/ayucha7/struckhigh-network-monitoring.git
cd struckhigh-network-monitoring
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python3 app.py
```

### 4. Open your browser

```
http://127.0.0.1:6100
```

That's it. No config files, no database, no setup wizards.

---

## Demo Mode

Want to see the dashboard with sample data (great for presentations or testing)?

```bash
DEMO=1 python3 app.py
```

This populates the dashboard with realistic fake data — nginx, postgres, redis, sshd, firefox, git, and more. No real system info is exposed.

---

## macOS Users

For full connection visibility (all PIDs and process names), run with elevated privileges:

```bash
sudo python3 app.py
```

Without `sudo`, the app automatically falls back to `lsof` which still shows your user's connections.

---

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                    Browser (UI)                      │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐ │
│  │  Stats   │ │  Chart   │ │ Table  │ │  Ports   │ │
│  └────┬─────┘ └────┬─────┘ └───┬────┘ └────┬─────┘ │
│       │            │           │            │       │
│       └────────────┴─────┬─────┴────────────┘       │
│                          │ fetch every 2s           │
└──────────────────────────┼──────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Flask API  │
                    │  /api/*     │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────┴─────┐ ┌───┴───┐ ┌─────┴─────┐
        │  psutil   │ │ lsof  │ │ Background│
        │ (primary) │ │(fallbk)│ │  Thread   │
        └───────────┘ └───────┘ │ (1s poll) │
                                └───────────┘
```

| Component | Role |
|-----------|------|
| **Background thread** | Samples `psutil.net_io_counters()` every 1s, stores 60-point rolling history |
| **psutil** | Primary source for connections, interfaces, and traffic counters |
| **lsof fallback** | Parses `lsof -i -n -P` when psutil returns empty (macOS without sudo) |
| **Flask API** | Four JSON endpoints: `/api/traffic`, `/api/connections`, `/api/interfaces`, `/api/ports` |
| **Frontend** | Single-page HTML with Chart.js, polls every 2s, dark/light theme |

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/traffic` | Rolling 60s bandwidth history + totals |
| `GET /api/connections` | All active TCP/UDP connections |
| `GET /api/interfaces` | Network interfaces with addresses and stats |
| `GET /api/ports` | Aggregated listening and active ports |

### Sample Response — `/api/traffic`

```json
{
  "timestamps": ["14:30:01", "14:30:02", "14:30:03"],
  "speed_up": [12400, 8200, 15600],
  "speed_down": [245000, 189000, 312000],
  "total_sent": 1200000000,
  "total_recv": 4800000000,
  "total_sent_fmt": "1.1 GB",
  "total_recv_fmt": "4.5 GB"
}
```

### Sample Response — `/api/connections`

```json
[
  {
    "family": "IPv4",
    "type": "TCP",
    "local_addr": "127.0.0.1:5000",
    "remote_addr": "—",
    "status": "LISTEN",
    "pid": 1234,
    "process": "python3"
  },
  {
    "family": "IPv4",
    "type": "TCP",
    "local_addr": "192.168.1.10:52341",
    "remote_addr": "140.82.121.4:443",
    "status": "ESTABLISHED",
    "pid": 1200,
    "process": "git"
  }
]
```

### Sample Response — `/api/ports`

```json
{
  "listening": [
    { "port": 22, "processes": ["sshd"] },
    { "port": 443, "processes": ["nginx"] },
    { "port": 5000, "processes": ["python3"] },
    { "port": 5432, "processes": ["postgres"] }
  ],
  "established": [
    { "port": 443, "processes": ["curl", "firefox"] },
    { "port": 52341, "processes": ["git"] }
  ]
}
```

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Backend runtime |
| **Flask 3.x** | Lightweight web framework |
| **psutil** | Cross-platform system monitoring |
| **Chart.js 4** | Beautiful, responsive charts |
| **lsof** | macOS fallback for connection data |

---

## Project Structure

```
struckhigh-network-monitoring/
├── app.py                      # Flask backend + data collection
├── templates/
│   └── index.html              # Dashboard UI (Flask version)
├── static/
│   └── assets/
│       └── logo-struckhigh.png # Struckhigh logo (local copy)
├── docs/
│   ├── index.html              # Static demo for GitHub Pages
│   └── assets/
│       └── logo-struckhigh.png # Logo for GitHub Pages
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
├── .gitignore
└── README.md
```

---

## Privacy & Security

- **Zero data collection** — nothing is logged, stored, or transmitted
- **Local only** — the server binds to `127.0.0.1`, not accessible from other machines
- **No accounts** — no sign-up, no tracking, no analytics
- **Demo mode** — use `DEMO=1` to show fake data for presentations
- **Open source** — inspect every line of code yourself

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/awesome-feature`)
3. Commit your changes (`git commit -m 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/awesome-feature`)
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <img src="static/assets/logo-struckhigh.png" alt="Struckhigh" height="40" />
</p>
<p align="center">
  <strong>Built with ❤️ by <a href="https://struckhigh.co.in">Struckhigh Solutions</a></strong><br/>
  <sub>Think Bigger. Design Smarter.</sub>
</p>
<p align="center">
  <a href="https://struckhigh.co.in">🌐 Website</a> &nbsp;·&nbsp;
  <a href="https://instagram.com/struckhigh">📸 Instagram</a> &nbsp;·&nbsp;
  <a href="https://www.linkedin.com/company/struckhigh/">💼 LinkedIn</a> &nbsp;·&nbsp;
  <a href="https://www.facebook.com/struckhigh/">📘 Facebook</a> &nbsp;·&nbsp;
  <a href="https://twitter.com/struckhigh/">🐦 Twitter</a>
</p>
