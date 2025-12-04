# analytics/create_bq_table.py
import os
from google.cloud import bigquery

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "/home/Jehison/.secrets/euroelite-478518-513802434b73.json")
PROJECT = "euroelite-478518"
DATASET = "Eventos_EuroElite"
TABLE_ID = f"{PROJECT}.{DATASET}.events"

client = bigquery.Client(project=PROJECT)

schema = [
    bigquery.SchemaField("event_time", "TIMESTAMP"),
    bigquery.SchemaField("event_date", "DATE"),
    bigquery.SchemaField("user_id", "STRING"),
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("event_type", "STRING"),
    bigquery.SchemaField("properties", "STRING"),
]

table = bigquery.Table(TABLE_ID, schema=schema)
# particionado por event_date
table.time_partitioning = bigquery.TimePartitioning(field="event_date")
table = client.create_table(table, exists_ok=True)  # exists_ok soportado en versiones recientes
print("Created (or confirmed) table:", table.table_id)