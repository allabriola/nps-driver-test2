import re, shutil

with open('C:/claudinho/reputacion_longtail_abr_mai_2026.html', encoding='utf-8') as f:
    html = f.read()

# ── 1. Adicionar CDN ChartDataLabels ────────────────────────
old_cdn = '<script src="chartjs.min.js"></script>'
new_cdn = '<script src="chartjs.min.js"></script>\n<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>'
html = html.replace(old_cdn, new_cdn, 1)

# ── 2. Registrar globalmente com default OFF ─────────────────
old_show = 'function showTab(id, btn) {'
new_show = '''// ChartDataLabels: registro global, default off
if (typeof ChartDataLabels !== 'undefined') {
  Chart.register(ChartDataLabels);
  Chart.defaults.plugins.datalabels.display = false;
}

// Helper: adicionar variação abaixo do chart
function addChartDelta(canvasId, deltaNPS, deltaExcl) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  const fmt = (v) => (v >= 0 ? '+' : '') + v.toFixed(1) + 'pp';
  const cls = (v) => v >= 0 ? 'pos' : 'neg';
  const div = document.createElement('div');
  div.className = 'chart-delta';
  div.innerHTML =
    '<span class="cd-nps ' + cls(deltaNPS) + '">&#916; NPS: ' + fmt(deltaNPS) + '</span>' +
    '<span class="cd-sep">|</span>' +
    '<span class="cd-excl ' + cls(deltaExcl) + '">&#916; Excl: ' + fmt(deltaExcl) + '</span>';
  const wrap = el.closest('.chart-container');
  if (wrap) wrap.insertAdjacentElement('afterend', div);
}

function showTab(id, btn) {'''
html = html.replace(old_show, new_show, 1)

# ── 3. CSS para chart-delta ──────────────────────────────────
old_css = '/* ── EXCL VOLUME ── */'
new_css = '''/* ── CHART DELTA ── */
.chart-delta { display:flex; gap:12px; padding:5px 4px 0; font-size:11px; font-weight:700; flex-wrap:wrap; }
.chart-delta .cd-sep { color:#ccc; }
.cd-nps { color:var(--green); }
.cd-nps.neg { color:var(--red); }
.cd-excl { color:#ff7733; }
.cd-excl.neg { color:var(--red); }
/* ── EXCL VOLUME ── */'''
html = html.replace(old_css, new_css, 1)

# ── 4. makeCorrelChart: datalabels + variação ────────────────
old_fn = '''function makeCorrelChart(canvasId, npsData, exclData, npsMin, npsMax, exclMin, exclMax) {
  if (!document.getElementById(canvasId)) return;
  new Chart(document.getElementById(canvasId), {
    type: 'bar',

    data: {
      labels: ['Abril', 'Maio'],
      datasets: [
        {
          type: 'bar',
          label: 'NPS Lineal (%)',
          data: npsData,
          backgroundColor: ['rgba(52,131,250,0.75)', 'rgba(0,166,80,0.8)'],
          borderRadius: 8,
          yAxisID: 'yNPS',
          order: 2,
          barPercentage: 0.5
        },
        {
          type: 'line',
          label: 'Taxa de Exclusão (%)',
          data: exclData,
          borderColor: '#ff7733',
          backgroundColor: 'rgba(255,119,51,0.08)',
          pointBackgroundColor: '#ff7733',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 7,
          pointHoverRadius: 9,
          borderWidth: 2.5,
          fill: true,
          tension: 0.3,
          yAxisID: 'yExcl',
          order: 1
        }
      ]
    },'''
