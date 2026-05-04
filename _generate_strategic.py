#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera strategic summary (best/worst driver) para WoW e MoM."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open("_cdu_analysis.json", encoding="utf-8") as f:
    cdu_data = json.load(f)
with open("_transcripts_by_driver.json", encoding="utf-8") as f:
    transcripts = json.load(f)
with open("_commerce_raw.json", encoding="utf-8") as f:
    comments_raw = json.load(f)
with open("dd_breakdown.json", encoding="utf-8") as f:
    dd = json.load(f)

def nps(p, d, s):
    return round(100*(p-d)/s, 2) if s > 0 else None

def canal_bk(driver, pa, pb):
    c = dd.get(driver, {}).get("C", {})
    dA = c.get(pa, {}); dB = c.get(pb, {})
    totB = sum(v.get("s", 0) for v in dB.values()) or 1
    result = []
    for k in set(list(dA.keys()) + list(dB.keys())):
        a = dA.get(k, {"nps": None, "s": 0})
        b = dB.get(k, {"nps": None, "s": 0})
        na, nb = a.get("nps"), b.get("nps")
        result.append({
            "k": k, "nps_b": nb,
            "delta": round(nb-na, 1) if na and nb else None,
            "share": round(b.get("s", 0)/totB*100, 1),
            "s": b.get("s", 0)
        })
    return [r for r in sorted(result, key=lambda x: -(x["s"] or 0)) if r["s"] >= 5][:4]

def senior_bk(driver, pa, pb):
    s = dd.get(driver, {}).get("Sr", {})
    out = {}
    for lvl in ["Expert", "Newbie"]:
        a = s.get(pa, {}).get(lvl, {"nps": None, "s": 0})
        b = s.get(pb, {}).get(lvl, {"nps": None, "s": 0})
        na, nb = a.get("nps"), b.get("nps")
        d = round(nb-na, 1) if na and nb else None
        sign = "+" if d and d >= 0 else ""
        out[lvl] = f"NPS {nb:.1f}% ({sign}{d}pp, {b.get('s',0)} surv)" if nb else "Sem dados"
    return out

def fmt_canal(rows):
    return " | ".join(
        f"{r['k']}: {r['nps_b']:.1f}% ({('+' if r['delta'] and r['delta']>=0 else '')}{r['delta'] or '-'}pp, {r['share']:.0f}% vol)"
        for r in rows if r.get("nps_b")
    )

def get_cdu(data_dict, key, index=0):
    items = data_dict.get(key, [])
    if not items or index >= len(items):
        return {"cdu": "", "sol": "", "delta": 0}
    item = items[index]
    return {"cdu": item.get("cdu", ""), "sol": item.get("sol", ""), "delta": item.get("delta", 0)}

def extract_comments(driver_key, tipo):
    data = comments_raw.get(driver_key, {})
    items = data.get("detractors", []) if tipo == "det" else data.get("promoters", [])
    return [f"[{c.get('senior','?')}] {c.get('comment','')[:100]}"
            for c in items[:4] if c.get("comment", "")]

# ── WoW ──────────────────────────────────────────────────────────────────────
me_c_wow  = canal_bk("ME Vendedor Seller Dev", "S2", "S1")
me_s_wow  = senior_bk("ME Vendedor Seller Dev", "S2", "S1")
pub_c_wow = canal_bk("Publicaciones Seller Dev", "S2", "S1")
pub_s_wow = senior_bk("Publicaciones Seller Dev", "S2", "S1")

# ── MoM ──────────────────────────────────────────────────────────────────────
me_c_mom  = canal_bk("ME Vendedor Seller Dev", "M2", "M1")
me_s_mom  = senior_bk("ME Vendedor Seller Dev", "M2", "M1")
pub_c_mom = canal_bk("Publicaciones Seller Dev", "M2", "M1")
pub_s_mom = senior_bk("Publicaciones Seller Dev", "M2", "M1")

