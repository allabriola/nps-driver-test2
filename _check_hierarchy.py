from google.cloud import bigquery
import time
from google.api_core.exceptions import Forbidden

bq = bigquery.Client(project="meli-bi-data")

def run(sql, retries=5, wait=15):
    for attempt in range(retries):
        try:
            return [dict(r) for r in bq.query(sql).result()]
        except Forbidden as e:
            if 'quotaExceeded' in str(e) and attempt < retries-1:
                print(f"quota, aguardando {wait}s..."); time.sleep(wait)
            else: raise

TEAMS_IN = '"BR_ME_Sellers_Longtail","BR_Publicaciones_Sellers_Longtail","BR_Ventas_Sellers_Longtail","BR_ME_Sellers_Mature","BR_Publicaciones_Sellers_Mature","BR_Ventas_Sellers_Mature"'

# TMO por rep (DM_CX_TMO)
print("=== TMO por rep via DM_CX_TMO ===")
rows = run(f"""
SELECT USER_LDAP, USER_TEAM_NAME,
  ROUND(AVG(TMO_SEC) / 60, 1) AS tmo_min,
  COUNT(*) AS n_interacoes
FROM `meli-bi-data.WHOWNER.DM_CX_TMO`
WHERE USER_TEAM_NAME IN ({TEAMS_IN})
  AND DATE(ASSIGN_DTTM) BETWEEN "2026-06-01" AND "2026-06-07"
  AND NOT FLAG_IS_OUTLIER
  AND NOT FLAG_DROP
GROUP BY 1, 2
ORDER BY tmo_min DESC
LIMIT 8
""")
for r in rows: print(r)

# Produtividade por rep
print("\n=== Produtividade por rep via DM_CX_PRODUCTIVITY_AGENT_HOUR ===")
rows2 = run(f"""
SELECT USER_LDAP, USER_TEAM_NAME,
  SUM(NUM_QUANTITY) AS casos_totais,
  ROUND(SUM(DENOM_PRODUCTIVE_STATUS), 2) AS horas_prod,
  ROUND(SUM(NUM_QUANTITY) / NULLIF(SUM(DENOM_PRODUCTIVE_STATUS), 0), 2) AS casos_por_hora
FROM `meli-bi-data.WHOWNER.DM_CX_PRODUCTIVITY_AGENT_HOUR`
WHERE USER_TEAM_NAME IN ({TEAMS_IN})
  AND DATE(DATETIME_ID) BETWEEN "2026-06-01" AND "2026-06-07"
GROUP BY 1, 2
ORDER BY casos_por_hora DESC
LIMIT 8
""")
for r in rows2: print(r)
