import unittest
import os
import sys

# Adicionar diretorio pai ao path para importacoes funcionarem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.engine import EnterpriseBrainEngine

class TestEnterpriseBrainEngine(unittest.TestCase):
    def setUp(self):
        # Inicializa o motor que carrega default_config e company_config
        self.engine = EnterpriseBrainEngine()

    def test_config_merging(self):
        # Verifica se o merge das configuracoes ocorreu corretamente
        # default_config tem max_payment_limit: 10000.0, mas company_config substitui para 50000.0
        limit = self.engine.config.get("agents", {}).get("guardrail", {}).get("max_payment_limit")
        self.assertEqual(limit, 50000.0)
        
        # O nome da empresa deve ter sido importado do company_config
        company_name = self.engine.config.get("company", {}).get("name")
        self.assertEqual(company_name, "Gestão Integrada de Condomínios S.A.")

    def test_router_intent_classification(self):
        # Testar classificações do Roteador
        intent_payment = self.engine.router.route("Gostaria de rodar os pagamentos e enviar a remessa")
        self.assertEqual(intent_payment, "PROCESSAR_PAGAMENTOS")

        intent_report = self.engine.router.route("Me mostre o saldo do condominio")
        self.assertEqual(intent_report, "RELATORIO_FINANCEIRO")

        intent_other = self.engine.router.route("Como faco para cadastrar um novo morador?")
        self.assertEqual(intent_other, "DUVIDA_GERAL")

    def test_guardrail_authorization(self):
        # Testar caso de uso autorizado (Papel correto, valor sob o limite de 50.000,00)
        authorized, reason = self.engine.guardrail.validate_payment(
            user_role="condo_financial_analyst", 
            value=25000.0, 
            condo_id="C01"
        )
        self.assertTrue(authorized)
        self.assertEqual(reason, "Aprovado")

    def test_guardrail_unauthorized_role(self):
        # Testar caso bloqueado por cargo nao permitido (ABAC)
        authorized, reason = self.engine.guardrail.validate_payment(
            user_role="condo_manager", # Manager nao esta na regra de execucao de pagamento
            value=1000.0, 
            condo_id="C01"
        )
        self.assertFalse(authorized)
        self.assertIn("nao possui permissao", reason)

    def test_guardrail_value_over_limit(self):
        # Testar caso bloqueado por valor acima do limite (50k)
        authorized, reason = self.engine.guardrail.validate_payment(
            user_role="condo_financial_analyst", 
            value=60000.0, 
            condo_id="C01"
        )
        self.assertFalse(authorized)
        self.assertIn("excede o limite maximo", reason)

    def test_process_request_flow(self):
        # Testar o fluxo completo integrado na Engine
        res = self.engine.process_request(
            prompt="Processar lote de pagamento de R$ 5000.00",
            user_role="condo_financial_analyst",
            user_id="analista_01",
            condo_id="C01",
            payment_value=5000.0
        )
        self.assertEqual(res["status"], "executado")
        self.assertEqual(res["intent"], "PROCESSAR_PAGAMENTOS")
        self.assertEqual(res["action_result"]["status"], "sucesso")

    def test_cypher_injection_guardrail(self):
        # Testar bloqueio de comandos de escrita no Grafo (Cypher Injection Protection)
        query_normal = "MATCH (c:Condominio) RETURN c"
        self.assertTrue(self.engine.graph.validate_query(query_normal))
        
        query_perigosa = "MATCH (c:Condominio) DETACH DELETE c"
        self.assertFalse(self.engine.graph.validate_query(query_perigosa))
        
        # Executar deve levantar ValueError
        with self.assertRaises(ValueError):
            self.engine.graph.query(query_perigosa)

    def test_chat_memory_store(self):
        # Testar escrita e leitura de historico de chat
        sessao_teste = "session_test_999"
        
        # Limpar registros anteriores se houver
        self.engine.memory.add_message(sessao_teste, "user", "Ola Cérebro")
        self.engine.memory.add_message(sessao_teste, "agent", "Ola Humano, como posso ajudar?")
        
        historico = self.engine.memory.get_history(sessao_teste)
        self.assertEqual(len(historico), 2)
        self.assertEqual(historico[0]["sender"], "user")
        self.assertEqual(historico[0]["message"], "Ola Cérebro")
        self.assertEqual(historico[1]["sender"], "agent")
        self.assertEqual(historico[1]["message"], "Ola Humano, como posso ajudar?")

if __name__ == "__main__":
    unittest.main()

