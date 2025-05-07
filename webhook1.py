from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import os
import json
from collections import deque

app = Flask(__name__)
LOG_FILE = "log.json"

# HTML template with Bootstrap for a better UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Webhook Catcher</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 900px; }
        h1 { color: #333; }
        textarea { width: 100%; height: 200px; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        .btn { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Webhook Received!</h1>
        <p><strong>Timestamp:</strong> {{ time }}</p>
        <p><strong>Method:</strong> {{ method }}</p>
        <p><strong>Headers:</strong></p>
        <textarea readonly>{{ headers }}</textarea>
        <p><strong>Data:</strong></p>
        <textarea readonly>{{ data }}</textarea>
        <br>
        <a href="/" class="btn btn-primary">Back to Webhook</a>
        <a href="/latest" class="btn btn-info">View Latest</a>
        <a href="/clear" class="btn btn-danger">Clear Log</a>
        <a href="/logs" class="btn btn-secondary">View All Logs</a>
        <a href="/download" class="btn btn-success">Download Logs</a>
    </div>
</body>
</html>
"""

# In-memory log store to display the latest logs (for faster access)
log_deque = deque(maxlen=100)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    time = datetime.utcnow().isoformat()
    headers = dict(request.headers)
    data = request.args if request.method == 'GET' else request.form

    # Create a log entry as a dictionary
    log_entry = {
        "timestamp": time,
        "method": request.method,
        "headers": headers,
        "data": data
    }

    # Save the log entry in memory (for the latest logs view)
    log_deque.append(log_entry)

    # Also log the request into a file (log in JSON format for better parsing)
    with open(LOG_FILE, "a") as f:
        json.dump(log_entry, f)
        f.write("\n")

    return render_template_string(
        HTML_TEMPLATE,
        time=time,
        method=request.method,
        headers=json.dumps(headers, indent=4),
        data=json.dumps(data, indent=4)
    )

@app.route('/latest')
def latest():
    # Show the most recent log entry
    if len(log_deque) > 0:
        latest_log = log_deque[-1]
        return jsonify(latest_log)
    else:
        return "No logs yet!"

@app.route('/clear')
def clear():
    # Clear the log file and in-memory log store
    open(LOG_FILE, "w").close()
    log_deque.clear()
    return "Log cleared."

@app.route('/logs')
def logs():
    # Show all logs from the log file
    if not os.path.exists(LOG_FILE):
        return "No logs yet!"
    
    with open(LOG_FILE, "r") as f:
        logs = f.readlines()

    logs_content = ''.join(logs)
    return f"<pre>{logs_content if logs_content else 'No data yet.'}</pre>"

@app.route('/download')
def download_logs():
    # Provide the option to download the log file
    if not os.path.exists(LOG_FILE):
        return "No logs to download yet."
    
    return jsonify({
        "download_url": f"/static/{LOG_FILE}",
        "message": "Click to download the logs."
    })

# To make sure you can access static files (logs for download)
@app.route('/static/<filename>')
def serve_log(filename):
    return app.send_static_file(filename)

# Start the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))  # Use the PORT environment variable if available
    app.run(host='0.0.0.0', port=port)
