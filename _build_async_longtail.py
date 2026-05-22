#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Chat Assíncrono — Longtail Sellers BR
Equipes: BR_ME_Sellers_Longtail, BR_Publicaciones_Sellers_Longtail, BR_Ventas_Sellers_Longtail
Gera: _async_longtail.html
"""
import sys, json
from datetime import date, timedelta
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery

BQ = bigquery.Client(project="meli-bi-data")

TEAMS = [
    "BR_ME_Sellers_Longtail",
    "BR_Publicaciones_Sellers_Longtail",
    "BR_Ventas_Sellers_Longtail",
]
TEAM_SHORT = {
    "BR_ME_Sellers_Longtail":            "ME",
    "BR_Publicaciones_Sellers_Longtail": "Publicaciones",
    "BR_Ventas_Sellers_Longtail":        "Ventas",
}
TEAMS_IN = ", ".join(f'"{t}"' for t in TEAMS)
COLORS   = ['#3498db','#e74c3c','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e67e22','#34495e','#e91e63','#00bcd4']

today       = date.today()
dow         = today.weekday()
monday      = today - timedelta(days=dow)
sem_ant_ini = monday - timedelta(days=7)
sem_ant_fin = monday - timedelta(days=1)
sem_act_ini = monday
mes_ini     = today.replace(day=1)
trend_ini   = monday - timedelta(days=56)
ontem       = today - timedelta(days=1)

print(f"Datas: sem_ant={sem_ant_ini}–{sem_ant_fin} | sem_act={sem_act_ini}–{ontem} | mes={mes_ini} | trend={trend_ini}")

def run(sql, retries=6, wait=15):
    import time
    from google.api_core.exceptions import Forbidden
    for attempt in range(retries):
        try:
            return [dict(row) for row in BQ.query(sql).result()]
        except Forbidden as e:
            if 'quotaExceeded' in str(e) and attempt < retries - 1:
                print(f"    quota exceeded, aguardando {wait}s (tentativa {attempt+1}/{retries})...")
                time.sleep(wait)
            else:
                raise

print("Rodando queries...")

# Q1 — diário 15 dias
q1 = run(f"""
SELECT DATE_ID AS dia, USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 15 DAY) AND DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1 DESC, async_por_caso DESC
"""); print(f"  Q1 diário: {len(q1)}")

# Q2 — semana anterior
q2 = run(f"""
SELECT USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2 ORDER BY 1, async_por_caso DESC
"""); print(f"  Q2 sem ant: {len(q2)}")

# Q3 — semana atual
q3 = run(f"""
SELECT USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID BETWEEN "{sem_act_ini}" AND "{ontem}"
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2 ORDER BY 1, async_por_caso DESC
"""); print(f"  Q3 sem act: {len(q3)}")

# Q4 — mês acumulado
q4 = run(f"""
SELECT USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID >= "{mes_ini}" AND DATE_ID < CURRENT_DATE()
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2 ORDER BY 1, async_por_caso DESC
"""); print(f"  Q4 mês: {len(q4)}")

# Q5 — líderes semana anterior
q5 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, staff.USER_TEAM_LEADER_LDAP AS lider, ixc.USER_OFFICE AS escritorio,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
LEFT JOIN (
  SELECT USER_LDAP, USER_TEAM_LEADER_LDAP FROM `meli-bi-data.WHOWNER.BT_CX_STAFF_HISTORY`
  WHERE DATE_ID = "{sem_ant_fin}" AND USER_TEAM_NAME IN ({TEAMS_IN})
) staff ON ixc.CI_OWNER_ID = staff.USER_LDAP
WHERE ixc.VALID_IXC_FLAG = TRUE
  AND ixc.DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CS_MANAGER IS NOT NULL
  AND staff.USER_TEAM_LEADER_LDAP IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1, async_por_caso DESC
"""); print(f"  Q5 líderes: {len(q5)}")

# Q6 — top reps
q6 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, ixc.CI_OWNER_ID AS rep, ixc.USER_OFFICE AS escritorio,
  staff.USER_TEAM_LEADER_LDAP AS lider,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
