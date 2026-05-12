import json, math

# ── dados coletados do BigQuery ──────────────────────────────────────────────

WEEKS = ['30/03','06/04','13/04','20/04','27/04','04/05']

NPS_W  = dict(
    treatment=[65.9, 59.9, 59.5, 67.7, 69.6, 69.5],
    control  =[57.5, 56.0, 53.2, 53.1, 50.4, 54.9],
)
TMO_W  = dict(
    treatment=[31.6, 36.8, 38.6, 39.1, 39.4, 40.4],
    control  =[28.3, 31.1, 30.8, 30.7, 29.9, 30.2],
)
PROD_W = dict(
    treatment=[0.98, 0.87, 1.09, 1.17, 1.16, 1.07],
    control  =[1.11, 1.10, 1.30, 1.37, 1.31, 1.25],
)

# mensais: Mar, Abr, Mai*
NPS_M  = dict(treatment=[49.2, 64.2, 70.0], control=[61.4, 53.9, 53.7])
TMO_M  = dict(treatment=[34.7, 38.8, 40.2], control=[29.7, 31.3, 29.8])
PROD_M = dict(treatment=[1.15, 1.06, 1.10], control=[1.38, 1.24, 1.30])

PESQ_M = dict(
    treatment=[63,   3087, 1276],
    control  =[114,  5454, 1441],
)
REPS_M = dict(
    treatment=[42,   206,  196],
    control  =[79,   413,  255],
)
CASOS_M = dict(
    treatment=[48855, 64124, 26377],
    control  =[115411,119526, 34435],
)

# scorecard últimas 2 semanas (Abr28-Mai11)
SC = dict(
    treatment=dict(nps=70.5, reps=202, pesq=1652),
    control  =dict(nps=52.6, reps=311, pesq=2003),
)

# reps treatment individuais
with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_rep_data_me.json', encoding='utf-8') as f:
    REPS_RAW = json.load(f)

# ── helpers ──────────────────────────────────────────────────────────────────

def fmt_nps(v):
    if v is None: return '<span class="sd">—</span>'
    v = float(v)
    cls = 'gc' if v >= 65 else ('yc' if v >= 50 else 'rc')
    return f'<span class="{cls}">{v:.1f}%</span>'

def fmt_tmo(v):
    if v is None: return '<span class="sd">—</span>'
    return f'{v:.1f}'

def delta_nps(t, c):
    d = round(t - c, 1)
    cls = 'pos' if d > 0 else ('neg' if d < 0 else 'neu')
    sign = '+' if d > 0 else ''
    return f'<span class="dlt {cls}">{sign}{d}pp</span>'

def delta_pct(t, c, reverse=False):
    d = round((t - c) / c * 100, 1)
    better = d < 0 if reverse else d > 0
    cls = 'pos' if better else ('neg' if not better else 'neu')
    sign = '+' if d > 0 else ''
    return f'<span class="dlt {cls}">{sign}{d}%</span>'

def scorecard_row(label, t_val, c_val, fmt='nps', reverse=False, unit=''):
    if fmt == 'nps':
        tv = f'{t_val:.1f}%'
        cv = f'{c_val:.1f}%'
        d  = delta_nps(t_val, c_val)
    elif fmt == 'tmo':
        tv = f'{t_val:.1f} min'
        cv = f'{c_val:.1f} min'
        d  = delta_pct(t_val, c_val, reverse=True)
    else:
        tv = f'{t_val:.2f}'
        cv = f'{c_val:.2f}'
        d  = delta_pct(t_val, c_val, reverse=reverse)
    arrow = '↑' if not reverse else '↓'
    return f'''
    <div class="kc">
      <div class="lbl">{label} {arrow}</div>
      <div class="val">{tv}</div>
      <div class="cmp">Controle: {cv}</div>
      {d}
    </div>'''

