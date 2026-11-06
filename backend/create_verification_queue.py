import csv
import json
from pathlib import Path
from urllib.parse import urlparse

source = Path("data/reviewed_corpus.jsonl")
output = Path("data/source_verification_queue.csv")

with source.open("r", encoding="utf-8-sig") as f, \
     output.open("w", encoding="utf-8-sig", newline="") as out:

    writer = csv.DictWriter(
        out,
        fieldnames=[
            "id", "title", "source_url", "domain",
            "language", "category", "review_status",
            "approved_for_rag", "issue", "text_preview"
        ]
    )
    writer.writeheader()

    for line in f:
        if not line.strip():
            continue

        row = json.loads(line)
        url = str(row.get("source_url", "")).strip()
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        issues = []

        if parsed.scheme not in ("http", "https") or not domain:
            issues.append("missing_or_invalid_url")
        if domain == "example.org" or domain.endswith(".example.org"):
            issues.append("placeholder_domain")
        if row.get("approved_for_rag") is not True:
            issues.append("approval_pending")

        if issues:
            writer.writerow({
                "id": row.get("id", ""),
                "title": row.get("title", ""),
                "source_url": url,
                "domain": domain,
                "language": row.get("language", ""),
                "category": row.get("category", ""),
                "review_status": row.get("review_status", ""),
                "approved_for_rag": row.get("approved_for_rag", False),
                "issue": ";".join(issues),
                "text_preview": str(row.get("text", ""))[:300]
            })

print("Verification queue saved to:", output)
