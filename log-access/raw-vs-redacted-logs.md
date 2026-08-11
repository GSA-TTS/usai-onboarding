# RAW vs REDACTED Logs - Quick Comparison

**Choose which log bucket to access based on your needs.**

> **Upcoming change — context-history split.** The RAW interaction stream is
> changing so that conversation content is written to a separate S3 object
> instead of being embedded in the streamed event. Existing consumers must be
> updated. See [Upcoming change: context-history split](#upcoming-change-context-history-split)
> below for the new shapes, the migration steps, and what is still unconfirmed.
> Everything above that section describes the format in production today.

---

## Two Options

### REDACTED (Recommended for Most Users)

**Bucket naming:** `usai-{tenant}-core-production-interaction-redacted`

**What you get:**
- Token metrics (`prompt_tokens`, `completion_tokens`, `total_tokens`) and `model`
- PII masked with tokens like `<PERSON>`, `<PHONE>`, `<EMAIL>`
- User IDs (`user_id`), `event_time`, `request_id`, `source`, `stream`, `truncated`

**What you don't get:**
- Actual conversation content
- `latency_ms`, `platform_model_id`, or tool definitions/calls (raw only)

**Example:**
```json
{
  "model": "gemini-2.5-pro",
  "prompt_redacted": {
    "messages": [
      { "role": "user", "content": [ { "type": "text", "text": "Can you contact <PERSON> at <PHONE>?" } ] }
    ],
    "temperature": 0.0
  },
  "response_redacted": {
    "choices": [ { "content": "...", "finish_reason": "stop" } ],
    "usage": { "prompt_tokens": 15, "completion_tokens": 42, "total_tokens": 57 }
  }
}
```

**Use for:**
- Usage analytics ✓
- Cost tracking ✓
- Performance monitoring ✓
- Model comparison ✓
- Token consumption analysis ✓

**Security:** Lower risk, PII already removed

---

### RAW (Full Content)

**Bucket naming:** `usai-{tenant}-core-production-interaction-raw`

**What you get:**
- Everything from REDACTED bucket
- Complete, unredacted conversation text (`prompt` / `response`)
- `platform_model_id`, `latency_ms` (in `usage`)
- Tool definitions (`prompt.tools`, `tool_choice`) and tool calls (`response.choices[].tool_calls`)

**Example:**
```json
{
  "model": "claude-sonnet-4.6",
  "platform_model_id": "inference-profile/us.anthropic.claude-sonnet-4-6",
  "prompt": {
    "messages": [
      { "role": "user", "content": [ { "type": "text", "text": "Can you help me with a Power Query question?" } ] }
    ],
    "tool_choice": "auto",
    "tools": [ { "type": "function", "function": { "name": "read_file", "parameters": { "type": "object" } } } ]
  },
  "response": {
    "choices": [
      { "content": "Of course! I'd be happy to help...", "finish_reason": "tool_calls",
        "tool_calls": [ { "id": "toolu_01ABC", "type": "function", "function": { "name": "read_file", "arguments": "{\"path\": \"src/main.py\"}" } } ] }
    ],
    "usage": { "prompt_tokens": 18452, "completion_tokens": 312, "total_tokens": 18764, "latency_ms": 4210 }
  }
}
```

**Use for:**
- Content quality analysis
- Training data collection
- Detailed investigations
- QA review of responses

**Security:** Higher risk, contains PII and full conversation content

---

## Quick Decision Guide

**Choose REDACTED if you need:**
- Usage statistics
- Performance metrics
- Cost analysis
- Model usage patterns

**Choose RAW if you need:**
- Actual conversation text
- Content analysis
- Quality assurance
- Training data

**Still unsure?** → Start with REDACTED

---

## Technical Details

| Aspect | REDACTED | RAW |
|--------|----------|-----|
| **File size** | ~3-5 KB | ~10-20 KB |
| **PII** | Removed (`<PERSON>`, `<PHONE>`, ...) | Present |
| **Content** | Masked | Full text |
| **Payload keys** | `prompt_redacted` / `response_redacted` | `prompt` / `response` |
| **Token metrics** (`usage`) | Yes | Yes |
| **`latency_ms`** | No | Yes (in `usage`) |
| **`platform_model_id`** | No | Yes |
| **Tools / tool_calls** | No | Yes |
| **User IDs / Timestamps** | Yes | Yes |
| **Security requirement** | Standard | Strict |

---

## Upcoming change: context-history split

**Status:** announced by the platform team; cutover date not yet published.
**Applies to:** the RAW interaction stream. Whether the REDACTED stream also
splits is **not yet confirmed** — see [Open questions](#open-questions) below.

### Why it is changing

As conversation contexts grew, the logged items became too large for Kinesis to
carry reliably. After the change, Kinesis still delivers one event per request to
the same bucket and prefix layout, but that event no longer contains the chat/API
content. The content is written separately to S3, and its location is published on
the event as `context_history_s3_key`.

Benefits:
- Analytics that only need token usage or model selection process far less data.
- No more failures when writing very large objects.

### What each request produces after the split

Both artifacts land in the **same tenant S3 bucket as the metadata event** for
that stream (raw or redacted) — only the key prefix differs. No new bucket is
provisioned for the split.
| Artifact | Delivered via | Location | Schema |
|---|---|---|---|
| **1. Metadata event** | Kinesis Firehose → S3 (unchanged prefix, NDJSON) | `{YEAR}/{MONTH}/{DAY}/{TIMESTAMP}-{UUID}.json` | [`interaction_raw_metadata_event_schema.json`](examples/interaction_raw_metadata_event_schema.json) |
| **2. Context-history document** | Written directly to S3 (single JSON doc, not NDJSON) | `chat/{conversation_id}/{event_id}.json` or `api/{user_id}/{event_id}.json` | [`interaction_context_history_schema.json`](examples/interaction_context_history_schema.json) |

### Metadata event (item 1)

Content fields (`prompt`, `response`) and `truncated` are **gone**. New fields:
`status`, `context_history_s3_key`, top-level `usage`, and `conversation_id` for
chat traffic.

```json
{
  "event_id": "fd0be7bb-48d2-4376-bd4d-774a965a779d",
  "event_time": "2026-07-23T17:46:33.705182+00:00",
  "source": "chat",
  "stream": true,
  "kind": "chat_completion",
  "user_id": "9506e4f2-2b17-41e6-8ecc-b9c730b394c2",
  "conversation_id": "e2065dd3-75ae-405c-aa81-2faef48853bd",
  "request_id": "20b7b796-dafa-415f-a5ae-a753678cef2c",
  "model": "gpt-5.5",
  "platform_model_id": "gpt-5.5-DefaultV2",
  "usage": { "prompt_tokens": 2237, "completion_tokens": 38, "total_tokens": 2275, "latency_ms": null },
  "status": "success",
  "context_history_s3_key": "chat/e2065dd3-75ae-405c-aa81-2faef48853bd/fd0be7bb-48d2-4376-bd4d-774a965a779d.json"
}
```

Full examples: [chat](examples/interaction_raw_metadata_event_chat_example.json),
[api](examples/interaction_raw_metadata_event_api_example.json).

### Context-history document (item 2)

Fetched from the key above. Holds `prompt` (with `messages`, `tools`,
`tool_choice`) and `response` (with `choices`), plus `user_id` and, for chat
traffic, `conversation_id`.

```json
{
  "user_id": "local-api",
  "prompt": {
    "messages": [ { "role": "user", "content": [ { "type": "text", "text": "Hello" } ] } ]
  },
  "response": {
    "choices": [ { "content": "Hello! It's nice to meet you...", "finish_reason": "stop" } ],
    "usage": { "prompt_tokens": 36, "completion_tokens": 24, "total_tokens": 60 }
  }
}
```

Full examples: [chat](examples/interaction_context_history_chat_example.json),
[api](examples/interaction_context_history_api_example.json).

### Token usage location

Read `usage` **from the metadata event first, then fall back to the
context-history document** at `response.usage`. This is the same order used by the
USAi console pipeline, the reference consumer for these logs: it reads top-level
`usage` and only consults `response.usage` for old-format records.

The published samples show both placements — chat traffic carries `usage` on the
metadata event, while an API sample carried it only inside the context document —
so defensive reads remain the correct approach:

```bash
# Token totals from metadata events, falling back is not possible in one pass —
# read the metadata event value and treat null/absent as "fetch the context doc".
jq -c '{event_id, model, total: (.usage.total_tokens // null),
        context_history_s3_key}' log.json
```

```python
usage = event.get("usage") or {}
if not usage.get("total_tokens"):
    ctx = json.load(s3.get_object(Bucket=bucket, Key=event["context_history_s3_key"])["Body"])
    usage = ctx.get("response", {}).get("usage", {})
```

### Field-by-field delta (RAW stream)

| Field | Before (inline) | After (split) |
|---|---|---|
| `prompt` / `response` | On the event | Moved to the context-history document |
| `truncated` | Required on the event | Removed (the split makes truncation unnecessary) |
| `usage` | `response.usage` | Top-level `usage` on the metadata event (fall back to `response.usage` in the context doc) |
| `usage.latency_ms` | Integer | Integer **or `null`** |
| `status` | Not present | New, e.g. `"success"` |
| `context_history_s3_key` | Not present | New; pointer to the content object |
| `conversation_id` | Undocumented but emitted for chat | Documented; also a path segment of the content key |
| `event_id`, `event_time`, `source`, `stream`, `kind`, `user_id`, `request_id`, `model`, `platform_model_id` | Unchanged | Unchanged |

### Migration checklist for consumers

1. Stop requiring `prompt`, `response`, and `truncated` on streamed events.
2. Read `usage` from the top level, with a fallback to the context document.
3. Allow `usage.latency_ms` to be `null`.
4. Add a second S3 `GetObject` for `context_history_s3_key` wherever you need
   conversation content. Handle a missing or not-yet-written object with a retry.
5. Update any jq/SQL/Glue/Athena projections that reference `.response.usage`,
   `.prompt.messages`, or `truncated`.
6. Confirm your IAM policy grants `s3:GetObject` on the `chat/*` and `api/*`
   prefixes. The context-history documents are written to the **same bucket** you
   read today, so no new bucket access is needed — but a policy scoped narrowly to
   the dated `{YEAR}/{MONTH}/{DAY}/*` prefix will not cover them. Policies granting
   bucket-wide read need no change; request an updated policy if yours is
   prefix-scoped.

### Open questions

These are unresolved with the platform team; this guide will be updated when they
are answered. Do not assume an answer.

1. **Cutover date**, and whether old-format and new-format objects will coexist
   in the same prefix during a transition window.
2. **Redacted stream** — does it split too, and is the context-history document
   PII-redacted for the redacted tenant path? Tracked in
   GSA-TTS/usai-console-pipeline#84, which flags that the redaction job may not
   yet read the new prefixes. Until that is resolved, treat this document as
   describing the **raw** stream only.
3. **`status` values** — the full set, and whether `truncated` is fully retired.
4. **Retention and SQS notifications** for context-history objects — are S3
   event notifications emitted for them, or only for the firehose objects?

### Resolved

- **Same bucket.** Context-history documents are written to the same tenant bucket
  as the metadata events; no separate bucket is provisioned. Only the key prefix
  differs.
- **Canonical `usage` location.** Read top-level `usage` first, then fall back to
  `response.usage` in the context document. This matches the reference consumer in
  the USAi console pipeline, which reads top-level `usage` and only consults
  `response.usage` for old-format records.

Questions or migration help: [usai-security@gsa.gov](mailto:usai-security@gsa.gov).

---

## Both Buckets Available

You can access either or both buckets. The notification infrastructure (SQS queue) can be set up for either bucket - just specify which one you want when requesting access.

**Python script configuration:**
```python
# For REDACTED logs
BUCKET_NAME = "usai-{tenant}-core-production-interaction-redacted"

# For RAW logs
BUCKET_NAME = "usai-{tenant}-core-production-interaction-raw"
```

---

## Recommendation

**Start with REDACTED:**
- Covers 90% of use cases
- Lower security risk
- Easier to get approved
- Can add RAW access later if needed

**Only choose RAW if:**
- You specifically need conversation content
- You have security controls for PII
- You're doing quality assurance work

---

## How is PII Detected?

REDACTED logs use 19 regex patterns to detect and mask PII including names, emails, SSNs, phone numbers, addresses, and more.

**Full details:** See [PII_REDACTION_COMPLETE.md](PII_REDACTION_COMPLETE.md) for complete methodology, detected PII types, and examples.

---

**Questions?** Contact your infrastructure team.

**Last updated:** 2026-02-02
**Platforms:** Works on Windows, macOS, and Linux
**Related:** [PII_REDACTION_COMPLETE.md](PII_REDACTION_COMPLETE.md) - Complete PII detection methodology
