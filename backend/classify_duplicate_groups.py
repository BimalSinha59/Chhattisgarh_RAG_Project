import json
import hashlib
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit

path = Path("data/reviewed_corpus.jsonl")
groups = defaultdict(list)

def normalize_url(url):
    url = str(url or "").strip()
    if not url:
        return ""
    try:
        p = urlsplit(url)
        return urlunsplit((
            p.scheme.lower(),
            p.netloc.lower(),
            p.path.rstrip("/"),
            p.query,
            ""
        ))
    except Exception:
        return url

with path.open("r", encoding="utf-8-sig") as f:
    for line_no, line in enumerate(f, 1):
        if not line.strip():
            continue
        d = json.loads(line)
        text = str(d.get("text", "")).strip()
        if not text:
            continue

        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        groups[digest].append({
            "line": line_no,
            "id": d.get("id", ""),
            "title": str(d.get("title", "")).strip().casefold(),
            "url": normalize_url(d.get("source_url", "")),
            "language": str(d.get("language", "")).strip().casefold(),
            "category": str(d.get("category", "")).strip().casefold(),
            "district": str(d.get("district", "")).strip().casefold(),
            "approved": d.get("approved_for_rag", False),
            "status": d.get("review_status", ""),
        })

duplicates = [items for items in groups.values() if len(items) > 1]

safe = []
metadata_conflicts = []

for items in duplicates:
    signatures = {
        (x["title"], x["url"], x["language"])
        for x in items
    }
    if len(signatures) == 1:
        safe.append(items)
    else:
        metadata_conflicts.append(items)

print("Exact-text duplicate groups:", len(duplicates))
print("Same text + title + URL + language:", len(safe))
print("Groups with metadata conflicts:", len(metadata_conflicts))
print("Extra records in safe groups:", sum(len(x)-1 for x in safe))
print("Extra records in conflict groups:", sum(len(x)-1 for x in metadata_conflicts))

print("\nFirst 5 metadata-conflict groups:")
for items in metadata_conflicts[:5]:
    print("\nGroup:")
    for x in items:
        print(
            " id=", x["id"],
            "| line=", x["line"],
            "| title=", x["title"],
            "| language=", x["language"],
            "| category=", x["category"],
            "| district=", x["district"],
            "| approved=", x["approved"],
            "| status=", x["status"],
            "| url=", x["url"],
        )
