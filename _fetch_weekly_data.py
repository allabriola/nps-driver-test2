#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca dados NPS por driver usando DM_CX_NPS_CS_GOALS_MGR_AND_UP
Tabela correta - tem DRIVER_TARGET_NPS diretamente!
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
client = bigquery.Client(project="meli-bi-data")

# Periods atualizados para 19/mai/2026
PERIODS = {
    "S1_new":  ("2026-06-08", "2026-06-14", "WEEK"),
    "S2_new":  ("2026-06-01", "2026-06-07", "WEEK"),
    "VIG_new": ("2026-06-15", "2026-06-19", "WEEK"),
}

_DRV_IN = ("'ME Vendedor Seller Dev','ME Vendedor Mature','ME Vendedor Meli Pro',"
           "'PCF Vendedor Seller Dev','PCF Vendedor Mature','PCF Vendedor Meli Pro',"
           "'Post Venta Seller Dev','Post Venta Mature','Post Venta Meli Pro',"
           "'Publicaciones Seller Dev','Publicaciones Mature','Publicaciones Meli Pro',"
           "'Experiencia Impositiva Seller Dev','Experiencia Impositiva Mature','Experiencia Impositiva Meli Pro',"
           "'Partners','CBT','FBM-S Seller Dev','FBM-S Mature','FBM-S Meli Pro',"
           "'PDD DS&XD - Vendedor','PDD FBM - Vendedor','PDD MP,FLEX & CBT - Vendedor',"
           "'PDD Fotos - Vendedor','PNR ME - Vendedor','PNR MP - Vendedor','Otros CV'")

BASE_SQL = """
SELECT DRIVER_TARGET_NPS AS DRIVER,
       SUM(PROMOTERS)   AS P,
       SUM(DETRACTORS)  AS D,
       SUM(SURVEYS)     AS S
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP`
WHERE DATE_ID BETWEEN DATE("{start}") AND DATE("{end}")
  AND CENTER = "BR"
  AND SIT_SITE_ID = "MLB"
  AND QUE_QUEUE_TYPE = "VALID_CS"
  AND MP_ON_FLAG = "E-Commerce"
  AND FLAG_QUARTER_MONTH = "{flag}"
  AND DRIVER_TARGET_NPS IN (""" + _DRV_IN + """)
GROUP BY 1
ORDER BY 1
"""

all_data = {}
for label, (start, end, flag) in PERIODS.items():
    sql = BASE_SQL.replace("{start}", start).replace("{end}", end).replace("{flag}", flag)
    print(f"\n=== {label} ({start} - {end}) ===")
    rows = list(client.query(sql).result())
    period_data = {}
    for r in rows:
        p = int(r.P or 0); d = int(r.D or 0); s = int(r.S or 0)
        nps = round(100*(p-d)/s, 2) if s > 0 else 0
        period_data[r.DRIVER] = (p, d, s)
        print(f"  {r.DRIVER:<45}: ({p}, {d}, {s})  NPS={nps}")
    all_data[label] = period_data
    total_s = sum(v[2] for v in period_data.values())
    total_p = sum(v[0] for v in period_data.values())
    total_d = sum(v[1] for v in period_data.values())
    nps_all = round(100*(total_p-total_d)/total_s, 2) if total_s else 0
    print(f"  TOTAL {label}: surveys={total_s} NPS={nps_all}%")

# Save
with open("_new_weekly_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print("\n\nSaved to _new_weekly_data.json")

# Print in build_driver_impact.py format
print("\n\n" + "="*60)
print("# Dados para build_driver_impact.py")
print("="*60)

# Get all drivers
drivers = sorted(set(
    d for pd in all_data.values() for d in pd.keys()
))

print("\n# weekly_driver update:")
print("# S2=old_S1 (stays same), S1=new, VIG=new")
for drv in drivers:
    s2 = all_data.get("S2_new", {}).get(drv, (0,0,0))
    s1 = all_data.get("S1_new", {}).get(drv, (0,0,0))
    vig = all_data.get("VIG_new", {}).get(drv, (0,0,0))
    print(f'    "{drv}":{" "*(45-len(drv))}{{"S2": {s2}, "S1": {s1}, "VIG": {vig}}},')
