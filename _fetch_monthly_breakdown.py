#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca breakdowns mensais (Processo, Canal, Oficina) da tabela oficial
DM_CX_NPS_CS_GOALS_MGR_AND_UP com filtros corretos VALID_CS/E-Commerce/Sellers.
Salva em _monthly_breakdown.json para uso no dashboard de tendências.
"""
import json, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
bq = bigquery.Client(project="meli-bi-data")

SELLERS = (
    'ME Vendedor Seller Dev','ME Vendedor Mature','ME Vendedor Meli Pro',
    'Experiencia Impositiva Seller Dev','Experiencia Impositiva Mature','Experiencia Impositiva Meli Pro',
    'PCF Vendedor Seller Dev','PCF Vendedor Mature','PCF Vendedor Meli Pro',
    'Post Venta Seller Dev','Post Venta Mature','Post Venta Meli Pro',
    'Publicaciones Seller Dev','Publicaciones Mature','Publicaciones Meli Pro',
    'FBM-S Seller Dev','FBM-S Mature','FBM-S Meli Pro',
    'Partners','Otros CV',
    'CBT','PDD DS&XD - Vendedor','PDD FBM - Vendedor','PDD Fotos - Vendedor',
    'PDD MP,FLEX & CBT - Vendedor','PNR ME - Vendedor','PNR MP - Vendedor',
)
DRV_IN = "'" + "','".join(d.replace("'","''") for d in SELLERS) + "'"

from datetime import date, timedelta
import calendar, re as _re

# ── Calcula períodos dinamicamente ───────────────────────────────────────────
_today     = date.today()
_yesterday = _today - timedelta(days=1)

def _month_range(y, m):
    return date(y, m, 1), date(y, m, calendar.monthrange(y, m)[1])

_m1 = _today.month
_y1 = _today.year
_m2 = _m1 - 1 if _m1 > 1 else 12
_y2 = _y1 if _m1 > 1 else _y1 - 1
_ABBR = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

_cur_first = date(_y1, _m1, 1)
_prev_first, _prev_last = _month_range(_y2, _m2)

PERIODS_MONTHLY = {
    _ABBR[_m2 - 1]: (str(_prev_first), str(_prev_last)),
    _ABBR[_m1 - 1]: (str(_cur_first),  str(_yesterday)),
}

# Períodos semanais lidos de _fetch_weekly_data.py
with open('_fetch_weekly_data.py', encoding='utf-8') as _fw:
    _fw_src = _fw.read()
_pm = _re.search(r'PERIODS\s*=\s*\{(.+?)\}', _fw_src, _re.DOTALL)
def _ep(name):
    m = _re.search(rf'"{name}".*?"(\d{{4}}-\d{{2}}-\d{{2}})".*?"(\d{{4}}-\d{{2}}-\d{{2}})"', _pm.group(1))
    return m.group(1), m.group(2)

PERIODS_WEEKLY = {
    'S2': _ep('S2_new'),
    'S1': _ep('S1_new'),
}

print("Períodos breakdown:")
for k, (s, e) in {**PERIODS_MONTHLY, **PERIODS_WEEKLY}.items():
    print(f"  {k}: {s} → {e}")

SQL = """
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
  AND FLAG_QUARTER_MONTH='MONTH'
  AND DATE_ID BETWEEN DATE('{start}') AND DATE('{end}')
  AND DRIVER_TARGET_NPS IN ({drv})
