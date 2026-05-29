# SobatBalita Dashboard

Dashboard interaktif berbasis Streamlit untuk membantu membaca status gizi balita dari data antropometri. Dashboard ini berfokus pada dua indikator utama:

- **Stunting**: kondisi ketika tinggi badan anak lebih rendah dari standar usianya.
- **Wasting**: kondisi ketika berat badan anak terlalu rendah dibanding tinggi badannya.

Dashboard dirancang agar visualisasi dan insight mudah dipahami oleh pengguna umum, tetapi tetap menjawab kebutuhan analisis dari data.

## Demo

Dashboard dapat diakses melalui link berikut:

[https://pjclhgogxpjmtbmy2mty3d.streamlit.app/](https://pjclhgogxpjmtbmy2mty3d.streamlit.app/)

## Fitur Utama

- Ringkasan jumlah data balita, stunting, wasting, dan rata-rata umur.
- Visualisasi status utama stunting dan wasting.
- Analisis kategori status gizi secara rinci.
- Analisis antropometri berdasarkan umur, tinggi badan, dan berat badan.
- Analisis demografi berdasarkan jenis kelamin dan kelompok umur.
- Insight dan kesimpulan otomatis berdasarkan filter yang dipilih.
- Implementasi A/B testing menggunakan Python untuk membandingkan proporsi stunting dan wasting.
- Filter interaktif untuk memilih jenis kelamin dan rentang umur.

## Halaman Dashboard

### Beranda

Menampilkan ringkasan utama dashboard, grafik status stunting dan wasting, kelompok umur yang perlu diperhatikan, serta pengertian singkat stunting dan wasting.

### Overview Dataset

Menampilkan ringkasan data terpilih, pratinjau dataset, informasi kolom, dan statistik dasar seperti rata-rata umur, tinggi badan, dan berat badan.

### Status Gizi

Menampilkan distribusi kategori stunting dan wasting, komposisi ringkas stunting vs non-stunting, serta wasting vs non-wasting.

### Antropometri

Menampilkan hubungan umur, tinggi badan, dan berat badan. Halaman ini juga memberikan penjelasan numerik di bawah setiap grafik agar hasil visualisasi lebih mudah dipahami.

### Demografi

Menampilkan distribusi data berdasarkan jenis kelamin dan kelompok umur, serta membandingkan risiko stunting dan wasting pada tiap jenis kelamin.

### Insight

Merangkum temuan utama, jawaban pertanyaan bisnis, perbandingan indikator menurut umur, dan kesimpulan praktis dari data yang sedang difilter.

## Dataset

Dataset yang digunakan berada pada folder `data/df_clean.csv` dan memuat informasi:

- jenis kelamin
- umur balita dalam bulan
- tinggi badan dalam cm
- berat badan dalam kg
- kategori stunting
- kategori wasting
- status stunting

## A/B Testing

Proyek ini juga dilengkapi implementasi A/B testing menggunakan Python pada file `ab_testing.py`.

A/B testing dilakukan sebagai analisis perbandingan dua kelompok balita berdasarkan:

- jenis kelamin: laki-laki vs perempuan
- kelompok umur: 0-12 bulan vs 13-24 bulan

Metrik yang diuji:

- status stunting
- status wasting

Script A/B testing dapat dijalankan dengan perintah:

```bash
python ab_testing.py
```

Hasil pengujian digunakan untuk melihat apakah terdapat perbedaan proporsi stunting atau wasting yang signifikan antara dua kelompok. Karena dataset ini bersifat observasional, A/B testing pada proyek ini dipahami sebagai perbandingan kelompok, bukan eksperimen perlakuan langsung.

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly

## Struktur Folder

```text
sobatbalita-dashboard/
|-- ab_testing.py
|-- app.py
|-- dashboard_utils.py
|-- requirements.txt
|-- README.md
|-- assets/
|   `-- 277937024.png
|-- data/
|   `-- df_clean.csv
`-- pages/
    |-- 1_overview.py
    |-- 2_statusGizi.py
    |-- 3_antropometri.py
    |-- 4_demografi.py
    `-- 5_insight.py
```

## Cara Menjalankan

### 1. Clone repository

```bash
git clone <repository-url>
cd sobatbalita-dashboard
```

### 2. Install dependency

```bash
pip install -r requirements.txt
```

### 3. Jalankan Streamlit

```bash
streamlit run app.py
```
