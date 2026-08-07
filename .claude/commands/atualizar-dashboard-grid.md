---
description: Atualiza os 5 dashboards diários (outgoing drivers, NPS Seller Dev, Copiloto, Async Longtail, CSAT) e publica no Grid com link compartilhável
---

Atualize os cinco dashboards abaixo, nesta ordem. São scripts Python em `C:\claudinho` que consultam o BigQuery (podem demorar alguns minutos cada) e geram HTMLs que são publicados no Grid (não no GitHub Pages).

Os doc_ids do Grid estão em `C:\claudinho\_grid_doc_ids.json`. Sempre use `file_new_version: true` para criar nova versão no doc existente — nunca crie um novo documento.

**Versão do skill Grid:** verifique com `curl -s "https://grid.melioffice.com/skill/version?current_version=3.6.4"` antes de iniciar. Se retornar `up_to_date: false`, peça ao usuário rodar `/skill install https://grid.melioffice.com/skill` em um terminal interativo do Claude antes de continuar. Se não for possível atualizar agora, use `skip_version_check: true` nos curls abaixo.

Regras gerais:
- Rode cada bloco de forma independente: se um falhar, registre o erro, siga para o próximo e reporte no final. Não aborte tudo por causa de um.
- Após gerar cada HTML com sucesso, publique imediatamente no Grid (curl abaixo) antes de passar para o próximo dashboard.
- Ao terminar, entregue um resumo em tabela: dashboard | status (OK/erro) | versão Grid | link | observação (ex.: datas, contagens, lag da fonte).

---

## 1. Outgoing Drivers — `outgoing_drivers_analysis.html`

**Gerar HTML:**
- Rode: `python build_outgoing_drivers.py` (aguarde `✓ Gerado: outgoing_drivers_analysis.html`; pode levar até ~10 min; se der quota do BQ, o script faz retry sozinho).

**Publicar no Grid:**
```bash
curl -s -X POST "https://grid.melioffice.com/api/v1/engine/run" \
  -F 'config={"skill_version":"3.6.4","doc_id":"01KX12R63S5G2VZXXH7J5QDSZN","file_new_version":true}' \
  -F "file=@C:/claudinho/outgoing_drivers_analysis.html"
```
Link: https://grid.adminml.com/d/01KX12R63S5G2VZXXH7J5QDSZN/view

---

## 2. NPS Tendências Seller Dev — `nps_tendencias_seller_dev.html`

**Gerar HTML** — pipeline completo de dados frescos (vigente + mensal), nesta ordem:
1. `python _fetch_weekly_data.py`  (janela vigente dinâmica; "Dados até" = última data com dado real — lag ~D-2 é normal)
2. `python _update_weekly.py`
3. `python _fetch_monthly_data.py`  (recomputa meses fechados + mês corrente MTD)
4. `python _update_monthly.py`  (trava de virada: mantém mês anterior como M1 enquanto o corrente estiver vazio)
4b. `python _fetch_monthly_breakdown.py`  (aberturas mensais por processo/senioridade/oficina/equipe — mês atual + anterior; alimenta a aba Evolução Mensal → Análise por Driver. Pode demorar, tem várias queries.)
5. `python generate_html_tendencias.py`  (gera nps_tendencias_gerencia.html)
6. `python generate_html_seller_dev.py`  (gera nps_tendencias_seller_dev.html — o erro `Grid: No module named 'playwright'` é esperado e NÃO afeta o Grid)
7. `python _save_monthly_snapshot.py`  (aba "Fechamentos Mensais": snapshota o último mês fechado completo; remove o mês corrente da aba)
8. **SÓ SE HOJE FOR SEGUNDA-FEIRA** (virada de semana): congela a semana que fechou.
   - (Verifique o dia com: `python -c "import datetime;print(datetime.date.today().weekday())"` → 0 = segunda.)
   - `python _fetch_recurrence_historical.py`  (**OBRIGATÓRIO antes do _save_snapshot** — atualiza o WHY analysis da semana que fechou: processo top negativo/positivo, CDU e motivos dos casos. Sem esse passo, o resumo executivo da semana fechada fica sem análise de causa.)
   - `python _save_snapshot.py`
   - `python _generate_weekly_snapshots.py`
   - `python generate_html_seller_dev.py`  (regera p/ embutir o histórico novo)

   **Após gerar, verificar antes de publicar:**
   - Aba da semana recém fechada → Resumo Executivo deve conter "O processo X foi o principal vetor da queda..." (não apenas bullets básicos de NPS)
   - Aba Visão Executiva → Highlights & Análise deve ter **6 drivers** (ME Vendedor, PCF Vendedor, Post Venta, Publicaciones, Exp. Impositiva, Partners), cada um com seniority breakdown + oficinas + CDU/processo. Se faltar: rodar `python _build_exec_sd.py` e `python generate_html_seller_dev.py` novamente.

