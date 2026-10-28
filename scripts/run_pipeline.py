# Main GridPilot pipeline orchestrator.
# Downloads data, updates the processed dataset,
# and records exactly one monitoring log row per run.

import csv
import datetime
import os
import sys
import zoneinfo

from download_ieso_demand import download_ieso_demand
from check_new_rows import (
    update_demand_dataset,
    get_trusted_dataset_state
)


LOG_FILE = "logs/pipeline_runs.csv"

ontario_timezone = zoneinfo.ZoneInfo("America/Toronto")


def write_run_log(result):

    run_time = datetime.datetime.now(
        ontario_timezone
    ).strftime("%Y-%m-%d %H:%M:%S %Z")

    os.makedirs("logs", exist_ok=True)

    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        if not file_exists:
            writer.writerow([
                "run_time",
                "new_rows",
                "promoted_row_count",
                "promoted_latest_timestamp",
                "candidate_row_count",
                "candidate_latest_timestamp",
                "status",
                "error_message"
            ])

        writer.writerow([
            run_time,
            result["new_rows"],
            result["promoted_row_count"],
            result["promoted_latest_timestamp"],
            result["candidate_row_count"],
            result["candidate_latest_timestamp"],
            result["status"],
            result["error_message"]
        ])


def get_current_state_safely():
    try:
        return get_trusted_dataset_state()
    except Exception:
        return None, None


def run_pipeline():

    # ---------------------------------------------------------
    # 1. Download latest IESO data
    # ---------------------------------------------------------

    try:
        download_ieso_demand()
        print("IESO demand data downloaded successfully.")

    except Exception as error:

        row_count, latest_timestamp = get_current_state_safely()

        result = {
            "new_rows": None,
            "promoted_row_count": row_count,
            "promoted_latest_timestamp": latest_timestamp,
            "candidate_row_count": None,
            "candidate_latest_timestamp": None,
            "status": "FAILED",
            "error_message": f"DOWNLOAD: {error}"
        }

        write_run_log(result)

        print(f"Pipeline failed during download: {error}")
        sys.exit(1)

    # ---------------------------------------------------------
    # 2. Update and validate dataset
    # ---------------------------------------------------------

    try:
        result = update_demand_dataset()

    except Exception as error:

        row_count, latest_timestamp = get_current_state_safely()

        result = {
            "new_rows": None,
            "promoted_row_count": row_count,
            "promoted_latest_timestamp": latest_timestamp,
            "candidate_row_count": None,
            "candidate_latest_timestamp": None,
            "status": "FAILED",
            "error_message": f"UPDATE: {error}"
        }

        write_run_log(result)

        print(f"Pipeline failed during update: {error}")
        sys.exit(1)

    # ---------------------------------------------------------
    # 3. Write exactly one run log
    # ---------------------------------------------------------

    write_run_log(result)

    # ---------------------------------------------------------
    # 4. Report result
    # ---------------------------------------------------------

    if result["status"] == "FAILED":
        print(f"Pipeline validation failed: {result['error_message']}")
        sys.exit(1)

    if result["status"] == "NO_NEW_DATA":
        print("No new rows found. Pipeline completed successfully.")
        return

    print(
        f"Pipeline update successful. "
        f"{result['new_rows']} new rows added. "
        f"Final row count: {result['promoted_row_count']}. "
        f"Latest timestamp: "
        f"{result['promoted_latest_timestamp']}."
    )


if __name__ == "__main__":
    run_pipeline()