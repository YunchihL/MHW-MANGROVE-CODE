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
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
NE_COUNTRIES_SHP = Path('world.shp')


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
    fig.savefig(out_svg)
    plt.close(fig)
    print(f"[OK] {out_png}")
    print(f"[OK] {out_svg}")

def _style_map_axis(ax: plt.Axes, extent: tuple[float, float, float, float]) -> None:
    if ccrs is None or shpreader is None:
        return
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.set_facecolor("#EAF2F8")
    if NE_COUNTRIES_SHP.exists():
        reader = shpreader.Reader(str(NE_COUNTRIES_SHP))
        countries = list(reader.geometries())
        ax.add_geometries(
            countries,
            crs=ccrs.PlateCarree(),
            facecolor="#F2F4F0",
            edgecolor="#7A8491",
            linewidth=0.32,
            zorder=1,
        )
    else:
        ax.set_facecolor("#F7FAFC")
    gl = ax.gridlines(draw_labels=True, linewidth=0.35, color="#CBD5E1", alpha=0.8, linestyle="-")
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 7.0}
    gl.ylabel_style = {"size": 7.0}

def plot() -> None:
    _set_gcb_style()
    annual = read_table(INPUT, 'main3_annual.csv').sort_values('year').reset_index(drop=True)
    df = read_table(INPUT, 'main3_spatial.csv')
    display = read_table(INPUT, 'main3_display.csv').iloc[0]
    positive_years = [2017, 2020]
    top10_share = float(display['top10_share'])
    top20pct_share = float(display['top20pct_share'])

    fig = plt.figure(figsize=(8.1, 3.15), constrained_layout=False)
    gs = fig.add_gridspec(1, 2, width_ratios=[0.88, 1.52], wspace=0.27)
    ax_annual = fig.add_subplot(gs[0, 0])
    ax_map = fig.add_subplot(gs[0, 1], projection=ccrs.PlateCarree())

    x = np.arange(len(annual))
    delta_tg_c = annual["delta_gpp"] / 1e12
    bar_colors = np.where(delta_tg_c >= 0, COLORS["positive"], COLORS["negative"])
    ax_annual.bar(
        x,
        delta_tg_c,
        color=bar_colors,
        edgecolor="white",
        linewidth=0.7,
        width=0.74,
    )
    ax_annual.axhline(0, color=COLORS["dark"], lw=0.9)
    positive_points: dict[int, tuple[int, float]] = {}
    for year in positive_years:
        xpos = int(np.where(annual["year"].to_numpy() == year)[0][0])
        value = float(delta_tg_c.iloc[xpos])
        positive_points[year] = (xpos, value)
        ax_annual.scatter(
            [xpos],
            [value],
            s=58,
            facecolor="none",
            edgecolor=COLORS["dark"],
            linewidth=1.1,
            zorder=5,
        )
    label_x = positive_points[2017][0] + 1.15
    label_y = 0.325
    ax_annual.annotate(
        "Positive years\n2017, 2020",
        xy=positive_points[2017],
        xytext=(label_x, label_y),
        arrowprops={
            "arrowstyle": "-|>",
            "lw": 0.75,
            "color": COLORS["dark"],
            "shrinkA": 2,
            "shrinkB": 3,
        },
        ha="left",
        va="center",
        fontsize=7.4,
        color=COLORS["dark"],
    )
    ax_annual.annotate(
        "",
        xy=positive_points[2020],
        xytext=(label_x + 0.55, label_y - 0.01),
        arrowprops={
            "arrowstyle": "-|>",
            "lw": 0.75,
            "color": COLORS["dark"],
            "shrinkA": 2,
            "shrinkB": 3,
        },
    )
    ax_annual.set_xticks(x)
    ax_annual.set_xticklabels(annual["year"].astype(str), rotation=40, ha="right")
    ax_annual.set_ylabel("Annual signed ΔGPP\n(Tg C yr$^{-1}$)")
    ax_annual.set_ylim(-0.66, 0.37)
    ax_annual.set_title("Annual signed differences", loc="left", pad=6)
    ax_annual.grid(axis="y", color=COLORS["grid"], lw=0.55, alpha=0.8)
    ax_annual.set_axisbelow(True)
    _panel_label(ax_annual, "a")
    ax_annual.legend(
        handles=[
            mpatches.Patch(facecolor=COLORS["negative"], edgecolor="none", label="ΔGPP < 0"),
            mpatches.Patch(facecolor=COLORS["positive"], edgecolor="none", label="ΔGPP > 0"),
        ],
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0.02, 0.98),
    )

    extent = (106.0, 142.5, -10.5, 4.5)
    _style_map_axis(ax_map, extent)
    ax_map.set_aspect("equal", adjustable="box")
    vmax = float(display['vmax'])
    norm = mpl.colors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "gcb_delta",
        ["#2B6CB0", "#EFF6FF", "#FEE2E2", "#B83232"],
    )
    regional = df[
        df["lon_c"].between(extent[0], extent[1])
        & df["lat_c"].between(extent[2], extent[3])
    ].copy()
    for row in regional.itertuples(index=False):
        ax_map.add_patch(
            Rectangle(
                (row.lon_c - 0.25, row.lat_c - 0.25),
                0.5,
                0.5,
                transform=ccrs.PlateCarree(),
                facecolor=cmap(norm(row.mean_bgc)),
                edgecolor="#FFFFFF",
                linewidth=0.18,
                alpha=0.96,
                zorder=4,
            )
        )
    ax_map.text(
        110.7,
        0.4,
        "Borneo",
        transform=ccrs.PlateCarree(),
        fontsize=7.8,
        color=COLORS["muted"],
        zorder=7,
    )
    ax_map.text(
        135.0,
        -3.2,
        "Papua",
        transform=ccrs.PlateCarree(),
        fontsize=7.8,
        color=COLORS["muted"],
        zorder=7,
    )
    ax_map.text(
        0.97,
        0.92,
        f"Top 10: {top10_share:.1f}%\nTop 20%: {top20pct_share:.1f}%",
        transform=ax_map.transAxes,
        ha="right",
        va="top",
        fontsize=8.0,
        fontweight="semibold",
        color=COLORS["dark"],
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "white",
            "edgecolor": "#C7D2DE",
            "linewidth": 0.8,
        },
        zorder=8,
    )
    ax_map.set_title("Grid-level mean annual ΔGPP", loc="left", pad=6)
    _panel_label(ax_map, "b")
    scalar = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    scalar.set_array([])
    colorbar = fig.colorbar(
        scalar,
        ax=ax_map,
        orientation="horizontal",
        fraction=0.046,
        pad=0.14,
        aspect=34,
    )
    colorbar.set_label("Mean annual ΔGPP (10$^9$ g C yr$^{-1}$)")

    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.23)
    out_stem = "Figure_3"
    _save(fig, out_stem)


