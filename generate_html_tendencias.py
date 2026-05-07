#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NPS Tendencias Gerencia — Dashboard Executivo de Tendencias e Evolucao
Le dados automaticamente de generate_html_gerencia.py (Secoes 1 e 2).
Rodar: python generate_html_tendencias.py
"""
import json as _json
import re   as _re
import html as _html

# ══════════════════════════════════════════════════════════════════════
# 1. CARREGA DADOS DO generate_html_gerencia.py
# ══════════════════════════════════════════════════════════════════════
with open('generate_html_gerencia.py', 'r', encoding='utf-8') as _f:
    _src = _f.read()

_stop = _re.search(r'# SECTION 5', _src)
_stop = _stop.start() if _stop else len(_src)

_ns = {}
exec(compile(_src[:_stop], 'generate_html_gerencia.py', 'exec'), _ns)

MONTH_LABELS    = _ns['MONTH_LABELS']
WEEK_LABELS     = _ns['WEEK_LABELS']
monthly_history = _ns['monthly_history']
weekly_history  = _ns['weekly_history']
DRIVER_TARGETS  = _ns['DRIVER_TARGETS']
NPS_TARGET      = _ns['NPS_TARGET']
DRIVER_SHORT    = _ns['DRIVER_SHORT']
DRIVER_COLORS   = _ns['DRIVER_COLORS']
M1_LABEL        = _ns['M1_LABEL']
M2_LABEL        = _ns['M2_LABEL']
S1_LABEL        = _ns['S1_LABEL']
S2_LABEL        = _ns.get('S2_LABEL', '')
REPORT_DATE     = _ns['REPORT_DATE']

OUTPUT_FILE = 'nps_tendencias_gerencia.html'

# ══════════════════════════════════════════════════════════════════════
# 2. CONFIGURACOES
# ══════════════════════════════════════════════════════════════════════
DRIVER_GROUPS = {
    "ME Vendedor":       ["ME Vendedor Seller Dev", "ME Vendedor Mature", "ME Vendedor Meli Pro"],
    "Exp. Impositiva":   ["Experiencia Impositiva Seller Dev", "Experiencia Impositiva Mature",
                          "Experiencia Impositiva Meli Pro"],
    "PCF Vendedor":      ["PCF Vendedor Seller Dev", "PCF Vendedor Mature", "PCF Vendedor Meli Pro"],
    "Post Venta":        ["Post Venta Seller Dev", "Post Venta Mature", "Post Venta Meli Pro"],
    "Publicaciones":     ["Publicaciones Seller Dev", "Publicaciones Mature", "Publicaciones Meli Pro"],
    "FBM-S":             ["FBM-S Seller Dev", "FBM-S Mature", "FBM-S Meli Pro"],
    "PDD":               ["PDD DS&XD - Vendedor", "PDD FBM - Vendedor",
                          "PDD Fotos - Vendedor", "PDD MP,FLEX & CBT - Vendedor"],
    "PNR":               ["PNR ME - Vendedor", "PNR MP - Vendedor"],
    "Partners":          ["Partners"],
    "CBT":               ["CBT"],
    "Otros CV":          ["Otros CV"],
}

CATEGORIES = {
    "Longtail":    ["Experiencia Impositiva Seller Dev", "ME Vendedor Seller Dev", "Partners",
                    "PCF Vendedor Seller Dev", "Post Venta Seller Dev", "Publicaciones Seller Dev"],
    "Mature":      ["Experiencia Impositiva Mature", "ME Vendedor Mature", "PCF Vendedor Mature",
                    "Post Venta Mature", "Publicaciones Mature"],
    "Meli Pro":    ["Experiencia Impositiva Meli Pro", "ME Vendedor Meli Pro", "PCF Vendedor Meli Pro",
                    "Post Venta Meli Pro", "Publicaciones Meli Pro"],
    "FBM":         ["FBM-S Mature", "FBM-S Meli Pro", "FBM-S Seller Dev"],
    "PDD/PNR/CBT": ["CBT", "PDD DS&XD - Vendedor", "PDD FBM - Vendedor", "PDD Fotos - Vendedor",
                    "PDD MP,FLEX & CBT - Vendedor", "PNR ME - Vendedor", "PNR MP - Vendedor"],
    "Otros CV":    ["Otros CV"],
}

CAT_COLORS = {
    "Longtail":    "#3483FA",
    "Mature":      "#00A650",
    "Meli Pro":    "#FF7733",
    "FBM":         "#F39C12",
    "PDD/PNR/CBT": "#9B59B6",
    "Otros CV":    "#95A5A6",
}

EXCLUIDOS = frozenset([
    "CBT",
    "PDD DS&XD - Vendedor",
    "PDD FBM - Vendedor",
    "PDD Fotos - Vendedor",
    "PDD MP,FLEX & CBT - Vendedor",
    "PNR ME - Vendedor",
    "PNR MP - Vendedor",
])

GROUP_COLORS = {
    "ME Vendedor":       "#00A650",
    "Exp. Impositiva":   "#3483FA",
    "PCF Vendedor":      "#FF7733",
    "Post Venta":        "#E84142",
    "Publicaciones":     "#B7950B",
    "FBM-S":             "#F39C12",
    "Partners":          "#1ABC9C",
    "Otros CV":          "#95A5A6",
}

# Remove drivers excluídos de todos os grupos e descarta grupos vazios
DRIVER_GROUPS = {g: [d for d in drvs if d not in EXCLUIDOS]
                 for g, drvs in DRIVER_GROUPS.items()
                 if any(d not in EXCLUIDOS for d in drvs)}

ALL_DRIVERS = [d for d in monthly_history.keys() if d not in EXCLUIDOS]

# ══════════════════════════════════════════════════════════════════════
# 2B. EXEC_DATA — análise qualitativa por driver (de _exec_data.json)
# ══════════════════════════════════════════════════════════════════════
import os as _os
_EXEC = {}
if _os.path.exists("_exec_data.json"):
    with open("_exec_data.json", encoding="utf-8") as _f:
        _EXEC = _json.load(_f)

# ── QUANT_ANALYSIS — análise quantitativa promotores vs detratores
_QA = {}
if _os.path.exists("_quant_analysis.json"):
    with open("_quant_analysis.json", encoding="utf-8") as _f:
        _QA = _json.load(_f)

# ── PROCESS_ANALYSIS — análise detalhada por processo
_PA = {}
if _os.path.exists("_process_analysis.json"):
    with open("_process_analysis.json", encoding="utf-8") as _f:
        _PA = _json.load(_f)

# ── DD_BREAKDOWN — processos, canal, oficina, senioridade
_DD = {}
if _os.path.exists("dd_breakdown.json"):
    with open("dd_breakdown.json", encoding="utf-8") as _f:
        _DD = _json.load(_f)

_DD_MAI = {}
if _os.path.exists("_mai_breakdown.json"):
    with open("_mai_breakdown.json", encoding="utf-8") as _f:
        _DD_MAI = _json.load(_f)

def _agg_dim(drvs, dim, period, source=None):
    """Agrega dimensão/período somando p/d/s para um grupo de drivers."""
    db = source if source is not None else _DD
    result = {}
    for drv in drvs:
        for key, vals in db.get(drv, {}).get(dim, {}).get(period, {}).items():
            if not key or key.startswith("(sem"): continue
            r = result.setdefault(key, {"p": 0, "d": 0, "s": 0})
            r["p"] += vals.get("p", 0)
            r["d"] += vals.get("d", 0)
            r["s"] += vals.get("s", 0)
    for v in result.values():
        v["nps"] = round(100.0*(v["p"]-v["d"])/v["s"], 1) if v["s"] > 0 else None
    return result

# M1 = Maio (_mai_breakdown), M2 = Abril (dd_breakdown M1)
grp_breakdown = {}
for _grp, _drvs in DRIVER_GROUPS.items():
    grp_breakdown[_grp] = {
        "P_M1":  _agg_dim(_drvs, "P",  "Mai", _DD_MAI),
        "P_M2":  _agg_dim(_drvs, "P",  "M1",  _DD),
        "C_M1":  _agg_dim(_drvs, "C",  "Mai", _DD_MAI),
        "C_M2":  _agg_dim(_drvs, "C",  "M1",  _DD),
        "O_M1":  _agg_dim(_drvs, "O",  "Mai", _DD_MAI),
        "Sr_M1": _agg_dim(_drvs, "Sr", "Mai", _DD_MAI),
        "Sr_M2": _agg_dim(_drvs, "Sr", "M1",  _DD),
    }

# S1 = semana atual, S2 = semana anterior (dd_breakdown)
grp_wk_bd = {}
for _grp, _drvs in DRIVER_GROUPS.items():
    grp_wk_bd[_grp] = {
        "P_M1":  _agg_dim(_drvs, "P",  "S1", _DD),
        "P_M2":  _agg_dim(_drvs, "P",  "S2", _DD),
        "C_M1":  _agg_dim(_drvs, "C",  "S1", _DD),
        "C_M2":  _agg_dim(_drvs, "C",  "S2", _DD),
        "O_M1":  _agg_dim(_drvs, "O",  "S1", _DD),
        "Sr_M1": _agg_dim(_drvs, "Sr", "S1", _DD),
        "Sr_M2": _agg_dim(_drvs, "Sr", "S2", _DD),
    }

# ══════════════════════════════════════════════════════════════════════
# 3. CALCULOS
# ══════════════════════════════════════════════════════════════════════
def _nps_t(t):
    p, d, s = t
    return round(100.0 * (p - d) / s, 2) if s > 0 else None

def _cons(hist, labels, drivers=None):
    dset = drivers if drivers is not None else list(hist.keys())
    out = []
    for lb in labels:
        tp = sum(hist[d].get(lb, (0,0,0))[0] for d in dset if d in hist)
        td = sum(hist[d].get(lb, (0,0,0))[1] for d in dset if d in hist)
        ts = sum(hist[d].get(lb, (0,0,0))[2] for d in dset if d in hist)
        out.append(round(100.0*(tp-td)/ts, 2) if ts > 0 else None)
    return out

def _drv_s(hist, labels, drv):
    return [_nps_t(hist[drv].get(lb, (0,0,0))) for lb in labels]

mon_cons = _cons(monthly_history, MONTH_LABELS)
wk_cons  = _cons(weekly_history,  WEEK_LABELS)

cat_mon = {cat: _cons(monthly_history, MONTH_LABELS, drvs) for cat, drvs in CATEGORIES.items()}
cat_wk  = {cat: _cons(weekly_history,  WEEK_LABELS,  drvs) for cat, drvs in CATEGORIES.items()}

grp_mon = {grp: _cons(monthly_history, MONTH_LABELS, drvs) for grp, drvs in DRIVER_GROUPS.items()}
grp_wk  = {grp: _cons(weekly_history,  WEEK_LABELS,  drvs) for grp, drvs in DRIVER_GROUPS.items()}

def _grp_target(drvs):
    """Target ponderado pelo volume do último mês fechado."""
    lB  = MONTH_LABELS[-2]   # mês anterior = último fechado
    num = sum(monthly_history[d].get(lB,(0,0,0))[2] * DRIVER_TARGETS.get(d, NPS_TARGET)
              for d in drvs if d in monthly_history)
    den = sum(monthly_history[d].get(lB,(0,0,0))[2] for d in drvs if d in monthly_history)
    return round(num / den, 2) if den else NPS_TARGET

grp_targets = {grp: _grp_target(drvs) for grp, drvs in DRIVER_GROUPS.items()}

drv_m = {d: _drv_s(monthly_history, MONTH_LABELS, d) for d in ALL_DRIVERS}
drv_w = {d: _drv_s(weekly_history,  WEEK_LABELS,  d) for d in ALL_DRIVERS}

curr_m  = {d: drv_m[d][-1] for d in ALL_DRIVERS}
prev_m  = {d: drv_m[d][-2] for d in ALL_DRIVERS}
trend_m = {d: round(curr_m[d] - prev_m[d], 2)
           if curr_m[d] is not None and prev_m[d] is not None else None
           for d in ALL_DRIVERS}

curr_w  = {d: drv_w[d][-1] for d in ALL_DRIVERS}
prev_w  = {d: drv_w[d][-2] for d in ALL_DRIVERS}
trend_w = {d: round(curr_w[d] - prev_w[d], 2)
           if curr_w[d] is not None and prev_w[d] is not None else None
           for d in ALL_DRIVERS}

delta_tgt = {d: round(curr_m[d] - DRIVER_TARGETS.get(d, NPS_TARGET), 2)
             if curr_m[d] is not None else None
             for d in ALL_DRIVERS}

kpi_nps    = mon_cons[-1]
kpi_delta_m = (round(mon_cons[-1] - mon_cons[-2], 2)
               if mon_cons[-1] is not None and mon_cons[-2] is not None else None)
kpi_vs_tgt  = (round(mon_cons[-1] - NPS_TARGET, 2) if mon_cons[-1] is not None else None)

# Dados das cascatas ─────────────────────────────────────────────
def _nps0(t):
    p, d, s = t
    return round(100.0 * (p - d) / s, 2) if s > 0 else 0.0

def _grp_raw(label, drvs):
    """Agrega (promoters, detractors, surveys) de um grupo para um período."""
    p = sum(monthly_history[d].get(label, (0,0,0))[0] for d in drvs if d in monthly_history)
    det = sum(monthly_history[d].get(label, (0,0,0))[1] for d in drvs if d in monthly_history)
    s = sum(monthly_history[d].get(label, (0,0,0))[2] for d in drvs if d in monthly_history)
    return p, det, s

def _mm_waterfall():
    """M2 → M1: decomposição MIX + NETO agrupada por driver base."""
    lA, lB = MONTH_LABELS[-2], MONTH_LABELS[-1]
    sA_tot = sum(monthly_history[d].get(lA, (0,0,0))[2] for d in ALL_DRIVERS)
    sB_tot = sum(monthly_history[d].get(lB, (0,0,0))[2] for d in ALL_DRIVERS)
    nps_B  = mon_cons[-1] or 0.0
    d_dict = {}
    for grp, drvs in DRIVER_GROUPS.items():
        pA, dA, sA = _grp_raw(lA, drvs)
        pB, dB, sB = _grp_raw(lB, drvs)
        na  = _nps0((pA, dA, sA))
        nb  = _nps0((pB, dB, sB))
        sha = sA / sA_tot if sA_tot else 0
        shb = sB / sB_tot if sB_tot else 0
        neto = round(sha * (nb - na), 2)
        mix  = round((shb - sha) * (nb - nps_B), 2)
        d_dict[grp] = {"var": round(neto + mix, 2)}
    return mon_cons[-2] or 0.0, mon_cons[-1] or 0.0, d_dict

def _tgt_waterfall():
    """Target → Atual: contribuição agrupada do gap vs target."""
    lB    = MONTH_LABELS[-1]
    sB_tot = sum(monthly_history[d].get(lB, (0,0,0))[2] for d in ALL_DRIVERS)
    d_dict = {}
    for grp, drvs in DRIVER_GROUPS.items():
        pB, dB, sB = _grp_raw(lB, drvs)
        nb  = _nps0((pB, dB, sB))
        # target ponderado pelo volume de cada driver no grupo
        tgt = (sum(monthly_history[d].get(lB,(0,0,0))[2] * DRIVER_TARGETS.get(d, NPS_TARGET)
                   for d in drvs if d in monthly_history) / sB) if sB else NPS_TARGET
        shb = sB / sB_tot if sB_tot else 0
        d_dict[grp] = {"var": round(shb * (nb - tgt), 2)}
    return NPS_TARGET, mon_cons[-1] or 0.0, d_dict

# ══════════════════════════════════════════════════════════════════════
# 4. HELPERS HTML
# ══════════════════════════════════════════════════════════════════════
def fn(v):
    return f"{v:.1f}".replace(".", ",") if v is not None else "—"

def chip(v, suffix="pp"):
    if v is None:
        return '<span class="chip chip-neu">—</span>'
    sign = "+" if v > 0 else ""
    cls  = "chip-pos" if v > 0 else ("chip-neg" if v < 0 else "chip-neu")
    return f'<span class="chip {cls}">{sign}{fn(v)}{suffix}</span>'

def arr(v, thr=0.3):
    if v is None:   return '<span class="arr arr-neu">—</span>'
    if v >  thr:    return '<span class="arr arr-pos">&#9650;</span>'
    if v < -thr:    return '<span class="arr arr-neg">&#9660;</span>'
    return '<span class="arr arr-neu">&#8594;</span>'

def cell_bg(nps_v, tgt_v):
    if nps_v is None:
        return ""
    diff = nps_v - tgt_v
    if diff >= 0:   return "style='background:#e6f9ee;color:#1a7a42'"
    if diff >= -3:  return "style='background:#fffae6;color:#7a5800'"
    if diff >= -10: return "style='background:#fff0e0;color:#7a3a00'"
    return "style='background:#fde8e8;color:#a01010'"

def drv_cat(drv):
    for cat, drvs in CATEGORIES.items():
        if drv in drvs:
            return cat
    return "—"

def esc(s):
    return _html.escape(str(s))

# ══════════════════════════════════════════════════════════════════════
# 5. BLOCOS DE GRAFICOS (Chart.js)
# ══════════════════════════════════════════════════════════════════════
_FMT = 'function(v){return v!=null?v.toFixed(1).replace(".",",")+"%":""}'

def _chart_script(chart_id, cfg_json, height=240):
    return (f'<div style="position:relative;height:{height}px;">'
            f'<canvas id="{chart_id}"></canvas></div>'
            f'<script>new Chart(document.getElementById("{chart_id}"),{cfg_json});</script>')

def chart_bar_monthly(cid):
    datasets = [
        {"type": "bar", "label": "NPS Consolidado",
         "data": mon_cons,
         "backgroundColor": "#3483FAcc", "borderColor": "#3483FA",
         "borderWidth": 1, "borderRadius": 5,
         "datalabels": {"display": True, "anchor": "end", "align": "end",
                        "offset": 3, "color": "#333",
                        "font": {"size": 11, "weight": "700"},
                        "formatter": "__FMT__"}},
        {"type": "line", "label": f"Target ({str(NPS_TARGET).replace('.', ',')}%)",
         "data": [NPS_TARGET] * len(MONTH_LABELS),
         "borderColor": "#E84142", "borderDash": [6, 3], "borderWidth": 2,
         "pointRadius": 0, "fill": False, "datalabels": {"display": False}},
    ]
    cfg = {"type": "bar",
           "data": {"labels": MONTH_LABELS, "datasets": datasets},
           "options": {
               "responsive": True, "maintainAspectRatio": False,
               "layout": {"padding": {"top": 28, "bottom": 4}},
               "plugins": {
                   "legend": {"position": "bottom", "labels": {"boxWidth": 10, "padding": 8, "font": {"size": 10}}},
                   "datalabels": {}},
               "scales": {
                   "y": {"min": 30, "max": 80, "ticks": {"stepSize": 10}, "grid": {"color": "#f0f0f0"}},
                   "x": {"grid": {"display": False}}}}}
    j = _json.dumps(cfg).replace('"__FMT__"', _FMT)
    return _chart_script(cid, j, 240)

def waterfall_chart(cid, label_a, nps_a, label_b, nps_b, d_dict, height=370):
    sorted_drvs = sorted(d_dict.keys(), key=lambda d: -d_dict[d]['var'])

    y_lo    = max(30, int(min(nps_a, nps_b)) - 5)
    y_hi    = min(85, int(max(nps_a, nps_b)) + 14)
    y_lo    = (y_lo // 5) * 5
    y_hi    = ((y_hi + 4) // 5) * 5

    labels  = [label_a]
    bars    = [[y_lo, round(nps_a, 2)]]
    colors  = ['#3483FAcc']
    deltas  = [None]
    running = nps_a

    for drv in sorted_drvs:
        v = round(d_dict[drv]['var'], 2)
        labels.append(DRIVER_SHORT.get(drv, drv))
        lo = round(min(running, running + v), 2)
        hi = round(max(running, running + v), 2)
        bars.append([lo, hi])
        colors.append('#00a650cc' if v >= 0 else '#e84142cc')
        deltas.append(v)
        running += v

    labels.append(label_b)
    bars.append([y_lo, round(nps_b, 2)])
    colors.append('#3483FAcc')
    deltas.append(None)

    deltas_js = _json.dumps(deltas)
    wf_fmt = (f'function(v,ctx){{'
              f'var d={deltas_js}[ctx.dataIndex];'
              f'if(d===null){{return v!=null?v[1].toFixed(1).replace(".",",")+"%":"";}}'
              f'return (d>0?"+":"")+d.toFixed(1).replace(".",",")+"%";}}')

    dataset = {"type": "bar", "data": bars,
               "backgroundColor": colors, "borderRadius": 2, "borderSkipped": False,
               "datalabels": {"display": True, "anchor": "end", "align": "end",
                              "offset": 2, "color": "#333",
                              "font": {"size": 8, "weight": "600"},
                              "formatter": "__WF_FMT__"}}
    cfg = {"type": "bar",
           "data": {"labels": labels, "datasets": [dataset]},
           "options": {
               "responsive": True, "maintainAspectRatio": False,
               "layout": {"padding": {"top": 22, "bottom": 4}},
               "plugins": {"legend": {"display": False}, "datalabels": {}},
               "scales": {
                   "y": {"min": y_lo, "max": y_hi,
                         "ticks": {"stepSize": 5}, "grid": {"color": "#f0f0f0"}},
                   "x": {"ticks": {"font": {"size": 10}, "maxRotation": 30},
                         "grid": {"display": False}}}}}
    cfg_json = _json.dumps(cfg).replace('"__WF_FMT__"', wf_fmt)
    return _chart_script(cid, cfg_json, height)

def chart_small_multiples(base_cid, items, cons_data, labels):
    """
    Grid de mini-gráficos: barras (resultado) + linha target + consolidado cinza.
    items: lista de (name, series, color, target_val)
    """
    blocks = []
    for i, (name, series, color, target_val) in enumerate(items):
        cid = f"{base_cid}_{i}"

        curr_v  = next((v for v in reversed(series) if v is not None), None)
        prev_v  = next((v for v in reversed(series[:-1]) if v is not None), None)
        trend_v = round(curr_v - prev_v, 1) if curr_v is not None and prev_v is not None else None
        nps_str   = fn(curr_v) + "%" if curr_v is not None else "—"
        trend_str = (("+" if trend_v >= 0 else "") + fn(trend_v) + "pp") if trend_v is not None else ""
        trend_cls = "sm-pos" if trend_v is not None and trend_v > 0 else ("sm-neg" if trend_v is not None and trend_v < 0 else "sm-neu")
        vs_tgt  = round(curr_v - target_val, 1) if curr_v is not None else None
        vs_str  = (("+" if vs_tgt >= 0 else "") + fn(vs_tgt) + "pp vs tgt") if vs_tgt is not None else ""
        vs_cls  = "sm-pos" if vs_tgt is not None and vs_tgt >= 0 else "sm-neg"

        datasets = [
            {"type": "bar", "label": name, "data": series,
             "backgroundColor": color + "bb", "borderColor": color,
             "borderWidth": 1, "borderRadius": 3,
             "datalabels": {"display": True, "anchor": "end", "align": "end",
                            "offset": 2, "color": "#444",
                            "font": {"size": 8, "weight": "700"},
                            "formatter": "__FMT__"}},
            {"type": "line", "label": "Consolidado", "data": cons_data,
             "borderColor": "#bbb", "borderWidth": 1.2,
             "pointRadius": 0, "fill": False, "tension": 0.35, "borderDash": [3, 3],
             "datalabels": {"display": False}},
            {"type": "line", "label": "Target", "data": [target_val] * len(labels),
             "borderColor": "#E84142", "borderDash": [6, 3],
             "borderWidth": 1.8, "pointRadius": 0, "fill": False,
             "datalabels": {"display": False}},
        ]
        cfg = {"type": "bar",
               "data": {"labels": labels, "datasets": datasets},
               "options": {
                   "responsive": True, "maintainAspectRatio": False,
                   "layout": {"padding": {"top": 14, "right": 46, "bottom": 2, "left": 4}},
                   "interaction": {"mode": "index", "intersect": False},
                   "plugins": {"legend": {"display": False}, "datalabels": {}},
                   "scales": {
                       "y": {"min": -20, "max": 100,
                             "ticks": {"stepSize": 20, "font": {"size": 9}},
                             "grid": {"color": "#f0f0f0"}},
                       "x": {"ticks": {"font": {"size": 9}}, "grid": {"display": False}}}}}

        mini_chart = (f'<div style="position:relative;height:155px;">'
                      f'<canvas id="{cid}"></canvas></div>'
                      f'<script>new Chart(document.getElementById("{cid}"),'
                      f'{_json.dumps(cfg).replace(chr(34)+"__FMT__"+chr(34), _FMT)});</script>')

        blocks.append(
            f'<div class="sm-item" style="border-top:3px solid {color}">'
            f'<div class="sm-header"><span class="sm-cat">{esc(name)}</span>'
            f'<span class="sm-nps">{nps_str} <span class="{trend_cls}">{trend_str}</span></span></div>'
            f'<div class="sm-sub {vs_cls}">{vs_str}</div>'
            f'{mini_chart}</div>'
        )

    return f'<div class="sm-grid">{"".join(blocks)}</div>'

# ══════════════════════════════════════════════════════════════════════
# 6. CONTEUDO DAS ABAS
# ══════════════════════════════════════════════════════════════════════

def _tab_exec():
    # --- KPI Cards ---
    nps_disp   = fn(kpi_nps) + "%" if kpi_nps is not None else "—"
    delta_sign = "+" if kpi_delta_m is not None and kpi_delta_m >= 0 else ""
    delta_disp = (delta_sign + fn(kpi_delta_m) + "pp") if kpi_delta_m is not None else "—"
    delta_cls  = "kpi-pos" if kpi_delta_m is not None and kpi_delta_m >= 0 else "kpi-neg"
    tgt_sign   = "+" if kpi_vs_tgt is not None and kpi_vs_tgt >= 0 else ""
    tgt_disp   = (tgt_sign + fn(kpi_vs_tgt) + "pp") if kpi_vs_tgt is not None else "—"
    tgt_cls    = "kpi-pos" if kpi_vs_tgt is not None and kpi_vs_tgt >= 0 else "kpi-neg"
    tgt_status = "Acima &#x2713;" if kpi_vs_tgt is not None and kpi_vs_tgt >= 0 else "Abaixo &#x2717;"
    prev_disp  = fn(mon_cons[-2]) + "%" if mon_cons[-2] is not None else "—"
    curr_disp  = fn(mon_cons[-1]) + "%" if mon_cons[-1] is not None else "—"

    kpis = f"""<div class="kpi-strip">
  <div class="kpi-card">
    <div class="kpi-label">NPS Consolidado &mdash; {esc(MONTH_LABELS[-1])}</div>
    <div class="kpi-value">{nps_disp}</div>
    <div class="kpi-sub">Target: {str(NPS_TARGET).replace('.', ',')}%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Varia&#231;&#227;o M/M ({esc(MONTH_LABELS[-2])} &rarr; {esc(MONTH_LABELS[-1])})</div>
    <div class="kpi-value {delta_cls}">{delta_disp}</div>
    <div class="kpi-sub">{prev_disp} &rarr; {curr_disp}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">&#916; vs Target</div>
    <div class="kpi-value {tgt_cls}">{tgt_disp}</div>
    <div class="kpi-sub">{tgt_status} do target</div>
  </div>
