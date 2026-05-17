import csv
import math
from pathlib import Path


DATA_PATH = Path(__file__).parent / "data" / "df_clean.csv"
ALPHA = 0.05


def read_dataset(path):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def add_derived_columns(rows):
    for row in rows:
        row["wasting_status"] = (
            "Wasting"
            if row["wasting"] in ["Underweight", "Severely Underweight"]
            else "Non-Wasting"
        )

        umur_bulan = int(row["umur_bulan"])
        row["kelompok_umur_ab"] = "0-12 bulan" if umur_bulan <= 12 else "13-24 bulan"


def build_2x2_table(rows, group_col, metric_col, group_a, group_b, positive_label):
    negative_label = f"Non-{positive_label}"
    table = {
        group_a: {positive_label: 0, negative_label: 0},
        group_b: {positive_label: 0, negative_label: 0},
    }

    for row in rows:
        group_value = row[group_col]
        metric_value = row[metric_col]

        if group_value not in table:
            continue

        if metric_value == positive_label:
            table[group_value][positive_label] += 1
        else:
            table[group_value][negative_label] += 1

    return table


def chi_square_2x2(table, group_a, group_b, positive_label):
    negative_label = f"Non-{positive_label}"
    observed = [
        [table[group_a][positive_label], table[group_a][negative_label]],
        [table[group_b][positive_label], table[group_b][negative_label]],
    ]

    row_totals = [sum(row) for row in observed]
    col_totals = [
        observed[0][0] + observed[1][0],
        observed[0][1] + observed[1][1],
    ]
    total = sum(row_totals)

    chi_square = 0
    for row_index in range(2):
        for col_index in range(2):
            expected = row_totals[row_index] * col_totals[col_index] / total
            chi_square += (observed[row_index][col_index] - expected) ** 2 / expected

    # Untuk chi-square dengan derajat bebas 1, p-value bisa dihitung memakai erfc.
    p_value = math.erfc(math.sqrt(chi_square / 2))
    return chi_square, p_value


def format_percent(value):
    return f"{value:.2f}%"


def print_table(table, group_a, group_b, positive_label):
    negative_label = f"Non-{positive_label}"
    print(f"{'Kelompok':<15} {positive_label:>15} {negative_label:>15} {'Total':>15}")

    for group in [group_a, group_b]:
        positive_count = table[group][positive_label]
        negative_count = table[group][negative_label]
        total = positive_count + negative_count
        print(f"{group:<15} {positive_count:>15,} {negative_count:>15,} {total:>15,}")


def run_ab_test(rows, group_col, metric_col, group_a, group_b, positive_label, test_title):
    table = build_2x2_table(rows, group_col, metric_col, group_a, group_b, positive_label)
    chi_square, p_value = chi_square_2x2(table, group_a, group_b, positive_label)

    total_a = sum(table[group_a].values())
    total_b = sum(table[group_b].values())
    positive_a = table[group_a][positive_label]
    positive_b = table[group_b][positive_label]
    rate_a = positive_a / total_a * 100
    rate_b = positive_b / total_b * 100
    difference = rate_a - rate_b

    print("=" * 72)
    print(test_title)
    print("=" * 72)
    print(f"Kelompok A: {group_a}")
    print(f"Kelompok B: {group_b}")
    print(f"Metrik yang diuji: {metric_col}")
    print()
    print("Tabel Kontingensi:")
    print_table(table, group_a, group_b, positive_label)
    print()
    print("Ringkasan:")
    print(f"- {group_a}: {positive_a:,} dari {total_a:,} data ({format_percent(rate_a)})")
    print(f"- {group_b}: {positive_b:,} dari {total_b:,} data ({format_percent(rate_b)})")
    print(f"- Selisih A - B: {difference:.2f} poin persentase")
    print()
    print("Hasil Uji Chi-Square:")
    print(f"- Chi-square: {chi_square:.4f}")
    print(f"- P-value: {p_value:.6f}")
    print(f"- Alpha: {ALPHA}")
    print()

    if p_value < ALPHA:
        print("Kesimpulan:")
        print("Terdapat perbedaan yang signifikan antara kelompok A dan kelompok B.")
    else:
        print("Kesimpulan:")
        print("Tidak terdapat perbedaan yang signifikan antara kelompok A dan kelompok B.")

    print()


def main():
    rows = read_dataset(DATA_PATH)
    add_derived_columns(rows)

    print("IMPLEMENTASI A/B TESTING DATASET SOBATBALITA")
    print()
    print(f"Jumlah data: {len(rows):,}")
    print(f"Dataset: {DATA_PATH}")
    print()

    run_ab_test(
        rows=rows,
        group_col="jenis_kelamin",
        metric_col="stunting_status",
        group_a="Laki-laki",
        group_b="Perempuan",
        positive_label="Stunting",
        test_title="A/B Test 1: Jenis Kelamin terhadap Status Stunting",
    )

    run_ab_test(
        rows=rows,
        group_col="jenis_kelamin",
        metric_col="wasting_status",
        group_a="Laki-laki",
        group_b="Perempuan",
        positive_label="Wasting",
        test_title="A/B Test 2: Jenis Kelamin terhadap Status Wasting",
    )

    run_ab_test(
        rows=rows,
        group_col="kelompok_umur_ab",
        metric_col="stunting_status",
        group_a="0-12 bulan",
        group_b="13-24 bulan",
        positive_label="Stunting",
        test_title="A/B Test 3: Kelompok Umur terhadap Status Stunting",
    )

    run_ab_test(
        rows=rows,
        group_col="kelompok_umur_ab",
        metric_col="wasting_status",
        group_a="0-12 bulan",
        group_b="13-24 bulan",
        positive_label="Wasting",
        test_title="A/B Test 4: Kelompok Umur terhadap Status Wasting",
    )


if __name__ == "__main__":
    main()
