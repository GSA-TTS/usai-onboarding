# Tenant Admin Log Access Guide

**Audience:** Tenant administrators
**Purpose:** Access analytics interaction logs from your tenant's AWS account
**Last Updated:** 2026-02-02

## Overview

Your USAI tenant has analytics logs automatically delivered to S3 via AWS Kinesis Firehose. When new log files are created, notifications are sent to an SQS queue. You can poll this queue to discover new files and download them for analysis.

**⚠️ Important:** You have TWO bucket options - **RAW** (full conversation content) or **REDACTED** (PII masked). See [raw-vs-redacted-logs.md](raw-vs-redacted-logs.md) to choose which is right for you. Most users should start with **REDACTED**.

**Architecture:**
```
Application → Firehose → S3 Bucket
                           ↓ (S3 Event: ObjectCreated)
                        SNS Topic
                           ↓
                        SQS Queue ← You poll here

S3 Bucket ← You download files from here
```

## Prerequisites

### 1. Tenant Information

Contact your infrastructure team to obtain:

- **AWS Account ID** - Your tenant's AWS account number
- **Tenant Code** - Your identifier (e.g., "gsa", "ed", "hhs")
- **IAM Role ARN** - Role you'll assume to access logs
- **SQS Queue URL** - Queue to poll for notifications
- **S3 Bucket Name** - Bucket containing your log files
- **AWS Region** - Typically `us-east-1`

### 2. AWS CLI Installation

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows (PowerShell as Administrator)
# Download and run the MSI installer from:
# https://awscli.amazonaws.com/AWSCLIV2.msi
# Or use: msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify installation (all platforms)
aws --version
```

### 3. Python (for automation scripts)

```bash
# macOS/Linux: Python 3.8+ recommended
python3 --version
pip install boto3

# Windows: Download from https://www.python.org/downloads/
# Verify installation
python --version
pip install boto3
```

## Resource Naming Pattern

Your resources follow this pattern:

| Resource | Pattern | Example |
|----------|---------|---------|
| SQS Queue (RAW) | `usai-{TENANT}-core-production-interaction-raw-queue` | `usai-example-core-production-interaction-raw-queue` |
| SQS Queue (REDACTED) | `usai-{TENANT}-core-production-interaction-redacted-queue` | `usai-example-core-production-interaction-redacted-queue` |
| S3 Bucket (RAW) | `usai-{TENANT}-core-production-interaction-raw` | `usai-example-core-production-interaction-raw` |
| S3 Bucket (REDACTED) | `usai-{TENANT}-core-production-interaction-redacted` | `usai-example-core-production-interaction-redacted` |
| IAM User (RAW) | `usai-{TENANT}-production-interaction-raw-reader-user` | `usai-example-production-interaction-raw-reader-user` |
| IAM User (REDACTED) | `usai-{TENANT}-production-interaction-redacted-reader-user` | `usai-example-production-interaction-redacted-reader-user` |

**Note:** Replace `{TENANT}` with your tenant code. You'll be given access to either RAW or REDACTED resources based on your needs.

## Access Methods

### Method 1: IAM User with Access Keys (Standard)

Your infrastructure team has created an IAM user for log access:
- **User Name (RAW):** `usai-{TENANT}-production-interaction-raw-reader-user`
- **User Name (REDACTED):** `usai-{TENANT}-production-interaction-redacted-reader-user`
- **Example:** `usai-gsa-production-interaction-raw-reader-user` or `usai-gsa-production-interaction-redacted-reader-user`

**Note:** You'll receive credentials for either RAW or REDACTED based on your chosen bucket type.

**Get Access Keys from Infrastructure Team:**

Your infrastructure team will provide:
1. AWS Access Key ID
2. AWS Secret Access Key

**Configure AWS CLI:**

```bash
# Configure credentials (all platforms)
aws configure --profile {tenant}-logs
# Enter Access Key ID when prompted
# Enter Secret Access Key when prompted
# Region: us-east-1
# Output format: json

