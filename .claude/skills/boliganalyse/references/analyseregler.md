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
  1. `omrade.medianKrM2Leiligheter` fra `scripts/omrade.py` (tinglyste salg i strøket siste kvartal). Juster referansen for alder, standard og beliggenhet innad i strøket, og forklar justeringen. Ellers:
  2. median kr/m² for andre boliger i samme bydel i oversikten (minst 3), ellers
  3. referansepris i `kriterier.md`, ellers
  4. din egen vurdering, som da skrives som usikker i `delscoreBegrunnelse`.
- Utgangspunkt 70 når prisen er lik referansen. Juster ±10 for hver 5 % under/over, og hold resultatet mellom 10 og 100.
- Trekk 5–15 hvis kjent oppussingsbehov ikke ser ut til å være priset inn.
- Trekk 20 hvis totalprisen (inkl. omkostninger, som på Finn) er over `maksTotalpris`, og skriv hvilket bud som trengs (`budForBudsjett`).
- Kr/m² sammenlignes alltid uten omkostninger (`krPerM2` = (prisantydning + fellesgjeld) / BRA-i), slik at andel og selveier blir sammenlignbare.

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
- Grunnlag: den **lengste** av de to reisetidene til jobb (Håkon og Camilla), der hver reisetid er det raskeste av kollektiv og gange. Reisetid til sentrum teller ikke.

  | Reisetid | Grunnlag |
  |---|---|
  | ≤ 15 min | 100 |
  | ≤ 20 min | 90 |
  | ≤ 25 min | 80 |
  | ≤ 30 min | 70 |
  | ≤ 40 min | 50 |
  | Over 40 min | 30 |

- Ingen justering for område (se `kriterier.md`).
- Solforhold: bruk `sol.solscore` fra `scripts/omrade.py`. ≥ 75 gir +10, ≤ 45 gir −10. Vurder også salgsoppgavens beskrivelse og retningen på uteplassen.
- Støy fra trafikkert vei, Bybanen eller utesteder: −5.

### Mine kriterier (`kriterier`)
- Start på 50.
- Legg til poeng for oppfylte ønsker etter vekt, +3 per vektpoeng, maks 100.
- Et ønske som ikke er oppfylt gir 0, ikke trekk. Trekk bare for klare motsetninger til noe brukeren har skrevet at de ikke vil ha.
- «Kort vei til kollektiv» er oppfylt når `bybane.meter` er under 700 eller `buss.meter` er under 400 (gangavstand fra `reisetid.py`).
- «Energimerke A eller B» er oppfylt når `grontLan` er `true` (fra `beregn.py`).
- «Gode solforhold» er oppfylt når `sol.solscore` er minst 65, eller når salgsoppgaven tydelig beskriver gode solforhold og uteplass mot sør eller vest.
- Eieform: selveier gir pluss etter vekt. Andel og aksje gir verken pluss eller trekk.
- **Må-krav** sjekkes mot `kriterier.md`:
  - totalpris (`budForBudsjett` fra `beregn.py`)
  - soverom (`soverom`, `soveromM2` og `kontor`)
  - reisetid for begge
  - `mndKostnad`
  - antall større jobber (`storreJobber`)
  - TG3
- Hvis et må-krav er brutt: maks 30, legg bruddet i `rodeFlagg`, og nevn det først i `oppsummering`.

### Investering (`investering`)
Satt sammen av fire deler. Regn ut hver del, skriv dem i `investeringDeler` og i begrunnelsen, og sett
`investering = round(0,30 × A + 0,25 × B + 0,25 × C + 0,20 × D)`.
Bruk data fra `scripts/omrade.py` (lagret som `omrade`, `marked` og `sol`) og scenariene fra `beregn.py`.

**A. Prisutvikling i strøket (30 %).** Sammenlign `omrade.vekst5aar` med `omrade.bergenVekst5aar` (SSB):

| Strøket mot Bergen | A |
|---|---|
| ≥ 1 prosentpoeng over | 100 |
| 0 til 1 over | 80 |
| 0 til 1 under | 60 |
| 1 til 2,5 under | 40 |
| Mer enn 2,5 under | 20 |
| Ingen områdetall | 50 (si fra) |

Har strøket få salg (under ca. 100 siste 12 mnd), skriv at tallet er usikkert.

**B. Verdiøkningspotensial (25 %).** Kan oppussing løfte verdien mer enn den koster, eller går pengene bare til å bevare den?

| Situasjon | B |
|---|---|
| Gammelt kjøkken, bad eller overflater, eller uutnyttet areal (loft, kjeller), der løftet trolig er større enn kostnaden, og prisen gjenspeiler dagens standard | 90–100 |
| Innflyttingsklar, lite å hente, men lite å betale | 60 |
| Vedlikehold som bare bevarer verdien venter (rør, vinduer, ventilasjon, el, fasade), moderat beløp | 40 |
| Store kostnader uten verdiløft (rørfornying, tak, drenering), eller nylig oppusset av selger og priset deretter (dere betaler for andres oppussing) | 20 |

- Juster +10 hvis `krPerM2` er mer enn 10 % under `omrade.medianKrM2Leiligheter`, og −10 hvis den er mer enn 10 % over.
- Sett `verdiokningOppussing` (kr) etter disse tommelfingerreglene. De er anslag og skal merkes som det:
  - overflater (maling, gulv): løft ca. 1–1,5 × kostnaden
  - nytt kjøkken eller bad der det gamle er utdatert: ca. 0,5–1 × kostnaden
  - verdibevarende tiltak (rør, vinduer, ventilasjon, el, bereder): ca. 0

**C. Salgbarhet (25 %).** Start på 60, og juster med:

| Forhold | Justering |
|---|---|
| `sol.solscore` ≥ 70 / ≤ 45 | +10 / −10 |
| `marked.andelOver` ≥ 70 % | +10 |
| `marked.dagerPaaMarkedet` ≤ 14 | +5 |
| 2–3 rom på 45–80 m² | +5 |
| Uteplass | +5 |
| Energimerke A eller B / F eller G | +5 / −5 |
| 4. etasje eller høyere uten heis | −10 |
| Kjent støy eller trafikk | −5 |

Hold resultatet mellom 0 og 100.

**D. Robusthet (20 %).** Hvor lang tid det tar før kjøpet lønner seg i det pessimistiske scenariet (0 % prisvekst, `investering.scenarier.pessimistisk.breakEvenAar`):

| År | D |
|---|---|
| ≤ 5 | 100 |
| ≤ 8 | 75 |
| ≤ 12 | 50 |
| ≤ 20 | 25 |
| Aldri | 10 |

**Krav til teksten:**
- Begrunnelsen skal nevne strøkets vekst mot Bergen, budmarkedet, solscore og hvor mange år kjøpet tar på å lønne seg i hvert av de tre scenariene.
- Ikke skriv at kjøpet «lønner seg etter X år» uten å si hvilket scenario og hvilken prisvekst det gjelder.

### Totalscore
`score = round(sum(delscore × vekt))` med de seks vektene fra `kriterier.md` (pris, tilstand, økonomi, beliggenhet, kriterier, investering).
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
