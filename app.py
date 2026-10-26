import os
import streamlit as st
# pyrefly: ignore[missing-import]
import joblib
import re
from urllib.parse import urlparse

# Path model — konsisten dengan train_model.py
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scam_text_model.pkl')

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="AI Scam & Phishing Detector",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------------------------------
# Load Trained NLP Model
# ---------------------------------------------------------
@st.cache_resource
def load_nlp_model():
    """
    Muat model dari disk jika ada, atau train otomatis jika belum ada.
    Diperlukan untuk deployment di Streamlit Community Cloud.
    Return (model, pesan_error).
    """
    if not os.path.exists(MODEL_PATH):
        # Auto-train jika model belum ada (misalnya saat pertama deploy)
        try:
            import pandas as pd
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.pipeline import Pipeline

            data = {
                'text': [
                    "Selamat! Anda memenangkan hadiah 100 juta rupiah dari Bank XYZ. Klik link bit.ly/klaim-hadiah untuk klaim.",
                    "URGENT: Akun Gmail Anda ditangguhkan. Verifikasi kata sandi Anda di login-google-security.com sekarang.",
                    "Transfer dana sebesar Rp 500.000 telah berhasil dikirim ke rekening Anda.",
                    "Halo bro, besok kumpul di mana untuk kerjain tugas kelompok?",
                    "Tolong kirimkan laporan mingguan sebelum jam 5 sore ya.",
                    "ALERT! Rekening bank Anda diblokir. Segera konfirmasi PIN Anda di http://secure-update-bank.com",
                    "Pengingat jadwal kuliah Pemrograman Web besok jam 08.00 WIB.",
                    "Anda mendapatkan kuota gratis 50GB. Masukkan nomor HP dan OTP di link berikut."
                ],
                'label': [1, 1, 0, 0, 0, 1, 0, 1]
            }
            df = pd.DataFrame(data)
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
            pipeline.fit(df['text'], df['label'])
            joblib.dump(pipeline, MODEL_PATH, compress=3)
            return pipeline, None
        except Exception as e:
            return None, f"Gagal melatih model secara otomatis: {e}"
    try:
        model = joblib.load(MODEL_PATH)
        return model, None
    except Exception as e:
        return None, f"Gagal memuat model: {e}"

model, model_error = load_nlp_model()

# ---------------------------------------------------------
# Fungsi Deteksi Phishing URL (Heuristic/Feature-based)
# ---------------------------------------------------------
def analyze_url(url):
    reasons = []
    score = 0  # Semakin tinggi semakin mencurigakan (0-100)
    
    # Normalisasi URL
    if not url.startswith(('http://', 'https://')):
        url_to_check = 'http://' + url
    else:
        url_to_check = url
        
    parsed = urlparse(url_to_check)
    domain = parsed.netloc

    # 1. Cek penggunaan IP address langsung
    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    if re.match(ip_pattern, domain):
        score += 35
        reasons.append("Menggunakan alamat IP langsung alih-alih nama domain domain resmi.")

    # 2. Cek Karakter URL Pendek / URL Shortener
    shorteners = ['bit.ly', 'tinyurl.com', 'is.gd', 'buff.ly', 'ow.ly', 't.co', 'cutt.ly']
    if any(s in domain for s in shorteners):
        score += 25
        reasons.append("Menggunakan layanan URL Shortener (menyembunyikan link tujuan asli).")

    # 3. Cek Jumlah Subdomain & Karakter 'Hyphen' (-)
    if domain.count('-') >= 2:
        score += 15
        reasons.append("Domain memiliki banyak tanda hubung ('-'), sering digunakan untuk penipuan typosquatting.")
    
    if domain.count('.') > 2:
        score += 15
        reasons.append("Domain memiliki sub-domain terlalu bertingkat/kompleks.")

    # 4. Cek Kata Kunci Mencurigakan di URL
    suspicious_keywords = ['login', 'verify', 'update', 'account', 'banking', 'secure', 'klaim', 'hadiah', 'free']
    found_keywords = [kw for kw in suspicious_keywords if kw in url.lower()]
    if found_keywords:
        score += 20
        reasons.append(f"URL mengandung kata kunci sensitif: `{', '.join(found_keywords)}`")

    # 5. Cek Penggunaan HTTPS
    if not url.startswith('https://'):
        score += 10
        reasons.append("URL tidak menggunakan protokol aman HTTPS.")

    score = min(score, 100)
    return score, reasons