new_fn = '''function makeCorrelChart(canvasId, npsData, exclData, npsMin, npsMax, exclMin, exclMax) {
  if (!document.getElementById(canvasId)) return;
  new Chart(document.getElementById(canvasId), {
    type: 'bar',
    data: {
      labels: ['Abril', 'Maio'],
      datasets: [
        {
          type: 'bar',
          label: 'NPS Lineal (%)',
          data: npsData,
          backgroundColor: ['rgba(52,131,250,0.75)', 'rgba(0,166,80,0.8)'],
          borderRadius: 8,
          yAxisID: 'yNPS',
          order: 2,
          barPercentage: 0.5,
          datalabels: { display:true, anchor:'center', align:'center', color:'#fff', font:{size:11,weight:'800'}, formatter:v=>v!=null?v.toFixed(1)+'%':'' }
        },
        {
          type: 'line',
          label: 'Taxa de Exclusão (%)',
          data: exclData,
          borderColor: '#ff7733',
          backgroundColor: 'rgba(255,119,51,0.08)',
          pointBackgroundColor: '#ff7733',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 7,
          pointHoverRadius: 9,
          borderWidth: 2.5,
          fill: true,
          tension: 0.3,
          yAxisID: 'yExcl',
          order: 1,
          datalabels: { display:true, anchor:'center', align:'right', offset:8, color:'#ff7733', backgroundColor:'rgba(26,26,46,.82)', borderRadius:3, padding:{top:2,bottom:2,left:4,right:4}, font:{size:10,weight:'700'}, formatter:v=>v!=null?v.toFixed(1)+'%':'' }
        }
      ]
    },'''
html = html.replace(old_fn, new_fn, 1)

# Adicionar addChartDelta após makeCorrelChart calls
old_calls = '''// ── Chart 8a: Correlação — Reputación ──
makeCorrelChart('chartCorrRep',   [69.7, 76.7], [65, 68], 60, 85, 58, 76);

// ── Chart 8b: Correlação — Reputación ME ──
makeCorrelChart('chartCorrRepME', [82.6, 86.8], [80, 84], 75, 92, 73, 90);'''
new_calls = '''// ── Chart 8a: Correlação — Reputación ──
makeCorrelChart('chartCorrRep',   [69.7, 76.7], [65, 68], 60, 85, 58, 76);
addChartDelta('chartCorrRep', 76.7-69.7, 68-65);

// ── Chart 8b: Correlação — Reputación ME ──
makeCorrelChart('chartCorrRepME', [82.6, 86.8], [80, 84], 75, 92, 73, 90);
addChartDelta('chartCorrRepME', 86.8-82.6, 84-80);'''
html = html.replace(old_calls, new_calls, 1)

# ── 5. makeTeamChart: datalabels + variação ──────────────────
old_team_bar = '''          data:[npsAbr, npsMai],
          backgroundColor:['rgba(52,131,250,0.75)','rgba(0,166,80,0.8)'],
          borderRadius:8, barPercentage:0.5, yAxisID:'yNPS', order:2 },'''
new_team_bar = '''          data:[npsAbr, npsMai],
          backgroundColor:['rgba(52,131,250,0.75)','rgba(0,166,80,0.8)'],
          borderRadius:8, barPercentage:0.5, yAxisID:'yNPS', order:2,
          datalabels:{ display:true, anchor:'center', align:'center', color:'#fff', font:{size:10,weight:'800'}, formatter:v=>v!=null?v.toFixed(1)+'%':'' } },'''
html = html.replace(old_team_bar, new_team_bar, 1)

old_team_line = '''          yAxisID:'yExcl', order:1 }'''
new_team_line = '''          yAxisID:'yExcl', order:1,
          datalabels:{ display:true, anchor:'center', align:'right', offset:8, color:'#ff7733', backgroundColor:'rgba(26,26,46,.82)', borderRadius:3, padding:2, font:{size:9,weight:'700'}, formatter:v=>v!=null?v.toFixed(1)+'%':'' } }'''
html = html.replace(old_team_line, new_team_line, 1)

# Adicionar addChartDelta após makeTeamChart calls
def add_delta_after_team(html, cid, nps_abr, nps_mai, excl_abr, excl_mai):
    old = f"makeTeamChart('{cid}',"
    pos = html.find(old)
    if pos == -1: return html
    end = html.find(';', pos) + 1
    delta_nps = round(nps_mai - nps_abr, 1)
    delta_excl = round(excl_mai - excl_abr, 1)
    insert = f"\naddChartDelta('{cid}', {delta_nps}, {delta_excl});"
    return html[:end] + insert + html[end:]

