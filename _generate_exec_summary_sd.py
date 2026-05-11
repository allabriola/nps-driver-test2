#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera Resumo Executivo NPS — Seller Dev BR (6 drivers: Exp.Impositiva/ME Vendedor/
PCF Vendedor/Post Venta/Publicaciones/Partners).
Saída: _exec_summary_sd.html  (embutido por generate_html_seller_dev.py)
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
import anthropic

bq_client = bigquery.Client(project="meli-bi-data")

import os
_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not _api_key:
    print("ERRO: variável ANTHROPIC_API_KEY não definida.")
    print("  Execute:  $env:ANTHROPIC_API_KEY='sk-ant-...'  (PowerShell)")
    sys.exit(1)
ai_client = anthropic.Anthropic(api_key=_api_key)

# ══════════════════════════════════════════════════════════════════════
# 1. CARREGA DADOS
# ══════════════════════════════════════════════════════════════════════
with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    _src = f.read()
_stop = re.search(r'# SECTION 3', _src)
_ns = {}
exec(compile(_src[:_stop.start()], 'g', 'exec'), _ns)

MONTH_LABELS = _ns['MONTH_LABELS']
DRIVER_TARGETS = _ns['DRIVER_TARGETS']
NPS_TARGET = _ns['NPS_TARGET']
monthly_history = _ns['monthly_history']

# Sobrescreve com dados frescos de _monthly_result.json
if os.path.exists("_monthly_result.json"):
    with open("_monthly_result.json", encoding="utf-8") as _f:
        _mr = json.load(_f)
    for _lbl, _drv_map in _mr.items():
        for _drv, _vals in _drv_map.items():
            if _drv not in monthly_history:
                monthly_history[_drv] = {}
            monthly_history[_drv][_lbl] = tuple(_vals)

# Apenas Seller Dev + Partners
DRIVER_GROUPS = {
    "Exp. Impositiva":  ["Experiencia Impositiva Seller Dev"],
    "ME Vendedor":      ["ME Vendedor Seller Dev"],
    "PCF Vendedor":     ["PCF Vendedor Seller Dev"],
    "Post Venta":       ["Post Venta Seller Dev"],
    "Publicaciones":    ["Publicaciones Seller Dev"],
    "Partners":         ["Partners"],
}
ALL_DRIVERS = [d for drvs in DRIVER_GROUPS.values() for d in drvs]

# Análise: último mês fechado vs anterior
lCURR = MONTH_LABELS[-2]   # Abr
lPREV = MONTH_LABELS[-3]   # Mar

DATE_RANGES = {
    "Jan": ("2026-01-01", "2026-01-31"),
    "Fev": ("2026-02-01", "2026-02-28"),
    "Mar": ("2026-03-01", "2026-03-31"),
    "Abr": ("2026-04-01", "2026-04-30"),
    "Mai": ("2026-05-01", "2026-05-31"),
}
CURR_START, CURR_END = DATE_RANGES[lCURR]
PREV_START, PREV_END = DATE_RANGES[lPREV]

# ══════════════════════════════════════════════════════════════════════
# 2. CÁLCULOS QUANTITATIVOS
# ══════════════════════════════════════════════════════════════════════
def nps_raw(p, d, s):
    return round(100.0*(p-d)/s, 2) if s > 0 else None

def grp_nps(label, drvs):
    p   = sum(monthly_history[d].get(label,(0,0,0))[0] for d in drvs if d in monthly_history)
    det = sum(monthly_history[d].get(label,(0,0,0))[1] for d in drvs if d in monthly_history)
    s   = sum(monthly_history[d].get(label,(0,0,0))[2] for d in drvs if d in monthly_history)
    return nps_raw(p, det, s), s

def grp_target(drvs):
    num = sum(monthly_history[d].get(lCURR,(0,0,0))[2] * DRIVER_TARGETS.get(d, NPS_TARGET)
              for d in drvs if d in monthly_history)
    den = sum(monthly_history[d].get(lCURR,(0,0,0))[2] for d in drvs if d in monthly_history)
    return round(num/den, 2) if den else NPS_TARGET

def cons_nps(label):
    p   = sum(monthly_history[d].get(label,(0,0,0))[0] for d in ALL_DRIVERS)
    det = sum(monthly_history[d].get(label,(0,0,0))[1] for d in ALL_DRIVERS)
    s   = sum(monthly_history[d].get(label,(0,0,0))[2] for d in ALL_DRIVERS)
    return nps_raw(p, det, s), s

