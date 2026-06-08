#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Chat Assíncrono — Longtail Sellers BR
Equipes: BR_ME_Sellers_Longtail, BR_Publicaciones_Sellers_Longtail, BR_Ventas_Sellers_Longtail
Gera: _async_longtail.html
"""
import sys, json, time
from datetime import date, timedelta, datetime as dt
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
from google.api_core.exceptions import Forbidden

BQ = bigquery.Client(project="meli-bi-data")

LONGTAIL_TEAMS = [
    "BR_ME_Sellers_Longtail",
    "BR_Publicaciones_Sellers_Longtail",
    "BR_Ventas_Sellers_Longtail",
]
MATURE_TEAMS = [
    "BR_ME_Sellers_Mature",
    "BR_Publicaciones_Sellers_Mature",
    "BR_Ventas_Sellers_Mature",
]
ALL_TEAMS = LONGTAIL_TEAMS + MATURE_TEAMS
TEAMS = LONGTAIL_TEAMS  # usado nos gráficos e abas do Geral/Semanal/Mensal
TEAM_SHORT = {
    "BR_ME_Sellers_Longtail":            "ME",
    "BR_Publicaciones_Sellers_Longtail": "Publicaciones",
    "BR_Ventas_Sellers_Longtail":        "Ventas",
    "BR_ME_Sellers_Mature":              "ME-M",
    "BR_Publicaciones_Sellers_Mature":   "Pub-M",
    "BR_Ventas_Sellers_Mature":          "Ventas-M",
}
TEAMS_IN = ", ".join(f'"{t}"' for t in ALL_TEAMS)  # queries incluem Longtail + Mature
COLORS   = ['#3498db','#e74c3c','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e67e22','#34495e','#e91e63','#00bcd4']

SENIORITY_COLORS = {'Expert': '#2ecc71', 'Newbie': '#e74c3c'}
SENIORITY_ORDER  = ['Expert', 'Newbie']
FAIXA_COLORS     = {'M1': '#3498db', 'M2': '#2ecc71', 'M3': '#f39c12', 'M4+': '#9b59b6'}
FAIXA_ORDER      = ['M1', 'M2', 'M3', 'M4+']

_MESES_PT = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
def fmt_mes(k):
    """'2026-01' → 'jan/26'"""
    y, m = k[:4], k[5:7]
    return f"{_MESES_PT[int(m)-1]}/{y[2:]}"

def monthly_keys_jan26():
    """Todos os meses de Fev/2026 até o mês atual, como 'YYYY-MM'."""
    keys, y, m = [], 2026, 2
    while date(y, m, 1) <= today.replace(day=1):
        keys.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12: m, y = 1, y + 1
    return keys

today       = date.today()
dow         = today.weekday()
monday      = today - timedelta(days=dow)
sem_ant_ini = monday - timedelta(days=7)
sem_ant_fin = monday - timedelta(days=1)
sem_act_ini = monday
trend_ini   = monday - timedelta(days=56)
ontem       = today - timedelta(days=1)
mes_jan26   = date(2026, 2, 1)   # período mensal: Fev/2026 → atual

# Se hoje é o dia 1, o mês corrente ainda não tem dados → usar mês anterior
if today.day == 1:
    mes_ini = (today - timedelta(days=1)).replace(day=1)
else:
    mes_ini = today.replace(day=1)

print(f"Datas: sem_ant={sem_ant_ini}–{sem_ant_fin} | mes_ini={mes_ini} | trend={trend_ini} | mensal desde {mes_jan26}")

def run(sql, retries=6, wait=15):
    for attempt in range(retries):
        try:
            return [dict(row) for row in BQ.query(sql).result()]
        except Forbidden as e:
            if 'quotaExceeded' in str(e) and attempt < retries - 1:
                print(f"    quota exceeded, aguardando {wait}s ({attempt+1}/{retries})...")
                time.sleep(wait)
            else:
                raise

print("Rodando queries...")

q1 = run(f"""
SELECT DATE_ID AS dia, USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 15 DAY) AND DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1 DESC, async_por_caso DESC
"""); print(f"  Q1 diário: {len(q1)}")

q2 = run(f"""
SELECT USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE AND DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2 ORDER BY 1, async_por_caso DESC
"""); print(f"  Q2 sem ant: {len(q2)}")

q3 = run(f"""
SELECT USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE AND DATE_ID BETWEEN "{sem_act_ini}" AND "{ontem}"
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2 ORDER BY 1, async_por_caso DESC
"""); print(f"  Q3 sem act: {len(q3)}")

q4 = run(f"""
SELECT USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE AND DATE_ID >= "{mes_ini}" AND DATE_ID < CURRENT_DATE()
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2 ORDER BY 1, async_por_caso DESC
"""); print(f"  Q4 mês: {len(q4)}")

q5 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, staff.USER_TEAM_LEADER_LDAP AS lider, ixc.USER_OFFICE AS escritorio,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
LEFT JOIN (SELECT USER_LDAP, USER_TEAM_LEADER_LDAP FROM `meli-bi-data.WHOWNER.BT_CX_STAFF_HISTORY`
  WHERE DATE_ID = "{sem_ant_fin}" AND USER_TEAM_NAME IN ({TEAMS_IN})) staff
  ON ixc.CI_OWNER_ID = staff.USER_LDAP
WHERE ixc.VALID_IXC_FLAG = TRUE AND ixc.DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CS_MANAGER IS NOT NULL
  AND staff.USER_TEAM_LEADER_LDAP IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1, async_por_caso DESC
"""); print(f"  Q5 líderes: {len(q5)}")

q6 = run(f"""
SELECT main.*, qi.pct_qi, qi.amostras_qi, tmo.tmo_min, prod.produtividade
FROM (
  SELECT equipe, rep, escritorio, lider, async_total, incoming_cr, async_por_caso FROM (
    SELECT ixc.USER_TEAM_NAME AS equipe, ixc.CI_OWNER_ID AS rep, ixc.USER_OFFICE AS escritorio,
      staff.USER_TEAM_LEADER_LDAP AS lider,
      COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
      SUM(ixc.DENOM_IXC) AS incoming_cr,
      ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
    FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
    LEFT JOIN (SELECT USER_LDAP, USER_TEAM_LEADER_LDAP FROM `meli-bi-data.WHOWNER.BT_CX_STAFF_HISTORY`
      WHERE DATE_ID = "{sem_ant_fin}" AND USER_TEAM_NAME IN ({TEAMS_IN})) staff
      ON ixc.CI_OWNER_ID = staff.USER_LDAP
    WHERE ixc.VALID_IXC_FLAG = TRUE AND ixc.DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
      AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CI_OWNER_ID IS NOT NULL AND ixc.CS_MANAGER IS NOT NULL
    GROUP BY 1,2,3,4 HAVING SUM(ixc.DENOM_IXC) >= 10
    QUALIFY ROW_NUMBER() OVER (PARTITION BY ixc.USER_TEAM_NAME ORDER BY
      ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) DESC) <= 20
  )
) main
LEFT JOIN (
  SELECT USER_LDAP,
    ROUND(AVG(QM_GESTION) * 100, 1) AS pct_qi,
    COUNT(*) AS amostras_qi
  FROM `meli-bi-data.WHOWNER.BT_NRT_QI_METRIC_REASONS_SFTP`
  WHERE USER_TEAM_NAME IN ({TEAMS_IN})
    AND REFERENCE_DATE BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
    AND FLAG_NOT_NA AND FLAG_NOT_DUPLICATED AND FLAG_NOT_ELIMINATED AND FLAG_VALID_REASON
  GROUP BY 1
) qi ON main.rep = qi.USER_LDAP
LEFT JOIN (
  SELECT USER_LDAP,
    ROUND(AVG(TMO_SEC) / 60, 1) AS tmo_min
  FROM `meli-bi-data.WHOWNER.DM_CX_TMO`
  WHERE USER_TEAM_NAME IN ({TEAMS_IN})
    AND DATE(ASSIGN_DTTM) BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
    AND NOT FLAG_IS_OUTLIER AND NOT FLAG_DROP
  GROUP BY 1
) tmo ON main.rep = tmo.USER_LDAP
LEFT JOIN (
  SELECT USER_LDAP,
    ROUND(SUM(NUM_QUANTITY) / NULLIF(SUM(DENOM_PRODUCTIVE_STATUS), 0), 2) AS produtividade
  FROM `meli-bi-data.WHOWNER.DM_CX_PRODUCTIVITY_AGENT_HOUR`
  WHERE USER_TEAM_NAME IN ({TEAMS_IN})
    AND DATE(DATETIME_ID) BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  GROUP BY 1
) prod ON main.rep = prod.USER_LDAP
ORDER BY equipe, async_por_caso DESC
"""); print(f"  Q6 reps: {len(q6)}")

