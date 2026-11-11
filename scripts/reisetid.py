"""Reisetid fra en bolig til arbeidsstedene i config.json, via Entur (dekker Skyss).

Bruk:  python3 scripts/reisetid.py <lat> <lon>
Ut:    JSON {"_bybane": {...}, "_buss": {...}, "<id>": {"navn", "adresse", "kollektivMin", "bytter", "rute", "gangKollektivMin",
                      "gangMin", "gangKm", "sykkelMin"}, ...}

Kollektiv: raskeste av inntil 5 forslag med oppmøte kl. <ankomst> neste <ukedag>.
Tiden er dør-til-dør (inkl. gange til/fra holdeplass), men uten venting før avreise.
Kun standardbiblioteket. Krever nettilgang til api.entur.io.
"""

import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
URL = "https://api.entur.io/journey-planner/v3/graphql"
HODER = {"Content-Type": "application/json", "ET-Client-Name": "privat-boligjakt-bergen"}
SPORRING = """
query($from: Location!, $to: Location!, $dt: DateTime!, $modes: Modes, $n: Int) {
  trip(from: $from, to: $to, dateTime: $dt, arriveBy: true, numTripPatterns: $n, modes: $modes) {
    tripPatterns {
      duration walkDistance distance startTime expectedEndTime
      legs { mode duration distance line { publicCode name } fromPlace { name } toPlace { name } }
    }
  }
}"""
UKEDAGER = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
MODUS = {"tram": "Bybanen", "bus": "Buss", "rail": "Tog", "water": "Båt", "coach": "Buss", "metro": "T-bane"}


def neste_dag(ukedag, kl):
    i = UKEDAGER.index(ukedag)
    idag = dt.date.today()
    dager = (i - idag.weekday()) % 7 or 7
    dato = idag + dt.timedelta(days=dager)
    h, m = map(int, kl.split(":"))
    # Norsk tid; Entur tolker offset riktig. Vintertid +01:00, sommertid +02:00.
    sommer = 3 < dato.month < 11
    return f"{dato.isoformat()}T{h:02d}:{m:02d}:00+0{2 if sommer else 1}:00"


def tur(fra, til, tid, modes=None, n=5):
    body = {"query": SPORRING, "variables": {
        "from": {"coordinates": {"latitude": fra[0], "longitude": fra[1]}},
        "to": {"coordinates": {"latitude": til[0], "longitude": til[1]}},
        "dt": tid, "modes": modes, "n": n}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=HODER)
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    if d.get("errors"):
        raise RuntimeError(d["errors"])
    return d["data"]["trip"]["tripPatterns"]


def beskriv(p):
    deler = []
    for leg in p["legs"]:
        if leg["mode"] == "foot":
            continue
        navn = MODUS.get(leg["mode"], leg["mode"])
        kode = (leg.get("line") or {}).get("publicCode") or ""
        deler.append(f"{navn} {kode}".strip())
    return " → ".join(deler) or "Gange"


def main(lat, lon):
    cfg = json.loads((ROT / "config.json").read_text())
    tid = neste_dag(cfg["reisetid"]["ukedag"], cfg["reisetid"]["ankomst"])
    fra = (lat, lon)
    ut = {}
    for a in cfg["arbeidssteder"]:
        til = (a["lat"], a["lon"])
        r = {"navn": a["navn"], "adresse": a["adresse"]}
        try:
            kol = tur(fra, til, tid)
            kol = [p for p in kol if any(l["mode"] != "foot" for l in p["legs"])] or kol
            best = min(kol, key=lambda p: p["duration"])
            r["kollektivMin"] = round(best["duration"] / 60)
            r["bytter"] = max(0, sum(1 for l in best["legs"] if l["mode"] != "foot") - 1)
            r["rute"] = beskriv(best)
            r["gangKollektivMin"] = round(sum(l["duration"] for l in best["legs"] if l["mode"] == "foot") / 60)
        except Exception as e:
            r["kollektivFeil"] = str(e)[:200]
        try:
            g = tur(fra, til, tid, {"directMode": "foot", "transportModes": []}, 1)[0]
            r["gangMin"] = round(g["duration"] / 60)
            r["gangKm"] = round(g["distance"] / 1000, 1)
        except Exception as e:
            r["gangFeil"] = str(e)[:200]
        try:
            s = tur(fra, til, tid, {"directMode": "bicycle", "transportModes": []}, 1)[0]
            r["sykkelMin"] = round(s["duration"] / 60)
        except Exception as e:
            r["sykkelFeil"] = str(e)[:200]
        ut[a["id"]] = r
    for nokkel, modus in (("_bybane", "tram"), ("_buss", "bus")):
        try:
            ut[nokkel] = naermeste_stopp(lat, lon, modus)
        except Exception as e:
            ut[nokkel] = {"feil": str(e)[:200]}
    ut["_beregnet"] = {"ankomst": tid}
    print(json.dumps(ut, ensure_ascii=False, indent=1))


def naermeste_stopp(lat, lon, modus="tram"):
    """Nærmeste holdeplass for Bybanen (tram) eller buss (bus), med gangavstand langs gangnettet (Entur)."""
    q = """{ nearest(latitude: %f, longitude: %f, maximumDistance: 3000, maximumResults: 1,
             filterByModes: [%s], filterByPlaceTypes: [stopPlace]) {
             edges { node { distance place { ... on StopPlace { name } } } } } }""" % (lat, lon, modus)
    req = urllib.request.Request(URL, data=json.dumps({"query": q}).encode(), headers=HODER)
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    kanter = d["data"]["nearest"]["edges"]
    if not kanter:
        return {"stopp": None, "meter": None, "gangMin": None}
    n = kanter[0]["node"]
    m = round(n["distance"])
    return {"stopp": n["place"]["name"], "meter": m, "gangMin": max(1, round(m / 80))}


if __name__ == "__main__":
    main(float(sys.argv[1]), float(sys.argv[2]))