**Publicar no Grid:**
```bash
curl -s -X POST "https://grid.melioffice.com/api/v1/engine/run" \
  -F 'config={"skill_version":"3.6.4","doc_id":"01KRBESTYE6P7M3FG2FS4KVES2","file_new_version":true}' \
  -F "file=@C:/claudinho/nps_tendencias_seller_dev.html"
```
Link: https://grid.adminml.com/d/01KRBESTYE6P7M3FG2FS4KVES2/view

---

## 3. Copiloto Usabilidade — `copiloto_usabilidade.html`

**Gerar HTML:**
1. `python _copilot_fetch.py`  (o 403 nas transcrições é esperado — aba "Consultas" fica indisponível; os dados de reps/adoção/NPS/TMO funcionam normalmente)
2. `python _build_copilot_dashboard.py`
- Senioridade Expert/Newbie vem de `BT_CX_KM_TRAINING_STATUS`; filtro de ativos vem de `BT_CX_STAFF_HISTORY` (USER_STATUS). Não mexer nisso.

**Publicar no Grid:**
```bash
curl -s -X POST "https://grid.melioffice.com/api/v1/engine/run" \
  -F 'config={"skill_version":"3.6.4","doc_id":"01KX131TPRN818YPAJZKY21DHE","file_new_version":true}' \
  -F "file=@C:/claudinho/copiloto_usabilidade.html"
```
Link: https://grid.adminml.com/d/01KX131TPRN818YPAJZKY21DHE/view

---

## 4. Async Longtail — `async_longtail.html`

**Gerar HTML:**
- Rode: `python _build_async_longtail.py`  (auto-suficiente; gera `_async_longtail.html` e `async_longtail.html`)

**Publicar no Grid:**
```bash
curl -s -X POST "https://grid.melioffice.com/api/v1/engine/run" \
  -F 'config={"skill_version":"3.6.4","doc_id":"01KX12PSQHT8NHA128X1CYN2EN","file_new_version":true}' \
  -F "file=@C:/claudinho/async_longtail.html"
```
Link: https://grid.adminml.com/d/01KX12PSQHT8NHA128X1CYN2EN/view

---

---

## 5. CSAT — `csat_dashboard.html`

**Gerar HTML:**
1. `python csat_fetch.py`  (busca dados do BQ para 4 equipes; salva `_csat_data.json`)
2. `python csat_diagnostic.py`  (Claude API → diagnóstico por processo; salva `_csat_diagnostic.json`. Requer `ANTHROPIC_API_KEY`. Se falhar, o build continua sem diagnóstico IA.)
3. `python build_csat_dashboard.py`  (gera `csat_dashboard.html`)

**Publicar no Grid:**
```bash
curl -s -X POST "https://grid.melioffice.com/api/v1/engine/run" \
  -F 'config={"skill_version":"3.6.5","doc_id":"01KQ3BMS9EGKTB3QHEZXXW4E46","file_new_version":true,"title":"CSAT — BR Longtail + ExpImpo"}' \
  -F "file=@C:/claudinho/csat_dashboard.html"
```
Link: https://grid.adminml.com/d/01KQ3BMS9EGKTB3QHEZXXW4E46/view

---

## Fechamento

Confirme que as versões subiram verificando o campo `version` na resposta de cada curl.
Entregue resumo em tabela:

| Dashboard | Status | Versão Grid | Link |
|---|---|---|---|
| Outgoing Drivers | | | https://grid.adminml.com/d/01KX12R63S5G2VZXXH7J5QDSZN/view |
| NPS Tendências Seller Dev | | | https://grid.adminml.com/d/01KRBESTYE6P7M3FG2FS4KVES2/view |
| Copiloto Usabilidade | | | https://grid.adminml.com/d/01KX131TPRN818YPAJZKY21DHE/view |
| Async Longtail | | | https://grid.adminml.com/d/01KX12PSQHT8NHA128X1CYN2EN/view |
| CSAT | | | https://grid.adminml.com/d/01KQ3BMS9EGKTB3QHEZXXW4E46/view |
