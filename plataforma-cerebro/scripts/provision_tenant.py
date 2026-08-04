import os
import sys
import yaml
import secrets
import argparse

def provision_tenant(name, port, api_key=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, "config")
    
    # 1. Normalizar nome do tenant
    tenant_id = name.lower().replace(" ", "_")
    
    # 2. Gerar chaves se nao informadas
    if not api_key:
        api_key = f"key_{tenant_id}_{secrets.token_hex(6)}"
        
    signing_key = f"sig_{tenant_id}_{secrets.token_hex(8)}"
    db_path = f"chat_history_{tenant_id}.db"

    # 3. Construir dicionario de configuracao isolado (Single Tenant)
    tenant_config = {
        "company": {
            "name": name,
            "api_key": api_key,
            "signing_key": signing_key
        },
        "database": {
            "provider": "sqlite",
            "memory": {
                "provider": "sqlite",
                "database": db_path
            }
        },
        "agents": {
            "guardrail": {
                "max_payment_limit": 50000.0
            }
        }
    }

    # 4. Gravar arquivo YAML de configuracao do tenant
    config_file_name = f"tenant_{tenant_id}_config.yaml"
    config_file_path = os.path.join(config_dir, config_file_name)
    
    with open(config_file_path, "w", encoding="utf-8") as f:
        yaml.dump(tenant_config, f, default_flow_style=False, indent=2)

    # 5. Criar script de execucao isolado (Windows .bat)
    run_script_name = f"run_{tenant_id}.bat"
    run_script_path = os.path.join(base_dir, run_script_name)
    
    bat_content = f"""@echo off
echo =========================================================
echo INICIANDO INSTANCIA ISOLADA (SINGLE TENANT)
echo Tenant: {name}
echo Porta: {port}
echo API Key: {api_key}
echo =========================================================
set COMPANY_CONFIG_PATH=config\\{config_file_name}
set PORT={port}
python -m uvicorn core.api:app --host 0.0.0.0 --port %PORT%
"""
    with open(run_script_path, "w", encoding="utf-8") as f:
        f.write(bat_content)

    print("="*60)
    print(f"TENANT '{name}' PROVISIONADO COM SUCESSO!")
    print("="*60)
    print(f"  - Config: {os.path.relpath(config_file_path, base_dir)}")
    print(f"  - Batch: {os.path.relpath(run_script_path, base_dir)}")
    print(f"  - API Key de Gateway: {api_key}")
    print(f"  - Signing Key (HMAC): {signing_key}")
    print(f"  - Porta de Escuta: {port}")
    print(f"Para iniciar este tenant, execute: .\\{run_script_name}")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Provisionamento do Plataforma Cérebro para Novos Tenants (Single Tenant).")
    parser.add_argument("--name", required=True, help="Nome do Condominio/Cliente Tenant")
    parser.add_argument("--port", required=True, type=int, help="Porta TCP de execucao do tenant")
    parser.add_argument("--key", help="API Key do Gateway (Opcional - Gerada automaticamente se omitida)")
    
    args = parser.parse_args()
    provision_tenant(args.name, args.port, args.key)

if __name__ == "__main__":
    main()
