# Mor Chhattisgarh — Hybrid RAG (HNSW + BM25)

This backend keeps the existing `/chat` request/response shape and combines:

1. **Semantic retrieval:** multilingual SentenceTransformer embeddings + FAISS `IndexHNSWFlat` approximate nearest-neighbor search.
2. **Lexical retrieval:** BM25 via `rank-bm25`, using Unicode-aware tokenization for Latin and Devanagari text.
3. **Hybrid fusion:** Reciprocal Rank Fusion (RRF), which combines the two rankings without treating their raw scores as directly comparable.
4. **Answer generation:** optional Ollama; if Ollama is unavailable, the API transparently returns retrieved excerpts.

PostgreSQL and GIN are not required for this implementation.

## Important corpus review note

The included `data/faiss_metadata.json` snapshot had 1,177 records, but the reviewed corpus currently marks only **1 record** with `approved_for_rag=true`. The default index build intentionally indexes approved records only. Do not mark records approved unless the facts, source, language/translation, and reuse permissions have been checked.

For a temporary local retrieval smoke test, you can include unreviewed records using `--include-unreviewed`. This is for testing plumbing only; do not treat unreviewed output as verified research.

## 1. Install dependencies (Windows PowerShell)

Run from this `backend` directory:

```powershell
python -m pip install -r requirements.txt
```

The first index build downloads the multilingual embedding model and needs internet access. Use a 64-bit Python environment compatible with `faiss-cpu`.

## 2. Build the HNSW semantic index

Reviewed records only (recommended):

```powershell
python scripts/build_index.py --corpus data/reviewed_corpus.jsonl
```

Temporary smoke test using the entire current corpus:

```powershell
python scripts/build_index.py --corpus data/reviewed_corpus.jsonl --include-unreviewed
```

The script writes a **new** `data/faiss_hnsw.index` and aligned `data/faiss_hnsw_metadata.json`; it does not overwrite the old `faiss.index` or `faiss_metadata.json`.

## 3. Run the backend

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Check:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

When the new index loads, `/health` should report `semantic_index: HNSW`, `lexical_index: BM25`, and `retrieval_method: hybrid_hnsw_bm25_rrf`.

## 4. Test `/chat`

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/chat" `
  -ContentType "application/json" `
  -Body '{"question":"Tell me about Bastar Dussehra","language":"en"}'
```

Existing frontend compatibility is preserved: request fields remain `question` and `language`; response fields remain `answer`, `sources`, `retrieval_ready`, and `generation_mode`.

## 5. Optional answer generation with Ollama

Install Ollama separately and pull the configured model:

```powershell
ollama pull qwen2.5:7b
```

Ensure Ollama is running. If it is unavailable, retrieval still runs and `generation_mode` is `retrieval_only`.

## How hybrid ranking works

- HNSW produces a semantic nearest-neighbor ranking.
- BM25 produces a term-match ranking.
- RRF combines ranks using `1 / (RRF_K + rank)`.
- Top results are returned after duplicate source/title pairs are collapsed.

Tune `TOP_K`, `SEMANTIC_CANDIDATES`, `LEXICAL_CANDIDATES`, and `RRF_K` through environment variables if needed.
