"""ITU Elektrik-Elektronik Fakultesi cevresindeki binalari OpenStreetMap'ten (Overpass API) indirir -> osm_binalar.json
Calistirma:  python osm_indir.py
EEF: OSM relation 3324674 (Nominatim: 41.1040507, 29.0245551). Yaricap: radar menzili 300 m + pay.
"""
import json, os, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
LAT0, LON0, YARICAP = 41.1040507, 29.0245551, 350
SORGU = f'[out:json][timeout:120];(nwr["building"](around:{YARICAP},{LAT0},{LON0}););out geom tags;'
SUNUCULAR = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
             "https://overpass.private.coffee/api/interpreter"]

for ep in SUNUCULAR * 2:
    try:
        r = requests.post(ep, data={"data": SORGU}, headers={"User-Agent": "EHB415-ISAC-ogrenci-projesi/1.0 (akademik)"}, timeout=150)
        r.raise_for_status()
        veri = r.json()
        veri["_kaynak"] = dict(sunucu=ep, lat0=LAT0, lon0=LON0, yaricap_m=YARICAP, sorgu=SORGU)
        json.dump(veri, open(os.path.join(HERE, "osm_binalar.json"), "w", encoding="utf-8"), ensure_ascii=False)
        print("sunucu:", ep, "| oge sayisi:", len(veri["elements"]))
        break
    except Exception as e:
        print("HATA", ep, e); time.sleep(5)
else:
    raise SystemExit("hicbir Overpass sunucusundan veri alinamadi")

# Bazi yansi sunucular iliskilerin (cok parcali binalar) uye geometrisini vermiyor; eksik olanlari tek tek yeniden cek
for i, e in enumerate(veri["elements"]):
    if e["type"] == "relation" and not e.get("members"):
        for ep in SUNUCULAR * 2:
            try:
                r = requests.post(ep, data={"data": f'[out:json][timeout:60];rel({e["id"]});out geom;'}, headers={"User-Agent": "EHB415-ISAC-ogrenci-projesi/1.0 (akademik)"}, timeout=90)
                r.raise_for_status(); yeni = r.json()["elements"][0]
                if yeni.get("members"): veri["elements"][i] = yeni; print("iliski", e["id"], "uyeleri alindi:", ep); break
            except Exception as ex:
                print("HATA iliski", e["id"], ep, ex); time.sleep(3)
        else:
            print("UYARI: iliski", e["id"], "uye geometrisi alinamadi, sahneye girmeyecek")
json.dump(veri, open(os.path.join(HERE, "osm_binalar.json"), "w", encoding="utf-8"), ensure_ascii=False)

tur = {}
yuk = lev = 0
for e in veri["elements"]:
    tur[e["type"]] = tur.get(e["type"], 0) + 1
    t = e.get("tags", {})
    yuk += "height" in t; lev += "building:levels" in t
print("turler:", tur, "| 'height' etiketli:", yuk, "| 'building:levels' etiketli:", lev)
for e in veri["elements"]:
    if e["id"] == 3324674:
        print("EEF etiketleri:", e.get("tags"))
