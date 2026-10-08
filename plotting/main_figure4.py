"""Render final plotting tables; no prediction or statistical estimation."""
from __future__ import annotations
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from .io import read_table
INPUT = Path('.')
OUT = Path('outputs')


COLORS = {
    "negative": "#2B6CB0",
    "positive": "#B83232",
    "event": "#DD6B20",
    "non_event": "#6B7280",
    "teal": "#2C7A7B",
    "green": "#2F855A",
    "dark": "#1F2937",
    "muted": "#6B7280",
    "grid": "#D1D5DB",
    "panel_bg": "#F8FAFC",
}

POSITIVE_YEARS = [2017, 2020]

def _set_gcb_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.4,
            "axes.titlesize": 9.0,
            "axes.titleweight": "semibold",
            "axes.labelsize": 8.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 8.0,
            "savefig.dpi": 450,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.035,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "svg.fonttype": "none",
            "svg.hashsalt": "manuscript-figures",
            "pdf.fonttype": 42,
        }
    )

def _panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.08,
        1.05,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=10.0,
        fontweight="bold",
        color=COLORS["dark"],
    )

def _save(fig: plt.Figure, out_stem: str) -> None:
    out_png = OUT / f"{out_stem}.png"
    out_svg = OUT / f"{out_stem}.svg"
    fig.savefig(out_png, dpi=450)
    fig.savefig(out_svg, metadata={"Date": None})
    plt.close(fig)
    print(f"[OK] {out_png}")
    print(f"[OK] {out_svg}")

