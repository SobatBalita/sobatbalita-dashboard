from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "df_clean.csv"
ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_CANDIDATES = [
    ASSETS_DIR / "SobaBalita_Images.png"
]

COLOR_MAP = {
    "Normal": "#2A9D8F",
    "Tall": "#4C78A8",
    "Stunted": "#F4A261",
    "Severely Stunted": "#E76F51",
    "Non-Stunting": "#2A9D8F",
    "Stunting": "#E76F51",
    "Normal weight": "#2A9D8F",
    "Risk of Overweight": "#E9C46A",
    "Underweight": "#F4A261",
    "Severely Underweight": "#E76F51",
    "Laki-laki": "#4C78A8",
    "Perempuan": "#B279A2",
}

STUNTING_ORDER = ["Normal", "Tall", "Stunted", "Severely Stunted"]
WASTING_ORDER = [
    "Normal weight",
    "Risk of Overweight",
    "Underweight",
    "Severely Underweight",
]
AGE_GROUP_ORDER = ["0-5 bulan", "6-11 bulan", "12-23 bulan", "24-35 bulan", "36+ bulan"]

DISPLAY_LABELS = {
    "jenis_kelamin": "Jenis kelamin",
    "umur_bulan": "Umur balita (bulan)",
    "tinggi_badan_cm": "Tinggi badan (cm)",
    "berat_badan_kg": "Berat badan (kg)",
    "stunting": "Kategori stunting",
    "wasting": "Kategori wasting",
    "stunting_status": "Status stunting",
    "risiko_stunting": "Risiko stunting",
    "risiko_wasting": "Risiko wasting",
    "kelompok_umur": "Kelompok umur",
    "jumlah": "Jumlah balita",
    "status": "Status gizi",
    "status_wasting": "Status wasting",
    "Status": "Status gizi",
    "Jumlah": "Jumlah balita",
    "Persentase": "Persentase balita",
    "Jenis kelamin": "Jenis kelamin",
    "Indikator": "Indikator gizi",
    "Stunting (%)": "Stunting (%)",
    "Wasting (%)": "Wasting (%)",
}