</div>"""

    # --- Resumo Executivo ---
    exec_html = f'<div class="section-block"><div class="exec-wrap">{_load_exec_summary()}</div></div>'

    # --- Chart ---
    chart_sec = f"""<div class="section-block">
  <div class="section-title">Evolu&#231;&#227;o NPS Consolidado &mdash; Mensal YTD</div>
  {chart_bar_monthly("c_exec_mon")}
</div>"""

    # --- Cascatas ---
    nps_a_mm, nps_b_mm, dd_mm   = _mm_waterfall()
    nps_a_tg, nps_b_tg, dd_tg   = _tgt_waterfall()

    lA = esc(MONTH_LABELS[-2])
    lB = esc(MONTH_LABELS[-1])

    wf_mm = f"""<div class="section-block">
  <div class="section-title">Cascata M/M &mdash; {lA} &rarr; {lB}
    <span style="font-weight:400;font-size:12px;color:#888;margin-left:8px;">
      {fn(nps_a_mm)}% &rarr; {fn(nps_b_mm)}% &nbsp;{chip(round(nps_b_mm - nps_a_mm, 2))}
    </span>
  </div>
  {waterfall_chart("c_wf_mm", lA, nps_a_mm, lB, nps_b_mm, dd_mm)}
</div>"""

    tgt_str = str(NPS_TARGET).replace('.', ',')
    wf_tg = f"""<div class="section-block">
  <div class="section-title">Cascata vs Target &mdash; {lB}
    <span style="font-weight:400;font-size:12px;color:#888;margin-left:8px;">
      Target {tgt_str}% &rarr; Real {fn(nps_b_tg)}% &nbsp;{chip(round(nps_b_tg - NPS_TARGET, 2))}
    </span>
  </div>
  {waterfall_chart("c_wf_tg", f"Target ({tgt_str}%)", nps_a_tg, lB, nps_b_tg, dd_tg)}
