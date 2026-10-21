# Checks whether the latest IESO demand file contains new hourly records
# that are not yet stored in the processed Parquet dataset.

'''
Check for new data
        ↓
No new data → Log → Stop
        ↓
New data found
        ↓
Build updated Parquet
        ↓
Validate row count
        ↓
Validate duplicates
        ↓
Validate latest timestamp
        ↓
Promote updated file
        ↓
Log successful run
'''

import csv
import datetime
import os
import sys
import zoneinfo

import duckdb


PROCESSED_FILE = "data/processed/ontario_demand_2026.parquet"
UPDATED_FILE = "data/processed/ontario_demand_2026_updated.parquet"
LOG_FILE = "logs/pipeline_runs.csv"

ontario_timezone = zoneinfo.ZoneInfo("America/Toronto")


def write_run_log(
    new_rows,
    promoted_row_count,
    promoted_latest_timestamp,
    candidate_row_count,
    candidate_latest_timestamp,
    status,
    error_message
):
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
            new_rows,
            promoted_row_count,
            promoted_latest_timestamp,
            candidate_row_count,
            candidate_latest_timestamp,
            status,
            error_message
        ])


# ---------------------------------------------------------
# 1. Identify new rows
# ---------------------------------------------------------

with open("sql/incremental/01_identify_new_rows.sql", "r") as f:
    check_sql = f.read()

rows = duckdb.sql(check_sql).fetchall()
new_row_count = len(rows)


# ---------------------------------------------------------
# 2. Capture the current trusted dataset state
# ---------------------------------------------------------

existing_row_count = duckdb.sql(
    f"SELECT COUNT(*) FROM '{PROCESSED_FILE}'"
).fetchone()[0]

old_max_timestamp = duckdb.sql(
    f"SELECT MAX(hour_ending_timestamp) FROM '{PROCESSED_FILE}'"
).fetchone()[0]


# ---------------------------------------------------------
# 3. Stop cleanly if there is no new data
# ---------------------------------------------------------

if new_row_count == 0:
    write_run_log(
        new_rows=0,
        promoted_row_count=existing_row_count,
        promoted_latest_timestamp=old_max_timestamp,
        candidate_row_count=None,
        candidate_latest_timestamp=None,
        status="NO_NEW_DATA",
        error_message=""
    )

    print("No new rows found. Pipeline stopped.")
    sys.exit(0)


# ---------------------------------------------------------
# 4. Build candidate updated dataset
# ---------------------------------------------------------

with open("sql/incremental/02_build_updated_dataset.sql", "r") as f:
    update_sql = f.read()

duckdb.sql(update_sql)

updated_row_count = duckdb.sql(
    f"SELECT COUNT(*) FROM '{UPDATED_FILE}'"
).fetchone()[0]

updated_max_timestamp = duckdb.sql(
    f"SELECT MAX(hour_ending_timestamp) FROM '{UPDATED_FILE}'"
).fetchone()[0]

print(f"Candidate dataset created with {new_row_count} new rows.")


# ---------------------------------------------------------
# 5. Validate row count
# ---------------------------------------------------------

expected_row_count = existing_row_count + new_row_count

if updated_row_count != expected_row_count:
    error_message = (
        f"Row count validation failed. "
        f"Expected {expected_row_count}, found {updated_row_count}."
    )

    write_run_log(
        new_rows=new_row_count,
        promoted_row_count=existing_row_count,
        promoted_latest_timestamp=old_max_timestamp,
        candidate_row_count=updated_row_count,
        candidate_latest_timestamp=updated_max_timestamp,
        status="FAILED",
        error_message=error_message
    )

    print(f"Error: {error_message}")
    sys.exit(1)


# ---------------------------------------------------------
# 6. Validate duplicates
# ---------------------------------------------------------

duplicate_check = duckdb.sql(
    f"""
    SELECT Date, Hour, COUNT(*)
    FROM '{UPDATED_FILE}'
    GROUP BY Date, Hour
    HAVING COUNT(*) > 1
    """
).fetchall()

duplicate_count = len(duplicate_check)

if duplicate_count > 0:
    error_message = (
        f"Duplicate validation failed. "
        f"Found {duplicate_count} duplicate Date/Hour groups."
    )

    write_run_log(
        new_rows=new_row_count,
        promoted_row_count=existing_row_count,
        promoted_latest_timestamp=old_max_timestamp,
        candidate_row_count=updated_row_count,
        candidate_latest_timestamp=updated_max_timestamp,
        status="FAILED",
        error_message=error_message
    )

    print(f"Error: {error_message}")
    sys.exit(1)

print("No duplicates found in the candidate dataset.")


# ---------------------------------------------------------
# 7. Validate timestamp advancement
# ---------------------------------------------------------

if updated_max_timestamp <= old_max_timestamp:
    error_message = (
        f"Timestamp validation failed. "
        f"Old latest timestamp: {old_max_timestamp}, "
        f"candidate latest timestamp: {updated_max_timestamp}."
    )

    write_run_log(
        new_rows=new_row_count,
        promoted_row_count=existing_row_count,
        promoted_latest_timestamp=old_max_timestamp,
        candidate_row_count=updated_row_count,
        candidate_latest_timestamp=updated_max_timestamp,
        status="FAILED",
        error_message=error_message
    )

    print(f"Error: {error_message}")
    sys.exit(1)

print(
    f"Candidate dataset contains new records through "
    f"{updated_max_timestamp}."
)


# ---------------------------------------------------------
# 8. Promote validated candidate dataset
# ---------------------------------------------------------

os.replace(UPDATED_FILE, PROCESSED_FILE)

print("Updated dataset promoted to replace the old dataset.")


# ---------------------------------------------------------
# 9. Log successful pipeline run
# ---------------------------------------------------------

write_run_log(
    new_rows=new_row_count,
    promoted_row_count=updated_row_count,
    promoted_latest_timestamp=updated_max_timestamp,
    candidate_row_count=updated_row_count,
    candidate_latest_timestamp=updated_max_timestamp,
    status="SUCCESS",
    error_message=""
)

print(
    f"Pipeline update successful. "
    f"{new_row_count} new rows added. "
    f"Final row count: {updated_row_count}."
)