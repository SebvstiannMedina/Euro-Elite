"""
Crea tabla en BigQuery con `properties` como STRING (JSON serializado).

Esto mantiene flexibilidad: no se requiere un esquema fijo para campos anidados.

Uso:
  python analytics/create_bq_table_simple.py --project my-project --dataset Eventos_EuroElite --table eventos

Opciones:
  --dry-run: imprime el esquema y no crea la tabla.
  --credentials: ruta alternativa a GOOGLE_APPLICATION_CREDENTIALS.
"""

import argparse
import os
import sys

try:
    from google.cloud import bigquery
except Exception:
    bigquery = None


def build_schema():
    return [
        bigquery.SchemaField("name", "STRING", mode="REQUIRED", description="Nombre del evento"),
        bigquery.SchemaField("ts", "TIMESTAMP", mode="REQUIRED", description="Timestamp del evento"),
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE", description="ID del usuario"),
        bigquery.SchemaField("session_id", "STRING", mode="NULLABLE", description="ID de sesión"),
        bigquery.SchemaField("event_type", "STRING", mode="REQUIRED", description="Tipo de evento"),
        bigquery.SchemaField("properties", "STRING", mode="NULLABLE", description="Propiedades como JSON string"),
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create BigQuery simple table with properties as STRING.")
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
            print([{"name": f.name, "type": f.field_type, "mode": f.mode} for f in schema])
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
        existing = client.get_table(table_id)
        print(f"✓ Tabla ya existe: {existing.table_id}")
        print(f"  Filas: {existing.num_rows}")
        print(f"  Tamaño: {existing.num_bytes} bytes")
        return 0
    except Exception:
        try:
            created = client.create_table(bq_table)
            print(f"✓ Tabla creada: {created.table_id}")
            print(f"✓ Particionada por: ts (diaria)")
            print(f"✓ Clustering por: name, user_id")
            print(f"✓ Retención: 90 días")
            return 0
        except Exception as e:
            print(f"✗ Error creando tabla: {e}")
            return 3


if __name__ == "__main__":
    sys.exit(main())
