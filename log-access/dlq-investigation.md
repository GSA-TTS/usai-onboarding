# Dead Letter Queue (DLQ) Investigation Guide

**When to use this guide:** You received a CloudWatch alarm indicating messages in your DLQ

---

## What is a DLQ?

A Dead Letter Queue captures messages that failed to process after multiple retries (typically 3 attempts). Messages in the DLQ indicate a problem that needs investigation.

**DLQs are required for:**
- Splunk integration compliance
- Data quality assurance
- Debugging processing failures

---

## Before You Begin

You'll need:
- Your DLQ URL (from your tenant configuration)
- Your main queue URL
- AWS CLI configured with your tenant profile

**Example:**
```bash
DLQ_URL="your-dlq-url"
QUEUE_URL="your-main-queue-url"
AWS_REGION="us-east-1"
TENANT_PROFILE="your-tenant-logs"
```

---

## Quick Check

### Step 1: Confirm DLQ Has Messages

```bash
aws sqs get-queue-attributes \
  --queue-url ${DLQ_URL} \
  --attribute-names ApproximateNumberOfMessages ApproximateAgeOfOldestMessage \
  --region ${AWS_REGION}
```

**Expected Output:**
```json
{
  "Attributes": {
    "ApproximateNumberOfMessages": "5",
    "ApproximateAgeOfOldestMessage": "3600"
  }
}
```

- **0 messages:** False alarm or messages already processed
- **>0 messages:** Continue investigation

---

## Investigation Steps

### Step 2: Retrieve Sample Messages

```bash
# Get up to 10 messages (doesn't delete them)
aws sqs receive-message \
  --queue-url ${DLQ_URL} \
  --max-number-of-messages 10 \
  --message-attribute-names All \
  --attribute-names All \
  --region ${AWS_REGION} > dlq-messages.json

# View message count
cat dlq-messages.json | jq '.Messages | length'

# View first message
cat dlq-messages.json | jq '.Messages[0]'
```

### Step 3: Analyze Message Pattern

```bash
# Extract all message bodies
cat dlq-messages.json | jq '.Messages[].Body' > bodies.txt

# Check for common errors
cat bodies.txt | jq '.errorMessage' 2>/dev/null || echo "No error messages in body"

# Check message attributes
cat dlq-messages.json | jq '.Messages[].MessageAttributes'

# Check when first received
cat dlq-messages.json | jq '.Messages[].Attributes.ApproximateFirstReceiveTimestamp'
```

---

## Common Failure Causes

### 1. Malformed JSON

**Symptoms:**
- Message body is not valid JSON
- Missing required fields

**Example:**
```json
{"event_id": "123", "incomplete
```

**Solution:**
- Contact development team to fix message producer
- May indicate application bug

---

### 2. Downstream System Unavailable

**Symptoms:**
- Timeout errors
- Connection refused
- Multiple messages failing around same time

**Common Culprits:**
- Splunk ingestion service down
- S3 temporarily unavailable
- Network connectivity issues

**Solution:**
1. Check downstream system status
2. Wait for system to recover
3. Redrive messages (see below)

---

### 3. Permission Errors

**Symptoms:**
- "AccessDenied" in error logs
- 403 errors

**Solution:**
- Verify IAM permissions for consumer
- Contact infrastructure team

---

### 4. Message Too Large

**Symptoms:**
- Message exceeds 256KB
- Large conversation history

**Solution:**
- Contact development team to implement message chunking
- May require application changes

---

### 5. Processing Logic Bug

**Symptoms:**
- Specific message types always fail
- Error in consumer code

**Solution:**
- Review consumer application logs
- Deploy fix
- Redrive messages after fix

---

## Resolution Steps

### After Identifying Root Cause

**1. Fix the Issue**
- Deploy application fix, or
- Wait for downstream system recovery, or
- Correct IAM permissions

**2. Redrive Messages**

Move messages from DLQ back to main queue:

