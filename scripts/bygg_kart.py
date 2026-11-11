"""Bygger kartdataene til oversikten (oversikt/bergen.geo.json).

Kilder (alle åpne data):
  - Kartverket N50 Kartdata, FGDB, EPSG:25833, kommune 4601 Bergen og 4627 Askøy.
    Bestilles via nedlasting.geonorge.no (se `hent_n50`).
  - Kartverket «Norske fylker og kommuner illustrasjonsdata 2021» for nabokommunene
    (grovere). Hentet fra github.com/robhop/fylker-og-kommuner.
  - SSB bydeler for Bergen (kilder/ssb_bydeler_bergen.topo.json), fra
    github.com/AnalyseABO/Kart-fylker-og-kommuner-json.
  - Stedsnavn fra Kartverkets stedsnavn-API (ws.geonorge.no).

Krever: pip install pyproj shapely pyogrio pandas, og node/npx (mapshaper)
Bruk:   python scripts/bygg_kart.py <mappe med N50-zipper utpakket> <kommuner2021.json>

Lag i resultatet (properties.lag):
  land, by, skog, vann, vei (klasse: e/r/f/k), bane, bydel, nabo, sted
"""

import json
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pyogrio
import pyproj
import shapely
from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union

ROT = Path(__file__).resolve().parent.parent
BBOX_WGS = box(5.02, 60.18, 5.72, 60.56)
NABOER = {
    "4626": "Øygarden", "4624": "Bjørnafjorden", "4630": "Osterøy",
    "4631": "Alver", "4623": "Samnanger", "4628": "Vaksdal", "4625": "Austevoll",
}
STEDER = [
    "Sentrum", "Sandviken", "Nordnes", "Møhlenpris", "Nygårdshøyden", "Landås", "Minde",
    "Paradis", "Nesttun", "Loddefjord", "Kronstad", "Fløyen", "Ulriken", "Bryggen",
    "Solheimsviken", "Eidsvåg", "Indre Arna", "Kokstad", "Lagunen", "Hop", "Godvik",
    "Mathopen", "Ulset", "Tertnes", "Kalfaret", "Sletten", "Damsgård", "Gyldenpris",
    "Nattland", "Fjøsanger", "Hesthaugen", "Storetveit", "Bønes", "Søreide", "Kolstien",
    "Haukeland", "Ytre Sandviken", "Skjold", "Rådal", "Flaktveit", "Åstveit", "Ytrebygda",
]
TOL = {"land": 8, "by": 20, "skog": 40, "vann": 12, "vei": 12, "bane": 10, "bydel": 10}  # meter


