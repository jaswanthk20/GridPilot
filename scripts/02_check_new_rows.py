import duckdb

with open("sql/incremental/01_identify_new_rows.sql", "r") as f:
    sql = f.read()

result = duckdb.sql(sql)
rows = result.fetchall()

print("New rows:", len(rows))