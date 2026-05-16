import plotly.express as px
import streamlit as st

from dashboard_utils import (
    COLOR_MAP,
    add_sidebar_filters,
    apply_chart_layout,
    format_percent,
    load_data,
    page_header,
    risk_rate,
)


st.set_page_config(page_title="Antropometri - SobatBalita", page_icon=":chart_with_upwards_trend:", layout="wide")

df = load_data()
filtered = add_sidebar_filters(df, "antropometri")

page_header(
    "Analisis Antropometri",
    "Telusuri hubungan umur, tinggi badan, dan berat badan terhadap status gizi balita. Setiap titik pada grafik mewakili satu data balita.",
)

if filtered.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Data terpilih", f"{len(filtered):,}")
col2.metric("Rata-rata tinggi", f"{filtered['tinggi_badan_cm'].mean():.1f} cm")
col3.metric("Rata-rata berat", f"{filtered['berat_badan_kg'].mean():.1f} kg")
col4.metric("Stunting", format_percent(risk_rate(filtered["risiko_stunting"])))

st.subheader("Hubungan tinggi dan berat badan")
fig = px.scatter(
    filtered,
    x="tinggi_badan_cm",
    y="berat_badan_kg",
    color="stunting_status",
    opacity=0.62,
    hover_data={
        "jenis_kelamin": True,
        "umur_bulan": True,
        "tinggi_badan_cm": ":.1f",
        "berat_badan_kg": ":.1f",
        "stunting": True,
        "stunting_status": False,
    },
    color_discrete_map=COLOR_MAP,
    title="Sebaran tinggi dan berat berdasarkan status stunting",
)
fig.update_traces(marker=dict(size=7, line=dict(width=0)))
st.plotly_chart(apply_chart_layout(fig, height=520), use_container_width=True)

st.markdown(
    """
    <div class="note">
    Gunakan hover pada titik data untuk melihat umur, jenis kelamin, tinggi, berat, dan kategori gizi.
    Pola titik yang berada lebih rendah pada tinggi badan biasanya perlu dibaca bersama umur balita.
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2)

with left:
    st.subheader("Distribusi umur")
    fig = px.histogram(
        filtered,
        x="umur_bulan",
        nbins=24,
        color="stunting_status",
        color_discrete_map=COLOR_MAP,
        title="Jumlah balita berdasarkan umur",
    )
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

with right:
    st.subheader("Tinggi badan per status")
    fig = px.box(
        filtered,
        x="stunting",
        y="tinggi_badan_cm",
        color="stunting",
        points=False,
        color_discrete_map=COLOR_MAP,
        title="Perbandingan tinggi badan antar kategori stunting",
    )
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

st.subheader("Tabel data yang sesuai filter")
st.dataframe(
    filtered.sort_values(["risiko_stunting", "umur_bulan"], ascending=[False, True])[
        [
            "jenis_kelamin",
            "umur_bulan",
            "tinggi_badan_cm",
            "berat_badan_kg",
            "stunting",
            "wasting",
            "stunting_status",
        ]
    ].head(300),
    use_container_width=True,
    hide_index=True,
)