GROUP BY 1,2,3,4,5
HAVING SUM(SURVEYS) >= 2
ORDER BY 1,8 DESC
"""

def nps(p,d,s): return round(100.0*(p-d)/s, 2) if s>0 else None

result = {}   # {period: {driver: {P:{}, C:{}, O:{}}}}

all_periods = [(p,s,e,'MONTH') for p,(s,e) in PERIODS_MONTHLY.items()] + \
              [(p,s,e,'WEEK')  for p,(s,e) in PERIODS_WEEKLY.items()]

for period, start, end, flag in all_periods:
    sql_period = SQL.replace("FLAG_QUARTER_MONTH='MONTH'", f"FLAG_QUARTER_MONTH='{flag}'")
    print(f'\nPeriodo: {period} ({start} -> {end}, {flag})')
    time.sleep(2)
    rows = list(bq.query(sql_period.format(start=start, end=end, drv=DRV_IN)).result())
    print(f'  {len(rows)} linhas')

    period_data = {}
    for r in rows:
        drv = r.driver
        if drv not in period_data:
            period_data[drv] = {'P': {}, 'C': {}, 'O': {}, 'T': {}}
        p, d, s = int(r.p or 0), int(r.d or 0), int(r.s or 0)

        # Processo
        proc = r.proc
        if proc and not proc.startswith('('):
            pv = period_data[drv]['P'].setdefault(proc, {'p':0,'d':0,'s':0})
            pv['p']+=p; pv['d']+=d; pv['s']+=s

        # Canal (normaliza)
        canal = r.canal
        if canal and not canal.startswith('('):
            canal = canal.replace('MULTICANAL ', '')
            cv = period_data[drv]['C'].setdefault(canal, {'p':0,'d':0,'s':0})
            cv['p']+=p; cv['d']+=d; cv['s']+=s

        # Oficina
        office = r.office
        if office and not office.startswith('('):
            ov = period_data[drv]['O'].setdefault(office, {'p':0,'d':0,'s':0})
            ov['p']+=p; ov['d']+=d; ov['s']+=s

        # Equipe (CX_TEAM_NAME)
        team = r.team
        if team and not team.startswith('('):
            tv = period_data[drv]['T'].setdefault(team, {'p':0,'d':0,'s':0})
            tv['p']+=p; tv['d']+=d; tv['s']+=s

    # Calcula NPS por item
    for drv in period_data:
        for dim in ['P','C','O','T']:
            for k,v in period_data[drv][dim].items():
                v['nps'] = nps(v['p'],v['d'],v['s'])

    # ── Seniority: usa processos do breakdown oficial para filtrar ──
    # Agrupa todos os processos por driver a partir do period_data já calculado
    for drv in period_data:
        procs = list(period_data[drv]['P'].keys())
        if not procs: continue
        procs_in = "'" + "','".join(p.replace("'","''") for p in procs[:20]) + "'"
        SR_SQL = f"""
        SELECT COALESCE(ANTIGUEDAD_REP,'(sem senior)') as seniority,
          SUM(PROMOTER) as p, SUM(DETRACTOR) as d, COUNT(*) as s
        FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
        WHERE SIT_SITE_ID='MLB' AND SURVEY_CENTER='BR'
          AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
          AND PRO_PROCESS_NAME IN ({procs_in})
          AND (PROMOTER=1 OR DETRACTOR=1)
        GROUP BY 1 HAVING COUNT(*) >= 2
        """
        try:
            time.sleep(0.8)
            sr_rows = list(bq.query(SR_SQL).result())
            period_data[drv].setdefault('Sr', {})
            for r in sr_rows:
                sr_key = r.seniority
                if not sr_key or sr_key.startswith('(sem') or sr_key in ('UNAVAILABLE','unavailable'): continue
                sr_key = {'EXPERT':'Expert','NEWBIE':'Newbie','TRAINING':'Training'}.get(sr_key, sr_key.capitalize() if sr_key.isupper() else sr_key)
                sv = period_data[drv]['Sr'].setdefault(sr_key, {'p':0,'d':0,'s':0})
                sv['p'] += int(r.p); sv['d'] += int(r.d); sv['s'] += int(r.s)
            for k,v in period_data[drv]['Sr'].items():
                v['nps'] = nps(v['p'],v['d'],v['s'])
        except Exception as e:
            print(f'  Sr {drv[:30]}: ERRO {e}')

    result[period] = period_data
    for drv, dims in period_data.items():
        tot = sum(v['s'] for v in dims['P'].values())
        if tot > 0:
            print(f'    {drv[:40]}: P={tot:,} surv')

with open('_monthly_breakdown.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('\nSalvo em _monthly_breakdown.json')
