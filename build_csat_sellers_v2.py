#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_csat_sellers_v2.py — Dashboard CSAT Sellers Longtail BR
Abas: Visão Geral | Lineal | Driver | Bottom Box | Comentários
Fonte: _csat_sellers_data.json (gerado por csat_sellers_fetch.py)
"""
import json, sys, html as _html, os, glob as _glob, re
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

INPUT  = "_csat_sellers_data.json"
OUTPUT = "csat_sellers_dashboard.html"

# ── Carregar dados ─────────────────────────────────────────────────────────────
print(f"Carregando dados… ({INPUT})")
with open(INPUT, encoding="utf-8") as f:
    D = json.load(f)

TEAMS        = D["teams"]
MONTHS       = D["months"]
MONTH_LABELS = D["month_labels"]
MONTH_CUR    = D["month_cur"]
MONTH_LBL    = D["month_cur_label"]
WEEK_LBL     = D["week_label"]
UPDATED      = D["updated_at"]

TEAM_LABELS = {
    "BR_ME_Sellers_Longtail":            "ME Sellers",
    "BR_Ventas_Sellers_Longtail":        "Ventas",
    "BR_Publicaciones_Sellers_Longtail": "Publicaciones",
}
TEAM_COLORS = {
    "BR_ME_Sellers_Longtail":            "#7c3aed",
    "BR_Ventas_Sellers_Longtail":        "#16a34a",
    "BR_Publicaciones_Sellers_Longtail": "#0369a1",
}

def lbl(t):  return TEAM_LABELS.get(t, t)
def clr(t):  return TEAM_COLORS.get(t, "#888")
def esc(s):  return _html.escape(str(s or ""))
def pct(v):  return f"{v:.1f}%" if v is not None else "—"
def fmt(n):  return f"{int(n):,}".replace(",", ".")

def csat_color(v):
    if v is None: return "#888"
    if v >= 84:   return "#16a34a"   # verde
    if v >= 80:   return "#d97706"   # laranja
    return "#dc2626"                  # vermelho

def bb_color(v):
    if v is None: return "#888"
    if v <= 15:   return "#16a34a"
    if v <= 25:   return "#d97706"
    return "#dc2626"

# ── Helpers de lookup ─────────────────────────────────────────────────────────
def by_team_month(month):
    return {r["team"]: r for r in D["monthly"]["by_team"]
            if r["month"] == month}

def by_team_week():
    return {r["team"]: r for r in D["weekly"]["by_team"]}

def by_process_month(month, team=None):
    rows = [r for r in D["monthly"]["by_process"]
            if r["month"] == month and (team is None or r["team"] == team)]
    agg = {}
    for r in rows:
        k = r["process"]
        if k not in agg:
            agg[k] = {"process": k, "total": 0, "satisfied": 0.0, "bottom_box": 0}
        agg[k]["total"]      += r["total"]
        agg[k]["satisfied"]  += r["csat"] * r["total"] / 100 if r["csat"] is not None else 0
        agg[k]["bottom_box"] += r["bottom_box"]
    out = []
    for v in agg.values():
        t = v["total"]
        c = round(v["satisfied"] / t * 100, 1) if t else None
        bb = round(v["bottom_box"] / t * 100, 1) if t else None
        out.append({"process": v["process"], "total": t, "csat": c,
                    "bottom_box": v["bottom_box"], "bottom_box_pct": bb})
    return sorted(out, key=lambda x: -x["total"])

def by_process_week(team=None):
    rows = [r for r in D["weekly"]["by_process"]
            if team is None or r["team"] == team]
    agg = {}
    for r in rows:
        k = r["process"]
        if k not in agg:
            agg[k] = {"process": k, "total": 0, "satisfied": 0.0, "bottom_box": 0}
        agg[k]["total"]      += r["total"]
        agg[k]["satisfied"]  += r["csat"] * r["total"] / 100 if r["csat"] is not None else 0
        agg[k]["bottom_box"] += r["bottom_box"]
    out = []
    for v in agg.values():
        t = v["total"]
        c = round(v["satisfied"] / t * 100, 1) if t else None
        bb = round(v["bottom_box"] / t * 100, 1) if t else None
        out.append({"process": v["process"], "total": t, "csat": c,
                    "bottom_box": v["bottom_box"], "bottom_box_pct": bb})
    return sorted(out, key=lambda x: -x["total"])

def rr_by_team_month(month):
    return {r["team"]: r for r in D["response_rate"]["monthly"]
            if r["month"] == month}

def rr_by_team_week():
    return {r["team"]: r for r in D["response_rate"]["weekly"]}

# ── CONSOLIDADOS ───────────────────────────────────────────────────────────────
def consol(rows_dict):
    tot, sat, bb = 0, 0.0, 0
    for r in rows_dict.values():
        tot += r["total"]
        sat += (r["csat"] or 0) * r["total"] / 100
        bb  += r["bottom_box"]
    c = round(sat / tot * 100, 1) if tot else None
    b = round(bb / tot * 100, 1) if tot else None
    return {"total": tot, "csat": c, "bottom_box": bb, "bottom_box_pct": b}

# ── JS DATA ────────────────────────────────────────────────────────────────────
# Prepara dados para gráfico de linha (trend mensal por equipe)
chart_months = MONTHS
chart_labels = [MONTH_LABELS.get(m, m) for m in chart_months]
chart_datasets = []
for t in TEAMS:
    row_map = {r["month"]: r for r in D["monthly"]["by_team"] if r["team"] == t}
    vals = [row_map[m]["csat"] if m in row_map else None for m in chart_months]
    chart_datasets.append({
        "label": lbl(t),
        "data": vals,
        "borderColor": clr(t),
        "backgroundColor": clr(t) + "22",
        "tension": 0.3,
        "fill": False,
    })

JS_CHART = json.dumps({
    "labels": chart_labels,
    "datasets": chart_datasets
}, ensure_ascii=False)

# ── Dados comentários para JS ──────────────────────────────────────────────────
all_comments = []
for period in ["monthly", "weekly"]:
    idx = D["diagnostic_raw"][period]
    seen = set()
    for team, procs in idx.items():
        for proc, items in procs.items():
            for it in items:
                key = (team, proc, it["score"], it["comentario"][:50])
                if key not in seen:
                    seen.add(key)
                    all_comments.append({
                        "period": "MTD" if period == "monthly" else "WTD",
                        "team":   lbl(team),
                        "team_id": team,
                        "process": proc,
                        "score":   it["score"],
                        "text":    it["comentario"],
                    })

# Limita a 500 comentários para não explodir o HTML
all_comments = sorted(all_comments, key=lambda x: x["score"])[:500]
JS_COMMENTS = json.dumps(all_comments, ensure_ascii=False)

# ── Histórico de snapshots ─────────────────────────────────────────────────────
GHPAGES_BASE  = "https://allabriola.github.io/nps-driver-test2/"
HISTORY_DIR   = "history_csat"
_hist_files   = sorted(_glob.glob(f"{HISTORY_DIR}/semana_*.html"), reverse=True)
history_items = []
for _hf in _hist_files:
    _fn = os.path.basename(_hf)
    _m  = re.match(r"semana_(\d{4}-\d{2}-\d{2})\.html", _fn)
    if _m:
        _d = _m.group(1)
        history_items.append({"file": _fn, "label": "Semana até " + _d, "date": _d})
JS_HISTORY = json.dumps(history_items, ensure_ascii=False)

# ── Bottom Box table data ──────────────────────────────────────────────────────
bb_rows_mtd = []
for r in D["monthly"]["by_process"]:
    if r["month"] == MONTH_CUR:
        bb_rows_mtd.append({
            "team":    lbl(r["team"]),
            "team_id": r["team"],
            "process": r["process"],
            "total":   r["total"],
            "bb":      r["bottom_box"],
            "bb_pct":  r["bottom_box_pct"],
            "csat":    r["csat"],
        })
bb_rows_mtd.sort(key=lambda x: -(x["bb_pct"] or 0))

bb_rows_wtd = []
for r in D["weekly"]["by_process"]:
    bb_rows_wtd.append({
        "team":    lbl(r["team"]),
        "team_id": r["team"],
        "process": r["process"],
        "total":   r["total"],
        "bb":      r["bottom_box"],
        "bb_pct":  r["bottom_box_pct"],
        "csat":    r["csat"],
    })
bb_rows_wtd.sort(key=lambda x: -(x["bb_pct"] or 0))

JS_BB_MTD = json.dumps(bb_rows_mtd, ensure_ascii=False)
JS_BB_WTD = json.dumps(bb_rows_wtd, ensure_ascii=False)

# ── Lineal data ────────────────────────────────────────────────────────────────
lineal_mtd = []
mtd = by_team_month(MONTH_CUR)
rr_mtd = rr_by_team_month(MONTH_CUR)
for t in TEAMS:
    r = mtd.get(t, {})
    rr = rr_mtd.get(t, {})
    lineal_mtd.append({
        "team":    lbl(t),
        "team_id": t,
        "csat":    r.get("csat"),
        "total":   r.get("total", 0),
        "bb_pct":  r.get("bottom_box_pct"),
        "rr_pct":  rr.get("rr_pct"),
        "sent":    rr.get("sent", 0),
    })

lineal_wtd = []
wtd = by_team_week()
rr_wtd = rr_by_team_week()
for t in TEAMS:
    r = wtd.get(t, {})
    rr = rr_wtd.get(t, {})
    lineal_wtd.append({
        "team":    lbl(t),
        "team_id": t,
        "csat":    r.get("csat"),
        "total":   r.get("total", 0),
        "bb_pct":  r.get("bottom_box_pct"),
        "rr_pct":  rr.get("rr_pct"),
        "sent":    rr.get("sent", 0),
    })

JS_LINEAL_MTD = json.dumps(lineal_mtd, ensure_ascii=False)
JS_LINEAL_WTD = json.dumps(lineal_wtd, ensure_ascii=False)

# Lineal: process breakdown (MTD e WTD por equipe)
lineal_proc_mtd = {}
for t in TEAMS:
    procs = [r for r in D["monthly"]["by_process"]
             if r["month"] == MONTH_CUR and r["team"] == t]
    lineal_proc_mtd[t] = procs

lineal_proc_wtd = {}
for t in TEAMS:
    procs = [r for r in D["weekly"]["by_process"] if r["team"] == t]
    lineal_proc_wtd[t] = procs

JS_LINEAL_PROC_MTD = json.dumps({lbl(k): v for k, v in lineal_proc_mtd.items()}, ensure_ascii=False)
JS_LINEAL_PROC_WTD = json.dumps({lbl(k): v for k, v in lineal_proc_wtd.items()}, ensure_ascii=False)

# Driver data (aggregated across teams)
driver_mtd = by_process_month(MONTH_CUR)
driver_wtd = by_process_week()
JS_DRIVER_MTD = json.dumps(driver_mtd, ensure_ascii=False)
JS_DRIVER_WTD = json.dumps(driver_wtd, ensure_ascii=False)

# Driver data por equipe (para filtro de equipe na aba Driver)
driver_by_team_mtd = [
    {"team": lbl(r["team"]), "team_id": r["team"], "process": r["process"],
     "csat": r["csat"], "total": r["total"],
     "bottom_box": r["bottom_box"], "bottom_box_pct": r["bottom_box_pct"]}
    for r in D["monthly"]["by_process"] if r["month"] == MONTH_CUR
]
driver_by_team_wtd = [
    {"team": lbl(r["team"]), "team_id": r["team"], "process": r["process"],
     "csat": r["csat"], "total": r["total"],
     "bottom_box": r["bottom_box"], "bottom_box_pct": r["bottom_box_pct"]}
    for r in D["weekly"]["by_process"]
]
JS_DRIVER_BY_TEAM_MTD = json.dumps(driver_by_team_mtd, ensure_ascii=False)
JS_DRIVER_BY_TEAM_WTD = json.dumps(driver_by_team_wtd, ensure_ascii=False)

# Consol
c_mtd = consol(mtd) if mtd else {}
c_wtd = consol(wtd) if wtd else {}

rr_mtd_all = rr_by_team_month(MONTH_CUR)
rr_wtd_all = rr_by_team_week()
rr_consol_mtd = {"sent": sum(r.get("sent",0) for r in rr_mtd_all.values()),
                  "answered": sum(r.get("answered",0) for r in rr_mtd_all.values())}
rr_consol_wtd = {"sent": sum(r.get("sent",0) for r in rr_wtd_all.values()),
                  "answered": sum(r.get("answered",0) for r in rr_wtd_all.values())}
rr_consol_mtd["rr_pct"] = round(rr_consol_mtd["answered"] / rr_consol_mtd["sent"] * 100, 1) if rr_consol_mtd["sent"] else None
rr_consol_wtd["rr_pct"] = round(rr_consol_wtd["answered"] / rr_consol_wtd["sent"] * 100, 1) if rr_consol_wtd["sent"] else None

# ── HTML builder helpers ───────────────────────────────────────────────────────
def metric_card(title, value, subtitle="", color=None, small=False):
    col = color or "#1e293b"
    sz  = "1.6rem" if small else "2.2rem"
    return f"""<div class="card">
  <div class="card-title">{esc(title)}</div>
  <div class="card-value" style="color:{col};font-size:{sz}">{esc(value)}</div>
  {"<div class='card-sub'>"+esc(subtitle)+"</div>" if subtitle else ""}
