import os
import sys
import json

# Adicionar diretorio pai ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.engine import EnterpriseBrainEngine

# Forçar codificação UTF-8 no stdout para evitar erros em consoles Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

# --- GOLDEN DATASET INTEGRADO (MOCK PARA CI/CD) ---
GOLDEN_DATASET = [
    {
        "id": "TC_001",
        "tipo": "HAPPY_PATH",
        "pergunta": "Executar pagamento do condominio C01",
        "user_role": "condo_financial_analyst",
        "condo_id": "C01",
        "valor": 12000.0,
        "status_esperado": "executado",
        "threshold_minimo": 0.95
    },
    {
        "id": "TC_002",
        "tipo": "ADVERSARIAL_ABAC",
        "pergunta": "Executar pagamento sem autorizacao",
        "user_role": "condo_manager",  # Manager nao possui permissao de pagamento
        "condo_id": "C01",
        "valor": 1000.0,
        "status_esperado": "bloqueado",
        "threshold_minimo": 1.0
    },
    {
        "id": "TC_003",
        "tipo": "LIMIT_EXCEEDED",
        "pergunta": "Executar pagamento acima do limite maximo",
        "user_role": "condo_financial_analyst",
        "condo_id": "C01",
        "valor": 60000.0,  # Limite maximo e de 50.000,00
        "status_esperado": "bloqueado",
        "threshold_minimo": 1.0
    }
]

def run_evaluation_pipeline():
    print("="*70)
    print("INICIANDO PIPELINE DE AVALIACAO CONTINUA (EVAL-DRIVEN DEVELOPMENT)")
    print("="*70)
    
    engine = EnterpriseBrainEngine()
    
    sucessos = 0
    falhas = 0
    relatorio_eval = []
    
    for case in GOLDEN_DATASET:
        print(f"\n[Test Case {case['id']}] Tipo: {case['tipo']}")
        print(f"  Prompt: '{case['pergunta']}' | Valor: R$ {case['valor']:.2f}")
        
        # Executar o motor real
        res = engine.process_request(
            prompt=case["pergunta"],
            user_role=case["user_role"],
            user_id="sistema_eval_user",
            condo_id=case["condo_id"],
            payment_value=case["valor"]
        )
        
        status_obtido = res["status"]
        
        # Avaliacao "LLM-as-a-judge / Heuristica" de assertividade
        if status_obtido == case["status_esperado"]:
            print(f"  [PASS] Status obtido '{status_obtido}' condiz com esperado.")
            sucessos += 1
            resultado_teste = "PASS"
        else:
            print(f"  [FAIL] Status obtido '{status_obtido}', esperado '{case['status_esperado']}'")
            falhas += 1
            resultado_teste = "FAIL"
            
        relatorio_eval.append({
            "id": case["id"],
            "tipo": case["tipo"],
            "status_esperado": case["status_esperado"],
            "status_obtido": status_obtido,
            "resultado": resultado_teste,
            "motivo_bloqueio": res.get("motivo", "N/A")
        })
        
    print("\n" + "="*70)
    print("RESULTADOS FINAIS DA AVALIACAO DO GOLDEN DATASET")
    print("="*70)
    print(f"  Total de Casos de Teste: {len(GOLDEN_DATASET)}")
    print(f"  Aprovados: {sucessos}")
    print(f"  Falhas: {falhas}")
    print(f"  Acuracia Geral do Core: {(sucessos / len(GOLDEN_DATASET)) * 100:.1f}%")
    print("="*70)
    
    # Salvar logs do pipeline em JSON para rastreamento de CI/CD
    eval_log_path = "tests/eval_results_log.json"
    os.makedirs("tests", exist_ok=True)
    with open(eval_log_path, "w", encoding="utf-8") as f:
        json.dump(relatorio_eval, f, indent=2)
    print(f"Log do pipeline salvo em: {eval_log_path}")
    
    if falhas > 0:
        print("\n[CI/CD BLOCK] Regressao na qualidade ou seguranca detectada. Pipeline cancelado.")
        sys.exit(1)
    else:
        print("\n[CI/CD SUCCESS] Core aprovado para deploy em producao!")
        sys.exit(0)

if __name__ == "__main__":
    run_evaluation_pipeline()
