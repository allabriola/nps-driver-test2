#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca breakdown (Processo, Canal, Oficina, Senioridade) de Maio do BQ
e salva em _mai_breakdown.json para uso como M1 no dashboard de tendências.
"""
import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery

bq = bigquery.Client(project="meli-bi-data")

MAI_START, MAI_END = "2026-05-01", "2026-05-06"

with open("dd_breakdown.json", encoding="utf-8") as f:
    DD = json.load(f)

ALL_DRIVERS = list(DD.keys())

def get_procs(drv):
    procs = set()
    for period_data in DD.get(drv, {}).get("P", {}).values():
        procs.update(period_data.keys())
    return list(procs)

# ── Query genérica por dimensão ──────────────────────────────────────
QUERY_P = """
SELECT PRO_PROCESS_NAME AS dim_key,
  SUM(PROMOTER) AS p, SUM(DETRACTOR) AS d, COUNT(*) AS s
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID='MLB' AND SURVEY_CENTER='BR'
  AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
  AND PRO_PROCESS_NAME IN ({procs})
GROUP BY 1 HAVING COUNT(*) >= 2
"""

QUERY_C = """
SELECT COALESCE(SURVEY_CHANNEL,'(sem canal)') AS dim_key,
  SUM(PROMOTER) AS p, SUM(DETRACTOR) AS d, COUNT(*) AS s
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID='MLB' AND SURVEY_CENTER='BR'
  AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
  AND PRO_PROCESS_NAME IN ({procs})
GROUP BY 1 HAVING COUNT(*) >= 2
"""

QUERY_O = """
SELECT COALESCE(USER_OFFICE,'(sem office)') AS dim_key,
  SUM(PROMOTER) AS p, SUM(DETRACTOR) AS d, COUNT(*) AS s
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID='MLB' AND SURVEY_CENTER='BR'
  AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
  AND PRO_PROCESS_NAME IN ({procs})
GROUP BY 1 HAVING COUNT(*) >= 2
"""

QUERY_SR = """
SELECT COALESCE(ANTIGUEDAD_REP,'(sem senior)') AS dim_key,
  SUM(PROMOTER) AS p, SUM(DETRACTOR) AS d, COUNT(*) AS s
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID='MLB' AND SURVEY_CENTER='BR'
  AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
  AND PRO_PROCESS_NAME IN ({procs})
GROUP BY 1 HAVING COUNT(*) >= 2
"""

def run_query(sql, drv, dim_name):
    procs = get_procs(drv)
    if not procs:
        return {}
    procs_in = "'" + "','".join(p.replace("'", "''") for p in procs[:25]) + "'"
    q = sql.format(start=MAI_START, end=MAI_END, procs=procs_in)
    try:
        rows = list(bq.query(q).result())
        result = {}
        for r in rows:
            p, d, s = int(r.p or 0), int(r.d or 0), int(r.s or 0)
            nps = round(100.0*(p-d)/s, 2) if s > 0 else None
            result[r.dim_key] = {"p": p, "d": d, "s": s, "nps": nps}
        return result
    except Exception as e:
        print(f"    [WARN] {drv} {dim_name}: {e}")
        return {}

result = {}
dim_map = [("P", QUERY_P), ("C", QUERY_C), ("O", QUERY_O), ("Sr", QUERY_SR)]

for drv in ALL_DRIVERS:
    print(f"  {drv[:45]}...", end=" ", flush=True)
    result[drv] = {}
    for dim, sql in dim_map:
        time.sleep(1.5)   # throttle
        result[drv][dim] = {"Mai": run_query(sql, drv, dim)}
    total = sum(v["s"] for v in result[drv]["P"]["Mai"].values())
    print(f"s={total:,}")

with open("_mai_breakdown.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\nSalvo em _mai_breakdown.json")
