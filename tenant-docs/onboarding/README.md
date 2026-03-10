# Getting Started with USAI Log Access

**Quick guide for tenant administrators receiving log access**

---

## 📦 What You're Getting

### AWS Resources

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

## 📋 What You'll Receive

From the USAI infrastructure team:

1. **Credentials** (via secure method)
   - AWS Access Key ID
   - AWS Secret Access Key

2. **Configuration File**
   - Your queue URLs
   - Your bucket names
   - AWS region and account ID

3. **Documentation Links**
   - Quick Start guide
   - Troubleshooting resources

---

## 🚀 Getting Started (Day 1)

### 1. Configure AWS CLI (5 minutes)

```bash
aws configure --profile usai-logs
# Enter credentials from handoff email
```

### 2. Test Queue Access (2 minutes)

```bash
# Use queue URL from your config file
aws sqs receive-message \
  --queue-url [YOUR_QUEUE_URL] \
  --max-number-of-messages 1 \
  --profile usai-logs
```

✅ **Success:** Returns empty response or S3 event notifications

### 3. Test S3 Access (2 minutes)

```bash
# Use bucket name from your config file
aws s3 ls s3://[YOUR_BUCKET_NAME]/ --profile usai-logs
```

✅ **Success:** Lists log files (or empty if no logs yet)

### 4. Download a Log File (2 minutes)

```bash
aws s3 cp s3://[YOUR_BUCKET_NAME]/[FILE_KEY] /tmp/ --profile usai-logs
```

✅ **Success:** File downloaded locally

---

## 📖 Next Steps

**Week 1:**
- Review **[Quick Start Guide](../QUICK_START.md)** for detailed setup
- Review your tenant-specific configuration file
- Test all 3 queue types (raw, redacted, audit)

**Week 2:**
- Optional: Deploy automated consumer (see Quick Start)
- Set up credential rotation reminder (90 days)

---

## 🆘 Troubleshooting

### Access Denied
```bash
# Verify your identity
aws sts get-caller-identity --profile usai-logs
```
Should show your IAM user ARN.

### Queue Empty
- Logs may not be flowing yet (new system)
- Use `--wait-time-seconds 20` for long polling
- Verify queue URL is correct

### Credentials Not Working
- Double-check credentials (no typos)
- Verify AWS region matches your config
- Contact USAI infrastructure team

---

## 📞 Support

| Issue | Contact |
|-------|---------|
| Credentials/Access | USAI Infrastructure Team |
| Log Format | USAI Development Team |
| Security Incident | USAI Security Team (immediate) |

---

## ✅ Setup Checklist

- [ ] Received credentials securely
- [ ] Configured AWS CLI profile
- [ ] Tested queue access (all 3 queues)
- [ ] Tested S3 bucket access
- [ ] Downloaded first log file
- [ ] Set 90-day rotation reminder

---

**Next:** See [Quick Start Guide](../QUICK_START.md) for detailed usage

**Last Updated:** 2026-02-17
