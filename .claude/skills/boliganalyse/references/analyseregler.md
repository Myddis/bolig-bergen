# Analyseregler

## Hva du skal finne i salgsoppgaven

| Område | Se etter |
|---|---|
| Nøkkelinfo | Prisantydning, fellesgjeld, totalpris, omkostninger, felleskost./mnd og hva den dekker (TV/internett, varmtvann, oppvarming), kommunale avgifter/år, eiendomsskatt |
| Areal | BRA-i (primær), BRA, BRA-e, P-ROM (eldre oppgaver), arealfordeling per etasje |
| Bolig | Soverom, rom, etasje, heis, balkong/terrasse og retning, parkering, bod, oppvarming, energimerke, byggeår, siste oppussing |
| Tilstandsrapport | Alle TG2 og TG3: bygningsdel, rom, beskrivelse, tiltak, kostnadsestimat. Merk TGIU (ikke undersøkt) |
| Våtrom | Alder, membran, sluk, fall, ventilasjon, fuktmåling |
| Tekniske anlegg | El-anlegg (alder, samsvarserklæring, sikringsskap), vann/avløp (alder, materiale), varmtvannsbereder (alder) |
| Konstruksjon | Tak, vinduer, fasade, drenering, grunnmur, fukt i kjeller, pipe |
| Borettslag/sameie | Navn, antall enheter, total fellesgjeld, lånetype, rente, avdragsfritt til, nedbetalingstid, IN-ordning, disponible midler/vedlikeholdsfond, budsjett, planlagte felleskostnadsøkninger |
| Vedlikehold | Gjennomført og planlagt vedlikehold, rehabiliteringsplan, vedtak på generalforsamling, bygningsmessige utbedringer |
| Juridisk | Egenerklæring (alle «ja»-svar), ferdigattest/midlertidig brukstillatelse, godkjenning av rom/bruksendring, forkjøpsrett, reguleringsplan, heftelser/servitutter, radon, vedtekter om dyr og utleie |
| Omgivelser | Solforhold, utsikt, støy (vei, bybane, utesteder), barnehage og skole |
| Visning | Datoer og tider |

## Røde flagg (alltid med i `rodeFlagg` hvis de finnes)
- TG3 på våtrom, tak, drenering, el-anlegg, vann/avløp eller bærende konstruksjon.
- Våtrom eldre enn ca. 20 år eller uten dokumentert membran, særlig sammen med TG2.
- El-anlegg uten samsvarserklæring, eller med feil påpekt.
- Manglende ferdigattest, eller rom brukt som P-rom/soverom uten godkjenning.
- Avdragsfrihet på fellesgjelden som slutter innen 3 år. Regn ut omtrentlig økning i kr/mnd hvis mulig.
- Planlagt større rehabilitering (tak, fasade, rør, balkonger, heis) uten finansiering, eller med varslet økning i felleskostnadene.
- Høy fellesgjeld: over ca. 15 000 kr/m² BRA-i, eller over ca. 40 % av totalprisen.
- Felleskostnader over ca. 55 kr/m² BRA-i per mnd (husk å se hva de dekker).
- Fukt, råte, sopp eller skadedyr nevnt i rapport eller egenerklæring.
- Vesentlige «ja»-svar i egenerklæringen: tidligere vannskader, arbeid uten fagfolk, pågående tvister.
- Forkjøpsrett, eller vedtekter som hindrer dyrehold eller utleie hvis det betyr noe for brukeren.
- Høy radon, eller ikke målt i sokkel/1. etasje.
- Et må-krav i `kriterier.md` er brutt.

## Grove kostnadsintervaller (når takstmannen ikke oppgir tall)
Bruk bare som anslag, merket «anslag», og oppgi intervallet.

| Tiltak | Intervall |
|---|---|
| Nytt bad, lite (≤ 5 m²) | 200 000–350 000 kr |
| Nytt kjøkken | 100 000–250 000 kr |
| Utbedring el-anlegg / nytt sikringsskap | 20 000–80 000 kr |
| Nytt vaskerom | 80 000–150 000 kr |
| Utskifting varmtvannsbereder | 15 000–25 000 kr |
| Nye vinduer (per stk.) | 10 000–20 000 kr |
| Overflateoppussing (maling, gulv) per m² | 1 500–3 500 kr |

## Delscorer (0–100)

### Pris (`pris`)
- Sammenlign `krPerM2` med:
  1. median kr/m² for andre boliger i samme bydel i oversikten (minst 3), ellers
  2. referansepris i `kriterier.md`, ellers
  3. din egen vurdering, som da skrives som usikker i `delscoreBegrunnelse`.
