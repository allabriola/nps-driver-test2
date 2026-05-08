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

PERIODS = {
    'Abr': ('2026-04-01', '2026-04-30'),
    'Mai': ('2026-05-01', '2026-05-08'),
}

SQL = """
SELECT
  DRIVER_TARGET_NPS as driver,
  COALESCE(PRO_PROCESS_NAME, '(sem processo)') as proc,
  COALESCE(CX_USER_TEAM_CHANNEL, '(sem canal)') as canal,
  COALESCE(CX_USER_OFFICE, '(sem office)') as office,
  SUM(PROMOTERS) as p, SUM(DETRACTORS) as d, SUM(SURVEYS) as s
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_CS_GOALS_MGR_AND_UP`
WHERE CENTER='BR' AND SIT_SITE_ID='MLB'
  AND QUE_QUEUE_TYPE='VALID_CS' AND MP_ON_FLAG='E-Commerce'
  AND FLAG_QUARTER_MONTH='MONTH'
  AND DATE_ID BETWEEN DATE('{start}') AND DATE('{end}')
  AND DRIVER_TARGET_NPS IN ({drv})
GROUP BY 1,2,3,4
HAVING SUM(SURVEYS) >= 2
ORDER BY 1,7 DESC
"""

def nps(p,d,s): return round(100.0*(p-d)/s, 2) if s>0 else None

result = {}   # {period: {driver: {P:{}, C:{}, O:{}}}}

for period, (start, end) in PERIODS.items():
    print(f'\nPeriodo: {period} ({start} -> {end})')
    time.sleep(2)
    rows = list(bq.query(SQL.format(start=start, end=end, drv=DRV_IN)).result())
    print(f'  {len(rows)} linhas')

    period_data = {}
    for r in rows:
        drv = r.driver
        if drv not in period_data:
            period_data[drv] = {'P': {}, 'C': {}, 'O': {}}
        p, d, s = int(r.p), int(r.d), int(r.s)
        n = nps(p, d, s)

        # Processo
        proc = r.proc
        if proc and not proc.startswith('('):
            pv = period_data[drv]['P'].setdefault(proc, {'p':0,'d':0,'s':0})
            pv['p']+=p; pv['d']+=d; pv['s']+=s

        # Canal (normaliza)
        canal = r.canal
        if canal and not canal.startswith('('):
            canal = canal.replace('MULTICANAL ', '')   # normaliza MULTICANAL CHAT -> CHAT
            cv = period_data[drv]['C'].setdefault(canal, {'p':0,'d':0,'s':0})
            cv['p']+=p; cv['d']+=d; cv['s']+=s

        # Oficina
        office = r.office
        if office and not office.startswith('('):
            ov = period_data[drv]['O'].setdefault(office, {'p':0,'d':0,'s':0})
            ov['p']+=p; ov['d']+=d; ov['s']+=s

    # Calcula NPS por item
    for drv in period_data:
        for dim in ['P','C','O']:
            for k,v in period_data[drv][dim].items():
                v['nps'] = nps(v['p'],v['d'],v['s'])

    result[period] = period_data
    # Total por driver
    for drv, dims in period_data.items():
        tot = sum(v['s'] for v in dims['P'].values())
        if tot > 0:
            print(f'    {drv[:40]}: P={tot:,} surv')

with open('_monthly_breakdown.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('\nSalvo em _monthly_breakdown.json')
