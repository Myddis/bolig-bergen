"""Fyller inn utregnede felt i et bolig-dokument (JSON) og skriver det tilbake.

Bruk:  python3 scripts/beregn.py data/leiligheter/<finnkode>.json

Totalpris regnes som på Finn: prisantydning + omkostninger + fellesgjeld.
Regner ut: totalpris, prisInklFellesgjeld, maksBud, krPerM2 (uten omkostninger), felleskostPerM2, mndKostnad, mndKostnadEtterFradrag,
budForBudsjett og investering (år før kjøp lønner seg mot å leie, formue om 5 år).
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


def main(sti):
    p = Path(sti)
    d = json.loads(p.read_text())
    k = les_kriterier()
    mangler = []

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
        if "husleie" in k and "prisvekst" in k:
            d["investering"] = investering(verdi, fg, laan, lan_mnd, felles + avg, k)
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
                                               "mndKostnadEtterFradrag", "mndKostnadForklaring", "budForBudsjett", "investering")},
                     ensure_ascii=False, indent=1))
    if mangler:
        print("MANGLER:", ", ".join(mangler), file=sys.stderr)
    if maks and tp and tp > maks:
        print(f"MÅ-KRAV BRUTT: totalpris {kr(tp)} er over {kr(maks)}. Bud må være ≤ {kr(d['budForBudsjett'])}"
              + (f" (prisantydning {kr(pa)})" if pa else ""), file=sys.stderr)
    if k.get("maksMndKostnad") and d.get("mndKostnad") and d["mndKostnad"] > k["maksMndKostnad"]:
        print(f"MÅ-KRAV BRUTT: månedskostnad {kr(d['mndKostnad'])} er over {kr(k['maksMndKostnad'])}", file=sys.stderr)


def investering(tp, fg, laan, lan_mnd, faste_mnd, k):
    """Kjøp mot å fortsette å leie, måned for måned i 30 år.

    Kjøp: verdi vokser med prisvekst; formue = verdi - restlån - fellesgjeld (antas uendret) - salgskostnad.
    Leie: egenkapitalen spares med alternativ avkastning; hver måned spares (kjøpskostnad etter
    rentefradrag - husleie), negativt hvis kjøp er billigere. Husleien øker med husleievekst.
    """
    r = k["rente"] / 100 / 12
    g = (1 + k["prisvekst"] / 100) ** (1 / 12) - 1
    a = (1 + k.get("alternativAvkastning", 4) / 100) ** (1 / 12) - 1
    hv = k.get("husleievekst", 3) / 100
    fradrag = k.get("rentefradrag", 22) / 100
    salg = k.get("salgskostnad", 80000)
    rest, sparing, verdi = laan, float(k["egenkapital"]), float(tp)
    break_even, aar5 = None, {}
    for m in range(1, 361):
        renter = rest * r
        avdrag = min(rest, lan_mnd - renter) if rest > 0 else 0
        rest -= avdrag
        kost_kjop = (renter + avdrag) + faste_mnd - fradrag * renter
        husleie = k["husleie"] * (1 + hv) ** ((m - 1) // 12)
        sparing = sparing * (1 + a) + (kost_kjop - husleie)
        verdi *= 1 + g
        if m % 12 == 0:
            y = m // 12
            formue_kjop = verdi - rest - fg - salg
            if break_even is None and formue_kjop >= sparing:
                break_even = y
            if y == 5:
                aar5 = {"verdi": verdi, "kjop": formue_kjop, "leie": sparing}
    return {
        "breakEvenAar": break_even,
        "verdi5": round(aar5["verdi"]),
        "formueKjop5": round(aar5["kjop"]),
        "formueLeie5": round(aar5["leie"]),
        "gevinst5": round(aar5["kjop"] - aar5["leie"]),
        "antagelser": (f"Prisvekst {k['prisvekst']} %/år, rente {k['rente']} %, husleie {kr(k['husleie'])} kr/mnd "
                       f"(+{k.get('husleievekst', 3)} %/år), avkastning på sparing {k.get('alternativAvkastning', 4)} %, "
                       f"rentefradrag {k.get('rentefradrag', 22)} %, salgskostnad {kr(salg)} kr, fellesgjeld uendret."),
    }


if __name__ == "__main__":
    main(sys.argv[1])
