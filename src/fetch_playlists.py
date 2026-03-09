import os
import re
import csv
import requests

EVERYNOISE_URL = "https://everynoise.com/everynoise1d.html"

print(f"Fetching playlist index from {EVERYNOISE_URL} ...")

response = requests.get(EVERYNOISE_URL, timeout=60)
response.raise_for_status()

html = response.text

pattern = re.compile(
    r'spotify:playlist:([A-Za-z0-9]+)[^>]*>'   # capture playlist ID
    r'.*?'                                       # skip icon markup
    r'<a href="everynoise1d-[^"]+?"[^>]*?>([^<]+)</a>',  # capture genre name
    re.DOTALL,
)

playlists = []
seen_ids = set()

for match in pattern.finditer(html):
    playlist_id, genre_name = match.group(1), match.group(2).strip()
    if playlist_id not in seen_ids:
        seen_ids.add(playlist_id)
        playlists.append((genre_name, playlist_id))

print(f"Found {len(playlists)} playlists.")

os.makedirs("data", exist_ok=True)

output_path = "data/playlists.csv"

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["genre", "playlist_id"])
    for name, pid in playlists:
        writer.writerow([name, pid])

print(f"Saved to: {output_path}")