q7 = run(f"""
SELECT USER_TEAM_NAME AS equipe, DATE_TRUNC(DATE_ID, WEEK(MONDAY)) AS semana, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE AND DATE_ID >= "{trend_ini}" AND DATE_ID < CURRENT_DATE()
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1, 2 ASC, async_por_caso DESC
"""); print(f"  Q7 semanal: {len(q7)}")

q8 = run(f"""
SELECT USER_TEAM_NAME AS equipe, FORMAT_DATE('%Y-%m', DATE_ID) AS mes, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE AND DATE_ID >= "{mes_jan26}" AND DATE_ID < CURRENT_DATE()
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1, 2 ASC, async_por_caso DESC
"""); print(f"  Q8 mensal: {len(q8)}")

# Q9 — senioridade (Expert/Newbie) × semana
q9 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, DATE_TRUNC(ixc.DATE_ID, WEEK(MONDAY)) AS semana,
  CASE WHEN km.FLAG_EXPERT_STATUS THEN 'Expert' ELSE 'Newbie' END AS senioridade,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
JOIN `meli-bi-data.WHOWNER.BT_CX_KM_TRAINING_STATUS` km
  ON ixc.CI_OWNER_ID = km.USER_LDAP AND ixc.DATE_ID = km.DATE_ID
  AND km.USER_TEAM_NAME IN ({TEAMS_IN})
WHERE ixc.VALID_IXC_FLAG = TRUE AND ixc.DATE_ID >= "{trend_ini}" AND ixc.DATE_ID < CURRENT_DATE()
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CI_OWNER_ID IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1,2,3
"""); print(f"  Q9 sen semanal: {len(q9)}")

# Q10 — faixa M1/M2/M3/M4+ × semana (MIN(DATE_ID) na equipe = data de entrada no time)
q10 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, DATE_TRUNC(ixc.DATE_ID, WEEK(MONDAY)) AS semana,
  CASE
    WHEN staff.fst_day IS NULL OR staff.fst_day < DATE '2026-01-01' THEN 'M4+'
    WHEN DATE_DIFF(DATE_TRUNC(ixc.DATE_ID, MONTH), DATE_TRUNC(staff.fst_day, MONTH), MONTH) <= 1 THEN 'M1'
    WHEN DATE_DIFF(DATE_TRUNC(ixc.DATE_ID, MONTH), DATE_TRUNC(staff.fst_day, MONTH), MONTH) = 2  THEN 'M2'
    WHEN DATE_DIFF(DATE_TRUNC(ixc.DATE_ID, MONTH), DATE_TRUNC(staff.fst_day, MONTH), MONTH) = 3  THEN 'M3'
    ELSE 'M4+'
  END AS faixa,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
LEFT JOIN (
  SELECT USER_LDAP, COALESCE(MIN(FST_DAY_QUEUE_DATE), MIN(DATE_ID)) AS fst_day
  FROM `meli-bi-data.WHOWNER.BT_CX_STAFF_HISTORY`
  WHERE USER_TEAM_NAME IN ({TEAMS_IN})
  GROUP BY 1
) staff ON ixc.CI_OWNER_ID = staff.USER_LDAP
WHERE ixc.VALID_IXC_FLAG = TRUE AND ixc.DATE_ID >= "{trend_ini}" AND ixc.DATE_ID < CURRENT_DATE()
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CI_OWNER_ID IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1,2,3
"""); print(f"  Q10 faixa semanal: {len(q10)}")

# Q11 — senioridade × mês (Jan/2026 em diante)
q11 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, FORMAT_DATE('%Y-%m', ixc.DATE_ID) AS mes,
  CASE WHEN km.FLAG_EXPERT_STATUS THEN 'Expert' ELSE 'Newbie' END AS senioridade,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
JOIN `meli-bi-data.WHOWNER.BT_CX_KM_TRAINING_STATUS` km
  ON ixc.CI_OWNER_ID = km.USER_LDAP AND ixc.DATE_ID = km.DATE_ID
  AND km.USER_TEAM_NAME IN ({TEAMS_IN})
WHERE ixc.VALID_IXC_FLAG = TRUE AND ixc.DATE_ID >= "{mes_jan26}" AND ixc.DATE_ID < CURRENT_DATE()
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CI_OWNER_ID IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1,2,3
"""); print(f"  Q11 sen mensal: {len(q11)}")

# Q12 — faixa × mês (Jan/2026, MIN(DATE_ID) na equipe = data de entrada no time)
q12 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, FORMAT_DATE('%Y-%m', ixc.DATE_ID) AS mes,
  CASE
    WHEN staff.fst_day IS NULL OR staff.fst_day < DATE '2026-01-01' THEN 'M4+'
    WHEN DATE_DIFF(DATE_TRUNC(ixc.DATE_ID, MONTH), DATE_TRUNC(staff.fst_day, MONTH), MONTH) <= 1 THEN 'M1'
    WHEN DATE_DIFF(DATE_TRUNC(ixc.DATE_ID, MONTH), DATE_TRUNC(staff.fst_day, MONTH), MONTH) = 2  THEN 'M2'
    WHEN DATE_DIFF(DATE_TRUNC(ixc.DATE_ID, MONTH), DATE_TRUNC(staff.fst_day, MONTH), MONTH) = 3  THEN 'M3'
    ELSE 'M4+'
  END AS faixa,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
LEFT JOIN (
  SELECT USER_LDAP, COALESCE(MIN(FST_DAY_QUEUE_DATE), MIN(DATE_ID)) AS fst_day
  FROM `meli-bi-data.WHOWNER.BT_CX_STAFF_HISTORY`
  WHERE USER_TEAM_NAME IN ({TEAMS_IN})
  GROUP BY 1
) staff ON ixc.CI_OWNER_ID = staff.USER_LDAP
WHERE ixc.VALID_IXC_FLAG = TRUE AND ixc.DATE_ID >= "{mes_jan26}" AND ixc.DATE_ID < CURRENT_DATE()
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CI_OWNER_ID IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1,2,3
"""); print(f"  Q12 faixa mensal: {len(q12)}")

# Q13 — senioridade × dia (últimos 15 dias)
q13 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, ixc.DATE_ID AS dia,
  CASE WHEN km.FLAG_EXPERT_STATUS THEN 'Expert' ELSE 'Newbie' END AS senioridade,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
JOIN `meli-bi-data.WHOWNER.BT_CX_KM_TRAINING_STATUS` km
  ON ixc.CI_OWNER_ID = km.USER_LDAP AND ixc.DATE_ID = km.DATE_ID
  AND km.USER_TEAM_NAME IN ({TEAMS_IN})
WHERE ixc.VALID_IXC_FLAG = TRUE
  AND ixc.DATE_ID BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 15 DAY) AND DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CI_OWNER_ID IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1,2,3
"""); print(f"  Q13 sen diário: {len(q13)}")

# Q14 — faixa × dia (últimos 15 dias)
q14 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, ixc.DATE_ID AS dia,
  CASE
    WHEN staff.fst_day IS NULL OR staff.fst_day < DATE '2026-01-01' THEN 'M4+'
    WHEN DATE_DIFF(DATE_TRUNC(ixc.DATE_ID, MONTH), DATE_TRUNC(staff.fst_day, MONTH), MONTH) <= 1 THEN 'M1'
    WHEN DATE_DIFF(DATE_TRUNC(ixc.DATE_ID, MONTH), DATE_TRUNC(staff.fst_day, MONTH), MONTH) = 2  THEN 'M2'
    WHEN DATE_DIFF(DATE_TRUNC(ixc.DATE_ID, MONTH), DATE_TRUNC(staff.fst_day, MONTH), MONTH) = 3  THEN 'M3'
    ELSE 'M4+'
  END AS faixa,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
LEFT JOIN (
  SELECT USER_LDAP, COALESCE(MIN(FST_DAY_QUEUE_DATE), MIN(DATE_ID)) AS fst_day
  FROM `meli-bi-data.WHOWNER.BT_CX_STAFF_HISTORY`
  WHERE USER_TEAM_NAME IN ({TEAMS_IN}) GROUP BY 1
) staff ON ixc.CI_OWNER_ID = staff.USER_LDAP
WHERE ixc.VALID_IXC_FLAG = TRUE
  AND ixc.DATE_ID BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 15 DAY) AND DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CI_OWNER_ID IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1,2,3
"""); print(f"  Q14 faixa diário: {len(q14)}")

# ── aggregações para Geral ────────────────────────────────────────────────────

