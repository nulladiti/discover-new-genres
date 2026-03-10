import os
import re
import time
import requests

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