LEFT JOIN (
  SELECT USER_LDAP, USER_TEAM_LEADER_LDAP FROM `meli-bi-data.WHOWNER.BT_CX_STAFF_HISTORY`
  WHERE DATE_ID = "{sem_ant_fin}" AND USER_TEAM_NAME IN ({TEAMS_IN})
) staff ON ixc.CI_OWNER_ID = staff.USER_LDAP
WHERE ixc.VALID_IXC_FLAG = TRUE
  AND ixc.DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN}) AND ixc.CI_OWNER_ID IS NOT NULL AND ixc.CS_MANAGER IS NOT NULL
GROUP BY 1,2,3,4 HAVING SUM(ixc.DENOM_IXC) >= 10
ORDER BY 1, async_por_caso DESC LIMIT 60
"""); print(f"  Q6 reps: {len(q6)}")

# Q7 — tendência semanal 8 semanas
q7 = run(f"""
SELECT USER_TEAM_NAME AS equipe,
  DATE_TRUNC(DATE_ID, WEEK(MONDAY)) AS semana,
  USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID >= "{trend_ini}" AND DATE_ID < CURRENT_DATE()
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1, 2 ASC, async_por_caso DESC
"""); print(f"  Q7 semanal: {len(q7)}")

# Q8 — mensal últimos 6 meses
mes_6m = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
mes_6m = (mes_6m.replace(day=1) - timedelta(days=1)).replace(day=1)
mes_6m = (mes_6m.replace(day=1) - timedelta(days=1)).replace(day=1)
mes_6m = (mes_6m.replace(day=1) - timedelta(days=1)).replace(day=1)
mes_6m = (mes_6m.replace(day=1) - timedelta(days=1)).replace(day=1)
q8 = run(f"""
SELECT USER_TEAM_NAME AS equipe,
  FORMAT_DATE('%Y-%m', DATE_ID) AS mes,
  USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID >= "{mes_6m}" AND DATE_ID < CURRENT_DATE()
  AND USER_TEAM_NAME IN ({TEAMS_IN}) AND USER_OFFICE IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1, 2 ASC, async_por_caso DESC
