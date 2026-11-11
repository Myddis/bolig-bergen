"""Fyller inn utregnede felt i et bolig-dokument (JSON) og skriver det tilbake.

Bruk:  python3 scripts/beregn.py data/leiligheter/<finnkode>.json

Regner ut: totalpris, krPerM2, felleskostPerM2, mndKostnad (+ mndKostnadForklaring).
Lånebeløp = totalpris - fellesgjeld + omkostninger - egenkapital (fellesgjeld betjenes via felleskost.).
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
    if pa is None and d.get("totalpris") is None:
        mangler.append("prisantydning/totalpris")
    if d.get("totalpris") is None and pa is not None:
        d["totalpris"] = round(pa + fg)
    tp = d.get("totalpris")

    areal = d.get("braI") or d.get("pRom")
    if not areal:
        mangler.append("braI")
    d["krPerM2"] = round(tp / areal) if tp and areal else None
    d["felleskostPerM2"] = round(d["fellesMnd"] / areal) if d.get("fellesMnd") and areal else None

    if tp and "egenkapital" in k and "rente" in k:
        laan = max(0, tp - fg + (d.get("omkostninger") or 0) - k["egenkapital"])
        lan_mnd = annuitet(laan, k["rente"], k.get("nedbetalingAar", 30))
        felles = d.get("fellesMnd") or 0
        avg = ((d.get("kommunaleAvgAar") or 0) + (d.get("eiendomsskattAar") or 0)) / 12
        d["mndKostnad"] = round(lan_mnd + felles + avg)
        d["mndKostnadForklaring"] = (
            f"Lån {kr(laan)} kr ({k['rente']} %, {int(k.get('nedbetalingAar', 30))} år, egenkapital {kr(k['egenkapital'])}): "
            f"{kr(lan_mnd)} + felleskost. {kr(felles)}" + (f" + avgifter {kr(avg)}" if avg else "") + " kr/mnd"
        )
        if not d.get("fellesMnd"):
            mangler.append("fellesMnd")
    else:
        d["mndKostnad"] = None

    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k2: d.get(k2) for k2 in ("totalpris", "krPerM2", "felleskostPerM2", "mndKostnad", "mndKostnadForklaring")},
                     ensure_ascii=False, indent=1))
    if mangler:
        print("MANGLER:", ", ".join(mangler), file=sys.stderr)
    if k.get("maksTotalpris") and tp and tp > k["maksTotalpris"]:
        print(f"OBS: totalpris {kr(tp)} er over maksTotalpris {kr(k['maksTotalpris'])}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
