import logging
import json

logger = logging.getLogger("router_agent")

class RouterAgent:
    """
    Agente Roteador. Responsavel por analisar a entrada e direcionar 
    para o fluxo de acao ou consulta correspondente.
    """
    def __init__(self, config):
        self.config = config
        self.strategy = config.get("routing_strategy", "prompt_classifier")
        logger.info(f"RouterAgent inicializado com estrategia: {self.strategy}")

    def route(self, user_prompt):
        logger.info(f"[Router Agent] Classificando prompt: '{user_prompt}'")
        
        # Classificador determinístico simples para simulação
        prompt_lower = user_prompt.lower()
        
        if "pagamento" in prompt_lower or "pagar" in prompt_lower or "remessa" in prompt_lower:
            intent = "PROCESSAR_PAGAMENTOS"
        elif "saldo" in prompt_lower or "extrato" in prompt_lower or "financeiro" in prompt_lower:
            intent = "RELATORIO_FINANCEIRO"
        else:
            intent = "DUVIDA_GERAL"
            
        logger.info(f"[Router Agent] Intencao classificada: {intent}")
        return intent
