from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.data_models import SpeciesParams
from src.calibration import build_calibration_report

DATA = ROOT / "data"

species_df = pd.read_csv(DATA / "species_params.csv")
bench_df = pd.read_csv(DATA / "stand_benchmarks.csv")

# Map species groups to existing keys if possible; here we assume names match or are simple synonyms
alias = {
    # examples if you later add Sal/ChirPine/Oak
    # "Sal": "Teak",  # if you want to borrow Teak params as a placeholder
}

def normalize_species(s: str) -> str:
    return alias.get(s, s)

species_df["species"] = species_df["species"].astype(str)
species_map = {row["species"]: SpeciesParams(**row) for row in species_df.to_dict(orient="records")}
bench_df["species_group"] = bench_df["species_group"].map(normalize_species)

report = build_calibration_report(species_map, bench_df, age_years=10)

OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
report_path = OUT / "calibration_report.csv"
report.to_csv(report_path, index=False)
print(f"Wrote calibration report to {report_path}")
print(report)
