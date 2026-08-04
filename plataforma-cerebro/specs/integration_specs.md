# Especificação de Integração (Integration Specs)

Esta especificação define os contratos de interface e barramentos de conexão do **Cérebro de Empresa**. Como um sistema multicliente baseado em contêineres isolados (Single-Tenant), toda a camada de integração é configurada dinamicamente através de injeção de variáveis de ambiente e arquivos manifestos.

---

## 🔌 1. Conexão com Bancos de Dados de Clientes

### A. Banco de Dados Gráfico (Neo4j)
*   **Protocolo:** Bolt/Bolt+Routing (Neo4j Aura ou instância privada Docker)
*   **Contrato de Inicialização:**
    ```python
    class Neo4jConfig:
        uri: str       # bolt:// ou neo4j://
        username: str
        password: str
        database: str  # Nome lógico (padrão: "neo4j")
    ```
*   **Resolução de Esquema Dinâmica:**
    O banco de dados gráfico do cliente deve conter um dicionário de metadados em nós do tipo `(:SchemaNode)` para descrever as chaves estrangeiras dinâmicas e o relacionamento entre os domínios corporativos.

### B. Banco de Dados de Vetores (Vector DB)
*   **Provedor Padrão:** PGVector (PostgreSQL) para evitar custos excessivos de serviços terceirizados, ou ChromaDB para deploys compactos.
*   **Contrato de Inicialização:**
    ```python
    class VectorDbConfig:
        host: str
        port: int
        database: str
        collection_name: str
        embedding_model: str # ex: "text-embedding-3-small"
    ```

---

## 🛠️ 2. Integração de Sistemas via MCP (Model Context Protocol)

O **ActionAgent** descobre ferramentas expostas dinamicamente a partir dos servidores MCP mapeados no manifesto do cliente.

### Estrutura de Servidores MCP Mapeados:
```yaml
mcp_servers:
  financial_api:
    command: "node"
    args: ["/opt/mcp/dist/financial-mcp.js"]
    env:
      API_KEY: "${COMPANY_API_KEY}"
  tickets_system:
    command: "python"
    args: ["/opt/mcp/tickets_mcp.py"]
```

### Contrato de Chamada de Ferramenta (Tool Call Contract):
Todas as ações executadas pelos sub-agentes corporativos devem seguir a especificação JSON-RPC do MCP:

*   **Request:**
    ```json
    {
      "jsonrpc": "2.0",
      "method": "tools/call",
      "params": {
        "name": "executar_pagamento",
        "arguments": {
          "valor": 12500.0,
          "condominio_id": "C99",
          "favorecido_pix": "chave@pix.com"
        }
      },
      "id": 1
    }
    ```
*   **Response (Sucesso):**
    ```json
    {
      "jsonrpc": "2.0",
      "result": {
        "content": [
          {
            "type": "text",
            "text": "{\"status\": \"processado\", \"transacao_id\": \"TX_89231\"}"
          }
        ]
      },
      "id": 1
    }
    ```

---

## 🛡️ 3. Protocolo de Reconciliação e Isolamento Semântico

*   **Pilar Crítico:** Em hipótese alguma o core pode misturar caches de RAG ou históricos de memória entre contêineres.
*   **Trace de Auditoria:** Toda ação de escrita executada pelo MCP deve obrigatoriamente registrar um evento de conciliação bi-temporal (`valid_time` e `system_time`) no banco relacional auxiliar e no Grafo, no formato:
    ```cypher
    CREATE (t:TransactionLog {
        id: $txId,
        agent: "ActionAgent",
        timestamp: datetime(),
        status: "Enviado",
        payload: $jsonPayload
    })
    ```
