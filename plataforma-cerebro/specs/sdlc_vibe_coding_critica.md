# Análise Comparativa: New SDLC no Contexto de Vibe Coding (Google Framework)

Este documento analisa e critica o projeto da **Plataforma Cérebro de Empresa** frente aos conceitos e pilares do **New SDLC B2B** (especialmente focado no padrão *Spec-Driven Development* na era do *Vibe Coding*).

---

## 📐 O Paradigma: Vibe Coding vs. Spec-Driven Development (SDD)

*   **Vibe Coding (Prototipagem Rápida):** Caracteriza-se por gerar códigos rapidamente via prompts em linguagem natural, frequentemente deixando de lado testes estruturados, segurança ou manutenibilidade de longo prazo (código "descartável" sem controle).
*   **New SDLC (Google/Enterprise Standard):** O desenvolvedor deixa de focar na sintaxe do código e assume o papel de **Arquiteto de Especificações**. O código em si torna-se descartável, enquanto os arquivos de especificação (integração, testes comportamentais e DevOps) são a verdadeira fonte de verdade permanente.

---

## 📊 Matriz de Gaps do Projeto no New SDLC

| Pilar do New SDLC | Status Atual | Descrição no Cérebro de Empresa | Gaps Identificados | Plano de Ação / Mitigação |
| :--- | :---: | :--- | :--- | :--- |
| **1. The Factory Model (Código Descartável)** | **Parcial** | O código em `core/` foi escrito sob demanda seguindo os arquivos em `specs/`. | Se a especificação em `specs/` mudar, o código em `core/` precisa ser atualizado manualmente por um humano. | Implementar um script gerador (`scripts/generate_code.py`) que consome o `specs/integration_specs.md` e usa a API do Gemini para regenerar o código Python automaticamente. |
| **2. Spec-Driven Testing (Gherkin/Feature)** | **Parcial** | Possuímos `specs/test_specs.md` descrevendo os testes de fidelidade e comportamento. | Os arquivos de especificação são markdown textual informal. Não são interpretados programaticamente na execução do pipeline. | Migrar o arquivo `test_specs.md` para um manifesto estruturado (como Gherkin/Cucumber `.feature` ou YAML estruturado) interpretado dinamicamente pelo `eval_pipeline.py`. |
| **3. Zero-Trust Verification Pipeline** | **Aderente** | O `tests/eval_pipeline.py` atua como barreira rígida de qualidade e segurança antes de permitir deploys. | O pipeline avalia comportamento da IA, mas não realiza análises estáticas de segurança no código gerado pelo agente (ex: busca por chaves de API estáticas vazadas). | Adicionar uma ferramenta de análise estática e verificação de políticas (*Policy Checking*) no pipeline de CI/CD para auditar a segurança do código. |
| **4. Context Engineering (Harness Estrito)** | **Aderente** | O motor fornece um ecossistema controlado com conectores, roteador de intenções e guardrail ABAC. | Nenhum gap crítico. O agente opera estritamente limitado pelas ferramentas e regras fornecidas, reduzindo a área de ataque de alucinação. | Manter a documentação de limites de ferramentas atualizada no `integration_specs.md`. |
| **5. Vibe Diff & Intent Verification** | **Aderente** | Implementado o fluxo de "Vibe Diff" e aprovação humana pendente para transações financeiras de alto risco. | Nenhum gap. O "Vibe Diff" impede que o agente execute operações de mutação física sem uma revisão estruturada da sua intenção pelo usuário. | Integrar o Vibe Diff visualmente em painéis administrativos em fases futuras do frontend. |

---

## 🎯 Próximo Passo Prático para SDD Real: O Script de Geração Automática

Para tornar este projeto o "desejo absoluto das empresas" e aderir ao **Factory Model** do New SDLC, devemos implementar o **[Pilar 1]**: Um script de compilação de código que lê a especificação e cospe o arquivo de código-fonte atualizado via IA.

Isso significa que, se a empresa compradora quiser mudar a regra do conector no `specs/integration_specs.md`, ela simplesmente altera a especificação e roda:
`python scripts/generate_code.py core/database/graph_connector.py`
E o motor se reconstrói sozinho.
