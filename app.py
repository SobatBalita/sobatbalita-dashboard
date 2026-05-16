import plotly.express as px
import streamlit as st
import pandas as pd

from dashboard_utils import (
    AGE_GROUP_ORDER,
    COLOR_MAP,
    DISPLAY_LABELS,
    apply_chart_layout,
    load_data,
    page_header,
    render_sidebar,
    risk_rate,
)


st.set_page_config(
    page_title="SobatBalita Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

df = load_data()
render_sidebar("home")

page_header(
    "SobatBalita Dashboard",
    "Dashboard interaktif untuk membaca kondisi stunting dan wasting balita dari data antropometri. "
    "Setiap halaman dirancang agar pengguna umum bisa langsung memahami angka, grafik, dan maknanya.",
)

total_children = len(df)
stunting_total = int(df["risiko_stunting"].sum())
wasting_total = int(df["risiko_wasting"].sum())
avg_age = df["umur_bulan"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total data balita", f"{total_children:,}")
col2.metric("Balita stunting", f"{stunting_total:,}", f"{risk_rate(df['risiko_stunting']):.1f}%")
col3.metric("Balita wasting", f"{wasting_total:,}", f"{risk_rate(df['risiko_wasting']):.1f}%")
col4.metric("Rata-rata umur", f"{avg_age:.1f} bulan")

st.markdown(
    """
    <div class="note">
    Mulai dari halaman Overview untuk ringkasan cepat, lalu gunakan halaman Status Gizi,
    Antropometri, Demografi, dan Insight untuk menggali penyebab pola yang terlihat.
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.15, 0.85])

with left:
    st.subheader("Kelompok umur yang perlu diperhatikan")
    age_summary = (
        df.groupby("kelompok_umur", observed=False)
        .agg(
            jumlah=("umur_bulan", "size"),
            stunting_rate=("risiko_stunting", "mean"),
            wasting_rate=("risiko_wasting", "mean"),
        )
        .reset_index()
    )
    age_summary["stunting_rate"] *= 100
    age_summary["wasting_rate"] *= 100
    age_summary = age_summary[age_summary["jumlah"] > 0].copy()
    visible_age_groups = [group for group in AGE_GROUP_ORDER if group in age_summary["kelompok_umur"].astype(str).tolist()]
    age_risk_long = age_summary.melt(
        id_vars=["kelompok_umur", "jumlah"],
        value_vars=["stunting_rate", "wasting_rate"],
        var_name="Indikator",
        value_name="Persentase",
    )
    age_risk_long["Indikator"] = age_risk_long["Indikator"].map(
        {"stunting_rate": "Stunting", "wasting_rate": "Wasting"}
    )

    fig = px.bar(
        age_risk_long,
        x="kelompok_umur",
        y="Persentase",
        color="Indikator",
        barmode="group",
        text="Persentase",
        category_orders={"kelompok_umur": visible_age_groups},
        color_discrete_sequence=["#E76F51", "#F4A261"],
        title="Persentase stunting dan wasting berdasarkan umur",
        labels=DISPLAY_LABELS,
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    fig.update_yaxes(ticksuffix="%")
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

    highest_stunting = age_summary.sort_values("stunting_rate", ascending=False).iloc[0]
    highest_wasting = age_summary.sort_values("wasting_rate", ascending=False).iloc[0]
    st.markdown(
        f"""
        <div class="note">
        Kelompok umur {highest_stunting['kelompok_umur']} memiliki persentase
        stunting tertinggi ({highest_stunting['stunting_rate']:.1f}%), sedangkan wasting tertinggi
        berada pada kelompok umur {highest_wasting['kelompok_umur']} ({highest_wasting['wasting_rate']:.1f}%).
        Kelompok umur yang tidak memiliki data tidak ditampilkan agar grafik lebih mudah dibaca.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.subheader("Status utama")
    status_summary = pd.DataFrame(
        [
            {
                "Indikator": "Stunting",
                "Status": "Perlu perhatian",
                "Jumlah": stunting_total,
                "Persentase": risk_rate(df["risiko_stunting"]),
            },
            {
                "Indikator": "Stunting",
                "Status": "Tidak terindikasi",
                "Jumlah": total_children - stunting_total,
                "Persentase": 100 - risk_rate(df["risiko_stunting"]),
            },
            {
                "Indikator": "Wasting",
                "Status": "Perlu perhatian",
                "Jumlah": wasting_total,
                "Persentase": risk_rate(df["risiko_wasting"]),
            },
            {
                "Indikator": "Wasting",
                "Status": "Tidak terindikasi",
                "Jumlah": total_children - wasting_total,
                "Persentase": 100 - risk_rate(df["risiko_wasting"]),
            },
        ]
    )
    status_summary["Label"] = status_summary["Persentase"].map(lambda value: f"{value:.1f}%")
    fig = px.bar(
        status_summary,
        x="Indikator",
        y="Persentase",
        color="Status",
        text="Label",
        barmode="stack",
        color_discrete_map={"Perlu perhatian": "#E76F51", "Tidak terindikasi": "#2A9D8F"},
        title="Komposisi status stunting dan wasting",
        labels=DISPLAY_LABELS,
    )
    fig.update_traces(
        textposition="inside",
        hovertemplate="<b>%{x}</b><br>%{customdata[0]}<br>Jumlah: %{customdata[1]:,}<br>Persentase: %{y:.1f}%<extra></extra>",
        customdata=status_summary[["Status", "Jumlah"]],
    )
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

    st.markdown(
        f"""
        <div class="note">
        Pada data ini, {risk_rate(df['risiko_stunting']):.1f}% balita terindikasi stunting
        dan {risk_rate(df['risiko_wasting']):.1f}% terindikasi wasting. Keduanya ditampilkan
        sebagai status utama karena mewakili dua sisi masalah gizi: tinggi badan menurut umur
        dan berat badan menurut tinggi badan.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Istilah penting")
st.markdown(
    """
    <div class="note">
    <ul>
        <li><strong>Stunting</strong>: kondisi ketika tinggi badan anak lebih rendah dari standar usianya.</li>
        <li><strong>Wasting</strong>: kondisi ketika berat badan anak terlalu rendah dibanding tinggi badannya.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Cara membaca dashboard")
guide1, guide2, guide3 = st.columns(3)
guide1.info("Gunakan filter di sidebar pada tiap halaman untuk memilih umur dan jenis kelamin.")
guide2.info("Arahkan kursor ke grafik untuk melihat angka detail tanpa membuka tabel.")
guide3.info("Perhatikan kotak insight untuk ringkasan makna dari grafik yang sedang tampil.")
