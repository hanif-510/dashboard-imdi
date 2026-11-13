# Dashboard Potret Masyarakat Digital Jawa Timur 2025

## Cara menjalankan
1. Pasang Python 3.10+ (centang "Add Python to PATH").
2. Buka folder ini di VS Code, lalu buka terminal (Ctrl + `).
3. `pip install -r requirements.txt`
4. `python -m streamlit run app.py`
5. Buka http://localhost:8501 jika browser tidak terbuka otomatis.

## Struktur
- `app.py` – konfigurasi, sidebar, navigasi
- `utils.py` – muat data, warna, format angka
- `halaman/` – satu modul per menu
- `data/` – CSV dan GeoJSON
