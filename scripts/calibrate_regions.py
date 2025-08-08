from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.data_models import SpeciesParams
from src.calibration import calibrate_climate_factor

DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

species_df = pd.read_csv(DATA / "species_params.csv")
bench_df = pd.read_csv(DATA / "stand_benchmarks.csv")
regions_df = pd.read_csv(DATA / "regions.csv")

species_map = {row["species"]: SpeciesParams(**row) for row in species_df.to_dict(orient="records")}

# Fallback reference if a benchmark species is not present in species_map
region_ref_species = {
    "Subtropical": "Sal",
    "Temperate": "Oak",
    "Tropical": "Teak",
}

rows = []
for region_class, grp in bench_df.groupby("region_class"):
    factors = []
    for _, r in grp.iterrows():
        bench_species = str(r.get("species_group")) if not pd.isna(r.get("species_group")) else None
        # Prefer species-specific parameters if available
        sp_key = bench_species if bench_species in species_map else region_ref_species.get(region_class)
        sp = species_map.get(sp_key)
        if sp is None:
            continue
        cseq_mgc = r.get("cseq_mgc_ha_yr")
        stems = r.get("stems_per_ha")
        if pd.isna(cseq_mgc) or pd.isna(stems) or stems <= 0:
            continue
        target_tco2 = float(cseq_mgc) * (44.0/12.0)
        fac, modeled = calibrate_climate_factor(sp, float(stems), target_tco2, age_years=10)
        factors.append(fac)
    if factors:
        rec = sum(factors) / len(factors)
        rows.append({"region": region_class, "recommended_climate_factor": rec, "n_benchmarks": len(factors)})

overrides = pd.DataFrame(rows)
overrides_path = DATA / "region_calibration_overrides.csv"
overrides.to_csv(overrides_path, index=False)
print(f"Wrote overrides to {overrides_path}")
print(overrides)

# Produce a calibrated regions file without overwriting the original
cal_regions = regions_df.copy()
cal_regions = cal_regions.merge(overrides[["region", "recommended_climate_factor"]], on="region", how="left")
cal_regions["climate_factor"] = cal_regions["recommended_climate_factor"].fillna(cal_regions["climate_factor"])
cal_regions.drop(columns=[c for c in ["recommended_climate_factor"] if c in cal_regions.columns], inplace=True)
cal_regions_path = DATA / "regions_calibrated.csv"
cal_regions.to_csv(cal_regions_path, index=False)
print(f"Wrote calibrated regions to {cal_regions_path}")
