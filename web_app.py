import os
import threading
import webbrowser
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from googleapiclient.errors import HttpError

from youtube_agent import (
    build_client,
    fetch_all_videos,
    get_channel_info,
    group_by_month,
    resolve_channel_id,
)

load_dotenv()

app = Flask(__name__)

# In-memory history for the lifetime of the server process
_history: list[dict] = []
_next_id = 1


@app.route("/")
def index():
    return render_template("index.html")


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

        grouped = group_by_month(videos)

        groups = []
        for (year, month), vids in grouped.items():
            groups.append({
                "label": datetime(year, month, 1).strftime("%B %Y"),
                "year": year,
                "month": month,
                "videos": [
                    {
                        "title": v["title"],
                        "url": v["url"],
                        "published_at": v["published_at"],
                    }
                    for v in vids
                ],
            })

        total = sum(len(g["videos"]) for g in groups)
        result = {
            "channel_title": info["title"],
            "channel_id": channel_id,
            "total": total,
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
    print(f"Starting YouTube Channel Explorer at {url}")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    app.run(host=host, port=port, debug=False, use_reloader=False)
