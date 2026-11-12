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
- Forkjøpsrett for andre enn BOB-medlemmer (f.eks. OBOS eller Vestbo), som kan gjøre at dere mister boligen etter budrunden. Vedtekter som hindrer dyrehold eller utleie, hvis det betyr noe for brukeren.
- BOB-forkjøpsrett som allerede er forhåndsutlyst med interessenter, slik at andre BOB-medlemmer med lengre ansiennitet kan ta boligen.
- Høy radon, eller ikke målt i sokkel/1. etasje.
- Totalpris over kjøpsrammen, reisetid over 30 min, månedskostnad over grensen eller mer enn én større jobb (se «Røde flagg fra kriteriene deres»).

## Grønne flagg (alltid med i `gronneFlagg` hvis de finnes)
Klare fordeler for akkurat Håkon og Camilla. Grønne flagg påvirker ikke scoren direkte, men skal nevnes i `oppsummering`.
- **BOB-forkjøpsrett:** andel i et borettslag tilknyttet BOB der BOB-medlemmer har forkjøpsrett. Håkon og Camilla er BOB-medlemmer og kan gå inn på høyeste bud. Sett `bobForkjopsrett: true`, og skriv fristen for å melde interesse og om forkjøpsretten er forhåndsutlyst. Er den forhåndsutlyst, kan forkjøpsretten bare brukes hvis dere meldte interesse innen fristen. Skriv det tydelig.
- Sett `bobForkjopsrett: false` når forkjøpsretten tilhører et annet boligbyggelag eller det ikke er forkjøpsrett, og `null` når det er ukjent.

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

## Boligscore (0–100)
Modellen følger `references/boligscore.md` («Boligscore – førstegangskjøp i Bergen»). Boligen vurderes som egen bolig med salg etter 3–5 år.

- Hver av de ni kategoriene får et **grunnlag** fra 0 til 100 etter reglene under.
- Grunnlaget gjøres om til en **karakter** fra 0 til 10 i halve trinn: `karakter = round(grunnlag / 5) / 2`.
- `poeng = karakter / 10 × vekt`. **Totalscoren** er summen av poengene, med én desimal.
- Det finnes ingen må-krav, tak eller trekk. Det som tidligere var må-krav, blir røde flagg og påvirker kategoriene og risikonivået.
- Gi aldri høy karakter fordi informasjon mangler. Sett ukjente forhold nøytralt og skriv dem i `mangler`.

Lagre i `kategorier.<navn>` som `{karakter, poeng, grunnlag}`, og begrunn hver kategori i `kategoriBegrunnelse.<navn>`. Vektene står i `kriterier.md`.

| Nøkkel | Kategori | Vekt |
|---|---|---|
| `beliggenhet` | Beliggenhet og mikrolokasjon | 18 |
| `kjopspris` | Kjøpspris og markedsverdi | 17 |
| `videresalg` | Videresalgspotensial | 15 |
| `teknisk` | Teknisk tilstand og risiko | 14 |
| `oppgradering` | Oppgraderings- og verdipotensial | 12 |
| `planlosning` | Planløsning og areal | 8 |
| `fellesokonomi` | Sameie/borettslag og fellesøkonomi | 6 |
| `trivsel` | Egen trivsel og bokvalitet | 5 |
| `lopende` | Løpende kostnader | 5 |

### Beliggenhet og mikrolokasjon (`beliggenhet`, 18)
Tre like deler: `grunnlag = (tilgjengelighet + sol + omgivelser) / 3`. Lagre delene i `beliggenhetDeler`. Vurder den konkrete adressen, ikke bare bydelen.

**Tilgjengelighet** = ½ jobb + ¼ sentrum + ¼ kollektiv:
- **Jobb:** den lengste av reisetidene til Håkon og Camilla. Hver reisetid er det raskeste av kollektiv og gange. `100 − 2 × (minutter − 15)`, mellom 30 og 100.
- **Sentrum:** reisetid til sentrum (`pendling.sentrum`). `100 − 3 × (minutter − 10)`, mellom 30 og 100.
- **Kollektiv:** 100 hvis Bybanen er under 700 m eller buss under 400 m å gå. 30 hvis begge er over 1 km. Ellers 60.

