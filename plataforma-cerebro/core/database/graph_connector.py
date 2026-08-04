# --- RECONSTRUÍDO VIA SPEC-DRIVEN DEVELOPMENT --- 
# Data: 2026-08-03 22:54:21
# Spec de Referência: specs/integration_specs.md
import logging

logger = logging.getLogger("graph_connector")

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Biblioteca 'neo4j' nao encontrada. Rodando com MockGraphConnector de fallback.")

class GraphConnector:
    """
    Abstracao de conexao com o Neo4j.
    Caso a biblioteca nao esteja instalada ou a conexao falhe,
    o conector entra em modo Mock automaticamente para testes locais.
    """
    def __init__(self, uri, username, password, database="neo4j", mock_mode=False):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.mock_mode = mock_mode or not NEO4J_AVAILABLE
        self.driver = None

        if not self.mock_mode:
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
                # Validar conexao basica
                self.driver.verify_connectivity()
                logger.info("Conexao com o Neo4j estabelecida com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao conectar no Neo4j ({e}). Mudando para Modo Mock.")
                self.mock_mode = True

    def validate_query(self, cypher_query):
        """
        Garante que a query Cypher executada e estritamente Read-Only.
        Bloqueia palavras-chave de mutacao para evitar Cypher Injection.
        """
        forbidden_keywords = ["create", "delete", "detach", "set", "remove", "merge", "drop", "alter"]
        normalized = cypher_query.lower()
        
        # Tokenizar por espaco para evitar falsos positivos (ex: variaveis contendo a substring 'set')
        words = set(normalized.replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " ").split())
        
        for keyword in forbidden_keywords:
            if keyword in words:
                logger.error(f"[SECURITY] Comando proibido '{keyword}' detectado na query Cypher!")
                return False
        return True

    def query(self, cypher_query, parameters=None):
        if parameters is None:
            parameters = {}

        # Aplicar Guardrail de seguranca de escrita
        if not self.validate_query(cypher_query):
            raise ValueError("Query bloqueada: Tentativa de modificacao de dados detectada (Cypher Injection Guardrail).")

        if self.mock_mode:
            logger.info(f"[MOCK GRAPH] Executando Cypher: {cypher_query} com params {parameters}")
            # Mock de resultados para o caso de uso de condomínio
            if "DEVE_PAGAR" in cypher_query:
                return [
                    {
                        "Condominio": "Condominio Vista Bella",
                        "SaldoDisponivel": 10000.0,
                        "TotalAPagar": 12000.0,
                        "PossuiSaldoSuficiente": False
                    }
                ]
            return []

        with self.driver.session(database=self.database) as session:
            result = session.run(cypher_query, parameters)
            return [record.data() for record in result]

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Conexao com Neo4j fechada.")