TABLE_COLUMN_LABELS = {
    "jenis_kelamin": "Jenis kelamin",
    "umur_bulan": "Umur balita (bulan)",
    "tinggi_badan_cm": "Tinggi badan (cm)",
    "berat_badan_kg": "Berat badan (kg)",
    "stunting": "Kategori stunting",
    "wasting": "Kategori wasting",
    "stunting_status": "Status stunting",
}


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["risiko_stunting"] = df["stunting_status"].eq("Stunting")
    df["risiko_wasting"] = df["wasting"].isin(["Underweight", "Severely Underweight"])
    df["kelompok_umur"] = pd.cut(
        df["umur_bulan"],
        bins=[-1, 5, 11, 23, 35, 120],
        labels=AGE_GROUP_ORDER,
    )
    return df


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --primary: #0F766E;
            --primary-soft: #DDF4EF;
            --ink: #102A35;
            --body: #233B45;
            --muted: #52656D;
            --surface: #FFFFFF;
            --page: #F3F8F7;
            --sidebar: #E7F2EF;
            --line: #C9DAD6;
        }

        .stApp {
            background: var(--page);
            color: var(--body);
        }

        [data-testid="stSidebar"] {
            background: var(--sidebar);
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] * {
            color: var(--ink);
        }

        [data-testid="stSidebarNav"] {
            display: none;
        }

        .sidebar-brand {
            padding: 0 0 1rem;
            margin-bottom: 0.4rem;
            border-bottom: 1px solid var(--line);
        }

        .sidebar-logo-wrap {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.75rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 8px 18px rgba(16, 42, 53, 0.07);
        }

        .sidebar-logo-wrap img {
            display: block;
            width: 100%;
            height: auto;
            max-height: 96px;
            object-fit: contain;
        }

        [data-testid="stSidebar"] [data-testid="stImage"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.75rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 8px 18px rgba(16, 42, 53, 0.07);
        }

        [data-testid="stSidebar"] [data-testid="stImage"] img {
            max-height: 108px;
            object-fit: contain;
        }

        .sidebar-brand h2 {
            font-size: 1.35rem;
            line-height: 1.15;
            margin: 0 0 0.35rem;
            color: var(--ink);
        }

        .sidebar-brand p {
            font-size: 0.86rem;
            line-height: 1.45;
            margin: 0;
            color: var(--muted);
        }

        .sidebar-section-title {
            margin: 1rem 0 0.45rem;
            font-size: 0.76rem;
            font-weight: 700;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            min-height: 2.8rem;
            padding: 0.65rem 0.85rem;
            border-radius: 8px;
            color: var(--ink);
            font-weight: 600;
            border: 1px solid transparent;
            transition: all 140ms ease;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: #FFFFFF;
            border-color: var(--line);
            box-shadow: 0 6px 16px rgba(16, 42, 53, 0.08);
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
            background: #FFFFFF;
            border-color: var(--primary);
            box-shadow: inset 4px 0 0 var(--primary), 0 8px 18px rgba(16, 42, 53, 0.1);
        }

        .sidebar-help {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.9rem;
            margin-top: 1rem;
            box-shadow: 0 8px 18px rgba(16, 42, 53, 0.07);
        }

        .sidebar-help strong {
            display: block;
            color: var(--ink);
            margin-bottom: 0.3rem;
            font-size: 0.94rem;
        }

        .sidebar-help span {
            display: block;
            color: var(--muted);
            line-height: 1.45;
            font-size: 0.86rem;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1220px;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--ink);
        }

        p, li, label, span, div {
            color: var(--body);
        }

        .hero {
            padding: 1.2rem 0 1rem;
            border-bottom: 1px solid var(--line);
            margin-bottom: 1.2rem;
        }

        .hero h1 {
            font-size: 2.4rem;
            line-height: 1.1;
            margin-bottom: 0.45rem;
        }

        .hero p {
            max-width: 760px;
            color: var(--muted);
            font-size: 1.02rem;
            margin: 0;
        }

        .note {
            border-left: 4px solid var(--primary);
            background: var(--primary-soft);
            padding: 0.9rem 1rem;
            border-radius: 6px;
            color: var(--ink);
            margin: 0.7rem 0 1rem;
            font-weight: 500;
        }

        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 8px 20px rgba(16, 42, 53, 0.08);
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--muted);
            font-size: 0.88rem;
        }

        div[data-testid="stMetricValue"] {
            color: var(--ink);
        }

        .stPlotlyChart {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.35rem;
        }

        div[data-testid="stAlert"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            color: var(--ink);
        }

        div[data-testid="stAlert"] * {
            color: var(--ink);
        }

        div[data-testid="stDataFrame"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
        }

        .stSelectbox label,
        .stSlider label,
        .stDataFrame,
        [data-testid="stMarkdownContainer"] {
            color: var(--body);
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 8px;
            color: var(--ink);
            box-shadow: none;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] > div:hover,
        [data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(15, 118, 110, 0.16);
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] span,
        [data-testid="stSidebar"] div[data-baseweb="select"] svg {
            color: var(--ink);
            fill: var(--ink);
        }

        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] [role="listbox"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 12px 28px rgba(16, 42, 53, 0.18);
        }

        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] [role="option"] {
            background: #FFFFFF;
            color: var(--ink);
        }

        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] [role="option"]:hover {
            background: var(--primary-soft);
            color: var(--ink);
        }

        div[data-baseweb="popover"] li[aria-selected="true"],
        div[data-baseweb="popover"] [role="option"][aria-selected="true"] {
            background: #CFEAE4;
            color: var(--ink);
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, description):
    apply_theme()
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(active_page=None):
    apply_theme()
    logo_path = next((path for path in LOGO_CANDIDATES if path.exists()), None)
    if logo_path is None:
        logo_path = next(iter(sorted(ASSETS_DIR.glob("*.png"))), None)

    if logo_path is not None:
        st.sidebar.image(str(logo_path), use_container_width=True)

    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <h2>SobatBalita</h2>
            <p>Dashboard status gizi balita berbasis data antropometri.</p>
        </div>
        <div class="sidebar-section-title">Navigasi</div>
        """,
        unsafe_allow_html=True,
    )

    pages = [
        ("app.py", "Beranda", "home"),
        ("pages/1_overview.py", "Overview Dataset", "overview"),
        ("pages/2_statusGizi.py", "Status Gizi", "status"),
        ("pages/3_antropometri.py", "Antropometri", "antropometri"),
        ("pages/4_demografi.py", "Demografi", "demografi"),
        ("pages/5_insight.py", "Insight", "insight"),
    ]

    for path, label, _key in pages:
        st.sidebar.page_link(path, label=label)

    st.sidebar.markdown(
        """
        <div class="sidebar-help">
            <strong>Panduan cepat</strong>
            <span>Pilih halaman analisis, lalu gunakan filter umur dan jenis kelamin untuk mempersempit data.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_percent(value):
    return f"{value:.1f}%"


