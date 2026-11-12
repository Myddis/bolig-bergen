"""Fyller inn utregnede felt i et bolig-dokument (JSON) og skriver det tilbake.

Bruk:  python3 scripts/beregn.py data/leiligheter/<finnkode>.json

Totalpris regnes som på Finn: prisantydning + omkostninger + fellesgjeld.
Regner ut: totalpris, prisInklFellesgjeld, maksBud, krPerM2 (uten omkostninger), felleskostPerM2, mndKostnad, mndKostnadEtterFradrag,
budForBudsjett, forventetPris/mndKostnadForventetPris (fra typisk budavvik i strøket) og investering
(tre prisvekst-scenarier: år før kjøp lønner seg mot å leie og formue om 5 år, med oppussing,
verdiløft og vedlikehold).
Lånebeløp = prisantydning + omkostninger - egenkapital (fellesgjeld betjenes via felleskost.).
Økonomiske forutsetninger leses fra ```kriterier-blokker i references/kriterier.md.
"""

import json
import re
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
KRITERIER = ROT / ".claude/skills/boliganalyse/references/kriterier.md"


def les_kriterier():
    tekst = KRITERIER.read_text()
    verdier = {}
    for blokk in re.findall(r"```kriterier\n(.*?)```", tekst, flags=re.S):
        for linje in blokk.splitlines():
            linje = linje.split("#", 1)[0].strip()
            if ":" in linje:
                k, v = linje.split(":", 1)
                try:
                    verdier[k.strip()] = float(v.strip())
                except ValueError:
                    pass
    return verdier


def annuitet(laan, rente_pst, aar):
    if laan <= 0:
        return 0
    r = rente_pst / 100 / 12
    n = int(aar * 12)
    return laan * r / (1 - (1 + r) ** -n) if r else laan / n


def kr(v):
    return f"{round(v):,}".replace(",", " ")


def gront_lan(d):
    """Fana Sparebank Grønt boliglån: energimerke A eller B, men bare A for boliger bygget etter 2019."""
    merke = str(d.get("energimerke") or "").strip().upper()[:1]
    if not merke:
        return None  # ukjent
    if (d.get("byggeaar") or 0) >= 2020:
        return merke == "A"
    return merke in ("A", "B")


