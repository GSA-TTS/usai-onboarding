
# **USAi Administrator Guide**
## **System Configuration Options**
# **Introduction**
Welcome to USAi. As an administrator, you have elevated system access that enables you to manage and configure several aspects of the product at your agency. This guide provides instructions on managing user permissions, large language models, API keys, and system prompts.
Options for configuring your agency's USAi environment are located under the **Configurations** menu in the **Console**.

## **User Permissions (Groups)**
Access levels within the platform are determined by membership in specific **Groups**. Upon agency onboarding, all users that authenticate into the platform via your single sign-on solution are automatically assigned to the **Default-User** group.
Users within the **Admin** or **Group-Manager** groups have the authority to manage memberships. Available groups and their respective permissions are listed below, and also listed within the Console’s Group Manager page:

### **Groups Manager**
| **Group Name** | **Description** |
| :- | :- |
| API-Key-Admin | Can manage API keys for any user within the agency |
| API-Key-User-Short-Term | Can manage their short-term API keys |
| Admin | Can manage Groups, API keys, system prompts, models, API budgets, Projects, and long duration API keys for Projects |
| Default-User | Can access Chat, Console, and API documentation |
| Group-Manager | Can manage Groups |
| Model-Manager | Can manage agency model availability and default model |
| Financial-Manager | Can manage weekly short-term API key budget, can create Projects with a budget |

## **Models Manager**
The **Models Manager** section allows **Admins** and the **Model-Manager** Group to manage which large language models are available to users within their agency, whether they are available via API or Chat, and which model is set as the default. You can enable or disable specific models based on agency needs, security requirements, or cost considerations by using the checkboxes.
Model Cards and Evaluation data are available in the Console to help agencies understand the costs, trustworthiness, and relative strengths of each model.
More detailed trustworthiness analysis of the Azure models (GPT, Grok) are available in the USAi security folder.

## **API Key Management**
**Admins** and users in the **API-Key-Admin** group have access to **API Key Management**. This interface allows the ability to rotate, revoke, or delete all API keys within an agency. For example, if someone accidentally checks an API key into GitHub and it needs to be deactivated, someone is out of the office and needs an API key rotated, or someone left the agency and we need to disable all their API keys. 
Additionally, individuals in the **Admin** and **Financial-Manager** groups can modify the **API Budget**. The API Budget manages a per-person weekly budget for API keys. Each user in the **API-Key-User-Short-Term** group can create their own short-duration, personal API keys for use with the USAi API. The budget that is managed is a total amount of token spend across all keys an individual creates for themselves.  
  
For example: An **Admin** navigates to the **API Budget** page and enters $500 for the weekly budget. This means that Joe Smith can use a total of $500 worth of tokens through the USAi API on a weekly basis from Monday through Sunday. If Joe reaches $500 of tokens during any week, the API will return an error and Joe will not be able to use the API until the next week.  
  
The **API Budget** can be turned on and off with a toggle on the page. If the budget is turned off, then API users will have no maximum amount of tokens they can spend each week.  
  
By default, the budget is set to “on” and $200 per person per week.

## **System Prompts**
System prompts tell USAi how the AI should behave. They provide the basic instructions the model follows when responding to users, such as tone, safety expectations, and agency-specific guidance.
Admins can manage system prompts in Prompt Manager under the “Tenant Prompt” section. 
The default USAi System Prompt cannot be edited. It contains required platform-wide instructions that help keep USAi safe, consistent, and reliable.
If your agency needs additional guidance, you can add custom instructions in the editable section. These custom instructions work alongside the default USAi System Prompt; they do not replace it.

## **Projects**
Projects in USAi are dedicated management spaces within the USAi Console to group agency initiatives or team workloads. Currently, only API keys (personal and service keys) can be added to a Project.
  - **Personal API keys:** Short duration API keys (7 days) intended for individual use, such as experimentation, prototyping, exploratory, and project implementation work. 
  - **Service API keys:** Long duration API keys (90 days) intended to be used to connect applications to USAi APIs. Each service key must be associated with a Project and can support application workloads, including production use. Multiple users may share a service API key. 

**Adding Members to a Project**
All projects must be initiated by an Administrator. Administrators manage project access directly through the USAi Console interface
  - **Navigate to Projects:** In the USAi Console navigation menu, open the Projects section to view existing agency projects or click Create Project to establish a new Project.
  - **Select Project & Add Members:** Open the target project, click on the Members icons for a project, and search for users or user groups by name or email to add them to the project roster. Hover over a project roster member to add or remove the member from the project admin group.
  - **Provision Access & API Keys:** From the Keys section, assign project-specific Personal API keys or Service API keys. 

**Permissions & Roles**
USAi applies a hierarchical governance flow (Tenant → Project → User) to ensure security and budget control. Each level may modify the level below. 
**Tenant / Agency Administrator**
  - Full authority to create (including sub-projects) across the agency tenant.
  - Adds and removes Project Managers and Project Members.
  - Generates and manages service level, long duration API keys associated with projects.
**Financial Manager**
  - Full authority to create (including sub-projects) across the agency tenant.
**Project Manager**
  - Adds and removes Project Managers and Project Members.
**Project Member**
  - Generates and manages personal, short duration API keys associated with projects.

## **Other configuration options**
Certain configuration options, such as limiting document upload capabilities and web grounding features, require coordination with the USAi core team for implementation. Please [contact us](mailto:partnerships@usai.gov) for assistance with these settings.

```
