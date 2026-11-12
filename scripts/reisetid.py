"""Reisetid fra en bolig til arbeidsstedene og stedene (sentrum) i config.json.

Kollektiv og gange hentes fra Google Maps (Routes API), som stemmer med det Håkon og Camilla ser i Google Maps.
Entur (dekker Skyss) er reserve hvis Google ikke svarer, og brukes alltid for sykkel og nærmeste holdeplass.
Hver reisetid får feltet "kilde" ("Google Maps" eller "Entur"). REISETID_KILDE=entur tvinger Entur.
API-nøkkelen til Google legges inn av proxyen (nettverkshemmelighet for routes.googleapis.com), ikke her.

Bruk:  python3 scripts/reisetid.py <lat> <lon>
Ut:    JSON {"_bybane": {...}, "_buss": {...}, "<id>": {"navn", "adresse", "kollektivMin", "bytter", "rute", "gangKollektivMin",
                      "gangMin", "gangKm", "sykkelMin"}, ...}

Kollektiv: raskeste av inntil 5 forslag med oppmøte kl. <ankomst> neste <ukedag>.
Tiden er dør-til-dør (inkl. gange til/fra holdeplass), men uten venting før avreise.
Kun standardbiblioteket. Krever nettilgang til routes.googleapis.com og api.entur.io.
"""

import datetime as dt
import json
import os
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


GOOGLE_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
GOOGLE_FELT = ",".join([
    "routes.duration", "routes.distanceMeters", "routes.legs.steps.travelMode", "routes.legs.steps.staticDuration",
    "routes.legs.steps.distanceMeters", "routes.legs.steps.transitDetails.transitLine.nameShort",
    "routes.legs.steps.transitDetails.transitLine.vehicle.type",
])
GOOGLE_MODUS = {"BUS": "Buss", "INTERCITY_BUS": "Buss", "TROLLEYBUS": "Buss", "TRAM": "Bybanen", "LIGHT_RAIL": "Bybanen",
                "RAIL": "Tog", "HEAVY_RAIL": "Tog", "COMMUTER_TRAIN": "Tog", "FERRY": "Båt", "SUBWAY": "T-bane"}


def google(fra, til, modus, ankomst=None):
    body = {"origin": {"location": {"latLng": {"latitude": fra[0], "longitude": fra[1]}}},
            "destination": {"location": {"latLng": {"latitude": til[0], "longitude": til[1]}}},
            "travelMode": modus, "languageCode": "no"}
    if modus == "TRANSIT":
        body.update(arrivalTime=ankomst, computeAlternativeRoutes=True)
    req = urllib.request.Request(GOOGLE_URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "X-Goog-FieldMask": GOOGLE_FELT})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    ruter = d.get("routes") or []
    if not ruter:
        raise RuntimeError(f"Google fant ingen rute ({modus})")
    return ruter


def sek(v):
    return int(str(v or "0s").rstrip("s") or 0)


def google_reise(fra, til, ankomst):
    """Kollektiv (raskeste av Googles forslag med oppmøte til ankomst) og gange."""
    r = {}
    ruter = google(fra, til, "TRANSIT", ankomst)
    steg = lambda rute: [s for leg in rute.get("legs", []) for s in leg.get("steps", [])]
    med_kollektiv = [x for x in ruter if any(s.get("travelMode") == "TRANSIT" for s in steg(x))] or ruter
    best = min(med_kollektiv, key=lambda x: sek(x.get("duration")))
    linjer = []
    for s in steg(best):
        if s.get("travelMode") == "TRANSIT":
            ln = (s.get("transitDetails") or {}).get("transitLine") or {}
            navn = GOOGLE_MODUS.get((ln.get("vehicle") or {}).get("type"), "Kollektiv")
            linjer.append(f"{navn} {ln.get('nameShort') or ''}".strip())
    r["kollektivMin"] = round(sek(best.get("duration")) / 60)
    r["bytter"] = max(0, len(linjer) - 1)
    r["rute"] = " → ".join(linjer) or "Gange"
    r["gangKollektivMin"] = round(sum(sek(s.get("staticDuration")) for s in steg(best) if s.get("travelMode") == "WALK") / 60)
    g = google(fra, til, "WALK")[0]
    r["gangMin"] = round(sek(g.get("duration")) / 60)
    r["gangKm"] = round((g.get("distanceMeters") or 0) / 1000, 1)
    return r


def beskriv(p):
    deler = []
    for leg in p["legs"]:
        if leg["mode"] == "foot":
            continue
        navn = MODUS.get(leg["mode"], leg["mode"])
        kode = (leg.get("line") or {}).get("publicCode") or ""
        deler.append(f"{navn} {kode}".strip())
    return " → ".join(deler) or "Gange"


def entur_reise(fra, til, tid):
    """Reserve: kollektiv og gange fra Entur."""
    r = {}
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
    return r


def main(lat, lon):
    cfg = json.loads((ROT / "config.json").read_text())
    tid = neste_dag(cfg["reisetid"]["ukedag"], cfg["reisetid"]["ankomst"])
    fra = (lat, lon)
    ut = {}
    for a in cfg["arbeidssteder"] + cfg.get("steder", []):
        til = (a["lat"], a["lon"])
        r = {"navn": a["navn"], "adresse": a["adresse"]}
        if os.environ.get("REISETID_KILDE", "").lower() != "entur":
            try:
                r.update(google_reise(fra, til, tid), kilde="Google Maps")
            except Exception as e:
                r["googleFeil"] = str(e)[:200]
        if r.get("kilde") != "Google Maps":
            r.update(entur_reise(fra, til, tid), kilde="Entur")
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