</div>"""

def team_row_html(r, show_rr=True):
    t = r["team_id"]
    rr_str = pct(r.get("rr_pct")) if show_rr else ""
    return f"""<tr>
  <td><span class="dot" style="background:{clr(t)}"></span> {esc(r['team'])}</td>
  <td style="color:{csat_color(r['csat'])};font-weight:700">{pct(r['csat'])}</td>
  <td>{fmt(r['total'])}</td>
  <td style="color:{bb_color(r['bb_pct'])};font-weight:600">{pct(r['bb_pct'])}</td>
  {"<td>"+esc(rr_str)+"</td>" if show_rr else ""}
</tr>"""

# ── ABA: VISÃO GERAL ──────────────────────────────────────────────────────────
def tab_visao_geral():
    # Consol cards
    cards_html = f"""
<div class="section">
  <div class="section-title">CONSOLIDADO</div>
  <div class="cards-row">
    {metric_card("CSAT LINEAL · "+MONTH_LBL, pct(c_mtd.get('csat')), fmt(c_mtd.get('total',0))+" pesquisas", csat_color(c_mtd.get('csat')))}
    {metric_card("CSAT LINEAL · Semana "+WEEK_LBL, pct(c_wtd.get('csat')), fmt(c_wtd.get('total',0))+" pesquisas", csat_color(c_wtd.get('csat')))}
    {metric_card("BOTTOM BOX · "+MONTH_LBL, pct(c_mtd.get('bottom_box_pct')), "Notas 1-2", bb_color(c_mtd.get('bottom_box_pct')))}
    {metric_card("RESPONSE RATE · "+MONTH_LBL, pct(rr_consol_mtd.get('rr_pct')), fmt(rr_consol_mtd.get('answered',0))+" de "+fmt(rr_consol_mtd.get('sent',0))+" enviadas")}
  </div>
