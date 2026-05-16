import plotly.express as px
import streamlit as st

from dashboard_utils import (
    AGE_GROUP_ORDER,
    COLOR_MAP,
    DISPLAY_LABELS,
    add_sidebar_filters,
    apply_chart_layout,
    bar_chart,
    format_percent,
    load_data,
    page_header,
    render_sidebar,
)


st.set_page_config(page_title="Demografi - SobatBalita", page_icon=":busts_in_silhouette:", layout="wide")

df = load_data()
render_sidebar("demografi")
filtered = add_sidebar_filters(df, "demografi")

page_header(
    "Analisis Demografi",
    "Bandingkan pola status gizi berdasarkan jenis kelamin dan kelompok umur agar perbedaan antar kelompok lebih mudah terlihat.",
)

if filtered.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih.")
    st.stop()

total_filtered = len(filtered)
gender_counts = filtered["jenis_kelamin"].value_counts().reset_index()
gender_counts.columns = ["Jenis kelamin", "Jumlah"]
gender_counts["Persentase"] = gender_counts["Jumlah"] / total_filtered * 100
dominant_gender = gender_counts.iloc[0]
if len(gender_counts) > 1:
    second_gender = gender_counts.iloc[1]
    gender_gap = int(dominant_gender["Jumlah"] - second_gender["Jumlah"])
    gender_explanation = (
        f"Dari {total_filtered:,} balita yang dianalisis, kelompok {dominant_gender['Jenis kelamin']} "
        f"menjadi yang paling banyak dengan {dominant_gender['Jumlah']:,} data "
        f"({dominant_gender['Persentase']:.1f}%). Kelompok {second_gender['Jenis kelamin']} berjumlah "
        f"{second_gender['Jumlah']:,} data ({second_gender['Persentase']:.1f}%), sehingga selisihnya "
        f"{gender_gap:,} data."
    )
else:
    gender_explanation = (
        f"Semua {total_filtered:,} data pada filter saat ini berasal dari kelompok "
        f"{dominant_gender['Jenis kelamin']}. Karena hanya ada satu jenis kelamin, grafik ini belum bisa "
        "digunakan untuk membandingkan laki-laki dan perempuan."
    )

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
    st.markdown(
        f"""
        <div class="note">
        {gender_explanation}
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.subheader("Kelompok umur")
    age_gender = (
        filtered.groupby(["kelompok_umur", "jenis_kelamin"], observed=False)
        .size()
        .reset_index(name="Jumlah")
    )
    age_gender = age_gender[age_gender["Jumlah"] > 0].copy()
    visible_age_groups = [group for group in AGE_GROUP_ORDER if group in age_gender["kelompok_umur"].astype(str).tolist()]
    age_total = (
        filtered.groupby("kelompok_umur", observed=False)
        .size()
        .reset_index(name="Jumlah")
    )
    age_total = age_total[age_total["Jumlah"] > 0].copy()
    dominant_age = age_total.sort_values("Jumlah", ascending=False).iloc[0]
    dominant_age_gender = age_gender.sort_values("Jumlah", ascending=False).iloc[0]
    fig = px.bar(
        age_gender,
        x="kelompok_umur",
        y="Jumlah",
        color="jenis_kelamin",
        barmode="group",
        text="Jumlah",
        color_discrete_map=COLOR_MAP,
        category_orders={"kelompok_umur": visible_age_groups},
        title="Jumlah balita berdasarkan umur dan jenis kelamin",
        labels=DISPLAY_LABELS,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)
    st.markdown(
        f"""
        <div class="note">
        Kelompok umur dengan data terbanyak adalah {dominant_age['kelompok_umur']}, yaitu
        {int(dominant_age['Jumlah']):,} balita ({dominant_age['Jumlah'] / total_filtered * 100:.1f}%).
        Kombinasi umur dan jenis kelamin yang paling dominan adalah {dominant_age_gender['kelompok_umur']}
        pada {dominant_age_gender['jenis_kelamin']}, dengan {int(dominant_age_gender['Jumlah']):,} balita.
        Kelompok umur tanpa data tidak ditampilkan agar grafik tetap fokus pada data yang tersedia.
        </div>
        """,
        unsafe_allow_html=True,
    )

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
highest_stunting = risk_by_gender.sort_values("Stunting (%)", ascending=False).iloc[0]
highest_wasting = risk_by_gender.sort_values("Wasting (%)", ascending=False).iloc[0]
if len(risk_by_gender) > 1:
    lowest_stunting = risk_by_gender.sort_values("Stunting (%)", ascending=True).iloc[0]
    lowest_wasting = risk_by_gender.sort_values("Wasting (%)", ascending=True).iloc[0]
    stunting_gap = highest_stunting["Stunting (%)"] - lowest_stunting["Stunting (%)"]
    wasting_gap = highest_wasting["Wasting (%)"] - lowest_wasting["Wasting (%)"]
    risk_explanation = (
        f"Risiko stunting tertinggi terdapat pada kelompok {highest_stunting['jenis_kelamin']} "
        f"sebesar {format_percent(highest_stunting['Stunting (%)'])}, lebih tinggi "
        f"{stunting_gap:.1f} poin persentase dibanding {lowest_stunting['jenis_kelamin']}. "
        f"Untuk wasting, kelompok tertinggi adalah {highest_wasting['jenis_kelamin']} "
        f"dengan {format_percent(highest_wasting['Wasting (%)'])}, selisih "
        f"{wasting_gap:.1f} poin persentase dibanding {lowest_wasting['jenis_kelamin']}."
    )
else:
    risk_explanation = (
        f"Pada filter saat ini hanya ada kelompok {highest_stunting['jenis_kelamin']}. "
        f"Persentase stuntingnya {format_percent(highest_stunting['Stunting (%)'])}, sedangkan "
        f"persentase wastingnya {format_percent(highest_stunting['Wasting (%)'])}. Perbandingan antar "
        "jenis kelamin belum dapat dihitung karena data hanya memuat satu kelompok."
    )

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
    labels=DISPLAY_LABELS,
)
fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
fig.update_yaxes(ticksuffix="%")
st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

st.markdown(
    f"""
    <div class="note">
    {risk_explanation}
    </div>
    """,
    unsafe_allow_html=True,
)
