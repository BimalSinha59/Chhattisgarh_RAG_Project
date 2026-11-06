"""
Prepare a normalized corpus from CSV/JSON/JSONL files in a dataset ZIP.
Does not mark unverified records as approved. It preserves provenance and
sets approved_for_rag only when the source record explicitly signals approval.
"""
import argparse, csv, json, re, zipfile
from pathlib import Path

TEXT_KEYS = [
    "content", "text", "description", "summary", "body", "abstract",
    "details", "content_text", "english", "hindi", "chhattisgarhi_form_ipa_as_published",
    "title_native", "notes"
]
TITLE_KEYS = ["title", "source_title", "name", "topic", "category", "record_id", "document_id"]
ID_KEYS = ["record_id", "document_id", "id", "recordid"]
URL_KEYS = ["source_url", "url", "source", "source_link"]
LANG_KEYS = ["language", "lang"]
APPROVAL_KEYS = ["approved_for_rag", "review_status", "verification_status", "quality_flag", "extraction_status"]

def truthy(v):
    return str(v).strip().lower() in {"true", "1", "yes", "approved", "verified", "reviewed"}

def flatten_record(row, source_file, index):
    if not isinstance(row, dict):
        row = {"text": str(row)}
    lower = {str(k).lower(): v for k, v in row.items()}
    title = next((str(lower[k]).strip() for k in TITLE_KEYS if lower.get(k) not in (None, "")), f"Record {index}")
    text_parts = []
    for key in TEXT_KEYS:
        value = lower.get(key)
        if value is not None and str(value).strip():
            s = re.sub(r"\s+", " ", str(value)).strip()
            if s and s not in text_parts:
                text_parts.append(s)
    # For district/culture entries, title alone is not a useful retrieval chunk.
    text = "\n".join(text_parts)
    if len(text) < 20:
        return None
    rid = next((str(lower[k]).strip() for k in ID_KEYS if lower.get(k) not in (None, "")), f"{Path(source_file).stem}_{index}")
    url = next((str(lower[k]).strip() for k in URL_KEYS if lower.get(k) not in (None, "")), "")
    lang = next((str(lower[k]).strip() for k in LANG_KEYS if lower.get(k) not in (None, "")), "unknown")
    approval_raw = lower.get("approved_for_rag", False)
    review = str(lower.get("review_status", lower.get("verification_status", ""))).strip().lower()
    quality = str(lower.get("quality_flag", "")).strip().lower()
    # Draft language resources must not be automatically approved.
    risky_draft = any(word in (review + " " + quality) for word in ["needs_native_speaker_review", "synthetic_draft", "not_independently_verified", "unverified", "draft"])
    approved = truthy(approval_raw) or review in {"approved", "verified", "reviewed"}
    if risky_draft:
        approved = False
    return {
        "id": rid,
        "title": title,
        "text": text,
        "source_url": url,
        "source_file": source_file,
        "language": lang,
        "category": str(lower.get("category", lower.get("topic", "general"))),
        "district": str(lower.get("district", "")),
        "review_status": review or ("needs_review" if not approved else "approved"),
        "quality_flag": str(lower.get("quality_flag", "")),
        "approved_for_rag": bool(approved)
    }

def read_member(name, raw):
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return []
    ext = Path(name).suffix.lower()
    try:
        if ext == ".jsonl":
            rows = [json.loads(line) for line in decoded.splitlines() if line.strip()]
        elif ext == ".json":
            obj = json.loads(decoded)
            rows = obj if isinstance(obj, list) else (obj.get("records", [obj]) if isinstance(obj, dict) else [])
        elif ext == ".csv":
            rows = list(csv.DictReader(decoded.splitlines()))
        else:
            return []
    except Exception:
        return []
    out = []
    for i, row in enumerate(rows, 1):
        item = flatten_record(row, name, i)
        if item:
            out.append(item)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True, help="Path to original dataset ZIP")
    ap.add_argument("--out", default="data/reviewed_corpus.jsonl")
    ap.add_argument("--include-nested-zips", action="store_true", help="Also read supported files inside nested ZIPs")
    args = ap.parse_args()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    records, seen = [], set()
    with zipfile.ZipFile(args.zip) as z:
        for name in z.namelist():
            if Path(name).suffix.lower() not in {".csv", ".json", ".jsonl"}:
                continue
            for row in read_member(name, z.read(name)):
                key = (row["id"], row["source_url"], row["text"][:160])
                if key not in seen:
                    seen.add(key); records.append(row)
        if args.include_nested_zips:
            for nested_name in [n for n in z.namelist() if n.lower().endswith(".zip")]:
                try:
                    with zipfile.ZipFile(__import__("io").BytesIO(z.read(nested_name))) as nz:
                        for name in nz.namelist():
                            if Path(name).suffix.lower() not in {".csv", ".json", ".jsonl"}:
                                continue
                            for row in read_member(f"{nested_name}::{name}", nz.read(name)):
                                key = (row["id"], row["source_url"], row["text"][:160])
                                if key not in seen:
                                    seen.add(key); records.append(row)
                except zipfile.BadZipFile:
                    pass
    with output.open("w", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    approved = sum(r["approved_for_rag"] for r in records)
    print(f"Corpus written: {output.resolve()}")
    print(f"Records: {len(records)} | approved for RAG: {approved} | needs review: {len(records)-approved}")
    print("Review records before approving them; source presence alone is not proof of factual or language quality.")

if __name__ == "__main__":
    main()