def chart_data(weeks_data, label1, label2):
    return (
        f'{{label:"{label1}",data:{json.dumps(weeks_data["treatment"])},'
        f'borderColor:BLUE,backgroundColor:BLUE+"18",borderWidth:2.5,'
        f'pointRadius:5,tension:0.35,spanGaps:true}},'
        f'{{label:"{label2}",data:{json.dumps(weeks_data["control"])},'
        f'borderColor:GRAY,backgroundColor:GRAY+"18",borderWidth:2,'
        f'pointRadius:4,tension:0.35,borderDash:[6,4],spanGaps:true}}'
    )

# ── tabela por representante ─────────────────────────────────────────────────

def rep_row(r):
    ldap  = r['ldap']
    sen   = r.get('seniority','')
    conv  = int(r.get('conversas_cop',0) or 0)
    p_abr = int(r.get('pesq_abr',0) or 0)
    n_abr = r.get('nps_abr')
    p_mai = int(r.get('pesq_mai',0) or 0)
    n_mai = r.get('nps_mai')
    sen_badge = f'<span class="sen-e">E</span>' if sen=='EXPERT' else f'<span class="sen-n">N</span>'
    abr_cell = f'{fmt_nps(n_abr)} <span class="n-small">({p_abr})</span>' if p_abr else '<span class="sd">—</span>'
    mai_cell = f'{fmt_nps(n_mai)} <span class="n-small">({p_mai})</span>' if p_mai else '<span class="sd">—</span>'
    return (f'<tr><td class="rep-name">{ldap} {sen_badge}</td>'
            f'<td>{conv}</td><td>{abr_cell}</td><td>{mai_cell}</td></tr>')

rows_html = '\n'.join(rep_row(r) for r in REPS_RAW)

# ── HTML completo ─────────────────────────────────────────────────────────────

