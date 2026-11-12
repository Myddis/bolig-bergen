# Kriterier og rammer

Rammene til Håkon og Camilla. Scoremodellen står i `boligscore.md` og reglene i `analyseregler.md`.
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
husleie: 20540               # dagens husleie, kr/mnd, brukt i «resultat ved salg» (mot å leie)
husleievekst: 3.0            # antatt årlig økning i husleie hvis vi fortsetter å leie, %
prisvekst: 5.0               # FALLBACK: brukes bare når områdetall mangler. Normalt hentes prisvekst per strøk med scripts/omrade.py
vedlikeholdAar: 10000        # innvendig vedlikehold per år som eier, kr (maling, hvitevarer, småreparasjoner)
alternativAvkastning: 4.0    # årlig avkastning på sparing hvis vi fortsetter å leie, %
salgskostnad: 80000          # meglerhonorar og markedsføring ved et senere salg, kr
rentefradrag: 22             # skattefradrag på renteutgifter, %
```

Lånet er innvilget ut fra framtidig inntekt (finansieringsbevis), så det sjekkes ikke mot 5 ganger inntekten.

Energimerket påvirker renten. Med energimerke A eller B (bare A hvis boligen er bygget etter 2019) kan vi få Grønt boliglån i Fana Sparebank, som i dag er 0,25 prosentpoeng lavere enn Boliglån Ung. `beregn.py` bruker da `renteGront` i månedskostnad, budsjett og resultat ved salg, og setter `rente` og `grontLan` i dokumentet. Er energimerket ukjent, regnes det med vanlig rente. Sjekk satsene i Fana Sparebanks prisliste av og til.

## Rammebetingelser og søkeprofil
Fra `boligscore.md`. Dette er en profil, ikke absolutte krav: ingenting gir tak eller trekk i totalscoren. Brudd blir røde flagg og påvirker kategoriene.

- **Formål:** egen bolig med godt utgangspunkt for salg etter ca. 3–5 år.
- **Kjøpsramme:** totalpris (prisantydning + omkostninger + fellesgjeld) høyst 4,9 mill. Over rammen gir maks karakter 3 i Kjøpspris og et rødt flagg.
- **Beliggenhet:** sentrumsnær, med godt kollektivtilbud og kort vei til daglige tilbud. Reisetid til jobb for Håkon og Camilla teller i Beliggenhet. Over 30 min for en av dem er et rødt flagg.
- **Størrelse:** ca. 45–75 m² BRA-i.
- **Soverom:** helst to. En god toroms (ett soverom), gjerne med kontor, kan også være aktuell.
- **Standard:** gjerne eldre kjøkken eller overflater som kan moderniseres, men et forsvarlig teknisk utgangspunkt. Badet bør helst ha dokumentert god tilstand. Mer enn én større jobb de neste 5 årene er et rødt flagg.
- **Ellers et pluss:** balkong eller terrasse, gode lysforhold og lite innsyn, fornuftige energikostnader (energimerke A/B gir grønt boliglån), heis fra 3. etasje, parkering eller sykkelbod.
- **BOB-medlemmer:** Håkon og Camilla er medlemmer i BOB. BOB-forkjøpsrett er et grønt flagg. Forkjøpsrett for andre boligbyggelag er et rødt flagg.
- **Månedskostnad:** over 28 000 kr før rentefradrag (`maksMndKostnad`) er et rødt flagg og gir lav karakter i Løpende kostnader.

## Vekter (poeng av 100)
Summen skal bli 100.

```kriterier
vektBeliggenhet: 18
vektKjopspris: 17
vektVideresalg: 15
vektTeknisk: 14
vektOppgradering: 12
vektPlanlosning: 8
vektFellesokonomi: 6
vektTrivsel: 5
vektLopende: 5
```

## Referansepriser (valgfritt)
Typisk kr/m² (BRA-i) for brukte leiligheter per bydel. Brukes bare når Eiendomssjekk ikke har tall for strøket.
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
