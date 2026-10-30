"""Archive one official program source for a candidate.

Usage:
  tools/.venv/bin/python -W ignore tools/fetch.py <slug> <url> \
      --label "Programme ..." --year 2027 --kind pdf|page --official-2027 yes|no \
      [--publisher "Site officiel de ..."]

Downloads the source into sources/<slug>/raw/, extracts plain text into
sources/<slug>/text/<id>.txt and records it (URL, date, sha256) in
sources/<slug>/manifest.json. Re-running with the same URL replaces the entry.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import pathlib
import re
import sys
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def download(url):
    # curl copes better than urllib with redirects, compression and picky servers
    out = subprocess.run(
        ["curl", "-sSL", "--compressed", "--max-time", "90", "-A", UA, "-H", "Accept-Language: fr-FR,fr;q=0.9",
         "-w", "\n%{content_type}\n%{url_effective}\n%{http_code}", "-o", "-", url],
        capture_output=True, check=True,
    ).stdout
    body, ctype, final_url, code = out.rsplit(b"\n", 3)
    if not code.startswith(b"2"):
        sys.exit(f"HTTP {code.decode()} for {url}")
    return body, ctype.decode(), final_url.decode()


def pdf_text(data):
    """Column-aware extraction with poppler's pdftotext (reading order), page markers between pages."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(data)
        f.flush()
        out = subprocess.run(["pdftotext", "-enc", "UTF-8", f.name, "-"], capture_output=True, check=True).stdout
    pages = out.decode("utf-8", errors="replace").split("\f")
    return "".join(f"\n\n[[page {i}]]\n{p}" for i, p in enumerate(pages, 1) if p.strip() or i < len(pages))


def html_full_text(data):
    """Whole-page text minus scripts, styles, navigation and footer; for pages trafilatura truncates."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(data.decode("utf-8", errors="replace"), "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "form", "svg"]):
        tag.decompose()
    root = soup.find("main") or soup.body or soup
    lines = [l.strip() for l in root.get_text("\n").splitlines()]
    return "\n".join(l for l in lines if l)


def html_text(data, url):
    import trafilatura

    html = data.decode("utf-8", errors="replace")
    text = trafilatura.extract(html, url=url, include_comments=False, include_tables=True, favor_recall=True)
    return text or ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("url")
    ap.add_argument("--label", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--kind", choices=["pdf", "page"], required=True)
    ap.add_argument("--official-2027", choices=["yes", "no"], required=True)
    ap.add_argument("--publisher", default="")
    ap.add_argument("--html-full", action="store_true", help="extract the whole page text instead of trafilatura's main-content guess")
    ap.add_argument("--from-file", help="archive a file already downloaded (e.g. via a browser) instead of fetching url")
    a = ap.parse_args()

    if a.from_file:
        data = pathlib.Path(a.from_file).read_bytes()
        ctype, final_url = ("application/pdf" if data[:5] == b"%PDF-" else "text/html"), a.url
    else:
        data, ctype, final_url = download(a.url)
    is_pdf = data[:5] == b"%PDF-" or "pdf" in ctype
    if a.kind == "pdf" and not is_pdf:
        sys.exit(f"Expected a PDF but got {ctype!r} from {final_url}")

    sha = hashlib.sha256(data).hexdigest()
    sid = re.sub(r"[^a-z0-9]+", "-", a.label.lower()).strip("-")[:60] + "-" + sha[:8]
    base = ROOT / "sources" / a.slug
    (base / "raw").mkdir(parents=True, exist_ok=True)
    (base / "text").mkdir(parents=True, exist_ok=True)

    raw_path = base / "raw" / (sid + (".pdf" if is_pdf else ".html"))
    raw_path.write_bytes(data)
    text = pdf_text(data) if is_pdf else (html_full_text(data) if a.html_full else html_text(data, final_url))
    if len(text.strip()) < 200:
        print(f"WARNING: only {len(text.strip())} chars of text extracted (scanned PDF or JS-rendered page?)")
    (base / "text" / (sid + ".txt")).write_text(text, encoding="utf-8")

    manifest_path = base / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"slug": a.slug, "sources": []}
    manifest["sources"] = [s for s in manifest["sources"] if s["url"] != a.url]
    manifest["sources"].append({
        "id": sid,
        "label": a.label,
        "publisher": a.publisher,
        "url": a.url,
        "final_url": final_url,
        "year": a.year,
        "kind": "pdf" if is_pdf else "page",
        "official_2027_program": a.official_2027 == "yes",
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "sha256": sha,
        "raw": str(raw_path.relative_to(ROOT)),
        "text": str((base / "text" / (sid + ".txt")).relative_to(ROOT)),
        "text_chars": len(text),
    })
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"OK {sid} ({len(text)} chars) -> {raw_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
