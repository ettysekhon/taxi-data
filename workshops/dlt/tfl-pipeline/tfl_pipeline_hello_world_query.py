import dlt

pipeline = dlt.attach("hello_pipeline")
with pipeline.sql_client() as client:
    result = client.execute_sql("SELECT * FROM tube_data.stations")
    for row in result:
        print(row)
