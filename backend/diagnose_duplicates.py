from collections import defaultdict
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

duplicates = [
    items for items in groups.values()
    if len(items) > 1
]

print("Total indexed records:", len(m._metadata))
print("Unique canonical URL/title groups:", len(groups))
print("Duplicate groups:", len(duplicates))
print("Records inside duplicate groups:",
      sum(len(items) for items in duplicates))

print("\nFirst 15 duplicate groups:")
for items in duplicates[:15]:
    print("\n---")
    for idx, d in items:
        print(
            "index:", idx,
            "| id:", d.get("id"),
            "| title:", d.get("title"),
            "| approved:", d.get("approved_for_rag"),
            "| status:", d.get("review_status"),
        )
