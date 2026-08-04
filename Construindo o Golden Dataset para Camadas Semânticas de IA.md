A criação de um Golden Dataset (ou Dataset de Ouro) é uma etapa central do Desenvolvimento Orientado a Avaliação (Eval-Driven Development) para garantir que a Camada Semântica e os agentes de IA operem com precisão e confiabilidade 1\. Sem um golden set, é impossível medir melhorias ou evitar regressões na qualidade e no roteamento do seu Cérebro de Empresa 2\.  
Para construir e validar a Camada Semântica usando um Golden Dataset, as melhores práticas da indústria seguem este processo:  
**1\. Coleta Manual por Especialistas (SMEs)**O processo começa com Especialistas do Assunto (Subject Matter Experts) da empresa escrevendo manualmente um conjunto inicial de 50 a 500 perguntas complexas ou casos de uso, juntamente com as respostas ideais validadas (as chamadas *golden queries*) 3-5. Esse conjunto de referência serve para testar as regras de negócio reais que a Camada Semântica deve resolver.  
**2\. Estruturação Rigorosa dos Casos de Teste**Cada caso de teste no dataset não pode ser apenas uma pergunta e uma resposta genérica. Ele deve ser altamente estruturado para avaliar o fluxo cognitivo do agente, contendo tipicamente:

* **Entrada do Usuário:** O prompt original 6\.  
* **Contexto Simulado / Ferramentas:** O contexto disponível no Grafo/Vector DB e quais ferramentas são permitidas para a tarefa 6, 7\.  
* **Saída Esperada (Ground Truth):** A resposta exata, em um formato ou padrão esperado 6, 7\.  
* **Regra de Falha e Comportamento:** O que constitui uma infração grave na execução 6\.  
* **Métrica de Avaliação Principal:** O que especificamente está sendo testado naquele caso 7\.

**3\. Cobertura de Cenários Críticos**O Golden Dataset deve ser abrangente e cobrir ativamente diferentes espectros de interação, estruturados da seguinte forma 7, 8:

* **Caminho Feliz (Happy Path):** Casos em que a informação flui normalmente e as entidades da camada semântica operam sem conflito 7\.  
* **Casos de Borda (Edge Cases):** Perguntas ambíguas, cenários conflitantes onde a política de reconciliação do cérebro deve agir, ou dados imprecisos 7, 8\.  
* **Testes de Segurança e Guardrails (Adversariais):** Testes onde o usuário tenta realizar injeção de prompt (*prompt injection*) ou solicita dados sensíveis e o agente deve se recusar firmemente com base nas regras de acesso (ABAC/RBAC) 7, 8\.

**4\. Escala via Geração Sintética com IA**Após ter a base montada pelos especialistas humanos, você deve dar escala ao dataset usando um LLM poderoso (como Qwen ou GPT-4) para gerar milhares de variações sintéticas de perguntas e casos extremos com base nos documentos da própria empresa 5\. Isso amplia radicalmente a cobertura dos testes.  
**5\. Execução e Avaliação Contínua (CI/CD de IA)**O Golden Dataset deve ser versionado como código e executado automaticamente usando o padrão *LLM-as-a-judge* e frameworks de métricas (como RAGAS ou DeepEval) sempre que um prompt for alterado, um modelo for atualizado ou a base de conhecimento sofrer regressão 4, 5, 9\. Ao rodar o dataset, as principais métricas acompanhadas devem ser:

* **Faithfulness (Fidelidade):** A resposta do agente está 100% ancorada nos documentos recuperados da camada semântica e do grafo, sem alucinações 10\.  
* **Context Recall (Revocação de Contexto):** O sistema recuperou todas as informações ou fatias do grafo de conhecimento necessárias para formular a resposta 10\.  
* **Tool Selection Accuracy:** O agente escolheu as rotas e métricas semânticas aprovadas (ex: consultou a métrica de "receita recorrente" pré-calculada) em vez de inventar uma consulta SQL do zero 10\.

Caso qualquer alteração faça com que o score caia em métricas vitais — por exemplo, a fidelidade cair de 96% para 94% contra o Golden Dataset — o pipeline de CI/CD deve bloquear automaticamente a implantação e alertar os engenheiros, mostrando o rastro (*trace*) exato de onde ocorreu a falha no raciocínio do agente 5\.  
