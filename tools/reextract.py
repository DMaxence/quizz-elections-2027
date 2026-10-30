"""Re-run text extraction on every archived PDF (raw files are untouched, so sha256 stays valid).

Usage: tools/.venv/bin/python -W ignore tools/reextract.py [slug ...]
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fetch import ROOT, pdf_text  # noqa: E402


def main():
    slugs = sys.argv[1:] or [p.name for p in sorted((ROOT / "sources").iterdir()) if p.is_dir()]
    for slug in slugs:
        mpath = ROOT / "sources" / slug / "manifest.json"
        if not mpath.exists():
            continue
        manifest = json.loads(mpath.read_text())
        for s in manifest["sources"]:
            if s["kind"] != "pdf":
                continue
            text = pdf_text((ROOT / s["raw"]).read_bytes())
            (ROOT / s["text"]).write_text(text, encoding="utf-8")
            print(f"{slug}: {s['id']} {s['text_chars']} -> {len(text)} chars")
            s["text_chars"] = len(text)
        mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
