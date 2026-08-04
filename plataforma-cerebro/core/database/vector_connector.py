import logging

logger = logging.getLogger("vector_connector")

class VectorConnector:
    """
    Abstracao para Banco de Dados de Vetores (PGVector/ChromaDB).
    Fornece busca semantica de documentos.
    """
    def __init__(self, provider="chromadb", host="localhost", port=8000, collection_name="enterprise_knowledge", mock_mode=True):
        self.provider = provider
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.mock_mode = mock_mode
        logger.info(f"VectorConnector inicializado com provedor '{provider}' (Modo Mock: {mock_mode}).")

    def similarity_search(self, query_text, limit=3):
        logger.info(f"[VECTOR SEARCH] Buscando por: '{query_text}' (limit={limit})")
        if self.mock_mode:
            # Retorna documentos mocks relevantes para condomínio
            return [
                {
                    "content": "Regra de Isolamento Financeiro: Um condomínio não pode utilizar fundos de contas correntes de outros condomínios.",
                    "score": 0.98
                },
                {
                    "content": "Matriz de Alçada de Pagamento: Gastos acima de R$ 50.000,00 necessitam de aprovação manual do conselho administrativo.",
                    "score": 0.91
                }
            ]
        return []
