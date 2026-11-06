"""Build a normalized-vector FAISS HNSW index for semantic retrieval."""
import argparse
import json
import os
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="data/reviewed_corpus.jsonl")
    ap.add_argument("--index", default="data/faiss_hnsw.index")
    ap.add_argument("--metadata", default="data/faiss_hnsw_metadata.json")
    ap.add_argument("--include-unreviewed", action="store_true",
                    help="Development/demo only; includes records not approved for RAG.")
    ap.add_argument("--hnsw-m", type=int, default=32,
                    help="HNSW graph connectivity (M).")
    ap.add_argument("--ef-construction", type=int, default=200)
    args = ap.parse_args()

    rows = []
    with open(args.corpus, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            approved = row.get("approved_for_rag") is True
            if (approved or args.include_unreviewed) and row.get("text", "").strip():
                rows.append(row)
    if not rows:
        raise SystemExit(
            "No eligible records. Review corpus and set approved_for_rag=true. "
            "For a temporary local smoke test only, add --include-unreviewed."
        )

    model_name = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    texts = [f"{r.get('title', '')}\n{r.get('text', '')}" for r in rows]
    vectors = model.encode(
        texts, normalize_embeddings=True, show_progress_bar=True,
        convert_to_numpy=True,
    )
    vectors = np.asarray(vectors, dtype="float32")
    dim = vectors.shape[1]

    # Inner product on normalized vectors approximates cosine similarity.
    index = faiss.IndexHNSWFlat(dim, args.hnsw_m, faiss.METRIC_INNER_PRODUCT)
    index.hnsw.efConstruction = args.ef_construction
    index.hnsw.efSearch = max(64, 2 * 10)
    index.add(vectors)

    Path(args.index).parent.mkdir(parents=True, exist_ok=True)
    Path(args.metadata).parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, args.index)
    with open(args.metadata, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Built HNSW index with {len(rows)} records -> {args.index}")
    print(f"Saved aligned metadata -> {args.metadata}")


if __name__ == "__main__":
    main()
