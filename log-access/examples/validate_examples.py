"""Validate log-access example documents against their schemas.

Static/local validation. Run:
    /tmp/pr13/venv/bin/python log-access/examples/validate_examples.py
"""
import json
import os
import sys

import jsonschema

HERE = os.path.dirname(os.path.abspath(__file__))

PAIRS = [
    ("interaction_raw_event_schema.json", "interaction_raw_event_example.json"),
    ("interaction_redacted_event_schema.json", "interaction_redacted_event_example.json"),
    ("interaction_raw_metadata_event_schema.json", "interaction_raw_metadata_event_chat_example.json"),
    ("interaction_raw_metadata_event_schema.json", "interaction_raw_metadata_event_api_example.json"),
    ("interaction_context_history_schema.json", "interaction_context_history_chat_example.json"),
    ("interaction_context_history_schema.json", "interaction_context_history_api_example.json"),
]


def main():
    failures = 0
    for schema_name, example_name in PAIRS:
        schema = json.load(open(os.path.join(HERE, schema_name)))
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema)
        doc = json.load(open(os.path.join(HERE, example_name)))
        errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
        status = "OK  " if not errors else "FAIL"
        print(f"{status} {example_name} -> {schema_name}")
        for err in errors:
            path = "/".join(str(p) for p in err.path) or "<root>"
            print(f"       [{path}] {err.message}")
        failures += len(errors)
    print("\nfailures:", failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
