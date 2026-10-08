"""Render main manuscript figures 3-6 from externally supplied final tables."""
from __future__ import annotations
import argparse
import importlib
import os
from pathlib import Path
import tempfile

CHOICES = ['3', '4', '5', '6']

def main():
    parser = argparse.ArgumentParser(
        description='Render main figures 3-6 as PNG and SVG from final plotting tables.',
        epilog='Install environment/requirements-plotting.txt in Python 3.13. '
        'Inspect input_schema/tables.json for fields and units. Empty CSVs are templates, not data. '
        'Figure 3 optionally reads a separately supplied Natural Earth 110m countries shapefile. '
        'Future panels display the final 2091-2100 summaries only. '
        'Model implementation is provided separately for inspection. Data, training, '
        'prediction generation, statistical estimation and supplementary figures are not included.',
    )
    parser.add_argument('--input-dir', type=Path, required=True, help='Directory containing final plotting tables')
    parser.add_argument('--output-dir', type=Path, required=True, help='Destination for PNG and SVG files')
    parser.add_argument('--figures', nargs='+', choices=CHOICES, default=CHOICES, help='Main figure numbers; default: 3 4 5 6')
    parser.add_argument('--world-shapefile', type=Path, help='Optional Natural Earth countries .shp, with .shx/.dbf/.prj companions')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'mhw-plot-matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    for figure in args.figures:
        module = importlib.import_module(f'plotting.main_figure{figure}')
        module.INPUT = args.input_dir.resolve()
        module.OUT = args.output_dir.resolve()
        if args.world_shapefile:
            if not args.world_shapefile.is_file():
                parser.error(f'Missing --world-shapefile: {args.world_shapefile}')
            module.NE_COUNTRIES_SHP = args.world_shapefile.resolve()
        try:
            module.plot()
        except (FileNotFoundError, ValueError) as exc:
            parser.exit(2, f'Figure {figure}: {exc}\n')
        print(f'Figure {figure}: {args.output_dir}')

if __name__ == '__main__':
    main()
