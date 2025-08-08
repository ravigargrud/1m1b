from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
from src.data_models import SpeciesParams, RegionParams, Scenario
from src.simulator import Simulator
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Afforestation Impact Modeling", page_icon="🌳", layout="wide")

# Theme-aware green accents
GREEN_SEQ = ["#2ea043", "#22863a", "#34d399", "#065f46", "#bbf7d0"]
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = GREEN_SEQ

# Subtle style tweaks
st.markdown(
    """
    <style>
      div.stMetric { padding: 0.5rem 0.75rem; border: 1px solid #d1fae5; border-radius: 10px; background: #ffffff; }
      .block-container { padding-top: 1.3rem; }
      h1, h2, h3 { color: #0b3d2e !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

@st.cache_data
def load_data():
    species_df = pd.read_csv(DATA / "species_params.csv")
    # Prefer calibrated regions if present
    regions_path = DATA / "regions_calibrated.csv"
    regions_source = "regions_calibrated.csv" if regions_path.exists() else "regions.csv"
    if not regions_path.exists():
        regions_path = DATA / "regions.csv"
    regions_df = pd.read_csv(regions_path)
    species = {r["species"]: SpeciesParams(**r) for r in species_df.to_dict(orient="records")}
    regions = {r["region"]: RegionParams(**r) for r in regions_df.to_dict(orient="records")}
    # Benchmarks optional
    bench_path = DATA / "stand_benchmarks.csv"
    benchmarks_df = pd.read_csv(bench_path) if bench_path.exists() else None
    return species, regions, regions_source, benchmarks_df

species, regions, regions_source, benchmarks_df = load_data()

st.title("Afforestation Impact Modeling")

# Sidebar controls and info
with st.sidebar:
    st.header("Setup")
    species_name = st.selectbox("Species", list(species.keys()))
    region_name = st.selectbox("Region", list(regions.keys()))
    trees = st.number_input("Trees planted", min_value=100, max_value=200000, value=1000, step=100)
    years = st.slider("Years", min_value=5, max_value=40, value=20, step=1)
    st.divider()
    st.caption(f"Regions source: {regions_source}")
    show_per_ha = st.checkbox("Enable per-hectare metrics", value=False)
    stems_per_ha = None
    if show_per_ha:
        stems_per_ha = st.number_input("Stems per hectare (for per-ha conversion)", min_value=100, max_value=5000, value=1000, step=50)
    st.divider()
    sp = species[species_name]
    with st.expander("Species parameters", expanded=False):
        st.json({
            "K_biomass_kg (above-ground)": sp.K_biomass_kg,
            "r_growth": sp.r_growth,
            "t0_inflection": sp.t0_inflection,
            "carbon_fraction": sp.carbon_fraction,
            "root_shoot_ratio": sp.root_shoot_ratio,
        })
    rg = regions[region_name]
    with st.expander("Region parameters", expanded=False):
        st.json({
            "survival_rate_year1": rg.survival_rate_year1,
            "annual_mortality_rate": rg.annual_mortality_rate,
            "climate_factor": rg.climate_factor,
        })

sc = Scenario(scenario=f"custom-{species_name}-{region_name}", species=species_name, region=region_name, trees_planted=int(trees), years=int(years))

sim = Simulator(species, regions)
out = sim.run(sc)
df = out.to_dataframe()
# Derived metrics
df["annual_increment_tons"] = df["total_co2_tons"].diff().fillna(df["total_co2_tons"]).clip(lower=0)

# Metrics row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Final CO₂ (tons)", f"{df['total_co2_tons'].iloc[-1]:.1f}")
with c2:
    st.metric("Avg annual increment (t/yr)", f"{df['annual_increment_tons'].mean():.2f}")
with c3:
    st.metric("Peak annual increment (t/yr)", f"{df['annual_increment_tons'].max():.2f}")
with c4:
    st.metric("Final living trees", f"{df['living_trees'].iloc[-1]:.0f}")

# Tabs for richer visuals
overview_tab, per_tree_tab, per_ha_tab, benchmarks_tab = st.tabs([
    "Overview",
    "Per tree",
    "Per hectare",
    "Benchmarks",
])

with overview_tab:
    st.subheader("Total CO₂ sequestered (tons)")
    fig_total = px.line(df, x="year", y="total_co2_tons", title=None, template="plotly_white")
    fig_total.update_traces(line=dict(width=3))
    st.plotly_chart(fig_total, use_container_width=True)

    st.subheader("Annual CO₂ increment (tons/year)")
    fig_inc = px.bar(df, x="year", y="annual_increment_tons", title=None, template="plotly_white")
    st.plotly_chart(fig_inc, use_container_width=True)

with per_tree_tab:
    st.subheader("Per-tree CO₂ (kg)")
    fig_pt = px.line(df, x="year", y="co2_kg_per_tree", labels={"co2_kg_per_tree": "kg CO₂ per tree"}, template="plotly_white")
    fig_pt.update_traces(line=dict(width=3))
    st.plotly_chart(fig_pt, use_container_width=True)

    st.subheader("Per-tree biomass breakdown (final year)")
    last = df.iloc[-1]
    above = last["above_biomass_kg_per_tree"]
    below = last["below_biomass_kg_per_tree"]
    pie_df = pd.DataFrame({"component": ["Above-ground", "Below-ground"], "kg": [above, below]})
    fig_pie = px.pie(pie_df, names="component", values="kg", hole=0.45, template="plotly_white")
    st.plotly_chart(fig_pie, use_container_width=True)

with per_ha_tab:
    st.subheader("Per-hectare metrics (requires stems/ha)")
    if show_per_ha and stems_per_ha and stems_per_ha > 0:
        # area in ha implied by planting density
        area_ha = trees / stems_per_ha
        df_ha = df.copy()
        df_ha["total_tco2_per_ha"] = df_ha["total_co2_tons"] / max(area_ha, 1e-9)
        df_ha["annual_tco2_per_ha"] = df_ha["annual_increment_tons"] / max(area_ha, 1e-9)
        c5, c6 = st.columns(2)
        with c5:
            st.metric("Final total (tCO₂/ha)", f"{df_ha['total_tco2_per_ha'].iloc[-1]:.1f}")
        with c6:
            st.metric("Avg annual (tCO₂/ha/yr)", f"{df_ha['annual_tco2_per_ha'].mean():.2f}")
        fig_ha_total = px.line(df_ha, x="year", y="total_tco2_per_ha", title="Total tCO₂/ha", template="plotly_white")
        st.plotly_chart(fig_ha_total, use_container_width=True)
        fig_ha_inc = px.bar(df_ha, x="year", y="annual_tco2_per_ha", title="Annual tCO₂/ha/yr", template="plotly_white")
        st.plotly_chart(fig_ha_inc, use_container_width=True)
        st.dataframe(df_ha[["year", "total_tco2_per_ha", "annual_tco2_per_ha"]].round(3).tail(10), use_container_width=True)
    else:
        st.info("Enable per-hectare metrics and set stems per hectare in the sidebar to view these charts.")

with benchmarks_tab:
    st.subheader("Compare with stand benchmarks")
    if benchmarks_df is None:
        st.info("No stand_benchmarks.csv found in data/.")
    else:
        region_class = region_name  # assuming same labels (Tropical/Subtropical/Temperate)
        bench = benchmarks_df[benchmarks_df["region_class"] == region_class].copy()
        if bench.empty:
            st.info(f"No benchmarks for region '{region_class}'.")
        else:
            bench["tco2_ha_yr"] = bench["cseq_mgc_ha_yr"].astype(float) * (44.0/12.0)
            show_species_only = st.checkbox("Filter to matching species group (if available)", value=False)
            if show_species_only:
                bench = bench[bench["species_group"].astype(str).str.lower() == species_name.lower()]
            st.dataframe(bench[["forest_type", "location", "stems_per_ha", "tco2_ha_yr", "reference"]], use_container_width=True)

            if show_per_ha and stems_per_ha and stems_per_ha > 0:
                # Model's average annual per-ha increment
                area_ha = trees / stems_per_ha
                modeled = df["annual_increment_tons"].mean() / max(area_ha, 1e-9)
                comp_df = pd.DataFrame({
                    "Type": ["Modeled"] + bench["forest_type"].tolist(),
                    "tco2_ha_yr": [modeled] + bench["tco2_ha_yr"].tolist(),
                })
                fig_cmp = px.bar(comp_df, x="Type", y="tco2_ha_yr", title="Annual tCO₂/ha/yr: Model vs Benchmarks", template="plotly_white")
                st.plotly_chart(fig_cmp, use_container_width=True)
            else:
                st.info("To compare quantitatively, enable per-hectare metrics and set stems/ha in the sidebar.")

st.download_button("Download yearly CSV", data=df.to_csv(index=False), file_name=f"{sc.scenario}_yearly.csv", mime="text/csv")
