// Configurações globais
function getHeaders() {
    const apiKey = document.getElementById("api-key-input").value;
    const jitToken = document.getElementById("jit-token-input").value;
    
    const headers = {
        "Content-Type": "application/json",
        "X-API-Key": apiKey
    };
    
    if (jitToken) {
        headers["X-User-Session-Token"] = jitToken;
    }
    
    return headers;
}

function showNotification(message, isError = false) {
    const notif = document.getElementById("notification");
    notif.innerText = message;
    notif.className = `notification ${isError ? 'error' : 'success'}`;
    
    setTimeout(() => {
        notif.className = "notification hide";
    }, 4000);
}

// Carregar Dados do Tenant
async function loadTenantInfo() {
    try {
        const res = await fetch("/health");
        if (res.ok) {
            const data = await res.json();
            document.getElementById("tenant-badge").innerText = `Tenant: ${data.tenant} (v${data.version})`;
        } else {
            document.getElementById("tenant-badge").innerText = "Tenant Desconectado";
        }
    } catch (e) {
        document.getElementById("tenant-badge").innerText = "Erro ao Conectar";
    }
}

// Carregar Transações Pendentes (Human-in-the-loop)
async function loadApprovals() {
    const container = document.getElementById("approvals-container");
    container.innerHTML = `<div class="empty-state">Buscando transações...</div>`;
    
    try {
        const res = await fetch("/api/v1/approvals", {
            headers: getHeaders()
        });
        
        if (!res.ok) {
            const err = await res.json();
            container.innerHTML = `<div class="empty-state" style="color:#ef4444">Erro: ${err.detail || 'Falha na autenticacao'}</div>`;
            return;
        }
        
        const approvals = await res.json();
        
        if (approvals.length === 0) {
            container.innerHTML = `<div class="empty-state">Nenhum pagamento aguardando aprovação.</div>`;
            return;
        }
        
        container.innerHTML = "";
        approvals.forEach(app => {
            const card = document.createElement("div");
            card.className = "approval-card";
            
            // Formatando o Vibe Diff
            card.innerHTML = `
                <div class="approval-header">
                    <span class="approval-id">${app.id}</span>
                    <span class="badge" style="background:rgba(245,158,11,0.1); color:#f59e0b; border:1px solid rgba(245,158,11,0.2)">${app.status}</span>
                </div>
                
                <div class="vibe-diff">
                    <div class="diff-line">
                        <span class="diff-label">Condomínio:</span>
                        <span class="diff-value">${app.condo_id}</span>
                    </div>
                    <div class="diff-line">
                        <span class="diff-label">Valor:</span>
                        <span class="diff-value">R$ ${app.payment_value.toFixed(2)}</span>
                    </div>
                    <div class="diff-line">
                        <span class="diff-label">Solicitante:</span>
                        <span class="diff-value">${app.user_id} (${app.user_role})</span>
                    </div>
                    <div class="diff-line">
                        <span class="diff-label">Intenção original:</span>
                        <span class="diff-value">"${app.prompt}"</span>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-success" onclick="processApproval('${app.id}', 'APPROVED')">Assinar e Pagar</button>
                    <button class="btn btn-danger" onclick="processApproval('${app.id}', 'REJECTED')">Rejeitar</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (e) {
        container.innerHTML = `<div class="empty-state" style="color:#ef4444">Erro de conexao com a API.</div>`;
    }
}

// Processar Ação de Aprovação
async function processApproval(approvalId, status) {
    try {
        const payload = {
            approval_id: approvalId,
            approver_role: "condo_financial_analyst", // Perfil exigido por ABAC
            approver_id: "analista_web_01"
        };
        
        // Se for rejeitado, apenas atualiza status
        const headers = getHeaders();
        const res = await fetch("/api/v1/approve", {
            method: "POST",
            headers: headers,
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        
        if (res.ok) {
            if (data.status === "executado" || data.status === "sucesso") {
                showNotification(`Transação ${approvalId} processada com sucesso!`);
            } else {
                showNotification(`Ação processada: ${data.response || data.motivo}`, true);
            }
            loadApprovals();
        } else {
            showNotification(`Erro ao aprovar: ${data.detail || 'Não autorizado'}`, true);
        }
    } catch (e) {
        showNotification("Erro na requisição de aprovação.", true);
    }
}

// Carregar Histórico de Mensagens
async function loadHistory() {
    const sessionId = document.getElementById("session-search-input").value;
    const container = document.getElementById("chat-history-container");
    
    if (!sessionId) {
        showNotification("Informe o ID da sessão para carregar.", true);
        return;
    }
    
    container.innerHTML = `<div class="empty-state">Buscando mensagens...</div>`;
    
    try {
        const res = await fetch(`/api/v1/history/${sessionId}`, {
            headers: getHeaders()
        });
        
        if (!res.ok) {
            const err = await res.json();
            container.innerHTML = `<div class="empty-state" style="color:#ef4444">Erro: ${err.detail || 'Falha na autenticacao'}</div>`;
            return;
        }
        
        const data = await res.json();
        const messages = data.messages;
        
        if (messages.length === 0) {
            container.innerHTML = `<div class="empty-state">Nenhuma mensagem registrada nesta sessão.</div>`;
            return;
        }
        
        container.innerHTML = "";
        messages.forEach(msg => {
            const bubble = document.createElement("div");
            bubble.className = `chat-bubble ${msg.sender}`;
            bubble.innerHTML = `
                <span>${msg.message}</span>
                <span class="chat-meta">${msg.sender.toUpperCase()} - ${msg.timestamp.split(" ")[1] || msg.timestamp}</span>
            `;
            container.appendChild(bubble);
        });
        
        // Scroll para o fim do chat
        container.scrollTop = container.scrollHeight;
    } catch (e) {
        container.innerHTML = `<div class="empty-state" style="color:#ef4444">Erro ao conectar à API de histórico.</div>`;
    }
}

// Inicialização
window.onload = () => {
    loadTenantInfo();
    loadApprovals();
};
