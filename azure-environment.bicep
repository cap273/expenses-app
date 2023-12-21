param location string = resourceGroup().location
param appName string
param appServicePlanName string
param sqlServerName string
param sqlDatabaseName string
param sqlAdministratorLogin string
param allowedIpAddress string
@secure()
param sqlAdministratorPassword string

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  properties: {
    reserved: true
  }
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
}

resource appService 'Microsoft.Web/sites@2022-09-01' = {
  name: appName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'DB_SERVER'
            value: '${sqlServerName}${environment().suffixes.sqlServerHostname}'
        }
        {
          name: 'DB_NAME'
          value: sqlDatabaseName
        }
        {
          name: 'DB_USERNAME'
          value: sqlAdministratorLogin
        }
        {
          name: 'DB_PASSWORD'
          value: sqlAdministratorPassword
        }
      ]
      linuxFxVersion: 'Python|3.12'
      alwaysOn: false
      ftpsState: 'FtpsOnly'
      minTlsVersion:'1.2'
      http20Enabled: true
    }
  }
}

resource appServiceSourceControl 'Microsoft.Web/sites/sourcecontrols@2022-09-01' = {
  parent: appService
  name: 'web'
  properties: {
    repoUrl: 'https://github.com/cap273/expenses-app'
    branch: 'main'
    isManualIntegration: false
    isMercurial: false
    deploymentRollbackEnabled: false
  }
}

resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdministratorLogin
    administratorLoginPassword: sqlAdministratorPassword
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: 'GP_S_Gen5_1'
    tier: 'GeneralPurpose'
  }
}

// Firewall rule resource
resource sqlFirewallRule 'Microsoft.Sql/servers/firewallRules@2022-05-01-preview' = {
  parent: sqlServer
  name: 'AllowClientIP'
  properties: {
    startIpAddress: allowedIpAddress
    endIpAddress: allowedIpAddress
  }
}
