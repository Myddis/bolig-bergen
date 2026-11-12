"""Områdedata for en eiendom: prisutvikling i strøket, solforhold, kollektivfrekvens og budmarked.

Bruk:  python3 scripts/omrade.py <gnr> <bnr>        (fra geokod.py)
Ut:    JSON med
  omrade:     navn, slug, url, medianKrM2 (siste kvartal), salg12mnd,
              vekst5aar (årlig snitt, %), vekst12mnd (%), kvartaler (tabell)
  bergen:     vekst5aar, vekst12mnd for blokkleiligheter i Bergen (SSB 07221)
  sol:        solscore (0–100), timerJuni, timerDes, vurdering
  marked:     avvikProsent (typisk salg over/under prisantydning), andelOver, dagerPaaMarkedet
  kollektiv:  stopp, avgangerRushtid
  nabolag:    dagligvare {navn, meter}, trening {navn, meter}, servering1km (antall kafeer og restauranter), url
  kilder:     liste med URL-er

Kilder: eiendomssjekk.no (tinglyste salg fra Kartverkets grunnbok, Finn-annonser, solberegning)
og SSBs prisindeks for brukte boliger (tabell 07221). Krever nettilgang til eiendomssjekk.no og data.ssb.no.

Vekst beregnes robust: snitt av de fire siste kvartalene mot snitt av fire kvartaler tidligere
(4 år tilbake for 5-årsvekst, 1 år tilbake for 12-månedersvekst), slik at enkeltkvartaler med få salg
ikke styrer resultatet.
"""

import html
import json
import re
import sys
import urllib.request

ES = "https://eiendomssjekk.no"
UA = {"User-Agent": "bolig-bergen/1.0 (privat boligsok)"}


def hent(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def tekst(html_kode):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", html_kode, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", t)).replace("\u00a0", " ").replace("\u202f", " ")
    linjer = [re.sub(r" +", " ", l.strip()) for l in t.split("\n") if l.strip()]
    return " | ".join(linjer)


def tall(s):
    return float(s.replace(" ", "").replace(" ", "").replace(",", "."))


def snitt(xs):
    xs = [x for x in xs if x]
    return sum(xs) / len(xs) if xs else None


def vekst(kvartaler, tilbake):
    """Årlig vekst (%) fra snitt av 4 kvartaler `tilbake` kvartaler før de 4 siste."""
    if len(kvartaler) < tilbake + 4:
        return None
    siste = snitt([k[1] for k in kvartaler[-4:]])
    for_ = snitt([k[1] for k in kvartaler[-4 - tilbake:-tilbake]])
    if not siste or not for_:
        return None
    aar = tilbake / 4
    return round(((siste / for_) ** (1 / aar) - 1) * 100, 1)


def eiendom(gnr, bnr):
    url = f"{ES}/eiendom/4601-{gnr}-{bnr}"
    h = hent(url)
    s = tekst(h)
    ut = {"url": url}
    m = re.search(r'href="/omraade/([a-z0-9-]+)"', h)
    ut["omradeSlug"] = m.group(1) if m else None
    m = re.search(r"Solscore (\d+) av 100", s)
    ut["solscore"] = int(m.group(1)) if m else None
    m = re.search(r"([\d,]+) t juni / ([\d,]+) t des", s)
    if m:
        ut["timerJuni"], ut["timerDes"] = tall(m.group(1)), tall(m.group(2))
    m = re.search(r"(\w+ solforhold) \|", s)
    ut["solvurdering"] = m.group(1) if m else None
    # Solscoren gjelder ett målepunkt for hele eiendommen. På store tomter med flere bygg kan det ligge langt unna boligen.
    m = re.search(r"Målepunkt nærmest ([^|]+?) \|", s)
    ut["malepunkt"] = m.group(1).strip() if m else None
    m = re.search(r"Alle adresser \((\d+)\)", s)
    ut["adresserPaaEiendom"] = int(m.group(1)) if m else 1
    m = re.search(r"Tomteareal \| ([\d  ]+) m²", s)
    ut["tomtM2"] = int(re.sub(r"\D", "", m.group(1))) if m else None
    m = re.search(r"Kollektiv \| ([^|]+) \| ([^|]+) \| Avganger i timen i rushet[^|]*\| ([\d,]+)", s)
    if m:
        ut["kollektiv"] = {"stopp": m.group(1).strip(), "avstand": m.group(2).strip(), "avgangerRushtid": tall(m.group(3))}
    return ut


def meter(s):
    s = s.strip()
    return round(tall(s[:-2]) * 1000) if s.endswith("km") else round(tall(s[:-1]))


