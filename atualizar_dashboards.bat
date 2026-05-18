@echo off
:: Atualiza os dashboards de NPS - roda diariamente via Task Scheduler
:: Saida de log: C:\Users\allabriola\PROJETO CLAUDINHO\logs\atualizar_%data%.log

setlocal
set PROJ=C:\Users\allabriola\PROJETO CLAUDINHO
set LOG_DIR=%PROJ%\logs
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set LOG=%LOG_DIR%\atualizar_%%c%%b%%a.log

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo [%date% %time%] === Iniciando atualizacao diaria === >> "%LOG%"

:: Ativar ambiente Python correto
cd /d "%PROJ%"

:: Detecta se hoje e segunda-feira (0=Dom, 1=Seg, ..., 6=Sab no PowerShell)
for /f %%D in ('powershell -NoProfile -Command "(Get-Date).DayOfWeek.value__"') do set DOW=%%D

:: 1 - NPS Seller Dev BR
echo [%date% %time%] Atualizando NPS Seller Dev BR... >> "%LOG%"
python generate_html.py >> "%LOG%" 2>&1
if %errorlevel% equ 0 (
    echo [%date% %time%] NPS Seller Dev BR: OK >> "%LOG%"
) else (
    echo [%date% %time%] NPS Seller Dev BR: ERRO (codigo %errorlevel%) >> "%LOG%"
)

:: 2 - Driver Impact Dashboard
echo [%date% %time%] Atualizando Driver Impact... >> "%LOG%"
python build_driver_impact.py >> "%LOG%" 2>&1
if %errorlevel% equ 0 (
    git add driver_impact.html build_driver_impact.py 2>> "%LOG%"
    git commit -m "Auto-update Driver Impact - %date%" 2>> "%LOG%"
    git push origin main 2>> "%LOG%"
    echo [%date% %time%] Driver Impact: OK >> "%LOG%"
) else (
    echo [%date% %time%] Driver Impact: ERRO (codigo %errorlevel%) >> "%LOG%"
)

:: 3 - NPS Tendencias Gerencia (todos os drivers - diario)
echo [%date% %time%] Atualizando NPS Tendencias Gerencia... >> "%LOG%"
python generate_html_tendencias.py >> "%LOG%" 2>&1
if %errorlevel% equ 0 (
    git add nps_tendencias_gerencia.html >> "%LOG%" 2>&1
    git commit -m "Auto-update NPS Tendencias Gerencia - %date%" >> "%LOG%" 2>&1
    git push origin main >> "%LOG%" 2>&1
    echo [%date% %time%] NPS Tendencias Gerencia: OK >> "%LOG%"
) else (
    echo [%date% %time%] NPS Tendencias Gerencia: ERRO (codigo %errorlevel%) >> "%LOG%"
)

:: 4 - Busca casos detratores do BQ (para Highlights & Resumos por driver)
echo [%date% %time%] Buscando casos recorrentes BQ... >> "%LOG%"
python _fetch_recurrence_cases.py >> "%LOG%" 2>&1
if %errorlevel% equ 0 (
    echo [%date% %time%] Casos BQ: OK >> "%LOG%"
) else (
    echo [%date% %time%] Casos BQ: ERRO (codigo %errorlevel%) >> "%LOG%"
)

:: 5 - Gera Highlights & Analise (exec summary com dados frescos)
echo [%date% %time%] Gerando exec summary SD... >> "%LOG%"
python _build_exec_sd.py >> "%LOG%" 2>&1
if %errorlevel% equ 0 (
    echo [%date% %time%] Exec summary SD: OK >> "%LOG%"
) else (
    echo [%date% %time%] Exec summary SD: ERRO (codigo %errorlevel%) >> "%LOG%"
)

:: 6 - NPS Tendencias Seller Dev (diario)
echo [%date% %time%] Atualizando NPS Tendencias Seller Dev... >> "%LOG%"
python generate_html_seller_dev.py >> "%LOG%" 2>&1
if %errorlevel% equ 0 (
    git add nps_tendencias_seller_dev.html _recurrence_cases.json _exec_summary_sd.html >> "%LOG%" 2>&1
    git commit -m "Auto-update NPS Tendencias Seller Dev - %date%" >> "%LOG%" 2>&1
    git push origin main >> "%LOG%" 2>&1
    echo [%date% %time%] NPS Tendencias Seller Dev: OK >> "%LOG%"
) else (
    echo [%date% %time%] NPS Tendencias Seller Dev: ERRO (codigo %errorlevel%) >> "%LOG%"
)

:: 7 - Snapshot mensal parcial (diario - mantem Maio MTD atualizado)
echo [%date% %time%] Atualizando snapshot mensal MTD... >> "%LOG%"
python _save_monthly_snapshot.py >> "%LOG%" 2>&1
if %errorlevel% equ 0 (
    git add history_sd/mensal_*.html history_sd/mensal_index.json >> "%LOG%" 2>&1
    git commit -m "Auto-update snapshot mensal MTD - %date%" >> "%LOG%" 2>&1
    git push origin main >> "%LOG%" 2>&1
    echo [%date% %time%] Snapshot mensal: OK >> "%LOG%"
) else (
    echo [%date% %time%] Snapshot mensal: ERRO (codigo %errorlevel%) >> "%LOG%"
)

:: 8 - Snapshot semanal (somente segunda-feira, DOW=1)
if "%DOW%"=="1" (
    echo [%date% %time%] Segunda-feira: salvando snapshots e gerando semanas fechadas... >> "%LOG%"
    python _save_snapshot.py >> "%LOG%" 2>&1
    python _generate_weekly_snapshots.py >> "%LOG%" 2>&1
    if %errorlevel% equ 0 (
        :: Regera SD para embutir history atualizado e faz push
        python generate_html_seller_dev.py >> "%LOG%" 2>&1
        git add history/ history_sd/ nps_tendencias_gerencia.html nps_tendencias_seller_dev.html >> "%LOG%" 2>&1
        git commit -m "Auto-snapshot semanal + semanas fechadas - %date%" >> "%LOG%" 2>&1
        git push origin main >> "%LOG%" 2>&1
        echo [%date% %time%] Snapshot semanal: OK >> "%LOG%"
    ) else (
        echo [%date% %time%] Snapshot semanal: ERRO (codigo %errorlevel%) >> "%LOG%"
    )
)

echo [%date% %time%] === Atualizacao concluida === >> "%LOG%"
endlocal
