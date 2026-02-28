from flask import Flask, render_template, jsonify
import json
import os
import subprocess
import sys
import monitor
from datetime import datetime

SCRIPT_FOLDER = "scripts"  
LOG_FOLDER = "logs"

app = Flask(__name__)

@app.route("/")
def dashboard():
    if os.path.exists("status.json"):
        with open("status.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    total = len(data)
    changed = sum(1 for s in data.values() if s["overall_status"] == "Changed")
    no_change = sum(1 for s in data.values() if s["overall_status"] == "No Change")

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        changed=changed,
        no_change=no_change
    )


@app.route("/refresh")
def refresh():
    try:
        monitor.run_monitor()
        return jsonify({"status": "Success"})
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)})

SCRIPT_FOLDER = "scripts"
LOG_FOLDER = "logs"

# Create logs folder if not exists
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)


@app.route("/run_script/<source_id>")

def run_script(source_id):

    script_path = os.path.join(SCRIPT_FOLDER, f"{source_id}.py")

    if not os.path.exists(script_path):
        return jsonify({"status": "Error", "message": "Script not found!"})

    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"{source_id}_{timestamp}.log"
    log_path = os.path.join(LOG_FOLDER, log_filename)

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300
        )

        # Combine stdout + stderr
        full_output = (
            "STDOUT:\n" + result.stdout +
            "\n\nSTDERR:\n" + result.stderr
        )

        # Save log file
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write(full_output)

        if result.returncode == 0:
            return jsonify({
                "status": "Success",
                "output": result.stdout,
                "log_file": log_filename
            })
        else:
            return jsonify({
                "status": "Failed",
                "output": result.stderr,
                "log_file": log_filename
            })

    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "Failed",
            "message": "Script execution timed out."
        })

    except Exception as e:
        return jsonify({
            "status": "Error",
            "message": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)