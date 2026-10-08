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

BLUE = "#2F6FB3"

RED = "#C23636"

DARK = "#1F2937"

def setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.0,
            "axes.titlesize": 10.0,
            "axes.titleweight": "bold",
            "axes.labelsize": 9.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.85,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8.5,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.dpi": 450,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "axes.unicode_minus": False,
            "svg.hashsalt": "manuscript-figures",
        }
    )

def save(fig: plt.Figure, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png", dpi=450)
    fig.savefig(
        OUT / f"{name}.svg",
        metadata={"Date": None},
    )
    plt.close(fig)

def plot() -> None:
    setup_style()
    grid_year = read_table(INPUT, 'main6_historical.csv')
    heatmap = read_table(INPUT, 'main6_heatmap.csv')
    future_grid = read_table(INPUT, 'main6_future.csv')
    label_table = read_table(INPUT, 'main6_labels.csv')
    labels = dict(zip(label_table['grid_id'], label_table['label']))
    if len(labels) != 3:
        raise ValueError('Figure 6 requires three representative grids in label-table order')
    heat_vars = [
        ("mean_sst", "Mean SST"),
        ("vpd_pa", "VPD"),
        ("srad_mj_m2_day", "SRAD"),
        ("isMHW", "MHW months"),
        ("duration_weighted_sum", "Duration load"),
        ("intensity_cumulative_weighted_sum", "Cumulative load"),
    ]
    fig, axes = plt.subplots(3, 3, figsize=(13.2, 9.0), gridspec_kw={"width_ratios": [1.05, 1.65, 1.0]})
    im = None
    for ri, gid in enumerate(labels):
        h = grid_year[grid_year["grid_id"] == gid].sort_values("year")
        ax = axes[ri, 0]
        vals = h["delta_gpp"] / 1e9
        xpos = np.arange(len(h))
        ax.bar(xpos, vals, color=np.where(vals > 0, RED, BLUE), width=0.7, edgecolor="white")
        ax.axhline(0, color=DARK, lw=0.8)
        ax.set_xticks(xpos)
        ax.set_xticklabels(h["year"].astype(int), rotation=40, ha="right")
        ax.set_ylabel("10$^9$ g C yr$^{-1}$")
        if ri == 0:
            ax.set_title("Historical annual ΔGPP", loc="left")
        ax.text(
            -0.40,
            0.5,
            labels[gid],
            transform=ax.transAxes,
            rotation=90,
            rotation_mode="anchor",
            ha="center",
            va="center",
            fontweight="bold",
        )
        ax.grid(axis="y", color="#D5D9DF", lw=0.45, alpha=0.55)

        yearly = heatmap[heatmap['grid_id'] == gid].sort_values('year')
        mat = [yearly[col].to_numpy(dtype=float) for col, _ in heat_vars]
        axh = axes[ri, 1]
        im = axh.imshow(np.vstack(mat), aspect="auto", cmap="RdBu_r", vmin=-2, vmax=2)
        axh.set_yticks(np.arange(len(heat_vars)))
        axh.set_yticklabels([label for _, label in heat_vars])
        axh.set_xticks(np.arange(len(yearly)))
        axh.set_xticklabels(yearly["year"].astype(int), rotation=40, ha="right")
        axh.tick_params(length=0)
        if ri == 0:
            axh.set_title("Within-grid standardised covariates", loc="left")

        axf = axes[ri, 2]
        f = future_grid[future_grid["grid_id"] == gid].copy()
        f["tag_text"] = f["tag"].astype(str)
        f = f.set_index("tag_text").loc[TAG_ORDER]
        fv = f["annual_delta_gpp_cf_minus_factual_mean_2091_2100"] / 1e9
        bars = axf.bar(np.arange(4), fv, color=[BLUE, BLUE, RED, RED], edgecolor="white")
        axf.axhline(0, color=DARK, lw=0.8)
        axf.set_xticks(np.arange(4))
        axf.set_xticklabels([TAG_LABELS[t].replace("\n", " ") for t in TAG_ORDER], rotation=35, ha="right")
        axf.set_ylabel("10$^9$ g C yr$^{-1}$")
        if ri == 0:
            axf.set_title("Late-century fixed-area ΔGPP", loc="left")
        for bar, value in zip(bars, fv):
            axf.text(bar.get_x() + bar.get_width() / 2, value + np.sign(value) * max(abs(fv)) * 0.03, f"{value:.1f}", ha="center", va="bottom" if value >= 0 else "top", fontsize=7.5)
        axf.grid(axis="y", color="#D5D9DF", lw=0.45, alpha=0.55)
    fig.subplots_adjust(left=0.17, right=0.985, top=0.95, bottom=0.13, hspace=0.42, wspace=0.48)
    if im is not None:
        cax = fig.add_axes([0.4567, 0.045, 0.25, 0.018])
        cb = fig.colorbar(im, cax=cax, orientation="horizontal")
        cb.set_label("Within-grid z score")
    save(fig, "Figure_6")
