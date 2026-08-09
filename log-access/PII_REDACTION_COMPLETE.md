# PII Redaction Methodology - Complete Documentation

**For:** Tenant administrators
**Question:** How is PII detected and redacted in REDACTED logs?
**Source:** `console-data/utils/redact_pii.py`
**Last Updated:** 2026-02-02

---

## Overview

USAI uses **regex-based pattern matching** to automatically detect and redact PII from analytics logs. The redaction process runs as a batch job that reads from the RAW bucket and writes redacted logs to the REDACTED bucket.

---

## Technology Used

**Method:** Regex (Regular Expression) Pattern Matching
**Library:** Python standard library `re` module
**Processing:** Batch process (S3 to S3)
**Implementation:** `console-data/utils/redact_pii.py`

### Why Regex?

**Alternatives Tested:**
- **StarPII** - Open source Named Entity Recognition (NER) model
- **Presidio** - Microsoft's PII detection framework

**Decision:** Regex was chosen despite having a **high false positive rate** (over-redacts)

**Rationale:**
- ✅ **Safer to over-redact than under-redact** - False positives (extra redaction) are safer than false negatives (missed PII)
- ✅ **Simple and deployable** - No ML model dependencies, easier to maintain
- ✅ **Predictable behavior** - Regex patterns are deterministic and auditable
- ✅ **Sufficient for use case** - Meets security requirements for REDACTED bucket

**Trade-off:** Some non-PII content may be redacted (false positives), but this is acceptable to ensure PII protection.

---

## What PII Types Are Detected?

The system detects **19 different types** of PII:

| PII Type | Example | Replacement Tag | Regex-Based |
|----------|---------|-----------------|-------------|
| **Person Names** | John Smith | `<PERSON>` | ✅ |
| **Email Addresses** | user@example.com | `<EMAIL>` | ✅ |
| **Phone Numbers** | (555) 123-4567 | `<PHONE>` | ✅ |
| **Social Security Numbers** | 123-45-6789 | `<SSN>` | ✅ |
| **Credit Card Numbers** | 4111111111111111 | `<CREDIT_CARD>` | ✅ |
| **IP Addresses** | 192.168.1.1 | `<IP_ADDRESS>` | ✅ |
| **Dates** | 01/15/2024 | `<DATE>` | ✅ |
| **US Driver Licenses** | A1234567 | `<DRIVER_LICENSE>` | ✅ |
| **Passports** | US1234567 | `<PASSPORT>` | ✅ |
| **Bank Account Numbers** | 123456789012 | `<BANK_ACCOUNT>` | ✅ |
| **Routing Numbers** | 021000021 | `<ROUTING_NUMBER>` | ✅ |
| **URLs** | https://example.com | `<URL>` | ✅ |
| **Street Addresses** | 123 Main Street | `<ADDRESS>` | ✅ |
| **ZIP Codes** | 12345-6789 | `<ZIP_CODE>` | ✅ |
| **Medical Record Numbers** | MRN: 1234567 | `<MEDICAL_RECORD>` | ✅ |
| **Bitcoin Addresses** | 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa | `<BITCOIN_ADDRESS>` | ✅ |
| **IBAN** | GB82WEST12345698765432 | `<IBAN>` | ✅ |
| **MAC Addresses** | 00:1B:44:11:3A:B7 | `<MAC_ADDRESS>` | ✅ |
| **GUIDs/UUIDs** | 550e8400-e29b-41d4-a716-446655440000 | `<GUID>` | ✅ |

---

## How It Works

### 1. Processing Pipeline

```
RAW S3 Bucket → Batch Processor → REDACTED S3 Bucket
    ↓
Read NDJSON files
    ↓
Extract text from "prompt.messages[].content[].text" and "response.choices[].content"
    ↓
Apply regex patterns to detect PII
    ↓
Replace PII with placeholder tags (e.g., <PERSON>, <PHONE>)
    ↓
Write to REDACTED bucket with renamed fields (prompt_redacted / response_redacted)
```

### 2. Fields Processed

**Text fields redacted (default):**
- `prompt.messages[].content[].text` → renamed to `prompt_redacted.messages[].content[].text`
- `response.choices[].content` → renamed to `response_redacted.choices[].content`

