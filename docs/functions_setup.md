# Azure Functions Setup Guide

This guide walks you through deploying the Azure Functions included in this project.

## Prerequisites

- Azure subscription
- Azure CLI installed (`az`)
- Azure Functions Core Tools (`func`)
- Python 3.11+

## Local Development

### Step 1: Install Azure Functions Core Tools

**macOS:**
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

**Windows:**
```bash
npm install -g azure-functions-core-tools@4
```

**Linux:**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4
```

### Step 2: Run Functions Locally

```bash
cd functions

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the function app
func start
```

Functions will be available at:
- Health Check: `http://localhost:7071/api/health`
- Quote: `http://localhost:7071/api/quote`

### Step 3: Test Locally

```bash
# Test health check
curl http://localhost:7071/api/health

# Test quote (with category)
curl "http://localhost:7071/api/quote?category=wisdom"
```

## Deploy to Azure

### Step 1: Create Function App

**Using Azure Portal:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Function App"
4. Configure:
   - **Subscription**: Your subscription
   - **Resource Group**: Use existing or create new
   - **Function App name**: `northwestern-functions` (must be globally unique)
   - **Runtime stack**: Python
   - **Version**: 3.11
   - **Region**: Same as your AI Hub
   - **Plan type**: Consumption (Serverless)
5. Click "Review + create" then "Create"

**Using Azure CLI:**

```bash
# Create storage account (required for Functions)
az storage account create \
    --name northwesternfuncstor \
    --resource-group northwestern-rg \
    --location eastus \
    --sku Standard_LRS

# Create function app
az functionapp create \
    --name northwestern-functions \
    --storage-account northwesternfuncstor \
    --resource-group northwestern-rg \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --os-type Linux
```

### Step 2: Deploy Functions

```bash
cd functions

# Deploy using Azure Functions Core Tools
func azure functionapp publish northwestern-functions
```

### Step 3: Get Function URL and Key

**Using Azure Portal:**

1. Navigate to your Function App
2. Go to "Functions" and click on a function (e.g., `health`)
3. Click "Get Function URL"
4. Copy the URL (includes the function key)

**Using Azure CLI:**

```bash
# Get function app URL
az functionapp show \
    --name northwestern-functions \
    --resource-group northwestern-rg \
    --query defaultHostName -o tsv

# Get function key
az functionapp keys list \
    --name northwestern-functions \
    --resource-group northwestern-rg
```

### Step 4: Update Environment Configuration

Add to your `.env` file:

```bash
AZURE_FUNCTION_APP_URL="https://northwestern-functions.azurewebsites.net"
AZURE_FUNCTION_KEY="your-function-key-here"
```

## Function Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/health` | GET | Health check | None |
| `/api/quote` | GET | Get quote | `category` (optional): motivation, wisdom, humor |

### Example Responses

**Health Check:**
```json
{
    "status": "healthy",
    "service_name": "northwestern-foundry-functions",
    "version": "1.0.0",
    "timestamp": "2024-01-15T10:30:00.000000+00:00",
    "details": {
        "python_version": "3.11.0",
        "function_app": "running"
    }
}
```

**Quote:**
```json
{
    "quote": "The only way to do great work is to love what you do.",
    "author": "Steve Jobs",
    "category": "motivation",
    "timestamp": "2024-01-15T10:30:00.000000+00:00"
}
```

## Troubleshooting

### Common Issues

1. **"Function app not found"**
   - Verify the function app name is correct
   - Check if deployment succeeded

2. **"401 Unauthorized"**
   - Verify the function key is correct
   - Check authentication settings in Azure Portal

3. **"500 Internal Server Error"**
   - Check function logs in Azure Portal
   - Verify Python dependencies are installed

### Viewing Logs

**Using Azure Portal:**
1. Navigate to Function App
2. Go to "Monitor" → "Log stream"

**Using Azure CLI:**
```bash
az functionapp log tail \
    --name northwestern-functions \
    --resource-group northwestern-rg
```

## Next Steps

After deploying functions:

1. Test endpoints using curl or a REST client
2. Proceed to [Logic Apps Setup](logic_apps_setup.md)
3. Run the function tool notebooks
