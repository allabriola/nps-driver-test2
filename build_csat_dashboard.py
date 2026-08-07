#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_csat_dashboard.py — Gera csat_dashboard.html a partir dos dados de CSAT

Lê:  _csat_data.json, _csat_diagnostic.json (opcional)
Salva: csat_dashboard.html
"""
import sys, json, os, html as _html
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

def esc(s): return _html.escape(str(s) if s is not None else "")

# ── Carrega dados ──────────────────────────────────────────────────────────────
print("Carregando dados…")
with open("_csat_data.json", encoding="utf-8-sig") as f:
    D = json.load(f)

DIAG = {}
if os.path.exists("_csat_diagnostic.json"):
    with open("_csat_diagnostic.json", encoding="utf-8-sig") as f:
        DIAG = json.load(f)
    print("  ✓ Diagnóstico carregado")
else:
    print("  ! _csat_diagnostic.json não encontrado — tooltips sem diagnóstico IA")

# ── Helpers ────────────────────────────────────────────────────────────────────
UPDATED   = D.get("updated_at", "")
MONTHS    = D.get("months", [])
MLABELS   = D.get("month_labels", {})
MONTH_CUR = D.get("month_cur", "")
WEEK_LBL  = D.get("week_label", "")
MONTH_LBL = D.get("month_cur_label", "Mês MTD")
TEAMS     = D.get("teams", [])

TEAM_LABELS = {
    "BR_ME_Sellers_Longtail":             "ME",
    "BR_Publicaciones_Sellers_Longtail":  "Publicaciones",
    "BR_Ventas_Sellers_Longtail":         "Ventas",
    "MLB_ExpImpo":                        "ExpImpo",
}
TEAM_FULL = {
    "BR_ME_Sellers_Longtail":             "BR ME Sellers Longtail",
    "BR_Publicaciones_Sellers_Longtail":  "BR Publicaciones Sellers Longtail",
    "BR_Ventas_Sellers_Longtail":         "BR Ventas Sellers Longtail",
    "MLB_ExpImpo":                        "MLB ExpImpo",
}

KM_ORDER = ["M1", "M2", "M3", "VETERANO", "NESTING"]

def fn(v, dec=1):
    if v is None: return "—"
    try:
        return f"{float(v):.{dec}f}".replace(".", ",")
    except Exception:
        return str(v)

def fmt_pct(v):  return fn(v, 1) + "%" if v is not None else "—"
def fmt_vol(v):  return f"{int(v):,}".replace(",", ".") if v is not None else "—"

def csat_color_class(csat_val, target_val):
    """Retorna classe CSS conforme gap vs target."""
    if csat_val is None or target_val is None or target_val == 0:
        return "neu"
    if csat_val >= target_val:
        return "ok"
    if csat_val >= target_val * 0.90:
        return "warn"
    return "crit"

def gap_str(g):
    if g is None: return "—"
    sign = "+" if g >= 0 else ""
    return f"{sign}{fn(g, 1)}pp"

def gap_class(g):
    if g is None: return "neu"
    if g >= 0: return "ok"
    if g >= -3: return "warn"
    return "crit"

# ── Lookup helpers ─────────────────────────────────────────────────────────────
def lookup_team_month(period: str, team: str | None = None):
    """Retorna linha do by_team para o período e equipe."""
    rows = D["monthly"]["by_team"] if period == "month" else D["weekly"]["by_team"]
    key  = "month" if period == "month" else None
    out  = []
    for r in rows:
        if period == "month" and r.get("month") != MONTH_CUR:
            continue
        if team and r.get("team") != team:
            continue
        out.append(r)
    return out

def lookup_by(dim: str, period: str, month: str | None = None, team: str | None = None):
    """
    dim: 'process' | 'seniority' | 'segment'
    period: 'month' | 'week'
    """
    key = "by_" + dim
    rows = D["monthly"][key] if period == "month" else D["weekly"][key]
    out = []
    for r in rows:
        if period == "month" and r.get("month") != (month or MONTH_CUR):
            continue
        if team and r.get("team") != team:
            continue
        out.append(r)
    return out

def get_rr(period: str, team: str | None = None):
    rows = D["response_rate"]["monthly"] if period == "month" else D["response_rate"]["weekly"]
    for r in rows:
        if period == "month" and r.get("month") != MONTH_CUR:
            continue
        if team and r.get("team") == team:
            return r
        if not team:
            return r  # fallback: first row
    return {}

def get_halo(period: str, team: str | None = None):
    rows = D["halo"]["monthly"] if period == "month" else D["halo"]["weekly"]
    for r in rows:
        if team and r.get("team") == team:
            return r
    return {}

def get_diag(period: str, team: str, process: str) -> str:
    """Retorna texto diagnóstico para (period, team, process)."""
    key = "monthly" if period == "month" else "weekly"
    return DIAG.get(key, {}).get(team, {}).get(process, "")

def agg_teams(rows_list: list[list[dict]], key_field: str) -> list[dict]:
    """Agrega múltiplas equipes num consolidado."""
    bucket = defaultdict(lambda: {"total": 0, "csat_n": 0.0, "target_n": 0.0})
    for rows in rows_list:
        for r in rows:
            k = r.get(key_field, "")
            t = r.get("total") or 0
            c = r.get("csat")
            tg = r.get("target")
            bucket[k]["total"] += t
            if c is not None: bucket[k]["csat_n"] += c * t
            if tg is not None: bucket[k]["target_n"] += tg * t
    out = []
    for k, v in sorted(bucket.items(), key=lambda x: -x[1]["total"]):
        t = v["total"]
        c = round(v["csat_n"] / t, 2) if t > 0 else None
        tg = round(v["target_n"] / t, 2) if t > 0 else None
        g = round(c - tg, 2) if c is not None and tg is not None else None
        item = {key_field: k, "total": t, "csat": c, "target": tg, "gap": g}
        out.append(item)
    return out

# ── Construção HTML ────────────────────────────────────────────────────────────
def kpi_tile(label: str, value: str, sub: str = "", color: str = ""):
    color_style = f"color:{color};" if color else ""
    return f"""
