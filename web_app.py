import os
import threading
import webbrowser
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from googleapiclient.errors import HttpError

from youtube_agent import (
    build_client,
    enrich_videos,
    extract_video_id,
    fetch_all_videos,
    fetch_single_video,
    get_channel_info,
    group_by_month,
    resolve_channel_id,
)

load_dotenv()

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True

# In-memory history for the lifetime of the server process
_history: list[dict] = []
_next_id = 1


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/offline")
def offline():
    return render_template("offline.html")


@app.route("/sw.js")
def service_worker():
    resp = app.send_static_file("sw.js")
    resp.headers["Service-Worker-Allowed"] = "/"
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.route("/.well-known/assetlinks.json")
def assetlinks():
    resp = app.send_static_file("assetlinks.json")
    resp.headers["Content-Type"] = "application/json"
    return resp


@app.route("/api/search", methods=["POST"])
def search():
    global _next_id
    data = request.get_json(force=True)
    channel_input = (data.get("channel") or "").strip()
    year_raw = data.get("year")
    year_filter = int(year_raw) if year_raw else None

    if not channel_input:
        return jsonify({"error": "Channel is required"}), 400

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return jsonify({"error": "YOUTUBE_API_KEY not set in .env"}), 500

    try:
        youtube = build_client(api_key)
        channel_id = resolve_channel_id(youtube, channel_input)
        info = get_channel_info(youtube, channel_id)
        videos = fetch_all_videos(youtube, info["uploads_playlist_id"])

        if year_filter:
            videos = [v for v in videos if v["dt"].year == year_filter]

        enrich_videos(youtube, videos)
        grouped = group_by_month(videos)

        groups = []
        for (year, month), vids in grouped.items():
            g_views = sum(v["views"] for v in vids)
            g_likes = sum(v["likes"] for v in vids)
            g_comments = sum(v["comments"] for v in vids)
            g_duration = sum(v["duration_seconds"] for v in vids)
            groups.append({
                "label": datetime(year, month, 1).strftime("%B %Y"),
                "year": year,
                "month": month,
                "views": g_views,
                "likes": g_likes,
                "comments": g_comments,
                "duration_seconds": g_duration,
                "videos": [
                    {
                        "title": v["title"],
                        "url": v["url"],
                        "published_at": v["published_at"],
                        "views": v["views"],
                        "likes": v["likes"],
                        "comments": v["comments"],
                        "duration_seconds": v["duration_seconds"],
                    }
                    for v in vids
                ],
            })

        total = sum(len(g["videos"]) for g in groups)
        totals = {
            "videos": total,
            "views": sum(g["views"] for g in groups),
            "likes": sum(g["likes"] for g in groups),
            "comments": sum(g["comments"] for g in groups),
            "duration_seconds": sum(g["duration_seconds"] for g in groups),
        }
        result = {
            "channel_title": info["title"],
            "channel_id": channel_id,
            "total": total,
            "totals": totals,
            "year_filter": year_filter,
            "groups": groups,
        }

        entry = {
            "id": _next_id,
            "channel_input": channel_input,
            "channel_title": info["title"],
            "year_filter": year_filter,
            "total": total,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "result": result,
        }
        _history.append(entry)
        _next_id += 1

        return jsonify({"result": result, "history_id": entry["id"]})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except HttpError as e:
        return jsonify({"error": f"YouTube API error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/video", methods=["POST"])
def video():
    data = request.get_json(force=True)
    raw = (data.get("video") or "").strip()
    if not raw:
        return jsonify({"error": "Video URL or ID is required"}), 400

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return jsonify({"error": "YOUTUBE_API_KEY not set in .env"}), 500

    vid = extract_video_id(raw)
    if not vid:
        return jsonify({"error": "Could not find a video ID in that link"}), 400

    try:
        youtube = build_client(api_key)
        return jsonify({"video": fetch_single_video(youtube, vid)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except HttpError as e:
        return jsonify({"error": f"YouTube API error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "Message required"}), 400
    entry = (
        f"[{datetime.now().isoformat(timespec='seconds')}] "
        f"{data.get('type', 'Feedback')} | {data.get('email') or 'anonymous'}\n{msg}\n\n"
    )
    with open(os.path.join(os.path.dirname(__file__), "feedback.log"), "a", encoding="utf-8") as f:
        f.write(entry)
    return jsonify({"ok": True})


@app.route("/api/history")
def get_history():
    return jsonify([
        {k: v for k, v in h.items() if k != "result"}
        for h in _history
    ])


@app.route("/api/history/<int:history_id>")
def get_history_item(history_id: int):
    for h in _history:
        if h["id"] == history_id:
            return jsonify(h["result"])
    return jsonify({"error": "Not found"}), 404


def start(host: str = "127.0.0.1", port: int = 5000) -> None:
    url = f"http://{host}:{port}"
    print(f"Starting Growline at {url}")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    app.run(host=host, port=port, debug=False, use_reloader=False)
