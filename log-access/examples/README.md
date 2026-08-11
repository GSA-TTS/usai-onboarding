# Interaction Log Schemas and Examples

Canonical JSON Schemas (draft 2020-12) and matching examples for USAi interaction
logs. Two format generations are represented here.

## Current format (in production today)

Content is inline on each streamed NDJSON event.

| File | Purpose |
|---|---|
| [`interaction_raw_event_schema.json`](interaction_raw_event_schema.json) | RAW event, content inline |
| [`interaction_raw_event_example.json`](interaction_raw_event_example.json) | Example RAW event |
| [`interaction_redacted_event_schema.json`](interaction_redacted_event_schema.json) | REDACTED event, content inline |
| [`interaction_redacted_event_example.json`](interaction_redacted_event_example.json) | Example REDACTED event |

## Split format (upcoming — context-history split)

Each request produces a small metadata event plus a separate S3 document holding
the conversation content. Applies to the RAW stream; the REDACTED stream's
behavior is not yet confirmed. Cutover date not yet published.

| File | Purpose |
|---|---|
| [`interaction_raw_metadata_event_schema.json`](interaction_raw_metadata_event_schema.json) | Metadata event with `context_history_s3_key` |
| [`interaction_raw_metadata_event_chat_example.json`](interaction_raw_metadata_event_chat_example.json) | Example metadata event, `source: "chat"` |
| [`interaction_raw_metadata_event_api_example.json`](interaction_raw_metadata_event_api_example.json) | Example metadata event, `source: "api"` |
| [`interaction_context_history_schema.json`](interaction_context_history_schema.json) | The content document at `context_history_s3_key` |
| [`interaction_context_history_chat_example.json`](interaction_context_history_chat_example.json) | Example content document, chat traffic |
| [`interaction_context_history_api_example.json`](interaction_context_history_api_example.json) | Example content document, API traffic |

Narrative documentation, the field-by-field delta, and the consumer migration
checklist are in
[`../raw-vs-redacted-logs.md`](../raw-vs-redacted-logs.md#upcoming-change-context-history-split).

## Note on artifact shape

The metadata events are **NDJSON** — one JSON object per line in the delivered S3
object. The `*_example.json` files here are pretty-printed single objects for
readability; a real log file has one compact object per line.

The context-history documents are **single JSON documents**, not NDJSON.

## Validating a sample against these schemas

```bash
python3 -m venv .venv && .venv/bin/pip install jsonschema
```

```python
import json
import jsonschema

schema = json.load(open("interaction_raw_metadata_event_schema.json"))
validator = jsonschema.Draft202012Validator(schema)

with open("log.json") as f:                 # NDJSON from S3
    for lineno, line in enumerate(f, 1):
        for err in validator.iter_errors(json.loads(line)):
            path = "/".join(str(p) for p in err.path) or "<root>"
            print(f"line {lineno} [{path}]: {err.message}")
```

Note that these schemas do not set `additionalProperties: false`. Unknown fields
are allowed so that a new platform field does not break tenant validation; run the
loop above after any platform release to spot fields worth adopting.
