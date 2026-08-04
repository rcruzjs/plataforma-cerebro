# Blueprint de DevOps e Deployment (DevOps Blueprint)

Este documento especifica a infraestrutura automatizada e o fluxo de implantação (*deployment*) para o modelo de **SaaS Gerenciado com Instâncias Isoladas (Single-Tenant)**.

---

## 🏗️ 1. Arquitetura da Nuvem SaaS

Cada empresa cliente possui sua própria sandbox rodando o contêiner do **Cérebro de Empresa**.

```
                   [ Tráfego do Usuário / API Gateway ]
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
      [ Cliente A ]          [ Cliente B ]          [ Cliente C ]
   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │ Docker Container │   │ Docker Container │   │ Docker Container │
   │ (Python Engine)  │   │ (Python Engine)  │   │ (Python Engine)  │
   └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
            ▼                      ▼                      ▼
     ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
     │ Neo4j Aura   │       │ Neo4j Aura   │       │ Neo4j Aura   │
     │ (Base A)     │       │ (Base B)     │       │ (Base C)     │
     └──────────────┘       └──────────────┘       └──────────────┘
```

---

## 🐋 2. Especificação do Contêiner (Dockerfile Core)

O contêiner do motor corporativo expõe uma API REST leve (FastAPI) para interação do usuário e integrações de webhook.

```dockerfile
# Dockerfile da Plataforma Cérebro
FROM python:3.11-slim

# Instalar dependências de build básicas
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar dependências primeiro para cacheamento de camadas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte
COPY core/ ./core
COPY config/default_config.yaml ./config/default_config.yaml

# Variáveis de Ambiente Injetadas na Inicialização pelo SaaS Controller
ENV COMPANY_CONFIG_PATH="/app/config/company_config.yaml"
ENV PORT=8000

EXPOSE 8000

CMD ["python", "-m", "core.engine"]
```

---

## ⚙️ 3. Injeção de Configuração por Cliente (Config Injector)

No momento em que um novo cliente se cadastra na plataforma, o painel do SaaS (Control Plane) realiza o provisionamento automático:

1.  **Criação de Infraestrutura:** Cria um banco Neo4j Aura dedicado e um banco PostgreSQL para vetores.
2.  **Criação de Segredos:** Gera credenciais seguras e as armazena no AWS Secrets Manager ou HashiCorp Vault.
3.  **Deploy do Container:** Inicializa o contêiner Docker injetando a montagem do volume para `/app/config/company_config.yaml` com as APIs, segredos e conexões do cliente.

### Exemplo de Configuração de Orquestração (docker-compose do Cliente):
```yaml
version: '3.8'

services:
  cerebro-engine:
    image: plataforma-cerebro-core:latest
    ports:
      - "8080:8000"
    volumes:
      - ./company_config.yaml:/app/config/company_config.yaml
    environment:
      - NEO4J_URI=bolt://neo4j-aura-instance:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=segredo-cliente-super-secreto
      - OPENAI_API_KEY=sk-proj-chave-cliente
    restart: always
```
