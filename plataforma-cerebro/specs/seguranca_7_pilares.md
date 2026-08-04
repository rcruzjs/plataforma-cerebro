# Diagnóstico de Segurança: Os 7 Pilares de Segurança Agêntica

Este documento analisa a conformidade do **Cérebro de Empresa** com o framework **The 7-Pillar Agent Security Architecture** (Arquitetura de Segurança de Agentes de 7 Pilares), identificando os níveis de aderência e apontando os camais de correção (*mitigações*) para produção.

---

## 📊 Matriz de Aderência aos 7 Pilares

| Pilar de Segurança | Status Atual | Descrição no Projeto | Gaps Identificados | Plano de Mitigação |
| :--- | :---: | :--- | :--- | :--- |
| **1. Sandboxing (Kernel-Level)** | **Parcial** | Utiliza isolamento de contêineres Docker (Single-Tenant por cliente). | Docker não evita escape de contêiner se o contêiner rodar como root ou se houver vulnerabilidade no kernel do host. | Configurar o runtime dos contêineres utilizando **gVisor** (Google) ou **Firecracker microVMs** para execução isolada. |
| **2. Supply Chain Defence** | **Ausente** | Instalação de pacotes estáticos no build do Docker. | Se um Agente MCP puder instalar pacotes dinamicamente (ex: `pip/npm install`), ele pode ser vítima de *slopsquatting*. | Bloquear execuções de comandos de instalação em runtime. Lock estrito de versões no `requirements.txt` com hash. |
| **3. Zero Ambient Authority** | **Parcial** | O `GuardrailAgent` intercepta requisições baseado no papel do usuário. | O `ActionAgent` possui acesso direto e permanente à `FINANCIAL_API_KEY` corporativa de escrita. | Implementar **JIT (Just-In-Time) Credentials**. O token da API corporativa deve ser temporário e com escopo reduzido ao usuário logado. |
| **4. Human-in-the-Loop** | **Parcial** | Limites rígidos (ex: R$ 50.000,00) que barram a execução automática da IA. | Não há uma fila formal de aprovação interativa integrada ao fluxo da API. | Criar o estado `PENDING_APPROVAL` na API e expor endpoints de aprovação manual para o analista financeiro. |
| **5. Vibe Diff** | **Ausente** | O sistema executa as ações e atualiza a base diretamente. | O usuário não consegue ver e revisar o "antes e depois" estruturado da ação que a IA propõe realizar. | Gerar um "Dry-Run" (pré-visualização) do payload ou alterações no banco de dados e exigir confirmação visual do usuário. |
| **6. Agent Observability** | **Aderente** | O E2E blueprint especifica coletas de Traces e Spans via OpenTelemetry (OTEL). | Rastreamento e gráficos de MLOps ainda não estão consolidados em produção. | Acoplar a biblioteca OpenInference e exportar traces para o **Arize Phoenix** ou **Jaeger** hospedados no SaaS. |
| **7. Intent Drift Detection** | **Parcial** | O `RouterAgent` detecta a intenção principal no início da requisição. | Em execuções multi-etapas, o agente pode sofrer "desvio de intenção" e iniciar ações não autorizadas a meio caminho. | Implementar um validador de etapa (Step-by-step Guardrail) que compara a ação atual com a intenção inicial autorizada. |

---

## 🛡️ Detalhamento dos Gaps Mais Críticos

### 1. Zero Ambient Authority (Autoridade Base Zero)
*   **O Risco:** No estado atual, se o contêiner for invadido ou o agente sofrer jailbreak, o invasor terá acesso à `FINANCIAL_API_KEY` global que tem poder total de pagamento no cliente.
*   **A Correção:** A chave global de API não deve ficar no contêiner do agente. As ferramentas MCP devem receber um Token de Usuário (OAuth downscoped) gerado dinamicamente para aquela sessão, limitando a ação da IA aos limites estritos do próprio usuário.

### 2. O conceito de "Vibe Diff"
*   **O Risco:** O Agente de Ações decide fazer um pagamento. Ele gera os dados e os grava no CNAB. Se houver um erro de tradução lógica, o dinheiro é enviado incorretamente.
*   **A Correção:** Antes de transmitir qualquer arquivo para o banco, o sistema deve suspender a execução, exportar um objeto estruturado descrevendo `{"de": conta_a, "para": conta_b, "valor": x}` (o Vibe Diff) e exigir assinatura digital do usuário (Human-in-the-loop).