**Sol.** Utgangspunkt er `sol.solscore` (0–100) fra `scripts/omrade.py`. Den er målt på bakkenivå, så juster:
- +10 for 4. etasje eller høyere, eller for en solrik uteplass mot sør eller vest. Gi bare +10 én gang.
- −10 hvis uteplassen eller stuen vender mot nord, eller er beskrevet som skyggefull.
- Mangler solscore, start på 50 og skriv det i `mangler`.

**Omgivelser.** Start på 60, og juster med tabellen. Hold resultatet mellom 0 og 100.

| Forhold | Justering |
|---|---|
| Dagligvare ≤ 400 m / > 1 km å gå (`nabolag.dagligvare.meter`) | +10 / −10 |
| Treningssenter ≤ 800 m, eller minst 10 serveringssteder innen 1 km (`nabolag`) | +5 |
| Park, sjø, vann eller turområde innen ca. 500 m | +10 |
| Utsikt beskrevet i annonse eller salgsoppgave | +5 |
| Boligen eller tomten i gul / rød støysone (støysonekart i salgsoppgaven) | −10 / −20 |
| Nabolagsprofilen (Finn/Nabolag.no) sier mye støy, under ca. 60/100 | −5 |
| Hovedvei, terminal, industri eller utesteder rett ved | −10 |
| Trygghet i nabolagsprofilen ≥ 85 / < 60 | +5 / −10 |

- Ligger bare en liten del av tomten i støysone, og nabolagsprofilen sier lite støy (80/100 eller mer), gi halvt trekk.
- Lagre funnene i `omgivelser` (støy, natur, utsikt og trafikk, med kilde og PDF-side).

### Kjøpspris og markedsverdi (`kjopspris`, 17)
- Sammenlign `krPerM2` med:
  1. `omrade.medianKrM2Leiligheter` fra `scripts/omrade.py`. Juster referansen for alder, standard og beliggenhet innad i strøket, og forklar justeringen. Ellers:
  2. median kr/m² for andre boliger i samme bydel i oversikten (minst 3), ellers
  3. din egen vurdering, som da skrives som usikker.
- Utgangspunkt 70 når prisen er lik referansen. ±10 for hver 5 % under eller over.
- **Forhandlingsrom:** typisk budavvik i strøket (`marked.avvikProsent`) over +5 % gir −5, og under 0 % gir +5.
- Kjent oppussingsbehov som ikke ser ut til å være priset inn gir −5 til −15.
- **Over kjøpsrammen:** er totalprisen ved prisantydning over `maksTotalpris` (4,9 mill), er grunnlaget maks 30. Legg et rødt flagg med `budForBudsjett`.
- Kr/m² sammenlignes alltid uten omkostninger: (prisantydning + fellesgjeld) / BRA-i.

### Videresalgspotensial (`videresalg`, 15)
Hvor lett boligen kan selges om 3–5 år, og hvor stor kjøpergruppen er. Start på 50.

| Forhold | Justering |
|---|---|
| Bred kjøpergruppe: 45–75 m² BRA-i og 1–3 soverom | +15 |
| Prisvekst i strøket mot Bergen (`omrade.vekst5aar` mot `bergenVekst5aar`): ≥ 1 poeng over / 0–1 over / 0–1 under / 1–2,5 under / mer enn 2,5 under | +15 / +10 / +5 / 0 / −10 |
| `marked.andelOver` ≥ 70 % | +10 |
| `marked.dagerPaaMarkedet` ≤ 14 | +5 |
| Uteplass | +5 |
| Selveier | +5 |
| 4. etasje eller høyere uten heis | −10 |
| Energimerke F eller G | −5 |

Har strøket få salg (under ca. 100 siste 12 mnd), skriv at veksttallet er usikkert.

### Teknisk tilstand og risiko (`teknisk`, 14)
- Start på 100.
- TG3: −20 hver på våtrom, tak, drenering, el-anlegg eller vann/avløp, ellers −10.
- TG2: −6 hver på våtrom, ellers −3.
- Trekk 5 hvis noe er ikke undersøkt (TGIU) der det burde vært undersøkt.
- Trekk 5–10 hvis våtrom er over 20 år, og 5 hvis el-anlegget er over 30 år.
- Laveste verdi er 5.