def main(sti):
    p = Path(sti)
    d = json.loads(p.read_text())
    k = les_kriterier()
    mangler = []

    # Renten avhenger av energimerket: grønt boliglån gir lavere rente enn Boliglån Ung.
    d["grontLan"] = gront_lan(d)
    if d["grontLan"] and "renteGront" in k:
        k["rente"] = k["renteGront"]
    d["rente"] = k.get("rente")
    if d["grontLan"] is None:
        mangler.append("energimerke (avgjør om grønt boliglån med lavere rente er mulig)")

    pa, fg = d.get("prisantydning"), d.get("fellesgjeld") or 0
    omk = d.get("omkostninger") or 0
    if pa is None:
        mangler.append("prisantydning")
    if not d.get("omkostninger"):
        mangler.append("omkostninger")
    # Totalpris som på Finn: prisantydning + omkostninger + fellesgjeld.
    # Markedsverdi (uten omkostninger) brukes til kr/m² og investeringsberegningen.
    verdi = round(pa + fg) if pa is not None else None
    if pa is not None:
        d["totalpris"] = round(pa + omk + fg)
    d["prisInklFellesgjeld"] = verdi
    tp = d.get("totalpris")

    areal = d.get("braI") or d.get("pRom")
    if not areal:
        mangler.append("braI")
    d["krPerM2"] = round(verdi / areal) if verdi and areal else None
    d["felleskostPerM2"] = round(d["fellesMnd"] / areal) if d.get("fellesMnd") and areal else None

    if verdi and "egenkapital" in k and "rente" in k:
        laan = max(0, pa + omk - k["egenkapital"])
        aar = int(k.get("nedbetalingAar", 30))
        lan_mnd = annuitet(laan, k["rente"], aar)
        felles = d.get("fellesMnd") or 0
        avg = ((d.get("kommunaleAvgAar") or 0) + (d.get("eiendomsskattAar") or 0)) / 12
        d["mndKostnad"] = round(lan_mnd + felles + avg)
        fradrag = k.get("rentefradrag", 22) / 100
        rente1 = laan * k["rente"] / 100 / 12
        d["mndKostnadEtterFradrag"] = round(d["mndKostnad"] - fradrag * rente1)
        d["mndKostnadForklaring"] = (
            f"Lån {kr(laan)} kr ({k['rente']} %, {aar} år, egenkapital {kr(k['egenkapital'])}): "
            f"{kr(lan_mnd)} + felleskost. {kr(felles)}" + (f" + avgifter {kr(avg)}" if avg else "")
            + f" = {kr(d['mndKostnad'])} kr/mnd, ca. {kr(d['mndKostnadEtterFradrag'])} etter rentefradrag første år"
        )
        if not d.get("fellesMnd"):
            mangler.append("fellesMnd")
        d["resultatVedSalg"] = resultat_ved_salg(d, verdi, fg, pa, omk, laan, lan_mnd, felles + avg, k)
        d.pop("investering", None)
        # Månedskostnad ved forventet salgspris i strøket (typisk avvik mot prisantydning)
        avvik = (d.get("marked") or {}).get("avvikProsent")
        if avvik is not None:
            fpris = int(round(pa * (1 + avvik / 100), -3))
            ekstra_omk = 0.025 * (fpris - pa) if (d.get("eieform") or "").lower() == "selveier" else 0
            laan_f = max(0, fpris + omk + ekstra_omk - k["egenkapital"])
            d["forventetPris"] = fpris
            d["mndKostnadForventetPris"] = round(annuitet(laan_f, k["rente"], aar) + felles + avg)
    else:
        d["mndKostnad"] = None

    # Høyeste bud som holder totalpris (inkl. omkostninger) innenfor maksTotalpris.
    # Selveier: dokumentavgift 2,5 % av kjøpesummen; resten av omkostningene regnes som faste.
    maks = k.get("maksTotalpris")
    if maks and pa is not None:
        if (d.get("eieform") or "").lower() == "selveier":
            fast = max(0, omk - 0.025 * pa)
            d["maksBud"] = round((maks - fg - fast) / 1.025)
        else:
            d["maksBud"] = round(maks - fg - omk)
    d["budForBudsjett"] = d.get("maksBud") if maks and tp and tp > maks else None

    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k2: d.get(k2) for k2 in ("totalpris", "prisInklFellesgjeld", "maksBud", "krPerM2", "felleskostPerM2", "mndKostnad",
                                               "mndKostnadEtterFradrag", "forventetPris", "mndKostnadForventetPris",
                                               "mndKostnadForklaring", "budForBudsjett", "resultatVedSalg")},
                     ensure_ascii=False, indent=1))
    if mangler:
        print("MANGLER:", ", ".join(mangler), file=sys.stderr)
    if maks and tp and tp > maks:
        print(f"OVER KJØPSRAMMEN: totalpris {kr(tp)} er over {kr(maks)}. Bud må være ≤ {kr(d['budForBudsjett'])}"
              + (f" (prisantydning {kr(pa)})" if pa else ""), file=sys.stderr)
    if k.get("maksMndKostnad") and d.get("mndKostnad") and d["mndKostnad"] > k["maksMndKostnad"]:
        print(f"RØDT FLAGG: månedskostnad {kr(d['mndKostnad'])} er over {kr(k['maksMndKostnad'])}", file=sys.stderr)


