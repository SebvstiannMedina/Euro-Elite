import os
import json
import time
import uuid
from google.cloud import bigquery
from google.api_core import exceptions as gcp_exceptions

# Lee configuración desde variables de entorno definidas en el WSGI
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "euroelite-478518")
BQ_DATASET = os.environ.get("BQ_DATASET", "Eventos_EuroElite")
BQ_TABLE = f"{PROJECT_ID}.{BQ_DATASET}.events"  # tabla destino: proyecto.dataset.events


def get_bq_client():
    """
    Crea y devuelve un cliente de BigQuery que usa la variable GOOGLE_APPLICATION_CREDENTIALS
    definida en el entorno (WSGI).
    """
    return bigquery.Client(project=PROJECT_ID)


def _make_row(event_dict):
    """
    Asegura el formato apropiado para BigQuery:
    - event_time: ISO timestamp (BigQuery TIMESTAMP)
    - event_date: YYYY-MM-DD (DATE) — opcional si la tabla está particionada por event_date
    - properties: un JSON serializable (BigQuery JSON)
    """
    row = dict(event_dict)  # copia para no mutar original

    # asegurarse de que event_time y event_date existan (si no, intentar derivar)
    if "event_time" not in row and "ts" in row:
        # si viene como datetime.isoformat() en ts
        row["event_time"] = row.get("ts")
    if "event_date" not in row and row.get("event_time"):
        # derive date
        try:
            row["event_date"] = str(row["event_time"]).split("T")[0]
        except Exception:
            row["event_date"] = None

    # properties como JSON (si viene dict)
    props = row.get("properties") or row.get("props") or {}
    if not isinstance(props, (str, bytes)):
        try:
            row["properties"] = json.dumps(props, ensure_ascii=False)
        except Exception:
            row["properties"] = json.dumps({})
    else:
        row["properties"] = props

    # normalizar user_id a string (opcional)
    if "user_id" in row and row["user_id"] is not None:
        row["user_id"] = str(row["user_id"])

    # event_type / name
    if "event_type" not in row and "name" in row:
        row["event_type"] = row["name"]

    return row


def insert_event(event_dict, max_retries=3):
    """
    Inserta un evento en BigQuery usando insert_rows_json con insertId para deduplicación.
    Devuelve True si se insertó correctamente, False en caso de error.
    """
    client = get_bq_client()

    row = _make_row(event_dict)
    insert_id = row.get("id") or str(uuid.uuid4())  # insertId único por fila

    # BigQuery expects JSON-like dicts; we pass row as-is
    json_rows = [row]

    attempt = 0
    while attempt < max_retries:
        try:
            errors = client.insert_rows_json(BQ_TABLE, json_rows, row_ids=[insert_id])
            if errors:
                # errors is a list of error dictionaries
                print(f"[analytics.bq] BigQuery insert errors: {errors}")
                attempt += 1
                time.sleep(2 ** attempt)
                continue
            return True
        except gcp_exceptions.Aborted as e:
            # transient error, reintentar
            print(f"[analytics.bq] transient error, retrying: {e}")
            attempt += 1
            time.sleep(2 ** attempt)
            continue
        except Exception as e:
            # error grave: loguear y salir
            print(f"[analytics.bq] fatal error inserting to BigQuery: {e}")
            return False

    print("[analytics.bq] failed to insert after retries")
    return False