</div>"""

    # Por equipe
    team_sections = ""
    for t in TEAMS:
        r_m = mtd.get(t, {})
        r_w = wtd.get(t, {})
        rr_m = rr_mtd_all.get(t, {})
        rr_w = rr_wtd_all.get(t, {})
        team_sections += f"""
<div class="section" style="border-left:4px solid {clr(t)};padding-left:12px">
  <div class="section-title" style="color:{clr(t)}">{esc(lbl(t))}</div>
  <div class="cards-row">
    {metric_card("CSAT · "+MONTH_LBL, pct(r_m.get('csat')), fmt(r_m.get('total',0))+" pesquisas", csat_color(r_m.get('csat')), small=True)}
    {metric_card("CSAT · Semana "+WEEK_LBL, pct(r_w.get('csat')), fmt(r_w.get('total',0))+" pesquisas", csat_color(r_w.get('csat')), small=True)}
    {metric_card("BOTTOM BOX · "+MONTH_LBL, pct(r_m.get('bottom_box_pct')), str(r_m.get('bottom_box',0))+" detratores", bb_color(r_m.get('bottom_box_pct')), small=True)}
    {metric_card("RESPONSE RATE · "+MONTH_LBL, pct(rr_m.get('rr_pct')), fmt(rr_m.get('answered',0))+" de "+fmt(rr_m.get('sent',0)), None, small=True)}
  </div>
</div>"""

    # Chart de trend
    chart_html = f"""
<div class="section">
  <div class="section-title">EVOLUÇÃO MENSAL — CSAT LINEAL POR EQUIPE</div>
  <div style="max-width:700px;margin:0 auto">
    <canvas id="trendChart" height="120"></canvas>
  </div>
</div>"""

    return cards_html + team_sections + chart_html

# ── ABA: EVOLUÇÃO MENSAL ─────────────────────────────────────────────────────
def tab_mensal():
    # Tabela multi-mês por equipe
    month_rows = ""
    for m in MONTHS:
        m_lbl = MONTH_LABELS.get(m, m)
        tms = by_team_month(m)
        for t in TEAMS:
            r = tms.get(t, {})
            month_rows += f"""<tr>
  <td style="color:#64748b;font-weight:600">{esc(m_lbl)}</td>
  <td><span class="dot" style="background:{clr(t)}"></span>{esc(lbl(t))}</td>
  <td style="color:{csat_color(r.get('csat'))};font-weight:700">{pct(r.get('csat'))}</td>
  <td>{fmt(r.get('total',0))}</td>
  <td style="color:{bb_color(r.get('bottom_box_pct'))};font-weight:600">{pct(r.get('bottom_box_pct'))}</td>
</tr>"""

    mtd_rows = "".join(team_row_html(r) for r in lineal_mtd)

    return f"""
<div class="section">
  <div class="section-title">CSAT POR MÊS E EQUIPE</div>
  <table class="tbl">
    <thead><tr><th>Mês</th><th>Equipe</th><th>CSAT</th><th>Volume</th><th>Bottom Box</th></tr></thead>
    <tbody>{month_rows}</tbody>
  </table>
</div>

<div class="section">
  <div class="section-title">LINEAL — POR EQUIPE · {MONTH_LBL}</div>
  <div class="section-sub">Equipe que atendeu o contato — responsabilidade operacional</div>
  <table class="tbl">
    <thead><tr><th>Equipe</th><th>CSAT</th><th>Volume</th><th>Bottom Box</th><th>Response Rate</th></tr></thead>
    <tbody>{mtd_rows}</tbody>
  </table>
</div>

<div class="section">
  <div class="section-title">BREAKDOWN POR PROCESSO · {MONTH_LBL}</div>
  <div id="mensal-proc-container"></div>
</div>

<div class="section">
  <div class="section-title">DRIVER (PROCESSO) · {MONTH_LBL}</div>
  <div class="notice" style="margin-bottom:10px">
    <b>Driver</b> = processo responsável pelo resultado — responsabilidade de negócio/produto.
  </div>
  <div class="filter-row">
    <span>Filtrar equipe:</span>
    <select id="mensal-driver-team-filter" onchange="renderMensalDriver()">
      <option value="">Todas</option>
      {"".join(f'<option value="{esc(lbl(t))}">{esc(lbl(t))}</option>' for t in TEAMS)}
    </select>
  </div>
  <div id="mensal-driver-table">{driver_table_html(driver_mtd, MONTH_LBL)}</div>
</div>

<div class="section">
  <div class="section-title">BOTTOM BOX · {MONTH_LBL}</div>
  <div class="notice" style="margin-bottom:10px"><b>Bottom Box</b> = notas 1 e 2. Priorizar BB &gt; 25% com vol &gt; 100.</div>
  <div class="filter-row">
    <span>Filtrar equipe:</span>
    <select id="mensal-bb-team-filter" onchange="renderMensalBB()">
      <option value="">Todas</option>
      {"".join(f'<option value="{esc(lbl(t))}">{esc(lbl(t))}</option>' for t in TEAMS)}
    </select>
    <span style="margin-left:16px">Volume mín.:</span>
    <select id="mensal-bb-vol-filter" onchange="renderMensalBB()">
      <option value="0">Sem filtro</option>
      <option value="50">≥ 50</option>
      <option value="100" selected>≥ 100</option>
      <option value="300">≥ 300</option>
    </select>
  </div>
  <div id="mensal-bb-table"></div>
</div>"""


# ── ABA: EVOLUÇÃO SEMANAL ─────────────────────────────────────────────────────
def tab_semanal():
    wtd_rows = "".join(team_row_html(r) for r in lineal_wtd)

    week_cards = f"""
