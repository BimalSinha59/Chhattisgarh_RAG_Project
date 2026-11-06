import numpy as np
import app.main as m

m.load_index()

queries = [
    "बस्तर दशहरा की परंपराएँ बताइए",
    "बस्तर दशहरा",
    "Bastar Dussehra festival traditions",
]

target_ids = {"bastar_0036", "bastar_bastar_dussehra"}

for q in queries:
    print("\n" + "=" * 65)
    print("QUERY:", q)
    print("TOKENS:", m.tokenize(q))

    scores = m._bm25.get_scores(m.tokenize(q))
    order = np.argsort(scores)[::-1]

    for target_id in target_ids:
        idx = next(
            (i for i, d in enumerate(m._metadata)
             if d.get("id") == target_id or d.get("record_id") == target_id),
            None
        )
        if idx is not None:
            rank = int(np.where(order == idx)[0][0]) + 1
            print(
                target_id,
                "| BM25 rank:", rank,
                "| score:", round(float(scores[idx]), 4)
            )

    print("\nTop 5 BM25:")
    for idx in order[:5]:
        d = m._metadata[int(idx)]
        print(
            d.get("id", d.get("record_id")),
            "|", d.get("title"),
            "| score:", round(float(scores[int(idx)]), 4)
        )

print("\n" + "=" * 65)
print("RETRIEVE FUNCTION SOURCE")
print("=" * 65)

import inspect
print(inspect.getsource(m.retrieve))
