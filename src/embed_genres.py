import os
import csv
import numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer

# ---------------------------
# Paths
# ---------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ARTISTS_PATH = os.path.join(ROOT, "data", "artists.csv")
EMBEDDINGS_OUT = os.path.join(ROOT, "data", "genre_embeddings.npy")
INDEX_OUT = os.path.join(ROOT, "data", "genre_index.csv")

# ---------------------------------------------------------
# Load and organize text data by genre
# ---------------------------------------------------------

# genre -> list of text pieces to embed
genre_texts = defaultdict(list)

with open(ARTISTS_PATH, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        genre = row["genre"].strip()
        artist = row.get("artist_names", "").strip()

        if genre not in genre_texts:
            # Anchor the embedding with the genre name (weighted 3x)
            genre_texts[genre].extend([genre] * 3)

        if artist:
            genre_texts[genre].append(artist)

print(f"Loaded text for {len(genre_texts)} genres.")

# -----------------------------
# Embed
# -----------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

genres = list(genre_texts.keys())
print(f"Embedding {len(genres)} genres...")

# Store embeddings here
genre_embeddings = []

for i, genre in enumerate(genres):
    # Convert texts into embedding vectors and average them
    texts = genre_texts[genre]
    vecs = model.encode(texts, batch_size=256, show_progress_bar=False, convert_to_numpy=True)
    genre_embeddings.append(vecs.mean(axis=0))

    if (i + 1) % 500 == 0:
        print(f"  {i + 1}/{len(genres)} genres embedded...")

embeddings_matrix = np.array(genre_embeddings)  # shape: (n_genres, 384)
