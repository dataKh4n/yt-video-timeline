# Growline

A Python CLI tool that fetches every video from any YouTube channel and displays them grouped by month and year — as a full list with links or as a clean pivot table.

---

## Prerequisites

- Python 3.10+
- A [YouTube Data API v3](https://console.cloud.google.com/) key (free)

### Getting a YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services → Library**
4. Search for **YouTube Data API v3** and click **Enable**
5. Go to **APIs & Services → Credentials**
6. Click **+ Create Credentials → API Key**
7. Copy the generated key

> **Tip:** After copying, restrict the key to "YouTube Data API v3" only under *API restrictions* to limit exposure if the key is ever leaked.

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/dataKh4n/tubeline.git
cd tubeline

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Add your API key
cp .env.example .env
# Open .env and replace the placeholder with your key
```

`.env` file should look like:
```
YOUTUBE_API_KEY=AIzaSy...your_key_here
```

---

## Usage

```bash
python3 main.py "<channel>"
```

The `<channel>` argument accepts any of the following formats:

| Format | Example |
|--------|---------|
| `@handle` | `@mkbhd` |
| Full URL | `https://www.youtube.com/@mkbhd` |
| Channel name | `"Marques Brownlee"` |
| Channel ID | `UCBJycsmduvYEL83R_U4JriQ` |

---

## Examples

### Full video list for a channel

```bash
python3 main.py "@mkbhd"
python3 main.py "@Kevin Stratvert"
python3 main.py "https://www.youtube.com/@LinusTechTips"
```

```
Channel : MKBHD (UCBJycsmduvYEL83R_U4JriQ)
Fetching videos ...

Found 1600 video(s)
============================================================

## June 2024 (5 video(s))
  The Nothing Phone (2a) Review
    https://www.youtube.com/watch?v=abc123
  Spatial Video on Vision Pro is Crazy
    https://www.youtube.com/watch?v=def456
  ...
```

### Filter to a specific year

```bash
python3 main.py "@mkbhd" --year 2023
python3 main.py "@NetworkChuck" --year 2022
```

### Summary pivot table — videos per month × year

```bash
python3 main.py "@mkbhd" --summary
```

```
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║                                       MKBHD                                          ║
╠═══════╦═════╦═════╦═════╦═════╦═════╦═════╦═════╦═════╦═════╦═════╦═════╦═════╦═══════╣
║  Year ║ Jan ║ Feb ║ Mar ║ Apr ║ May ║ Jun ║ Jul ║ Aug ║ Sep ║ Oct ║ Nov ║ Dec ║ Total ║
╠═══════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═══════╣
║  2024 ║   4 ║   3 ║   5 ║   4 ║   6 ║   5 ║   4 ║   5 ║   5 ║   5 ║   4 ║   4 ║    54 ║
║  2023 ║   5 ║   4 ║   6 ║   5 ║   5 ║   4 ║   5 ║   6 ║   5 ║   4 ║   5 ║   4 ║    58 ║
...
╠═══════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═════╬═══════╣
║ Total ║  90 ║  80 ║  95 ║  85 ║  88 ║  82 ║  84 ║  87 ║  83 ║  80 ║  82 ║  75 ║  1031 ║
╚═══════╩═════╩═════╩═════╩═════╩═════╩═════╩═════╩═════╩═════╩═════╩═════╩═════╩═══════╝
```

### Pivot table filtered by year

```bash
python3 main.py "@Kevin Stratvert" --summary --year 2024
```

---

## API Quota

The YouTube Data API v3 has a free daily quota of **10,000 units**. A typical run costs:

| Channel size | Approx. quota used |
|---|---|
| ~100 videos | ~4 units |
| ~500 videos | ~12 units |
| ~1,000 videos | ~22 units |

You won't hit the limit under normal personal use.

---

## Project Structure

```
tubeline/
├── main.py            # CLI entry point (argument parsing)
├── youtube_agent.py   # All YouTube API logic
├── requirements.txt   # Dependencies
├── .env.example       # API key template
└── .env               # Your API key (never commit this)
```
