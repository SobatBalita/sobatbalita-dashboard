import plotly.express as px
import streamlit as st

from dashboard_utils import (
    COLOR_MAP,
    DISPLAY_LABELS,
    add_sidebar_filters,
    apply_chart_layout,
    format_percent,
    load_data,
    page_header,
    readable_table,
    render_sidebar,
    risk_rate,
)


st.set_page_config(page_title="Antropometri - SobatBalita", page_icon=":chart_with_upwards_trend:", layout="wide")

df = load_data()
render_sidebar("antropometri")
filtered = add_sidebar_filters(df, "antropometri")

page_header(
    "Analisis Antropometri",
    "Telusuri hubungan umur, tinggi badan, dan berat badan terhadap status gizi balita. Setiap titik pada grafik mewakili satu data balita.",
)

if filtered.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih.")
    st.stop()

total_filtered = len(filtered)
stunting_count = int(filtered["risiko_stunting"].sum())
wasting_count = int(filtered["risiko_wasting"].sum())
non_stunting_count = total_filtered - stunting_count
non_wasting_count = total_filtered - wasting_count
avg_height_stunting = filtered.loc[filtered["risiko_stunting"], "tinggi_badan_cm"].mean()
avg_height_non_stunting = filtered.loc[~filtered["risiko_stunting"], "tinggi_badan_cm"].mean()
avg_weight_wasting = filtered.loc[filtered["risiko_wasting"], "berat_badan_kg"].mean()
avg_weight_non_wasting = filtered.loc[~filtered["risiko_wasting"], "berat_badan_kg"].mean()
median_height_stunting = filtered.loc[filtered["risiko_stunting"], "tinggi_badan_cm"].median()
median_height_non_stunting = filtered.loc[~filtered["risiko_stunting"], "tinggi_badan_cm"].median()
median_weight_stunting = filtered.loc[filtered["risiko_stunting"], "berat_badan_kg"].median()
median_weight_non_stunting = filtered.loc[~filtered["risiko_stunting"], "berat_badan_kg"].median()
most_common_age = filtered["umur_bulan"].value_counts().idxmax()
most_common_age_count = int(filtered["umur_bulan"].value_counts().max())
most_common_age_rate = most_common_age_count / total_filtered * 100
if stunting_count > 0 and non_stunting_count > 0:
    height_scatter_explanation = (
        f"Dari {total_filtered:,} balita yang dianalisis, terdapat {stunting_count:,} balita "
        f"({format_percent(risk_rate(filtered['risiko_stunting']))}) yang masuk kelompok stunting. "
        f"Rata-rata tinggi balita stunting adalah {avg_height_stunting:.1f} cm, sedangkan kelompok "
        f"non-stunting {avg_height_non_stunting:.1f} cm. Selisih sekitar "
        f"{(avg_height_non_stunting - avg_height_stunting):.1f} cm ini menunjukkan perbedaan pertumbuhan "
        "tinggi badan yang cukup terlihat pada data terpilih."
    )
    height_box_explanation = (
        f"Median tinggi badan kelompok stunting adalah {median_height_stunting:.1f} cm, sedangkan median kelompok "
        f"non-stunting adalah {median_height_non_stunting:.1f} cm. Selisih median sekitar "
        f"{(median_height_non_stunting - median_height_stunting):.1f} cm memperkuat bahwa kelompok stunting "
        "memiliki sebaran tinggi badan yang lebih rendah pada data terpilih."
    )
    weight_box_explanation = (
        f"Median berat badan kelompok stunting adalah {median_weight_stunting:.1f} kg, sedangkan median kelompok "
        f"non-stunting adalah {median_weight_non_stunting:.1f} kg. Selisih median sekitar "
        f"{(median_weight_non_stunting - median_weight_stunting):.1f} kg menunjukkan bahwa perbedaan status tinggi badan "
        "juga diikuti perbedaan berat badan pada data yang sedang dianalisis."
    )
