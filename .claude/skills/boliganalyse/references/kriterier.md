# Mine kriterier

> **Fyll ut denne filen.** Den styrer delscoren «Mine kriterier» og vektingen av totalscoren.
> Verdier merket `TODO` er plassholdere. Analysen bruker dem, men sier fra at de ikke er bekreftet.

## Økonomi
Tallene brukes i `scripts/beregn.py`, som leser blokken under. Behold formatet `nøkkel: verdi`.

```kriterier
egenkapital: 800000          # TODO: kr tilgjengelig egenkapital
maksTotalpris: 5500000       # TODO: øvre grense totalpris (prisantydning + fellesgjeld), kr
rente: 5.2                   # TODO: forventet nominell rente på boliglån, %
nedbetalingAar: 30           # nedbetalingstid boliglån, år
maksMndKostnad: 25000        # TODO: smertegrense for samlet månedskostnad, kr
```

## Må-krav
Brudd på et må-krav gir maks 30 i «Mine kriterier» og et rødt flagg.

- [ ] Minst `2` soverom (TODO: juster)
- [ ] Totalpris under `maksTotalpris`
- [ ] Reisetid under `40` min (kollektiv eller gange) for **begge** (TODO: juster)
- [ ] Ingen TG3 på våtrom, tak, drenering eller el-anlegg uten at det er tatt høyde for i prisen (TODO: behold/fjern)

## Ønsker
Hvert oppfylt ønske gir pluss i «Mine kriterier». Vekt: 1 = litt viktig, 3 = veldig viktig.

| Ønske | Vekt |
|---|---|
| Balkong eller terrasse | 2 |
| Kort vei til Bybanen | 2 |
| BRA-i over 60 m² | 2 |
| Heis (hvis 3. etasje eller høyere) | 1 |
| Gode solforhold / utsikt | 1 |
| Selveier (fremfor andel) | 1 |
| Lave felleskostnader (< 45 kr/m² BRA-i per mnd) | 1 |
| Parkering eller gode sykkelforhold | 1 |
| Innflyttingsklar (ingen større oppussing de neste 5 årene) | 2 |

TODO: legg til, fjern eller endre vekt.

## Områder
- Foretrukne bydeler / strøk: TODO (f.eks. Bergenhus, Årstad, Sandviken, Møhlenpris, Landås)
- Områder vi helst unngår: TODO

## Vekter for totalscore
Summen bør bli 1.0.

```kriterier
vektPris: 0.25
vektTilstand: 0.25
vektOkonomi: 0.15
vektBeliggenhet: 0.20
vektKriterier: 0.15
```

## Referansepriser (valgfritt)
Typisk kr/m² (BRA-i) for brukte leiligheter per bydel, til prisvurdering før oversikten har nok egne boliger.
Fyll inn fra Eiendom Norge / Finn prisstatistikk. La stå tomt hvis ukjent. Da sammenligner analysen bare med boligene i oversikten.

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
