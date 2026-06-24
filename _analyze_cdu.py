#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coleta CDU breakdown S1 vs S2 para todos os 27 drivers,
identifica top CDU de maior aumento/queda, busca transcrições
e prepara dados para análise.
"""
import sys, json, math
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
from collections import defaultdict

client = bigquery.Client(project="meli-bi-data")

# Períodos
S1_START, S1_END = "2026-04-27", "2026-05-03"
S2_START, S2_END = "2026-04-20", "2026-04-26"

# Mapeamento driver → processos (raw process names do BQ)
# Fonte: dd_breakdown.json dimensão P
with open("dd_breakdown.json", encoding="utf-8") as f:
    DD = json.load(f)

def get_procs(driver):
    """Retorna raw process names de um driver (de M1 ou S1 em dd_breakdown)."""
    p = DD.get(driver, {}).get("P", {})
    procs = set()
    for period_data in p.values():
        procs.update(period_data.keys())
    return list(procs)

# Drivers de maior volume (analisar todos, priorizar os grandes)
DRIVERS = [
    "ME Vendedor Seller Dev",
    "Partners",
    "Publicaciones Seller Dev",
    "Post Venta Seller Dev",
    "PCF Vendedor Seller Dev",
    "Experiencia Impositiva Seller Dev",
    "ME Vendedor Mature",
    "Publicaciones Mature",
    "Post Venta Mature",
    "PCF Vendedor Mature",
    "ME Vendedor Meli Pro",
    "Post Venta Meli Pro",
    "Publicaciones Meli Pro",
    "PCF Vendedor Meli Pro",
    "FBM-S Seller Dev",
    "FBM-S Mature",
    "FBM-S Meli Pro",
    "CBT",
    "PDD DS&XD - Vendedor",
    "PDD FBM - Vendedor",
    "PNR ME - Vendedor",
    "PNR MP - Vendedor",
    "Otros CV",
    "Experiencia Impositiva Mature",
    "Experiencia Impositiva Meli Pro",
    "PDD Fotos - Vendedor",
    "PDD MP,FLEX & CBT - Vendedor",
]

def nps(p, d, s):
    return round(100.0*(p-d)/s, 2) if s > 0 else None

def query_cdu_period(driver, date_start, date_end):
    """Query CDU × solução para um driver em um período."""
    procs = get_procs(driver)
    if not procs:
        return []
    procs_in = "'" + "','".join(p.replace("'","''") for p in procs[:20]) + "'"
    q = f"""
    SELECT
      COALESCE(CDU, 'Sem CDU')         AS cdu,
      COALESCE(CX_SOL_NAME, 'Sem solucao') AS solucao,
      SUM(PROMOTER)  AS p,
      SUM(DETRACTOR) AS d,
      COUNT(*)       AS s
    FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
    WHERE SIT_SITE_ID = 'MLB'
      AND SURVEY_CENTER = 'BR'
      AND SURVEY_DATE_SURVEY BETWEEN '{date_start}' AND '{date_end}'
      AND PRO_PROCESS_NAME IN ({procs_in})
    GROUP BY cdu, solucao
    HAVING COUNT(*) >= 5
    ORDER BY COUNT(*) DESC
    LIMIT 50
    """
    rows = list(client.query(q).result())
    return [{"cdu": r.cdu, "sol": r.solucao,
             "p": int(r.p or 0), "d": int(r.d or 0), "s": int(r.s or 0),
             "nps": nps(int(r.p or 0), int(r.d or 0), int(r.s or 0))} for r in rows]

def top_changes(s1_data, s2_data, min_surveys=10):
    """Compara S1 vs S2 por (cdu, solucao) e retorna top aumento/queda."""
    s2_map = {(r["cdu"], r["sol"]): r for r in s2_data}
    changes = []
    for r in s1_data:
        key = (r["cdu"], r["sol"])
        prev = s2_map.get(key)
        if prev and r["nps"] is not None and prev["nps"] is not None and r["s"] >= min_surveys:
            delta = round(r["nps"] - prev["nps"], 2)
            changes.append({**r, "nps_s2": prev["nps"], "delta": delta, "key": key})
    changes.sort(key=lambda x: x["delta"])
    worst = [c for c in changes if c["delta"] < 0][:3]
    best  = [c for c in changes if c["delta"] > 0][-3:][::-1]
    return worst, best

print("=" * 70)
print("CDU BREAKDOWN — S1 (27/abr-03/mai) vs S2 (20/abr-26/abr)")
print("=" * 70)

results = {}
for drv in DRIVERS:
    print(f"\n>>> {drv}")
    try:
        s1 = query_cdu_period(drv, S1_START, S1_END)
        s2 = query_cdu_period(drv, S2_START, S2_END)
        worst, best = top_changes(s1, s2)
        results[drv] = {"s1": s1, "s2": s2, "worst": worst, "best": best}
        if worst:
            print(f"  QUEDA: {worst[0]['cdu']} / {worst[0]['sol'][:50]}"
                  f"  NPS {worst[0]['nps_s2']:.1f}→{worst[0]['nps']:.1f} (Δ{worst[0]['delta']:+.2f}pp, {worst[0]['s']} surveys)")
        if best:
            print(f"  ALTA:  {best[0]['cdu']} / {best[0]['sol'][:50]}"
                  f"  NPS {best[0]['nps_s2']:.1f}→{best[0]['nps']:.1f} (Δ{best[0]['delta']:+.2f}pp, {best[0]['s']} surveys)")
    except Exception as e:
        print(f"  ERRO: {e}")
        results[drv] = {"error": str(e)}

with open("_cdu_analysis.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n\nSalvo em _cdu_analysis.json")
