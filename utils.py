"""Muat data, warna, format angka, dan fungsi bantu dashboard IMDI Jawa Timur 2025."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

BASE = Path(__file__).parent
PILAR = ["Infrastruktur dan Ekosistem", "Literasi Digital", "Pemberdayaan", "Pekerjaan"]
PILAR_PENDEK = dict(zip(PILAR, ["Infrastruktur", "Literasi", "Pemberdayaan", "Pekerjaan"]))
PILAR_WARNA = dict(zip(PILAR, ["#4E79A7", "#59A14F", "#F2C94C", "#F28E2B"]))
KAT = ["Sangat Rendah", "Rendah", "Cukup", "Tinggi", "Sangat Tinggi"]
KAT_WARNA = dict(zip(KAT, ["#F28E2B", "#F2C94C", "#59A14F", "#4E79A7", "#1F3A5F"]))
BATAS = [-np.inf, 33.66, 39.70, 51.74, 57.76, np.inf]
CL_WARNA = {1: "#EBA05A", 2: "#6FA3E6"}
CL_LABEL = {1: "Capaian pilar relatif lebih rendah", 2: "Capaian pilar relatif lebih tinggi"}
MERAH, HIJAU, ABU = "#d64545", "#2f9e5b", "#98a2b3"
FEATURE_KEY = "properties.Kabupaten/Kota"
SUMBER = "Sumber: data skor IMDI 2025 per kabupaten/kota Jawa Timur, diolah."
JENIS_OPSI = ["Semua", "Kabupaten", "Kota"]


def fmt(x, d=2):
    """Format angka gaya Indonesia (koma desimal)."""
    return f"{x:.{d}f}".replace(".", ",")


def sign(x):
    return ("+" if x >= 0 else "−") + fmt(abs(x))


def rgba(hex_, a):
    h = hex_.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def tag(c):
    return f'<span class="tag" style="background:{CL_WARNA[c]}">Cluster {c}</span>'


def dot(color):
    return f'<i class="dot" style="background:{color}"></i>'


def legend(items):
    """items: list of (label, color)."""
    return "".join(f'<span style="margin-right:14px;white-space:nowrap">{dot(c)}{l}</span>' for l, c in items)


@st.cache_data
def muat_data() -> pd.DataFrame:
    raw = pd.read_csv(BASE / "data" / "data_imdi_jatim_2025.csv", encoding="utf-8-sig")
    df = pd.DataFrame({
        "Kunci": raw["Kabupaten/Kota"].str.strip(),
        **{p: raw[p].astype(float) for p in PILAR},
        "Cluster": raw["Cluster"].astype(int),
        "Skor": raw["Indeks Masyarakat Digital"].astype(float),
        "Kategori": raw["Kategori IMDI"].str.strip(),
    })
    df["Wilayah"] = df["Kunci"].str.title().str.replace(r"^Kab\.?\s*", "Kab. ", regex=True)
    df["Wilayah"] = df["Wilayah"].str.replace(r"^Kota\s+", "Kota ", regex=True)
    df["Jenis"] = np.where(df["Kunci"].str.upper().str.startswith("KAB"), "Kabupaten", "Kota")
    # cadangan: hitung ulang kategori dari skor jika kolom CSV tidak valid
    if not df["Kategori"].isin(KAT).all():
        df["Kategori"] = pd.cut(df["Skor"], BATAS, labels=KAT, right=False).astype(str)
    df["Peringkat"] = df["Skor"].rank(ascending=False, method="min").astype(int)
    for p in PILAR:
        df["Rk " + p] = df[p].rank(ascending=False, method="min").astype(int)
    return df


def _luas(ring):
    return sum(ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1] for i in range(len(ring) - 1)) / 2


def _putar(ring, searah_jarum):
    """Plotly (d3-geo) butuh cincin luar searah jarum jam dan lubang berlawanan arah."""
    cw = _luas(ring) < 0
    return ring if cw == searah_jarum else ring[::-1]


@st.cache_data
def muat_geojson():
    with open(BASE / "data" / "batas_wilayah_jatim.geojson", encoding="utf-8") as f:
        gj = json.load(f)
    for ft in gj["features"]:
        g = ft["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            for i, ring in enumerate(poly):
                poly[i] = _putar(ring, searah_jarum=(i == 0))
    return gj


def filter_jenis(df, jenis):
    return df if jenis == "Semua" else df[df["Jenis"] == jenis]


def css():
    st.markdown("""<style>
.block-container{max-width:1120px;padding-top:1.6rem}
.brand small{color:#6FA3E6;font-weight:700;letter-spacing:.08em;font-size:11px}
.brand h1{font-size:19px;line-height:1.25;margin:4px 0 6px;padding:0}
.brand p{margin:0 0 6px;color:#98a2b3;font-size:12.5px}
.kpi{border:1px solid #2c3340;border-radius:12px;padding:12px 14px;background:#1b2029;height:100%}
.kpi b{display:block;font-size:26px}.kpi span{color:#98a2b3;font-size:12.5px;display:block}
.tag{padding:2px 8px;border-radius:10px;color:#fff;font-size:12px}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}
.note{color:#98a2b3;font-size:12.5px}
.tbw{overflow:auto;max-width:100%}
.tbw table{border-collapse:collapse;width:100%;font-size:13px}
.tbw th,.tbw td{text-align:left;padding:5px 8px;border-bottom:1px solid #2c3340}
.tbw th{position:sticky;top:0;background:#1b2029}
.tbw td.n,.tbw th.n{text-align:right}
.cl{padding-left:12px;margin-bottom:6px}
</style>""", unsafe_allow_html=True)


def kpi(label, nilai, ket, warna):
    return (f'<div class="kpi" style="border-top:4px solid {warna}"><span>{label}</span>'
            f'<b>{nilai}</b><span>{ket}</span></div>')


def html_table(headers, rows, num_from=1, maxh=None, bold_rows=()):
    """headers: list judul; rows: list list string (boleh HTML); kolom >= num_from rata kanan."""
    th = "".join(f'<th class="{"n" if i >= num_from else ""}">{h}</th>' for i, h in enumerate(headers))
    body = ""
    for r_i, r in enumerate(rows):
        st_ = ' style="font-weight:600"' if r_i in bold_rows else ""
        body += f"<tr{st_}>" + "".join(f'<td class="{"n" if i >= num_from else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>"
    h = f"max-height:{maxh}px;" if maxh else ""
    return f'<div class="tbw" style="{h}"><table><tr>{th}</tr>{body}</table></div>'


def sumber():
    st.markdown(f'<p class="note">{SUMBER}</p>', unsafe_allow_html=True)


def fig_layout(fig, h=None, **kw):
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=h, **kw)
    return fig