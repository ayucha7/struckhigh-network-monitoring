"""
Network Monitor — A Flask-based local network monitoring dashboard.
Tracks real-time incoming/outgoing traffic, active connections, and port usage.

All data is read live from YOUR machine only. Nothing is stored, logged, or sent
anywhere. Safe to run on any system.
"""

import os
import re
import subprocess
import time
import threading
import random
from collections import deque
from datetime import datetime

import psutil
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Demo mode — set DEMO=1 to show sample data without real system access
# ---------------------------------------------------------------------------
DEMO_MODE = os.environ.get("DEMO", "0") == "1"

# ---------------------------------------------------------------------------
# In-memory history (last 60 data points ≈ 60 seconds at 1 s interval)
# ---------------------------------------------------------------------------
MAX_HISTORY = 60
traffic_history = {
    "timestamps": deque(maxlen=MAX_HISTORY),
    "bytes_sent": deque(maxlen=MAX_HISTORY),
    "bytes_recv": deque(maxlen=MAX_HISTORY),
    "speed_up": deque(maxlen=MAX_HISTORY),
    "speed_down": deque(maxlen=MAX_HISTORY),
}

_prev_counters = None
_lock = threading.Lock()


def _collect_traffic():
    """Background thread: sample network counters every second."""
    global _prev_counters
    cumulative_sent = 1_200_000_000  # demo starting point
    cumulative_recv = 4_800_000_000

    while True:
        now = datetime.now().strftime("%H:%M:%S")

        if DEMO_MODE:
            up = random.randint(8_000, 250_000)
            down = random.randint(50_000, 1_800_000)
            cumulative_sent += up
            cumulative_recv += down
            with _lock:
                traffic_history["timestamps"].append(now)
                traffic_history["bytes_sent"].append(cumulative_sent)
                traffic_history["bytes_recv"].append(cumulative_recv)
                traffic_history["speed_up"].append(up)
                traffic_history["speed_down"].append(down)
        else:
            counters = psutil.net_io_counters()
            with _lock:
                if _prev_counters is not None:
                    up = counters.bytes_sent - _prev_counters.bytes_sent
                    down = counters.bytes_recv - _prev_counters.bytes_recv
                else:
                    up = 0
                    down = 0

                traffic_history["timestamps"].append(now)
                traffic_history["bytes_sent"].append(counters.bytes_sent)
                traffic_history["bytes_recv"].append(counters.bytes_recv)
                traffic_history["speed_up"].append(up)
                traffic_history["speed_down"].append(down)

                _prev_counters = counters

        time.sleep(1)


