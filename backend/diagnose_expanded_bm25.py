import app.main as m
import numpy as np

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

for q in ["बस्तर दशहरा की परंपराएँ बताइए", "बस्तर दशहरा"]:
    tokens = list(m.tokenize(q))
    for token in list(tokens):
        tokens.extend(aliases.get(token, []))
    tokens = list(dict.fromkeys(tokens))

    scores = m._bm25.get_scores(tokens)
    order = np.argsort(scores)[::-1]

    print("\nQUERY:", q)
    print("Expanded tokens:", tokens)
    print("\nTop 10 BM25 results:")

    shown = 0
    for idx in order:
        idx = int(idx)
        if scores[idx] <= 0:
            break

        d = m._metadata[idx]
        print(
            f"score={scores[idx]:.3f}",
            "| id=", d.get("id"),
            "| title=", d.get("title"),
            "| approved=", d.get("approved_for_rag"),
            "| status=", d.get("review_status"),
        )
        shown += 1
        if shown >= 10:
            break
