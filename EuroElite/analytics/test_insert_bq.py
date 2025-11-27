# test_insert_bq.py
import os, json, datetime
from google.cloud import bigquery

# asegurar la variable (opcional, si WSGI ya la define)
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "/home/Jehison/.secrets/euroelite-478518-513802434b73.json")

PROJECT = "euroelite-478518"
DATASET = "Eventos_EuroElite"
TABLE = f"{PROJECT}.{DATASET}.events"

client = bigquery.Client(project=PROJECT)

row = {
    "event_time": datetime.datetime.utcnow().isoformat()+"Z",
    "event_date": datetime.date.today().isoformat(),
    "user_id": "test-user-1",
    "session_id": "test-session-123",
    "event_type": "test_event",
    "properties": json.dumps({"test": True})
}

errors = client.insert_rows_json(TABLE, [row], row_ids=[None])
if errors:
    print("Errores al insertar:", errors)
else:
    print("Insertado OK")