</div>"""

    return kpis + chart_sec + wf_mm + wf_tg + exec_html


def _dim_table(dim_dict, max_rows=4, label="Nome"):
    """Mini-tabela de uma dimensão (CDU/Sol/Sen) com NPS + delta vs global."""
    rows = sorted(dim_dict.items(), key=lambda x: -x[1]["s"])[:max_rows]
    html = (f'<table class="bd-tbl"><thead>'
            f'<tr><th>{esc(label)}</th><th>NPS</th><th>Vol</th></tr>'
            f'</thead><tbody>')
    for name, v in rows:
        nps_v = v.get("nps")
        html += (f'<tr><td class="bd-name">{esc(name[:40])}</td>'
                 f'<td class="bd-nps">{fn(nps_v) if nps_v is not None else "—"}%</td>'
                 f'<td class="bd-vol">{v["s"]:,}</td></tr>')
    return html + '</tbody></table>'

def _reason_list(reason_dict, max_items=4, color="#a01010"):
    items = sorted(reason_dict.items(), key=lambda x: -x[1])[:max_items]
    if not items:
        return '<div style="color:#aaa;font-size:11px">Sem motivos estruturados registrados.</div>'
    return "".join(
        f'<div class="exec-bullet" style="font-size:11px">'
        f'<span style="color:{color};font-weight:600">{esc(r[:60])}</span>'
        f' <span style="color:#aaa">({n} caso{"s" if n>1 else ""})</span></div>'
        for r, n in items
    )

def _trx_bullets(transcripts, max_t=10):
    """Analisa transcrições e retorna bullets de padrões identificados."""
    if not transcripts:
        return ""
    total = len(transcripts)
    KW = {
        "Transferência para outro atendente": ["transfiro","vou te transferir","encaminhar para","outro atendente"],
        "Reincidência (seller já tentou antes)": ["já abri","já tentei","segunda vez","desde ontem","semanas","meses tentando"],
        "Risco de escalação legal (PROCON/judicial)": ["procon","judicial","advogado","reclamação formal","vou processar"],
        "Sem indicação de resolução no encerramento": None,  # inferido
        "Resposta automatizada sem análise do caso": None,   # inferido por comprimento
        "Empatia identificada do atendente": ["entendo sua","lamento","me desculpe","sinto muito","compreendo sua"],
    }
    counts = {k: 0 for k in KW}
    resolved = 0
    for cid, txt in list(transcripts.items())[:max_t]:
        tl = txt.lower()
        lines_rep = [l for l in txt.split("\n") if l.startswith("[REP]")]
        has_res = any(k in tl for k in ["resolvido","solucionado","concluído","feito isso","problema resolvido"])
        if has_res: resolved += 1
        for pat, kws in KW.items():
            if kws is None: continue
            if any(k in tl for k in kws):
                counts[pat] += 1
        if sum(1 for m in lines_rep if len(m) > 250) >= 2:
            counts["Resposta automatizada sem análise do caso"] += 1
    counts["Sem indicação de resolução no encerramento"] = total - resolved

    bullets = ""
    for pat, n in counts.items():
        if n == 0: continue
        pct = round(100*n/total)
        color = "#a01010" if "sem" in pat.lower() or "transfer" in pat.lower() or "reinci" in pat.lower() or "risco" in pat.lower() or "automa" in pat.lower() else "#00A650"
        bullets += (f'<div class="exec-bullet" style="font-size:11px">'
                    f'<span style="color:{color};font-weight:600">{n}/{total} casos ({pct}%)</span>'
                    f' — {esc(pat)}</div>')
    return bullets

def _quant_section_html(grp):
    """Gera seção de análise quantitativa promotores vs detratores."""
    qa = _QA.get(grp)
    if not qa:
        return ""

    det = qa.get("det", {}); pro = qa.get("pro", {})
    conclusions   = qa.get("conclusions", [])
    triggers      = qa.get("trigger_answers", [])
    nd = det.get("n", 0); np = pro.get("n", 0)
    if nd == 0 and np == 0:
        return ""

    def _bar(val, max_val=100, color="#3483FA"):
        pct = min(100, round(100 * val / max_val)) if max_val else 0
        return (f'<div style="background:#f0f2f5;border-radius:4px;height:8px;width:100%;margin-top:2px">'
                f'<div style="background:{color};border-radius:4px;height:8px;width:{pct}%"></div></div>')

    def _metric_row(label, det_v, pro_v, unit="", higher_is_better=True, fmt=".1f"):
        diff  = det_v - pro_v if det_v is not None and pro_v is not None else None
        is_bad = (diff > 0 and not higher_is_better) or (diff < 0 and higher_is_better) if diff is not None else False
        color = "#E84142" if is_bad else "#00A650"
        det_str = f"{det_v:{fmt}}{unit}" if det_v is not None else "—"
        pro_str = f"{pro_v:{fmt}}{unit}" if pro_v is not None else "—"
        diff_str = (f"{'+' if diff>0 else ''}{diff:{fmt}}{unit}") if diff is not None else ""
        diff_html = f'<span style="color:{color};font-weight:600;font-size:10px">{diff_str}</span>' if diff else ""
        return (f'<tr>'
                f'<td class="bd-name">{esc(label)}</td>'
                f'<td class="bd-nps" style="color:#E84142">{det_str}</td>'
                f'<td class="bd-nps" style="color:#00A650">{pro_str}</td>'
                f'<td style="text-align:right">{diff_html}</td>'
                f'</tr>')

    # Tabela comparativa
    rows  = _metric_row("Resolução confirmada (%)", det.get("pct_resolved"), pro.get("pct_resolved"), "%", True, ".0f")
    rows += _metric_row("Transferências (%)",       det.get("pct_transfer"), pro.get("pct_transfer"), "%", False, ".0f")
    rows += _metric_row("Reincidência (%)",          det.get("pct_reincidence"), pro.get("pct_reincidence"), "%", False, ".0f")
    rows += _metric_row("Escalação legal (%)",       det.get("pct_escalation"), pro.get("pct_escalation"), "%", False, ".0f")
    rows += _metric_row("Resposta automatizada (%)", det.get("pct_bot_heavy"), pro.get("pct_bot_heavy"), "%", False, ".0f")
    rows += _metric_row("Mudança de processo (%)",   det.get("pct_proc_change"), pro.get("pct_proc_change"), "%", False, ".0f")
    rows += _metric_row("Msgs por conversa",         det.get("avg_msgs_total"), pro.get("avg_msgs_total"), "", False, ".1f")
    rows += _metric_row("Compr. médio resp. (chars)",det.get("avg_rep_len"), pro.get("avg_rep_len"), "", True, ".0f")

    table_html = (f'<table class="bd-tbl" style="width:100%"><thead>'
                  f'<tr><th>Métrica</th>'
                  f'<th style="color:#E84142">Detratores<br><span style="font-weight:400;font-size:9px">({nd} casos)</span></th>'
                  f'<th style="color:#00A650">Promotores<br><span style="font-weight:400;font-size:9px">({np} casos)</span></th>'
                  f'<th>Δ</th></tr></thead>'
                  f'<tbody>{rows}</tbody></table>')

    # Conclusões com badges
    conc_html = ""
    for c in conclusions[:5]:
        icon  = "🔴" if c["type"] == "neg" else "🟢"
        color = "#fde8e8" if c["type"] == "neg" else "#e6f9ee"
        tc    = "#a01010"  if c["type"] == "neg" else "#1a7a42"
        conc_html += (f'<div style="background:{color};border-radius:6px;padding:8px 10px;'
                      f'margin-bottom:6px;font-size:12px;color:{tc}">'
                      f'{icon} {esc(c["msg"])}</div>')

    # Respostas às perguntas disparadoras
    trigger_html = ""
    if triggers:
        items = "".join(f'<div class="exec-bullet">{t}</div>' for t in triggers)
        trigger_html = (f'<div style="margin-top:12px">'
                        f'<div style="font-size:11px;font-weight:700;color:#3483FA;margin-bottom:6px">'
                        f'&#128161; Respostas &#224;s Perguntas Disparadoras</div>'
                        f'{items}</div>')

    return (f'<div class="exec-section">'
            f'<div class="exec-title">&#128200; An&#225;lise Quantitativa &mdash; '
            f'Promotores vs Detratores</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start">'
            f'<div>{table_html}</div>'
            f'<div>'
            f'<div style="font-size:11px;font-weight:700;color:#555;margin-bottom:8px">Conclus&#245;es baseadas nas transcri&#231;&#245;es</div>'
            f'{conc_html}'
            f'{trigger_html}'
            f'</div></div></div>')

def _dim_contributions(m1, m2):
    """
    Calcula contribuição NETO de cada item de uma dimensão para a variação M/M.
    Retorna lista de (item, contrib_pp, nps_m1, nps_m2, s_m1) ordenada por |contrib|.
    """
    s_tot_m1 = sum(v["s"] for v in m1.values()) or 1
    s_tot_m2 = sum(v["s"] for v in m2.values()) or 1
    results = []
    for item, v1 in m1.items():
        v2 = m2.get(item)
        if not v2 or v1["nps"] is None or v2["nps"] is None: continue
        share_m1 = v1["s"] / s_tot_m1
        share_m2 = v2["s"] / s_tot_m2
        neto = round(share_m1 * (v1["nps"] - v2["nps"]), 2)
        results.append((item, neto, v1["nps"], v2["nps"], v1["s"]))
    results.sort(key=lambda x: abs(x[1]), reverse=True)
    return results

def _comment_patterns(comments):
    """
    Detecta padrões qualitativos nos comentários de detratores e promotores.
    Retorna dict com evidências por padrão.
    """
    PAT = {
        "Reclamação de mudança de processo":
            ["mudou","antes era","antigamente","mudança","novo processo","mudaram","era diferente"],
        "Oportunidade de atendimento (sem resolução)":
            ["não resolveu","não me ajudou","não consegui","sem solução","ninguém resolve",
             "várias tentativas","múltiplos atendentes","vários atendentes"],
        "Problema sistêmico (plataforma/bug)":
            ["sistema","erro no sistema","bug","plataforma fora","instabilidade",
             "não funciona","erro","falha no sistema","plataforma"],
        "Demora excessiva no atendimento":
            ["demorou","muito tempo","hora esperando","aguardando","tempo de resposta",
             "sem retorno","dias esperando"],
        "Resolução no primeiro contato":
            ["resolveu rapidamente","primeiro contato","de imediato","rápido","ágil",
             "resolveu no mesmo","logo de cara"],
        "Atendimento consultivo/personalizado":
            ["explicou detalhado","me orientou","me ajudou muito","foi além",
             "proativo","personalizado","atenção especial"],
    }
    found = {}
    for c in comments:
        txt = (c.get("comment") or "").lower()
        if not txt or len(txt) < 10: continue
        for pat, kws in PAT.items():
            if any(k in txt for k in kws):
                found.setdefault(pat, [])
                if len(found[pat]) < 2:
                    found[pat].append(c.get("comment","")[:150])
    return found

def _trend_class(series):
    """Classifica a tendência dos últimos meses."""
    vals = [v for v in series if v is not None]
    if len(vals) < 2: return "indefinida", "#aaa"
    last3 = vals[-3:]
    diffs = [last3[i+1] - last3[i] for i in range(len(last3)-1)]
    avg_diff = sum(diffs) / len(diffs) if diffs else 0
    if all(d > 0 for d in diffs): return "alta consistente", "#00A650"
    if all(d < 0 for d in diffs): return "queda consistente", "#E84142"
    if avg_diff > 1: return "tendência positiva", "#00A650"
    if avg_diff < -1: return "tendência negativa", "#E84142"
    if abs(vals[-1] - vals[-2]) > 5: return "volátil", "#F39C12"
    return "estável", "#888"

def _process_exec_html(grp, mode="monthly"):
    """Gera análise executiva diagnóstica completa com causa raiz dimensional."""
    pa = _PA.get(grp)
    if not pa:
        return ""

    lCURR = _EXEC.get("lCURR", MONTH_LABELS[-1])
    lPREV = _EXEC.get("lPREV", MONTH_LABELS[-2])
    wf    = _EXEC.get("waterfall", {}).get(grp, {})
    top_neg_list = _EXEC.get("top_neg", [])
    top_pos_list = _EXEC.get("top_pos", [])
    qual  = _EXEC.get("qual", {}).get(grp, {})
    color = GROUP_COLORS.get(grp, "#3483FA")
    bd    = grp_breakdown.get(grp, {})

    # ── 1. Diagnóstico Dimensional ──────────────────────────────────
    canal_contrib = _dim_contributions(bd.get("C_M1",{}), bd.get("C_M2",{}))
    sen_contrib   = _dim_contributions(bd.get("Sr_M1",{}), bd.get("Sr_M2",{}))

    # Identifica qual dimensão explica mais a variação
    def _top_contrib(contribs, n=2):
        return [(item, c, n1, n2, s) for item,c,n1,n2,s in contribs if abs(c) >= 0.1][:n]

    top_canal = _top_contrib(canal_contrib)
    top_sen   = _top_contrib(sen_contrib)

    # Qual dimensão tem mais poder explicativo?
    canal_power = sum(abs(c) for _,c,*_ in top_canal)
    sen_power   = sum(abs(c) for _,c,*_ in top_sen)

    # ── 2. Causa raiz dominante ──────────────────────────────────────
    pa_neg = pa.get("top_neg"); pa_pos = pa.get("top_pos")
    proc_power = abs(pa_neg["contrib"]) if pa_neg and pa_neg.get("contrib") else 0

    dimensions_sorted = sorted([
        ("Processo",    proc_power,  pa_neg),
        ("Canal",       canal_power, top_canal),
        ("Senioridade", sen_power,   top_sen),
    ], key=lambda x: -x[1])

    dominant_dim = dimensions_sorted[0][0] if dimensions_sorted[0][1] > 0 else None

    # ── 3. Padrões qualitativos nos comentários ──────────────────────
    comments = qual.get("comments", [])
    dets = [c for c in comments if c.get("perfil") == "detrator"]
    pros = [c for c in comments if c.get("perfil") == "promotor"]
    qual_patterns = _comment_patterns(dets + pros)

    # ── 4. Tendência histórica ───────────────────────────────────────
    t_data  = _EXEC.get("nps_trend", {}).get(grp, {})
    t_series= t_data.get("series", [])
    t_lbls  = t_data.get("labels", MONTH_LABELS)
    trend_label, trend_color = _trend_class(t_series)

    nps_g = wf.get("nps_curr"); nps_p = wf.get("nps_prev")
    delta_mm = round(nps_g - nps_p, 2) if nps_g is not None and nps_p is not None else None
    d_tgt = wf.get("delta_tgt"); var = wf.get("var")
    tgt   = wf.get("target", NPS_TARGET)

    pos_data = pa.get("top_pos")
    neg_data = pa.get("top_neg")
    same_proc = pos_data and neg_data and pos_data.get("proc") == neg_data.get("proc")

    def _proc_card(proc_info, role):
        if not proc_info: return ""
        proc   = proc_info["proc"]
        delta  = proc_info.get("delta", 0)
        share  = proc_info.get("share", 0)
        nps_m  = proc_info.get("nps_mai")
        nps_a  = proc_info.get("nps_abr")
        detail = proc_info.get("detail", {})
        trxs   = proc_info.get("transcripts", {})
        nps_tot= detail.get("nps_total")
        surv   = detail.get("ts", 0)

        card_cls = "exec-card-pos" if role == "pos" else "exec-card-neg"
        icon     = "🟢" if role == "pos" else "🔴"
        title    = f"{icon} {'Processo de Alta' if role=='pos' else 'Processo de Queda'}"

        # Header do processo
        hdr = (f'<div class="exec-card {card_cls}" style="margin-bottom:12px">'
               f'<div class="exec-label">{esc(proc)}</div>'
               f'<div style="font-size:12px;margin-top:4px;display:flex;flex-wrap:wrap;gap:12px">'
               f'<span>NPS {esc(lCURR)}: <strong>{fn(nps_m)}%</strong></span>'
               f'<span>NPS {esc(lPREV)}: <strong>{fn(nps_a)}%</strong></span>'
               f'<span>{chip(delta, "pp &#916;M/M")}</span>'
               f'<span style="color:#888">{share:.1f}% do volume do driver &nbsp;|&nbsp; {surv:,} pesquisas</span>'
               f'</div></div>')

        # Grid: CDU | Solução | Seniority
        cdu_tbl = _dim_table(detail.get("cdu",{}), 4, "CDU")
        sol_tbl = _dim_table(detail.get("sol",{}), 4, "Solução")
        sen_tbl = _dim_table(detail.get("seniority",{}), 3, "Senioridade")

        # Motivos
        if role == "neg":
            motivos_html = (f'<div style="margin-top:6px">'
                            f'<div class="bd-sec-title">Principais motivos de detração</div>'
                            f'{_reason_list(detail.get("det_reasons",{}), 4, "#a01010")}'
                            f'</div>')
        else:
            motivos_html = (f'<div style="margin-top:6px">'
                            f'<div class="bd-sec-title">Principais motivos de promoção</div>'
                            f'{_reason_list(detail.get("pro_reasons",{}), 4, "#1a7a42")}'
                            f'</div>')

        grid = (f'<div class="bd-grid" style="margin-bottom:12px">'
                f'<div class="bd-sec"><div class="bd-sec-title">CDU</div>{cdu_tbl}</div>'
                f'<div class="bd-sec"><div class="bd-sec-title">Solução</div>{sol_tbl}</div>'
                f'<div class="bd-sec"><div class="bd-sec-title">Newbie vs Veterano</div>{sen_tbl}</div>'
                f'<div class="bd-sec">{motivos_html}</div>'
                f'</div>')

        # Transcrições
        trx_bullets = _trx_bullets(trxs)
        trx_sec = ""
        if trx_bullets:
            trx_sec = (f'<div style="margin-bottom:12px">'
                       f'<div class="bd-sec-title" style="color:#3483FA">&#128172; Avaliação das transcrições ({len(trxs)} casos)</div>'
                       f'{trx_bullets}</div>')

        return f'<div class="exec-section"><div class="exec-title">{title}</div>{hdr}{grid}{trx_sec}</div>'

    pos_card = _proc_card(pos_data, "pos") if not same_proc else ""
    neg_card = _proc_card(neg_data, "neg")

    # ── Seção 1: Resumo Executivo ────────────────────────────────────
    role_str = ("uma das principais <strong>alavancas positivas</strong>"
                if grp in top_pos_list else
                ("uma das principais <strong>causas de queda</strong>"
                 if grp in top_neg_list else "um driver em monitoramento"))

    delta_txt = (f"{('+'if delta_mm>=0 else '')}{fn(delta_mm)}pp MoM") if delta_mm is not None else ""
    trend_tag = f'<span style="color:{trend_color};font-weight:700">{trend_label}</span>'

    # Causa dominante
    if dominant_dim == "Processo" and pa_neg:
        causa = (f"A variação é explicada principalmente pelo <strong>processo {esc(pa_neg['proc'])}</strong> "
                 f"({pa_neg.get('share',0):.1f}% do volume, NPS {fn(pa_neg.get('nps_mai'))}%, "
                 f"Δ={pa_neg.get('delta',0):+.1f}pp MoM)")
    elif dominant_dim == "Canal" and top_canal:
        item, c, n1, n2, s = top_canal[0]
        causa = (f"A variação é explicada principalmente pelo <strong>canal {esc(item)}</strong> "
                 f"(NPS {fn(n1)}% vs {fn(n2)}% no mês anterior, contribuição {c:+.2f}pp)")
    elif dominant_dim == "Senioridade" and top_sen:
        item, c, n1, n2, s = top_sen[0]
        causa = (f"A variação é explicada principalmente por <strong>atendentes {esc(item)}</strong> "
                 f"(NPS {fn(n1)}% vs {fn(n2)}% no mês anterior, contribuição {c:+.2f}pp)")
    else:
        causa = "A causa principal da variação não pôde ser isolada com os dados disponíveis"

    status_color = "#00A650" if d_tgt is not None and d_tgt >= 0 else "#E84142"
    status_txt = (f'{("+"if d_tgt>=0 else "")}{fn(d_tgt)}pp vs target'
                  if d_tgt is not None else "")

    p1 = (f"<strong>{esc(grp)}</strong> é {role_str} no período {esc(lPREV)}→{esc(lCURR)}, "
          f"com NPS de <strong>{fn(nps_g)}%</strong> ({delta_txt}). "
          f"A tendência histórica é {trend_tag} com base nos últimos 5 meses. "
          + (f'<span style="color:{status_color};font-weight:600">{status_txt}.</span>' if status_txt else ""))
    p2 = f"{causa}."

    # Padrões qualitativos identificados
    opp_bullets = ""
    for pat, evidences in qual_patterns.items():
        if not evidences: continue
        is_neg = any(k in pat.lower() for k in ["mudança","sem resolução","sistêmico","demora"])
        c_icon = "🔴" if is_neg else "🟢"
        ev_txt = f' — <em>&ldquo;{esc(evidences[0][:100])}&rdquo;</em>' if evidences else ""
        opp_bullets += f'<div class="exec-bullet">{c_icon} <strong>{esc(pat)}</strong>{ev_txt}</div>'

    opp_sec = ""
    if opp_bullets:
        p3 = (f"Padrões identificados nos comentários e transcrições: "
              f"{'oportunidades de melhoria' if any('sem resol' in p.lower() or 'demora' in p.lower() for p in qual_patterns) else 'indicadores positivos'} "
              f"confirmados abaixo.")
        opp_sec = (f'<div style="margin-top:8px">'
                   f'<div style="font-size:11px;font-weight:700;color:#555;margin-bottom:6px">'
                   f'Padr&#245;es qualitativos identificados:</div>'
                   f'{opp_bullets}</div>')
    else:
        p3 = ""

    resumo_body = f'<p>{p1}</p><p>{p2}</p>' + (f'<p style="font-size:12px;color:#555">{p3}</p>' if p3 else "")
    resumo = (f'<div class="exec-section">'
              f'<div class="exec-title">&#128203; Resumo Executivo &mdash; {esc(grp)}</div>'
              f'<div class="exec-body">{resumo_body}</div>'
              f'{opp_sec}</div>')

    # ── Seção 2: Diagnóstico Dimensional ────────────────────────────
    def _dim_card(label, contribs, icon):
        if not contribs: return ""
        rows = ""
        for item, c, n1, n2, s in contribs[:3]:
            d_cls = "bd-pos" if c > 0 else "bd-neg"
            rows += (f'<tr><td class="bd-name">{esc(item[:35])}</td>'
                     f'<td class="bd-nps">{fn(n1)}%</td>'
                     f'<td class="bd-nps" style="color:#aaa">{fn(n2)}%</td>'
                     f'<td class="bd-delta {d_cls}">{c:+.2f}pp</td></tr>')
        tbl = (f'<table class="bd-tbl"><thead>'
               f'<tr><th>{icon} {esc(label)}</th><th>{esc(lCURR)}</th>'
               f'<th>{esc(lPREV)}</th><th>Contrib</th></tr>'
               f'</thead><tbody>{rows}</tbody></table>')
        is_dom = (label == dominant_dim)
        border = f"border:2px solid {color}" if is_dom else ""
        tag = f'<span style="background:{color};color:#fff;font-size:9px;padding:1px 6px;border-radius:8px;margin-left:6px">DOMINANTE</span>' if is_dom else ""
        return (f'<div class="exec-card" style="background:#fafbfc;{border}">'
                f'<div class="exec-label">{esc(label)}{tag}</div>{tbl}</div>')

    proc_dim_card = ""
    if pa_neg:
        proc_row = (f'<tr><td class="bd-name">{esc(pa_neg["proc"][:35])}</td>'
                    f'<td class="bd-nps">{fn(pa_neg.get("nps_mai"))}%</td>'
                    f'<td class="bd-nps" style="color:#aaa">{fn(pa_neg.get("nps_abr"))}%</td>'
                    f'<td class="bd-delta {"bd-pos" if pa_neg.get("contrib",0)>0 else "bd-neg"}">{pa_neg.get("contrib",0):+.3f}pp</td></tr>')
        if pa_pos and not same_proc:
            proc_row += (f'<tr><td class="bd-name">{esc(pa_pos["proc"][:35])}</td>'
                         f'<td class="bd-nps">{fn(pa_pos.get("nps_mai"))}%</td>'
                         f'<td class="bd-nps" style="color:#aaa">{fn(pa_pos.get("nps_abr"))}%</td>'
                         f'<td class="bd-delta bd-pos">{pa_pos.get("contrib",0):+.3f}pp</td></tr>')
        proc_tbl = (f'<table class="bd-tbl"><thead>'
                    f'<tr><th>📋 Processo</th><th>{esc(lCURR)}</th>'
                    f'<th>{esc(lPREV)}</th><th>Contrib</th></tr>'
                    f'</thead><tbody>{proc_row}</tbody></table>')
        is_dom = (dominant_dim == "Processo")
        tag = f'<span style="background:{color};color:#fff;font-size:9px;padding:1px 6px;border-radius:8px;margin-left:6px">DOMINANTE</span>' if is_dom else ""
        border = f"border:2px solid {color}" if is_dom else ""
        proc_dim_card = (f'<div class="exec-card" style="background:#fafbfc;{border}">'
                         f'<div class="exec-label">Processo{tag}</div>{proc_tbl}</div>')

    canal_dim_card = _dim_card("Canal", top_canal, "📱")
    sen_dim_card   = _dim_card("Senioridade", top_sen, "🎓")

    dim_cards = "".join(c for c in [proc_dim_card, canal_dim_card, sen_dim_card] if c)
    diag_sec = (f'<div class="exec-section">'
                f'<div class="exec-title">&#128270; Diagn&#243;stico Dimensional &mdash; '
                f'Causa da Varia&#231;&#227;o M/M <span style="font-size:11px;font-weight:400;color:#888">'
                f'({esc(lPREV)} &rarr; {esc(lCURR)})</span></div>'
                f'<div class="exec-cards">{dim_cards}</div>'
                f'</div>') if dim_cards else ""

    # ── Seção 3: Tendência histórica ─────────────────────────────────
    # Aba semanal: usa série semanal (WEEK_LABELS + grp_wk) em vez de mensal
    if mode == "weekly":
        t_lbls   = WEEK_LABELS
        t_series = grp_wk.get(grp, [None] * len(WEEK_LABELS))
        lCURR_trend = esc(S1_LABEL) if S1_LABEL else lCURR
        delta_unit  = "WoW"
    else:
        lCURR_trend = lCURR
        delta_unit  = "M/M"

    rec_rows = ""
    for i, (lbl, val) in enumerate(zip(t_lbls, t_series)):
        if val is None: continue
        prev_val = next((t_series[j] for j in range(i-1,-1,-1) if t_series[j] is not None), None)
        dv = round(val - prev_val, 1) if prev_val is not None else None
        d_cls = "bd-pos" if dv and dv > 0 else ("bd-neg" if dv and dv < 0 else "")
        d_str = (("+" if dv > 0 else "") + f"{dv:.1f}pp") if dv else "—"
        bold  = "font-weight:700;" if lbl == lCURR else ""
        is_below_tgt = val < tgt - 3
        bg = ";background:#fff8f8" if is_below_tgt else ""
        rec_rows += (f'<tr style="{bold}{bg}"><td class="bd-name">{esc(lbl)}</td>'
                     f'<td class="bd-nps">{fn(val)}%</td>'
                     f'<td class="bd-delta {d_cls}">{d_str}</td>'
                     f'<td class="bd-vol" style="color:#888">'
                     f'{"&#9660; abaixo tgt" if is_below_tgt else "&#9989; ok"}'
                     f'</td></tr>')
    period_lbl = "Semana" if mode == "weekly" else "M&#234;s"
    rec_sec = (f'<div class="exec-section">'
               f'<div class="exec-title">&#128260; Tend&#234;ncia Hist&#243;rica &mdash; '
               f'{trend_tag} <span style="font-size:11px;font-weight:400;color:#888">(target: {fn(tgt)}%)</span>'
               f'</div>'
               f'<table class="bd-tbl" style="max-width:360px">'
               f'<thead><tr><th>{period_lbl}</th><th>NPS</th>'
               f'<th>&#916; {delta_unit}</th><th>vs Target</th></tr></thead>'
               f'<tbody>{rec_rows}</tbody></table>'
               f'</div>')

    quant_sec = _quant_section_html(grp)
    return resumo + diag_sec + quant_sec + neg_card + pos_card + rec_sec

def _analyze_transcripts(transcripts):
    """
    Analisa o conteúdo real das transcrições e retorna padrões identificados.
    Retorna dict com contagens e exemplos por padrão.
    """
    if not transcripts:
        return None

    total = len(transcripts)
    patterns = {
        "transferencia":        {"n": 0, "ex": []},
        "sem_resolucao":        {"n": 0, "ex": []},
        "reincidencia":         {"n": 0, "ex": []},
        "escalacao_legal":      {"n": 0, "ex": []},
        "resposta_automatica":  {"n": 0, "ex": []},
        "resolucao_ok":         {"n": 0, "ex": []},
        "empatia_rep":          {"n": 0, "ex": []},
        "demora_atendimento":   {"n": 0, "ex": []},
    }

    KW = {
        "transferencia":      ["transfiro", "encaminhar para", "vou te transferir", "outro atendente",
                               "equipe especializada", "outro canal", "fale conosco"],
        "sem_resolucao":      [],   # inferido por ausência de resolução
        "reincidencia":       ["já abri", "já tentei", "segunda vez", "terceira vez", "desde ontem",
                               "já entrei em contato", "semanas", "meses tentando", "abri chamado"],
        "escalacao_legal":    ["procon", "judicial", "advogado", "reclamação formal", "ação judicial",
                               "ouvidoria", "vou processar", "vou acionar"],
        "resposta_automatica":["para continuar", "qual opção", "pode me informar",
                               "para te direcionar", "preciso de um contexto"],
        "resolucao_ok":       ["resolvido", "solucionado", "feito", "problema resolvido",
                               "concluído", "encerrado com sucesso", "ok, resolvemos"],
        "empatia_rep":        ["entendo sua frustração", "lamento", "me desculpe", "sinto muito",
                               "entendo sua situação", "peço desculpas", "compreendo"],
        "demora_atendimento": ["ainda online", "continua no chat", "aguardando", "esperando",
                               "hora", "mais de uma hora", "30 minutos"],
    }

    for cid, txt in transcripts.items():
        tl = txt.lower()
        lines_rep = [l for l in txt.split("\n") if l.startswith("[REP]")]
        lines_usr = [l for l in txt.split("\n") if l.startswith("[USER]")]
        usr_text  = " ".join(l[7:] for l in lines_usr)

        found_transfer  = any(k in tl for k in KW["transferencia"])
        found_resolucao = any(k in tl for k in KW["resolucao_ok"])
        found_reinci    = any(k in tl for k in KW["reincidencia"])
        found_escal     = any(k in tl for k in KW["escalacao_legal"])
        found_auto      = sum(1 for m in lines_rep if len(m) > 250) >= 2  # 2+ mensagens longas de bot
        found_empatia   = any(k in tl for k in KW["empatia_rep"])
        found_demora    = any(k in tl for k in KW["demora_atendimento"])

        if found_transfer:
            patterns["transferencia"]["n"] += 1
            if not patterns["transferencia"]["ex"] and usr_text:
                patterns["transferencia"]["ex"].append(usr_text[:100])
        if not found_resolucao:
            patterns["sem_resolucao"]["n"] += 1
        else:
            patterns["resolucao_ok"]["n"] += 1
        if found_reinci:
            patterns["reincidencia"]["n"] += 1
            if not patterns["reincidencia"]["ex"] and usr_text:
                patterns["reincidencia"]["ex"].append(usr_text[:100])
        if found_escal:
            patterns["escalacao_legal"]["n"] += 1
            if not patterns["escalacao_legal"]["ex"] and usr_text:
                patterns["escalacao_legal"]["ex"].append(usr_text[:120])
        if found_auto:
            patterns["resposta_automatica"]["n"] += 1
        if found_empatia:
            patterns["empatia_rep"]["n"] += 1
        if found_demora:
            patterns["demora_atendimento"]["n"] += 1

    return {"total": total, "patterns": patterns}

def _trx_summary_html(grp):
    """Gera seção exec-section com resumo + bullets baseados em transcrições."""
    qual        = _EXEC.get("qual", {}).get(grp, {})
    transcripts = qual.get("transcripts", {})
    comments    = qual.get("comments", [])

    analysis = _analyze_transcripts(transcripts)
    if not analysis:
        return (f'<div class="exec-section">'
                f'<div class="exec-title">&#128172; Avalia&#231;&#227;o das Transcri&#231;&#245;es</div>'
                f'<div class="exec-no-data">Transcrições não disponíveis para este driver. '
                f'Execute <code>python _fetch_exec_data.py</code> para gerar.</div></div>')

    total = analysis["total"]
    P     = analysis["patterns"]

    # Resumo narrativo baseado nos padrões dominantes
    dominant = []
    if P["sem_resolucao"]["n"] > total * 0.5:
        dominant.append(f"<strong>{P['sem_resolucao']['n']} de {total}</strong> casos sem indicação de resolução no encerramento")
    if P["transferencia"]["n"]:
        dominant.append(f"<strong>{P['transferencia']['n']}</strong> caso{'s' if P['transferencia']['n']>1 else ''} com transferência para outro atendente ou canal")
    if P["reincidencia"]["n"]:
        dominant.append(f"<strong>{P['reincidencia']['n']}</strong> caso{'s' if P['reincidencia']['n']>1 else ''} com reincidência — seller já havia tentado resolver anteriormente")
    if P["escalacao_legal"]["n"]:
        dominant.append(f"<strong>{P['escalacao_legal']['n']}</strong> caso{'s' if P['escalacao_legal']['n']>1 else ''} com risco de escal. legal (PROCON / ação judicial)")
    if P["resposta_automatica"]["n"] > total * 0.3:
        dominant.append(f"<strong>{P['resposta_automatica']['n']}</strong> casos com padrão de resposta automatizada sem análise específica do problema")

    positivos = []
    if P["resolucao_ok"]["n"]:
        positivos.append(f"<strong>{P['resolucao_ok']['n']}</strong> casos com resolução identificada na conversa")
    if P["empatia_rep"]["n"] > total * 0.2:
        positivos.append(f"<strong>{P['empatia_rep']['n']}</strong> casos com linguagem empática do atendente")

    # Texto do resumo
    if P["sem_resolucao"]["n"] > P["resolucao_ok"]["n"]:
        tom = "predominantemente <strong>não resolutivo</strong>"
    else:
        tom = "predominantemente <strong>resolutivo</strong>"

    resumo_txt = (f"Em <strong>{total} transcrições</strong> analisadas, o padrão geral é {tom}. "
                  + (f"{', '.join(dominant[:2])}." if dominant else "Sem padrão negativo dominante identificado."))

    # Bullets negativos
    neg_bullets = "".join(
        f'<div class="exec-bullet">{item}</div>' for item in dominant
    ) or '<div class="exec-bullet" style="color:#aaa">Nenhum padrão negativo dominante identificado nas transcrições.</div>'

    # Bullets positivos
    pos_bullets = "".join(
        f'<div class="exec-bullet">{item}</div>' for item in positivos
    ) if positivos else ""

    # Card principal
    card_cls = "exec-card-neg" if P["sem_resolucao"]["n"] > P["resolucao_ok"]["n"] else "exec-card-pos"

    card = (f'<div class="exec-card {card_cls}">'
            f'<div class="exec-label">{esc(grp)} — {total} transcrições analisadas</div>'
            f'<div class="exec-body" style="font-size:12px;margin:6px 0"><p>{resumo_txt}</p></div>'
            f'<div style="margin-top:8px;font-size:11px;font-weight:700;color:#555;margin-bottom:4px">Pontos de aten&#231;&#227;o:</div>'
            f'{neg_bullets}'
            + (f'<div style="margin-top:8px;font-size:11px;font-weight:700;color:#555;margin-bottom:4px">Pontos positivos:</div>{pos_bullets}' if pos_bullets else "")
            + f'</div>')

    return (f'<div class="exec-section">'
            f'<div class="exec-title">&#128172; Avalia&#231;&#227;o das Transcri&#231;&#245;es</div>'
            f'{card}</div>')

def _drv_analysis_html(grp):
    """Gera seções de análise executiva por driver: resumo, recorrência, alavancas/causas, target."""
    wf   = _EXEC.get("waterfall", {}).get(grp, {})
    qual = _EXEC.get("qual", {}).get(grp, {})
    trend = _EXEC.get("nps_trend", {}).get(grp, {})
    top_neg = _EXEC.get("top_neg", [])
    top_pos = _EXEC.get("top_pos", [])
    lCURR   = _EXEC.get("lCURR", MONTH_LABELS[-1])
    lPREV   = _EXEC.get("lPREV", MONTH_LABELS[-2])

    nps_c = wf.get("nps_curr")
    nps_p = wf.get("nps_prev")
    tgt   = wf.get("target", NPS_TARGET)
    d_tgt = wf.get("delta_tgt")
    var   = wf.get("var")

    # ── Recorrência ──────────────────────────────────────────────────
    t_series = trend.get("series", [])
    t_labels = trend.get("labels", MONTH_LABELS)
    t_trend  = trend.get("trend", "indefinido")
    rec_rows = ""
    for i, (lbl, val) in enumerate(zip(t_labels, t_series)):
        if val is None: continue
        prev_val = next((t_series[j] for j in range(i-1, -1, -1) if t_series[j] is not None), None)
        delta_v  = round(val - prev_val, 1) if prev_val is not None else None
        d_cls    = "bd-pos" if delta_v and delta_v > 0 else ("bd-neg" if delta_v and delta_v < 0 else "")
        d_str    = (("+" if delta_v > 0 else "") + f"{delta_v:.1f}pp") if delta_v else "—"
        is_curr  = lbl == lCURR
        bold     = "font-weight:700;" if is_curr else ""
        rec_rows += (f'<tr style="{bold}">'
                     f'<td class="bd-name">{esc(lbl)}</td>'
                     f'<td class="bd-nps">{fn(val)}%</td>'
                     f'<td class="bd-delta {d_cls}">{d_str}</td>'
                     f'<td class="bd-vol" style="color:#888;">'
                     f'{"← atual" if lbl==lCURR else ("← prev" if lbl==lPREV else "")}</td>'
                     f'</tr>\n')

    trend_badge_map = {
        "alta":   ('<span style="color:#00A650;font-weight:700">&#8593; Alta</span>', "#00A650"),
        "queda":  ('<span style="color:#E84142;font-weight:700">&#8595; Queda</span>', "#E84142"),
        "estavel":('<span style="color:#888;font-weight:700">&#8594; Estável</span>', "#888"),
    }
    badge_html, _ = trend_badge_map.get(t_trend, ("—", "#aaa"))

    rec_sec = f"""<div class="exec-section">
  <div class="exec-title">&#128260; Recorr&#234;ncia &mdash; Tend&#234;ncia: {badge_html}</div>
  <table class="bd-tbl" style="max-width:360px">
    <thead><tr><th>M&#234;s</th><th>NPS</th><th>&#916; M/M</th><th></th></tr></thead>
    <tbody>{rec_rows}</tbody>
  </table>