```bash
# Get ARNs from queue URLs
DLQ_ARN=$(aws sqs get-queue-attributes --queue-url ${DLQ_URL} --attribute-names QueueArn --region ${AWS_REGION} --query 'Attributes.QueueArn' --output text)
QUEUE_ARN=$(aws sqs get-queue-attributes --queue-url ${QUEUE_URL} --attribute-names QueueArn --region ${AWS_REGION} --query 'Attributes.QueueArn' --output text)

# Start redrive task
aws sqs start-message-move-task \
  --source-arn ${DLQ_ARN} \
  --destination-arn ${QUEUE_ARN} \
  --region ${AWS_REGION}
```

**Expected Output:**
```json
{
  "TaskHandle": "abc123..."
}
```

**3. Monitor Redrive Progress**

```bash
# Check task status
aws sqs list-message-move-tasks \
  --source-arn ${DLQ_ARN} \
  --region ${AWS_REGION}

# Watch DLQ drain
watch -n 5 "aws sqs get-queue-attributes \
  --queue-url ${DLQ_URL} \
  --attribute-names ApproximateNumberOfMessages \
  --region ${AWS_REGION}"
```

**4. Verify Processing**

```bash
# Check main queue is processing
aws sqs get-queue-attributes \
  --queue-url ${QUEUE_URL} \
  --attribute-names ApproximateNumberOfMessages \
  --region ${AWS_REGION}

# Review consumer logs for successful processing
# (specific command depends on your consumer deployment)
```

---

## When Messages Return to DLQ

If messages move back to DLQ after redrive:

**Indicates:** Root cause not fully resolved

**Actions:**
1. Review error logs again
2. Check if fix was properly deployed
3. Verify downstream systems are healthy
4. Contact USAI infrastructure team for assistance

---

## Preventing Future DLQ Messages

### Best Practices

**1. Monitor Consumer Health**
- Set up alerts for consumer errors
- Monitor processing latency
- Track success/failure rates

**2. Implement Retry Logic**
- Exponential backoff for transient failures
- Circuit breakers for downstream systems
- Graceful degradation

**3. Validate Messages**
- Schema validation before processing
- Handle missing fields gracefully
- Log validation errors

**4. Regular Audits**
- Weekly DLQ checks (even when empty)
- Review failure patterns
- Update monitoring as needed

---

## DLQ Retention

**Main Queue:** 4 days
**DLQ:** 14 days

Messages in DLQ are deleted after 14 days. Investigate promptly to avoid data loss.

---

## Multiple Queue Types

Most tenants have multiple queue types, each with its own DLQ:

| Queue Type | Purpose |
|------------|---------|
| **Raw Logs** | Unredacted interaction logs (internal use) |
| **Redacted Logs** | PII-redacted logs (Splunk, partners) |
| **Security Audit** | Authentication and authorization events |

**Each DLQ should be monitored independently.**

Check your tenant configuration for specific queue URLs.

---

## When to Escalate

Contact USAI Infrastructure Team if:

- ❌ Can't determine failure cause
- ❌ Messages keep returning to DLQ after redrive
- ❌ Suspected system-wide issue
- ❌ Large number of messages (>100) in DLQ
- ❌ Critical data in DLQ approaching 14-day retention limit

---

## Incident Documentation

After resolution, document:

1. **Root Cause:** What caused messages to fail?
2. **Impact:** How many messages? What time period?
3. **Resolution:** What was done to fix?
4. **Prevention:** How to prevent recurrence?

Keep incident log for compliance and future reference.

---

## Related Documentation

- [Quick Start Guide](../QUICK_START.md) - Getting started with log access
- [Security Best Practices](../admin-guides/security-best-practices.md) - Credential management
- [Architecture Overview](../architecture/log-notification-architecture.md) - How the system works
- [Complete Queue Inventory](../../docs/SQS_QUEUE_INVENTORY.md) - Platform reference

---

**Need Help?** Contact USAI Infrastructure Team

**Last Updated:** 2026-02-17