**Fields NOT redacted (preserved):**
- `user_id` (api-key alias) - preserved for analytics
- `request_id` (UUID) - preserved for request tracking
- `event_id` - preserved for correlation
- `event_time` - timestamp preserved
- `source`, `stream`, `kind`, `truncated` - metadata preserved
- `model` - model name preserved
- `response_redacted.usage` - token counts (`prompt_tokens`, `completion_tokens`, `total_tokens`) preserved

**Fields dropped in redacted logs:**
- `platform_model_id` - raw only
- `prompt.tools` / `tool_choice` and `response.choices[].tool_calls` - raw only
- `usage.latency_ms` - raw only

See [examples/interaction_redacted_event_schema.json](examples/interaction_redacted_event_schema.json) for the authoritative redacted schema.

---

## Redaction Examples

### Example 1: Person Names

**Original:**
```
"Can John Smith help me with the project?"
```

**Redacted:**
```
"Can <PERSON> help me with the project?"
```

### Example 2: Multiple PII Types

**Original:**
```
"Contact Jane Doe at jane.doe@company.com or call 555-123-4567"
```

**Redacted:**
```
"Contact <PERSON> at <EMAIL> or call <PHONE>"
```

### Example 3: Structured Data

**Original:**
```
"My SSN is 123-45-6789 and I live at 456 Oak Street, ZIP 90210"
```

**Redacted:**
```
"My SSN is <SSN> and I live at <ADDRESS>, ZIP <ZIP_CODE>"
```

### Example 4: Technical Data

**Original:**
```
"Server IP 192.168.1.100, MAC 00:1B:44:11:3A:B7, accessed from https://internal.example.com"
```

**Redacted:**
```
"Server IP <IP_ADDRESS>, MAC <MAC_ADDRESS>, accessed from <URL>"
```

---

## Detection Accuracy

### Strengths

✅ **High precision for structured data:**
- SSNs, credit cards, phone numbers (formatted patterns)
- Email addresses (standard formats)
- ZIP codes, routing numbers
- IP addresses, MAC addresses

✅ **Preserves text structure:**
- Replacement tags maintain word boundaries
- Sentence structure preserved
- Length information tracked

### Limitations

⚠️ **Person name detection:**
- Uses capitalization patterns (e.g., "John Smith")
- May miss: all lowercase names, single names, nicknames
- May flag: proper nouns that aren't names (brands, places)

⚠️ **Context-dependent patterns:**
- "123 Main Street" detected as address
- "123" alone not detected
- Requires context clues in pattern

⚠️ **High false positive rate (intentional):**
- GUIDs might flag legitimate IDs
- Dates might flag version numbers (1/2/2024 vs v1.2.2024)
- Bank account numbers might flag other long number sequences
- Person name pattern may flag proper nouns (brands, places)
- **This is acceptable** - better to over-redact than risk missing PII

⚠️ **No semantic understanding:**
- Regex doesn't understand context
- Can't detect PII described indirectly ("my mother's maiden name is...")
- Can't handle obfuscated PII ("john dot smith at company dot com")

---

## Processing Schedule

**When:** Batch process (specific schedule TBD)
**Trigger:** Can be run for specific dates or date ranges
**Latency:** Not real-time (batch processing after RAW logs written)

**Command format:**
```python
redact_pii_s3_to_s3(
    date_string="2026-02-02",
    source_bucket="usai-{tenant}-production-interaction-raw",
    dest_bucket="usai-{tenant}-production-interaction-redacted",
    text_fields=["prompt", "response"],
    pii_models=["regex"]
)
```

---

## Why Placeholder Tags Instead of Removal?

**Using tags like `<PERSON>` instead of complete removal:**

✅ **Preserves structure:**
- Sentence structure intact
- Word count approximation possible
- Conversation flow understandable

✅ **Enables analysis:**
- Can count how much PII was in text
- Can see where PII appeared
- Can analyze patterns

✅ **Debugging:**
- Can verify redaction worked
- Can identify missed PII (human review)

**Example:**
```
Original: "John called Mary about the report"
With tags: "<PERSON> called <PERSON> about the report"
Removed:   "called about the report"  ← Less useful
```

---

## Can Redaction Be Reversed?

**No.** The original PII is not stored or encrypted - it's replaced.

❌ Cannot recover original names from `<PERSON>` tags
❌ Cannot recover original emails from `<EMAIL>` tags
❌ Process is one-way (lossy)

**However:**
- RAW logs still contain original data
- Redaction doesn't modify RAW bucket
- Both buckets coexist

