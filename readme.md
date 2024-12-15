# Workflow de Deploy para LocalStack

Este arquivo `deploy.yml` define um workflow de CI/CD automatizado que é executado no GitHub Actions. O objetivo do workflow é realizar o deploy de recursos simulados da AWS utilizando LocalStack. O LocalStack oferece uma implementação local dos serviços da AWS, permitindo testes e desenvolvimento sem depender de recursos reais na nuvem.

## Visão Geral

Este workflow é acionado sempre que há um push para a branch `master`. Ele inicializa os serviços simulados da AWS, como Cognito, Lambda e API Gateway, utilizando o LocalStack. Além disso, o workflow configura a infraestrutura com o Terraform e realiza algumas operações para testar a interação com esses serviços, como a criação de um usuário no Cognito e a invocação de funções Lambda via API Gateway.

## Estrutura do Arquivo `deploy.yml`


# 1. Acionamento do Workflow (Trigger)
on: 
  push:
    branches: 
      - master
# Descrição: O workflow é ativado automaticamente sempre que há um push na branch master.

# 2. Definição do Job de Deploy
jobs:
  deploy:
    runs-on: ubuntu-latest
# Descrição: Define um único job chamado deploy, que será executado em uma máquina virtual com a imagem Ubuntu (ubuntu-latest).

# 3. Configuração do Serviço LocalStack
    services:
      localstack:
        image: localstack/localstack-pro:latest
        ports:
          - 4566:4566
          - 4510-4559:4510-4559
        env:
          SERVICES: "cognito-idp,sqs,lambda,iam,apigateway"
          DEBUG: "1"
          DATA_DIR: "/tmp/localstack/data"
          LOCALSTACK_AUTH_TOKEN: ${{ secrets.LOCALSTACK_AUTH_TOKEN }}
          AWS_DEFAULT_REGION: us-east-1
          AWS_ACCESS_KEY_ID: test
          AWS_SECRET_ACCESS_KEY: test
          LAMBDA_EXECUTOR: docker
        volumes:
          - "/var/run/docker.sock:/var/run/docker.sock"
# Descrição: Configura o LocalStack como um serviço dentro de um container Docker.
# Imagem: Utiliza a imagem localstack/localstack-pro:latest.
# Portas: Mapeia as portas necessárias para os serviços do LocalStack.
# Variáveis de ambiente: Define a região da AWS, as credenciais para simulação no LocalStack, e os serviços que serão inicializados, como Cognito, Lambda, SQS, IAM e API Gateway.
# Volumes: Monta o docker.sock para permitir que o LocalStack execute containers Docker para funções Lambda.

# 4. Configuração das Variáveis de Ambiente Globais
    env: 
      AWS_ACCESS_KEY_ID: "test"
      AWS_SECRET_ACCESS_KEY: "test"
      AWS_REGION: "us-east-1"
      AWS_DEFAULT_REGION: "us-east-1"
# Descrição: Define as variáveis de ambiente globais, como credenciais da AWS e a região que será utilizada durante a execução do workflow.

# 5. Passos do Workflow

# 5.1. Checkout do Repositório
    steps:
      - name: Checkout Repositório
        uses: actions/checkout@v3
# Descrição: Realiza o checkout do repositório no qual o workflow está sendo executado.

# 5.2. Instalação das Dependências
      - name: Instalar Dependências
        run: |
          sudo apt-get update
          sudo apt-get install -y unzip
# Descrição: Atualiza os pacotes do sistema e instala a ferramenta unzip, necessária para lidar com arquivos compactados, especialmente ao lidar com funções Lambda.

# 5.3. Instalação do Terraform
      - name: Instalar Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0
# Descrição: Instala a versão do Terraform (1.5.0) utilizando a ação oficial do HashiCorp.

# 5.4. Inicialização do Terraform
      - name: Inicializar Terraform
        working-directory: ./infrastructure
        run: |
          terraform init
# Descrição: Inicializa o Terraform no diretório ./infrastructure, onde estão localizados os arquivos de configuração da infraestrutura.

# 5.5. Aplicação do Terraform
      - name: Aplicar Terraform
        working-directory: ./infrastructure
        run: |
          terraform apply -auto-approve
# Descrição: Aplica as configurações do Terraform, criando ou atualizando os recursos definidos, como Lambda, API Gateway e Cognito.

# 5.6. Criação de Usuário no Cognito
      - name: Criar Usuário
        run: |
          aws --endpoint-url=http://localhost:4566 cognito-idp admin-create-user \
          --user-pool-id $(aws --endpoint-url=http://localhost:4566 cognito-idp list-user-pools --max-results 10 --query "UserPools[?Name=='localstack-user-pool'].Id" --output text) \
          --username "12345678900" \
          --user-attributes Name=email,Value=teste@example.com
# Descrição: Utiliza a AWS CLI para criar um usuário no Cognito. O comando busca o ID do Pool de Usuários do LocalStack e cria um usuário com o CPF 12345678900 e o e-mail teste@example.com.

# 5.7. Chamada para Lambda via API Gateway
      - name: Buscar usuário com a Lambda através do API GATEWAY
        run: |
          curl -X POST http://localhost:4566/restapis/$(aws apigateway get-rest-apis --endpoint-url=http://localhost:4566 \
            --query "items[0].id" --output text)/prod/_user_request_/user-check -H "Content-Type: application/json" -d '{"cpf": "12345678900"}'
# Descrição: Realiza uma chamada HTTP utilizando curl para invocar uma função Lambda via API Gateway. A função Lambda será acionada para buscar o usuário com o CPF fornecido.
