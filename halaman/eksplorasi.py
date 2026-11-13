import plotly.graph_objects as go
import streamlit as st

from utils import (JENIS_OPSI, MERAH, PILAR, PILAR_PENDEK, PILAR_WARNA, dot, fig_layout, filter_jenis, fmt,
                   html_table, rgba)


def boxplot(df):
    fig = go.Figure()
    for p in PILAR:
        fig.add_trace(go.Box(x=df[p], name=PILAR_PENDEK[p], orientation="h", boxpoints=False,
                             marker_color=PILAR_WARNA[p], fillcolor=rgba(PILAR_WARNA[p], .4),
                             line_color=PILAR_WARNA[p], hoverinfo="x"))
        q1, q3 = df[p].quantile(.25), df[p].quantile(.75)
        iqr = q3 - q1
        o = df[(df[p] < q1 - 1.5 * iqr) | (df[p] > q3 + 1.5 * iqr)]
        if len(o):
            fig.add_trace(go.Scatter(x=o[p], y=[PILAR_PENDEK[p]] * len(o), mode="markers+text", showlegend=False,
                                     marker=dict(color=MERAH, size=9), text=o.Wilayah.str.replace("Kota ", ""),
                                     textposition="top center", hovertext=[f"{w}: {fmt(v)}" for w, v in zip(o.Wilayah, o[p])],
                                     hoverinfo="text"))
    fig.update_xaxes(range=[10, 90])
    fig.update_yaxes(autorange="reversed")
    return fig_layout(fig, 300, showlegend=False)


def heatmap(df):
    r = df[PILAR].corr()
    nama = [PILAR_PENDEK[p] for p in PILAR]
    fig = go.Figure(go.Heatmap(z=r.values, x=nama, y=nama, zmin=.2, zmax=1, showscale=False,
                               colorscale=[[0, "#8FB3DD"], [1, "#2F6DB5"]],
                               text=[[fmt(v) for v in row] for row in r.values], texttemplate="%{text}",
                               textfont=dict(color="white", size=13),
                               hovertemplate="%{y} × %{x}: %{text}<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    return fig_layout(fig, 300)


def render(df):
    with st.container(border=True):
        st.markdown("**Statistik deskriptif empat pilar**")
        rows = []
        for p in PILAR:
            c = df[p]
            rows.append([dot(PILAR_WARNA[p]) + p, *[fmt(v) for v in (c.mean(), c.median(), c.std(ddof=1), c.min(),
                                                                       c.quantile(.25), c.quantile(.75), c.max())]])
        st.markdown(html_table(["Pilar", "Rata-rata", "Median", "Std", "Min", "Q1", "Q3", "Maks"], rows),
                    unsafe_allow_html=True)

    kiri, kanan = st.columns(2)
    with kiri, st.container(border=True):
        st.markdown("**Sebaran dan pencilan (IQR)**")
        st.caption("Titik merah = pencilan: hanya pada Infrastruktur (Kota Malang 79,61 dan Kota Surabaya 83,10; "
                   "batas atas 76,74). Keduanya dipertahankan karena valid.")
        st.plotly_chart(boxplot(df), use_container_width=True)
    with kanan, st.container(border=True):
        st.markdown("**Korelasi Pearson antar-pilar**")
        st.caption("Semua positif; tertinggi Literasi–Pemberdayaan, terendah Infrastruktur–Pekerjaan.")
        st.plotly_chart(heatmap(df), use_container_width=True)

    a, b, c = st.columns(3)
    p = a.selectbox("Lihat per pilar", PILAR)
    jenis = b.selectbox("Jenis wilayah", JENIS_OPSI)
    urut = c.selectbox("Urutan", ["Tertinggi", "Terendah"])
    d = filter_jenis(df, jenis).sort_values(p, ascending=(urut == "Terendah"))
    with st.container(border=True):
        st.markdown(f"**Peringkat {p} ({len(d)} wilayah)**")
        fig = go.Figure(go.Bar(x=d[p], y=d.Wilayah, orientation="h", marker_color=PILAR_WARNA[p], cliponaxis=False,
                               text=[fmt(v) for v in d[p]], textposition="outside",
                               hovertemplate="%{y}: %{text}<extra></extra>"))
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(range=[0, d[p].max() * 1.12])
        st.plotly_chart(fig_layout(fig, max(300, 22 * len(d) + 40)), use_container_width=True)
