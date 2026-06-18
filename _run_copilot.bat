@echo off
chcp 65001 > nul
echo ============================================
echo  CX Copilot - Dashboard de Usabilidade
echo ============================================
echo.

echo [1/3] Buscando dados do BigQuery...
python _copilot_fetch.py
if %errorlevel% neq 0 (echo ERRO no fetch! & pause & exit /b 1)
echo.

echo [2/3] Categorizando consultas com Claude...
python _copilot_categorize.py
if %errorlevel% neq 0 (echo ERRO na categorização! & pause & exit /b 1)
echo.

echo [3/3] Gerando dashboard HTML...
python _build_copilot_dashboard.py
if %errorlevel% neq 0 (echo ERRO no build! & pause & exit /b 1)
echo.

echo ============================================
echo  Dashboard gerado: copiloto_usabilidade.html
echo ============================================
start copiloto_usabilidade.html
