# Sourcing brief (for research agents)

Project: `/Users/max/perso/presidentielle-2027` — read `PLAN.md` first. Today is 2026-10-30.
Goal: for each assigned candidate, find and ARCHIVE their official program sources. You are NOT
analysing positions yet — only collecting documents. Neutrality matters: apply the exact same effort
and rules to every candidate.

## For each candidate
1. **Status check.** Confirm they are still a declared candidate for the 2027 presidential election
   as of today (news search is fine for this step only). If they withdrew / lost a primary / now
   back someone else, record that with the source and stop there for that candidate.
2. **Official sites.** Identify the candidate's campaign site, personal site and party site(s).
3. **2027 program.** Look for an official 2027 presidential program: a PDF, or a dedicated program
   page ("programme", "projet", "propositions", "nos mesures") published for 2027 on an official site.
4. **If no 2027 program**, archive the best substitutes, in this priority order, max ~4 sources:
   a. programmatic pages/PDFs on the candidate's or party's official site (current proposals,
      "nos propositions", manifesto, "projet pour la France", book-length program PDFs published
      by the party)
   b. the party's own 2024 program (législatives 2024 or européennes 2024). If it is a coalition
      program shared by several parties (e.g. Nouveau Front populaire, Ensemble), still archive it
      but say so in the label, e.g. "Programme du Nouveau Front populaire — législatives 2024
      (commun LFI, PS, Écologistes, PCF…)".
   Prefer the most comprehensive and most recent documents. Skip pure news/blog posts, press
   releases about a single event, donation pages, merch, events.
5. **Only official domains** of the candidate or their party. NEVER media articles, Wikipedia,
   comparators (MonVote2027, ÉlyséeScope…), YouTube, social networks.
6. **Archive** each source with the fetch tool (run from the project root):
   ```
   tools/.venv/bin/python -W ignore tools/fetch.py <slug> "<url>" --label "<label in French>" \
     --year <year> --kind pdf|page --official-2027 yes|no --publisher "<site name>"
   ```
   Then open `sources/<slug>/text/<id>.txt` and check the extracted text is real program content
   (not a cookie wall, menu, or a 300-char stub). If extraction is bad or the site blocks (403,
   JS-only page), delete that entry's files + manifest entry and list the URL under `blocked` in
   candidate.json so the lead can archive it with a real browser.
   Multi-page programs on a website (one page per theme): archive each theme page (it's fine to go
   above 4 sources in that case, up to ~15).
7. **Write `sources/<slug>/candidate.json`**:
   ```json
   {
     "slug": "…", "name": "Prénom Nom", "party": "Nom du parti", "party_short": "Sigle",
     "declared": true,
     "declaration_note": "Candidature annoncée le … (source)",
     "declaration_source": "https://…",
     "official_sites": ["https://…"],
     "program_status": "officiel | partiel | aucun",
     "program_status_note": "One French sentence for users, e.g. « Pas encore de programme 2027 ; propositions issues du programme des législatives 2024 du RN et du site officiel. »",
     "blocked": [{"url": "…", "why": "403 / JS-rendered / scanned PDF"}],
     "notes": "anything the lead should know"
   }
   ```
   Status: `officiel` only if an official 2027 program was archived; `partiel` if only substitutes;
   `aucun` if nothing usable.

## Report back
A short table per candidate: status, sources archived (label + chars of text), blocked URLs, doubts.
Do not paste document contents into your report.
