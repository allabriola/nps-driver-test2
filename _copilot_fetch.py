#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca dados de CX Copilot do BigQuery para o dashboard de usabilidade.
Gera: _copilot_reps.json, _copilot_by_process.json, _copilot_transcripts_raw.json
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery

client = bigquery.Client(project="meli-bi-data")
DAYS_BACK = 30

def run_query(sql, label=""):
    print(f"  [{label}] rodando...")
    rows = list(client.query(sql).result())
    print(f"  → {len(rows)} linhas")
    return [dict(r) for r in rows]

# ══════════════════════════════════════════════════════════════════════
# Q1: Base de reps — adoção + NPS + TMO + Estilo Meli + metadata
# ══════════════════════════════════════════════════════════════════════
SQL_REPS = f"""
WITH km AS (
  SELECT
    USER_LDAP,
    USER_OFFICE,
    USER_TEAM_CHANNEL,
    USER_TEAM_NAME,
    IF(FLAG_EXPERT_STATUS, 'Expert', 'Newbie') AS senioridade
  FROM `meli-bi-data.WHOWNER.BT_CX_KM_TRAINING_STATUS`
  WHERE DATE_ID = (SELECT MAX(DATE_ID) FROM `meli-bi-data.WHOWNER.BT_CX_KM_TRAINING_STATUS`)
),
reps_ativos AS (
  SELECT USER_LDAP
  FROM `meli-bi-data.WHOWNER.LK_CX_CXCOPILOT_REPS`
  WHERE DATE_ID_TO IS NULL
),
adoption AS (
  SELECT
    USER_LDAP,
    SUM(CASE WHEN FLAG_ON = 1 THEN OUTGOING_TOTAL       ELSE 0 END) AS outgoing_total,
    SUM(CASE WHEN FLAG_ON = 1 THEN COALESCE(OUTGOING_COPILOT, 0) ELSE 0 END) AS outgoing_copilot,
    ROUND(SAFE_DIVIDE(
      SUM(CASE WHEN FLAG_ON = 1 THEN COALESCE(OUTGOING_COPILOT, 0) ELSE 0 END),
      NULLIF(SUM(CASE WHEN FLAG_ON = 1 THEN OUTGOING_TOTAL ELSE 0 END), 0)
    ) * 100, 1) AS pct_adopcion,
    ROUND(AVG(CASE WHEN FLAG_COPILOT = 1 THEN TMO_TOTAL END)) AS tmo_com_copilot,
    ROUND(AVG(CASE WHEN FLAG_COPILOT = 0 THEN TMO_TOTAL END)) AS tmo_sem_copilot,
    COUNT(DISTINCT CASE WHEN FLAG_COPILOT = 1 THEN DATE(GESTION_DT) END) AS dias_uso
  FROM `meli-bi-data.WHOWNER.BT_CX_CXCOPILOT_TMO`
  WHERE FLAG_ON = 1
    AND GESTION_DT >= DATE_SUB(CURRENT_DATE(), INTERVAL {DAYS_BACK} DAY)
  GROUP BY USER_LDAP
),
nps AS (
  SELECT
    USER_LDAP,
    ROUND(AVG(CASE WHEN FLAG_CASE_COPILOT = 1 THEN NPS_VALUE END) * 100, 1) AS nps_copilot,
    COUNT(CASE WHEN FLAG_CASE_COPILOT = 1 THEN 1 END) AS n_nps
  FROM `meli-bi-data.WHOWNER.BT_CX_COPILOT_NPS`
  WHERE NPS_DATE >= DATE_SUB(CURRENT_DATE(), INTERVAL {DAYS_BACK} DAY)
    AND FLAG_HAS_COPILOT_INFO = 1
  GROUP BY USER_LDAP
),
qm AS (
  SELECT
    USER_LDAP,
    ROUND(AVG(QM_TOTAL), 1) AS estilo_meli,
    COUNT(*)                 AS n_qm
  FROM `meli-bi-data.WHOWNER.DM_CX_QM_ANALYSIS_METRIC_REASON`
  WHERE FORM_ANALYSIS_NAME = 'Estilo Meli IA'
    AND ASSIGN_DATE >= DATE_SUB(CURRENT_DATE(), INTERVAL {DAYS_BACK} DAY)
    AND SIT_SITE_ID = 'MLB'
  GROUP BY USER_LDAP
)
SELECT
  ra.USER_LDAP,
  COALESCE(km.USER_OFFICE,        'N/D') AS USER_OFFICE,
  COALESCE(km.USER_TEAM_CHANNEL,  'N/D') AS USER_TEAM_CHANNEL,
  COALESCE(km.USER_TEAM_NAME,     'N/D') AS USER_TEAM_NAME,
  COALESCE(km.senioridade,        'N/D') AS senioridade,
  COALESCE(a.pct_adopcion,         0.0)  AS pct_adopcion,
  COALESCE(a.outgoing_total,          0) AS outgoing_total,
  COALESCE(a.outgoing_copilot,        0) AS outgoing_copilot,
  a.tmo_com_copilot,
  a.tmo_sem_copilot,
  COALESCE(a.dias_uso,                0) AS dias_uso,
  n.nps_copilot,
  COALESCE(n.n_nps,                   0) AS n_nps,
  q.estilo_meli,
  COALESCE(q.n_qm,                    0) AS n_qm
FROM reps_ativos ra
LEFT JOIN km        USING (USER_LDAP)
LEFT JOIN adoption  a USING (USER_LDAP)
LEFT JOIN nps       n USING (USER_LDAP)
LEFT JOIN qm        q USING (USER_LDAP)
WHERE a.USER_LDAP IS NOT NULL
ORDER BY a.pct_adopcion DESC NULLS LAST
"""

