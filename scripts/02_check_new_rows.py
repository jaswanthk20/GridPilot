# Checks whether the latest IESO demand file contains new hourly records that are not yet stored in the processed Parquet dataset.
'''
Check for new data
        ↓
No new data → Stop
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
'''

import duckdb
import os
import sys

# Read the SQL query to identify new rows from the latest IESO demand file
with open("sql/incremental/01_identify_new_rows.sql", "r") as f:
    check_sql = f.read()

result = duckdb.sql(check_sql)
rows = result.fetchall()
new_row_count = len(rows)

# Execute the SQL query to find out existing rows in the old dataset
existing_row_count = duckdb.sql("SELECT COUNT(*) FROM 'data/processed/ontario_demand_2026.parquet'").fetchone()[0]

if new_row_count == 0:
    print("No new rows found. Pipeline stopped.")
else: 
    # Read the SQL query to update the dataset with new rows
    with open("sql/incremental/02_build_updated_dataset.sql", "r") as f:
        update_sql = f.read()
    duckdb.sql(update_sql)

    # Execute the SQL query to find out existing rows in the new dataset
    updated_row_count = duckdb.sql("SELECT COUNT(*) FROM 'data/processed/ontario_demand_2026_updated.parquet'").fetchone()[0]

    if updated_row_count == existing_row_count + new_row_count: 
        print(f"Updated dataset created with {new_row_count} new rows.")

        # Execute the SQL query to check duplicates in the updated dataset
        duplicate_check = duckdb.sql("SELECT Date, Hour, COUNT(*) FROM 'data/processed/ontario_demand_2026_updated.parquet' GROUP BY Date, Hour HAVING COUNT(*) > 1").fetchall()
        duplicate_count = len(duplicate_check)
        if duplicate_count > 0:
            print(f"Error: The updated dataset contains {duplicate_count} duplicate Date/Hour groups.")
            sys.exit(1)
        else: 
            print("No duplicates found in the updated dataset.")

            # Execute the SQL query to check for lastest timestamp in the updated dataset
            old_max_timestamp = duckdb.sql("SELECT MAX(hour_ending_timestamp) FROM 'data/processed/ontario_demand_2026.parquet'").fetchone()[0]    
            updated_max_timestamp = duckdb.sql("SELECT MAX(hour_ending_timestamp) FROM 'data/processed/ontario_demand_2026_updated.parquet'").fetchone()[0]
            
            if updated_max_timestamp > old_max_timestamp:
                print(f"Updated dataset contains new records with latest timestamp: {updated_max_timestamp}.")

                # Promote the updated dataset to replace the old dataset
                os.replace("data/processed/ontario_demand_2026_updated.parquet", "data/processed/ontario_demand_2026.parquet")
                print("Updated dataset promoted to replace the old dataset.")

            else: 
                print(f"Error: The updated dataset does not contain new records with latest timestamp. Old max timestamp: {old_max_timestamp}, Updated max timestamp: {updated_max_timestamp}.")
                sys.exit(1)

    else:
        print(f"Error: The updated dataset does not contain the expected number of rows.")
        sys.exit(1)
