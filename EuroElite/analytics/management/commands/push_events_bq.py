from django.core.management.base import BaseCommand
import json
from datetime import datetime

from analytics.models import Event
from analytics import bq


class Command(BaseCommand):
    help = "Push local analytics Event rows to BigQuery in batches."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=500)
        parser.add_argument("--start-id", type=int)
        parser.add_argument("--limit", type=int)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        batch_size = options.get("batch_size") or 500
        start_id = options.get("start_id")
        limit = options.get("limit")
        dry = options.get("dry_run")

        qs = Event.objects.all().order_by("id")
        if start_id:
            qs = qs.filter(id__gte=start_id)

        total = qs.count()
        if limit:
            total = min(total, limit)

        self.stdout.write(f"Preparing to push up to {total} events (dry_run={dry})")

        sent = 0
        batch = []

        for ev in qs.iterator():
            if limit and sent >= limit:
                break

            # Parse properties: convert to dict if needed
            props = ev.props
            if isinstance(props, str):
                try:
                    props = json.loads(props)
                except Exception:
                    props = {}
            elif props is None:
                props = {}
            elif not isinstance(props, dict):
                props = {}

            # Serialize properties as JSON string (for BigQuery STRING column)
            try:
                properties_json = json.dumps(props, ensure_ascii=False, default=str)
            except Exception:
                properties_json = "{}"

            # Build row with all fields serialized properly
            row = {
                "name": ev.name,
                "ts": ev.ts.isoformat(),  # ISO format timestamp string
                "user_id": str(ev.user_id) if ev.user_id else None,
                "session_id": ev.session_id,
                "event_type": ev.name,
                "properties": properties_json,  # JSON string, not dict
            }

            batch.append(row)
            sent += 1

            if len(batch) >= batch_size:
                self._flush_batch(batch, dry, sent)
                batch = []

        # Flush remainder
        if batch:
            self._flush_batch(batch, dry, sent)

        self.stdout.write(f"Done. Processed {sent} events.")

    def _flush_batch(self, batch, dry, processed_count):
        if dry:
            self.stdout.write(f"[dry-run] would push {len(batch)} rows (processed {processed_count})")
            if batch:
                # Print sample row for debugging
                sample = batch[0].copy()
                if "properties" in sample and len(sample["properties"]) > 100:
                    sample["properties"] = sample["properties"][:100] + "..."
                self.stdout.write(f"  Sample: {sample}")
            return

        client = bq.get_bq_client()
        if client is None:
            self.stderr.write("BigQuery client not available. Aborting.")
            return

        try:
            errors = client.insert_rows_json(bq.BQ_TABLE, batch)
            if errors:
                self.stderr.write(f"Errors inserting batch: {errors}")
            else:
                self.stdout.write(f"✓ Pushed {len(batch)} rows (processed {processed_count})")
        except Exception as e:
            self.stderr.write(f"Exception while inserting batch: {e}")
