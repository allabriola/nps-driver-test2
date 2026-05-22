#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Chat Assíncrono — Longtail Sellers BR
Equipes: BR_ME_Sellers_Longtail, BR_Publicaciones_Sellers_Longtail, BR_Ventas_Sellers Longtail
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
    "BR_Ventas_Sellers Longtail",
]
TEAM_SHORT = {
    "BR_ME_Sellers_Longtail": "ME",
    "BR_Publicaciones_Sellers_Longtail": "Publicaciones",
    "BR_Ventas_Sellers Longtail": "Ventas",
}
TEAMS_IN = ", ".join(f'"{t}"' for t in TEAMS)

COLORS = ['#3498db','#e74c3c','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e67e22','#34495e','#e91e63','#00bcd4']

today = date.today()
dow = today.weekday()
monday = today - timedelta(days=dow)
sem_ant_ini = monday - timedelta(days=7)
sem_ant_fin = monday - timedelta(days=1)
sem_act_ini = monday
mes_ini = today.replace(day=1)
trend_ini = monday - timedelta(days=56)
ontem = today - timedelta(days=1)

print(f"Datas: sem_ant={sem_ant_ini}–{sem_ant_fin} | sem_act={sem_act_ini}–{ontem} | mes={mes_ini} | trend={trend_ini}–{ontem}")

def run(sql):
    return [dict(row) for row in BQ.query(sql).result()]

print("Rodando queries...")

# Q1 — heatmap diário 15 dias
q1 = run(f"""
SELECT DATE_ID AS dia, USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 15 DAY) AND DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND USER_TEAM_NAME IN ({TEAMS_IN})
  AND USER_OFFICE IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1 DESC, async_por_caso DESC
""")
print(f"  Q1 heatmap: {len(q1)} linhas")

# Q2 — semana anterior
q2 = run(f"""
SELECT USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND USER_TEAM_NAME IN ({TEAMS_IN})
  AND USER_OFFICE IS NOT NULL
GROUP BY 1,2 ORDER BY 1, async_por_caso DESC
""")
print(f"  Q2 sem ant: {len(q2)} linhas")

# Q3 — semana atual
q3 = run(f"""
SELECT USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID BETWEEN "{sem_act_ini}" AND "{ontem}"
  AND USER_TEAM_NAME IN ({TEAMS_IN})
  AND USER_OFFICE IS NOT NULL
GROUP BY 1,2 ORDER BY 1, async_por_caso DESC
""")
print(f"  Q3 sem act: {len(q3)} linhas")

# Q4 — mês acumulado
q4 = run(f"""
SELECT USER_TEAM_NAME AS equipe, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID >= "{mes_ini}"
  AND DATE_ID < CURRENT_DATE()
  AND USER_TEAM_NAME IN ({TEAMS_IN})
  AND USER_OFFICE IS NOT NULL
GROUP BY 1,2 ORDER BY 1, async_por_caso DESC
""")
print(f"  Q4 mes: {len(q4)} linhas")

# Q5 — por team leader via JOIN com BT_CX_STAFF_HISTORY
q5 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, staff.USER_TEAM_LEADER_LDAP AS lider, ixc.USER_OFFICE AS escritorio,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
LEFT JOIN (
  SELECT USER_LDAP, USER_TEAM_LEADER_LDAP
  FROM `meli-bi-data.WHOWNER.BT_CX_STAFF_HISTORY`
  WHERE DATE_ID = "{sem_ant_fin}"
    AND USER_TEAM_NAME IN ({TEAMS_IN})
) staff ON ixc.CI_OWNER_ID = staff.USER_LDAP
WHERE ixc.VALID_IXC_FLAG = TRUE
  AND ixc.DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN})
  AND ixc.CS_MANAGER IS NOT NULL
  AND staff.USER_TEAM_LEADER_LDAP IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1, async_por_caso DESC
