# Isoloir — présidentielle 2027

Quiz neutre : des propositions tirées des programmes officiels, sans nom ni visage ; au « dépouillement »,
les noms apparaissent avec les citations exactes et leurs sources. Règles et décisions : `PLAN.md`.

## Données (tout est vérifiable)
| Étape | Fichiers | Outil |
|---|---|---|
| Candidats, statut (pastille), sites | `sources/<slug>/candidate.json` | — |
| Documents archivés (brut + texte + sha256) | `sources/<slug>/raw`, `text`, `manifest.json` | `tools/fetch.py` (`--from-file` pour un PDF téléchargé à la main, `--html-full` si l'extraction est tronquée) |
| Propositions relevées | `data/propositions/<slug>.json` | brief : `tools/EXTRACTION_BRIEF.md` |
| Questions (+ `scope` interne, `help` affiché) | `data/questions.json` | la version courte (30) est choisie par `build_data.py` |
| Positions (pour / contre + citations) | `data/stances/<slug>.json` | brief : `tools/STANCE_BRIEF.md` |
| Relecture indépendante | `data/review/<slug>.md` | brief : `tools/REVIEW_BRIEF.md` |
| Vérification mot pour mot | — | `tools/.venv/bin/python tools/verify_quotes.py` (doit afficher 100 %) |
| Export vers le site | `site/src/data/*.json`, `site/public/photos` | `tools/.venv/bin/python tools/build_data.py` |

Mettre à jour un candidat : archiver le nouveau document avec `fetch.py`, refaire ses positions
(brief stances puis review), lancer `verify_quotes.py` puis `build_data.py`.

## Site
```bash
cd site && npm install && npm run dev      # http://localhost:4321
npm run build                              # sortie statique dans site/dist
```
Aucun serveur, aucun cookie, aucune mesure d'audience : les réponses restent dans `localStorage`
(clé `isoloir:v1`). La page du quiz n'embarque que les questions ; noms, citations et liens ne sont
chargés que sur `/resultats`.

## Déploiement Cloudflare
Projet relié au dépôt Git, à la racine du dépôt : *Build command* `npm run build` (installe puis construit
`site/`), *Deploy command* `npx wrangler deploy` (lit `wrangler.jsonc` : site statique servi depuis
`site/dist`). Version de Node fixée par `.node-version`. Chaque push sur `main` redéploie.