<div class="kpi-card">
  <div class="label">{esc(label)}</div>
  <div class="value" style="{color_style}">{esc(value)}</div>
  {f'<div class="sub">{esc(sub)}</div>' if sub else ""}
</div>"""

def halo_section(h: dict) -> str:
    if not h:
        return '<p class="info-note">Dados HALO não disponíveis para este período/equipe.</p>'
    def kpi(lbl, val, goal, lower_is_better=False, pct=True):
        v = fn(val, 1) + ("%" if pct else "")
        g = fn(goal, 1) + ("%" if pct else "")
        if val is None or goal is None:
            cls = "neu"
        elif lower_is_better:
            cls = "ok" if float(val) <= float(goal) else ("warn" if float(val) <= float(goal) * 1.1 else "crit")
        else:
            cls = "ok" if float(val) >= float(goal) else ("warn" if float(val) >= float(goal) * 0.9 else "crit")
        return f'<div class="halo-kpi"><span class="halo-lbl">{esc(lbl)}</span><span class="{cls} halo-val">{esc(v)}</span><span class="halo-goal">meta: {esc(g)}</span></div>'

    tdi  = h.get("tdi"); tdi_g = h.get("tdi_goal")
    rec  = h.get("recontact_pct"); rec_g = h.get("recontact_goal")
    ixc  = h.get("ixc"); ixc_g = h.get("ixc_goal")
    em   = h.get("estilo_meli"); em_g = h.get("estilo_meli_goal")

    return f"""
<div class="halo-grid">
  {kpi("TDI", tdi, tdi_g, lower_is_better=True, pct=False)}
  {kpi("Recontato", rec, rec_g, lower_is_better=True)}
  {kpi("IXC", ixc, ixc_g, lower_is_better=False, pct=False)}
  {kpi("Estilo Meli", em, em_g, lower_is_better=False, pct=False)}
