# Log Notification Architecture

**Last Updated:** 2026-01-28

## Overview

USAI uses AWS Kinesis Firehose to deliver analytics logs to S3 buckets. When new log files are created, notifications are sent via Amazon SNS to Amazon SQS queues, where tenant administrators can poll for updates.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Application Layer (Python/FastAPI)                             │
│                                                                  │
│  ┌─────────────┐        ┌──────────────┐                       │
│  │   Chat API  │        │  Analytics   │                       │
│  │   Events    │───────▶│  Event       │                       │
│  │             │        │  Writer      │                       │
│  └─────────────┘        └──────────────┘                       │
│                               │                                 │
│                               │ Batch: 400 events or 3.5 MiB   │
│                               ▼                                 │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│  AWS Analytics Pipeline (Per Tenant)                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  AWS Kinesis Firehose                                      │ │
│  │                                                            │ │
│  │  • Buffer: 5 MB or 5 minutes                             │ │
│  │  • Compression: Uncompressed (NDJSON)                    │ │
│  │  • Destination: S3 bucket                                │ │
│  └─────────────────────┬──────────────────────────────────────┘ │
│                        │                                         │
│                        │ Writes files                            │
│                        ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Amazon S3 Bucket                                          │ │
│  │                                                            │ │
│  │  • Name: usai-{tenant}-core-production-interaction-raw    │ │
│  │  • Encryption: AES256 or KMS                              │ │
│  │  • Structure: YYYY/MM/DD/HH-MM-SS-uuid.json               │ │
│  │  • Format: NDJSON (one JSON object per line)             │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────┐        │ │
│  │  │  S3 Event Notifications                       │        │ │
│  │  │  • Trigger: ObjectCreated:*                   │        │ │
│  │  │  • Filter: *.json files                       │        │ │
│  │  └──────────────────┬───────────────────────────┘        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                        │                                         │
│                        │ Publishes notification                  │
│                        ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Amazon SNS Topic                                          │ │
│  │                                                            │ │
│  │  • Name: usai-{tenant}-core-production-interaction-...    │ │
│  │  • Encryption: KMS (optional)                             │ │
│  │  • Message: S3 event with bucket and key                  │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────┐        │ │
│  │  │  Topic Policy                                 │        │ │
│  │  │  • Allow S3 to publish                        │        │ │
│  │  │  • Allow SQS subscriptions                    │        │ │
│  │  └──────────────────────────────────────────────┘        │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
│                         │                                        │
│                         │ Fan-out to subscribers                 │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Amazon SQS Queue                                          │ │
│  │                                                            │ │
│  │  • Name: usai-{tenant}-core-production-interaction-...    │ │
│  │  • Encryption: KMS (optional)                             │ │
│  │  • Retention: 4 days (default)                            │ │
│  │  • Visibility timeout: 5 minutes                          │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────┐        │ │
│  │  │  Queue Policy                                 │        │ │
│  │  │  • Allow SNS to send messages                 │        │ │
│  │  └──────────────────────────────────────────────┘        │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
│                         │                                        │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          │ Long polling
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  Tenant Administrators                                           │
│                                                                  │
│  ┌────────────────┐           ┌────────────────┐               │
│  │  AWS CLI       │           │  Python        │               │
│  │  • Poll SQS    │           │  Consumer      │               │
│  │  • Download S3 │           │  Script        │               │
│  └────────────────┘           └────────────────┘               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  IAM Role: usai-{tenant}-log-reader                      │  │
│  │                                                           │  │
│  │  • SQS: ReceiveMessage, DeleteMessage                    │  │
│  │  • S3: GetObject, ListBucket                             │  │
│  │  • KMS: Decrypt (if encrypted)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Application Layer

**Event Generation:**
- FastAPI application generates analytics events
- Events batched by Event Writer (400 events or 3.5 MiB max)
- Sent to Kinesis Firehose via AWS SDK

**Event Types:**
- Chat interactions
- API calls
- Model usage
- User actions

### 2. AWS Kinesis Firehose

**Purpose:** Reliable delivery of analytics events to S3

**Configuration:**
- Buffer size: 5 MB
- Buffer interval: 300 seconds (5 minutes)
- Compression: Uncompressed (NDJSON format)
- Error handling: Failed events sent to error bucket (if configured)

**Per-Tenant Isolation:**
- Each tenant has their own Firehose delivery stream
- Naming: `usai-{tenant}-core-production-firehose`

### 3. Amazon S3 Bucket

**Purpose:** Long-term storage of analytics logs

**Structure:**
```
s3://usai-{tenant}-core-production-interaction-raw/
└── {YEAR}/
    └── {MONTH}/
        └── {DAY}/
            └── {TIMESTAMP}-{UUID}.json
```

**Example:**
```
s3://usai-example-core-production-interaction-raw/
└── 2026/
    └── 01/
        └── 28/
            ├── 10-30-00-abc123def456.json
            ├── 10-35-00-xyz789ghi012.json
            └── 10-40-00-mno345pqr678.json
```

**File Format:**
- NDJSON (Newline Delimited JSON)
- One JSON object per line
- Optionally gzip-compressed

