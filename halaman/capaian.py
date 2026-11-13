import plotly.graph_objects as go
import streamlit as st

from utils import JENIS_OPSI, KAT, KAT_WARNA, fig_layout, filter_jenis, fmt, legend


def donut(d):
    labels, vals, cols, tips = [], [], [], []
    for k in KAT:
        m = d[d.Kategori == k].sort_values("Skor", ascending=False)
        if m.empty:
            continue
        labels.append(k); vals.append(len(m)); cols.append(KAT_WARNA[k])
        tips.append(f"<b>{k}</b> · {len(m)} wilayah ({fmt(len(m) / len(d) * 100, 1)}%)<br>" +
                    "<br>".join(f"{w} ({fmt(s)})" for w, s in zip(m.Wilayah, m.Skor)))
    fig = go.Figure(go.Pie(labels=labels, values=vals, hole=.55, sort=False, marker_colors=cols,
                           textinfo="none", hovertext=tips, hoverinfo="text"))
    fig.add_annotation(text=f"<b>{len(d)}</b><br>wilayah", showarrow=False, font_size=18)
    return fig_layout(fig, 230, showlegend=False)


def render(df):
    a, b, c = st.columns(3)
    jenis = a.selectbox("Jenis wilayah", JENIS_OPSI)
    kat = b.selectbox("Kategori", ["Semua", *KAT])
    urut = c.selectbox("Urutan", ["Tertinggi", "Terendah"])
    jf = filter_jenis(df, jenis)
    d = jf if kat == "Semua" else jf[jf.Kategori == kat]
    d = d.sort_values("Skor", ascending=(urut == "Terendah"))

    kiri, kanan = st.columns([2, 1])
    with kiri, st.container(border=True):
        st.markdown(f"**Peringkat skor IMDI ({len(d)} wilayah)**")
        st.caption("Warna = kategori IMDI.")
        if d.empty:
            st.caption("Tidak ada wilayah.")
        else:
            fig = go.Figure(go.Bar(x=d.Skor, y=d.Wilayah, orientation="h", cliponaxis=False,
                                   marker_color=[KAT_WARNA[k] for k in d.Kategori],
                                   text=[fmt(v) for v in d.Skor], textposition="outside",
                                   hovertemplate="%{y}: %{text}<extra></extra>"))
            fig.update_yaxes(autorange="reversed")
            fig.update_xaxes(range=[0, 70])
            st.plotly_chart(fig_layout(fig, max(300, 22 * len(d) + 40)), use_container_width=True)
    with kanan, st.container(border=True):
        st.markdown("**Sebaran kategori IMDI**")
        st.caption(f"Arahkan kursor ke irisan untuk melihat wilayahnya. Mengikuti filter jenis wilayah ({jenis}).")
        st.plotly_chart(donut(jf), use_container_width=True)
        for k in KAT:
            n = int((jf.Kategori == k).sum())
            st.markdown(legend([(f"{k}: <b>{n}</b> ({fmt(n / len(jf) * 100, 1)}%)", KAT_WARNA[k])]), unsafe_allow_html=True)
        st.markdown('<p class="note">Klasifikasi IMDI 2025: &lt;33,66 Sangat Rendah · 33,66–39,69 Rendah · '
                    '39,70–51,73 Cukup · 51,74–57,75 Tinggi · ≥57,76 Sangat Tinggi.</p>', unsafe_allow_html=True)
