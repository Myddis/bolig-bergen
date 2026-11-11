# Boligjakt Bergen

Privat verktøy for å vurdere leiligheter i Bergen. Svar på norsk (bokmål).

- **Oversikt (artifact):** https://claude.ai/artifact/PSuhmmL6pbLh7nYsgSyQZ2. Kart med alle analyserte boliger. Dataene ligger i artifactens database (samling `leiligheter`) og leses/skrives med `ArtifactData`.
- **Analyse av en ny bolig:** bruk skillen `/boliganalyse` (`.claude/skills/boliganalyse/`) med Finn-lenke og salgsoppgave (PDF).
- **Kriterier og økonomi:** `.claude/skills/boliganalyse/references/kriterier.md`.
- **Arbeidssteder og reisetid:** `config.json` (speiles i databasen som `oppsett/arbeidssteder`).

## Struktur
- `scripts/geokod.py`: adresse til koordinater og bydel (Kartverket, ws.geonorge.no).
- `scripts/reisetid.py`: kollektiv, gange og sykkel til arbeidsstedene (Entur, api.entur.io).
- `scripts/beregn.py`: totalpris, kr/m² og månedskostnad.
- `scripts/bygg_kart.py`: bygger `oversikt/bergen.topo.json` fra Kartverket N50 og SSB-bydeler. Kjøres sjelden.
- `oversikt/index.html` + `oversikt/bergen.topo.json`: kilden til artifacten.
  - Publiser på nytt med Artifact-verktøyet, `url` = artifact-URL-en over og `files: {"bergen.topo.json": "oversikt/bergen.topo.json"}`.
  - Uten `capabilities` beholdes `db`.
- `data/leiligheter/*.json`: sikkerhetskopi, tas bare når Håkon ber om det. Databasen er hovedlageret.

## Nettverk
Skymiljøet `bolig-bergen` slipper til `www.finn.no`, `ws.geonorge.no`, `api.entur.io` og `nedlasting.geonorge.no`.
Finn blokkerer WebFetch og `curl` fra skyen (DataDome). Ikke prøv å omgå det.
Les Finn gjennom Håkons egen nettleser når verktøyene finnes: Claude i Chrome (`claude-in-chrome`) eller nettleseren i Claude-appen (`Claude_Browser`). Ellers brukes salgsoppgaven og skjermbilder.
Håkon (arbeidssted-id `meg`) og samboeren Camilla (`samboer`) er brukerne.
