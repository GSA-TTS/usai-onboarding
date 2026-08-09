# RAW vs REDACTED Logs - Quick Comparison

**Choose which log bucket to access based on your needs.**

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
