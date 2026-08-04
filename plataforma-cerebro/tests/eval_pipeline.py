import os
import sys
import json
import subprocess
import re

# Adicionar diretorio pai ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.engine import EnterpriseBrainEngine

# Forçar codificação UTF-8 no stdout para evitar erros em consoles Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

def run_static_security_audit():
    """Executa a auditoria de segurança estática no início do pipeline."""
    print("="*70)
    print("ETAPA 1: RODANDO AUDITORIA DE SEGURANCA ESTATICA...")
    print("="*70)
    
    script_path = os.path.join("scripts", "verify_policy.py")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    
    print(result.stdout)
    if result.returncode != 0:
        print("[CI/CD BLOCK] Falha na Auditoria de Segurança Estática. Deploy bloqueado!")
        sys.exit(1)

def parse_gherkin_specs(feature_path):
    """
    Parser simplificado de Gherkin (.feature).
    Lê o arquivo de especificação e extrai os cenários de forma estruturada.
    """
    if not os.path.exists(feature_path):
        print(f"Erro: Arquivo Gherkin '{feature_path}' nao encontrado.")
        sys.exit(1)
        
    with open(feature_path, "r", encoding="utf-8") as f:
        content = f.read()

    scenarios = []
    current_scenario = None
    
    lines = content.splitlines()
    for line in lines:
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("#"):
            continue
            
        if line_strip.startswith("Scenario:"):
            if current_scenario:
                scenarios.append(current_scenario)
            current_scenario = {
                "name": line_strip.split("Scenario:")[1].strip(),
                "user_role": None,
                "condo_id": None,
                "payment_value": 0.0,
                "prompt": None,
                "status_esperado": None
            }
        elif current_scenario:
            if line_strip.startswith("Given o usuario possui cargo"):
                # Extrai o valor entre aspas simples
                role = re.search(r"'(.*?)'", line_strip)
                if role:
                    current_scenario["user_role"] = role.group(1)
            elif line_strip.startswith("And o condominio e"):
                condo = re.search(r"'(.*?)'", line_strip)
                if condo:
                    current_scenario["condo_id"] = condo.group(1)
            elif line_strip.startswith("And o valor do pagamento e R$"):
                val = re.search(r"R\$\s*([0-9.]+)", line_strip)
                if val:
                    current_scenario["payment_value"] = float(val.group(1))
            elif line_strip.startswith("When o usuario solicita"):
                pr = re.search(r"'(.*?)'", line_strip)
                if pr:
                    current_scenario["prompt"] = pr.group(1)
            elif line_strip.startswith("Then o motor deve retornar status"):
                st = re.search(r"'(.*?)'", line_strip)
                if st:
                    current_scenario["status_esperado"] = st.group(1)

    if current_scenario:
        scenarios.append(current_scenario)
        
    return scenarios

def run_evaluation_pipeline():
    # 1. Executar a Auditoria Estática de Segurança
    run_static_security_audit()
    
    print("\n" + "="*70)
    print("ETAPA 2: PARSEANDO ESPECIFICACOES GHERKIN EXECUTAVEIS...")
    print("="*70)
    
    feature_path = os.path.join("specs", "test_specs.feature")
    scenarios = parse_gherkin_specs(feature_path)
    
    print(f"Sucesso: {len(scenarios)} cenários de teste Gherkin parseados.")
    
    print("\n" + "="*70)
    print("ETAPA 3: EXECUTANDO AVALIACAO DO GOLDEN DATASET (GHERKIN RUNNER)")
    print("="*70)
    
    engine = EnterpriseBrainEngine()
    
    sucessos = 0
    falhas = 0
    relatorio_eval = []
    
    for case in scenarios:
        print(f"\n[Scenario] {case['name']}")
        print(f"  Given: Role='{case['user_role']}' | Condo='{case['condo_id']}' | Value=R$ {case['payment_value']:.2f}")
        print(f"  When: Prompt='{case['prompt']}'")
        
        # Executar o motor real passando o token JIT
        res = engine.process_request(
            prompt=case["prompt"],
            user_role=case["user_role"],
            user_id="sistema_eval_user",
            condo_id=case["condo_id"],
            payment_value=case["payment_value"],
            session_token="token-valido-eval"
        )
        
        status_obtido = res["status"]
        
        # Validação
        if status_obtido == case["status_esperado"]:
            print(f"  [PASS] Status obtido '{status_obtido}' condiz com esperado '{case['status_esperado']}'.")
            sucessos += 1
            resultado_teste = "PASS"
        else:
            print(f"  [FAIL] Status obtido '{status_obtido}', esperado '{case['status_esperado']}'")
            falhas += 1
            resultado_teste = "FAIL"
            
        relatorio_eval.append({
            "scenario": case["name"],
            "status_esperado": case["status_esperado"],
            "status_obtido": status_obtido,
            "resultado": resultado_teste,
            "motivo_bloqueio": res.get("motivo", "N/A")
        })
        
    print("\n" + "="*70)
    print("RESULTADOS FINAIS DA AVALIACAO GHERKIN E CI/CD")
    print("="*70)
    print(f"  Total de Cenários Executados: {len(scenarios)}")
    print(f"  Aprovados: {sucessos}")
    print(f"  Falhas: {falhas}")
    print(f"  Acuracia Geral do Core: {(sucessos / len(scenarios)) * 100:.1f}%")
    print("="*70)
    
    # Salvar logs do pipeline em JSON para rastreamento de CI/CD
    eval_log_path = "tests/eval_results_log.json"
    os.makedirs("tests", exist_ok=True)
    with open(eval_log_path, "w", encoding="utf-8") as f:
        json.dump(relatorio_eval, f, indent=2)
    print(f"Log do pipeline salvo em: {eval_log_path}")
    
    if falhas > 0:
        print("\n[CI/CD BLOCK] Falha nos testes de especificacao. Pipeline cancelado.")
        sys.exit(1)
    else:
        print("\n[CI/CD SUCCESS] Core aprovado e auditado para deploy em producao!")
        sys.exit(0)

if __name__ == "__main__":
    run_evaluation_pipeline()
