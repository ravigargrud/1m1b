from __future__ import annotations
import pandas as pd


def summarize_simulation(df: pd.DataFrame) -> pd.DataFrame:
    last = df.sort_values("year").iloc[-1]
    summary = {
        "years": int(last["year"]),
        "final_living_trees": float(last["living_trees"]),
        "final_total_co2_tons": float(last["total_co2_tons"]),
        "avg_co2_tons_per_year": float(df["total_co2_tons"].diff().fillna(df["total_co2_tons"]).mean()),
        "peak_yearly_increment_tons": float(df["total_co2_tons"].diff().max()),
    }
    return pd.DataFrame([summary])
