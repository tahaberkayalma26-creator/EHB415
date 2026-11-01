"""OpenStreetMap bina verisinden (osm_binalar.json) Sionna RT sahnesi uretir: sahne.xml + meshes/*.ply
Calistirma:  python sahne_uret.py          (once osm_indir.py calismis olmali)
Cikti: sahne.xml, meshes/{zemin,eef,binalar}.ply, sahne_ozet.json, sahne_ust_gorunum.png

VARSAYIMLAR (hepsi asagida PARAM bolumunde, ozet dosyasina da yazilir):
  - Bina yuksekligi: OSM 'height' etiketi; yoksa 'building:levels' x KAT_M; ikisi de yoksa VARSAYILAN_M.
  - Arazi duz (z=0); gercek egim modellenmedi.
  - Tum binalar 'concrete', zemin 'medium_dry_ground' (Sionna ITU malzemeleri; OSM malzeme bilgisi yok).
  - gNB: EEF (OSM relation 3324674) cati yuksekligi + DIREK_M.
"""
import json, os, re
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import polygonize, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
EEF_ID = 3324674
KAT_M, VARSAYILAN_M, DIREK_M = 3.0, 9.0, 2.0      # varsayim: kat yuksekligi, etiketsiz bina yuksekligi, cati ustu anten direği
YARI_BOYUT = 450.0                                 # zemin levhasi yarim kenari (m)

D = json.load(open(os.path.join(HERE, "osm_binalar.json"), encoding="utf-8"))
K = D["_kaynak"]; LAT0, LON0 = K["lat0"], K["lon0"]
R_YER = 6378137.0
def yerel(lat, lon):                               # kucuk alanda esdikdortgen izdusum: x=dogu, y=kuzey (m)
    return (np.radians(lon - LON0) * R_YER * np.cos(np.radians(LAT0)), np.radians(lat - LAT0) * R_YER)
def hat(g): return LineString([yerel(p["lat"], p["lon"]) for p in g])

def poligon(e):
    if e["type"] == "way":
        pts = [yerel(p["lat"], p["lon"]) for p in e["geometry"]]
        return Polygon(pts).buffer(0) if len(pts) >= 4 else None
    dis = [hat(m["geometry"]) for m in e.get("members", []) if m.get("role") == "outer" and m.get("geometry")]
    ic = [hat(m["geometry"]) for m in e.get("members", []) if m.get("role") == "inner" and m.get("geometry")]
    if not dis: return None
    p = unary_union(list(polygonize(unary_union(dis))))
    if ic: p = p.difference(unary_union(list(polygonize(unary_union(ic)))))
    return p.buffer(0)

def yukseklik(t):
    if "height" in t:
        m = re.search(r"[\d.]+", t["height"].replace(",", "."))
        if m: return float(m.group()), "height"
    if "building:levels" in t:
        m = re.search(r"[\d.]+", t["building:levels"])
        if m: return float(m.group()) * KAT_M, "levels"
    return VARSAYILAN_M, "varsayilan"

def ekstrude(p, h):
    parcalar = []
    for q in (p.geoms if isinstance(p, MultiPolygon) else [p]):
        if q.is_empty or q.area < 4.0: continue            # 4 m2'den kucuk parcalar (OSM gurultusu) atlandi
        parcalar.append(trimesh.creation.extrude_polygon(q.simplify(0.3), h))
    return parcalar

binalar, eef, say, kayit, gnb = [], [], {"height": 0, "levels": 0, "varsayilan": 0}, [], None
for e in D["elements"]:
    p = poligon(e)
    if p is None or p.is_empty: continue
    h, kaynak = yukseklik(e.get("tags", {})); say[kaynak] += 1
    meshler = ekstrude(p, h)
    if not meshler: continue
    kayit.append(dict(id=e["id"], tur=e["type"], h=h, kaynak=kaynak, p=p))
    if e["id"] == EEF_ID:
        eef += meshler; rp = p.representative_point(); gnb = [float(rp.x), float(rp.y), h + DIREK_M]
    else:
        binalar += meshler
