from django.core.management.base import BaseCommand
import json

from analytics.models import Event
from analytics import bq
from django.conf import settings


class Command(BaseCommand):
    help = "Push local analytics Event rows to BigQuery in batches."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=500, help="Number of rows per batch sent to BQ")
        parser.add_argument("--start-id", type=int, help="Start from this Event.id (inclusive)")
        parser.add_argument("--limit", type=int, help="Max number of events to push")
        parser.add_argument("--dry-run", action="store_true", help="Do not send to BigQuery, only print what would be sent")

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

            # Parse properties: convert to dict, then serialize back to JSON string for BigQuery
            props = ev.props
            if isinstance(props, str):
                try:
                    props = json.loads(props)
                except Exception:
                    props = {}
            elif props is None:
                props = {}
            
            # Serialize properties as JSON string (BigQuery column is STRING, not RECORD)
            properties_str = json.dumps(props, ensure_ascii=False)

            row = {
                "name": ev.name,
                "ts": ev.ts.isoformat(),
                "user_id": str(ev.user_id) if ev.user_id is not None else None,
                "session_id": ev.session_id,
                "event_type": ev.name,  # or use ev.event_type if you have that field
                "properties": properties_str,  # JSON string, not dict
            }

            batch.append(row)
            sent += 1

            if len(batch) >= batch_size:
                self._flush_batch(batch, dry, sent)
                batch = []

        # flush remainder
        if batch:
            self._flush_batch(batch, dry, sent)

        self.stdout.write(f"Done. Processed {sent} events.")

    def _flush_batch(self, batch, dry, processed_count):
        if dry:
            self.stdout.write(f"[dry-run] would push batch of {len(batch)} (processed so far: {processed_count})")
            if batch:
                self.stdout.write(f"  Sample row: {batch[0]}")
            return

        client = bq.get_bq_client()
        if client is None:
            self.stderr.write("BigQuery client not available (DEBUG=True or credentials missing). Aborting push.")
            return

        try:
            errors = client.insert_rows_json(bq.BQ_TABLE, batch)
            if errors:
                self.stderr.write(f"Errors inserting batch: {errors}")
            else:
                self.stdout.write(f"✓ Pushed batch of {len(batch)} (processed so far: {processed_count})")
        except Exception as e:
            self.stderr.write(f"Exception while inserting batch: {e}")