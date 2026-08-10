# USAi Interaction and Security Log Access

**Get up and running in 10 minutes**

---

## What You're Getting

As a USAi tenant, you receive dedicated AWS resources for interaction and security log access:

**3 SQS Queues** (one per log type):
- `interaction-raw` - Unredacted logs with PII
- `interaction-redacted` - PII-redacted logs
- `sec-auditlogs` - Security and audit events

**3 S3 Buckets** (matching log types):
- Raw logs bucket
- Redacted logs bucket
- Audit logs bucket

**IAM Credentials**:
- Access Key ID
- Secret Access Key
- Read-only permissions (SQS + S3)

---

## Before You Begin

You'll need:
- Your AWS credentials (Access Key ID and Secret Access Key)
- Your tenant configuration values (provided by USAI)

```bash
# AWS Configuration
AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
AWS_REGION="YOUR_REGION"          # Usually us-east-1
TENANT_CODE="YOUR_TENANT_CODE"     # Example: ed, hhs, gsa

# Queue URLs
QUEUE_URL="YOUR_SQS_QUEUE_URL"
DLQ_URL="YOUR_DLQ_URL"

# S3 Bucket
BUCKET_NAME="YOUR_S3_BUCKET_NAME"
```

**Don't have these?** Contact [usai-security@gsa.gov](mailto:usai-security@gsa.gov). 

---

## Setup (5 minutes)

### Step 1: Install AWS CLI

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Verify
aws --version
```

### Step 2: Configure Credentials

```bash
# Use your tenant code as profile name
aws configure --profile ${TENANT_CODE}-logs

# When prompted, enter:
# - AWS Access Key ID: [from infrastructure team]
# - AWS Secret Access Key: [from infrastructure team]
# - Default region name: [your AWS_REGION]
# - Default output format: json
```

### Step 3: Quick Tests

```bash
# Set profile
export AWS_PROFILE=${TENANT_CODE}-logs

# Test 1: Verify identity
aws sts get-caller-identity

# Test 2: Poll queue
aws sqs receive-message \
  --queue-url ${QUEUE_URL} \
  --max-number-of-messages 1 \
  --wait-time-seconds 5 \
  --region ${AWS_REGION}

# Test 3: List S3 files
aws s3 ls s3://${BUCKET_NAME}/ --region ${AWS_REGION}
```

**All three commands work?** You're ready!

---

## Download Logs (Manual)

```bash
# 1. Poll queue for notifications
aws sqs receive-message \
  --queue-url ${QUEUE_URL} \
  --max-number-of-messages 10 \
  --wait-time-seconds 20 \
  --region ${AWS_REGION} > messages.json

# 2. Extract S3 key
cat messages.json | jq -r '.Messages[0].Body | fromjson | .Message | fromjson | .Records[0].s3.object.key'

# 3. Download file (replace KEY with output from step 2)
aws s3 cp s3://${BUCKET_NAME}/[KEY] ./log.json --region ${AWS_REGION}

