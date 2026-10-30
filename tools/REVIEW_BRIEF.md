# Review brief — independent check of stances

Project: `/Users/max/perso/presidentielle-2027` (read `PLAN.md`). Another agent assigned each candidate a
position ("pour" / "contre") on quiz questions, backed by verbatim quotes. Quotes are already verified to
exist word for word in the sources. Your job is to check the JUDGEMENT, adversarially and neutrally.

For each stance in `data/stances/<slug>.json` of your assigned candidates:
1. Read the question and its `scope` in `data/questions.json`.
2. Read the quote, then open the source text (`sources/<slug>/text/<source>.txt`, find the quote with
   Grep) and read the surrounding paragraph for context.
3. Decide: does the text, in context, really support that stance under the scope?
   - KEEP if yes.
   - FLIP if it clearly supports the opposite.
   - DROP if it is ambiguous, about a different measure, conditional, merely descriptive (diagnosis,
     attack on opponents), or inferred from orientation rather than stated. When unsure → DROP.
   - Also check the source is the right one: a 2027 source must win over an older one if they disagree
     (`official_2027_program` in the manifest). If an older-source stance contradicts a 2027 source, DROP
     or FLIP accordingly.
4. Apply your decisions directly in `data/stances/<slug>.json` (remove dropped entries, change flipped
   ones; when flipping, the quote must still support the new stance — otherwise drop). Never add new
   stances and never use your own knowledge of the candidates.
5. Run `tools/.venv/bin/python tools/verify_quotes.py <slug>` after editing.

Write a log of every non-KEEP decision in `data/review/<slug>.md` (question id, decision, one-line reason).
Report: per candidate, kept / flipped / dropped counts and anything systematic you noticed
(e.g. one agent consistently over-reading). Same rigour for every candidate.
