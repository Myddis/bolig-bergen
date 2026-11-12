# Datamodell: `leiligheter/<finnkode>`

Ett dokument per bolig i artifactens database (samling `leiligheter`, doc_id = Finn-koden).
Sikkerhetskopi i repoet (`data/leiligheter/<finnkode>.json`) tas bare når brukeren ber om det.

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
  "kilde": "salgsoppgave + annonse",             // f.eks. "salgsoppgave", "vedlegg + skjermbilde av annonse"
  "forelopig": false,                            // true når pris/økonomi mangler (se analyseregler.md)
  "manglerTall": [],                             // feltnavn som mangler, f.eks. ["prisantydning", "fellesgjeld"]
  "lagtTil": "2026-11-11T18:00:00Z",             // bare ved første lagring
  "analysertDato": "2026-11-11T18:00:00Z",

  // Pris og kostnader
  "prisantydning": 4100000,
  "fellesgjeld": 250000,
  "totalpris": 4462000,                          // beregn.py, som på Finn: prisantydning + omkostninger + fellesgjeld
  "prisInklFellesgjeld": 4350000,                // beregn.py, markedsverdi uten omkostninger (brukes til kr/m² og investering)
  "maksBud": 4680000,                            // beregn.py, høyeste bud som holder totalpris ≤ maksTotalpris
  "omkostninger": 112000,
  "fellesMnd": 3900,
  "fellesDekker": "Kommunale avg., TV/internett, varmtvann",
  "kommunaleAvgAar": null,                       // null hvis inkludert i fellesMnd
  "eiendomsskattAar": null,
  "krPerM2": 75000,                              // beregn.py ((prisantydning + fellesgjeld) / BRA-i)
  "felleskostPerM2": 67,                         // beregn.py
  "mndKostnad": 24500,                           // beregn.py (lån + felles + avgifter), før rentefradrag
  "mndKostnadEtterFradrag": 22300,               // beregn.py, første år
  "budForBudsjett": null,                        // beregn.py: maks bud for å holde totalpris ≤ maksTotalpris, null hvis innenfor
  "mndKostnadForklaring": "Lån 3,55 mill, 5,2 %, 30 år: 19 500 + felles 3 900 + …",

  // Boligen
  "braI": 58, "bra": 63, "braE": 5, "pRom": null,
  "soverom": 2, "rom": 3, "etasje": "3",
  "soveromM2": [12.4, 10.8],                     // størrelse på hvert soverom
  "byggeaar": 1962, "eieform": "Andel",          // "Selveier" | "Andel" | "Aksje"
  "energimerke": "D", "heis": false, "balkong": true,
  "parkering": "Gateparkering",                  // fritekst eller null
  "oppvarming": "Varmepumpe, panelovner",

  // Tilstand (tilstandsrapporten)
  "tg3": [{ "rom": "Bad", "tekst": "Lekkasje ved sluk, fukt i vegg", "estimat": 250000, "side": 31 }],
  "tg2": [{ "rom": "Kjøkken", "tekst": "Mangler komfyrvakt", "estimat": 3000, "side": 33 }],
  "tgiu": ["Krypkjeller"],
  "oppussingEstimat": 280000,                    // midtpunkt, kr
  "storreJobber": ["Bad"],                       // større jobber de neste 5 årene (bad, kjøkken, el, tak, drenering, vinduer, rør)

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

  // Nærmeste Bybane-holdeplass (scripts/reisetid.py → _bybane)
  "bybane": { "stopp": "Wergeland", "meter": 290, "gangMin": 4 },
  "buss": { "stopp": "Wergelandsveien", "meter": 120, "gangMin": 2 },   // reisetid.py → _buss

  // Strøk og marked (scripts/omrade.py)
  "omrade": { "navn": "Sandviken", "url": "https://eiendomssjekk.no/omraade/sandviken-bergen", "medianKrM2": 86154,
              "medianKrM2Leiligheter": 86291, "salg12mnd": 750, "vekst5aar": 5.2, "vekst12mnd": 7.8,
              "bergenVekst5aar": 7.1, "bergenVekst12mnd": 10.5 },
  "marked": { "avvikProsent": 3.3, "andelOver": 65, "dagerPaaMarkedet": 9, "grunnlagSalg": 297 },
  "sol": { "solscore": 63, "timerJuni": 17.3, "timerDes": 4.8, "solvurdering": "Middels solforhold" },
  "kollektivFrekvens": { "stopp": "Buss, Eikeviken", "avstand": "1 min til fots (70 m)", "avgangerRushtid": 23 },
  "kilderOmrade": ["https://eiendomssjekk.no/…", "https://www.ssb.no/statbank/table/07221"],
  "prisvekst": { "pessimistisk": 0, "forventet": 5.2, "optimistisk": 7.8, "kilde": "Eiendomssjekk, tinglyste salg i Sandviken …" },
  "verdiokningOppussing": 10000,                 // anslått verdiløft fra oppussingEstimat (analyseregler.md)
  "forventetPris": 4122000,                      // beregn.py: prisantydning × (1 + typisk budavvik i strøket)
  "mndKostnadForventetPris": 25752,              // beregn.py

  // Investering (beregn.py): kjøp mot å fortsette å leie, tre scenarier
  "investering": {
    "scenarier": {
      "pessimistisk": { "vekst": 0, "breakEvenAar": 10, "verdi5": 4107021, "formueKjop5": 810078, "formueLeie5": 1012890, "gevinst5": -202811 },
      "forventet":    { "vekst": 5.2, "breakEvenAar": 2, "…": "…" },
      "optimistisk":  { "vekst": 7.8, "breakEvenAar": 1, "…": "…" }
    },
    "breakEvenAar": 2, "verdi5": 5291827, "formueKjop5": 1994884, "formueLeie5": 1012890, "gevinst5": 981995,   // = forventet
    "antagelser": "Prisvekst 0 / 5.2 / 7.8 %/år …"
  },
  "investeringDeler": { "omradeVekst": 40, "verdipotensial": 50, "salgbarhet": 70, "robusthet": 50 },

  // Vurdering
  "score": 72,                                   // foreløpig score hvis forelopig: true
  "delscorer": { "pris": 70, "tilstand": 66, "okonomi": 75, "beliggenhet": 80, "kriterier": 70, "investering": 52 },
  "delscoreBegrunnelse": { "pris": "…", "tilstand": "…", "okonomi": "…", "beliggenhet": "…", "kriterier": "…", "investering": "…" },
  "oppsummering": "2–4 setninger med anbefaling.",
  "styrker": ["…"],
  "svakheter": ["…"],
  "rodeFlagg": ["TG3 på bad: lekkasje ved sluk (PDF s. 31)"],
  "sporsmal": ["Når ble badet sist pusset opp, og finnes det dokumentasjon?"],
  "visninger": [{ "dato": "2026-11-16", "tid": "12:00–13:00" }],
  "mangler": ["Energimerke ikke oppgitt"],

  // Brukerens felt: settes bare ved første lagring, ellers aldri
  "status": "tilsalgs",                          // tilsalgs | solgt (eldre verdier som «ny» regnes som til salgs)
  "solgtDato": null,                             // settes av oversikten når boligen markeres som solgt
  "favoritt": false,
  "notat": ""
}
```

## Andre dokumenter
- `jobber/<jobbId>`: analysejobber lagt inn fra oversikten («Legg til leilighet»).
  ```jsonc
  {
    "finnUrl": "https://www.finn.no/realestate/homes/ad.html?finnkode=480597898",
    "finnkode": "480597898",
    "filer": [{ "id": "<asset-id>", "navn": "annonse.png", "type": "image/png" },
              { "id": "<asset-id>", "navn": "salgsoppgave.pdf", "type": "application/pdf" }],
               // PDF over 19 MB deles i oversikten. Hver del har i tillegg
               // "original": "salgsoppgave.pdf", "del": 1, "av": 3, "fraSide": 1, "tilSide": 13
    "status": "venter",        // venter | analyserer | ferdig | feilet
    "opprettet": "2026-11-12T10:00:00Z", "startet": null, "ferdig": null,
    "melding": "",             // fremdrift, eller hva som gikk galt
    "score": null, "forelopig": null
  }
  ```
- Bolig-dokumentet får `vedlegg: [{id, navn, type}]` når det er analysert fra køen. Filene vises via `/_blob/<id>`.
- `oppsett/arbeidssteder`: `{ "liste": [{ "id", "navn", "adresse", "lat", "lon" }] }`. Speiler `config.json`. Oversikten tegner arbeidsstedene og lager reisetidsfiltre fra dette dokumentet.
