# Checks whether the latest IESO demand file contains new hourly records that are not yet stored in the processed Parquet dataset.

import duckdb

with open("sql/incremental/01_identify_new_rows.sql", "r") as f:
    sql = f.read()

result = duckdb.sql(sql)
rows = result.fetchall()
new_row_count = len(rows)

if new_row_count == 0:
    print("No new rows found. Pipeline stopped.")
else: 
    print("New rows:", new_row_count)