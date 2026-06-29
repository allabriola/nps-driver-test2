#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca dados mensais NPS por driver — últimos 6 meses + mês atual MTD.
Tabela: DM_CX_NPS_CS_GOALS_MGR_AND_UP com filtros VALID_CS / E-Commerce / Sellers.
Os períodos são calculados automaticamente com base na data de hoje.
"""
import sys, json
from datetime import date, timedelta
import calendar

sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery

client = bigquery.Client(project="meli-bi-data")

# ── Calcula períodos dinamicamente ───────────────────────────────────────────
MONTH_ABBR = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

today = date.today()
# Ontem (último dia com dados completos)
yesterday = today - timedelta(days=1)

def month_range(year, month):
    """Retorna (primeiro_dia, ultimo_dia) do mês."""
    first = date(year, month, 1)
    last  = date(year, month, calendar.monthrange(year, month)[1])
    return first, last

# Monta 6 meses fechados + mês atual MTD
PERIODS = {}
for i in range(5, 0, -1):
    # Calcula mês retroativo
    m = today.month - i
    y = today.year
    while m <= 0:
        m += 12
        y -= 1
    first, last = month_range(y, m)
    lbl = MONTH_ABBR[m - 1]
    PERIODS[lbl] = (str(first), str(last))

# Mês atual — até ontem (MTD)
cur_first = date(today.year, today.month, 1)
cur_end   = yesterday if yesterday >= cur_first else cur_first
lbl_cur   = MONTH_ABBR[today.month - 1]
PERIODS[lbl_cur] = (str(cur_first), str(cur_end))

print("Períodos calculados:")
for lbl, (s, e) in PERIODS.items():
    print(f"  {lbl}: {s} → {e}")

# ── Drivers ──────────────────────────────────────────────────────────────────
SELLERS_DRIVERS = (
    "ME Vendedor Seller Dev","ME Vendedor Mature","ME Vendedor Meli Pro",
    "Experiencia Impositiva Seller Dev","Experiencia Impositiva Mature","Experiencia Impositiva Meli Pro",
    "PCF Vendedor Seller Dev","PCF Vendedor Mature","PCF Vendedor Meli Pro",
    "Post Venta Seller Dev","Post Venta Mature","Post Venta Meli Pro",
    "Publicaciones Seller Dev","Publicaciones Mature","Publicaciones Meli Pro",
    "FBM-S Seller Dev","FBM-S Mature","FBM-S Meli Pro",
    "Partners","Otros CV",
    "CBT","PDD DS&XD - Vendedor","PDD FBM - Vendedor","PDD Fotos - Vendedor",
    "PDD MP,FLEX & CBT - Vendedor","PNR ME - Vendedor","PNR MP - Vendedor",
)
_DRV_IN = "'" + "','".join(d.replace("'","''") for d in SELLERS_DRIVERS) + "'"

BASE_SQL = """
SELECT DRIVER_TARGET_NPS AS DRIVER,
       SUM(PROMOTERS)    AS P,
       SUM(DETRACTORS)   AS D,
       SUM(SURVEYS)      AS S
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP`
WHERE DATE_ID BETWEEN DATE("{start}") AND DATE("{end}")
  AND CENTER = "BR"
  AND SIT_SITE_ID = "MLB"
  AND QUE_QUEUE_TYPE = "VALID_CS"
  AND MP_ON_FLAG = "E-Commerce"
  AND FLAG_QUARTER_MONTH = "MONTH"
  AND DRIVER_TARGET_NPS IN (""" + _DRV_IN + """)
GROUP BY 1
ORDER BY 1
"""

# ── Executa queries ───────────────────────────────────────────────────────────
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
print(f"Mês atual (M1): {lbl_cur} ({str(cur_first)} → {str(cur_end)})")
print(f"Total surveys {lbl_cur}: {sum(v[2] for v in all_data.get(lbl_cur,{}).values()):,}")