</div>"""

def process_table(rows: list[dict], period: str, team: str | None = None,
                  show_diag: bool = True) -> str:
    if not rows:
        return '<p class="info-note">Sem dados para este período.</p>'

    rows_sorted = sorted(rows, key=lambda x: -(x.get("total") or 0))
    thead = """<tr>
      <th style="text-align:left">Processo</th>
      <th>CSAT%</th><th>Meta%</th><th>Gap</th><th>Vol</th>
    </tr>"""
    tbody = ""
    for r in rows_sorted:
        proc = r.get("process", "—")
        c = r.get("csat"); tg = r.get("target"); g = r.get("gap"); v = r.get("total")
        cls_csat = csat_color_class(c, tg)
        cls_gap  = gap_class(g)

        # Tooltip diagnóstico
        tip_html = ""
        if show_diag and team:
            diag_txt = get_diag(period, team, proc)
            if diag_txt:
                tip_data = esc(diag_txt)
                tip_html = f' class="tip" data-tip="{tip_data}"'

        tbody += f"""
<tr>
  <td{tip_html}><strong>{esc(proc)}</strong></td>
  <td class="num {cls_csat}">{fmt_pct(c)}</td>
  <td class="num">{fmt_pct(tg)}</td>
  <td class="num {cls_gap}">{gap_str(g)}</td>
  <td class="num-s">{fmt_vol(v)}</td>
</tr>"""

    return f"""
