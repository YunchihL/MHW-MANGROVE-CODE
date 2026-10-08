# Mangrove MHW–GPP: model and main-figure code

Selected code for research on marine heatwaves (MHWs), mangrove gross primary productivity (GPP), and future scenarios. This release contains the basic Temporal Fusion Transformer (TFT) model factory and plotting scripts for main Figures 3–6.

## Files

| File | Purpose |
| --- | --- |
| `model/tft_model.py` | Constructs the TFT using `pytorch-forecasting`; contains no training loop or weights. |
| `model/inspect_model.py` | Inspects the model factory and optionally the installed TFT source without constructing a model. |
| `model/__init__.py` | Defines the model Python package. |
| `plot_figures.py` | Command-line entry point for rendering Figures 3–6 as PNG and SVG. |
| `plotting/main_figure3.py` | Draws annual and spatial historical ΔGPP patterns. |
| `plotting/main_figure4.py` | Draws historical patterns by year, month, and latitude. |
| `plotting/main_figure5.py` | Draws scenario comparisons, fixed-area GPP summaries, and area-scenario ranges. |
| `plotting/main_figure6.py` | Draws representative-grid historical and future summaries and driver heatmaps. |
| `plotting/io.py` | Reads final plotting tables and checks required columns and non-empty inputs. |
| `plotting/__init__.py` | Defines the plotting Python package. |
| `environment/requirements-model.txt` | Dependencies for model inspection in Python 3.10. |
| `environment/requirements-plotting.txt` | Dependencies for plotting in Python 3.13. |
| `input_schema/tables.json` | Required table columns, units, and figure assignments. |
| `.gitignore` | Excludes common local caches, environments, and generated outputs. |
| `README.md` | Describes this release and how to inspect or run it. |

All CSV files below are **header-only templates**, not research data:

| Template in `input_schema/` | Purpose |
| --- | --- |
| `main3_annual.csv` | Annual historical ΔGPP totals. |
| `main3_spatial.csv` | Grid coordinates and spatial ΔGPP values. |
| `main3_display.csv` | Precomputed contribution shares and map colour limit. |
| `main4_positive_years.csv` | Summaries for positive-total years. |
| `main4_negative_years_summary.csv` | Precomputed summaries for negative-total years. |
| `main4_month.csv` | Monthly positive and negative shares. |
| `main4_latitude.csv` | Positive and negative shares by latitude. |
| `main5_hazard.csv` | Precomputed hazard ratios and confidence intervals. |
| `main5_fixed.csv` | Fixed-area scenario GPP summaries for 2091–2100. |
| `main5_area_ranges.csv` | Precomputed minimum, mean, and maximum area-scenario ratios. |
| `main6_historical.csv` | Annual historical ΔGPP for representative grids. |
| `main6_future.csv` | Representative-grid scenario means for 2091–2100. |
| `main6_heatmap.csv` | Already-standardised driver values for heatmaps. |
| `main6_labels.csv` | Representative-grid display labels. |

## Running the code

Use separate environments for model inspection and plotting. From the repository root:

```bash
# Python 3.10: inspect the model implementation
python -m pip install -r environment/requirements-model.txt
python -m model.inspect_model
python -m model.inspect_model --show-core
```

```bash
# Python 3.13: render figures after obtaining populated final plotting tables
python -m pip install -r environment/requirements-plotting.txt
python plot_figures.py --input-dir /path/to/final_tables --output-dir outputs --figures 3 4 5 6
```

Figure 3 optionally accepts `--world-shapefile /path/to/countries.shp`, with its companion shapefile files. Future panels show 2091–2100 summaries only. Empty templates are intentionally rejected as plotting inputs.

## Scope and citation

This release does not include training scripts, trained weights, research data, prediction-generation workflows, statistical-estimation workflows, or supplementary-figure scripts. The model implementation is available for inspection; it cannot regenerate the manuscript predictions without the omitted materials. Plotting requires populated final tables supplied separately.

**Prior authorization from the repository owner is required before citing this repository or its code in a publication.** Please contact [YunchihL](https://github.com/YunchihL) to request authorization.

**Additional code will be added in future updates.**