# ---------------------------------------------------------
# UI Layout Streamlit
# ---------------------------------------------------------
st.title("🛡️ AI Scam & Phishing Detector")
st.markdown("""
Aplikasi berbasis AI & Analisis Heuristik untuk mendeteksi potensi **pesan penipuan (Scam/Phishing)** 
serta **tautan (link) berbahaya**.
""")

st.divider()

# Tab Fitur
tab1, tab2 = st.tabs(["📧 Analisis Pesan Email/SMS", "🔗 Analisis Link / URL Phishing"])

# ---------------------------------------------------------
# TAB 1: Analisis Pesan Teks (NLP)
# ---------------------------------------------------------
with tab1:
    st.subheader("Cek Teks Pesan")
    user_text = st.text_area(
        "Salin & tempel pesan email, SMS, atau chat di bawah ini:",
        height=150,
        placeholder="Contoh: Selamat Anda mendapatkan hadiah 100 juta rupiah..."
    )

    if st.button("Analisis Pesan", type="primary"):
        if not user_text.strip():
            st.warning("Silakan masukkan teks pesan terlebih dahulu.")
        elif model_error:
            st.error(f"⚠️ {model_error}")
        else:
            # Prediksi dengan model NLP
            prediction = model.predict([user_text])[0]
            probabilities = model.predict_proba([user_text])[0]
            confidence = max(probabilities) * 100

            st.divider()
            if prediction == 1:
                st.error(f"🚨 **Peringatan: Pesan Terindikasi SCAM / PHISHING!** (Tingkat Keyakinan: {confidence:.1f}%)")
                st.markdown("""
                **Rekomendasi Tindakan:**
                - Jangan mengeklik tautan apa pun di dalam pesan tersebut.
                - Jangan memberikan informasi pribadi, PIN, OTP, atau kata sandi.
                - Laporkan atau hapus pesan ini.
                """)
            else:
                st.success(f"✅ **Pesan Terindikasi AMAN** (Tingkat Keyakinan: {confidence:.1f}%)")
                st.info("Pesan tidak menunjukkan pola umum penipuan, namun tetap waspada terhadap informasi sensitif.")

# ---------------------------------------------------------
# TAB 2: Analisis Link / URL
# ---------------------------------------------------------
with tab2:
    st.subheader("Cek Link Phishing")
    user_url = st.text_input(
        "Masukkan URL/Link yang ingin diperiksa:",
        placeholder="https://login-google-security.com/update"
    )

    if st.button("Analisis Link", type="primary"):
        if not user_url.strip():
            st.warning("Silakan masukkan URL terlebih dahulu.")
        else:
            score, reasons = analyze_url(user_url.strip())
            
            st.divider()
            col1, col2 = st.columns([1, 2])

            with col1:
                st.metric("Skor Risiko Phishing", f"{score}/100")
                if score >= 60:
                    st.error("Status: **SANGAT BERBAHAYA**")
                elif score >= 30:
                    st.warning("Status: **MENCURIGAKAN**")
                else:
                    st.success("Status: **RELATIF AMAN**")

            with col2:
                st.markdown("**Hasil Indikator Risiko:**")
                if reasons:
                    for r in reasons:
                        st.write(f"- ⚠️ {r}")
                else:
                    st.write(" Tidak ditemukan pola struktur URL yang mencurigakan secara umum.")

st.divider()
st.caption("Proyek Tugas Kuliah Semester 5 | Teknik Informatika | Built with Streamlit & Scikit-Learn")