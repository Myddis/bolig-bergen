# Datamodell: `leiligheter/<finnkode>`

Ett dokument per bolig i artifactens database (samling `leiligheter`, doc_id = Finn-koden).
Kopi i repoet: `data/leiligheter/<finnkode>.json`.

- Alle beløp er i kroner (heltall), alle areal i m² og alle tider i minutter.
- Ukjent verdi er `null`. Ikke utelat felt som er listet som påkrevd.
- Kartoversikten leser feltnavnene nøyaktig som her. Endrer du dem, må `oversikt/index.html` også endres.

```jsonc
{
  // Identitet
  "finnkode": "412345678",
  "url": "https://www.finn.no/realestate/homes/ad.html?finnkode=412345678",
  "tittel": "Lys 3-roms med balkong …",         // annonsens overskrift
  "adresse": "Eksempelveien 12",                 // uten leilighetsnr.
  "postnr": "5063",
  "bydel": "Årstad",                             // fra geokod.py
  "lat": 60.3605, "lon": 5.3523,                 // påkrevd for prikk på kartet
  "boligtype": "Leilighet",
  "kilde": "salgsoppgave + annonse",             // eller "salgsoppgave", "kun annonse"
  "lagtTil": "2026-11-11T18:00:00Z",             // bare ved første lagring
  "analysertDato": "2026-11-11T18:00:00Z",

  // Pris og kostnader
  "prisantydning": 4100000,
  "fellesgjeld": 250000,
  "totalpris": 4350000,                          // beregn.py
  "omkostninger": 112000,
  "fellesMnd": 3900,
  "fellesDekker": "Kommunale avg., TV/internett, varmtvann",
  "kommunaleAvgAar": null,                       // null hvis inkludert i fellesMnd
  "eiendomsskattAar": null,
  "krPerM2": 75000,                              // beregn.py (totalpris / BRA-i)
  "felleskostPerM2": 67,                         // beregn.py
  "mndKostnad": 24500,                           // beregn.py (lån + felles + avgifter)
  "mndKostnadForklaring": "Lån 3,55 mill, 5,2 %, 30 år: 19 500 + felles 3 900 + …",

  // Boligen
  "braI": 58, "bra": 63, "braE": 5, "pRom": null,
  "soverom": 2, "rom": 3, "etasje": "3",
  "byggeaar": 1962, "eieform": "Andel",          // "Selveier" | "Andel" | "Aksje"
  "energimerke": "D", "heis": false, "balkong": true,
  "parkering": "Gateparkering",                  // fritekst eller null
  "oppvarming": "Varmepumpe, panelovner",

  // Tilstand (tilstandsrapporten)
  "tg3": [{ "rom": "Bad", "tekst": "Lekkasje ved sluk, fukt i vegg", "estimat": 250000, "side": 31 }],
  "tg2": [{ "rom": "Kjøkken", "tekst": "Mangler komfyrvakt", "estimat": 3000, "side": 33 }],
  "tgiu": ["Krypkjeller"],
  "oppussingEstimat": 280000,                    // midtpunkt, kr

  // Borettslag / sameie
  "borettslag": {
    "navn": "Eksempel Borettslag",
    "type": "Borettslag",                        // "Borettslag" | "Sameie" | "Aksjeselskap"
    "antallEnheter": 48,
    "fellesgjeldTotal": 12000000,
    "rente": 5.1,
    "avdragsfriTil": "2027-06",
    "disponibleMidler": 1500000,
    "forretningsforer": "BOB",
    "planlagteTiltak": ["Rehabilitering av balkonger 2027, ca. +400 kr/mnd"],
    "vurdering": "Moderat fellesgjeld …"
  },

  // Juridisk
  "ferdigattest": true,
  "forkjopsrett": true,
  "egenerklaringMerknader": ["Vannskade på bad 2019, utbedret av rørlegger"],

  // Reisetid (scripts/reisetid.py), én nøkkel per arbeidssted-id i config.json
  "pendling": {
    "samboer": { "kollektivMin": 28, "bytter": 0, "rute": "Bybanen 1", "gangMin": 58, "gangKm": 4.3, "sykkelMin": 25 },
    "meg":     { "kollektivMin": 12, "bytter": 0, "rute": "Buss 610", "gangMin": 25, "gangKm": 1.8, "sykkelMin": 14 }
  },

  // Vurdering
  "score": 72,
  "delscorer": { "pris": 70, "tilstand": 66, "okonomi": 75, "beliggenhet": 80, "kriterier": 70 },
  "delscoreBegrunnelse": { "pris": "…", "tilstand": "…", "okonomi": "…", "beliggenhet": "…", "kriterier": "…" },
  "oppsummering": "2–4 setninger med anbefaling.",
  "styrker": ["…"],
  "svakheter": ["…"],
  "rodeFlagg": ["TG3 på bad: lekkasje ved sluk (s. 31)"],
  "sporsmal": ["Når ble badet sist pusset opp, og finnes det dokumentasjon?"],
  "visninger": [{ "dato": "2026-11-16", "tid": "12:00–13:00" }],
  "mangler": ["Energimerke ikke oppgitt"],

  // Brukerens felt: settes bare ved første lagring, ellers aldri
  "status": "ny",                                // ny | interessert | visning | bud | avvist | solgt
  "favoritt": false,
  "notat": ""
}
```

## Andre dokumenter
- `oppsett/arbeidssteder`: `{ "liste": [{ "id", "navn", "adresse", "lat", "lon" }] }`. Speiler `config.json`. Oversikten tegner arbeidsstedene og lager reisetidsfiltre fra dette dokumentet.
