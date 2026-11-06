import json
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict

source = Path("data/reviewed_corpus.jsonl")
backup = Path("data/reviewed_corpus.before_dedup.jsonl")
report = Path("data/exact_duplicate_groups.txt")

if not source.exists():
    raise SystemExit(f"Corpus not found: {source}")

if not backup.exists():
    shutil.copy2(source, backup)
    print("Backup created:", backup)
else:
    print("Backup already exists:", backup)

groups = defaultdict(list)

with source.open("r", encoding="utf-8-sig") as f:
    for line_no, line in enumerate(f, 1):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            print("Invalid JSON at line:", line_no)
            continue

        text = str(record.get("text", "")).strip()
        if not text:
            continue

        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        groups[digest].append({
            "line": line_no,
            "id": record.get("id", ""),
            "title": record.get("title", ""),
            "url": record.get("source_url", ""),
            "approved": record.get("approved_for_rag", False),
            "review_status": record.get("review_status", ""),
        })

duplicates = [
    entries for entries in groups.values()
    if len(entries) > 1
]

duplicate_records = sum(len(entries) for entries in duplicates)
extra_records = sum(len(entries) - 1 for entries in duplicates)

with report.open("w", encoding="utf-8") as f:
    for number, entries in enumerate(duplicates, 1):
        f.write(f"\nGROUP {number} | records={len(entries)}\n")
        for item in entries:
            f.write(
                f"  line={item['line']} | id={item['id']} "
                f"| approved={item['approved']} "
                f"| status={item['review_status']}\n"
                f"    title={item['title']}\n"
                f"    url={item['url']}\n"
            )

print("\nTotal exact-text duplicate groups:", len(duplicates))
print("Records inside those groups:", duplicate_records)
print("Extra records beyond one per group:", extra_records)
print("Detailed report:", report)
