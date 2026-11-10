# USAi Administrator Guide

## System Configuration Options

### Introduction

Welcome to USAi. As an administrator, you have elevated system access that enables you to manage and configure several aspects of the product at your agency. This guide provides instructions on managing user permissions, large language models, API keys, and system prompts.

Options for configuring your agency's USAi environment are located under the **Configurations** menu in the Console.

## User Permissions (Groups)

Access levels within the platform are determined by membership in specific groups. Upon agency onboarding, all users who authenticate into the platform via your single sign-on solution are automatically assigned to the **Default-User** group.

Users in the **Admin** or **Group-Manager** groups have the authority to manage memberships. Available groups and their respective permissions are listed below and in the Console’s **Group Manager** page.

### Groups Manager

| Group Name | Description |
|---|---|
| `API-Key-Admin` | Can manage API keys for any user within the agency. |
| `API-Key-User-Short-Term` | Can manage their short-term API keys. |
| `Admin` | Can manage Groups, API keys, system prompts, models, API budgets, Projects, and long-duration API keys for Projects. |
| `Default-User` | Can access Chat, Console, and API documentation. |
| `Group-Manager` | Can manage Groups. |
| `Model-Manager` | Can manage agency model availability and the default model. |
| `Financial-Manager` | Can manage the weekly short-term API key budget and create Projects with a budget. |

## Models Manager

The **Models Manager** section allows Admins and members of the **Model-Manager** group to manage which large language models are available to users within their agency, whether they are available via API or Chat, and which model is set as the default. You can enable or disable specific models based on agency needs, security requirements, or cost considerations by using the checkboxes.

Model Cards and evaluation data are available in the Console to help agencies understand the costs, trustworthiness, and relative strengths of each model.

More detailed trustworthiness analysis of the Azure models (GPT, Grok) is available in the USAi security folder.

## API Key Management

Admins and users in the **API-Key-Admin** group have access to **API Key Management**. This interface allows them to rotate, revoke, or delete all API keys within an agency. For example, an API key may need to be deactivated if someone accidentally checks it into GitHub, rotated while its owner is out of the office, or disabled when someone leaves the agency.

Additionally, individuals in the **Admin** and **Financial-Manager** groups can modify the API Budget. The API Budget manages a per-person weekly budget for API keys. Each user in the **API-Key-User-Short-Term** group can create their own short-duration, personal API keys for use with the USAi API. The budget tracks the total amount of token spend across all keys an individual creates for themselves.

For example, an Admin navigates to the API Budget page and enters a weekly budget of $500. Joe Smith can then use up to $500 worth of tokens through the USAi API each week, from Monday through Sunday. If Joe reaches $500 in token spend during any week, the API will return an error (`429: budget limit reached for this billing cycle`), and Joe will not be able to use the API until the next week.

The API Budget can be turned on or off with a toggle on the page. If the budget is turned off, API users will not have a maximum weekly token spend.

By default, the budget is **on** and set to **$200 per person per week**.

## System Prompts

System prompts tell USAi how the AI should behave. They provide the basic instructions the model follows when responding to users, such as tone, safety expectations, and agency-specific guidance.

Admins can manage system prompts in **Prompt Manager**, under the **Tenant Prompt** section.

The default USAi System Prompt cannot be edited. It contains required platform-wide instructions that help keep USAi safe, consistent, and reliable.

If your agency needs additional guidance, you can add custom instructions in the editable section. These custom instructions work alongside the default USAi System Prompt; they do not replace it.

## Projects and 90-Day API Keys

Projects in USAi are dedicated management spaces within the USAi Console to group agency initiatives or team workloads. A project is needed, and a project manager must be assigned, before teams can generate service / 90-day keys. Currently, only API keys (personal and service keys) can be added to a Project. We expect to continue extending this concept to allow additional configuration and management.

```text
Tenant (for example, GSA or USDA)
│
├── Tenant roles — assigned through named groups
│   ├── Admin
│   ├── Finance Admin
│   └── API key admin
│
├── Tenant API keys — 7-day, API-short-term-user group
│
└── Projects — each has its own members, managers, and weekly budget
    └── Project
        ├── Personal keys (7 days) — any member
        ├── Service keys (90 days) — managers only
        └── Sub-projects
            └── Sub-project — its own members, managers, budget, keys

```
## How Projects Work

USAi is introducing Projects as a structure to help organize and track platform use. Your tenant, such as GSA or USDA, is the top level, and Projects and sub-projects sit inside it. This structure helps your organization set up and organize work in a way that reflects how your agency is organized.

Two things control permissions:

