import os
import json
import time
import sys

# Forçar codificação UTF-8 no stdout para evitar erros em consoles Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

# --- BANCO DE DADOS EM MEMÓRIA (MOCK) ---
DB = {
    "condominios": {
        "C01": {"nome": "Condominio Vista Bella", "saldo": 10000.0},
        "C02": {"nome": "Condominio Parque Club", "saldo": 5000.0},
        "C03": {"nome": "Condominio Grand Tower", "saldo": 20000.0}
    },
    "fornecedores": {
        "F01": {"nome": "Elevadores S/A", "cpf_cnpj": "12.345.678/0001-90", "chave_pix": "elevadores@corp.com"},
        "F02": {"nome": "Limpeza Silva", "cpf_cnpj": "98.765.432/0001-10", "chave_pix": "financeiro@limpezasilva.com"},
        "F03": {"nome": "Pintura Express", "cpf_cnpj": "45.678.901/0001-20", "chave_pix": "contato@pinturaexpress.com"},
        "F04": {"nome": "Distribuidora Agua", "cpf_cnpj": "11.222.333/0001-44", "chave_pix": "chave-errada-pix"} # Chave propositalmente inválida
    },
    "despesas": [
        {"id": "D01", "condo_id": "C01", "fornecedor_id": "F01", "valor": 8000.0, "status": "Agendado", "desc": "Manutencao Mensal de Elevadores"},
        {"id": "D02", "condo_id": "C01", "fornecedor_id": "F02", "valor": 4000.0, "status": "Agendado", "desc": "Servicos de Limpeza Emergencial"},
        {"id": "D03", "condo_id": "C02", "fornecedor_id": "F03", "valor": 3000.0, "status": "Agendado", "desc": "Pintura do Hall"},
        {"id": "D04", "condo_id": "C03", "fornecedor_id": "F04", "valor": 3000.0, "status": "Agendado", "desc": "Compra de Galoes de Agua"}
    ]
}

# --- AUXILIARES DE FORMATAÇÃO (ASCII SEGURO) ---
def log_agent(agent_name, message):
    print(f"[{agent_name}] {message}")
    time.sleep(0.3)

# --- 1. ROUTER AGENT ---
def run_router_agent(event_type):
    log_agent("Router Agent", f"Novo evento detectado: {event_type}. Direcionando fluxo...")
    if event_type == "PROCESSAR_PAGAMENTOS_FIM_DIA":
        return "WORKFLOW_PAGAMENTOS"
    return "UNKNOWN"

# --- 2. KB QUERY AGENT ---
def run_kb_query_agent():
    log_agent("KB Query Agent", "Consultando despesas agendadas para hoje e saldos dos condominios no Grafo...")
    agenda_hoje = []
    for d in DB["despesas"]:
        if d["status"] == "Agendado":
            condo = DB["condominios"][d["condo_id"]]
            forn = DB["fornecedores"][d["fornecedor_id"]]
            agenda_hoje.append({
                "despesa_id": d["id"],
                "condo_id": d["condo_id"],
                "condo_nome": condo["nome"],
                "saldo_atual": condo["saldo"],
                "valor_despesa": d["valor"],
                "desc": d["desc"],
                "forn_nome": forn["nome"],
                "forn_doc": forn["cpf_cnpj"],
                "forn_pix": forn["chave_pix"]
            })
    log_agent("KB Query Agent", f"Sucesso: {len(agenda_hoje)} lancamentos encontrados.")
    return agenda_hoje

