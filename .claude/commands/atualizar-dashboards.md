---
description: Atualiza os 4 dashboards diários (outgoing drivers, NPS Seller Dev, Copiloto, Async Longtail) e publica no GitHub Pages
---

Atualize os quatro dashboards abaixo, nesta ordem. São scripts Python em `C:\claudinho` que consultam o BigQuery (podem demorar alguns minutos cada) e geram HTMLs publicados no repo `allabriola/nps-driver-test2` (GitHub Pages, branch `main`).

Regras gerais:
- Rode cada bloco de forma independente: se um falhar, registre o erro, siga para o próximo e reporte no final. Não aborte tudo por causa de um.
- Use a data de hoje no formato DD/MM/YYYY nas mensagens de commit.
- Faça commit + push ao final de cada bloco que gerar com sucesso (ou um único commit no fim com tudo — sua escolha, mas garanta o push).
- Ao terminar, entregue um resumo em tabela: dashboard | status (OK/erro) | observação (ex.: datas, contagens, lag da fonte).

## 1. Outgoing Drivers — `outgoing_drivers_analysis.html`
- Rode: `python build_outgoing_drivers.py` (aguarde `✓ Gerado: outgoing_drivers_analysis.html`; pode levar até ~10 min; se der quota do BQ, o script faz retry sozinho).
- Commit: `outgoing_drivers_analysis.html _cache_drivers_charts.json _tr_cache_Drivers_*.json _tr_weekly_*.json`

## 2. NPS Tendências Seller Dev — `nps_tendencias_seller_dev.html`
Pipeline completo de dados frescos (vigente + mensal), nesta ordem:
1. `python _fetch_weekly_data.py`  (janela vigente dinâmica; "Dados até" = última data com dado real — lag ~D-2 é normal)
2. `python _update_weekly.py`
3. `python _fetch_monthly_data.py`  (recomputa meses fechados + mês corrente MTD)
4. `python _update_monthly.py`  (trava de virada: mantém mês anterior como M1 enquanto o corrente estiver vazio)
5. `python generate_html_tendencias.py`  (gera nps_tendencias_gerencia.html)
6. `python generate_html_seller_dev.py`  (gera nps_tendencias_seller_dev.html — o erro `Grid: No module named 'playwright'` é esperado e NÃO afeta o GitHub Pages)
7. `python _save_monthly_snapshot.py`  (aba "Fechamentos Mensais": snapshota o último mês fechado completo; remove o mês corrente da aba)
8. **SÓ SE HOJE FOR SEGUNDA-FEIRA** (virada de semana): congela a semana que fechou.
   - `python _save_snapshot.py`
   - `python _generate_weekly_snapshots.py`
   - `python generate_html_seller_dev.py`  (regera p/ embutir o histórico novo)
   - Nesse caso, inclua também `history/ history_sd/` no commit.
   - (Verifique o dia com: `python -c "import datetime;print(datetime.date.today().weekday())"` → 0 = segunda.)
- Commit: `nps_tendencias_seller_dev.html nps_tendencias_gerencia.html generate_html_gerencia.py _new_weekly_data.json _monthly_result.json history_sd/ history/`

## 3. Copiloto Usabilidade — `copiloto_usabilidade.html`
1. `python _copilot_fetch.py`  (o 403 nas transcrições é esperado — aba "Consultas" fica indisponível; os dados de reps/adoção/NPS/TMO funcionam normalmente)
2. `python _build_copilot_dashboard.py`
- Senioridade Expert/Newbie vem de `BT_CX_KM_TRAINING_STATUS`; filtro de ativos vem de `BT_CX_STAFF_HISTORY` (USER_STATUS). Não mexer nisso.
- Commit: `copiloto_usabilidade.html _copilot_reps.json _copilot_by_process.json`

## 4. Async Longtail — `async_longtail.html`
- Rode: `python _build_async_longtail.py`  (auto-suficiente; gera `_async_longtail.html` e `async_longtail.html`)
- Commit: `async_longtail.html _async_longtail.html`

## Fechamento
- `git push` (se não empurrou por bloco).
- Confirme que os links estão no ar:
  - https://allabriola.github.io/nps-driver-test2/outgoing_drivers_analysis.html
  - https://allabriola.github.io/nps-driver-test2/nps_tendencias_seller_dev.html
  - https://allabriola.github.io/nps-driver-test2/copiloto_usabilidade.html
  - https://allabriola.github.io/nps-driver-test2/async_longtail.html