nps_curr, surv_curr = cons_nps(lCURR)
nps_prev, surv_prev = cons_nps(lPREV)
delta_mm  = round(nps_curr - nps_prev, 2)  if nps_curr and nps_prev else None
delta_tgt = round(nps_curr - NPS_TARGET, 2) if nps_curr else None

sA_tot = sum(monthly_history[d].get(lPREV,(0,0,0))[2] for d in ALL_DRIVERS)
sB_tot = sum(monthly_history[d].get(lCURR,(0,0,0))[2] for d in ALL_DRIVERS)

waterfall_mm = {}
for grp, drvs in DRIVER_GROUPS.items():
    pA = sum(monthly_history[d].get(lPREV,(0,0,0))[0] for d in drvs if d in monthly_history)
    dA = sum(monthly_history[d].get(lPREV,(0,0,0))[1] for d in drvs if d in monthly_history)
    sA = sum(monthly_history[d].get(lPREV,(0,0,0))[2] for d in drvs if d in monthly_history)
    pB = sum(monthly_history[d].get(lCURR,(0,0,0))[0] for d in drvs if d in monthly_history)
    dB = sum(monthly_history[d].get(lCURR,(0,0,0))[1] for d in drvs if d in monthly_history)
    sB = sum(monthly_history[d].get(lCURR,(0,0,0))[2] for d in drvs if d in monthly_history)
    na = nps_raw(pA, dA, sA) or 0
    nb = nps_raw(pB, dB, sB) or 0
    sha = sA / sA_tot if sA_tot else 0
    shb = sB / sB_tot if sB_tot else 0
    neto = round(sha * (nb - na), 2)
    mix  = round((shb - sha) * (nb - (nps_curr or 0)), 2)
    g_nps_curr, g_surv = grp_nps(lCURR, drvs)
    g_nps_prev, _      = grp_nps(lPREV, drvs)
    g_tgt = grp_target(drvs)
    waterfall_mm[grp] = {
        "var": round(neto + mix, 2),
        "nps_curr": g_nps_curr, "nps_prev": g_nps_prev,
        "surv": g_surv, "target": g_tgt,
        "delta_tgt": round(g_nps_curr - g_tgt, 2) if g_nps_curr is not None else None,
    }

sorted_groups = sorted(waterfall_mm.items(), key=lambda x: x[1]["var"])
top_neg = sorted_groups[:3]
top_pos = sorted_groups[-3:][::-1]

print(f"SD Consolidado: {lPREV} {nps_prev:.2f}% → {lCURR} {nps_curr:.2f}%  Δ={delta_mm:+.2f}pp vs target={delta_tgt:+.2f}pp")
print(f"Top negativo: {', '.join(g for g,_ in top_neg)}")
print(f"Top positivo: {', '.join(g for g,_ in top_pos)}")

# ══════════════════════════════════════════════════════════════════════
# 3. QUERY COMENTÁRIOS
# ══════════════════════════════════════════════════════════════════════
COMMENT_SQL = """
SELECT
  PRO_PROCESS_NAME                                  AS driver,
  COALESCE(CDU, 'N/I')                             AS cdu,
  COALESCE(CX_SOL_NAME, 'N/I')                    AS solucao,
  COALESCE(ANTIGUEDAD_REP, 'N/I')                 AS seniority,
  COALESCE(SURVEY_CHANNEL, 'N/I')                 AS canal,
  COALESCE(USER_OFFICE, 'N/I')                    AS oficina,
  NPS                                               AS score,
  CASE WHEN PROMOTER=1 THEN 'promotor'
       WHEN DETRACTOR=1 THEN 'detrator'
       ELSE 'neutro' END                            AS perfil,
  COALESCE(RES_DETRACTION_REASON, '')              AS motivo_detrator,
  COALESCE(RES_PROMOTION_REASON, '')               AS motivo_promotor,
  NULLIF(TRIM(COMMENTS), '')                       AS comentario,
  CAST(CAS_CASE_ID AS STRING)                      AS case_id
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID = 'MLB'
  AND SURVEY_CENTER = 'BR'
  AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
  AND PRO_PROCESS_NAME IN ({drivers_in})
  AND (PROMOTER = 1 OR DETRACTOR = 1)
ORDER BY RAND()
LIMIT {lim}
"""

