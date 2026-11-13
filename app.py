"""Dashboard 'Potret Masyarakat Digital Jawa Timur 2025'. Jalankan: streamlit run app.py"""
import streamlit as st

import utils
from halaman import beranda, capaian, eksplorasi, hasil_cluster, peta, profil

st.set_page_config(page_title="Potret Masyarakat Digital Jawa Timur 2025", page_icon="📊", layout="wide")
utils.css()

MENU = {
    "Beranda": beranda,
    "Capaian & Kategori": capaian,
    "Eksplorasi Pilar": eksplorasi,
    "Hasil Cluster": hasil_cluster,
    "Peta Persebaran": peta,
    "Profil Wilayah": profil,
}

with st.sidebar:
    st.markdown('<div class="brand"><small>IMDI 2025</small><h1>Potret Masyarakat Digital Jawa Timur</h1>'
                '<p>Menelusuri capaian 38 kabupaten/kota dan kelompok wilayahnya</p></div>', unsafe_allow_html=True)
    pilihan = st.radio("Menu", list(MENU), label_visibility="collapsed")

df = utils.muat_data()
st.markdown(f"## {pilihan}")
MENU[pilihan].render(df)
utils.sumber()
