terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {}
}

# 🔹 Création du groupe de ressources
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group
  location = var.location
}

# 🔹 Création du registre ACR
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location           = azurerm_resource_group.rg.location
  sku                = "Basic"
  admin_enabled      = true
}

# 🔹 Création du serveur SQL (remplacé par azurerm_mssql_server)
resource "azurerm_mssql_server" "sql" {
  name                         = "sqlserver${var.container_name}"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  version                      = "12.0"
  administrator_login          = "admin${var.container_name}"
  administrator_login_password = "P@ssword123" # À remplacer par une variable sécurisée
  ssl_enforcement              = "Enabled"
}

# 🔹 Création de la base de données SQL (remplacement de sku_name par edition)
resource "azurerm_sql_database" "db" {
  name                = "${var.container_name}-db"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  server_name         = azurerm_mssql_server.sql.name
  edition             = "Basic" # Remplacé sku_name par edition
}

# 🔹 Déploiement du conteneur
resource "azurerm_container_group" "aci" {
  name                = var.container_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"

  container {
    name   = var.container_name
    image  = "${azurerm_container_registry.acr.login_server}/${var.image_name}:latest"
    cpu    = var.cpu
    memory = var.memory
    
    ports {
      port     = var.port
      protocol = "TCP"
    }

    environment_variables = {
      serverdj_            = azurerm_mssql_server.sql.fully_qualified_domain_name
      portdj_              = "1433"
      usernamedj_          = "admin${var.container_name}"
      passworddj_          = "P@ssword123" # À remplacer par une variable sécurisée
      driverdj_            = "ODBC Driver 18 for SQL Server"
      databasedj_          = "${var.container_name}-db"
      SECRET_KEY_          = "c3f55e56eae44a9191a7c6a3077e5dd372c08c57c55a8c4baf7681a84a3b4d5c"
      ALGORITHM_           = "HS256"
      ACCESS_TOKEN_EXPIRE_MINUTES_ = "2160"
    }
  }
}
