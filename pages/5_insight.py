import plotly.express as px
import streamlit as st

from dashboard_utils import (
    AGE_GROUP_ORDER,
    DISPLAY_LABELS,
    add_sidebar_filters,
    apply_chart_layout,
    format_percent,
    load_data,
    page_header,
    render_sidebar,
    risk_rate,
)


st.set_page_config(page_title="Insight - SobatBalita", page_icon=":bulb:", layout="wide")

df = load_data()
render_sidebar("insight")
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
avg_height_stunting = filtered.loc[filtered["stunting_status"].eq("Stunting"), "tinggi_badan_cm"].mean()
avg_height_non_stunting = filtered.loc[filtered["stunting_status"].eq("Non-Stunting"), "tinggi_badan_cm"].mean()
avg_weight_stunting = filtered.loc[filtered["stunting_status"].eq("Stunting"), "berat_badan_kg"].mean()
avg_weight_non_stunting = filtered.loc[filtered["stunting_status"].eq("Non-Stunting"), "berat_badan_kg"].mean()
has_both_stunting_groups = filtered["stunting_status"].nunique() >= 2
height_gap = avg_height_non_stunting - avg_height_stunting if has_both_stunting_groups else 0
weight_gap = avg_weight_non_stunting - avg_weight_stunting if has_both_stunting_groups else 0
age_summary = (
    filtered.groupby("kelompok_umur", observed=False)
    .agg(
        jumlah=("umur_bulan", "size"),
        stunting=("risiko_stunting", "mean"),
        wasting=("risiko_wasting", "mean"),
    )
    .reset_index()
)
age_summary = age_summary[age_summary["jumlah"] > 0].copy()
age_summary["Stunting (%)"] = age_summary["stunting"] * 100
age_summary["Wasting (%)"] = age_summary["wasting"] * 100
visible_age_groups = [group for group in AGE_GROUP_ORDER if group in age_summary["kelompok_umur"].astype(str).tolist()]
highest_stunting_age = age_summary.sort_values("Stunting (%)", ascending=False).iloc[0]
highest_wasting_age = age_summary.sort_values("Wasting (%)", ascending=False).iloc[0]

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
    f"Stunting tertinggi berada pada kelompok umur {highest_stunting_age['kelompok_umur']} "
    f"({highest_stunting_age['Stunting (%)']:.1f}%)."
)

st.subheader("Jawaban pertanyaan bisnis")
answer1, answer2, answer3 = st.columns(3)
answer1.info(
    "Pola umur, tinggi, dan berat dapat dibaca dari halaman Antropometri. "
    "Semakin rendah posisi anak pada grafik umur-tinggi atau tinggi-berat, semakin perlu diperhatikan status gizinya."
)
if has_both_stunting_groups:
    answer2.success(
        f"Rata-rata tinggi kelompok non-stunting lebih tinggi sekitar {height_gap:.1f} cm dibanding kelompok stunting. "
        f"Selisih berat badannya sekitar {weight_gap:.1f} kg pada data terpilih."
    )
else:
    answer2.success(
        "Filter saat ini hanya memuat satu status stunting, sehingga perbandingan langsung antara stunting "
        "dan non-stunting belum dapat dihitung."
    )
answer3.warning(
    f"Rentang umur yang paling perlu diperhatikan untuk stunting adalah {highest_stunting_age['kelompok_umur']} "
    f"({highest_stunting_age['Stunting (%)']:.1f}%). Untuk wasting, kelompok tertinggi adalah "
    f"{highest_wasting_age['kelompok_umur']} ({highest_wasting_age['Wasting (%)']:.1f}%)."
)

st.subheader("Perbandingan indikator menurut umur")
age_risk = age_summary.copy()

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
    category_orders={"kelompok_umur": visible_age_groups},
    color_discrete_sequence=["#E76F51", "#F4A261"],
    title="Perubahan persentase risiko pada tiap kelompok umur",
    labels=DISPLAY_LABELS,
)
fig.update_yaxes(ticksuffix="%")
st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

