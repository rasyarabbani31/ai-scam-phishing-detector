import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
# pyrefly: ignore[missing-import]
import joblib

# Path model disimpan relatif terhadap lokasi skrip ini
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scam_text_model.pkl')

# 1. Sample Dataset Sederhana (Bisa diganti/diperluas dengan dataset Kaggle: Spam Email / Phishing Dataset)
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
    'label': [1, 1, 0, 0, 0, 1, 0, 1]  # 1 = Scam/Phishing, 0 = Safe
}

df = pd.DataFrame(data)

# 2. Pipeline Feature Extraction (TF-IDF) + Model Classifier
model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# 3. Train Model
model_pipeline.fit(df['text'], df['label'])

# 4. Save Model
try:
    joblib.dump(model_pipeline, MODEL_PATH, compress=3)
    print(f"[OK] Model berhasil dilatih dan disimpan di: {MODEL_PATH}")
except Exception as e:
    print(f"[ERROR] Gagal menyimpan model: {e}")