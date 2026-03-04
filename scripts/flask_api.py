from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route("/run_clara", methods=["GET"])
def run_clara():

    print("🚀 n8n triggered Clara pipeline")

    subprocess.Popen(
        ["python", "batch_run.py"],
        cwd=r"D:\a-Zero-Cost-Automation-Pipeline\scripts",
        env={**os.environ, "OLLAMA_HOST": "http://127.0.0.1:11434"}
    )

    return jsonify({
        "status": "success",
        "message": "Clara pipeline started"
    })


@app.route("/health")
def health():
    return {"status": "Clara API running"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)