@echo off
:: Abre o Chrome com debug remoto habilitado para o Grid
:: Rodar este script UMA VEZ por dia (ou deixar Chrome aberto)
:: Após abrir, faça login no Grid normalmente

set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist %CHROME% set CHROME="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

echo Abrindo Chrome com debug remoto para o Grid...
start "" %CHROME% ^
  --remote-debugging-port=9222 ^
  --user-data-dir="C:\Users\allabriola\ChromeGridProfile" ^
  "https://grid.adminml.com/d/01KRBESTYE6P7M3FG2FS4KVES2/view"

echo Chrome aberto. Faca login no Grid se necessario.
echo Pode fechar esta janela.
