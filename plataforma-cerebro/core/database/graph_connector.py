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

    def query(self, cypher_query, parameters=None):
        if parameters is None:
            parameters = {}

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
