import numpy as np
import app.main as m

m.load_index()

queries = [
    "बस्तर दशहरा की परंपराएँ बताइए",
    "Bastar Dussehra festival traditions",
    "What makes Bastar Dussehra unique?"
]

target_id = "bastar_0036"

target_indices = [
    i for i, d in enumerate(m._metadata)
    if d.get("record_id") == target_id or d.get("id") == target_id
]

print("\nFAISS vector count:", m._faiss_index.ntotal)
print("Metadata count:", len(m._metadata))
print("Target metadata indices:", target_indices)

if not target_indices:
    print("TARGET NOT FOUND")
    raise SystemExit

target_idx = target_indices[0]
target = m._metadata[target_idx]

print("Target title:", target.get("title"))
print("Target approval:", target.get("approved_for_rag"))
print("Target source:", target.get("source_url", ""))

for q in queries:
    print("\n" + "=" * 65)
    print("QUERY:", q)

    vector = m._embedder.encode(
        [q], normalize_embeddings=True, convert_to_numpy=True
    )
    vector = np.asarray(vector, dtype="float32")

    k = min(100, m._faiss_index.ntotal)
    distances, indices = m._faiss_index.search(vector, k)

    semantic_rank = next(
        (rank for rank, idx in enumerate(indices[0], 1)
         if int(idx) == target_idx),
        None
    )

    tokens = m.tokenize(q)
    scores = m._bm25.get_scores(tokens)
    lexical_order = np.argsort(scores)[::-1]
    lexical_rank = next(
        (rank for rank, idx in enumerate(lexical_order, 1)
         if int(idx) == target_idx),
        None
    )

    print("Semantic rank (top 100):", semantic_rank)
    print("BM25 rank (all documents):", lexical_rank)
    print("BM25 target score:", round(float(scores[target_idx]), 4))

    print("Top semantic results:")
    for rank, idx in enumerate(indices[0][:5], 1):
        idx = int(idx)
        if 0 <= idx < len(m._metadata):
            d = m._metadata[idx]
            print(rank, d.get("record_id", d.get("id")),
                  "-", d.get("title"))

    print("Top BM25 results:")
    for rank, idx in enumerate(lexical_order[:5], 1):
        idx = int(idx)
        d = m._metadata[idx]
        print(rank, d.get("record_id", d.get("id")),
              "-", d.get("title"),
              "| score:", round(float(scores[idx]), 3))
