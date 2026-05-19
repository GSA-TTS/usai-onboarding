# USAi SCIM Provisioning Guide

This guide explains how SCIM provisioning works with USAi, what your agency
controls in Microsoft Entra ID, and what happens to existing USAi users when
SCIM is introduced.

SCIM is separate from single sign-on. Users still authenticate through your
identity provider using OIDC or SAML. SCIM manages user records, attributes, and
group membership in USAi.

## End-To-End Flow

```
Microsoft Entra ID provisioning service
  -> USAi SCIM endpoint
  -> USAi authentication service
  -> USAi user and group records
```

In this model, Entra ID is the SCIM client and USAi is the SCIM service
provider.

Entra sends provisioning requests to USAi. USAi does not push users or groups to
Entra.

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

- Entra owns USAi access groups.
- Agency admins add or remove users from Entra groups.
- Entra syncs those groups and memberships to USAi through SCIM.
- USAi maps those synced groups to the appropriate USAi roles.

Avoid creating disconnected duplicate groups in Entra and USAi. If the group
names do not line up, agree on the mapping with the USAi team before turning
provisioning on.

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
- The Entra groups that should be provisioned.
- The intended mapping from Entra groups to USAi roles.
- The intended deprovisioning behavior.
- A technical contact who can view Entra provisioning logs during testing.
