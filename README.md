# Electric Vehicle Analysis — Washington State

This project cleans, transforms, plots and explores (*EDA*) the data on electric vehicles (BEVs and PHEVs) registered in Washington State. The goal is to understand the adoption of clean transport technology, the evolution of battery range and the *market share* trends among manufacturers.

---

## Data Source

The data is published by the *Washington State Department of Licensing* (DOL) and is available on the Washington State open data portal: [data.wa.gov](https://data.wa.gov).

The file used is `Electric_Vehicle_Population_Data_20260122.csv`, holding roughly **271 thousand records** of electric vehicles registered in the state. It is a frozen snapshot, taken on 2026-01-22: the live file is updated continuously, and refreshing it would silently change every count below.

---

## Project Layout

```text
data/raw/          the frozen DOL export, never modified in place
data/processed/    the cleaned export, written by I-cleaning
notebooks/         the narrative; calls into src/, does not duplicate it
src/               cleaning.py, viz.py, utils.py — all reusable logic
tests/             the pytest suite for the pure functions in src/
images/            exported PNGs
```

The analysis is split across two *notebooks*:

| Notebook | Description |
| --- | --- |
| `I-cleaning.ipynb` | Initial exploration, cleaning and transformation |
| `II-analysis.ipynb` | Visualisations, analysis and *insights* |

Both are written to run **from the repository root**, not from `notebooks/`. Locally, `.vscode/settings.json` already points VS Code's Jupyter root at the workspace folder; on Colab and Kaggle, the setup cell at the top of each notebook clones the repository and moves into it.

---

## Questions the Analysis Asks

- **Growth over time:** how has the adoption of EVs evolved across the years?
- **Distribution by manufacturer:** which makes dominate the fleet?
- **Mean range:** how has battery capacity evolved by model year?
- **Location:** which cities hold the highest density of electric vehicles?
- ***Market share*:** what is each manufacturer's real slice of the market, as a percentage?

---

## Cleaning Steps (`I-cleaning.ipynb`)

1. **Removal of incomplete rows** — 10 rows holding *NaN* in fields such as city and county were removed. In a *dataframe* of ~271 thousand rows, the loss is negligible.
2. **Geographic filter** — rows registered outside Washington State were removed (649 records), keeping the analysis in focus.
3. **Unusable range** — any `Electric Range` outside what the row's own vehicle type can reach was replaced with *NaN*, since it cannot be a measurement of that vehicle. It removes three things: the `0` the DOL writes for a battery it has not researched, the `1` carried by 32 model year 2025 Mercedes-Benz plug-ins, and the `29` on 8 rows badged BEV, which is the published figure for the *plug-in* Hyundai IONIQ. Genuinely low ratings, such as the 6 miles of the 2012–2015 Prius Plug-in, survive. A status read off a range that went is dropped with it, so every `CAFV Status` in the export is one the range column still accounts for.
4. **Removal of irrelevant columns** — dropped: `VIN (1-10)`, `State`, `Postal Code`, `Legislative District`, `DOL Vehicle ID` and `2020 Census Tract`, none of which serve the questions above.
5. **Coordinates** — `Vehicle Location` is kept and parsed into `Longitude` and `Latitude`, because it is what figure 3 is drawn from. The DOL geocodes each registration to the centroid of its postal area rather than to an address, so 270 thousand vehicles sit on 825 distinct points; 78 rows carry no location and keep *NaN*.
6. **Creation of the `Vehicle Age` column** — calculated as `2026 - Model Year`, the vehicle's age in years, measured against the year of the snapshot.
7. **Name standardisation** — the `Clean Alternative Fuel Vehicle (CAFV) Eligibility` column was renamed to `CAFV Status` and its values shortened, and the vehicle types were abbreviated to `BEV` and `PHEV`. Three cities the source spells two ways (Sedro-Woolley, Silverlake, McCleary) were collapsed onto one spelling each, which is why the fleet covers 491 cities and not the 494 a naive count reports.
8. **Cleaning of the `Electric Utility` column** — only the first provider is kept, since the source packs several into one field, and the trailing `- (WA)` and `INC` are stripped from it. `No Known Electric Utility Service` records the absence of a provider rather than a provider, so those 350 rows became *NaN*, which is why the column holds 19 names and not 20.
9. **Outlier check** — the quartile method (IQR) applied. The *outliers* it finds, such as a 1999 Ford Ranger, were kept, because they are true records inside a *dataset* that spans 27 years. A separate plausibility check, run against bounds taken from the domain rather than from the distribution, catches what the quartiles structurally cannot.
10. **Export check** — `cleaning.check_export` raises unless the finished frame holds every promise the cleaning makes about it: no range impossible for its own vehicle type, no CAFV ruling left behind by the range it was read off, no vehicle age disagreeing with its model year, no city under two spellings and no empty value in a field that should never be empty.

---

## Analysis and Visualisations (`II-analysis.ipynb`)

### Part II — Fleet Overview

| Figure | Chart | Description |
| --- | --- | --- |
| Fig. 1 | Grouped bars | Top 10 makes: share of the whole fleet against share of model years 2024 onwards |
| Fig. 2 | Area | Model year profile of the fleet |
| Fig. 3 | Map | Where the fleet is registered — one bubble per geocoded point, sized by registrations |

The BEV/PHEV split is given as a table rather than a chart: two numbers do not need a pie. *CAFV* eligibility is not charted at all, because the rule `Electric Range >= 30` explains 100% of the statuses the DOL has ruled on — the column repeats the range column, and a chart of it would silently show 37% of the fleet.

### Part III — Range and Technological Evolution

| Figure | Chart | Description |
| --- | --- | --- |
| Fig. 4 | Lines | Median range by model year and type, drawn only where the DOL researched it |
| Fig. 5 | *Scatter plot* | Mean range against volume per model, 2015 – 2019 |
| Fig. 6 | *Scatter plot* | Mean range against volume per model, 2020 – 2026 |

Figure 4 answers the question directly and shows what the file cannot answer: the BEV line stops at model year 2020, because from 2021 on the DOL researched the range of 4% of them and then none at all, while plug-in coverage stays at 100% throughout. The two *scatter plots* then set the number of registrations against the mean range per model. Only models with researched coverage appear on them, so that both axes of a point describe the same vehicles — which is why the 2020 – 2026 chart holds 17% of that window's registrations and almost no BEVs.

### Part IV — *Market Share*

A table of every make's share of the fleet, with no chart. The treemap that used to sit here repeated figure 1's top ten in the same order, and rounding each share to one decimal gave twelve real makes an area of zero.

---

## The Columns

Below are the columns of the original *dataset*. The ~~struck through~~ ones were removed during cleaning; the **bold** ones were used in the analysis.

| Original Column | Status | Description |
| --- | --- | --- |
| ~~VIN (1-10)~~ | Removed | The vehicle's chassis number |
| **County** | Kept | County the vehicle is registered in |
| **City** | Kept | City the vehicle is registered in |
| ~~State~~ | Removed | State (all of them Washington) |
| ~~Postal Code~~ | Removed | Postal code |
| **Model Year** | Kept | Year the vehicle was built |
| **Make** | Kept | Manufacturer |
| **Model** | Kept | Model of the vehicle |
| **Electric Vehicle Type** | Kept | Type: BEV (fully electric) or PHEV (plug-in hybrid) |
| ~~Clean Alternative Fuel Vehicle (CAFV) Eligibility~~ → **CAFV Status** | Renamed | Eligibility for the tax incentive (requires a range of ≥ 30 miles / ~48 km) |
| **Electric Range** | Kept | Range in miles on a charged battery |
| ~~Legislative District~~ | Removed | Legislative district code |
| ~~DOL Vehicle ID~~ | Removed | Registration id at the *Department of Licensing* |
| **Vehicle Location** → **Longitude** / **Latitude** | Parsed | The coordinates the DOL geocoded the registration to, split into two numeric columns |
| **Electric Utility** | Kept | Electricity provider associated with the vehicle |
| ~~2020 Census Tract~~ | Removed | Census tract identifier |
| **Vehicle Age** *(created)* | New | The vehicle's age in years (`2026 - Model Year`) |

---

## Typographic Conventions

- *Italics:* foreign or technical terms.
- **Bold:** the important claim.
- ~~Strikethrough:~~ columns, values or elements removed along the way.

---

## Libraries Used

| Library | Use | Documentation |
| --- | --- | --- |
| pandas | Data manipulation and analysis | [pandas.pydata.org](https://pandas.pydata.org/docs/) |
| NumPy | Numeric operations and type handling | [numpy.org](https://numpy.org/doc/2.4/) |
| Plotly Express | Interactive visualisations | [plotly.com/python](https://plotly.com/python/) |
| Matplotlib | Auxiliary visual support | [matplotlib.org](https://matplotlib.org/stable/index.html) |

---

## ⚠️ A Note on the Charts (Plotly)

*Plotly* draws **interactive** charts in the *Jupyter Notebook* — they can be zoomed, filtered and explored directly. That is also why the figures may **fail to render** when the *notebooks* are viewed on GitHub.

The static images are saved in the `images/` folder.

**For the best experience, run the notebooks locally, on Google Colab or on Kaggle.**

> ⚠️ For the map (Fig. 3) and the *scatter plots* (Figs. 5 and 6), **PNG is not recommended**: those charts lose real information once flattened — the map in particular is worth panning and hovering.

## ⚠️ A Note on the Dataset

**The raw export is committed to the repository, in `data/raw/`.** Because new data is added to the live file continuously, re-downloading it would "break" the counts throughout the analysis, so the version frozen on the day it was downloaded is the one analysed here.