<div class="section">
  <div class="section-title">RESUMO · Semana {WEEK_LBL}</div>
  <div class="cards-row">
    {metric_card("CSAT LINEAL · Semana "+WEEK_LBL, pct(c_wtd.get('csat')), fmt(c_wtd.get('total',0))+" pesquisas", csat_color(c_wtd.get('csat')))}
    {metric_card("BOTTOM BOX · Semana "+WEEK_LBL, pct(c_wtd.get('bottom_box_pct')), "Notas 1-2", bb_color(c_wtd.get('bottom_box_pct')))}
    {metric_card("RESPONSE RATE · Semana "+WEEK_LBL, pct(rr_consol_wtd.get('rr_pct')), fmt(rr_consol_wtd.get('answered',0))+" de "+fmt(rr_consol_wtd.get('sent',0))+" enviadas")}
  </div>
</div>"""

    return f"""
{week_cards}

<div class="section">
  <div class="section-title">LINEAL — POR EQUIPE · Semana {WEEK_LBL}</div>
  <div class="section-sub">Equipe que atendeu o contato — responsabilidade operacional</div>
  <table class="tbl">
    <thead><tr><th>Equipe</th><th>CSAT</th><th>Volume</th><th>Bottom Box</th><th>Response Rate</th></tr></thead>
    <tbody>{wtd_rows}</tbody>
  </table>
</div>

<div class="section">
  <div class="section-title">BREAKDOWN POR PROCESSO · Semana {WEEK_LBL}</div>
  <div id="semanal-proc-container"></div>
</div>

<div class="section">
  <div class="section-title">DRIVER (PROCESSO) · Semana {WEEK_LBL}</div>
  <div class="notice" style="margin-bottom:10px">
    <b>Driver</b> = processo responsável pelo resultado — responsabilidade de negócio/produto.
  </div>
  <div class="filter-row">
    <span>Filtrar equipe:</span>
    <select id="semanal-driver-team-filter" onchange="renderSemanalDriver()">
      <option value="">Todas</option>
      {"".join(f'<option value="{esc(lbl(t))}">{esc(lbl(t))}</option>' for t in TEAMS)}
    </select>
  </div>
  <div id="semanal-driver-table">{driver_table_html(driver_wtd, "Semana "+WEEK_LBL)}</div>
</div>

<div class="section">
  <div class="section-title">BOTTOM BOX · Semana {WEEK_LBL}</div>
  <div class="notice" style="margin-bottom:10px"><b>Bottom Box</b> = notas 1 e 2. Priorizar BB &gt; 25% com vol &gt; 100.</div>
  <div class="filter-row">
    <span>Filtrar equipe:</span>
    <select id="semanal-bb-team-filter" onchange="renderSemanalBB()">
      <option value="">Todas</option>
      {"".join(f'<option value="{esc(lbl(t))}">{esc(lbl(t))}</option>' for t in TEAMS)}
    </select>
    <span style="margin-left:16px">Volume mín.:</span>
    <select id="semanal-bb-vol-filter" onchange="renderSemanalBB()">
      <option value="0">Sem filtro</option>
      <option value="50">≥ 50</option>
      <option value="100" selected>≥ 100</option>
      <option value="300">≥ 300</option>
    </select>
  </div>
  <div id="semanal-bb-table"></div>
</div>"""


# ── ABA: LINEAL ───────────────────────────────────────────────────────────────
def tab_lineal():
    # MTD table
    mtd_rows = "".join(team_row_html(r) for r in lineal_mtd)
    wtd_rows = "".join(team_row_html(r) for r in lineal_wtd)

    return f"""
<div class="period-bar">
  <button class="pbtn active" onclick="switchLineal('MTD',this)">{MONTH_LBL}</button>
  <button class="pbtn" onclick="switchLineal('WTD',this)">Semana {WEEK_LBL}</button>
</div>

<div id="lineal-MTD">
  <div class="section">
    <div class="section-title">CSAT LINEAL — POR EQUIPE · {MONTH_LBL}</div>
    <div class="section-sub">Equipe que atendeu o contato — responsabilidade operacional</div>
    <table class="tbl">
      <thead><tr><th>Equipe</th><th>CSAT</th><th>Volume</th><th>Bottom Box</th><th>Response Rate</th></tr></thead>
      <tbody id="lineal-mtd-rows">{mtd_rows}</tbody>
    </table>
  </div>
  <div class="section">
    <div class="section-title">BREAKDOWN POR PROCESSO · {MONTH_LBL}</div>
    <div id="lineal-proc-mtd-container"></div>
  </div>
</div>

<div id="lineal-WTD" style="display:none">
  <div class="section">
    <div class="section-title">CSAT LINEAL — POR EQUIPE · Semana {WEEK_LBL}</div>
    <div class="section-sub">Equipe que atendeu o contato — responsabilidade operacional</div>
    <table class="tbl">
      <thead><tr><th>Equipe</th><th>CSAT</th><th>Volume</th><th>Bottom Box</th><th>Response Rate</th></tr></thead>
      <tbody id="lineal-wtd-rows">{wtd_rows}</tbody>
    </table>
  </div>
  <div class="section">
    <div class="section-title">BREAKDOWN POR PROCESSO · Semana {WEEK_LBL}</div>
    <div id="lineal-proc-wtd-container"></div>
  </div>
</div>"""

# ── ABA: DRIVER ───────────────────────────────────────────────────────────────
def driver_table_html(rows, period_lbl):
    if not rows:
        return "<p>Sem dados.</p>"
    html_rows = ""
    for r in rows:
        html_rows += f"""<tr>
  <td>{esc(r['process'])}</td>
  <td style="color:{csat_color(r['csat'])};font-weight:700">{pct(r['csat'])}</td>
  <td>{fmt(r['total'])}</td>
  <td style="color:{bb_color(r['bottom_box_pct'])};font-weight:600">{pct(r['bottom_box_pct'])}</td>
  <td>{fmt(r['bottom_box'])}</td>
</tr>"""
    return f"""<table class="tbl">
  <thead><tr><th>Processo (Driver)</th><th>CSAT</th><th>Volume</th><th>Bottom Box %</th><th>Detratores</th></tr></thead>
  <tbody>{html_rows}</tbody>
</table>"""

def tab_driver():
    return f"""
<div class="period-bar">
  <button class="pbtn active" onclick="switchDriver('MTD',this)">{MONTH_LBL}</button>
  <button class="pbtn" onclick="switchDriver('WTD',this)">Semana {WEEK_LBL}</button>
</div>
<div class="notice" style="margin-bottom:12px">
  <b>Driver</b> = processo responsável pelo resultado — responsabilidade de negócio/produto.<br>
  Quando CSAT Driver diverge do Lineal, o problema é estrutural, não operacional.
</div>