strategic = {
    "sem": {
        "periodo": "WoW: S2 (20/abr-26/abr) vs S1 (27/abr-03/mai)",
        "best_driver": "ME Vendedor Seller Dev",
        "worst_driver": "Publicaciones Seller Dev",
        "best": {
            "driver": "ME Vendedor Seller Dev",
            "nps_a": 69.27, "nps_b": 72.68, "delta": 3.41, "contribution": 1.249,
            "top_process": "Reputação ME",
            "process_nps_a": 82.95, "process_nps_b": 85.54, "process_delta": 2.59,
            "process_impact": 1.468, "process_share": 46.6,
            "top_cdu_queda": get_cdu(cdu_data.get("ME Vendedor Seller Dev", {}), "worst"),
            "top_cdu_alta":  get_cdu(cdu_data.get("ME Vendedor Seller Dev", {}), "best"),
            "canal": fmt_canal(me_c_wow),
            "senioridade": me_s_wow,
            "oportunidade": (
                "Educacao proativa em categorias especiais de envio gerou +53pp no CDU correspondente. "
                "Canal Chat (+3.1pp) performa acima da media — boas praticas replicaveis. "
                "Newbie cresceu +5.2pp WoW — metodologia de desenvolvimento escalavel. "
                "Logistica Places com NPS 87.5%: entender mudanca operacional que sustenta o resultado."
            ),
            "conclusao": (
                "Reputacao ME e o principal motor do driver, sustentando NPS 85.5% com ganho de +2.6pp WoW. "
                "CDU 'Envio pelo V: categorias especiais' subiu +53pp quando rep explica regras de custo proativamente. "
                "Risco: CDU 'Desativar ME' caiu -30pp — restricao sistemica sem solucao para o agente, "
                "gerando detratores estruturais independente da qualidade do atendimento."
            ),
            "voc_pro": extract_comments("ME Vendedor Seller Dev", "pro"),
            "voc_det": extract_comments("ME Vendedor Seller Dev", "det"),
            "gerado_em": "2026-05-04"
        },
        "worst": {
            "driver": "Publicaciones Seller Dev",
            "nps_a": 62.89, "nps_b": 56.67, "delta": -6.22, "contribution": -0.781,
            "top_process": "Denuncia de usuario",
            "process_nps_a": 81.2, "process_nps_b": 29.4, "process_delta": -51.8,
            "process_impact": -1.457, "process_share": 3.0,
            "top_cdu_queda": get_cdu(cdu_data.get("Publicaciones Seller Dev", {}), "worst"),
            "top_cdu_alta":  get_cdu(cdu_data.get("Publicaciones Seller Dev", {}), "best"),
            "canal": fmt_canal(pub_c_wow),
            "senioridade": pub_s_wow,
            "oportunidade": (
                "Gestao de Publicacao (+13.9pp WoW) mostra que orientacao clara de publicacao melhora NPS. "
                "PR-Propiedad Intelectual (+8.5pp) — fluxo de rollback funcionando bem. "
                "Afiliados ML concentra 40% do volume: criar SLA de moderacao de videos resolvia o maior gargalo."
            ),
            "conclusao": (
                "Denuncia de usuario colapsou -51.8pp WoW (NPS 81% para 29%) em apenas 17 surveys. "
                "Potenciar Ventas caiu -8.5pp: CDU Clips/Potencializador sem resposta adequada do agente. "
                "Afiliados ML (40% vol) apresenta instabilidade estrutural: metricas de comissao opacas "
                "e campanhas de video sumindo sem SLA visivel. VoC dominante: nao resolvem, redundancia. "
                "Acao urgente: FAQ de elegibilidade + notificacao de moderacao com prazo no app."
            ),
            "voc_pro": extract_comments("Publicaciones Seller Dev", "pro"),
            "voc_det": extract_comments("Publicaciones Seller Dev", "det"),
            "gerado_em": "2026-05-04"
        },
        "gerado_em": "2026-05-04"
    },
    "mes": {
        "periodo": "MoM: M2 (Marco 2026) vs M1 (Abril 2026)",
        "best_driver": "ME Vendedor Seller Dev",
        "worst_driver": "Publicaciones Seller Dev",
        "best": {
            "driver": "ME Vendedor Seller Dev",
            "nps_a": 67.10, "nps_b": 68.20, "delta": 1.12, "contribution": 0.480,
            "top_process": "Reputacao ME",
            "process_nps_a": 80.43, "process_nps_b": 82.65, "process_delta": 2.22,
            "process_impact": 2.402, "process_share": 62.2,
            "top_cdu_queda": get_cdu(cdu_data.get("ME Vendedor Seller Dev", {}), "mom_worst"),
            "top_cdu_alta":  get_cdu(cdu_data.get("ME Vendedor Seller Dev", {}), "mom_best"),
            "canal": fmt_canal(me_c_mom),
            "senioridade": me_s_mom,
            "oportunidade": (
                "ME Places (Logistica Places) reverteu de NPS -13% para +34.8% (+48pp MoM) — "
                "mudanca operacional identificada que e replicavel a outros CDUs de logistica. "
                "Despacho Ventas y Publicacoes cresceu +5.7pp MoM — segundo maior ganho de qualidade."
            ),
            "conclusao": (
                "Reputacao ME lidera crescimento mensal (+2.22pp MoM, +2.40pp de contribuicao ao consolidado). "
                "Logistica Places reverteu drasticamente — investigar o que mudou na operacao em Abril. "
                "CDU Desativar ME acumulou -14.9pp MoM — deterioracao progressiva por restricao sistemica. "
                "Driver opera 10.4pp acima do target com trajetoria consistente ha 5 meses."
            ),
            "voc_pro": extract_comments("ME Vendedor Seller Dev", "pro"),
            "voc_det": extract_comments("ME Vendedor Seller Dev", "det"),
            "gerado_em": "2026-05-04"
        },
        "worst": {
            "driver": "Publicaciones Seller Dev",
            "nps_a": 68.52, "nps_b": 64.13, "delta": -4.33, "contribution": -0.702,
            "top_process": "Afiliados ML",
            "process_nps_a": 69.9, "process_nps_b": 65.7, "process_delta": -4.2,
            "process_impact": -2.233, "process_share": 41.9,
            "top_cdu_queda": get_cdu(cdu_data.get("Publicaciones Seller Dev", {}), "mom_worst"),
            "top_cdu_alta":  get_cdu(cdu_data.get("Publicaciones Seller Dev", {}), "mom_best"),
            "canal": fmt_canal(pub_c_mom),
            "senioridade": pub_s_mom,
            "oportunidade": (
                "Gestao de Publicacao (+1.1pp MoM) e PR-Articulos prohibidos (+4.8pp) mostram que "
                "moderacao com criterio claro gera NPS alto. Criar padroes de resposta para Afiliados ML "
                "reduziria o principal gargalo do driver."
            ),
            "conclusao": (
                "Afiliados ML (42% do volume) e o maior ofensor mensal: -4.2pp MoM, -2.23pp contribuicao. "
                "CDU Clips/Potencializador colapsou -52.9pp em Abril — mudanca de produto sem treinamento. "
                "CDU Funcionalidade Preco por variacao subiu +39pp: quando produto e bem explicado, NPS e alto. "
                "VoC: metricas de comissao nao entrando, redundancia de resposta em casos de Afiliados. "
                "Acao: FAQ de elegibilidade de indicacoes + notificacao de status de moderacao com prazo."
            ),
            "voc_pro": extract_comments("Publicaciones Seller Dev", "pro"),
            "voc_det": extract_comments("Publicaciones Seller Dev", "det"),
            "gerado_em": "2026-05-04"
        },
        "gerado_em": "2026-05-04"
    }
}

# VIG same as WoW
import copy
strategic["vig"] = copy.deepcopy(strategic["sem"])
strategic["vig"]["periodo"] = "Vigente (referencia: S1 27/abr-03/mai)"

# Save
with open("dd_summaries.json", encoding="utf-8") as f:
    summaries = json.load(f)
summaries["_strategic"] = strategic
with open("dd_summaries.json", "w", encoding="utf-8") as f:
    json.dump(summaries, f, ensure_ascii=False, indent=2)

print("OK — _strategic salvo em dd_summaries.json")
for period in ["sem", "mes"]:
    s = strategic[period]
    print(f"  {period}: best={s['best_driver']}, worst={s['worst_driver']}")
