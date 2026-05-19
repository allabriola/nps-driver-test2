import json, math

# ═══════════════════════════════════════════════════════════════════════
# DADOS  (coletados do BigQuery em 19/05/2026)
# ═══════════════════════════════════════════════════════════════════════

# ── Labels ──────────────────────────────────────────────────────────────
MONTH_LABELS = ['Jan','Fev','Mar','Abr','Mai*']
MONTHS       = ['2026-01','2026-02','2026-03','2026-04','2026-05']
WEEK_LABELS  = ['30/03','06/04','13/04','20/04','27/04','04/05','11/05','18/05*']

# ── NPS Mensal (Mar,Abr,Mai - NaN para Jan/Fev) ─────────────────────────
# Geral (treatment_all vs control_all)
NPS_M = {
    'treatment_all': [None, None, 49.2, 64.2, 70.0],
    'control_all':   [None, None, 61.4, 53.9, 57.0],  # mai: 56.1 (expert-only) ~57
}
# Expert
NPS_M_E = {
    'treatment': [None, None, 47.1, 71.4, 74.1],
    'control':   [None, None, 61.4, 53.8, 56.1],
}
# Newbie (control = baseline expert pois sem split controle)
NPS_M_N = {
    'treatment': [None, None, 51.7, 56.7, 66.9],
    'control':   [None, None, 61.4, 53.8, 56.1],
}

# ── NPS Semanal ──────────────────────────────────────────────────────────
NPS_W = {
    'treatment_all': [65.9, 59.9, 59.5, 67.7, 69.6, 69.5, 71.7, 73.2],
    'control_all':   [57.5, 56.0, 53.2, 53.1, 50.4, 54.9, 59.2, 57.4],
}
NPS_W_E = {
    'treatment': [67.1, 69.7, 71.7, 72.9, 72.7, 75.4, 74.5, 69.1],
    'control':   [57.3, 55.9, 53.2, 53.1, 50.2, 54.7, 59.2, 57.4],
}
NPS_W_N = {
    'treatment': [64.6, 45.7, 48.3, 63.3, 67.0, 62.6, 68.7, 76.7],
    'control':   [57.3, 55.9, 53.2, 53.1, 50.2, 54.7, 59.2, 57.4],
}

# ── TMO Mensal (min, Jan-Mai) ─────────────────────────────────────────────
TMO_M = {
    'treatment_all': [30.0, 29.9, 34.7, 38.8, 40.2],  # jan~avg expert (only exp jan/feb)
    'control_all':   [26.4, 25.2, 29.7, 31.3, 29.8],
}
TMO_M_E = {
    'treatment': [30.6, 29.9, 33.1, 33.5, 35.6],
    'control':   [26.4, 25.2, 29.6, 31.3, 30.4],
}
TMO_M_N = {
    'treatment': [None, 25.3, 37.4, 39.2, 39.0],
    'control':   [26.4, 25.2, 29.6, 31.3, 30.4],
}

# ── TMO Semanal ──────────────────────────────────────────────────────────
TMO_W = {
    'treatment_all': [31.6, 36.8, 38.6, 39.1, 39.4, 40.4, 38.0, 38.0],
    'control_all':   [28.3, 31.1, 30.8, 30.7, 29.9, 30.2, 30.5, 28.2],
}
TMO_W_E = {
    'treatment': [29.8, 33.4, 33.1, 33.3, 33.7, 34.8, 36.2, 34.8],
    'control':   [28.3, 31.0, 30.8, 30.6, 29.8, 30.2, 30.5, 28.2],
}
TMO_W_N = {
    'treatment': [33.9, 37.6, 39.2, 38.7, 38.4, 38.3, 39.5, 39.5],
    'control':   [28.3, 31.0, 30.8, 30.6, 29.8, 30.2, 30.5, 28.2],
}

# ── Produtividade Mensal (at/h) ─────────────────────────────────────────
PROD_M = {
    'treatment_all': [1.12, 1.40, 1.15, 1.06, 1.10],
    'control_all':   [1.31, 1.61, 1.39, 1.24, 1.31],
}
PROD_M_E = {
    'treatment': [1.12, 1.40, 1.16, 1.03, 1.07],
    'control':   [1.31, 1.61, 1.39, 1.24, 1.31],
}
PROD_M_N = {
    'treatment': [None, 1.54, 1.07, 1.08, 1.12],
    'control':   [1.31, 1.61, 1.39, 1.24, 1.31],
}

