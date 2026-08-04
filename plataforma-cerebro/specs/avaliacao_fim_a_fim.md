# Arquitetura de Avaliação Fim-a-Fim (End-to-End Evaluation Blueprint)

Este documento especifica a estratégia de **Avaliação Fim-a-Fim (E2E Eval)** da plataforma, detalhando como avaliar a acurácia de raciocínio da IA, a segurança de acessos, a integridade operacional de banco de dados e o acoplamento de ferramentas via MCP.

---

## 📊 1. As Três Dimensões de Avaliação do Cérebro

Para atestar que a plataforma funciona perfeitamente antes de cada deploy (e monitorar a qualidade em produção), medimos o sistema em três dimensões distintas:

```
                   ┌─────────────────────────────────────────┐
                   │  Dimensões de Avaliação Fim-a-Fim (E2E) │
                   └────────────────────┬────────────────────┘
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                              ▼                              ▼
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│ 1. Qualidade RAG │           │ 2. Ações & Fluxo │           │  3. Guardrails   │
│  (Fidelidade)    │           │ (Chamadas MCP)   │           │   (Segurança)    │
└──────────────────┘           └──────────────────┘           └──────────────────┘
```

### Dimensão 1: Acurácia Cognitiva e RAG (Recuperação de Informação)
*   **Fidelidade (Faithfulness):** Avalia se a resposta da IA baseia-se unicamente nas informações reais retornadas pelo GraphDB/VectorDB. Bloqueia alucinações (ex: inventar que um condomínio tem saldo se a query falhou).
*   **Relevância do Contexto (Context Relevance):** Garante que o RAG recuperou apenas as tabelas e nós necessários, evitando sobrecarga de contexto e latência.
*   **Relevância da Resposta (Answer Relevance):** Mede se a resposta final atende diretamente à necessidade do prompt do usuário.

### Dimensão 2: Integridade de Fluxo e Chamada de Ferramentas (MCP)
*   **Acurácia de Seleção de Ferramenta (Tool Call Accuracy):** Garante que o `RouterAgent` e o `ActionAgent` acionaram a API de pagamento correta (`financial_mcp`) com as variáveis de entrada exatas (valor correto, ID do condomínio correspondente).
*   **Consistência de Estado (State Reconciliation):** Valida se o banco de dados mudou de status corretamente (ex: de `Agendado` para `Pago` após o retorno de sucesso da API) e se o valor debitado coincide com o enviado.

### Dimensão 3: Segurança, Privacidade e Guardrails (Compliance)
*   **Acurácia de Bloqueio ABAC/RBAC:** Testa se acessos não autorizados a relatórios ou rotinas de pagamentos foram 100% interceptados pelo `GuardrailAgent`.
*   **Resistência a Ataques Adversariais:** Simula tentativas de injeção de prompt e tentativas de obtenção de dados privados (PII) de outros condomínios (*cross-tenant leakage*).

---

## 🏗️ 2. Arquitetura de Coleta de Traces em Produção

Para avaliar o processo como um todo, não podemos analisar apenas a entrada e a saída. Precisamos analisar os passos intermediários da cadeia de raciocínio. Usamos o padrão **OpenTelemetry** para registrar e rastrear a execução:

```
[ Usuário ] -> [ API Gateway ] -> [ Router Agent ] ──(Gera Trace ID)──> [ Action Agent ] 
                                                                               │
[ MLOps Dashboards ] <── [ Banco de Traces (Jaeger/Phoenix) ] <──(Registra Span)┘
```

1.  **Trace ID Único:** Cada requisição do usuário recebe um `Trace ID` que acompanha o fluxo de todos os sub-agentes.
2.  **Registro de Spans (Passos):** Cada agente registra seu tempo de execução, prompts enviados ao LLM, contexto retornado pelas consultas e o payload enviado às ferramentas MCP.
3.  **Análise LLM-as-a-Judge (Runtime):** Amostras de traces de produção são enviadas diariamente a um pipeline de avaliação estocástica para identificar se houve degradação na qualidade do modelo ou nas respostas (*concept drift*).

---

## 🧪 3. Workflow de Execução de Evals no CI/CD

O pipeline do Golden Dataset (`tests/eval_pipeline.py`) atual simula este comportamento de forma automatizada:

1.  **Criação do Cenário Limpo:** O pipeline inicializa a Engine com uma base de dados mock limpa.
2.  **Injeção de Casos Extremos:** Executa requisições de Happy Path, de violação de limite financeiro e de credenciais inválidas.
3.  **Validação Cruzada:** O pipeline verifica o retorno final, o histórico de memória gerado no `MemoryStore` e a integridade da query no `GraphConnector`.
4.  **Score e Gate de Deploy:** Calcula a acurácia geral. Se o score mínimo exigido (ex: 100% em segurança, 95% em fidelidade) for alcançado, o contêiner Docker do tenant é assinado e liberado para deploy em produção na nuvem SaaS.
