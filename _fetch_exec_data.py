#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coleta dados qualitativos para o resumo executivo (sem chamada de API)."""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
bq = bigquery.Client(project="meli-bi-data")

with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)

monthly_history = ns['monthly_history']
MONTH_LABELS    = ns['MONTH_LABELS']
DRIVER_TARGETS  = ns['DRIVER_TARGETS']
NPS_TARGET      = float(ns['NPS_TARGET'])

EXCLUIDOS_EARLY = frozenset([
    "CBT","PDD DS&XD - Vendedor","PDD FBM - Vendedor","PDD Fotos - Vendedor",
    "PDD MP,FLEX & CBT - Vendedor","PNR ME - Vendedor","PNR MP - Vendedor",
])
ALL_DRIVERS = [d for d in monthly_history.keys() if d not in EXCLUIDOS_EARLY]

lCURR, lPREV = MONTH_LABELS[-2], MONTH_LABELS[-3]
DATES = {"Jan":("2026-01-01","2026-01-31"),"Fev":("2026-02-01","2026-02-28"),
         "Mar":("2026-03-01","2026-03-31"),"Abr":("2026-04-01","2026-04-30"),
         "Mai":("2026-05-01","2026-05-31")}
CURR_S, CURR_E = DATES[lCURR]

# Carrega mapeamento driver → processos do dd_breakdown.json
import os
_DD_PATH = "dd_breakdown.json"
_DD = {}
if os.path.exists(_DD_PATH):
    with open(_DD_PATH, encoding='utf-8') as f:
        _DD = json.load(f)

def get_procs(drvs):
    """Retorna lista de PRO_PROCESS_NAME para uma lista de drivers."""
    procs = set()
    for drv in drvs:
        for period_data in _DD.get(drv, {}).get("P", {}).values():
            procs.update(period_data.keys())
    return list(procs)

EXCLUIDOS = frozenset([
    "CBT","PDD DS&XD - Vendedor","PDD FBM - Vendedor","PDD Fotos - Vendedor",
    "PDD MP,FLEX & CBT - Vendedor","PNR ME - Vendedor","PNR MP - Vendedor",
])

DRIVER_GROUPS = {
    "ME Vendedor":     ["ME Vendedor Seller Dev","ME Vendedor Mature","ME Vendedor Meli Pro"],
    "Exp. Impositiva": ["Experiencia Impositiva Seller Dev","Experiencia Impositiva Mature","Experiencia Impositiva Meli Pro"],
    "PCF Vendedor":    ["PCF Vendedor Seller Dev","PCF Vendedor Mature","PCF Vendedor Meli Pro"],
    "Post Venta":      ["Post Venta Seller Dev","Post Venta Mature","Post Venta Meli Pro"],
    "Publicaciones":   ["Publicaciones Seller Dev","Publicaciones Mature","Publicaciones Meli Pro"],
    "FBM-S":           ["FBM-S Seller Dev","FBM-S Mature","FBM-S Meli Pro"],
    "Partners":        ["Partners"],
    "Otros CV":        ["Otros CV"],
}

def nps_r(p,d,s): return round(100.0*(p-d)/s,2) if s>0 else None
def grp_nps(lbl,drvs):
    p=sum(monthly_history[d].get(lbl,(0,0,0))[0] for d in drvs if d in monthly_history)
    dt=sum(monthly_history[d].get(lbl,(0,0,0))[1] for d in drvs if d in monthly_history)
    s=sum(monthly_history[d].get(lbl,(0,0,0))[2] for d in drvs if d in monthly_history)
    return nps_r(p,dt,s), s

sA=sum(monthly_history[d].get(lPREV,(0,0,0))[2] for d in ALL_DRIVERS)
sB=sum(monthly_history[d].get(lCURR,(0,0,0))[2] for d in ALL_DRIVERS)
pB_c=sum(monthly_history[d].get(lCURR,(0,0,0))[0] for d in ALL_DRIVERS)
dB_c=sum(monthly_history[d].get(lCURR,(0,0,0))[1] for d in ALL_DRIVERS)
nps_curr=nps_r(pB_c,dB_c,sB)
pA_c=sum(monthly_history[d].get(lPREV,(0,0,0))[0] for d in ALL_DRIVERS)
dA_c=sum(monthly_history[d].get(lPREV,(0,0,0))[1] for d in ALL_DRIVERS)
nps_prev=nps_r(pA_c,dA_c,sA)