def scenarier(d, k):
    """Prisvekst-scenarier (% per år). Fra dokumentets `prisvekst` (satt fra scripts/omrade.py),
    ellers fallback til `prisvekst` i kriterier.md."""
    pv = d.get("prisvekst") or {}
    forv = pv.get("forventet")
    if forv is None:
        forv = k.get("prisvekst", 4.0)
    opt = pv.get("optimistisk")
    if opt is None or opt < forv:
        opt = forv + 2
    pes = pv.get("pessimistisk", 0.0)
    return {"pessimistisk": pes, "forventet": forv, "optimistisk": opt}


def resultat_ved_salg(d, verdi0, fg, pa, omk, laan, lan_mnd, faste_mnd, k):
    """Økonomisk resultat ved salg etter 3 og 5 år, i tre prisvekst-scenarier (boligscore.md, avsnitt 8).

    resultat = salgspris − kjøpspris − kjøpsomkostninger − oppussing − salgskostnad − eierkostnader,
    der eierkostnader er renter etter rentefradrag, felleskost./avgifter og vedlikehold. Avdrag er sparing
    og trekkes ikke fra. Priser er uten fellesgjeld (fellesgjelden antas overtatt av kjøper, uendret).
    motLeie = resultat + spart husleie − tapt avkastning på egenkapital og oppussingspenger.
    """
    sc = scenarier(d, k)
    oppussing = d.get("oppussingEstimat") or 0
    verdiloft = d.get("verdiokningOppussing") or 0
    r = k["rente"] / 100 / 12
    fradrag = k.get("rentefradrag", 22) / 100
    salg = k.get("salgskostnad", 80000)
    vedlikehold = k.get("vedlikeholdAar", 0) / 12
    hv = k.get("husleievekst", 3) / 100
    alt = k.get("alternativAvkastning", 4) / 100
    ek = float(k["egenkapital"]) + oppussing
    ut = {}
    for navn, vekst in sc.items():
        e = {"vekst": vekst}
        for aar in (3, 5):
            rest, eier, husleie = laan, 0.0, 0.0
            for m in range(1, aar * 12 + 1):
                renter = rest * r
                rest -= min(rest, lan_mnd - renter) if rest > 0 else 0
                eier += renter * (1 - fradrag) + faste_mnd + vedlikehold
                husleie += k.get("husleie", 0) * (1 + hv) ** ((m - 1) // 12)
            salgspris = (verdi0 + verdiloft) * (1 + vekst / 100) ** aar - fg
            resultat = salgspris - pa - omk - oppussing - salg - eier
            mot_leie = resultat + husleie - ek * ((1 + alt) ** aar - 1)
            e[f"aar{aar}"] = {"salgspris": int(round(salgspris, -3)), "eierkostnader": round(eier), "resultat": round(resultat),
                              "motLeie": round(mot_leie)}
        ut[navn] = e
    kilde = (d.get("prisvekst") or {}).get("kilde") or "fallback fra kriterier.md (ingen områdetall)"
    return {
        "scenarier": ut,
        "antagelser": (f"Prisvekst {sc['pessimistisk']} / {sc['forventet']} / {sc['optimistisk']} %/år "
                       f"(pessimistisk / nøytralt / optimistisk; kilde: {kilde}). Rente {k['rente']} % med "
                       f"{k.get('rentefradrag', 22)} % rentefradrag, vedlikehold {kr(k.get('vedlikeholdAar', 0))} kr/år, "
                       f"oppussing {kr(oppussing)} kr med verdiløft {kr(verdiloft)} kr, salgskostnad {kr(salg)} kr, "
                       f"fellesgjeld uendret. «Mot å leie» legger til spart husleie ({kr(k.get('husleie', 0))} kr/mnd, "
                       f"+{k.get('husleievekst', 3)} %/år) og trekker fra {k.get('alternativAvkastning', 4)} % avkastning "
                       f"på egenkapitalen. Gevinst ved salg av egen bolig er normalt skattefri etter minst ett års eier- og botid."),
    }


if __name__ == "__main__":
    main(sys.argv[1])
