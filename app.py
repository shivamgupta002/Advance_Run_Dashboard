from flask import Flask, render_template, jsonify
import json
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

STATUS_FILE = "status.json"
LOG_FOLDER = "logs"

os.makedirs(LOG_FOLDER, exist_ok=True)


# ---------------- DASHBOARD ---------------- #
@app.route("/")
def dashboard():

    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    total = len(data)
    changed = sum(1 for s in data.values() if s["overall_status"] == "Changed")
    no_change = total - changed

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        changed=changed,
        no_change=no_change
    )


# ---------------- RUN SCRIPT ---------------- #
@app.route("/run_script/<source_id>")
def run_script(source_id):

    log_file = f"{source_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(LOG_FOLDER, log_file)

    try:
        result = subprocess.run(
            ["python", "monitor.py", source_id],
            capture_output=True,
            text=True
        )

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)
            f.write("\n")
            f.write(result.stderr)

        status = "Success" if result.returncode == 0 else "Failed"

        return jsonify({
            "status": status,
            "output": result.stdout,
            "log_file": log_file,
            "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        return jsonify({
            "status": "Error",
            "message": str(e)
        })


# ---------------- REFRESH MONITOR ---------------- #
@app.route("/refresh")
def refresh():
    try:
        subprocess.run(["python", "monitor.py"])
        return jsonify({"status": "Refreshed"})
    except:
        return jsonify({"status": "Error"})


if __name__ == "__main__":
    app.run(debug=True)