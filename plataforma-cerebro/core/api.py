import os
import sys
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional

# Adicionar diretorio pai ao path para importar core corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.engine import EnterpriseBrainEngine

app = FastAPI(
    title="Plataforma Cerebro de Empresa B2B API",
    description="Interface REST unificada para integracao de sistemas e frontends do Cerebro de Empresa.",
    version="1.0.0"
)

# Inicializar a Engine
engine = EnterpriseBrainEngine()

# Configurar seguranca de API Key
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Obter token esperado da configuracao do cliente
EXPECTED_API_KEY = engine.config.get("company", {}).get("api_key", "default-secret-key")

def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Token X-API-Key ausente no cabeçalho da requisição."
        )
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Token X-API-Key invalido ou nao autorizado para este tenant."
        )
    return api_key

# --- SCHEMAS DE REQUISICAO ---
class QueryRequest(BaseModel):
    prompt: str
    user_role: str
    user_id: str
    condo_id: str
    payment_value: float = 0.0
    session_id: Optional[str] = None

class ApproveRequest(BaseModel):
    approval_id: str
    approver_role: str
    approver_id: str

# --- ENDPOINTS ---

@app.get("/health")
def health_check():
    """
    Endpoint publico para monitoramento de liveness/readiness (Kubernetes/Docker).
    Nao exige token de seguranca.
    """
    return {
        "status": "healthy",
        "tenant": engine.config.get("company", {}).get("name", "Default Tenant"),
        "version": "1.0.0"
    }

@app.post("/api/v1/query", dependencies=[Depends(verify_api_key)])
def execute_query(
    payload: QueryRequest,
    x_user_session_token: Optional[str] = Header(None, alias="X-User-Session-Token")
):
    """
    Processa prompts de linguagem natural dos usuarios do condomínio.
    Aplica Guardrails, busca no Neo4j e executa acoes MCP se necessario.
    Suporta JIT session tokens para Zero Ambient Authority.
    """
    try:
        result = engine.process_request(
            prompt=payload.prompt,
            user_role=payload.user_role,
            user_id=payload.user_id,
            condo_id=payload.condo_id,
            payment_value=payload.payment_value,
            session_id=payload.session_id,
            session_token=x_user_session_token
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento cognitivo: {str(e)}")

@app.post("/api/v1/approve", dependencies=[Depends(verify_api_key)])
def approve_query(
    payload: ApproveRequest,
    x_user_session_token: Optional[str] = Header(None, alias="X-User-Session-Token")
):
    """
    Endpoint de aprovacao manual (Human-In-The-Loop) para transacoes em retencao.
    Exige credencial de sessao JIT valida.
    """
    try:
        result = engine.approve_transaction(
            approval_id=payload.approval_id,
            approver_role=payload.approver_role,
            approver_id=payload.approver_id,
            session_token=x_user_session_token
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar aprovacao: {str(e)}")

@app.get("/api/v1/history/{session_id}", dependencies=[Depends(verify_api_key)])
def get_chat_history(session_id: str):
    """
    Recupera o historico persistente de chat (PostgreSQL/SQLite) para uma determinada sessao.
    """
    try:
        history = engine.memory.get_history(session_id)
        return {
            "session_id": session_id,
            "total_messages": len(history),
            "messages": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar historico da base: {str(e)}")

if __name__ == "__main__":
    # Inicia o servidor local
    port = int(os.environ.get("PORT", 8000))
    print(f"Iniciando API REST do Cerebro em http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