if gnb is None: raise SystemExit("EEF (relation 3324674) osm_binalar.json icinde bulunamadi")

os.makedirs(os.path.join(HERE, "meshes"), exist_ok=True)
zemin = trimesh.creation.box(extents=[2 * YARI_BOYUT, 2 * YARI_BOYUT, 1.0]); zemin.apply_translation([0, 0, -0.5])
for ad, m in (("zemin", zemin), ("eef", trimesh.util.concatenate(eef)), ("binalar", trimesh.util.concatenate(binalar))):
    m.export(os.path.join(HERE, "meshes", f"{ad}.ply"))

xml = """<scene version="2.1.0">
	<bsdf type="itu-radio-material" id="concrete"><string name="type" value="concrete"/><float name="thickness" value="0.1"/></bsdf>
	<bsdf type="itu-radio-material" id="medium_dry_ground"><string name="type" value="medium_dry_ground"/><float name="thickness" value="0.1"/></bsdf>
""" + "".join(f"""	<shape type="ply" id="mesh-{ad}"><string name="filename" value="meshes/{ad}.ply"/><boolean name="face_normals" value="true"/><ref id="{b}" name="bsdf"/></shape>
""" for ad, b in (("zemin", "medium_dry_ground"), ("eef", "concrete"), ("binalar", "concrete"))) + "</scene>\n"
open(os.path.join(HERE, "sahne.xml"), "w", encoding="utf-8").write(xml)

json.dump([dict(id=k["id"], h=k["h"], kaynak=k["kaynak"], wkt=k["p"].wkt) for k in kayit], open(os.path.join(HERE, "bina_izdusumleri.json"), "w"))   # rastgele IHA konumu bina icine dusmesin diye

hh = np.array([k["h"] for k in kayit])
ozet = dict(merkez_lat=LAT0, merkez_lon=LON0, yaricap_m=K["yaricap_m"], bina_sayisi=len(kayit), yukseklik_kaynagi=say,
            varsayimlar=dict(kat_m=KAT_M, varsayilan_bina_m=VARSAYILAN_M, direk_m=DIREK_M, arazi="duz z=0", bina_malzeme="concrete", zemin_malzeme="medium_dry_ground"),
            eef_catı_m=gnb[2] - DIREK_M, gnb_xyz_m=gnb, en_yuksek_bina_m=float(hh.max()), ortalama_yukseklik_m=float(hh.mean()))
json.dump(ozet, open(os.path.join(HERE, "sahne_ozet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(ozet, ensure_ascii=False, indent=1))

fig, ax = plt.subplots(figsize=(7.4, 7.4))
renk = {"height": "#16a34a", "levels": "#2563eb", "varsayilan": "#9ca3af"}
for k in kayit:
    for q in (k["p"].geoms if isinstance(k["p"], MultiPolygon) else [k["p"]]):
        x, y = q.exterior.xy
        ax.fill(x, y, color="#dc2626" if k["id"] == EEF_ID else renk[k["kaynak"]], alpha=0.85, ec="black", lw=0.3)
for r in (100, 200, 300):
    ax.add_patch(plt.Circle(gnb[:2], r, fill=False, ls="--", lw=0.8, color="#6b7280")); ax.text(gnb[0] + r * 0.71, gnb[1] + r * 0.71, f"{r} m", fontsize=7, color="#6b7280")
ax.plot(*gnb[:2], "*", color="yellow", ms=16, mec="black", zorder=5)
ax.set_aspect("equal"); ax.set_xlim(-360, 360); ax.set_ylim(-360, 360); ax.set_xlabel("x, doğu (m)"); ax.set_ylabel("y, kuzey (m)")
ax.set_title("İTÜ Elektrik-Elektronik Fakültesi çevresi (OpenStreetMap)\nkırmızı=EEF (gNB çatıda ★), yeşil=OSM yüksekliği, mavi=kat sayısından, gri=VARSAYIM 9 m", fontsize=9)
fig.savefig(os.path.join(HERE, "sahne_ust_gorunum.png"), dpi=140, bbox_inches="tight")
