# Présidentielle 2027 — quiz « les idées, pas les visages »

Static French quiz (Cloudflare Pages, localStorage only, no server, no analytics).
Users answer ~30 questions built **only** from candidates' program documents, without knowing
who proposed what. Results reveal matching candidates (photo, name, party) and a comparison table.

## Rules (non-negotiable)
- Stances come only from archived official documents (candidate or party website). Never media,
  Wikipedia, comparators, interviews, social posts, or model knowledge.
- Every stance = verbatim quote + source id (+ page). No quote → "non mentionné".
- "Non mentionné" never counts for or against a candidate.
- Source URLs/quotes are only revealed on the results page (not during the quiz).
- Questions in neutral French; roughly half phrased "for X", half "against Y".
- Coverage balanced: no candidate dominates the scored questions.

## Program status dots
- 🟢 `officiel` — official 2027 program published (PDF or dedicated program page)
- 🟠 `partiel` — no 2027 program yet, but programmatic content exists: 2024 programs of their
  party (législatives / européennes) or proposals on their official websites
- 🔴 `aucun` — nothing usable yet

## Pipeline
1. `sources/<slug>/candidate.json` — who, party, declaration source, official sites, status.
2. `tools/fetch.py` — archive each source: raw file + extracted text + sha256 in `manifest.json`.
3. `data/propositions/<slug>.json` — concrete propositions with verbatim quotes, per theme.
4. `data/questions.json` — ~30 questions derived from common/divergent propositions.
5. `data/stances.json` — question × candidate → pour / contre / non_mentionne + quote + source.
6. `tools/verify_quotes.py` — every quote must be found verbatim (whitespace/typography-normalised)
   in the archived text. Plus an independent agent pass checking the quote supports the stance.
7. `site/` — Astro static site, French.

## Candidates (Wikipedia « Candidatures à l'élection présidentielle française de 2027 », 30 Oct 2026)
arthaud, asselineau, attal, batho, becht, bertrand, bouamrane, cazeneuve, dupont-aignan, durif,
glucksmann, kazib, labib, lalanne, le-pen, lisnard, markovic, mathieu, melenchon, mikolajczak,
mlekuz, philippe, philippot, platret, polony, retailleau, roussel, ruffin, tondelier, zemmour

## État au 30 octobre 2026
- 32 candidats (21 🟢, 10 🟠, 1 🔴), ~200 documents archivés, 32 questions avec explication,
  287 positions / 315 citations vérifiées à 100 %, relecture indépendante (33 positions retirées).
- Site construit (`site/dist`), testé desktop + mobile ; non déployé.
- À revoir : Mikolajczak (programme annoncé le 2 nov.), Mélenchon (nouvelle édition 6 nov.),
  Becht (parties 9–11 du livre les 2, 5, 9 nov.), Asselineau (programme « prochainement »),
  Platret (livre annoncé en novembre), Retailleau / Dupont-Aignan / Ruffin (publication par étapes).
- Choix à valider par Max : explications `help` (rédigées, non issues des programmes) ;
  projet du PS utilisé pour Glucksmann ; copie archivée Wayback pour Durif ; Cazeneuve
  (lettre « pas une déclaration de candidature » mais déclaré selon la presse).
