@echo off
:: csat_daily_update.bat — Atualiza CSAT Dashboard diariamente
:: Task Scheduler: "CSAT Longtail Daily Update" às 08:20

setlocal
set PROJ=C:\claudinho
set LOG_DIR=%PROJ%\logs
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set LOG=%LOG_DIR%\csat_%%c%%b%%a.log

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%PROJ%"
echo [%date% %time%] === CSAT Dashboard — inicio === >> "%LOG%"

:: 1 — Fetch BQ
echo [%date% %time%] [1/3] Buscando dados BQ... >> "%LOG%"
python csat_fetch.py >> "%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo [%date% %time%] ERRO no csat_fetch.py — abortando >> "%LOG%"
    exit /b 1
)
echo [%date% %time%] [1/3] Fetch: OK >> "%LOG%"

:: 2 — Diagnóstico Claude API
echo [%date% %time%] [2/3] Gerando diagnostico (Claude API)... >> "%LOG%"
python csat_diagnostic.py >> "%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo [%date% %time%] AVISO: csat_diagnostic.py falhou — continuando sem diagnostico IA >> "%LOG%"
    :: Não aborta: build_csat_dashboard aceita _csat_diagnostic.json ausente
)
echo [%date% %time%] [2/3] Diagnostico: OK (ou skip) >> "%LOG%"

:: 3 — Build HTML
echo [%date% %time%] [3/3] Gerando HTML... >> "%LOG%"
python build_csat_dashboard.py >> "%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo [%date% %time%] ERRO no build_csat_dashboard.py >> "%LOG%"
    exit /b 1
)
echo [%date% %time%] [3/3] Build: OK >> "%LOG%"

:: Git commit + push
echo [%date% %time%] Commit git... >> "%LOG%"
git add csat_dashboard.html _csat_data.json _csat_diagnostic.json >> "%LOG%" 2>&1
git commit -m "Auto-update CSAT Dashboard - %date%" >> "%LOG%" 2>&1
git push origin main >> "%LOG%" 2>&1
echo [%date% %time%] Git: OK >> "%LOG%"

echo [%date% %time%] === CSAT Dashboard — concluido === >> "%LOG%"
endlocal
