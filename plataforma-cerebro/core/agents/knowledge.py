import logging

logger = logging.getLogger("knowledge_agent")

class KnowledgeAgent:
    """
    Agente de Busca Semantica e RAG.
    Consulta de forma coordenada o banco relacional/vetorial e o grafo de conhecimento (Neo4j).
    """
    def __init__(self, config, graph_connector, vector_connector):
        self.config = config
        self.graph = graph_connector
        self.vector = vector_connector
        self.hybrid_search = config.get("hybrid_search", True)
        logger.info(f"KnowledgeAgent inicializado (Hybrid Search: {self.hybrid_search})")

    def retrieve_context(self, query_text):
        logger.info(f"[Knowledge Agent] Buscando contexto hibrido para: '{query_text}'")
        
        # 1. Recuperar regras factuais do banco vetorial
        vector_results = self.vector.similarity_search(query_text)
        
        # 2. Recuperar informacoes financeiras estruturadas do Neo4j
        # (Aqui simulamos o roteamento Cypher adequado com base na query)
        cypher_query = "MATCH (c:Condominio)-[:POSSUI_CONTA]->(cb:ContaBancaria) RETURN c.nome, cb.saldo_atual"
        graph_results = self.graph.query(cypher_query)
        
        context = {
            "regras_seguranca": [doc["content"] for doc in vector_results],
            "financeiro_grafo": graph_results
        }
        
        logger.info(f"[Knowledge Agent] Contexto estruturado recuperado contendo {len(vector_results)} documentos e {len(graph_results)} registros do Grafo.")
        return context
