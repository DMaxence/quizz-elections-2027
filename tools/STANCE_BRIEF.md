# Stance brief — position of each candidate on each quiz question

Project: `/Users/max/perso/presidentielle-2027` (read `PLAN.md`). The quiz questions are in
`data/questions.json`. For each of your assigned candidates and EACH question, decide the candidate's
position using ONLY their archived texts in `sources/<slug>/text/*.txt` (index in
`sources/<slug>/manifest.json`). `data/propositions/<slug>.json` is a useful starting index, but it is
not exhaustive: search the full texts (Grep several keywords and synonyms per question).
Never use your own knowledge of the candidate, party or ideology. Never the web. Same rigour for everyone.

## The three outcomes
- **pour**: the text explicitly proposes or supports the measure as phrased in the question
  (a stronger version in the same direction counts, e.g. question "Augmenter le SMIC" and text
  "porter le SMIC à 1 600 € net").
- **contre**: the text explicitly rejects the measure, or proposes something incompatible with it
  (question "Abaisser l'âge légal de départ à la retraite", text "reporter l'âge légal à 65 ans").
- **non mentionné**: everything else. Simply leave the question out of the file. This includes:
  the topic is discussed but the text takes no clear side; the text supports a related but different
  measure; you would have to infer from the candidate's general orientation. When in doubt, leave it out.

Each question has `"help"` / `"scope"` notes when the wording needs precision: respect them.
If a 2027 source (`official_2027_program: true`) and an older source disagree, the 2027 source wins.
Shared coalition documents (e.g. the Nouveau Front populaire program) only count when the candidate's
own sources are silent on that question; say so in the note.

## Output: `data/stances/<slug>.json`
```json
{
  "slug": "<slug>",
  "stances": {
    "q01": {
      "stance": "pour",
      "quotes": [{ "quote": "Citation exacte…", "source_id": "<manifest id>", "page": 12 }],
      "note": "Facultatif : une phrase neutre si la position a une nuance (ex. « Propose 62 ans. »)."
    }
  }
}
```
- 1 quote per stance, 2 at most, the one that shows the position most directly.
- Quotes are verbatim (see `tools/EXTRACTION_BRIEF.md`, "Quotes must be verbatim"; `[…]` allowed).
- `page`: nearest preceding `[[page N]]` marker, or null.
- Notes are neutral, short, in French, never evaluative.

## Check before finishing
Run `tools/.venv/bin/python tools/verify_quotes.py <slug>` for each slug and fix every FAIL.
Report per candidate: number of pour / contre / non mentionné, and every case you found hard to decide
(question id + one line). Do not paste the stances.
