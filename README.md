# 🛡️ AI Scam & Phishing Detector

Aplikasi berbasis **AI & Analisis Heuristik** untuk mendeteksi pesan penipuan (Scam/Phishing) dan tautan berbahaya, dibangun dengan Streamlit dan Scikit-Learn.

## Fitur
- 📧 **Analisis Pesan** — Deteksi teks email/SMS scam menggunakan model NLP (TF-IDF + Random Forest)
- 🔗 **Analisis URL** — Deteksi phishing link berdasarkan analisis heuristik (IP langsung, URL shortener, kata kunci mencurigakan, dll)

## Cara Menjalankan Lokal

```bash
pip install -r requirements.txt
python train_model.py   # opsional, app.py akan auto-train jika model belum ada
python -m streamlit run app.py
```

## Deploy ke Streamlit Cloud

1. Push repository ini ke GitHub
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Klik **"New app"** → pilih repository & branch
4. Set **Main file path**: `app.py`
5. Klik **Deploy!**

> Model akan di-train otomatis saat pertama kali app dijalankan di cloud.

## Stack
- Python 3.9+
- Streamlit
- Scikit-learn (TF-IDF + RandomForestClassifier)
- Pandas, Joblib

---
*Proyek Tugas Kuliah Semester 5 | Teknik Informatika*
