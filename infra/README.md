# Infrastructure

This directory contains infrastructure-as-code templates for deploying Azure resources.

## Files

- `main.bicep` - Azure Bicep template for core infrastructure
- `parameters.json` - Parameter file for Bicep deployment

## Deployment

### Prerequisites

- Azure CLI installed
- Logged in to Azure (`az login`)
- Appropriate permissions to create resources

### Deploy using Azure CLI

```bash
# Create resource group
az group create --name northwestern-rg --location eastus

# Deploy Bicep template
az deployment group create \
    --resource-group northwestern-rg \
    --template-file main.bicep \
    --parameters parameters.json
```

## Resources Created

The template creates:

1. **Azure AI Hub** - AI Foundry workspace
2. **Azure AI Project** - Project within the hub
3. **Storage Account** - For function app
4. **Function App** - Serverless compute for HTTP functions
5. **Logic App** - Workflow automation

## Customization

Edit `parameters.json` to customize:

- Resource names
- Region
- SKU/pricing tiers
- Tags

## Notes

- This is a minimal template for educational purposes
- For production, add networking, monitoring, and security configurations
- Review Azure pricing before deployment