""")
print(f"  Q5 lideres: {len(q5)} linhas")

# Q6 — top reps com lider via JOIN com BT_CX_STAFF_HISTORY
q6 = run(f"""
SELECT ixc.USER_TEAM_NAME AS equipe, ixc.CI_OWNER_ID AS rep, ixc.USER_OFFICE AS escritorio,
  staff.USER_TEAM_LEADER_LDAP AS lider,
  COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(ixc.DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(ixc.SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(ixc.DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL` ixc
LEFT JOIN (
  SELECT USER_LDAP, USER_TEAM_LEADER_LDAP
  FROM `meli-bi-data.WHOWNER.BT_CX_STAFF_HISTORY`
  WHERE DATE_ID = "{sem_ant_fin}"
    AND USER_TEAM_NAME IN ({TEAMS_IN})
) staff ON ixc.CI_OWNER_ID = staff.USER_LDAP
WHERE ixc.VALID_IXC_FLAG = TRUE
  AND ixc.DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND ixc.USER_TEAM_NAME IN ({TEAMS_IN})
  AND ixc.CI_OWNER_ID IS NOT NULL
  AND ixc.CS_MANAGER IS NOT NULL
GROUP BY 1,2,3,4
HAVING SUM(ixc.DENOM_IXC) >= 10
ORDER BY 1, async_por_caso DESC
LIMIT 60
""")
print(f"  Q6 reps: {len(q6)} linhas")

# Q7 — tendência 8 semanas
q7 = run(f"""
SELECT USER_TEAM_NAME AS equipe,
  DATE_TRUNC(DATE_ID, WEEK(MONDAY)) AS semana,
  USER_OFFICE AS escritorio,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso,
  SUM(DENOM_IXC) AS incoming_cr
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID >= "{trend_ini}"
  AND DATE_ID < CURRENT_DATE()
  AND USER_TEAM_NAME IN ({TEAMS_IN})
  AND USER_OFFICE IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1, 2 ASC, async_por_caso DESC
""")
print(f"  Q7 trend: {len(q7)} linhas")

# ── helpers ──────────────────────────────────────────────────────────────────

def jd(obj):
    if hasattr(obj, 'isoformat'): return obj.isoformat()
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
    return str(d)[:10][5:].replace('-','/')

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

# ── office filter ─────────────────────────────────────────────────────────────

def section_office_filter(team):
    offices = get_offices(team)
    short = TEAM_SHORT[team]
    btns = f'<button class="off-btn active" onclick="filterOffice(\'{short}\',\'ALL\',this)">Todos</button>'
    for off in offices:
        btns += f'<button class="off-btn" onclick="filterOffice(\'{short}\',\'{off}\',this)">{off}</button>'
    return f'<div class="off-filter" id="filter-{short}">{btns}</div>'

# ── tables ────────────────────────────────────────────────────────────────────

def section_wow(team):
    ant = {r['escritorio']: r for r in q2 if r['equipe'] == team}
    act = {r['escritorio']: r for r in q3 if r['equipe'] == team}
    offices = sorted(set(list(ant.keys()) + list(act.keys())))
    if not offices: return "<p class='empty'>Sem dados</p>"
    rows_html = ""
    for off in offices:
        a, c = ant.get(off, {}), act.get(off, {})
        vant, vact = a.get('async_por_caso'), c.get('async_por_caso')
        rows_html += f"""
        <tr data-office="{off}">
          <td>{off}</td>
          <td class="num">{icon(vant)}</td><td class="num-s">{int(a.get('incoming_cr',0) or 0)}</td>
          <td class="num">{icon(vact)}</td><td class="num-s">{int(c.get('incoming_cr',0) or 0)}</td>
          <td class="num">{delta_arrow(vant, vact)}</td>
        </tr>"""
    return f"""
    <table class="dt">
      <thead><tr>
        <th>Escritório</th>
        <th>Sem Ant<br><small>{fmt_date(sem_ant_ini)}–{fmt_date(sem_ant_fin)}</small></th><th>CR</th>
        <th>Sem Atual<br><small>{fmt_date(sem_act_ini)}–{fmt_date(ontem)}</small></th><th>CR</th>
        <th>Delta</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>"""

def section_mes(team):
    rows = pivot_offices(q4, team)
    if not rows: return "<p class='empty'>Sem dados</p>"
    rows_html = ""
    for r in rows:
        rows_html += f"""
        <tr data-office="{r['escritorio']}">
          <td>{r['escritorio']}</td>
          <td class="num">{icon(r.get('async_por_caso'))}</td>
          <td class="num-s">{int(r.get('incoming_cr') or 0)}</td>
          <td class="num-s">{int(r.get('async_total') or 0)}</td>
        </tr>"""
    return f"""
    <table class="dt">
      <thead><tr>
        <th>Escritório</th>
        <th>Async/Caso<br><small>{fmt_date(mes_ini)}–{fmt_date(ontem)}</small></th>
        <th>CR</th><th>Async Total</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>"""

def section_lideres(team):
    rows = sorted([r for r in q5 if r['equipe'] == team], key=lambda x: -(x.get('async_por_caso') or 0))
    if not rows: return "<p class='empty'>Sem dados</p>"
    rows_html = "".join(f"""
    <tr data-office="{r['escritorio']}">
      <td>{r['lider'] or '—'}</td>
      <td>{r['escritorio']}</td>
      <td class='num'>{icon(r.get('async_por_caso'))}</td>
      <td class='num-s'>{int(r.get('incoming_cr') or 0)}</td>
      <td class='num-s'>{int(r.get('async_total') or 0)}</td>
    </tr>""" for r in rows)
    return f"""
    <table class="dt">
      <thead><tr><th>Líder</th><th>Escritório</th><th>Async/Caso</th><th>CR</th><th>Async</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>"""

def section_reps(team):
    rows = sorted([r for r in q6 if r['equipe'] == team], key=lambda x: -(x.get('async_por_caso') or 0))[:20]
    if not rows: return "<p class='empty'>Sem dados (mín. 10 CR)</p>"
    rows_html = "".join(f"""
    <tr data-office="{r['escritorio']}">
      <td>{r['rep']}</td>
      <td>{r['escritorio']}</td>
      <td>{r['lider'] or '—'}</td>
      <td class='num'>{icon(r.get('async_por_caso'))}</td>
      <td class='num-s'>{int(r.get('incoming_cr') or 0)}</td>
      <td class='num-s'>{int(r.get('async_total') or 0)}</td>
    </tr>""" for r in rows)
    return f"""
    <table class="dt">
      <thead><tr><th>Rep</th><th>Escritório</th><th>Líder</th><th>Async/Caso</th><th>CR</th><th>Async</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>"""

# ── charts ────────────────────────────────────────────────────────────────────

def build_line_datasets(offices, idx_fn, keys, color_map):
    datasets = []
    n = len(offices)
    for i, off in enumerate(offices):
        color = color_map[off]
        data = [float(v) if (v := idx_fn(off, k)) is not None else None for k in keys]
        datasets.append({
            'label': off,
            'data': data,
            'borderColor': color,
            'backgroundColor': color + '22',
            'tension': 0.35,
            'spanGaps': True,
            'pointRadius': 4,
            'pointHoverRadius': 6,
            'borderWidth': 2,
            'fill': False,
        })
    # reference lines
    n_pts = len(keys)
    datasets.append({'label': '__ref1__', 'data': [1.0]*n_pts, 'borderColor': '#b8860b',
                     'borderDash': [6,4], 'pointRadius': 0, 'borderWidth': 1.5,
                     'fill': False, 'tension': 0})
    datasets.append({'label': '__ref2__', 'data': [2.0]*n_pts, 'borderColor': '#c0392b',
                     'borderDash': [6,4], 'pointRadius': 0, 'borderWidth': 1.5,
                     'fill': False, 'tension': 0})
    return datasets

def section_chart_daily(team):
    team_rows = [r for r in q1 if r['equipe'] == team]
    if not team_rows: return "<p class='empty'>Sem dados</p>"
    dias = sorted(set(str(r['dia'])[:10] for r in team_rows))
    offices = sorted(set(r['escritorio'] for r in team_rows))
    idx = {(str(r['dia'])[:10], r['escritorio']): r.get('async_por_caso') for r in team_rows}
    color_map = {off: COLORS[i % len(COLORS)] for i, off in enumerate(offices)}
    labels = [d[5:].replace('-','/') for d in dias]
    datasets = build_line_datasets(offices, lambda o, d: idx.get((d, o)), dias, color_map)
    short = TEAM_SHORT[team]
    cid = f"chart-daily-{short}"
    data_json = json.dumps({'labels': labels, 'datasets': datasets}, default=jd)
    return f"""<div style="position:relative;height:300px"><canvas id="{cid}"></canvas></div>
<script>(function(){{
  var ctx=document.getElementById('{cid}').getContext('2d');
  window._charts=window._charts||{{}};
  window._charts['{cid}']=new Chart(ctx,{{
    type:'line',
    data:{data_json},
    options:{{
      responsive:true,maintainAspectRatio:false,
      interaction:{{mode:'index',intersect:false}},
      plugins:{{
        legend:{{
          position:'top',
          labels:{{filter:function(i){{return !i.text.startsWith('__');}},boxWidth:12,font:{{size:11}}}}
        }},
        tooltip:{{filter:function(i){{return !i.dataset.label.startsWith('__');}}}}
      }},
      scales:{{
        y:{{title:{{display:true,text:'async/caso',font:{{size:11}}}},min:0,
           ticks:{{font:{{size:11}}}}}},
        x:{{ticks:{{maxRotation:45,font:{{size:10}}}}}}
      }}
    }}
  }});
}})();
</script>"""

def section_chart_trend(team):
    team_rows = [r for r in q7 if r['equipe'] == team]
    if not team_rows: return "<p class='empty'>Sem dados</p>"
    semanas = sorted(set(str(r['semana'])[:10] for r in team_rows))
    offices = sorted(set(r['escritorio'] for r in team_rows))
    idx = {(str(r['semana'])[:10], r['escritorio']): r.get('async_por_caso') for r in team_rows}
    color_map = {off: COLORS[i % len(COLORS)] for i, off in enumerate(offices)}
    labels = [s[5:].replace('-','/') for s in semanas]
    datasets = build_line_datasets(offices, lambda o, s: idx.get((s, o)), semanas, color_map)
    short = TEAM_SHORT[team]
    cid = f"chart-trend-{short}"
    data_json = json.dumps({'labels': labels, 'datasets': datasets}, default=jd)
    return f"""<div style="position:relative;height:300px"><canvas id="{cid}"></canvas></div>
<script>(function(){{
  var ctx=document.getElementById('{cid}').getContext('2d');
  window._charts=window._charts||{{}};
  window._charts['{cid}']=new Chart(ctx,{{
    type:'line',
    data:{data_json},
    options:{{
      responsive:true,maintainAspectRatio:false,
      interaction:{{mode:'index',intersect:false}},
      plugins:{{
        legend:{{
          position:'top',
          labels:{{filter:function(i){{return !i.text.startsWith('__');}},boxWidth:12,font:{{size:11}}}}
        }},
        tooltip:{{filter:function(i){{return !i.dataset.label.startsWith('__');}}}}
      }},
      scales:{{
        y:{{title:{{display:true,text:'async/caso',font:{{size:11}}}},min:0,
           ticks:{{font:{{size:11}}}}}},
        x:{{ticks:{{font:{{size:11}}}}}}
      }}
    }}
  }});
}})();
</script>"""

# ── exec summary ──────────────────────────────────────────────────────────────

def exec_summary(team):
    ant = {r['escritorio']: r for r in q2 if r['equipe'] == team}
    act = {r['escritorio']: r for r in q3 if r['equipe'] == team}
    all_offices = pivot_offices(q2, team)
    worst = all_offices[0] if all_offices else None
    bullet1 = (f"Office com maior async/caso (sem ant): <strong>{worst['escritorio']}</strong> — {icon(worst.get('async_por_caso'))}"
               if worst else "Sem dados de office")
    if worst:
        off = worst['escritorio']
        vant = ant.get(off, {}).get('async_por_caso')
        vact = act.get(off, {}).get('async_por_caso')
        d = (vact - vant) if (vact is not None and vant is not None) else None
        if d is not None:
            dstr = f"+{d:.2f}" if d >= 0 else f"{d:.2f}"
            bullet2 = f"Delta WoW {off}: {icon(vant)} → {icon(vact)} ({dstr})"
        else:
            bullet2 = f"Delta WoW {off}: sem dados da semana atual"
    else:
        bullet2 = "Sem dados WoW"
    criticos = [r for r in q6 if r['equipe'] == team and (r.get('async_por_caso') or 0) > 2.0]
    bullet3 = f"Reps com async/caso &gt; 2.0 (sem ant): <strong>{len(criticos)}</strong> rep{'s' if len(criticos)!=1 else ''}"
    return f"""
    <ul class="exec">
      <li>{bullet1}</li>
      <li>{bullet2}</li>
      <li>{bullet3}</li>
    </ul>"""

# ── tab content ───────────────────────────────────────────────────────────────

def tab_content(team):
    short = TEAM_SHORT[team]
    return f"""
    <div id="tab-{short}" class="tab-content">
      <h2>{team}</h2>
      {section_office_filter(team)}

      <div class="card">
        <h3>Resumo Executivo</h3>
        {exec_summary(team)}
      </div>

      <div class="card">
        <h3>WoW por Office</h3>
        {section_wow(team)}
      </div>

      <div class="card">
        <h3>Mês Acumulado por Office <small>({mes_ini.strftime('%b/%Y')})</small></h3>
        {section_mes(team)}
      </div>

      <div class="card">
        <h3>Diário — últimos 15 dias por Office <small>(linhas tracejadas: limites 1.0 e 2.0)</small></h3>
        {section_chart_daily(team)}
      </div>

      <div class="card">
        <h3>Por Team Leader <small>(sem {fmt_date(sem_ant_ini)}–{fmt_date(sem_ant_fin)})</small></h3>
        {section_lideres(team)}
      </div>

      <div class="card">
        <h3>Top 20 Reps — maior async/caso <small>(mín. 10 CR)</small></h3>
        {section_reps(team)}
      </div>

      <div class="card">
        <h3>Tendência 8 Semanas por Office <small>(linhas tracejadas: limites 1.0 e 2.0)</small></h3>
        {section_chart_trend(team)}
      </div>
    </div>"""

# ── assemble HTML ─────────────────────────────────────────────────────────────

tabs_nav = ""
tabs_body = ""
for i, team in enumerate(TEAMS):
    short = TEAM_SHORT[team]
    active = "active" if i == 0 else ""
    tabs_nav += f'<button class="tab-btn {active}" onclick="showTab(\'{short}\')">{short}</button>'
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
    --green: #1a8a3c; --yellow: #b8860b; --red: #c0392b;
    --bg: #f4f6f8; --card: #fff; --border: #dde3ea;
    --head: #2c3e50; --accent: #3498db;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); color: #222; font-size: 13px; }}
  header {{ background: var(--head); color: #fff; padding: 16px 24px; }}
  header h1 {{ font-size: 18px; }}
  header .sub {{ font-size: 11px; opacity: .7; margin-top: 4px; }}
  .legend {{ display: flex; gap: 16px; padding: 8px 24px; background: #fff; border-bottom: 1px solid var(--border); font-size: 11px; }}
  .legend span {{ display: flex; align-items: center; gap: 4px; }}
  .tabs {{ display: flex; gap: 4px; padding: 12px 24px 0; background: #fff; border-bottom: 2px solid var(--accent); }}
  .tab-btn {{ padding: 8px 20px; border: none; background: #eef2f7; border-radius: 6px 6px 0 0; cursor: pointer; font-size: 13px; font-weight: 600; color: #555; transition: all .15s; }}
  .tab-btn.active {{ background: var(--accent); color: #fff; }}
  .tab-btn:hover:not(.active) {{ background: #d5e8f7; }}
  .tab-content {{ display: none; padding: 20px 24px; }}
  .tab-content.show {{ display: block; }}
  .tab-content h2 {{ font-size: 15px; color: var(--head); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
  .card h3 {{ font-size: 13px; font-weight: 700; color: var(--head); margin-bottom: 12px; }}
  .card h3 small {{ font-weight: 400; color: #777; font-size: 11px; }}
  /* office filter */
  .off-filter {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }}
  .off-btn {{ padding: 5px 14px; border: 1.5px solid var(--border); background: #fff; border-radius: 20px;
              cursor: pointer; font-size: 11px; font-weight: 600; color: #555; transition: all .15s; }}
  .off-btn.active {{ background: var(--head); color: #fff; border-color: var(--head); }}
  .off-btn:hover:not(.active) {{ background: #eef2f7; border-color: #aaa; }}
  /* tables */
  table.dt {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
  table.dt th {{ background: #f0f4f8; padding: 6px 10px; text-align: center; font-size: 11px; border-bottom: 2px solid var(--border); white-space: nowrap; }}
  table.dt th:first-child {{ text-align: left; }}
  table.dt td {{ padding: 5px 10px; border-bottom: 1px solid #eef0f3; white-space: nowrap; text-align: center; }}
  table.dt td:first-child {{ text-align: left; }}
  table.dt tr:hover td {{ background: #f7fafd; }}
  td.num {{ text-align: center; font-weight: 600; }}
  td.num-s {{ text-align: center; color: #666; }}
  td.day {{ font-weight: 600; color: #444; text-align: left; }}
  .ok   {{ color: var(--green); }}
  .warn {{ color: var(--yellow); }}
  .crit {{ color: var(--red); font-weight: 700; }}
  .nd   {{ color: #bbb; }}
  .good {{ color: var(--green); }}
  .bad  {{ color: var(--red); }}
  .neutral {{ color: #888; }}
  ul.exec {{ padding-left: 18px; }}
  ul.exec li {{ margin-bottom: 6px; line-height: 1.5; }}
  .empty {{ color: #999; font-style: italic; padding: 8px 0; }}
  @media (max-width: 600px) {{
    .tabs {{ overflow-x: auto; flex-wrap: nowrap; }}
    .tab-content {{ padding: 12px; }}
  }}
</style>
</head>
<body>
<header>
  <h1>Chat Assíncrono — Longtail Sellers BR</h1>
  <div class="sub">Atualizado: {today.strftime('%d/%m/%Y')} &nbsp;|&nbsp; Tabela: DM_CX_IXC_DETAIL &nbsp;|&nbsp; Métrica: async/caso = disparos assíncronos / DENOM_IXC</div>
</header>

<div class="legend">
  <span><span class="ok">●</span> &lt; 1.0 Normal</span>
  <span><span class="warn">●</span> 1.0–2.0 Atenção</span>
  <span><span class="crit">●</span> &gt; 2.0 Crítico</span>
  <span style="margin-left:auto; color:#888">↑ piora &nbsp; ↓ melhora &nbsp; → estável (&lt;0.05)</span>
</div>

<div class="tabs">
  {tabs_nav}
</div>

{tabs_body}

<script>
function showTab(id) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('show'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('show');
  event.target.classList.add('active');
}}
document.querySelector('.tab-content').classList.add('show');

function filterOffice(team, office, btn) {{
  // botões
  document.querySelectorAll('#filter-' + team + ' .off-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  // linhas das tabelas
  document.querySelectorAll('#tab-' + team + ' tr[data-office]').forEach(row => {{
    row.style.display = (office === 'ALL' || row.dataset.office === office) ? '' : 'none';
  }});
  // gráficos
  ['chart-daily-' + team, 'chart-trend-' + team].forEach(cid => {{
    var chart = (window._charts || {{}})[cid];
    if (!chart) return;
    chart.data.datasets.forEach((ds, i) => {{
      var isRef = ds.label.startsWith('__');
      var visible = isRef || office === 'ALL' || ds.label === office;
      chart.setDatasetVisibility(i, visible);
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
print(f"HTML salvo em {out_raw} e {out_pub}")
