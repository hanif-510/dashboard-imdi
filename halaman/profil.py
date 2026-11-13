import plotly.graph_objects as go
import streamlit as st

from utils import (CL_LABEL, CL_WARNA, HIJAU, MERAH, PILAR, PILAR_PENDEK, fig_layout, fmt, html_table, sign, tag)


def render(df):
    urut_skor = df.sort_values("Skor", ascending=False)
    nama = sorted(df.Wilayah)
    nama_sel = st.selectbox("Wilayah", nama, index=nama.index(urut_skor.Wilayah.iloc[0]))
    r = df[df.Wilayah == nama_sel].iloc[0]
    c = int(r.Cluster)
    cl = df[df.Cluster == c]

    with st.container(border=True):
        st.markdown(f'<h3 style="margin:0">{r.Wilayah} {tag(c)}</h3><div class="note">{CL_LABEL[c]} · Skor IMDI '
                    f'<b>{fmt(r.Skor)}</b> ({r.Kategori}) · peringkat {r.Peringkat} dari 38</div>', unsafe_allow_html=True)

    kiri, kanan = st.columns(2)
    with kiri, st.container(border=True):
        st.markdown("**Profil empat pilar**")
        theta = [PILAR_PENDEK[p] for p in PILAR]
        warna_cl = CL_WARNA[c]

        def seri(v, nama_, warna, dash=None, fill=None):
            return go.Scatterpolar(r=[*v, v[0]], theta=[*theta, theta[0]], name=nama_, line=dict(color=warna, width=2, dash=dash),
                                   fill="toself" if fill else None, fillcolor=fill)

        fig = go.Figure([
            seri([df[p].mean() for p in PILAR], "Rata-rata provinsi", "#888888", "dash"),
            seri([cl[p].mean() for p in PILAR], "Rata-rata cluster", warna_cl, "dash"),
            seri([r[p] for p in PILAR], r.Wilayah, MERAH, None, "rgba(214,69,69,.2)")])
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100], tickvals=[25, 50, 75, 100])),
                          legend=dict(orientation="h", y=-.1))
        st.plotly_chart(fig_layout(fig, 380), use_container_width=True)
    with kanan, st.container(border=True):
        st.markdown("**Perbandingan**")
        rows = []
        for p in [*PILAR, "Skor IMDI"]:
            kol, rk = ("Skor", "Peringkat") if p == "Skor IMDI" else (p, "Rk " + p)
            v = r[kol]
            a, b = v - df[kol].mean(), v - cl[kol].mean()
            sw = lambda x: f'<span style="color:{HIJAU if x >= 0 else MERAH}">{sign(x)}</span>'
            rows.append([p, fmt(v), f"{int(r[rk])}/38", sw(a), sw(b)])
        st.markdown(html_table(["Pilar", "Skor", "Peringkat", "vs Provinsi", "vs Cluster"], rows), unsafe_allow_html=True)
        st.markdown('<p class="note">Hijau = di atas rata-rata, merah = di bawah.</p>', unsafe_allow_html=True)
