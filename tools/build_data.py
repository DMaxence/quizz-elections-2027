"""Assemble everything the site needs into site/src/data/*.json.

- candidates.json : every candidate (status dot, party, photo, sources) — no stances
- questions.json  : the quiz questions only (what the quiz page ships)
- results.json    : stances with quotes and source links (shipped only to the results page)

Usage: tools/.venv/bin/python tools/build_data.py
"""
import json
import pathlib
import shutil
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "src" / "data"
PHOTOS_OUT = ROOT / "site" / "public" / "photos"
SHORT_LEN = 30


def surname_key(name):
    # alphabetical by surname, ignoring accents and particles
    parts = name.split()
    last = " ".join(parts[1:]) if len(parts) > 1 else name
    for prefix in ("de ", "du ", "le ", "la "):
        if last.lower().startswith(prefix) and last.lower() not in ("le pen",):
            last = last[len(prefix):]
    return unicodedata.normalize("NFKD", last).encode("ascii", "ignore").decode().lower()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PHOTOS_OUT.mkdir(parents=True, exist_ok=True)
    credits = {c["slug"]: c for c in json.loads((ROOT / "data/photos/credits.json").read_text())}

    candidates = []
    for cfile in sorted((ROOT / "sources").glob("*/candidate.json")):
        c = json.loads(cfile.read_text())
        if not c.get("declared", True):
            continue
        manifest_path = cfile.parent / "manifest.json"
        sources = json.loads(manifest_path.read_text())["sources"] if manifest_path.exists() else []
        photo = None
        for ext in ("jpg", "png"):
            src = ROOT / "data/photos" / f"{c['slug']}.{ext}"
            if src.exists():
                shutil.copy(src, PHOTOS_OUT / src.name)
                photo = f"/photos/{src.name}"
        cr = credits.get(c["slug"])
        candidates.append({
            "slug": c["slug"],
            "name": c["name"],
            "party": c["party"],
            "party_short": c.get("party_short", ""),
            "status": c["program_status"],
            "status_note": c.get("program_status_note", ""),
            "photo": photo,
            "photo_credit": (f"{cr['author']}, {cr['licence']}" if cr and photo else None),
            "photo_page": (cr["commons_page"] if cr and photo else None),
            "sources": [
                {"id": s["id"], "label": s["label"], "year": s["year"], "url": s["url"],
                 "official_2027": s["official_2027_program"], "retrieved_at": s["retrieved_at"][:10],
                 "sha256": s["sha256"]}
                for s in sources
            ],
        })
    candidates.sort(key=lambda c: surname_key(c["name"]))

    qpath = ROOT / "data/questions.json"
    questions = json.loads(qpath.read_text()) if qpath.exists() else []

    stances = {}
    for f in sorted((ROOT / "data/stances").glob("*.json")) if (ROOT / "data/stances").exists() else []:
        d = json.loads(f.read_text())
        stances[f.stem] = d.get("stances", {})

    # Short version: in each theme, the two questions on which the most programs take a position
    # (ties: lower id), then the next best-covered questions overall up to SHORT_LEN.
    coverage = {q["id"]: sum(1 for st in stances.values() if q["id"] in st) for q in questions}
    rank = lambda q: (-coverage[q["id"]], q["id"])
    core = set()
    for theme in dict.fromkeys(q["theme"] for q in questions):
        core.update(q["id"] for q in sorted((q for q in questions if q["theme"] == theme), key=rank)[:2])
    for q in sorted(questions, key=rank):
        if len(core) >= SHORT_LEN:
            break
        core.add(q["id"])
    for q in questions:
        q["core"] = q["id"] in core

    (OUT / "candidates.json").write_text(json.dumps(candidates, ensure_ascii=False, indent=1))
    (OUT / "questions.json").write_text(json.dumps(
        [{k: q[k] for k in ("id", "theme", "text", "short", "help", "core") if k in q} for q in questions],
        ensure_ascii=False, indent=1))
    (OUT / "results.json").write_text(json.dumps({"stances": stances}, ensure_ascii=False, indent=1))
    n_quotes = sum(len(s.get("quotes", [])) for st in stances.values() for s in st.values())
    print(f"{len(candidates)} candidates, {len(questions)} questions ({len(core)} in the short version), {n_quotes} quotes")
    print("short version:", " ".join(sorted(core)))


if __name__ == "__main__":
    main()