TRANSCRIPT_SQL = """
SELECT
  CAST(CAS_CASE_ID AS STRING)            AS case_id,
  SPEAKER_ROLE,
  SUBSTR(COALESCE(OBFUSCATED_MESSAGE_CONTENT,''), 1, 400) AS msg,
  INITIAL_DTTM
FROM `meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT`
WHERE CAS_CASE_ID IN ({ids})
  AND SPEAKER_ROLE IN ('USER','REP','AA')
ORDER BY CAS_CASE_ID, INITIAL_DTTM
"""

def drivers_in_sql(drvs):
    return "'" + "','".join(d.replace("'","''") for d in drvs) + "'"

def fetch_comments(drvs, start, end, lim=60):
    sql = COMMENT_SQL.format(start=start, end=end, drivers_in=drivers_in_sql(drvs), lim=lim)
    try:
        rows = list(bq_client.query(sql).result())
        return [{"driver": r.driver, "cdu": r.cdu, "solucao": r.solucao,
                 "seniority": r.seniority, "canal": r.canal, "oficina": r.oficina,
                 "score": int(r.score or 0), "perfil": r.perfil,
                 "motivo": r.motivo_detrator if r.perfil == "detrator" else r.motivo_promotor,
                 "comentario": r.comentario, "case_id": r.case_id} for r in rows]
    except Exception as e:
        print(f"  [WARN] comments: {e}")
        return []

def fetch_transcripts(case_ids, batch=800):
    if not case_ids:
        return {}
    result = {}
    for i in range(0, len(case_ids), batch):
        chunk = case_ids[i:i+batch]
        sql = TRANSCRIPT_SQL.format(ids=",".join(chunk))
        try:
            rows = list(bq_client.query(sql).result())
            for r in rows:
                cid = r.case_id
                if cid not in result:
                    result[cid] = []
                result[cid].append(f"[{r.SPEAKER_ROLE}] {r.msg}")
        except Exception as e:
            print(f"  [WARN] transcripts chunk {i}: {e}")
    return {cid: "\n".join(msgs[:8]) for cid, msgs in result.items()}

priority_groups = [g for g, _ in top_neg] + [g for g, _ in top_pos if g not in [g2 for g2,_ in top_neg]]

qual_data = {}
for grp in priority_groups:
    drvs = DRIVER_GROUPS[grp]
    print(f"  Buscando comentários: {grp} ({lCURR})...")
    comments = fetch_comments(drvs, CURR_START, CURR_END, lim=60)
    detrator_ids = [c["case_id"] for c in comments if c["perfil"] == "detrator" and c["case_id"]][:30]
    promotor_ids = [c["case_id"] for c in comments if c["perfil"] == "promotor"  and c["case_id"]][:20]
    print(f"    {len(comments)} registros | {len(detrator_ids)} detratores | {len(promotor_ids)} promotores")
    transcripts = fetch_transcripts(detrator_ids[:20] + promotor_ids[:10])
    print(f"    {len(transcripts)} transcrições")
    qual_data[grp] = {"comments": comments, "transcripts": transcripts}