**Security:**
- Encryption at rest (AES256 or KMS)
- Bucket policy with IP restrictions
- Versioning enabled (optional)
- Lifecycle policies for archival

### 4. S3 Event Notifications

**Purpose:** Trigger notifications when new files are created

**Configuration:**
- Event type: `s3:ObjectCreated:*`
- Filter: `*.json` files (or no filter)
- Destination: SNS topic

**How it Works:**
1. Firehose writes file to S3
2. S3 generates ObjectCreated event
3. S3 publishes event to SNS topic

### 5. Amazon SNS Topic

**Purpose:** Fan-out notifications to multiple subscribers

**Configuration:**
- Naming: `usai-{tenant}-core-production-interaction-raw-topic`
- Encryption: KMS (optional)
- Delivery policy: Retry with exponential backoff

**Message Format:**
```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "eventName": "ObjectCreated:Put",
      "s3": {
        "bucket": {
          "name": "usai-example-core-production-interaction-raw"
        },
        "object": {
          "key": "2026/01/28/10-30-00-abc123.json",
          "size": 12345
        }
      }
    }
  ]
}
```

**Subscribers:**
- Internal SQS queue (for monitoring)
- Additional queues can be added as needed

### 6. Amazon SQS Queue

**Purpose:** Queue notifications for tenant administrators to poll

**Configuration:**
- Naming: `usai-{tenant}-core-production-interaction-raw-queue`
- Encryption: KMS (optional)
- Message retention: 4 days (default)
- Visibility timeout: 5 minutes
- Receive wait time: 20 seconds (long polling)

**Dead Letter Queue (DLQ):**
- **Required** for Splunk integration and compliance
- Retention: 14 days (longer than main queue)
- Max receive count: 3-5 retries before moving to DLQ
- Naming pattern: `{queue-name}-dlq`

**Production DLQ Examples:**
```
# Raw interaction logs DLQ
usai-${TENANT_CODE}-core-production-interaction-raw-dlq

# Redacted interaction logs DLQ (PII removed)
usai-${TENANT_CODE}-core-production-interaction-redacted-dlq

# Security audit logs DLQ
usai-${TENANT_CODE}-core-production-sec-auditlogs-dlq
```

**Why DLQs are Required:**
- **Data Quality**: Identifies malformed messages that fail processing
- **Compliance**: Proves no data loss (Splunk requirement)
- **Debugging**: Preserves failed messages for investigation
- **Monitoring**: Alerts when processing failures occur

### 7. IAM Role (Tenant Access)

**Purpose:** Provide secure access for tenant administrators

**Permissions:**
- **SQS:** `ReceiveMessage`, `DeleteMessage`, `GetQueueAttributes`, `GetQueueUrl`, `ChangeMessageVisibility`
- **S3:** `GetObject`, `GetObjectVersion`, `ListBucket`, `GetBucketLocation`
- **KMS:** `Decrypt` (if encrypted)

**Trust Policy:**
- Allows tenant's SSO admin roles to assume
- Optional: IP restrictions, MFA requirement

## Data Flow

### 1. Event Generation

```python
# Application code
from analytics import EventWriter

writer = EventWriter(sink="firehose")
writer.write_event({
    "event_id": "evt_123",
    "event_time": "2026-01-28T10:30:00Z",
    "event_type": "chat_message",
    "user_id": "user_456",
    "model": "claude-sonnet-4",
    "tokens_used": 150
})
```

### 2. Batch and Deliver

```
EventWriter → Batch (400 events) → Firehose → S3 (every 5 min)
```

### 3. Notification Flow

```
S3 → S3 Event → SNS → SQS → Admin Poll
```

### 4. Admin Access

```python
# Admin consumer script
import boto3

sqs = boto3.client('sqs')
s3 = boto3.client('s3')

# Poll queue
response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=20)

for message in response['Messages']:
    # Parse S3 event
    event = json.loads(message['Body'])
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Download file
    s3.download_file(bucket, key, f'./logs/{key}')

    # Delete message
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
```

## Security Model

### Tenant Isolation

Each tenant has:
- Separate AWS account
- Separate S3 bucket
- Separate SNS topic
- Separate SQS queue
- No cross-tenant access

### Defense in Depth

**Layer 1: IAM**
- Role-based access control
- Least privilege permissions
- Temporary credentials via AssumeRole

**Layer 2: Encryption**
- Encryption at rest (S3, SQS)
- Encryption in transit (TLS)
- KMS for key management

**Layer 3: Network**
- IP allowlists on S3 bucket policy
- VPC endpoints (optional)

**Layer 4: Audit**
- CloudTrail logging of all access
- S3 access logs
- SQS message attributes

## Performance Characteristics

### Latency

| Stage | Typical Latency |
|-------|-----------------|
| Event generation | < 1 ms |
| Event batching | 0-5 minutes |
| Firehose delivery | 0-5 minutes |
| S3 notification | < 1 second |
| SNS delivery | < 1 second |
| SQS availability | Immediate |

**Total:** 0-10 minutes from event generation to admin notification

### Throughput

