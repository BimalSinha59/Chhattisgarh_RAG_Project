import app.main as m
from collections import defaultdict

m.load_index()

target_id = "bastar_0036"
target = next(
    (d for d in m._metadata
     if d.get("record_id") == target_id or d.get("id") == target_id),
    None
)

print("\n" + "=" * 70)
print("1. TARGET RECORD FIELDS")
print("=" * 70)

if target is None:
    print("Target record not found")
    raise SystemExit

print("Available fields:", list(target.keys()))

for key, value in target.items():
    if any(term in key.lower() for term in [
        "text", "content", "title", "summary", "description",
        "source", "language", "approval", "review"
    ]):
        print(f"\n{key}:")
        print(str(value)[:1200])

print("\n" + "=" * 70)
print("2. TOKENIZER CHECK")
print("=" * 70)

queries = [
    "बस्तर दशहरा की परंपराएँ बताइए",
    "बस्तर दशहरा",
    "Bastar Dussehra festival traditions",
]

for q in queries:
    print("\nQuery:", q)
    print("Tokens:", m.tokenize(q))

print("\n" + "=" * 70)
print("3. SAME-TITLE RECORDS")
print("=" * 70)

for i, d in enumerate(m._metadata):
    if "dussehra" in str(d.get("title", "")).lower():
        print(
            "Index:", i,
            "| ID:", d.get("record_id", d.get("id")),
            "| Approved:", d.get("approved_for_rag"),
            "| Title:", d.get("title"),
            "| URL:", d.get("source_url", "")
        )

print("\n" + "=" * 70)
print("4. ACTUAL HYBRID RETRIEVAL")
print("=" * 70)

for q in queries:
    print("\nQuery:", q)
    try:
        results = m.retrieve(q)
        for rank, item in enumerate(results, 1):
            if isinstance(item, dict):
                print(
                    rank,
                    "| ID:", item.get("record_id", item.get("id")),
                    "| Title:", item.get("title")
                )
            else:
                print(rank, str(item)[:300])
    except Exception as e:
        print("Retrieval error:", repr(e))
