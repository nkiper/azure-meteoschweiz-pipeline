# We strongly recommend using the required_providers block to set the
# Azure Provider source and version being used
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>5.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
}

# Create resource group
resource "azurerm_resource_group" "rg-meteoschweiz-dev" {
  name     = "rg-meteoschweiz-dev"
  location = "Switzerland North"
}

# Create storage account
resource "azurerm_storage_account" "nkipermeteodata001" {
    name                     = "nkipermeteodata001"
    resource_group_name      = azurerm_resource_group.rg-meteoschweiz-dev.name
    location                 = azurerm_resource_group.rg-meteoschweiz-dev.location
    account_tier             = "Standard"
    account_replication_type = "LRS"
    account_kind             = "StorageV2"
    is_hns_enabled           = true
}

# Create SQL server

variable "admin_password" {
    type = string
    description = "SQL server admin password"
    sensitive = true
}

resource "azurerm_mssql_server" "sqls-nkipermeteo-dev" {
    name                         = "sqls-nkipermeteo-dev"
    resource_group_name          = azurerm_resource_group.rg-meteoschweiz-dev.name
    location                     = azurerm_resource_group.rg-meteoschweiz-dev.location
    version                      = "12.0"
    administrator_login          = "nkiper"
    administrator_login_password = var.admin_password
}

# Create SQL database
resource "azurerm_mssql_database" "db-nkipermeteo" {
    name                 = "db-nkipermeteo" 
    server_id            = azurerm_mssql_server.sqls-nkipermeteo-dev.id
    storage_account_type = "Local"

    lifecycle {
      prevent_destroy = true
    }
}

# Create databricks workspace
resource "azurerm_databricks_workspace" "dbw-nkipermeteo-dev" {
    name                          = "dbw-nkipermeteo-dev"
    resource_group_name           = azurerm_resource_group.rg-meteoschweiz-dev.name
    location                      = azurerm_resource_group.rg-meteoschweiz-dev.location
    sku                           = "trial"
    public_network_access_enabled = true
}