# ══════════════════════════════════════════════════════════════════════
# Q2: Adoção por rep × processo
# ══════════════════════════════════════════════════════════════════════
SQL_BY_PROCESS = f"""
SELECT
  T.USER_LDAP,
  COALESCE(P.cx_pr_name_hsp, CAST(T.UNASSIGN_PROCESS_ID AS STRING)) AS processo,
  SUM(CASE WHEN T.FLAG_ON = 1 THEN T.OUTGOING_TOTAL            ELSE 0 END) AS outgoing_total,
  SUM(CASE WHEN T.FLAG_ON = 1 THEN COALESCE(T.OUTGOING_COPILOT, 0) ELSE 0 END) AS outgoing_copilot,
  ROUND(SAFE_DIVIDE(
    SUM(CASE WHEN T.FLAG_ON = 1 THEN COALESCE(T.OUTGOING_COPILOT, 0) ELSE 0 END),
    NULLIF(SUM(CASE WHEN T.FLAG_ON = 1 THEN T.OUTGOING_TOTAL ELSE 0 END), 0)
  ) * 100, 1) AS pct_adopcion
FROM `meli-bi-data.WHOWNER.BT_CX_CXCOPILOT_TMO` T
JOIN `meli-bi-data.WHOWNER.LK_CX_CXCOPILOT_REPS` R
  ON T.USER_LDAP = R.USER_LDAP AND R.DATE_ID_TO IS NULL
LEFT JOIN `meli-bi-data.WHOWNER.LK_CX_PROCESS_ADM` P
  ON P.cx_pr_id = T.UNASSIGN_PROCESS_ID
WHERE T.FLAG_ON = 1
  AND T.GESTION_DT >= DATE_SUB(CURRENT_DATE(), INTERVAL {DAYS_BACK} DAY)
GROUP BY T.USER_LDAP, processo
HAVING outgoing_total >= 5
ORDER BY T.USER_LDAP, pct_adopcion DESC
"""

# ══════════════════════════════════════════════════════════════════════
# Q3: Transcrições rep↔Copilot para categorização
# ══════════════════════════════════════════════════════════════════════
SQL_TRANSCRIPTS = f"""
SELECT
  TR.CONVERSATION_ID,
  SUBSTR(TR.COPILOT_TRANSCRIPT, 1, 3000) AS copilot_transcript,
  COALESCE(P.cx_pr_name_hsp, M.PROCESS_ID) AS processo
FROM `meli-bi-data.WHOWNER.BT_CX_CXCOPILOT_TRANSCRIPT` TR
JOIN `meli-bi-data.WHOWNER.BT_CX_COPILOT_METRICS` M
  ON TR.CONVERSATION_ID = M.CONVERSATION_ID
 AND M.FLAG_FIRST = 1
 AND M.USER_MESSAGE_QTY >= 1
LEFT JOIN `meli-bi-data.WHOWNER.LK_CX_PROCESS_ADM` P
  ON P.cx_pr_id = SAFE_CAST(M.PROCESS_ID AS NUMERIC)
WHERE TR.CONV_CREATED_DATE >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)
  AND TR.COPILOT_ORIGIN = 'MAXWELL'
  AND TR.COPILOT_TRANSCRIPT IS NOT NULL
  AND LENGTH(TR.COPILOT_TRANSCRIPT) > 100
ORDER BY RAND()
LIMIT 800
"""

# ── MAIN ──────────────────────────────────────────────────────────────
print("=== CX Copilot — Fetch BQ ===\n")

print("1. Reps (adoção + NPS + TMO + Estilo Meli)...")
reps = run_query(SQL_REPS, "reps")
with open("_copilot_reps.json", "w", encoding="utf-8") as f:
    json.dump(reps, f, ensure_ascii=False, indent=2, default=str)
print(f"   Salvo: _copilot_reps.json ({len(reps)} reps)\n")

print("2. Adoção por processo...")
by_proc = run_query(SQL_BY_PROCESS, "por processo")
with open("_copilot_by_process.json", "w", encoding="utf-8") as f:
    json.dump(by_proc, f, ensure_ascii=False, indent=2, default=str)
print(f"   Salvo: _copilot_by_process.json ({len(by_proc)} linhas)\n")

print("3. Transcrições para categorização (opcional — requer permissão especial)...")
try:
    transcripts = run_query(SQL_TRANSCRIPTS, "transcrições")
    with open("_copilot_transcripts_raw.json", "w", encoding="utf-8") as f:
        json.dump(transcripts, f, ensure_ascii=False, indent=2, default=str)
    print(f"   Salvo: _copilot_transcripts_raw.json ({len(transcripts)} transcrições)\n")
except Exception as e:
    print(f"   ! Acesso negado à tabela de transcrições — aba Consultas ficará indisponível.")
    print(f"   ! Erro: {str(e)[:120]}\n")

print("=== Fetch concluído! ===")
print("Próximo: python _build_copilot_dashboard.py")
