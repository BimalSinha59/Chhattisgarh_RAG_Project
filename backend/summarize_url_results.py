import csv
from collections import Counter

path = "data/url_verification_results.csv"

with open(path, "r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

print("RECORD-LEVEL STATUS SUMMARY")
print("Total records:", len(rows))

counts = Counter(row.get("url_result", "") for row in rows)
for status, count in counts.most_common():
    print(f"{status}: {count}")

print("\nHTTP STATUS COUNTS")
http_counts = Counter(row.get("http_status", "") or "(none)" for row in rows)
for status, count in http_counts.most_common():
    print(f"{status}: {count}")

print("\nRECORDS NEEDING URL REVIEW")
for row in rows:
    status = row.get("url_result", "")
    if status not in ("ACCESSIBLE",):
        print(
            f"{row.get('id', '')} | {status} | "
            f"HTTP {row.get('http_status', '')} | "
            f"{row.get('source_url', '')} | "
            f"Final: {row.get('final_url', '')}"
        )