_collector = threading.Thread(target=_collect_traffic, daemon=True)
_collector.start()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _fmt_bytes(b):
    """Human-readable byte string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(b) < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


# ---------------------------------------------------------------------------
# Demo data generators
# ---------------------------------------------------------------------------
_DEMO_CONNECTIONS = [
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "127.0.0.1:5000",  "local_port": 5000,  "remote_addr": "—",                "status": "LISTEN",      "pid": 1234, "process": "python3"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "0.0.0.0:443",     "local_port": 443,   "remote_addr": "—",                "status": "LISTEN",      "pid": 800,  "process": "nginx"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "0.0.0.0:80",      "local_port": 80,    "remote_addr": "—",                "status": "LISTEN",      "pid": 800,  "process": "nginx"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "0.0.0.0:22",      "local_port": 22,    "remote_addr": "—",                "status": "LISTEN",      "pid": 500,  "process": "sshd"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "0.0.0.0:5432",    "local_port": 5432,  "remote_addr": "—",                "status": "LISTEN",      "pid": 600,  "process": "postgres"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "0.0.0.0:6379",    "local_port": 6379,  "remote_addr": "—",                "status": "LISTEN",      "pid": 700,  "process": "redis-server"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "0.0.0.0:3306",    "local_port": 3306,  "remote_addr": "—",                "status": "LISTEN",      "pid": 650,  "process": "mysqld"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "0.0.0.0:8080",    "local_port": 8080,  "remote_addr": "—",                "status": "LISTEN",      "pid": 900,  "process": "java"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "192.168.1.10:443", "local_port": 443,  "remote_addr": "93.184.216.34:443", "status": "ESTABLISHED", "pid": 1100, "process": "curl"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "192.168.1.10:52341","local_port": 52341,"remote_addr": "140.82.121.4:443", "status": "ESTABLISHED", "pid": 1200, "process": "git"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "192.168.1.10:52400","local_port": 52400,"remote_addr": "151.101.1.140:443","status": "ESTABLISHED", "pid": 1300, "process": "firefox"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "192.168.1.10:52410","local_port": 52410,"remote_addr": "172.217.14.99:443","status": "ESTABLISHED", "pid": 1300, "process": "firefox"},
    {"fd": -1, "family": "IPv6", "type": "TCP", "local_addr": "::1:5000",         "local_port": 5000, "remote_addr": "—",                "status": "LISTEN",      "pid": 1234, "process": "python3"},
    {"fd": -1, "family": "IPv4", "type": "UDP", "local_addr": "0.0.0.0:5353",     "local_port": 5353, "remote_addr": "—",                "status": "—",           "pid": 300,  "process": "mDNSResponder"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "192.168.1.10:52500","local_port": 52500,"remote_addr": "52.6.140.41:443",  "status": "TIME_WAIT",   "pid": None, "process": "—"},
    {"fd": -1, "family": "IPv4", "type": "TCP", "local_addr": "192.168.1.10:52501","local_port": 52501,"remote_addr": "34.120.54.55:443", "status": "CLOSE_WAIT",  "pid": 1300, "process": "firefox"},
]

_DEMO_INTERFACES = [
    {
        "name": "en0", "is_up": True, "speed": 1000, "mtu": 1500,
        "addresses": [
            {"family": "AF_INET", "address": "192.168.1.10", "netmask": "255.255.255.0"},
            {"family": "AF_LINK", "address": "a4:83:e7:2b:1f:c0", "netmask": None},
        ],
        "bytes_sent": 1_200_000_000, "bytes_recv": 4_800_000_000,
        "bytes_sent_fmt": "1.1 GB", "bytes_recv_fmt": "4.5 GB",
    },
    {
        "name": "lo0", "is_up": True, "speed": 0, "mtu": 16384,
        "addresses": [
            {"family": "AF_INET", "address": "127.0.0.1", "netmask": "255.0.0.0"},
            {"family": "AF_INET6", "address": "::1", "netmask": None},
        ],
        "bytes_sent": 52_000_000, "bytes_recv": 52_000_000,
        "bytes_sent_fmt": "49.6 MB", "bytes_recv_fmt": "49.6 MB",
    },
    {
        "name": "utun0", "is_up": True, "speed": 0, "mtu": 1380,
        "addresses": [
            {"family": "AF_INET6", "address": "fe80::ce81:b1c:bd2c:69e", "netmask": None},
        ],
        "bytes_sent": 0, "bytes_recv": 0,
        "bytes_sent_fmt": "0.0 B", "bytes_recv_fmt": "0.0 B",
    },
    {
        "name": "awdl0", "is_up": True, "speed": 0, "mtu": 1484,
        "addresses": [
            {"family": "AF_LINK", "address": "4a:60:f3:b2:8e:11", "netmask": None},
        ],
        "bytes_sent": 1_024_000, "bytes_recv": 512_000,
        "bytes_sent_fmt": "1000.0 KB", "bytes_recv_fmt": "500.0 KB",
    },
]


# ---------------------------------------------------------------------------
# Connection fetchers
# ---------------------------------------------------------------------------
def _get_connections():
    """Return a list of active network connections with process info.

    Uses psutil first; if it returns nothing (common on macOS without sudo),
    falls back to parsing ``lsof -i -n -P`` which works for the current user.
    In DEMO mode, returns sample data.
    """
    if DEMO_MODE:
        return _DEMO_CONNECTIONS

    # --- Try psutil first ---------------------------------------------------
    try:
        raw = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, OSError):
        raw = []

    if raw:
        conns = []
        for c in raw:
            entry = {
                "fd": c.fd,
                "family": "IPv4" if c.family.value == 2 else "IPv6",
                "type": "TCP" if c.type.value == 1 else "UDP",
                "local_addr": f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "—",
                "local_port": c.laddr.port if c.laddr else None,
                "remote_addr": f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "—",
                "status": c.status if c.status != "NONE" else "—",
                "pid": c.pid,
                "process": "—",
            }
            if c.pid:
                try:
                    entry["process"] = psutil.Process(c.pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            conns.append(entry)
        return conns

    # --- Fallback: parse lsof -----------------------------------------------
    return _get_connections_lsof()


def _get_connections_lsof():
    """Parse ``lsof -i -n -P`` to build the connections list."""
    try:
        out = subprocess.check_output(
            ["lsof", "-i", "-n", "-P"], stderr=subprocess.DEVNULL, text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    conns = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 9:
            continue

        process = parts[0]
        pid = parts[1]
        proto_raw = parts[7]
        proto = proto_raw.upper() if proto_raw.upper() in ("TCP", "UDP") else "TCP"
        addr_info = parts[8]
        status = parts[9] if len(parts) > 9 else "—"
        status = status.strip("()")

        family = "IPv6" if "IPv6" in line else "IPv4"

        if "->" in addr_info:
            local_part, remote_part = addr_info.split("->", 1)
        else:
            local_part = addr_info
            remote_part = ""

        local_port = None
        if ":" in local_part:
            port_str = local_part.rsplit(":", 1)[-1]
            if port_str.isdigit():
                local_port = int(port_str)

        conns.append({
            "fd": -1,
            "family": family,
            "type": proto,
            "local_addr": local_part or "—",
            "local_port": local_port,
            "remote_addr": remote_part or "—",
            "status": status if status else "—",
            "pid": int(pid) if pid.isdigit() else None,
            "process": process,
        })
    return conns


def _get_interfaces():
    """Return per-interface addresses and stats."""
    if DEMO_MODE:
        return _DEMO_INTERFACES

    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    io = psutil.net_io_counters(pernic=True)

    interfaces = []
    for name, addr_list in addrs.items():
        iface = {
            "name": name,
            "is_up": stats[name].isup if name in stats else False,
            "speed": stats[name].speed if name in stats else 0,
            "mtu": stats[name].mtu if name in stats else 0,
            "addresses": [],
            "bytes_sent": 0,
            "bytes_recv": 0,
        }
        for a in addr_list:
            iface["addresses"].append({
                "family": str(a.family.name),
                "address": a.address,
                "netmask": a.netmask,
            })
        if name in io:
            iface["bytes_sent"] = io[name].bytes_sent
            iface["bytes_recv"] = io[name].bytes_recv
            iface["bytes_sent_fmt"] = _fmt_bytes(io[name].bytes_sent)
            iface["bytes_recv_fmt"] = _fmt_bytes(io[name].bytes_recv)
        interfaces.append(iface)
    return interfaces


def _get_port_summary(connections):
    """Aggregate listening and established ports from connections list."""
    listening = {}
    established = {}

    source = connections if connections else _get_connections()

    for c in source:
        port = c["local_port"]
        if port is None:
            continue
        status = (c.get("status") or "").upper()
        if status == "LISTEN":
            listening.setdefault(port, []).append(c["process"])
        else:
            established.setdefault(port, []).append(c["process"])

    return {
        "listening": [
            {"port": p, "processes": list(set(procs))}
            for p, procs in sorted(listening.items())
        ],
        "established": [
            {"port": p, "processes": list(set(procs))}
            for p, procs in sorted(established.items())
        ],
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/traffic")
def api_traffic():
    with _lock:
        data = {
            "timestamps": list(traffic_history["timestamps"]),
            "speed_up": list(traffic_history["speed_up"]),
            "speed_down": list(traffic_history["speed_down"]),
            "total_sent": traffic_history["bytes_sent"][-1] if traffic_history["bytes_sent"] else 0,
            "total_recv": traffic_history["bytes_recv"][-1] if traffic_history["bytes_recv"] else 0,
            "total_sent_fmt": _fmt_bytes(traffic_history["bytes_sent"][-1]) if traffic_history["bytes_sent"] else "0 B",
            "total_recv_fmt": _fmt_bytes(traffic_history["bytes_recv"][-1]) if traffic_history["bytes_recv"] else "0 B",
        }
    return jsonify(data)


@app.route("/api/connections")
def api_connections():
    conns = _get_connections()
    return jsonify(conns)


@app.route("/api/interfaces")
def api_interfaces():
    return jsonify(_get_interfaces())


@app.route("/api/ports")
def api_ports():
    conns = _get_connections()
    return jsonify(_get_port_summary(conns))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=6100)