</div>"""

    # ── Resumo do driver ──────────────────────────────────────────────
    role = "positivo" if grp in top_pos else ("negativo" if grp in top_neg else "neutro")
    d_tgt_txt = (("+" if d_tgt and d_tgt >= 0 else "") + f"{d_tgt:.1f}pp vs target") if d_tgt else ""
    var_txt   = (("+" if var and var >= 0 else "") + f"{var:.2f}pp contribuição") if var else ""

    trend_desc = {"alta": "em alta sustentada", "queda": "em queda recorrente",
                  "estavel": "estável", "indefinido": "com tendência indefinida"}.get(t_trend, "")

    if role == "positivo":
        intro = f"<strong>{esc(grp)}</strong> é uma das principais <strong>alavancas positivas</strong> do período ({var_txt}), com NPS de {fn(nps_c)}% no {esc(lCURR)} e tendência {trend_desc}."
    elif role == "negativo":
        intro = f"<strong>{esc(grp)}</strong> é uma das principais <strong>causas de queda</strong> do período ({var_txt}), com NPS de {fn(nps_c)}% no {esc(lCURR)} e tendência {trend_desc}."
    else:
        intro = f"<strong>{esc(grp)}</strong> registrou NPS de <strong>{fn(nps_c)}%</strong> no {esc(lCURR)} ({var_txt}), {trend_desc}."

    if d_tgt_txt:
        status_color = "#00A650" if d_tgt and d_tgt >= 0 else "#E84142"
        intro += f' <span style="color:{status_color};font-weight:600">{d_tgt_txt}.</span>'

    resumo_sec = (f'<div class="exec-section">'
                  f'<div class="exec-title">&#128203; Resumo Executivo &mdash; {esc(grp)}</div>'
                  f'<div class="exec-body"><p>{intro}</p></div>'
                  f'</div>')

    # ── Síntese qualitativa ───────────────────────────────────────────
    comments   = qual.get("comments", [])
    transcripts= qual.get("transcripts", {})
    dets = [c for c in comments if c.get("perfil") == "detrator"]
    pros = [c for c in comments if c.get("perfil") == "promotor"]

    _GENERIC = {"péssimo","ótimo","ok","bom","ruim","horrível","excelente",
                "top","nao","não","sim","","regular","boa","boa,","gostei"}

    def _best_comment(items):
        """Retorna o comentário mais informativo (mais longo e específico)."""
        cands = [c.get("comment","") for c in items
                 if c.get("comment") and len(c.get("comment","").strip()) > 20
                 and c.get("comment","").strip().lower() not in _GENERIC]
        if not cands: return None
        return max(cands, key=len)

    def _cdu_synthesis(items):
        """Agrupa por CDU e sintetiza o padrão dominante de cada grupo."""
        clusters = {}
        for c in items:
            cdu = c.get("cdu","N/I")
            clusters.setdefault(cdu, []).append(c)
        top = sorted(clusters.items(), key=lambda x: -len(x[1]))[:3]
        results = []
        for cdu, clist in top:
            n   = len(clist)
            best= _best_comment(clist)
            sol_freq = {}
            for c in clist:
                s = c.get("sol","") or c.get("solucao","")
                if s: sol_freq[s] = sol_freq.get(s, 0) + 1
            top_sol = sorted(sol_freq.items(), key=lambda x: -x[1])
            sol_str = f" — solução recorrente: <em>{esc(top_sol[0][0][:50])}</em>" if top_sol else ""
            results.append((cdu, n, best, sol_str))
        return results

    def _trx_pattern(transcripts, det_ids):
        """Extrai o padrão de interação da transcrição mais informativa."""
        for cid, txt in transcripts.items():
            if cid not in det_ids: continue
            lines = [l.strip() for l in txt.split("\n") if l.strip() and len(l.strip()) > 10]
            user_msgs = [l[7:] for l in lines if l.startswith("[USER]")]
            rep_msgs  = [l[6:]  for l in lines if l.startswith("[REP]")]
            if user_msgs and rep_msgs:
                u = max(user_msgs, key=len)[:150]
                r = max(rep_msgs,  key=len)[:150]
                return u, r
        return None, None

    def _pro_themes(items):
        """Identifica temas positivos dominantes nos promotores."""
        keywords = {
            "agilidade":    ["rápido","ágil","agilidade","rapido"],
            "empatia":      ["gentil","atenciosa","atencioso","simpática","educado","empático"],
            "resolução":    ["resolveu","solucionou","resolvido","solucionado","funciona"],
            "clareza":      ["claro","clara","explicou","explicado","entendeu"],
            "eficiência":   ["eficiente","eficiência","eficaz","objetivo"],
        }
        counts = {t: 0 for t in keywords}
        for c in items:
            txt = (c.get("comment") or "").lower()
            for theme, kws in keywords.items():
                if any(k in txt for k in kws):
                    counts[theme] += 1
        return sorted(counts.items(), key=lambda x: -x[1])

    # ── Principais Causas de Queda (exec-card-neg por CDU) ──────────
    if dets:
        synth    = _cdu_synthesis(dets)
        det_ids  = {c.get("cid") for c in dets if c.get("cid")}
        u_msg, r_msg = _trx_pattern(transcripts, det_ids)

        cdu_cards = ""
        for cdu, n, best_c, sol_str in synth:
            trx_block = ""
            if u_msg and r_msg and synth.index((cdu,n,best_c,sol_str)) == 0:
                trx_block = (f'<div class="exec-evidence" style="margin-top:6px">'
                             f'<strong>Padr&#227;o nas transcri&#231;&#245;es &mdash;</strong> '
                             f'<em>Seller:</em> &ldquo;{esc(u_msg[:120])}&rdquo; &nbsp;'
                             f'<em>Atendente:</em> &ldquo;{esc(r_msg[:120])}&rdquo;</div>')
            evidence = ""
            if best_c:
                evidence = f'<div class="exec-evidence">&ldquo;{esc(best_c[:200])}&rdquo;</div>'
            cdu_cards += (f'<div class="exec-card exec-card-neg">'
                          f'<div class="exec-label">{esc(cdu)} '
                          f'<span style="font-weight:400;color:#888;font-size:11px">({n} caso{"s" if n>1 else ""})</span>'
                          f'</div>'
                          + (f'<div style="font-size:11px;color:#888;margin-bottom:4px">{sol_str[4:]}</div>' if sol_str else "")
                          + evidence + trx_block
                          + f'</div>')

        det_sec = (f'<div class="exec-section">'
                   f'<div class="exec-title">&#128308; Principais Causas de Queda '
                   f'<span style="font-weight:400;font-size:11px;color:#888">({len(dets)} detratores analisados)</span></div>'
                   f'<div class="exec-cards">{cdu_cards}</div></div>')
    else:
        det_sec = ""

    # ── Principais Alavancas de Alta (exec-card-pos) ─────────────────
    if pros:
        themes    = _pro_themes(pros)
        top_t     = [(t, n) for t, n in themes if n > 0][:4]
        best_pro  = _best_comment(pros)

        bullets = "".join(
            f'<div class="exec-bullet"><strong>{esc(t.capitalize())}:</strong> '
            f'citado em {n} de {len(pros)} avalia&#231;&#245;es positivas</div>'
            for t, n in top_t
        ) if top_t else '<div class="exec-bullet">Avalia&#231;&#245;es positivas sem tema dominante identificado.</div>'

        evidence = f'<div class="exec-evidence">&ldquo;{esc(best_pro[:200])}&rdquo;</div>' if best_pro else ""

        pro_sec = (f'<div class="exec-section">'
                   f'<div class="exec-title">&#128994; Principais Alavancas de Alta '
                   f'<span style="font-weight:400;font-size:11px;color:#888">({len(pros)} promotores analisados)</span></div>'
                   f'<div class="exec-card exec-card-pos">'
                   f'<div class="exec-label">O que os promotores valorizam</div>'
                   f'{bullets}{evidence}</div></div>')
    else:
        pro_sec = ""

    # ── Driver Fora do Target ─────────────────────────────────────────
    if d_tgt is not None:
        tgt_cls   = "exec-card-pos" if d_tgt >= 0 else ("exec-card-warn" if d_tgt >= -5 else "exec-card-neg")
        tgt_label = "Acima &#x2713;" if d_tgt >= 0 else ("Pr&#243;ximo (~)" if d_tgt >= -3 else ("Abaixo &#9660;" if d_tgt >= -10 else "Cr&#237;tico &#x2717;"))
        tgt_sec = (f'<div class="exec-section">'
                   f'<div class="exec-title">&#127919; Status vs Target</div>'
                   f'<div class="exec-card {tgt_cls}">'
                   f'<div class="exec-label">{esc(grp)} &nbsp; '
                   f'{chip(d_tgt)} &nbsp; {tgt_label}</div>'
                   f'<div style="font-size:12px;margin-top:4px">'
                   f'NPS {esc(lCURR)}: <strong>{fn(nps_c)}%</strong> &nbsp;|&nbsp; '
                   f'Target: <strong>{fn(tgt)}%</strong></div>'
                   f'</div></div>')
    else:
        tgt_sec = ""

    if not comments:
        det_sec = (f'<div class="exec-section">'
                   f'<div class="exec-title">&#9432; An&#225;lise Qualitativa</div>'
                   f'<div class="exec-no-data">Dados qualitativos n&#227;o dispon&#237;veis. '
                   f'Execute <code>python _fetch_exec_data.py</code> para gerar.</div></div>')
        pro_sec = ""

    trx_sec = _trx_summary_html(grp)
    return f'<div class="bd-analysis exec-wrap">{resumo_sec}{rec_sec}{trx_sec}{pro_sec}{det_sec}{tgt_sec}</div>'

def _bd_table(items_m1, items_m2, max_rows=6):
    """Mini-tabela: Nome | NPS M1 | Δ M/M | Volume."""
    rows = ""
    sorted_items = sorted(items_m1.items(), key=lambda x: -x[1]["s"])[:max_rows]
    for name, v1 in sorted_items:
        v2    = items_m2.get(name)
        nps1  = v1["nps"]
        delta = round(nps1 - v2["nps"], 1) if v2 and v2["nps"] is not None and nps1 is not None else None
        d_cls = "bd-pos" if delta is not None and delta > 0 else ("bd-neg" if delta is not None and delta < 0 else "")
        d_str = (("+" if delta > 0 else "") + f"{delta:.1f}pp") if delta is not None else "—"
        rows += (f'<tr><td class="bd-name">{esc(name[:38])}</td>'
                 f'<td class="bd-nps">{fn(nps1) if nps1 is not None else "—"}%</td>'
                 f'<td class="bd-delta {d_cls}">{d_str}</td>'
                 f'<td class="bd-vol">{v1["s"]:,}</td></tr>\n')
    return (f'<table class="bd-tbl">'
            f'<thead><tr><th>Nome</th><th>NPS</th><th>&#916; M/M</th><th>Vol</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')

def _bd_seniority(sr_m1, sr_m2):
    rows = ""
    for key in ["Expert", "Newbie", "Training"]:
        v1 = sr_m1.get(key)
        v2 = sr_m2.get(key) if sr_m2 else None
        if not v1: continue
        nps1  = v1["nps"]
        delta = round(nps1 - v2["nps"], 1) if v2 and v2["nps"] is not None and nps1 is not None else None
        d_cls = "bd-pos" if delta and delta > 0 else ("bd-neg" if delta and delta < 0 else "")
        d_str = (("+" if delta > 0 else "") + f"{delta:.1f}pp") if delta is not None else "—"
        rows += (f'<tr><td class="bd-name">{esc(key)}</td>'
                 f'<td class="bd-nps">{fn(nps1) if nps1 is not None else "—"}%</td>'
                 f'<td class="bd-delta {d_cls}">{d_str}</td>'
                 f'<td class="bd-vol">{v1["s"]:,}</td></tr>\n')
    return (f'<table class="bd-tbl">'
            f'<thead><tr><th>Seniority</th><th>NPS</th><th>&#916; M/M</th><th>Vol</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')

def _build_driver_breakdowns(mode="monthly"):
    """
    mode='monthly': usa grp_breakdown (Mai vs Abr), comparação M/M
    mode='weekly':  usa grp_wk_bd (S1 vs S2), comparação W/W
    """
    if mode == "weekly":
        bd_src  = grp_wk_bd
        lM1     = esc(S1_LABEL)
        lM2     = esc(S2_LABEL)
        nps_curr_fn  = lambda g: grp_wk[g][-1]  if grp_wk.get(g) else None
        nps_prev_fn  = lambda g: grp_wk[g][-2]  if grp_wk.get(g) and len(grp_wk[g])>=2 else None
        section_title = f"An&#225;lise por Driver &mdash; {esc(S1_LABEL)} vs {esc(S2_LABEL)}"
        cid_prefix = "wk"
    else:
        bd_src  = grp_breakdown
        lM1     = esc(MONTH_LABELS[-1])
        lM2     = esc(MONTH_LABELS[-2])
        nps_curr_fn  = lambda g: grp_mon[g][-2]  if grp_mon.get(g) else None
        nps_prev_fn  = lambda g: grp_mon[g][-3]  if grp_mon.get(g) and len(grp_mon[g])>=3 else None
        section_title = f"An&#225;lise por Driver &mdash; {esc(MONTH_LABELS[-1])} vs {esc(MONTH_LABELS[-2])}"
        cid_prefix = "mn"

    # Botões de filtro — sem "Todos", primeiro driver ativo por padrão
    pfx   = f"{cid_prefix}-"    # prefixo para evitar colisão de IDs entre abas
    first = True
    btns  = ""
    for grp in DRIVER_GROUPS:
        slug = pfx + grp.replace(" ", "-").replace("/", "-").replace(".", "")
        active_cls = " active" if first else ""
        btns += (f'<button class="drv-fbtn{active_cls}" data-grp="{slug}" '
                 f'onclick="filterDrv(this,\'{slug}\')">{esc(grp)}</button>')
        first = False

    filter_bar = f'<div class="drv-fbar">{btns}</div>'

    delta_lbl = "WoW" if mode == "weekly" else "MoM"

    cards = ""
    for grp, drvs in DRIVER_GROUPS.items():
        slug  = pfx + grp.replace(" ", "-").replace("/", "-").replace(".", "")
        color = GROUP_COLORS.get(grp, "#aaa")
        bd    = bd_src.get(grp, {})

        g_nps  = nps_curr_fn(grp)
        g_prev = nps_prev_fn(grp)
        g_tgt  = grp_targets.get(grp, NPS_TARGET)
        g_delta = round(g_nps - g_prev, 1) if g_nps is not None and g_prev is not None else None
        g_dtgt  = round(g_nps - g_tgt,  1) if g_nps is not None else None

        hdr = (f'<div class="bd-hdr" style="border-left:5px solid {color}">'
               f'<span class="bd-grp-name">{esc(grp)}</span>'
               f'<span class="bd-kpis">'
               f'NPS {lM1}: <strong>{fn(g_nps)}%</strong>'
               f' &nbsp;{chip(g_delta, suffix=f"pp {delta_lbl}")}'
               f' &nbsp;{chip(g_dtgt, suffix="pp vs tgt")}'
               f'</span></div>')

        proc_tbl  = _bd_table(bd.get("P_M1",{}),  bd.get("P_M2",{}),  max_rows=6)
        canal_tbl = _bd_table(bd.get("C_M1",{}),  bd.get("C_M2",{}),  max_rows=5)
        ofic_tbl  = _bd_table(bd.get("O_M1",{}),  {},                  max_rows=4)
        sen_tbl   = _bd_seniority(bd.get("Sr_M1",{}), bd.get("Sr_M2",{}))

        grid = (f'<div class="bd-grid">'
                f'<div class="bd-sec"><div class="bd-sec-title">&#128204; Processos</div>{proc_tbl}</div>'
                f'<div class="bd-sec"><div class="bd-sec-title">&#128241; Canal</div>{canal_tbl}</div>'
                f'<div class="bd-sec"><div class="bd-sec-title">&#127970; Oficina</div>{ofic_tbl}</div>'
                f'<div class="bd-sec"><div class="bd-sec-title">&#127891; Senioridade</div>{sen_tbl}</div>'
                f'</div>')

        analysis = _process_exec_html(grp, mode=mode) or _drv_analysis_html(grp)
        cards += (f'<div class="drv-card" data-grp="{slug}">'
                  f'{hdr}{grid}{analysis}</div>')

    return (f'<div class="section-block">'
            f'<div class="section-title">{section_title}</div>'
            f'{filter_bar}'
            f'<div class="drv-cards">{cards}</div>'
            f'</div>')

def _tab_mensal():
    chart_sec = f"""<div class="section-block">
  <div class="section-title">Evolu&#231;&#227;o NPS por Categoria &mdash; Mensal</div>
  {chart_small_multiples("c_mon",
      [(g, grp_mon[g], GROUP_COLORS[g], grp_targets[g]) for g in DRIVER_GROUPS],
      mon_cons, MONTH_LABELS)}
