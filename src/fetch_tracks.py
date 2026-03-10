import os
import re
import time
import requests
import csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYLISTS_PATH = os.path.join(ROOT, "data", "playlists.csv")
OUTPUT_PATH = os.path.join(ROOT, "data", "tracks.csv")


# Genre name → everynoise slug, e.g. "k-pop" → "kpop", "r&b" → "rb"
def genre_to_slug(genre):
    return re.sub(r"[^a-z0-9]", "", genre.lower())


def fetch_artists(slug, retries=5):
    """Return list of artist name strings from the everynoise genre page."""
    url = f"https://everynoise.com/engenremap-{slug}.html"
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 404:
                return []
            r.raise_for_status()
            return re.findall(r'class="genre scanme"[^>]*>([^<]+)<a', r.text)
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError) as e:
            wait = 2 ** attempt
            print(f"  Timeout ({e.__class__.__name__}), retrying in {wait}s... (attempt {attempt+1}/{retries})")
            time.sleep(wait)
    print(f"  Giving up on {slug} after {retries} attempts.")
    return []


with open(PLAYLISTS_PATH, newline="", encoding="utf-8") as f:
    playlists = list(csv.DictReader(f))

# Resume support: skip genres already written
already_done = set()
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            already_done.add(row["playlist_id"])

remaining = [p for p in playlists if p["playlist_id"] not in already_done]
print(f"Total genres: {len(playlists)}, already fetched: {len(already_done)}, remaining: {len(remaining)}")