<div class="filter-row">
  <span>Filtrar equipe:</span>
  <select id="driver-team-filter" onchange="renderDriver()">
    <option value="">Todas</option>
    {"".join(f'<option value="{esc(lbl(t))}">{esc(lbl(t))}</option>' for t in TEAMS)}
  </select>
</div>

<div id="driver-MTD">
  <div class="section">
    <div class="section-title">CSAT POR DRIVER (PROCESSO) · {MONTH_LBL}</div>
    <div id="driver-mtd-table">{driver_table_html(driver_mtd, MONTH_LBL)}</div>
  </div>
</div>
<div id="driver-WTD" style="display:none">
  <div class="section">
    <div class="section-title">CSAT POR DRIVER (PROCESSO) · Semana {WEEK_LBL}</div>
    <div id="driver-wtd-table">{driver_table_html(driver_wtd, WEEK_LBL)}</div>
  </div>
</div>"""

# ── ABA: BOTTOM BOX ───────────────────────────────────────────────────────────
def tab_bottom_box():
    return f"""
<div class="period-bar">
  <button class="pbtn active" onclick="switchBB('MTD',this)">{MONTH_LBL}</button>
  <button class="pbtn" onclick="switchBB('WTD',this)">Semana {WEEK_LBL}</button>
</div>
<div class="notice" style="margin-bottom:12px">
  <b>Bottom Box</b> = notas 1 e 2. Priorizar processos com BB &gt; 25% E volume &gt; 100 pesquisas.
</div>

<div class="filter-row">
  <span>Filtrar equipe:</span>
  <select id="bb-team-filter" onchange="renderBB()">
    <option value="">Todas</option>
    {"".join(f'<option value="{esc(lbl(t))}">{esc(lbl(t))}</option>' for t in TEAMS)}
  </select>
  <span style="margin-left:16px">Volume mín.:</span>
  <select id="bb-vol-filter" onchange="renderBB()">
    <option value="0">Sem filtro</option>
    <option value="50">≥ 50</option>
    <option value="100" selected>≥ 100</option>
    <option value="300">≥ 300</option>
  </select>
</div>

<div id="bb-MTD">
  <div class="section">
    <div class="section-title">BOTTOM BOX POR PROCESSO · {MONTH_LBL}</div>
    <div id="bb-mtd-table"></div>
  </div>
</div>
<div id="bb-WTD" style="display:none">
  <div class="section">
    <div class="section-title">BOTTOM BOX POR PROCESSO · Semana {WEEK_LBL}</div>
    <div id="bb-wtd-table"></div>
  </div>
</div>"""

# ── ABA: COMENTÁRIOS ──────────────────────────────────────────────────────────
def tab_comentarios():
    unique_procs = sorted({c["process"] for c in all_comments})
    proc_opts = "".join(f'<option value="{esc(p)}">{esc(p)}</option>' for p in unique_procs)
    unique_teams = sorted({c["team"] for c in all_comments})
    team_opts = "".join(f'<option value="{esc(t)}">{esc(t)}</option>' for t in unique_teams)

    return f"""
<div class="notice" style="margin-bottom:12px">
  Verbatims de detratores (nota 1–2). Total disponível: {len(all_comments)} comentários.
</div>
<div class="filter-row" style="flex-wrap:wrap;gap:8px">
  <span>Período:</span>
  <select id="com-period-filter" onchange="renderComments()">
    <option value="">Todos</option>
    <option value="MTD">MTD</option>
    <option value="WTD">Semana</option>
  </select>
  <span>Equipe:</span>
  <select id="com-team-filter" onchange="renderComments()">
    <option value="">Todas</option>
    {team_opts}
  </select>
  <span>Processo:</span>
  <select id="com-proc-filter" onchange="renderComments()">
    <option value="">Todos</option>
    {proc_opts}
  </select>
  <span>Nota:</span>
  <select id="com-score-filter" onchange="renderComments()">
    <option value="">Todas</option>
    <option value="1">1</option>
    <option value="2">2</option>
  </select>
  <input id="com-search" type="text" placeholder="Buscar texto…" oninput="renderComments()"
         style="padding:4px 8px;border:1px solid #cbd5e1;border-radius:6px;font-size:13px;flex:1;min-width:150px">
</div>
<div class="section" style="margin-top:8px">
  <div id="com-count" style="font-size:12px;color:#64748b;margin-bottom:8px"></div>
  <div id="com-table"></div>