else:
    available_status = "stunting" if stunting_count > 0 else "non-stunting"
    height_scatter_explanation = (
        f"Filter saat ini hanya memuat kelompok {available_status}, sehingga perbandingan rata-rata tinggi badan "
        "antara stunting dan non-stunting belum dapat dihitung. Grafik tetap menunjukkan sebaran tinggi badan "
        f"dari {total_filtered:,} balita yang sedang dipilih."
    )
    height_box_explanation = (
        f"Filter saat ini hanya memuat kelompok {available_status}, sehingga boxplot menampilkan sebaran tinggi badan "
        "untuk satu status saja dan belum dapat digunakan untuk membandingkan dua kelompok."
    )
    weight_box_explanation = (
        f"Filter saat ini hanya memuat kelompok {available_status}, sehingga boxplot menampilkan sebaran berat badan "
        "untuk satu status saja dan belum dapat digunakan untuk membandingkan dua kelompok."
    )

if wasting_count > 0 and non_wasting_count > 0:
    wasting_scatter_explanation = (
        f"Pada grafik ini terdapat {wasting_count:,} balita ({format_percent(risk_rate(filtered['risiko_wasting']))}) "
        f"yang masuk kelompok wasting dan {non_wasting_count:,} balita yang tidak terindikasi wasting. "
        f"Rata-rata berat badan kelompok wasting adalah {avg_weight_wasting:.1f} kg, sedangkan kelompok "
        f"non-wasting {avg_weight_non_wasting:.1f} kg. Selisih sekitar "
        f"{(avg_weight_non_wasting - avg_weight_wasting):.1f} kg menggambarkan adanya ketimpangan berat badan "
        "pada sebagian balita terhadap tinggi badannya."
    )
else:
    available_wasting_status = "wasting" if wasting_count > 0 else "non-wasting"
    wasting_scatter_explanation = (
        f"Filter saat ini hanya memuat kelompok {available_wasting_status}, sehingga perbandingan rata-rata berat badan "
        "antara wasting dan non-wasting belum dapat dihitung. Grafik tetap memperlihatkan posisi berat badan "
        "terhadap tinggi badan pada data yang sedang dipilih."
    )

col1, col2, col3, col4 = st.columns(4)
col1.metric("Data terpilih", f"{len(filtered):,}")
col2.metric("Rata-rata tinggi", f"{filtered['tinggi_badan_cm'].mean():.1f} cm")
col3.metric("Rata-rata berat", f"{filtered['berat_badan_kg'].mean():.1f} kg")
col4.metric("Stunting", format_percent(risk_rate(filtered["risiko_stunting"])))

st.subheader("Apa itu antropometri?")
st.markdown(
    """
    <div class="note">
    Antropometri adalah pengukuran fisik tubuh anak, seperti umur, tinggi badan, dan berat badan.
    Pada dashboard ini, pengukuran tersebut digunakan untuk membantu membaca apakah pertumbuhan
    anak sudah sesuai atau perlu mendapat perhatian lebih.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Pola tinggi badan menurut umur")
fig = px.scatter(
    filtered,
    x="umur_bulan",
    y="tinggi_badan_cm",
    color="stunting",
    opacity=0.58,
    hover_data={
        "jenis_kelamin": True,
        "berat_badan_kg": ":.1f",
        "tinggi_badan_cm": ":.1f",
        "wasting": True,
    },
    color_discrete_map=COLOR_MAP,
    title="Hubungan umur dan tinggi badan berdasarkan kategori stunting",
    labels=DISPLAY_LABELS,
)
fig.update_traces(marker=dict(size=7, line=dict(width=0)))
st.plotly_chart(apply_chart_layout(fig, height=520), use_container_width=True)

st.markdown(
    f"""
    <div class="note">
    {height_scatter_explanation}
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2)