- Utgangspunkt 70 når prisen er lik referansen. Juster ±10 for hver 5 % under/over, og hold resultatet mellom 10 og 100.
- Trekk 5–15 hvis kjent oppussingsbehov ikke ser ut til å være priset inn.
- Trekk 20 hvis totalprisen er over `maksTotalpris`.

### Tilstand (`tilstand`)
- Start på 100.
- TG3: −20 hver på våtrom, tak, drenering, el-anlegg eller vann/avløp, ellers −10.
- TG2: −6 hver på våtrom, ellers −3.
- Trekk 5 hvis noe er ikke undersøkt (TGIU) der det burde vært undersøkt.
- Trekk 5–10 hvis våtrom er over 20 år, og 5 hvis el-anlegget er over 30 år.
- Laveste verdi er 5.

### Økonomi i laget (`okonomi`)
- Start på 80.
- Fellesgjeld per m² BRA-i: under 5 000 kr gir +10, 5 000–15 000 kr gir 0, over 15 000 kr gir −15.
- Avdragsfrihet som slutter innen 3 år: −10.
- Planlagte tiltak med varslet økning i felleskostnadene: −5 til −20.
- Solid vedlikeholdsfond eller disponible midler: +5.
- Felleskost. per m² over 55 kr: −10. Under 35 kr: +5.
- Selveier uten sameie av betydning: sett 75 og begrunn.
- Hold resultatet mellom 10 og 100.

### Beliggenhet (`beliggenhet`)
- Grunnlag: den **lengste** av de to reisetidene, der hver reisetid er det raskeste av kollektiv og gange.

  | Reisetid | Grunnlag |
  |---|---|
  | ≤ 15 min | 100 |
  | ≤ 20 min | 90 |
  | ≤ 25 min | 80 |
  | ≤ 30 min | 70 |
  | ≤ 40 min | 50 |
  | Over 40 min | 30 |

- Juster ±10 for foretrukne eller uønskede områder i `kriterier.md`, og ±5 for sol/utsikt eller støy.
- Står foretrukne områder som TODO i `kriterier.md`, gjøres ingen områdejustering. Skriv det i begrunnelsen.

### Mine kriterier (`kriterier`)
- Start på 50.
- Legg til poeng for oppfylte ønsker etter vekt, ca. +5 per vektpoeng, maks 100.
- Et ønske som ikke er oppfylt gir 0, ikke trekk. Trekk bare for klare motsetninger til noe brukeren har skrevet at de ikke vil ha.
- «Kort vei til Bybanen» er oppfylt når `bybane.meter` (gangavstand fra `reisetid.py`) er under 700.
- Eieform: selveier gir pluss etter vekt. Andel og aksje gir verken pluss eller trekk.
- Hvis et må-krav er brutt: maks 30.

### Totalscore
`score = round(sum(delscore × vekt))` med vektene fra `kriterier.md`.
Hvis et må-krav er brutt, er maks totalscore 45.

## Foreløpig modus
Brukes når pris- eller økonomitallene mangler (typisk: PDF-en er bare vedlegg og Finn-annonsen er blokkert), og brukeren har sagt «fortsett».

- Sett delscorer uten grunnlag til `null`. Typisk `pris` (uten totalpris) og `okonomi` (uten fellesgjeld/felleskost.).
- Gjett aldri tall for å kunne score.
- **Foreløpig score** = vektet snitt av delscorene som finnes, med vektene skalert opp så de summerer til 1:
  `score = round(sum(delscore × vekt) / sum(vekt))`, bare over delscorer som ikke er `null`.
- Krever minst `tilstand` og én annen delscore. Ellers `score: null`.
- Sett `forelopig: true` og `manglerTall` til feltnavnene som mangler (f.eks. `["prisantydning", "fellesgjeld", "fellesMnd", "omkostninger"]`).
- Skriv i `oppsummering` at scoren er foreløpig og hva som mangler.
- Når tallene kommer («Fullfør analysene»): regn ut alt på nytt, og sett `forelopig: false` og `manglerTall: []`.

## Tone
- Skriv som en erfaren og nøktern rådgiver: konkret, ingen salgsspråk.
- Vis til sidetall der du kan, f.eks. «(PDF s. 23)». Sidetallet er PDF-sidetallet, ikke rapportens egen nummerering.
- Skill tydelig mellom fakta fra salgsoppgaven og dine vurderinger og anslag.
