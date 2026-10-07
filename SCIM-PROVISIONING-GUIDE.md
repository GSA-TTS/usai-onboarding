# USAi SCIM Provisioning Guide

This guide explains how SCIM provisioning works with USAi, what your agency
controls in Microsoft Entra ID or Okta, and what happens to existing USAi users when
SCIM is introduced.

This guide supplements the full
[USAi Single Sign-On Setup Guide](./SSO-INTEGRATION-GUIDE-CUSTOMER.md). Use
that guide for the complete SSO and SCIM connector setup steps.

SCIM is separate from single sign-on. Users still authenticate through your
identity provider using OIDC or SAML. SCIM manages user records, attributes, and
group membership in USAi.

## Okta setup

Start with Okta's
[Create your private integration in Okta](https://developer.okta.com/docs/guides/scim-provisioning-integration-connect/main/#create-your-private-integration-in-okta)
guide, then use the [USAi Okta SCIM connector settings](./SSO-INTEGRATION-GUIDE-CUSTOMER.md#okta-scim-connector-setup).

If USAi supplied a SCIM client ID and secret, your integration needs
**OAuth2 → Client Credentials**. Some Okta test templates instead ask for a
bearer token. Do not paste a client secret into that field. Confirm the available
authentication options with your Okta administrator; they can vary by connector
and Okta environment.

The sections below that name Microsoft Entra describe Entra-specific screens.
Use the linked Okta instructions for the Okta setup screens.

## End-To-End Flow

```
Microsoft Entra ID or Okta provisioning service
  -> USAi SCIM endpoint
  -> USAi authentication service
  -> USAi user and group records
```

Your identity provider is the SCIM client. USAi is the SCIM service provider.

Your identity provider sends provisioning requests to USAi. USAi does not push
users or groups to your identity provider.

## What SCIM Can Manage

SCIM can manage these objects in USAi:

- Users
- User profile attributes, such as username, email, first name, and last name
- Groups
- Group membership
- User active or inactive state

Authentication still happens through SSO. A provisioned user signs in with the
same agency credentials they use today.

## Existing USAi Users

If your agency already has users who signed in through OIDC or SAML before SCIM
is enabled, those users already have USAi accounts.

Adding a SCIM integration does not automatically delete, disable, or recreate
those existing users.

What happens next depends on the Entra provisioning scope and mappings:

- If an existing user is assigned to the USAi provisioning application, Entra can
  match and update that existing USAi user.
- If an existing user is not assigned to the USAi provisioning application, Entra
  normally does not send create or update requests for that user.
- If Entra is configured to deprovision out-of-scope users, Entra may send a
  disable or delete action for users it manages.

Before turning provisioning on, decide whether SCIM should manage all existing
USAi users or only a smaller set of users and groups.

## SCIM And Just-In-Time User Creation

SCIM and Just-in-Time user creation are different provisioning models.

- With Just-in-Time user creation, USAi creates the user account during the
  first successful SSO sign-in.
- With SCIM provisioning, Entra creates or updates the user account before the
  user signs in.

If your agency chooses SCIM-only provisioning, users must be provisioned by SCIM
before they can sign in. If a user can authenticate through SSO but has not been
provisioned, they may not receive access until the SCIM sync creates or updates
their USAi account and required group membership.

## User Provisioning

When Entra provisions a user, it sends a SCIM user record to USAi.

Recommended user mappings:

| Microsoft Entra attribute | USAi SCIM attribute |
|---------------------------|---------------------|
| `userPrincipalName` | `userName` |
| `mail` | `emails[type eq "work"].value` |
| `givenName` | `name.givenName` |
| `surname` | `name.familyName` |
| `displayName` | `displayName` |
| `Switch([IsSoftDeleted], , "False", "True", "True", "False")` | `active` |

The `active` mapping controls whether the USAi user account is enabled or
disabled.

## What `active = false` Means

For USAi, `active = false` means the user account is disabled in the USAi
authentication service.

The account record can still exist for audit and history, but the user should
not be able to sign in while disabled.

Microsoft documents this as normal SCIM soft-deprovisioning behavior. When a
user is disabled, deleted, or removed from provisioning scope, Entra can send
`active = false` to the target SCIM application.

Reference:
[How Microsoft Entra provisioning works](https://learn.microsoft.com/en-us/entra/identity/app-provisioning/how-provisioning-works)

## Where To Configure `active` In Microsoft Entra

Use the Entra enterprise application that is configured for USAi SCIM
provisioning. This is often a non-gallery enterprise application named something
like `USAi Provisioning - [Agency Name]`.

1. Open the Microsoft Entra admin center.
2. Go to **Identity**.
3. Go to **Applications**.
4. Open **Enterprise applications**.
5. Select the USAi provisioning enterprise application.
6. Open **Provisioning**.
7. Select **Edit provisioning** if the provisioning overview page is shown.
8. Expand **Mappings**.
9. Open **Provision Microsoft Entra ID Users**.
10. In **Target object actions**, confirm the intended actions:
    - **Create** creates users in USAi.
    - **Update** updates user attributes and can send `active = false`.
    - **Delete** allows hard-delete requests when applicable.
11. In **Attribute Mappings**, find the target attribute named `active`.
12. Confirm the `active` mapping uses this expression:

    ```text
    Switch([IsSoftDeleted], , "False", "True", "True", "False")
    ```

13. Save the mapping.

Reference:
[Customize application attribute mappings in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/app-provisioning/customize-application-attributes)

## Provisioning Scope

Provisioning scope controls which users and groups Entra sends to USAi.

For most agencies, USAi recommends:

```text
Sync only assigned users and groups
```

To configure scope:

1. Open the USAi provisioning enterprise application.
2. Open **Provisioning**.
3. Open **Settings**.
4. Set **Scope** to **Sync only assigned users and groups**.
5. Save the setting.

Then assign the users or groups that should be provisioned:

1. Open the USAi provisioning enterprise application.
2. Open **Users and groups**.
3. Select **Add user/group**.
4. Assign the Entra groups or individual users that should have USAi access.

## Group Provisioning

SCIM group provisioning lets Entra send groups and membership to USAi.

### Required: Create Matching Groups In Your IdP

Before enabling group provisioning, create the USAi access groups in Entra or
Okta. Each IdP group `displayName` must **exactly match** the corresponding
group that already exists in your USAi realm. Matching includes capitalization,
spaces, and hyphens. For example, `API-Key-Admin` matches; `API Key Admin`,
`api-key-admin`, and `USAi-Admins` do not.

The standard USAi groups are:

| Exact group name | Access provided |
|------------------|-----------------|
| `Default-User` | Chat, Console, and API documentation |
| `Admin` | Full agency administration |
| `API Users` | Invoke the API |
| `API-Key-Admin` | Manage API keys for agency users |
| `API-Key-User-Short-Term` | Manage the user's own short-term API keys |
| `Model-Manager` | Manage agency model availability and the default model |
| `Financial-Manager` | Manage the agency API budget |
| `Group-Manager` | Manage groups |

> **Current limitation:** USAi supports SCIM provisioning only for the groups
> listed above. Do not create or provision custom or additional groups. USAi is
> not accommodating additional-group requests at this time.

Create only the listed groups your agency will use, add users to the appropriate
groups, and assign those groups to the USAi provisioning application.

Do not invent new IdP group names and expect USAi to translate them into roles.
The matching USAi groups already have the appropriate roles. SCIM synchronizes
membership into those groups; it does not create the USAi authorization model.

Recommended group mappings:

| Microsoft Entra attribute | USAi SCIM attribute |
|---------------------------|---------------------|
| `displayName` | `displayName` |
| `members` | `members` |

To configure group provisioning:

1. Open the USAi provisioning enterprise application.
2. Open **Provisioning**.
3. Select **Edit provisioning** if needed.
4. Expand **Mappings**.
5. Open **Provision Microsoft Entra ID Groups**.
6. Set **Enabled** to **Yes**.
7. Confirm the `displayName` and `members` mappings.
8. In **Target object actions**, confirm Create, Update, and Delete match your
   agency's intended behavior.
9. Save the mapping.

## Choosing A Group Model

Before enabling group provisioning, decide which system owns group membership.

Recommended model:

- The USAi team owns the groups and role assignments in the USAi realm.
- The agency creates same-named groups and owns their membership in Entra or
  Okta.
- Agency admins add or remove users from those matching IdP groups.
- The IdP syncs group membership to the existing USAi groups through SCIM.

Do not create disconnected groups with different names in the IdP and USAi. If
the exact group names do not line up, stop and confirm the correct names with
the USAi team before turning provisioning on.

## Deprovisioning Decisions

Before enabling SCIM, decide what should happen when a user is removed from the
USAi provisioning scope.

Common options:

- Leave the existing USAi account unchanged.
- Remove the user only from SCIM-managed groups.
- Disable the user by sending `active = false`.
- Delete the user by sending a SCIM delete request.

For most agencies, disabling users is safer than deleting them because it keeps
the account record available for audit and support.

## Testing In Entra

Before turning provisioning on for a broad user population, test with one user
and one group.

1. Assign a test user or test group to the USAi provisioning enterprise
   application.
2. Open **Provisioning**.
3. Use **Provision on demand** if available, or turn provisioning on and wait for
   the next cycle.
4. Open **Provisioning logs**.
5. Confirm the user action succeeded.
6. Confirm the group action succeeded, if group provisioning is enabled.
7. Remove the test user from the assigned group or application.
8. Confirm the deprovisioning behavior matches the decision your agency made.

The USAi team can confirm whether the user and group appeared correctly in USAi.

## Information To Send The USAi Team

Before a co-work session, send:

- The agency name.
- The USAi realm name, if already provided.
- Whether SCIM should manage users, groups, or both.
- Whether SCIM should manage all existing USAi users or only newly assigned
  users.
- The exact same-named IdP and USAi groups that should be provisioned.
- Confirmation that capitalization, spaces, and hyphens match.
- The intended deprovisioning behavior.
- A technical contact who can view Entra or Okta provisioning logs during testing.
