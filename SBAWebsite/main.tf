provider "azurerm" {
  features {}
}

# Variables pour la configuration de l'API Django
variable "db_path" {}
variable "username_" {}
variable "email" {}
variable "default_password" {}
variable "first_name" {}
variable "last_name" {}
variable "role" {}

# Variables pour la configuration de la base de données SQL Server (existant)
variable "serverdj_" {}
variable "portdj_" {}
variable "usernamedj_" {}
variable "passworddj_" {}
variable "driverdj_" {}
variable "databasedj_" {}

# Variables pour la configuration de l'API Django
variable "secret_key_" {}
variable "algorithm_" {}
variable "debug" {}
variable "allowed_hosts" {}
variable "api_url" {}
variable "access_token_expire_minutes_" {}

# Variables pour Azure
variable "azure_resource_group" {}
variable "azure_acr_name" {}
variable "azure_container_name" {}
variable "azure_image_name" {}
variable "azure_location" {}
variable "azure_port" {}
variable "dns_label" {}

# Définir le groupe de ressources
resource "azurerm_resource_group" "example" {
  name     = var.azure_resource_group
  location = var.azure_location
}

# Définir le registre ACR
resource "azurerm_container_registry" "example" {
  name                     = var.azure_acr_name
  resource_group_name      = azurerm_resource_group.example.name
  location                 = var.azure_location
  sku                      = "Basic"
  admin_enabled            = true
}

# Définir le conteneur Azure
resource "azurerm_container_group" "example" {
  name                = var.azure_container_name
  location            = var.azure_location
  resource_group_name = azurerm_resource_group.example.name
  os_type             = "Linux"
  dns_name_label = var.dns_label

  # Authentification avec le registre Azure Container Registry
  image_registry_credential {
    server   = azurerm_container_registry.example.login_server
    username = azurerm_container_registry.example.admin_username
    password = azurerm_container_registry.example.admin_password
  }

  container {
    name   = var.azure_container_name
    image  = "${azurerm_container_registry.example.login_server}/${var.azure_image_name}:latest"
    cpu    = "2"
    memory = "4"
    ports {
      port     = tonumber(var.azure_port)
      protocol = "TCP"
    }

    environment_variables = {
      server_                        = var.serverdj_
      port_                          = var.portdj_
      username_                      = var.usernamedj_
      password_                      = var.passworddj_
      driver_                        = var.driverdj_
      database_                      = var.databasedj_
      SECRET_KEY_                    = var.secret_key_
      ALGORITHM_                     = var.algorithm_
      ACCESS_TOKEN_EXPIRE_MINUTES_   = var.access_token_expire_minutes_
      DEBUG                          = var.debug
      ALLOWED_HOSTS                  = var.allowed_hosts
      API_URL                        = var.api_url
    }
  }
}

# Sortie de l'IP publique du conteneur avec DNS
output "container_ip" {
  value = azurerm_container_group.example.ip_address
}

# Générer l'URL du FQDN avec le DNS label
output "container_fqdn" {
  value = "${var.dns_label}.${var.azure_location}.azurecontainer.io"
}
