# GridPilot: Living Ontario Electricity Demand Data Pipeline

GridPilot is a continuously updating data engineering and analytics project built around real Ontario electricity demand data.

The project currently maintains a reliable **living dataset** that automatically downloads the latest electricity demand data from the Independent Electricity System Operator (IESO), identifies newly available hourly observations, validates candidate updates, maintains a trusted historical dataset, records pipeline health, and runs automatically in the cloud using GitHub Actions.

The long-term goal is to evolve GridPilot into an end-to-end electricity analytics, forecasting, and decision-support system using electricity demand, weather data, machine learning, optimization, and eventually reinforcement learning experiments.

---

## Current Status

### GridPilot v0.1 — Living Dataset

**Status: Implemented**

GridPilot can currently:

- download the latest IESO hourly demand report
- preserve the raw source file
- detect newly available hourly observations
- process only new records incrementally
- validate candidate datasets before promotion
- prevent duplicate Date/Hour observations
- maintain a processed Parquet dataset
- preserve trusted data when validation fails
- record pipeline execution history
- distinguish `SUCCESS`, `NO_NEW_DATA`, and `FAILED` runs
- capture pipeline error messages
- run automatically through GitHub Actions
- commit updated datasets and monitoring logs back to GitHub

### Next Stage

> **GridPilot v0.2 — Electricity Demand Analytics**

The next phase will use the historical dataset to build reusable SQL analytical tables and exploratory analysis for hourly, daily, weekly, monthly, seasonal, and peak-demand patterns.

---

## Table of Contents