st.markdown(
    f"""
    <div class="note">
    Grafik umur menunjukkan bahwa stunting tertinggi berada pada {highest_stunting_age['kelompok_umur']}
    sebesar {highest_stunting_age['Stunting (%)']:.1f}%, sedangkan wasting tertinggi berada pada
    {highest_wasting_age['kelompok_umur']} sebesar {highest_wasting_age['Wasting (%)']:.1f}%.
    Kelompok umur tanpa data tidak ditampilkan agar kesimpulan mengikuti data yang tersedia.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Rata-rata kondisi fisik menurut umur")
age_physical = (
    filtered.groupby(["umur_bulan", "stunting_status"], observed=False)
    .agg(
        tinggi_badan_cm=("tinggi_badan_cm", "mean"),
        berat_badan_kg=("berat_badan_kg", "mean"),
    )
    .reset_index()
)
metric_choice = st.radio(
    "Pilih indikator fisik",
    ["Tinggi badan", "Berat badan"],
    horizontal=True,
)
if metric_choice == "Tinggi badan":
    y_col = "tinggi_badan_cm"
    chart_title = "Rata-rata tinggi badan berdasarkan umur dan status stunting"
    y_title = "Rata-rata tinggi badan (cm)"
else:
    y_col = "berat_badan_kg"
    chart_title = "Rata-rata berat badan berdasarkan umur dan status stunting"
    y_title = "Rata-rata berat badan (kg)"

fig = px.line(
    age_physical,
    x="umur_bulan",
    y=y_col,
    color="stunting_status",
    markers=True,
    color_discrete_map={"Stunting": "#E76F51", "Non-Stunting": "#2A9D8F"},
    title=chart_title,
    labels=DISPLAY_LABELS,
)
fig.update_xaxes(title_text="Umur balita (bulan)")
fig.update_yaxes(title_text=y_title)
st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

age_physical_gap = age_physical.pivot(index="umur_bulan", columns="stunting_status", values=y_col)
if {"Stunting", "Non-Stunting"}.issubset(age_physical_gap.columns):
    age_physical_gap = age_physical_gap.dropna(subset=["Stunting", "Non-Stunting"])
    if not age_physical_gap.empty:
        age_physical_gap["selisih"] = age_physical_gap["Non-Stunting"] - age_physical_gap["Stunting"]
        largest_gap_age = int(age_physical_gap["selisih"].idxmax())
        largest_gap_value = age_physical_gap.loc[largest_gap_age, "selisih"]
        physical_explanation = (
            f"Pada indikator {metric_choice.lower()}, selisih rata-rata terbesar antara kelompok non-stunting "
            f"dan stunting terlihat pada umur {largest_gap_age} bulan, yaitu sekitar {largest_gap_value:.1f} "
            f"{'cm' if metric_choice == 'Tinggi badan' else 'kg'}."
        )
    else:
        physical_explanation = (
            f"Pada filter saat ini, grafik {metric_choice.lower()} belum memiliki umur yang berisi kelompok "
            "stunting dan non-stunting sekaligus, sehingga selisih rata-rata per umur belum bisa dihitung."
        )
else:
    physical_explanation = (
        f"Pada filter saat ini, grafik {metric_choice.lower()} hanya memuat satu status stunting, sehingga "
        "perbandingan rata-rata antara stunting dan non-stunting belum bisa dihitung."
    )

st.markdown(
    f"""
    <div class="note">
    {physical_explanation}
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Kesimpulan praktis")
st.markdown(
    f"""
    <div class="note">
    Kesimpulan praktisnya: dari {total:,} data terpilih, risiko stunting adalah
    {format_percent(stunting_rate)} dan risiko wasting adalah {format_percent(wasting_rate)}.
    Kelompok umur prioritas untuk stunting adalah {highest_stunting_age['kelompok_umur']}, sedangkan
    kelompok umur prioritas untuk wasting adalah {highest_wasting_age['kelompok_umur']}.
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
