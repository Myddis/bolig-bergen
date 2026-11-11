"""Adresse -> koordinater (Kartverket) + bydel i Bergen (SSB).

Bruk:  python3 scripts/geokod.py "Nygårdsgaten 5"      (eller med postnummer: "Nygårdsgaten 5, 5015")
Ut:    JSON med adresse, postnr, lat, lon, bydel, treff (antall treff i API-et)

Kun standardbiblioteket. Krever nettilgang til ws.geonorge.no.
"""

import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
BYDELER = ROT / "kilder/ssb_bydeler_bergen.topo.json"


def sok_adresse(tekst):
    tekst = re.sub(r"\b(leil(ighet)?|bolig|seksjon|snr|bnr)\.?\s*[\w-]+", "", tekst, flags=re.I)
    postnr = None
    m = re.search(r"\b(5\d{3})\b", tekst)
    if m:
        postnr = m.group(1)
        tekst = tekst.replace(m.group(0), "")
    tekst = re.sub(r"\bBergen\b", "", tekst, flags=re.I).strip(" ,")
    params = {"sok": tekst, "kommunenummer": "4601", "treffPerSide": 5, "utkoordsys": 4258}
    if postnr:
        params["postnummer"] = postnr
    url = "https://ws.geonorge.no/adresser/v1/sok?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as r:
        d = json.load(r)
    return d.get("adresser", []), d.get("metadata", {}).get("totaltAntallTreff", 0)


def les_bydeler():
    t = json.loads(BYDELER.read_text())
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    arcs = []
    for arc in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        out = []
        for i in idx:
            a = arcs[i] if i >= 0 else list(reversed(arcs[~i]))
            out.extend(a if not out else a[1:])
        return out

    res = []
    for obj in t["objects"].values():
        for g in obj["geometries"]:
            polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
            res.append((g["properties"]["bydelnavn"], [[ring(r) for r in p] for p in polys]))
    return res


def i_ring(x, y, ring):
    inn = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inn = not inn
        j = i
    return inn


def bydel_for(lon, lat):
    bydeler = les_bydeler()
    for navn, polys in bydeler:
        for p in polys:
            if i_ring(lon, lat, p[0]) and not any(i_ring(lon, lat, h) for h in p[1:]):
                return navn
    # Utenfor de grove polygonene (typisk helt ved sjøen): nærmeste hjørnepunkt
    best, avst = None, 1e9
    for navn, polys in bydeler:
        for p in polys:
            for x, y in p[0]:
                d = ((x - lon) * 0.5) ** 2 + (y - lat) ** 2
                if d < avst:
                    best, avst = navn, d
    return best


def main():
    adr, treff = sok_adresse(" ".join(sys.argv[1:]))
    if not adr:
        print(json.dumps({"feil": "Fant ingen adresse i Bergen", "sok": " ".join(sys.argv[1:])}, ensure_ascii=False))
        sys.exit(1)
    a = adr[0]
    p = a["representasjonspunkt"]
    print(json.dumps({
        "adresse": a["adressetekst"],
        "postnr": a["postnummer"],
        "lat": round(p["lat"], 6),
        "lon": round(p["lon"], 6),
        "bydel": bydel_for(p["lon"], p["lat"]),
        "gnr": a.get("gardsnummer"),
        "bnr": a.get("bruksnummer"),
        "treff": treff,
        "alternativer": [x["adressetekst"] + ", " + x["postnummer"] for x in adr[1:]],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
