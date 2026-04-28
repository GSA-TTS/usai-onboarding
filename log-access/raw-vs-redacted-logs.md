# RAW vs REDACTED Logs - Quick Comparison

**Choose which log bucket to access based on your needs.**

---

## Two Options

### REDACTED (Recommended for Most Users)

**Bucket naming:** `usai-{tenant}-core-production-interaction-redacted`

**What you get:**
- All performance metrics (latency, tokens, model)
- PII masked with `<PERSON>` tags
- User IDs, timestamps, session data
- Original and redacted text lengths

**What you don't get:**
- Actual conversation content

**Example:**
```json
{
  "prompt_redacted": {
    "content": "Can <PERSON> help with <PERSON>?"
  },
  "tokens_prompt": 15,
  "latency_ms": 2595,
  "model": "google_vertex_manifold_pipeline.gemini-2.5-flash"
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
- Complete, unredacted conversation text
- Full prompts and responses

**Example:**
```json
{
  "prompt": {
    "content": "Can you help me with a Power Query question?"
  },
  "response": {
    "content": "Of course! I'd be happy to help..."
  },
  "tokens_prompt": 15,
  "latency_ms": 2595
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
| **PII** | Removed | Present |
| **Content** | Masked | Full text |
| **Metrics** | Complete | Complete |
| **User IDs** | Yes | Yes |
| **Timestamps** | Yes | Yes |
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