</div>"""

    return chart_sec + _build_driver_breakdowns()


def _tab_semanal():
    chart_sec = f"""<div class="section-block">
  <div class="section-title">Evolu&#231;&#227;o NPS por Categoria &mdash; Semanal</div>
  {chart_small_multiples("c_wk",
      [(g, grp_wk[g], GROUP_COLORS[g], grp_targets[g]) for g in DRIVER_GROUPS],
      wk_cons, WEEK_LABELS)}
</div>"""

    return chart_sec + _build_driver_breakdowns(mode="weekly")


def _tab_ranking():
    ranking = sorted(ALL_DRIVERS,
                     key=lambda d: delta_tgt.get(d) if delta_tgt.get(d) is not None else -999,
                     reverse=True)

    rows = ""
    for i, drv in enumerate(ranking, 1):
        nps_v = curr_m.get(drv)
        tgt_v = DRIVER_TARGETS.get(drv, NPS_TARGET)
        d_t   = delta_tgt.get(drv)
        d_mm  = trend_m.get(drv)
        d_ww  = trend_w.get(drv)
        cat   = drv_cat(drv)
        short = DRIVER_SHORT.get(drv, drv)
        dot   = DRIVER_COLORS.get(drv, "#aaa")
        diff  = (nps_v - tgt_v) if nps_v is not None else None

        if diff is None:    st_txt, st_cls = "—", ""
        elif diff >= 0:     st_txt, st_cls = "&#x2713; Acima",   "st-ok"
        elif diff >= -3:    st_txt, st_cls = "~ Pr&#243;ximo",   "st-near"
        elif diff >= -10:   st_txt, st_cls = "&#9660; Abaixo",   "st-below"
        else:               st_txt, st_cls = "&#x2717; Cr&#237;tico", "st-crit"

        row_cls = ' class="row-crit"' if diff is not None and diff < -10 else ""
        rows += f"""<tr{row_cls}>
  <td class="rk-num">{i}</td>
  <td class="drv-cell"><span class="dot" style="background:{dot}"></span>{esc(short)}</td>
  <td class="cat-cell">{esc(cat)}</td>
  <td><strong>{fn(nps_v)}%</strong></td>
  <td>{fn(tgt_v)}%</td>
  <td>{chip(d_t)}</td>
  <td>{chip(d_mm)}</td>
  <td>{chip(d_ww)}</td>
  <td><span class="{st_cls}">{st_txt}</span></td>