# Use the profile
# macOS/Linux:
export AWS_PROFILE={tenant}-logs
# Windows (Command Prompt):
set AWS_PROFILE={tenant}-logs
# Windows (PowerShell):
$env:AWS_PROFILE="{tenant}-logs"

# Verify access (all platforms)
aws sts get-caller-identity
```

**Security Note:** Store access keys securely. Never commit them to source control.

## Quick Start: Manual Access

### Step 1: Check for Notifications

```bash
# macOS/Linux: Set your queue URL (get from infrastructure team)
QUEUE_URL="https://sqs.{REGION}.amazonaws.com/{ACCOUNT_ID}/usai-{TENANT}-core-production-interaction-raw-queue"

# Poll the queue
aws sqs receive-message \
  --queue-url "$QUEUE_URL" \
  --max-number-of-messages 10 \
  --wait-time-seconds 20 \
  --region {REGION}
```

**Windows users:** Replace `$QUEUE_URL` with the full queue URL in all commands.

**Output:** JSON with S3 object keys in the message body

### Step 2: Parse the Notification

The SQS message contains an SNS notification, which contains the S3 event:

```json
{
  "Messages": [
    {
      "MessageId": "abc-123...",
      "ReceiptHandle": "xyz-789...",
      "Body": "{\"Message\": \"{\\\"Records\\\":[{\\\"s3\\\":{\\\"bucket\\\":{\\\"name\\\":\\\"usai-example-...\\\"},\\\"object\\\":{\\\"key\\\":\\\"2026/01/28/file.json\\\"}}}}]}\"}"
    }
  ]
}
```

Extract the S3 bucket and key from the nested JSON.

### Step 3: Download the File

```bash
# Download from S3
aws s3 cp \
  s3://usai-{TENANT}-core-production-interaction-raw/2026/01/28/file.json \
  ./downloaded-logs/ \
  --region {REGION}
```

### Step 4: Delete the SQS Message

After successfully downloading:

```bash
aws sqs delete-message \
  --queue-url "$QUEUE_URL" \
  --receipt-handle "xyz-789..." \
  --region {REGION}
```

**Important:** Always delete messages after processing to avoid reprocessing.

## Automated Access: Python Script

### Complete Consumer Script

Save as `consume_logs.py`:

```python
#!/usr/bin/env python3
"""
USAI Analytics Log Consumer

Polls SQS queue for new log file notifications and downloads them from S3.
"""

import json
import boto3
import sys
import os
from pathlib import Path
from datetime import datetime

# ==================== CONFIGURATION ====================
# UPDATE THESE VALUES FOR YOUR TENANT
TENANT = "example"  # CHANGE THIS: Your tenant code (e.g., gsa, ed, hhs)
AWS_REGION = "us-east-1"  # CHANGE THIS: Your AWS region
AWS_ACCOUNT_ID = "123456789012"  # CHANGE THIS: Your AWS account ID
LOG_TYPE = "raw"  # CHANGE THIS: "raw" or "redacted" (see raw-vs-redacted-logs.md)

# Constructed from above (usually don't need to change)
QUEUE_NAME = f"usai-{TENANT}-core-production-interaction-{LOG_TYPE}-queue"
BUCKET_NAME = f"usai-{TENANT}-core-production-interaction-{LOG_TYPE}"
DOWNLOAD_DIR = "./downloaded-logs"
# =======================================================

# Initialize AWS clients
sqs = boto3.client('sqs', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)

def get_queue_url():
    """Get the SQS queue URL from the queue name."""
    try:
        response = sqs.get_queue_url(QueueName=QUEUE_NAME)
        return response['QueueUrl']
    except Exception as e:
        print(f"Error getting queue URL: {e}")
        print(f"\nMake sure you've configured:")
        print(f"  - TENANT = '{TENANT}'")
        print(f"  - AWS_ACCOUNT_ID = '{AWS_ACCOUNT_ID}'")
        print(f"  - AWS credentials are configured")
        sys.exit(1)

