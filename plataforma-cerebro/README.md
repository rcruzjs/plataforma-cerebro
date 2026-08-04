# 🧠 Plataforma Cérebro de Empresa (Enterprise Brain Platform)

> **Motor Cognitivo Multicliente de IA Agêntica para Orquestração Corporativa**  
> Desenvolvido sob o padrão **SDD (Spec-Driven Development)** de alta fidelidade técnica e orquestração de infraestrutura isolada (Single-Tenant).

---

## 💎 Visão Geral do Produto

Esta plataforma permite a implantação de um **Cérebro de Empresa** customizado e seguro para grandes organizações. Ele atua como uma camada cognitiva unificada que:
1. **Consome silos de dados** e os organiza em um **Grafo de Conhecimento Semântico** (Neo4j).
2. **Orquestra ações no mundo real** via APIs e integrações usando o **Model Context Protocol (MCP)**.
3. **Garante segurança absoluta** baseada em regras de controle de acesso dinâmico (**ABAC/RBAC**).
4. **Evita regressão** rodando validações contínuas de fidelidade de RAG contra um **Golden Dataset**.

---

## 🏗️ Diferenciais Arquiteturais (Estado da Arte)

* **Desenvolvimento Orientado a Especificações (SDD):** Toda a infraestrutura, testes e integrações são descritos primeiramente em especificações formais de projeto na pasta `specs/`. O código atua estritamente como executor dessas especificações.
* **Isolamento de Contêineres (SaaS Single-Tenant):** Cada empresa parceira possui sua própria sandbox contêinerizada. Isso isola completamente a memória, chaves de API, banco de dados vetorial e Neo4j Aura de cada cliente, garantindo conformidade total com a LGPD e políticas corporativas de segurança.
* **Injeção de Configuração Dinâmica:** O motor (`core/engine.py`) carrega as configurações padrões da plataforma e as mescla de forma transparente com as especificidades do cliente fornecidas em `/config/company_config.yaml`.

---

## 📂 Estrutura do Projeto

*   **`config/`**: Manifestos de configuração. `company_config.yaml` descreve as conexões do banco de dados, limites de pagamento e servidores MCP do cliente.
*   **`specs/`**: Especificações técnicas formais do sistema:
    *   [integration_specs.md](specs/integration_specs.md) - Contratos de API, drivers Neo4j e barramentos MCP.
    *   [test_specs.md](specs/test_specs.md) - Modelagem do Golden Dataset e métricas de assertividade.
    *   [devops_blueprint.md](specs/devops_blueprint.md) - Dockerfiles e fluxos de injeção de segredos no SaaS.
*   **`core/`**: O motor principal (*engine*) escrito em Python estruturado com conectores e agentes.
*   **`tests/`**: Suítes de testes unitários e o script avaliador contínuo do Golden Dataset.

---

## ⚡ Inicialização e Execução

### 1. Instalação das Dependências
Com o Python instalado, configure seu ambiente virtual e instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

### 2. Rodando Testes Unitários do Core
Valide que a engine e as regras do Guardrail / Roteador estão íntegras:
```bash
python -m unittest tests/test_engine.py
```

### 3. Rodando a Validação Contínua (CI/CD do Golden Dataset)
Simule o pipeline de deploy que valida a assertividade e segurança do modelo contra o dataset de ouro:
```bash
python tests/eval_pipeline.py
```
*(Nota: Em caso de falha de acurácia ou quebra de guardrail, o pipeline retorna código de saída `1` bloqueando o deploy automaticamente).*
