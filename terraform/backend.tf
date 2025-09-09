terraform {
  backend "azurerm" {
    resource_group_name  = "main-infra"
    storage_account_name = "terraformstate2076"
    container_name       = "tfstate"
  }
}