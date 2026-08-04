# 🧠 Plataforma Cérebro de Empresa (Enterprise Brain Platform)

> **Motor Cognitivo Agêntica Multicliente B2B para Orquestração Corporativa com Segurança de 7 Pilares e Desenvolvimento Orientado a Especificações (Spec-Driven Development)**

---

## 💎 Visão Geral do Produto

Esta plataforma permite a implantação de um **Cérebro de Empresa** customizado e seguro para grandes organizações (SaaS Gerenciado Single-Tenant por contêiner). Ela consolida silos de dados em um Grafo Semântico (Neo4j), realiza buscas semânticas híbridas (RAG) e executa ações de negócios no mundo real via barramentos do **Model Context Protocol (MCP)**, protegida por camadas robustas de guardrails corporativos.

---

## 🛡️ Segurança Agêntica Extrema: Mitigação de Gaps (7 Pilares)

Implementamos proteções contra os principais vetores de vulnerabilidades em sistemas baseados em inteligência artificial corporativa:

1.  **Zero Ambient Authority (JIT Credentials - Pilar 3):** O agente de execução de ferramentas MCP ([action.py](file:///c:/Users/rcruz/.gemini/antigravity-ide/scratch/meu-book/plataforma-cerebro/core/agents/action.py)) não possui privilégios de acesso estáticos ou permanentes. Chamadas de escrita financeira (como transferências bancárias) exigem a assinatura dinâmica de um token de sessão de usuário válido (`X-User-Session-Token`), que expira de forma contínua (*Downscoped JIT Credentials*).
2.  **Human-In-The-Loop & Vibe Diff (Pilar 4 & 5):** Qualquer transação financeira de mutação solicitada de forma autônoma pela IA que exceda R$ 10.000,00 é retida e gravada com status `PENDING` na base persistente. O motor gera um **Vibe Diff** (resumo em linguagem natural sobre o impacto físico e a justificativa da retenção) e o expõe para aprovação manual de um analista autorizado pelo endpoint `/api/v1/approve`.
3.  **Intent Drift Detection (Pilar 7):** Monitoramento em tempo real do roteamento de ferramentas. Se o agente de execução tentar acionar ferramentas financeiras críticas em um fluxo de trabalho com intenção inicial roteada como puramente informativa (ex: dúvidas ou relatórios), a operação é bloqueada de forma imediata por violação de desvio de escopo (*Intent Drift*).
4.  **HMAC-SHA256 Payload Signing:** Todas as chamadas de transações destinadas a servidores MCP são assinadas digitalmente via **HMAC-SHA256** utilizando a chave criptográfica simétrica exclusiva do tenant do cliente. O servidor MCP valida a integridade do payload antes de autorizar o payout, neutralizando ataques *Man-in-the-Middle*.
5.  **Grafo Protegido contra Cypher Injection:** O conector do Neo4j valida sintaticamente todas as queries geradas por IA, aplicando bloqueios estritos contra palavras-chave destrutivas (`DELETE`, `DETACH`, `REMOVE`, `CREATE`, `SET`) para garantir que o Grafo Semântico opere exclusivamente em modo leitura (*Read-Only*) contra injeção de código.

---

## 🏗️ Metodologia New SDLC e Vibe Coding

Adotamos as melhores práticas do **New SDLC (Software Development Life Cycle)** agêntico, onde as especificações técnicas escritas em linguagem natural são as verdadeiras fontes permanentes de verdade, e o código operacional é considerado descartável/compilável:

### A. O Modelo Fábrica (Spec compiler com Self-Healing)
*   **Compilador agêntico (`scripts/generate_code.py`):** Este utilitário recebe um arquivo de especificação markdown (ex: `specs/integration_specs.md`) e um arquivo de destino e reconstrói o código Python inteiro chamando a API do Gemini.
*   **Mecanismo de Auto-Correção (*Self-Healing*):** Se o código gerado quebrar a suíte de testes corporativos, o compilador entra em loop automático (até 3 tentativas). Ele extrai o log de erros do traceback, repassa como feedback para a IA do Gemini e regenera o código até que as validações passem com 100% de sucesso. Em caso de falha irreversível, realiza o rollback seguro para a versão operacional anterior.

### B. Especificações Executáveis (Gherkin/Feature)
*   Traduzimos os casos de uso de teste da plataforma no arquivo Gherkin formal **[test_specs.feature](file:///c:/Users/rcruz/.gemini/antigravity-ide/scratch/meu-book/plataforma-cerebro/specs/test_specs.feature)**.
*   O runner do pipeline de CI/CD (**[eval_pipeline.py](file:///c:/Users/rcruz/.gemini/antigravity-ide/scratch/meu-book/plataforma-cerebro/tests/eval_pipeline.py)**) lê e interpreta as especificações Gherkin (`Given/And/When/Then`) dinamicamente, rodando as asserções em runtime contra o Cérebro de Empresa.

### C. Auditoria Estática de Segurança (Policy Checker)
*   O script **[verify_policy.py](file:///c:/Users/rcruz/.gemini/antigravity-ide/scratch/meu-book/plataforma-cerebro/scripts/verify_policy.py)** analisa estaticamente a base de código do projeto no início de cada pipeline. Ele detecta chaves de API/segredos hardcoded, comandos de execução arbitrária (`eval`/`exec`) e instalações de dependências dinâmicas não mapeadas, bloqueando deploys inseguros.

---

## 📂 Estrutura do Projeto

*   **`config/`**: Arquivos de configuração dos tenants (ex: `default_config.yaml`, `company_config.yaml`).
*   **`specs/`**: Especificações de arquitetura, testes funcionais e infraestrutura:
    *   [integration_specs.md](file:///c:/Users/rcruz/.gemini/antigravity-ide/scratch/meu-book/plataforma-cerebro/specs/integration_specs.md) - Contratos de API, drivers Neo4j e barramentos MCP.
    *   [test_specs.md](file:///c:/Users/rcruz/.gemini/antigravity-ide/scratch/meu-book/plataforma-cerebro/specs/test_specs.md) - Especificações do Gherkin e auditoria estática.
    *   [test_specs.feature](file:///c:/Users/rcruz/.gemini/antigravity-ide/scratch/meu-book/plataforma-cerebro/specs/test_specs.feature) - Especificações executáveis formatadas em Gherkin.
    *   [sdlc_vibe_coding_critica.md](file:///c:/Users/rcruz/.gemini/antigravity-ide/scratch/meu-book/plataforma-cerebro/specs/sdlc_vibe_coding_critica.md) - Ficha técnica de aderência ao New SDLC de Vibe Coding.
    *   [seguranca_7_pilares.md](file:///c:/Users/rcruz/.gemini/antigravity-ide/scratch/meu-book/plataforma-cerebro/specs/seguranca_7_pilares.md) - Mitigações frente à 7-Pillar Architecture.
*   **`core/`**: O motor central (*engine*) em Python: agentes cognitivos, adaptadores de banco, e arquivos do **Painel Admin Web** (`static/`).
*   **`scripts/`**: Utilitários de automação e auditorias de políticas do SDLC:
    *   `generate_code.py` - Compilador de specs com auto-correção (*Self-Healing*).
    *   `verify_policy.py` - Linting estático de segurança e segredos vazados.
    *   `provision_tenant.py` - Provisionador automatizado para novos condomínios/tenants.
*   **`tests/`**: Suítes de testes de regressão unitários e pipeline de integração CI/CD.

---

## ⚡ Inicialização e Execução

### 1. Instalação
Com o Python 3.10+ configurado, instale as dependências:
```bash
pip install -r requirements.txt
```

### 2. Rodando Testes Unitários
```bash
python -m unittest tests/test_engine.py
```

### 3. Rodando o Pipeline de Integração e Segurança (Gherkin + Policy Lint)
```bash
python tests/eval_pipeline.py
```

### 4. Executando o Dashboard Administrativo Web
Para iniciar a API local e abrir a console de auditoria de histórico de conversas e fila de aprovação de transações com Vibe Diff:
```bash
python -m uvicorn core.api:app --host 0.0.0.0 --port 8000
```
*   Acesse no navegador: **[http://localhost:8000/](http://localhost:8000/)**
*   API Key de Gateway padrão: `prod-sec-key-1298`
*   JIT Token de Sessão padrão: `token-valido-123`

### 5. Provisionando um Novo Tenant Isolado
Para criar a infraestrutura configurada e o script de execução em portas isoladas para um novo condomínio cliente:
```bash
python scripts/provision_tenant.py --name "Condominio Vista Bella" --port 8001
```
*   Isso criará a configuração `config/tenant_condominio_vista_bella_config.yaml` e o script de inicialização `run_condominio_vista_bella.bat` na porta configurada.
