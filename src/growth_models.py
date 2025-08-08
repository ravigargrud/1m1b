from __future__ import annotations
from dataclasses import dataclass
from math import exp

@dataclass
class LogisticGrowth:
    K: float  # carrying capacity
    r: float  # intrinsic growth rate
    t0: float  # inflection point

    def biomass_at(self, t_years: float) -> float:
        # Logistic function: K / (1 + exp(-r (t - t0)))
        return self.K / (1.0 + exp(-self.r * (t_years - self.t0)))


def annual_survival(starting: float, year: int, p_year1: float, p_mortality: float) -> float:
    """
    Compute expected number of living trees in a cohort given survival probabilities.
    - year 0: planting
    - after first year: multiply by survival_rate_year1
    - each subsequent year: multiply by (1 - annual_mortality_rate)
    Returns expected number of living trees (can be non-integer expected value).
    """
    if year <= 0:
        return starting
    if year == 1:
        return starting * p_year1
    # year >= 2
    return starting * p_year1 * ((1.0 - p_mortality) ** (year - 1))
