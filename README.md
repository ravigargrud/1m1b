# Afforestation Impact Modeling

A Python project to model CO₂ sequestration from tree-planting initiatives over 10–20 years.

## Features
- Species-specific sequestration modeling
- Regional growth and survival integration
- Scenario simulations for planting strategies
- Interactive Streamlit app and plots

## Quickstart
1. Create and activate a virtual environment
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv; .\.venv\Scripts\Activate.ps1
     ```
    - macOS / Linux (bash/zsh):
     ```bash
     python3 -m venv .venv && source .venv/bin/activate
     ```

2. Install requirements
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Generate synthetic datasets and run a demo simulation
   ```powershell
   python scripts\generate_synthetic_data.py; python scripts\run_demo.py
   ```
4. Launch the Streamlit app
   ```powershell
   streamlit run app\app.py
   ```

## Project Structure
```
├─ app/
│  └─ app.py
├─ data/
│  ├─ species_params.csv
│  ├─ regions.csv
│  └─ scenarios.csv
├─ notebooks/
├─ scripts/
│  ├─ generate_synthetic_data.py
│  └─ run_demo.py
├─ src/
│  ├─ __init__.py
│  ├─ data_models.py
│  ├─ growth_models.py
│  ├─ simulator.py
│  ├─ analysis.py
│  └─ plotting.py
├─ tests/
│  └─ test_simulator.py
├─ requirements.txt
└─ README.md
```

## Outputs
- CSVs of yearly biomass and CO₂ per scenario
- Plots in `outputs/`

## License
MIT
