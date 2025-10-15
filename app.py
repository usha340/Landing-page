import os
import subprocess
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

# Directory to store generated HLS stream folders
STREAM_DIR = os.path.join(os.getcwd(), "streams")
os.makedirs(STREAM_DIR, exist_ok=True)

# Keep track of active FFmpeg processes
processes = {}

# ------------------------- Helper Function -------------------------
def run_ffmpeg(stream_id, rtsp_url, hls_path):
    """Run FFmpeg to convert RTSP stream to HLS and log output."""
    os.makedirs(hls_path, exist_ok=True)
    log_path = os.path.join(hls_path, "ffmpeg.log")

    # Explicit ffmpeg path (optional) – automatically works if ffmpeg is in PATH
    ffmpeg_cmd = "ffmpeg"

    cmd = [
        ffmpeg_cmd,
        "-rtsp_transport", "tcp",      # ✅ helps with stability on Windows
        "-i", rtsp_url,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-f", "hls",
        "-hls_time", "2",
        "-hls_list_size", "5",
        "-hls_flags", "delete_segments",
        os.path.join(hls_path, "index.m3u8")
    ]

    # Open log file to capture FFmpeg output
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"Running command:\n{' '.join(cmd)}\n\n")
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=log_file,
                creationflags=subprocess.CREATE_NO_WINDOW  # hide ffmpeg console
            )
            processes[stream_id] = proc
            proc.wait()
            log_file.write(f"\nFFmpeg exited with return code {proc.returncode}\n")
        except FileNotFoundError:
            log_file.write("\nError: FFmpeg not found in PATH.\n")
        except Exception as e:
            log_file.write(f"\nUnexpected error: {e}\n")

    # Remove process entry once it exits
    if stream_id in processes:
        del processes[stream_id]


# ------------------------- ROUTES -------------------------

@app.route("/start", methods=["POST"])
def start_stream():
    """Start converting RTSP stream to HLS."""
    data = request.get_json()
    rtsp_url = data.get("rtsp_url")

    if not rtsp_url:
        return jsonify({"error": "Missing RTSP URL"}), 400

    # Unique ID for each stream session
    stream_id = str(uuid.uuid4().int)[:18]
    hls_path = os.path.join(STREAM_DIR, stream_id)
    os.makedirs(hls_path, exist_ok=True)

    # Run FFmpeg in a background thread
    t = threading.Thread(target=run_ffmpeg, args=(stream_id, rtsp_url, hls_path))
    t.daemon = True
    t.start()

    # Generate HLS access URL
    hls_url = f"http://localhost:5000/streams/{stream_id}/index.m3u8"
    return jsonify({"message": "Stream started", "hls_url": hls_url})


@app.route("/stop/<stream_id>", methods=["POST"])
def stop_stream(stream_id):
    """Stop an active stream."""
    proc = processes.get(stream_id)
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        del processes[stream_id]
        return jsonify({"message": f"Stream {stream_id} stopped"})
    return jsonify({"error": "Stream not found"}), 404


@app.route("/streams/<stream_id>/<path:filename>")
def serve_stream(stream_id, filename):
    """Serve generated HLS files."""
    return send_from_directory(os.path.join(STREAM_DIR, stream_id), filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