def agg_to_team(rows, date_key):
    buf = {}
    for r in rows:
        k = (r['equipe'], str(r[date_key])[:10] if r.get(date_key) else '')
        buf.setdefault(k, {'equipe': r['equipe'], date_key: k[1], 'async_total': 0, 'incoming_cr': 0})
        buf[k]['async_total'] += int(r.get('async_total') or 0)
        buf[k]['incoming_cr'] += int(r.get('incoming_cr') or 0)
    out = []
    for v in buf.values():
        cr = v['incoming_cr']
        v['async_por_caso'] = round(v['async_total'] / cr, 2) if cr else None
        out.append(v)
    return out

q1_geral  = agg_to_team([r for r in q1  if r['equipe'] in LONGTAIL_TEAMS], 'dia')
q7_geral  = agg_to_team([r for r in q7  if r['equipe'] in LONGTAIL_TEAMS], 'semana')
q8_geral  = agg_to_team([r for r in q8  if r['equipe'] in LONGTAIL_TEAMS], 'mes')

def agg_group_total(rows, date_key, team_list, group_name):
    """Agrega todas as equipes de um grupo em uma única série com nome group_name."""
    buf = {}
    for r in rows:
        if r['equipe'] not in team_list: continue
        k = str(r[date_key])[:10] if r.get(date_key) else ''
        buf.setdefault(k, {'equipe': group_name, date_key: k, 'async_total': 0, 'incoming_cr': 0})
        buf[k]['async_total'] += int(r.get('async_total') or 0)
        buf[k]['incoming_cr'] += int(r.get('incoming_cr') or 0)
    out = []
    for v in buf.values():
        cr = v['incoming_cr']
        v['async_por_caso'] = round(v['async_total'] / cr, 2) if cr else None
        out.append(v)
    return out

# dados de comparação Longtail vs Mature
q7_cmp = (agg_group_total(q7, 'semana', LONGTAIL_TEAMS, 'Longtail') +
          agg_group_total(q7, 'semana', MATURE_TEAMS,   'Mature'))
q8_cmp = (agg_group_total(q8, 'mes', LONGTAIL_TEAMS, 'Longtail') +
          agg_group_total(q8, 'mes', MATURE_TEAMS,   'Mature'))

# ── helpers ───────────────────────────────────────────────────────────────────

def jd(obj):
    if hasattr(obj, 'isoformat'): return obj.isoformat()
    if hasattr(obj, '__float__'):  return float(obj)
    raise TypeError

def _to_float(v, m=1):
    return round(float(v) * m, 2) if v is not None else None

def _dk(r, k):
    v = r.get(k)
    return str(v)[:10] if v is not None else ''

def icon(v):
    if v is None: return "—"
    v = float(v)
    if v < 1.0:  return f'<span class="ok">{v:.2f}</span>'
    if v <= 2.0: return f'<span class="warn">{v:.2f}</span>'
    return           f'<span class="crit">{v:.2f}</span>'

def icon_qi(v):
    """% QI: verde >= 85%, amarelo >= 70%, vermelho < 70%."""
    if v is None: return "<span style='color:#bbb'>—</span>"
    v = float(v)
    if v >= 85:  return f'<span class="ok">{v:.1f}%</span>'
    if v >= 70:  return f'<span class="warn">{v:.1f}%</span>'
    return           f'<span class="crit">{v:.1f}%</span>'

def delta_arrow(prev, curr):
    if prev is None or curr is None: return "—"
    d = float(curr) - float(prev)
    if abs(d) < 0.05: arrow, cls = "→", "neutral"
    elif d > 0:       arrow, cls = "↑", "bad"
    else:             arrow, cls = "↓", "good"
    return f'<span class="{cls}">{arrow} {abs(d):.2f}</span>'

def fmt_date(d):
    if d is None: return "—"
    s = d.strftime('%d/%m') if hasattr(d, 'strftime') else str(d)[:10][5:].replace('-','/')
    return s

def pivot_offices(rows, team):
    return sorted([r for r in rows if r['equipe'] == team], key=lambda x: -(float(x.get('async_por_caso') or 0)))

def get_offices(team):
    seen, result = set(), []
    for rlist in [q1, q2, q3, q4]:
        for r in rlist:
            o = r.get('escritorio')
            if r['equipe'] == team and o and o not in seen:
                seen.add(o); result.append(o)
    return sorted(result)

# ── filtros ───────────────────────────────────────────────────────────────────

def section_office_filter(team):
    s = TEAM_SHORT[team]
    btns = f'<button class="off-btn active" onclick="filterOffice(\'{s}\',\'ALL\',this)">Todos</button>'
    for off in get_offices(team):
        btns += f'<button class="off-btn" onclick="filterOffice(\'{s}\',\'{off}\',this)">{off}</button>'
    return f'<div class="off-filter" id="filter-{s}">{btns}</div>'

def section_team_filter(tab_id):
    btns = f'<button class="off-btn active" onclick="filterTeamSection(\'{tab_id}\',\'ALL\',this)">Todas</button>'
    for t in TEAMS:
        s = TEAM_SHORT[t]
        btns += f'<button class="off-btn" onclick="filterTeamSection(\'{tab_id}\',\'{s}\',this)">{s}</button>'
    return f'<div class="off-filter" id="team-filter-{tab_id}">{btns}</div>'

# ── tabelas ───────────────────────────────────────────────────────────────────

def section_wow(team):
    """Tabela pivotada: últimas 4 semanas completas × office."""
    team_rows = [r for r in q7 if r['equipe'] == team]
    if not team_rows: return "<p class='empty'>Sem dados</p>"
    semanas = sorted(set(str(r['semana'])[:10] for r in team_rows), reverse=True)[:4]
    semanas = list(reversed(semanas))  # crescente: mais antiga → mais recente
    offices = sorted(set(r['escritorio'] for r in team_rows))
    idx = {(str(r['semana'])[:10], r['escritorio']): r for r in team_rows}
    def week_label(s):
        d = date.fromisoformat(s)
        fim = d + timedelta(days=6)
        return f"{d.strftime('%d/%m')}–{fim.strftime('%d/%m')}"
    head = "<tr><th>Escritório</th>" + "".join(f"<th><small>{week_label(s)}</small></th>" for s in semanas) + "</tr>"
    body = ""
    for off in offices:
        body += f'<tr data-office="{off}"><td>{off}</td>'
        for s in semanas:
            r = idx.get((s, off))
            v = r.get('async_por_caso') if r else None
            body += f'<td class="num">{icon(v)}</td>'
        body += "</tr>"
    return f'<table class="dt"><thead>{head}</thead><tbody>{body}</tbody></table>'

def wow_table_all():
    rows_html = ""
    for team in TEAMS:
        def agg_q(q):
            rs = [r for r in q if r['equipe'] == team]
            if not rs: return None, 0
            at = sum(int(r.get('async_total') or 0) for r in rs)
            cr = sum(int(r.get('incoming_cr') or 0) for r in rs)
            return (round(at/cr, 2) if cr else None), cr
        vant, cr_ant = agg_q(q2); vact, cr_act = agg_q(q3)
        s = TEAM_SHORT[team]
        rows_html += f'<tr data-team="{s}"><td><strong>{s}</strong></td><td class="num">{icon(vant)}</td><td class="num-s">{cr_ant:,}</td><td class="num">{icon(vact)}</td><td class="num-s">{cr_act:,}</td><td class="num">{delta_arrow(vant,vact)}</td></tr>'
    return f'<table class="dt"><thead><tr><th>Equipe</th><th>Sem Ant<br><small>{fmt_date(sem_ant_ini)}–{fmt_date(sem_ant_fin)}</small></th><th>CR</th><th>Sem Atual<br><small>{fmt_date(sem_act_ini)}–{fmt_date(ontem)}</small></th><th>CR</th><th>Delta</th></tr></thead><tbody>{rows_html}</tbody></table>'

def section_mes(team):
    """Tabela pivotada: últimos 4 meses × office."""
    team_rows = [r for r in q8 if r['equipe'] == team]
    if not team_rows: return "<p class='empty'>Sem dados</p>"
    meses = sorted(set(str(r['mes']) for r in team_rows), reverse=True)[:4]
    meses = list(reversed(meses))
    offices = sorted(set(r['escritorio'] for r in team_rows))
    idx = {(str(r['mes']), r['escritorio']): r for r in team_rows}
    head = "<tr><th>Escritório</th>" + "".join(f"<th>{fmt_mes(m)}</th>" for m in meses) + "</tr>"
    body = ""
    for off in offices:
        body += f'<tr data-office="{off}"><td>{off}</td>'
        for m in meses:
            r = idx.get((m, off))
            v = r.get('async_por_caso') if r else None
            body += f'<td class="num">{icon(v)}</td>'
        body += "</tr>"
    return f'<table class="dt"><thead>{head}</thead><tbody>{body}</tbody></table>'