</tr>\n"""

    last_m = esc(MONTH_LABELS[-1])
    return f"""<div class="section-block">
  <div class="section-title">Ranking CDUs &mdash; {last_m} (ordenado por &#916; vs Target)</div>
  <div class="tbl-wrap"><table class="dtbl rk-tbl"><thead>
    <tr>
      <th>#</th><th>CDU</th><th>Categoria</th>
      <th>NPS ({last_m})</th><th>Target</th>
      <th>&#916; vs Tgt</th><th>&#916; M/M</th><th>&#916; W/W</th><th>Status</th>
    </tr>
  </thead><tbody>
{rows}  </tbody></table></div>
</div>"""

# ══════════════════════════════════════════════════════════════════════
# 7. CSS
# ══════════════════════════════════════════════════════════════════════
_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Roboto', 'Segoe UI', sans-serif;
       font-size: 13px; background: #f4f6f9; color: #222; }

.header { background: linear-gradient(135deg,#3483FA 0%,#1C5BBD 100%);
          color:#fff; padding:16px 24px; display:flex; align-items:center;
          justify-content:space-between; }
.header-title { font-size:18px; font-weight:700; letter-spacing:.3px; }
.header-sub   { font-size:11px; opacity:.85; margin-top:2px; }
.header-date  { font-size:11px; opacity:.8; text-align:right; line-height:1.7; }

.tabs { display:flex; background:#fff; border-bottom:2px solid #e8eaf0;
        padding:0 24px; position:sticky; top:0; z-index:100;
        box-shadow:0 2px 8px rgba(0,0,0,.07); overflow-x:auto; }
.tab-btn { padding:12px 20px; font-size:13px; font-weight:500; cursor:pointer;
           border:none; background:none; color:#666; white-space:nowrap;
           border-bottom:3px solid transparent; margin-bottom:-2px; transition:all .2s; }
.tab-btn:hover  { color:#3483FA; background:#f0f4ff; }
.tab-btn.active { color:#3483FA; border-bottom-color:#3483FA; font-weight:700; }

.tab-pane { display:none; padding:20px 24px; max-width:1400px; margin:0 auto; }
.tab-pane.active { display:block; }

.kpi-strip { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:20px; }
.kpi-card  { background:#fff; border-radius:10px; padding:18px 20px;
             box-shadow:0 1px 8px rgba(0,0,0,.06); border-top:4px solid #3483FA; }
.kpi-label { font-size:11px; color:#888; text-transform:uppercase; letter-spacing:.5px; margin-bottom:6px; }
.kpi-value { font-size:28px; font-weight:700; color:#1a1a2e; }
.kpi-sub   { font-size:11px; color:#aaa; margin-top:4px; }
.kpi-pos   { color:#00A650 !important; }
.kpi-neg   { color:#E84142 !important; }

.section-block { background:#fff; border-radius:10px; padding:18px 20px; margin-bottom:20px;
                 box-shadow:0 1px 8px rgba(0,0,0,.06); }
.section-title { font-size:14px; font-weight:700; color:#333; margin-bottom:14px; }

.cat-hdr { font-size:11px; font-weight:700; color:#555; padding:5px 10px;
           background:#f4f6f9; border-radius:6px; margin-bottom:10px; margin-top:14px;
           text-transform:uppercase; letter-spacing:.5px; }

.card-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(145px,1fr));
             gap:10px; margin-bottom:4px; }
.cdu-card  { background:#fafbfc; border-radius:8px; padding:12px 13px;
             box-shadow:0 1px 4px rgba(0,0,0,.05); }
.cdu-name  { font-size:11px; font-weight:600; color:#555; margin-bottom:4px;
             display:flex; justify-content:space-between; align-items:center; }
.cdu-nps   { font-size:22px; font-weight:700; color:#1a1a2e; margin-bottom:4px; }
.cdu-det   { font-size:10px; color:#888; }

.chip     { display:inline-block; padding:1px 7px; border-radius:10px; font-size:11px;
            font-weight:600; white-space:nowrap; }
.chip-pos { background:#e6f9ee; color:#1a7a42; }
.chip-neg { background:#fde8e8; color:#a01010; }
.chip-neu { background:#f0f0f0; color:#666; }

.arr     { font-size:12px; font-weight:700; }
.arr-pos { color:#00A650; }
.arr-neg { color:#E84142; }
.arr-neu { color:#aaa; }

.tbl-wrap { overflow-x:auto; }
.dtbl { width:100%; border-collapse:collapse; font-size:12px; }
.dtbl th { background:#f4f6f9; padding:8px 10px; text-align:center;
           font-weight:600; color:#555; border-bottom:2px solid #e0e4ec; white-space:nowrap; }
.dtbl th:first-child, .dtbl th:nth-child(2) { text-align:left; }
.dtbl td { padding:7px 10px; text-align:center; border-bottom:1px solid #f0f2f5; }
.dtbl td:first-child, .dtbl td:nth-child(2) { text-align:left; }
.dtbl tr:hover td { background:#f8f9ff !important; }
.cons-row td { background:#f0f4ff !important; border-top:2px solid #3483FA; }
.row-crit td { background:#fff8f8 !important; }

.drv-cell { white-space:nowrap; }
.cat-cell  { color:#888; font-size:11px; white-space:nowrap; }
.dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; flex-shrink:0; vertical-align:middle; }

.rk-tbl td { padding:8px 10px; }
.rk-num    { color:#bbb; font-weight:700; width:30px; }
.st-ok     { color:#00A650; font-weight:600; }
.st-near   { color:#7a5800; font-weight:600; }
.st-below  { color:#c05700; font-weight:600; }
.st-crit   { color:#E84142; font-weight:700; }

/* Driver breakdown filter */
.drv-fbar { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:16px; }
.drv-fbtn { padding:5px 14px; border-radius:20px; border:1.5px solid #ddd;
            background:#fff; font-size:12px; font-weight:500; cursor:pointer;
            color:#666; transition:all .18s; }
.drv-fbtn:hover { border-color:#3483FA; color:#3483FA; }
.drv-fbtn.active { background:#3483FA; border-color:#3483FA; color:#fff; font-weight:700; }

/* Driver cards */
.drv-cards { display:flex; flex-direction:column; gap:16px; }
.drv-card  { background:#fafbfc; border-radius:10px; border:1px solid #e8eaf0;
             overflow:hidden; }
.bd-hdr    { padding:12px 16px; background:#fff; display:flex; align-items:center;
             justify-content:space-between; flex-wrap:wrap; gap:8px; }
.bd-grp-name { font-size:14px; font-weight:700; color:#222; }
.bd-kpis   { font-size:12px; color:#555; display:flex; align-items:center; gap:6px; flex-wrap:wrap; }

.bd-grid   { display:grid; grid-template-columns:repeat(4,1fr); gap:0;
             border-top:1px solid #e8eaf0; }
.bd-sec    { padding:14px 16px; border-right:1px solid #e8eaf0; }
.bd-sec:last-child { border-right:none; }
.bd-sec-title { font-size:11px; font-weight:700; color:#888; text-transform:uppercase;
                letter-spacing:.5px; margin-bottom:8px; }

.bd-tbl    { width:100%; border-collapse:collapse; font-size:11px; }
.bd-tbl th { color:#aaa; font-weight:600; padding:2px 4px; text-align:left;
             border-bottom:1px solid #f0f0f0; font-size:10px; }
.bd-tbl td { padding:3px 4px; border-bottom:1px solid #f5f5f5; }
.bd-name   { max-width:160px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#333; }
.bd-nps    { font-weight:600; color:#1a1a2e; text-align:right; white-space:nowrap; }
.bd-delta  { text-align:right; white-space:nowrap; font-weight:600; font-size:10px; }
.bd-vol    { text-align:right; color:#aaa; font-size:10px; }
.bd-pos    { color:#00A650; }
.bd-neg    { color:#E84142; }

/* Driver analysis sections */
.bd-analysis    { border-top:2px solid #e8eaf0; }
.bd-ana-sec     { padding:14px 16px; border-bottom:1px solid #f0f2f5; }
.bd-ana-sec:last-child { border-bottom:none; }
.bd-ana-title   { font-size:11px; font-weight:700; color:#555; text-transform:uppercase;
                  letter-spacing:.5px; margin-bottom:8px; }

@media (max-width:1100px) { .bd-grid { grid-template-columns:repeat(2,1fr); } }
@media (max-width:600px)  { .bd-grid { grid-template-columns:1fr; } }

.sm-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
.sm-item { background:#fff; border-radius:8px; padding:12px 14px;
           box-shadow:0 1px 6px rgba(0,0,0,.06); }
.sm-header { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:1px; }
.sm-cat  { font-size:11px; font-weight:700; color:#555; text-transform:uppercase; letter-spacing:.4px; }
.sm-nps  { font-size:15px; font-weight:700; color:#1a1a2e; }
.sm-sub  { font-size:10px; margin-bottom:6px; font-weight:600; }
.sm-pos  { color:#00A650; }
.sm-neg  { color:#E84142; }
.sm-neu  { color:#aaa; }

/* Resumo executivo */
.exec-wrap    { display:flex; flex-direction:column; gap:16px; }
.exec-section { background:#fff; border-radius:10px; padding:18px 20px;
                box-shadow:0 1px 8px rgba(0,0,0,.06); }
.exec-title   { font-size:14px; font-weight:700; color:#333; margin-bottom:12px;
                padding-bottom:8px; border-bottom:2px solid #f0f2f5; }
.exec-body    { font-size:13px; color:#444; line-height:1.7; }
.exec-body p  { margin-bottom:8px; }
.exec-cards   { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:12px; }
.exec-card    { border-radius:8px; padding:14px 16px; font-size:12px; line-height:1.6; }
.exec-card-pos  { background:#e8f8f0; border-left:4px solid #00A650; }
.exec-card-neg  { background:#fdf0f0; border-left:4px solid #E84142; }
.exec-card-warn { background:#fffae6; border-left:4px solid #F39C12; }
.exec-label   { font-weight:700; font-size:12px; margin-bottom:4px; color:#222; }
.exec-evidence{ font-size:11px; color:#666; font-style:italic; margin-top:4px; border-top:1px solid rgba(0,0,0,.06); padding-top:4px; }
.exec-bullet  { display:flex; gap:8px; margin-bottom:6px; font-size:12px; }
.exec-bullet::before { content:"•"; color:#3483FA; font-weight:700; flex-shrink:0; }
.exec-no-data { color:#aaa; font-size:12px; font-style:italic; padding:12px 0; }

@media (max-width:900px) { .sm-grid { grid-template-columns:repeat(2,1fr); } }
@media (max-width:768px) {
  .kpi-strip { grid-template-columns:1fr; }
  .card-grid { grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); }
  .sm-grid   { grid-template-columns:1fr; }
}
"""

# ══════════════════════════════════════════════════════════════════════
# 8. MONTAGEM FINAL
# ══════════════════════════════════════════════════════════════════════
def _load_exec_summary():
    import os
    path = '_exec_summary.html'
    if not os.path.exists(path):
        return (f'<div class="exec-no-data">Resumo executivo não gerado ainda. '
                f'Execute <code>python _generate_exec_summary.py</code> para gerar.</div>')
    with open(path, encoding='utf-8') as f:
        return f.read()

def build():
    t0 = _tab_exec()
    t1 = _tab_mensal()
    t2 = _tab_semanal()
    t3 = _tab_ranking()

    js = """
function showTab(n){
  document.querySelectorAll('.tab-btn').forEach(function(b,i){b.classList.toggle('active',i===n);});
  document.querySelectorAll('.tab-pane').forEach(function(p,i){p.classList.toggle('active',i===n);});
}
function filterDrv(btn, grp){
  document.querySelectorAll('.drv-fbtn').forEach(function(b){b.classList.remove('active');});
  btn.classList.add('active');
  document.querySelectorAll('.drv-card').forEach(function(c){
    c.style.display = (c.dataset.grp===grp) ? '' : 'none';
  });
}
// Inicializa cada grupo de cards: esconde todos exceto o primeiro por container
(function(){
  document.querySelectorAll('.drv-cards').forEach(function(container){
    var cards = container.querySelectorAll('.drv-card');
    for(var i=1;i<cards.length;i++) cards[i].style.display='none';
  });
})();
"""
    tgt_str = str(NPS_TARGET).replace('.', ',')
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>NPS Tend&#234;ncias Ger&#234;ncia &mdash; Sellers BR</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<script>Chart.register(ChartDataLabels);</script>
<style>{_CSS}</style>
</head>
<body>

<div class="header">
  <div>
    <div class="header-title">NPS Tend&#234;ncias Ger&#234;ncia &mdash; Sellers BR</div>
    <div class="header-sub">Evolu&#231;&#227;o mensal &amp; semanal &middot; Tend&#234;ncias &middot; Ranking por CDU &middot; 27 drivers</div>
  </div>
  <div class="header-date">
    Atualizado: {REPORT_DATE}<br>
    Semana fechada: {esc(S1_LABEL)}<br>
    M&#234;s fechado: {esc(M1_LABEL)}<br>
    Target: {tgt_str}%
  </div>
</div>

<div class="tabs">
  <button class="tab-btn active" onclick="showTab(0)">&#x1F4CA; Vis&#227;o Executiva</button>
  <button class="tab-btn" onclick="showTab(1)">&#x1F4C5; Evolu&#231;&#227;o Mensal</button>
  <button class="tab-btn" onclick="showTab(2)">&#x1F4C6; Evolu&#231;&#227;o Semanal</button>
  <button class="tab-btn" onclick="showTab(3)">&#x1F3C6; Ranking CDUs</button>
</div>

<div class="tab-pane active">{t0}</div>
<div class="tab-pane">{t1}</div>
<div class="tab-pane">{t2}</div>
<div class="tab-pane">{t3}</div>

<script>{js}</script>
</body>
</html>"""


if __name__ == '__main__':
    html = build()
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Dashboard gerado: {OUTPUT_FILE}")
