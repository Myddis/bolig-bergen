# Mine kriterier

Kriteriene til Håkon og Camilla. De styrer delscorene «Mine kriterier» og «Investering», og vektingen av totalscoren.
Sist oppdatert: 2026-11-12.

## Økonomi
Tallene brukes i `scripts/beregn.py`, som leser blokken under. Behold formatet `nøkkel: verdi`.

```kriterier
egenkapital: 730000          # kr tilgjengelig egenkapital
maksTotalpris: 4900000       # finansieringsbevis; gjelder totalpris som på Finn: bud + omkostninger + fellesgjeld
rente: 5.5                   # nominell rente, Fana Sparebank Boliglån Ung (5,45 % fra 29.09.2026), satt med margin
renteGront: 5.25             # Fana Sparebank Grønt boliglån (5,20 % fra 29.09.2026) + samme margin. Gjelder energimerke A eller B (bare A hvis bygget etter 2019)
nedbetalingAar: 30           # nedbetalingstid boliglån, år
maksMndKostnad: 28000        # smertegrense for samlet månedskostnad (lån + felleskost. + avgifter), før rentefradrag. Hevet fra 25 000 i nov. 2026
husleie: 20540               # dagens husleie, kr/mnd, brukt i investeringsberegningen
husleievekst: 3.0            # antatt årlig økning i husleie hvis vi fortsetter å leie, %
prisvekst: 5.0               # FALLBACK: brukes bare når områdetall mangler. Normalt hentes prisvekst per strøk med scripts/omrade.py
vedlikeholdAar: 10000        # innvendig vedlikehold per år som eier, kr (maling, hvitevarer, småreparasjoner)
alternativAvkastning: 4.0    # årlig avkastning på sparing hvis vi fortsetter å leie, %
salgskostnad: 80000          # meglerhonorar og markedsføring ved et senere salg, kr
rentefradrag: 22             # skattefradrag på renteutgifter, %
```

Lånet er innvilget ut fra framtidig inntekt (finansieringsbevis), så det sjekkes ikke mot 5 ganger inntekten.

Energimerket påvirker renten. Med energimerke A eller B (bare A hvis boligen er bygget etter 2019) kan vi få Grønt boliglån i Fana Sparebank, som i dag er 0,25 prosentpoeng lavere enn Boliglån Ung. `beregn.py` bruker da `renteGront` i månedskostnad, budsjett og investering, og setter `rente` og `grontLan` i dokumentet. Er energimerket ukjent, regnes det med vanlig rente. Sjekk satsene i Fana Sparebanks prisliste av og til.

## Må-krav
Det er to typer krav:
- **Harde krav** (totalpris, soverom, oppussing og TG3): brudd gir maks 30 i «Mine kriterier», maks 45 i totalscore og et rødt flagg.
- **Myke krav** (reisetid og månedskostnad): ingen tak. Hvert minutt eller hver krone over grensen gir et gradvis trekk i totalscoren, og et rødt flagg. Ett minutt over skal ikke velte en ellers god bolig.

- [ ] **Totalpris ≤ 4,9 mill** (som på Finn: prisantydning + omkostninger + fellesgjeld). `maksBud` er høyeste bud innenfor grensen. Er totalprisen ved prisantydning over, er kravet brutt, og `budForBudsjett` viser hvilket bud som trengs.
- [ ] **Soverom:** minst 2, **eller** 1 soverom og i tillegg enten:
  - soverommet er minst 14 m², eller
  - boligen har et **kontor**: et eget rom med dør, på minst ca. 5 m², utenom stue, kjøkken og bad. Det kan kalles kontor, arbeidsrom, hobbyrom, gjesterom eller være et lite soverom. Et hjørne eller en nisje i stuen teller ikke.
- [ ] **Reisetid ≤ 30 min** for **både** Håkon og Camilla (raskeste av kollektiv og gange). *Mykt krav:* −3 i totalscore per minutt den lengste av de to reisene er over 30, maks −30.
- [ ] **Månedskostnad ≤ 28 000 kr** (`mndKostnad`, før rentefradrag). *Mykt krav:* −3 i totalscore per 500 kr over (forholdsmessig), maks −30.
- [ ] **Oppussing:** høyst **én** større jobb de neste 5 årene (bad, kjøkken, el-anlegg, tak, drenering, vinduer, rør). Helst bare overflate.
- [ ] Ingen TG3 på våtrom, tak, drenering eller el-anlegg uten at det er tatt høyde for i prisen.

## Ønsker
Hvert oppfylt ønske gir pluss i «Mine kriterier». Vekt: 1 = litt viktig, 3 = veldig viktig.

| Ønske | Vekt |
|---|---|
| Uteplass: balkong eller terrasse | 3 |
| Kort vei til kollektiv: Bybanen under 700 m eller buss under 400 m å gå | 3 |
| Lave felleskostnader (under 45 kr/m² BRA-i per mnd) | 3 |
| Energimerke A eller B (gir grønt boliglån med lavere rente) | 2 |
| Innflyttingsklar (bare overflate de neste 5 årene) | 2 |
| BRA-i over 60 m² | 1 |
| Heis (hvis 3. etasje eller høyere) | 1 |
| Selveier (andel gir ikke trekk, bare ikke pluss) | 1 |
| Parkering eller trygg sykkelbod | 1 |

Solforhold er ikke lenger et ønske her. Sol er en tredjedel av beliggenhetsscoren (se `analyseregler.md`).

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