</div>"""

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f1f5f9;color:#1e293b;font-size:14px}
.header{background:#1e293b;color:#fff;padding:16px 24px;display:flex;justify-content:space-between;align-items:flex-start}
.header h1{font-size:1.3rem;font-weight:700;margin-bottom:4px}
.header .sub{font-size:11px;color:#94a3b8;line-height:1.6}
.header .meta{text-align:right;font-size:12px;color:#94a3b8;white-space:nowrap}
.header .meta b{color:#e2e8f0;font-size:13px}
.tabs-nav{background:#fff;border-bottom:1px solid #e2e8f0;display:flex;padding:0 20px;overflow-x:auto}
.tab-btn{padding:12px 18px;font-size:13px;font-weight:600;color:#64748b;border:none;background:none;cursor:pointer;border-bottom:3px solid transparent;white-space:nowrap}
.tab-btn:hover{color:#0f172a}
.tab-btn.active{color:#0369a1;border-bottom-color:#0369a1}
.tab-pane{display:none;padding:20px}
.tab-pane.active{display:block}
.notice{background:#fefce8;border:1px solid #fde68a;border-radius:8px;padding:10px 14px;font-size:12px;color:#713f12}
.period-bar{display:flex;gap:8px;margin-bottom:16px}
.pbtn{padding:6px 16px;border-radius:20px;border:1.5px solid #cbd5e1;background:#fff;cursor:pointer;font-size:13px;font-weight:600;color:#475569}
.pbtn.active{background:#0369a1;color:#fff;border-color:#0369a1}
.filter-row{display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap}
.filter-row select{padding:4px 10px;border:1px solid #cbd5e1;border-radius:6px;font-size:13px}
.section{background:#fff;border-radius:10px;padding:18px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.section-title{font-size:11px;font-weight:700;color:#64748b;letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px}
.section-sub{font-size:11px;color:#94a3b8;margin-bottom:12px}
.cards-row{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px}
.card{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 18px;min-width:160px;flex:1}
.card-title{font-size:10px;font-weight:700;color:#64748b;letter-spacing:.05em;text-transform:uppercase;margin-bottom:6px}
.card-value{font-size:2.2rem;font-weight:800;line-height:1;margin-bottom:4px}
.card-sub{font-size:11px;color:#94a3b8}
.tbl{width:100%;border-collapse:collapse;font-size:13px}
.tbl th{background:#f8fafc;color:#64748b;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;padding:8px 12px;text-align:left;border-bottom:2px solid #e2e8f0}
.tbl td{padding:8px 12px;border-bottom:1px solid #f1f5f9}
.tbl tr:hover td{background:#f8fafc}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}
.proc-table{margin-top:12px}
.com-row{border-bottom:1px solid #f1f5f9;padding:10px 0}
.com-row:last-child{border-bottom:none}
.badge{display:inline-block;padding:2px 7px;border-radius:10px;font-size:11px;font-weight:700}
.badge-1{background:#fee2e2;color:#991b1b}
.badge-2{background:#fed7aa;color:#92400e}
/* ── Sidebar histórico ─────────────────────────────────── */
.wk-sidebar{position:fixed;top:0;left:0;width:220px;height:100vh;background:#1a1e2e;color:#c8cfe0;display:flex;flex-direction:column;z-index:300;}
.wk-sb-head{padding:14px 16px 10px;border-bottom:1px solid #2e3350;flex-shrink:0;}
.wk-sb-title{font-size:13px;font-weight:700;color:#fff;margin-bottom:3px;}
.wk-sb-sub{font-size:10px;color:#7a8aaa;}
.wk-sb-nav{overflow-y:auto;flex:1;padding:6px 0 20px;}
.wk-sb-nav::-webkit-scrollbar{width:3px;}
.wk-sb-nav::-webkit-scrollbar-thumb{background:#2e3350;border-radius:4px;}
.wk-sb-week{padding:8px 16px;display:flex;align-items:center;gap:8px;cursor:pointer;border-left:3px solid transparent;transition:all .15s;}
.wk-sb-week:hover{background:#252a3d;color:#fff;}
.wk-sb-week.active{background:#252a3d;border-left-color:#0369a1;}
.wk-sb-week.active .wk-lbl{color:#fff;font-weight:700;}
.wk-lbl{font-size:12px;color:#c8cfe0;flex:1;line-height:1.4;}
.wk-badge{font-size:9px;font-weight:700;padding:1px 5px;border-radius:4px;white-space:nowrap;}
.wk-badge.vig{background:#0369a133;color:#38bdf8;border:1px solid #0369a166;}
.wk-badge.old{background:#2e3350;color:#7a8aaa;}
/* ── Layout principal ──────────────────────────────────── */
.main-content{margin-left:220px;min-height:100vh;}
/* ── Viewer de snapshot histórico ──────────────────────── */
.wk-viewer{display:none;position:fixed;top:0;left:220px;right:0;bottom:0;z-index:200;flex-direction:column;background:#f1f5f9;}
.wk-viewer.open{display:flex;}
.wk-viewer-bar{background:#1a1e2e;color:#fff;padding:8px 16px;display:flex;align-items:center;gap:14px;flex-shrink:0;box-shadow:0 2px 8px rgba(0,0,0,.3);}
.wk-back-btn{background:#0369a1;color:#fff;border:none;border-radius:6px;padding:5px 14px;font-size:12px;font-weight:700;cursor:pointer;}
.wk-back-btn:hover{background:#0284c7;}
.wk-viewer-title{font-size:13px;font-weight:700;flex:1;}
.wk-viewer-sub{font-size:11px;color:#7a8aaa;}
.wk-viewer-frame{flex:1;border:none;width:100%;}
"""

