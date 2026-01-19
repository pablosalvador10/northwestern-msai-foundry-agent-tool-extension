# Azure Logic Apps Setup Guide

This guide walks you through creating and configuring an Azure Logic App for use with the AI agent.

## Prerequisites

- Azure subscription
- Azure Portal access
- Understanding of HTTP triggers

## Step 1: Create Logic App

### Using Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Logic App"
4. Select "Logic App (Consumption)" for pay-per-execution
5. Configure:
   - **Subscription**: Your subscription
   - **Resource Group**: Use existing or create new
   - **Logic App name**: `northwestern-logic-app`
   - **Region**: Same as your other resources
   - **Plan type**: Consumption
6. Click "Review + create" then "Create"

### Using Azure CLI

```bash
az logic workflow create \
    --name northwestern-logic-app \
    --resource-group northwestern-rg \
    --location eastus
```

## Step 2: Configure HTTP Trigger

### Using Logic App Designer

1. Navigate to your Logic App
2. Click "Logic app designer"
3. Select "When a HTTP request is received" as the trigger
4. Configure the trigger:
   - **Method**: POST
   - **Request Body JSON Schema**: See below

### Request Body Schema

```json
{
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "description": "Action to perform"
        },
        "inputData": {
            "type": "object",
            "description": "Input data for the workflow"
        },
        "correlationId": {
            "type": "string",
            "description": "Correlation ID for tracking"
        },
        "metadata": {
            "type": "object",
            "description": "Additional metadata"
        },
        "timestamp": {
            "type": "string",
            "description": "Request timestamp"
        }
    },
    "required": ["action"]
}
```

## Step 3: Add Workflow Logic

### Example: Echo Workflow

For testing purposes, create a simple echo workflow:

1. Add a new step after the HTTP trigger
2. Select "Response" action
3. Configure:
   - **Status Code**: 200
   - **Headers**: `Content-Type: application/json`
   - **Body**:
   ```json
   {
       "workflow_run_id": "@{workflow().run.name}",
       "status": "succeeded",
       "output_data": {
           "received_action": "@{triggerBody()?['action']}",
           "processed_at": "@{utcNow()}"
       },
       "error": null,
       "started_at": "@{workflow().run.startTime}",
       "completed_at": "@{utcNow()}"
   }
   ```

4. Save the workflow

## Step 4: Get Trigger URL

1. In the Logic App designer, click on the HTTP trigger
2. Copy the "HTTP POST URL"
3. This URL contains a SAS token for authentication

> **Security Note**: The trigger URL contains authentication. Keep it secure!

## Step 5: Update Environment Configuration

Add to your `.env` file:

```bash
LOGIC_APP_TRIGGER_URL="https://prod-xx.eastus.logic.azure.com:443/workflows/xxx/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=xxx"
```

## Sample Payload Schemas

See `docs/logic_app_payloads/` for complete examples:

### Request Payload

```json
{
    "action": "process_document",
    "inputData": {
        "document_id": "doc-12345",
        "document_type": "invoice",
        "priority": "normal"
    },
    "correlationId": "corr-abc-123",
    "metadata": {
        "source": "ai-agent",
        "user_id": "user-001"
    },
    "timestamp": "2024-01-15T10:30:00.000000Z"
}
```

### Response Payload

```json
{
    "workflow_run_id": "08585xxxxx",
    "status": "succeeded",
    "output_data": {
        "document_id": "doc-12345",
        "processed": true,
        "result": "Document processed successfully"
    },
    "error": null,
    "started_at": "2024-01-15T10:30:00.000000Z",
    "completed_at": "2024-01-15T10:30:05.000000Z"
}
```

## Testing the Logic App

### Using curl

```bash
curl -X POST "YOUR_TRIGGER_URL" \
    -H "Content-Type: application/json" \
    -d '{
        "action": "test",
        "inputData": {"message": "Hello from test!"},
        "correlationId": "test-001"
    }'
```

### Using Python

```python
from northwestern_foundry_agent.integrations.logic_apps import (
    LogicAppsClient,
    LogicAppRequest,
)

client = LogicAppsClient()
request = LogicAppRequest(
    action="test",
    input_data={"message": "Hello from Python!"},
    correlation_id="py-test-001",
)

response = await client.trigger(request)
print(f"Status: {response.status}")
print(f"Output: {response.output_data}")
```

## Advanced Workflows

### Adding Conditions

1. Add a "Condition" action after the trigger
2. Configure based on the `action` field:
   - If action == "process_document" → Document processing branch
   - If action == "send_notification" → Notification branch
   - Else → Default branch

### Adding External Connectors

Logic Apps supports 400+ connectors:

- **Office 365**: Send emails, create events
- **Azure Services**: Blob Storage, Service Bus, Cosmos DB
- **Third-party**: Salesforce, Slack, Twitter

### Error Handling

1. Use "Scope" actions to group steps
2. Configure "Run after" settings for error handling
3. Add parallel branches for compensation logic

## Troubleshooting

### Common Issues

1. **"401 Unauthorized"**
   - Verify the trigger URL is correct (includes SAS token)
   - Check if the Logic App is enabled

2. **"Workflow run failed"**
   - Check run history in Azure Portal
   - Review the inputs/outputs at each step

3. **"Timeout"**
   - Default timeout is 90 seconds for HTTP trigger
   - Consider async patterns for long-running workflows

### Viewing Run History

1. Navigate to your Logic App
2. Click "Overview" to see recent runs
3. Click on a run to see step-by-step execution

## Next Steps

After setting up Logic Apps:

1. Create more complex workflows
2. Run the Logic App integration notebook
3. Explore additional connectors
