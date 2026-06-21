import os
import re
from collections import defaultdict
from datetime import datetime, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def build_client(api_key: str):
    return build("youtube", "v3", developerKey=api_key)


def resolve_channel_id(youtube, raw_input: str) -> str:
    """
    Accept a channel URL, @handle, legacy /c/ or /user/ slug, or plain name.
    Returns the canonical channel ID (UC...).
    """
    raw = raw_input.strip()

    # Direct channel ID
    if re.fullmatch(r"UC[a-zA-Z0-9_-]{22}", raw):
        return raw

    # youtube.com/channel/UC...
    m = re.search(r"youtube\.com/channel/(UC[a-zA-Z0-9_-]{22})", raw)
    if m:
        return m.group(1)

    # @handle in URL or bare (@handle or handle)
    m = re.search(r"youtube\.com/@([a-zA-Z0-9_.-]+)", raw)
    handle = m.group(1) if m else (raw.lstrip("@") if raw.startswith("@") else None)
    if handle:
        resp = youtube.channels().list(part="id", forHandle=handle).execute()
        if resp.get("items"):
            return resp["items"][0]["id"]

    # /c/customname or /user/username
    m = re.search(r"youtube\.com/(?:c|user)/([a-zA-Z0-9_.-]+)", raw)
    if m:
        slug = m.group(1)
        resp = youtube.channels().list(part="id", forUsername=slug).execute()
        if resp.get("items"):
            return resp["items"][0]["id"]

    # Fall back: search by name
    resp = (
        youtube.search()
        .list(part="snippet", q=raw, type="channel", maxResults=1)
        .execute()
    )
    if resp.get("items"):
        return resp["items"][0]["snippet"]["channelId"]

    raise ValueError(f"Could not resolve channel: {raw_input!r}")


def get_channel_info(youtube, channel_id: str) -> dict:
    resp = (
        youtube.channels()
        .list(part="snippet,contentDetails", id=channel_id)
        .execute()
    )
    if not resp.get("items"):
        raise ValueError(f"Channel not found: {channel_id}")
    item = resp["items"][0]
    return {
        "title": item["snippet"]["title"],
        "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"],
    }


def fetch_all_videos(youtube, playlist_id: str) -> list[dict]:
    """Fetch every video from the uploads playlist, handling pagination."""
    videos = []
    page_token = None

    while True:
        resp = (
            youtube.playlistItems()
            .list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=page_token,
            )
            .execute()
        )

        for item in resp.get("items", []):
            snippet = item["snippet"]
            video_id = snippet["resourceId"]["videoId"]
            # Private/deleted videos have placeholder titles
            if snippet["title"] in ("Deleted video", "Private video"):
                continue
            published_at = snippet["publishedAt"]
            videos.append(
                {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "published_at": published_at,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "dt": datetime.fromisoformat(
                        published_at.replace("Z", "+00:00")
                    ),
                }
            )

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return videos


def group_by_month(videos: list[dict]) -> dict:
    """Return {(year, month): [video, ...]} sorted newest-first."""
    grouped: dict = defaultdict(list)
    for v in videos:
        key = (v["dt"].year, v["dt"].month)
        grouped[key].append(v)
    return dict(sorted(grouped.items(), reverse=True))


def print_summary_table(grouped: dict, total: int, channel_title: str) -> None:
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    YW, MW, TW = 5, 3, 5  # content widths (padding adds 2 each)

    segs    = ['═'*(YW+2)] + ['═'*(MW+2)]*12 + ['═'*(TW+2)]
    inner_w = sum(len(s) for s in segs) + 13  # 13 internal separators

    def hline(lo, sep, ro):
        return lo + sep.join(segs) + ro

    def row(year_label, counts, row_total):
        cells = [f" {str(year_label):>{YW}} "]
        for c in counts:
            cells.append(f" {(str(c) if c else '-'):>{MW}} ")
        cells.append(f" {str(row_total):>{TW}} ")
        return "║" + "║".join(cells) + "║"

    years        = sorted({y for y, _ in grouped}, reverse=True)
    year_data    = {y: [len(grouped.get((y, m), [])) for m in range(1, 13)] for y in years}
    month_totals = [sum(year_data[y][m] for y in years) for m in range(12)]

    header = "║" + "║".join(
        [f" {'Year':>{YW}} "] + [f" {m:>{MW}} " for m in MONTHS] + [f" {'Total':>{TW}} "]
    ) + "║"

    print()
    print("╔" + "═" * inner_w + "╗")
    print(f"║{channel_title:^{inner_w}}║")
    print(hline("╠", "╦", "╣"))
    print(header)
    print(hline("╠", "╬", "╣"))
    for y in years:
        print(row(y, year_data[y], sum(year_data[y])))
    print(hline("╠", "╬", "╣"))
    print(row("Total", month_totals, total))
    print(hline("╚", "╩", "╝"))


def run(
    channel_input: str,
    api_key: str,
    year_filter: int | None = None,
    summary: bool = False,
) -> None:
    youtube = build_client(api_key)

    print(f"Resolving channel: {channel_input!r} ...")
    channel_id = resolve_channel_id(youtube, channel_input)

    info = get_channel_info(youtube, channel_id)
    print(f"Channel : {info['title']} ({channel_id})")

    print("Fetching videos (this may take a moment for large channels) ...")
    videos = fetch_all_videos(youtube, info["uploads_playlist_id"])

    if year_filter:
        videos = [v for v in videos if v["dt"].year == year_filter]

    if not videos:
        print("No videos found.")
        return

    grouped = group_by_month(videos)
    total = sum(len(v) for v in grouped.values())

    if summary:
        print_summary_table(grouped, total, info["title"])
        return

    print(f"\nFound {total} video(s)\n{'=' * 60}")
    for (year, month), vids in grouped.items():
        label = datetime(year, month, 1).strftime("%B %Y")
        print(f"\n## {label} ({len(vids)} video(s))")
        for v in vids:
            print(f"  {v['title']}")
            print(f"    {v['url']}")
