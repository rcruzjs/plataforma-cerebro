import os
import sqlite3
import datetime
import logging

logger = logging.getLogger("memory_store")

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("Biblioteca 'psycopg2' nao encontrada. Rodando historico de chat com SQLite.")

class MemoryStore:
    """
    Gerenciador de Memoria Persistente de Chat.
    Conecta no PostgreSQL por padrao, mas tem fallback inteligente para SQLite local
    caso a conexao com o Postgres falhe ou nao esteja configurada.
    """
    def __init__(self, db_config=None):
        self.db_config = db_config or {}
        self.use_postgres = self.db_config.get("provider") == "postgres" and PSYCOPG2_AVAILABLE
        self.conn = None
        self.sqlite_path = "chat_history.db"

        if self.use_postgres:
            try:
                # Tentar conectar no PostgreSQL
                host = self.db_config.get("host", "localhost")
                port = self.db_config.get("port", 5432)
                dbname = self.db_config.get("database", "postgres")
                user = self.db_config.get("username", "postgres")
                password = self.db_config.get("password", "")

                self.conn = psycopg2.connect(
                    host=host,
                    port=port,
                    dbname=dbname,
                    user=user,
                    password=password,
                    connect_timeout=3
                )
                self.conn.autocommit = True
                logger.info("Conexao com PostgreSQL para historico de chat estabelecida.")
            except Exception as e:
                logger.warning(f"Erro ao conectar no PostgreSQL ({e}). Modificando fallback para SQLite local.")
                self.use_postgres = False

        if not self.use_postgres:
            # Fallback para SQLite local
            try:
                self.conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
                logger.info(f"Conexao com SQLite local estabelecida em: {self.sqlite_path}")
            except Exception as e:
                logger.error(f"Erro ao criar banco de dados SQLite local ({e})")
                raise e

        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        if self.use_postgres:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    sender VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
        cursor.close()

    def add_message(self, session_id, sender, message):
        cursor = self.conn.cursor()
        query = "INSERT INTO chat_history (session_id, sender, message) VALUES (%s, %s, %s)" if self.use_postgres else \
                "INSERT INTO chat_history (session_id, sender, message) VALUES (?, ?, ?)"
        
        try:
            cursor.execute(query, (session_id, sender, message))
            if not self.use_postgres:
                self.conn.commit()
            logger.info(f"[Memory Store] Mensagem registrada para session_id '{session_id}': {sender} -> {message[:30]}...")
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem no historico: {e}")
        finally:
            cursor.close()

    def get_history(self, session_id):
        cursor = self.conn.cursor()
        query = "SELECT sender, message, timestamp FROM chat_history WHERE session_id = %s ORDER BY id ASC" if self.use_postgres else \
                "SELECT sender, message, timestamp FROM chat_history WHERE session_id = ? ORDER BY id ASC"
        
        history = []
        try:
            cursor.execute(query, (session_id,))
            rows = cursor.fetchall()
            for row in rows:
                history.append({
                    "sender": row[0],
                    "message": row[1],
                    "timestamp": str(row[2])
                })
        except Exception as e:
            logger.error(f"Erro ao ler historico do session_id '{session_id}': {e}")
        finally:
            cursor.close()
            
        return history

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Conexao com o historico de chat fechada.")