wf={}
for grp,drvs in DRIVER_GROUPS.items():
    pA=sum(monthly_history[d].get(lPREV,(0,0,0))[0] for d in drvs if d in monthly_history)
    dA=sum(monthly_history[d].get(lPREV,(0,0,0))[1] for d in drvs if d in monthly_history)
    sA_g=sum(monthly_history[d].get(lPREV,(0,0,0))[2] for d in drvs if d in monthly_history)
    pB=sum(monthly_history[d].get(lCURR,(0,0,0))[0] for d in drvs if d in monthly_history)
    dB=sum(monthly_history[d].get(lCURR,(0,0,0))[1] for d in drvs if d in monthly_history)
    sB_g=sum(monthly_history[d].get(lCURR,(0,0,0))[2] for d in drvs if d in monthly_history)
    na=nps_r(pA,dA,sA_g) or 0; nb=nps_r(pB,dB,sB_g) or 0
    sha=sA_g/sA if sA else 0; shb=sB_g/sB if sB else 0
    tgt_num=sum(monthly_history[d].get(lCURR,(0,0,0))[2]*DRIVER_TARGETS.get(d,NPS_TARGET) for d in drvs if d in monthly_history)
    tgt=tgt_num/sB_g if sB_g else NPS_TARGET
    g_curr,g_surv=grp_nps(lCURR,drvs); g_prev,_=grp_nps(lPREV,drvs)
    wf[grp]={"var":round(sha*(nb-na)+(shb-sha)*(nb-(nps_curr or 0)),2),
             "nps_curr":g_curr,"nps_prev":g_prev,"surv":g_surv,"target":round(tgt,2),
             "delta_tgt":round(g_curr-tgt,2) if g_curr is not None else None}

sorted_wf=sorted(wf.items(),key=lambda x:x[1]["var"])
top_neg=[g for g,_ in sorted_wf[:3]]
top_pos=[g for g,_ in sorted_wf[-3:][::-1]]
priority=top_neg+top_pos

print(f"Consolidado: {lPREV} {nps_prev:.2f}% → {lCURR} {nps_curr:.2f}%  Δ={nps_curr-nps_prev:+.2f}pp")
print(f"Top neg: {top_neg}  |  Top pos: {top_pos}")

# Busca comentários
SQL="""SELECT PRO_PROCESS_NAME AS driver, COALESCE(CDU,'N/I') AS cdu,
  COALESCE(CX_SOL_NAME,'N/I') AS sol, COALESCE(ANTIGUEDAD_REP,'N/I') AS sen,
  COALESCE(SURVEY_CHANNEL,'N/I') AS canal, COALESCE(USER_OFFICE,'N/I') AS office,
  NPS AS score,
  CASE WHEN PROMOTER=1 THEN 'promotor' WHEN DETRACTOR=1 THEN 'detrator' ELSE 'neutro' END AS perfil,
  COALESCE(RES_DETRACTION_REASON,'') AS mot_det, COALESCE(RES_PROMOTION_REASON,'') AS mot_pro,
  NULLIF(TRIM(COMMENTS),'') AS comment, CAST(CAS_CASE_ID AS STRING) AS cid
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID='MLB' AND SURVEY_CENTER='BR'
  AND SURVEY_DATE_SURVEY BETWEEN '{s}' AND '{e}'
  AND PRO_PROCESS_NAME IN ({drv})
  AND (PROMOTER=1 OR DETRACTOR=1)
ORDER BY RAND() LIMIT 80"""

TRX="""SELECT CAST(CAS_CASE_ID AS STRING) AS cid, SPEAKER_ROLE,
  SUBSTR(COALESCE(OBFUSCATED_MESSAGE_CONTENT,''),1,350) AS msg, INITIAL_DTTM
FROM `meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT`
WHERE CAS_CASE_ID IN ({ids}) AND SPEAKER_ROLE IN ('USER','REP','AA')
ORDER BY CAS_CASE_ID, INITIAL_DTTM"""

qual={}
for grp in priority:
    drvs=DRIVER_GROUPS[grp]
    procs = get_procs(drvs)
    if not procs:
        qual[grp]={"comments":[],"transcripts":{}}
        print(f"  {grp}... sem processos mapeados")
        continue
    drv_in="'"+"','".join(p.replace("'","''") for p in procs[:30])+"'"
    print(f"  {grp} ({len(procs)} procs)...", end=" ", flush=True)
    try:
        rows=list(bq.query(SQL.format(s=CURR_S,e=CURR_E,drv=drv_in)).result())
        comments=[{"driver":r.driver,"cdu":r.cdu,"sol":r.sol,"sen":r.sen,"canal":r.canal,
                   "office":r.office,"score":int(r.score or 0),"perfil":r.perfil,
                   "motivo":r.mot_det if r.perfil=="detrator" else r.mot_pro,
                   "comment":r.comment,"cid":r.cid} for r in rows]
        det_ids=[c["cid"] for c in comments if c["perfil"]=="detrator" and c["cid"]][:25]
        transcripts={}
        if det_ids:
            ids_str=",".join(det_ids)
            trows=list(bq.query(TRX.format(ids=ids_str)).result())
            for r in trows:
                transcripts.setdefault(r.cid,[]).append(f"[{r.SPEAKER_ROLE}] {r.msg}")
            transcripts={c:"\n".join(v[:6]) for c,v in transcripts.items()}
        qual[grp]={"comments":comments,"transcripts":transcripts}
        print(f"{len(comments)} comentários | {len(transcripts)} transcrições")
    except Exception as e:
        qual[grp]={"comments":[],"transcripts":{}}
        print(f"ERRO: {e}")

out={"lCURR":lCURR,"lPREV":lPREV,"nps_curr":nps_curr,"nps_prev":nps_prev,
     "surv_curr":sB,"surv_prev":sA,"target":NPS_TARGET,
     "waterfall":wf,"top_neg":top_neg,"top_pos":top_pos,
     "qual":qual}
with open("_exec_data.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print("\nSalvo em _exec_data.json")
