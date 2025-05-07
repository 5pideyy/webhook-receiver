from flask import Flask, request, jsonify, render_template_string, send_file
from flask_socketio import SocketIO
from datetime import datetime
import os
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
LOG_FILE = "log.txt"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Webhook Logger</title>
    <style>
        body {
            font-family: "Segoe UI", sans-serif;
            background: #f0f0f0;
            margin: 0; padding: 0;
        }
        header {
            background: #2c3e50;
            color: white;
            padding: 10px 20px;
        }
        nav {
            background: #ecf0f1;
            padding: 10px 20px;
            display: flex;
            gap: 10px;
        }
        nav button {
            padding: 8px 16px;
            border: none;
            background: #3498db;
            color: white;
            border-radius: 5px;
            cursor: pointer;
        }
        nav button:hover {
            background: #2980b9;
        }
        #content {
            padding: 20px;
        }
        pre {
            white-space: pre-wrap;
            background: #fff;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #ccc;
            max-height: 500px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <header>
    <h2>🚀 Webhook Logger Dashboard</h2>
    <p style="margin: 5px 0; font-size: 14px; color: #ccc;">
        Send your GET or POST requests to: 
        <code style="background:#333;color:#fff;padding:2px 5px;border-radius:4px;">/hook</code>
    </p>
</header>

    <nav>
        <button onclick="switchTab('realtime')">Real-Time Logs</button>
        <button onclick="loadAllLogs()">View All Logs</button>
        <button onclick="clearLogs()">Clear Logs</button>
    </nav>
    <div id="content">
        <pre id="log">Select an option to begin...</pre>
    </div>
    <script src="https://cdn.socket.io/4.6.1/socket.io.min.js"></script>
    <script>
        const socket = io();
        const logDiv = document.getElementById('log');
        let currentTab = '';

        function switchTab(tab) {
            logDiv.textContent = "Listening for logs...";
            currentTab = tab;
        }

        function loadAllLogs() {
            currentTab = 'all';
            fetch('/logs')
                .then(res => res.text())
                .then(text => logDiv.textContent = text || 'No logs yet.');
        }

        function clearLogs() {
            fetch('/clear', { method: 'POST' })
                .then(res => res.text())
                .then(text => {
                    logDiv.textContent = "Logs cleared.";
                });
        }

        socket.on('log', data => {
            if (currentTab === 'realtime') {
                logDiv.textContent += '\\n' + data;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def ui():
    return render_template_string(HTML_TEMPLATE)

@app.route('/hook', methods=['GET', 'POST'])
def webhook():
    time = datetime.utcnow().isoformat()
    headers = dict(request.headers)
    data = request.args if request.method == 'GET' else request.form

    log_entry = {
        "timestamp": time,
        "method": request.method,
        "headers": headers,
        "data": data
    }

    entry_str = json.dumps(log_entry, indent=2)

    with open(LOG_FILE, "a") as f:
        f.write(entry_str + "\n")

    socketio.emit('log', entry_str)
    return "OK", 200

@app.route('/logs')
def logs():
    if not os.path.exists(LOG_FILE):
        return "No logs yet."
    with open(LOG_FILE, "r") as f:
        return f.read()

@app.route('/clear', methods=['POST'])
def clear():
    open(LOG_FILE, "w").close()
    return "Logs cleared."

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