# ── Produtividade Semanal ─────────────────────────────────────────────────
PROD_W = {
    'treatment_all': [0.98, 0.87, 1.09, 1.17, 1.16, 1.07, 1.08, 1.11],
    'control_all':   [1.11, 1.10, 1.30, 1.37, 1.31, 1.25, 1.31, 1.32],
}
PROD_W_E = {
    'treatment': [0.98, 0.87, 1.09, 1.14, 1.14, 1.03, 1.06, 1.12],
    'control':   [1.11, 1.10, 1.30, 1.37, 1.32, 1.25, 1.31, 1.32],
}
PROD_W_N = {
    'treatment': [0.97, 0.88, 1.07, 1.18, 1.16, 1.09, 1.10, 1.10],
    'control':   [1.11, 1.10, 1.30, 1.37, 1.32, 1.25, 1.31, 1.32],
}

# ── TDI Mensal (Abr,Mai - NaN para Jan-Mar) ─────────────────────────────
TDI_M = {
    'treatment_all': [None, None, None, 8.7,  6.2],  # weighted avg exp+newbie
    'control_all':   [None, None, None, 8.2,  7.2],
}
TDI_M_E = {
    'treatment': [None, None, None, 6.9, 4.8],
    'control':   [None, None, None, 8.2, 7.2],
}
TDI_M_N = {
    'treatment': [None, None, None, 11.5, 7.3],
    'control':   [None, None, None, 8.2,  7.2],
}

# ── TDI Semanal (sem 23/Mar onward, mas TDI só existe a partir de Mar-30 real)
# Usando semanas de 30/03 para consistência
TDI_W = {
    'treatment_all': [6.3, 7.0, 9.1, 12.3, 8.7, 4.6, 7.0, 4.5],
    'control_all':   [7.6, 7.7, 8.1, 8.6,  8.6, 7.7, 7.4, 4.1],
}
TDI_W_E = {
    'treatment': [5.4, 6.3, 5.8, 10.2, 7.0, 3.7, 5.6, 5.2],
    'control':   [7.6, 7.7, 8.1, 8.6,  8.6, 7.7, 7.4, 4.1],
}
TDI_W_N = {
    'treatment': [7.7, 8.1, 12.4, 14.9, 11.0, 5.8, 8.6, 3.2],
    'control':   [7.6, 7.7, 8.1,  8.6,  8.6,  7.7, 7.4, 4.1],
}

# ── Recontato Mensal (%) ─────────────────────────────────────────────────
REC_M = {
    'treatment_all': [None, None, 22.5, 4.8,  3.2],
    'control_all':   [None, None, 18.9, 4.1,  2.5],
}
REC_M_E = {
    'treatment': [None, None, 20.9, 4.1, 2.8],
    'control':   [None, None, 18.9, 4.1, 2.5],
}
REC_M_N = {
    'treatment': [None, None, 24.7, 5.5, 3.7],
    'control':   [None, None, 18.9, 4.1, 2.5],
}

# ── Recontato Semanal (excl. semana 23/Mar que é ruidosa) ────────────────
REC_W = {
    'treatment_all': [6.3, 4.9, 4.9, 4.5, 4.2, 4.0, 2.6, 0.5],
    'control_all':   [6.0, 4.6, 4.3, 3.5, 2.6, 3.1, 2.2, 0.2],
}
REC_W_E = {
    'treatment': [5.2, 3.8, 4.2, 3.9, 3.9, 3.7, 2.2, 0.4],
    'control':   [6.0, 4.6, 4.3, 3.5, 2.6, 3.1, 2.2, 0.2],
}
REC_W_N = {
    'treatment': [7.8, 6.3, 5.7, 5.2, 4.8, 4.4, 3.0, 0.6],
    'control':   [6.0, 4.6, 4.3, 3.5, 2.6, 3.1, 2.2, 0.2],
}

