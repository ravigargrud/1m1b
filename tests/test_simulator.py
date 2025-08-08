from __future__ import annotations
import pandas as pd
from src.data_models import SpeciesParams, RegionParams, Scenario
from src.simulator import Simulator

species = {
    "Test": SpeciesParams(
        species="Test",
        K_biomass_kg=100.0,
        r_growth=0.5,
        t0_inflection=5.0,
        carbon_fraction=0.47,
        root_shoot_ratio=0.3,
    )
}
regions = {
    "TestRegion": RegionParams(
        region="TestRegion",
        survival_rate_year1=0.8,
        annual_mortality_rate=0.05,
        climate_factor=1.0,
    )
}

def test_simulation_reasonable_outputs():
    sim = Simulator(species, regions)
    sc = Scenario(scenario="test", species="Test", region="TestRegion", trees_planted=1000, years=20)
    out = sim.run(sc)
    df = out.to_dataframe()
    # totals must be non-negative and start at zero year >= 0
    assert (df["total_co2_tons"] >= 0).all()
    # per-tree biomass should be non-decreasing with logistic model
    assert (df["co2_kg_per_tree"].diff().fillna(0) >= -1e-6).all()
    # living trees should not increase over time
    assert (df["living_trees"].diff().fillna(0) <= 1e-6).all()
