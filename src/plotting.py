from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")


def plot_total_co2(df: pd.DataFrame, title: str = "Total CO₂ (tons)"):
    plt.figure(figsize=(8, 4))
    sns.lineplot(data=df, x="year", y="total_co2_tons")
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel("CO₂ (tons)")
    plt.tight_layout()
    return plt.gcf()


def plot_per_tree_co2(df: pd.DataFrame, title: str = "Per-tree CO₂ (kg)"):
    plt.figure(figsize=(8, 4))
    sns.lineplot(data=df, x="year", y="co2_kg_per_tree")
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel("CO₂ per tree (kg)")
    plt.tight_layout()
    return plt.gcf()
