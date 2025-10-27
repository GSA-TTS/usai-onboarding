# USAi Onboarding
Welcome to the USAi onboarding guide! The following items are decisions to be made, or implementations to work through as we work to deploy USAi to your agency. 
## Building the tech stack
As soon as the MOU is signed, we get started on building out your tenant instance. There isn’t anything we need from you immediately to get that started. 
## Meetings to expect
### Kick-off call
After the MOU is signed, we’ll schedule a kick-off call to:
- Meet members of your implementation team (e.g. project manager, tech lead, security lead, etc)
- Do a short demo of USAi for individuals who may have missed previous demos
- Walk through implementation details found in this guide
- Answer any questions you may have

Please see the [onboarding slides](https://github.com/GSA-TTS/usai-onboarding/blob/main/USAi%20_%20Partner%20Onboarding.pdf). We likely won’t walk through these in detail, but they can serve as a read-ahead.
### Single sign-on integration co-work 
Once we have the tenant instance built, and the firewalls open to your IP addresses (see below), we’ll schedule a co-work with your team to connect your single sign-on solution to USAi. In this meeting you should expect:
- Partner will configure USAi as a client application in their IDP console
- We will exchange ClientID, Secret, and discovery endpoint and redirect URI
- We will setup mapping for properties (e.g. email address, name, org codes)
- We will validate that the partner can sign into the system with their IDP

### Recurring syncs
We don’t have strong preferences about how we establish this cadence and what topics to cover, but we know we do want to hear and learn from your experiences with USAi! 
## What we need from you
### Security
- **Access security package** - To access the GSA Moderate ATO security package (ATO letter, pen test results, POA&M, etc), please complete the [USAi security package access request spreadsheet](https://github.com/GSA-TTS/usai-onboarding/blob/main/(Template)%20USAi%20Security%20Package%20Access%20Request%20Spreadsheet%20V1.1.xlsx). Short-term access will be available via a pin for 7 days, but if access is needed for longer we can accommodate that too. Please return the spreadsheet to **usai-security@gsa.gov**.
- **(Optional) SSPP template** - To help agencies comply with the customer responsibility matrix in the MOU, we developed an [optional SSPP template](https://github.com/GSA-TTS/usai-onboarding/blob/main/(Template)%20USAi-Partner%20SSPP%20V1.0%20(1).docx). Please feel free to use this template if it’s helpful, or not. We do not need this returned to us.

### Firewall requests

To ensure we open up the firewall to the right egress IP addresses for your agency, please complete the [USAi firewall request spreadsheet](https://github.com/GSA-TTS/usai-onboarding/blob/main/(Template)%20USAi-Partner%20Firewall%20Request%20Update%20V1.1%20.xlsx). Please return the spreadsheet to **usai-security@gsa.gov**.
- **Note:** it usually takes the GSA team 7 days to make the firewall updates, so this item is a little time-sensitive.

### Models to deploy
USAi currently has the following models available (or coming soon!) with current costs shown. If you would like to disable any models, please let us know at partnerships@usai.gov.

Model Name | Vendor | Price per 1M input tokens  | Price per 1M output tokens
--- | --- | --- | --- | 
GPT-4o | OpenAI | $2.75 | $11.00 
GPT-41 | OpenAI | $0.44 | $0.22
GPT-5 | OpenAI | - | - 
GPT-5 | OpenAI | - | -
Gemini 2.5 Pro | Google | $1.25 | $10.00 
Gemini 2 Flash | Google | $0.15 | $0.60
Llama 4 Maverick | Meta | $0.24 | $0.97
Opus 4 | Anthropic | $15.00 | $75.00 
Opus 4.1 | Anthropic | $15.00 | $75.00
Sonnet 3.7 | Anthropic | $3.00 | $15.00 
Sonnet 4 | Anthropic | $3.00 | $15.00
Sonnet 4.5 | Anthropic | $3.30 | $16.50
Sonnet 4.5 - Long Context | Anthropic | $6.60 | $24.75
Haiku 3.5 | Anthropic | $0.80 | $4.00
Haiku 4.5 | Anthropic | $1.10 | $5.50

### System prompts

You will have the ability to modify the USAi Chat’s system prompts to improve behavior, security, performance, and alignment with Federal AI requirements. [GSA's current system prompts](https://github.com/GSA-TTS/usai-onboarding/blob/main/USAi%20Chat%20_%20System%20Prompts.docx) are attached as a reference. Please send a word document tailored to your agency’s needs to partnerships@usai.gov. Some notes to consider:

- We've seen these increase GSA's LLM safeguards from approximately 78% to 90%.
- To ensure optimal performance and manage costs, it is critical to keep system prompts clear and concise. Overly complex, restrictive, or lengthy prompts can degrade performance and increase operational expenses.

### API user management
The workflow for API management is not included in USAi (request, approve, assign). At this time we’ve decided to default to whatever is customary at an agency, or their preference (e.g. Jira, ServiceNow, email, etc). Agencies have discretion on how they’d like to manage this, and we’ll incorporate it into your agency-specific API documentation upon implementation. Please update the [API documentation](https://github.com/GSA-TTS/usai-onboarding/blob/main/(Template)%20USAi%20API%20guidance.docx) in the section highlighted in yellow and return it to partnerships@usai.gov. 

## Additional things for you to (potentially) think about
### Privacy policy
You may want to think about what data you are comfortable with users inputting into USAi based on agency use cases, strategy, risk tolerance, and policy (e.g. CUI/ PII). Please see the USAi [privacy policy](https://www.usai.gov/privacy/) and [rules of behavior](https://www.usai.gov/rules-of-behavior/) as reference. 
### Comms
We are sharing [GSA's comms regarding our implementation of AI](https://github.com/user-attachments/files/23168016/Sample.GSA.comms.docx) as reference. 
