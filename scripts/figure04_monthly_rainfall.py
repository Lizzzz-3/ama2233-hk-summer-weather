"""图四：从仓库三份原始 CSV 核对完整年份，绘制平均月雨量。"""
from pathlib import Path
import calendar
import csv
from datetime import date
import math
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
MONTHS = (6, 7, 8)
PERIODS = (("early_1991_2000", 1991, 2000), ("recent_2016_2025", 2016, 2025))
# 图三制作时也请使用这两个时期颜色。
COLORS = ("#246C8A", "#C05A37")


def read_raw(filename, rainfall=False):
    """保留 C 标记的有效数值；Trace 按计划记作 0，缺失不填零。"""
    rows = {}
    with (ROOT / "data/raw" / filename).open(encoding="utf-8-sig", newline="") as f:
        next(f)
        next(f)
        for row in csv.DictReader(f):
            try:
                y, m, d = (int(row[k]) for k in ("年/Year", "月/Month", "日/Day"))
            except (ValueError, TypeError):
                continue  # 原始 CSV 末尾的说明行
            if not (1991 <= y <= 2025 and m in MONTHS):
                continue
            day = date(y, m, d)
            if day in rows:
                raise ValueError(f"Duplicate date: {filename}: {day}")
            value = row["數值/Value"]
            trace = rainfall and value == "Trace"
            try:
                number = 0.0 if trace else float(value)
            except (ValueError, TypeError):
                number = math.nan
            valid = row["數據完整性/data Completeness"] == "C" and math.isfinite(number)
            if rainfall and valid and number < 0:
                raise ValueError(f"Negative rainfall: {day}")
            rows[day] = (number, valid, trace)
    return rows


def prepare_data():
    """每日求和 → 每年各月总量 → 时期内跨年平均，并核对已有指标。"""
    sources = [read_raw("daily_mean_temperature_hko.csv"),
               read_raw("daily_maximum_temperature_hko.csv"),
               read_raw("daily_rainfall_hko.csv", rainfall=True)]
    monthly, valid_years = {}, []
    for year in range(1991, 2026):
        days = [date(year, month, day) for month in MONTHS
                for day in range(1, calendar.monthrange(year, month)[1] + 1)]
        if not all(day in source and source[day][1] for day in days for source in sources):
            continue
        valid_years.append(year)
        for month in MONTHS:
            monthly[year, month] = math.fsum(sources[2][d][0] for d in days if d.month == month)
    # 与仓库每年各月指标逐项核对，防止绘图与小组表格不一致。
    with (ROOT / "data/metrics/monthly_summer_metrics.csv").open() as f:
        existing = {(int(r["year"]), int(r["month"])): float(r["monthly_total_rainfall_mm"])
                    for r in csv.DictReader(f)}
    if existing.keys() != monthly.keys() or any(
        not math.isclose(existing[k], v, abs_tol=1e-8) for k, v in monthly.items()
    ):
        raise ValueError("Raw data and monthly_summer_metrics.csv disagree")
    with (ROOT / "data/metrics/period_monthly_summary.csv").open() as f:
        summary = {(r["period"], int(r["month"])): r for r in csv.DictReader(f)}
    records = []
    for period, start, end in PERIODS:
        years = [y for y in valid_years if start <= y <= end]
        if not years:
            raise ValueError(f"No complete summers in {period}")
        for month in MONTHS:
            value = mean(monthly[y, month] for y in years)
            original = summary[period, month]
            if int(original["year_count"]) != len(years) or not math.isclose(
                value, float(original["average_monthly_total_rainfall_mm"]), abs_tol=1e-8
            ):
                raise ValueError("Raw data and period_monthly_summary.csv disagree")
            traces = sum(sources[2][d][2] for d in sources[2] if d.year in years and d.month == month)
            records.append(dict(period=period, month=month, year_count=len(years),
                                valid_years=";".join(map(str, years)),
                                average_monthly_total_rainfall_mm=value,
                                trace_upper_bound_mm=traces * 0.05 / len(years)))
    print(f"Verified {len(valid_years)} complete summers, {len(monthly)} monthly totals and 6 period means.")
    return records


def make_figure(records):
    """与现有图五一致的字体、版式、PNG 分辨率和 SVG 字体路径。"""
    style = {"font.family": "DejaVu Sans", "font.size": 10,
             "text.color": "#243746", "axes.labelcolor": "#243746",
             "xtick.color": "#51616D", "ytick.color": "#51616D", "svg.fonttype": "path"}
    with plt.rc_context(style):
        fig, ax = plt.subplots(figsize=(8.6, 6.4), facecolor="white")
        fig.subplots_adjust(left=0.115, right=0.955, bottom=0.235, top=0.77)
        width = 0.32
        for i, (period, start, end) in enumerate(PERIODS):
            data = [r for r in records if r["period"] == period]
            bars = ax.bar([x + (i - 0.5) * width for x in range(3)],
                          [r["average_monthly_total_rainfall_mm"] for r in data],
                          width=width, color=COLORS[i], edgecolor="white", linewidth=0.7,
                          label=f"{start}–{end} (n = {data[0]['year_count']} years)", zorder=3)
            ax.bar_label(bars, fmt="%.2f", padding=5, fontsize=10)
        ax.set_xticks(range(3), ["June (6)", "July (7)", "August (8)"])
        ax.set_xlabel("Month", labelpad=12)
        ax.set_ylabel("Mean monthly total rainfall (mm)", labelpad=12)
        ymax = max(r["average_monthly_total_rainfall_mm"] for r in records)
        ax.set_ylim(0, math.ceil(ymax * 1.16 / 100) * 100)
        ax.grid(axis="y", color="#E5EAED", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color("#B8C3CA")
        ax.tick_params(length=3, color="#B8C3CA")
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), ncol=2, frameon=False, fontsize=9)
        fig.text(0.115, 0.93, "Figure 4. Monthly rainfall comparison", fontsize=16, weight="bold")
        fig.text(0.115, 0.88, "Hong Kong Observatory · June–August · Study period: 1991–2025",
                 fontsize=10, color="#51616D")
        fig.text(0.115, 0.10, "Bars show the across-year mean of monthly totals; complete summers only.", fontsize=8.5, color="#51616D")
        fig.text(0.115, 0.06, "Source: project HKO daily CSVs. Trace (<0.05 mm) treated as 0 mm.", fontsize=8.5, color="#51616D")
        output = ROOT / "figures"
        output.mkdir(exist_ok=True)
        for ext in ("png", "svg"):
            path = output / f"04_monthly_rainfall_comparison.{ext}"
            fig.savefig(path, dpi=300, facecolor="white")
            print(path)
        plt.close(fig)


def main():
    records = prepare_data()
    output = ROOT / "reports/figure04_values.csv"
    output.parent.mkdir(exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    make_figure(records)
    return records


if __name__ == "__main__":
    main()
