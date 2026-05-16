import plotly.express as px
import streamlit as st

from dashboard_utils import (
    AGE_GROUP_ORDER,
    add_sidebar_filters,
    apply_chart_layout,
    format_percent,
    load_data,
    page_header,
    risk_rate,
)


st.set_page_config(page_title="Insight - SobatBalita", page_icon=":bulb:", layout="wide")

df = load_data()
filtered = add_sidebar_filters(df, "insight")

page_header(
    "Insight dan Kesimpulan",
    "Halaman ini merangkum temuan utama dari data terpilih dalam bahasa yang mudah dibaca oleh pengguna umum.",
)

if filtered.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih.")
    st.stop()

total = len(filtered)
stunting_rate = risk_rate(filtered["risiko_stunting"])
wasting_rate = risk_rate(filtered["risiko_wasting"])
highest_age = (
    filtered.groupby("kelompok_umur", observed=False)["risiko_stunting"]
    .mean()
    .reindex(AGE_GROUP_ORDER)
    .fillna(0)
    .idxmax()
)

col1, col2, col3 = st.columns(3)
col1.metric("Data dianalisis", f"{total:,}")
col2.metric("Risiko stunting", format_percent(stunting_rate))
col3.metric("Risiko wasting", format_percent(wasting_rate))

st.subheader("Temuan utama")
insight1, insight2, insight3 = st.columns(3)
insight1.success(
    f"{format_percent(stunting_rate)} data terpilih masuk kelompok stunting. "
    "Angka ini dihitung dari status Stunting dan Non-Stunting."
)
insight2.warning(
    f"{format_percent(wasting_rate)} data terpilih masuk kelompok wasting. "
    "Kategori yang dihitung adalah Underweight dan Severely Underweight."
)
insight3.info(
    f"Kelompok umur dengan persentase stunting tertinggi pada filter ini adalah {highest_age}."
)

st.subheader("Perbandingan indikator menurut umur")
age_risk = (
    filtered.groupby("kelompok_umur", observed=False)
    .agg(
        stunting=("risiko_stunting", "mean"),
        wasting=("risiko_wasting", "mean"),
    )
    .reindex(AGE_GROUP_ORDER)
    .reset_index()
)
age_risk["Stunting (%)"] = age_risk["stunting"] * 100
age_risk["Wasting (%)"] = age_risk["wasting"] * 100

fig = px.line(
    age_risk.melt(
        id_vars="kelompok_umur",
        value_vars=["Stunting (%)", "Wasting (%)"],
        var_name="Indikator",
        value_name="Persentase",
    ),
    x="kelompok_umur",
    y="Persentase",
    color="Indikator",
    markers=True,
    category_orders={"kelompok_umur": AGE_GROUP_ORDER},
    color_discrete_sequence=["#E76F51", "#F4A261"],
    title="Perubahan persentase risiko pada tiap kelompok umur",
)
fig.update_yaxes(ticksuffix="%")
st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

st.subheader("Kesimpulan praktis")
st.markdown(
    """
    <div class="note">
    Dashboard ini menunjukkan bahwa status gizi balita perlu dibaca dari beberapa sisi:
    umur, tinggi badan, berat badan, jenis kelamin, dan kategori status gizi. Kombinasi
    filter dan grafik membantu pengguna melihat kelompok mana yang memerlukan perhatian
    lebih lanjut tanpa harus membaca tabel mentah dari awal.
    </div>
    """,
    unsafe_allow_html=True,
)

st.dataframe(
    age_risk[["kelompok_umur", "Stunting (%)", "Wasting (%)"]].style.format(
        {"Stunting (%)": "{:.1f}%", "Wasting (%)": "{:.1f}%"}
    ),
    use_container_width=True,
    hide_index=True,
)
