#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcula targets corretos por período usando SUM(NUM_TARGET_NPS)/SUM(DENOM_TARGET_NPS).
Cobre todos os meses e semanas do histórico.
Salva em _period_targets.json
"""
import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
bq = bigquery.Client(project="meli-bi-data")

DG = {
    'ME Vendedor':     ['ME Vendedor Seller Dev','ME Vendedor Mature','ME Vendedor Meli Pro'],
    'Exp. Impositiva': ['Experiencia Impositiva Seller Dev','Experiencia Impositiva Mature','Experiencia Impositiva Meli Pro'],
    'PCF Vendedor':    ['PCF Vendedor Seller Dev','PCF Vendedor Mature','PCF Vendedor Meli Pro'],
    'Post Venta':      ['Post Venta Seller Dev','Post Venta Mature','Post Venta Meli Pro'],
    'Publicaciones':   ['Publicaciones Seller Dev','Publicaciones Mature','Publicaciones Meli Pro'],
    'FBM-S':           ['FBM-S Seller Dev','FBM-S Mature','FBM-S Meli Pro'],
    'Partners':        ['Partners'],
    'Otros CV':        ['Otros CV'],
}
SELLERS_SEM_MED = list(set(d for drvs in DG.values() for d in drvs))
DRV_IN = "'" + "','".join(d.replace("'","''") for d in SELLERS_SEM_MED) + "'"

# Períodos a calcular
MONTHLY_PERIODS = {
    'Jan': ('2026-01-01','2026-01-31'),
    'Fev': ('2026-02-01','2026-02-28'),
    'Mar': ('2026-03-01','2026-03-31'),
    'Abr': ('2026-04-01','2026-04-30'),
    'Mai': ('2026-05-01','2026-05-11'),
}
WEEKLY_PERIODS = {
    '23/mar': ('2026-03-23','2026-03-29'),
    '30/mar': ('2026-03-30','2026-04-05'),
    '06/abr': ('2026-04-06','2026-04-12'),
    '13/abr': ('2026-04-13','2026-04-19'),
    '20/abr': ('2026-04-20','2026-04-26'),
    '27/abr': ('2026-04-27','2026-05-03'),
    '04/mai': ('2026-05-04','2026-05-10'),
    'VIG':    ('2026-05-11','2026-05-11'),
}

SQL = """
SELECT DRIVER_TARGET_NPS as driver,
  ROUND(100.0 * SUM(NUM_TARGET_NPS) / NULLIF(SUM(DENOM_TARGET_NPS),0), 2) as tgt
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP`
WHERE CENTER='BR' AND SIT_SITE_ID='MLB'
  AND QUE_QUEUE_TYPE='VALID_CS' AND MP_ON_FLAG='E-Commerce'
  AND FLAG_QUARTER_MONTH='{flag}'
  AND DATE_ID BETWEEN DATE('{start}') AND DATE('{end}')
  AND DRIVER_TARGET_NPS IN ({drv})
GROUP BY 1
"""

def query_targets(start, end, flag):
    rows = list(bq.query(SQL.format(start=start, end=end, flag=flag, drv=DRV_IN)).result())
    drv_tgts = {r.driver: float(r.tgt) for r in rows if r.tgt}
    # Grupos
    grp_tgts = {}
    for grp, drvs in DG.items():
        num = sum(drv_tgts.get(d,0) for d in drvs if d in drv_tgts)
        den_cnt = sum(1 for d in drvs if d in drv_tgts)
        # Método correto: query separada por grupo
        drv_in_g = "'" + "','".join(d.replace("'","''") for d in drvs) + "'"
        try:
            r = list(bq.query(f"""
            SELECT ROUND(100.0*SUM(NUM_TARGET_NPS)/NULLIF(SUM(DENOM_TARGET_NPS),0),2) as tgt
            FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP`
            WHERE CENTER='BR' AND SIT_SITE_ID='MLB' AND QUE_QUEUE_TYPE='VALID_CS'
              AND MP_ON_FLAG='E-Commerce' AND FLAG_QUARTER_MONTH='{flag}'
              AND DATE_ID BETWEEN DATE('{start}') AND DATE('{end}')
              AND DRIVER_TARGET_NPS IN ({drv_in_g})
            """).result())
            grp_tgts[grp] = float(r[0].tgt) if r and r[0].tgt else None
            time.sleep(0.5)
        except: grp_tgts[grp] = None
    # Consolidado
    try:
        rc = list(bq.query(f"""
        SELECT ROUND(100.0*SUM(NUM_TARGET_NPS)/NULLIF(SUM(DENOM_TARGET_NPS),0),2) as tgt
        FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP`
        WHERE CENTER='BR' AND SIT_SITE_ID='MLB' AND QUE_QUEUE_TYPE='VALID_CS'
          AND MP_ON_FLAG='E-Commerce' AND FLAG_QUARTER_MONTH='{flag}'
          AND DATE_ID BETWEEN DATE('{start}') AND DATE('{end}')
          AND DRIVER_TARGET_NPS IN ({DRV_IN})
        """).result())
        consolidated = float(rc[0].tgt) if rc and rc[0].tgt else None
        time.sleep(0.5)
    except: consolidated = None
    return {"drivers": drv_tgts, "groups": grp_tgts, "consolidated": consolidated}

result = {"monthly": {}, "weekly": {}}

print("=== TARGETS MENSAIS ===")
for period, (start, end) in MONTHLY_PERIODS.items():
    print(f"  {period} ({start})...", end=" ", flush=True)
    time.sleep(1)
    result["monthly"][period] = query_targets(start, end, "MONTH")
    cons = result["monthly"][period]["consolidated"]
    print(f"cons={cons}%")

print("\n=== TARGETS SEMANAIS ===")
for period, (start, end) in WEEKLY_PERIODS.items():
    print(f"  {period} ({start})...", end=" ", flush=True)
    time.sleep(1)
    result["weekly"][period] = query_targets(start, end, "WEEK")
    cons = result["weekly"][period]["consolidated"]
    print(f"cons={cons}%")

with open("_period_targets.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\nSalvo em _period_targets.json")
