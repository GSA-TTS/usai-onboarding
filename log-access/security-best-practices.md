# Security Best Practices - USAI Log Access

**Quick reference for secure credential and log management**

---

## Credential Management

### ✅ DO

**Store Securely:**
- AWS Secrets Manager (recommended)
- Password manager (1Password, LastPass)
- Encrypted key vault
- Environment variables (production servers only)

**Rotate Regularly:**
- Every 90 days (required)
- Immediately if compromised
- After team member departure

**Restrict Access:**
- Share on need-to-know basis
- Use separate credentials per environment
- Enable MFA on AWS account

**Monitor Usage:**
- Review CloudTrail logs monthly
- Set up alerts for unusual activity
- Track who has access

---

### ❌ DON'T

**Never Store In:**
- Git repositories
- Source code
- Plain text files
- Shared documents
- Email or chat

**Never:**
- Share credentials via email
- Reuse credentials across systems
- Use credentials after departure
- Skip rotation schedule

---

## AWS CLI Configuration

### Secure Setup

**Use AWS Profiles:**
```bash
# Good: Isolated profile
aws configure --profile ed-logs

# Bad: Default profile (conflicts with other projects)
aws configure
```

**Credentials File Permissions:**
```bash
# Restrict access to your user only
chmod 600 ~/.aws/credentials
chmod 600 ~/.aws/config

# Verify
ls -la ~/.aws/
# Should show: -rw------- (600)
```

**Environment Variables:**
```bash
# Development (session only)
export AWS_PROFILE=ed-logs
export AWS_REGION=us-east-1

# Production (systemd service file, docker-compose, etc.)
Environment="AWS_PROFILE=ed-logs"
Environment="AWS_REGION=us-east-1"
```

---

## Key Rotation

### Every 90 Days

**Step 1: Create New Key**
```bash
# Request new access key from infrastructure team
# You'll receive: New Access Key ID and Secret Access Key
```

**Step 2: Test New Key**
```bash
# Configure new key as separate profile
aws configure --profile ed-logs-new

# Test access
AWS_PROFILE=ed-logs-new aws sts get-caller-identity
```

**Step 3: Update Applications**
```bash
# Update all systems using old credentials
# Test each system with new credentials
```

**Step 4: Deactivate Old Key**
```bash
# Notify infrastructure team to deactivate old key
# Monitor for any failures (indicates missed system)
```

**Step 5: Delete Old Key**
```bash
# After 7 days, if no issues, request old key deletion
```

---

## Access Permissions

### Your IAM User Can:

✅ **SQS:**
- Receive messages from your queue
- Delete messages after processing
- Get queue attributes

✅ **S3:**
- List objects in your bucket
- Download log files
- View object metadata

✅ **CloudWatch (optional):**
- View logs related to your resources

---

### Your IAM User Cannot:

❌ **Prevent:**
- Write to S3 bucket
- Delete S3 objects
- Modify queue configuration
- Access other tenants' resources
- Create/delete AWS resources

---

## Data Handling

### Log Files Contain Sensitive Data

**PII May Include:**
- User conversations (interaction-raw queue)
- Email addresses, names
- Agency-specific information

**Security Requirements:**
- Encrypt at rest
- Encrypt in transit
- Access logging
- Retention policies

---

### Downloaded Logs

**Local Storage:**
```bash
# Encrypt downloaded logs
mkdir -p ~/secure-logs
chmod 700 ~/secure-logs

# Download to encrypted directory
aws s3 cp s3://bucket/key ~/secure-logs/

# Optional: Encrypt files
gpg --encrypt --recipient your@email.com ~/secure-logs/log.json
```

**Retention:**
- Delete after processing (if possible)
- Max 90 days local retention
- Use encrypted drives

**Transfer:**
- Use SFTP/SCP (never FTP)
- Encrypt before sending
- Delete after confirmation

---

## Network Security

### IP Restrictions (Optional)

Request IP allowlist from infrastructure team:
```
# Example allowlist
203.0.113.0/24    # Office network
198.51.100.0/24   # VPN network
```

---

### VPC Endpoints (Optional)

For maximum security, request VPC endpoint access:
- No internet exposure
- Traffic stays within AWS network
- Requires VPC setup

---

## Monitoring and Auditing

### What Gets Logged

**CloudTrail captures:**
- AWS API calls
- Authentication attempts
- S3 downloads
- SQS message receives
- Failed access attempts

---

### Regular Reviews

**Monthly:**
- Review CloudTrail logs
- Check for unauthorized access
- Verify access patterns

**Quarterly:**
- Audit user access list
- Remove departed team members
- Update IP allowlists

**Annually:**
- Security assessment
- Policy review
- Training refresh

---

## Incident Response

### If Credentials Compromised

**Immediate Actions (within 1 hour):**

1. **Notify infrastructure team**
   - Request immediate key deactivation
   - Provide incident details

2. **Change all passwords**
   - AWS console password
   - Associated accounts

3. **Review access logs**
   ```bash
   # Check recent activity
   aws cloudtrail lookup-events \
     --lookup-attributes AttributeKey=Username,AttributeValue=usai-${TENANT_CODE}-production-interaction-raw-reader-user \
     --max-results 50 \
     --region us-east-1
   ```

4. **Generate new credentials**
   - Request new access key
   - Update all systems
   - Verify old key deactivated

---

### Suspicious Activity

**Indicators:**
- Unexpected API calls
- Access from unknown IPs
- Failed authentication attempts
- Large data downloads

**Response:**
1. Document suspicious activity
2. Notify security team
3. Rotate credentials
4. Review access logs
5. Update security controls

---

## Compliance

### FISMA/FedRAMP Requirements

**Credential Rotation:**
- Every 90 days (required)
- Document rotation schedule
- Maintain audit trail

**Access Logging:**
- CloudTrail enabled
- Logs retained 90+ days
- Regular log reviews

**Encryption:**
- TLS 1.2+ for transit
- AES-256 for rest
- KMS key management

---

### Audit Documentation

**Maintain Records:**
- Access requests
- Key rotations
- Incident responses
- Security reviews

**Annual Audit:**
- Provide access to auditors
- Demonstrate compliance
- Update policies

---

## Security Checklist

### Initial Setup
- [ ] Credentials stored in password manager
- [ ] AWS CLI credentials file permissions (600)
- [ ] MFA enabled on AWS account
- [ ] Test access with new credentials
- [ ] Bookmark 90-day rotation date
- [ ] Review security policies

### Monthly
- [ ] Review CloudTrail logs
- [ ] Check for suspicious activity
- [ ] Verify active users list
- [ ] Test backup access method

### Quarterly (90 days)
- [ ] Rotate access keys
- [ ] Update all systems with new credentials
- [ ] Audit access logs
- [ ] Review team access list
- [ ] Update IP allowlists (if used)

### Annually
- [ ] Security assessment
- [ ] Policy review
- [ ] Team training
- [ ] Compliance documentation

---

## Related Documentation

- [Quick Start Guide](../QUICK_START.md)
- [Complete Admin Guide](./log-access-guide.md)
- [DLQ Investigation](../troubleshooting/dlq-investigation.md)

---

## Security Contacts

**Incident Response:**
- Rotate credentials immediately
- Contact: USAI Security Team

**Policy Questions:**
- Contact: USAI Compliance Team

**Access Issues:**
- Contact: USAI Infrastructure Team

---

**Last Updated:** 2026-02-17
**Review Frequency:** Quarterly