html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Copiloto — BR_ME_Sellers_Longtail</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f7;color:#1a1a2e}}
.header{{background:#1a1a2e;color:white;padding:20px 32px}}
.header h1{{font-size:18px;font-weight:700}}
.header .sub{{font-size:12px;color:#94a3b8;margin-top:4px}}
.container{{max-width:1320px;margin:0 auto;padding:20px 16px 40px}}
.legend{{display:flex;gap:18px;align-items:center;margin-bottom:14px}}
.leg{{display:flex;align-items:center;gap:6px;font-size:12px;color:#374151}}
.leg-solid{{width:22px;height:0;border-top:2.5px solid}}
.leg-dash{{width:22px;height:0;border-top:2.5px dashed}}
.section-lbl{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#94a3b8;margin:22px 0 10px;padding-top:10px;border-top:1px solid #e2e8f0}}
.period-label{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#94a3b8;margin:12px 0 8px}}
.sc-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:10px}}
.kc{{background:white;border-radius:10px;padding:12px 14px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.kc .lbl{{font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:#94a3b8;font-weight:600;margin-bottom:7px}}
.kc .val{{font-size:20px;font-weight:800;color:#1d4ed8;line-height:1}}
.kc .cmp{{font-size:11px;color:#94a3b8;margin-top:4px}}
.dlt{{font-size:11px;font-weight:600;padding:2px 7px;border-radius:5px;margin-top:7px;display:inline-block}}
.pos{{background:#dcfce7;color:#15803d}}.neg{{background:#fee2e2;color:#dc2626}}.neu{{background:#f1f5f9;color:#64748b}}
.ch-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:10px}}
.cc{{background:white;border-radius:10px;padding:16px 20px 14px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.cc h3{{font-size:12px;font-weight:700;color:#1e293b}}
.cc p{{font-size:10.5px;color:#94a3b8;margin:2px 0 10px}}
.rep-table-wrap{{margin-top:14px;overflow-x:auto}}
table.rt{{width:100%;border-collapse:collapse;font-size:11.5px}}
table.rt th{{background:#1a1a2e;color:white;padding:7px 10px;text-align:center;font-size:10.5px;font-weight:600;letter-spacing:.3px;white-space:nowrap}}
table.rt th.left{{text-align:left}}
table.rt td{{padding:5px 9px;border-bottom:1px solid #f1f5f9;text-align:center;white-space:nowrap}}
table.rt td.rep-name{{text-align:left;font-weight:600;font-size:11px;color:#1e293b}}
table.rt tr:hover td{{filter:brightness(.97)}}
.gc{{background:#dcfce7;color:#15803d;font-weight:700;padding:1px 6px;border-radius:4px}}
.yc{{background:#fef9c3;color:#854d0e;font-weight:700;padding:1px 6px;border-radius:4px}}
.rc{{background:#fee2e2;color:#dc2626;font-weight:700;padding:1px 6px;border-radius:4px}}
.sd{{color:#cbd5e1;font-style:italic}}
.n-small{{font-size:9.5px;color:#94a3b8}}
.sen-e{{background:#dbeafe;color:#1d4ed8;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;margin-left:3px}}
.sen-n{{background:#fef9c3;color:#854d0e;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;margin-left:3px}}
.note{{font-size:11px;color:#94a3b8;background:white;padding:9px 14px;border-radius:8px;border-left:3px solid #e2e8f0;margin-top:10px;line-height:1.6}}
.note strong{{color:#64748b}}
.note.warn{{border-left-color:#f59e0b;background:#fffbeb}}.note.warn strong{{color:#92400e}}
hr.div{{border:none;border-top:2px solid #e2e8f0;margin:24px 0}}
.footer{{font-size:11px;color:#94a3b8;text-align:center;margin-top:28px}}
.stat-row{{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap}}
.stat-chip{{background:white;border-radius:8px;padding:8px 14px;box-shadow:0 1px 3px rgba(0,0,0,.06);font-size:12px;color:#374151}}
.stat-chip strong{{color:#1d4ed8;font-size:15px}}
@media(max-width:900px){{.sc-grid{{grid-template-columns:repeat(2,1fr)}}.ch-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="header">
  <h1>Copiloto — Experimento Treatment vs Control · BR_ME_Sellers_Longtail</h1>
  <div class="sub">MULTICANAL CHAT · 209 reps com Copilot vs ~436 sem Copilot · Abr–Mai 2026 (rollout iniciado ~22/04)</div>
  <div class="sub" style="margin-top:5px;color:#64748b" id="ts"></div>
</div>

<div class="container">

  <div class="legend">
    <div class="leg"><span class="leg-solid" style="border-color:#2563EB"></span>Com Copiloto (Treatment)</div>
    <div class="leg"><span class="leg-dash" style="border-color:#9CA3AF"></span>Sem Copiloto (Controle)</div>
    <div class="leg" style="font-size:11px;color:#94a3b8">* Mai vigente até 11/05 &nbsp;·&nbsp; NPS por rep com &lt;5 pesquisas tem alta variância</div>
  </div>

  <!-- ===================== SCORECARD CONSOLIDADO ===================== -->
  <div class="section-lbl">Scorecard Consolidado — Últimas 2 Semanas (28/04–11/05)</div>
  <div class="stat-row">
    <div class="stat-chip">Treatment: <strong>202 reps</strong> · {SC['treatment']['pesq']:,} pesquisas NPS</div>
    <div class="stat-chip">Controle: <strong>311 reps</strong> · {SC['control']['pesq']:,} pesquisas NPS</div>
    <div class="stat-chip">Total: <strong>21.196 conversas Copilot</strong> registradas</div>
  </div>
  <div class="sc-grid">
    {scorecard_row('NPS', SC['treatment']['nps'], SC['control']['nps'], 'nps')}
    {scorecard_row('TMO ↓', TMO_M['treatment'][1], TMO_M['control'][1], 'tmo', True)}
    {scorecard_row('Produtividade', PROD_M['treatment'][1], PROD_M['control'][1], 'prod')}
  </div>

  <!-- ===================== MENSAL ===================== -->
  <div class="section-lbl">Por Mês</div>

  <div class="period-label">Março 2026 — fechado · <em style="color:#f59e0b;font-size:10px">⚠ Copilot ainda não ativo para a maioria. Dados do NPS com amostras reduzidas (n={PESQ_M['treatment'][0]} treatment / n={PESQ_M['control'][0]} controle)</em></div>
  <div class="sc-grid">
    {scorecard_row('NPS', NPS_M['treatment'][0], NPS_M['control'][0], 'nps')}
    {scorecard_row('TMO ↓', TMO_M['treatment'][0], TMO_M['control'][0], 'tmo', True)}
    {scorecard_row('Produtividade', PROD_M['treatment'][0], PROD_M['control'][0], 'prod')}
  </div>

  <div class="period-label">Abril 2026 — fechado · n={PESQ_M['treatment'][1]:,} pesquisas treatment / n={PESQ_M['control'][1]:,} controle</div>
  <div class="sc-grid">
    {scorecard_row('NPS', NPS_M['treatment'][1], NPS_M['control'][1], 'nps')}
    {scorecard_row('TMO ↓', TMO_M['treatment'][1], TMO_M['control'][1], 'tmo', True)}
    {scorecard_row('Produtividade', PROD_M['treatment'][1], PROD_M['control'][1], 'prod')}
  </div>

  <div class="period-label">Maio 2026* — vigente até 11/05 · n={PESQ_M['treatment'][2]:,} pesquisas treatment / n={PESQ_M['control'][2]:,} controle</div>
  <div class="sc-grid">
    {scorecard_row('NPS', NPS_M['treatment'][2], NPS_M['control'][2], 'nps')}
    {scorecard_row('TMO ↓', TMO_M['treatment'][2], TMO_M['control'][2], 'tmo', True)}
    {scorecard_row('Produtividade', PROD_M['treatment'][2], PROD_M['control'][2], 'prod')}
  </div>

  <hr class="div">

  <!-- ===================== GRÁFICOS SEMANAIS ===================== -->
  <div class="section-lbl">Evolução Semanal — 6 Semanas (30/03–04/05)</div>
  <div class="ch-grid">
    <div class="cc">
      <h3>NPS †</h3>
      <p>% · Maior é melhor ↑ · Treatment consistentemente acima do controle a partir de Abr</p>
      <canvas id="chartNPS"></canvas>
    </div>
    <div class="cc">
      <h3>TMO por Caso</h3>
      <p>min · Menor é melhor ↓ · Treatment com TMO mais alto (~+9 min): reps gastam mais tempo com respostas qualificadas</p>
      <canvas id="chartTMO"></canvas>
    </div>
    <div class="cc">
      <h3>Produtividade</h3>
      <p>at/h · Maior é melhor ↑ · Controle com produtividade levemente superior</p>
      <canvas id="chartPROD"></canvas>
    </div>
  </div>

  <div class="note warn">
    <strong>⚠ Interpretação:</strong> Treatment tem NPS <strong>+{round(NPS_M['treatment'][2]-NPS_M['control'][2],1)}pp</strong> em Maio vs Controle, mas TMO <strong>+{round(TMO_M['treatment'][2]-TMO_M['control'][2],1)} min</strong> maior e Produtividade <strong>{round((PROD_M['treatment'][2]/PROD_M['control'][2]-1)*100,0):.0f}%</strong> menor. O trade-off sugere que o Copilot melhora a qualidade percebida pelo cliente (respostas mais completas/assertivas) ao custo de maior tempo de atendimento. O volume de casos diferentes entre os grupos ({CASOS_M['treatment'][1]:,} treatment vs {CASOS_M['control'][1]:,} controle em Abr) reflete o número de reps, não uma seleção de casos.
  </div>

  <hr class="div">

  <!-- ===================== TABELA POR REPRESENTANTE ===================== -->
  <div class="section-lbl">Acompanhamento por Representante — Treatment Group (209 reps com Copilot)</div>
  <div class="note" style="margin-bottom:10px">
    <strong>Colunas:</strong> Conversas Copilot = total de sessões com o assistente (Abr+Mai) · NPS Abr / NPS Mai = % NPS do rep no período · (n) = número de pesquisas respondidas · <span class="gc">Verde</span> ≥ 65% · <span class="yc">Amarelo</span> 50–65% · <span class="rc">Vermelho</span> &lt; 50% · <span class="sen-e">E</span> Expert / <span class="sen-n">N</span> Newbie
  </div>
  <div class="rep-table-wrap">
    <table class="rt">
      <thead>
        <tr>
          <th class="left">Representante</th>
          <th>Conversas<br>Copilot</th>
          <th>NPS Abril</th>
          <th>NPS Maio*</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>

  <div class="note" style="margin-top:10px">
    <strong>Reps sem NPS:</strong> alguns dos 209 reps com Copilot não aparecem na tabela por não ter tido pesquisas respondidas no período analisado (ex: reps novos, em treinamento ou em filas sem survey).<br>
    <strong>Fonte:</strong> BT_CX_COPILOT_METRICS (Copilot) · DM_CX_NPS_Y20_DETAIL (NPS) · BT_CX_CXCOPILOT_TMO (TMO/Produt.) · Equipe: BR_ME_Sellers_Longtail · Período: Abr–Mai 2026
  </div>

  <div class="footer">Gerado em <span id="ts2"></span> · BR_ME_Sellers_Longtail Copiloto Analysis</div>
</div>

<script>
document.getElementById('ts').textContent = new Date().toLocaleDateString('pt-BR',{{day:'2-digit',month:'2-digit',year:'numeric'}});
document.getElementById('ts2').textContent = document.getElementById('ts').textContent;

const WEEKS = {json.dumps(WEEKS)};
const BLUE  = '#2563EB';
const GRAY  = '#9CA3AF';

function makeChart(id, ds, yLabel, yMin, yMax) {{
  new Chart(document.getElementById(id), {{
    type: 'line',
    data: {{ labels: WEEKS, datasets: ds }},
    options: {{
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1.6,
      plugins: {{
        legend: {{ position:'bottom', labels:{{ font:{{size:11}}, padding:12, usePointStyle:true, pointStyleWidth:8 }} }},
        tooltip: {{ callbacks: {{ label: ctx => ctx.parsed.y==null ? null : ` ${{ctx.dataset.label}}: ${{ctx.parsed.y.toFixed(2)}} ${{yLabel}}` }} }}
      }},
      scales: {{
        y: {{ min:yMin, max:yMax, grid:{{color:'#f1f5f9'}}, ticks:{{font:{{size:11}}}} }},
        x: {{ grid:{{display:false}}, ticks:{{font:{{size:11}}}} }}
      }}
    }}
  }});
}}

const ds = (tData, cData, tLabel, cLabel) => [
  {{label:tLabel, data:tData, borderColor:BLUE, backgroundColor:BLUE+'18', borderWidth:2.5, pointRadius:5, tension:0.35, spanGaps:true}},
  {{label:cLabel, data:cData, borderColor:GRAY, backgroundColor:GRAY+'18', borderWidth:2, pointRadius:4, tension:0.35, borderDash:[6,4], spanGaps:true}}
];

makeChart('chartNPS',
  ds({json.dumps(NPS_W['treatment'])},{json.dumps(NPS_W['control'])},'Com Copiloto','Sem Copiloto'),
  '%', 35, 90);

makeChart('chartTMO',
  ds({json.dumps(TMO_W['treatment'])},{json.dumps(TMO_W['control'])},'Com Copiloto','Sem Copiloto'),
  'min', 20, 50);

makeChart('chartPROD',
  ds({json.dumps(PROD_W['treatment'])},{json.dumps(PROD_W['control'])},'Com Copiloto','Sem Copiloto'),
  'at/h', 0.6, 1.6);

// Filtro de busca na tabela
document.addEventListener('DOMContentLoaded', function() {{
  const rows = document.querySelectorAll('table.rt tbody tr');
  const input = document.createElement('input');
  input.type = 'text'; input.placeholder = 'Buscar representante...';
  input.style.cssText = 'width:280px;padding:6px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;margin-bottom:8px;';
  input.oninput = () => {{
    const q = input.value.toLowerCase();
    rows.forEach(r => r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none');
  }};
  document.querySelector('.rep-table-wrap').before(input);
}});
</script>
</body>
</html>'''

out_path = r'c:\Users\allabriola\PROJETO CLAUDINHO\copiloto_analise_me.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Gerado: {out_path}')
print(f'Reps na tabela: {len(REPS_RAW)}')
