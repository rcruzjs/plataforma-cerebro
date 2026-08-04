import logging

logger = logging.getLogger("action_agent")

class ActionAgent:
    """
    Agente Executor de Acoes.
    Carrega as ferramentas do cliente configuradas no manifesto (como MCP servers)
    e executa chamadas de acao contra as APIs corporativas.
    """
    def __init__(self, config):
        self.config = config
        self.mcp_servers = config.get("mcp_servers", {})
        logger.info(f"ActionAgent inicializado com {len(self.mcp_servers)} servidores MCP mapeados.")

    def execute_action(self, tool_name, arguments, session_token=None):
        logger.info(f"[Action Agent] Solicitando execucao de ferramenta MCP '{tool_name}' com args {arguments}")
        
        # Simular acoplamento com servidores de acao configurados
        if tool_name == "financial_mcp/process_payout":
            # Validar credencial JIT (Zero Ambient Authority)
            if not session_token or session_token == "token-invalido":
                logger.error("[Action Agent] [SECURITY ERROR] Chamada rejeitada. Falta de credencial JIT valida!")
                return {"status": "erro", "motivo": "Violacao de JIT: Token de sessao invalido ou ausente."}

            # Validar argumentos obrigatorios
            if "valor" not in arguments or "condo_id" not in arguments:
                return {"status": "erro", "motivo": "Argumentos invalidos"}
                
            valor = arguments["valor"]
            condo_id = arguments["condo_id"]
            
            logger.info(f"[Action Agent] [MCP financial_mcp] Enviando solicitacao de transferencia no valor R$ {valor:.2f} para o banco do condominio {condo_id} usando JIT Session Token {session_token[:6]}...")
            return {"status": "sucesso", "transacao_id": "TX_90123"}
            
        logger.warning(f"[Action Agent] Ferramenta '{tool_name}' nao encontrada ou nao configurada neste tenant.")
        return {"status": "erro", "motivo": f"Ferramenta '{tool_name}' inexistente"}

