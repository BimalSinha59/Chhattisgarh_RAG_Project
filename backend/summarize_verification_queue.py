import csv
from collections import Counter

path = "data/source_verification_queue.csv"

with open(path, "r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

print("Total queue records:", len(rows))

issues = Counter()
domains = Counter()

for row in rows:
    for issue in row.get("issue", "").split(";"):
        if issue.strip():
            issues[issue.strip()] += 1

    domain = row.get("domain", "").strip()
    if domain:
        domains[domain] += 1

print("\nIssue counts:")
for issue, count in issues.most_common():
    print(f"{issue}: {count}")

print("\nTop 15 domains:")
for domain, count in domains.most_common(15):
    print(f"{count:4}  {domain}")

print("\nFirst 10 records:")
for row in rows[:10]:
    print(
        row.get("id", ""),
        "|", row.get("title", ""),
        "|", row.get("source_url", ""),
        "|", row.get("issue", "")
    )