### Oppgraderings- og verdipotensial (`oppgradering`, 12)
Kan kostnadseffektive forbedringer gjøre boligen bedre å bo i og lettere å selge? Se `boligscore.md`, avsnitt 6.

| Situasjon | Grunnlag |
|---|---|
| Eldre kjøkken, overflater eller gulv som kan moderniseres kosmetisk, og prisen gjenspeiler dagens standard | 90–100 |
| Uutnyttet areal (loft, bod) som kan tas i bruk uten store inngrep | 80 |
| Innflyttingsklar, lite å hente | 50 |
| Vedlikehold som bare bevarer verdien (rør, vinduer, ventilasjon, el, fasade) | 40 |
| Totalrehabilitering av bad, rør eller el, fukt, eller inngrep i konstruksjon | 20–30 |
| Nylig oppusset av selger og priset deretter | 20 |

- Juster +10 hvis `krPerM2` er mer enn 10 % under `omrade.medianKrM2Leiligheter`, og −10 hvis den er mer enn 10 % over.
- Sett `verdiokningOppussing` (kr) etter disse tommelfingerreglene, merket som anslag:
  - overflater (maling, gulv): ca. 1–1,5 × kostnaden
  - nytt kjøkken eller bad der det gamle er utdatert: ca. 0,5–1 × kostnaden
  - verdibevarende tiltak: ca. 0
- Ikke regn med at en oppussing gir like mye i verdi som den koster.

### Planløsning og areal (`planlosning`, 8)
Start på 50.

| Forhold | Justering |
|---|---|
| BRA-i 45–75 m² / 40–45 eller 75–85 m² / over 85 m² / under 40 m² | +20 / +10 / +5 / −10 |
| Soverom: 2 / 3 eller flere / 1 med kontor (eget rom ≥ ca. 5 m²) / 1 («god toroms») | +20 / +15 / +10 / +5 |
| Boder og god oppbevaring | +5 |
| Gode lysforhold eller lite innsyn | +5 |
| Gjennomgangsrom, ulogisk planløsning eller mye bortkastet areal | −10 |

Rom som brukes som soverom uten godkjenning, teller ikke som soverom.

### Sameie/borettslag og fellesøkonomi (`fellesokonomi`, 6)
- Start på 80.
- Fellesgjeld per m² BRA-i: under 5 000 kr gir +10, 5 000–15 000 kr gir 0, over 15 000 kr gir −15.
- Avdragsfrihet som slutter innen 3 år: −10.
- Planlagte tiltak med varslet økning i felleskostnadene: −5 til −20.
- Solid vedlikeholdsfond eller disponible midler: +5.
- Regnskap, vedlikeholdsplan eller vedtekter som mangler: −5.
- Selveier uten sameie av betydning: sett 75 og begrunn.
- Felleskostnadene per m² vurderes ikke her, men i Løpende kostnader.

### Egen trivsel og bokvalitet (`trivsel`, 5)
Om boligen fungerer for dere i hverdagen gjennom eierperioden. Start på 50.

| Forhold | Justering |
|---|---|
| Balkong, terrasse eller annen privat uteplass | +15 |
| Innflyttingsklar, eller bare kosmetisk oppussing (`storreJobber` er tom) | +10 |
| Heis i 3. etasje eller høyere / ingen heis i 4. etasje eller høyere | +5 / −5 |
| Parkering eller trygg sykkelbod | +5 |
| Lyst og luftig, eller lite innsyn | +5 |

### Løpende kostnader (`lopende`, 5)
- Grunnlag: `100 − 10 × (mndKostnad − 22 000) / 1 000`, mellom 0 og 100. Under 22 000 kr gir 100.
- Felleskost. per m² BRA-i: under 45 kr gir +10, over 100 kr gir −10.
- Energimerke A eller B (`grontLan`) gir +10. F eller G gir −10, fordi strøm og oppvarming koster mer.
- Er `mndKostnad` over `maksMndKostnad` (28 000), legg et rødt flagg.

