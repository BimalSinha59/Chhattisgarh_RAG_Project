from collections import defaultdict
import hashlib
import app.main as m

m.load_index()
groups = defaultdict(list)

for i, d in enumerate(m._metadata):
    url = m.canonical_url(d.get("source_url", ""))
    title = (d.get("title") or "").strip().casefold()

    if url:
        key = (url, title)
    else:
        key = (
            (d.get("source_file") or "").strip().casefold(),
            title,
        )

    groups[key].append((i, d))

duplicates = [items for items in groups.values() if len(items) > 1]

identical_groups = 0
different_groups = 0

for items in duplicates:
    hashes = set()
    for _, d in items:
        text = (d.get("text") or "").strip()
        hashes.add(hashlib.sha256(text.encode("utf-8")).hexdigest())

    if len(hashes) == 1:
        identical_groups += 1
    else:
        different_groups += 1

print("\nDuplicate groups:", len(duplicates))
print("Groups with identical text:", identical_groups)
print("Groups with different text:", different_groups)

print("\nFirst 10 groups with different text:")
shown = 0

for items in duplicates:
    hashes = {
        hashlib.sha256(
            (d.get("text") or "").strip().encode("utf-8")
        ).hexdigest()
        for _, d in items
    }

    if len(hashes) > 1:
        print("\n---")
        for idx, d in items:
            text = (d.get("text") or "").replace("\n", " ")
            print(
                "index:", idx,
                "| id:", d.get("id"),
                "| chars:", len(text),
                "| text:", text[:220],
            )
        shown += 1
        if shown >= 10:
            break
