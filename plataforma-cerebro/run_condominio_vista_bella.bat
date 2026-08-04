@echo off
echo =========================================================
echo INICIANDO INSTANCIA ISOLADA (SINGLE TENANT)
echo Tenant: Condominio Vista Bella
echo Porta: 8001
echo API Key: key_condominio_vista_bella_7445ed99b909
echo =========================================================
set COMPANY_CONFIG_PATH=config\tenant_condominio_vista_bella_config.yaml
set PORT=8001
python -m uvicorn core.api:app --host 0.0.0.0 --port %PORT%
