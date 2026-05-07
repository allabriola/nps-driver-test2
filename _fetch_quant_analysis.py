#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise quantitativa: busca transcrições de PROMOTORES e DETRATORES,
calcula métricas comparativas e gera conclusões por driver.
Salva em _quant_analysis.json.
"""
import json, time, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
bq = bigquery.Client(project="meli-bi-data")

with open("_exec_data.json", encoding="utf-8") as f:
    EXEC = json.load(f)

DRIVER_GROUPS = list(EXEC.get("qual", {}).keys())

TRX_SQL = """
SELECT CAST(CAS_CASE_ID AS STRING) AS cid,
  SPEAKER_ROLE,
  COALESCE(OBFUSCATED_MESSAGE_CONTENT,'') AS msg,
  INITIAL_DTTM
FROM `meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT`
WHERE CAS_CASE_ID IN ({ids})
  AND SPEAKER_ROLE IN ('USER','REP','AA','BOT')
ORDER BY CAS_CASE_ID, INITIAL_DTTM
"""

def fetch_transcripts_batch(case_ids, batch=800):
    if not case_ids:
        return {}
    result = {}
    for i in range(0, len(case_ids), batch):
        chunk = case_ids[i:i+batch]
        try:
            rows = list(bq.query(TRX_SQL.format(ids=",".join(chunk))).result())
            for r in rows:
                result.setdefault(r.cid, []).append({
                    "role": r.SPEAKER_ROLE,
                    "msg":  r.msg.strip(),
                    "len":  len(r.msg.strip())
                })
            time.sleep(1)
        except Exception as e:
            print(f"  [WARN] {e}")
    return result

# ── Métricas quantitativas de uma transcrição ─────────────────────────
RES_KW   = ["resolvido","solucionado","concluído","problema resolvido","ok, resolvemos",
            "feito isso","encerr","resolvemos","ótimo, finalizamos"]
TRANS_KW = ["transfiro","te transfer","encaminhar para","outro atendente","fale conosco",
            "outro canal","equipe especializada"]
REINCI_KW= ["já abri","já tentei","segunda vez","terceira vez","desde ontem",
            "semanas","meses tentando","abri chamado"]
ESCAL_KW = ["procon","judicial","advogado","reclamação formal","vou processar","ouvidoria"]
MUDAN_KW = ["mudou","antes era","antigamente","novo processo","mudaram","era diferente",
            "antes funcionava"]
BOT_MIN_LEN = 200    # mensagem REP maior que isso é provavelmente automatizada

def calc_metrics(msgs_list):
    """Calcula métricas quantitativas de uma lista de mensagens de uma transcrição."""
    if not msgs_list:
        return {}
    user = [m for m in msgs_list if m["role"] == "USER"]
    rep  = [m for m in msgs_list if m["role"] in ("REP","BOT","AA")]
    full_txt = " ".join(m["msg"].lower() for m in msgs_list)

    has_resolution   = any(k in full_txt for k in RES_KW)
    has_transfer     = any(k in full_txt for k in TRANS_KW)
    has_reincidence  = any(k in full_txt for k in REINCI_KW)
    has_escalation   = any(k in full_txt for k in ESCAL_KW)
    has_proc_change  = any(k in full_txt for k in MUDAN_KW)
    auto_msgs        = sum(1 for m in rep if m["len"] > BOT_MIN_LEN)
    is_bot_heavy     = len(rep) > 0 and auto_msgs / len(rep) >= 0.5

    return {
        "n_msgs_total":   len(msgs_list),
        "n_msgs_user":    len(user),
        "n_msgs_rep":     len(rep),
        "avg_rep_len":    round(sum(m["len"] for m in rep) / len(rep)) if rep else 0,
        "avg_user_len":   round(sum(m["len"] for m in user) / len(user)) if user else 0,
        "rep_ratio":      round(len(rep) / len(msgs_list), 2) if msgs_list else 0,
        "has_resolution": has_resolution,
        "has_transfer":   has_transfer,
        "has_reincidence":has_reincidence,
        "has_escalation": has_escalation,
        "has_proc_change":has_proc_change,
        "is_bot_heavy":   is_bot_heavy,
    }

def aggregate_metrics(all_metrics):
    """Agrega métricas de múltiplas transcrições."""
    n = len(all_metrics)
    if n == 0:
        return {"n": 0}
    def avg(key): return round(sum(m.get(key, 0) for m in all_metrics) / n, 2)
    def pct(key): return round(100 * sum(1 for m in all_metrics if m.get(key)) / n, 1)
    return {
        "n":                  n,
        "avg_msgs_total":     avg("n_msgs_total"),
        "avg_msgs_user":      avg("n_msgs_user"),
        "avg_msgs_rep":       avg("n_msgs_rep"),
        "avg_rep_len":        avg("avg_rep_len"),
        "avg_user_len":       avg("avg_user_len"),
        "avg_rep_ratio":      avg("rep_ratio"),
        "pct_resolved":       pct("has_resolution"),
        "pct_transfer":       pct("has_transfer"),
        "pct_reincidence":    pct("has_reincidence"),
        "pct_escalation":     pct("has_escalation"),
        "pct_proc_change":    pct("has_proc_change"),
        "pct_bot_heavy":      pct("is_bot_heavy"),
    }

# ── Processa cada driver ──────────────────────────────────────────────
result = {}

for grp in DRIVER_GROUPS:
    qual     = EXEC["qual"][grp]
    comments = qual.get("comments", [])
    print(f"\n{'='*55}")
    print(f"Driver: {grp} ({len(comments)} comentários)")

    det_ids = [c["cid"] for c in comments if c.get("perfil") == "detrator" and c.get("cid")][:30]
    pro_ids = [c["cid"] for c in comments if c.get("perfil") == "promotor"  and c.get("cid")][:30]

    print(f"  Detratores: {len(det_ids)} IDs | Promotores: {len(pro_ids)} IDs")

    # Busca transcrições
    time.sleep(1.5)
    det_trx = fetch_transcripts_batch(det_ids)
    time.sleep(1.5)
    pro_trx = fetch_transcripts_batch(pro_ids)

    print(f"  Transcrições det={len(det_trx)} | pro={len(pro_trx)}")

    # Calcula métricas
    det_metrics = [calc_metrics(msgs) for msgs in det_trx.values()]
    pro_metrics = [calc_metrics(msgs) for msgs in pro_trx.values()]

    det_agg = aggregate_metrics(det_metrics)
    pro_agg = aggregate_metrics(pro_metrics)

    # Conclusões comparativas automáticas
    conclusions = []

    def cmp(key, label, higher_is_better=True, threshold=5):
        dv = det_agg.get(key, 0); pv = pro_agg.get(key, 0)
        if dv == 0 and pv == 0: return
        diff = round(dv - pv, 1)
        if abs(diff) < threshold * 0.5: return
        if higher_is_better:
            if diff > 0:
                conclusions.append({"type": "neg", "msg": f"Detratores têm {label} {diff:+.1f} {'pp' if 'pct' in key else ''} maior que promotores — sinal de {'problema' if higher_is_better else 'oportunidade'}"})
            else:
                conclusions.append({"type": "pos", "msg": f"Promotores têm {label} {abs(diff):.1f} {'pp' if 'pct' in key else ''} maior que detratores — diferencial positivo"})
        else:
            if diff > 0:
                conclusions.append({"type": "neg", "msg": f"Detratores têm {label} {diff:+.1f} {'pp' if 'pct' in key else ''} maior que promotores — indica {'mais tempo sem resolução' if 'msg' in key else 'mais complexidade'}"})
            else:
                conclusions.append({"type": "pos", "msg": f"Promotores têm {label} {abs(diff):.1f} {'pp' if 'pct' in key else ''} maior — conversas mais longas com desfecho positivo"})

    cmp("pct_resolved",    "taxa de resolução identificada", higher_is_better=True,  threshold=10)
    cmp("pct_transfer",    "taxa de transferências",          higher_is_better=False, threshold=5)
    cmp("pct_reincidence", "taxa de reincidência",            higher_is_better=False, threshold=5)
    cmp("pct_escalation",  "taxa de escalação legal",         higher_is_better=False, threshold=2)
    cmp("avg_msgs_total",  "volume de mensagens por conversa",higher_is_better=False, threshold=2)
    cmp("avg_rep_len",     "comprimento médio das mensagens do atendente", higher_is_better=True, threshold=30)
    cmp("pct_bot_heavy",   "taxa de resposta automatizada",   higher_is_better=False, threshold=10)
    cmp("pct_proc_change", "menções de mudança de processo",  higher_is_better=False, threshold=5)

    # Diagnóstico das perguntas disparadoras
    trigger_answers = []

    res_gap = pro_agg.get("pct_resolved",0) - det_agg.get("pct_resolved",0)
    if res_gap > 10:
        trigger_answers.append(f"<strong>Oportunidade de atendimento:</strong> Promotores têm {res_gap:.0f}pp mais resoluções confirmadas — resolução no primeiro contato é o principal diferenciador.")
    elif det_agg.get("pct_transfer",0) > 20:
        trigger_answers.append(f"<strong>Oportunidade de atendimento:</strong> {det_agg['pct_transfer']:.0f}% dos detratores passaram por transferência — processo de escalonamento ineficiente.")

    if det_agg.get("pct_reincidence",0) > 15:
        trigger_answers.append(f"<strong>Problema de recorrência:</strong> {det_agg['pct_reincidence']:.0f}% dos detratores já haviam tentado resolver antes — solução de longo prazo necessária.")

    if det_agg.get("pct_proc_change",0) > 10:
        trigger_answers.append(f"<strong>Mudança de processo detectada:</strong> {det_agg['pct_proc_change']:.0f}% das transcrições de detratores mencionam mudança de processo — possível causa da queda.")

    if det_agg.get("pct_bot_heavy",0) > 30:
        trigger_answers.append(f"<strong>Excesso de automação:</strong> {det_agg['pct_bot_heavy']:.0f}% das conversas de detratores têm resposta predominantemente automatizada — falta análise humana do caso.")

    if det_agg.get("avg_msgs_total",0) > pro_agg.get("avg_msgs_total",0) * 1.3:
        ratio = det_agg["avg_msgs_total"] / pro_agg["avg_msgs_total"] if pro_agg.get("avg_msgs_total",0) > 0 else 0
        trigger_answers.append(f"<strong>Complexidade/demora:</strong> Conversas de detratores têm {ratio:.1f}x mais mensagens — indicativo de problema não resolvido na jornada.")

    result[grp] = {
        "det": det_agg, "pro": pro_agg,
        "conclusions": conclusions,
        "trigger_answers": trigger_answers,
        "det_trx_sample": {cid: [m["role"] + ": " + m["msg"][:200] for m in msgs[:5]]
                           for cid, msgs in list(det_trx.items())[:3]},
        "pro_trx_sample": {cid: [m["role"] + ": " + m["msg"][:200] for m in msgs[:3]]
                           for cid, msgs in list(pro_trx.items())[:2]},
    }

    print(f"  Det: res={det_agg.get('pct_resolved')}% transf={det_agg.get('pct_transfer')}% msgs={det_agg.get('avg_msgs_total')}")
    print(f"  Pro: res={pro_agg.get('pct_resolved')}% transf={pro_agg.get('pct_transfer')}% msgs={pro_agg.get('avg_msgs_total')}")
    print(f"  Conclusões: {len(conclusions)} | Respostas disparadoras: {len(trigger_answers)}")

with open("_quant_analysis.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\n\nSalvo em _quant_analysis.json")