# ── TMO por Processo ──────────────────────────────────────────────────────
PROC_NAMES = {
    81:   'Reputación',
    683:  'Post Compra Funcionalidades',
    1647: 'Reversa',
    1660: 'Asignación ME Sellers LT',
    1797: 'Drivers',
    1813: 'Despacho Vendas e Publicaciones',
    1814: 'Reputación ME',
    1816: 'Gestiones Operativas',
    2358: 'Places Kangu',
    2570: 'Viaje del paquete - Vendedor',
}
# {proc_id: {'com': (tmo, casos), 'sem': (tmo, casos)}}
PROC_TMO = {
    81:   {'com': (39.8, 347),   'sem': (32.6, 7688)},
    683:  {'com': (40.2, 743),   'sem': (36.1, 11624)},
    1647: {'com': (36.5, 572),   'sem': (38.9, 9732)},
    1660: {'com': (41.1, 144),   'sem': (34.6, 1458)},
    1797: {'com': (40.0, 1246),  'sem': (40.4, 14548)},
    1813: {'com': (41.2, 2428),  'sem': (40.2, 33936)},
    1814: {'com': (35.4, 210),   'sem': (32.0, 4514)},
    1816: {'com': (39.4, 631),   'sem': (36.5, 7438)},
    2358: {'com': (38.3, 853),   'sem': (39.7, 9065)},
    2570: {'com': (38.9, 277),   'sem': (37.6, 3646)},
}

# ── Reps individuais ─────────────────────────────────────────────────────
with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_rep_data_me.json', encoding='utf-8') as f:
    REPS_RAW = json.load(f)

# Corrigir pct_utilizacao = conversas_cop / total_casos * 100
for r in REPS_RAW:
    cc = int(r.get('conversas_cop') or 0)
    tc = int(r.get('total_casos') or 0)
    r['pct_utilizacao'] = round(cc/tc*100, 1) if tc > 0 else 0.0

# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════

def jnull(lst):
    return json.dumps([x if x is not None else 'null' for x in lst]).replace('"null"','null')

def fmt_nps(v):
    if v is None: return '<span class="sd">—</span>'
    v = float(v)
    cls = 'gc' if v >= 65 else ('yc' if v >= 50 else 'rc')
    return f'<span class="{cls}">{v:.1f}%</span>'

def delta_pp(t, c):
    if t is None or c is None: return ''
    d = round(t - c, 1)
    cls = 'pos' if d > 0 else ('neg' if d < 0 else 'neu')
    sign = '+' if d > 0 else ''
    return f'<span class="dlt {cls}">{sign}{d}pp</span>'

def delta_pct_rel(t, c, reverse=False):
    if t is None or c is None or c == 0: return ''
    d = round((t - c) / c * 100, 1)
    better = d < 0 if reverse else d > 0
    cls = 'pos' if better else ('neg' if not better else 'neu')
    sign = '+' if d > 0 else ''
    return f'<span class="dlt {cls}">{sign}{d}%</span>'

def sc(label, t, c, mode='nps'):
    if t is None: return ''
    tv = f'{t:.1f}%' if mode=='nps' else (f'{t:.1f} min' if mode=='tmo' else f'{t:.2f}')
    cv = f'{c:.1f}%' if mode=='nps' else (f'{c:.1f} min' if mode=='tmo' else f'{c:.2f}')
    d  = delta_pp(t,c) if mode=='nps' else (delta_pct_rel(t,c,reverse=True) if mode=='tmo' else delta_pct_rel(t,c))
    return f'''<div class="kc"><div class="lbl">{label}</div>
<div class="val">{tv}</div><div class="cmp">Controle: {cv}</div>{d}</div>'''