"""); print(f"  Q8 mensal: {len(q8)}")

# ── aggregations para aba Geral ───────────────────────────────────────────────

def agg_to_team(rows, date_key):
    """Soma async_total e incoming_cr por (equipe, date_key), recalcula async_por_caso."""
    buf = {}
    for r in rows:
        k = (r['equipe'], str(r[date_key])[:10] if hasattr(r[date_key], 'isoformat') else str(r[date_key]))
        if k not in buf:
            buf[k] = {'equipe': r['equipe'], date_key: k[1], 'async_total': 0, 'incoming_cr': 0}
        buf[k]['async_total'] += int(r.get('async_total') or 0)
        buf[k]['incoming_cr'] += int(r.get('incoming_cr') or 0)
    out = []
    for v in buf.values():
        cr = v['incoming_cr']
        v['async_por_caso'] = round(v['async_total'] / cr, 2) if cr > 0 else None
        out.append(v)
    return out

q1_geral = agg_to_team(q1, 'dia')
q7_geral = agg_to_team(q7, 'semana')
q8_geral = agg_to_team(q8, 'mes')

# ── helpers ───────────────────────────────────────────────────────────────────

def jd(obj):
    if hasattr(obj, 'isoformat'): return obj.isoformat()
    if hasattr(obj, '__float__'): return float(obj)
    raise TypeError

def icon(v):
    if v is None: return "—"
    if v < 1.0:   return f'<span class="ok">{v:.2f}</span>'
    if v <= 2.0:  return f'<span class="warn">{v:.2f}</span>'
    return             f'<span class="crit">{v:.2f}</span>'

def delta_arrow(prev, curr):
    if prev is None or curr is None: return "—"
    d = curr - prev
    if abs(d) < 0.05: arrow, cls = "→", "neutral"
    elif d > 0:       arrow, cls = "↑", "bad"
    else:             arrow, cls = "↓", "good"
    return f'<span class="{cls}">{arrow} {abs(d):.2f}</span>'

def fmt_date(d):
    if d is None: return "—"
    if hasattr(d, 'strftime'): return d.strftime('%d/%m')
    s = str(d)[:10]
    return s[5:].replace('-', '/')

def pivot_offices(rows, team):
    return sorted([r for r in rows if r['equipe'] == team], key=lambda x: -(x.get('async_por_caso') or 0))

def get_offices(team):
    seen, result = set(), []
    for rlist in [q1, q2, q3, q4]:
        for r in rlist:
            o = r.get('escritorio')
            if r['equipe'] == team and o and o not in seen:
                seen.add(o); result.append(o)
    return sorted(result)

# ── office filter ──────────────────────────────────────────────────────────────

def section_office_filter(team):
    offices = get_offices(team)
    short = TEAM_SHORT[team]
    btns = f'<button class="off-btn active" onclick="filterOffice(\'{short}\',\'ALL\',this)">Todos</button>'
    for off in offices:
        btns += f'<button class="off-btn" onclick="filterOffice(\'{short}\',\'{off}\',this)">{off}</button>'
    return f'<div class="off-filter" id="filter-{short}">{btns}</div>'

# ── tabelas ────────────────────────────────────────────────────────────────────

def section_wow(team):
    ant = {r['escritorio']: r for r in q2 if r['equipe'] == team}
    act = {r['escritorio']: r for r in q3 if r['equipe'] == team}
    offices = sorted(set(list(ant.keys()) + list(act.keys())))
    if not offices: return "<p class='empty'>Sem dados</p>"
    rows_html = ""
    for off in offices:
        a, c = ant.get(off, {}), act.get(off, {})
        vant, vact = a.get('async_por_caso'), c.get('async_por_caso')
        rows_html += f'<tr data-office="{off}"><td>{off}</td><td class="num">{icon(vant)}</td><td class="num-s">{int(a.get("incoming_cr",0) or 0)}</td><td class="num">{icon(vact)}</td><td class="num-s">{int(c.get("incoming_cr",0) or 0)}</td><td class="num">{delta_arrow(vant,vact)}</td></tr>'
    return f'<table class="dt"><thead><tr><th>Escritório</th><th>Sem Ant<br><small>{fmt_date(sem_ant_ini)}–{fmt_date(sem_ant_fin)}</small></th><th>CR</th><th>Sem Atual<br><small>{fmt_date(sem_act_ini)}–{fmt_date(ontem)}</small></th><th>CR</th><th>Delta</th></tr></thead><tbody>{rows_html}</tbody></table>'

def section_mes(team):
    rows = pivot_offices(q4, team)
    if not rows: return "<p class='empty'>Sem dados</p>"
    rows_html = "".join(f'<tr data-office="{r["escritorio"]}"><td>{r["escritorio"]}</td><td class="num">{icon(r.get("async_por_caso"))}</td><td class="num-s">{int(r.get("incoming_cr") or 0)}</td><td class="num-s">{int(r.get("async_total") or 0)}</td></tr>' for r in rows)
    return f'<table class="dt"><thead><tr><th>Escritório</th><th>Async/Caso<br><small>{fmt_date(mes_ini)}–{fmt_date(ontem)}</small></th><th>CR</th><th>Async Total</th></tr></thead><tbody>{rows_html}</tbody></table>'

def section_lideres(team):
    rows = sorted([r for r in q5 if r['equipe'] == team], key=lambda x: -(x.get('async_por_caso') or 0))
    if not rows: return "<p class='empty'>Sem dados</p>"
    rows_html = "".join(f'<tr data-office="{r["escritorio"]}"><td>{r["lider"] or "—"}</td><td>{r["escritorio"]}</td><td class="num">{icon(r.get("async_por_caso"))}</td><td class="num-s">{int(r.get("incoming_cr") or 0)}</td><td class="num-s">{int(r.get("async_total") or 0)}</td></tr>' for r in rows)
    return f'<table class="dt"><thead><tr><th>Líder</th><th>Escritório</th><th>Async/Caso</th><th>CR</th><th>Async</th></tr></thead><tbody>{rows_html}</tbody></table>'

def section_reps(team):
    rows = sorted([r for r in q6 if r['equipe'] == team], key=lambda x: -(x.get('async_por_caso') or 0))[:20]
    if not rows: return "<p class='empty'>Sem dados (mín. 10 CR)</p>"
    rows_html = "".join(f'<tr data-office="{r["escritorio"]}"><td>{r["rep"]}</td><td>{r["escritorio"]}</td><td>{r["lider"] or "—"}</td><td class="num">{icon(r.get("async_por_caso"))}</td><td class="num-s">{int(r.get("incoming_cr") or 0)}</td><td class="num-s">{int(r.get("async_total") or 0)}</td></tr>' for r in rows)
    return f'<table class="dt"><thead><tr><th>Rep</th><th>Escritório</th><th>Líder</th><th>Async/Caso</th><th>CR</th><th>Async</th></tr></thead><tbody>{rows_html}</tbody></table>'

# ── gráficos ──────────────────────────────────────────────────────────────────

def make_chart(cid, labels, datasets, y_label, bar=True, height=280, x_rotation=0):
    data_json = json.dumps({'labels': labels, 'datasets': datasets}, default=jd)
    chart_type = 'bar' if bar else 'line'
    rotation = f'maxRotation:{x_rotation},' if x_rotation else ''
    return f"""<div style="position:relative;height:{height}px"><canvas id="{cid}"></canvas></div>
