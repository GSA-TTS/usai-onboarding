# USAI Tenant Documentation

**Quick, focused documentation for tenant administrators**

**Last Updated:** 2026-02-17 | **Version:** 2.0

---

## 🚀 Getting Started

### Quick Start Guide

**[QUICK_START.md](./QUICK_START.md)** - Universal setup guide for all tenants (10 minutes)

**New to USAI?**
1. Read [QUICK_START.md](./QUICK_START.md)
2. Use values from your tenant-specific configuration file (provided by USAI team)

---

## 📚 Documentation Structure

### Quick Start (⚡ 10 minutes)
Universal setup guide for all tenants:
- **[QUICK_START.md](./QUICK_START.md)** - Get log access working in 10 minutes (tenant-agnostic)

### Admin Guides (📖 Complete)
Comprehensive how-to guides:
- **[Log Access Guide](./admin-guides/log-access-guide.md)** - Complete guide to accessing logs
- **[Security Best Practices](./admin-guides/security-best-practices.md)** - Credentials, rotation, monitoring
- **[Raw vs Redacted Logs](./admin-guides/raw-vs-redacted-logs.md)** - Understanding PII redaction

### Troubleshooting (🔧 Fix Problems)
Problem-solving guides:
- **[DLQ Investigation Guide](./troubleshooting/dlq-investigation.md)** - Dead letter queue debugging

### Architecture (🏗️ How It Works)
Technical overviews:
- **[Log Notification Architecture](./architecture/log-notification-architecture.md)** - S3 → SNS → SQS flow

### Onboarding (🚀 For New Tenant Administrators)
**Starting your USAI log access?**
- **[Getting Started Guide](./onboarding/README.md)** - What to expect during onboarding

---

## 🎯 Quick Links by Task

### I want to...

| Task | Document | Time |
|------|----------|------|
| **Set up log access (first time)** | [Quick Start](./QUICK_START.md) + config from USAI team | 10 min |
| **Download logs manually** | [Quick Start](./QUICK_START.md) → Manual Download | 5 min |
| **Automate log collection** | [Quick Start](./QUICK_START.md) → Python Script | 15 min |
| **Rotate my access keys** | [Security Best Practices](./admin-guides/security-best-practices.md) | 15 min |
| **Fix DLQ alert** | [DLQ Investigation Guide](./troubleshooting/dlq-investigation.md) | 20 min |
| **Understand log format** | [Quick Start](./QUICK_START.md) → Log Format | 5 min |
| **Learn the architecture** | [Log Notification Architecture](./architecture/log-notification-architecture.md) | 10 min |

---

## 📂 Directory Structure

```
public/
├── README.md                          # This file
├── QUICK_START.md                     # ⚡ Universal 10-minute setup guide
│
├── onboarding/                        # 🚀 For new tenant administrators
│   └── README.md                      # What to expect during onboarding
│
├── admin-guides/                      # 📖 How-to guides
│   ├── log-access-guide.md
│   ├── security-best-practices.md
│   └── raw-vs-redacted-logs.md
│
├── troubleshooting/                   # 🔧 Problem solving
│   └── dlq-investigation.md
│
└── architecture/                      # 🏗️ System design
    └── log-notification-architecture.md
```

---

## 🎓 Learning Path

**New Administrator? Follow this path:**

### Day 1: Get Access Working
- **Read:** [Quick Start](./QUICK_START.md) + your [tenant config](./tenants/)
- **Do:** Set up AWS CLI, verify access, download first log

### Week 1: Automate
- **Read:** [Quick Start](./QUICK_START.md) → Python Script
- **Do:** Deploy automated consumer, verify downloads

### Week 2: Secure
- **Read:** [Security Best Practices](./admin-guides/security-best-practices.md)
- **Do:** Implement credential storage, set rotation schedule

### Month 1: Monitor
- **Read:** [DLQ Investigation Guide](./troubleshooting/dlq-investigation.md)
- **Do:** Set up DLQ alerts, test investigation process

### Ongoing: Maintain
- Monitor DLQ weekly
- Review security logs monthly
- Rotate keys quarterly (90 days)

---

## 🌐 Universal Documentation

All documentation in this directory is tenant-agnostic and works for all USAI tenants.

**Your tenant-specific configuration** (AWS account, queue URLs, bucket names) will be provided by the USAI infrastructure team during onboarding.

**Getting started:**
- See [Getting Started Guide](./onboarding/README.md) - What to expect during onboarding
- Review [Quick Start Guide](./QUICK_START.md) when you receive your configuration

---

## 🔒 Security & Tenant Isolation

### Each Tenant Has:
- ✅ Isolated AWS account
- ✅ Separate S3 bucket and SQS queues
- ✅ Private credentials
- ✅ No cross-tenant access

### Security Notes:
- This documentation contains placeholders (no real credentials)
- Actual credentials provided separately via secure channel
- Never commit credentials to git
- Rotate keys every 90 days

---

## 📞 Support

### Before Contacting Support

1. ✅ Check your tenant's **Quick Start** guide
2. ✅ Search **Admin Guides** for your question
3. ✅ Review **Troubleshooting** guides

### Contact Information

| Issue Type | Contact |
|------------|---------|
| **Access/Credentials/IAM** | USAI Infrastructure Team |
| **Log Content/Format** | USAI Development Team |
| **Security Incident** | USAI Security Team (Immediate) |

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-02-17 | Added Quick Start guides, DLQ docs, restructured for clarity |
| 1.0 | 2026-01-28 | Initial documentation |

---

## 📖 Related Documentation

### AWS Documentation
- [AWS SQS](https://docs.aws.amazon.com/sqs/)
- [AWS S3](https://docs.aws.amazon.com/s3/)
- [Boto3 Python SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

## 📝 Documentation Philosophy

### Our Approach

**Quick Start First:** Get working in 10 minutes, drill into details later

**Task-Oriented:** Organized by "I want to..." not "This is how it works"

**Progressive Disclosure:** Start simple, link to details when needed

**Real Examples:** Working commands you can copy-paste

### Document Types

| Type | Goal | Format | Example |
|------|------|--------|---------|
| **⚡ Quick Start** | Working in 10 min | Step-by-step with variables | [QUICK_START.md](./QUICK_START.md) |
| **🚀 Onboarding** | What to expect | Timeline + setup | [Getting Started](./onboarding/README.md) |
| **📖 Admin Guide** | Complete reference | Detailed + examples | [Log Access Guide](./admin-guides/log-access-guide.md) |
| **🔧 Troubleshooting** | Fix problem | Symptom → fix | [DLQ Guide](./troubleshooting/dlq-investigation.md) |
| **🏗️ Architecture** | Understand system | Diagrams + details | [Architecture](./architecture/log-notification-architecture.md) |

---

**Questions?** Start with your Quick Start guide! 🚀
