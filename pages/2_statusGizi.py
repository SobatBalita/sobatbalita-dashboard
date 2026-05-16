import plotly.express as px
import streamlit as st

from dashboard_utils import (
    COLOR_MAP,
    STUNTING_ORDER,
    WASTING_ORDER,
    add_sidebar_filters,
    apply_chart_layout,
    bar_chart,
    format_percent,
    load_data,
    page_header,
    risk_rate,
)


st.set_page_config(page_title="Status Gizi - SobatBalita", page_icon=":bar_chart:", layout="wide")

df = load_data()
filtered = add_sidebar_filters(df, "status")

page_header(
    "Distribusi Status Gizi",
    "Lihat seberapa besar proporsi balita pada kategori stunting dan wasting. Grafik dibuat ringkas agar perbedaan kategori mudah dibaca.",
)

if filtered.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih.")
    st.stop()

stunting_rate = risk_rate(filtered["risiko_stunting"])
wasting_rate = risk_rate(filtered["risiko_wasting"])

col1, col2, col3 = st.columns(3)
col1.metric("Data dianalisis", f"{len(filtered):,}")
col2.metric("Persentase stunting", format_percent(stunting_rate))
col3.metric("Persentase wasting", format_percent(wasting_rate))

left, right = st.columns(2)

with left:
    st.subheader("Kategori stunting")
    stunting_counts = filtered["stunting"].value_counts().reindex(STUNTING_ORDER, fill_value=0).reset_index()
    stunting_counts.columns = ["Status", "Jumlah"]
    stunting_counts["Persentase"] = stunting_counts["Jumlah"] / stunting_counts["Jumlah"].sum() * 100
    fig = bar_chart(
        stunting_counts,
        x="Status",
        y="Jumlah",
        color="Status",
        text="Jumlah",
        title="Jumlah balita per kategori stunting",
        category_orders={"Status": STUNTING_ORDER},
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Kategori wasting")
    wasting_counts = filtered["wasting"].value_counts().reindex(WASTING_ORDER, fill_value=0).reset_index()
    wasting_counts.columns = ["Status", "Jumlah"]
    wasting_counts["Persentase"] = wasting_counts["Jumlah"] / wasting_counts["Jumlah"].sum() * 100
    fig = bar_chart(
        wasting_counts,
        x="Status",
        y="Jumlah",
        color="Status",
        text="Jumlah",
        title="Jumlah balita per kategori wasting",
        category_orders={"Status": WASTING_ORDER},
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown(
    f"""
    <div class="note">
    Pada data terpilih, {format_percent(stunting_rate)} balita berada pada kelompok stunting,
    sedangkan {format_percent(wasting_rate)} masuk kelompok wasting. Angka ini membantu
    memprioritaskan kelompok yang perlu ditelaah lebih dalam pada halaman Antropometri.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Komposisi ringkas")
pie1, pie2 = st.columns(2)
with pie1:
    status_counts = filtered["stunting_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Jumlah"]
    fig = px.pie(
        status_counts,
        names="Status",
        values="Jumlah",
        hole=0.55,
        color="Status",
        color_discrete_map=COLOR_MAP,
        title="Stunting vs non-stunting",
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

with pie2:
    wasting_binary = filtered.assign(
        status_wasting=filtered["risiko_wasting"].map({True: "Wasting", False: "Non-Wasting"})
    )
    wasting_binary_counts = wasting_binary["status_wasting"].value_counts().reset_index()
    wasting_binary_counts.columns = ["Status", "Jumlah"]
    fig = px.pie(
        wasting_binary_counts,
        names="Status",
        values="Jumlah",
        hole=0.55,
        color="Status",
        color_discrete_map={"Wasting": "#E76F51", "Non-Wasting": "#2A9D8F"},
        title="Wasting vs non-wasting",
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)