<script>(function(){{
  var ctx=document.getElementById('{cid}').getContext('2d');
  window._charts=window._charts||{{}};
  window._charts['{cid}']=new Chart(ctx,{{
    type:'{chart_type}',
    data:{data_json},
    options:{{
      responsive:true,maintainAspectRatio:false,
      interaction:{{mode:'index',intersect:false}},
      plugins:{{
        legend:{{position:'top',labels:{{filter:function(i){{return !i.text.startsWith('__');}},boxWidth:12,font:{{size:11}}}}}},
        tooltip:{{filter:function(i){{return !i.dataset.label.startsWith('__');}}}}
      }},
      scales:{{
        y:{{title:{{display:true,text:'{y_label}',font:{{size:11}}}},min:0,ticks:{{font:{{size:11}}}}}},
        x:{{ticks:{{{rotation}font:{{size:10}}}}}}
      }}
    }}
  }});
}})();</script>"""

def _to_float(v, multiplier=1):
    return round(float(v) * multiplier, 2) if v is not None else None

def bar_datasets(series_map, color_map, multiplier=1, total=None):
    n = max(len(v) for v in series_map.values()) if series_map else 0
    ds = []
    for label, values in series_map.items():
        c = color_map[label]
        ds.append({'type':'bar','label':label,
                   'data':[_to_float(v,multiplier) for v in values],
                   'backgroundColor':c+'bb','borderColor':c,'borderWidth':1,'borderRadius':3,'skipNull':True})
    if total:
        ds.append({'type':'line','label':'Total',
                   'data':[_to_float(v,multiplier) for v in total],
                   'borderColor':'#1a1a2e','backgroundColor':'#1a1a2e22','borderWidth':2.5,
                   'pointRadius':3,'tension':0.3,'fill':False,'spanGaps':True,'order':0})
    ref1 = 1.0*multiplier; ref2 = 2.0*multiplier
    ds.append({'type':'line','label':'__ref1__','data':[ref1]*n,'borderColor':'#b8860b','borderDash':[6,4],'pointRadius':0,'borderWidth':1.5,'fill':False,'tension':0})
    ds.append({'type':'line','label':'__ref2__','data':[ref2]*n,'borderColor':'#c0392b','borderDash':[6,4],'pointRadius':0,'borderWidth':1.5,'fill':False,'tension':0})
    return ds

def line_datasets(series_map, color_map, multiplier=1, total=None):
    ds = []
    for label, values in series_map.items():
        c = color_map[label]
        ds.append({'type':'line','label':label,
                   'data':[_to_float(v,multiplier) for v in values],
                   'borderColor':c,'backgroundColor':c+'33','borderWidth':2,
                   'tension':0.35,'spanGaps':True,'pointRadius':4,'fill':False})
    if total:
        ds.insert(0, {'type':'line','label':'Total',
                      'data':[_to_float(v,multiplier) for v in total],
                      'borderColor':'#1a1a2e','backgroundColor':'#1a1a2e22','borderWidth':3,
                      'pointRadius':4,'tension':0.3,'fill':False,'spanGaps':True})
    return ds

def _dk(r, date_key):
    v = r.get(date_key)
    return str(v)[:10] if v is not None else ''

def build_office_series(rows, team, date_key):
    """Retorna (keys, series_map, color_map, total) agrupados por office."""
    team_rows = [r for r in rows if r['equipe'] == team]
    if not team_rows: return [], {}, {}, []
    keys    = sorted(set(_dk(r, date_key) for r in team_rows))
    offices = sorted(set(r['escritorio'] for r in team_rows))
    idx     = {(_dk(r, date_key), r['escritorio']): r for r in team_rows}
    series_map = {off: [idx.get((k, off), {}).get('async_por_caso') for k in keys] for off in offices}
    color_map  = {off: COLORS[i % len(COLORS)] for i, off in enumerate(offices)}
    # total por chave = sum(async_total) / sum(incoming_cr)
    total = []
    for k in keys:
        rows_k = [r for r in team_rows if _dk(r, date_key) == k]
        at = sum(int(r.get('async_total') or 0) for r in rows_k)
        cr = sum(int(r.get('incoming_cr') or 0) for r in rows_k)
        total.append(round(at/cr, 2) if cr else None)
    return keys, series_map, color_map, total

def build_team_series(rows, date_key):
    """Retorna (keys, series_map, color_map, total) agrupados por equipe (aba Geral)."""
    if not rows: return [], {}, {}, []
    keys   = sorted(set(str(r[date_key])[:10] for r in rows))
    idx    = {}
    for r in rows:
        k = str(r[date_key])[:10]
        idx.setdefault((k, r['equipe']), {'at': 0, 'cr': 0})
        idx[(k, r['equipe'])]['at'] += int(r.get('async_total') or 0)
        idx[(k, r['equipe'])]['cr'] += int(r.get('incoming_cr') or 0)
    def val(k, t):
        d = idx.get((k, t)); return round(d['at']/d['cr'], 2) if d and d['cr'] else None
    series = {TEAM_SHORT[t]: [val(k, t) for k in keys] for t in TEAMS}
    colors = {TEAM_SHORT[t]: COLORS[i] for i, t in enumerate(TEAMS)}
    # total geral
    total_buf = {}
    for r in rows:
        k = str(r[date_key])[:10]
        total_buf.setdefault(k, {'at': 0, 'cr': 0})
        total_buf[k]['at'] += int(r.get('async_total') or 0)
        total_buf[k]['cr'] += int(r.get('incoming_cr') or 0)
    total = [round(total_buf[k]['at']/total_buf[k]['cr'], 2) if total_buf.get(k,{}).get('cr') else None for k in keys]
    return keys, series, colors, total

# — gráficos por equipe —

def chart_daily(team):
    keys, series, cmap, total = build_office_series(q1, team, 'dia')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[5:].replace('-','/') for k in keys]
    return make_chart(f'cd-{TEAM_SHORT[team]}', labels, bar_datasets(series, cmap, total=total), 'async/caso', bar=True, x_rotation=45)

def chart_weekly(team):
    keys, series, cmap, total = build_office_series(q7, team, 'semana')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[5:].replace('-','/') for k in keys]
    return make_chart(f'cw-{TEAM_SHORT[team]}', labels, bar_datasets(series, cmap, total=total), 'async/caso', bar=True)

def chart_monthly(team):
    keys, series, cmap, total = build_office_series(q8, team, 'mes')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[2:].replace('-','/') for k in keys]
    return make_chart(f'cm-{TEAM_SHORT[team]}', labels, bar_datasets(series, cmap, total=total), 'async/caso', bar=True)

def chart_pct_weekly(team):
    keys, series, cmap, total = build_office_series(q7, team, 'semana')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[5:].replace('-','/') for k in keys]
    return make_chart(f'cpw-{TEAM_SHORT[team]}', labels, line_datasets(series, cmap, multiplier=100, total=total), '% async/CR', bar=False)

def chart_pct_monthly(team):
    keys, series, cmap, total = build_office_series(q8, team, 'mes')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[2:].replace('-','/') for k in keys]
    return make_chart(f'cpm-{TEAM_SHORT[team]}', labels, line_datasets(series, cmap, multiplier=100, total=total), '% async/CR', bar=False)

# — gráficos Geral (série = equipe) —

def chart_geral_daily():
    keys, series, cmap, total = build_team_series(q1_geral, 'dia')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[5:].replace('-','/') for k in keys]
    return make_chart('cg-daily', labels, bar_datasets(series, cmap, total=total), 'async/caso', bar=True, x_rotation=45)

def chart_geral_weekly():
    keys, series, cmap, total = build_team_series(q7_geral, 'semana')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[5:].replace('-','/') for k in keys]
    return make_chart('cg-weekly', labels, bar_datasets(series, cmap, total=total), 'async/caso', bar=True)

def chart_geral_monthly():
    keys, series, cmap, total = build_team_series(q8_geral, 'mes')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[2:].replace('-','/') for k in keys]
    return make_chart('cg-monthly', labels, bar_datasets(series, cmap, total=total), 'async/caso', bar=True)

def chart_geral_pct_weekly():
    keys, series, cmap, total = build_team_series(q7_geral, 'semana')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[5:].replace('-','/') for k in keys]
    return make_chart('cg-cpw', labels, line_datasets(series, cmap, multiplier=100, total=total), '% async/CR', bar=False)

def chart_geral_pct_monthly():
    keys, series, cmap, total = build_team_series(q8_geral, 'mes')
    if not keys: return "<p class='empty'>Sem dados</p>"
    labels = [k[2:].replace('-','/') for k in keys]
    return make_chart('cg-cpm', labels, line_datasets(series, cmap, multiplier=100, total=total), '% async/CR', bar=False)

# ── resumo executivo ──────────────────────────────────────────────────────────

def exec_summary(team):
    ant = {r['escritorio']: r for r in q2 if r['equipe'] == team}
    act = {r['escritorio']: r for r in q3 if r['equipe'] == team}
    worst = (pivot_offices(q2, team) or [None])[0]
    b1 = (f"Office com maior async/caso (sem ant): <strong>{worst['escritorio']}</strong> — {icon(worst.get('async_por_caso'))}" if worst else "Sem dados")
    if worst:
        off = worst['escritorio']
        vant, vact = ant.get(off,{}).get('async_por_caso'), act.get(off,{}).get('async_por_caso')
        d = (vact - vant) if (vact is not None and vant is not None) else None
        b2 = (f"Delta WoW {off}: {icon(vant)} → {icon(vact)} ({'+' if d>=0 else ''}{d:.2f})" if d is not None else f"Delta WoW {off}: sem dados da semana atual")
    else:
        b2 = "Sem dados WoW"
    n_crit = len([r for r in q6 if r['equipe'] == team and (r.get('async_por_caso') or 0) > 2.0])
    b3 = f"Reps com async/caso &gt; 2.0 (sem ant): <strong>{n_crit}</strong> rep{'s' if n_crit!=1 else ''}"
    return f'<ul class="exec"><li>{b1}</li><li>{b2}</li><li>{b3}</li></ul>'

# ── conteúdo das abas ─────────────────────────────────────────────────────────

def tab_content(team):
    s = TEAM_SHORT[team]
    return f"""
    <div id="tab-{s}" class="tab-content">
      <h2>{team}</h2>
      {section_office_filter(team)}

      <div class="card"><h3>Resumo Executivo</h3>{exec_summary(team)}</div>

      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>WoW por Office</h3>{section_wow(team)}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Mês Acumulado <small>({mes_ini.strftime('%b/%Y')})</small></h3>{section_mes(team)}</div>
      </div>

      <div class="section-title">Async/Caso</div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Diário <small>últimos 15 dias</small></h3>{chart_daily(team)}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Semanal <small>últimas 8 semanas</small></h3>{chart_weekly(team)}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Mensal <small>últimos 6 meses</small></h3>{chart_monthly(team)}</div>
      </div>

      <div class="section-title">% de Uso Assíncrono <small style="font-weight:400;font-size:11px">(async total / CR × 100)</small></div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Tendência Semanal</h3>{chart_pct_weekly(team)}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Tendência Mensal</h3>{chart_pct_monthly(team)}</div>
      </div>

      <div class="card"><h3>Por Team Leader <small>(sem {fmt_date(sem_ant_ini)}–{fmt_date(sem_ant_fin)})</small></h3>{section_lideres(team)}</div>
      <div class="card"><h3>Top 20 Reps — maior async/caso <small>(mín. 10 CR)</small></h3>{section_reps(team)}</div>
    </div>"""

def tab_geral():
    # resumo geral: WoW por equipe
    rows_wow = ""
    for team in TEAMS:
        ant = next((r for r in q2 if r['equipe'] == team), None)
        act = next((r for r in q3 if r['equipe'] == team), None)
        # aggregate across offices
        def agg_q(q, t):
            rows = [r for r in q if r['equipe'] == t]
            if not rows: return None, 0
            tot = sum(int(r.get('async_total') or 0) for r in rows)
            cr  = sum(int(r.get('incoming_cr') or 0) for r in rows)
            return (round(tot/cr, 2) if cr else None), cr
        vant, cr_ant = agg_q(q2, team)
        vact, cr_act = agg_q(q3, team)
        rows_wow += f'<tr><td><strong>{TEAM_SHORT[team]}</strong></td><td class="num">{icon(vant)}</td><td class="num-s">{cr_ant:,}</td><td class="num">{icon(vact)}</td><td class="num-s">{cr_act:,}</td><td class="num">{delta_arrow(vant,vact)}</td></tr>'
    wow_table = f'<table class="dt"><thead><tr><th>Equipe</th><th>Sem Ant<br><small>{fmt_date(sem_ant_ini)}–{fmt_date(sem_ant_fin)}</small></th><th>CR</th><th>Sem Atual<br><small>{fmt_date(sem_act_ini)}–{fmt_date(ontem)}</small></th><th>CR</th><th>Delta</th></tr></thead><tbody>{rows_wow}</tbody></table>'

    return f"""
    <div id="tab-Geral" class="tab-content">
      <h2>Geral — Longtail Sellers BR</h2>

      <div class="card"><h3>WoW por Equipe</h3>{wow_table}</div>

      <div class="section-title">Async/Caso por Equipe</div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Diário</h3>{chart_geral_daily()}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Semanal</h3>{chart_geral_weekly()}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Mensal</h3>{chart_geral_monthly()}</div>
      </div>

      <div class="section-title">% de Uso Assíncrono por Equipe</div>
      <div style="display:flex;gap:16px">
        <div class="card" style="flex:1;min-width:0"><h3>Tendência Semanal</h3>{chart_geral_pct_weekly()}</div>
        <div class="card" style="flex:1;min-width:0"><h3>Tendência Mensal</h3>{chart_geral_pct_monthly()}</div>
      </div>
    </div>"""

# ── montagem HTML ─────────────────────────────────────────────────────────────

tabs_nav  = '<button class="tab-btn active" onclick="showTab(\'Geral\')">Geral</button>'
tabs_body = tab_geral()
for team in TEAMS:
    s = TEAM_SHORT[team]
    tabs_nav  += f'<button class="tab-btn" onclick="showTab(\'{s}\')">{s}</button>'
    tabs_body += tab_content(team)

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chat Assíncrono — Longtail Sellers BR</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --green:#1a8a3c; --yellow:#b8860b; --red:#c0392b;
    --bg:#f4f6f8; --card:#fff; --border:#dde3ea; --head:#2c3e50; --accent:#3498db;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',sans-serif;background:var(--bg);color:#222;font-size:13px}}
  header{{background:var(--head);color:#fff;padding:16px 24px}}
  header h1{{font-size:18px}}
  header .sub{{font-size:11px;opacity:.7;margin-top:4px}}
  .legend{{display:flex;gap:16px;padding:8px 24px;background:#fff;border-bottom:1px solid var(--border);font-size:11px}}
  .legend span{{display:flex;align-items:center;gap:4px}}
  .tabs{{display:flex;gap:4px;padding:12px 24px 0;background:#fff;border-bottom:2px solid var(--accent);flex-wrap:wrap}}
  .tab-btn{{padding:8px 20px;border:none;background:#eef2f7;border-radius:6px 6px 0 0;cursor:pointer;font-size:13px;font-weight:600;color:#555;transition:all .15s}}
  .tab-btn.active{{background:var(--accent);color:#fff}}
  .tab-btn:hover:not(.active){{background:#d5e8f7}}
  .tab-content{{display:none;padding:20px 24px}}
  .tab-content.show{{display:block}}
  .tab-content h2{{font-size:15px;color:var(--head);margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border)}}
  .section-title{{font-size:12px;font-weight:700;color:var(--head);text-transform:uppercase;letter-spacing:.5px;margin:8px 0 8px;padding-left:2px}}
  .card{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px;margin-bottom:16px}}
  .card h3{{font-size:13px;font-weight:700;color:var(--head);margin-bottom:12px}}
  .card h3 small{{font-weight:400;color:#777;font-size:11px}}
  .off-filter{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}}
  .off-btn{{padding:5px 14px;border:1.5px solid var(--border);background:#fff;border-radius:20px;cursor:pointer;font-size:11px;font-weight:600;color:#555;transition:all .15s}}
  .off-btn.active{{background:var(--head);color:#fff;border-color:var(--head)}}
  .off-btn:hover:not(.active){{background:#eef2f7;border-color:#aaa}}
  table.dt{{border-collapse:collapse;width:100%;font-size:12px}}
  table.dt th{{background:#f0f4f8;padding:6px 10px;text-align:center;font-size:11px;border-bottom:2px solid var(--border);white-space:nowrap}}
  table.dt th:first-child{{text-align:left}}
  table.dt td{{padding:5px 10px;border-bottom:1px solid #eef0f3;white-space:nowrap;text-align:center}}
  table.dt td:first-child{{text-align:left}}
  table.dt tr:hover td{{background:#f7fafd}}
  td.num{{text-align:center;font-weight:600}}
  td.num-s{{text-align:center;color:#666}}
  .ok{{color:var(--green)}} .warn{{color:var(--yellow)}} .crit{{color:var(--red);font-weight:700}}
  .good{{color:var(--green)}} .bad{{color:var(--red)}} .neutral{{color:#888}}
  ul.exec{{padding-left:18px}}
  ul.exec li{{margin-bottom:6px;line-height:1.5}}
  .empty{{color:#999;font-style:italic;padding:8px 0}}
  @media(max-width:900px){{
    .tabs{{overflow-x:auto}}
    div[style*="display:flex"]{{flex-direction:column!important}}
  }}
</style>
</head>
<body>
<header>
  <h1>Chat Assíncrono — Longtail Sellers BR</h1>
  <div class="sub">Atualizado: {today.strftime('%d/%m/%Y')} &nbsp;|&nbsp; Fonte: DM_CX_IXC_DETAIL &nbsp;|&nbsp; async/caso = disparos assíncronos ÷ DENOM_IXC</div>
</header>
<div class="legend">
  <span><span class="ok">●</span> &lt;1.0 Normal</span>
  <span><span class="warn">●</span> 1.0–2.0 Atenção</span>
  <span><span class="crit">●</span> &gt;2.0 Crítico</span>
  <span style="margin-left:auto;color:#888">↑ piora &nbsp;↓ melhora &nbsp;→ estável</span>
</div>
<div class="tabs">{tabs_nav}</div>
{tabs_body}
<script>
function showTab(id){{
  document.querySelectorAll('.tab-content').forEach(el=>el.classList.remove('show'));
  document.querySelectorAll('.tab-btn').forEach(el=>el.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('show');
  event.target.classList.add('active');
}}
document.querySelector('.tab-content').classList.add('show');

function filterOffice(team,office,btn){{
  document.querySelectorAll('#filter-'+team+' .off-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('#tab-'+team+' tr[data-office]').forEach(row=>{{
    row.style.display=(office==='ALL'||row.dataset.office===office)?'':'none';
  }});
  ['cd-','cw-','cm-','cpw-','cpm-'].forEach(prefix=>{{
    var chart=(window._charts||{{}})[prefix+team];
    if(!chart)return;
    chart.data.datasets.forEach((ds,i)=>{{
      var isRef=ds.label.startsWith('__');
      chart.setDatasetVisibility(i,isRef||office==='ALL'||ds.label===office);
    }});
    chart.update();
  }});
}}
</script>
</body>
</html>"""

out_raw = r"c:\Users\allabriola\PROJETO CLAUDINHO\_async_longtail.html"
out_pub = r"c:\Users\allabriola\PROJETO CLAUDINHO\async_longtail.html"
for path in [out_raw, out_pub]:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
print(f"HTML salvo: {out_pub}")