def nabolag(gnr, bnr):
    """Hverdagstjenester rundt eiendommen (Eiendomssjekk, avstander langs gangnettet fra OpenStreetMap)."""
    url = f"{ES}/eiendom/4601-{gnr}-{bnr}/nabolag"
    s = tekst(hent(url))
    ut = {"url": url}
    for typ, nokkel in (("dagligvare", "dagligvare"), ("treningssenter", "trening")):
        m = re.search(r"\| ([^|]+) \| " + typ + r" \| [^|]+ \| ([\d ,]+ ?k?m) \|", s)
        ut[nokkel] = {"navn": m.group(1).strip(), "meter": meter(m.group(2))} if m else None
    m = re.search(r"Innen en kilometer i luftlinje fra eiendommen ligger (\d+) restauranter", s)
    ut["servering1km"] = int(m.group(1)) if m else None
    return ut


def omrade(slug):
    url = f"{ES}/omraade/{slug}"
    h = hent(url)
    s = tekst(h)
    ut = {"slug": slug, "url": url}
    m = re.search(r"Område i Bergen \| ([^|]+) \|", s)
    ut["navn"] = m.group(1).strip() if m else slug
    rader = re.findall(r"(20\d\dK[1-4]) \| (\d+) \| [\d\s ]+ kr \| ([\d\s ]+) kr/m²", s)
    kv = [(q, tall(krm2), int(n)) for q, n, krm2 in rader]
    ut["kvartaler"] = [{"kvartal": q, "medianKrM2": round(v), "salg": n} for q, v, n in kv]
    ut["medianKrM2"] = round(kv[-1][1]) if kv else None
    m = re.search(r"Sist målt: leiligheter ([\d\s ]+) kr/m²", s)
    ut["medianKrM2Leiligheter"] = round(tall(m.group(1))) if m else None
    m = re.search(r"\| ([\d\s ]+) \| salg siste 12 måneder", s)
    ut["salg12mnd"] = int(tall(m.group(1))) if m else None
    serie = [(q, v) for q, v, n in kv]
    ut["vekst5aar"] = vekst(serie, 16)
    ut["vekst12mnd"] = vekst(serie, 4)
    marked = {}
    m = re.search(r"selges typisk ([\d,]+) prosent (over|under) prisantydning", s)
    if m:
        marked["avvikProsent"] = tall(m.group(1)) * (1 if m.group(2) == "over" else -1)
    m = re.search(r"\| (\d+) % \| solgt over prisantydning", s)
    if m:
        marked["andelOver"] = int(m.group(1))
    m = re.search(r"\| (\d+) dager \| typisk tid på markedet", s)
    if m:
        marked["dagerPaaMarkedet"] = int(m.group(1))
    m = re.search(r"Basert på (\d+) salg siste 12 måneder der vi fant Finn-annonsen", s)
    if m:
        marked["grunnlagSalg"] = int(m.group(1))
    ut["marked"] = marked
    return ut


def bergen_ssb():
    """SSB 07221: prisindeks for brukte blokkleiligheter i Bergen, kvartalsvis."""
    url = "https://data.ssb.no/api/v0/no/table/07221"
    q = {"query": [
        {"code": "Region", "selection": {"filter": "item", "values": ["003"]}},
        {"code": "Boligtype", "selection": {"filter": "item", "values": ["03"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Boligindeks"]}},
        {"code": "Tid", "selection": {"filter": "top", "values": ["24"]}},
    ], "response": {"format": "json-stat2"}}
    d = json.loads(hent(url, json.dumps(q).encode(), {"Content-Type": "application/json"}))
    tider = list(d["dimension"]["Tid"]["category"]["index"].keys())
    tider.sort(key=lambda t: d["dimension"]["Tid"]["category"]["index"][t])
    serie = [(t, v) for t, v in zip(tider, d["value"]) if v is not None]
    return {"vekst5aar": vekst(serie, 16), "vekst12mnd": vekst(serie, 4), "sisteKvartal": serie[-1][0],
            "kilde": "SSB tabell 07221, blokkleiligheter Bergen"}


def main(gnr, bnr):
    ut = {"kilder": []}
    try:
        e = eiendom(gnr, bnr)
        ut["sol"] = {k: e.get(k) for k in ("solscore", "timerJuni", "timerDes", "solvurdering", "malepunkt", "adresserPaaEiendom", "tomtM2")}
        ut["kollektiv"] = e.get("kollektiv")
        ut["kilder"].append(e["url"])
        try:
            ut["nabolag"] = nabolag(gnr, bnr)
            ut["kilder"].append(ut["nabolag"]["url"])
        except Exception as ex:
            ut["nabolagFeil"] = str(ex)[:200]
        if e.get("omradeSlug"):
            o = omrade(e["omradeSlug"])
            ut["marked"] = o.pop("marked")
            ut["omrade"] = o
            ut["kilder"].append(o["url"])
    except Exception as ex:
        ut["eiendomssjekkFeil"] = str(ex)[:200]
    try:
        ut["bergen"] = bergen_ssb()
        ut["kilder"].append("https://www.ssb.no/statbank/table/07221")
    except Exception as ex:
        ut["ssbFeil"] = str(ex)[:200]
    print(json.dumps(ut, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
