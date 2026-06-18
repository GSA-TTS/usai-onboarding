# USAi SCIM Provisioning Guide

This guide is the authoritative SCIM setup guide for USAi. It explains how SCIM
provisioning works, what your agency controls in Microsoft Entra ID or Okta, how
to handle existing USAi users, and how to choose provisioning scope, group
ownership, and deprovisioning behavior.

For the broader SSO setup, including OIDC and SAML authentication, see the
[USAi Single Sign-On Setup Guide](./SSO-INTEGRATION-GUIDE.md).

SCIM is separate from single sign-on. Users still authenticate through your
identity provider using OIDC or SAML. SCIM manages user records, user attributes,
groups, group membership, and active/inactive state in USAi.

---

## End-To-End Flow

```text
Microsoft Entra ID or Okta provisioning service
  -> USAi SCIM endpoint
  -> USAi authentication service
  -> USAi user and group records
```

In this model, your identity provider is the SCIM client and USAi is the SCIM
service provider.

Your identity provider sends provisioning requests to USAi. USAi does not push
users or groups back to your identity provider.

---

## SCIM Endpoint And Authentication

The USAi team will provide:

| Item | Value |
|------|-------|
| **SCIM Base URL / Tenant URL** | `https://auth.usai.gov/realms/your-realm/scim/v2` |
| **Authentication** | Bearer token |
| **Token field in Entra** | Secret Token |
| **Token field in Okta** | API Token |

Replace `your-realm` with the realm name provided by the USAi team.

---

## What SCIM Can Manage

SCIM can manage these objects in USAi:

- Users
- User profile attributes, such as username, email, first name, and last name
- Groups
- Group membership
- User active or inactive state

Authentication still happens through SSO. A provisioned user signs in with the
same agency credentials they use today.

---

## Existing USAi Users

If your agency already has users who signed in through OIDC or SAML before SCIM
is enabled, those users already have USAi accounts.

Adding a SCIM integration does **not** automatically delete, disable, or recreate
those existing users.

What happens next depends on provisioning scope and mappings:

- If an existing user is assigned to the USAi provisioning application, your IdP
  can match and update that existing USAi user.
- If an existing user is not assigned to the USAi provisioning application, your
  IdP normally does not send create or update requests for that user.
- If your IdP is configured to deprovision out-of-scope users, it may send a
  disable or delete action for users it manages.

Before turning provisioning on, decide whether SCIM should manage all existing
USAi users or only a smaller set of users and groups.

---

## SCIM And Just-In-Time User Creation

SCIM and Just-in-Time user creation are different provisioning models.

| Model | What creates the user? | When is the user created? |
|-------|-------------------------|----------------------------|
| Just-in-Time user creation | USAi during SSO sign-in | First successful SSO sign-in |
| SCIM provisioning | Your identity provider | Before the user signs in |

If your agency chooses SCIM-only provisioning, users must be provisioned by SCIM
before they can sign in. If a user can authenticate through SSO but has not been
provisioned, they may not receive access until the SCIM sync creates or updates
their USAi account and required group membership.

---

## Microsoft Entra ID Setup

### Step 1: Create Or Select The Provisioning Enterprise Application

You will usually need a separate Enterprise Application for SCIM provisioning.
If you set up OIDC earlier using an App Registration, the corresponding
Enterprise Application may have the **Provisioning** option grayed out. That is a
Microsoft platform limitation for App Registration-based Enterprise Apps.

Create the provisioning Enterprise Application:

1. Sign in to the [Azure Portal](https://portal.azure.com).
2. Navigate to **Azure Active Directory** → **Enterprise applications**.
3. Click **+ New application**.
4. Click **+ Create your own application**.
5. Enter a name such as `USAi Provisioning - [Your Agency Name]`.
6. Select **Integrate any other application you don't find in the gallery (Non-gallery)**.
7. Click **Create**.

If you already have a non-gallery Enterprise Application where **Provisioning**
is not grayed out, you can use that application instead.

### Step 2: Enable Provisioning

1. In the USAi provisioning Enterprise Application, click **Provisioning**.
2. If **Provisioning** is grayed out, create a non-gallery Enterprise Application
   as described above.
3. Click **Get started**.
4. Set **Provisioning Mode** to **Automatic**.

### Step 3: Enter Admin Credentials

Under **Admin Credentials**, enter:

| Field | Value |
|-------|-------|
| **Tenant URL** | `https://auth.usai.gov/realms/your-realm/scim/v2` |
| **Secret Token** | The bearer token provided by the USAi team |

Click **Test Connection**. Entra should report that the supplied credentials are
authorized to enable provisioning.

If the test fails, check:

- The URL has no trailing slash and no typo.
- `your-realm` was replaced with the realm name provided by USAi.
- The bearer token was copied completely, without leading or trailing spaces.
- Your network/firewall allows outbound HTTPS traffic to `auth.usai.gov`.

Click **Save** before continuing.

### Step 4: Configure User Attribute Mappings

1. Open the USAi provisioning Enterprise Application.
2. Open **Provisioning**.
3. Select **Edit provisioning** if the provisioning overview page is shown.
4. Expand **Mappings**.
5. Open **Provision Azure Active Directory Users**. Microsoft Entra may still use
   this legacy label in the provisioning UI.
6. Set **Enabled** to **Yes**.
7. Configure these mappings. Remove or adjust default mappings that conflict with
   this list.

| Microsoft Entra attribute | USAi SCIM attribute | Mapping type |
|---------------------------|---------------------|--------------|
| `userPrincipalName` | `userName` | Direct |
| `mail` | `emails[type eq "work"].value` | Direct |
| `givenName` | `name.givenName` | Direct |
| `surname` | `name.familyName` | Direct |
| `displayName` | `displayName` | Direct |
| `Switch([IsSoftDeleted], , "False", "True", "True", "False")` | `active` | Expression |

The `active` mapping controls whether the USAi user account is enabled or
disabled.

To configure the `active` mapping:

1. Click the `active` mapping, or click **Add New Mapping** if it does not exist.
2. Set **Mapping type** to **Expression**.
3. Enter exactly:

   ```text
   Switch([IsSoftDeleted], , "False", "True", "True", "False")
   ```

4. Set **Target attribute** to `active`.
5. Click **OK**.

### Step 5: Choose Target Object Actions For Users

In **Target object actions**, confirm the actions match your agency's intended
behavior:

- **Create** creates users in USAi.
- **Update** updates user attributes and can send `active = false`.
- **Delete** allows hard-delete requests only if your agency intentionally chooses
  hard deletion.

For most agencies, soft deactivation with `active = false` is safer than hard
deletion because it keeps the account record available for audit and support.

**Update must be enabled** for Entra to send `active = false` soft-deprovisioning
updates.

### Step 6: Configure Group Provisioning

If you want group-based access control, enable group provisioning:

1. Open the USAi provisioning Enterprise Application.
2. Open **Provisioning**.
3. Select **Edit provisioning** if needed.
4. Expand **Mappings**.
5. Open **Provision Azure Active Directory Groups**. Microsoft Entra may still
   use this legacy label in the provisioning UI.
6. Set **Enabled** to **Yes**.
7. Configure these mappings:

| Microsoft Entra attribute | USAi SCIM attribute | Mapping type |
|---------------------------|---------------------|--------------|
| `displayName` | `displayName` | Direct |
| `members` | `members` | Direct |

In **Target object actions**, confirm Create, Update, and Delete match your
agency's intended behavior. Enable Delete only if your agency intentionally
chooses hard-delete behavior for groups.

### Step 7: Set Provisioning Scope

Provisioning scope controls which users and groups Entra sends to USAi.

For most agencies, USAi recommends:

```text
Sync only assigned users and groups
```

To configure scope:

1. Open the USAi provisioning Enterprise Application.
2. Open **Provisioning**.
3. Open **Settings**.
4. Set **Scope** to **Sync only assigned users and groups**.
5. Save the setting.

If a user already exists in USAi but is not assigned to the provisioning
application, Entra normally does not create or update that user. If the user was
previously managed by this provisioning application and then moves out of scope,
the result depends on the deprovisioning behavior configured in Entra.

### Step 8: Assign Users And Groups

Assign the users or groups that should be provisioned:

1. Open the USAi provisioning Enterprise Application.
2. Open **Users and groups**.
3. Select **Add user/group**.
4. Assign the Entra groups or individual users that should have USAi access.

USAi recommends assigning groups rather than individual users. Group assignment
lets your agency manage USAi access by adding or removing users from Entra
groups.

### Step 9: Start Provisioning

1. Go back to **Provisioning**.
2. Set **Provisioning Status** to **On**.
3. Click **Save**.

The initial provisioning cycle typically takes 20–40 minutes, depending on the
number of users and groups.

### Step 10: Verify The Initial Sync

1. Stay on the **Provisioning** page and wait for the initial cycle to complete.
2. Open **Provisioning logs**.
3. Review results:
   - **Success** means users or groups were created or updated in USAi.
   - **Failure** means the error details need review.
   - **Skipped** often means the user or group did not meet scope requirements.
4. Verify assigned users were created or updated.
5. Verify assigned groups were created or updated, if group provisioning is enabled.
6. Verify user attributes, such as email and name, were sent correctly.
7. Let the USAi team know when the initial sync is complete so they can confirm
   users and groups appeared correctly in USAi.

### Step 11: Monitor Ongoing Provisioning

After the initial sync, Entra runs incremental syncs approximately every 40
minutes.

Monitor these locations:

- **Provisioning logs**: Enterprise Applications → USAi → Provisioning logs
- **Audit logs**: Azure Active Directory → Audit logs, filtered by
  **Service: Account Provisioning**
- **Alerts**: Configure a notification email under Provisioning → Settings so
  Azure can notify you if provisioning enters quarantine after repeated failures.

---

## Okta Setup

1. In your USAi application, open the **Provisioning** tab.
2. Click **Configure API Integration**.
3. Check **Enable API integration**.
4. Enter:

   | Field | Value |
   |-------|-------|
   | **Base URL** | `https://auth.usai.gov/realms/your-realm/scim/v2` |
   | **API Token** | The bearer token provided by the USAi team |

5. Click **Test API Credentials**.
6. Under **To App**, enable the actions your agency intends to use:
   - Create Users
   - Update User Attributes
   - Deactivate Users
7. Configure attribute mappings as needed.
8. Save and enable provisioning.

---

## Choosing A Group Model

Before enabling group provisioning, decide which system owns group membership.

Recommended model:

- Your identity provider owns USAi access groups.
- Agency admins add or remove users from those groups in the identity provider.
- The identity provider syncs those groups and memberships to USAi through SCIM.
- USAi maps synced groups to the appropriate USAi roles.

Avoid creating disconnected duplicate groups in your identity provider and USAi.
If group names do not line up, agree on the mapping with the USAi team before
turning provisioning on.

---

## Deprovisioning Decisions

Before enabling SCIM, decide what should happen when a user is removed from USAi
provisioning scope.

Common options:

- Leave the existing USAi account unchanged.
- Remove the user only from SCIM-managed groups.
- Disable the user by sending `active = false`.
- Delete the user by sending a SCIM delete request.

For most agencies, disabling users is safer than deleting them because it keeps
the account record available for audit and support.

---

## Managing Users With SCIM Groups

### Initial Setup

1. Create groups in your identity provider for different USAi access levels, such
   as `USAi-Users`, `USAi-Admins`, or `USAi-PowerUsers`.
2. Assign those groups to the USAi provisioning application.
3. Let the USAi team know which groups should map to which USAi roles.
4. Wait for the initial SCIM sync to complete.

### Adding A User

1. Add the user to the appropriate group or groups in your identity provider.
2. SCIM provisions or updates the user in USAi.
3. The user can sign in through SSO after the required user record and group
   membership exist in USAi.

### Removing A User

1. Remove the user from the group or unassign them from the provisioning
   application.
2. SCIM applies the deprovisioning behavior your agency configured, usually either
   removing the user from SCIM-managed groups or sending `active = false` to
   deactivate the user.
3. If the user is deactivated or no longer has required group membership, they
   lose access on their next sign-in attempt.

### Changing Roles

1. Move the user to a different group in your identity provider.
2. SCIM syncs the updated membership.
3. The user's permissions update based on the USAi role mapping for those groups.

---

## Testing

Before turning provisioning on for a broad user population, test with one user
and one group.

1. Assign a test user or test group to the USAi provisioning application.
2. Open **Provisioning**.
3. Use **Provision on demand** if available, or turn provisioning on and wait for
   the next cycle.
4. Open **Provisioning logs**.
5. Confirm the user action succeeded.
6. Confirm the group action succeeded, if group provisioning is enabled.
7. Confirm the USAi team sees the user and group correctly in USAi.
8. Update the test user's name or email in the identity provider and confirm the
   change syncs.
9. Remove the test user from the assigned group or application.
10. Confirm the deprovisioning behavior matches the decision your agency made.

---

## Troubleshooting

### Provisioning Fails With Authentication Error

The bearer token may be invalid or expired.

To fix it:

1. Contact the USAi team to request a new bearer token.
2. Update the token in your identity provider's provisioning configuration.
3. Test the connection again.

### Users Are Not Deactivated When Removed

Deprovisioning may not be enabled, or the configured deprovisioning behavior may
not be what you intended.

To fix it:

1. Verify the user was managed by the USAi provisioning application.
2. Verify the user moved out of provisioning scope or was removed from the
   assigned group/application.
3. Verify **Update** is enabled in Target Object Actions if you expect
   `active = false` soft deactivation.
4. Check provisioning logs for failed or skipped operations.
5. Confirm the expected deprovisioning behavior with the USAi team.

### Common SCIM Error Codes

| Error | What It Means | What To Do |
|-------|--------------|------------|
| `401 Unauthorized` | Invalid or expired token | Request a new token from USAi |
| `409 Conflict` | User already exists | Check for duplicate emails or usernames |
| `400 Bad Request` | Attribute format issue | Verify attribute mappings |
| `404 Not Found` | User or group does not exist | Ensure the initial sync completed |
| `429 Too Many Requests` | Rate limit triggered | Reduce sync frequency or batch size |

---

## Information To Send The USAi Team

Before a co-work session, send:

- Agency name.
- USAi realm name, if already provided.
- Whether SCIM should manage users, groups, or both.
- Whether SCIM should manage all existing USAi users or only newly assigned users.
- Identity provider groups that should be provisioned.
- Intended mapping from identity provider groups to USAi roles.
- Intended deprovisioning behavior.
- Technical contact who can view provisioning logs during testing.
