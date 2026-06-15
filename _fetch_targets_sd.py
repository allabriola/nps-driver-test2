#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca targets corretos para os 6 drivers Seller Dev + Partners via BQ.
Fórmula: SUM(NUM_TARGET_NPS) / SUM(DENOM_TARGET_NPS)
Salva em _period_targets_sd.json  (usado por generate_html_seller_dev.py)
"""
import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
bq = bigquery.Client(project="meli-bi-data")

SD_DRIVERS = [
    'Experiencia Impositiva Seller Dev',
    'ME Vendedor Seller Dev',
    'PCF Vendedor Seller Dev',
    'Post Venta Seller Dev',
    'Publicaciones Seller Dev',
    'Partners',
]
DRV_IN = "'" + "','".join(d.replace("'","''") for d in SD_DRIVERS) + "'"

MONTHLY_PERIODS = {
    'Jan': ('2026-01-01', '2026-01-31', 'MONTH'),
    'Fev': ('2026-02-01', '2026-02-28', 'MONTH'),
    'Mar': ('2026-03-01', '2026-03-31', 'MONTH'),
    'Abr': ('2026-04-01', '2026-04-30', 'MONTH'),
    'Mai': ('2026-05-01', '2026-05-31', 'MONTH'),
    'Jun': ('2026-06-01', '2026-06-30', 'MONTH'),
}
WEEKLY_PERIODS = {
    '23/mar': ('2026-03-23', '2026-03-29', 'WEEK'),
    '30/mar': ('2026-03-30', '2026-04-05', 'WEEK'),
    '06/abr': ('2026-04-06', '2026-04-12', 'WEEK'),
    '13/abr': ('2026-04-13', '2026-04-19', 'WEEK'),
    '20/abr': ('2026-04-20', '2026-04-26', 'WEEK'),
    '27/abr': ('2026-04-27', '2026-05-03', 'WEEK'),
    '04/mai': ('2026-05-04', '2026-05-10', 'WEEK'),
    '11/mai': ('2026-05-11', '2026-05-17', 'WEEK'),
    '18/mai': ('2026-05-18', '2026-05-24', 'WEEK'),
    '25/mai': ('2026-05-25', '2026-05-31', 'WEEK'),
    '01/jun': ('2026-06-01', '2026-06-07', 'WEEK'),
    '08/jun': ('2026-06-08', '2026-06-14', 'WEEK'),
    'VIG':    ('2026-06-15', '2026-06-15', 'WEEK'),
}

SQL_CONS = """
SELECT ROUND(100.0 * SUM(NUM_TARGET_NPS) / NULLIF(SUM(DENOM_TARGET_NPS), 0), 2) AS tgt
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP`
WHERE CENTER = 'BR'
  AND SIT_SITE_ID = 'MLB'
  AND QUE_QUEUE_TYPE = 'VALID_CS'
  AND MP_ON_FLAG = 'E-Commerce'
  AND FLAG_QUARTER_MONTH = '{flag}'
  AND DATE_ID BETWEEN DATE('{start}') AND DATE('{end}')
  AND DRIVER_TARGET_NPS IN ({drv})
"""

SQL_DRV = """
SELECT DRIVER_TARGET_NPS AS driver,
  ROUND(100.0 * SUM(NUM_TARGET_NPS) / NULLIF(SUM(DENOM_TARGET_NPS), 0), 2) AS tgt
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP`
WHERE CENTER = 'BR'
  AND SIT_SITE_ID = 'MLB'
  AND QUE_QUEUE_TYPE = 'VALID_CS'
  AND MP_ON_FLAG = 'E-Commerce'
  AND FLAG_QUARTER_MONTH = '{flag}'
  AND DATE_ID BETWEEN DATE('{start}') AND DATE('{end}')
  AND DRIVER_TARGET_NPS IN ({drv})
GROUP BY 1
"""

def query_period(start, end, flag):
    # Consolidado SD
    try:
        rc = list(bq.query(SQL_CONS.format(start=start, end=end, flag=flag, drv=DRV_IN)).result())
        consolidated = float(rc[0].tgt) if rc and rc[0].tgt else None
    except Exception as e:
        print(f"    WARN consolidado: {e}")
        consolidated = None
    time.sleep(0.5)

    # Individual por driver
    try:
        rows = list(bq.query(SQL_DRV.format(start=start, end=end, flag=flag, drv=DRV_IN)).result())
        drivers = {r.driver: float(r.tgt) for r in rows if r.tgt}
    except Exception as e:
        print(f"    WARN drivers: {e}")
        drivers = {}

    return {"consolidated": consolidated, "drivers": drivers}

result = {"monthly": {}, "weekly": {}}

print("=== TARGETS MENSAIS (Seller Dev + Partners) ===")
for period, (start, end, flag) in MONTHLY_PERIODS.items():
    print(f"  {period} ({start}–{end})...", end=" ", flush=True)
    data = query_period(start, end, flag)
    result["monthly"][period] = data
    print(f"consolidado={data['consolidated']}%")
    for d, t in data["drivers"].items():
        print(f"    {d:<42} {t}%")

print("\n=== TARGETS SEMANAIS (Seller Dev + Partners) ===")
for period, (start, end, flag) in WEEKLY_PERIODS.items():
    print(f"  {period} ({start})...", end=" ", flush=True)
    data = query_period(start, end, flag)
    result["weekly"][period] = data
    print(f"consolidado={data['consolidated']}%")

with open("_period_targets_sd.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\nSalvo em _period_targets_sd.json")
