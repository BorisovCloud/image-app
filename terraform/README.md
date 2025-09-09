# Image Upload App - Terraform Infrastructure

This directory contains Terraform configuration to provision Azure infrastructure for the Image Upload Flask application.

## 🏗️ Infrastructure Components

### Resources Created:
- **Resource Group** - Container for all resources
- **Storage Account** - Azure Blob Storage for image uploads
- **Storage Containers** - `uploads` and `thumbnails` containers
- **Application Insights** - Monitoring and telemetry

### Features:
- ✅ Configurable storage replication and performance tier
- ✅ CORS enabled for web applications
- ✅ Blob versioning and soft delete (7 days retention)
- ✅ TLS 1.2 minimum security
- ✅ Randomized storage account names for global uniqueness
- ✅ Comprehensive output values for application configuration

## 📋 Prerequisites

1. **Azure CLI** installed and authenticated
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   ```

2. **Terraform** installed (v1.0+)
   ```bash
   # Windows (chocolatey)
   choco install terraform
   
   # macOS (homebrew)
   brew install terraform
   
   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   ```

3. **Azure Subscription** with contributor access

## 🚀 Quick Start

### 1. Configure Variables

```bash
# Copy the example file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your desired values
notepad terraform.tfvars  # Windows
vim terraform.tfvars      # Linux/Mac
```

### 2. Initialize Terraform

```bash
cd terraform
terraform init
```

### 3. Plan Deployment

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

### 5. Get Configuration for Web App

```bash
# Get sensitive outputs (connection strings, keys)
terraform output -json

# Generate .env file for the webapp
terraform output -raw env_file_content > ../webapp/.env
```

## ⚙️ Configuration Options

### terraform.tfvars Variables:

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `location` | Azure region | "East US" | Any Azure region |
| `environment` | Environment name | "dev" | dev, staging, prod |
| `project_name` | Project name for resources | "imageapp" | alphanumeric |
| `storage_account_tier` | Storage performance | "Standard" | Standard, Premium |
| `storage_replication_type` | Replication type | "LRS" | LRS, GRS, RAGRS, ZRS |
| `blob_container_access_type` | Container access | "private" | private, blob, container |

### Container Access Types:

- **`private`** - Private access, requires SAS tokens (most secure)
- **`blob`** - Public read access for individual blobs
- **`container`** - Public read access for containers and blobs

## 📊 Outputs

After deployment, Terraform provides these outputs:

```bash
# Resource information
terraform output resource_group_name
terraform output storage_account_name
terraform output storage_account_primary_blob_endpoint

# Sensitive configuration (use carefully)
terraform output storage_account_connection_string
terraform output storage_account_primary_key
terraform output application_insights_instrumentation_key
```

## 🔧 Advanced Usage

### Custom Resource Tags

```hcl
# In terraform.tfvars
tags = {
  Project     = "Image Upload App"
  Environment = "Production"
  ManagedBy   = "Terraform"
  Owner       = "Platform Team"
  CostCenter  = "Engineering"
}
```

### Different Environments

```bash
# Development
terraform workspace new dev
terraform apply -var="environment=dev"

# Production
terraform workspace new prod
terraform apply -var="environment=prod" -var="storage_replication_type=GRS"
```

### Backend Configuration (Recommended for Teams)

Create `backend.tf`:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "terraformstatesa"
    container_name       = "tfstate"
    key                  = "imageapp.terraform.tfstate"
  }
}
```

## 🛡️ Security Considerations

### Access Control
- Storage account uses TLS 1.2 minimum
- Resource Group provides boundary for access control
- Use private containers with SAS tokens for production

### Key Management
- Store sensitive outputs securely
- Rotate storage account keys regularly
- Use Azure Key Vault for production secrets

### Network Security
```hcl
# Add to storage account for network restrictions
network_rules {
  default_action             = "Deny"
  ip_rules                   = ["YOUR_PUBLIC_IP"]
  virtual_network_subnet_ids = [azurerm_subnet.example.id]
}
```

## 🧹 Cleanup

```bash
# Destroy all resources
terraform destroy

# Destroy specific resources
terraform destroy -target=azurerm_storage_account.main
```

## 🔍 Troubleshooting

### Common Issues:

**Storage account name conflicts:**
```bash
# The random suffix should prevent this, but if it occurs:
terraform apply -replace=random_string.suffix
```

**Permission errors:**
```bash
# Check Azure CLI authentication
az account show
az account list-locations --output table
```

**State file issues:**
```bash
# Refresh state
terraform refresh

# Import existing resource
terraform import azurerm_resource_group.main /subscriptions/SUB_ID/resourceGroups/RG_NAME
```

## 📁 File Structure

```
terraform/
├── main.tf                    # Provider configuration
├── variables.tf               # Variable definitions
├── resources.tf               # Resource definitions
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example variables
└── README.md                  # This file
```

## 🔗 Integration with Web App

After running Terraform:

1. **Generate .env file:**
   ```bash
   terraform output -raw env_file_content > ../webapp/.env
   ```

2. **Update Flask app configuration:**
   ```bash
   cd ../webapp
   python app.py  # Should now connect to Azure resources
   ```

3. **Verify deployment:**
   - Check Azure Portal for created resources
   - Test image upload functionality
   - Monitor Application Insights for telemetry

## 📚 Additional Resources

- [Terraform Azure Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Storage Account Best Practices](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview)
- [Azure Resource Naming Conventions](https://docs.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/naming-and-tagging)
