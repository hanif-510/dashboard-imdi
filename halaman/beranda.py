import streamlit as st

from utils import (CL_LABEL, CL_WARNA, PILAR, PILAR_WARNA, ABU, fmt, kpi, tag)


def render(df):
    n_kab = int((df.Jenis == "Kabupaten").sum())
    ks = [("Kabupaten/kota", "38", f"{n_kab} kabupaten · {38 - n_kab} kota", ABU),
          ("Rata-rata IMDI", fmt(df.Skor.mean()), "tingkat provinsi", CL_WARNA[2]),
          *[(f"Rata-rata {p}", fmt(df[p].mean()), "rata-rata 38 wilayah", PILAR_WARNA[p]) for p in PILAR]]
    for baris in (ks[:3], ks[3:]):
        for col, k in zip(st.columns(3), baris):
            col.markdown(kpi(*k), unsafe_allow_html=True)
        st.write("")

    with st.container(border=True):
        st.markdown("### Temuan utama: dua kelompok wilayah")
        st.caption("Dibentuk dari empat pilar IMDI (bukan dari skor IMDI) dengan Ward Linkage, k = 2.")
        for col, c in zip(st.columns(2), (1, 2)):
            d = df[df.Cluster == c]
            lab = CL_LABEL[c]
            col.markdown(
                f'<div style="border-left:5px solid {CL_WARNA[c]};padding-left:12px">{tag(c)}'
                f'<h4 style="margin:6px 0 0">{lab}</h4><b style="font-size:24px">{len(d)} wilayah</b>'
                f'<div class="note">Rata-rata skor IMDI {fmt(d.Skor.mean())}</div></div>', unsafe_allow_html=True)

    c1, c2 = df[df.Cluster == 1], df[df.Cluster == 2]
    k2 = int((c2.Jenis == "Kota").sum())
    n_cukup = int((df.Kategori == "Cukup").sum())
    sel = {p: c2[p].mean() - c1[p].mean() for p in PILAR}
    urut = sorted(sel, key=sel.get, reverse=True)
    rata = {p: df[p].mean() for p in PILAR}
    tinggi, rendah = max(rata, key=rata.get), min(rata, key=rata.get)
    dekat = " dan ".join(p.lower() for p in urut[2:])
    with st.container(border=True):
        st.markdown("### Ringkasan temuan")
        st.markdown(
            f"- Skor IMDI rata-rata {fmt(df.Skor.mean())}; "
            f"{'separuh wilayah' if n_cukup * 2 == len(df) else 'sebagian wilayah'} berkategori **Cukup** ({n_cukup} dari 38).\n"
            f"- Seluruh {k2} kota berada di Cluster 2; Cluster 1 berisi {len(c1)} kabupaten, "
            f"Cluster 2 berisi {len(c2) - k2} kabupaten dan {k2} kota.\n"
            f"- Pembeda terbesar antar-cluster: **{urut[0]}** (selisih {fmt(sel[urut[0]])}) dan "
            f"**{urut[1]}** ({fmt(sel[urut[1]])}); {dekat} relatif lebih dekat.\n"
            f"- {tinggi} adalah pilar tertinggi (rata-rata {fmt(rata[tinggi])}); "
            f"{rendah} terendah ({fmt(rata[rendah])}).")
