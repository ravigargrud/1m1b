from __future__ import annotations
from typing import Dict
from .data_models import SpeciesParams, RegionParams, Scenario, YearlyResult, SimulationOutput, co2_from_carbon_kg
from .growth_models import LogisticGrowth, annual_survival

import math

class Simulator:
    def __init__(self, species: Dict[str, SpeciesParams], regions: Dict[str, RegionParams]):
        self.species = species
        self.regions = regions

    def run(self, scenario: Scenario) -> SimulationOutput:
        sp = self.species[scenario.species]
        rg = self.regions[scenario.region]

        growth = LogisticGrowth(K=sp.K_biomass_kg, r=sp.r_growth * rg.climate_factor, t0=sp.t0_inflection)

        yearly: list[YearlyResult] = []
        for year in range(0, scenario.years + 1):
            above_kg = growth.biomass_at(year)
            below_kg = above_kg * sp.root_shoot_ratio
            total_biomass = above_kg + below_kg
            carbon_kg_per_tree = total_biomass * sp.carbon_fraction
            co2_kg_per_tree = co2_from_carbon_kg(carbon_kg_per_tree)

            living = annual_survival(
                starting=scenario.trees_planted,
                year=year,
                p_year1=rg.survival_rate_year1,
                p_mortality=rg.annual_mortality_rate,
            )
            total_co2_tons = (living * co2_kg_per_tree) / 1000.0

            yearly.append(
                YearlyResult(
                    year=year,
                    living_trees=living,
                    above_biomass_kg_per_tree=above_kg,
                    below_biomass_kg_per_tree=below_kg,
                    carbon_kg_per_tree=carbon_kg_per_tree,
                    co2_kg_per_tree=co2_kg_per_tree,
                    total_co2_tons=total_co2_tons,
                )
            )

        return SimulationOutput(scenario=scenario, yearly=yearly)
