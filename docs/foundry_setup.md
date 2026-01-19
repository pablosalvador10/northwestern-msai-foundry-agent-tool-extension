# Azure AI Foundry Setup Guide

This guide walks you through setting up Azure AI Foundry for this project.

## Prerequisites

- Azure subscription with appropriate permissions
- Azure CLI installed (`az`)
- Python 3.11+

## Step 1: Create an Azure AI Hub

### Using Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Azure AI Foundry"
3. Click "Create a hub"
4. Fill in the required details:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Name**: `northwestern-ai-hub` (or your preferred name)
   - **Region**: Choose a region close to you with AI services available
5. Click "Review + create" then "Create"

### Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name northwestern-rg --location eastus

# Create AI Hub (requires Azure AI CLI extension)
az extension add --name ai-foundry --allow-preview true

az ai hub create \
    --name northwestern-ai-hub \
    --resource-group northwestern-rg \
    --location eastus
```

## Step 2: Create an Azure AI Project

### Using Azure Portal

1. Navigate to your AI Hub
2. Click "Projects" in the left menu
3. Click "New project"
4. Enter project details:
   - **Name**: `foundry-agent-project`
   - **Description**: Northwestern MSAI Foundry Agent Lab
5. Click "Create"

### Using Azure CLI

```bash
az ai project create \
    --name foundry-agent-project \
    --hub-name northwestern-ai-hub \
    --resource-group northwestern-rg
```

## Step 3: Deploy a Model

### Using Azure Portal

1. In your AI Project, go to "Deployments"
2. Click "Deploy model"
3. Select "gpt-4o" (or your preferred model)
4. Configure deployment:
   - **Deployment name**: `gpt-4o`
   - **Model version**: Latest
   - **Tokens per minute**: Based on your needs
5. Click "Deploy"

### Using Azure CLI

```bash
az ai deployment create \
    --name gpt-4o \
    --project-name foundry-agent-project \
    --hub-name northwestern-ai-hub \
    --resource-group northwestern-rg \
    --model-name gpt-4o
```

## Step 4: Get Connection String

### Using Azure Portal

1. Go to your AI Project
2. Navigate to "Settings" → "Properties"
3. Copy the "Connection string"

### Using Azure CLI

```bash
az ai project show \
    --name foundry-agent-project \
    --hub-name northwestern-ai-hub \
    --resource-group northwestern-rg \
    --query connectionString -o tsv
```

## Step 5: Configure Environment

Add the connection string to your `.env` file:

```bash
AZURE_AI_PROJECT_CONNECTION_STRING="your-connection-string-here"
AZURE_SUBSCRIPTION_ID="your-subscription-id"
AZURE_RESOURCE_GROUP="northwestern-rg"
AZURE_AI_PROJECT_NAME="foundry-agent-project"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
```

## Step 6: Verify Setup

Run this Python script to verify your setup:

```python
from northwestern_foundry_agent import Settings, FoundryAgent

# Load settings
settings = Settings()
print(f"Project configured: {settings.is_configured}")

# Verify connection (requires proper credentials)
if settings.is_configured:
    agent = FoundryAgent(settings)
    print("Agent initialized successfully!")
```

## Troubleshooting

### Common Issues

1. **"Connection string is not configured"**
   - Ensure `.env` file exists and contains the connection string
   - Verify the connection string format

2. **"Authentication failed"**
   - Run `az login` to refresh credentials
   - Check Azure AD permissions

3. **"Model deployment not found"**
   - Verify the deployment name matches `AZURE_OPENAI_DEPLOYMENT`
   - Check if deployment is active in Azure Portal

### Getting Help

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure CLI AI Extension](https://learn.microsoft.com/cli/azure/ai)

## Next Steps

After completing this setup:

1. Proceed to [Azure Functions Setup](functions_setup.md)
2. Configure Logic Apps (optional)
3. Run the lab notebooks
