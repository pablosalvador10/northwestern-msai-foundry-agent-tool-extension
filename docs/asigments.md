# Assignments

## Week 3: Build Your Single Agent + Add External Tools

This week you'll build a single AI agent in Azure AI Foundry and extend it with external tools.

**Start here**: [Single Agent Architecture](single_agent_architecture.md) — Understand the problem and architecture before diving into the labs.

### Deliverables

| Component | Points |
|-----------|--------|
| Architecture diagram + brief reasoning | 15 pts |
| **Choose one:** | |
| → Create an Azure Function and connect it to your agent | 15 pts |
| → Create a Logic App and connect it to your agent | 10 pts |

**Total: 30 points**

### Approach: Divide and Conquer

Don't try to build everything at once. Follow the labs step by step:

1. **First** — Build your tool independently (Azure Function OR Logic App)
   - [Lab 1: Azure Functions](../notebooks/lab1_azure_functions.ipynb)
   - [Lab 2: Logic Apps](../notebooks/lab2_logic_apps.ipynb)
2. **Then** — Create your agent in Azure AI Foundry
3. **Finally** — Connect the tool to your agent and test it
   - [Lab 3: Single Agent Tool Calling](../notebooks/lab3_single_agent_tool_calling.ipynb)

This divide-and-conquer approach lets you debug each piece in isolation before wiring them together.

### What to Submit

1. **Architecture diagram** — Show your agent, tools, and how they connect
2. **Brief reasoning** — Why did you choose this architecture? What are the benefits?
3. **Working demo** — Screenshot or recording of your agent using the tool

## Week 4: Coming Soon

*Details will be added here.*