---

## Security Considerations

### What's Protected

✅ **REDACTED bucket is safer because:**
- Most PII removed via pattern matching
- Multiple PII types detected (19 types)
- Lower risk if credentials compromised
- Suitable for broader distribution

### What's NOT Protected

⚠️ **Not foolproof:**
- Regex can miss PII (false negatives)
- User IDs (UUIDs) still present
- Timestamps still present
- Context from surrounding text might reveal identity

⚠️ **Still treat as sensitive:**
- Not public data
- Requires access controls
- User IDs can be correlated
- Conversation patterns might be identifying

---

## Alternative Approaches Considered

### Tested But Not Deployed

**1. StarPII (Open Source NER)**
- Named Entity Recognition model for PII detection
- Better accuracy for names and context
- Not deployed: Added complexity, model dependencies

**2. Presidio (Microsoft)**
- Comprehensive PII detection framework
- Supports multiple detection methods
- Not deployed: Heavier framework, harder to maintain

**Decision:** Regex's simplicity and acceptable false positive rate (over-redaction) made it suitable for deployment. Security benefit of over-redaction outweighs occasional non-PII being masked.

### Future Enhancements Could Include

1. **Hybrid approach:** Regex + ML models for lower false positive rate
2. **StarPII integration:** Better name detection with less over-redaction
3. **Presidio adoption:** More comprehensive framework if needed
4. **Custom patterns:** Tenant-specific PII types
5. **Confidence scores:** Tag PII with detection confidence
6. **Multi-language support:** Non-English PII detection

**Note:** Current regex approach is intentionally conservative (over-redacts) for maximum PII protection.

---

## Configuration Options

### Configurable Parameters

**Text fields:** Which fields to redact (default: `["prompt", "response"]`)
**PII models:** Which detection methods (default: `["regex"]`)
**Date range:** Which dates to process

### Not Currently Configurable

- Which PII types to detect (all or nothing)
- Custom patterns (requires code change)
- Replacement tags (hardcoded)

---

## Verification

### How to Verify Redaction Worked

1. **Compare file sizes:** REDACTED files are smaller
2. **Check for tags:** Look for `<PERSON>`, `<EMAIL>`, etc.
3. **Check length fields:** `prompt_original_length` vs `prompt_redacted_length`
4. **Manual review:** Sample files for missed PII

### Reporting Issues

If you find PII that should have been redacted:
1. Note the pattern
2. Report to USAI application team
3. Don't share the actual PII in the report
4. Pattern can be added to regex list

---

## Summary

**Q: How is PII determined?**
**A:** Using 19 regex patterns that detect common PII types (names, emails, SSNs, etc.)

**Q: What's redacted?**
**A:** Text in `prompt` and `response` fields only. Metadata (user IDs, timestamps, metrics) preserved.

**Q: How accurate is it?**
**A:** Very accurate for structured data (SSN, emails). Has **high false positive rate** (intentionally over-redacts) - some non-PII may be masked, but this ensures maximum PII protection.

**Q: Why not use more accurate methods like ML models?**
**A:** We tested StarPII (NER) and Presidio (Microsoft), but chose regex for simplicity and maintainability. Over-redacting is safer than risking missed PII.

**Q: Will some non-PII content be redacted?**
**A:** Yes, that's intentional. Better to mask extra content than miss actual PII. Examples: brand names matching person name patterns, legitimate numbers matching SSN patterns.

**Q: Can we customize it?**
**A:** Not currently, but patterns can be added if needed.

**Q: Is REDACTED completely safe?**
**A:** Safer than RAW, but still treat as sensitive data. User IDs and context remain. The conservative approach ensures PII protection.

---

## References

**Code Location:** `console-data/utils/redact_pii.py`
**Repository:** https://github.com/GSA-TTS/usai-console-data
**Lines:** 12-94 (PII_PATTERNS definitions)
**Lines:** 516-552 (redaction logic)

---

## Questions?

**Application Team:** For questions about detection patterns or adding new PII types
**Infrastructure Team:** For questions about processing schedule or bucket access
**Security Team:** For questions about risk assessment or compliance

---

**Document Status:** ✅ Complete
**Based On:** Actual code implementation
**Tenant Questions:** ✅ Answered

---

**Last Updated:** 2026-02-02
**Reviewed By:** Infrastructure Team
**Code Version:** Current (main branch)
