import plotly.express as px
import streamlit as st

from dashboard_utils import (
    COLOR_MAP,
    DISPLAY_LABELS,
    STUNTING_ORDER,
    WASTING_ORDER,
    add_sidebar_filters,
    apply_chart_layout,
    bar_chart,
    format_percent,
    load_data,
    page_header,
    render_sidebar,
    risk_rate,
)


st.set_page_config(page_title="Status Gizi - SobatBalita", page_icon=":bar_chart:", layout="wide")

df = load_data()
render_sidebar("status")
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

left, right = st.columns(2)

with left:
    st.subheader("Kategori stunting")
    stunting_counts = filtered["stunting"].value_counts().reindex(STUNTING_ORDER, fill_value=0).reset_index()
    stunting_counts.columns = ["Status", "Jumlah"]
    stunting_counts["Persentase"] = stunting_counts["Jumlah"] / stunting_counts["Jumlah"].sum() * 100
    largest_stunting_category = stunting_counts.sort_values("Jumlah", ascending=False).iloc[0]
    stunted_count = int(stunting_counts.loc[stunting_counts["Status"].eq("Stunted"), "Jumlah"].iloc[0])
    severe_stunted_count = int(stunting_counts.loc[stunting_counts["Status"].eq("Severely Stunted"), "Jumlah"].iloc[0])
    fig = bar_chart(
        stunting_counts,
        x="Jumlah",
        y="Status",
        color="Status",
        text="Jumlah",
        title="Jumlah balita per kategori stunting",
        category_orders={"Status": STUNTING_ORDER},
        orientation="h",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"""
        <div class="note">
        Kategori stunting terbanyak adalah {largest_stunting_category['Status']} dengan
        {int(largest_stunting_category['Jumlah']):,} balita
        ({largest_stunting_category['Persentase']:.1f}%). Kelompok yang perlu perhatian terdiri dari
        {stunted_count:,} balita Stunted dan {severe_stunted_count:,} balita Severely Stunted.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.subheader("Kategori wasting")
    wasting_counts = filtered["wasting"].value_counts().reindex(WASTING_ORDER, fill_value=0).reset_index()
    wasting_counts.columns = ["Status", "Jumlah"]
    wasting_counts["Persentase"] = wasting_counts["Jumlah"] / wasting_counts["Jumlah"].sum() * 100
    largest_wasting_category = wasting_counts.sort_values("Jumlah", ascending=False).iloc[0]
    underweight_count = int(wasting_counts.loc[wasting_counts["Status"].eq("Underweight"), "Jumlah"].iloc[0])
    severe_underweight_count = int(wasting_counts.loc[wasting_counts["Status"].eq("Severely Underweight"), "Jumlah"].iloc[0])
    fig = bar_chart(
        wasting_counts,
        x="Jumlah",
        y="Status",
        color="Status",
        text="Jumlah",
        title="Jumlah balita per kategori wasting",
        category_orders={"Status": WASTING_ORDER},
        orientation="h",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"""
        <div class="note">
        Kategori wasting terbanyak adalah {largest_wasting_category['Status']} dengan
        {int(largest_wasting_category['Jumlah']):,} balita
        ({largest_wasting_category['Persentase']:.1f}%). Kelompok yang dihitung sebagai wasting terdiri dari
        {underweight_count:,} balita Underweight dan {severe_underweight_count:,} balita Severely Underweight.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Komposisi ringkas")
pie1, pie2 = st.columns(2)
with pie1:
    status_counts = filtered["stunting_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Jumlah"]
    status_counts["Persentase"] = status_counts["Jumlah"] / status_counts["Jumlah"].sum() * 100
    fig = px.pie(
        status_counts,
        names="Status",
        values="Jumlah",
        hole=0.55,
        color="Status",
        color_discrete_map=COLOR_MAP,
        title="Stunting vs non-stunting",
        labels=DISPLAY_LABELS,
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)
    st.markdown(
        f"""
        <div class="note">
        Komposisi ringkas menunjukkan {int(status_counts.loc[status_counts['Status'].eq('Stunting'), 'Jumlah'].sum()):,}
        balita masuk kelompok stunting dari total {len(filtered):,} data terpilih.
        </div>
        """,
        unsafe_allow_html=True,
    )

with pie2:
    wasting_binary = filtered.assign(
        status_wasting=filtered["risiko_wasting"].map({True: "Wasting", False: "Non-Wasting"})
    )
    wasting_binary_counts = wasting_binary["status_wasting"].value_counts().reset_index()
    wasting_binary_counts.columns = ["Status", "Jumlah"]
    wasting_binary_counts["Persentase"] = wasting_binary_counts["Jumlah"] / wasting_binary_counts["Jumlah"].sum() * 100
    fig = px.pie(
        wasting_binary_counts,
        names="Status",
        values="Jumlah",
        hole=0.55,
        color="Status",
        color_discrete_map={"Wasting": "#E76F51", "Non-Wasting": "#2A9D8F"},
        title="Wasting vs non-wasting",
        labels=DISPLAY_LABELS,
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)
    st.markdown(
        f"""
        <div class="note">
        Komposisi ringkas menunjukkan {int(wasting_binary_counts.loc[wasting_binary_counts['Status'].eq('Wasting'), 'Jumlah'].sum()):,}
        balita masuk kelompok wasting dari total {len(filtered):,} data terpilih.
        </div>
        """,
        unsafe_allow_html=True,
    )
