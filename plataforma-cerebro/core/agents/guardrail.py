import logging

logger = logging.getLogger("guardrail_agent")

class GuardrailAgent:
    """
    Agente de Seguranca e Guardrail.
    Verifica limites operacionais e aplica regras ABAC (Attribute-Based Access Control)
    definidas nas configuracoes do cliente.
    """
    def __init__(self, config):
        self.config = config
        self.max_limit = config.get("max_payment_limit", 10000.0)
        self.abac_rules = config.get("abac_rules", [])
        logger.info(f"GuardrailAgent configurado com limite maximo de pagamento: R$ {self.max_limit:.2f}")

    def validate_payment(self, user_role, value, condo_id):
        logger.info(f"[Guardrail Agent] Validando pagamento de R$ {value:.2f} para o Condominio {condo_id} solicitado por cargo: '{user_role}'")
        
        # 1. Validar Limite Maximo do Lote
        if value > self.max_limit:
            reason = f"Valor solicitado R$ {value:.2f} excede o limite maximo da IA de R$ {self.max_limit:.2f}"
            logger.warning(f"[Guardrail Agent] Bloqueado: {reason}")
            return False, reason
            
        # 2. Validar Regra ABAC (Controle de Acesso por Papel)
        authorized = False
        for rule in self.abac_rules:
            if rule["action"] == "payment_execution":
                if rule["role_required"] == user_role:
                    authorized = True
                    break
                    
        if not authorized:
            reason = f"Cargo '{user_role}' nao possui permissao para executar acao 'payment_execution'"
            logger.warning(f"[Guardrail Agent] Bloqueado: {reason}")
            return False, reason
            
        logger.info("[Guardrail Agent] Validacao concluida com SUCESSO.")
        return True, "Aprovado"
