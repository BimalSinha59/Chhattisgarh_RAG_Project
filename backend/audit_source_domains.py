import json
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse

path = Path("data/reviewed_corpus.jsonl")
domains = Counter()
missing_url = 0
empty_text = 0
records = 0

with path.open("r", encoding="utf-8-sig") as f:
    for line in f:
        if not line.strip():
            continue

        row = json.loads(line)
        records += 1

        url = str(row.get("source_url", "")).strip()
        if url:
            domain = urlparse(url).netloc.lower()
            if domain:
                domains[domain] += 1
            else:
                missing_url += 1
        else:
            missing_url += 1

        if not str(row.get("text", "")).strip():
            empty_text += 1

print("Total records:", records)
print("Records without a valid domain:", missing_url)
print("Records with empty text:", empty_text)
print("\nTop source domains:")
for domain, count in domains.most_common():
    print(f"{count:4}  {domain}")
