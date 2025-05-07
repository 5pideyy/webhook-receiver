from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os

app = Flask(__name__)
LOG_FILE = "log.txt"

# HTML frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Webhook Catcher</title>
    <style>
        body { font-family: sans-serif; background: #f5f5f5; padding: 20px; }
        h1 { color: #333; }
        textarea { width: 100%; height: 200px; }
        a { margin-right: 15px; }
    </style>
</head>
<body>
    <h1>Webhook Received!</h1>
    <p><strong>Timestamp:</strong> {{ time }}</p>
    <p><strong>Method:</strong> {{ method }}</p>
    <p><strong>Headers:</strong></p>
    <textarea readonly>{{ headers }}</textarea>
    <p><strong>Data:</strong></p>
    <textarea readonly>{{ data }}</textarea>
    <br><br>
    <a href="/">Back to Webhook</a>
    <a href="/latest">View Latest</a>
    <a href="/clear">Clear Log</a>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def webhook():
    time = datetime.utcnow().isoformat()
    headers = dict(request.headers)
    data = request.args if request.method == 'GET' else request.form

    # Log the request
    log_entry = f"{time} | {request.method} | {data}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

    return render_template_string(
        HTML_TEMPLATE,
        time=time,
        method=request.method,
        headers=headers,
        data=data
    )

@app.route('/latest')
def latest():
    if not os.path.exists(LOG_FILE):
        return "No logs yet!"
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    return f"<pre>{lines[-1] if lines else 'No data yet.'}</pre>"

@app.route('/clear')
def clear():
    open(LOG_FILE, "w").close()
    return "Log cleared."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
