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

GROUP_COLORS = {
    "ME Vendedor":       "#00A650",
    "Exp. Impositiva":   "#3483FA",
    "PCF Vendedor":      "#FF7733",
    "Post Venta":        "#E84142",
    "Publicaciones":     "#B7950B",
    "FBM-S":             "#F39C12",
    "PDD":               "#9B59B6",
    "PNR":               "#17A589",
    "Partners":          "#1ABC9C",
    "CBT":               "#2E86C1",
    "Otros CV":          "#95A5A6",
}

ALL_DRIVERS = list(monthly_history.keys())

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

    return kpis + exec_html + chart_sec + wf_mm + wf_tg


def _tab_mensal():
    chart_sec = f"""<div class="section-block">
  <div class="section-title">Evolu&#231;&#227;o NPS por Categoria &mdash; Mensal</div>
  {chart_small_multiples("c_mon",
      [(g, grp_mon[g], GROUP_COLORS[g], grp_targets[g]) for g in DRIVER_GROUPS],
      mon_cons, MONTH_LABELS)}
</div>"""

    rows = ""
    for drv in ALL_DRIVERS:
        tgt_v = DRIVER_TARGETS.get(drv, NPS_TARGET)
        cat   = drv_cat(drv)
        short = DRIVER_SHORT.get(drv, drv)
        dot   = DRIVER_COLORS.get(drv, "#aaa")
        rows += f'<tr><td class="drv-cell"><span class="dot" style="background:{dot}"></span>{esc(short)}</td>'
        rows += f'<td class="cat-cell">{esc(cat)}</td>'
        for v in drv_m[drv]:
            rows += f'<td {cell_bg(v, tgt_v)}>{fn(v)}%</td>'
        rows += f'<td>{chip(trend_m.get(drv))}</td>'
        rows += f'<td>{chip(delta_tgt.get(drv))}</td>'
        rows += f'<td>{arr(trend_m.get(drv))}</td></tr>\n'

    # Consolidated footer row
    cons_tr   = (round(mon_cons[-1] - mon_cons[-2], 2)
                 if mon_cons[-1] is not None and mon_cons[-2] is not None else None)
    cons_dtgt = (round(mon_cons[-1] - NPS_TARGET, 2) if mon_cons[-1] is not None else None)
    cons_cells = "".join(f'<td {cell_bg(v, NPS_TARGET)}><strong>{fn(v)}%</strong></td>' for v in mon_cons)
    rows += (f'<tr class="cons-row"><td colspan="2"><strong>Consolidado</strong></td>'
             f'{cons_cells}'
             f'<td>{chip(cons_tr)}</td>'
             f'<td>{chip(cons_dtgt)}</td>'
             f'<td>{arr(cons_tr)}</td></tr>\n')

    month_ths = "".join(f'<th>{esc(m)}</th>' for m in MONTH_LABELS)
    table_sec = f"""<div class="section-block">
  <div class="section-title">Detalhe por CDU &mdash; Mensal</div>
  <div class="tbl-wrap"><table class="dtbl"><thead>
    <tr><th>CDU</th><th>Categoria</th>{month_ths}<th>&#916; M/M</th><th>&#916; vs Tgt</th><th>Tend.</th></tr>
  </thead><tbody>
{rows}  </tbody></table></div>
</div>"""

    return chart_sec + table_sec


def _tab_semanal():
    chart_sec = f"""<div class="section-block">
  <div class="section-title">Evolu&#231;&#227;o NPS por Categoria &mdash; Semanal</div>
  {chart_small_multiples("c_wk",
      [(g, grp_wk[g], GROUP_COLORS[g], grp_targets[g]) for g in DRIVER_GROUPS],
      wk_cons, WEEK_LABELS)}
</div>"""

    rows = ""
    for drv in ALL_DRIVERS:
        cat   = drv_cat(drv)
        short = DRIVER_SHORT.get(drv, drv)
        dot   = DRIVER_COLORS.get(drv, "#aaa")
        rows += f'<tr><td class="drv-cell"><span class="dot" style="background:{dot}"></span>{esc(short)}</td>'
        rows += f'<td class="cat-cell">{esc(cat)}</td>'
        for v in drv_w[drv]:
            rows += f'<td>{fn(v)}%</td>'
        rows += f'<td>{chip(trend_w.get(drv))}</td>'
        rows += f'<td>{arr(trend_w.get(drv))}</td></tr>\n'

    wk_tr = (round(wk_cons[-1] - wk_cons[-2], 2)
              if wk_cons[-1] is not None and wk_cons[-2] is not None else None)
    cons_cells = "".join(f'<td><strong>{fn(v)}%</strong></td>' for v in wk_cons)
    rows += (f'<tr class="cons-row"><td colspan="2"><strong>Consolidado</strong></td>'
             f'{cons_cells}'
             f'<td>{chip(wk_tr)}</td>'
             f'<td>{arr(wk_tr)}</td></tr>\n')

    week_ths = "".join(f'<th>{esc(w)}</th>' for w in WEEK_LABELS)
    table_sec = f"""<div class="section-block">
  <div class="section-title">Detalhe por CDU &mdash; Semanal</div>
  <div class="tbl-wrap"><table class="dtbl"><thead>
    <tr><th>CDU</th><th>Categoria</th>{week_ths}<th>&#916; W/W</th><th>Tend.</th></tr>
  </thead><tbody>
{rows}  </tbody></table></div>
</div>"""

    return chart_sec + table_sec


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
