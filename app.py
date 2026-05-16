import plotly.express as px
import streamlit as st

from dashboard_utils import (
    AGE_GROUP_ORDER,
    COLOR_MAP,
    apply_chart_layout,
    load_data,
    page_header,
    risk_rate,
)


st.set_page_config(
    page_title="SobatBalita Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

df = load_data()

page_header(
    "SobatBalita Dashboard",
    "Dashboard interaktif untuk membaca kondisi stunting dan wasting balita dari data antropometri. "
    "Setiap halaman dirancang agar pengguna umum bisa langsung memahami angka, grafik, dan maknanya.",
)

st.sidebar.success("Pilih halaman analisis dari menu di atas.")

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
    st.subheader("Peta cepat kelompok umur")
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

    fig = px.bar(
        age_summary,
        x="kelompok_umur",
        y="jumlah",
        color="kelompok_umur",
        text="jumlah",
        category_orders={"kelompok_umur": AGE_GROUP_ORDER},
        color_discrete_sequence=["#4C78A8", "#72B7B2", "#E9C46A", "#F4A261", "#E76F51"],
        title="Jumlah data berdasarkan umur",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

with right:
    st.subheader("Status utama")
    status_summary = df["stunting_status"].value_counts().reset_index()
    status_summary.columns = ["status", "jumlah"]
    fig = px.pie(
        status_summary,
        names="status",
        values="jumlah",
        hole=0.58,
        color="status",
        color_discrete_map=COLOR_MAP,
        title="Komposisi stunting",
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

st.subheader("Cara membaca dashboard")
guide1, guide2, guide3 = st.columns(3)
guide1.info("Gunakan filter di sidebar pada tiap halaman untuk memilih umur dan jenis kelamin.")
guide2.info("Arahkan kursor ke grafik untuk melihat angka detail tanpa membuka tabel.")
guide3.info("Perhatikan kotak insight untuk ringkasan makna dari grafik yang sedang tampil.")