### Røde flagg fra kriteriene deres
Disse påvirker ikke scoren direkte, men skal stå først i `rodeFlagg` og nevnes i `oppsummering`:
- totalpris over 4,9 mill ved prisantydning (med `budForBudsjett`)
- reisetid over 30 min for Håkon eller Camilla
- månedskostnad over 28 000 kr
- mer enn én større jobb de neste 5 årene

### Risikonivå (`risiko`)
Separat fra scoren (`boligscore.md`, avsnitt 7). Sett `risiko: {"niva": "lav" | "middels" | "hoy", "grunner": [...]}`.
- **Høy:**
  - TG3 på våtrom, tak, drenering eller el som ikke ser ut til å være priset inn
  - fukt eller lekkasje som ikke er utbedret
  - mer enn én større jobb
  - rom brukt som soverom uten godkjenning
  - svak økonomi i laget
  - stor rehabilitering med kraftig økning i felleskostnader eller fellesgjeld
- **Middels:**
  - TG3 som er priset inn
  - TG2 på våtrom
  - eldre rør
  - el-anlegg uten dokumentasjon
  - planlagt rehabilitering
  - viktige dokumenter som mangler (full salgsoppgave, regnskap)
- **Lav:** ingen vesentlige problemer, og dokumentasjonen er god.

Ved høy risiko: skriv i `oppsummering` at det bør hentes mer dokumentasjon eller en fagkyndig vurdering før bud.

### Tolkning (`tolkning`)
| Score | Tolkning |
|---|---|
| 90–100 | Eksepsjonelt attraktivt |
| 80–89 | Svært attraktivt |
| 70–79 | Godt potensial |
| 60–69 | Flere kompromisser |
| 50–59 | Svakt objekt |
| Under 50 | Lite attraktivt |

Les alltid totalscore, risikonivå og resultat ved salg sammen. En bolig med 75 poeng og lav risiko kan være et bedre kjøp enn en med 85 poeng og høy risiko.

### Resultat ved salg (`resultatVedSalg`, ikke en del av scoren)
`beregn.py` regner ut resultatet ved salg etter 3 og 5 år i tre scenarier: pessimistisk (0 %), nøytralt (strøkets 5-årssnitt) og optimistisk.
- `resultat` = salgspris − kjøpspris − omkostninger − oppussing − salgskostnad − eierkostnader (renter etter fradrag, felleskost., avgifter, vedlikehold).
- `motLeie` legger til spart husleie og trekker fra avkastning på egenkapitalen.

Ikke anbefal et kjøp som bare lønner seg hvis prisene stiger. Nevn det pessimistiske resultatet i `oppsummering` hvis det er sterkt negativt etter 5 år.

## Foreløpig modus
Brukes når pris- eller økonomitallene mangler (typisk: PDF-en er bare vedlegg og Finn-annonsen er blokkert), og brukeren har sagt «fortsett».

- Sett kategorier uten grunnlag til `null`. Typisk `kjopspris` (uten totalpris), `fellesokonomi` og `lopende` (uten fellesgjeld og felleskost.).
- Gjett aldri tall for å kunne score.
- **Foreløpig score** = poengene som finnes, skalert opp til 100:
  `score = round(sum(poeng) / sum(vekt for kategoriene som finnes) × 100, 1)`.
- Krever minst `teknisk` og én annen kategori. Ellers `score: null`.
- Sett `forelopig: true` og `manglerTall` til feltnavnene som mangler (f.eks. `["prisantydning", "fellesgjeld", "fellesMnd", "omkostninger"]`).
- Skriv i `oppsummering` at scoren er foreløpig og hva som mangler.
- Når tallene kommer («Fullfør analysene»): regn ut alt på nytt, og sett `forelopig: false` og `manglerTall: []`.

## Tone
- Skriv som en erfaren og nøktern rådgiver: konkret, ingen salgsspråk.
- Vis til sidetall der du kan, f.eks. «(PDF s. 23)». Sidetallet er PDF-sidetallet, ikke rapportens egen nummerering.
- Skill tydelig mellom fakta fra salgsoppgaven og dine vurderinger og anslag.
