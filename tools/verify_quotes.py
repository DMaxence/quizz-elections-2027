"""Check that every quote in data/propositions/*.json and data/stances/*.json appears
verbatim in the archived text of the source it cites.

Comparison ignores whitespace, case, typographic quote/dash/space variants, ligatures,
end-of-line hyphenation and page markers. A quote may skip text with "[…]"; each fragment
must then be found, in order. Exits non-zero if anything fails.

Usage: tools/.venv/bin/python tools/verify_quotes.py [slug ...]
"""
import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = re.compile(r"\s*(?:\[…\]|\[\.\.\.\]|\(…\)|\(\.\.\.\))\s*")
PAGE = re.compile(r"\[\[page (\d+)\]\]")


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("­", "")
    s = re.sub(r"[‘’ʼ`´]", "'", s)
    s = re.sub(r"[“”«»„]", '"', s)
    s = re.sub(r"[‐‑‒–—―]", "-", s)
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)  # end-of-line hyphenation
    s = re.sub(r"[\s  ]+", " ", s)
    s = re.sub(r'\s*"\s*', '"', s)
    s = re.sub(r"\s*'\s*", "'", s)
    s = re.sub(r"\s+([,.;:!?)])", r"\1", s)
    return s.strip().lower()


_texts = {}


def source_text(slug, source_id):
    key = (slug, source_id)
    if key not in _texts:
        manifest = json.loads((ROOT / "sources" / slug / "manifest.json").read_text())
        entry = next((s for s in manifest["sources"] if s["id"] == source_id), None)
        if entry is None:
            _texts[key] = None
        else:
            raw = (ROOT / entry["text"]).read_text(encoding="utf-8")
            # keep page markers out of the searchable text but remember offsets per page
            pages, buf, page = [], [], 1
            for part in PAGE.split(raw):
                if part.isdigit() and len(part) < 5:
                    pages.append((page, norm(" ".join(buf))))
                    buf, page = [], int(part)
                else:
                    buf.append(part)
            pages.append((page, norm(" ".join(buf))))
            _texts[key] = (norm(PAGE.sub(" ", raw)), pages)
    return _texts[key]


def find(slug, source_id, quote):
    """Return (ok, page) for a quote."""
    st = source_text(slug, source_id)
    if st is None:
        return False, None, "unknown source_id"
    full, pages = st
    pos = 0
    first = None
    for frag in [f for f in SKIP.split(quote) if f.strip()]:
        nf = norm(frag)
        i = full.find(nf, pos)
        if i < 0:
            return False, None, f"fragment not found: {frag[:80]!r}"
        first = nf if first is None else first
        pos = i + len(nf)
    page = next((p for p, t in pages if first and first in t), None)
    return True, page, ""


def iter_quotes(only=()):
    for f in sorted((ROOT / "data" / "propositions").glob("*.json")):
        if only and f.stem not in only:
            continue
        slug = f.stem
        for p in json.loads(f.read_text()):
            yield f, slug, p.get("id"), p
    for f in sorted((ROOT / "data" / "stances").glob("*.json")):
        if only and f.stem not in only:
            continue
        slug = f.stem
        for qid, st in json.loads(f.read_text()).get("stances", {}).items():
            for q in st.get("quotes", []):
                yield f, slug, qid, q


def main():
    fails = total = 0
    for f, slug, ref, q in iter_quotes(tuple(sys.argv[1:])):
        total += 1
        ok, page, why = find(slug, q["source_id"], q["quote"])
        if not ok:
            fails += 1
            print(f"FAIL {f.relative_to(ROOT)} [{ref}] {why}")
        elif q.get("page") not in (None, page) and page is not None:
            print(f"PAGE {f.relative_to(ROOT)} [{ref}] cited p.{q.get('page')}, found p.{page}")
    print(f"{total - fails}/{total} quotes verified")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
