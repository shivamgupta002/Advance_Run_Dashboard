from flask import Flask, render_template, jsonify
import json
import os
import subprocess
import sys
import monitor

app = Flask(__name__)

SCRIPT_FOLDER = "scripts"  # Folder where your scripts are stored


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


@app.route("/run_script/<source_id>")
def run_script(source_id):

    script_path = os.path.join(SCRIPT_FOLDER, f"{source_id}.py")

    if not os.path.exists(script_path):
        return jsonify({"status": "Error", "message": "Script not found!"})

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            return jsonify({
                "status": "Success",
                "output": result.stdout or "Script executed successfully."
            })
        else:
            return jsonify({
                "status": "Failed",
                "output": result.stderr or "Script failed."
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