def section_lideres(team):
    rows = sorted([r for r in q5 if r['equipe'] == team], key=lambda x: -(float(x.get('async_por_caso') or 0)))
    if not rows: return "<p class='empty'>Sem dados</p>"
    rows_html = "".join(f'<tr data-office="{r["escritorio"]}"><td>{r["lider"] or "—"}</td><td>{r["escritorio"]}</td><td class="num">{icon(r.get("async_por_caso"))}</td><td class="num-s">{int(r.get("incoming_cr") or 0)}</td><td class="num-s">{int(r.get("async_total") or 0)}</td></tr>' for r in rows)
    return f'<table class="dt"><thead><tr><th>Líder</th><th>Escritório</th><th>Async/Caso</th><th>CR</th><th>Async</th></tr></thead><tbody>{rows_html}</tbody></table>'

def section_reps(team):
    rows = sorted([r for r in q6 if r['equipe'] == team], key=lambda x: -(float(x.get('async_por_caso') or 0)))[:20]
    if not rows: return "<p class='empty'>Sem dados (mín. 10 CR)</p>"
    def qi_cell(r):
        n = int(r.get('amostras_qi') or 0)
        tip = f'{n} análise{"s" if n!=1 else ""} feita{"s" if n!=1 else ""}' if n else 'sem análises no período'
        return f'<td class="num"><span class="tip" data-tip="{tip}">{icon_qi(r.get("pct_qi"))}</span></td>'
    def tmo_cell(r):
        v = r.get('tmo_min')
        if v is None: return '<td class="num-s">—</td>'
        v = float(v)
        return f'<td class="num-s">{v:.1f} min</td>'
    def prod_cell(r):
        v = r.get('produtividade')
        if v is None: return '<td class="num-s">—</td>'
        return f'<td class="num-s">{float(v):.2f}/h</td>'
    rows_html = "".join(
        f'<tr data-office="{r["escritorio"]}"><td>{r["rep"]}</td><td>{r["escritorio"]}</td>'
        f'<td>{r["lider"] or "—"}</td>'
        f'<td class="num">{icon(r.get("async_por_caso"))}</td>'
        f'<td class="num-s">{int(r.get("incoming_cr") or 0)}</td>'
        f'<td class="num-s">{int(r.get("async_total") or 0)}</td>'
        f'{tmo_cell(r)}{prod_cell(r)}{qi_cell(r)}</tr>'
        for r in rows)
    return f'<table class="dt"><thead><tr><th>Rep</th><th>Escritório</th><th>Líder</th><th>Async/Caso</th><th>CR</th><th>Async</th><th>TMO</th><th>Produtividade</th><th>% QI</th></tr></thead><tbody>{rows_html}</tbody></table>'

# ── build series ───────────────────────────────────────────────────────────────

def build_office_series(rows, team, date_key, forced_keys=None):
    team_rows = [r for r in rows if r['equipe'] == team]
    if not team_rows and not forced_keys: return [], {}, {}, []
    keys    = forced_keys if forced_keys else sorted(set(_dk(r, date_key) for r in team_rows))
    offices = sorted(set(r['escritorio'] for r in team_rows))
    if not offices: return keys, {}, {}, [None]*len(keys)
    idx     = {(_dk(r, date_key), r['escritorio']): r for r in team_rows}
    series_map = {off: [idx.get((k, off), {}).get('async_por_caso') for k in keys] for off in offices}
    color_map  = {off: COLORS[i % len(COLORS)] for i, off in enumerate(offices)}
    total = []
    for k in keys:
        rows_k = [r for r in team_rows if _dk(r, date_key) == k]
        at = sum(int(r.get('async_total') or 0) for r in rows_k)
        cr = sum(int(r.get('incoming_cr') or 0) for r in rows_k)
        total.append(round(at/cr, 2) if cr else None)
    return keys, series_map, color_map, total

def build_team_series(rows, date_key, forced_keys=None):
    if not rows and not forced_keys: return [], {}, {}, []
    auto_keys = sorted(set(str(r[date_key])[:10] for r in rows)) if rows else []
    keys = forced_keys if forced_keys else auto_keys
    idx = {}
    for r in rows:
        k = str(r[date_key])[:10]
        idx.setdefault((k, r['equipe']), {'at': 0, 'cr': 0})
        idx[(k, r['equipe'])]['at'] += int(r.get('async_total') or 0)
        idx[(k, r['equipe'])]['cr'] += int(r.get('incoming_cr') or 0)
    def val(k, t):
        d = idx.get((k, t)); return round(d['at']/d['cr'], 2) if d and d['cr'] else None
    series = {TEAM_SHORT[t]: [val(k, t) for k in keys] for t in TEAMS}
    colors = {TEAM_SHORT[t]: COLORS[i] for i, t in enumerate(TEAMS)}
    total_buf = {}
    for r in rows:
        k = str(r[date_key])[:10]
        total_buf.setdefault(k, {'at': 0, 'cr': 0})
        total_buf[k]['at'] += int(r.get('async_total') or 0)
        total_buf[k]['cr'] += int(r.get('incoming_cr') or 0)
    total = [round(total_buf[k]['at']/total_buf[k]['cr'], 2) if total_buf.get(k, {}).get('cr') else None for k in keys]
    return keys, series, colors, total

def build_category_series(rows, team, date_key, cat_key, categories, forced_keys=None):
    team_rows = [r for r in rows if r.get('equipe') == team] if team else list(rows)
    if not team_rows and not forced_keys: return [], {}, {}, []
    keys = forced_keys if forced_keys else sorted(set(_dk(r, date_key) for r in team_rows))
    idx = {}
    for r in team_rows:
        k = _dk(r, date_key); c = str(r.get(cat_key, ''))
        if c: idx[(k, c)] = r
    series_map = {c: [idx.get((k, c), {}).get('async_por_caso') for k in keys] for c in categories}
    total = []
    for k in keys:
        rows_k = [r for r in team_rows if _dk(r, date_key) == k]
        at = sum(int(r.get('async_total') or 0) for r in rows_k)
        cr = sum(int(r.get('incoming_cr') or 0) for r in rows_k)
        total.append(round(at/cr, 2) if cr else None)
    return keys, series_map, {}, total

# ── dataset builders ───────────────────────────────────────────────────────────

def bar_datasets(series_map, color_map, multiplier=1, total=None):
    n = max((len(v) for v in series_map.values()), default=0)
    ds = []
    for label, values in series_map.items():
        c = color_map.get(label, '#999999')
        ds.append({'type':'bar','label':label,'data':[_to_float(v,multiplier) for v in values],
                   'backgroundColor':c+'bb','borderColor':c,'borderWidth':1,'borderRadius':3,'skipNull':True})
    if total:
        ds.append({'type':'line','label':'Total','data':[_to_float(v,multiplier) for v in total],
                   'borderColor':'#1a1a2e','backgroundColor':'#1a1a2e22','borderWidth':2.5,
                   'pointRadius':3,'tension':0.3,'fill':False,'spanGaps':True,'order':0})
    ref1 = 1.0*multiplier; ref2 = 2.0*multiplier
    ds.append({'type':'line','label':'__ref1__','data':[ref1]*n,'borderColor':'#b8860b','borderDash':[6,4],'pointRadius':0,'borderWidth':1.5,'fill':False,'tension':0})
    ds.append({'type':'line','label':'__ref2__','data':[ref2]*n,'borderColor':'#c0392b','borderDash':[6,4],'pointRadius':0,'borderWidth':1.5,'fill':False,'tension':0})
    return ds

def line_datasets(series_map, color_map, multiplier=1, total=None):
    ds = []
    for label, values in series_map.items():
        c = color_map.get(label, '#999999')
        ds.append({'type':'line','label':label,'data':[_to_float(v,multiplier) for v in values],
                   'borderColor':c,'backgroundColor':c+'33','borderWidth':2,
                   'tension':0.35,'spanGaps':True,'pointRadius':4,'fill':False})
    if total:
        ds.insert(0, {'type':'line','label':'Total','data':[_to_float(v,multiplier) for v in total],
                      'borderColor':'#1a1a2e','backgroundColor':'#1a1a2e22','borderWidth':3,
                      'pointRadius':4,'tension':0.3,'fill':False,'spanGaps':True})
    return ds

# ── make chart ─────────────────────────────────────────────────────────────────