# --- 3. GUARDRAIL AGENT ---
def run_guardrail_agent(agenda):
    log_agent("Guardrail Agent", "Iniciando validacao de limites e regras de saldo por Condominio...")
    aprovados = []
    rejeitados_saldo = []
    
    # Rastrear saldos simulando descontos virtuais durante as validações deste lote
    saldos_temporarios = {cid: info["saldo"] for cid, info in DB["condominios"].items()}

    for item in agenda:
        cid = item["condo_id"]
        valor = item["valor_despesa"]
        
        # Validar Limite Geral de IA (Guardrail rígido)
        if valor > 50000.0:
            log_agent("Guardrail Agent", f"VIOLACAO: Despesa {item['despesa_id']} excede limite maximo sem aprovacao humana!")
            rejeitados_saldo.append({**item, "motivo": "Excede Limite Operacional da IA"})
            continue
            
        # Validar Isolamento Financeiro / Saldo Suficiente
        if saldos_temporarios[cid] >= valor:
            saldos_temporarios[cid] -= valor
            aprovados.append(item)
            log_agent("Guardrail Agent", f"Aprovado: {item['desc']} ({item['condo_nome']}) - R$ {valor:.2f}")
        else:
            log_agent("Guardrail Agent", f"REJEITADO: {item['desc']} ({item['condo_nome']}) - Saldo Insuficiente (Disponivel: R$ {saldos_temporarios[cid]:.2f})")
            rejeitados_saldo.append({**item, "motivo": "Saldo Insuficiente"})

    return aprovados, rejeitados_saldo

