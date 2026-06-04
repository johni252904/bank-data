import streamlit as st
import pandas as pd
import requests

# Set judul web bapak
st.set_page_config(page_title="Bank Data SLO - Pak Johni", layout="centered")
st.title("🚀 Bank Data Penjualan SLO")
st.subheader("Dashboard Upload Bulanan ala Pak Johni")
st.write("---")

# Konfigurasi kunci rahasia Supabase bapak
SUPABASE_URL = "https://yhpyscuwrsidcgdszuic.supabase.co/rest/v1/data_penjualan_slo"
API_KEY = "sb_publishable_AxSE09q2alSwFDmjaI308g_zOFY5yY" 

headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Kotak Drag and Drop File Excel
uploaded_file = st.file_uploader("Cemplungkan File Excel Bulanan Bapak di Sini:", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Membaca data excel
        df = pd.read_excel(uploaded_file)
        
        st.write("👀 **Pratinjau Data yang Terbaca:**")
        st.dataframe(df.head(5)) # Menampilkan 5 baris teratas buat ngecek
        
        # Tombol Eksekusi Kirim ke Cloud Database
        if st.button("🔥 Jalankan Proses Kirim Data Ke Bank Data Cloud"):
            with st.spinner("Sedang menembakkan data ke server internet bapak... Mohon tunggu..."):
                
                # Memastikan nama kolom di excel bapak huruf kecil semua agar cocok dengan database
                df.columns = [c.lower() for c in df.columns]
                
                # JALUR AMAN: Mengubah semua kolom tanggal/waktu menjadi teks biasa agar tidak eror JSON
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]) or 'tanggal' in col:
                        df[col] = df[col].astype(str)
                
                # Mengubah dataframe menjadi struktur data JSON
                data_json = df.to_dict(orient="records")
                
                # Menembak data ke server Supabase
                response = requests.post(SUPABASE_URL, headers=headers, json=data_json)
                
                if response.status_code in [200, 201]:
                    st.success("✅ BERHASIL TOTAL, PAK JOHNI! Data sudah mendarat di awan. Silakan refresh Excel laptop bapak! 🎉")
                else:
                    st.error(f"❌ Aduh Gagal Pak, Kode Eror: {response.status_code} - {response.text}")
                    
    except Exception as e:
        st.error(f"⚠️ Terjadi kesalahan membaca file Excel bapak: {e}")

st.write("---")
st.caption("Sistem Otomatisasi Bank Data SLO © 2026 - Pak Johni & Gemini")