def make_chart(cid, labels, datasets, y_label, bar=True, height=280, x_rotation=0):
    data_json  = json.dumps({'labels': labels, 'datasets': datasets}, default=jd)
    chart_type = 'bar' if bar else 'line'
    rotation   = f'maxRotation:{x_rotation},' if x_rotation else ''
    return f"""<div style="position:relative;height:{height}px"><canvas id="{cid}"></canvas></div>
<script>(function(){{
  var ctx=document.getElementById('{cid}').getContext('2d');
  window._charts=window._charts||{{}};
  window._charts['{cid}']=new Chart(ctx,{{
    type:'{chart_type}',data:{data_json},
    options:{{responsive:true,maintainAspectRatio:false,interaction:{{mode:'index',intersect:false}},
      plugins:{{
        legend:{{position:'top',labels:{{filter:function(i){{return !i.text.startsWith('__');}},boxWidth:12,font:{{size:11}}}}}},
        tooltip:{{filter:function(i){{return !i.dataset.label.startsWith('__');}}}}
      }},
      scales:{{
        y:{{title:{{display:true,text:'{y_label}',font:{{size:11}}}},min:0,ticks:{{font:{{size:11}}}}}},
        x:{{ticks:{{{rotation}font:{{size:10}}}}}}
      }}
    }}
  }});
}})();</script>"""

# ── gráficos por office (abas ME/Pub/Ventas) ──────────────────────────────────

def chart_daily(team, pfx=''):
    keys, series, cmap, total = build_office_series(q1, team, 'dia')
    if not keys: return "<p class='empty'>Sem dados</p>"
    cid = f'cd-{pfx}-{TEAM_SHORT[team]}' if pfx else f'cd-{TEAM_SHORT[team]}'
    return make_chart(cid, [k[5:].replace('-','/') for k in keys], bar_datasets(series, cmap, total=total), 'async/caso', bar=True, x_rotation=45)

def chart_weekly(team, pfx=''):
    keys, series, cmap, total = build_office_series(q7, team, 'semana')
    if not keys: return "<p class='empty'>Sem dados</p>"
    cid = f'cw-{pfx}-{TEAM_SHORT[team]}' if pfx else f'cw-{TEAM_SHORT[team]}'
    return make_chart(cid, [k[5:].replace('-','/') for k in keys], bar_datasets(series, cmap, total=total), 'async/caso', bar=True)

def chart_monthly(team, pfx=''):
    fk = monthly_keys_jan26()
    keys, series, cmap, total = build_office_series(q8, team, 'mes', forced_keys=fk)
    if not series: return "<p class='empty'>Sem dados</p>"
    cid = f'cm-{pfx}-{TEAM_SHORT[team]}' if pfx else f'cm-{TEAM_SHORT[team]}'
    return make_chart(cid, [fmt_mes(k) for k in keys], bar_datasets(series, cmap, total=total), 'async/caso', bar=True)

def chart_pct_weekly(team, pfx=''):
    keys, series, cmap, total = build_office_series(q7, team, 'semana')
    if not keys: return "<p class='empty'>Sem dados</p>"
    cid = f'cpw-{pfx}-{TEAM_SHORT[team]}' if pfx else f'cpw-{TEAM_SHORT[team]}'
    return make_chart(cid, [k[5:].replace('-','/') for k in keys], line_datasets(series, cmap, multiplier=100, total=total), '% async/CR', bar=False)

def chart_pct_monthly(team, pfx=''):
    fk = monthly_keys_jan26()
    keys, series, cmap, total = build_office_series(q8, team, 'mes', forced_keys=fk)
    if not series: return "<p class='empty'>Sem dados</p>"
    cid = f'cpm-{pfx}-{TEAM_SHORT[team]}' if pfx else f'cpm-{TEAM_SHORT[team]}'
    return make_chart(cid, [fmt_mes(k) for k in keys], line_datasets(series, cmap, multiplier=100, total=total), '% async/CR', bar=False)

# ── gráficos Geral (série = equipe) ──────────────────────────────────────────

def _geral_chart(q, date_key, cid, label_fn, y_label, pct=False, bar=True, x_rot=0, forced_keys=None):
    keys, series, cmap, total = build_team_series(q, date_key, forced_keys=forced_keys)
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [label_fn(k) for k in keys]
    if pct:
        ds = line_datasets(series, cmap, multiplier=100, total=total)
    elif bar:
        ds = bar_datasets(series, cmap, total=total)
    else:
        ds = line_datasets(series, cmap, total=total)
    return make_chart(cid, labels, ds, y_label, bar=bar, x_rotation=x_rot)

def chart_geral_daily():    return _geral_chart(q1_geral, 'dia',    'cg-daily',   lambda k: k[5:].replace('-','/'), 'async/caso', bar=True, x_rot=45)
def chart_geral_weekly():   return _geral_chart(q7_geral, 'semana', 'cg-weekly',  lambda k: k[5:].replace('-','/'), 'async/caso', bar=True)
def chart_geral_monthly():  return _geral_chart(q8_geral, 'mes',    'cg-monthly', fmt_mes, 'async/caso', bar=True,  forced_keys=monthly_keys_jan26())
def chart_geral_pct_wkly(): return _geral_chart(q7_geral, 'semana', 'cg-cpw',    lambda k: k[5:].replace('-','/'), '% async/CR', pct=True, bar=False)

# ── visão geral 4 charts (tabs Semanal / Mensal) ──────────────────────────────

def _chart_total(q_geral, date_key, cid, label_fn, forced_keys=None):
    """Barras: total consolidado (soma de todas as equipes)."""
    keys, _, _, total = build_team_series(q_geral, date_key, forced_keys=forced_keys)
    if not keys: return "<p class='empty'>Sem dados</p>"
    ds = bar_datasets({'Total': total}, {'Total': '#3498db'})
    return make_chart(cid, [label_fn(k) for k in keys], ds, 'async/caso', bar=True)

def _chart_equipes(q_geral, date_key, cid, label_fn, forced_keys=None):
    """Linhas: uma linha por equipe."""
    return _geral_chart(q_geral, date_key, cid, label_fn, 'async/caso', bar=False, forced_keys=forced_keys)

def _chart_sen_geral(q_sen, date_key, cid, label_fn, forced_keys=None):
    """Linhas: Expert vs Newbie — todas as equipes combinadas."""
    keys, series, _, total = build_category_series(q_sen, None, date_key, 'senioridade', SENIORITY_ORDER, forced_keys=forced_keys)
    if not series: return "<p class='empty'>Sem dados</p>"
    return make_chart(cid, [label_fn(k) for k in keys], line_datasets(series, SENIORITY_COLORS, total=total), 'async/caso', bar=False)

def _chart_faixa_geral(q_faixa, date_key, cid, label_fn, forced_keys=None):
    """Linhas: M1/M2/M3/M4+ — todas as equipes combinadas."""
    keys, series, _, total = build_category_series(q_faixa, None, date_key, 'faixa', FAIXA_ORDER, forced_keys=forced_keys)
    if not series: return "<p class='empty'>Sem dados</p>"
    return make_chart(cid, [label_fn(k) for k in keys], line_datasets(series, FAIXA_COLORS, total=total), 'async/caso', bar=False)

def visao_geral_semanal():
    lbl = lambda k: k[5:].replace('-','/')
    return f"""
    <div class="section-title">Visão Geral <small style="font-weight:400;font-size:11px">(últimas 8 semanas — todas as equipes)</small></div>
    <div style="display:flex;gap:16px">
      <div class="card" style="flex:1;min-width:0"><h3>Evolução Geral</h3>{_chart_total(q7_geral,'semana','vs-total',lbl)}</div>
      <div class="card" style="flex:1;min-width:0"><h3>Evolução por Equipe</h3>{_chart_equipes(q7_geral,'semana','vs-equipe',lbl)}</div>
    </div>
    <div style="display:flex;gap:16px">
      <div class="card" style="flex:1;min-width:0"><h3>Evolução por Senioridade</h3>{_chart_sen_geral(q9,'semana','vs-sen',lbl)}</div>
      <div class="card" style="flex:1;min-width:0"><h3>Evolução por Período (M1–M4+)</h3>{_chart_faixa_geral(q10,'semana','vs-faixa',lbl)}</div>
    </div>"""

def visao_geral_mensal():
    fk  = monthly_keys_jan26()
    lbl = fmt_mes
    return f"""
    <div class="section-title">Visão Geral <small style="font-weight:400;font-size:11px">(fev/26 → hoje — todas as equipes)</small></div>
    <div style="display:flex;gap:16px">
      <div class="card" style="flex:1;min-width:0"><h3>Evolução Geral</h3>{_chart_total(q8_geral,'mes','vm-total',lbl,fk)}</div>
      <div class="card" style="flex:1;min-width:0"><h3>Evolução por Equipe</h3>{_chart_equipes(q8_geral,'mes','vm-equipe',lbl,fk)}</div>
    </div>
    <div style="display:flex;gap:16px">
      <div class="card" style="flex:1;min-width:0"><h3>Evolução por Senioridade</h3>{_chart_sen_geral(q11,'mes','vm-sen',lbl,fk)}</div>
      <div class="card" style="flex:1;min-width:0"><h3>Evolução por Período (M1–M4+)</h3>{_chart_faixa_geral(q12,'mes','vm-faixa',lbl,fk)}</div>
    </div>"""

