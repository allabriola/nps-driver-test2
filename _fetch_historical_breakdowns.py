#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca breakdowns históricos (processo/canal/oficina/seniority) para todas as
semanas em WEEK_LABELS. Salva em _breakdown_historical.json com chave=label_semana.
Permite que _generate_weekly_snapshots.py use dados corretos para cada semana.
"""
import json, sys, time, re
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
bq = bigquery.Client(project="meli-bi-data")

# ── Carrega WEEK_LABELS e datas ───────────────────────────────────────
with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'generate_html_gerencia.py', 'exec'), ns)
WEEK_LABELS = ns['WEEK_LABELS']

# Mapeamento label → intervalo de datas (segunda a domingo)
MON_NUM = {"jan":"01","fev":"02","mar":"03","abr":"04","mai":"05",
           "jun":"06","jul":"07","ago":"08","set":"09","out":"10","nov":"11","dez":"12"}

def lbl_to_monday(lbl):
    parts = lbl.strip().split('/')
    if len(parts)==2:
        day, mon = parts[0].zfill(2), parts[1].lower().strip()
        return f"2026-{MON_NUM.get(mon,'01')}-{day}"
    return None

def monday_to_sunday(monday_str):
    from datetime import date, timedelta
    d = date.fromisoformat(monday_str)
    return str(d + timedelta(days=6))

# Constrói períodos para cada semana
PERIODS = {}
for lbl in WEEK_LABELS:
    mon = lbl_to_monday(lbl)
    if mon:
        PERIODS[lbl] = (mon, monday_to_sunday(mon))

SELLERS_DRIVERS = (
    "ME Vendedor Seller Dev","ME Vendedor Mature","ME Vendedor Meli Pro",
    "Experiencia Impositiva Seller Dev","Experiencia Impositiva Mature","Experiencia Impositiva Meli Pro",
    "PCF Vendedor Seller Dev","PCF Vendedor Mature","PCF Vendedor Meli Pro",
    "Post Venta Seller Dev","Post Venta Mature","Post Venta Meli Pro",
    "Publicaciones Seller Dev","Publicaciones Mature","Publicaciones Meli Pro",
    "FBM-S Seller Dev","FBM-S Mature","FBM-S Meli Pro",
    "Partners","Otros CV",
)
DRV_IN = "'" + "','".join(d.replace("'","''") for d in SELLERS_DRIVERS) + "'"

SQL_MAIN = """
SELECT
  DRIVER_TARGET_NPS as driver,
  COALESCE(PRO_PROCESS_NAME, '(sem processo)') as proc,
  COALESCE(CX_USER_TEAM_CHANNEL, '(sem canal)') as canal,
  COALESCE(CX_USER_OFFICE, '(sem office)') as office,
  COALESCE(CX_TEAM_NAME, '(sem equipe)') as team,
  SUM(PROMOTERS) as p, SUM(DETRACTORS) as d, SUM(SURVEYS) as s
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP`
WHERE CENTER='BR' AND SIT_SITE_ID='MLB'
  AND QUE_QUEUE_TYPE='VALID_CS' AND MP_ON_FLAG='E-Commerce'
  AND FLAG_QUARTER_MONTH='WEEK'
  AND DATE_ID BETWEEN DATE('{start}') AND DATE('{end}')
  AND DRIVER_TARGET_NPS IN ({drv})
GROUP BY 1,2,3,4,5
HAVING SUM(SURVEYS) >= 1
ORDER BY 1,8 DESC
"""

SQL_SR = """
SELECT COALESCE(ANTIGUEDAD_REP,'(sem senior)') as seniority,
  SUM(PROMOTER) as p, SUM(DETRACTOR) as d, COUNT(*) as s
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID='MLB' AND SURVEY_CENTER='BR'
  AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
  AND PRO_PROCESS_NAME IN ({procs})
  AND (PROMOTER=1 OR DETRACTOR=1)
GROUP BY 1 HAVING COUNT(*) >= 2
"""

def nps(p,d,s): return round(100*(p-d)/s,2) if s>0 else None

result = {}
print(f"Buscando breakdowns para {len(PERIODS)} semanas...\n")

for lbl, (start, end) in PERIODS.items():
    print(f"  {lbl} ({start} → {end})...", end=" ", flush=True)
    try:
        sql = SQL_MAIN.format(start=start, end=end, drv=DRV_IN)

        rows = list(bq.query(sql).result())
        drv_data = {}
        SR_NORM = {"EXPERT":"Expert","NEWBIE":"Newbie","TRAINING":"Training",
                   "expert":"Expert","newbie":"Newbie","training":"Training"}
        for r in rows:
            drv = r.driver
            if drv not in drv_data:
                drv_data[drv] = {"P":{}, "C":{}, "O":{}, "T":{}, "Sr":{}}
            p, d, s = int(r.p or 0), int(r.d or 0), int(r.s or 0)
            def add(dim, key):
                if not key or key.startswith('(sem'): return
                canal_norm = key.replace('MULTICANAL ','') if dim=='C' else key
                x = drv_data[drv][dim].setdefault(canal_norm, {"p":0,"d":0,"s":0})
                x["p"]+=p; x["d"]+=d; x["s"]+=s
            add("P", r.proc); add("C", r.canal); add("O", r.office); add("T", r.team)

        # Seniority via DM_CX_NPS_Y20_DETAIL
        for drv in drv_data:
            procs = list(drv_data[drv]["P"].keys())
            if not procs: continue
            procs_in = "'" + "','".join(p.replace("'","''") for p in procs[:20]) + "'"
            try:
                time.sleep(0.5)
                sr_rows = list(bq.query(SQL_SR.format(start=start, end=end, procs=procs_in)).result())
                for r in sr_rows:
                    sr_key = SR_NORM.get(r.seniority, r.seniority)
                    if not sr_key or sr_key.startswith('(') or sr_key in ('UNAVAILABLE','unavailable'): continue
                    x = drv_data[drv]["Sr"].setdefault(sr_key, {"p":0,"d":0,"s":0})
                    x["p"]+=int(r.p or 0); x["d"]+=int(r.d or 0); x["s"]+=int(r.s or 0)
            except Exception as e2:
                print(f" Sr({drv[:20]}): {e2}", end="")

        # Calcula NPS
        for drv in drv_data:
            for dim in drv_data[drv]:
                for v in drv_data[drv][dim].values():
                    v["nps"] = nps(v["p"],v["d"],v["s"])

        result[lbl] = drv_data
        total_s = sum(sum(v["s"] for v in drv_data[d]["P"].values()) for d in drv_data)
        print(f"{total_s:,} surveys, {len(drv_data)} drivers")
        time.sleep(0.5)
    except Exception as e:
        print(f"ERRO: {e}")
        result[lbl] = {}

with open('_breakdown_historical.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print(f"\nSalvo em _breakdown_historical.json")
print("Semanas:", list(result.keys()))