<div class="scroll-x">
<table class="dt">
<thead>{thead}</thead>
<tbody>{tbody}</tbody>
</table>
</div>"""

def seniority_table(rows: list[dict]) -> str:
    if not rows: return '<p class="info-note">Sem dados.</p>'
    order = {"VETERANO": 0, "NEWBIE": 1}
    rows_s = sorted(rows, key=lambda x: order.get(x.get("seniority", ""), 9))
    thead = '<tr><th style="text-align:left">Senioridade</th><th>CSAT%</th><th>Meta%</th><th>Gap</th><th>Vol</th></tr>'
    tbody = ""
    for r in rows_s:
        s = r.get("seniority", "—")
        c = r.get("csat"); tg = r.get("target"); g = r.get("gap"); v = r.get("total")
        cls_c = csat_color_class(c, tg); cls_g = gap_class(g)
        tbody += f'<tr><td><strong>{esc(s)}</strong></td><td class="num {cls_c}">{fmt_pct(c)}</td><td class="num">{fmt_pct(tg)}</td><td class="num {cls_g}">{gap_str(g)}</td><td class="num-s">{fmt_vol(v)}</td></tr>'
    return f'<div class="scroll-x"><table class="dt"><thead>{thead}</thead><tbody>{tbody}</tbody></table></div>'

def segment_table(rows: list[dict]) -> str:
    if not rows: return '<p class="info-note">Sem dados.</p>'
    rows_s = sorted(rows, key=lambda x: KM_ORDER.index(x.get("km_segment", ""))
                    if x.get("km_segment", "") in KM_ORDER else 9)
    thead = '<tr><th style="text-align:left">Segmento</th><th>CSAT%</th><th>Meta%</th><th>Gap</th><th>Vol</th></tr>'
    tbody = ""
    for r in rows_s:
        seg = r.get("km_segment", "—")
        c = r.get("csat"); tg = r.get("target"); g = r.get("gap"); v = r.get("total")
        cls_c = csat_color_class(c, tg); cls_g = gap_class(g)
        tbody += f'<tr><td><strong>{esc(seg)}</strong></td><td class="num {cls_c}">{fmt_pct(c)}</td><td class="num">{fmt_pct(tg)}</td><td class="num {cls_g}">{gap_str(g)}</td><td class="num-s">{fmt_vol(v)}</td></tr>'
    return f'<div class="scroll-x"><table class="dt"><thead>{thead}</thead><tbody>{tbody}</tbody></table></div>'

def seller_seg_table(rows: list[dict]) -> str:
    if not rows: return '<p class="info-note">Sem dados de segmentação de seller.</p>'
    thead = '<tr><th style="text-align:left">Segmento Seller</th><th>CSAT%</th><th>Meta%</th><th>Gap</th><th>Vol</th></tr>'
    tbody = ""
    for r in sorted(rows, key=lambda x: -(x.get("total") or 0)):
        seg = r.get("seller_segment", "—")
        c = r.get("csat"); tg = r.get("target"); g = r.get("gap"); v = r.get("total")
        cls_c = csat_color_class(c, tg); cls_g = gap_class(g)
        tbody += f'<tr><td><strong>{esc(seg)}</strong></td><td class="num {cls_c}">{fmt_pct(c)}</td><td class="num">{fmt_pct(tg)}</td><td class="num {cls_g}">{gap_str(g)}</td><td class="num-s">{fmt_vol(v)}</td></tr>'
    return f'<div class="scroll-x"><table class="dt"><thead>{thead}</thead><tbody>{tbody}</tbody></table></div>'

def fiscal_table(period: str) -> str:
    rows = D.get("fiscal_comparison", [])
    if not rows: return '<p class="info-note">Sem dados de comparativo fiscal.</p>'

    # Filtra mês corrente
    if period == "month":
        rows = [r for r in rows if r.get("month") == MONTH_CUR]
    # Para semanal não temos fiscal separado, usamos o mensal como referência
    if not rows:
        return '<p class="info-note">Sem dados fiscais para o período selecionado.</p>'

    # Organiza por processo × equipe
    proc_data = defaultdict(dict)
    for r in rows:
        proc_data[r["process"]][r["team"]] = r

    thead = '<tr><th style="text-align:left">Processo Fiscal</th><th colspan="2">MLB ExpImpo</th><th colspan="2">Ventas LT</th></tr>'
    thead2 = '<tr><th></th><th>CSAT%</th><th>Vol</th><th>CSAT%</th><th>Vol</th></tr>'
    tbody = ""
    for proc in sorted(proc_data.keys()):
        teams_ = proc_data[proc]
        exp = teams_.get("MLB_ExpImpo", {})
        ven = teams_.get("BR_Ventas_Sellers_Longtail", {})
        exp_c = exp.get("csat"); exp_tg = exp.get("target"); exp_v = exp.get("total")
        ven_c = ven.get("csat"); ven_tg = ven.get("target"); ven_v = ven.get("total")
        cls_e = csat_color_class(exp_c, exp_tg)
        cls_v = csat_color_class(ven_c, ven_tg)
        tbody += (f'<tr><td>{esc(proc)}</td>'
                  f'<td class="num {cls_e}">{fmt_pct(exp_c)}</td><td class="num-s">{fmt_vol(exp_v)}</td>'
                  f'<td class="num {cls_v}">{fmt_pct(ven_c)}</td><td class="num-s">{fmt_vol(ven_v)}</td></tr>')

    return f'<div class="scroll-x"><table class="dt"><thead>{thead}{thead2}</thead><tbody>{tbody}</tbody></table></div>'

def rr_badge(rr: dict) -> str:
    pct = rr.get("rr_pct")
    if pct is None: return "—"
    cls = "ok" if pct >= 40 else ("warn" if pct >= 25 else "crit")
    return f'<span class="{cls}">{fn(pct, 1)}%</span>'

# ── Monta seção de uma equipe (MÊS ou SEMANA) ─────────────────────────────────
def team_section(team: str | None, period: str) -> str:
    """Gera HTML completo para uma equipe num período."""
    is_consol = team is None
    period_lbl = MONTH_LBL if period == "month" else f"Semana {WEEK_LBL}"

    # Dados da equipe
    if is_consol:
        # Consolida todas as equipes
        t_rows_all = [r for r in (D["monthly"]["by_team"] if period == "month"
                                  else D["weekly"]["by_team"])
                      if (period == "month" and r.get("month") == MONTH_CUR) or period == "week"]
        t_total = sum(r.get("total") or 0 for r in t_rows_all)
        t_csat  = (round(sum((r.get("csat") or 0) * (r.get("total") or 0) for r in t_rows_all) / t_total, 2)
                   if t_total else None)
        t_tgt   = (round(sum((r.get("target") or 0) * (r.get("total") or 0) for r in t_rows_all) / t_total, 2)
                   if t_total else None)
        t_gap   = round(t_csat - t_tgt, 2) if t_csat is not None and t_tgt is not None else None
        rr      = {}  # response rate consolidado não disponível direto
    else:
        t_rows = [r for r in (D["monthly"]["by_team"] if period == "month"
                               else D["weekly"]["by_team"])
                  if r.get("team") == team
                  and (period == "week" or r.get("month") == MONTH_CUR)]
        row = t_rows[0] if t_rows else {}
        t_total = row.get("total"); t_csat = row.get("csat")
        t_tgt   = row.get("target"); t_gap  = row.get("gap")
        rr = get_rr(period, team)

    cls_csat = csat_color_class(t_csat, t_tgt)
    cls_gap  = gap_class(t_gap)
    csat_colors = {"ok": "#00a650", "warn": "#ff7733", "crit": "#e84142", "neu": "#888"}
    csat_col = csat_colors.get(cls_csat, "#888")

    # KPI tiles
    kpi_row = f"""
