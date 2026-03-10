import os
import re
import time
import requests
import csv

# ---------------------------
# Paths
# ---------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYLISTS_PATH = os.path.join(ROOT, "data", "playlists.csv")
OUTPUT_PATH = os.path.join(ROOT, "data", "artists.csv")


# ---------------------------
# Helper functions
# ---------------------------

# Genre name → everynoise slug, e.g. "k-pop" → "kpop", "r&b" → "rb"
def genre_to_slug(genre):
    """Convert a genre name to an EveryNoise URL-friendly slug."""
    return re.sub(r"[^a-z0-9]", "", genre.lower())


def fetch_artists(slug, retries=5):
    """Return list of artist name strings from the everynoise genre page.

    Args:
        slug (str): Genre slug for the URL.
        retries (int): Number of retries in case of timeout or connection error.

    Returns:
        List[str]: List of artist names.
    """
    url = f"https://everynoise.com/engenremap-{slug}.html"
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 404:
                return []
            r.raise_for_status()
            # Extract artist names using regex
            return re.findall(r'class="genre scanme"[^>]*>([^<]+)<a', r.text)
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError) as e:
            wait = 2 ** attempt
            print(f"  Timeout ({e.__class__.__name__}), retrying in {wait}s... (attempt {attempt+1}/{retries})")
            time.sleep(wait)
    print(f"  Giving up on {slug} after {retries} attempts.")
    return []


# ---------------------------
# Load playlists and determine remaining
# ---------------------------

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


# ---------------------------
# Fetch artists and write to CSV
# ---------------------------

# Write header only if file doesn't exist or is empty
write_header = not os.path.exists(OUTPUT_PATH) or os.path.getsize(OUTPUT_PATH) == 0

with open(OUTPUT_PATH, "a", newline="", encoding="utf-8") as out:
    writer = csv.writer(out)
    if write_header:
        writer.writerow(["genre", "playlist_id", "artist_name"])

    for i, row in enumerate(remaining):
        genre = row["genre"]
        playlist_id = row["playlist_id"]
        slug = genre_to_slug(genre)

        artists = fetch_artists(slug)

        for artist in artists:
            writer.writerow([genre, playlist_id, artist.strip()])

        out.flush()
        print(f"[{len(already_done) + i + 1}/{len(playlists)}] {genre} ({slug}): {len(artists)} artists")

        time.sleep(0.5)

print(f"\nDone. Saved to {OUTPUT_PATH}")