def parse_s3_event(message_body):
    """
    Parse the S3 event from the SQS message.

    SQS message contains SNS notification, which contains S3 event.
    Returns list of (bucket, key) tuples.
    """
    try:
        # Parse outer SNS message
        sns_message = json.loads(message_body)

        # Parse inner S3 event
        s3_event = json.loads(sns_message['Message'])

        # Extract S3 records
        records = []
        for record in s3_event.get('Records', []):
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            records.append((bucket, key))

        return records
    except Exception as e:
        print(f"Error parsing S3 event: {e}")
        return []

def download_file(bucket, key):
    """Download a file from S3 to local directory."""
    try:
        # Create local path preserving S3 structure
        local_path = Path(DOWNLOAD_DIR) / key
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Download file
        print(f"Downloading: s3://{bucket}/{key}")
        s3.download_file(bucket, key, str(local_path))
        print(f"  → Saved to: {local_path}")

        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def process_messages(queue_url, max_messages=10):
    """Poll SQS queue and process messages."""
    try:
        # Receive messages from queue
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=20,  # Long polling
            MessageAttributeNames=['All']
        )

        messages = response.get('Messages', [])

        if not messages:
            print(f"[{datetime.now()}] No new messages")
            return 0

        print(f"\n[{datetime.now()}] Received {len(messages)} message(s)")

        processed = 0
        for message in messages:
            message_id = message['MessageId']
            receipt_handle = message['ReceiptHandle']
            body = message['Body']

            print(f"\nProcessing message: {message_id}")

            # Parse S3 events from message
            s3_records = parse_s3_event(body)

            if not s3_records:
                print("  → No S3 records found, skipping")
                continue

            # Download all files in this notification
            all_successful = True
            for bucket, key in s3_records:
                if not download_file(bucket, key):
                    all_successful = False

            # Delete message from queue if all downloads successful
            if all_successful:
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle
                )
                print(f"  → Message deleted from queue")
                processed += 1
            else:
                print(f"  → Message left in queue (download failed)")

        return processed

    except Exception as e:
        print(f"Error processing messages: {e}")
        return 0

def main():
    """Main loop - poll queue and download files."""
    print(f"USAI Analytics Log Consumer")
    print(f"============================")
    print(f"Tenant: {TENANT}")
    print(f"Account: {AWS_ACCOUNT_ID}")
    print(f"Region: {AWS_REGION}")
    print(f"Queue: {QUEUE_NAME}")
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Download Directory: {DOWNLOAD_DIR}\n")

    # Create download directory
    Path(DOWNLOAD_DIR).mkdir(exist_ok=True)

    # Get queue URL
    queue_url = get_queue_url()
    print(f"Queue URL: {queue_url}\n")

    # Poll queue continuously
    print("Starting to poll queue (Ctrl+C to stop)...\n")

    try:
        while True:
            processed = process_messages(queue_url)

            if processed > 0:
                print(f"\nProcessed {processed} message(s)")

    except KeyboardInterrupt:
        print("\n\nStopping consumer...")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### Configuration

**Before running, update these variables at the top of the script:**

```python
TENANT = "your-tenant-code"  # e.g., "gsa", "ed", "hhs"
AWS_REGION = "us-east-1"     # Your AWS region
AWS_ACCOUNT_ID = "123456789012"  # Your AWS account ID
LOG_TYPE = "raw"  # "raw" or "redacted" - see raw-vs-redacted-logs.md
```

### Run the Consumer

```bash
# macOS/Linux
chmod +x consume_logs.py
./consume_logs.py

# Windows (Command Prompt or PowerShell)
python consume_logs.py
```

## Log File Format

Log files are in **NDJSON** (Newline Delimited JSON) format, optionally gzip-compressed.

