resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_cognito_user_pool" "user_pool" {
  name = "localstack-user-pool"

  schema {
    attribute_data_type = "String"
    name                = "email"
    required            = true
    mutable             = true
  }

  username_attributes = []
  auto_verified_attributes = ["email"]
}

resource "aws_lambda_function" "check_user_by_cpf" {
  filename         = "lambda.zip" 
  function_name    = "check-user-by-cpf"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  timeout          = 10

  source_code_hash = filebase64sha256("lambda.zip")
  
  environment {
    variables = {
      USER_POOL_ID = aws_cognito_user_pool.user_pool.id
    }
  }
}

resource "aws_api_gateway_rest_api" "api" {
  name        = "API-Gateway-CheckUser"
  description = "API Gateway para chamar a Lambda check-user-by-cpf"
}

resource "aws_api_gateway_resource" "user_check" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "user-check"
}

resource "aws_api_gateway_method" "get_user_check" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.user_check.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.user_check.id
  http_method             = aws_api_gateway_method.get_user_check.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.check_user_by_cpf.arn}/invocations"
}

resource "aws_lambda_permission" "lambda_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.check_user_by_cpf.function_name
  principal     = "apigateway.amazonaws.com"
}
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.api.id
}


resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = "prod"
}