# 4. View contents
head -5 log.json | jq .
```

---

## Log Format

**Format:** NDJSON (one JSON object per line)

Each line is a `chat_completion` event. There are two shapes depending on which
bucket you read from: **redacted** (`prompt_redacted` / `response_redacted`) and
**raw** (`prompt` / `response`, plus `platform_model_id` and tool data). See the
canonical schemas and examples in [`examples/`](./examples/).

> **⚠️ Upcoming change:** the RAW stream is moving to a **context-history split** —
> streamed events will carry metadata plus a `context_history_s3_key` pointer, and
> conversation content will live in a separate S3 object. `prompt`, `response`, and
> `truncated` disappear from the streamed event, `usage` moves to the top level, and
> `usage.latency_ms` may be `null`. If you are building a consumer now, read
> [Upcoming change: context-history split](./raw-vs-redacted-logs.md#upcoming-change-context-history-split)
> and follow the migration checklist there.

**Example Event (redacted):**
```json
{
  "event_id": "6e111d4e-928a-40fa-8bd9-8448637e9a6a",
  "event_time": "2026-04-28T06:01:22.670432+00:00",
  "source": "api",
  "stream": false,
  "kind": "chat_completion",
  "user_id": "api-key-abcd",
  "request_id": "a29e5dc8-a5ff-426e-b127-3b3e7716b09c",
  "model": "gemini-2.5-pro",
  "truncated": false,
  "prompt_redacted": {
    "messages": [
      { "role": "user", "content": [ { "type": "text", "text": "... contact <PHONE> ..." } ] }
    ],
    "temperature": 0.0
  },
  "response_redacted": {
    "choices": [ { "content": "...", "finish_reason": "stop" } ],
    "usage": { "prompt_tokens": 9848, "completion_tokens": 206, "total_tokens": 11855 }
  }
}
```

**Field notes:**
- Token counts live under `usage`: `prompt_tokens`, `completion_tokens`, `total_tokens`.
- `latency_ms` is present in `response.usage` on **raw** events only.
- Message text is a list of typed parts (`content[].text`), not a plain string.
- **Raw** events add `platform_model_id`, `prompt.tools` / `tool_choice`, and `response.choices[].tool_calls`.
- `source` is `"api"` for direct API traffic and `"chat"` for USAi Chat traffic.
  Chat events carry a `conversation_id` and a UUID `user_id`; API events use an
  api-key alias such as `api-key-<uuid>` or `local-api`.
- **After the context-history split** (raw stream): `usage` moves to the top level,
  `usage.latency_ms` may be `null`, `truncated` is removed, and `status` plus
  `context_history_s3_key` are added. Content is fetched separately from
  `context_history_s3_key`.

**Common Operations:**
```bash
# View first 5 events
head -5 log.json | jq .

# Count events
wc -l log.json

# Extract key fields (redacted)
cat log.json | jq '{event_id, model, usage: .response_redacted.usage}'

# Extract key fields (raw)
cat log.json | jq '{event_id, model, platform_model_id, usage: .response.usage}'

# Extract key fields (raw, after the context-history split)
cat log.json | jq '{event_id, model, platform_model_id, status, usage, context_history_s3_key}'

# Count by model
cat log.json | jq -r '.model' | sort | uniq -c

# Sum total tokens (redacted)
cat log.json | jq '.response_redacted.usage.total_tokens' | paste -sd+ - | bc

# Sum total tokens (raw, after the context-history split)
cat log.json | jq '.usage.total_tokens' | paste -sd+ - | bc

# Fetch the conversation content for one event (after the split)
KEY=$(head -1 log.json | jq -r '.context_history_s3_key')
aws s3 cp s3://${BUCKET_NAME}/${KEY} - --region ${AWS_REGION} | jq .
```

---

## Common Issues

### "Access Denied"
```bash
# Check profile is set
echo $AWS_PROFILE  # Should be: ${TENANT_CODE}-logs

# Verify credentials
aws sts get-caller-identity
```

### Queue is Empty
This is normal! Logs are batched every ~5 minutes. Check S3 directly:
```bash
aws s3 ls s3://${BUCKET_NAME}/$(date +%Y/%m/%d)/ --region ${AWS_REGION}
```

### DLQ Alert
Dead Letter Queue should be empty. If you receive an alert, see the [DLQ Investigation Guide](./dlq-investigation.md).

---

## Quick Checklist

- [ ] AWS CLI installed
- [ ] Credentials configured
- [ ] Identity verified (Test 1)
- [ ] Queue accessible (Test 2)
- [ ] S3 accessible (Test 3)
- [ ] Downloaded first log file
- [ ] Reviewed log format
- [ ] Set 90-day key rotation reminder

---

## Further Reading

| Topic | Document |
|-------|----------|
| Complete setup reference | [Log Access Guide](./log-access-guide.md) |
| Raw vs redacted logs | [Raw vs Redacted](./raw-vs-redacted-logs.md) |
| PII redaction methodology | [PII Redaction Complete](./PII_REDACTION_COMPLETE.md) |
| Credential management | [Security Best Practices](./security-best-practices.md) |
| DLQ troubleshooting | [DLQ Investigation](./dlq-investigation.md) |
| System architecture | [Architecture](./architecture.md) |

---

## Support

| Issue Type | Contact |
|------------|---------|
| **Access/Credentials/IAM** | [usai-security@gsa.gov](mailto:usai-security@gsa.gov) |
| **Log Content/Format** | [usai-security@gsa.gov](mailto:usai-security@gsa.gov)|
| **Security Incident** | [usai-security@gsa.gov](mailto:usai-security@gsa.gov) |

---

**Last Updated:** 2026-02-17