def visao_geral_diaria():
    lbl = lambda k: k[5:].replace('-','/')
    q13_g = agg_to_team(q13, 'dia')
    q14_g = agg_to_team(q14, 'dia')
    return f"""
    <div class="section-title">Visão Geral <small style="font-weight:400;font-size:11px">(últimos 15 dias — todas as equipes)</small></div>
    <div style="display:flex;gap:16px">
      <div class="card" style="flex:1;min-width:0"><h3>Evolução Geral</h3>{_chart_total(q1_geral,'dia','vd-total',lbl)}</div>
      <div class="card" style="flex:1;min-width:0"><h3>Evolução por Equipe</h3>{_chart_equipes(q1_geral,'dia','vd-equipe',lbl)}</div>
    </div>
    <div style="display:flex;gap:16px">
      <div class="card" style="flex:1;min-width:0"><h3>Evolução por Senioridade</h3>{_chart_sen_geral(q13,'dia','vd-sen',lbl)}</div>
      <div class="card" style="flex:1;min-width:0"><h3>Evolução por Período (M1–M4+)</h3>{_chart_faixa_geral(q14,'dia','vd-faixa',lbl)}</div>
    </div>"""
def chart_geral_pct_mth():  return _geral_chart(q8_geral, 'mes',    'cg-cpm',    fmt_mes, '% async/CR', pct=True, bar=False, forced_keys=monthly_keys_jan26())

# ── gráficos comparação Longtail vs Mature ────────────────────────────────────

CMP_COLORS = {'Longtail': '#3498db', 'Mature': '#e74c3c'}

def _chart_cmp(rows, date_key, cid, label_fn, forced_keys=None):
    """Linha Longtail vs Mature."""
    if not rows: return "<p class='empty'>Sem dados</p>"
    keys = forced_keys if forced_keys else sorted(set(str(r[date_key])[:10] if r.get(date_key) else r.get(date_key,'') for r in rows))
    idx  = {(str(r[date_key])[:10] if r.get(date_key) else r.get(date_key,''), r['equipe']): r.get('async_por_caso') for r in rows}
    series = {g: [idx.get((k, g)) for k in keys] for g in ['Longtail','Mature']}
    return make_chart(cid, [label_fn(k) for k in keys], line_datasets(series, CMP_COLORS), 'async/caso', bar=False)

def chart_cmp_weekly():  return _chart_cmp(q7_cmp, 'semana', 'cmp-wkly', lambda k: k[5:].replace('-','/'))
def chart_cmp_monthly(): return _chart_cmp(q8_cmp, 'mes',    'cmp-mth',  fmt_mes, forced_keys=monthly_keys_jan26())

# ── gráficos de senioridade/faixa ─────────────────────────────────────────────

def chart_sen_semanal(team, pfx='s'):
    keys, series, _, total = build_category_series(q9,  team, 'semana', 'senioridade', SENIORITY_ORDER)
    if not keys: return "<p class='empty'>Sem dados</p>"
    return make_chart(f'csen-{pfx}-{TEAM_SHORT[team]}', [k[5:].replace('-','/') for k in keys], line_datasets(series, SENIORITY_COLORS, total=total), 'async/caso', bar=False)

def chart_faixa_semanal(team, pfx='s'):
    keys, series, _, total = build_category_series(q10, team, 'semana', 'faixa',       FAIXA_ORDER)
    if not keys: return "<p class='empty'>Sem dados</p>"
    return make_chart(f'cfx-{pfx}-{TEAM_SHORT[team]}',  [k[5:].replace('-','/') for k in keys], line_datasets(series, FAIXA_COLORS,     total=total), 'async/caso', bar=False)

def chart_sen_mensal(team, pfx='m'):
    fk = monthly_keys_jan26()
    keys, series, _, total = build_category_series(q11, team, 'mes', 'senioridade', SENIORITY_ORDER, forced_keys=fk)
    if not series: return "<p class='empty'>Sem dados</p>"
    return make_chart(f'csen-{pfx}-{TEAM_SHORT[team]}', [fmt_mes(k) for k in keys], line_datasets(series, SENIORITY_COLORS, total=total), 'async/caso', bar=False)

def chart_faixa_mensal(team, pfx='m'):
    fk = monthly_keys_jan26()
    keys, series, _, total = build_category_series(q12, team, 'mes', 'faixa', FAIXA_ORDER, forced_keys=fk)
    if not series: return "<p class='empty'>Sem dados</p>"
    return make_chart(f'cfx-{pfx}-{TEAM_SHORT[team]}',  [fmt_mes(k) for k in keys], line_datasets(series, FAIXA_COLORS, total=total), 'async/caso', bar=False)

def chart_sen_diario(team, pfx='d'):
    keys, series, _, total = build_category_series(q13, team, 'dia', 'senioridade', SENIORITY_ORDER)
    if not keys: return "<p class='empty'>Sem dados</p>"
    return make_chart(f'csen-{pfx}-{TEAM_SHORT[team]}', [k[5:].replace('-','/') for k in keys], line_datasets(series, SENIORITY_COLORS, total=total), 'async/caso', bar=False, x_rotation=45)

def chart_faixa_diario(team, pfx='d'):
    keys, series, _, total = build_category_series(q14, team, 'dia', 'faixa', FAIXA_ORDER)
    if not keys: return "<p class='empty'>Sem dados</p>"
    return make_chart(f'cfx-{pfx}-{TEAM_SHORT[team]}',  [k[5:].replace('-','/') for k in keys], line_datasets(series, FAIXA_COLORS, total=total), 'async/caso', bar=False, x_rotation=45)

# ── seniority block reutilizável ──────────────────────────────────────────────

def seniority_block(team, period, pfx):
    s = TEAM_SHORT[team]
    if period == 'semanal':
        c_sen   = chart_sen_semanal(team, pfx)
        c_faixa = chart_faixa_semanal(team, pfx)
    else:
        c_sen   = chart_sen_mensal(team, pfx)
        c_faixa = chart_faixa_mensal(team, pfx)
    return f"""
    <div class="team-section" data-team="{s}">
      <div class="section-title">{s}</div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0">
          <h3>Senioridade — Expert vs Newbie</h3>{c_sen}
        </div>
        <div class="card" style="flex:1;min-width:0">
          <h3>Tempo de Operação — M1 / M2 / M3 / M4+</h3>{c_faixa}
        </div>
      </div>
    </div>"""

# ── resumo executivo ──────────────────────────────────────────────────────────

def exec_summary(team):
    ant = {r['escritorio']: r for r in q2 if r['equipe'] == team}
    act = {r['escritorio']: r for r in q3 if r['equipe'] == team}
    worst = (pivot_offices(q2, team) or [None])[0]
    b1 = (f"Office com maior async/caso (sem ant): <strong>{worst['escritorio']}</strong> — {icon(worst.get('async_por_caso'))}" if worst else "Sem dados")
    if worst:
        off = worst['escritorio']
        vant, vact = ant.get(off,{}).get('async_por_caso'), act.get(off,{}).get('async_por_caso')
        d = (float(vact)-float(vant)) if (vact is not None and vant is not None) else None
        b2 = (f"Delta WoW {off}: {icon(vant)} → {icon(vact)} ({'+' if d>=0 else ''}{d:.2f})" if d is not None else f"Delta WoW {off}: sem dados da semana atual")
    else:
        b2 = "Sem dados WoW"
    n_crit = len([r for r in q6 if r['equipe'] == team and float(r.get('async_por_caso') or 0) > 2.0])
    b3 = f"Reps com async/caso &gt; 2.0 (sem ant): <strong>{n_crit}</strong> rep{'s' if n_crit!=1 else ''}"
    return f'<ul class="exec"><li>{b1}</li><li>{b2}</li><li>{b3}</li></ul>'

# ── abas ───────────────────────────────────────────────────────────────────────

