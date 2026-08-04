import os
import sys
import subprocess
import datetime

def log_factory(message, success=True):
    prefix = "[SUCCESS]" if success else "[WARNING]"
    print(f"[Factory Model] {prefix} {message}")

def run_tests():
    """Roda a suíte de testes unitários e retorna se passaram."""
    try:
        # Executa o unittest
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "tests/test_engine.py"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stderr + result.stdout
    except Exception as e:
        return False, str(e)

def main():
    if len(sys.argv) < 3:
        print("Uso: python scripts/generate_code.py <caminho_especificacao> <caminho_arquivo_alvo>")
        sys.exit(1)

    spec_path = sys.argv[1]
    target_path = sys.argv[2]

    if not os.path.exists(spec_path):
        log_factory(f"Especificacao '{spec_path}' nao encontrada.", success=False)
        sys.exit(1)

    # 1. Ler a especificação
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_content = f.read()

    # 2. Ler código atual se existir
    existing_code = ""
    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            existing_code = f.read()

    log_factory(f"Lendo especificação '{spec_path}' para reconstruir '{target_path}'...")

    # 3. Verificar API Key do Gemini
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    generated_code = ""
    
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            
            # Utilizar o modelo gemini-1.5-flash para geração de código rápida
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            Você é um Engenheiro de IA especializado no framework New SDLC.
            Sua missão é gerar ou atualizar o código Python do arquivo '{target_path}' para que ele cumpra estritamente com a especificação fornecida abaixo.

            --- ESPECIFICAÇÃO ---
            {spec_content}
            ----------------------

            --- CÓDIGO ATUAL ---
            {existing_code}
            --------------------

            REGRAS DE GERAÇÃO:
            1. O código gerado deve ser sintaticamente correto em Python 3.
            2. Mantenha os conectores e o fallback mock caso as dependências externas não estejam instaladas.
            3. Retorne APENAS o código Python pronto para gravação. Não inclua blocos de markdown ```python ... ``` nem explicações textuais adicionais.
            """
            
            log_factory("Chamando API do Google Gemini para compilar especificação...")
            response = model.generate_content(prompt)
            generated_code = response.text.strip()
            
            # Limpar blocos de markdown que o modelo possa ter inserido por teimosia
            if generated_code.startswith("```python"):
                generated_code = generated_code[9:]
            if generated_code.endswith("```"):
                generated_code = generated_code[:-3]
            generated_code = generated_code.strip()
            
        except Exception as e:
            log_factory(f"Falha ao chamar API do Gemini ({e}). Entrando em modo Offline/Mock...", success=False)
            gemini_key = None

    if not gemini_key:
        # Modo Offline (Mock de geração para testes locais)
        log_factory("Rodando em modo OFFLINE/MOCK. Simulando a atualização de specs no arquivo alvo...")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simula a alteração inserindo um comentário de cabeçalho com a especificação
        header_comment = f"# --- RECONSTRUÍDO VIA SPEC-DRIVEN DEVELOPMENT --- \n# Data: {timestamp}\n# Spec de Referência: {spec_path}\n"
        if existing_code.startswith("# --- RECONSTRUÍDO VIA SPEC-DRIVEN DEVELOPMENT ---"):
            # Remover cabeçalho antigo para atualizar
            lines = existing_code.splitlines()
            # Pular as primeiras 3 linhas do cabeçalho antigo
            existing_code = "\n".join(lines[3:])
            
        generated_code = header_comment + existing_code

    # 4. Criar backup temporário para validação
    temp_target_path = target_path + ".tmp"
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(temp_target_path, "w", encoding="utf-8") as f:
        f.write(generated_code)

    # 5. Executar os testes de regressão com o código novo
    log_factory("Rodando testes de regressão antes de confirmar as alterações no core...")
    
    # Temporariamente substituir o arquivo original pelo temporário para rodar testes
    backup_path = target_path + ".bak"
    has_backup = os.path.exists(target_path)
    
    if has_backup:
        os.rename(target_path, backup_path)
    os.rename(temp_target_path, target_path)

    tests_passed, test_output = run_tests()

    if tests_passed:
        log_factory(f"Código validado! Todos os testes de regressão passaram.")
        if has_backup:
            os.remove(backup_path) # Deleta o backup antigo
        log_factory(f"Arquivo '{target_path}' atualizado com sucesso a partir das especificações.")
        sys.exit(0)
    else:
        log_factory("FALHA NA VALIDAÇÃO: O código gerado quebrou os testes unitários corporativos!", success=False)
        print("\n--- SAÍDA DOS TESTES ---")
        print(test_output)
        print("------------------------\n")
        
        # Reverter alteração
        os.remove(target_path)
        if has_backup:
            os.rename(backup_path, target_path)
        log_factory("Reversão concluída. Código original restaurado.", success=False)
        sys.exit(1)

if __name__ == "__main__":
    main()
