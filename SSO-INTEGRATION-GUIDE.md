# Single Sign-On Integration Guide

This guide provides comprehensive instructions for integrating your Identity Provider (IdP) with USAi using Keycloak. USAi supports both OIDC (OpenID Connect) and SAML protocols, along with SCIM 2.0 for automated user and group provisioning.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Integration Options](#integration-options)
4. [OIDC Integration](#oidc-integration)
5. [SAML Integration](#saml-integration)
6. [SCIM Provisioning](#scim-provisioning)
7. [Attribute Mapping](#attribute-mapping)
8. [Testing & Validation](#testing--validation)
9. [Troubleshooting](#troubleshooting)

## Overview

USAi uses Keycloak as its identity and access management solution, providing enterprise-grade SSO capabilities with support for:

- **OIDC (OpenID Connect)** - Modern OAuth 2.0-based authentication protocol (recommended)
- **SAML 2.0** - Industry-standard federation protocol for enterprise SSO
- **SCIM 2.0** - Automated user and group provisioning/deprovisioning

### Architecture

```
Your Agency IdP → Keycloak (USAi) → USAi Application
                     ↑
              SCIM Provisioning
```

## Prerequisites

Before beginning the integration, ensure you have:

### From Your Agency
- [ ] Admin access to your Identity Provider (Azure AD, Okta, Ping, etc.)
- [ ] **For Microsoft Entra ID users**: Your Tenant ID (GUID)
- [ ] Authority to register new applications in your IdP (or consent to USAi-created app for Entra)
- [ ] Authority to grant admin consent for application permissions (Entra ID)
- [ ] List of user attributes available for mapping
- [ ] Security policies for SSO and user provisioning
- [ ] IP addresses whitelisted (see [Firewall requests](#firewall-requests) in main README)

### From USAi Team
- [ ] USAi tenant instance URL (e.g., `https://your-agency.usai.gov`)
- [ ] Keycloak realm name for your agency
- [ ] Client ID and Client Secret (for OIDC)
- [ ] Metadata URLs or certificates (for SAML)
- [ ] SCIM endpoint URL and bearer token
- [ ] Scheduled co-work session

## Integration Options

### Option 1: OIDC Integration (Recommended)

**Best for:**
- Modern cloud-based identity providers (Azure AD, Okta, Auth0)
- Implementations requiring token-based authentication
- Mobile or API access scenarios
- Simplified configuration and maintenance

**Benefits:**
- Simpler configuration
- Better support for modern authentication flows
- Built-in token refresh capabilities
- Native support in most cloud IdPs

### Option 2: SAML Integration

**Best for:**
- Legacy enterprise SSO infrastructure
- Organizations with existing SAML-based integrations
- Specific compliance requirements mandating SAML

**Benefits:**
- Well-established enterprise standard
- Strong assertion-based security
- Wide compatibility with enterprise systems

### Option 3: Hybrid Approach

You can configure both OIDC and SAML simultaneously, allowing different user populations to authenticate using their preferred protocol.

## OIDC Integration

### Step 1: Register USAi in Your IdP

#### For Microsoft Entra ID (Streamlined Setup - Recommended)

If your agency uses Microsoft Entra ID (formerly Azure AD), USAi provides a streamlined setup process. This is the **recommended approach** as it ensures consistent configuration and reduces coordination time.

**How it works:**
1. **Your agency creates** the app registration in your Entra tenant (you maintain full control)
2. **You provide us** with your Tenant ID, Client ID, and Client Secret
3. **USAi automatically configures** the Keycloak side based on your information

**What we need from you:**
- **Tenant ID**: Your Microsoft Entra tenant ID (GUID format)
  - Find this in **Azure Portal** > **Azure Active Directory** > **Overview** > **Tenant ID**
  - Example: `12345678-1234-1234-1234-123456789abc`
- **Client ID**: The Application (client) ID after you create the app registration (see steps below)

**Your setup steps:**

1. Navigate to **Azure Portal** > **Azure Active Directory** > **App registrations**
2. Click **New registration**
3. Configure the application:
   ```
   Name: USAi - [Your Agency Name]
   Supported account types: Accounts in this organizational directory only
   Redirect URI: Web - https://your-agency.usai.gov/realms/your-realm/broker/oidc/endpoint
   ```
4. After creation, note the **Application (client) ID**
5. Navigate to **Certificates & secrets** > **New client secret**
6. Create a secret (recommended: 24-month expiration) and securely save the value
7. Navigate to **Token configuration** and add optional claims:
   - email
   - family_name
   - given_name
   - upn
8. Navigate to **API permissions** and ensure these are added:
   - Microsoft Graph > User.Read (Delegated)
   - OpenID permissions: openid, profile, email
9. Click **Grant admin consent for [Your Organization]**

**What to send us:** Email partnerships@usai.gov with:
```
Subject: Microsoft Entra OIDC Configuration - [Your Agency Name]

Tenant ID: [your-tenant-id]
Client ID: [your-client-id]
Client Secret: [your-client-secret]
Agency Name: [your-agency-name]
Technical Contact: [name and email]
```

**What USAi will do:**
The USAi team will automatically:
1. Configure the Keycloak identity provider with your Entra settings
2. Set up proper OIDC endpoints based on your Tenant ID
3. Configure attribute mappers for user profile fields
4. Set appropriate user session settings
5. Enable and test the identity provider

**Timeline:** Keycloak configuration typically completes within 1 business day after receiving your information.

---

#### For Microsoft Entra ID (Manual Co-work Setup)

If you prefer to configure both the Entra app and Keycloak during a live co-work session:

1. Create the app registration following the same steps as above
2. Bring the Client ID and Client Secret to the co-work session
3. We'll configure Keycloak together in real-time
4. We'll test the integration during the session

This approach is useful if you want hands-on involvement in the Keycloak configuration or have specific customization needs.

#### For Okta

1. Navigate to **Applications** > **Create App Integration**
2. Select **OIDC - OpenID Connect** and **Web Application**
3. Configure the application:
   ```
   App integration name: USAi - [Your Agency Name]
   Grant type: Authorization Code
   Sign-in redirect URIs: https://your-agency.usai.gov/realms/your-realm/broker/oidc/endpoint
   Sign-out redirect URIs: https://your-agency.usai.gov/realms/your-realm/broker/oidc/endpoint
   ```
4. Click **Save** and note the **Client ID** and **Client Secret**

#### For Other OIDC Providers

Consult your IdP documentation for creating an OIDC client application. You'll need:
- Authorization endpoint
- Token endpoint
- UserInfo endpoint
- JWKS URI (for token validation)
- Issuer URL

### Step 2: Configure Identity Provider in Keycloak

During the co-work session, the USAi team will configure Keycloak with your IdP information:

1. **Basic Configuration**
   - Alias: Your agency identifier (e.g., `agency-oidc`)
   - Display Name: What users see on login page
   - Enabled: Yes
   
2. **OIDC Settings**
   - Authorization URL: `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize` (Azure AD example)
   - Token URL: `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token`
   - Client ID: From Step 1
   - Client Secret: From Step 1
   - Client Authentication: Client secret sent as post
   - Validate Signatures: Yes
   - Use JWKS URL: Yes
   - JWKS URL: Your IdP's JWKS endpoint

3. **User Session Configuration**
   - Sync mode: Force
   - Trust Email: Yes (if your IdP is authoritative)
   - Account Linking Only: No (for first-time user creation)

### Step 3: Test OIDC Connection

1. Navigate to `https://your-agency.usai.gov`
2. Click the SSO button for your agency
3. You should be redirected to your IdP login page
4. After successful authentication, you should be redirected back to USAi
5. Verify user profile is populated correctly

## SAML Integration

### Step 1: Download USAi SAML Metadata

The USAi team will provide:
- **Entity ID**: `https://your-agency.usai.gov/realms/your-realm`
- **ACS URL**: `https://your-agency.usai.gov/realms/your-realm/broker/saml/endpoint`
- **SAML Metadata XML**: Complete metadata file

### Step 2: Register USAi in Your IdP

#### For Azure AD / Entra ID

1. Navigate to **Enterprise Applications** > **New application**
2. Select **Create your own application**
3. Choose **Integrate any other application you don't find in the gallery (Non-gallery)**
4. Name it: `USAi - [Your Agency Name]`
5. Navigate to **Single sign-on** > **SAML**
6. Click **Upload metadata file** and upload the USAi SAML metadata XML
7. Configure **User Attributes & Claims**:
   ```
   Required claims:
   - Unique User Identifier: user.userprincipalname
   - Email: user.mail
   - First Name: user.givenname
   - Last Name: user.surname
   ```
8. Download the **Federation Metadata XML**

#### For Okta

1. Navigate to **Applications** > **Create App Integration**
2. Select **SAML 2.0**
3. Configure General Settings:
   ```
   App name: USAi - [Your Agency Name]
   ```
4. Configure SAML Settings:
   ```
   Single sign on URL: https://your-agency.usai.gov/realms/your-realm/broker/saml/endpoint
   Audience URI (SP Entity ID): https://your-agency.usai.gov/realms/your-realm
   Name ID format: EmailAddress
   Application username: Email
   ```
5. Configure Attribute Statements:
   ```
   email: user.email
   firstName: user.firstName
   lastName: user.lastName
   ```
6. Click **Next** and complete the wizard
7. Navigate to **Sign On** tab and click **View SAML setup instructions**
8. Save the metadata XML or configuration URLs

### Step 3: Configure SAML Identity Provider in Keycloak

During the co-work session, the USAi team will:

1. Import your IdP's SAML metadata
2. Configure SAML settings:
   - Single Sign-On Service URL
   - Single Logout Service URL
   - NameID Policy Format: Email or Persistent
   - Want AuthnRequests Signed: Yes
   - Signature Algorithm: RSA_SHA256
   - SAML Signature Key Name: CERT_SUBJECT
3. Configure attribute mappers (see [Attribute Mapping](#attribute-mapping))
4. Enable the identity provider

### Step 4: Test SAML Connection

1. Navigate to `https://your-agency.usai.gov`
2. Click the SSO button for your agency
3. You should be redirected to your IdP SAML login page
4. After authentication, verify SAML response contains required attributes
5. Confirm successful login to USAi

## SCIM Provisioning

SCIM (System for Cross-domain Identity Management) enables automated user lifecycle management between your IdP and USAi.

### Benefits of SCIM Provisioning

- **Automated User Creation**: New users are automatically provisioned when added to your IdP
- **Real-time Updates**: User attribute changes sync immediately
- **Automated Deprovisioning**: Users removed from IdP are automatically deactivated in USAi
- **Group Management**: Group memberships are synchronized for access control
- **Centralized Authorization**: Use SCIM groups for role-based access control

### SCIM Configuration Options

USAi supports two mutually exclusive approaches for user provisioning:

#### Option 1: SCIM Provisioning (Recommended for Enterprise)
When SCIM provisioning is enabled, Just-in-Time (JIT) provisioning is automatically disabled. Users are **only** created via SCIM, not on first sign-in. This provides:
- ✅ **Centralized control** - IT controls who has access via IdP
- ✅ **Group-based authorization** - Roles assigned via SCIM group membership
- ✅ **Better audit trail** - All provisioning events logged in IdP
- ✅ **Prevents unauthorized access** - Users can't self-provision on first login

**When you enable SCIM provisioning:**
The USAi team will automatically configure:
- First Broker Login Flow: Disabled for automatic user creation
- SCIM as the sole provisioning method
- Group synchronization (if requested)

**Important:** Users must be provisioned via SCIM before they can sign in. If a user attempts to sign in before being provisioned via SCIM, they will receive an access denied message.

#### Option 2: Just-in-Time (JIT) Provisioning (Default without SCIM)
If you do **not** enable SCIM provisioning, JIT provisioning is used by default. Users are automatically created on first sign-in. This provides:
- ✅ **Easier initial rollout** - Users can access immediately after SSO setup
- ✅ **Self-service access** - No manual provisioning required
- ⚠️ **Less control** - Any user with IdP access can create an account
- ⚠️ **No group synchronization** - Group memberships must be managed manually in USAi

**Note:** You cannot have both SCIM and JIT enabled simultaneously. Enabling SCIM automatically disables JIT provisioning.

### SCIM Configuration Requirements

The USAi team will provide:
- **SCIM Base URL**: `https://your-agency.usai.gov/realms/your-realm/scim/v2`
- **Authentication Method**: Bearer Token
- **Bearer Token**: Long-lived API token for SCIM operations
- **Supported Operations**: Create, Read, Update, Delete, Search (for Users and Groups)

**What to tell us:**
- Whether you want SCIM provisioning enabled (this will automatically disable JIT provisioning)
- Whether you want group synchronization enabled
- Which IdP groups should map to USAi roles (if using group-based authorization)

### Step 1: Configure SCIM in Your IdP

#### For Azure AD / Entra ID

1. Navigate to your Enterprise Application for USAi
2. Go to **Provisioning** > **Get started**
3. Set **Provisioning Mode** to **Automatic**
4. Configure **Admin Credentials**:
   ```
   Tenant URL: https://your-agency.usai.gov/realms/your-realm/scim/v2
   Secret Token: [Bearer token provided by USAi team]
   ```
5. Click **Test Connection** to validate
6. Configure **Mappings**:
   
   **Provision Azure Active Directory Users:**
   - userName → userName
   - Switch([IsSoftDeleted], , "False", "True", "True", "False") → active
   - mail → emails[type eq "work"].value
   - givenName → name.givenName
   - surname → name.familyName
   - displayName → displayName
   
   **Provision Azure Active Directory Groups** (enable this for group-based authorization):
   - displayName → displayName
   - members → members
   
   **Important for SCIM-Only Provisioning:**
   - Go to **Settings** > **Scope**
   - Select **Sync only assigned users and groups**
   - This ensures only explicitly assigned users are provisioned (prevents self-provisioning)

7. **Configure Group Assignment** (if using group-based authorization):
   - Navigate to **Users and groups** in your Enterprise Application
   - Click **Add user/group**
   - Select the Entra ID groups that should have access to USAi
   - These groups will be synchronized via SCIM with their members

8. Set **Provisioning Status** to **On**
9. Click **Save** and wait for initial sync (typically 20-40 minutes)

#### For Okta

1. Navigate to your USAi application
2. Go to **Provisioning** tab
3. Click **Configure API Integration**
4. Check **Enable API integration**
5. Configure:
   ```
   Base URL: https://your-agency.usai.gov/realms/your-realm/scim/v2
   API Token: [Bearer token provided by USAi team]
   ```
6. Click **Test API Credentials**
7. Navigate to **To App** settings
8. Enable:
   - Create Users
   - Update User Attributes
   - Deactivate Users
   - Sync Password (optional)
9. Configure attribute mappings as needed
10. Navigate to **Provisioning** > **To App** and enable provisioning

### Step 2: Test SCIM Provisioning

#### Manual Testing with curl

```bash
# Set environment variables
export SCIM_BASE_URL="https://your-agency.usai.gov/realms/your-realm/scim/v2"
export SCIM_TOKEN="your-bearer-token"

# Test 1: Get Service Provider Configuration
curl -X GET "${SCIM_BASE_URL}/ServiceProviderConfig" \
  -H "Authorization: Bearer ${SCIM_TOKEN}" \
  -H "Accept: application/scim+json" | jq '.'

# Expected: Configuration showing supported features

# Test 2: List Users
curl -X GET "${SCIM_BASE_URL}/Users" \
  -H "Authorization: Bearer ${SCIM_TOKEN}" \
  -H "Accept: application/scim+json" | jq '.'

# Expected: List of provisioned users

# Test 3: Search for specific user
curl -X GET "${SCIM_BASE_URL}/Users?filter=userName eq \"user@agency.gov\"" \
  -H "Authorization: Bearer ${SCIM_TOKEN}" \
  -H "Accept: application/scim+json" | jq '.'

# Test 4: List Groups
curl -X GET "${SCIM_BASE_URL}/Groups" \
  -H "Authorization: Bearer ${SCIM_TOKEN}" \
  -H "Accept: application/scim+json" | jq '.'

# Expected: List of provisioned groups
```

#### Comprehensive SCIM Testing

For comprehensive SCIM testing including user creation, updates, group management, and cleanup, refer to the complete [SCIM Testing Guide](./SCIM-TESTING-GUIDE.md) included in this repository.

The testing guide includes:
- Full CRUD operations for users and groups
- Pagination and filtering tests
- Error handling scenarios
- Automated test scripts
- Cleanup procedures

#### IdP-based Testing

1. **Create a Test User** in your IdP
   - Assign the user to the USAi application
   - Wait 5-10 minutes for sync (or trigger manual sync)
   - Verify user appears in USAi Keycloak admin console

2. **Update Test User** attributes
   - Change name or email in IdP
   - Wait for sync
   - Verify changes reflected in USAi

3. **Remove Test User** from application
   - Unassign user from USAi in IdP
   - Wait for sync
   - Verify user is deactivated (not deleted) in USAi

4. **Test Group Provisioning** (if enabled)
   - Create a group in IdP
   - Assign users to the group
   - Assign group to USAi application
   - Verify group and members appear in USAi

### Group-Based Authorization Workflow

If you're using SCIM-only provisioning with group-based authorization, here's the recommended workflow:

#### Initial Setup
1. **Create Entra ID Groups** for different USAi roles/access levels:
   - Example: `USAi-Users`, `USAi-Admins`, `USAi-PowerUsers`
2. **Assign groups to the USAi Enterprise Application** in Entra
3. **Configure SCIM group provisioning** as described above
4. **Wait for initial SCIM sync** to complete

#### User Onboarding Process
1. **Add user to appropriate Entra ID group(s)**
   - User membership is synchronized to USAi via SCIM
   - User account is automatically created in USAi
   - Group memberships are reflected in USAi
2. **Map SCIM groups to USAi roles** (USAi team configures):
   - Entra group `USAi-Admins` → USAi Admin role
   - Entra group `USAi-Users` → USAi User role
3. **User can now sign in** via SSO
   - Authentication happens via OIDC/SAML
   - Authorization (roles) determined by SCIM group membership

#### User Offboarding Process
1. **Remove user from Entra ID group** or **unassign from application**
2. **SCIM sync automatically deactivates user** in USAi
3. **User loses access** on next authentication attempt

#### Role Changes
1. **Change user's group membership** in Entra ID
2. **SCIM sync updates** group membership in USAi
3. **User's roles/permissions automatically updated**

**Benefits of this approach:**
- No manual user management in USAi
- Authorization managed centrally in Entra ID
- Automatic compliance with organizational group policies
- Clear audit trail of all access changes

### SCIM Monitoring and Troubleshooting

#### Azure AD Provisioning Logs

1. Navigate to **Enterprise Applications** > **USAi** > **Provisioning logs**
2. Review sync cycles for:
   - Successfully provisioned users/groups
   - Failed operations
   - Skipped entries
3. Download logs for detailed analysis if needed

#### Okta Provisioning Logs

1. Navigate to **Reports** > **System Log**
2. Filter by:
   - Event Type: `user.provision.*`
   - Target: Your USAi application
3. Review successful and failed provisioning events

#### Common SCIM Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid or expired bearer token | Request new token from USAi team |
| 409 Conflict | User already exists | Check for duplicate emails or usernames |
| 400 Bad Request | Invalid attribute format | Verify attribute mapping matches SCIM schema |
| 404 Not Found | User/group doesn't exist | Ensure initial sync completed successfully |
| 429 Too Many Requests | Rate limiting | Reduce sync frequency or batch size |

## Attribute Mapping

Proper attribute mapping ensures user profiles are populated correctly in USAi.

### Required Attributes

| USAi Attribute | OIDC Claim | SAML Attribute | Description |
|----------------|------------|----------------|-------------|
| username | preferred_username or email | NameID or email | Unique identifier |
| email | email | email or mail | User's email address |
| firstName | given_name | firstName or givenName | User's first name |
| lastName | family_name | lastName or surname | User's last name |

### Optional Attributes

| USAi Attribute | OIDC Claim | SAML Attribute | Purpose |
|----------------|------------|----------------|---------|
| displayName | name | displayName | Full name for display |
| department | department | department | User's department/org |
| title | job_title | title | Job title |
| phone | phone_number | telephoneNumber | Contact number |
| organization | org_code | organization | Org code for multi-org agencies |

### Custom Attribute Mapping Example (Keycloak)

During the co-work session, we'll configure mappers like:

```json
{
  "name": "email",
  "protocol": "openid-connect",
  "protocolMapper": "oidc-usermodel-property-mapper",
  "config": {
    "user.attribute": "email",
    "claim.name": "email",
    "jsonType.label": "String",
    "id.token.claim": "true",
    "access.token.claim": "true",
    "userinfo.token.claim": "true"
  }
}
```

## Testing & Validation

### Pre-Production Testing Checklist

- [ ] Test user can successfully authenticate via SSO
- [ ] User profile attributes are correctly mapped
- [ ] User can access appropriate USAi features based on roles
- [ ] Logout functionality works correctly
- [ ] Session timeout behaves as expected
- [ ] SCIM provisioning creates users automatically (if configured)
- [ ] SCIM updates sync within expected timeframe
- [ ] SCIM deprovisioning deactivates users correctly
- [ ] Error messages are user-friendly and don't expose sensitive information

### Security Validation

- [ ] Verify HTTPS is enforced for all endpoints
- [ ] Confirm token/assertion signatures are validated
- [ ] Test session management and timeout policies
- [ ] Verify tokens are not leaked in URLs or logs
- [ ] Confirm proper logout terminates all sessions
- [ ] Test access with expired/invalid tokens (should fail)
- [ ] Verify SCIM API is only accessible with valid bearer token

### Production Rollout Checklist

- [ ] Document SSO configuration for your records
- [ ] Train helpdesk staff on SSO-related issues
- [ ] Prepare user communication about SSO rollout
- [ ] Set up monitoring for authentication errors
- [ ] Establish escalation path for SSO issues
- [ ] Schedule follow-up review after 30 days

## Troubleshooting

### Common OIDC Issues

#### "Invalid redirect URI" error

**Cause**: Redirect URI mismatch between IdP and Keycloak

**Solution**: 
1. Verify redirect URI in IdP exactly matches: `https://your-agency.usai.gov/realms/your-realm/broker/oidc/endpoint`
2. Check for trailing slashes or http vs https mismatches
3. Contact USAi team to verify Keycloak configuration

#### "Invalid client credentials" error

**Cause**: Incorrect Client ID or Secret

**Solution**:
1. Verify Client ID and Secret in IdP
2. Ensure secret hasn't expired (regenerate if needed)
3. Contact USAi team to update credentials in Keycloak

#### Users can authenticate but profile is incomplete

**Cause**: Missing or incorrect attribute mapping

**Solution**:
1. Verify IdP is sending required claims in ID token
2. Check token configuration in IdP includes email, name claims
3. Contact USAi team to verify mapper configuration in Keycloak

### Common SAML Issues

#### "Invalid SAML Response" error

**Cause**: Signature validation failure or expired assertion

**Solution**:
1. Verify system clocks are synchronized (NTP)
2. Check certificate hasn't expired
3. Ensure SAML response is signed correctly
4. Contact USAi team to verify certificate in Keycloak

#### "NameID not found" error

**Cause**: NameID format mismatch

**Solution**:
1. Verify NameID format in IdP matches Keycloak expectation
2. Common formats: Email, Persistent, Transient
3. Contact USAi team to align configuration

#### Logout doesn't work properly

**Cause**: Single Logout Service (SLS) not configured

**Solution**:
1. Verify SLS URL is configured in both IdP and Keycloak
2. Ensure logout requests are signed if required
3. Test logout from both USAi and IdP sides

### Common SCIM Issues

#### Provisioning sync fails with authentication error

**Cause**: Invalid or expired bearer token

**Solution**:
1. Contact USAi team to generate new bearer token
2. Update token in IdP provisioning configuration
3. Test connection after updating

#### Users provisioned but attributes are missing

**Cause**: Incorrect attribute mapping

**Solution**:
1. Review attribute mappings in IdP
2. Verify source attributes exist in IdP user profiles
3. Check SCIM logs for specific errors
4. Contact USAi team to verify Keycloak SCIM mapper configuration

#### Users not deprovisioning when removed from IdP

**Cause**: Deprovisioning not enabled or SCIM sync issue

**Solution**:
1. Verify deprovisioning is enabled in IdP
2. Check SCIM logs for failed delete/deactivate operations
3. Manually test with SCIM API to isolate issue
4. Contact USAi team if Keycloak-side issue suspected

### Getting Help

If you encounter issues not covered in this guide:

1. **Check logs**: Review authentication logs in your IdP
2. **Test connectivity**: Ensure firewall rules allow communication
3. **Gather details**: 
   - Error messages (screenshots or text)
   - Timestamp of the issue
   - User ID or email affected
   - Steps to reproduce
4. **Contact USAi Support**:
   - Email: partnerships@usai.gov
   - Include: Agency name, environment (test/prod), issue details
   - Response time: Within 1 business day

## Additional Resources

- [USAi Onboarding Guide](./README.md)
- [SCIM Testing Guide](./SCIM-TESTING-GUIDE.md)
- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OIDC Specification](https://openid.net/connect/)
- [SAML 2.0 Specification](http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [SCIM 2.0 Specification](https://tools.ietf.org/html/rfc7644)

## Appendix: Configuration Templates

### Microsoft Entra ID Streamlined Setup

For agencies using Microsoft Entra ID, USAi can automatically configure the integration on our side once you provide your credentials.

#### How It Works
```yaml
# What your agency creates in your Entra tenant
Application Registration:
  - Name: USAi - [Your Agency Name]
  - Redirect URI: https://your-agency.usai.gov/realms/your-realm/broker/oidc/endpoint
  - Client Type: Web
  - Client Secret: Generated by your admin
  - Token Claims: email, given_name, family_name, upn
  - API Permissions: User.Read, openid, profile, email
  - Admin Consent: Granted

# What you provide to USAi
Required Information:
  - Tenant ID: 12345678-1234-1234-1234-123456789abc
  - Client ID: (from your app registration)
  - Client Secret: (from your app registration)
  - Agency Name: Your Agency Name

# What USAi automatically configures
Keycloak Identity Provider:
  - Provider Type: OIDC
  - Authorization URL: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
  - Token URL: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
  - JWKS URL: https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys
  - Client credentials securely stored
  - Attribute mappers configured:
    * email → email
    * given_name → firstName
    * family_name → lastName
    * upn → username
  - User session settings
  - Trust email verification
  - Sync mode configuration
```

#### Benefits of Streamlined Setup
- ✅ You maintain full control of your Entra tenant
- ✅ Consistent configuration across all agencies
- ✅ Faster setup (typically completed within 1 business day)
- ✅ Reduced coordination time
- ✅ Automatic OIDC endpoint configuration
- ✅ Standardized attribute mapping
- ✅ Less room for configuration errors

---

### Azure AD OIDC Quick Reference (Manual Setup)

```yaml
# Application Registration
Client Type: Web
Redirect URI: https://your-agency.usai.gov/realms/your-realm/broker/oidc/endpoint

# Endpoints (replace {tenant} with your tenant ID)
Authorization: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
Token: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
JWKS: https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys
Issuer: https://login.microsoftonline.com/{tenant}/v2.0

# Token Claims
email: email
given_name: given_name  
family_name: family_name
```

### Okta OIDC Quick Reference

```yaml
# Application Settings
Application Type: Web Application
Grant Types: Authorization Code

# Endpoints (replace {org} with your Okta domain)
Authorization: https://{org}.okta.com/oauth2/default/v1/authorize
Token: https://{org}.okta.com/oauth2/default/v1/token
UserInfo: https://{org}.okta.com/oauth2/default/v1/userinfo
JWKS: https://{org}.okta.com/oauth2/default/v1/keys
Issuer: https://{org}.okta.com/oauth2/default

# Token Claims (default)
email: email
given_name: given_name
family_name: family_name
```

### SCIM Endpoint Reference

```yaml
# Base URL
Base: https://your-agency.usai.gov/realms/your-realm/scim/v2

# Endpoints
Service Provider Config: /ServiceProviderConfig
Resource Types: /ResourceTypes
Schemas: /Schemas
Users: /Users
Groups: /Groups

# Authentication
Method: Bearer Token
Header: Authorization: Bearer {token}

# Content Type
Request: application/scim+json
Response: application/scim+json
```

---

**Document Version**: 1.0  
**Last Updated**: November 10, 2025  
**Maintained By**: USAi Partnerships Team (partnerships@usai.gov)