def build_tab_content(suffix, nps_m, tmo_m, prod_m, tdi_m, rec_m,
                      nps_w, tmo_w, prod_w, tdi_w, rec_w,
                      note=''):
    key_t = 'treatment' if suffix != 'geral' else 'treatment_all'
    key_c = 'control'   if suffix != 'geral' else 'control_all'
    t_nps_m  = nps_m[key_t];  c_nps_m  = nps_m[key_c]
    t_tmo_m  = tmo_m[key_t];  c_tmo_m  = tmo_m[key_c]
    t_prod_m = prod_m[key_t]; c_prod_m = prod_m[key_c]
    t_tdi_m  = tdi_m[key_t];  c_tdi_m  = tdi_m[key_c]
    t_rec_m  = rec_m[key_t];  c_rec_m  = rec_m[key_c]
    t_nps_w  = nps_w[key_t];  c_nps_w  = nps_w[key_c]
    t_tmo_w  = tmo_w[key_t];  c_tmo_w  = tmo_w[key_c]
    t_prod_w = prod_w[key_t]; c_prod_w = prod_w[key_c]
    t_tdi_w  = tdi_w[key_t];  c_tdi_w  = tdi_w[key_c]
    t_rec_w  = rec_w[key_t];  c_rec_w  = rec_w[key_c]

    # Scorecard Abr e Mai
    sc_abr = ''.join([
        sc('NPS ↑',         t_nps_m[3],  c_nps_m[3],  'nps'),
        sc('TMO ↓',         t_tmo_m[3],  c_tmo_m[3],  'tmo'),
        sc('Produtividade ↑',t_prod_m[3], c_prod_m[3], 'prod'),
        sc('TDI ↓',         t_tdi_m[3],  c_tdi_m[3],  'nps'),
        sc('Recontato ↓',   t_rec_m[3],  c_rec_m[3],  'nps'),
    ])
    sc_mai = ''.join([
        sc('NPS ↑',          t_nps_m[4],  c_nps_m[4],  'nps'),
        sc('TMO ↓',          t_tmo_m[4],  c_tmo_m[4],  'tmo'),
        sc('Produtividade ↑', t_prod_m[4], c_prod_m[4], 'prod'),
        sc('TDI ↓',          t_tdi_m[4],  c_tdi_m[4],  'nps'),
        sc('Recontato ↓',    t_rec_m[4],  c_rec_m[4],  'nps'),
    ])

    scorecards_html = ''

    sid = suffix
    return f'''
{"<div class='note warn'>" + note + "</div>" if note else ""}
{scorecards_html}

<div class="section-lbl">Evolução Mensal — Jan a Mai/2026</div>
<div class="ch-grid-5">
  <div class="cc"><h3>NPS ↑</h3><p>% · Maior é melhor · Mar–Mai (Jan/Fev sem dados p/ este time)</p><canvas id="mNPS_{sid}"></canvas></div>
  <div class="cc"><h3>TMO ↓</h3><p>min · Menor é melhor</p><canvas id="mTMO_{sid}"></canvas></div>
  <div class="cc"><h3>Produtividade ↑</h3><p>at/h · Maior é melhor</p><canvas id="mPROD_{sid}"></canvas></div>
  <div class="cc"><h3>TDI ↓</h3><p>% · Menor é melhor · Apenas Abr–Mai disponíveis</p><canvas id="mTDI_{sid}"></canvas></div>
  <div class="cc"><h3>Recontato ↓</h3><p>% · Menor é melhor · A partir de Mar</p><canvas id="mREC_{sid}"></canvas></div>
</div>

<div class="section-lbl">Evolução Semanal — 8 Semanas (30/03–18/05)</div>
<div class="ch-grid-5">
  <div class="cc"><h3>NPS ↑</h3><p>%</p><canvas id="wNPS_{sid}"></canvas></div>
  <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="wTMO_{sid}"></canvas></div>
  <div class="cc"><h3>Produtividade ↑</h3><p>at/h</p><canvas id="wPROD_{sid}"></canvas></div>
  <div class="cc"><h3>TDI ↓</h3><p>%</p><canvas id="wTDI_{sid}"></canvas></div>
  <div class="cc"><h3>Recontato ↓</h3><p>%</p><canvas id="wREC_{sid}"></canvas></div>
</div>

<script>
(function(){{
const BLUE='{{"#2563EB"}}',GRAY='{{"#9CA3AF"}}',ORANGE='{{"#F59E0B"}}';
const MONTHS={json.dumps(MONTH_LABELS)};
const WEEKS={json.dumps(WEEK_LABELS)};
function mk(id,labels,ds,yLabel,yMin,yMax){{
  new Chart(document.getElementById(id),{{type:'line',data:{{labels,datasets:ds}},options:{{
    responsive:true,maintainAspectRatio:true,aspectRatio:1.55,
    plugins:{{legend:{{position:'bottom',labels:{{font:{{size:10}},padding:8,usePointStyle:true,pointStyleWidth:6}}}},
      tooltip:{{callbacks:{{label:c=>c.parsed.y==null?null:` ${{c.dataset.label}}: ${{c.parsed.y.toFixed(1)}} ${{yLabel}}`}}}}}},
    scales:{{y:{{min:yMin,max:yMax,grid:{{color:'#f1f5f9'}},ticks:{{font:{{size:10}}}}}},x:{{grid:{{display:false}},ticks:{{font:{{size:10}}}}}}}}
  }}}});
}}
function d(data,color,label,dashed){{return {{label,data,borderColor:color,backgroundColor:color+'18',
  borderWidth:dashed?2:2.5,pointRadius:4,tension:0.35,spanGaps:true,borderDash:dashed?[6,4]:[]}}}}

// Mensais
mk('mNPS_{sid}',MONTHS,[d({jnull(t_nps_m)},'#2563EB','Com Copiloto'),d({jnull(c_nps_m)},'#9CA3AF','Sem Copiloto',true)],'%',40,85);
mk('mTMO_{sid}',MONTHS,[d({jnull(t_tmo_m)},'#2563EB','Com Copiloto'),d({jnull(c_tmo_m)},'#9CA3AF','Sem Copiloto',true)],'min',22,45);
mk('mPROD_{sid}',MONTHS,[d({jnull(t_prod_m)},'#2563EB','Com Copiloto'),d({jnull(c_prod_m)},'#9CA3AF','Sem Copiloto',true)],'at/h',0.8,1.8);
mk('mTDI_{sid}',MONTHS,[d({jnull(t_tdi_m)},'#2563EB','Com Copiloto'),d({jnull(c_tdi_m)},'#9CA3AF','Sem Copiloto',true)],'%',2,16);
mk('mREC_{sid}',MONTHS,[d({jnull(t_rec_m)},'#2563EB','Com Copiloto'),d({jnull(c_rec_m)},'#9CA3AF','Sem Copiloto',true)],'%',0,30);

// Semanais
mk('wNPS_{sid}',WEEKS,[d({jnull(t_nps_w)},'#2563EB','Com Copiloto'),d({jnull(c_nps_w)},'#9CA3AF','Sem Copiloto',true)],'%',40,85);
mk('wTMO_{sid}',WEEKS,[d({jnull(t_tmo_w)},'#2563EB','Com Copiloto'),d({jnull(c_tmo_w)},'#9CA3AF','Sem Copiloto',true)],'min',24,44);
mk('wPROD_{sid}',WEEKS,[d({jnull(t_prod_w)},'#2563EB','Com Copiloto'),d({jnull(c_prod_w)},'#9CA3AF','Sem Copiloto',true)],'at/h',0.75,1.5);
mk('wTDI_{sid}',WEEKS,[d({jnull(t_tdi_w)},'#2563EB','Com Copiloto'),d({jnull(c_tdi_w)},'#9CA3AF','Sem Copiloto',true)],'%',2,18);
mk('wREC_{sid}',WEEKS,[d({jnull(t_rec_w)},'#2563EB','Com Copiloto'),d({jnull(c_rec_w)},'#9CA3AF','Sem Copiloto',true)],'%',0,10);
}})();
</script>
'''

