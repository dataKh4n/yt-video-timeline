#!/usr/bin/env python3
"""
YouTube Channel Video Lister

Usage:
    python main.py "<channel name or URL>"
    python main.py "<channel name or URL>" --year 2023
    python main.py "@mkbhd"
    python main.py "https://www.youtube.com/@mkbhd" --year 2024
"""
import argparse
import os
import sys

from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from youtube_agent import run

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="List all YouTube videos for a channel, grouped by month and year."
    )
    parser.add_argument(
        "channel",
        help="Channel name, @handle, or full YouTube channel URL",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Filter to a specific year (e.g. --year 2023)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a compact table of video counts per month instead of full list",
    )
    args = parser.parse_args()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        sys.exit(
            "Error: YOUTUBE_API_KEY not set. "
            "Copy .env.example to .env and add your key."
        )

    try:
        run(args.channel, api_key, year_filter=args.year, summary=args.summary)
    except ValueError as e:
        sys.exit(f"Error: {e}")
    except HttpError as e:
        sys.exit(f"YouTube API error: {e}")


if __name__ == "__main__":
    main()
