provider "aws" {
  skip_requesting_account_id = true
  access_key                  = "test"
  secret_key                  = "test"
  region                      = "us-east-1"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  endpoints {
    lambda          = "http://localhost:4566"
    apigateway      = "http://localhost:4566"
    iam             = "http://localhost:4566"
    s3              = "http://localhost:4566"
    cloudformation  = "http://localhost:4566"
    cognitoidp      = "http://localhost:4566"
    rds             = "http://localhost:4566"
  }
}