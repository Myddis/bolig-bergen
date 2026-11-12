# Boligjakt Bergen

Privat verktøy for å vurdere leiligheter i Bergen. Svar på norsk (bokmål).

- **Oversikt (artifact):** https://claude.ai/artifact/PSuhmmL6pbLh7nYsgSyQZ2. Kart med alle analyserte boliger. Dataene ligger i artifactens database (samling `leiligheter`) og leses/skrives med `ArtifactData`.
- **Analyse av en ny bolig:** bruk skillen `/boliganalyse` (`.claude/skills/boliganalyse/`) med Finn-lenke og salgsoppgave (PDF).
- **Kriterier og økonomi:** `.claude/skills/boliganalyse/references/kriterier.md`.
- **Arbeidssteder og reisetid:** `config.json` (speiles i databasen som `oppsett/arbeidssteder`).

## Struktur
- `scripts/geokod.py`: adresse til koordinater og bydel (Kartverket, ws.geonorge.no).
- `scripts/reisetid.py`: kollektiv og gange (Google Maps Routes API, Entur som reserve), sykkel og nærmeste holdeplass (Entur).
- `scripts/omrade.py`: prisutvikling i strøket, budmarked, solscore (Eiendomssjekk) og Bergen-indeks (SSB).
- `scripts/beregn.py`: totalpris, kr/m², månedskostnad og investering i tre scenarier.
- `scripts/bygg_kart.py`: bygger `oversikt/bergen.topo.json` fra Kartverket N50 og SSB-bydeler. Kjøres sjelden.
- `oversikt/index.html` + `oversikt/bergen.topo.json`: kilden til artifacten.
  - Publiser på nytt med Artifact-verktøyet, `url` = artifact-URL-en over og `files: {"bergen.topo.json": "oversikt/bergen.topo.json"}`.
  - Uten `capabilities` beholdes `db`.
- `data/leiligheter/*.json`: sikkerhetskopi, tas bare når Håkon ber om det. Databasen er hovedlageret.

## Nettverk
Skymiljøet `bolig-bergen` slipper til `www.finn.no`, `ws.geonorge.no`, `api.entur.io`, `nedlasting.geonorge.no`, `data.ssb.no`, `eiendomssjekk.no` og `routes.googleapis.com`.
Reisetid (kollektiv og gange) hentes fra Google Maps Routes API. API-nøkkelen ligger som nettverkshemmelighet i skymiljøet (header `X-Goog-Api-Key`), og proxyen legger den på. Entur er reserve og brukes for sykkel og nærmeste holdeplass.
Finn blokkerer WebFetch og `curl` fra skyen (DataDome). Ikke prøv å omgå det.
Les Finn gjennom Håkons egen nettleser når verktøyene finnes: Claude i Chrome (`claude-in-chrome`) eller nettleseren i Claude-appen (`Claude_Browser`). Ellers brukes salgsoppgaven og skjermbilder.
Håkon (arbeidssted-id `meg`) og samboeren Camilla (`samboer`) er brukerne.
