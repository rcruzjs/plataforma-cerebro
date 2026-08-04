# Diagnóstico e Mapeamento de Coleta para o Cérebro de Empresa

Este documento serve como um guia interativo de levantamento de informações para mapear ativos de conhecimento, processos e dados em uma organização. O objetivo é identificar as **lacunas (gaps)** críticas de dados e processos antes de iniciar a construção da Camada Semântica e do modelo de agentes da IA.

---

## 📊 Matriz de Levantamento e Maturidade de Dados

Classifique cada item conforme sua disponibilidade:
*   **[D] Disponível:** Documentado, atualizado e acessível via arquivo ou API.
*   **[P] Parcial:** Existe fisicamente ou digitalmente, mas está desatualizado ou incompletamente mapeado.
*   **[T] Tácito:** Existe apenas como conhecimento prático na cabeça das pessoas (sem registro formal).
*   **[I] Inexistente:** O processo ou dado não é mapeado nem estruturado na organização.

| Camada do Cérebro     | Ativo de Conhecimento / Processo                  | Formato Esperado          | Status (D/P/T/I) | Repositório / Fonte | Complexidade de Ingestão |
| :---                  | :---                                              | :---                       | :---:| :---| :---:|
| **1. Ingestão**       | Glossário de Termos e Siglas (Dicionário)         | PDF, Wiki, Notion          | | | Baixa |
| **1. Ingestão**       | Manuais de Integração e Onboarding                | PDF, Docs                  | | | Baixa |
| **1. Ingestão**       | Histórico de Chats de Suporte/Atendimento         | CSV, API (Zendesk)         | | | Alta  |
| **2. Grafo Semântico**| Esquemas de Banco de Dados (Dicionário de Dados)  | SQL DDL, PDF               | | | Média |
| **2. Grafo Semântico**| Mapeamento de Métricas de Negócio (ex: LTV, CAC)  | Planilhas, Docs            | | | Média |
| **3. Memória**        | FAQs Internos e Manuais de Resolução de Problemas | PDF, Wiki                  | | | Baixa |
| **3. Memória**        | Transcrições de Reuniões e Treinamentos           | MP4, TXT, VTT              | | | Média |
| **4. Recuperação**    | Base de Conhecimento Compartilhada (Wiki)         | Notion, Confluence         | | | Média |
| **5. Ação**           | Playbooks de Vendas, Suporte ou Operação          | PDF, Vídeo                 | | | Média |
| **5. Ação**           | Credenciais e Documentação de APIs Internas       | Swagger/OpenAPI            | | | Alta  |
| **6. Governança**     | Regras de Compliance e LGPD aplicadas a dados     | PDF, Word                  | | | Baixa |
| **6. Governança**     | Matriz de Controle de Acesso e Permissões (RBAC)  | Planilha, Active Directory | | | Alta  |

---

## 🔍 Detalhamento das Principais Lacunas (Gaps)

Ao realizar a coleta com os Especialistas de Negócio (SMEs), investigue e documente os seguintes pontos de atenção:

### 1. Lacuna de Glossário Único (Semantic Alignment Gap)
*   **O problema:** Áreas diferentes definem o mesmo termo (ex: "cliente ativo") de formas diferentes.
*   **Como identificar:** Pergunte a três departamentos distintos como eles calculam a receita ou contam novos clientes.
*   **Solução para o Grafo:** Criar um nó central de ontologia no Grafo de Conhecimento para harmonizar a métrica antes de expô-la aos agentes.

### 2. Lacuna de Conhecimento Tácito (Tribal Knowledge Gap)
*   **O problema:** Procedimentos cruciais que estão "na cabeça" do principal engenheiro ou vendedor.
*   **Como identificar:** Identifique gargalos operacionais onde as tarefas só avançam se uma pessoa específica estiver disponível.
*   **Solução para a Memória:** Realizar entrevistas curtas gravadas, transcrever com modelos Whisper/ASR e carregar na camada de Memória Episódica.

### 3. Lacuna de Autoridade e Ação (Execution Safety Gap)
*   **O problema:** Falta de clareza sobre quais ações o agente de IA pode executar autonomamente vs. quais exigem aprovação humana (Human-in-the-loop).
*   **Como identificar:** Mapear os endpoints de escrita (APIs) que realizam alterações críticas (ex: estornos, disparos de emails em massa) sem validação adicional.
*   **Solução para Orquestração:** Desenhar regras explícitas de barreira na Camada 6 (Governança/ABAC) associadas a workflows de aprovação.

---

## 📋 Plano de Ação para a Coleta de Informações

1.  **Kickoff com Gestores:** Alinhar o objetivo de construir o Cérebro de Empresa.
2.  **Entrevistas de Mapeamento Semântico:** Alinhar as métricas chaves com os SMEs.
3.  **Auditoria de Repositórios:** Acessar Notion, Google Drive e repositórios de código para baixar a documentação existente.
4.  **Extração de APIs e DBs:** Mapear junto ao time de tecnologia os esquemas de dados.
5.  **Preenchimento deste Diagnóstico:** Consolide os resultados nesta tabela para estimar o esforço de engenharia de dados.
