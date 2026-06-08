import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. KONFIGURASI HALAMAN MEWAH & MELEBAR
st.set_page_config(layout="wide", page_title="DASHBOARD SALES PPM")

# SUNTIKAN CSS UNTUK DARK MODE & TEKS NEON GREEN TOTAL
st.markdown("""
    <style>
    .stApp {
        background-color: #0d0d0d !important;
        color: #39ff14 !important;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.6), 0 0 20px rgba(57, 255, 20, 0.4) !important;
    }
    [data-testid="stMetricValue"] {
        color: #39ff14 !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 8px rgba(57, 255, 20, 0.5) !important;
    }
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    div.stSelectbox, div.stRadio {
        color: #39ff14 !important;
    }
    div.stRadio > div > label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stDataFrame {
        border: 1px solid #39ff14 !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Fungsi singkat uang
def singkat_uang(angka):
    if abs(angka) >= 1_000_000_000:
        return f"Rp {angka / 1_000_000_000:,.2f} M"
    elif abs(angka) >= 1_000_000:
        return f"Rp {angka / 1_000_000:,.2f} Jt"
    else:
        return f"Rp {angka:,.0f}"

# 2. HEADER
st.title("🚀 DASHBOARD SALES PPM")
st.write("Command Center Sales & Geospatial Radar v4.0 (AUTOPILOT MOD) — Powered by Pak Johni.")
st.markdown("---")

# Nama file Excel bapak yang ada di GitHub
NAMA_FILE_DATA = "MASTER_DATA_SLI_AUTOPILOT_REAL.xlsx"

# 3. SISTEM DETEKSI DATA OTOMATIS (AUTOPILOT)
if os.path.exists(NAMA_FILE_DATA):
    df_mentah = pd.read_excel(NAMA_FILE_DATA)
    
    # BONUS: Tetap kasih tombol opsional di bawah kalau bapak atau tim sewaktu-waktu mau upload file cadangan lain
    with st.sidebar:
        st.markdown("### ⚙️ Mode Admin")
        file_cadangan = st.file_uploader("🔄 Timpa data dengan Excel lain (opsional):", type=["xlsx"])
        if file_cadangan is not None:
            df_mentah = pd.read_excel(file_cadangan)
            st.success("Data berhasil ditimpa sementara!")

    # 4. FILTER BRAND
    st.subheader("🎯 Filter Tampilan Brand:")
    if "BRAND" in df_mentah.columns:
        lista_brand = sorted(df_mentah["BRAND"].unique().tolist())
        pilihan_brand = st.radio("Pilih Brand:", ["SEMUA BRAND"] + lista_brand, horizontal=True)
        if pilihan_brand != "SEMUA BRAND":
            df = df_mentah[df_mentah["BRAND"] == pilihan_brand].copy()
        else:
            df = df_mentah.copy()
    else:
        df = df_mentah.copy()
        pilihan_brand = "SEMUA BRAND"

    # Urutin bulan biar rapi
    urutan_bulan = ["JAN", "FEB", "MAR", "APR", "MEI", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    if "BULAN" in df.columns:
        df["BULAN"] = df["BULAN"].astype(str).str.upper()
        df["BULAN"] = pd.Categorical(df["BULAN"], categories=urutan_bulan, ordered=True)
        df = df.sort_values("BULAN")

    kolom_keuangan = [col for col in df.columns if 'ACTUAL' in col or 'TARGET' in col]
    
    # 5. Pilihan Sumbu Y Finansial
    st.subheader("📊 Pilih Indikator Keuangan:")
    pilihan_y = st.selectbox("Data Sumbu Y / Ukuran Radar Peta:", kolom_keuangan)

    st.markdown("---")

    # 6. KARTU METRIK UTAMA
    st.subheader(f"📈 Ringkasan Performa: {pilihan_brand}")
    kolom_m1, kolom_m2, kolom_m3 = st.columns(3)
    target_2026 = df["TOTAL TARGET 2026"].sum() if "TOTAL TARGET 2026" in df.columns else 0
    actual_2026 = df["ACTUAL 2026"].sum() if "ACTUAL 2026" in df.columns else 0
    actual_2025 = df["ACTUAL 2025"].sum() if "ACTUAL 2025" in df.columns else 0
    persen_ach_2026 = (actual_2026 / target_2026 * 100) if target_2026 > 0 else 0
    growth_rate = ((actual_2026 - actual_2025) / abs(actual_2025) * 100) if actual_2025 != 0 else 0
    
    if pilihan_y == "ACTUAL 2025":
        with kolom_m1: st.metric(label="Actual 2025", value=singkat_uang(actual_2025))
        with kolom_m2: st.metric(label="Actual 2026", value=singkat_uang(actual_2026))
        with kolom_m3: st.metric(label="Growth %", value=f"{growth_rate:,.2f} %")
    else:
        with kolom_m1: st.metric(label="Target 2026", value=singkat_uang(target_2026))
        with kolom_m2: st.metric(label="Actual 2026", value=singkat_uang(actual_2026))
        with kolom_m3: st.metric(label="Achievement %", value=f"{persen_ach_2026:,.2f} %")
        
    st.markdown("---")
    
    # 7. FITUR GEOSPATIAL MAP INDONESIA RADAR
    st.subheader("🗺️ Interaktif Geospatial Region Map")
    daftar_region_ada = sorted([r for r in df["REGION"].unique() if pd.notna(r)])
    pilihan_peta_region = st.radio("Silakan klik Wilayah untuk dinyalakan di Peta:", daftar_region_ada)
    
    # Koordinat Pulau Besar Indonesia
    koordinat_map = {
        'SUMATRA': {'lat': [-1, 2, -3, -5], 'lon': [102, 99, 104, 105], 'reg': 'WEST'},
        'JAWA': {'lat': [-6.5, -7, -7.5], 'lon': [107, 110, 112], 'reg': 'HO'},
        'KALIMANTAN': {'lat': [1, -1, 0], 'lon': [113, 115, 111], 'reg': 'CENTRAL'},
        'SULAWESI': {'lat': [-1, -3, 1], 'lon': [120, 122, 124], 'reg': 'EAST'},
        'PAPUA': {'lat': [-3, -4], 'lon': [136, 140], 'reg': 'EAST'}
    }
    
    map_rows = []
    for pulau, info in koordinat_map.items():
        for lt, ln in zip(info['lat'], info['lon']):
            map_rows.append({'Pulau': pulau, 'Latitude': lt, 'Longitude': ln, 'REGION': info['reg']})
    df_peta_base = pd.DataFrame(map_rows)
    
    total_dana_nasional = df[pilihan_y].sum()
    df_spesifik_reg = df[df["REGION"] == pilihan_peta_region]
    dana_aktual_reg = df_spesifik_reg[pilihan_y].sum()
    target_reg = df_spesifik_reg["TOTAL TARGET 2026"].sum() if "TOTAL TARGET 2026" in df_spesifik_reg.columns else 1
    ach_persen_reg = (dana_aktual_reg / target_reg * 100) if target_reg > 0 else 0
    kontribusi_nasional = (dana_aktual_reg / total_dana_nasional * 100) if total_dana_nasional > 0 else 0
    
    status_target = "🟢 ACHIEVED (>100%)" if ach_persen_reg >= 100 else "🔴 UNDER TARGET (<100%)"
    
    df_peta_base['Ukuran_Radar'] = df_peta_base['REGION'].apply(lambda x: 80 if x == pilihan_peta_region else 20)
    df_peta_base['Warna_Radar'] = df_peta_base['REGION'].apply(lambda x: '#39ff14' if x == pilihan_peta_region else '#333333')

    fig_map = px.scatter_geo(df_peta_base, lat='Latitude', lon='Longitude', hover_name='Pulau', size='Ukuran_Radar', color='Warna_Radar', color_discrete_map={'#39ff14': '#39ff14', '#333333': '#222222'}, size_max=40, template="plotly_dark")
    fig_map.update_geos(showland=True, landcolor="#111111", showocean=True, oceancolor="#050505", showcountries=True, countrycolor="#333333", center=dict(lat=-2, lon=118), projection_scale=6.5, visible=False)
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d', showlegend=False, height=450)
    
    kolom_peta_1, kolom_peta_2 = st.columns([2, 1])
    with kolom_peta_1:
        st.plotly_chart(fig_map, use_container_width=True)
    with kolom_peta_2:
        st.markdown(f"""
        <div style="background-color:#111111; border: 2px solid #39ff14; border-radius:12px; padding:25px; margin-top:20px;">
            <h3 style="margin-top:0; color:#ffffff;">📟 Radar Wilayah: <span style="color:#39ff14;">{pilihan_peta_region}</span></h3>
            <hr style="border-color:#39ff14;">
            <p style="font-size:16px; color:#ffffff;">💰 Total ({pilihan_y}):<br><b style="font-size:24px; color:#39ff14;">{singkat_uang(dana_aktual_reg)}</b></p>
            <p style="font-size:16px; color:#ffffff;">📊 Kontribusi vs Nasional:<br><b style="font-size:22px; color:#00bfff;">{kontribusi_nasional:,.1f}%</b></p>
            <p style="font-size:16px; color:#ffffff;">🎯 Status Target Region:<br><b style="font-size:18px;">{status_target} ({ach_persen_reg:,.1f}%)</b></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 8. GRAFIK TREN BULANAN ANTI-PECAH
    st.subheader("📊 Grafik Tren Bulanan")
    if "BULAN" in df.columns and "REGION" in df.columns:
        df_rangkum = df.groupby(["BULAN", "REGION"], as_index=False)[pilihan_y].sum()
        peta_warna_neon = {'CENTRAL': '#00bfff', 'EAST': '#39ff14', 'HO': '#ff3333', 'WEST': '#ffff00'}
        fig_bar = px.bar(df_rangkum, x="BULAN", y=pilihan_y, color="REGION", barmode="group", color_discrete_map=peta_warna_neon, template="plotly_dark")
        fig_bar.update_layout(plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d', font=dict(color='#ffffff'))
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")

    # 9. PIE CHARTS (ANALISIS KONTRIBUSI KUE)
    st.subheader(f"🍰 Analisis Kontribusi Proporsional ({pilihan_y})")
    kolom_pie1, kolom_pie2 = st.columns(2)

    with kolom_pie1:
        st.write("📍 Kontribusi Berdasarkan Wilayah (Region)")
        df_pie_reg = df.groupby("REGION", as_index=False)[pilihan_y].sum()
        df_pie_reg = df_pie_reg[df_pie_reg[pilihan_y] > 0]
        fig_pie_reg = px.pie(df_pie_reg, values=pilihan_y, names='REGION', color='REGION', color_discrete_map=peta_warna_neon, hole=0.4, template="plotly_dark")
        fig_pie_reg.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie_reg, use_container_width=True)

    with kolom_pie2:
        if pilihan_brand == "SEMUA BRAND" and "BRAND" in df.columns:
            st.write("🏷️ Kontribusi Berdasarkan Brand")
            df_pie_brand = df.groupby("BRAND", as_index=False)[pilihan_y].sum()
            df_pie_brand = df_pie_brand[df_pie_brand[pilihan_y] > 0]
            fig_pie_brand = px.pie(df_pie_brand, values=pilihan_y, names='BRAND', hole=0.4, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie_brand.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie_brand, use_container_width=True)
        else:
            st.info("💡 Pilih 'SEMUA BRAND' untuk melihat kontribusi kue antar Brand.")

    st.markdown("---")

    # 10. TABEL MATRIX DETAIL
    st.subheader("📋 Matrix Finansial Detail")
    if "BULAN" in df.columns and "REGION" in df.columns:
        pivot_df = df.pivot_table(index="BULAN", columns="REGION", values=pilihan_y, aggfunc="sum", margins=True, margins_name="TOTAL")
        st.dataframe(pivot_df.style.format("Rp {:,.0f}"), use_container_width=True)

else:
    st.error(f"🔴 File database utama '{NAMA_FILE_DATA}' tidak ditemukan di server GitHub bapak. Silakan periksa kembali penulisan nama file-nya.")