def hent_n50(ut_mappe, kommuner=(("4601", "Bergen"), ("4627", "Askøy"))):
    """Bestiller og laster ned N50 FGDB for kommunene (krever nedlasting.geonorge.no)."""
    uuid = "ea192681-d039-42ec-b1bc-f3ce04c189ac"
    body = {"orderLines": [{"metadataUuid": uuid,
                            "areas": [{"code": k, "type": "kommune", "name": n}],
                            "projections": [{"code": "25833"}],
                            "formats": [{"name": "FGDB"}]} for k, n in kommuner]}
    req = urllib.request.Request("https://nedlasting.geonorge.no/api/order",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        order = json.load(r)
    for f in order["files"]:
        dest = Path(ut_mappe) / f["name"]
        urllib.request.urlretrieve(f["downloadUrl"], dest)
        print("lastet ned", dest)


def gdb_for(mappe, knr):
    return next(Path(mappe).glob(f"**/Basisdata_{knr}_*_N50Kartdata_FGDB.gdb"))


def les(gdb, lag, filt=None):
    df = pyogrio.read_dataframe(gdb, layer=lag)
    return df if filt is None else df[filt(df)]


def til_wgs_fn():
    t = pyproj.Transformer.from_crs(25833, 4326, always_xy=True)

    def f(geom):
        return shapely.transform(geom, lambda c: np.column_stack(t.transform(c[:, 0], c[:, 1])))
    return f


def stedsnavn(navn):
    q = urllib.parse.urlencode({"sok": navn, "kommunenummer": "4601", "treffPerSide": 1, "utkoordsys": 4258})
    with urllib.request.urlopen(f"https://ws.geonorge.no/stedsnavn/v1/navn?{q}", timeout=30) as r:
        d = json.load(r)
    for n in d.get("navn", []):
        p = n.get("representasjonspunkt") or {}
        if "øst" in p:
            return p["øst"], p["nord"]
    return None


def les_topojson(sti):
    t = json.loads(Path(sti).read_text())
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
            if g["type"] == "Polygon":
                geo = {"type": "Polygon", "coordinates": [ring(r) for r in g["arcs"]]}
            else:
                geo = {"type": "MultiPolygon", "coordinates": [[ring(r) for r in p] for p in g["arcs"]]}
            res.append((g["properties"], shapely.make_valid(shape(geo))))
    return res


def main(n50_mappe, kommunefil):
    wgs = til_wgs_fn()
    bbox = shapely.transform(BBOX_WGS, lambda c: np.column_stack(
        pyproj.Transformer.from_crs(4326, 25833, always_xy=True).transform(c[:, 0], c[:, 1])))
    feats = []

    def legg_til(lag, geom, tol, **props):
        geom = shapely.make_valid(geom.intersection(bbox).simplify(tol))
        if geom.is_empty:
            return
        feats.append({"type": "Feature", "properties": {"lag": lag, **props}, "geometry": mapping(wgs(geom))})

    land_alle, by, skog, vann, veier, bane = [], [], [], [], {"e": [], "r": [], "f": [], "k": []}, []
    for knr in ("4601", "4627"):
        gdb = gdb_for(n50_mappe, knr)
        a = les(gdb, "N50_Arealdekke_omrade")
        land_alle.append(unary_union(a[a.objtype != "Havflate"].geometry.values))
        by.append(unary_union(a[a.objtype.isin(["Tettbebyggelse", "BymessigBebyggelse", "Industriområde"])].geometry.values))
        skog.append(unary_union(a[a.objtype.isin(["Skog", "Park"])].geometry.values))
        vann.append(unary_union(a[a.objtype.isin(["Innsjø", "InnsjøRegulert", "Elv"])].geometry.values))
        s = les(gdb, "N50_Samferdsel_senterlinje")
        v = s[(s.objtype == "Veglenke") & (s.medium != "U") & (s.typeveg == "enkelBilveg")]
        for kl in veier:
            veier[kl].append(unary_union(v[v.vegkategori == kl.upper()].geometry.values))
        b = s[(s.objtype == "Bane") & (s.medium != "U")]
        bane.append(unary_union(b.geometry.values))

    land = unary_union(land_alle)
    legg_til("land", land, TOL["land"])
    legg_til("by", unary_union(by), TOL["by"])
    legg_til("skog", unary_union(skog), TOL["skog"])
    legg_til("vann", unary_union(vann).buffer(0), TOL["vann"])
    for kl, deler in veier.items():
        legg_til("vei", shapely.line_merge(unary_union(deler)), TOL["vei"], klasse=kl)
    legg_til("bane", shapely.line_merge(unary_union(bane)), TOL["bane"])

    # Bydeler: SSB-polygoner (grove) skåret mot N50-land for Bergen.
    t_utm = pyproj.Transformer.from_crs(4326, 25833, always_xy=True)
    til_utm = lambda g: shapely.transform(g, lambda c: np.column_stack(t_utm.transform(c[:, 0], c[:, 1])))
    bergen_land = land_alle[0]
    grove = [(p, til_utm(g)) for p, g in les_topojson(ROT / "kilder/ssb_bydeler_bergen.topo.json")]
    deler = {p["bydelnavn"]: bergen_land.intersection(g) for p, g in grove}
    rest = bergen_land.difference(unary_union([g for _, g in grove]))
    for bit in getattr(rest, "geoms", [rest]):
        if bit.is_empty or bit.area == 0:
            continue
        navn = min(grove, key=lambda pg: pg[1].distance(bit.representative_point()))[0]["bydelnavn"]
        deler[navn] = deler[navn].union(bit)
    nr = {p["bydelnavn"]: p["bydelnr"] for p, _ in grove}
    etikett = {"Bergenhus": (5.333, 60.405)}
    for navn, g in sorted(deler.items()):
        g = shapely.make_valid(g)
        c = etikett.get(navn)
        if not c:
            c = wgs(g.buffer(-300).representative_point() if not g.buffer(-300).is_empty else g.representative_point())
            c = (c.x, c.y)
        legg_til("bydel", g, TOL["bydel"], navn=navn, nr=nr[navn], lx=round(c[0], 4), ly=round(c[1], 4))

    # Nabokommuner (grovere data)
    raw = json.loads(Path(kommunefil).read_text())
    for f in raw["features"]:
        knr = str(f["properties"]["Kommunenummer"])
        if knr in NABOER:
            g = shapely.make_valid(shape(f["geometry"])).difference(land.buffer(50))
            legg_til("nabo", g, 30, navn=NABOER[knr])

    for s in STEDER:
        try:
            p = stedsnavn(s)
        except Exception as e:
            print("stedsnavn feilet:", s, e, file=sys.stderr)
            p = None
        if p:
            feats.append({"type": "Feature", "properties": {"lag": "sted", "navn": s},
                          "geometry": {"type": "Point", "coordinates": [p[0], p[1]]}})

    def rund(o):
        if isinstance(o, float):
            return round(o, 5)
        if isinstance(o, (list, tuple)):
            return [rund(x) for x in o]
        if isinstance(o, dict):
            return {k: rund(v) for k, v in o.items()}
        return o

    geo = Path(tempfile.gettempdir()) / "bergen.geo.json"
    geo.write_text(json.dumps(rund({"type": "FeatureCollection", "features": feats}),
                              ensure_ascii=False, separators=(",", ":")))
    ut = ROT / "oversikt/bergen.topo.json"
    # TopoJSON via mapshaper (gir også ringretning som d3-geo forventer)
    subprocess.run(["npx", "-y", "mapshaper@0.6.102", "-i", str(geo), "name=kart",
                    "-o", "format=topojson", "quantization=200000", str(ut)], check=True)
    print(ut, ut.stat().st_size // 1024, "kB")
    for lag in ("land", "by", "skog", "vann", "vei", "bane", "bydel", "nabo", "sted"):
        n = sum(1 for f in feats if f["properties"]["lag"] == lag)
        kb = sum(len(json.dumps(rund(f))) for f in feats if f["properties"]["lag"] == lag) // 1024
        print(f"  {lag:6} {n:3} objekter  ~{kb} kB")


if __name__ == "__main__":
    if sys.argv[1] == "hent":
        hent_n50(sys.argv[2])
    else:
        main(sys.argv[1], sys.argv[2])
