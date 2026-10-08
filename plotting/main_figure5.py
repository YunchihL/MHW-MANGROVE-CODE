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


TAG_ORDER = ["gfdl245", "mpi245", "gfdl585", "mpi585"]

TAG_LABELS = {
    "gfdl245": "GFDL\nSSP245",
    "mpi245": "MPI\nSSP245",
    "gfdl585": "GFDL\nSSP585",
    "mpi585": "MPI\nSSP585",
}

SCENARIO_COLORS = {"ssp245": "#2B6CB0", "ssp585": "#B83232"}

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
    fig.savefig(out_png, dpi=450, metadata={"Software": "Matplotlib"})
    fig.savefig(out_svg, metadata={"Date": None})
    plt.close(fig)
    print(f"[OK] {out_png}")
    print(f"[OK] {out_svg}")

def plot() -> None:
    _set_gcb_style()
    mpl.rcParams.update(
        {
            "font.size": 9.0,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9.5,
            "xtick.labelsize": 8.8,
            "ytick.labelsize": 8.8,
            "legend.fontsize": 8.5,
        }
    )

    panel_a = read_table(INPUT, 'main5_hazard.csv')
    fixed = read_table(INPUT, 'main5_fixed.csv')
    area_summary = read_table(INPUT, 'main5_area_ranges.csv').set_index('area_case')

    metrics = [
        ("mhw_month_fraction", "MHW month\nfraction"),
        ("intensity_max_month_mhw_mean", "Peak monthly\nintensity"),
        ("duration_weighted_sum_mhw_mean", "Duration-weighted\nload"),
        (
            "intensity_cumulative_weighted_sum_mhw_mean",
            "Cumulative\nintensity load",
        ),
    ]
    metric_order = [metric for metric, _ in metrics]

    fixed['tag'] = pd.Categorical(fixed['tag'], TAG_ORDER, ordered=True)
    fixed = fixed.sort_values('tag').copy()

    case_order = ["persist_only", "partial_migration_q25", "potential_upper"]
    case_labels = {
        "persist_only": "Persistence\nonly",
        "partial_migration_q25": "Partial\nmigration",
        "potential_upper": "Upper\npotential",
    }
    case_colors = {
        "persist_only": COLORS["non_event"],
        "partial_migration_q25": COLORS["teal"],
        "potential_upper": COLORS["event"],
    }
    fig = plt.figure(figsize=(13.0, 5.75), constrained_layout=False)
    gs = fig.add_gridspec(
        1,
        3,
        width_ratios=[1.45, 0.98, 1.12],
        left=0.075,
        right=0.985,
        top=0.88,
        bottom=0.18,
        wspace=0.34,
    )
    ax_hazard = fig.add_subplot(gs[0, 0])
    ax_fixed = fig.add_subplot(gs[0, 1])
    ax_area = fig.add_subplot(gs[0, 2])

    y = np.arange(len(metrics))[::-1]
    scenario_specs = [
        ("ssp245", SCENARIO_COLORS["ssp245"], 0.07, "SSP245"),
        ("ssp585", SCENARIO_COLORS["ssp585"], -0.07, "SSP585"),
    ]
    for yi, metric in zip(y, metric_order):
        metric_values = panel_a[panel_a["metric"] == metric]
        line_max = float(metric_values["ci_high"].max())
        ax_hazard.plot(
            [1.0, line_max],
            [yi, yi],
            color=COLORS["grid"],
            lw=4.0,
            alpha=0.82,
            solid_capstyle="butt",
            zorder=1,
        )
        for scenario, color, offset, legend_label in scenario_specs:
            row = metric_values[metric_values["scenario"] == scenario].iloc[0]
            mean = float(row["mean_ratio"])
            left = mean - float(row["ci_low"])
            right = float(row["ci_high"]) - mean
            ax_hazard.errorbar(
                mean,
                yi + offset,
                xerr=np.array([[left], [right]]),
                fmt="o",
                markersize=5.0,
                color=color,
                ecolor=color,
                elinewidth=1.25,
                capsize=4.0,
                capthick=1.15,
                markeredgecolor="white",
                markeredgewidth=0.65,
                zorder=3,
                label=legend_label if metric == metric_order[0] else None,
            )
        ssp585 = metric_values[metric_values["scenario"] == "ssp585"].iloc[0]
        ax_hazard.text(
            float(ssp585["ci_high"]) + 0.10,
            yi - 0.07,
            f"{float(ssp585['mean_ratio']):.1f}x",
            ha="left",
            va="center",
            fontsize=8.4,
            color=COLORS["dark"],
        )
    ax_hazard.axvline(1.0, color=COLORS["dark"], lw=0.9, ls="--", zorder=2)
    ax_hazard.set_yticks(y)
    ax_hazard.set_yticklabels([label for _, label in metrics])
    ax_hazard.set_xlim(0.75, 7.35)
    ax_hazard.set_xlabel("Mean relative to historical baseline")
    ax_hazard.set_title("Late-century MHW forcing", loc="left", pad=7)
    ax_hazard.grid(False)
    ax_hazard.legend(
        frameon=False,
        loc="center right",
        bbox_to_anchor=(0.87, 0.73),
        handletextpad=0.5,
    )
    _panel_label(ax_hazard, "a")

    x = np.arange(len(fixed))
    bar_colors = [
        SCENARIO_COLORS["ssp245"] if str(tag).endswith("245") else SCENARIO_COLORS["ssp585"]
        for tag in fixed["tag"].astype(str)
    ]
    bars = ax_fixed.bar(
        x,
        fixed["delta_tg_c_yr"],
        color=bar_colors,
        edgecolor="white",
        linewidth=0.7,
        width=0.62,
    )
    for bar, value in zip(bars, fixed["delta_tg_c_yr"]):
        ax_fixed.text(
            bar.get_x() + bar.get_width() / 2,
            float(value) + 0.045,
            f"{float(value):.2f}",
            ha="center",
            va="bottom",
            fontsize=8.4,
        )
    ax_fixed.set_xticks(x)
    ax_fixed.set_xticklabels([TAG_LABELS[tag] for tag in fixed["tag"].astype(str)])
    ax_fixed.set_ylabel("Fixed-area ΔGPP\n(Tg C yr$^{-1}$)")
    ax_fixed.set_title("Fixed-area 2091–2100", loc="left", pad=7)
    ax_fixed.set_ylim(0, float(fixed["delta_tg_c_yr"].max()) * 1.24)
    ax_fixed.grid(axis="y", color=COLORS["grid"], lw=0.55, alpha=0.60)
    ax_fixed.set_axisbelow(True)
    _panel_label(ax_fixed, "b")

    area_y = np.arange(len(case_order))
    ax_area.axvline(1.0, color=COLORS["dark"], lw=0.9, ls="--", zorder=1)
    for yi, case in enumerate(case_order):
        values = area_summary.loc[case]
        color = case_colors[case]
        ax_area.plot(
            [values['min'], values['max']],
            [yi, yi],
            color=color,
            lw=10.0,
            alpha=0.25,
            solid_capstyle="round",
            zorder=2,
        )
        ax_area.scatter(
            [values['mean']],
            [yi],
            s=58,
            color=color,
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        ax_area.text(
            float(values['max']) + 0.045,
            yi,
            f"{values['min']:.2f}–{values['max']:.2f}",
            ha="left",
            va="center",
            fontsize=8.4,
            color=COLORS["dark"],
        )
    ax_area.set_yticks(area_y)
    ax_area.set_yticklabels([case_labels[case] for case in case_order])
    ax_area.invert_yaxis()
    ax_area.set_xlim(0.55, 2.15)
    ax_area.set_xlabel("Area-adjusted / fixed-area ΔGPP")
    ax_area.set_title("Area-pathway scaling", loc="left", pad=7)
    ax_area.grid(axis="x", color=COLORS["grid"], lw=0.55, alpha=0.60)
    ax_area.set_axisbelow(True)
    _panel_label(ax_area, "c")

    _save(fig, "Figure_5")
