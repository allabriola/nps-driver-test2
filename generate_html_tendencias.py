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

def chart_grouped_cats(cid, hist_cat, cons_data, labels, show_labels=False, height=300):
    # Bar datasets: one per category
    datasets = []
    for cat, color in CAT_COLORS.items():
        dl = {"display": show_labels, "anchor": "end", "align": "end",
              "offset": 2, "color": "#555", "font": {"size": 8, "weight": "600"},
              "formatter": "__FMT__"} if show_labels else {"display": False}
        datasets.append({
            "type": "bar", "label": cat, "data": hist_cat[cat],
            "backgroundColor": color + "bb", "borderColor": color,
            "borderWidth": 1, "borderRadius": 3,
            "datalabels": dl,
        })
    # Consolidated line overlay
    datasets.append({
        "type": "line", "label": "Consolidado",
        "data": cons_data,
        "borderColor": "#1a1a2e", "backgroundColor": "#1a1a2e22",
        "borderWidth": 2.5, "pointRadius": 5, "pointBackgroundColor": "#1a1a2e",
        "fill": False, "tension": 0.3, "order": 0,
        "datalabels": {"display": True, "anchor": "top", "align": "top",
                       "offset": 4, "color": "#1a1a2e",
                       "font": {"size": 9, "weight": "700"},
                       "formatter": "__FMT__"},
    })
    # Target dashed line
    datasets.append({
        "type": "line",
        "label": f"Target ({str(NPS_TARGET).replace('.', ',')}%)",
        "data": [NPS_TARGET] * len(labels),
        "borderColor": "#E84142", "borderDash": [6, 3],
        "borderWidth": 1.5, "pointRadius": 0, "fill": False, "order": 0,
        "datalabels": {"display": False},
    })

    cfg = {"type": "bar",
           "data": {"labels": labels, "datasets": datasets},
           "options": {
               "responsive": True, "maintainAspectRatio": False,
               "layout": {"padding": {"top": 28, "bottom": 4}},
               "interaction": {"mode": "index", "intersect": False},
               "plugins": {
                   "legend": {"position": "bottom",
                              "labels": {"boxWidth": 10, "padding": 10, "font": {"size": 10}}},
                   "datalabels": {}},
               "scales": {
                   "y": {"min": -20, "max": 100,
                         "ticks": {"stepSize": 20}, "grid": {"color": "#f0f0f0"}},
                   "x": {"grid": {"display": False}}}}}
    j = _json.dumps(cfg).replace('"__FMT__"', _FMT)
    return _chart_script(cid, j, height)

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

    # --- Chart ---
    chart_sec = f"""<div class="section-block">
  <div class="section-title">Evolu&#231;&#227;o NPS Consolidado &mdash; Mensal YTD</div>
  {chart_bar_monthly("c_exec_mon")}
</div>"""

    # --- CDU Cards ---
    cards = '<div class="section-block"><div class="section-title">Status por CDU &mdash; ' + esc(MONTH_LABELS[-1]) + '</div>'
    for cat, drvs in CATEGORIES.items():
        color = CAT_COLORS[cat]
        cards += f'<div class="cat-hdr" style="border-left:4px solid {color}">{esc(cat)}</div>'
        cards += '<div class="card-grid">'
        for drv in drvs:
            nps_v  = curr_m.get(drv)
            tgt_v  = DRIVER_TARGETS.get(drv, NPS_TARGET)
            tr     = trend_m.get(drv)
            d_t    = delta_tgt.get(drv)
            short  = DRIVER_SHORT.get(drv, drv)
            diff   = (nps_v - tgt_v) if nps_v is not None else None
            if diff is None:    border = "#ccc"
            elif diff >= 0:     border = "#00A650"
            elif diff >= -3:    border = "#F39C12"
            elif diff >= -10:   border = "#FF6B35"
            else:               border = "#E84142"
            cards += f"""<div class="cdu-card" style="border-left:4px solid {border}">
  <div class="cdu-name">{esc(short)} {arr(tr)}</div>
  <div class="cdu-nps">{fn(nps_v)}%</div>
  <div class="cdu-det">Tgt: {fn(tgt_v)}% &nbsp;{chip(d_t)}</div>
</div>"""
        cards += '</div>'
    cards += '</div>'

    return kpis + chart_sec + cards


def _tab_mensal():
    chart_sec = f"""<div class="section-block">
  <div class="section-title">Evolu&#231;&#227;o NPS por Categoria &mdash; Mensal</div>
  {chart_grouped_cats("c_mon_cat", cat_mon, mon_cons, MONTH_LABELS, show_labels=True, height=310)}
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
  {chart_grouped_cats("c_wk_cat", cat_wk, wk_cons, WEEK_LABELS, show_labels=False, height=310)}
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

@media (max-width:768px) {
  .kpi-strip { grid-template-columns:1fr; }
  .card-grid { grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); }
}
"""

# ══════════════════════════════════════════════════════════════════════
# 8. MONTAGEM FINAL
# ══════════════════════════════════════════════════════════════════════
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