def readable_table(df):
    return df.rename(columns=TABLE_COLUMN_LABELS)


def risk_rate(series):
    if len(series) == 0:
        return 0
    return series.mean() * 100


def add_sidebar_filters(df, key_prefix="filter"):
    st.sidebar.header("Filter Data")
    st.sidebar.caption("Gunakan filter ini untuk melihat kelompok anak tertentu.")

    gender_options = ["Semua"] + sorted(df["jenis_kelamin"].dropna().unique().tolist())
    gender = st.sidebar.selectbox("Jenis kelamin", gender_options, key=f"{key_prefix}_gender")

    min_age = int(df["umur_bulan"].min())
    max_age = int(df["umur_bulan"].max())
    age_range = st.sidebar.slider(
        "Rentang umur (bulan)",
        min_age,
        max_age,
        (min_age, max_age),
        key=f"{key_prefix}_age",
    )

    filtered = df[
        (df["umur_bulan"].between(age_range[0], age_range[1]))
        & ((df["jenis_kelamin"].eq(gender)) if gender != "Semua" else True)
    ].copy()

    st.sidebar.metric("Data terpilih", f"{len(filtered):,}")
    return filtered


def apply_chart_layout(fig, height=420):
    fig.update_layout(
        template=None,
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        colorway=["#0F766E", "#E76F51", "#4C78A8", "#F4A261", "#B279A2", "#E9C46A", "#72B7B2"],
        font=dict(family="Arial", color="#102A35", size=13),
        title=dict(font=dict(color="#102A35", size=18), x=0.02, xanchor="left"),
        legend=dict(font=dict(color="#102A35"), bgcolor="rgba(255,255,255,0.88)"),
        margin=dict(l=80, r=35, t=75, b=70),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#C9DAD6", font=dict(color="#102A35")),
    )
    fig.update_xaxes(
        color="#102A35",
        title_font=dict(color="#102A35"),
        tickfont=dict(color="#102A35"),
        gridcolor="#E6EFEC",
        zerolinecolor="#C9DAD6",
        automargin=True,
        title_standoff=18,
    )
    fig.update_yaxes(
        color="#102A35",
        title_font=dict(color="#102A35"),
        tickfont=dict(color="#102A35"),
        gridcolor="#E6EFEC",
        zerolinecolor="#C9DAD6",
        automargin=True,
        title_standoff=18,
    )
    fig.update_layout(uniformtext=dict(mode="show", minsize=10))
    return fig


def bar_chart(data, x, y, color=None, title=None, category_orders=None, text=None, orientation="v"):
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        text=text,
        title=title,
        color_discrete_map=COLOR_MAP,
        category_orders=category_orders,
        orientation=orientation,
        labels=DISPLAY_LABELS,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    fig = apply_chart_layout(fig)
    if orientation == "h":
        fig.update_layout(margin=dict(l=145, r=70, t=75, b=55))
        if category_orders and y in category_orders:
            fig.update_yaxes(categoryorder="array", categoryarray=list(reversed(category_orders[y])))
    return fig