| Metric | Capacity |
|--------|----------|
| Events/second | 1000+ |
| Firehose throughput | 5 MB/second per stream |
| SNS throughput | Unlimited |
| SQS throughput | Unlimited (standard queue) |

### Scalability

- **Horizontal:** Each tenant scales independently
- **Vertical:** Firehose auto-scales based on load
- **Storage:** S3 unlimited capacity

## Cost Model

### Monthly Cost (Example: 100K events/day)

| Service | Usage | Cost |
|---------|-------|------|
| Firehose | 10 GB/month | $0.34 |
| S3 Storage | 10 GB | $0.23 |
| S3 Requests | 100K PUT, 50K GET | $0.52 |
| SNS Messages | 3M/month | $1.50 |
| SQS Messages | 3M/month | $1.20 |
| KMS | 300K requests | $0.90 |
| **Total** | | **$4.69/month** |

### Cost Optimization

- Use S3 lifecycle policies for archival
- Batch events to reduce Firehose costs
- Use long polling on SQS to reduce empty receives
- Compress log files before storage

## Monitoring and Operations

### Key Metrics

**Firehose:**
- `IncomingBytes`
- `IncomingRecords`
- `DeliveryToS3.Success`
- `DeliveryToS3.DataFreshness`

**S3:**
- `NumberOfObjects`
- `BucketSizeBytes`
- `4xxErrors`
- `5xxErrors`

**SNS:**
- `NumberOfMessagesPublished`
- `NumberOfNotificationsFailed`
- `NumberOfNotificationsDelivered`

**SQS:**
- `ApproximateNumberOfMessagesVisible`
- `ApproximateAgeOfOldestMessage`
- `NumberOfMessagesReceived`
- `NumberOfMessagesDeleted`

### Alerts

**Critical:**
- Firehose delivery failures > 5%
- S3 upload errors > 1%
- SNS delivery failures > 1%

**Warning:**
- SQS queue depth > 100 messages
- Oldest message age > 1 hour
- Firehose data freshness > 10 minutes

### Dead Letter Queue Monitoring

**Metrics to Monitor:**
- `ApproximateNumberOfMessagesVisible` (should be 0)
- `ApproximateAgeOfOldestMessage` (age of stuck messages)
- `NumberOfMessagesReceived` (rate of failures)

**Automated Alerts:**
```bash
# CloudWatch alarm for any DLQ messages
aws cloudwatch put-metric-alarm \
  --alarm-name usai-${TENANT_CODE}-dlq-interaction-raw \
  --alarm-description "Messages in interaction-raw DLQ" \
  --metric-name ApproximateNumberOfMessagesVisible \
  --namespace AWS/SQS \
  --statistic Average \
  --period 60 \
  --threshold 0 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=QueueName,Value=usai-${TENANT_CODE}-core-production-interaction-raw-dlq \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:us-east-1:${AWS_ACCOUNT_ID}:ops-alerts
```

**Manual Investigation:**
```bash
# Check DLQ depth
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/${AWS_ACCOUNT_ID}/usai-${TENANT_CODE}-core-production-interaction-raw-dlq \
  --attribute-names ApproximateNumberOfMessages

# View failed messages
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/${AWS_ACCOUNT_ID}/usai-${TENANT_CODE}-core-production-interaction-raw-dlq \
  --max-number-of-messages 10

# Redrive messages back to main queue (after fixing issue)
aws sqs start-message-move-task \
  --source-arn arn:aws:sqs:us-east-1:${AWS_ACCOUNT_ID}:usai-${TENANT_CODE}-core-production-interaction-raw-dlq \
  --destination-arn arn:aws:sqs:us-east-1:${AWS_ACCOUNT_ID}:usai-${TENANT_CODE}-core-production-interaction-raw
```

**Common DLQ Failure Patterns:**
1. **Malformed JSON**: Message body not valid JSON
2. **Missing required fields**: Consumer expects fields not in message
3. **Downstream service unavailable**: Splunk or S3 temporarily down
4. **Permission errors**: IAM role lacks required permissions
5. **Message too large**: Exceeds SQS 256KB limit

## High Availability

### Multi-AZ

All AWS services are multi-AZ by default:
- S3: 99.99% availability
- SNS: 99.9% availability
- SQS: 99.9% availability
- Firehose: 99.9% availability

### Disaster Recovery

**Backup:**
- S3 versioning enabled
- Cross-region replication (optional)

**Recovery:**
- S3 objects are immutable
- Failed deliveries retry automatically
- SQS messages retained for 4 days

## Compliance

### Data Retention

- **SQS messages:** 4 days (configurable up to 14 days)
- **S3 logs:** Indefinite (or per lifecycle policy)
- **CloudTrail logs:** 90 days (or custom)

### Audit Requirements

- CloudTrail logs all API calls
- S3 access logs available
- IAM role usage tracked
- Regular access reviews required

---

**Version:** 1.0
**Last Updated:** 2026-01-28

**Related Documentation:**
- `tenant-docs/admin-guides/log-access-guide.md` - How to access logs
- `tenant-docs/infrastructure/iam-role-setup.md` - How to set up IAM roles
