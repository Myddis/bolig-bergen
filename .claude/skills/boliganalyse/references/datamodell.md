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
  "prisInklFellesgjeld": 4350000,                // beregn.py, markedsverdi uten omkostninger (brukes til kr/m² og resultat ved salg)
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
  "rente": 5.5,                                  // beregn.py, renten som er brukt (renteGront ved grønt boliglån)
  "grontLan": false,                             // beregn.py, true ved energimerke A/B (bare A hvis bygget etter 2019), null hvis energimerket er ukjent
  "budForBudsjett": null,                        // beregn.py: maks bud for å holde totalpris ≤ maksTotalpris, null hvis innenfor
  "mndKostnadForklaring": "Lån 3,55 mill, 5,2 %, 30 år: 19 500 + felles 3 900 + …",

  // Boligen
  "braI": 58, "bra": 63, "braE": 5, "pRom": null,
  "soverom": 2, "rom": 3, "etasje": "3",
  "soveromM2": [12.4, 10.8],                     // størrelse på hvert soverom
  "kontor": { "m2": 6.5, "navn": "Arbeidsrom", "side": 12 },  // eget rom som kan brukes som kontor (Planløsning i analyseregler.md), ellers null
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

  // Reisetid (scripts/reisetid.py), én nøkkel per id under arbeidssteder og steder i config.json.
  // «sentrum» (Byparken) teller i tilgjengelighet under Beliggenhet (¼).
  "pendling": {
    // kilde: "Google Maps" (kollektiv og gange) eller "Entur" (reserve). Sykkel er alltid Entur.
    "samboer": { "kollektivMin": 28, "bytter": 0, "rute": "Bybanen 1", "gangMin": 58, "gangKm": 4.3, "sykkelMin": 25, "kilde": "Google Maps" },
    "meg":     { "kollektivMin": 12, "bytter": 0, "rute": "Buss 610", "gangMin": 25, "gangKm": 1.8, "sykkelMin": 14 },
    "sentrum": { "kollektivMin": 16, "bytter": 0, "rute": "Buss 12", "gangMin": 69, "gangKm": 4.9, "sykkelMin": 18 }
  },

  // Nærmeste Bybane-holdeplass (scripts/reisetid.py → _bybane)
  "bybane": { "stopp": "Wergeland", "meter": 290, "gangMin": 4 },
  "buss": { "stopp": "Wergelandsveien", "meter": 120, "gangMin": 2 },   // reisetid.py → _buss

  // Strøk og marked (scripts/omrade.py)
  "omrade": { "navn": "Sandviken", "url": "https://eiendomssjekk.no/omraade/sandviken-bergen", "medianKrM2": 86154,
              "medianKrM2Leiligheter": 86291, "salg12mnd": 750, "vekst5aar": 5.2, "vekst12mnd": 7.8,
              "bergenVekst5aar": 7.1, "bergenVekst12mnd": 10.5 },
  "marked": { "avvikProsent": 3.3, "andelOver": 65, "dagerPaaMarkedet": 9, "grunnlagSalg": 297 },
  "sol": { "solscore": 63, "timerJuni": 17.3, "timerDes": 4.8, "solvurdering": "Middels solforhold",
           "malepunkt": "Helleveien 133", "adresserPaaEiendom": 3, "tomtM2": 1512 },   // målepunkt for solscoren (Eiendomssjekk)
  "kollektivFrekvens": { "stopp": "Buss, Eikeviken", "avstand": "1 min til fots (70 m)", "avgangerRushtid": 23 },
  "nabolag": { "dagligvare": { "navn": "Spar Eikeviken", "meter": 110 }, "trening": { "navn": "SATS Sandviken", "meter": 2900 },
               "servering1km": 6, "url": "https://eiendomssjekk.no/eiendom/4601-168-200/nabolag" },   // omrade.py → nabolag
  "omgivelser": { "stoy": "Gul støysone på 20 % av tomten (PDF s. 11), nabolagsprofil 84/100", "natur": "Turområde 300 m (PDF s. 5)",
                  "utsikt": "Utsikt mot Byfjorden (annonse)", "trafikk": null },   // fra annonse/salgsoppgave, null hvis ukjent
  "kilderOmrade": ["https://eiendomssjekk.no/…", "https://www.ssb.no/statbank/table/07221"],
  "prisvekst": { "pessimistisk": 0, "forventet": 5.2, "optimistisk": 7.8, "kilde": "Eiendomssjekk, tinglyste salg i Sandviken …" },
  "verdiokningOppussing": 10000,                 // anslått verdiløft fra oppussingEstimat (analyseregler.md)
  "forventetPris": 4122000,                      // beregn.py: prisantydning × (1 + typisk budavvik i strøket)
  "mndKostnadForventetPris": 25752,              // beregn.py

  // Resultat ved salg (beregn.py), ikke en del av scoren. Tre scenarier, etter 3 og 5 år.
  "resultatVedSalg": {
    "scenarier": {
      "pessimistisk": { "vekst": 0,   "aar3": { "salgspris": 3990000, "eierkostnader": 690000, "resultat": -780000, "motLeie": -120000 }, "aar5": { "…": "…" } },
      "forventet":    { "vekst": 5.2, "aar3": { "…": "…" }, "aar5": { "…": "…" } },
      "optimistisk":  { "vekst": 7.8, "aar3": { "…": "…" }, "aar5": { "…": "…" } }
    },
    "antagelser": "Prisvekst 0 / 5.2 / 7.8 %/år …"
  },

  // Vurdering (analyseregler.md, «Boligscore»). karakter 0–10 i halve trinn, poeng = karakter / 10 × vekt
  "score": 71.9,                                 // sum av poeng (0–100); foreløpig score hvis forelopig: true
  "tolkning": "Godt potensial",                  // 90+ Eksepsjonelt attraktivt … under 50 Lite attraktivt
  "kategorier": {
    "beliggenhet":   { "karakter": 7.5, "poeng": 13.5, "grunnlag": 73 },
    "kjopspris":     { "karakter": 5,   "poeng": 8.5,  "grunnlag": 50 },
    "videresalg":    { "…": "…" }, "teknisk": { "…": "…" }, "oppgradering": { "…": "…" },
    "planlosning":   { "…": "…" }, "fellesokonomi": { "…": "…" }, "trivsel": { "…": "…" }, "lopende": { "…": "…" }
  },
  "kategoriBegrunnelse": { "beliggenhet": "…", "kjopspris": "…", "videresalg": "…", "teknisk": "…", "oppgradering": "…",
                           "planlosning": "…", "fellesokonomi": "…", "trivsel": "…", "lopende": "…" },
  "beliggenhetDeler": { "tilgjengelighet": 75, "sol": 82, "omgivelser": 70 },
  "risiko": { "niva": "middels", "grunner": ["TG2 på bad: for lite fall til sluk (PDF s. 15)", "Full salgsoppgave mangler"] },   // lav | middels | hoy
  "oppsummering": "2–4 setninger med anbefaling.",
  "styrker": ["…"],
  "svakheter": ["…"],
  "rodeFlagg": ["TG3 på bad: lekkasje ved sluk (PDF s. 31)"],
  "gronneFlagg": ["BOB-forkjøpsrett: dere kan gå inn på høyeste bud (PDF s. 13)"],   // analyseregler.md, «Grønne flagg»
  "bobForkjopsrett": true,                       // true | false | null (ukjent)
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
- `oppsett/arbeidssteder`: `{ "liste": [{ "id", "navn", "adresse", "lat", "lon" }], "steder": [samme format] }`. Speiler `arbeidssteder` og `steder` i `config.json`. Stedene (sentrum) vises med reisetid i oversikten, men er ikke arbeidssteder. Oversikten tegner arbeidsstedene og lager reisetidsfiltre fra dette dokumentet.
