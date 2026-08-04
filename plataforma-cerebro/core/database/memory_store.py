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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_approvals (
                    id VARCHAR(255) PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    user_role VARCHAR(100) NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    condo_id VARCHAR(100) NOT NULL,
                    payment_value NUMERIC NOT NULL,
                    session_id VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'PENDING'
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_approvals (
                    id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    condo_id TEXT NOT NULL,
                    payment_value REAL NOT NULL,
                    session_id TEXT,
                    status TEXT DEFAULT 'PENDING'
                );
            """)
        cursor.close()

    def add_pending_approval(self, approval_id, prompt, user_role, user_id, condo_id, payment_value, session_id=None):
        cursor = self.conn.cursor()
        query = "INSERT INTO pending_approvals (id, prompt, user_role, user_id, condo_id, payment_value, session_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING')" if self.use_postgres else \
                "INSERT INTO pending_approvals (id, prompt, user_role, user_id, condo_id, payment_value, session_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING')"
        try:
            cursor.execute(query, (approval_id, prompt, user_role, user_id, condo_id, payment_value, session_id))
            if not self.use_postgres:
                self.conn.commit()
            logger.info(f"[Memory Store] Aprovacao pendente registrada: {approval_id} (Valor: R$ {payment_value:.2f})")
        except Exception as e:
            logger.error(f"Erro ao salvar aprovacao pendente: {e}")
        finally:
            cursor.close()

    def get_pending_approval(self, approval_id):
        cursor = self.conn.cursor()
        query = "SELECT prompt, user_role, user_id, condo_id, payment_value, session_id, status FROM pending_approvals WHERE id = %s" if self.use_postgres else \
                "SELECT prompt, user_role, user_id, condo_id, payment_value, session_id, status FROM pending_approvals WHERE id = ?"
        
        result = None
        try:
            cursor.execute(query, (approval_id,))
            row = cursor.fetchone()
            if row:
                result = {
                    "id": approval_id,
                    "prompt": row[0],
                    "user_role": row[1],
                    "user_id": row[2],
                    "condo_id": row[3],
                    "payment_value": float(row[4]),
                    "session_id": row[5],
                    "status": row[6]
                }
        except Exception as e:
            logger.error(f"Erro ao obter aprovacao pendente '{approval_id}': {e}")
        finally:
            cursor.close()
        return result

    def get_all_pending_approvals(self):
        cursor = self.conn.cursor()
        query = "SELECT id, prompt, user_role, user_id, condo_id, payment_value, session_id, status FROM pending_approvals ORDER BY id DESC"
        
        results = []
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    "id": row[0],
                    "prompt": row[1],
                    "user_role": row[2],
                    "user_id": row[3],
                    "condo_id": row[4],
                    "payment_value": float(row[5]),
                    "session_id": row[6],
                    "status": row[7]
                })
        except Exception as e:
            logger.error(f"Erro ao obter aprovacoes: {e}")
        finally:
            cursor.close()
        return results


    def update_approval_status(self, approval_id, status):
        cursor = self.conn.cursor()
        query = "UPDATE pending_approvals SET status = %s WHERE id = %s" if self.use_postgres else \
                "UPDATE pending_approvals SET status = ? WHERE id = ?"
        try:
            cursor.execute(query, (status, approval_id))
            if not self.use_postgres:
                self.conn.commit()
            logger.info(f"[Memory Store] Status da aprovacao '{approval_id}' atualizado para: {status}")
        except Exception as e:
            logger.error(f"Erro ao atualizar status da aprovacao '{approval_id}': {e}")
        finally:
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

