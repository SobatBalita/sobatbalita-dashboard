import streamlit as st

from dashboard_utils import (
    add_sidebar_filters,
    format_percent,
    load_data,
    page_header,
    risk_rate,
)


st.set_page_config(page_title="Overview - SobatBalita", page_icon=":bar_chart:", layout="wide")

df = load_data()
filtered = add_sidebar_filters(df, "overview")

page_header(
    "Overview Dataset",
    "Ringkasan cepat untuk memahami skala data, proporsi risiko, dan isi dataset sebelum masuk ke analisis yang lebih rinci.",
)

if filtered.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih. Coba longgarkan rentang umur atau jenis kelamin.")
    st.stop()

total_data = len(filtered)
stunting_count = int(filtered["risiko_stunting"].sum())
wasting_count = int(filtered["risiko_wasting"].sum())
avg_age = filtered["umur_bulan"].mean()
avg_height = filtered["tinggi_badan_cm"].mean()
avg_weight = filtered["berat_badan_kg"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Data terpilih", f"{total_data:,}")
col2.metric("Stunting", f"{stunting_count:,}", format_percent(risk_rate(filtered["risiko_stunting"])))
col3.metric("Wasting", f"{wasting_count:,}", format_percent(risk_rate(filtered["risiko_wasting"])))
col4.metric("Rata-rata umur", f"{avg_age:.1f} bulan")

col5, col6 = st.columns(2)
col5.metric("Rata-rata tinggi", f"{avg_height:.1f} cm")
col6.metric("Rata-rata berat", f"{avg_weight:.1f} kg")

st.markdown(
    """
    <div class="note">
    Angka pada kartu di atas ikut berubah sesuai filter. Gunakan ini sebagai titik awal
    untuk membandingkan kelompok umur atau jenis kelamin tertentu.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Pratinjau data")
st.dataframe(
    filtered[
        [
            "jenis_kelamin",
            "umur_bulan",
            "tinggi_badan_cm",
            "berat_badan_kg",
            "stunting",
            "wasting",
            "stunting_status",
        ]
    ].head(200),
    use_container_width=True,
    hide_index=True,
)

left, right = st.columns(2)
with left:
    st.subheader("Informasi kolom")
    info_df = filtered.dtypes.astype(str).reset_index()
    info_df.columns = ["Kolom", "Tipe data"]
    st.dataframe(info_df, use_container_width=True, hide_index=True)

with right:
    st.subheader("Statistik angka")
    st.dataframe(
        filtered[["umur_bulan", "tinggi_badan_cm", "berat_badan_kg"]].describe().T,
        use_container_width=True,
    )
