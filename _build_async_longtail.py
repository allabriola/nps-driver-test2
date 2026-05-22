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

today = date.today()
dow = today.weekday()  # Mon=0 Sun=6
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

# Q5 — por team leader
q5 = run(f"""
SELECT USER_TEAM_NAME AS equipe, CS_MANAGER AS lider, USER_OFFICE AS escritorio,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND USER_TEAM_NAME IN ({TEAMS_IN})
  AND CS_MANAGER IS NOT NULL
GROUP BY 1,2,3 ORDER BY 1, async_por_caso DESC
""")
print(f"  Q5 lideres: {len(q5)} linhas")

# Q6 — top reps
q6 = run(f"""
SELECT USER_TEAM_NAME AS equipe, CI_OWNER_ID AS rep, USER_OFFICE AS escritorio, CS_MANAGER AS lider,
  COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") AS async_total,
  SUM(DENOM_IXC) AS incoming_cr,
  ROUND(COUNTIF(SUB_TASA LIKE "%Chat asincrónico%") / NULLIF(SUM(DENOM_IXC), 0), 2) AS async_por_caso
FROM `meli-bi-data.WHOWNER.DM_CX_IXC_DETAIL`
WHERE VALID_IXC_FLAG = TRUE
  AND DATE_ID BETWEEN "{sem_ant_ini}" AND "{sem_ant_fin}"
  AND USER_TEAM_NAME IN ({TEAMS_IN})
  AND CI_OWNER_ID IS NOT NULL
GROUP BY 1,2,3,4
HAVING SUM(DENOM_IXC) >= 10
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

def icon(v):
    if v is None: return "—"
    if v < 1.0:   return f'<span class="ok">{v:.2f}</span>'
    if v <= 2.0:  return f'<span class="warn">{v:.2f}</span>'
    return             f'<span class="crit">{v:.2f}</span>'

def delta_arrow(prev, curr):
    if prev is None or curr is None: return "—"
    d = curr - prev
    if abs(d) < 0.05: arrow = "→"
    elif d > 0:       arrow = "↑"
    else:             arrow = "↓"
    cls = "bad" if d > 0 else ("good" if d < 0 else "neutral")
    return f'<span class="{cls}">{arrow} {abs(d):.2f}</span>'

def fmt_date(d):
    if d is None: return "—"
    if hasattr(d, 'strftime'): return d.strftime('%d/%m')
    return str(d)[:10][5:].replace('-','/')

# ── build pivot tables ────────────────────────────────────────────────────────

def pivot_offices(rows, team):
    """rows: list of dicts with escritorio + async_por_caso. Returns sorted list."""
    return sorted([r for r in rows if r['equipe'] == team], key=lambda x: -(x.get('async_por_caso') or 0))

# ── HTML sections per team ────────────────────────────────────────────────────

def section_wow(team):
    ant = {r['escritorio']: r for r in q2 if r['equipe'] == team}
    act = {r['escritorio']: r for r in q3 if r['equipe'] == team}
    offices = sorted(set(list(ant.keys()) + list(act.keys())))
    if not offices:
        return "<p class='empty'>Sem dados</p>"
    rows_html = ""
    for off in offices:
        a = ant.get(off, {})
        c = act.get(off, {})
        vant = a.get('async_por_caso')
        vact = c.get('async_por_caso')
        rows_html += f"""
        <tr>
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
    if not rows:
        return "<p class='empty'>Sem dados</p>"
    rows_html = ""
    for r in rows:
        rows_html += f"""
        <tr>
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

def section_heatmap(team):
    team_rows = [r for r in q1 if r['equipe'] == team]
    if not team_rows:
        return "<p class='empty'>Sem dados</p>"
    dias = sorted(set(str(r['dia'])[:10] for r in team_rows), reverse=True)
    offices = sorted(set(r['escritorio'] for r in team_rows))
    idx = {(str(r['dia'])[:10], r['escritorio']): r for r in team_rows}
    head = "<tr><th>Dia</th>" + "".join(f"<th>{o}</th>" for o in offices) + "</tr>"
    body = ""
    for d in dias:
        body += f"<tr><td class='day'>{d[5:].replace('-','/')}</td>"
        for o in offices:
            r = idx.get((d, o))
            v = r.get('async_por_caso') if r else None
            body += f"<td class='num'>{icon(v) if v is not None else '<span class=nd>—</span>'}</td>"
        body += "</tr>"
    return f"<table class='dt heat'><thead>{head}</thead><tbody>{body}</tbody></table>"

def section_lideres(team):
    rows = sorted([r for r in q5 if r['equipe'] == team], key=lambda x: -(x.get('async_por_caso') or 0))
    if not rows:
        return "<p class='empty'>Sem dados</p>"
    rows_html = "".join(f"""
    <tr>
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
    if not rows:
        return "<p class='empty'>Sem dados (mín. 10 CR)</p>"
    rows_html = "".join(f"""
    <tr>
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

def section_trend(team):
    team_rows = [r for r in q7 if r['equipe'] == team]
    if not team_rows:
        return "<p class='empty'>Sem dados</p>"
    semanas = sorted(set(str(r['semana'])[:10] for r in team_rows))
    offices = sorted(set(r['escritorio'] for r in team_rows))
    idx = {(str(r['semana'])[:10], r['escritorio']): r for r in team_rows}
    head = "<tr><th>Semana</th>" + "".join(f"<th>{o}</th>" for o in offices) + "</tr>"
    body = ""
    for i, s in enumerate(semanas):
        body += f"<tr><td class='day'>{fmt_date(s)}</td>"
        for o in offices:
            r = idx.get((s, o))
            v = r.get('async_por_caso') if r else None
            if i > 0:
                prev_r = idx.get((semanas[i-1], o))
                vp = prev_r.get('async_por_caso') if prev_r else None
                arr = delta_arrow(vp, v) if (v is not None and vp is not None) else ""
                cell = f"{icon(v) if v is not None else '—'} {arr}"
            else:
                cell = icon(v) if v is not None else "—"
            body += f"<td class='num'>{cell}</td>"
        body += "</tr>"
    return f"<table class='dt heat'><thead>{head}</thead><tbody>{body}</tbody></table>"

def exec_summary(team):
    """3 bullets: pior office, delta WoW, reps críticos"""
    ant = {r['escritorio']: r for r in q2 if r['equipe'] == team}
    act = {r['escritorio']: r for r in q3 if r['equipe'] == team}
    all_offices = pivot_offices(q2, team)
    worst = all_offices[0] if all_offices else None

    bullet1 = f"Office com maior async/caso (sem ant): <strong>{worst['escritorio']}</strong> — {icon(worst.get('async_por_caso'))}" if worst else "Sem dados de office"

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

# ── build tab content ─────────────────────────────────────────────────────────

def tab_content(team):
    short = TEAM_SHORT[team]
    return f"""
    <div id="tab-{short}" class="tab-content">
      <h2>{team}</h2>

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
        <h3>Heatmap Diário — últimos 15 dias</h3>
        <div class="scroll-x">{section_heatmap(team)}</div>
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
        <h3>Tendência 8 Semanas por Office</h3>
        <div class="scroll-x">{section_trend(team)}</div>
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
  .tab-content h2 {{ font-size: 15px; color: var(--head); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
  .card h3 {{ font-size: 13px; font-weight: 700; color: var(--head); margin-bottom: 12px; }}
  .card h3 small {{ font-weight: 400; color: #777; font-size: 11px; }}
  .scroll-x {{ overflow-x: auto; }}
  table.dt {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
  table.dt th {{ background: #f0f4f8; padding: 6px 10px; text-align: left; font-size: 11px; border-bottom: 2px solid var(--border); white-space: nowrap; }}
  table.dt td {{ padding: 5px 10px; border-bottom: 1px solid #eef0f3; white-space: nowrap; }}
  table.dt tr:hover td {{ background: #f7fafd; }}
  td.num {{ text-align: center; font-weight: 600; }}
  td.num-s {{ text-align: center; color: #666; }}
  td.day {{ font-weight: 600; color: #444; }}
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
</script>
</body>
</html>"""

out = r"c:\Users\allabriola\PROJETO CLAUDINHO\_async_longtail.html"
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML salvo: {out}")
