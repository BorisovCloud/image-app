output "resource_group_name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "storage_account_primary_key" {
  description = "Primary access key for the storage account"
  value       = azurerm_storage_account.main.primary_access_key
  sensitive   = true
}

output "storage_account_connection_string" {
  description = "Connection string for the storage account"
  value       = azurerm_storage_account.main.primary_connection_string
  sensitive   = true
}

output "storage_account_primary_blob_endpoint" {
  description = "Primary blob endpoint for the storage account"
  value       = azurerm_storage_account.main.primary_blob_endpoint
}

output "uploads_container_name" {
  description = "Name of the uploads container"
  value       = azurerm_storage_container.uploads.name
}

output "managed_identity_client_id" {
  description = "Client ID of the user-assigned managed identity"
  value       = azurerm_user_assigned_identity.main.client_id
}

output "managed_identity_principal_id" {
  description = "Principal ID of the user-assigned managed identity"
  value       = azurerm_user_assigned_identity.main.principal_id
}

# Output for .env file generation
output "env_file_content" {
  description = "Content for .env file"
  value = <<-EOT
# Authentication Method (use managed identity for production)
USE_MANAGED_IDENTITY=true

# Managed Identity Configuration
AZURE_STORAGE_ACCOUNT_NAME=${azurerm_storage_account.main.name}
AZURE_STORAGE_ACCOUNT_URL=${azurerm_storage_account.main.primary_blob_endpoint}
AZURE_CLIENT_ID=${azurerm_user_assigned_identity.main.client_id}

# Fallback Configuration (for local development)
AZURE_STORAGE_CONNECTION_STRING=${azurerm_storage_account.main.primary_connection_string}
AZURE_STORAGE_KEY=${azurerm_storage_account.main.primary_access_key}

# Container configuration
AZURE_BLOB_CONTAINER=${azurerm_storage_container.uploads.name}
AZURE_PUBLIC_CONTAINER=${var.blob_container_access_type == "blob" ? "true" : "false"}

# Flask configuration
FLASK_SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_DEBUG=false

EOT
  sensitive = true
}

output "acr_name" {
  description = "Azure Container Registry name"
  value       = azurerm_container_registry.main.name
}