team_data = [
    ('ct_me_rep',    71.8, 75.4, 71.8, 72.7),
    ('ct_me_repme',  79.4, 85.7, 88.5, 92.5),
    ('ct_ven_rep',   68.5, 71.2, 67.7, 69.7),
    ('ct_ven_repme', 88.9, 90.4, 90.4, 94.5),
    ('ct_pub_rep',   76.3, 80.8, 68.6, 74.9),
    ('ct_pub_repme', 74.8, 86.8, 85.3, 87.4),
]
for cid, na, nm, ea, em in team_data:
    html = add_delta_after_team(html, cid, na, nm, ea, em)

# ── 6. makeGrupoChart: datalabels nas barras ─────────────────
old_grupo_ds = '''        { type:'bar',  label:'NPS Abr', data:npsAbr,  backgroundColor:G_CORES.map(c=>c.replace('0.8','0.55').replace('0.75','0.55').replace('0.7','0.55')),
            borderRadius:5, yAxisID:'y', order:2, datalabels: DL_GRP },
          { type:'bar',  label:'NPS Mai', data:npsMai,  backgroundColor: G_CORES,
            borderRadius:5, yAxisID:'y', order:2, datalabels: DL_GRP }'''
# Try finding without DL_GRP
old_grupo_ds2 = '''        { type:'bar',  label:'NPS Abr', data:npsAbr,  backgroundColor:G_CORES.map(c=>c.replace('0.8','0.55').replace('0.75','0.55').replace('0.7','0.55')),
            borderRadius:5, yAxisID:'y', order:2 },
          { type:'bar',  label:'NPS Mai', data:npsMai,  backgroundColor: G_CORES,
            borderRadius:5, yAxisID:'y', order:2 }'''
new_grupo_ds = '''        { type:'bar',  label:'NPS Abr', data:npsAbr,  backgroundColor:G_CORES.map(c=>c.replace('0.8','0.55').replace('0.75','0.55').replace('0.7','0.55')),
            borderRadius:5, yAxisID:'y', order:2,
            datalabels:{ display:true, anchor:'end', align:'start', offset:3, color:'#fff', font:{size:9,weight:'800'}, formatter:v=>v!=null?v.toFixed(0)+'%':'' } },
          { type:'bar',  label:'NPS Mai', data:npsMai,  backgroundColor: G_CORES,
            borderRadius:5, yAxisID:'y', order:2,
            datalabels:{ display:true, anchor:'end', align:'start', offset:3, color:'#fff', font:{size:9,weight:'800'}, formatter:v=>v!=null?v.toFixed(0)+'%':'' } }'''
if old_grupo_ds in html:
    html = html.replace(old_grupo_ds, new_grupo_ds, 1)
elif old_grupo_ds2 in html:
    html = html.replace(old_grupo_ds2, new_grupo_ds, 1)

# ── 7. chartDecomp: datalabels nos segmentos ────────────────
old_decomp_dl = '''          formatter: v => '+'+v.toFixed(1)+'pp' }
      },
      {
        type:'bar',  label:'Efeito Experiência (NETO*)','''
new_decomp_dl = '''          formatter: v => '+'+v.toFixed(1)+'pp',
          display: true }
      },
      {
        type:'bar',  label:'Efeito Experiência (NETO*)','''
html = html.replace(old_decomp_dl, new_decomp_dl, 1)

# Segunda ocorrência (NETO dataset)
old_decomp_dl2 = '''          formatter: v => '+'+v.toFixed(1)+'pp' }
      }
    ]'''
new_decomp_dl2 = '''          formatter: v => '+'+v.toFixed(1)+'pp',
          display: true }
      }
    ]'''
html = html.replace(old_decomp_dl2, new_decomp_dl2, 1)

with open('C:/claudinho/reputacion_longtail_abr_mai_2026.html', 'w', encoding='utf-8') as f:
    f.write(html)
shutil.copy('C:/claudinho/reputacion_longtail_abr_mai_2026.html',
            'C:/claudinho/reputacion_lt_v2.html')
print(f'Salvo: {len(html)} chars')
