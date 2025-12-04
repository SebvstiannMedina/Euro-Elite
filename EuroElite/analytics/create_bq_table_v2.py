"""
Crea tabla mejorada en BigQuery con properties como RECORD (JSON) en lugar de STRING.

Uso:
  python analytics/create_bq_table_v2.py --project my-project --dataset Eventos_EuroElite --table eventos

Opciones:
  --dry-run: imprime el esquema y no crea la tabla.
  --credentials: ruta alternativa a GOOGLE_APPLICATION_CREDENTIALS.

Nota: en desarrollo, no ejecutar sin credenciales válidas o con `DEBUG=True`.
"""

import argparse
import json
import os
import sys

try:
    from google.cloud import bigquery
    from google.api_core.exceptions import Conflict
except Exception:
    bigquery = None


def build_schema():
    # Esquema con properties como RECORD (JSON)
    return [
        bigquery.SchemaField("name", "STRING", mode="REQUIRED", description="Nombre del evento"),
        bigquery.SchemaField("ts", "TIMESTAMP", mode="REQUIRED", description="Timestamp del evento"),
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE", description="ID del usuario autenticado"),
        bigquery.SchemaField("session_id", "STRING", mode="NULLABLE", description="ID de sesión"),
        bigquery.SchemaField("event_type", "STRING", mode="REQUIRED", description="Tipo de evento"),
        bigquery.SchemaField(
            "properties",
            "RECORD",
            mode="NULLABLE",
            fields=[
                bigquery.SchemaField(
                    "request",
                    "RECORD",
                    mode="NULLABLE",
                    fields=[
                        bigquery.SchemaField("url", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("path", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("method", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("host", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("scheme", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField(
                            "user_agent_parsed",
                            "RECORD",
                            mode="NULLABLE",
                            fields=[
                                bigquery.SchemaField("raw", "STRING", mode="NULLABLE"),
                                bigquery.SchemaField("is_mobile", "BOOLEAN", mode="NULLABLE"),
                                bigquery.SchemaField("is_bot", "BOOLEAN", mode="NULLABLE"),
                                bigquery.SchemaField("browser", "STRING", mode="NULLABLE"),
                                bigquery.SchemaField("os", "STRING", mode="NULLABLE"),
                            ],
                        ),
                        bigquery.SchemaField("referrer", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("ip", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField(
                            "query_params",
                            "RECORD",
                            mode="NULLABLE",
                            fields=[
                                bigquery.SchemaField("key", "STRING", mode="REPEATED"),
                                bigquery.SchemaField("value", "STRING", mode="REPEATED"),
                            ],
                        ),
                        bigquery.SchemaField("accept_language", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("accept_encoding", "STRING", mode="NULLABLE"),
                    ],
                ),
                bigquery.SchemaField(
                    "user",
                    "RECORD",
                    mode="NULLABLE",
                    fields=[
                        bigquery.SchemaField("is_authenticated", "BOOLEAN", mode="NULLABLE"),
                        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("username", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("email", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("first_name", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("last_name", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("is_staff", "BOOLEAN", mode="NULLABLE"),
                        bigquery.SchemaField("is_superuser", "BOOLEAN", mode="NULLABLE"),
                        bigquery.SchemaField("date_joined", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("last_login", "STRING", mode="NULLABLE"),
                    ],
                ),
                bigquery.SchemaField(
                    "session",
                    "RECORD",
                    mode="NULLABLE",
                    fields=[
                        bigquery.SchemaField("session_id", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("session_create_date", "STRING", mode="NULLABLE"),
                    ],
                ),
                bigquery.SchemaField(
                    "browser_context",
                    "RECORD",
                    mode="NULLABLE",
                    fields=[
                        bigquery.SchemaField("viewport_width", "INT64", mode="NULLABLE"),
                        bigquery.SchemaField("viewport_height", "INT64", mode="NULLABLE"),
                        bigquery.SchemaField("screen_width", "INT64", mode="NULLABLE"),
                        bigquery.SchemaField("screen_height", "INT64", mode="NULLABLE"),
                        bigquery.SchemaField("timezone", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("language", "STRING", mode="NULLABLE"),
                        bigquery.SchemaField("is_online", "BOOLEAN", mode="NULLABLE"),
                    ],
                ),
                bigquery.SchemaField("duration_ms", "INT64", mode="NULLABLE"),
                bigquery.SchemaField("status_code", "INT64", mode="NULLABLE"),
                bigquery.SchemaField("is_error", "BOOLEAN", mode="NULLABLE"),
                bigquery.SchemaField("timestamp", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("error", "STRING", mode="NULLABLE"),
            ],
        ),
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create BigQuery table with RECORD properties for analytics events.")
    parser.add_argument("--project", required=False, help="GCP project id")
    parser.add_argument("--dataset", default="Eventos_EuroElite", help="BigQuery dataset name")
    parser.add_argument("--table", default="eventos", help="BigQuery table name")
    parser.add_argument("--credentials", help="Path to a service account JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Print schema and exit without creating the table")
    args = parser.parse_args(argv)

    project = args.project or os.environ.get("GCP_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT")
    dataset = args.dataset
    table = args.table

    if args.credentials:
        os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", args.credentials)

    if args.dry_run:
        print("Dry-run: schema to be created:")
        if bigquery is None:
            print(" - google-cloud-bigquery package not available in environment.")
        else:
            schema = build_schema()
            print(json.dumps([{"name": f.name, "type": f.field_type, "mode": f.mode} for f in schema], indent=2, default=str))
        print("\nNo changes made (dry-run).")
        return 0

    if bigquery is None:
        print("google-cloud-bigquery no está instalado. Instálelo con: pip install google-cloud-bigquery")
        return 2

    if not project:
        print("No se ha especificado el project. Pásalo con --project o configura GCP_PROJECT_ID/GOOGLE_CLOUD_PROJECT.")
        return 2

    table_id = f"{project}.{dataset}.{table}"

    client = bigquery.Client(project=project)

    schema = build_schema()

    bq_table = bigquery.Table(table_id, schema=schema)
    bq_table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="ts",
        expiration_ms=90 * 24 * 60 * 60 * 1000,
    )
    bq_table.clustering_fields = ["name", "user_id"]

    try:
        # Si la tabla ya existe, get_table no lanzará excepción
        existing = client.get_table(table_id)
        print(f"La tabla ya existe: {existing.table_id}. No se modifica el esquema automáticamente.")
        print("Si necesita cambios en el esquema, actualícelos manualmente en BigQuery.")
        return 0
    except Exception:
        # No existe: crear
        try:
            created = client.create_table(bq_table)
            print(f"✓ Tabla creada: {created.table_id}")
            print(f"  Particionada por: ts (diaria)")
            print(f"  Clustering por: {', '.join(created.clustering_fields or [])}")
            return 0
        except Conflict:
            print("La tabla ya existe (conflict).")
            return 0
        except Exception as e:
            print(f"Error creando tabla: {e}")
            return 3


if __name__ == "__main__":
    sys.exit(main())
