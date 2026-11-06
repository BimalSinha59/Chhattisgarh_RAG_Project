import json
from pathlib import Path
from collections import defaultdict, Counter
import hashlib

path = Path("data/reviewed_corpus.jsonl")
groups = defaultdict(list)
approval_counts = Counter()
total = 0

with path.open("r", encoding="utf-8-sig") as f:
    for line_no, line in enumerate(f, 1):
        if not line.strip():
            continue

        row = json.loads(line)
        total += 1
        approval_counts[str(row.get("approved_for_rag", False))] += 1

        text = str(row.get("text", "")).strip()
        if not text:
            continue

        key = (
            hashlib.sha256(text.encode("utf-8")).hexdigest(),
            str(row.get("title", "")).strip().casefold(),
            str(row.get("source_url", "")).strip().rstrip("/").casefold(),
            str(row.get("language", "")).strip().casefold(),
        )
        groups[key].append({
            "id": row.get("id", ""),
            "approved": row.get("approved_for_rag") is True,
            "status": row.get("review_status", ""),
        })

safe_groups = [items for items in groups.values() if len(items) > 1]

approval_conflicts = [
    items for items in safe_groups
    if len({item["approved"] for item in items}) > 1
]

print("Total corpus records:", total)
print("Approval counts:", dict(approval_counts))
print("Exact duplicate groups eligible by text/title/URL/language:", len(safe_groups))
print("Groups with conflicting approval flags:", len(approval_conflicts))

for items in approval_conflicts[:5]:
    print("\nApproval conflict:")
    for item in items:
        print(item)