with left:
    st.subheader("Hubungan tinggi dan berat badan")
    fig = px.scatter(
        filtered,
        x="tinggi_badan_cm",
        y="berat_badan_kg",
        color="wasting",
        opacity=0.62,
        hover_data={
            "jenis_kelamin": True,
            "umur_bulan": True,
            "stunting": True,
            "tinggi_badan_cm": ":.1f",
            "berat_badan_kg": ":.1f",
        },
        color_discrete_map=COLOR_MAP,
        title="Hubungan tinggi dan berat berdasarkan kategori wasting",
        labels=DISPLAY_LABELS,
    )
    fig.update_traces(marker=dict(size=7, line=dict(width=0)))
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)
    st.markdown(
        f"""
        <div class="note">
        {wasting_scatter_explanation}
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.subheader("Distribusi umur")
    fig = px.histogram(
        filtered,
        x="umur_bulan",
        nbins=24,
        histfunc="count",
        color="stunting_status",
        color_discrete_map=COLOR_MAP,
        title="Jumlah balita berdasarkan umur",
        labels=DISPLAY_LABELS,
    )
    fig.update_yaxes(title_text="Jumlah balita")
    fig.update_xaxes(title_text="Umur balita (bulan)")
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)
    st.markdown(
        f"""
        <div class="note">
        Data paling banyak berada pada umur {most_common_age} bulan, yaitu {most_common_age_count:,} balita
        atau sekitar {most_common_age_rate:.1f}% dari seluruh data terpilih. Informasi ini penting karena
        kelompok umur dengan jumlah data lebih besar dapat lebih kuat memengaruhi pola umum pada grafik lainnya.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Perbandingan kondisi fisik balita")
box_left, box_right = st.columns(2)

with box_left:
    fig = px.box(
        filtered,
        x="stunting_status",
        y="tinggi_badan_cm",
        color="stunting_status",
        points=False,
        color_discrete_map=COLOR_MAP,
        title="Perbandingan tinggi badan berdasarkan status stunting",
        labels=DISPLAY_LABELS,
    )
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)
    st.markdown(
        f"""
        <div class="note">
        {height_box_explanation}
        </div>
        """,
        unsafe_allow_html=True,
    )

with box_right:
    fig = px.box(
        filtered,
        x="stunting_status",
        y="berat_badan_kg",
        color="stunting_status",
        points=False,
        color_discrete_map=COLOR_MAP,
        title="Perbandingan berat badan berdasarkan status stunting",
        labels=DISPLAY_LABELS,
    )
    st.plotly_chart(apply_chart_layout(fig), use_container_width=True)
    st.markdown(
        f"""
        <div class="note">
        {weight_box_explanation}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Kapan perbedaan mulai terlihat?")
age_height = (
    filtered.groupby(["umur_bulan", "stunting_status"], observed=False)["tinggi_badan_cm"]
    .mean()
    .reset_index()
)
age_height_gap = age_height.pivot(index="umur_bulan", columns="stunting_status", values="tinggi_badan_cm")
if {"Stunting", "Non-Stunting"}.issubset(age_height_gap.columns):
    age_height_gap = age_height_gap.dropna(subset=["Stunting", "Non-Stunting"])
    if not age_height_gap.empty:
        age_height_gap["selisih"] = age_height_gap["Non-Stunting"] - age_height_gap["Stunting"]
        largest_gap_age = int(age_height_gap["selisih"].idxmax())
        largest_gap_value = age_height_gap.loc[largest_gap_age, "selisih"]
    else:
        largest_gap_age = None
        largest_gap_value = None
else:
    largest_gap_age = None
    largest_gap_value = None
fig = px.line(
    age_height,
    x="umur_bulan",
    y="tinggi_badan_cm",
    color="stunting_status",
    markers=True,
    color_discrete_map=COLOR_MAP,
    title="Rata-rata tinggi badan menurut umur dan status stunting",
    labels=DISPLAY_LABELS,
)
fig.update_xaxes(title_text="Umur balita (bulan)")
fig.update_yaxes(title_text="Rata-rata tinggi badan (cm)")
st.plotly_chart(apply_chart_layout(fig), use_container_width=True)

st.markdown(
    f"""
    <div class="note">
    Grafik ini merangkum rata-rata tinggi badan pada setiap umur. {
        f"Selisih rata-rata terbesar terlihat pada umur {largest_gap_age} bulan, yaitu sekitar {largest_gap_value:.1f} cm antara kelompok non-stunting dan stunting."
        if largest_gap_age is not None
        else "Pada filter saat ini, selisih rata-rata per umur belum bisa dihitung lengkap karena tidak semua umur memiliki kelompok stunting dan non-stunting sekaligus."
    }
    Pola ini membantu menunjukkan umur mana yang perbedaan pertumbuhannya paling menonjol.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Tabel data yang sesuai filter")
st.dataframe(
    readable_table(filtered.sort_values(["risiko_stunting", "umur_bulan"], ascending=[False, True])[
        [
            "jenis_kelamin",
            "umur_bulan",
            "tinggi_badan_cm",
            "berat_badan_kg",
            "stunting",
            "wasting",
            "stunting_status",
        ]
    ].head(300)),
    use_container_width=True,
    hide_index=True,
)
