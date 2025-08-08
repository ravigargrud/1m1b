from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.data_models import SpeciesParams, RegionParams, Scenario
from src.simulator import Simulator
from src.analysis import summarize_simulation
from src.plotting import plot_total_co2

DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

species_df = pd.read_csv(DATA / "species_params.csv")
regions_df = pd.read_csv(DATA / "regions.csv")
scenarios_df = pd.read_csv(DATA / "scenarios.csv")

species = {r["species"]: SpeciesParams(**r) for r in species_df.to_dict(orient="records")}
regions = {r["region"]: RegionParams(**r) for r in regions_df.to_dict(orient="records")}

sim = Simulator(species, regions)

for row in scenarios_df.to_dict(orient="records"):
    sc = Scenario(**row)
    out = sim.run(sc)
    df = out.to_dataframe()
    df.to_csv(OUT / f"{sc.scenario}_yearly.csv", index=False)
    fig = plot_total_co2(df, title=f"Total CO₂ (tons): {sc.scenario}")
    fig.savefig(OUT / f"{sc.scenario}_total_co2.png", dpi=150, bbox_inches="tight")
    sm = summarize_simulation(df)
    sm.to_csv(OUT / f"{sc.scenario}_summary.csv", index=False)
    print(sm.to_string(index=False))

print(f"Results written to {OUT}")
