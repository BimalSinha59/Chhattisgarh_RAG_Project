import numpy as np
import app.main as m

m.load_index()

def expand_hindi_tokens(question):
    tokens = m.tokenize(question)

    aliases = {
        "बस्तर": ["bastar"],
        "दशहरा": ["dussehra"],
        "परंपरा": ["tradition", "traditions"],
        "परंपराएँ": ["tradition", "traditions"],
        "परंपराएं": ["tradition", "traditions"],
        "त्योहार": ["festival", "festivals"],
        "उत्सव": ["festival", "festivals"],
    }

    expanded = list(tokens)

    for token in tokens:
        expanded.extend(aliases.get(token, []))

    return list(dict.fromkeys(expanded))

queries = [
    "बस्तर दशहरा की परंपराएँ बताइए",
    "बस्तर दशहरा",
]

for q in queries:
    tokens = expand_hindi_tokens(q)
    scores = m._bm25.get_scores(tokens)
    order = np.argsort(scores)[::-1]

    print("\nQUERY:", q)
    print("Expanded tokens:", tokens)

    for rank, idx in enumerate(order[:10], 1):
        d = m._metadata[int(idx)]
        print(
            rank,
            "| ID:", d.get("id"),
            "| Title:", d.get("title"),
            "| BM25:", round(float(scores[int(idx)]), 4)
        )

    for target_id in ["bastar_0036", "bastar_bastar_dussehra"]:
        idx = next(
            (i for i, d in enumerate(m._metadata)
             if d.get("id") == target_id),
            None
        )
        if idx is not None:
            print(
                "TARGET:", target_id,
                "| Score:", round(float(scores[idx]), 4)
            )