1. [About the Project](#about-the-project)
2. [Project Principles](#project-principles)
3. [Current Architecture](#current-architecture)
4. [Technology Stack](#technology-stack)
5. [Dataset](#dataset)
6. [Processed Data](#processed-data)
7. [Data Quality Checks](#data-quality-checks)
8. [Pipeline Monitoring](#pipeline-monitoring)
9. [Installation](#installation)
10. [Usage](#usage)
11. [Automation](#automation)
12. [Project Structure](#project-structure)
13. [Roadmap](#roadmap)

---

## About the Project

Electricity demand changes continuously throughout the day and is influenced by factors such as:

- time of day
- day of week
- seasonality
- weather
- human activity
- holidays
- extreme events

GridPilot is being developed as both a **learning project** and a **portfolio project**.

The goal is to understand how a real data system progresses through an end-to-end workflow:

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
Deployment
        ↓
Monitoring
        ↓
Decision Support
```

Rather than beginning with machine learning, GridPilot first establishes a reliable data foundation.

The first milestone asked:

> **Can GridPilot reliably build and maintain its own continuously updating history of Ontario electricity demand using real public data?**

GridPilot v0.1 demonstrates that this can now be done automatically.

---

## Project Principles

GridPilot follows several engineering principles.

### Preserve raw data

The original source file should remain available whenever practical.

The IESO report is therefore stored in its original format before downstream transformations are applied.

### Validate before promoting

New data is never allowed to replace the trusted processed dataset until validation succeeds.

GridPilot first creates a candidate dataset, validates it, and only then promotes it.

### Prefer incremental processing

GridPilot does not rebuild the entire historical dataset every day.

Only observations newer than the latest trusted timestamp are added.

### Make pipelines idempotent

Running the pipeline when no new data exists should not create duplicates or modify the trusted dataset.

### Automate repetitive work

Manual workflows are first understood and verified before being automated.

### Separate orchestration from processing

The master pipeline controls execution and monitoring, while separate modules handle downloading and dataset updates.

### Start with simple baselines

Advanced analytics and machine learning techniques will only be introduced after simpler approaches have been established.

### Never fabricate project data

Real project analysis uses real publicly available observations.

Synthetic data may only be used for clearly labelled learning experiments and must remain separate from the actual GridPilot dataset.

---

## Current Architecture

The current GridPilot v0.1 architecture is:

```text
                    IESO
                     │
                     ▼
            PUB_Demand.csv
                     │
                     ▼
          download_ieso_demand.py
                     │
                     ▼
               Raw Data Layer
         data/raw/PUB_Demand.csv
                     │
                     ▼
              DuckDB + SQL
                     │
                     ▼
           Detect New Records
                     │
              ┌──────┴──────┐
              │             │
         No new data     New data
              │             │
              ▼             ▼
        NO_NEW_DATA    Build Candidate
              │             │
              │             ▼
              │      Validation Checks
              │        │     │     │
              │        │     │     └── Timestamp advancement
              │        │     └──────── Duplicate Date/Hour check
              │        └────────────── Expected row count
              │             │
              │       ┌─────┴─────┐
              │       │           │
              │     Failed      Passed
              │       │           │
              │       ▼           ▼
              │     FAILED      Promote
              │                   │
              │                   ▼
              │       Trusted Parquet Dataset
              │                   │
              └──────────┬────────┘
                         ▼
                  Pipeline Run Log
              logs/pipeline_runs.csv
                         │
                         ▼
                   GitHub Actions
                  Daily Cloud Run
                         │
                         ▼
             Commit Updated Files
                  Back to GitHub
```

The master orchestrator is:

```text
scripts/run_pipeline.py
```

It coordinates the download, update, validation, status reporting, and monitoring workflow.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline orchestration and data ingestion |
| SQL | Transformation, incremental processing, and data-quality logic |
| DuckDB | SQL execution over CSV and Parquet files |
| Parquet | Processed analytical data storage |
| CSV | Raw source storage and pipeline run history |
| Git | Version control |
| GitHub | Repository hosting |
| GitHub Actions | Cloud-based scheduled execution |
| IESO | Ontario electricity demand data source |

Current external Python dependency:

```text
duckdb==1.5.6
```

Other modules currently used, including `csv`, `datetime`, `os`, `sys`, `urllib`, and `zoneinfo`, are part of the Python standard library.

---

## Dataset

### IESO Hourly Demand Report

GridPilot currently uses publicly available electricity demand data from the **Independent Electricity System Operator (IESO)**.

Source:

```text
https://reports-public.ieso.ca/public/Demand/PUB_Demand.csv
```

The latest report is downloaded automatically and stored as:

```text
data/raw/PUB_Demand.csv
```

### Raw Data Philosophy

The raw IESO file is preserved without deleting its report metadata.

The first three lines contain metadata such as:

```text
Hourly Demand Report
Created at ...
For 2026
```

The actual CSV header begins after those rows:

```text
Date,Hour,Market Demand,Ontario Demand
```

GridPilot preserves the source exactly as provided and instructs DuckDB to skip the metadata rows during processing.

---

## Dataset Grain

One observation represents:

> **One hour of Ontario electricity demand**

The original dataset uses IESO **Hour Ending** values from `1` through `24`.

For example:

```text
Date = 2026-07-14
Hour = 17
```

represents the hourly interval ending at:

```text
2026-07-14 17:00:00
```

---

## Raw Columns

| Column | Description |
|---|---|
| `Date` | Date associated with the IESO hourly observation |
| `Hour` | Hour-ending period from 1 to 24 |
| `Market Demand` | Demand associated with the broader IESO-administered market |
| `Ontario Demand` | Electricity demand within Ontario in MW |

For GridPilot's future forecasting work:

> **Ontario Demand is the primary target variable of interest.**

---

## Processed Data

The trusted analysis-ready dataset is stored as:

```text
data/processed/ontario_demand_2026.parquet
```

The processed dataset contains:

| Column | Description |
|---|---|
| `Date` | Original IESO date |
| `Hour` | Original IESO hour |
| `Market Demand` | Market demand in MW |
| `Ontario Demand` | Ontario demand in MW |
| `hour_ending_timestamp` | Timestamp derived from Date and Hour |

### Timestamp Transformation

The timestamp is created using:

```text
Date + Hour
```

with the IESO hour-ending convention.

For example:

```text
2026-01-01, Hour 17
→ 2026-01-01 17:00:00
```

Hour 24 naturally becomes midnight on the following date:

```text
2026-01-01, Hour 24
→ 2026-01-02 00:00:00
```

This creates a continuous hourly timestamp suitable for time-series analysis and future weather integration.

---

## Incremental Processing

GridPilot does not rebuild the entire historical dataset during each pipeline run.

The latest trusted timestamp is obtained using:

```sql
MAX(hour_ending_timestamp)
```

New records are defined as observations where:

```text
incoming timestamp > latest stored timestamp
```

The pipeline therefore follows:

```text
Existing processed history
            +
New IESO observations only
            ↓
Candidate updated dataset
```

The candidate is written separately before the trusted dataset is modified.

---

## Data Quality Checks

GridPilot contains SQL-based data-quality checks under:

```text
sql/data_quality/
```

### 1. Duplicate Date and Hour

Each combination of:

```text
Date + Hour
```

must be unique.

Duplicate hourly observations could bias aggregates and future model training.

### 2. Daily Completeness

Completed days are checked for the expected hourly observations.

The newest day may legitimately be incomplete because the source is continuously updated.

### 3. Valid Hour Range

IESO Hour values must remain between:

```text
1 and 24
```

### 4. NULL Values

Core fields are checked for missing values:

- `Date`
- `Hour`
- `Market Demand`
- `Ontario Demand`

### 5. Non-Positive Ontario Demand

Ontario Demand is checked for values:

```text
<= 0
```

A zero or negative province-wide demand value would be treated as suspicious.

### 6. Demand Summary

Minimum, maximum, and average Ontario Demand are inspected to understand the observed range before introducing arbitrary thresholds.

### 7. Candidate Dataset Validation

Every incremental update must pass three checks before promotion:

```text
Expected row count
        ↓
No duplicate Date/Hour groups
        ↓
Latest timestamp advanced
        ↓
Promote candidate
```

If any validation fails, the trusted Parquet file is preserved.

---

## Pipeline Monitoring

GridPilot records operational history in:

```text
logs/pipeline_runs.csv
```

Each pipeline execution records:

| Field | Description |
|---|---|
| `run_time` | Pipeline execution time in the America/Toronto timezone |
| `new_rows` | Number of newly detected observations |
| `promoted_row_count` | Row count of the trusted dataset after the run |
| `promoted_latest_timestamp` | Latest timestamp in the trusted dataset |
| `candidate_row_count` | Row count of the candidate dataset when applicable |
| `candidate_latest_timestamp` | Latest timestamp in the candidate dataset |
| `status` | Pipeline outcome |
| `error_message` | Failure information when applicable |

### Pipeline Status Values

GridPilot currently uses three statuses:

```text
SUCCESS
NO_NEW_DATA
FAILED
```

#### SUCCESS

New observations were identified, validated, and promoted.

#### NO_NEW_DATA

The pipeline executed correctly, but no observations newer than the trusted dataset were available.

This is considered a successful pipeline execution.

#### FAILED

The pipeline encountered an ingestion, processing, or validation failure.

The trusted processed dataset remains unchanged.

### Failure Information

Error messages identify the area in which the pipeline failed, such as:

```text
DOWNLOAD
UPDATE
ROW_COUNT
DUPLICATES
TIMESTAMP
```

This allows pipeline failures to be diagnosed without manually inspecting every intermediate step.

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

All commands should be executed from the GridPilot project root.

### Run the Complete Pipeline

```bash
python scripts/run_pipeline.py
```

On Windows:

```powershell
py scripts/run_pipeline.py
```

The master pipeline performs:

```text
Download latest IESO data
        ↓
Identify new observations
        ↓
Build candidate dataset if required
        ↓
Validate candidate
        ↓
Promote trusted dataset
        ↓
Write pipeline run log
```

---

### Run Only the IESO Download

```bash
python scripts/download_ieso_demand.py
```

This downloads the current IESO report to:

```text
data/raw/PUB_Demand.csv
```

---

### Run Only the Dataset Update Logic

```bash
python scripts/check_new_rows.py
```

This:

- identifies records newer than the trusted dataset
- builds a candidate dataset when required
- validates the candidate
- promotes it only after validation succeeds

The master `run_pipeline.py` should normally be used for complete pipeline executions because it also owns centralized monitoring and error handling.

---

## Automation

GridPilot runs automatically in the cloud using **GitHub Actions**.

Workflow file:

```text
.github/workflows/daily_pipeline.yml
```

The workflow:

1. checks out the repository
2. starts an Ubuntu GitHub-hosted runner
3. configures Python 3.12.3
4. installs dependencies from `requirements.txt`
5. executes `scripts/run_pipeline.py`
6. commits updated source data, processed data, and monitoring logs
7. commits failure logs when a pipeline run fails

### Schedule

The workflow is configured to run daily at:

```text
8:15 AM America/Toronto
```

Using the `America/Toronto` timezone allows daylight-saving changes to be handled automatically.

The workflow can also be started manually using:

```text
workflow_dispatch
```

from the GitHub Actions interface.

This allows GridPilot to continue updating without requiring a local computer to remain powered on.

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
├── logs/
│   └── pipeline_runs.csv
│
├── scripts/
│   ├── download_ieso_demand.py
│   ├── check_new_rows.py
│   └── run_pipeline.py
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

# Roadmap

GridPilot is being developed incrementally.

Planned features are not presented as completed work.

---

## Phase 1 — Living Electricity Dataset

**Status: Implemented**

- [x] Identify IESO hourly electricity demand source
- [x] Understand dataset grain
- [x] Understand IESO Hour Ending convention
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
- [x] Validate candidate datasets before promotion
- [x] Automate IESO data download
- [x] Build Python pipeline orchestration
- [x] Schedule daily execution using GitHub Actions
- [x] Commit updated datasets automatically to GitHub
- [x] Handle no-new-data runs safely
- [x] Prevent failed candidates from replacing trusted data

---

## Phase 2 — Pipeline Monitoring

**Status: Implemented**

- [x] Create pipeline run-history logging
- [x] Record successful pipeline runs
- [x] Record no-new-data runs
- [x] Record failed runs
- [x] Capture pipeline error messages
- [x] Store promoted dataset state
- [x] Store candidate dataset state when applicable
- [x] Use America/Toronto timestamps
- [x] Clean up failed candidate files
- [x] Centralize pipeline logging in the master orchestrator
- [x] Preserve monitoring logs through GitHub Actions

---

## Phase 3 — Electricity Demand Analytics

**Status: Next**

The next phase will turn the historical dataset into reusable analytical information.

Planned work:

- [ ] Analyze hourly demand profiles
- [ ] Analyze daily demand patterns
- [ ] Compare weekday and weekend behavior
- [ ] Analyze monthly demand patterns
- [ ] Analyze seasonal behavior
- [ ] Identify historical peak-demand periods
- [ ] Calculate demand variability
- [ ] Build reusable SQL analytical tables
- [ ] Document major analytical findings
- [ ] Add analysis outputs to the project documentation

---

## Phase 4 — Weather Integration

**Status: Planned**

Potential source:

```text
Open-Meteo
```

Planned work:

- [ ] Identify representative Ontario weather locations
- [ ] Collect historical weather observations
- [ ] Automate continuously updating weather ingestion
- [ ] Understand weather dataset grain
- [ ] Validate weather observations
- [ ] Align weather and electricity timestamps
- [ ] Analyze temperature-demand relationships
- [ ] Investigate extreme-weather demand behavior
- [ ] Build a combined electricity + weather analytical dataset

---

## Phase 5 — Forecasting Baselines

**Status: Planned**

GridPilot will establish simple forecasting baselines before introducing machine learning.

Planned progression:

```text
Previous Value
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
- [ ] Understand time-series leakage
- [ ] Create lag features
- [ ] Create rolling features
- [ ] Create calendar features
- [ ] Add weather features
- [ ] Use time-based train/test splits
- [ ] Establish simple baseline forecasts
- [ ] Evaluate forecasting metrics
- [ ] Implement backtesting
- [ ] Compare ML models against the baseline

---

## Phase 6 — Peak Demand Risk

**Status: Planned**

- [ ] Define peak-demand thresholds
- [ ] Analyze historical peaks
- [ ] Identify conditions associated with high demand
- [ ] Develop peak-risk indicators
- [ ] Predict high-demand periods
- [ ] Compare predicted peaks against actual outcomes

---

## Phase 7 — Model Monitoring

**Status: Planned**

- [ ] Store forecasts
- [ ] Store actual outcomes
- [ ] Compare predictions against actual demand
- [ ] Track model errors over time
- [ ] Monitor performance degradation
- [ ] Compare new models against existing baselines
- [ ] Define retraining criteria

---

## Phase 8 — Dashboard and Decision Support

**Status: Planned**

Potential tools:

- Streamlit
- Metabase

Potential outputs:

- current electricity demand
- historical demand trends
- hourly demand profiles
- peak-demand indicators
- weather relationships
- forecast vs actual demand
- forecasting accuracy
- model performance
- pipeline health

---

## Phase 9 — Optimization

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

Optimization experiments will investigate how demand forecasts can support better electricity-related decisions.

A simple decision rule will always be established before more advanced optimization approaches are introduced.

---

## Phase 10 — Reinforcement Learning Research

**Status: Planned**

Reinforcement learning will only be explored after the analytics, forecasting, supervised learning, evaluation, optimization, and simulation foundations are established.

Potential tools:

- Gymnasium
- Stable-Baselines3

Before implementation, the project will explicitly define:

- State
- Action
- Reward
- Environment
- Episode
- Policy

The reinforcement learning component will be treated as a **simulation or research experiment** unless real operational control data becomes available.

Simulated outcomes will never be presented as real-world operational results.

---

## Repository

GitHub:

```text
https://github.com/jaswanthk20/GridPilot
```

---

## Current Project Status

### GridPilot v0.1 — Living Dataset ✅

The project now has a working cloud-scheduled data pipeline that:

```text
Downloads
   ↓
Transforms
   ↓
Incrementally updates
   ↓
Validates
   ↓
Promotes
   ↓
Monitors
   ↓
Commits results back to GitHub
```

The data engineering foundation is now established.

### Next: GridPilot v0.2 — Electricity Demand Analytics

The next development stage will use SQL and exploratory analysis to understand the behavior of Ontario electricity demand before weather integration or machine learning begins.