<div class="kpi-grid">
  {kpi_tile("CSAT", fmt_pct(t_csat), period_lbl, color=csat_col)}
  {kpi_tile("Meta", fmt_pct(t_tgt), "target da equipe")}
  {kpi_tile("Gap vs Meta", gap_str(t_gap), "positivo = acima da meta", color=csat_colors.get(cls_gap, "#888"))}
  {kpi_tile("Volume", fmt_vol(t_total), "pesquisas respondidas")}
  {kpi_tile("Response Rate", rr_badge(rr) if not is_consol else "—", f"enviadas: {fmt_vol(rr.get('sent'))}")}
</div>"""

    # HALO
    h = get_halo(period, team) if not is_consol else {}
    halo_html = f"""
<div class="section-title">HALO KPIs — {period_lbl}</div>
{halo_section(h)}"""

    # Processos
    if is_consol:
        proc_rows = agg_teams(
            [lookup_by("process", period, team=t) for t in TEAMS],
            "process"
        )
        proc_html = process_table(proc_rows, period, team=None, show_diag=False)
    else:
        proc_rows = lookup_by("process", period, team=team)
        proc_html = process_table(proc_rows, period, team=team)

    # Senioridade
    if is_consol:
        sen_rows = agg_teams(
            [lookup_by("seniority", period, team=t) for t in TEAMS],
            "seniority"
        )
    else:
        sen_rows = lookup_by("seniority", period, team=team)

    # KM Segment
    if is_consol:
        seg_rows = agg_teams(
            [lookup_by("segment", period, team=t) for t in TEAMS],
            "km_segment"
        )
    else:
        seg_rows = lookup_by("segment", period, team=team)

    # Seções extras para ExpImpo
    expimpo_html = ""
    if team == "MLB_ExpImpo":
        # Segmentação de seller
        if period == "month":
            ss_rows = [r for r in D["seller_segment"]["monthly"] if r.get("month") == MONTH_CUR]
        else:
            ss_rows = D["seller_segment"]["weekly"]
        expimpo_html = f"""
<div class="section-title">Segmentação de Seller — {period_lbl}</div>
<div class="card">{seller_seg_table(ss_rows)}</div>

<div class="section-title">Comparativo Processos Fiscais — ExpImpo vs Ventas ({period_lbl})</div>
<div class="card">
  <p class="info-note" style="margin-bottom:10px">
    Compara processos fiscais do ExpImpo com os mesmos processos na equipe Ventas Longtail (match dinâmico).
  </p>
  {fiscal_table(period)}