> **⚠️ Upcoming change — context-history split.** The RAW stream is changing so that
> conversation content is written to a **separate S3 object** rather than embedded in
> the streamed event. Firehose delivery, bucket, and dated prefix stay the same, but
> `prompt`, `response`, and `truncated` leave the event; `status`,
> `context_history_s3_key`, and a top-level `usage` are added. See
> [Context-history split](#context-history-split-upcoming) below and the
> [migration checklist](raw-vs-redacted-logs.md#migration-checklist-for-consumers).

### File Naming Pattern

```
{YEAR}/{MONTH}/{DAY}/{TIMESTAMP}-{UUID}.json
```

Example: `2026/01/28/10-30-00-abc123def456.json`

After the context-history split there is a second, separately keyed artifact per
request holding the conversation content:

```
chat/{conversation_id}/{event_id}.json      # source = "chat"
api/{user_id}/{event_id}.json               # source = "api"
```

### File Contents

Each line is a JSON object representing one analytics event.

**RAW logs contain:**
```json
{
  "event_id": "024f481f-8e11-42cc-bd23-e39e0596a6b2",
  "event_time": "2026-07-23T13:04:51.300501+00:00",
  "source": "api",
  "stream": true,
  "kind": "chat_completion",
  "user_id": "api-key-abcdefghijk",
  "request_id": "111e111c-3f65-47d8-abf0-c2ddf6c2f994",
  "model": "claude-sonnet-4.6",
  "platform_model_id": "inference-profile/us.anthropic.claude-sonnet-4-6",
  "truncated": false,
  "prompt": {
    "messages": [
      { "role": "user", "content": [ { "type": "text", "text": "Full user question text" } ] }
    ],
    "tool_choice": "auto",
    "tools": [ { "type": "function", "function": { "name": "read_file", "parameters": { "type": "object" } } } ]
  },
  "response": {
    "choices": [ { "content": "Full AI response text", "finish_reason": "stop" } ],
    "usage": { "prompt_tokens": 18452, "completion_tokens": 312, "total_tokens": 18764, "latency_ms": 4210 }
  }
}
```

**REDACTED logs contain:**
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

**See [raw-vs-redacted-logs.md](raw-vs-redacted-logs.md) for detailed comparison, and [examples/](examples/) for the full JSON Schemas.**

### Context-history split (upcoming)

**Status:** announced by the platform team; cutover date not yet published. Applies
to the RAW stream. Whether the REDACTED stream also splits is not yet confirmed.

After the split, each request produces **two** artifacts.

**1. Metadata event** — one NDJSON line in the same dated prefix as today
(schema: [`interaction_raw_metadata_event_schema.json`](examples/interaction_raw_metadata_event_schema.json)):

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

**2. Context-history document** — a single JSON document (not NDJSON) at
`context_history_s3_key`, holding `prompt` and `response`
(schema: [`interaction_context_history_schema.json`](examples/interaction_context_history_schema.json)).

**Fetching content for an event:**

```bash
KEY=$(head -1 log.json | jq -r '.context_history_s3_key')
aws s3 cp s3://${BUCKET_NAME}/${KEY} ./context.json --region ${AWS_REGION}
jq '.prompt.messages[-1], .response.choices[0].content' context.json
```

```python
import json
import boto3

s3 = boto3.client("s3")

def load_context(bucket, event):
    """Fetch the conversation content for a split-format metadata event."""
    key = event.get("context_history_s3_key")
    if not key:
        # Pre-cutover event: content is inline.
        return {"prompt": event.get("prompt"), "response": event.get("response")}
    body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    return json.loads(body)

def token_usage(bucket, event):
    """usage lives on the metadata event; fall back to the context document."""
    usage = event.get("usage") or {}
    if usage.get("total_tokens") is None:
        usage = (load_context(bucket, event).get("response") or {}).get("usage", {})
    return usage
```

The helper above handles both formats, so you can deploy it before cutover.

**IAM note:** if your read policy was scoped to the dated
`{YEAR}/{MONTH}/{DAY}/*` prefix, it will not cover `chat/*` and `api/*`. Request an
updated policy from [usai-security@gsa.gov](mailto:usai-security@gsa.gov) before
cutover. Whether the context-history documents land in the same bucket is one of
the [open questions](raw-vs-redacted-logs.md#open-questions).

### Processing Log Files

```python
import json
import gzip

# For uncompressed files
with open('file.json', 'r') as f:
    for line in f:
        event = json.loads(line)
        print(f"Event: {event['event_id']}, User: {event['user_id']}")

# For gzip-compressed files
with gzip.open('file.json.gz', 'rt') as f:
    for line in f:
        event = json.loads(line)
        print(f"Event: {event['event_id']}, User: {event['user_id']}")
```

## Troubleshooting

### Issue: "Access Denied" when polling SQS

**Cause:** Your IAM credentials don't have SQS permissions

**Solution:**
1. Verify you're using the correct AWS profile/credentials
2. Ask infrastructure team to verify your IAM role has `sqs:ReceiveMessage` permission
3. Check you're accessing the correct AWS account

```bash
# Verify your identity
aws sts get-caller-identity

# Should show your tenant's account ID
```

### Issue: "Access Denied" when downloading from S3

**Cause:** Your IAM credentials don't have S3 read permissions

**Solution:**
1. Ask infrastructure team to verify your IAM role has `s3:GetObject` permission
2. Verify the bucket policy allows your role
3. Check if IP allowlists are blocking your IP address

```bash
# Test S3 access
aws s3 ls s3://usai-{TENANT}-core-production-interaction-raw/
```

### Issue: Queue is empty but logs should exist

**Possible reasons:**
1. Another consumer already processed the messages
2. Messages exceeded retention period (typically 4 days)
3. Firehose hasn't written files yet (buffering: 5 minutes)

**Solution:**
1. Check S3 bucket directly for recent files
2. Wait for next batch of logs (up to 5 minutes)

```bash
# List recent files in S3
aws s3 ls s3://usai-{TENANT}-core-production-interaction-raw/2026/01/28/ --recursive
```

### Issue: Invalid credentials

**Cause:** Access keys are incorrect or expired

**Solution:**
1. Verify you entered the correct access key ID and secret key
2. Contact infrastructure team to verify keys are active
3. Request new access keys if needed

```bash
# Verify credentials
aws sts get-caller-identity

# Should show the IAM user
```

## Security Best Practices

### 1. Use Temporary Credentials

- ✅ **DO:** Use AWS SSO or AssumeRole for temporary credentials
- ❌ **DON'T:** Use long-lived IAM user access keys

### 2. Never Share Credentials

- ❌ Never share AWS access keys
- ❌ Never commit credentials to source control
- ❌ Never send credentials via email or chat

### 3. Rotate Access Keys Regularly

**Policy:** Access keys must be rotated every 90 days

**Process:**
1. Infrastructure team generates new keys
2. New keys provided via secure channel
3. Test new keys before deactivating old ones
4. Old keys deactivated after confirmation
5. Old keys deleted after 24-48 hours

**Tracking:** Recurring meeting/reminder for rotation coordination

### 4. Protect Your Keys

- Never commit access keys to source control
- Never send keys via email or chat (use secure methods)
- Use environment variables or AWS credential files
- Store in password manager or secrets management system

### 5. Monitor Your Access

Review CloudTrail logs periodically to ensure only authorized access.

## Getting Help

### Infrastructure Team

For AWS access issues or IAM role problems:
- Topics: Permissions, account access, role creation
- Contact: Your infrastructure team

### Application Team

For log format or pipeline questions:
- Topics: Log content, analytics data, API issues
- Repository: usai-main
- Code: `api/app/analytics/`

### Documentation Issues

- Report errors or suggestions to your team
- Do not include sensitive information (credentials, account IDs) in reports

---

**Version:** 1.1
**Last Updated:** 2026-02-02
**Platforms:** Windows, macOS, Linux
