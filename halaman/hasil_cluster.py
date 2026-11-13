import plotly.graph_objects as go
import streamlit as st

from utils import (CL_LABEL, CL_WARNA, JENIS_OPSI, PILAR, PILAR_PENDEK, fig_layout, fmt, html_table, legend)


def render(df):
    with st.container(border=True):
        st.markdown("**Profil rata-rata empat pilar tiap cluster**")
        st.caption("Karakteristik capaian pilar yang menjadi dasar pembentukan cluster.")
        fig = go.Figure()
        for c in (1, 2):
            v = [df[df.Cluster == c][p].mean() for p in PILAR]
            fig.add_trace(go.Bar(name=f"Cluster {c} · {CL_LABEL[c]}", x=[PILAR_PENDEK[p] for p in PILAR], y=v,
                                 marker_color=CL_WARNA[c], text=[fmt(x) for x in v], textposition="outside",
                                 hovertemplate="%{x}: %{text}<extra>Cluster " + str(c) + "</extra>"))
        fig.update_yaxes(range=[0, 70])
        st.plotly_chart(fig_layout(fig, 340, barmode="group", legend=dict(orientation="h", y=-.15)),
                        use_container_width=True)

    kiri, kanan = st.columns(2)
    with kiri, st.container(border=True):
        st.markdown("**Selisih Cluster 2 − Cluster 1**")
        m1, m2 = df[df.Cluster == 1], df[df.Cluster == 2]
        rows = [[p, fmt(m1[p].mean()), fmt(m2[p].mean()), f"<b>{fmt(m2[p].mean() - m1[p].mean())}</b>"] for p in PILAR]
        rows.append(["<i>Skor IMDI (info pendukung)</i>", fmt(m1.Skor.mean()), fmt(m2.Skor.mean()),
                     f"<b>{fmt(m2.Skor.mean() - m1.Skor.mean())}</b>"])
        st.markdown(html_table(["Variabel", "Cl. 1", "Cl. 2", "Selisih"], rows), unsafe_allow_html=True)
        st.markdown('<p class="note">Perbedaan dijelaskan secara deskriptif; tidak dilakukan uji inferensial. '
                    'Skor IMDI tidak ikut membentuk cluster.</p>', unsafe_allow_html=True)
    with kanan, st.container(border=True):
        st.markdown("**Pemisah cluster**")
        st.caption("Literasi vs Pemberdayaan, dua pilar dengan selisih terbesar.")
        fig = go.Figure()
        for c in (1, 2):
            d = df[df.Cluster == c]
            fig.add_trace(go.Scatter(x=d["Literasi Digital"], y=d["Pemberdayaan"], mode="markers", name=f"Cluster {c}",
                                     marker=dict(color=CL_WARNA[c], size=10, opacity=.85),
                                     hovertext=[f"{w} · Literasi {fmt(a)} · Pemberdayaan {fmt(b)}" for w, a, b in
                                                zip(d.Wilayah, d["Literasi Digital"], d["Pemberdayaan"])], hoverinfo="text"))
        fig.update_xaxes(range=[20, 75], title="Literasi Digital →")
        fig.update_yaxes(range=[10, 65], title="Pemberdayaan →")
        st.plotly_chart(fig_layout(fig, 320, legend=dict(orientation="h", y=-.25)), use_container_width=True)

    with st.container(border=True):
        st.markdown("**Anggota cluster**")
        a, b, c = st.columns([1, 1, 2])
        cl = a.selectbox("Cluster", ["Semua", "1", "2"])
        jn = b.selectbox("Jenis", JENIS_OPSI)
        cari = c.text_input("Cari wilayah", placeholder="Cari wilayah…")
        d = df
        if cl != "Semua":
            d = d[d.Cluster == int(cl)]
        if jn != "Semua":
            d = d[d.Jenis == jn]
        if cari:
            d = d[d.Wilayah.str.lower().str.contains(cari.lower(), regex=False)]
        d = d.sort_values(["Cluster", "Skor"], ascending=[True, False])
        rows = [[w, str(k), fmt(s), *[fmt(r[p]) for p in PILAR]] for w, k, s, (_, r) in
                zip(d.Wilayah, d.Cluster, d.Skor, d.iterrows())]
        if rows:
            html = html_table(["Wilayah", "Cluster", "Skor IMDI", *[PILAR_PENDEK[p] for p in PILAR]], rows, num_from=2, maxh=420)
        else:
            html = '<p class="note">Tidak ditemukan.</p>'
        st.markdown(html + f'<p class="note">{len(d)} wilayah</p>', unsafe_allow_html=True)

    with st.expander("Metode Ward Linkage (k = 2)"):
        st.write("Z-score → jarak Euclidean → AHC dengan 4 linkage × k = 2–6 (20 model). Dipilih model dengan total "
                 "peringkat terendah dari tiga indeks (Silhouette ↑, Davies-Bouldin ↓, Calinski-Harabasz ↑).")
        rows = [["Ward k=2", "0,349", "1,019", "26,463", "14"], ["Complete k=2", "0,331", "1,082", "27,144", "16"],
                ["Average k=3", "0,308", "1,014", "18,467", "23"]]
        st.markdown(html_table(["Model", "Silhouette", "DBI", "CHI", "Total rank"], rows, bold_rows=(0,)), unsafe_allow_html=True)
        st.markdown('<p class="note">Tiga teratas dari 20 kombinasi. Nilai DBI Ward k=2 bukan yang terbaik, sehingga '
                    'pemilihan didasarkan pada total peringkat. "Cluster 1/2" adalah label hasil analisis, bukan '
                    'kategori resmi IMDI.</p>', unsafe_allow_html=True)
