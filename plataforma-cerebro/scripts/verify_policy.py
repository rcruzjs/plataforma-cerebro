import os
import re
import sys

def log_policy(message, violation=False):
    prefix = "[VIOLATION]" if violation else "[POLICY]"
    print(f"{prefix} {message}")

def scan_files():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Padrões perigosos
    secret_patterns = [
        r"(?i)api_key\s*=\s*['\"][a-zA-Z0-9_-]{20,}['\"]", # chaves suspeitas atribuídas estaticamente
        r"(?i)sk-proj-[a-zA-Z0-9]{20,}",                     # chaves OpenAI reais
    ]
    
    forbidden_calls = [
        (r"\beval\(", "Chamada proibida para 'eval()' (risco de execucao de codigo dinamico)."),
        (r"\bexec\(", "Chamada proibida para 'exec()' (risco de execucao de codigo dinamico).")
    ]
    
    install_patterns = [
        (r"pip\s+install", "Comando dinamico de pip install detectado no codigo."),
        (r"npm\s+install", "Comando dinamico de npm install detectado no codigo.")
    ]

    violations = 0

    for root, dirs, files in os.walk(base_dir):
        # Ignorar pastas virtuais e caches
        if any(ignored in root for ignored in ["venv", ".git", "__pycache__", "chat_history.db"]):
            continue
            
        for file in files:
            if not file.endswith(".py"):
                continue
                
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, base_dir)
            
            # Ignorar o proprio script de politica
            if "verify_policy.py" in file:
                continue

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            lines = content.splitlines()
            
            # 1. Verificar Secrets Hardcoded
            for pattern in secret_patterns:
                matches = re.findall(pattern, content)
                # Ignorar placeholders conhecidos nos testes
                for match in matches:
                    if "default-secret-key" in match or "prod-sec-key" in match:
                        continue
                    log_policy(f"Secret estatico suspeito encontrado em '{relative_path}': '{match}'", violation=True)
                    violations += 1
            
            # 2. Verificar Chamadas Proibidas (eval/exec)
            for pattern, desc in forbidden_calls:
                for i, line in enumerate(lines):
                    # Ignorar comentarios
                    if line.strip().startswith("#"):
                        continue
                    if re.search(pattern, line):
                        log_policy(f"{desc} em '{relative_path}' na linha {i+1}: '{line.strip()}'", violation=True)
                        violations += 1

            # 3. Verificar Instaladores Dinamicos (Npm/Pip)
            for pattern, desc in install_patterns:
                for i, line in enumerate(lines):
                    if line.strip().startswith("#"):
                        continue
                    if re.search(pattern, line):
                        log_policy(f"{desc} em '{relative_path}' na linha {i+1}: '{line.strip()}'", violation=True)
                        violations += 1

    return violations

def main():
    print("="*70)
    print("AUDITORIA DE SEGURANCA ESTATICA (ZERO-TRUST POLICY CHECKER)")
    print("="*70)
    
    violations = scan_files()
    
    print("="*70)
    if violations > 0:
        log_policy(f"FALHA: {violations} violacao(oes) de politica de seguranca encontrada(s)!", violation=True)
        sys.exit(1)
    else:
        log_policy("SUCESSO: Nenhuma violacao de seguranca estatica encontrada no codigo core.")
        sys.exit(0)

if __name__ == "__main__":
    main()