- **Named Groups** control tenant-level roles, such as Admin, Finance Admin, and API key admin.
- **Project membership** controls project-level permissions. Each Project has its own members and managers.

Being a Tenant Admin lets you manage a Project, but it does not make you a member of it. To create keys in a Project, you must be added to that Project.

### Key Types

- **Personal project keys:** Short-duration API keys (7 days) intended for individual use, such as experimentation, prototyping, exploratory work, and project implementation.
- **Service project keys:** Long-duration API keys (90 days) intended to connect applications to the USAi API. Each service key must be associated with a Project and can support application workloads, including production use.

## Create a Project

All Projects must be created by an Admin or Financial Manager.

1. **Create a Project:** In the USAi Console navigation menu, open the **Projects** section to view existing agency Projects, or click **Create Project** to establish a new Project.
2. **Nest Projects:** Projects can be nested to whatever level you’d like—for example, `USA > Pennsylvania > Philadelphia > Old City > Liberty Bell`. Choose a structure that makes sense for your organization.
3. **Add a description and weekly budget:** You can use the description field to track SI use-case identifiers, if applicable. Weekly budgets run Monday through Sunday. If a Project team reaches its budget limit, they should receive an error (`429: budget limit reached for this billing cycle`). Project spending also counts toward your tenant's overall spending.
4. **Manage members:** Open the target Project, click the **Members** icon, and search for users by email to add them to the Project roster.
   - To make someone a Project Manager, hover over their name and select **Make Manager**.
   - To remove a user, search by name or email and select the **X** icon.
   - Users must have logged into USAi before they can be added to a Project.

## Create Project API Keys

Once a Project is created, Project members and Project managers can create API keys associated with that Project.

- **Personal project keys:** Create 7-day keys by navigating to **Keys > Create a Personal Key**, then select a Project from the dropdown. Any Project team member can create personal keys associated with the Project.
- **Service project keys:** Create 90-day keys by navigating to **Keys > Create Service Key**, then select a Project from the dropdown. Only Project managers can create service keys associated with the Project.

## Administering Project API Keys

Project keys can be administered in the following ways.

### Tenant-Level Roles (Assigned Through Groups)

- **Admin:** Has full authority to create Projects, including sub-projects, and add or remove Project members and Project managers. Cannot create or manage API keys associated with a Project unless they are a member of that Project.
- **API key admin:** Can take action on existing API keys, including Project keys, such as rotating and disabling them. Cannot create keys in a Project unless they are a member of that Project.

### Project-Level Roles (Assigned Through Project Membership)

- **Project manager:** Can create service (90-day) and personal (7-day) keys, rotate and disable any key in the Project, and add or remove Project managers and members.
- **Project member:** Can create personal (7-day) keys and rotate or disable their own keys.

## Administering Projects

### Reporting

Real-time visibility into cost data is not yet available for Project team members. Admins and Financial Managers can view Project data in the Console Dashboard using the **Export** function.

### Use Caution with Service Keys

USAi does not currently stop service keys from being used outside system integrations. USAi recommends 7-day API keys wherever a key could be lost or leaked, such as keys used by individuals or in development environments. Reserve service keys for production system integrations, and limit who at your agency is made a Project manager.

### Permissions and Roles

#### Tenant-Level Roles (Assigned Through Groups)

- **Admin:** Has full authority to create Projects, including sub-projects, and add or remove Project members and Project managers. Cannot create or manage API keys associated with a Project unless they are a member of that Project.
- **Financial Manager:** Has full authority to create Projects, including sub-projects, and add or remove Project members and Project managers. Cannot create or manage API keys associated with a Project unless they are a member of that Project.

#### Project-Level Roles (Assigned Through Project Membership)

- **Project manager:** Can create service (90-day) and personal (7-day) keys, rotate and disable any key in the Project, and add or remove Project managers and members.
- **Project member:** Can create personal (7-day) keys and rotate or disable their own keys.

### How Projects Differ from Groups

In Groups, **API-short-term-user** is unchanged. This grants users the ability to generate 7-day keys at the tenant level, enforced by a weekly budget if API Budget is enabled.

Projects allow new Project members to create API keys associated with a Project. They do not allow members to create API keys at the tenant level. Project API users:

- Will not appear in the **API-short-term-user** group.
- Are not constrained by the API Budget, but are constrained by the Project budget.
- Will not appear in the Console Dashboard as an API user.

## Other Configuration Options

Certain configuration options, such as limiting document upload capabilities and web grounding features, require coordination with the USAi core team for implementation. Please contact us for assistance with these settings.
