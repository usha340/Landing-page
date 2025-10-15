
# 🎥 RTSP to HLS Streaming App

This project enables users to convert **RTSP camera streams** into **HLS format** for playback in browsers.

---

## 🧩 Project Structure

```
/CC
  ├── back_end/
  │   ├── app.py
  │   ├── requirements.txt
  │   └── streams/
  └── front_end/
      └── (UI files for RTSP input and playback)
```

---

## 🚀 Setup Instructions

### Backend Setup
```bash
cd back_end
pip install -r requirements.txt
python app.py
```
The backend starts at `http://localhost:5000`.

### Frontend Setup
Unzip and serve `/front_end` folder using any web server (e.g., VSCode Live Server).

---

## 🧠 Usage Guide

### 1. Start a Stream
Input your RTSP camera URL in the UI (or via API):
```bash
POST http://localhost:5000/start
{
  "rtsp_url": "rtsp://your-camera-url"
}
```

### 2. Watch the Stream
Access the generated HLS file in the frontend player:
```
/streams/<stream_id>/index.m3u8
```

### 3. Stop the Stream
To stop conversion:
```bash
POST http://localhost:5000/stop/<stream_id>
```

---

## 🧾 Managing Overlays (Optional Feature)

If your frontend includes overlay controls (e.g., text, logos, timestamps):
- Open the web UI.
- Choose *Overlay Settings*.
- Add custom text, logos, or timestamp overlays before starting the stream.

---

## 🧰 Requirements

- **Python 3.8+**
- **FFmpeg** installed and available in PATH
- **Flask**, **flask-cors**, and dependencies from `requirements.txt`

---

## 📦 Deliverables Checklist
- ✅ Code Repository (backend + frontend)
- ✅ API Documentation (see `API_DOCUMENTATION.md`)
- ✅ User Documentation (this README file)