# ── JavaScript ─────────────────────────────────────────────────────────────────
JS = f"""
const CHART_DATA       = {JS_CHART};
const LINEAL_MTD       = {JS_LINEAL_MTD};
const LINEAL_WTD       = {JS_LINEAL_WTD};
const LINEAL_PROC_MTD  = {JS_LINEAL_PROC_MTD};
const LINEAL_PROC_WTD  = {JS_LINEAL_PROC_WTD};
const DRIVER_MTD       = {JS_DRIVER_MTD};
const DRIVER_WTD       = {JS_DRIVER_WTD};
const DRIVER_BY_TEAM_MTD = {JS_DRIVER_BY_TEAM_MTD};
const DRIVER_BY_TEAM_WTD = {JS_DRIVER_BY_TEAM_WTD};
const BB_MTD           = {JS_BB_MTD};
const BB_WTD           = {JS_BB_WTD};
const COMMENTS         = {JS_COMMENTS};
const TEAM_COLORS      = {json.dumps({lbl(t): clr(t) for t in TEAMS}, ensure_ascii=False)};
const TEAM_COLOR_IDS   = {json.dumps({t: clr(t) for t in TEAMS}, ensure_ascii=False)};
var   _GHPAGES_BASE    = "{GHPAGES_BASE}";
var   _HISTORY         = {JS_HISTORY};

// ── Sidebar histórico ─────────────────────────────────────────────────────────
(function buildNav() {{
  var nav = document.getElementById('wkNav');
  if(!nav) return;
  var html = '<div class="wk-sb-week active" id="wkVigEntry" data-file="" data-lbl="Semana Vigente" onclick="wkClick(this)">';
  html += '<div class="wk-lbl">Semana Vigente<br><span style="font-size:10px;color:#7a8aaa">{WEEK_LBL}</span></div>';
  html += '<span class="wk-badge vig">ATUAL</span></div>';
  _HISTORY.forEach(function(it) {{
    html += '<div class="wk-sb-week" data-file="' + encodeURIComponent(it.file) + '" data-lbl="' + it.label + '" onclick="wkClick(this)">';
    html += '<div class="wk-lbl">' + it.label + '</div>';
    html += '<span class="wk-badge old">↗</span></div>';
  }});
  if(!_HISTORY.length) {{
    html += '<div style="padding:16px;font-size:11px;color:#7a8aaa;line-height:1.6">Histórico acumula<br>a cada atualização</div>';
  }}
  nav.innerHTML = html;
}})();

function wkClick(el) {{
  var file = decodeURIComponent(el.getAttribute('data-file'));
  var lbl  = el.getAttribute('data-lbl');
  document.querySelectorAll('.wk-sb-week').forEach(function(w){{w.classList.remove('active');}});
  el.classList.add('active');
  if(!file) {{ wkBack(); return; }}
  document.getElementById('wkTitle').textContent = lbl;
  document.getElementById('wkFrame').src = _GHPAGES_BASE + 'history_csat/' + file + '?t=' + Date.now();
  document.getElementById('wkViewer').classList.add('open');
}}

function wkBack() {{
  document.getElementById('wkViewer').classList.remove('open');
  document.getElementById('wkFrame').src = 'about:blank';
  document.querySelectorAll('.wk-sb-week').forEach(function(w){{w.classList.remove('active');}});
  var vig = document.getElementById('wkVigEntry');
  if(vig) vig.classList.add('active');
}}

// ── Tab switching ──────────────────────────────────────────────────────────────
function showTab(id, el) {{
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
  if(id === 'tab-exec')    initChart();
  if(id === 'tab-mensal')  {{ renderMensalLineal(); renderMensalBB(); }}
  if(id === 'tab-semanal') {{ renderSemanalLineal(); renderSemanalBB(); }}
  if(id === 'tab-com')     renderComments();
}}

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(n) {{ return (n||0).toLocaleString('pt-BR'); }}
function pct(v) {{ return v!=null ? v.toFixed(1)+'%' : '—'; }}
function csatColor(v) {{
  if(v==null) return '#888';
  if(v>=84) return '#16a34a';
  if(v>=80) return '#d97706';
  return '#dc2626';
}}
function bbColor(v) {{
  if(v==null) return '#888';
  if(v<=15) return '#16a34a';
  if(v<=25) return '#d97706';
  return '#dc2626';
}}

function renderProcTable(procData, containerId) {{
  const el = document.getElementById(containerId);
  if(!el) return;
  let html = '';
  for(const [team, rows] of Object.entries(procData)) {{
    if(!rows.length) continue;
    const col = TEAM_COLORS[team] || '#888';
    html += `<div style="margin-bottom:16px"><div style="font-size:12px;font-weight:700;color:${{col}};margin-bottom:6px">${{team}}</div>`;
    html += '<table class="tbl"><thead><tr><th>Processo</th><th>CSAT</th><th>Volume</th><th>Bottom Box</th></tr></thead><tbody>';
    for(const r of rows) {{
      html += `<tr><td>${{r.process}}</td><td style="color:${{csatColor(r.csat)}};font-weight:700">${{pct(r.csat)}}</td><td>${{fmt(r.total)}}</td><td style="color:${{bbColor(r.bottom_box_pct)}};font-weight:600">${{pct(r.bottom_box_pct)}}</td></tr>`;
    }}
    html += '</tbody></table></div>';
  }}
  el.innerHTML = html || '<p style="color:#888">Sem dados.</p>';
}}

function renderDriverTable(data, byTeamData, teamFilterId, tableId) {{
  const teamFilter = document.getElementById(teamFilterId).value;
  const el = document.getElementById(tableId);
  if(!el) return;
  let rows = teamFilter ? byTeamData.filter(r => r.team === teamFilter).sort((a,b)=>b.total-a.total) : data;
  let html = '<table class="tbl"><thead><tr><th>Processo (Driver)</th>';
  if(teamFilter) html += '<th>Equipe</th>';
  html += '<th>CSAT</th><th>Volume</th><th>Bottom Box %</th><th>Detratores</th></tr></thead><tbody>';
  for(const r of rows) {{
    html += `<tr><td>${{r.process}}</td>${{teamFilter?'<td>'+r.team+'</td>':''}}
      <td style="color:${{csatColor(r.csat)}};font-weight:700">${{pct(r.csat)}}</td>
      <td>${{fmt(r.total)}}</td>
      <td style="color:${{bbColor(r.bottom_box_pct)}};font-weight:600">${{pct(r.bottom_box_pct)}}</td>
      <td>${{fmt(r.bottom_box)}}</td></tr>`;
  }}
  html += '</tbody></table>';
  el.innerHTML = html;
}}

function renderBBTable(raw, teamFilterId, volFilterId, tableId) {{
  const teamFilter = document.getElementById(teamFilterId).value;
  const volMin = parseInt(document.getElementById(volFilterId).value) || 0;
  const el = document.getElementById(tableId);
  if(!el) return;
  let rows = raw.filter(r => (!teamFilter || r.team===teamFilter) && r.total >= volMin);
  rows.sort((a,b) => (b.bb_pct||0)-(a.bb_pct||0));
  if(!rows.length) {{ el.innerHTML='<p style="color:#888">Sem dados com esses filtros.</p>'; return; }}
  let html = '<table class="tbl"><thead><tr><th>Processo</th><th>Equipe</th><th>CSAT</th><th>Volume</th><th>Detratores</th><th>Bottom Box %</th></tr></thead><tbody>';
  for(const r of rows) {{
    const crit = r.bb_pct > 25 && r.total >= 100;
    html += `<tr${{crit?' style="background:#fff7ed"':''}}>
      <td>${{r.process}}${{crit?' <span title="BB>25% e vol>100" style="color:#d97706">⚠</span>':''}}</td>
      <td><span class="dot" style="background:${{TEAM_COLOR_IDS[r.team_id]||'#888'}}"></span>${{r.team}}</td>
      <td style="color:${{csatColor(r.csat)}};font-weight:700">${{pct(r.csat)}}</td>
      <td>${{fmt(r.total)}}</td>
      <td>${{fmt(r.bb)}}</td>
      <td style="color:${{bbColor(r.bb_pct)}};font-weight:700">${{pct(r.bb_pct)}}</td>
    </tr>`;
  }}
  html += '</tbody></table>';
  el.innerHTML = html;
}}

// ── Trend chart ───────────────────────────────────────────────────────────────
let chartInst = null;
function initChart() {{
  if(chartInst) return;
  const ctx = document.getElementById('trendChart');
  if(!ctx) return;
  chartInst = new Chart(ctx, {{
    type: 'line',
    data: CHART_DATA,
    options: {{
      responsive:true,
      plugins:{{legend:{{position:'bottom'}}}},
      scales:{{y:{{min:70,max:100,ticks:{{callback:v=>v+'%'}}}}}}
    }}
  }});
}}

// ── Evolução Mensal ───────────────────────────────────────────────────────────
function renderMensalLineal() {{ renderProcTable(LINEAL_PROC_MTD, 'mensal-proc-container'); }}
function renderMensalDriver() {{ renderDriverTable(DRIVER_MTD, DRIVER_BY_TEAM_MTD, 'mensal-driver-team-filter', 'mensal-driver-table'); }}
function renderMensalBB()     {{ renderBBTable(BB_MTD, 'mensal-bb-team-filter', 'mensal-bb-vol-filter', 'mensal-bb-table'); }}

// ── Evolução Semanal ──────────────────────────────────────────────────────────
function renderSemanalLineal() {{ renderProcTable(LINEAL_PROC_WTD, 'semanal-proc-container'); }}
function renderSemanalDriver() {{ renderDriverTable(DRIVER_WTD, DRIVER_BY_TEAM_WTD, 'semanal-driver-team-filter', 'semanal-driver-table'); }}
function renderSemanalBB()     {{ renderBBTable(BB_WTD, 'semanal-bb-team-filter', 'semanal-bb-vol-filter', 'semanal-bb-table'); }}

// ── Comentários ───────────────────────────────────────────────────────────────
function renderComments() {{
  const period = document.getElementById('com-period-filter').value;
  const team   = document.getElementById('com-team-filter').value;
  const proc   = document.getElementById('com-proc-filter').value;
  const score  = document.getElementById('com-score-filter').value;
  const search = document.getElementById('com-search').value.toLowerCase();
  let rows = COMMENTS.filter(c =>
    (!period || c.period===period) &&
    (!team   || c.team===team) &&
    (!proc   || c.process===proc) &&
    (!score  || String(c.score)===score) &&
    (!search || c.text.toLowerCase().includes(search))
  );
  document.getElementById('com-count').textContent = rows.length + ' comentários';
  const el = document.getElementById('com-table');
  if(!rows.length) {{ el.innerHTML='<p style="color:#888">Sem comentários com esses filtros.</p>'; return; }}
  let html = '';
  for(const r of rows.slice(0,300)) {{
    const badgeCls = r.score===1 ? 'badge-1' : 'badge-2';
    html += `<div class="com-row">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <span class="badge ${{badgeCls}}">Nota ${{r.score}}</span>
        <span style="font-size:11px;color:${{TEAM_COLORS[r.team]||'#888'}};font-weight:700">${{r.team}}</span>
        <span style="font-size:11px;color:#64748b">· ${{r.process}}</span>
        <span style="font-size:11px;color:#94a3b8;margin-left:auto">${{r.period}}</span>
      </div>
      <div style="font-size:13px;color:#334155;line-height:1.5">${{r.text}}</div>
    </div>`;
  }}
  if(rows.length > 300) html += '<p style="color:#888;font-size:12px;margin-top:8px">Mostrando 300 de '+rows.length+' resultados.</p>';
  el.innerHTML = html;
}}

// ── Init ──────────────────────────────────────────────────────────────────────
window.addEventListener('load', () => {{
  initChart();
  renderMensalLineal();
  renderMensalBB();
  renderSemanalLineal();
  renderSemanalBB();
  renderComments();
}});
"""

