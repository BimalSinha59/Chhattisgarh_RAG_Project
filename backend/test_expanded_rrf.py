import numpy as np
import app.main as m

m.load_index()

aliases = {
    "बस्तर": ["bastar"],
    "दशहरा": ["dussehra"],
    "परंपरा": ["tradition", "traditions"],
    "परंपराएँ": ["tradition", "traditions"],
    "परंपराएं": ["tradition", "traditions"],
    "त्योहार": ["festival", "festivals"],
    "उत्सव": ["festival", "festivals"],
}

queries = [
    "बस्तर दशहरा की परंपराएँ बताइए",
    "बस्तर दशहरा",
]

for q in queries:
    expanded = list(m.tokenize(q))
    for token in list(expanded):
        expanded.extend(aliases.get(token, []))
    expanded = list(dict.fromkeys(expanded))

    scores = m._bm25.get_scores(expanded)
    lexical_order = np.argsort(scores)[::-1][:m.LEXICAL_CANDIDATES]

    vector = m._embedder.encode(
        [q], normalize_embeddings=True, convert_to_numpy=True
    ).astype("float32")
    _, semantic_indices = m._faiss_index.search(
        vector, min(m.SEMANTIC_CANDIDATES, len(m._metadata))
    )

    fused = {}
    for rank, idx in enumerate(semantic_indices[0], 1):
        idx = int(idx)
        if idx >= 0:
            fused[idx] = fused.get(idx, 0) + 1 / (m.RRF_K + rank)

    for rank, idx in enumerate(lexical_order, 1):
        idx = int(idx)
        fused[idx] = fused.get(idx, 0) + 1 / (m.RRF_K + rank)

    ranked = sorted(fused, key=fused.get, reverse=True)

    print("\nQUERY:", q)
    print("Expanded tokens:", expanded)

    for target_id in ["bastar_0036", "bastar_bastar_dussehra"]:
        idx = next(
            (i for i, d in enumerate(m._metadata)
             if d.get("id") == target_id),
            None
        )
        if idx is None:
            continue

        lexical_rank = next(
            (r for r, x in enumerate(np.argsort(scores)[::-1], 1)
             if int(x) == idx),
            None
        )
        semantic_rank = next(
            (r for r, x in enumerate(semantic_indices[0], 1)
             if int(x) == idx),
            None
        )
        rrf_rank = ranked.index(idx) + 1 if idx in ranked else None

        print(
            target_id,
            "| BM25 rank:", lexical_rank,
            "| HNSW rank:", semantic_rank,
            "| simulated RRF rank:", rrf_rank
        )

    print("Simulated RRF top 5:")
    for rank, idx in enumerate(ranked[:5], 1):
        d = m._metadata[idx]
        print(rank, d.get("id"), "|", d.get("title"))
