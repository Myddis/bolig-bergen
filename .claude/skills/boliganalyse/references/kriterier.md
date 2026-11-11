# Mine kriterier

Kriteriene til Håkon og Camilla. De styrer delscorene «Mine kriterier» og «Investering», og vektingen av totalscoren.
Sist oppdatert: 2026-11-11.

## Økonomi
Tallene brukes i `scripts/beregn.py`, som leser blokken under. Behold formatet `nøkkel: verdi`.

```kriterier
egenkapital: 730000          # kr tilgjengelig egenkapital
maksTotalpris: 4900000       # finansieringsbevis, inkludert fellesgjeld (prisantydning/bud + fellesgjeld)
rente: 5.5                   # nominell rente, Fana Sparebank Boliglån Ung, satt med margin
nedbetalingAar: 30           # nedbetalingstid boliglån, år
maksMndKostnad: 25000        # smertegrense for samlet månedskostnad (lån + felleskost. + avgifter), før rentefradrag
husleie: 20540               # dagens husleie, kr/mnd, brukt i investeringsberegningen
husleievekst: 3.0            # antatt årlig økning i husleie hvis vi fortsetter å leie, %
prisvekst: 8.0               # antatt årlig prisvekst, % (siste 12 mnd i Bergen ifølge Hjemla; optimistisk hvis veksten flater ut)
alternativAvkastning: 4.0    # årlig avkastning på sparing hvis vi fortsetter å leie, %
salgskostnad: 80000          # meglerhonorar og markedsføring ved et senere salg, kr
rentefradrag: 22             # skattefradrag på renteutgifter, %
```

Lånet er innvilget ut fra framtidig inntekt (finansieringsbevis), så det sjekkes ikke mot 5 ganger inntekten.

## Må-krav
Brudd på et må-krav gir maks 30 i «Mine kriterier», maks 45 i totalscore og et rødt flagg.

- [ ] **Totalpris ≤ 4,9 mill** (prisantydning + fellesgjeld). Er prisantydningen over, skriv hvilket bud som trengs (`budForBudsjett`). Kravet regnes som brutt hvis budet må under prisantydningen.
- [ ] **Soverom:** minst 2, **eller** 1 soverom på minst 14 m².
- [ ] **Reisetid ≤ 30 min** for **både** Håkon og Camilla (raskeste av kollektiv og gange).
- [ ] **Månedskostnad ≤ 25 000 kr** (`mndKostnad`, før rentefradrag).
- [ ] **Oppussing:** høyst **én** større jobb de neste 5 årene (bad, kjøkken, el-anlegg, tak, drenering, vinduer, rør). Helst bare overflate.
- [ ] Ingen TG3 på våtrom, tak, drenering eller el-anlegg uten at det er tatt høyde for i prisen.

## Ønsker
Hvert oppfylt ønske gir pluss i «Mine kriterier». Vekt: 1 = litt viktig, 3 = veldig viktig.

| Ønske | Vekt |
|---|---|
| Uteplass: balkong eller terrasse | 3 |
| Gode solforhold | 3 |
| Kort vei til kollektiv: Bybanen under 700 m eller buss under 400 m å gå | 3 |
| Lave felleskostnader (under 45 kr/m² BRA-i per mnd) | 3 |
| Innflyttingsklar (bare overflate de neste 5 årene) | 2 |
| BRA-i over 60 m² | 1 |
| Heis (hvis 3. etasje eller høyere) | 1 |
| Selveier (andel gir ikke trekk, bare ikke pluss) | 1 |
| Parkering eller trygg sykkelbod | 1 |

## Områder
Ikke et kriterium. Håkon legger bare inn boliger i strøk de kan tenke seg, så beliggenhet vurderes ut fra reisetid, sol, utsikt og støy.

## Vekter for totalscore
Summen skal bli 1.0.

```kriterier
vektPris: 0.15
vektTilstand: 0.20
vektOkonomi: 0.15
vektBeliggenhet: 0.20
vektKriterier: 0.15
vektInvestering: 0.15
```

## Referansepriser (valgfritt)
Typisk kr/m² (BRA-i) for brukte leiligheter per bydel, til prisvurdering før oversikten har nok egne boliger.
Fyll inn fra Eiendom Norge, Finn prisstatistikk eller Hjemla. La stå tomt hvis ukjent. Da sammenligner analysen bare med boligene i oversikten.

| Bydel | Kr/m² | Kilde / dato |
|---|---|---|
| Bergenhus | | |
| Årstad | | |
| Laksevåg | | |
| Fyllingsdalen | | |
| Fana | | |
| Ytrebygda | | |
| Åsane | | |
| Arna | | |
