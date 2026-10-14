# GridPilot: Living Ontario Electricity Demand Data Pipeline

GridPilot is a continuously updating data and analytics project built around real Ontario electricity demand data.

The current version focuses on building a reliable "living dataset" that automatically downloads the latest electricity demand data from the Independent Electricity System Operator (IESO), identifies new hourly observations, validates them, and maintains an updated historical dataset.

The long-term goal is to evolve GridPilot into an end-to-end electricity analytics, forecasting, and decision-support system using electricity, weather, machine learning, optimization, and eventually reinforcement learning experiments.

## Table of Contents

1. [About the Project](#about-the-project)
2. [Purpose](#purpose)
3. [Current Architecture](#current-architecture)
4. [Technology Stack](#technology-stack)
5. [Prerequisites](#prerequisites)
6. [Dataset](#dataset)
7. [Installation](#installation)
8. [Usage](#usage)
9. [Data Quality Checks](#data-quality-checks)
10. [Automation](#automation)
11. [Project Structure](#project-structure)
12. [Roadmap](#roadmap)

---

## About the Project

Electricity demand changes continuously throughout the day and is influenced by factors such as time, weather, seasonality, human activity, and extreme events.

GridPilot is being developed as a learning and portfolio project to understand how a real data system can move from:

```text
Public Data Source
        ↓
Data Ingestion
        ↓
Validation
        ↓
Storage
        ↓
SQL Transformation
        ↓
Exploratory Analysis
        ↓
Feature Engineering
        ↓
Machine Learning
        ↓
Evaluation
        ↓
Monitoring
        ↓
Decision Support
```

Rather than beginning with machine learning, the project first focuses on building a reliable data foundation.

The first milestone is:

> **GridPilot v0.1: Living Dataset**

The key question for this stage is:

> Can GridPilot reliably build and maintain its own continuously updating history of Ontario electricity-grid demand using real public data?

---

## Purpose

The project has two main objectives.

### 1. Build a continuously updating electricity dataset

GridPilot should be able to:

- retrieve the latest Ontario electricity demand data
- preserve the raw source file
- identify newly available hourly records
- prevent duplicate observations
- validate updates before accepting them
- maintain an analysis-ready historical dataset
- run automatically without manual intervention

### 2. Build an end-to-end analytics and machine learning system

Future versions of GridPilot are planned to include:

- exploratory electricity demand analysis
- weather data integration
- SQL analytical tables
- peak-demand analysis
- electricity demand forecasting
- baseline forecasting models
- supervised machine learning
- model evaluation and backtesting
- model performance monitoring
- dashboards and decision-support tools
- optimization experiments
- reinforcement learning experiments in a simulated environment

Advanced methods will only be introduced after simpler baselines have been established.

---

## Current Architecture

The currently implemented pipeline is:

```text
                IESO
                 │
                 ▼
        PUB_Demand.csv
                 │
                 ▼
       Python Data Download
                 │
                 ▼
          Raw Data Layer
                 │
                 ▼
         DuckDB + SQL
                 │
                 ▼
      Detect New Hourly Rows
                 │
                 ▼
        Build Candidate Dataset
                 │
                 ▼
          Validation Checks
          │       │       │
          │       │       └── Latest timestamp
          │       └────────── Duplicate check
          └────────────────── Row count check
                 │
                 ▼
        Validation Successful?
             │         │
            No        Yes
             │         │
             ▼         ▼
            Stop     Promote
                       │
                       ▼
          Processed Parquet Dataset
                       │
                       ▼
                GitHub Actions
              Daily Scheduled Run
```

The pipeline is designed to be incremental. Instead of rebuilding the entire historical dataset every day, GridPilot identifies records newer than the latest timestamp already stored.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline orchestration and data download |
| SQL | Data transformation, validation, and incremental logic |
| DuckDB | SQL analytics and querying CSV/Parquet files |
| Parquet | Processed analytical data storage |
| Git | Version control |
| GitHub | Repository and project hosting |
| GitHub Actions | Cloud-based daily pipeline scheduling |
| IESO | Ontario electricity demand data source |

Current Python dependency:

```text
duckdb==1.5.6
```

Most other Python modules currently used by the pipeline are part of the Python standard library.

---

## Prerequisites

To run GridPilot locally, install:

- Git
- Python 3.12 or compatible version
- pip

The automated GitHub Actions environment currently uses Python 3.12.3.

You can verify Python using:

```bash
python --version
```

or on Windows:

```powershell
py --version
```

---

## Dataset

### IESO Hourly Demand Data

GridPilot currently uses publicly available electricity demand data from the Independent Electricity System Operator (IESO).

Source:

https://reports-public.ieso.ca/public/Demand/PUB_Demand.csv

The source file is downloaded automatically and stored as:

```text
data/raw/PUB_Demand.csv
```

The raw file is preserved in the format provided by IESO.

The report contains metadata in the first three lines before the column header. These rows are preserved in the raw layer and skipped during SQL processing.

### Dataset Grain

One observation represents:

> **One hour of Ontario electricity demand**

### Raw Columns

| Column | Description |
|---|---|
| Date | Date of the electricity demand observation |
| Hour | IESO hour-ending period from 1 to 24 |
| Market Demand | Demand associated with the broader IESO-administered market |
| Ontario Demand | Electricity demand within Ontario, measured in MW |

For the current forecasting direction of the project, **Ontario Demand** is the primary variable of interest.

### Processed Dataset

The analysis-ready dataset is stored as:

```text
data/processed/ontario_demand_2026.parquet
```

The processed dataset contains:

| Column | Description |
|---|---|
| Date | Original IESO date |
| Hour | Original IESO hour |
| Market Demand | Market demand in MW |
| Ontario Demand | Ontario demand in MW |
| hour_ending_timestamp | Timestamp created from Date + Hour |

The timestamp transformation correctly handles `Hour = 24` by moving it to `00:00` on the following date.

Example:

```text
2026-01-01, Hour 17
→ 2026-01-01 17:00:00

2026-01-01, Hour 24
→ 2026-01-02 00:00:00
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/jaswanthk20/GridPilot.git
```

### 2. Enter the project directory

```bash
cd GridPilot
```

### 3. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Run the complete pipeline

From the project root:

```bash
python scripts/03_run_pipeline.py
```

On Windows, the following can also be used:

```powershell
py scripts/03_run_pipeline.py
```

The master pipeline performs the following sequence:

```text
Download latest IESO report
        ↓
Check for new hourly records
        ↓
No new data?
   │           │
  Yes          No
   │           │
  Stop         ▼
         Build updated dataset
                 ↓
              Validate
                 ↓
         Promote updated file
```

### Download only the latest IESO file

```bash
python scripts/01_download_ieso_demand.py
```

This downloads:

```text
https://reports-public.ieso.ca/public/Demand/PUB_Demand.csv
```

to:

```text
data/raw/PUB_Demand.csv
```

### Check and update the processed dataset

```bash
python scripts/02_check_new_rows.py
```

If no new records exist, the pipeline stops without modifying the processed dataset.

If new records exist, an updated candidate Parquet dataset is created and validated before replacing the existing processed dataset.

---

## Data Quality Checks

Several SQL checks were developed while validating the electricity dataset.

They are stored under:

```text
sql/data_quality/
```

Current checks include:

### Duplicate Date and Hour

Each combination of:

```text
Date + Hour
```

should occur only once.

### Daily Completeness

Completed days should contain the expected hourly observations.

The current incomplete day is treated separately because the source dataset is continuously updated.

### Valid Hour Range

IESO Hour values should remain within:

```text
1 to 24
```

### NULL Values

Core fields are checked for missing values:

- Date
- Hour
- Market Demand
- Ontario Demand

### Non-Positive Ontario Demand

Ontario Demand values are checked for values less than or equal to zero.

### Demand Summary Checks

Minimum, maximum, and average Ontario demand values are inspected to understand the observed range before introducing arbitrary validation thresholds.

### Candidate Dataset Validation

Before an updated dataset is promoted, GridPilot currently checks:

1. Expected row count
2. Duplicate Date/Hour combinations
3. Advancement of the latest timestamp

Only a successfully validated candidate dataset replaces the existing processed dataset.

---

## Automation

GridPilot currently runs in the cloud using **GitHub Actions**.

Workflow:

```text
.github/workflows/daily_pipeline.yml
```

The workflow:

1. checks out the repository
2. creates an Ubuntu runner
3. configures Python
4. installs project dependencies
5. runs the GridPilot pipeline
6. commits updated raw and processed data back to GitHub when changes exist

The workflow is scheduled daily at:

```text
8:15 AM America/Toronto
```

It can also be started manually through GitHub Actions using `workflow_dispatch`.

This allows GridPilot's dataset to continue updating without requiring a local computer to remain running.

---

## Project Structure

```text
GridPilot/
│
├── .github/
│   └── workflows/
│       └── daily_pipeline.yml
│
├── data/
│   ├── raw/
│   │   └── PUB_Demand.csv
│   │
│   └── processed/
│       └── ontario_demand_2026.parquet
│
├── scripts/
│   ├── 01_download_ieso_demand.py
│   ├── 02_check_new_rows.py
│   └── 03_run_pipeline.py
│
├── sql/
│   ├── data_quality/
│   │   ├── 01_check_duplicates.sql
│   │   ├── 02_check_daily_completeness.sql
│   │   ├── 03_check_hour_range.sql
│   │   ├── 04_check_null_values.sql
│   │   ├── 05_check_nonpositive_ontario_demand.sql
│   │   ├── 06_summarize_ontario_demand.sql
│   │   └── 07_check_updated_dataset.sql
│   │
│   ├── incremental/
│   │   ├── 01_identify_new_rows.sql
│   │   └── 02_build_updated_dataset.sql
│   │
│   └── transformations/
│       ├── 00_preview_raw_ieso.sql
│       └── 01_build_ontario_demand.sql
│
├── requirements.txt
└── README.md
```

---

## Roadmap

GridPilot is being developed incrementally. Planned features are not presented as completed work.

### Phase 1: Living Electricity Dataset

**Status: Implemented**

- [x] Identify IESO hourly electricity demand source
- [x] Understand dataset grain
- [x] Validate Date + Hour uniqueness
- [x] Check completed-day completeness
- [x] Validate Hour range
- [x] Check NULL values
- [x] Check non-positive demand
- [x] Analyze minimum, maximum, and average demand
- [x] Create hour-ending timestamps
- [x] Preserve raw source data
- [x] Create processed Parquet layer
- [x] Detect new records incrementally
- [x] Merge new records with historical data
- [x] Validate candidate dataset before promotion
- [x] Automate IESO data download
- [x] Build Python pipeline orchestration
- [x] Schedule daily execution using GitHub Actions
- [x] Commit updated datasets automatically to GitHub

### Phase 2: Pipeline Monitoring

**Status: In Progress**

- [ ] Create pipeline run-history logging
- [ ] Record successful pipeline runs
- [ ] Record no-new-data runs
- [ ] Record failed validation runs
- [ ] Capture pipeline error messages
- [ ] Improve temporary-file cleanup after failures
- [ ] Add additional pipeline health checks

### Phase 3: Exploratory Data Analysis

**Status: Planned**

- [ ] Analyze hourly demand patterns
- [ ] Analyze daily demand patterns
- [ ] Analyze weekday vs weekend demand
- [ ] Analyze monthly and seasonal patterns
- [ ] Investigate historical demand peaks
- [ ] Build reusable SQL analytical tables
- [ ] Document major findings

### Phase 4: Weather Integration

**Status: Planned**

Potential source:

- Open-Meteo

Planned work:

- [ ] Identify suitable Ontario weather locations
- [ ] Collect historical and continuously updating weather observations
- [ ] Align weather timestamps with IESO demand timestamps
- [ ] Validate weather data
- [ ] Analyze temperature-demand relationships
- [ ] Build a combined electricity + weather analytical dataset

### Phase 5: Forecasting Baselines

**Status: Planned**

Simple approaches will be established before advanced models.

Planned progression:

```text
Previous Hour
     ↓
Moving Average
     ↓
Linear Regression
     ↓
Decision Tree
     ↓
Random Forest / Gradient Boosting
```

Planned work:

- [ ] Define forecasting target
- [ ] Define forecasting horizon
- [ ] Create lag features
- [ ] Create rolling features
- [ ] Create calendar features
- [ ] Use time-based train/test splits
- [ ] Establish baseline forecasts
- [ ] Evaluate using appropriate forecasting metrics
- [ ] Implement backtesting

### Phase 6: Peak Demand Risk

**Status: Planned**

- [ ] Define peak-demand thresholds
- [ ] Analyze historical peaks
- [ ] Identify conditions associated with high demand
- [ ] Develop peak-risk indicators
- [ ] Compare predicted peaks against actual outcomes

### Phase 7: Model Monitoring

**Status: Planned**

- [ ] Store predictions
- [ ] Compare forecasts against actual demand
- [ ] Track model errors over time
- [ ] Monitor performance degradation
- [ ] Compare new models against existing baselines

### Phase 8: Dashboard and Decision Support

**Status: Planned**

Potential tools:

- Streamlit
- Metabase

Potential outputs:

- current electricity demand
- historical demand trends
- peak-demand indicators
- weather relationships
- forecast vs actual demand
- model performance
- pipeline health

### Phase 9: Optimization

**Status: Planned**

After forecasting is established:

```text
Forecast
   ↓
Decision Rule
   ↓
Optimization Model
   ↓
Compare Decisions
```

Optimization experiments will focus on how forecasts can support better electricity-related decisions.

### Phase 10: Reinforcement Learning Research

**Status: Planned**

Reinforcement learning will only be explored after the analytics, forecasting, supervised learning, evaluation, and simulation foundations are complete.

Potential tools:

- Gymnasium
- Stable-Baselines3

The reinforcement learning component will be treated as a simulation or research experiment unless real operational control data becomes available.

Simulated outcomes will not be presented as real-world operational results.

---

## Project Principles

GridPilot follows a few core engineering principles:

**Preserve raw data**

The original source should remain available whenever practical.

**Validate before promoting**

New data should not replace the trusted dataset until validation succeeds.

**Prefer incremental processing**

Only newly available observations should be processed when possible.

**Automate repetitive work**

Manual workflows should first be understood, then progressively automated.

**Start with simple baselines**

Advanced models should only be introduced when they provide measurable value over simpler methods.

**Never fabricate project data**

Real project analysis should use real publicly available observations. Synthetic data, if ever used for learning, must be clearly identified and kept separate from the real dataset.

---

## Repository

GitHub:

https://github.com/jaswanthk20/GridPilot

---

## Current Project Status

**GridPilot v0.1: Living Dataset**

The project currently has a working automated pipeline that downloads updated IESO electricity demand data, identifies new observations, validates candidate updates, maintains a processed Parquet dataset, and runs daily through GitHub Actions.

Pipeline monitoring is the next development stage.
