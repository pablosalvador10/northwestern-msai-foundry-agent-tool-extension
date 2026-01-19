// Northwestern MSAI Foundry Agent Infrastructure
// Bicep template for Azure resources

@description('Base name for all resources')
param baseName string = 'northwestern'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Environment tag')
param environment string = 'dev'

// Variables
var uniqueSuffix = uniqueString(resourceGroup().id)
var storageAccountName = '${baseName}stor${uniqueSuffix}'
var functionAppName = '${baseName}-functions-${uniqueSuffix}'
var appServicePlanName = '${baseName}-asp-${uniqueSuffix}'
var logicAppName = '${baseName}-logic-${uniqueSuffix}'

// Tags for all resources
var commonTags = {
  environment: environment
  project: 'northwestern-msai-foundry-agent'
  managedBy: 'bicep'
}

// Storage Account for Function App
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: commonTags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// App Service Plan (Consumption)
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  tags: commonTags
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true // Linux
  }
}

// Function App
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: functionAppName
  location: location
  tags: commonTags
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      pythonVersion: '3.11'
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
      ]
    }
    httpsOnly: true
  }
}

// Logic App (Consumption)
resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: logicAppName
  location: location
  tags: commonTags
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      triggers: {
        manual: {
          type: 'Request'
          kind: 'Http'
          inputs: {
            schema: {
              type: 'object'
              properties: {
                action: {
                  type: 'string'
                }
                inputData: {
                  type: 'object'
                }
                correlationId: {
                  type: 'string'
                }
                metadata: {
                  type: 'object'
                }
                timestamp: {
                  type: 'string'
                }
              }
              required: ['action']
            }
          }
        }
      }
      actions: {
        Response: {
          type: 'Response'
          kind: 'Http'
          inputs: {
            statusCode: 200
            body: {
              workflow_run_id: '@{workflow().run.name}'
              status: 'succeeded'
              output_data: {
                received_action: '@{triggerBody()?[\'action\']}'
                processed_at: '@{utcNow()}'
              }
              error: null
              started_at: '@{workflow().run.startTime}'
              completed_at: '@{utcNow()}'
            }
          }
          runAfter: {}
        }
      }
    }
  }
}

// Outputs
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output functionAppName string = functionApp.name
output logicAppName string = logicApp.name
output storageAccountName string = storageAccount.name
