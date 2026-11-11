# Boligjakt Bergen

Analyse av leiligheter i Bergen fra Finn-annonser og salgsoppgaver, med kartoversikt.

## Slik bruker du det
1. Start en ny økt i Claude Code med dette repoet og miljøet **bolig-bergen**. Start den helst fra **Claude-appen på PC-en**, og la appen være åpen. Da kan Claude lese Finn-annonsen og meglerens digitale salgsoppgave gjennom nettleseren i appen. Finn blokkerer alle andre automatiske hentinger.
2. Skriv `/boliganalyse https://www.finn.no/realestate/homes/ad.html?finnkode=…` og legg ved **full salgsoppgave** som PDF (knappen «Last ned salgsoppgave» hos megler, ikke bare vedleggene).
   - Starter du fra mobil eller web uten appen åpen: legg også ved et skjermbilde av Finn-annonsen der pris, fellesgjeld og felleskostnader står.
3. Claude:
   - leser salgsoppgaven og tilstandsrapporten
   - regner ut nøkkeltall og reisetid til jobb
   - setter en score og legger boligen inn i [oversikten](https://claude.ai/artifact/PSuhmmL6pbLh7nYsgSyQZ2)
4. I oversikten kan du filtrere, sette status (interessert, visning, bud …), markere favoritter og skrive notater.

## Tilpass
- **Kriterier, budsjett og vekter:** `.claude/skills/boliganalyse/references/kriterier.md`
- **Arbeidssteder:** `config.json`. Be Claude oppdatere reisetid for alle boligene etterpå.

## Datakilder
- Kartverket: adresser, stedsnavn og N50 Kartdata (CC BY 4.0)
- SSB: bydelsgrenser for Bergen
- Entur: reiseplanlegger (NLOD), som dekker Skyss