# --- 4. ACTION AGENT ---
def run_action_agent(aprovados):
    log_agent("Action Agent", "Iniciando geracao de arquivos de remessa bancaria CNAB...")
    
    # Simular Geração de CNAB Remessa
    remessa_lines = []
    for item in aprovados:
        line = f"REMESSA|{item['despesa_id']}|{item['condo_id']}|{item['forn_nome']}|{item['forn_doc']}|{item['forn_pix']}|{item['valor_despesa']:.2f}"
        remessa_lines.append(line)
        
    remessa_content = "\n".join(remessa_lines)
    remessa_path = "CNAB_remessa_mock.txt"
    with open(remessa_path, "w", encoding="utf-8") as f:
        f.write(remessa_content)
        
    log_agent("Action Agent", f"Remessa exportada com sucesso em: {remessa_path}")
    log_agent("Action Agent", "Enviando arquivo ao banco parceiro via SFTP...")
    
    # --- SIMULAÇÃO DE RESPOSTA DO BANCO (ARQUIVO RETORNO) ---
    log_agent("Action Agent", "Aguardando processamento bancario do lote...")
    retorno_lines = []
    for line in remessa_lines:
        parts = line.split("|")
        dep_id = parts[1]
        pix = parts[5]
        # Simular que a chave Pix inválida "chave-errada-pix" falha no banco
        if "chave-errada-pix" in pix:
            retorno_lines.append(f"RETORNO|{dep_id}|REJEITADO|Chave Pix Invalida")
        else:
            retorno_lines.append(f"RETORNO|{dep_id}|SUCESSO|Pago")
            
    retorno_content = "\n".join(retorno_lines)
    retorno_path = "CNAB_retorno_mock.txt"
    with open(retorno_path, "w", encoding="utf-8") as f:
        f.write(retorno_content)
    
    log_agent("Action Agent", f"Retorno do banco recebido e salvo: {retorno_path}")
    
    # Processar Retorno e Atualizar Banco de Dados
    log_agent("Action Agent", "Lendo retorno e aplicando atualizacoes no Banco de Dados...")
    resultados_banco = []
    with open(retorno_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            dep_id = parts[1]
            status_banco = parts[2]
            detalhe = parts[3]
            
            # Atualizar DB real
            for d in DB["despesas"]:
                if d["id"] == dep_id:
                    if status_banco == "SUCESSO":
                        d["status"] = "Pago"
                        # Descontar saldo real do condomínio
                        DB["condominios"][d["condo_id"]]["saldo"] -= d["valor"]
                    else:
                        d["status"] = f"Rejeitado: {detalhe}"
                    
                    resultados_banco.append({
                        "despesa_id": dep_id,
                        "status": status_banco,
                        "detalhe": detalhe,
                        "valor": d["valor"],
                        "condo_id": d["condo_id"]
                    })
                    
    return resultados_banco

# --- 5. EVALUATOR AGENT ---
def run_evaluator_agent(aprovados, rejeitados_guardrail, resultados_banco):
    log_agent("Evaluator Agent", "Iniciando auditoria matematica e consolidacao financeira...")
    
    pagos = [r for r in resultados_banco if r["status"] == "SUCESSO"]
    rejeitados_banco = [r for r in resultados_banco if r["status"] == "REJEITADO"]
    
    total_solicitado = sum(d["valor"] for d in DB["despesas"])
    total_pago = sum(p["valor"] for p in pagos)
    total_rejeitado_guardrail = sum(r["valor_despesa"] for r in rejeitados_guardrail)
    total_rejeitado_banco = sum(r["valor"] for r in rejeitados_banco)
    
    # Auditoria de Fechamento
    diferenca = total_solicitado - (total_pago + total_rejeitado_guardrail + total_rejeitado_banco)
    auditoria_status = "VERIFICADO E SEGURO" if diferenca == 0 else "DISCREPANCIA ENCONTRADA"
    
    # Criar Relatório Markdown
    relatorio = f"""# Relatorio Executivo de Pagamentos do Dia
**Data da Operacao:** 03/08/2026  
**Auditoria Financeira:** {auditoria_status} (Diferenca: R$ {diferenca:.2f})

## Metricas Consolidadas

| Metrica | Qtd | Valor Consolidado |
| :--- | :---: | :---: |
| **Total Solicitado** | {len(DB["despesas"])} | R$ {total_solicitado:.2f} |
| **Total Pago com Sucesso** | {len(pagos)} | R$ {total_pago:.2f} |
| **Retido por Falta de Saldo (Guardrail)** | {len(rejeitados_guardrail)} | R$ {total_rejeitado_guardrail:.2f} |
| **Rejeitado por Erros no Banco** | {len(rejeitados_banco)} | R$ {total_rejeitado_banco:.2f} |

---

## Ocorrencias e Rejeicoes Detalhadas

| Condominio | Favorecido | Valor | Origem do Bloqueio | Motivo / Detalhe |
| :--- | :--- | :--- | :---: | :--- |
"""
    # Adicionar rejeitados pelo guardrail
    for r in rejeitados_guardrail:
        relatorio += f"| {r['condo_nome']} | {r['forn_nome']} | R$ {r['valor_despesa']:.2f} | Guardrail Interno | {r['motivo']} |\n"
        
    # Adicionar rejeitados pelo banco
    for r in rejeitados_banco:
        condo_nome = DB["condominios"][r["condo_id"]]["nome"]
        # Achar favorecido
        for d in DB["despesas"]:
            if d["id"] == r["despesa_id"]:
                forn_nome = DB["fornecedores"][d["fornecedor_id"]]["nome"]
        relatorio += f"| {condo_nome} | {forn_nome} | R$ {r['valor']:.2f} | Processamento Banco | {r['detalhe']} |\n"
        
    relatorio += "\n\n*Relatorio emitido pelo **Agente de Auditoria (Evaluator)** com base nos traces CNAB e banco de dados local.*"
    
    report_path = "resultado_processamento_hoje.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(relatorio)
        
    log_agent("Evaluator Agent", f"Relatorio financeiro publicado com sucesso em: {report_path}")
    print("\n" + "="*50 + "\n" + relatorio + "\n" + "="*50)


# --- ORQUESTRADOR CENTRAL (PIPELINE) ---
def main():
    print("="*60)
    print("INICIANDO SIMULADOR MULTI-AGENTE: CEREBRO DE CONDOMINIOS")
    print("="*60 + "\n")
    
    # 1. Roteador
    fluxo = run_router_agent("PROCESSAR_PAGAMENTOS_FIM_DIA")
    if fluxo != "WORKFLOW_PAGAMENTOS":
        print("Fluxo abortado.")
        return
        
    # 2. Busca Semântica / Dados
    agenda = run_kb_query_agent()
    
    # 3. Guardrail / Validação de Saldo
    aprovados, rejeitados_guardrail = run_guardrail_agent(agenda)
    
    # 4. Executor / Integração Bancária
    resultados_banco = run_action_agent(aprovados)
    
    # 5. Auditor / Avaliador
    run_evaluator_agent(aprovados, rejeitados_guardrail, resultados_banco)

if __name__ == "__main__":
    main()
