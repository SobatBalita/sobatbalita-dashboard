import plotly.express as px
import streamlit as st

from dashboard_utils import (
    AGE_GROUP_ORDER,
    COLOR_MAP,
    add_sidebar_filters,
    apply_chart_layout,
    bar_chart,
    format_percent,
    load_data,
    page_header,
)


st.set_page_config(page_title="Demografi - SobatBalita", page_icon=":busts_in_silhouette:", layout="wide")

df = load_data()
filtered = add_sidebar_filters(df, "demografi")

page_header(
    "Analisis Demografi",
    "Bandingkan pola status gizi berdasarkan jenis kelamin dan kelompok umur agar perbedaan antar kelompok lebih mudah terlihat.",
)

if filtered.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih.")
    st.stop()

gender_counts = filtered["jenis_kelamin"].value_counts().reset_index()
gender_counts.columns = ["Jenis kelamin", "Jumlah"]

left, right = st.columns([0.85, 1.15])
with left:
    st.subheader("Distribusi jenis kelamin")
    fig = bar_chart(
        gender_counts,
        x="Jenis kelamin",
        y="Jumlah",
        color="Jenis kelamin",
        text="Jumlah",
        title="Jumlah data per jenis kelamin",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Kelompok umur")
    age_gender = (
        filtered.groupby(["kelompok_umur", "jenis_kelamin"], observed=False)
        .size()
        .reset_index(name="Jumlah")
    )
    fig = px.bar(
        age_gender,
        x="kelompok_umur",
        y="Jumlah",
        color="jenis_kelamin",
        barmode="group",
        text="Jumlah",
        color_discrete_map=COLOR_MAP,
        category_orders={"kelompok_umur": AGE_GROUP_ORDER},
        title="Jumlah balita berdasarkan umur dan jenis kelamin",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

st.subheader("Risiko gizi berdasarkan jenis kelamin")
risk_by_gender = (
    filtered.groupby("jenis_kelamin")
    .agg(
        jumlah=("jenis_kelamin", "size"),
        stunting_rate=("risiko_stunting", "mean"),
        wasting_rate=("risiko_wasting", "mean"),
    )
    .reset_index()
)
risk_by_gender["Stunting (%)"] = risk_by_gender["stunting_rate"] * 100
risk_by_gender["Wasting (%)"] = risk_by_gender["wasting_rate"] * 100

fig = px.bar(
    risk_by_gender.melt(
        id_vars="jenis_kelamin",
        value_vars=["Stunting (%)", "Wasting (%)"],
        var_name="Indikator",
        value_name="Persentase",
    ),
    x="jenis_kelamin",
    y="Persentase",
    color="Indikator",
    barmode="group",
    text="Persentase",
    color_discrete_sequence=["#E76F51", "#F4A261"],
    title="Persentase risiko stunting dan wasting",
)
fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
fig.update_yaxes(ticksuffix="%")
st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

highest = risk_by_gender.sort_values("Stunting (%)", ascending=False).iloc[0]
st.markdown(
    f"""
    <div class="note">
    Pada filter saat ini, kelompok {highest['jenis_kelamin']} memiliki persentase stunting
    tertinggi yaitu {format_percent(highest['Stunting (%)'])}. Gunakan halaman Status Gizi
    untuk melihat kategori detailnya.
    </div>
    """,
    unsafe_allow_html=True,
)
