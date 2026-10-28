# Identifies new IESO demand records, builds a candidate dataset,
# validates it, and promotes it only if all checks pass.

import os
import duckdb


PROCESSED_FILE = "data/processed/ontario_demand_2026.parquet"
UPDATED_FILE = "data/processed/ontario_demand_2026_updated.parquet"


def get_trusted_dataset_state():
    row_count = duckdb.sql(
        f"SELECT COUNT(*) FROM '{PROCESSED_FILE}'"
    ).fetchone()[0]

    latest_timestamp = duckdb.sql(
        f"SELECT MAX(hour_ending_timestamp) FROM '{PROCESSED_FILE}'"
    ).fetchone()[0]

    return row_count, latest_timestamp


def remove_candidate_file():
    if os.path.exists(UPDATED_FILE):
        os.remove(UPDATED_FILE)


def update_demand_dataset():

    # ---------------------------------------------------------
    # 1. Identify new rows
    # ---------------------------------------------------------

    with open("sql/incremental/01_identify_new_rows.sql", "r") as f:
        check_sql = f.read()

    rows = duckdb.sql(check_sql).fetchall()
    new_row_count = len(rows)

    existing_row_count, old_max_timestamp = get_trusted_dataset_state()

    # ---------------------------------------------------------
    # 2. No new data
    # ---------------------------------------------------------

    if new_row_count == 0:
        return {
            "new_rows": 0,
            "promoted_row_count": existing_row_count,
            "promoted_latest_timestamp": old_max_timestamp,
            "candidate_row_count": None,
            "candidate_latest_timestamp": None,
            "status": "NO_NEW_DATA",
            "error_message": ""
        }

    # ---------------------------------------------------------
    # 3. Build candidate dataset
    # ---------------------------------------------------------

    remove_candidate_file()

    with open("sql/incremental/02_build_updated_dataset.sql", "r") as f:
        update_sql = f.read()

    duckdb.sql(update_sql)

    updated_row_count = duckdb.sql(
        f"SELECT COUNT(*) FROM '{UPDATED_FILE}'"
    ).fetchone()[0]

    updated_max_timestamp = duckdb.sql(
        f"SELECT MAX(hour_ending_timestamp) FROM '{UPDATED_FILE}'"
    ).fetchone()[0]

    # ---------------------------------------------------------
    # 4. Validate row count
    # ---------------------------------------------------------

    expected_row_count = existing_row_count + new_row_count

    if updated_row_count != expected_row_count:
        error_message = (
            f"ROW_COUNT: Expected {expected_row_count} rows, "
            f"found {updated_row_count}."
        )

        result = {
            "new_rows": new_row_count,
            "promoted_row_count": existing_row_count,
            "promoted_latest_timestamp": old_max_timestamp,
            "candidate_row_count": updated_row_count,
            "candidate_latest_timestamp": updated_max_timestamp,
            "status": "FAILED",
            "error_message": error_message
        }

        remove_candidate_file()
        return result

    # ---------------------------------------------------------
    # 5. Validate duplicates
    # ---------------------------------------------------------

    duplicate_groups = duckdb.sql(
        f"""
        SELECT Date, Hour, COUNT(*)
        FROM '{UPDATED_FILE}'
        GROUP BY Date, Hour
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    duplicate_count = len(duplicate_groups)

    if duplicate_count > 0:
        error_message = (
            f"DUPLICATES: Found {duplicate_count} "
            f"duplicate Date/Hour groups."
        )

        result = {
            "new_rows": new_row_count,
            "promoted_row_count": existing_row_count,
            "promoted_latest_timestamp": old_max_timestamp,
            "candidate_row_count": updated_row_count,
            "candidate_latest_timestamp": updated_max_timestamp,
            "status": "FAILED",
            "error_message": error_message
        }

        remove_candidate_file()
        return result

    # ---------------------------------------------------------
    # 6. Validate timestamp advancement
    # ---------------------------------------------------------

    if updated_max_timestamp <= old_max_timestamp:
        error_message = (
            f"TIMESTAMP: Old latest timestamp was "
            f"{old_max_timestamp}; candidate latest timestamp "
            f"is {updated_max_timestamp}."
        )

        result = {
            "new_rows": new_row_count,
            "promoted_row_count": existing_row_count,
            "promoted_latest_timestamp": old_max_timestamp,
            "candidate_row_count": updated_row_count,
            "candidate_latest_timestamp": updated_max_timestamp,
            "status": "FAILED",
            "error_message": error_message
        }

        remove_candidate_file()
        return result

    # ---------------------------------------------------------
    # 7. Promote validated candidate
    # ---------------------------------------------------------

    os.replace(UPDATED_FILE, PROCESSED_FILE)

    return {
        "new_rows": new_row_count,
        "promoted_row_count": updated_row_count,
        "promoted_latest_timestamp": updated_max_timestamp,
        "candidate_row_count": updated_row_count,
        "candidate_latest_timestamp": updated_max_timestamp,
        "status": "SUCCESS",
        "error_message": ""
    }


if __name__ == "__main__":
    result = update_demand_dataset()
    print(result)