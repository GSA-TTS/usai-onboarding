# USAI Log Access - Quick Start

**Get up and running in 10 minutes**

---

## 📋 Before You Begin

You'll need:
- Your AWS credentials (Access Key ID and Secret Access Key)
- Your tenant configuration (see below)

**Don't have these?** Contact your USAI infrastructure team.

---

## 🔧 Your Tenant Configuration

Copy this information from your infrastructure team:

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

---

## 🚀 Setup (5 minutes)

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

# ✅ Test 1: Verify identity
aws sts get-caller-identity

# ✅ Test 2: Poll queue
aws sqs receive-message \
  --queue-url ${QUEUE_URL} \
  --max-number-of-messages 1 \
  --wait-time-seconds 5 \
  --region ${AWS_REGION}

# ✅ Test 3: List S3 files
aws s3 ls s3://${BUCKET_NAME}/ --region ${AWS_REGION}
```

**All three commands work?** ✅ You're ready!

---

## 📥 Download Logs (Manual)

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

## 🤖 Automated Consumer (Python)

### Configuration File

Create `config.env`:

```bash
# Copy your tenant configuration here
QUEUE_URL="your-queue-url"
BUCKET_NAME="your-bucket-name"
AWS_REGION="us-east-1"
DOWNLOAD_DIR="./logs"
```

### Consumer Script

Save as `consume_logs.py`:

```python
#!/usr/bin/env python3
"""
USAI Analytics Log Consumer
Polls SQS and downloads new log files from S3
"""

import json, boto3, os
from pathlib import Path
from dotenv import load_dotenv

# Load configuration
load_dotenv('config.env')

QUEUE_URL = os.getenv('QUEUE_URL')
BUCKET = os.getenv('BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', './logs')

# Initialize AWS clients
sqs = boto3.client('sqs', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)

def process_queue():
    """Poll queue and download files."""
    resp = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20
    )

    for msg in resp.get('Messages', []):
        try:
            # Parse S3 event (nested JSON)
            body = json.loads(msg['Body'])
            event = json.loads(body['Message'])

            for record in event.get('Records', []):
                key = record['s3']['object']['key']

                # Download file
                local_path = Path(DOWNLOAD_DIR) / key
                local_path.parent.mkdir(parents=True, exist_ok=True)
                s3.download_file(BUCKET, key, str(local_path))
                print(f"✅ Downloaded: {local_path}")

            # Delete message after successful download
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=msg['ReceiptHandle']
            )

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    Path(DOWNLOAD_DIR).mkdir(exist_ok=True)
    print(f"Polling {QUEUE_URL}")
    print("Press Ctrl+C to stop...")

    try:
        while True:
            process_queue()
    except KeyboardInterrupt:
        print("\nStopped")
```

### Run Consumer

```bash
# Install dependencies
pip install boto3 python-dotenv

# Set AWS profile
export AWS_PROFILE=${TENANT_CODE}-logs

# Run consumer
python3 consume_logs.py
```

---

## 📊 Log Format

**Format:** NDJSON (one JSON object per line)

**Example Event:**
```json
{
  "event_id": "abc-123",
  "event_time": "2026-02-17T10:30:00Z",
  "kind": "chat_completion",
  "user_id": "user-456",
  "model": "claude-sonnet-4",
  "tokens_prompt": 21,
  "tokens_response": 150,
  "latency_ms": 250
}
```

**Common Operations:**
```bash
# View first 5 events
head -5 log.json | jq .

# Count events
wc -l log.json

# Extract specific fields
cat log.json | jq '{event_id, model, tokens_prompt, tokens_response}'

# Count by model
cat log.json | jq -r '.model' | sort | uniq -c
```

---

## 🔧 Common Issues

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
Dead Letter Queue should be empty. If you receive an alert:
```bash
# Check DLQ
aws sqs get-queue-attributes \
  --queue-url ${DLQ_URL} \
  --attribute-names ApproximateNumberOfMessages \
  --region ${AWS_REGION}
```

**Has messages?** See: [DLQ Troubleshooting Guide](./troubleshooting/dlq-investigation.md)

---

## 📚 More Information

| Topic | Document | Time |
|-------|----------|------|
| **Complete Setup Guide** | [Admin Guide](./admin-guides/log-access-guide.md) | 20 min |
| **DLQ Troubleshooting** | [DLQ Investigation](./troubleshooting/dlq-investigation.md) | 15 min |
| **Security Best Practices** | [Security Guide](./admin-guides/security-best-practices.md) | 15 min |
| **System Architecture** | [Architecture](./architecture/log-notification-architecture.md) | 10 min |

---

## 🔒 Security Reminders

- ❌ Never commit credentials to git
- ❌ Never share credentials via email
- ✅ Rotate keys every 90 days
- ✅ Store in password manager or AWS Secrets Manager

---

## ✅ Quick Checklist

- [ ] AWS CLI installed
- [ ] Credentials configured
- [ ] Identity verified (Test 1)
- [ ] Queue accessible (Test 2)
- [ ] S3 accessible (Test 3)
- [ ] Downloaded first log file
- [ ] Reviewed log format

**All done?** 🎉 You're ready to access USAI logs!

---

## 📞 Support

**Questions?** Contact your USAI infrastructure team

**Key Rotation Due:** 90 days from key creation

---

**Last Updated:** 2026-02-17
**Version:** 2.0
