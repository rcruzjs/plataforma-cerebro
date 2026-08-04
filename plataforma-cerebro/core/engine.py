import os
import yaml
import logging
from core.database.graph_connector import GraphConnector
from core.database.vector_connector import VectorConnector
from core.database.memory_store import MemoryStore
from core.agents.router import RouterAgent
from core.agents.guardrail import GuardrailAgent
from core.agents.knowledge import KnowledgeAgent
from core.agents.action import ActionAgent
import json

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("engine_core")

class EnterpriseBrainEngine:
    """
    Motor Central de Execucao (Core Engine).
    Carrega as configuracoes de default e cliente, inicializa os conectores de banco
    e instancia a equipe de agentes de forma isolada (Single-Tenant).
    """
    def __init__(self, company_config_path=None):
        self.config = self._load_config(company_config_path)
        
        # 1. Inicializar Conectores de Dados
        db_config = self.config.get("database", {})
        graph_cfg = db_config.get("graph", {})
        vector_cfg = db_config.get("vector", {})
        memory_cfg = db_config.get("memory", {})
        
        self.graph = GraphConnector(
            uri=graph_cfg.get("uri"),
            username=graph_cfg.get("username"),
            password=graph_cfg.get("password"),
            database=graph_cfg.get("database", "neo4j")
        )
        
        self.vector = VectorConnector(
            provider=vector_cfg.get("provider"),
            host=vector_cfg.get("host"),
            port=vector_cfg.get("port"),
            collection_name=vector_cfg.get("collection_name")
        )
        
        self.memory = MemoryStore(memory_cfg)
        
        # 2. Inicializar Agentes
        agent_cfg = self.config.get("agents", {})
        self.router = RouterAgent(agent_cfg.get("router", {}))
        self.guardrail = GuardrailAgent(agent_cfg.get("guardrail", {}))
        self.knowledge = KnowledgeAgent(agent_cfg.get("knowledge", {}), self.graph, self.vector)
        self.action = ActionAgent(agent_cfg.get("action", {}))
        
        logger.info("Motor Central do Cerebro de Empresa carregado com sucesso.")

    def _load_config(self, company_config_path):
        # 1. Carregar Configuração Padrão (Base)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_path = os.path.join(base_dir, "config", "default_config.yaml")
        
        if not os.path.exists(default_path):
            # Tentar relativo caso execute de outra pasta
            default_path = os.path.join("config", "default_config.yaml")
            
        with open(default_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            
        # 2. Carregar e Mesclar Configuração do Cliente
        company_path = company_config_path or os.environ.get("COMPANY_CONFIG_PATH")
        if not company_path:
            company_path = os.path.join(base_dir, "config", "company_config.yaml")
            if not os.path.exists(company_path):
                company_path = os.path.join("config", "company_config.yaml")
                
        if os.path.exists(company_path):
            logger.info(f"Carregando configuracao do cliente em: {company_path}")
            with open(company_path, "r", encoding="utf-8") as f:
                company_config = yaml.safe_load(f) or {}
                # Mesclagem recursiva simples
                self._merge_dicts(config, company_config)
        else:
            logger.warning("Arquivo de configuracao do cliente nao encontrado. Utilizando padroes de fallback.")
            
        return config

    def _merge_dicts(self, target, source):
        for k, v in source.items():
            if isinstance(v, dict) and k in target and isinstance(target[k], dict):
                self._merge_dicts(target[k], v)
            else:
                target[k] = v

    def process_request(self, prompt, user_role, user_id, condo_id, payment_value=0.0, session_id=None):
        """
        Orquestra a execucao da pergunta/comando do usuario pelos agentes.
        """
        logger.info(f"[Engine] Recebendo prompt do usuario '{user_id}' ({user_role}): '{prompt}'")
        
        # Registrar entrada no historico
        if session_id:
            self.memory.add_message(session_id, "user", prompt)
            
        # 1. Roteamento
        intent = self.router.route(prompt)
        
        res = {}
        if intent == "PROCESSAR_PAGAMENTOS":
            # 2. Validacao de Segurança / Limites e ABAC
            authorized, reason = self.guardrail.validate_payment(user_role, payment_value, condo_id)
            if not authorized:
                res = {
                    "status": "bloqueado",
                    "intent": intent,
                    "motivo": reason,
                    "response": f"Seguranca: Operacao bloqueada. {reason}"
                }
            else:
                # 3. Consulta de contexto
                context = self.knowledge.retrieve_context(prompt)
                
                # 4. Execucao de acao via ferramenta
                action_result = self.action.execute_action(
                    "financial_mcp/process_payout", 
                    {"valor": payment_value, "condo_id": condo_id}
                )
                
                res = {
                    "status": "executado",
                    "intent": intent,
                    "context_retrieved": context,
                    "action_result": action_result,
                    "response": f"Pagamento de R$ {payment_value:.2f} processado com sucesso para o Condominio {condo_id}."
                }
            
        elif intent == "RELATORIO_FINANCEIRO":
            context = self.knowledge.retrieve_context(prompt)
            res = {
                "status": "sucesso",
                "intent": intent,
                "context_retrieved": context,
                "response": "Relatorio financeiro consolidado gerado a partir do Grafo Semantico."
            }
            
        else:
            res = {
                "status": "sucesso",
                "intent": intent,
                "response": "Resposta geral fornecida a partir de modelos genericos."
            }
            
        # Registrar saida no historico
        if session_id:
            self.memory.add_message(session_id, "agent", res["response"])
            
        return res


if __name__ == "__main__":
    # Exemplo rápido de execução do motor
    print("Testando inicializacao do Core Engine...")
    engine = EnterpriseBrainEngine()
    
    # Testar fluxo autorizado
    res = engine.process_request(
        prompt="Executar pagamento da despesa de R$ 500.00 do condominio C01",
        user_role="condo_financial_analyst",
        user_id="analista_financeiro_01",
        condo_id="C01",
        payment_value=500.0
    )
    print("Resultado da Execucao Autorizada:")
    print(json.dumps(res, indent=2))
    
    # Testar fluxo nao autorizado (ABAC)
    print("\nTestando fluxo bloqueado por ABAC...")
    res_bloqueado = engine.process_request(
        prompt="Executar pagamento da despesa de R$ 500.00 do condominio C01",
        user_role="condo_manager", # Manager nao pode fazer pagamentos, apenas ver saldos
        user_id="sindico_01",
        condo_id="C01",
        payment_value=500.0
    )
    print("Resultado da Execucao Bloqueada:")
    print(json.dumps(res_bloqueado, indent=2))
