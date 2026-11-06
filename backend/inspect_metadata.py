import json
from pathlib import Path
from app.main import METADATA_PATH

with Path(METADATA_PATH).open(encoding="utf-8") as f:
    docs = json.load(f)

terms = [
    "bastar dussehra",
    "बस्तर दशहरा",
    "bastar_0036",
    "traditional foods",
    "chhattisgarh lokoktiya",
]

print("Total metadata records:", len(docs))

for term in terms:
    matches = [
        (i, d) for i, d in enumerate(docs)
        if term.casefold() in (
            str(d.get("title", "")) + " " +
            str(d.get("text", "")) + " " +
            str(d.get("record_id", "")) + " " +
            str(d.get("id", ""))
        ).casefold()
    ]

    print(f"\n--- SEARCH: {term} | MATCHES: {len(matches)} ---")

    for i, d in matches[:5]:
        print("Metadata index:", i)
        print("ID:", d.get("record_id", d.get("id")))
        print("Title:", d.get("title"))
        print("Approved:", d.get("approved_for_rag"))
        print("Review:", d.get("review_status"))
        print("Text:", (d.get("text") or "")[:250].replace("\n", " "))
