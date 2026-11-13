import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (CL_LABEL, CL_WARNA, FEATURE_KEY, JENIS_OPSI, KAT, KAT_WARNA, PILAR, PILAR_PENDEK, PILAR_WARNA, dot,
                   fmt, legend, muat_geojson, tag)

RINGKASAN = "— Ringkasan cluster —"


def tip(r):
    pil = "<br>".join(f"{PILAR_PENDEK[p]} {fmt(r[p])}" for p in PILAR)
    return (f"<b>{r.Wilayah}</b><br>Cluster {r.Cluster} · {CL_LABEL[r.Cluster]}<br>"
            f"Skor IMDI <b>{fmt(r.Skor)}</b> ({r.Kategori}) · peringkat {r.Peringkat}/38<br>{pil}")


def detail(df, nama):
    if nama == RINGKASAN:
        for c in (1, 2):
            d = df[df.Cluster == c]
            st.markdown(f'<div class="cl" style="border-left:4px solid {CL_WARNA[c]}">{tag(c)} <b>{len(d)} wilayah</b>'
                        f'<div class="note">{CL_LABEL[c]}</div>'
                        f'<div style="font-size:12.5px;max-height:150px;overflow:auto">{", ".join(sorted(d.Wilayah))}</div></div>',
                        unsafe_allow_html=True)
        st.markdown('<p class="note">Pilih wilayah pada daftar di atas untuk melihat detailnya.</p>', unsafe_allow_html=True)
        return
    r = df[df.Wilayah == nama].iloc[0]
    pil = "<br>".join(f"{dot(PILAR_WARNA[p])}{PILAR_PENDEK[p]} {fmt(r[p])}" for p in PILAR)
    st.markdown(f'<b>{r.Wilayah}</b> {tag(r.Cluster)}<br><span class="note">{CL_LABEL[r.Cluster]}</span><br>'
                f'Skor IMDI <b>{fmt(r.Skor)}</b> ({r.Kategori}) · peringkat {r.Peringkat}/38<br>{pil}', unsafe_allow_html=True)


def render(df):
    gj = muat_geojson()
    a, b, c = st.columns(3)
    mode = a.selectbox("Warnai berdasarkan", ["Cluster", "Skor IMDI"])
    mc = b.selectbox("Cluster", ["Semua", "1", "2"])
    mj = c.selectbox("Jenis wilayah", JENIS_OPSI)

    ok = df.Cluster.notna()
    if mc != "Semua":
        ok &= df.Cluster == int(mc)
    if mj != "Semua":
        ok &= df.Jenis == mj
    d = df.copy()
    d["Grup"] = d.Cluster.map(lambda x: f"Cluster {x}") if mode == "Cluster" else d.Kategori
    d["tip"] = d.apply(tip, axis=1)
    cmap = {f"Cluster {k}": v for k, v in CL_WARNA.items()} if mode == "Cluster" else KAT_WARNA

    kiri, kanan = st.columns([5, 2])
    with kiri, st.container(border=True):
        st.markdown(f"**Persebaran {'cluster' if mode == 'Cluster' else 'skor IMDI'} kabupaten/kota Jawa Timur**")
        st.caption("Scroll untuk zoom, seret untuk menggeser, tombol di pojok kanan atas untuk reset tampilan.")
        fig = go.Figure()
        pudar = d[~ok]
        if len(pudar):
            fig.add_trace(go.Choropleth(geojson=gj, featureidkey=FEATURE_KEY, locations=pudar.Kunci, z=[0] * len(pudar),
                                        colorscale=[[0, "rgba(128,128,128,.12)"], [1, "rgba(128,128,128,.12)"]],
                                        showscale=False, hoverinfo="skip", marker_line_width=.5))
        aktif = d[ok]
        if len(aktif):
            f2 = px.choropleth(aktif, geojson=gj, featureidkey=FEATURE_KEY, locations="Kunci", color="Grup",
                               color_discrete_map=cmap, custom_data=["tip"])
            f2.update_traces(hovertemplate="%{customdata[0]}<extra></extra>", marker_line_width=.8, marker_line_color="#12151b")
            for t in f2.data:
                fig.add_trace(t)
        fig.update_geos(fitbounds="locations", visible=False, projection_type="mercator", bgcolor="rgba(0,0,0,0)")
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=560, showlegend=False, dragmode="pan",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displaylogo": False})
        lg = [(f"Cluster {k} · {CL_LABEL[k]}", v) for k, v in CL_WARNA.items()] if mode == "Cluster" else \
             [(k, KAT_WARNA[k]) for k in KAT]
        st.markdown(f'<div class="note">{legend(lg)}</div>', unsafe_allow_html=True)
    with kanan, st.container(border=True):
        st.markdown("**Detail wilayah**")
        nama = st.selectbox("Pilih wilayah", [RINGKASAN, *sorted(df.Wilayah)], label_visibility="collapsed")
        detail(df, nama)
    st.markdown('<p class="note">Batas wilayah: GADM yang disederhanakan (via azunzios/indonesia-geojson).</p>',
                unsafe_allow_html=True)