# ── Montar HTML final ─────────────────────────────────────────────────────────
print("Gerando HTML…")

HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CSAT — Sellers Longtail BR — {UPDATED}</title>
<script src="/d/_libs/chart.min.js"></script>
<style>{CSS}</style>
</head>
<body>

<!-- ── Sidebar de semanas ──────────────────────────────────────────── -->
<nav class="wk-sidebar" id="wkSidebar">
  <div class="wk-sb-head">
    <div class="wk-sb-title">CSAT Sellers BR</div>
    <div class="wk-sb-sub">Dados até {UPDATED}</div>
  </div>
  <div class="wk-sb-nav" id="wkNav"><!-- preenchido pelo JS --></div>
</nav>

<!-- ── Viewer de snapshot histórico ───────────────────────────────── -->
<div class="wk-viewer" id="wkViewer">
  <div class="wk-viewer-bar">
    <button class="wk-back-btn" onclick="wkBack()">&#8592; Atual</button>
    <span class="wk-viewer-title" id="wkTitle"></span>
    <span class="wk-viewer-sub">Dados do período selecionado</span>
  </div>
  <iframe class="wk-viewer-frame" id="wkFrame" src="about:blank"></iframe>
</div>

<!-- ── Conteúdo principal ─────────────────────────────────────────── -->
<div class="main-content" id="mainContent">

<div class="header">
  <div>
    <h1>CSAT — Sellers Longtail BR</h1>
    <div class="sub">Fonte: BT_CX_CSAT_DETAIL &nbsp;|&nbsp; Filtro: ELIGIBLE_CS=TRUE · IS_ANSWERED=TRUE · IS_EXCLUDED IS NOT TRUE</div>
    <div class="sub">Equipes: BR ME Sellers Longtail · BR Ventas Sellers Longtail · BR Publicaciones Sellers Longtail</div>
  </div>
  <div class="meta">
    <div><b>Dados até {UPDATED}</b></div>
    <div>{MONTH_LBL} · Semana {WEEK_LBL}</div>
  </div>
</div>

<div class="tabs-nav">
  <button class="tab-btn active" onclick="showTab('tab-exec',this)">&#128202; Vis&#227;o Executiva</button>
  <button class="tab-btn" onclick="showTab('tab-mensal',this)">&#128197; Evolu&#231;&#227;o Mensal</button>
  <button class="tab-btn" onclick="showTab('tab-semanal',this)">&#128198; Evolu&#231;&#227;o Semanal</button>
  <button class="tab-btn" onclick="showTab('tab-com',this)">&#128172; Coment&#225;rios</button>
</div>

<div id="tab-exec" class="tab-pane active">
  {tab_visao_geral()}
</div>

<div id="tab-mensal" class="tab-pane">
  {tab_mensal()}
</div>

<div id="tab-semanal" class="tab-pane">
  {tab_semanal()}
</div>

<div id="tab-com" class="tab-pane">
  {tab_comentarios()}
</div>

</div><!-- end .main-content -->

<script>{JS}</script>
</body>
</html>"""

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = len(HTML.encode("utf-8")) // 1024
print(f"\n✅ Salvo: {OUTPUT} ({size_kb} KB)")
print(f"   Abas: Visão Executiva · Evolução Mensal · Evolução Semanal · Comentários")
print(f"   MTD: {MONTH_LBL}  |  WTD: Semana {WEEK_LBL}")
print(f"   Comentários carregados: {len(all_comments)}")
print(f"   Histórico disponível: {len(history_items)} semanas em {HISTORY_DIR}/")

# ── Salvar snapshot histórico ──────────────────────────────────────────────────
os.makedirs(HISTORY_DIR, exist_ok=True)
snap_date  = D.get("yesterday", UPDATED[:10])
snap_file  = os.path.join(HISTORY_DIR, f"semana_{snap_date}.html")

if not os.path.exists(snap_file):
    # Snapshot: mesma estrutura do dashboard, mas sem a sidebar lateral
    SNAP_HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CSAT Sellers BR — Semana {WEEK_LBL}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>{CSS.replace('.main-content{margin-left:220px;min-height:100vh;}', '.main-content{margin-left:0;min-height:100vh;}')}</style>
</head>
<body>
<div class="header">
  <div>
    <h1>CSAT — Sellers Longtail BR</h1>
    <div class="sub">Snapshot: Semana {WEEK_LBL} &nbsp;|&nbsp; Dados até {UPDATED}</div>
    <div class="sub">Equipes: BR ME Sellers Longtail · BR Ventas Sellers Longtail · BR Publicaciones Sellers Longtail</div>
  </div>
  <div class="meta">
    <div><b>Dados até {UPDATED}</b></div>
    <div>{MONTH_LBL} · Semana {WEEK_LBL}</div>
  </div>
</div>
<div class="tabs-nav">
  <button class="tab-btn active" onclick="showTab('tab-exec',this)">&#128202; Vis&#227;o Executiva</button>
  <button class="tab-btn" onclick="showTab('tab-mensal',this)">&#128197; Evolu&#231;&#227;o Mensal</button>
  <button class="tab-btn" onclick="showTab('tab-semanal',this)">&#128198; Evolu&#231;&#227;o Semanal</button>
  <button class="tab-btn" onclick="showTab('tab-com',this)">&#128172; Coment&#225;rios</button>
</div>
<div id="tab-exec" class="tab-pane active">{tab_visao_geral()}</div>
<div id="tab-mensal" class="tab-pane">{tab_mensal()}</div>
<div id="tab-semanal" class="tab-pane">{tab_semanal()}</div>
<div id="tab-com" class="tab-pane">{tab_comentarios()}</div>
<script>{JS}</script>
</body>
</html>"""
    with open(snap_file, "w", encoding="utf-8") as f:
        f.write(SNAP_HTML)
    print(f"   ✓ Snapshot salvo: {snap_file}")
else:
    print(f"   ~ Snapshot já existe: {snap_file}")
