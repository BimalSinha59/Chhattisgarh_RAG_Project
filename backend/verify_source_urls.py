import csv
import json
import time
from pathlib import Path
from urllib.parse import urlparse, urlsplit, urlunsplit, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

source = Path("data/reviewed_corpus.jsonl")
output = Path("data/url_verification_results.csv")
cache = {}

def normalize_url(url):
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None

    # Encode Unicode characters in the URL path/query.
    path = quote(parts.path, safe="/%:@!$&'()*+,;=-._~%")
    query = quote(parts.query, safe="/?@!$&'()*+,;=:-._~%")
    return urlunsplit((
        parts.scheme, parts.netloc, path, query, parts.fragment
    ))

def check_url(url):
    if url in cache:
        return cache[url]

    normalized = normalize_url(url)
    if not normalized:
        result = ("INVALID_URL", "", "")
    elif urlparse(normalized).hostname in ("example.org",):
        result = ("PLACEHOLDER_DOMAIN", "", "")
    else:
        try:
            request = Request(
                normalized,
                headers={"User-Agent": "Mozilla/5.0"},
                method="GET",
            )
            with urlopen(request, timeout=12) as response:
                result = (
                    "ACCESSIBLE",
                    str(response.status),
                    response.geturl(),
                )
        except HTTPError as e:
            result = ("HTTP_ERROR", str(e.code), e.geturl() or normalized)
        except (URLError, TimeoutError, OSError, UnicodeError, ValueError) as e:
            result = ("CONNECTION_OR_URL_ERROR", "", str(e)[:200])
        except Exception as e:
            result = ("UNEXPECTED_ERROR", "", str(e)[:200])

    cache[url] = result
    return result

with source.open("r", encoding="utf-8-sig") as f:
    rows = [json.loads(line) for line in f if line.strip()]

unique_urls = list(dict.fromkeys(
    str(row.get("source_url", "")).strip()
    for row in rows if str(row.get("source_url", "")).strip()
))

print("Records:", len(rows))
print("Unique non-empty URLs:", len(unique_urls))

for i, url in enumerate(unique_urls, 1):
    status, http_status, final_url = check_url(url)
    print(f"[{i}/{len(unique_urls)}] {status} {http_status} {url}")
    time.sleep(0.1)

with output.open("w", encoding="utf-8-sig", newline="") as out:
    writer = csv.DictWriter(out, fieldnames=[
        "id", "title", "source_url", "domain",
        "http_status", "url_result", "final_url",
        "approved_for_rag", "review_status"
    ])
    writer.writeheader()

    for row in rows:
        url = str(row.get("source_url", "")).strip()
        status, http_status, final_url = (
            check_url(url) if url else ("MISSING_URL", "", "")
        )
        normalized = normalize_url(url) if url else None
        domain = urlparse(normalized).netloc.lower() if normalized else ""

        writer.writerow({
            "id": row.get("id", ""),
            "title": row.get("title", ""),
            "source_url": url,
            "domain": domain,
            "http_status": http_status,
            "url_result": status,
            "final_url": final_url,
            "approved_for_rag": row.get("approved_for_rag", False),
            "review_status": row.get("review_status", ""),
        })

print("\nSaved:", output)
print("Original corpus was not modified.")
