"""Read externally supplied final plotting tables using the empty input schemas."""
import json
from pathlib import Path
import pandas as pd

SCHEMA_DIR = Path(__file__).resolve().parents[1] / 'input_schema'

def read_table(input_dir: Path, filename: str) -> pd.DataFrame:
    path = input_dir / filename
    if not path.is_file():
        raise FileNotFoundError(
            f'Missing final plotting table: {path}. Research data are not bundled; '
            f'input_schema/{filename} contains column headers only.'
        )
    schema = json.loads((SCHEMA_DIR / 'tables.json').read_text())[filename]
    frame = pd.read_csv(path)
    missing = set(schema['columns']) - set(frame.columns)
    if missing:
        raise ValueError(f'{filename}: missing columns {sorted(missing)}')
    if frame.empty:
        raise ValueError(f'{filename}: header-only template; supply the final plotting values')
    return frame[schema['columns']].copy()
