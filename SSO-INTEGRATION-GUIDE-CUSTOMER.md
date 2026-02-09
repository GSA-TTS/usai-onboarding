# USAi Single Sign-On (SSO) Setup Guide

Welcome! This guide walks you through connecting your agency's identity system to USAi so your users can sign in with their existing credentials. The USAi team handles all of the backend configuration — you just need to set things up on your side and share a few details with us.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Before You Begin](#before-you-begin)
3. [Choose Your Integration Path](#choose-your-integration-path)
4. [Microsoft Entra ID Setup (Recommended)](#microsoft-entra-id-setup-recommended)
5. [Okta Setup](#okta-setup)
6. [Other Identity Providers](#other-identity-providers)
7. [SAML Setup (If Required)](#saml-setup-if-required)
8. [Automated User Provisioning (SCIM)](#automated-user-provisioning-scim)
9. [What Information We Need From You](#what-information-we-need-from-you)
10. [How We Map User Attributes](#how-we-map-user-attributes)
11. [Testing Your Integration](#testing-your-integration)
12. [Going Live](#going-live)
13. [Troubleshooting](#troubleshooting)
14. [Getting Help](#getting-help)

---

## How It Works

USAi uses industry-standard protocols to connect securely with your agency's identity provider (IdP). Here's the high-level flow:

```
Your Agency's Identity Provider  →  USAi Authentication Service  →  USAi Application
                                            ↑
                                  Automated User Provisioning
                                     (optional via SCIM)
```

**In plain terms:**
- Your users sign in using their existing agency credentials (the same ones they use every day).
- Your identity provider verifies who they are and sends that confirmation to USAi.
- USAi grants access — no separate passwords or accounts needed.

We support two authentication protocols:
- **OIDC (OpenID Connect)** — Our recommended option. Modern, straightforward, and works great with cloud-based identity providers.
- **SAML 2.0** — A well-established standard, often used in legacy enterprise environments.

We also support **SCIM 2.0** for automated user provisioning, so users can be automatically created and deactivated based on your directory — no manual account management in USAi.

---

## Before You Begin

Please confirm you have the following:

- [ ] **Admin access** to your identity provider (e.g., Microsoft Entra ID, Okta, Ping Identity)
- [ ] **Authority to register a new application** in your identity provider
- [ ] **Authority to grant admin consent** for application permissions (if using Microsoft Entra ID)
- [ ] **Network access**: Ensure traffic is allowed to `https://auth.usai.gov` (see firewall requirements in the [Onboarding Guide](./README.md))

The USAi team will provide you with:
- Your agency's dedicated **realm name** (used in redirect URLs)
- A **SCIM bearer token** (if using automated provisioning)
- A **scheduled co-work session** (if needed) to finalize configuration together

---

## Choose Your Integration Path

| Approach | Best For | Complexity |
|----------|----------|------------|
| **OIDC** (Recommended) | Microsoft Entra ID, Okta, and modern cloud IdPs | Low |
| **SAML** | Legacy enterprise SSO infrastructure or specific compliance requirements | Medium |
| **Hybrid** | Agencies with multiple user populations on different protocols | Varies |

Most agencies choose **OIDC**. If you're unsure, we recommend starting there.

---

## Microsoft Entra ID Setup (Recommended)

If your agency uses Microsoft Entra ID (formerly Azure AD), this is the fastest path. You create the app registration in your tenant — you maintain full control — and then share a few details with us. We handle the rest.

### Step 1: Find Your Tenant ID

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **Overview**
3. Copy the **Tenant ID** (a GUID like `12345678-1234-1234-1234-123456789abc`)

### Step 2: Create the App Registration

1. In the Azure Portal, go to **Azure Active Directory** → **App registrations**
2. Click **New registration**
3. Fill in the details:

   | Field | Value |
   |-------|-------|
   | **Name** | `USAi - [Your Agency Name]` |
   | **Supported account types** | Accounts in this organizational directory only |
   | **Redirect URI** | Platform: **Web** — URI: `https://auth.usai.gov/realms/your-realm/broker/oidc/endpoint` |

   > ⚠️ Replace `your-realm` with the realm name provided by the USAi team.

4. Click **Register**
5. On the app's overview page, copy the **Application (client) ID**

### Step 3: Create a Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description (e.g., "USAi SSO") and set expiration to **24 months** (recommended)
4. Click **Add**
5. **Immediately copy the secret value** — you won't be able to see it again

### Step 4: Configure Token Claims

1. Go to **Token configuration**
2. Click **Add optional claim** and add these for the **ID token**:
   - `email`
   - `family_name`
   - `given_name`
   - `upn`

### Step 5: Set API Permissions

1. Go to **API permissions**
2. Ensure the following permissions are present (add them if not):
   - **Microsoft Graph** → `User.Read` (Delegated)
   - **OpenID permissions**: `openid`, `profile`, `email`
3. Click **Grant admin consent for [Your Organization]**

### Step 6: Send Us Your Details

Email **partnerships@usai.gov** with:

```
Subject: Microsoft Entra OIDC Configuration - [Your Agency Name]

Tenant ID: [your-tenant-id]
Client ID: [your-client-id]
Client Secret: [your-client-secret]
Agency Name: [your-agency-name]
Technical Contact: [name and email]
```

### What Happens Next

Once we receive your information, the USAi team will:

1. Configure the connection on our side using your Tenant ID and credentials
2. Set up proper endpoint URLs automatically
3. Map your user attributes (email, first name, last name, etc.)
4. Enable the integration and notify you when it's ready to test

**Typical turnaround: 1 business day.**

> 💡 **Prefer a hands-on session?** If you'd rather configure the integration together in real time, let us know and we'll set up a co-work session.

---

## Okta Setup

### Step 1: Create the App Integration

1. In the Okta Admin Console, go to **Applications** → **Create App Integration**
2. Select **OIDC - OpenID Connect** and **Web Application**
3. Configure the application:

   | Field | Value |
   |-------|-------|
   | **App integration name** | `USAi - [Your Agency Name]` |
   | **Grant type** | Authorization Code |
   | **Sign-in redirect URI** | `https://auth.usai.gov/realms/your-realm/broker/oidc/endpoint` |
   | **Sign-out redirect URI** | `https://auth.usai.gov/realms/your-realm/broker/oidc/endpoint` |

   > ⚠️ Replace `your-realm` with the realm name provided by the USAi team.

4. Click **Save**
5. Copy the **Client ID** and **Client Secret**

### Step 2: Send Us Your Details

Email **partnerships@usai.gov** with:

```
Subject: Okta OIDC Configuration - [Your Agency Name]

Client ID: [your-client-id]
Client Secret: [your-client-secret]
Okta Domain: [your-org].okta.com
Agency Name: [your-agency-name]
Technical Contact: [name and email]
```

---

## Other Identity Providers

If you use a different OIDC-compatible identity provider (Ping Identity, Auth0, etc.), we can work with that too. Please gather the following from your IdP and send them to us:

- **Authorization endpoint URL**
- **Token endpoint URL**
- **UserInfo endpoint URL**
- **JWKS URI** (for token validation)
- **Issuer URL**
- **Client ID and Client Secret**

Email these details to **partnerships@usai.gov** and we'll configure the integration on our side.

---

## SAML Setup (If Required)

If your agency requires SAML instead of OIDC, here's how to set it up.

### Step 1: Request SAML Metadata From USAi

Contact **partnerships@usai.gov** and we'll provide you with:
- **Entity ID**: `https://auth.usai.gov/realms/your-realm`
- **ACS (Assertion Consumer Service) URL**: `https://auth.usai.gov/realms/your-realm/broker/saml/endpoint`
- **SAML Metadata XML file**

### Step 2: Register USAi in Your Identity Provider

#### Microsoft Entra ID

1. Go to **Enterprise Applications** → **New application** → **Create your own application**
2. Select **Integrate any other application you don't find in the gallery**
3. Name it `USAi - [Your Agency Name]`
4. Navigate to **Single sign-on** → **SAML**
5. Click **Upload metadata file** and upload the metadata XML we provided
6. Configure **User Attributes & Claims**:

   | Claim | Source Attribute |
   |-------|-----------------|
   | Unique User Identifier (NameID) | `user.userprincipalname` |
   | Email | `user.mail` |
   | First Name | `user.givenname` |
   | Last Name | `user.surname` |

7. Download **Federation Metadata XML** from the SAML Signing Certificate section
8. Send the Federation Metadata XML to **partnerships@usai.gov**

#### Okta

1. Go to **Applications** → **Create App Integration** → **SAML 2.0**
2. Set the app name to `USAi - [Your Agency Name]`
3. Configure SAML settings:

   | Field | Value |
   |-------|-------|
   | **Single sign-on URL** | `https://auth.usai.gov/realms/your-realm/broker/saml/endpoint` |
   | **Audience URI (SP Entity ID)** | `https://auth.usai.gov/realms/your-realm` |
   | **Name ID format** | EmailAddress |
   | **Application username** | Email |

4. Add attribute statements:

   | Name | Value |
   |------|-------|
   | `email` | `user.email` |
   | `firstName` | `user.firstName` |
   | `lastName` | `user.lastName` |

5. Complete the wizard, then go to the **Sign On** tab
6. Download or copy the SAML metadata and send it to **partnerships@usai.gov**

---

## Automated User Provisioning (SCIM)

SCIM provisioning lets you automatically manage user accounts in USAi from your identity provider. When someone joins your team, they get access. When they leave, access is revoked — automatically.

### Why Use SCIM?

| Benefit | Description |
|---------|-------------|
| **Automatic onboarding** | Users are created in USAi when added to your directory |
| **Automatic offboarding** | Users are deactivated when removed — no manual cleanup |
| **Real-time sync** | Name changes, role updates, and other edits are reflected automatically |
| **Group-based access** | Assign USAi roles by managing group memberships in your IdP |
| **Audit trail** | All provisioning events are logged in your identity provider |

### With vs. Without SCIM

| | With SCIM | Without SCIM (Default) |
|---|-----------|----------------------|
| **User creation** | Automatic — managed in your IdP | Automatic on first sign-in (Just-in-Time) |
| **Access control** | Only users you provision can sign in | Any user who can authenticate via SSO can create an account |
| **User removal** | Automatic when removed from your IdP | Manual — must be removed from USAi separately |
| **Group sync** | Yes — groups map to USAi roles | No — roles managed manually in USAi |

> **Important:** SCIM and Just-in-Time provisioning cannot be used simultaneously. If you enable SCIM, users **must** be provisioned via SCIM before they can sign in.

### Setting Up SCIM

Tell us you'd like SCIM enabled, and we'll provide:
- **SCIM Base URL**: `https://auth.usai.gov/realms/your-realm/scim/v2`
- **Bearer Token**: For authenticating SCIM requests

#### Microsoft Entra ID

1. In the Azure Portal, go to your **USAi Enterprise Application**
2. Navigate to **Provisioning** → **Get started**
3. Set **Provisioning Mode** to **Automatic**
4. Under **Admin Credentials**, enter:

   | Field | Value |
   |-------|-------|
   | **Tenant URL** | `https://auth.usai.gov/realms/your-realm/scim/v2` |
   | **Secret Token** | The bearer token we provided |

5. Click **Test Connection** — you should see a success message
6. Under **Mappings**, verify:

   **User mappings:**
   | Azure AD Attribute | SCIM Attribute |
   |-------------------|----------------|
   | `userName` | `userName` |
   | `mail` | `emails[type eq "work"].value` |
   | `givenName` | `name.givenName` |
   | `surname` | `name.familyName` |
   | `displayName` | `displayName` |
   | `Switch([IsSoftDeleted]...)` | `active` |

   **Group mappings** (if using group-based access):
   | Azure AD Attribute | SCIM Attribute |
   |-------------------|----------------|
   | `displayName` | `displayName` |
   | `members` | `members` |

7. Under **Settings** → **Scope**, select **Sync only assigned users and groups**
8. If using groups: go to **Users and groups**, click **Add user/group**, and select the groups that should have USAi access
9. Set **Provisioning Status** to **On** and click **Save**
10. Initial sync typically takes 20–40 minutes

#### Okta

1. In your USAi application, go to the **Provisioning** tab
2. Click **Configure API Integration** and check **Enable API integration**
3. Enter:

   | Field | Value |
   |-------|-------|
   | **Base URL** | `https://auth.usai.gov/realms/your-realm/scim/v2` |
   | **API Token** | The bearer token we provided |

4. Click **Test API Credentials** — you should see a success message
5. Under **To App**, enable:
   - Create Users
   - Update User Attributes
   - Deactivate Users
6. Configure attribute mappings as needed
7. Save and enable provisioning

### Managing Users With SCIM Groups

If you're using SCIM with group-based access, here's the recommended workflow:

**Initial Setup:**
1. Create groups in your IdP for different USAi access levels (e.g., `USAi-Users`, `USAi-Admins`)
2. Assign those groups to the USAi application
3. Let us know which groups should map to which USAi roles
4. Wait for the initial SCIM sync to complete

**Adding a User:**
1. Add the user to the appropriate group(s) in your IdP
2. SCIM automatically provisions the user in USAi
3. The user can now sign in via SSO

**Removing a User:**
1. Remove the user from the group or unassign them from the application
2. SCIM automatically deactivates the user in USAi
3. The user loses access on their next sign-in attempt

**Changing Roles:**
1. Move the user to a different group in your IdP
2. SCIM syncs the updated membership
3. The user's permissions update automatically

---

## What Information We Need From You

Here's a summary of everything we'll need, depending on your setup:

### For OIDC (All Providers)

| Item | Required? |
|------|-----------|
| Identity provider name (e.g., "Entra ID", "Okta") | ✅ Yes |
| Client ID | ✅ Yes |
| Client Secret | ✅ Yes |
| Tenant ID (Entra) or Okta domain | ✅ Yes |
| Agency name | ✅ Yes |
| Technical contact (name + email) | ✅ Yes |

### For SAML

| Item | Required? |
|------|-----------|
| Federation Metadata XML from your IdP | ✅ Yes |
| Agency name | ✅ Yes |
| Technical contact (name + email) | ✅ Yes |

### For SCIM

| Item | Required? |
|------|-----------|
| Confirmation that you want SCIM enabled | ✅ Yes |
| Whether you want group sync enabled | ✅ Yes |
| List of IdP groups → USAi role mappings | If using groups |

---

## How We Map User Attributes

When your users sign in, their profile information flows from your identity provider into USAi. Here's what we map:

### Required Attributes

| What USAi Needs | What Your IdP Sends (OIDC) | What Your IdP Sends (SAML) |
|-----------------|---------------------------|---------------------------|
| Username | `preferred_username` or `email` | NameID or `email` |
| Email address | `email` | `email` or `mail` |
| First name | `given_name` | `firstName` or `givenName` |
| Last name | `family_name` | `lastName` or `surname` |

### Optional Attributes

| What USAi Needs | What Your IdP Sends (OIDC) | What Your IdP Sends (SAML) |
|-----------------|---------------------------|---------------------------|
| Display name | `name` | `displayName` |
| Department | `department` | `department` |
| Job title | `job_title` | `title` |
| Phone number | `phone_number` | `telephoneNumber` |
| Organization code | `org_code` | `organization` |

> 💡 If your IdP uses different attribute names, let us know and we'll adjust our mapping to match.

---

## Testing Your Integration

Once we've confirmed the configuration is complete, here's how to verify everything is working:

### SSO Authentication Test

1. Open your browser and navigate to `https://auth.usai.gov`
2. Click the SSO button for your agency
3. You should be redirected to your identity provider's login page
4. Sign in with your agency credentials
5. After successful authentication, you should be redirected back to USAi
6. Verify your name and email appear correctly in your USAi profile

### SCIM Provisioning Test (If Enabled)

1. **Create a test user** in your IdP and assign them to the USAi application
2. Wait 5–10 minutes (or trigger a manual sync)
3. Confirm with us that the user appeared in USAi
4. **Update the test user's** name or email in your IdP
5. Wait for sync and confirm the change was reflected
6. **Remove the test user** from the application
7. Confirm the user was deactivated in USAi

### Pre-Go-Live Checklist

- [ ] Test user can successfully sign in via SSO
- [ ] User profile (name, email) appears correctly after sign-in
- [ ] User can access the appropriate USAi features
- [ ] Logout works correctly from both USAi and your IdP
- [ ] SCIM creates new users automatically (if enabled)
- [ ] SCIM deactivates removed users (if enabled)
- [ ] SCIM syncs group memberships correctly (if enabled)

---

## Going Live

Before rolling out SSO to all your users:

- [ ] Complete all testing from the checklist above
- [ ] Document the SSO configuration for your internal records
- [ ] Brief your helpdesk team on SSO-related issues and how to escalate
- [ ] Communicate the change to your users (when it takes effect, what to expect)
- [ ] Set up monitoring for authentication errors (in your IdP logs)
- [ ] Confirm an escalation path with the USAi team for urgent issues
- [ ] Schedule a follow-up review 30 days after go-live

---

## Troubleshooting

### "Invalid redirect URI" Error

**What it means:** The redirect URL in your app registration doesn't match what USAi expects.

**How to fix it:**
1. In your identity provider, verify the redirect URI is exactly: `https://auth.usai.gov/realms/your-realm/broker/oidc/endpoint`
2. Check for common mistakes: trailing slashes, `http` instead of `https`, or a typo in the realm name
3. If everything looks correct on your side, contact us — there may be a mismatch on ours

### "Invalid client credentials" Error

**What it means:** The Client ID or Client Secret doesn't match.

**How to fix it:**
1. Verify the Client ID and Secret in your identity provider
2. Check whether the secret has expired — if so, generate a new one and send it to us
3. Contact us to confirm we have the correct credentials

### Users Can Sign In But Their Profile Is Incomplete

**What it means:** Your identity provider isn't sending all the required information (name, email, etc.).

**How to fix it:**
1. Verify your token or claims configuration includes `email`, `given_name`, and `family_name`
2. For Entra ID: check the optional claims in **Token configuration**
3. For Okta: check attribute statements in your app configuration
4. Contact us if the issue persists — we can check the data we're receiving

### "Invalid SAML Response" Error (SAML Only)

**What it means:** The SAML assertion failed validation.

**How to fix it:**
1. Ensure your server's clock is synchronized (SAML assertions are time-sensitive)
2. Check whether your signing certificate has expired
3. Contact us — we can check the signature validation on our side

### Logout Doesn't Work Properly

**What it means:** Signing out of USAi doesn't sign you out of your identity provider (or vice versa).

**How to fix it:**
1. Verify that logout URLs are configured in your app registration
2. Contact us to confirm Single Logout is enabled on our side

### SCIM: Provisioning Fails With Authentication Error

**What it means:** The bearer token may be invalid or expired.

**How to fix it:**
1. Contact us to request a new bearer token
2. Update the token in your identity provider's provisioning configuration
3. Click **Test Connection** again to verify

### SCIM: Users Aren't Being Deactivated When Removed

**What it means:** Deprovisioning may not be enabled in your IdP.

**How to fix it:**
1. In your IdP, verify that deprovisioning/deactivation is turned on for the USAi app
2. Check your provisioning logs for any failed operations
3. Contact us if the issue appears to be on our side

### Common SCIM Error Codes

| Error | What It Means | What To Do |
|-------|--------------|------------|
| `401 Unauthorized` | Invalid or expired token | Request a new token from us |
| `409 Conflict` | User already exists | Check for duplicate emails or usernames |
| `400 Bad Request` | Attribute format issue | Verify your attribute mappings |
| `404 Not Found` | User/group doesn't exist | Ensure the initial sync completed |
| `429 Too Many Requests` | Rate limiting triggered | Reduce sync frequency or batch size |

---

## Getting Help

If you run into anything not covered here, we're happy to help.

**Before reaching out, please gather:**
- Error messages (screenshots or text)
- Timestamp of when the issue occurred
- Affected user's email address
- Steps to reproduce the issue

**Contact us:**
- 📧 **Email**: partnerships@usai.gov
- Include: Your agency name, environment (test or production), and issue details
- **Response time**: Within 1 business day

---

## Quick Reference

### OIDC Redirect URI
```
https://auth.usai.gov/realms/your-realm/broker/oidc/endpoint
```

### SAML ACS URL
```
https://auth.usai.gov/realms/your-realm/broker/saml/endpoint
```

### SAML Entity ID
```
https://auth.usai.gov/realms/your-realm
```

### SCIM Base URL
```
https://auth.usai.gov/realms/your-realm/scim/v2
```

> ⚠️ In all URLs above, replace `your-realm` with the realm name provided by the USAi team.

---

**Document Version**: 1.1  
**Last Updated**: February 9, 2026  
**Maintained By**: USAi Partnerships Team (partnerships@usai.gov)