# ══════════════════════════════════════════════════════════════════════
# 4. CONTEXTO PARA O CLAUDE
# ══════════════════════════════════════════════════════════════════════
def build_context():
    lines = []
    lines.append("=== CONTEXTO QUANTITATIVO — Seller Dev + Partners ===")
    lines.append(f"Período análise: {lPREV} vs {lCURR}")
    lines.append(f"NPS {lPREV}: {nps_prev:.2f}%  ({surv_prev:,} pesquisas)")
    lines.append(f"NPS {lCURR}: {nps_curr:.2f}%  ({surv_curr:,} pesquisas)")
    lines.append(f"Variação M/M: {delta_mm:+.2f}pp")
    lines.append(f"Target: {NPS_TARGET:.2f}%   Gap vs target: {delta_tgt:+.2f}pp")
    lines.append("")
    lines.append("--- CASCATA MoM (contribuição por driver) ---")
    for g, v in sorted_groups:
        lines.append(f"  {g:<22} var={v['var']:+.2f}pp | NPS {lPREV}={v['nps_prev']:.1f}% → {lCURR}={v['nps_curr']:.1f}% | surv={v['surv']:,} | tgt={v['target']:.1f}% (gap={v['delta_tgt']:+.1f}pp)")
    lines.append("")
    lines.append("=== CONTEXTO QUALITATIVO ===")
    for grp in priority_groups:
        data = qual_data.get(grp, {})
        comments = data.get("comments", [])
        transcripts = data.get("transcripts", {})
        lines.append(f"\n[DRIVER: {grp}]")
        if comments:
            lines.append("Comentários NPS Lineal (amostra):")
            for c in comments[:25]:
                if c.get("comentario"):
                    tag = "DETRATOR" if c["perfil"] == "detrator" else "PROMOTOR"
                    motivo = c.get("motivo","") or ""
                    lines.append(f"  [{tag}|{c['cdu'][:35]}|{c['solucao'][:30]}|{c['canal']}|{c['seniority']}|{c['oficina'][:20]}] motivo={motivo[:40]} | {c['comentario'][:200]}")
            cdu_counts = {}
            for c in comments:
                k = (c["perfil"], c["cdu"])
                cdu_counts[k] = cdu_counts.get(k, 0) + 1
            lines.append("CDU mais frequentes (detratores):")
            for (pf, cdu), cnt in sorted(cdu_counts.items(), key=lambda x: -x[1])[:6]:
                if pf == "detrator":
                    lines.append(f"  {cdu[:50]}: {cnt} casos")
        if transcripts:
            lines.append(f"Transcrições (amostra de {min(4,len(transcripts))} casos):")
            for cid, txt in list(transcripts.items())[:4]:
                lines.append(f"  --- Caso {cid} ---")
                lines.append(f"  {txt[:600]}")
    return "\n".join(lines)

context_text = build_context()

# ══════════════════════════════════════════════════════════════════════
# 5. CLAUDE API
# ══════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """Você é um analista sênior de Customer Experience (CX), NPS e Qualidade Operacional.
Sua saída DEVE ser exclusivamente HTML (sem markdown, sem ```html, sem texto fora das tags).
Use as classes CSS disponíveis no dashboard: exec-section, exec-title, exec-body, exec-card,
exec-card-pos, exec-card-neg, exec-card-warn, exec-bullet, exec-label, chip chip-pos chip-neg chip-neu.
Linguagem: português brasileiro, tom executivo, objetivo e acionável."""

USER_PROMPT = f"""Analise os dados abaixo e gere um Resumo Executivo NPS em HTML.
Escopo: apenas os 6 drivers Seller Dev (Exp. Impositiva SD, ME Vendedor SD, PCF Vendedor SD,
Post Venta SD, Publicaciones SD) e Partners. Não mencione outros segmentos (Mature, Meli Pro, FBM-S).

{context_text}

FORMATO OBRIGATÓRIO (em HTML com as classes CSS do sistema):

<div class="exec-section">
  <div class="exec-title">📋 Resumo Executivo — {lCURR} (Seller Dev + Partners)</div>
  <div class="exec-body">
    [2 parágrafos executivos: o que aconteceu + por que + impacto operacional]
  </div>
</div>

<div class="exec-section">
  <div class="exec-title">🟢 Principais Alavancas de Alta</div>
  [3 exec-card exec-card-pos com: Driver | Motivo | Evidência de comentários]
</div>

<div class="exec-section">
  <div class="exec-title">🔴 Principais Causas de Queda</div>
  [3 exec-card exec-card-neg com: Driver | Motivo | Evidência de comentários/transcrições]
</div>

<div class="exec-section">
  <div class="exec-title">⚠️ Drivers Fora do Target</div>
  [Lista dos drivers SD com gap vs target, causa raiz identificada]
</div>

<div class="exec-section">
  <div class="exec-title">💡 Recomendações Executivas</div>
  [Curto prazo | Médio prazo | Ajuste estrutural — máximo 6 bullets acionáveis]
</div>

REGRAS:
- Não assumir causalidade sem evidência em comentários/transcrições
- Sinalizar quando for hipótese
- Separar: Sintoma → Driver → Causa Raiz → Evidência → Ação
- Linguagem executiva, sem excesso técnico"""

print("\nChamando Claude API...")
resp = ai_client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": USER_PROMPT}]
)
summary_html = resp.content[0].text.strip()
print(f"Resumo gerado: {len(summary_html)} chars")

# ══════════════════════════════════════════════════════════════════════
# 6. SALVA
# ══════════════════════════════════════════════════════════════════════
with open("_exec_summary_sd.html", "w", encoding="utf-8") as f:
    f.write(summary_html)
print("Salvo em _exec_summary_sd.html")
