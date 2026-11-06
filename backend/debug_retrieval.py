from app.main import load_index, retrieve, _metadata

print("Loading hybrid RAG index...")
load_index()

import app.main as m

print("\n--- INDEX STATUS ---")
print("FAISS loaded:", m._faiss_index is not None)
print("Embedder loaded:", m._embedder is not None)
print("BM25 loaded:", m._bm25 is not None)
print("Metadata records:", len(m._metadata))

questions = [
    "बस्तर दशहरा की परंपराएँ बताइए",
    "छत्तीसगढ़ में प्रमुख खाने की चीजें क्या हैं?",
    "What are the famous tourist places in Chhattisgarh?"
]

for question in questions:
    print("\n" + "=" * 70)
    print("QUESTION:", question)

    results = retrieve(question)

    if not results:
        print("NO RESULTS")
        continue

    for rank, doc in enumerate(results, start=1):
        print(f"\n[{rank}] {doc.get('title', 'Untitled')}")
        print("ID:", doc.get("record_id", doc.get("id", "unknown")))
        print("RRF:", round(doc.get("score", 0), 5))
        print("Semantic:", doc.get("semantic_score"))
        print("BM25:", doc.get("bm25_score"))
        print("Approved:", doc.get("approved_for_rag"))
        print("Text:", (doc.get("text") or "")[:350].replace("\n", " "))
