# Building Agents in Azure AI Foundry

Build an AI agent. Give it tools. Deploy it to the cloud.

> Start with the **single-agent pattern** — one agent orchestrating multiple tools. Master this foundation, then level up to multi-agent systems and MCP.

**Jump to:** [The Big Picture](#the-big-picture) · [Assignments](#assignments) · [Labs](#labs-divide-and-conquer) · [Getting Started](#getting-started) · [Resources](#resources)


## The Big Picture 

### *Single Agent vs Multi-Agent*

A **single agent** is one AI entity that reasons, decides, and acts. It's the right choice when:
- The task can be handled by one "brain" with the right tools
- You want atomic, predictable decisions
- Complexity is manageable without delegation

When tasks require specialization, parallel work, or debate between perspectives — that's when you graduate to **multi-agent systems**. But start simple. Most problems don't need an orchestra; they need one good musician with the right instruments.

### *Tool Calling*

When you create an agent in **Azure AI Foundry**, you get a powerful AI runtime in the cloud. But agents become truly useful when they can take **actions** — calling APIs, processing data, sending notifications, etc.

To add actions, we register **tools**. Tools can be:
- **In-process functions** (code that runs inside the agent)
- **External services** like **Azure Functions** or **Logic Apps** (decoupled, cloud-based)

These labs focus on the decoupled approach: your agent lives in AI Foundry, and your tools live independently in Azure — clean, scalable, and production-ready. See the [Labs](#labs-divide-and-conquer) below.

### *MCP: Model Context Protocol*

**MCP** is an open standard for connecting AI agents to tools via a client-server architecture. Instead of hardcoding tool integrations:

- **MCP Server** = exposes tools (your functions, APIs, databases)
- **MCP Client** = the agent that discovers and calls those tools

Why it matters:
- **Reusability** — Build a tool once, use it across many agents
- **Security** — Centralized auth, audit, and access control
- **Discovery** — Agents can find and learn new tools dynamically

*We'll explore MCP in future labs.*

## Assignments

See the full assignment details: **[Week 3 Assignment](docs/asigments.md)**

## Labs (Divide and Conquer)

Build step by step — don't try to do everything at once:

| Step | Lab | What You'll Build |
|------|-----|-------------------|
| 1 | [Lab 1: Azure Functions](notebooks/lab1_azure_functions.ipynb) | Create and deploy an Azure Function |
| 2 | [Lab 2: Logic Apps](notebooks/lab2_logic_apps.ipynb) | Create and configure a Logic App |
| 3 | [Lab 3: Single Agent Tool Calling](notebooks/lab3_single_agent_tool_calling.ipynb) | Build your agent, add tools, chat with it |

> **Tip**: Complete Lab 1 OR Lab 2 first (depending on which tool you choose), then move to Lab 3 to wire everything together.

## Getting Started

```bash
# Clone and install
git clone <repo-url>
cd northwestern-msai-foundry-agent-tool-extension
pip install -r requirements.txt
```

Then open the notebooks and follow along!

## Resources

### Azure Portal & UI

- [Azure Portal](https://portal.azure.com) - Main Azure portal
- [Azure AI Foundry](https://ai.azure.com) - AI Foundry interface
- [Azure Functions](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites/kind/functionapp) - Function Apps management
- [Logic Apps](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Logic%2Fworkflows) - Logic Apps designer
- [Application Insights](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents) - Monitoring and diagnostics

### Documentation

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Azure Functions Documentation](https://learn.microsoft.com/en-us/azure/azure-functions/)
- [Azure Logic Apps Documentation](https://learn.microsoft.com/en-us/azure/logic-apps/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure Identity (Managed Identity)](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/)

### Python Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)
- [Pytest Documentation](https://docs.pytest.org/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
