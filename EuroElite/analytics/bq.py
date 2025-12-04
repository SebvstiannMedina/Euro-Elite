import os
import json
import time
import uuid
import threading
from django.conf import settings
from google.cloud import bigquery
from google.api_core import exceptions as gcp_exceptions

# Configuración desde variables de entorno
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "euroelite-478518")
BQ_DATASET = os.environ.get("BQ_DATASET", "Eventos_EuroElite")
BQ_TABLE = f"{PROJECT_ID}.{BQ_DATASET}.eventos"


def get_bq_client():
    """
    Crea y devuelve un cliente de BigQuery.
    Retorna None si DEBUG=True o credenciales faltantes.
    """
    try:
        if getattr(settings, "DEBUG", False):
            print("[analytics.bq] DEBUG=True -> BigQuery deshabilitado")
            return None
    except Exception:
        pass

    project = getattr(settings, "GCP_PROJECT_ID", PROJECT_ID)

    try:
        return bigquery.Client(project=project)
    except Exception as e:
        print(f"[analytics.bq] ERROR creando cliente BigQuery: {e}")
        return None


def _serialize_value(val):
    """Serializa un valor de forma segura para JSON."""
    if val is None:
        return None
    if isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, dict):
        return {k: _serialize_value(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [_serialize_value(v) for v in val]
    # Para datetime, date, etc.
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


def _make_row(event_dict):
    """
    Asegura el formato correcto para BigQuery.
    - name: STRING (requerido)
    - ts: TIMESTAMP ISO string (requerido)
    - user_id: STRING (opcional)
    - session_id: STRING (opcional)
    - event_type: STRING (requerido)
    - properties: STRING JSON (opcional)
    """
    row = {}

    # name
    row["name"] = event_dict.get("name") or event_dict.get("event_type") or "unknown"

    # ts: asegurar ISO format
    ts = event_dict.get("ts") or event_dict.get("event_time")
    if ts:
        if hasattr(ts, "isoformat"):
            row["ts"] = ts.isoformat()
        else:
            row["ts"] = str(ts)
    else:
        # Fallback: fecha actual
        from django.utils import timezone
        row["ts"] = timezone.now().isoformat()

    # user_id: convertir a string
    user_id = event_dict.get("user_id")
    row["user_id"] = str(user_id) if user_id is not None else None

    # session_id: convertir a string
    session_id = event_dict.get("session_id")
    row["session_id"] = str(session_id) if session_id else None

    # event_type
    row["event_type"] = event_dict.get("event_type") or row["name"]

    # properties: JSON string
    props = event_dict.get("properties") or {}
    
    # Si ya es string, parsearlo y re-serializarlo (asegurar validez)
    if isinstance(props, str):
        try:
            props = json.loads(props)
        except Exception:
            props = {}
    elif not isinstance(props, dict):
        props = {}

    # Serializar propiedades
    try:
        # Asegurar que todos los valores sean serializables
        props_clean = _serialize_value(props)
        row["properties"] = json.dumps(props_clean, ensure_ascii=False)
    except Exception as e:
        print(f"[analytics.bq] error serializing properties: {e}")
        row["properties"] = "{}"

    return row


def insert_event(event_dict, max_retries=3):
    """
    Inserta un evento en BigQuery.
    Retorna True si éxito, False si error.
    """
    client = get_bq_client()
    if client is None:
        print("[analytics.bq] BigQuery client not available")
        return False

    row = _make_row(event_dict)
    insert_id = str(uuid.uuid4())

    json_rows = [row]

    attempt = 0
    while attempt < max_retries:
        try:
            errors = client.insert_rows_json(BQ_TABLE, json_rows, row_ids=[insert_id])
            if errors:
                print(f"[analytics.bq] BigQuery insert errors: {errors}")
                attempt += 1
                time.sleep(2 ** attempt)
                continue
            return True
        except gcp_exceptions.Aborted as e:
            print(f"[analytics.bq] transient error, retrying: {e}")
            attempt += 1
            time.sleep(2 ** attempt)
            continue
        except Exception as e:
            print(f"[analytics.bq] fatal error: {e}")
            return False

    print("[analytics.bq] failed to insert after retries")
    return False


def insert_event_async(event_dict):
    """
    Inserta evento en background (hilo daemon).
    """
    try:
        if get_bq_client() is None:
            return False
    except Exception:
        pass

    try:
        t = threading.Thread(target=insert_event, args=(event_dict,), daemon=True)
        t.start()
        return True
    except Exception as e:
        print(f"[analytics.bq] failed to start background insert: {e}")
        return False
