import csv
from collections import defaultdict

groups = defaultdict(list)

with open("exact_duplicate_audit.csv", encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        groups[row["text_sha256"]].append(row)

print("Duplicate groups in CSV:", len(groups))
print("Records in CSV:", sum(len(v) for v in groups.values()))

print("\nFirst 10 duplicate groups:")
for n, rows in enumerate(groups.values()):
    if n >= 10:
        break
    print("\n---")
    for row in rows:
        print(
            "ID:", row["id"],
            "| Index:", row["index"],
            "| Title:", row["title"],
            "| Source:", row["source_url"] or row["source_file"],
            "| Approved:", row["approved_for_rag"],
            "| Status:", row["review_status"],
        )
