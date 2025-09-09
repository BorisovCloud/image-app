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

# output "application_insights_instrumentation_key" {
#   description = "Application Insights instrumentation key"
#   value       = azurerm_application_insights.main.instrumentation_key
#   sensitive   = true
# }

# output "application_insights_connection_string" {
#   description = "Application Insights connection string"
#   value       = azurerm_application_insights.main.connection_string
#   sensitive   = true
# }

# Output for .env file generation
output "env_file_content" {
  description = "Content for .env file"
  value = <<-EOT
# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=${azurerm_storage_account.main.primary_connection_string}
AZURE_STORAGE_ACCOUNT=${azurerm_storage_account.main.name}
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