</div>"""

    return f"""
{kpi_row}
{halo_html}
<div class="section-title">Por Processo — {period_lbl}
  <span style="font-size:11px;font-weight:400;color:#aaa;margin-left:8px">
    {'(passe o mouse para diagnóstico)' if not is_consol else ''}
  </span>
</div>
<div class="card">{proc_html}</div>

<div class="section-title">Por Senioridade (CX_USER_EXPERIENCE)</div>
<div class="card">{seniority_table(sen_rows)}</div>

<div class="section-title">Por Maturidade de Novatos (KM_SEGMENT)</div>
<div class="card">
  <p class="info-note" style="margin-bottom:8px">M1=1º mês · M2=2º mês · M3=3º mês ou mais · VETERANO=reps experientes</p>
  {segment_table(seg_rows)}
</div>
{expimpo_html}"""

# ── Monta abas (Consolidado + por equipe) ─────────────────────────────────────
def tabs_html(period: str) -> str:
    sfx = period  # "month" ou "week"

    tab_btns = f'<button class="tab-btn active" onclick="showTeamTab(this,\'consol-{sfx}\')">Consolidado</button>'
    tab_contents = f'<div id="team-consol-{sfx}" class="tab-content active">{team_section(None, period)}</div>'

    for team in TEAMS:
        lbl = TEAM_LABELS.get(team, team)
        tab_id = f'{team.replace("_","-")}-{sfx}'
        tab_btns    += f'<button class="tab-btn" onclick="showTeamTab(this,\'{tab_id}\')">{esc(lbl)}</button>'
        tab_contents += f'<div id="team-{tab_id}" class="tab-content">{team_section(team, period)}</div>'

    return f"""
<div class="tabs" id="team-tabs-{sfx}">{tab_btns}</div>
<div id="team-panels-{sfx}">{tab_contents}</div>"""

# ── Evolução mensal (últimos 3 meses) ─────────────────────────────────────────
def monthly_evolution_table() -> str:
    if len(MONTHS) < 2:
        return ""
    by_team_all = D["monthly"]["by_team"]
    # pivot: {team: {month: {csat, target, gap, total}}}
    pivot = defaultdict(dict)
    for r in by_team_all:
        pivot[r["team"]][r["month"]] = r

    mlbls = [MLABELS.get(m, m) for m in MONTHS]
    thead = '<tr><th style="text-align:left">Equipe</th>' + "".join(
        f'<th>{esc(lbl)}</th><th>Meta</th><th>Gap</th>' for lbl in mlbls
    ) + '</tr>'
    tbody = ""

    for team in TEAMS:
        lbl = TEAM_FULL.get(team, team)
        row_html = f'<td><strong>{esc(lbl)}</strong></td>'
        for m in MONTHS:
            r = pivot.get(team, {}).get(m, {})
            c = r.get("csat"); tg = r.get("target"); g = r.get("gap")
            cls_c = csat_color_class(c, tg); cls_g = gap_class(g)
            row_html += (f'<td class="num {cls_c}">{fmt_pct(c)}</td>'
                         f'<td class="num">{fmt_pct(tg)}</td>'
                         f'<td class="num {cls_g}">{gap_str(g)}</td>')
        tbody += f"<tr>{row_html}</tr>"

    return f"""
<div class="section-title">Evolução Mensal — por Equipe (últimos {len(MONTHS)} meses)</div>
<div class="card">
<div class="scroll-x">
<table class="dt">
<thead>{thead}</thead>
<tbody>{tbody}</tbody>
</table>
</div>
</div>"""

# ── HTML completo ──────────────────────────────────────────────────────────────
print("Gerando HTML…")

month_tab_html = f"""
<div class="period-section" id="period-month">
  {monthly_evolution_table()}
  {tabs_html("month")}
