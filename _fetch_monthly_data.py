#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca dados mensais NPS por driver (Abril final + Maio WTD).
Tabela: DM_CX_NPS_CS_GOALS_MGR_AND_UP com filtros VALID_CS / E-Commerce / Sellers.
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery

client = bigquery.Client(project="meli-bi-data")

PERIODS = {
    "Abr_final": ("2026-04-01", "2026-04-30"),
    "Mai_wtd":   ("2026-05-01", "2026-05-05"),
}

BASE_SQL = """
SELECT m.DRIVER_TARGET_NPS AS DRIVER,
       SUM(m.PROMOTERS)    AS P,
       SUM(m.DETRACTORS)   AS D,
       SUM(m.SURVEYS)      AS S
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP` m
INNER JOIN `meli-bi-data.WHOWNER.LK_CX_NPS_CS_GOALS_DRIVER_MANAGER` lk
  ON lk.NPS_TARGET_DRIVER = m.DRIVER_TARGET_NPS
  AND lk.CENTER = m.CENTER
  AND lk.MONTH_ID = DATE_TRUNC(m.DATE_ID, MONTH)
WHERE m.DATE_ID BETWEEN DATE("{start}") AND DATE("{end}")
  AND m.CENTER = "BR"
  AND m.QUE_QUEUE_TYPE = "VALID_CS"
  AND m.MP_ON_FLAG = "E-Commerce"
  AND m.FLAG_QUARTER_MONTH = "MONTH"
  AND lk.NPS_TARGET_DRIVER_GROUP = "Sellers"
GROUP BY 1
ORDER BY 1
"""

all_data = {}
for label, (start, end) in PERIODS.items():
    sql = BASE_SQL.replace("{start}", start).replace("{end}", end)
    print(f"\n=== {label} ({start} → {end}) ===")
    rows = list(client.query(sql).result())
    period_data = {}
    total_p = total_d = total_s = 0
    for r in rows:
        p = int(r.P or 0); d = int(r.D or 0); s = int(r.S or 0)
        nps = round(100*(p-d)/s, 2) if s > 0 else 0
        period_data[r.DRIVER] = (p, d, s)
        print(f"  {r.DRIVER:<45}: ({p:>5}, {d:>4}, {s:>5})  NPS={nps:.2f}%")
        total_p += p; total_d += d; total_s += s
    nps_tot = round(100*(total_p-total_d)/total_s, 2) if total_s else 0
    print(f"  >>> TOTAL: surveys={total_s:,}  NPS={nps_tot:.2f}%")
    all_data[label] = period_data

with open("_monthly_result.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print("\n\nSalvo em _monthly_result.json")
