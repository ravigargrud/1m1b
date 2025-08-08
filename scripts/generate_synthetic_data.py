from __future__ import annotations
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Synthetic but plausible species parameters derived from literature ranges
species = [
    {
        "species": "Teak",
        "K_biomass_kg": 500.0,  # per-tree above-ground dry mass at maturity
        "r_growth": 0.30,
        "t0_inflection": 8.0,
        "carbon_fraction": 0.47,
        "root_shoot_ratio": 0.28,
    },
    {
        "species": "Eucalyptus",
        "K_biomass_kg": 400.0,
        "r_growth": 0.35,
        "t0_inflection": 6.0,
        "carbon_fraction": 0.47,
        "root_shoot_ratio": 0.25,
    },
    {
        "species": "Mangrove",
        "K_biomass_kg": 300.0,
        "r_growth": 0.25,
        "t0_inflection": 7.0,
        "carbon_fraction": 0.48,
        "root_shoot_ratio": 0.40,
    },
    # Added Himalayan species based on stand benchmarks
    {
        "species": "Sal",
        "K_biomass_kg": 600.0,
        "r_growth": 0.26,
        "t0_inflection": 9.0,
        "carbon_fraction": 0.47,
        "root_shoot_ratio": 0.28,
    },
    {
        "species": "ChirPine",
        "K_biomass_kg": 350.0,
        "r_growth": 0.24,
        "t0_inflection": 8.0,
        "carbon_fraction": 0.47,
        "root_shoot_ratio": 0.25,
    },
    {
        "species": "Oak",
        "K_biomass_kg": 400.0,
        "r_growth": 0.22,
        "t0_inflection": 10.0,
        "carbon_fraction": 0.48,
        "root_shoot_ratio": 0.35,
    },
]

regions = [
    {
        "region": "Tropical",
        "survival_rate_year1": 0.85,
        "annual_mortality_rate": 0.03,
        "climate_factor": 1.10,
    },
    {
        "region": "Subtropical",
        "survival_rate_year1": 0.80,
        "annual_mortality_rate": 0.04,
        "climate_factor": 1.00,
    },
    {
        "region": "Temperate",
        "survival_rate_year1": 0.75,
        "annual_mortality_rate": 0.05,
        "climate_factor": 0.90,
    },
]

scenarios = [
    {"scenario": "S-1K-Teak-Trop", "species": "Teak", "region": "Tropical", "trees_planted": 1000, "years": 20},
    {"scenario": "S-1K-Euca-Sub", "species": "Eucalyptus", "region": "Subtropical", "trees_planted": 1000, "years": 20},
    {"scenario": "S-500-Mang-Temp", "species": "Mangrove", "region": "Temperate", "trees_planted": 500, "years": 20},
    # New scenarios for added species
    {"scenario": "S-1K-Sal-Sub", "species": "Sal", "region": "Subtropical", "trees_planted": 1000, "years": 20},
    {"scenario": "S-1K-Pine-Temp", "species": "ChirPine", "region": "Temperate", "trees_planted": 1000, "years": 20},
    {"scenario": "S-1K-Oak-Temp", "species": "Oak", "region": "Temperate", "trees_planted": 1000, "years": 20},
]

pd.DataFrame(species).to_csv(DATA_DIR / "species_params.csv", index=False)
pd.DataFrame(regions).to_csv(DATA_DIR / "regions.csv", index=False)
pd.DataFrame(scenarios).to_csv(DATA_DIR / "scenarios.csv", index=False)

print(f"Wrote species, regions, scenarios to {DATA_DIR}")
