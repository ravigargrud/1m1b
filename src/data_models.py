from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional

CarbonUnit = Literal["kgCO2", "tCO2"]

class SpeciesParams(BaseModel):
    species: str
    # Logistic growth params for above-ground biomass (kg dry mass per tree)
    K_biomass_kg: float = Field(gt=0, description="Carrying capacity of biomass per tree")
    r_growth: float = Field(gt=0, description="Intrinsic growth rate per year")
    t0_inflection: float = Field(description="Inflection year for logistic growth")
    carbon_fraction: float = Field(gt=0, lt=1, description="Fraction of dry biomass that is carbon (~0.47)")
    root_shoot_ratio: float = Field(gt=0, description="Below-ground to above-ground biomass ratio (0.2–0.4 typical)")

class RegionParams(BaseModel):
    region: str
    survival_rate_year1: float = Field(gt=0, lt=1)
    annual_mortality_rate: float = Field(ge=0, lt=1, description="Probability a tree dies each year after year 1")
    climate_factor: float = Field(gt=0, description="Multiplier on growth rate due to climate/soil (e.g., 0.8–1.2)")

class Scenario(BaseModel):
    scenario: str
    species: str
    region: str
    trees_planted: int = Field(gt=0)
    years: int = Field(ge=1, le=100)

class YearlyResult(BaseModel):
    year: int
    living_trees: float
    above_biomass_kg_per_tree: float
    below_biomass_kg_per_tree: float
    carbon_kg_per_tree: float
    co2_kg_per_tree: float
    total_co2_tons: float

class SimulationOutput(BaseModel):
    scenario: Scenario
    yearly: list[YearlyResult]

    def to_dataframe(self):
        import pandas as pd
        return pd.DataFrame([r.model_dump() for r in self.yearly])

# Utility
def co2_from_carbon_kg(c_kg: float) -> float:
    # Molecular weight ratio CO2/C = 44/12
    return c_kg * (44.0 / 12.0)