def tab_content(team):
    s = TEAM_SHORT[team]
    return f"""
    <div id="tab-{s}" class="tab-content">
      <h2>{team}</h2>
      {section_office_filter(team)}

      <div class="subtabs">
        <button class="stab-btn active" onclick="showSubTab('{s}','Geral',this)">Geral</button>
        <button class="stab-btn" onclick="showSubTab('{s}','Diario',this)">Diário</button>
        <button class="stab-btn" onclick="showSubTab('{s}','Semanal',this)">Semanal</button>
        <button class="stab-btn" onclick="showSubTab('{s}','Mensal',this)">Mensal</button>
      </div>

      <div id="stab-{s}-Geral" class="stab-content show">
        <div class="card"><h3>Resumo Executivo</h3>{exec_summary(team)}</div>
        <div style="display:flex;gap:16px">
          <div class="card" style="flex:1;min-width:0"><h3>Últimas 4 Semanas por Office</h3>{section_wow(team)}</div>
          <div class="card" style="flex:1;min-width:0"><h3>Últimos 4 Meses por Office</h3>{section_mes(team)}</div>
        </div>
        <div class="card"><h3>Por Team Leader <small>(sem {fmt_date(sem_ant_ini)}–{fmt_date(sem_ant_fin)})</small></h3>{section_lideres(team)}</div>
        <div class="card"><h3>Top 20 Reps — maior async/caso <small>(mín. 10 CR)</small></h3>{section_reps(team)}</div>
      </div>

      <div id="stab-{s}-Diario" class="stab-content">
        <div class="card"><h3>Async/Caso por Office <small>últimos 15 dias</small></h3>{chart_daily(team,'t')}</div>
        <div style="display:flex;gap:16px">
          <div class="card" style="flex:1;min-width:0"><h3>Senioridade — Expert vs Newbie</h3>{chart_sen_diario(team,'td')}</div>
          <div class="card" style="flex:1;min-width:0"><h3>Tempo de Operação — M1/M2/M3/M4+</h3>{chart_faixa_diario(team,'td')}</div>
        </div>
      </div>

      <div id="stab-{s}-Semanal" class="stab-content">
        <div class="card"><h3>Async/Caso por Office <small>8 semanas</small></h3>{chart_weekly(team,'t')}</div>
        <div style="display:flex;gap:16px">
          <div class="card" style="flex:1;min-width:0"><h3>Senioridade — Expert vs Newbie</h3>{chart_sen_semanal(team,'ts')}</div>
          <div class="card" style="flex:1;min-width:0"><h3>Tempo de Operação — M1/M2/M3/M4+</h3>{chart_faixa_semanal(team,'ts')}</div>
        </div>
      </div>

      <div id="stab-{s}-Mensal" class="stab-content">
        <div class="card"><h3>Async/Caso por Office <small>fev/26–hoje</small></h3>{chart_monthly(team,'t')}</div>
        <div style="display:flex;gap:16px">
          <div class="card" style="flex:1;min-width:0"><h3>Senioridade — Expert vs Newbie</h3>{chart_sen_mensal(team,'tm')}</div>
          <div class="card" style="flex:1;min-width:0"><h3>Tempo de Operação — M1/M2/M3/M4+</h3>{chart_faixa_mensal(team,'tm')}</div>
        </div>
      </div>
    </div>"""

def tab_geral():
    return f"""
    <div id="tab-Geral" class="tab-content">
      <h2>Geral — Longtail Sellers BR</h2>
      <div class="card"><h3>WoW por Equipe</h3>{wow_table_all()}</div>
      <div class="section-title">Async/Caso por Equipe — Longtail</div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Diário</h3>{chart_geral_daily()}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Semanal</h3>{chart_geral_weekly()}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Mensal</h3>{chart_geral_monthly()}</div>
      </div>
      <div class="section-title">% de Uso Assíncrono — Longtail</div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Mensal</h3>{chart_geral_pct_mth()}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Semanal</h3>{chart_geral_pct_wkly()}</div>
      </div>
      <div class="section-title">Comparação Longtail vs Mature <small style="font-weight:400;font-size:11px;text-transform:none">— async/caso agregado por grupo</small></div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Mensal</h3>{chart_cmp_monthly()}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Semanal</h3>{chart_cmp_weekly()}</div>
      </div>
    </div>"""

def _team_block_semanal(team):
    s = TEAM_SHORT[team]
    return f"""
    <div class="team-section" data-team="{s}">
      <div class="section-title">{s}</div>
      <div class="card"><h3>Async/Caso por Office</h3>{chart_weekly(team)}</div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Senioridade — Expert vs Newbie</h3>{chart_sen_semanal(team,'sw')}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Tempo de Operação — M1/M2/M3/M4+</h3>{chart_faixa_semanal(team,'sw')}</div>
      </div>
    </div>"""

def _team_block_mensal(team):
    s = TEAM_SHORT[team]
    return f"""
    <div class="team-section" data-team="{s}">
      <div class="section-title">{s}</div>
      <div class="card"><h3>Async/Caso por Office</h3>{chart_monthly(team)}</div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Senioridade — Expert vs Newbie</h3>{chart_sen_mensal(team,'mw')}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Tempo de Operação — M1/M2/M3/M4+</h3>{chart_faixa_mensal(team,'mw')}</div>
      </div>
    </div>"""

def _team_block_diario(team):
    s = TEAM_SHORT[team]
    return f"""
    <div class="team-section" data-team="{s}">
      <div class="section-title">{s}</div>
      <div class="card"><h3>Async/Caso por Office</h3>{chart_daily(team)}</div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Senioridade — Expert vs Newbie</h3>{chart_sen_diario(team,'dw')}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Tempo de Operação — M1/M2/M3/M4+</h3>{chart_faixa_diario(team,'dw')}</div>
      </div>
    </div>"""

def tab_diario():
    team_blocks = "".join(_team_block_diario(t) for t in TEAMS)
    return f"""
    <div id="tab-Diario" class="tab-content">
      <h2>Visão Diária — Longtail Sellers BR <small style="font-weight:400;font-size:12px">(últimos 15 dias)</small></h2>
      {visao_geral_diaria()}
      <div class="section-title">Abertura por Equipe <small style="font-weight:400;font-size:11px">— use o filtro abaixo para isolar uma equipe</small></div>
      {section_team_filter('Diario')}
      {team_blocks}
    </div>"""

def tab_semanal():
    team_blocks = "".join(_team_block_semanal(t) for t in TEAMS)
    return f"""
    <div id="tab-Semanal" class="tab-content">
      <h2>Visão Semanal — Longtail Sellers BR <small style="font-weight:400;font-size:12px">(últimas 8 semanas)</small></h2>
      {visao_geral_semanal()}
      <div class="section-title">Abertura por Equipe <small style="font-weight:400;font-size:11px">— use o filtro abaixo para isolar uma equipe</small></div>
      {section_team_filter('Semanal')}
      {team_blocks}
    </div>"""

def tab_mensal():
    team_blocks = "".join(_team_block_mensal(t) for t in TEAMS)
    return f"""
    <div id="tab-Mensal" class="tab-content">
      <h2>Visão Mensal — Longtail Sellers BR <small style="font-weight:400;font-size:12px">(fev/26 → {today.strftime('%b/%Y')})</small></h2>
      {visao_geral_mensal()}
      <div class="section-title">Abertura por Equipe <small style="font-weight:400;font-size:11px">— use o filtro abaixo para isolar uma equipe</small></div>
      {section_team_filter('Mensal')}
      {team_blocks}
    </div>"""

# ── HTML ───────────────────────────────────────────────────────────────────────

tabs_nav  = '<button class="tab-btn active" onclick="showTab(\'Geral\')">Geral</button>'
tabs_nav += '<button class="tab-btn" onclick="showTab(\'Diario\')">Diário</button>'
tabs_nav += '<button class="tab-btn" onclick="showTab(\'Semanal\')">Semanal</button>'
tabs_nav += '<button class="tab-btn" onclick="showTab(\'Mensal\')">Mensal</button>'
tabs_body = tab_geral() + tab_diario() + tab_semanal() + tab_mensal()
for team in TEAMS:
    s = TEAM_SHORT[team]
    tabs_nav  += f'<button class="tab-btn" onclick="showTab(\'{s}\')">{s}</button>'
    tabs_body += tab_content(team)