# ── Tabela de processos ───────────────────────────────────────────────────
def proc_table():
    rows = []
    for pid, nm in sorted(PROC_NAMES.items(), key=lambda x: -(PROC_TMO[x[0]]['com'][1]+PROC_TMO[x[0]]['sem'][1])):
        d = PROC_TMO[pid]
        tmo_com, n_com = d['com']
        tmo_sem, n_sem = d['sem']
        delta = round(tmo_com - tmo_sem, 1)
        cls = 'rc' if delta > 2 else ('gc' if delta < -2 else 'neu-cell')
        sign = '+' if delta > 0 else ''
        rows.append(
            f'<tr><td class="rep-name">{nm}</td>'
            f'<td>{tmo_com:.1f}</td><td class="n-small">{n_com:,}</td>'
            f'<td>{tmo_sem:.1f}</td><td class="n-small">{n_sem:,}</td>'
            f'<td><span class="{cls}">{sign}{delta:.1f} min</span></td></tr>'
        )
    return '\n'.join(rows)

# ── Tabela por representante ──────────────────────────────────────────────
def rep_rows():
    out = []
    for r in REPS_RAW:
        ldap  = r['ldap']
        sen   = r.get('seniority','')
        conv  = int(r.get('conversas_cop',0) or 0)
        pct_u = float(r.get('pct_utilizacao',0) or 0)
        p_abr = int(r.get('pesq_abr',0) or 0)
        n_abr = r.get('nps_abr')
        p_mai = int(r.get('pesq_mai',0) or 0)
        n_mai = r.get('nps_mai')
        sen_badge = '<span class="sen-e">E</span>' if sen=='EXPERT' else '<span class="sen-n">N</span>'
        # % utilização bar
        bar_w = min(pct_u, 100)
        bar_col = '#10b981' if pct_u >= 30 else ('#f59e0b' if pct_u >= 10 else '#ef4444')
        util_cell = (f'<div class="util-bar"><div class="util-fill" style="width:{bar_w}%;background:{bar_col}"></div>'
                     f'</div><span class="util-val">{pct_u:.0f}%</span>')
        abr_cell = f'{fmt_nps(n_abr)} <span class="n-small">({p_abr})</span>' if p_abr else '<span class="sd">—</span>'
        mai_cell = f'{fmt_nps(n_mai)} <span class="n-small">({p_mai})</span>' if p_mai else '<span class="sd">—</span>'
        out.append(
            f'<tr data-sen="{sen}">'
            f'<td class="rep-name">{ldap} {sen_badge}</td>'
            f'<td>{conv}</td>'
            f'<td>{util_cell}</td>'
            f'<td>{abr_cell}</td>'
            f'<td>{mai_cell}</td>'
            f'</tr>'
        )
    return '\n'.join(out)

