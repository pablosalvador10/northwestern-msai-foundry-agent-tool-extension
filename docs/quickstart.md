# Quick Start Guide

Get your local environment ready to run the labs.

## Prerequisites

- [VS Code](https://code.visualstudio.com/) with the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
- [uv](https://docs.astral.sh/uv/) — fast Python package manager

## Step 1: Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Step 2: Clone and Setup Environment

```bash
# Clone the repository
git clone <repo-url>
cd northwestern-msai-foundry-agent-tool-extension

# Create virtual environment and install dependencies
uv venv .venv-msai-foundry-agents
source .venv-msai-foundry-agents/bin/activate  # On Windows: .venv-msai-foundry-agents\Scripts\activate
uv pip install -r requirements.txt

# Create your .env file
cp .env.example .env
```

## Step 3: Configure Your .env File

The notebooks use `python-dotenv` to load secrets from a `.env` file. 

**You only need to fill in the variables for the lab you're working on:**

| Lab | Variables Needed |
|-----|------------------|
| Lab 1 | `AZURE_FUNCTION_URL`, `AZURE_FUNCTION_KEY` |
| Lab 2 | `LOGIC_APP_URL` |
| Lab 3 | `PROJECT_ENDPOINT`, `MODEL_DEPLOYMENT_NAME` + variables from Lab 1 or 2 |

Open `.env` and uncomment/fill in only what you need:

```bash
# Uncomment and fill in for Lab 1
# AZURE_FUNCTION_URL=https://your-function-app.azurewebsites.net/api/analyze_data
# AZURE_FUNCTION_KEY=your-function-key-here

# Uncomment and fill in for Lab 2
# LOGIC_APP_URL=https://prod-xx.eastus.logic.azure.com/workflows/...

# Uncomment and fill in for Lab 3
# PROJECT_ENDPOINT=https://your-project.services.ai.azure.com
# MODEL_DEPLOYMENT_NAME=gpt-4o
```

> **How it works**: Each notebook calls `load_dotenv()` which reads your `.env` file and makes the values available via `os.getenv()`.

## Step 4: Open in VS Code

```bash
code .
```

1. Open any notebook in the `notebooks/` folder
2. VS Code will prompt you to select a kernel — choose the `.venv-msai-foundry-agents` Python environment you just created
3. You're ready to run cells!

## Next Steps

Each lab will guide you through the Azure services you need:

| Lab | Azure Services Required |
|-----|------------------------|
| [Lab 1: Azure Functions](../notebooks/lab1_azure_functions.ipynb) | Azure Function App |
| [Lab 2: Logic Apps](../notebooks/lab2_logic_apps.ipynb) | Azure Logic App |
| [Lab 3: Single Agent Tool Calling](../notebooks/lab3_single_agent_tool_calling.ipynb) | Azure AI Foundry |

Start with the lab that matches your assignment choice. Each notebook includes setup instructions for the specific Azure resources you'll need.
