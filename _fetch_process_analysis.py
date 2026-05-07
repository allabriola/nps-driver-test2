#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Para cada grupo de driver identifica os processos mais impactantes (positivo e
negativo), busca CDU/Solução/Seniority/Motivos no BQ e salva em _process_analysis.json.
"""
import re, json, time, sys
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
bq = bigquery.Client(project="meli-bi-data")

# ── Carrega dados base ────────────────────────────────────────────────
with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)
MONTH_LABELS = ns['MONTH_LABELS']

with open('dd_breakdown.json', encoding='utf-8') as f:
    DD = json.load(f)
with open('_mai_breakdown.json', encoding='utf-8') as f:
    DD_MAI = json.load(f)

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

MAI_START, MAI_END = "2026-05-01", "2026-05-06"

# ── Helper: NPS ───────────────────────────────────────────────────────
def nps(p, d, s): return round(100.0*(p-d)/s, 2) if s > 0 else None

def agg_dim(drvs, dim, period, source):
    result = {}
    for drv in drvs:
        for key, v in source.get(drv, {}).get(dim, {}).get(period, {}).items():
            if not key or key.startswith("(sem"): continue
            r = result.setdefault(key, {"p":0,"d":0,"s":0})
            r["p"] += v.get("p",0); r["d"] += v.get("d",0); r["s"] += v.get("s",0)
    for v in result.values():
        v["nps"] = nps(v["p"],v["d"],v["s"])
    return result

# ── Para cada grupo: encontra top positivo e negativo ────────────────
def find_top_processes(grp, drvs):
    """Retorna (top_pos_proc, top_neg_proc) com maior/menor NPS em Maio."""
    p_mai = agg_dim(drvs, "P", "Mai", DD_MAI)
    p_abr = agg_dim(drvs, "P", "M1", DD)    # M1 dd = Abr

    if not p_mai:
        return None, None

    s_tot_mai = sum(v["s"] for v in p_mai.values())
    min_share  = 0.05   # processo deve ter >= 5% do volume

    candidates = []
    for proc, v_mai in p_mai.items():
        share = v_mai["s"] / s_tot_mai if s_tot_mai else 0
        if share < min_share: continue
        v_abr = p_abr.get(proc, {})
        nps_m = v_mai["nps"]
        nps_a = v_abr.get("nps")
        delta = round(nps_m - nps_a, 2) if nps_m is not None and nps_a is not None else 0
        # Contribuição = share_mai * (nps_mai - nps_abr)
        contrib = round(share * delta, 3) if delta else 0
        candidates.append({"proc": proc, "nps_mai": nps_m, "nps_abr": nps_a,
                            "delta": delta, "contrib": contrib, "s_mai": v_mai["s"],
                            "share": round(share*100, 1)})

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: x["contrib"], reverse=True)
    top_pos = candidates[0]  if candidates[0]["contrib"]  > 0  else None
    top_neg = candidates[-1] if candidates[-1]["contrib"] < 0  else None

    # Fallback: se nenhum contrib calculável, pega maior e menor NPS
    if top_pos is None:
        top_pos = max(candidates, key=lambda x: x["nps_mai"] or -999)
    if top_neg is None:
        top_neg = min(candidates, key=lambda x: x["nps_mai"] or 999)

    return top_pos, top_neg

# ── BQ: breakdown CDU/Sol/Seniority/Motivos por processo ─────────────
DETAIL_SQL = """
SELECT
  COALESCE(CDU,'N/I')                          AS cdu,
  COALESCE(CX_SOL_NAME,'N/I')                 AS sol,
  COALESCE(ANTIGUEDAD_REP,'N/I')              AS seniority,
  COALESCE(RES_DETRACTION_REASON,'N/I')       AS det_reason,
  COALESCE(RES_PROMOTION_REASON,'N/I')        AS pro_reason,
  SUM(PROMOTER) AS p, SUM(DETRACTOR) AS d, COUNT(*) AS s,
  ARRAY_AGG(
    NULLIF(TRIM(COMMENTS),'') IGNORE NULLS
    ORDER BY LENGTH(COALESCE(COMMENTS,'')) DESC
    LIMIT 3
  ) AS sample_comments,
  ARRAY_AGG(CAST(CAS_CASE_ID AS STRING) IGNORE NULLS LIMIT 5) AS case_ids
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID='MLB' AND SURVEY_CENTER='BR'
  AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
  AND PRO_PROCESS_NAME = '{proc}'
  AND (PROMOTER=1 OR DETRACTOR=1)