# ═══════════════════════════════════════════════════════════════════════
# HTML
# ═══════════════════════════════════════════════════════════════════════

geral_html   = build_tab_content('geral',  NPS_M, TMO_M, PROD_M, TDI_M, REC_M, NPS_W, TMO_W, PROD_W, TDI_W, REC_W)
expert_html  = build_tab_content('expert', NPS_M_E, TMO_M_E, PROD_M_E, TDI_M_E, REC_M_E, NPS_W_E, TMO_W_E, PROD_W_E, TDI_W_E, REC_W_E,
                                 note='Experts: NPS superiores desde a ativação (+20pp vs controle em Mai). TDI Expert com Copiloto caiu de 6.9% → 4.8% (Abr→Mai).')
newbie_html  = build_tab_content('newbie', NPS_M_N, TMO_M_N, PROD_M_N, TDI_M_N, REC_M_N, NPS_W_N, TMO_W_N, PROD_W_N, TDI_W_N, REC_W_N,
                                 note='Newbies: NPS crescendo rapidamente (+10pp de Abr→Mai). TDI era alto em Abr (11.5%) mas caiu para 7.3% em Mai. Controle = baseline Expert (sem split de senioridade disponível para o grupo controle).')

html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Copiloto — BR_ME_Sellers_Longtail</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f7;color:#1a1a2e;font-size:13px}}
.header{{background:#1a1a2e;color:white;padding:18px 28px}}
.header h1{{font-size:17px;font-weight:700}}
.header .sub{{font-size:11px;color:#94a3b8;margin-top:3px}}
.container{{max-width:1400px;margin:0 auto;padding:16px 14px 40px}}
/* Tabs */
.tabs{{display:flex;gap:4px;margin-bottom:16px;background:white;padding:5px;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.07);width:fit-content}}
.tab-btn{{padding:6px 22px;border-radius:7px;border:none;cursor:pointer;font-size:12px;font-weight:600;background:transparent;color:#64748b;transition:.15s}}
.tab-btn.active{{background:#1d4ed8;color:white}}
.tab-pane{{display:none}}.tab-pane.active{{display:block}}
/* Legend */
.legend{{display:flex;gap:16px;align-items:center;margin-bottom:12px;flex-wrap:wrap}}
.leg{{display:flex;align-items:center;gap:5px;font-size:11px;color:#374151}}
.leg-solid{{width:20px;height:0;border-top:2.5px solid}}
.leg-dash{{width:20px;height:0;border-top:2.5px dashed}}
/* Sections */
.section-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#94a3b8;margin:20px 0 8px;padding-top:8px;border-top:1px solid #e2e8f0}}
.period-label{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#94a3b8;margin:10px 0 6px}}
/* Scorecards */
.sc-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:8px}}
.kc{{background:white;border-radius:9px;padding:10px 12px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.kc .lbl{{font-size:9px;text-transform:uppercase;letter-spacing:.5px;color:#94a3b8;font-weight:600;margin-bottom:5px}}
.kc .val{{font-size:18px;font-weight:800;color:#1d4ed8;line-height:1}}
.kc .cmp{{font-size:10px;color:#94a3b8;margin-top:3px}}
.dlt{{font-size:10px;font-weight:600;padding:1px 6px;border-radius:4px;margin-top:5px;display:inline-block}}
.pos{{background:#dcfce7;color:#15803d}}.neg{{background:#fee2e2;color:#dc2626}}.neu{{background:#f1f5f9;color:#64748b}}
/* Charts 5-col */
.ch-grid-5{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:8px}}
.cc{{background:white;border-radius:9px;padding:12px 14px 10px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.cc h3{{font-size:11px;font-weight:700;color:#1e293b}}
.cc p{{font-size:9.5px;color:#94a3b8;margin:2px 0 8px}}
/* TMO processo table */
.proc-table-wrap{{margin-top:8px;overflow-x:auto}}
table.rt{{width:100%;border-collapse:collapse;font-size:11px}}
table.rt th{{background:#1a1a2e;color:white;padding:6px 9px;text-align:center;font-size:10px;font-weight:600;letter-spacing:.2px;white-space:nowrap}}
table.rt th.left{{text-align:left}}
table.rt td{{padding:4px 8px;border-bottom:1px solid #f1f5f9;text-align:center;white-space:nowrap}}
table.rt td.rep-name{{text-align:left;font-weight:600;font-size:10.5px;color:#1e293b}}
table.rt tr:hover td{{background:#f8fafc}}
/* Colors */
.gc{{background:#dcfce7;color:#15803d;font-weight:700;padding:1px 5px;border-radius:3px;font-size:10.5px}}
.yc{{background:#fef9c3;color:#854d0e;font-weight:700;padding:1px 5px;border-radius:3px;font-size:10.5px}}
.rc{{background:#fee2e2;color:#dc2626;font-weight:700;padding:1px 5px;border-radius:3px;font-size:10.5px}}
.neu-cell{{background:#f1f5f9;color:#64748b;font-weight:600;padding:1px 5px;border-radius:3px;font-size:10.5px}}
.sd{{color:#cbd5e1;font-style:italic}}
.n-small{{font-size:9px;color:#94a3b8}}
.sen-e{{background:#dbeafe;color:#1d4ed8;font-size:8px;font-weight:700;padding:1px 3px;border-radius:2px;margin-left:2px}}
.sen-n{{background:#fef9c3;color:#854d0e;font-size:8px;font-weight:700;padding:1px 3px;border-radius:2px;margin-left:2px}}
/* Utilização bar */
.util-bar{{display:inline-block;width:50px;height:6px;background:#e2e8f0;border-radius:3px;vertical-align:middle;margin-right:4px}}
.util-fill{{height:6px;border-radius:3px}}
.util-val{{font-size:10.5px;color:#374151;font-weight:600}}
/* Notes */
.note{{font-size:10.5px;color:#94a3b8;background:white;padding:8px 12px;border-radius:7px;border-left:3px solid #e2e8f0;margin-top:8px;line-height:1.6}}
.note strong{{color:#64748b}}
.note.warn{{border-left-color:#f59e0b;background:#fffbeb}}.note.warn strong{{color:#92400e}}
hr.div{{border:none;border-top:2px solid #e2e8f0;margin:20px 0}}
.footer{{font-size:10px;color:#94a3b8;text-align:center;margin-top:24px}}
/* Sen filter buttons */
.sen-filter{{display:flex;gap:6px;margin-bottom:10px;align-items:center}}
.sen-btn{{padding:4px 14px;border-radius:6px;border:1px solid #e2e8f0;cursor:pointer;font-size:11px;font-weight:600;background:white;color:#64748b;transition:.1s}}
.sen-btn.active{{background:#1d4ed8;color:white;border-color:#1d4ed8}}
@media(max-width:1100px){{.sc-grid{{grid-template-columns:repeat(3,1fr)}}.ch-grid-5{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:700px){{.sc-grid{{grid-template-columns:repeat(2,1fr)}}.ch-grid-5{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="header">
  <h1>Copiloto — Experimento Treatment vs Control · BR_ME_Sellers_Longtail</h1>
  <div class="sub">209 reps com Copilot vs ~436 sem Copilot · Rollout iniciado ~22/04/2026 · Atualizado em <span id="ts"></span></div>
</div>

<div class="container">

  <div class="legend">
    <div class="leg"><span class="leg-solid" style="border-color:#2563EB"></span>Com Copiloto (Treatment)</div>
    <div class="leg"><span class="leg-dash" style="border-color:#9CA3AF"></span>Sem Copiloto (Controle)</div>
    <div class="leg" style="font-size:10px;color:#94a3b8">* Mai até 18/05 · NPS com &lt;5 pesquisas/rep tem alta variância · Controle não tem split de senioridade (exibe Expert como baseline)</div>
  </div>

  <!-- TABS -->
  <div class="tabs">
    <button class="tab-btn active" onclick="setTab('geral',this)">Geral</button>
    <button class="tab-btn" onclick="setTab('expert',this)">Expert</button>
    <button class="tab-btn" onclick="setTab('newbie',this)">Newbie</button>
  </div>

  <div class="tab-pane active" id="tab-geral">{geral_html}</div>
  <div class="tab-pane" id="tab-expert">{expert_html}</div>
  <div class="tab-pane" id="tab-newbie">{newbie_html}</div>

  <hr class="div">

  <!-- TMO POR PROCESSO -->
  <div class="section-lbl">TMO por Processo — Com Copiloto vs Sem Copiloto (Abr–Mai 2026 · Treatment reps)</div>
  <div class="note" style="margin-bottom:8px">Comparação do TMO médio por caso para os mesmos reps (treatment), separando interações onde o Copiloto foi acionado (FLAG_COPILOT=1) das que não foram. Delta positivo = Copiloto aumenta TMO naquele processo.</div>
  <div class="proc-table-wrap">
    <table class="rt">
      <thead>
        <tr>
          <th class="left">Processo</th>
          <th>TMO c/ Copiloto</th><th class="n-small">Casos</th>
          <th>TMO s/ Copiloto</th><th class="n-small">Casos</th>
          <th>Delta</th>
        </tr>
      </thead>
      <tbody>{proc_table()}</tbody>
    </table>
  </div>

  <hr class="div">

  <!-- TABELA POR REP -->
  <div class="section-lbl">Representantes com Copiloto — 209 reps · Filtro por Senioridade</div>
  <div class="note" style="margin-bottom:8px">
    <strong>% Utilização:</strong> conversas Copilot / total casos atendidos (Abr–Mai) ·
    <strong>NPS:</strong> verde ≥65% · amarelo 50–65% · vermelho &lt;50% · (n) = pesquisas ·
    <span class="sen-e">E</span> Expert &nbsp; <span class="sen-n">N</span> Newbie
  </div>
  <div class="sen-filter">
    <span style="font-size:11px;font-weight:600;color:#64748b">Filtrar:</span>
    <button class="sen-btn active" onclick="filterSen('ALL',this)">Todos</button>
    <button class="sen-btn" onclick="filterSen('EXPERT',this)">Expert</button>
    <button class="sen-btn" onclick="filterSen('NEWBIE',this)">Newbie</button>
    <input id="rep-search" type="text" placeholder="Buscar LDAP..." style="padding:4px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:11px;margin-left:8px;">
  </div>
  <div class="proc-table-wrap">
    <table class="rt" id="rep-table">
      <thead>
        <tr>
          <th class="left">Representante</th>
          <th>Conversas Copilot</th>
          <th style="min-width:110px">% Utilização</th>
          <th>NPS Abril</th>
          <th>NPS Maio*</th>
        </tr>
      </thead>
      <tbody>{rep_rows()}</tbody>
    </table>
  </div>
  <div class="note" style="margin-top:8px">Reps sem NPS: sem pesquisas respondidas no período (ex: filas sem survey, treinamento). Ordenado por volume de conversas Copilot.</div>

  <div class="footer">Gerado em <span id="ts2"></span> · Fonte: BT_CX_COPILOT_METRICS · DM_CX_NPS_Y20_DETAIL · BT_CX_CXCOPILOT_TMO · BT_CX_TDI · BT_CX_BASIC_CS_RECONTACTS · BR_ME_Sellers_Longtail</div>
</div>

<script>
// Tabs
document.getElementById('ts').textContent = new Date().toLocaleDateString('pt-BR');
document.getElementById('ts2').textContent = document.getElementById('ts').textContent;

function setTab(id, btn) {{
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  btn.classList.add('active');
}}

// Seniority filter + search
function filterSen(sen, btn) {{
  document.querySelectorAll('.sen-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const q = document.getElementById('rep-search').value.toLowerCase();
  document.querySelectorAll('#rep-table tbody tr').forEach(r => {{
    const okSen = sen === 'ALL' || r.dataset.sen === sen;
    const okSearch = !q || r.textContent.toLowerCase().includes(q);
    r.style.display = okSen && okSearch ? '' : 'none';
  }});
}}
document.getElementById('rep-search').addEventListener('input', () => {{
  const active = document.querySelector('.sen-btn.active');
  filterSen(active ? active.textContent.trim().toUpperCase().replace('TODOS','ALL') : 'ALL', active || document.querySelector('.sen-btn'));
}});
</script>
</body>
</html>'''

out_path = r'c:\Users\allabriola\PROJETO CLAUDINHO\copiloto_analise_me.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Gerado: {out_path}  ({len(html)//1024} KB)')
print(f'Reps na tabela: {len(REPS_RAW)}')
