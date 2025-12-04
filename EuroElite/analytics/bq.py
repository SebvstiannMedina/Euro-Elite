import os
import json
import time
import uuid
import threading
from django.conf import settings
from google.cloud import bigquery
from google.api_core import exceptions as gcp_exceptions

# Lee configuración desde variables de entorno definidas en el WSGI
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "euroelite-478518")
BQ_DATASET = os.environ.get("BQ_DATASET", "Eventos_EuroElite")
BQ_TABLE = f"{PROJECT_ID}.{BQ_DATASET}.eventos"  # tabla destino: proyecto.dataset.eventos


def get_bq_client():
    """
    Crea y devuelve un cliente de BigQuery que usa la variable GOOGLE_APPLICATION_CREDENTIALS
    definida en el entorno (WSGI).
    """
    # No inicializar BigQuery en entornos de desarrollo/DEBUG
    try:
        if getattr(settings, "DEBUG", False):
            print("[analytics.bq] DEBUG=True -> BigQuery deshabilitado en entorno local")
            return None
    except Exception:
        # Si por alguna razón settings no está disponible, no romper
        pass

    # Forzar project desde settings si está definido, sino usar PROJECT_ID
    project = getattr(settings, "GCP_PROJECT_ID", PROJECT_ID)

    try:
        return bigquery.Client(project=project)
    except Exception as e:
        print(f"[analytics.bq] ERROR creando cliente BigQuery para proyecto '{project}': {e}")
        return None


def _make_row(event_dict):
    """
    Asegura el formato apropiado para BigQuery según la estructura de la tabla:
    - name: STRING
    - ts: TIMESTAMP (ISO format)
    - user_id: STRING
    - session_id: STRING
    - event_type: STRING
    - properties: STRING (JSON serializado)
    """
    row = dict(event_dict)  # copia para no mutar original

    # Asegurar que ts existe y está en formato ISO
    if "ts" not in row and "event_time" in row:
        row["ts"] = row["event_time"]
    
    if "ts" in row and row["ts"]:
        # Convertir a ISO format si es necesario
        ts_val = row["ts"]
        if hasattr(ts_val, "isoformat"):
            row["ts"] = ts_val.isoformat()
        else:
            row["ts"] = str(ts_val)

    # name (usar event_type si no existe name)
    if "name" not in row and "event_type" in row:
        row["name"] = row["event_type"]

    # event_type (defaultear a name si no existe)
    if "event_type" not in row and "name" in row:
        row["event_type"] = row["name"]

    # user_id a string
    if "user_id" in row and row["user_id"] is not None:
        row["user_id"] = str(row["user_id"])
    else:
        row["user_id"] = None

    # session_id a string
    if "session_id" in row and row["session_id"] is not None:
        row["session_id"] = str(row["session_id"])

    # properties como JSON string (no como dict)
    props = row.get("properties") or row.get("props") or {}
    if isinstance(props, str):
        try:
            props = json.loads(props)
        except Exception:
            props = {}
    elif not isinstance(props, dict):
        props = {}
    
    # Serializar a JSON string
    try:
        row["properties"] = json.dumps(props, ensure_ascii=False)
    except Exception:
        row["properties"] = "{}"

    # Remover campos que no existen en la tabla
    fields_to_keep = {"name", "ts", "user_id", "session_id", "event_type", "properties"}
    row = {k: v for k, v in row.items() if k in fields_to_keep}

    return row


def insert_event(event_dict, max_retries=3):
    """
    Inserta un evento en BigQuery usando insert_rows_json con insertId para deduplicación.
    Devuelve True si se insertó correctamente, False en caso de error.
    """
    client = get_bq_client()
    if client is None:
        # BigQuery no está disponible (modo DEBUG o credenciales faltantes)
        print("[analytics.bq] BigQuery client not available — skipping insert")
        return False

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


def insert_event_async(event_dict):
    """
    Inserta en background usando un hilo daemon. Útil para no bloquear la respuesta HTTP.
    """
    # Evitar crear hilos innecesarios si BigQuery no está disponible
    try:
        if get_bq_client() is None:
            print("[analytics.bq] BigQuery deshabilitado — no se crea hilo async")
            return False
    except Exception:
        pass

    try:
        t = threading.Thread(target=insert_event, args=(event_dict,), kwargs={}, daemon=True)
        t.start()
        return True
    except Exception as e:
        print(f"[analytics.bq] failed to start background insert: {e}")
        return False