GROUP BY cdu, sol, seniority, det_reason, pro_reason
HAVING COUNT(*) >= 2
ORDER BY s DESC LIMIT 300
"""

TRX_SQL = """
SELECT CAST(CAS_CASE_ID AS STRING) AS cid,
  SPEAKER_ROLE,
  SUBSTR(COALESCE(OBFUSCATED_MESSAGE_CONTENT,''),1,300) AS msg,
  INITIAL_DTTM
FROM `meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT`
WHERE CAS_CASE_ID IN ({ids})
  AND SPEAKER_ROLE IN ('USER','REP','AA')
ORDER BY CAS_CASE_ID, INITIAL_DTTM
"""

def fetch_process_detail(proc, start, end):
    sql = DETAIL_SQL.format(start=start, end=end,
                             proc=proc.replace("'","''"))
    try:
        rows = list(bq.query(sql).result())
        return [{"cdu": r.cdu, "sol": r.sol, "seniority": r.seniority,
                 "det_reason": r.det_reason, "pro_reason": r.pro_reason,
                 "p": int(r.p or 0), "d": int(r.d or 0), "s": int(r.s or 0),
                 "comments": [c for c in (r.sample_comments or []) if c],
                 "case_ids": list(r.case_ids or [])} for r in rows]
    except Exception as e:
        print(f"    [WARN] {e}")
        return []

def fetch_transcripts(case_ids, limit=15):
    if not case_ids:
        return {}
    ids_str = ",".join(case_ids[:limit])
    try:
        rows = list(bq.query(TRX_SQL.format(ids=ids_str)).result())
        result = {}
        for r in rows:
            result.setdefault(r.cid, []).append(f"[{r.SPEAKER_ROLE}] {r.msg}")
        return {c: "\n".join(v[:6]) for c,v in result.items()}
    except Exception as e:
        print(f"    [WARN TRX] {e}")
        return {}

def aggregate_detail(rows):
    """Agrega linhas do BQ em dimensões por CDU/Sol/Seniority/Motivos."""
    cdu   = {}; sol = {}; sen = {}; det_r = {}; pro_r = {}
    all_case_ids = []; all_comments = []
    tp = td = ts = 0
    for r in rows:
        tp += r["p"]; td += r["d"]; ts += r["s"]
        for dim, key in [(cdu,r["cdu"]),(sol,r["sol"]),(sen,r["seniority"])]:
            e = dim.setdefault(key, {"p":0,"d":0,"s":0})
            e["p"] += r["p"]; e["d"] += r["d"]; e["s"] += r["s"]
        if r["det_reason"] != "N/I":
            det_r[r["det_reason"]] = det_r.get(r["det_reason"],0) + r["d"]
        if r["pro_reason"] != "N/I":
            pro_r[r["pro_reason"]] = pro_r.get(r["pro_reason"],0) + r["p"]
        all_case_ids.extend(r["case_ids"])
        all_comments.extend(r["comments"])
    for dim in [cdu, sol, sen]:
        for v in dim.values():
            v["nps"] = nps(v["p"],v["d"],v["s"])
    return {"cdu": cdu, "sol": sol, "seniority": sen,
            "det_reasons": det_r, "pro_reasons": pro_r,
            "case_ids": list(set(all_case_ids))[:20],
            "comments": list(set(all_comments))[:10],
            "tp": tp, "td": td, "ts": ts,
            "nps_total": nps(tp,td,ts)}

# ── MAIN ──────────────────────────────────────────────────────────────
result = {}
for grp, drvs in DRIVER_GROUPS.items():
    print(f"\n{'='*55}")
    print(f"Driver: {grp}")
    top_pos, top_neg = find_top_processes(grp, drvs)

    grp_data = {}
    for role, proc_info in [("top_pos", top_pos), ("top_neg", top_neg)]:
        if proc_info is None:
            grp_data[role] = None
            continue
        proc = proc_info["proc"]
        print(f"  [{role}] {proc[:50]} — NPS Mai={proc_info['nps_mai']:.1f}% Δ={proc_info['delta']:+.1f}pp share={proc_info['share']:.1f}%")
        time.sleep(2)
        rows = fetch_process_detail(proc, MAI_START, MAI_END)
        print(f"    {len(rows)} combinações CDU/Sol/Sen no BQ")
        agg  = aggregate_detail(rows)
        print(f"    NPS total={agg['nps_total']:.1f}% surv={agg['ts']:,}")
        # Transcripts para detratores do processo
        det_ids = []
        for r in rows:
            if r["d"] > 0:
                det_ids.extend(r["case_ids"][:3])
        time.sleep(2)
        trxs = fetch_transcripts(list(set(det_ids))[:12])
        print(f"    {len(trxs)} transcrições")
        grp_data[role] = {**proc_info, "detail": agg, "transcripts": trxs}

    result[grp] = grp_data

with open("_process_analysis.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\n\nSalvo em _process_analysis.json")
