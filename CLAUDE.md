# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

CLI tool that accepts a YouTube channel name, @handle, or URL and prints every video grouped by month and year with titles and links. Uses the YouTube Data API v3.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your YOUTUBE_API_KEY
```

Get a YouTube Data API v3 key from the [Google Cloud Console](https://console.cloud.google.com/) — enable the "YouTube Data API v3" for the project.

## Running

```bash
python main.py "@mkbhd"
python main.py "https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ"
python main.py "Marques Brownlee" --year 2023
```

## Architecture

Two files contain all logic:

- **`youtube_agent.py`** — pure functions with no CLI concerns: `resolve_channel_id`, `get_channel_info`, `fetch_all_videos`, `group_by_month`, and `run`. All YouTube API calls live here.
- **`main.py`** — argument parsing, env loading, and error formatting. Calls `run()` from `youtube_agent.py`.

### Channel resolution order (`resolve_channel_id`)

1. Bare `UC...` channel ID
2. `/channel/UC...` URL pattern
3. `@handle` in URL or as bare input → `channels.list(forHandle=...)`
4. `/c/slug` or `/user/slug` → `channels.list(forUsername=...)`
5. Fallback: `search.list(type=channel)` by name

### Video fetching

Videos come from the channel's **uploads playlist** (ID = channel's `contentDetails.relatedPlaylists.uploads`). The playlist items API is paginated at 50 items per page; `fetch_all_videos` loops until `nextPageToken` is absent. Deleted/private videos are filtered by title.

### API quota

Each run costs roughly: 1 (resolve) + 1 (channel info) + N/50 (playlist pages) units. A channel with 500 videos costs ~12 units. The daily free quota is 10,000 units.
