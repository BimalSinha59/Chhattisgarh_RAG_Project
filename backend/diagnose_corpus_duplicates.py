import json
import hashlib
from pathlib import Path
from collections import defaultdict

root = Path("data")
files = list(root.rglob("*.jsonl"))

print("JSONL files found:", len(files))

content_groups = defaultdict(list)
id_groups = defaultdict(list)
total = 0

for path in files:
    try:
        with path.open("r", encoding="utf-8-sig") as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue

                total += 1
                record_id = str(d.get("id", "")).strip()
                text = str(d.get("text", "")).strip()
                title = str(d.get("title", "")).strip().casefold()
                url = str(d.get("source_url", "")).strip()

                if record_id:
                    id_groups[record_id].append(
                        (str(path), line_no, title)
                    )

                digest = hashlib.sha256(
                    text.encode("utf-8")
                ).hexdigest()

                if text:
                    content_groups[digest].append(
                        (str(path), line_no, record_id, title, url)
                    )
    except OSError as e:
        print("Could not read:", path, e)

duplicate_ids = {
    k: v for k, v in id_groups.items() if len(v) > 1
}
duplicate_content = {
    k: v for k, v in content_groups.items() if len(v) > 1
}

print("\nTotal JSONL records:", total)
print("IDs appearing more than once:", len(duplicate_ids))
print("Repeated exact-text groups:", len(duplicate_content))

print("\nSample repeated IDs:")
for record_id, entries in list(duplicate_ids.items())[:10]:
    print("\nID:", record_id)
    for path, line_no, title in entries:
        print(" ", path, "| line:", line_no, "|", title)

print("\nSample repeated-content groups:")
for digest, entries in list(duplicate_content.items())[:10]:
    print("\nHash:", digest[:12])
    for path, line_no, record_id, title, url in entries:
        print(
            " ", path, "| line:", line_no,
            "| id:", record_id,
            "| title:", title,
            "| url:", url
        )