# abas Mature
tabs_nav += '<span style="border-left:2px solid #dde3ea;margin:4px 4px 0;height:28px;display:inline-block;vertical-align:bottom"></span>'
for team in MATURE_TEAMS:
    s = TEAM_SHORT[team]
    tabs_nav  += f'<button class="tab-btn" onclick="showTab(\'{s}\')">{s}</button>'
    tabs_body += tab_content(team)

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chat Assíncrono — Longtail Sellers BR</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
<script>
Chart.register({{
  id:'datalabels',
  afterDatasetsDraw(chart){{
    var ctx=chart.ctx;
    chart.data.datasets.forEach(function(ds,i){{
      var lbl=ds.label||'';
      if(lbl.startsWith('__'))return;
      var meta=chart.getDatasetMeta(i);
      if(!meta.visible)return;
      meta.data.forEach(function(pt,j){{
        var v=ds.data[j];
        if(v==null||v<=0)return;
        var txt=parseFloat(v).toFixed(2);
        ctx.save();
        ctx.font='bold 9px Segoe UI,sans-serif';
        ctx.fillStyle='#333';
        ctx.textAlign='center';
        ctx.fillText(txt, pt.x, pt.y-6);
        ctx.restore();
      }});
    }});
  }}
}});
</script>
<style>
  :root{{--green:#1a8a3c;--yellow:#b8860b;--red:#c0392b;--bg:#f4f6f8;--card:#fff;--border:#dde3ea;--head:#2c3e50;--accent:#3498db}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',sans-serif;background:var(--bg);color:#222;font-size:13px}}
  header{{background:var(--head);color:#fff;padding:16px 24px}}
  header h1{{font-size:18px}} header .sub{{font-size:11px;opacity:.7;margin-top:4px}}
  .update-badge{{display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.35);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:700;color:#fff;margin-top:8px;letter-spacing:.3px}}
  .update-badge .dot{{width:8px;height:8px;border-radius:50%;background:#2ecc71;box-shadow:0 0 6px #2ecc71;flex-shrink:0}}
  .legend{{display:flex;gap:16px;padding:8px 24px;background:#fff;border-bottom:1px solid var(--border);font-size:11px;flex-wrap:wrap}}
  .legend span{{display:flex;align-items:center;gap:4px}}
  .tabs{{display:flex;gap:4px;padding:12px 24px 0;background:#fff;border-bottom:2px solid var(--accent);flex-wrap:wrap}}
  .tab-btn{{padding:8px 18px;border:none;background:#eef2f7;border-radius:6px 6px 0 0;cursor:pointer;font-size:13px;font-weight:600;color:#555;transition:all .15s}}
  .tab-btn.active{{background:var(--accent);color:#fff}}
  .tab-btn:hover:not(.active){{background:#d5e8f7}}
  .tab-content{{display:none;padding:20px 24px}}
  .tab-content.show{{display:block}}
  .tab-content h2{{font-size:15px;color:var(--head);margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border)}}
  .section-title{{font-size:11px;font-weight:700;color:var(--head);text-transform:uppercase;letter-spacing:.5px;margin:8px 0 8px;padding-left:2px}}
  .card{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px;margin-bottom:16px}}
  .card h3{{font-size:13px;font-weight:700;color:var(--head);margin-bottom:12px}}
  .card h3 small{{font-weight:400;color:#777;font-size:11px}}
  .off-filter{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}}
  .off-btn{{padding:5px 14px;border:1.5px solid var(--border);background:#fff;border-radius:20px;cursor:pointer;font-size:11px;font-weight:600;color:#555;transition:all .15s}}
  .off-btn.active{{background:var(--head);color:#fff;border-color:var(--head)}}
  .off-btn:hover:not(.active){{background:#eef2f7;border-color:#aaa}}
  table.dt{{border-collapse:collapse;width:100%;font-size:12px}}
  table.dt th{{background:#f0f4f8;padding:6px 10px;text-align:center;font-size:11px;border-bottom:2px solid var(--border);white-space:nowrap}}
  table.dt th:first-child{{text-align:left}}
  table.dt td{{padding:5px 10px;border-bottom:1px solid #eef0f3;white-space:nowrap;text-align:center}}
  table.dt td:first-child{{text-align:left}}
  table.dt tr:hover td{{background:#f7fafd}}
  td.num{{text-align:center;font-weight:600}} td.num-s{{text-align:center;color:#666}}
  .ok{{color:var(--green)}} .warn{{color:var(--yellow)}} .crit{{color:var(--red);font-weight:700}}
  .good{{color:var(--green)}} .bad{{color:var(--red)}} .neutral{{color:#888}}
  ul.exec{{padding-left:18px}} ul.exec li{{margin-bottom:6px;line-height:1.5}}
  .empty{{color:#999;font-style:italic;padding:8px 0}}
  .tip{{position:relative;cursor:help;border-bottom:1px dotted #999}}
  .tip::after{{content:attr(data-tip);position:absolute;bottom:130%;left:50%;transform:translateX(-50%);background:#2c3e50;color:#fff;padding:5px 10px;border-radius:5px;font-size:11px;font-weight:400;white-space:nowrap;opacity:0;pointer-events:none;transition:opacity .15s;z-index:999}}
  .tip:hover::after{{opacity:1}}
  .team-section{{margin-bottom:8px}}
  .subtabs{{display:flex;gap:6px;margin-bottom:16px;border-bottom:2px solid var(--border);padding-bottom:0}}
  .stab-btn{{padding:6px 18px;border:none;background:transparent;border-radius:6px 6px 0 0;cursor:pointer;font-size:12px;font-weight:600;color:#666;transition:all .15s;border-bottom:2px solid transparent;margin-bottom:-2px}}
  .stab-btn.active{{color:var(--accent);border-bottom-color:var(--accent)}}
  .stab-btn:hover:not(.active){{color:var(--head);background:#f0f4f8}}
  .stab-content{{display:none}}
  .stab-content.show{{display:block}}
  @media(max-width:900px){{div[style*="display:flex"]{{flex-direction:column!important}}}}
</style>
</head>
<body>
<header>
  <h1>Chat Assíncrono — Longtail Sellers BR</h1>
  <div class="update-badge"><span class="dot"></span>Última atualização: {dt.now().strftime('%d/%m/%Y às %H:%M')}</div>
  <div class="sub">Fonte: DM_CX_IXC_DETAIL &nbsp;|&nbsp; async/caso = disparos assíncronos ÷ DENOM_IXC</div>
</header>
<div class="legend">
  <span><span class="ok">●</span> &lt;1.0 Normal</span>
  <span><span class="warn">●</span> 1.0–2.0 Atenção</span>
  <span><span class="crit">●</span> &gt;2.0 Crítico</span>
  <span><span style="color:#2ecc71">●</span> Expert</span>
  <span><span style="color:#e74c3c">●</span> Newbie</span>
  <span><span style="color:#1a1a2e">—</span> Total</span>
  <span style="margin-left:auto;color:#888">↑ piora &nbsp;↓ melhora &nbsp;→ estável</span>
</div>
<div class="tabs">{tabs_nav}</div>
{tabs_body}
<script>
function showTab(id){{
  document.querySelectorAll('.tab-content').forEach(el=>el.classList.remove('show'));
  document.querySelectorAll('.tab-btn').forEach(el=>el.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('show');
  event.target.classList.add('active');
}}
document.querySelector('.tab-content').classList.add('show');

function filterOffice(team,office,btn){{
  document.querySelectorAll('#filter-'+team+' .off-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('#tab-'+team+' tr[data-office]').forEach(row=>{{
    row.style.display=(office==='ALL'||row.dataset.office===office)?'':'none';
  }});
  ['cd-','cd-t-','cw-','cw-t-','cm-','cm-t-','cpw-','cpw-t-','cpm-','cpm-t-'].forEach(p=>{{
    var c=(window._charts||{{}})[p+team];
    if(!c)return;
    c.data.datasets.forEach((ds,i)=>{{
      var r=ds.label.startsWith('__');
      c.setDatasetVisibility(i,r||office==='ALL'||ds.label===office);
    }});
    c.update();
  }});
}}

function showSubTab(team,subtab,btn){{
  document.querySelectorAll('#tab-'+team+' .stab-content').forEach(el=>el.classList.remove('show'));
  document.querySelectorAll('#tab-'+team+' .stab-btn').forEach(el=>el.classList.remove('active'));
  document.getElementById('stab-'+team+'-'+subtab).classList.add('show');
  btn.classList.add('active');
}}
function filterTeamSection(tab,team,btn){{
  document.querySelectorAll('#team-filter-'+tab+' .off-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('#tab-'+tab+' .team-section').forEach(sec=>{{
    sec.style.display=(team==='ALL'||sec.dataset.team===team)?'':'none';
  }});
  // filtrar linhas da tabela WoW
  document.querySelectorAll('#tab-'+tab+' tr[data-team]').forEach(row=>{{
    row.style.display=(team==='ALL'||row.dataset.team===team)?'':'none';
  }});
}}
</script>
</body>
</html>"""

out_raw = r"c:\Users\allabriola\PROJETO CLAUDINHO\_async_longtail.html"
out_pub = r"c:\Users\allabriola\PROJETO CLAUDINHO\async_longtail.html"
for path in [out_raw, out_pub]:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
print(f"HTML salvo: {out_pub}")