def plot() -> dict[str, object]:
    _set_gcb_style()
    focus = read_table(INPUT, 'main4_positive_years.csv').set_index('year')
    baseline = read_table(INPUT, 'main4_negative_years_summary.csv').set_index('metric')
    month = read_table(INPUT, 'main4_month.csv')
    latitude = read_table(INPUT, 'main4_latitude.csv')

    fig = plt.figure(figsize=(7.68, 4.84), constrained_layout=False)
    grid = fig.add_gridspec(2, 2, wspace=0.40, hspace=0.56)
    ax_share = fig.add_subplot(grid[0, 0])
    ax_grid = fig.add_subplot(grid[0, 1])
    ax_month = fig.add_subplot(grid[1, 0])
    ax_latitude = fig.add_subplot(grid[1, 1])

    metrics = [
        ("All months", "positive_month_share"),
        ("Event months", "event_positive_share"),
    ]
    y_positions = np.arange(len(metrics))
    lower = np.array([baseline.loc[column, 'lower'] for _, column in metrics])
    upper = np.array([baseline.loc[column, 'upper'] for _, column in metrics])
    means = np.array([baseline.loc[column, 'mean'] for _, column in metrics])
    ax_share.barh(
        y_positions,
        upper - lower,
        left=lower,
        height=0.28,
        color="#D8DEE9",
        edgecolor="none",
    )
    ax_share.scatter(
        means,
        y_positions,
        s=38,
        color=COLORS["muted"],
        zorder=4,
    )
    year_styles = [(2017, COLORS["positive"], "o", -0.075), (2020, COLORS["teal"], "s", 0.075)]
    for year, color, marker, offset in year_styles:
        values = np.array([focus.loc[year, column] * 100 for _, column in metrics])
        ax_share.scatter(
            values,
            y_positions + offset,
            s=48,
            marker=marker,
            color=color,
            edgecolor="white",
            linewidth=0.55,
            zorder=5,
        )
        for value, y_position in zip(values, y_positions + offset):
            ax_share.text(
                value + 0.55,
                y_position,
                f"{value:.1f}%",
                ha="left",
                va="center",
                fontsize=7.0,
                color=color,
            )
    ax_share.set_yticks(y_positions)
    ax_share.set_yticklabels([label for label, _ in metrics])
    ax_share.set_xlim(28, 61)
    ax_share.set_xlabel("Positive ΔGPP records (%)")
    ax_share.set_title("Positive-share shifts", loc="left", pad=5)
    ax_share.grid(axis="x", color=COLORS["grid"], linewidth=0.55, alpha=0.8)
    ax_share.set_axisbelow(True)
    legend_handles = [
        mpatches.Patch(facecolor="#D8DEE9", edgecolor="none", label="Negative-year range"),
        plt.Line2D(
            [0], [0], marker="o", linestyle="none", color=COLORS["muted"],
            markersize=5.5, label="Negative-year mean",
        ),
        plt.Line2D(
            [0], [0], marker="o", linestyle="none", color=COLORS["positive"],
            markersize=5.5, label="2017",
        ),
        plt.Line2D(
            [0], [0], marker="s", linestyle="none", color=COLORS["teal"],
            markersize=5.5, label="2020",
        ),
    ]
    ax_share.legend(
        handles=legend_handles,
        frameon=False,
        loc="center left",
        bbox_to_anchor=(0.01, 0.50),
        ncol=2,
        fontsize=6.5,
        handletextpad=0.40,
        columnspacing=0.75,
    )
    _panel_label(ax_share, "a")

    years = np.array(POSITIVE_YEARS)
    negative_counts = np.array([int(focus.loc[year, "negative_grids"]) for year in years])
    positive_counts = np.array([int(focus.loc[year, "positive_grids"]) for year in years])
    negative_pct = np.array([focus.loc[year, 'negative_pct'] for year in years])
    positive_pct = np.array([focus.loc[year, 'positive_pct'] for year in years])
    y = np.arange(len(years))
    ax_grid.barh(y, negative_pct, color=COLORS["negative"], edgecolor="white", height=0.48)
    ax_grid.barh(
        y,
        positive_pct,
        left=negative_pct,
        color=COLORS["positive"],
        edgecolor="white",
        height=0.48,
    )
    for index, year in enumerate(years):
        ax_grid.text(
            negative_pct[index] / 2,
            index,
            f"{negative_counts[index]}\nnegative",
            ha="center",
            va="center",
            color="white",
            fontsize=7.1,
            fontweight="semibold",
        )
        ax_grid.text(
            negative_pct[index] + positive_pct[index] / 2,
            index,
            f"{positive_counts[index]}\npositive",
            ha="center",
            va="center",
            color="white",
            fontsize=7.1,
            fontweight="semibold",
        )
    ax_grid.set_yticks(y)
    ax_grid.set_yticklabels(years.astype(str))
    ax_grid.invert_yaxis()
    ax_grid.set_xlim(0, 100)
    ax_grid.set_xlabel("Grid share (%)")
    ax_grid.set_title("Grid sign distribution", loc="left", pad=5)
    ax_grid.grid(axis="x", color=COLORS["grid"], linewidth=0.55, alpha=0.8)
    ax_grid.set_axisbelow(True)
    _panel_label(ax_grid, "b")

    month_x = np.arange(len(month))
    month_negative = month["negative_share"].to_numpy() * 100
    month_positive = month["positive_share"].to_numpy() * 100
    ax_month.bar(
        month_x,
        month_negative,
        color=COLORS["negative"],
        edgecolor="white",
        linewidth=0.35,
        width=0.76,
        label="ΔGPP < 0",
    )
    ax_month.bar(
        month_x,
        month_positive,
        bottom=month_negative,
        color=COLORS["positive"],
        edgecolor="white",
        linewidth=0.35,
        width=0.76,
        label="ΔGPP > 0",
    )
    ax_month.axhline(50, color=COLORS["dark"], linewidth=0.75, linestyle="--", alpha=0.65)
    ax_month.set_ylim(0, 100)
    ax_month.set_xticks(month_x)
    ax_month.set_xticklabels(month["month"].astype(int).astype(str))
    ax_month.set_xlabel("Month")
    ax_month.set_ylabel("Share of event-month records (%)")
    ax_month.set_title("Direction balance by month", loc="left", pad=5)
    ax_month.legend(frameon=False, ncol=2, loc="upper left", fontsize=7.0)
    ax_month.grid(axis="y", color=COLORS["grid"], linewidth=0.5, alpha=0.75)
    ax_month.set_axisbelow(True)
    _panel_label(ax_month, "c")

    latitude_x = np.arange(len(latitude))
    latitude_negative = latitude["negative_share"].to_numpy() * 100
    latitude_positive = latitude["positive_share"].to_numpy() * 100
    ax_latitude.bar(
        latitude_x,
        latitude_negative,
        color=COLORS["negative"],
        edgecolor="white",
        linewidth=0.35,
        width=0.72,
    )
    ax_latitude.bar(
        latitude_x,
        latitude_positive,
        bottom=latitude_negative,
        color=COLORS["positive"],
        edgecolor="white",
        linewidth=0.35,
        width=0.72,
    )
    ax_latitude.axhline(50, color=COLORS["dark"], linewidth=0.75, linestyle="--", alpha=0.65)
    ax_latitude.set_ylim(0, 100)
    ax_latitude.set_xticks(latitude_x)
    ax_latitude.set_xticklabels(
        [f"{value:g}" for value in latitude["midpoint"]]
    )
    ax_latitude.set_xlabel("Latitude-band midpoint (degrees)")
    ax_latitude.set_ylabel("Share of event-month records (%)")
    ax_latitude.set_title("Direction balance by latitude", loc="left", pad=5)
    ax_latitude.grid(axis="y", color=COLORS["grid"], linewidth=0.5, alpha=0.75)
    ax_latitude.set_axisbelow(True)
    _panel_label(ax_latitude, "d")

    fig.subplots_adjust(left=0.09, right=0.985, top=0.94, bottom=0.105)
    output_stem = "Figure_4"
    _save(fig, output_stem)