</div>"""

week_tab_html = f"""
<div class="period-section" id="period-week" style="display:none">
  {tabs_html("week")}
</div>"""

HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CSAT — BR Longtail + ExpImpo — {UPDATED}</title>
<style>
:root{{--yellow:#FFE600;--dark:#1a1a2e;--gray:#f5f5f5;--border:#e0e0e0;
  --green:#00a650;--red:#e84142;--warn:#ff7733;--blue:#3483fa;
  --text:#333;--light-green:#e6f7ee;--light-red:#fdecea;--light-warn:#fff3ec;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Proxima Nova',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:#f0f2f5;color:var(--text);font-size:14px;}}
.header{{background:var(--dark);color:#fff;padding:20px 32px;
  display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:12px;}}
.header h1{{font-size:20px;font-weight:800;letter-spacing:-.3px;}}
.header .sub{{font-size:12px;color:#aaa;margin-top:4px;}}
.header-right{{display:flex;flex-direction:column;align-items:flex-end;gap:8px;}}
.update-badge{{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);
  border-radius:20px;padding:4px 12px;font-size:11px;font-weight:600;display:flex;align-items:center;gap:6px;}}
.update-badge .dot{{width:7px;height:7px;border-radius:50%;background:#2ecc71;box-shadow:0 0 5px #2ecc71;}}
.period-toggle{{display:flex;gap:6px;padding:16px 32px 0;background:var(--dark);}}
.ptog-btn{{padding:8px 24px;border:2px solid rgba(255,255,255,0.3);background:transparent;
  color:rgba(255,255,255,0.7);font-size:13px;font-weight:700;cursor:pointer;
  border-radius:6px 6px 0 0;transition:all .15s;}}
.ptog-btn.active{{background:var(--yellow);color:#000;border-color:var(--yellow);}}
.ptog-btn:hover:not(.active){{background:rgba(255,255,255,0.1);color:#fff;}}
.container{{max-width:1280px;margin:0 auto;padding:24px 20px 60px;}}
.tabs{{display:flex;gap:4px;border-bottom:3px solid var(--border);margin-bottom:24px;flex-wrap:wrap;}}
.tab-btn{{padding:11px 22px;border:none;background:#fff;font-size:13px;font-weight:700;
  color:#999;cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-3px;
  border-radius:8px 8px 0 0;border:1px solid var(--border);border-bottom:3px solid transparent;
  transition:all .15s;}}
.tab-btn.active{{color:var(--dark);border-bottom-color:var(--yellow);background:#fff;}}
.tab-btn:hover:not(.active){{color:var(--dark);background:#f5f5f5;}}
.tab-content{{display:none;}}.tab-content.active{{display:block;}}
.section-title{{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;
  color:#888;margin:24px 0 12px;border-left:3px solid var(--yellow);padding-left:10px;}}
.kpi-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px;}}
.kpi-card{{background:#fff;border-radius:10px;padding:16px 18px;border:1px solid var(--border);}}
.kpi-card .label{{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;color:#999;margin-bottom:5px;}}
.kpi-card .value{{font-size:26px;font-weight:800;line-height:1;}}
.kpi-card .sub{{font-size:11px;color:#888;margin-top:5px;}}
.halo-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:4px;}}
.halo-kpi{{background:#fff;border-radius:8px;border:1px solid var(--border);padding:14px 16px;}}
.halo-lbl{{display:block;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#888;margin-bottom:6px;}}
.halo-val{{display:block;font-size:22px;font-weight:800;margin-bottom:2px;}}
.halo-goal{{display:block;font-size:11px;color:#888;}}
.card{{background:#fff;border-radius:10px;border:1px solid var(--border);overflow:hidden;margin-bottom:14px;padding:0;}}
.scroll-x{{overflow-x:auto;}}
table.dt{{border-collapse:collapse;width:100%;font-size:13px;}}
table.dt th{{background:#fafafa;padding:8px 12px;font-size:11px;font-weight:700;
  text-transform:uppercase;letter-spacing:.4px;color:#888;border-bottom:1px solid var(--border);
  text-align:center;white-space:nowrap;}}
table.dt th:first-child{{text-align:left;}}
table.dt td{{padding:8px 12px;border-bottom:1px solid #f5f5f5;text-align:center;white-space:nowrap;}}
table.dt td:first-child{{text-align:left;font-weight:600;}}
table.dt tr:last-child td{{border-bottom:none;}}
table.dt tr:hover td{{background:#f7faff;}}
.num{{text-align:center !important;font-weight:700;}}
.num-s{{text-align:center !important;color:#666;}}
.ok{{color:var(--green);}}.warn{{color:var(--warn);font-weight:700;}}.crit{{color:var(--red);font-weight:700;}}.neu{{color:#888;}}
.info-note{{font-size:12px;color:#888;padding:10px 16px;background:#fafafa;
  border-radius:6px;border-left:3px solid var(--yellow);margin:8px 0;}}
/* Tooltip diagnóstico */
.tip{{position:relative;cursor:help;}}
.tip::after{{content:attr(data-tip);position:absolute;bottom:125%;left:0;min-width:280px;max-width:380px;
  background:#1a1a2e;color:#fff;padding:9px 13px;border-radius:8px;font-size:12px;font-weight:400;
  white-space:normal;line-height:1.5;opacity:0;pointer-events:none;transition:opacity .15s;
  z-index:999;box-shadow:0 4px 12px rgba(0,0,0,.25);}}
.tip:hover::after{{opacity:1;}}
@media(max-width:900px){{
  .kpi-grid{{grid-template-columns:repeat(2,1fr);}}
  .halo-grid{{grid-template-columns:repeat(2,1fr);}}
}}
</style>
</head>
<body>
<div class="header">
  <div class="header-left">
    <h1>CSAT — BR Longtail + ExpImpo</h1>
    <p class="sub">Fonte: DM_CX_CSAT_Y20_DETAIL &nbsp;|&nbsp; Filtro: ELIGIBLE_CS=TRUE · IS_ANSWERED=TRUE · KM_SEGMENT NOT NULL</p>
    <p class="sub">Equipes: BR ME · Publicaciones · Ventas (Longtail) · MLB ExpImpo</p>
  </div>
  <div class="header-right">
    <div class="update-badge"><span class="dot"></span>Dados até {UPDATED}</div>
  </div>
</div>

<!-- Toggle MÊS / SEMANA -->
<div class="period-toggle">
  <button class="ptog-btn active" onclick="showPeriod('month',this)">{MONTH_LBL}</button>
  <button class="ptog-btn" onclick="showPeriod('week',this)">Semana {WEEK_LBL}</button>
</div>

<div class="container">
  {month_tab_html}
  {week_tab_html}
</div>

<script>
function showPeriod(period, btn) {{
  document.querySelectorAll('.period-section').forEach(s => s.style.display='none');
  document.querySelectorAll('.ptog-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('period-' + period).style.display = 'block';
  btn.classList.add('active');
}}

function showTeamTab(btn, tabId) {{
  // Encontra o container pai das tabs e panels
  var tabsEl = btn.closest('.tabs');
  var panelsId = 'team-panels-' + tabId.split('-').pop();
  var period = tabId.split('-').pop();

  // Remove active de todas as tabs do mesmo grupo
  tabsEl.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  // Esconde todos os panels do período
  var panelsEl = document.getElementById(panelsId);
  if (panelsEl) {{
    panelsEl.querySelectorAll('.tab-content').forEach(p => p.classList.remove('active'));
    var target = document.getElementById('team-' + tabId);
    if (target) target.classList.add('active');
  }}
}}
</script>
</body>
</html>"""

OUT = "csat_dashboard.html"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

sz_kb = os.path.getsize(OUT) / 1024
print(f"\n✅ Salvo: {OUT} ({sz_kb:.0f} KB)")
