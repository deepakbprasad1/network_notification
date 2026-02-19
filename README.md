# Network Status Monitor

A lightweight Python desktop application that monitors your internet connectivity in real-time and alerts you whenever the connection drops or comes back.

---

## Features

- **Real-time monitoring** — checks connectivity every 3 seconds
- **Visual status indicator** — 🟢 Online (green) / 🔴 Offline (red)
- **Popup notifications** — alerts on disconnect and reconnect with timestamps
- **Connection history** — scrollable log of all connectivity events
- **Non-blocking UI** — network checks run in background threads so the window never freezes
- **Start / Stop control** — monitoring only runs when you want it to

## How It Works

1. Click **Start Monitoring** to begin.
2. Every 3 seconds, the app sends a GET request to `https://www.google.com` (timeout: 3 s).
3. If the request succeeds → **Online**; if it fails for any reason → **Offline**.
4. When the status *changes* (online → offline or vice-versa), a popup notification appears with a timestamp.
5. All events are recorded in the scrollable history panel.
6. Click **Stop Monitoring** at any time to pause checks.

## Installation

### Prerequisites

- Python 3.8 or newer
- `pip` (comes with Python)
- **tkinter** (included with most Python installations)

### Install dependencies

```bash
cd network-monitor
pip install -r requirements.txt
```

## How to Run

```bash
python main.py
```

The GUI window will open — click **Start Monitoring** to begin checking your connection.

## Project Structure

```
network-monitor/
│
├── main.py              # Application source code
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Future Improvements

- **Logging to file** — persist connection history across sessions
- **System tray support** — minimise to tray and show balloon notifications
- **Custom check URL / interval** — let the user configure via the GUI
- **Latency display** — show response time alongside status
- **Connection uptime / downtime stats** — track percentages over time
- **Dark / light theme toggle** — user-selectable colour scheme
- **Cross-platform notifications** — native OS notifications (Windows toast, macOS alerts)
