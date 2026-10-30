# Extraction brief — propositions with verbatim quotes

Project: `/Users/max/perso/presidentielle-2027` (read `PLAN.md`). A neutral French quiz for the 2027
presidential election. You extract the concrete propositions of your assigned candidates, ONLY from
their archived texts in `sources/<slug>/text/*.txt` (index: `sources/<slug>/manifest.json`).
Never use your own knowledge of the candidate or party, never the web. If it is not in the text files,
it does not exist. Apply identical effort and standards to every candidate.

## Output: `data/propositions/<slug>.json`
A JSON array:
```json
[
  {
    "id": "<slug>-01",
    "theme": "<one of the themes below>",
    "measure": "Résumé neutre à l'infinitif, ≤ 20 mots (ex. « Supprimer l'aide médicale d'État »)",
    "quote": "Citation exacte, copiée caractère pour caractère depuis le fichier texte (1 à 3 phrases).",
    "source_id": "<id from manifest.json>",
    "page": 12,
    "concrete": true
  }
]
```
- `page`: the number from the nearest preceding `[[page N]]` marker in the text file, or null for web pages.
- `concrete`: true for an actionable measure (create / abolish / raise / lower / ban / allow / a figure,
  a law, an institution), false for a general orientation. Prefer concrete ones.
- `measure` must be faithful and neutral: no adjectives the program does not use, no judgement,
  keep the program's own scope (don't turn "réduire" into "supprimer").

## Themes (use exactly these strings)
- Économie, fiscalité et dette
- Travail, salaires et retraites
- Santé
- École et jeunesse
- Écologie, climat et énergie
- Agriculture et alimentation
- Immigration
- Sécurité et justice
- Institutions et démocratie
- Europe, international et défense
- Logement et territoires
- Protection sociale et famille
- Numérique, médias et culture
- Société et libertés

## How much
- Large programs: 30–45 propositions, spread over every theme the program covers (don't spend
  them all on one theme). Favour measures that are clear, distinctive, and that other candidates might
  plausibly support or oppose (taxes, retirement age, nuclear, immigration rules, EU, referendums,
  police, school, health, housing…). Small programs: every concrete proposition there is.
- When the candidate has an official 2027 source (`official_2027_program: true` in the manifest),
  take propositions from it first; use older/party sources only for themes the 2027 sources don't cover,
  and never when they contradict a 2027 source.
- Skip diagnosis, rhetoric, attacks on opponents, history.

## Quotes must be verbatim
Copy the quote exactly from the `.txt` file: same words, same order. Use Grep on the text file to
confirm the passage exists before writing it. You may drop a middle part with `[…]`. Do not fix
typos, do not merge lines into a sentence that isn't there. Line breaks in the file can be written
as spaces. Prefer a quote that is self-explanatory without context.

## Check before finishing
Run `tools/.venv/bin/python tools/verify_quotes.py <slug>` for each of your slugs and fix every FAIL
(re-copy the exact text). Report: number of propositions per candidate, per theme counts, and anything
odd (garbled text, sources that turned out empty or off-topic). Do not paste the propositions in your report.
