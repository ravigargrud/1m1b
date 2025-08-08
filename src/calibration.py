from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .data_models import SpeciesParams, co2_from_carbon_kg
from .growth_models import LogisticGrowth
import pandas as pd

CO2_PER_C = 44.0 / 12.0


def modeled_cseq_tco2_ha_per_year(sp: SpeciesParams, climate_factor: float, stems_per_ha: float, age_years: int = 10) -> float:
    """
    Approximate annual sequestration (tCO2/ha/yr) at a given age by differencing per-tree CO2 between age and age+1.
    Uses above+below biomass via root_shoot_ratio and carbon_fraction.
    """
    growth = LogisticGrowth(K=sp.K_biomass_kg, r=sp.r_growth * climate_factor, t0=sp.t0_inflection)
    above_t = growth.biomass_at(age_years)
    above_t1 = growth.biomass_at(age_years + 1)
    below_t = above_t * sp.root_shoot_ratio
    below_t1 = above_t1 * sp.root_shoot_ratio

    c_kg_t = (above_t + below_t) * sp.carbon_fraction
    c_kg_t1 = (above_t1 + below_t1) * sp.carbon_fraction
    delta_c_kg_per_tree = max(0.0, c_kg_t1 - c_kg_t)
    delta_co2_kg_per_tree = co2_from_carbon_kg(delta_c_kg_per_tree)

    tco2_ha_yr = (delta_co2_kg_per_tree * stems_per_ha) / 1000.0
    return tco2_ha_yr


def calibrate_climate_factor(sp: SpeciesParams, stems_per_ha: float, target_cseq_tco2_ha_yr: float, age_years: int = 10,
                              lo: float = 0.3, hi: float = 3.0, tol: float = 1e-3, max_iter: int = 60) -> tuple[float, float]:
    """
    Find climate_factor that makes modeled cseq match target (tCO2/ha/yr) near a given age.
    Returns (factor, modeled_at_factor).
    """
    # If baseline already close, return 1.0
    base = modeled_cseq_tco2_ha_per_year(sp, 1.0, stems_per_ha, age_years)
    if abs(base - target_cseq_tco2_ha_yr) <= tol:
        return 1.0, base

    # Bisection on monotonic response in r scaling
    lo_val = modeled_cseq_tco2_ha_per_year(sp, lo, stems_per_ha, age_years)
    hi_val = modeled_cseq_tco2_ha_per_year(sp, hi, stems_per_ha, age_years)

    # Ensure target is bracketed; if not, adjust ends
    # If both below target, increase hi
    expand_iter = 0
    while hi_val < target_cseq_tco2_ha_yr and expand_iter < 10:
        hi *= 1.5
        hi_val = modeled_cseq_tco2_ha_per_year(sp, hi, stems_per_ha, age_years)
        expand_iter += 1
    # If both above, decrease lo
    expand_iter = 0
    while lo_val > target_cseq_tco2_ha_yr and expand_iter < 10:
        lo *= 0.5
        lo_val = modeled_cseq_tco2_ha_per_year(sp, lo, stems_per_ha, age_years)
        expand_iter += 1

    a, fa = lo, lo_val
    b, fb = hi, hi_val
    for _ in range(max_iter):
        m = 0.5 * (a + b)
        fm = modeled_cseq_tco2_ha_per_year(sp, m, stems_per_ha, age_years)
        if abs(fm - target_cseq_tco2_ha_yr) <= tol:
            return m, fm
        # Decide which side to keep; response is monotonic increasing in factor
        if fm < target_cseq_tco2_ha_yr:
            a, fa = m, fm
        else:
            b, fb = m, fm
    return m, fm


def build_calibration_report(species_map: dict[str, SpeciesParams], benchmarks_df: pd.DataFrame, age_years: int = 10) -> pd.DataFrame:
    rows = []
    for _, r in benchmarks_df.iterrows():
        species_key = r.get("species_group")
        sp: Optional[SpeciesParams] = species_map.get(species_key)
        if sp is None:
            rows.append({
                "species": species_key,
                "region_class": r.get("region_class"),
                "stems_per_ha": r.get("stems_per_ha"),
                "target_cseq_tco2_ha_yr": float(r.get("cseq_mgc_ha_yr", 0.0)) * (44.0/12.0),
                "modeled_base_tco2_ha_yr": None,
                "recommended_climate_factor": None,
                "note": "species not found in species_params.csv"
            })
            continue
        target = float(r.get("cseq_mgc_ha_yr", 0.0)) * (44.0/12.0)
        stems = float(r.get("stems_per_ha", 0.0))
        base = modeled_cseq_tco2_ha_per_year(sp, 1.0, stems, age_years)
        factor, modeled = calibrate_climate_factor(sp, stems, target, age_years)
        rows.append({
            "species": species_key,
            "region_class": r.get("region_class"),
            "stems_per_ha": stems,
            "target_cseq_tco2_ha_yr": target,
            "modeled_base_tco2_ha_yr": base,
            "recommended_climate_factor": factor,
            "modeled_at_factor_tco2_ha_yr": modeled,
            "reference": r.get("reference"),
        })
    return pd.DataFrame(rows)
