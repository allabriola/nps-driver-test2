import json, math
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════════════════

MONTH_LABELS = ['Jan','Fev','Mar','Abr','Mai*']
MONTHS       = ['2026-01','2026-02','2026-03','2026-04','2026-05']
WEEK_LABELS  = ['30/03','06/04','13/04','20/04','27/04','04/05','11/05','18/05*']
WEEKS        = ['2026-03-30','2026-04-06','2026-04-13','2026-04-20','2026-04-27','2026-05-04','2026-05-11','2026-05-18']
OFFICES      = ['ALL', 'ATE', 'KTA_BRASIL', 'AEC', 'CTX']
CHANNELS     = ['ALL', 'MULTICANAL CHAT', 'MULTICANAL C2C']
TABS         = ['geral', 'expert', 'newbie']
METRICS      = ['nps', 'tmo', 'prod', 'tdi', 'rec']

# ── TMO por Processo (hardcoded) ──────────────────────────────────────
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
PROC_TMO = {
    81:   {'com': (41.0, 347),   'sem': (32.6, 7688)},
    683:  {'com': (42.2, 743),   'sem': (34.9, 11624)},
    1647: {'com': (35.9, 572),   'sem': (29.2, 9732)},
    1660: {'com': (41.5, 144),   'sem': (29.9, 1458)},
    1797: {'com': (39.3, 1246),  'sem': (29.8, 14548)},
    1813: {'com': (41.5, 2428),  'sem': (31.4, 33936)},
    1814: {'com': (37.5, 210),   'sem': (31.7, 4514)},
    1816: {'com': (40.7, 631),   'sem': (32.4, 7438)},
    2358: {'com': (38.8, 853),   'sem': (29.6, 9065)},
    2570: {'com': (39.6, 277),   'sem': (32.6, 3646)},
}

# ── Reps individuais ─────────────────────────────────────────────────
with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_rep_data_me.json', encoding='utf-8') as f:
    REPS_RAW = json.load(f)

for r in REPS_RAW:
    cc = int(r.get('conversas_cop') or 0)
    tc = int(r.get('total_casos') or 0)
    r['pct_utilizacao'] = round(cc/tc*100, 1) if tc > 0 else 0.0

# ═══════════════════════════════════════════════════════════════════════
# CONSTRUÇÃO DO DSET — agrega JSONs por (office, grupo, seniority, mes/semana)
# ═══════════════════════════════════════════════════════════════════════

def _agg(rows, keys):
    """Agrega lista de dicts numéricos pelo dict de somas."""
    totals = defaultdict(int)
    for r in rows:
        for k in keys:
            v = r.get(k)
            if v is not None:
                try:
                    totals[k] += int(v)
                except (ValueError, TypeError):
                    pass
    return totals

def _safe(num, den):
    if den == 0:
        return None
    return num / den

def build_dset():
    # Carregar JSONs
    with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_nps_by_office.json', encoding='utf-8') as f:
        nps_raw = json.load(f)
    with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_tmo_by_office.json', encoding='utf-8') as f:
        tmo_raw = json.load(f)
    with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_tdi_by_office.json', encoding='utf-8') as f:
        tdi_raw = json.load(f)
    with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_rec_by_office.json', encoding='utf-8') as f:
        rec_raw = json.load(f)

    # Helper: filtrar por office e channel
    def by_office(rows, office):
        if office == 'ALL':
            return rows
        return [r for r in rows if r.get('office') == office]

    def by_channel(rows, channel):
        if channel == 'ALL':
            return rows
        return [r for r in rows if r.get('channel') == channel]

    # Helper: filtrar por grupo + seniority
    def by_gs(rows, grupo, seniority):
        out = [r for r in rows if r.get('grupo') == grupo]
        if seniority is not None:
            out = [r for r in out if r.get('seniority') == seniority]
        return out

    # tab → (t_grupo, t_sen, c_grupo, c_sen)
    # geral: treatment any vs control any
    # expert: treatment EXPERT vs control EXPERT (controle não tem split, mas queremos filtrar EXPERT do controle)
    # newbie: treatment NEWBIE vs control EXPERT (baseline)
    TAB_FILTERS = {
        'geral':  ('treatment', None,      'control', None),
        'expert': ('treatment', 'EXPERT',  'control', 'EXPERT'),
        'newbie': ('treatment', 'NEWBIE',  'control', 'EXPERT'),
    }

    def rnd(lst, decimals=2):
        return [round(v, decimals) if v is not None else None for v in lst]

    def calc_tab(nps_oc, tmo_oc, tdi_oc, rec_oc, tab):
        tg, ts, cg, cs = TAB_FILTERS[tab]
        result = {}

        # NPS
        t_nps = by_gs(nps_oc, tg, ts); c_nps = by_gs(nps_oc, cg, cs)
        nps_t_m, nps_t_w, nps_c_m, nps_c_w = [], [], [], []
        for m in MONTHS:
            ag_t = _agg([r for r in t_nps if r.get('mes')==m], ['prom','det','pesquisas'])
            ag_c = _agg([r for r in c_nps if r.get('mes')==m], ['prom','det','pesquisas'])
            nps_t_m.append(_safe((ag_t['prom']-ag_t['det'])*100, ag_t['pesquisas']))
            nps_c_m.append(_safe((ag_c['prom']-ag_c['det'])*100, ag_c['pesquisas']))
        for w in WEEKS:
            ag_t = _agg([r for r in t_nps if r.get('semana')==w], ['prom','det','pesquisas'])
            ag_c = _agg([r for r in c_nps if r.get('semana')==w], ['prom','det','pesquisas'])
            nps_t_w.append(_safe((ag_t['prom']-ag_t['det'])*100, ag_t['pesquisas']))
            nps_c_w.append(_safe((ag_c['prom']-ag_c['det'])*100, ag_c['pesquisas']))
        result['nps'] = {'t':{'m':rnd(nps_t_m,1),'w':rnd(nps_t_w,1)}, 'c':{'m':rnd(nps_c_m,1),'w':rnd(nps_c_w,1)}}

        # TMO + PROD
        t_tmo = by_gs(tmo_oc, tg, ts); c_tmo = by_gs(tmo_oc, cg, cs)
        tmo_t_m,tmo_t_w,tmo_c_m,tmo_c_w = [],[],[],[]
        prod_t_m,prod_t_w,prod_c_m,prod_c_w = [],[],[],[]
        for m in MONTHS:
            ag_t = _agg([r for r in t_tmo if r.get('mes')==m], ['casos','tmo_total_seg','tmo_outgoing_seg','outgoing'])
            ag_c = _agg([r for r in c_tmo if r.get('mes')==m], ['casos','tmo_total_seg','tmo_outgoing_seg','outgoing'])
            tmo_t_m.append(_safe(ag_t['tmo_outgoing_seg'], ag_t['outgoing']*60) if ag_t['outgoing'] else None)
            tmo_c_m.append(_safe(ag_c['tmo_outgoing_seg'], ag_c['outgoing']*60) if ag_c['outgoing'] else None)
            prod_t_m.append(_safe(ag_t['outgoing']*3600, ag_t['tmo_total_seg']) if ag_t['tmo_total_seg'] else None)
            prod_c_m.append(_safe(ag_c['outgoing']*3600, ag_c['tmo_total_seg']) if ag_c['tmo_total_seg'] else None)
        for w in WEEKS:
            ag_t = _agg([r for r in t_tmo if r.get('semana')==w], ['casos','tmo_total_seg','tmo_outgoing_seg','outgoing'])
            ag_c = _agg([r for r in c_tmo if r.get('semana')==w], ['casos','tmo_total_seg','tmo_outgoing_seg','outgoing'])
            tmo_t_w.append(_safe(ag_t['tmo_outgoing_seg'], ag_t['outgoing']*60) if ag_t['outgoing'] else None)
            tmo_c_w.append(_safe(ag_c['tmo_outgoing_seg'], ag_c['outgoing']*60) if ag_c['outgoing'] else None)
            prod_t_w.append(_safe(ag_t['outgoing']*3600, ag_t['tmo_total_seg']) if ag_t['tmo_total_seg'] else None)
            prod_c_w.append(_safe(ag_c['outgoing']*3600, ag_c['tmo_total_seg']) if ag_c['tmo_total_seg'] else None)
        result['tmo']  = {'t':{'m':rnd(tmo_t_m,1),'w':rnd(tmo_t_w,1)}, 'c':{'m':rnd(tmo_c_m,1),'w':rnd(tmo_c_w,1)}}
        result['prod'] = {'t':{'m':rnd(prod_t_m,2),'w':rnd(prod_t_w,2)}, 'c':{'m':rnd(prod_c_m,2),'w':rnd(prod_c_w,2)}}

        # TDI
        t_tdi = by_gs(tdi_oc, tg, ts); c_tdi = by_gs(tdi_oc, cg, cs)
        tdi_t_m,tdi_t_w,tdi_c_m,tdi_c_w = [],[],[],[]
        for m in MONTHS:
            ag_t = _agg([r for r in t_tdi if r.get('mes')==m], ['deriv','tdi_incorretas'])
            ag_c = _agg([r for r in c_tdi if r.get('mes')==m], ['deriv','tdi_incorretas'])
            tdi_t_m.append(_safe(ag_t['tdi_incorretas']*100, ag_t['deriv']) if ag_t['deriv'] else None)
            tdi_c_m.append(_safe(ag_c['tdi_incorretas']*100, ag_c['deriv']) if ag_c['deriv'] else None)
        for w in WEEKS:
            ag_t = _agg([r for r in t_tdi if r.get('semana')==w], ['deriv','tdi_incorretas'])
            ag_c = _agg([r for r in c_tdi if r.get('semana')==w], ['deriv','tdi_incorretas'])
            tdi_t_w.append(_safe(ag_t['tdi_incorretas']*100, ag_t['deriv']) if ag_t['deriv'] else None)
            tdi_c_w.append(_safe(ag_c['tdi_incorretas']*100, ag_c['deriv']) if ag_c['deriv'] else None)
        result['tdi'] = {'t':{'m':rnd(tdi_t_m,1),'w':rnd(tdi_t_w,1)}, 'c':{'m':rnd(tdi_c_m,1),'w':rnd(tdi_c_w,1)}}

        # REC
        t_rec = by_gs(rec_oc, tg, ts); c_rec = by_gs(rec_oc, cg, cs)
        rec_t_m,rec_t_w,rec_c_m,rec_c_w = [],[],[],[]
        for m in MONTHS:
            ag_t = _agg([r for r in t_rec if r.get('mes')==m], ['atrib','recontatos'])
            ag_c = _agg([r for r in c_rec if r.get('mes')==m], ['atrib','recontatos'])
            rec_t_m.append(_safe(ag_t['recontatos']*100, ag_t['atrib']) if ag_t['atrib'] else None)
            rec_c_m.append(_safe(ag_c['recontatos']*100, ag_c['atrib']) if ag_c['atrib'] else None)
        for w in WEEKS:
            ag_t = _agg([r for r in t_rec if r.get('semana')==w], ['atrib','recontatos'])
            ag_c = _agg([r for r in c_rec if r.get('semana')==w], ['atrib','recontatos'])
            rec_t_w.append(_safe(ag_t['recontatos']*100, ag_t['atrib']) if ag_t['atrib'] else None)
            rec_c_w.append(_safe(ag_c['recontatos']*100, ag_c['atrib']) if ag_c['atrib'] else None)
        result['rec'] = {'t':{'m':rnd(rec_t_m,1),'w':rnd(rec_t_w,1)}, 'c':{'m':rnd(rec_c_m,1),'w':rnd(rec_c_w,1)}}

        return result

    # DSET[office][channel][tab][metric]
    DSET = {}
    for office in OFFICES:
        DSET[office] = {}
        nps_o  = by_office(nps_raw, office)
        tmo_o  = by_office(tmo_raw, office)
        tdi_o  = by_office(tdi_raw, office)
        rec_o  = by_office(rec_raw, office)
        for channel in CHANNELS:
            DSET[office][channel] = {}
            nps_oc = by_channel(nps_o, channel)
            tmo_oc = by_channel(tmo_o, channel)
            tdi_oc = by_channel(tdi_o, channel)
            rec_oc = by_channel(rec_o, channel)
            for tab in TABS:
                DSET[office][channel][tab] = calc_tab(nps_oc, tmo_oc, tdi_oc, rec_oc, tab)

    return DSET

DSET = build_dset()

# ═══════════════════════════════════════════════════════════════════════
# HELPERS HTML
# ═══════════════════════════════════════════════════════════════════════

def fmt_nps(v):
    if v is None: return '<span class="sd">—</span>'
    v = float(v)
    cls = 'gc' if v >= 65 else ('yc' if v >= 50 else 'rc')
    return f'<span class="{cls}">{v:.1f}%</span>'

def build_proc_data():
    with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_proc_tmo_by_office.json', encoding='utf-8') as f:
        raw = json.load(f)

    # Build PROC_DATA[office][channel][pid] = {'com': (tmo, casos), 'sem': (tmo, casos)}
    from collections import defaultdict
    # accumulators: [office][channel][pid][grupo] = {'tmo_num': sum, 'out': sum, 'casos': sum}
    acc = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'tmo_num': 0.0, 'out': 0, 'casos': 0}))))

    def accumulate(office, channel, row):
        pid   = int(row['ASSIGN_PROCESS_ID'])
        grupo = row['grupo']
        tmo   = float(row['tmo_min'] or 0)
        casos = int(row['casos'] or 0)
        # We'll store weighted sum: tmo * casos (to allow re-aggregation)
        acc[office][channel][pid][grupo]['tmo_num'] += tmo * casos
        acc[office][channel][pid][grupo]['casos']   += casos

    for row in raw:
        o = row['office']
        ch = row['channel']
        accumulate(o, ch, row)
        accumulate(o, 'ALL', row)   # office-specific ALL channel
        accumulate('ALL', ch, row)  # ALL office, channel-specific
        accumulate('ALL', 'ALL', row)

    # Flatten to final structure
    result = {}
    for office in list(acc.keys()):
        result[office] = {}
        for channel in list(acc[office].keys()):
            result[office][channel] = {}
            for pid in list(acc[office][channel].keys()):
                entry = {}
                for grupo in ['com', 'sem']:
                    d = acc[office][channel][pid].get(grupo, {})
                    casos = d.get('casos', 0)
                    tmo = round(d['tmo_num'] / casos, 1) if casos else None
                    entry[grupo] = [tmo, casos]
                result[office][channel][pid] = entry

    # Ensure all OFFICES x CHANNELS exist (fill missing with None)
    for o in OFFICES:
        result.setdefault(o, {})
        for ch in CHANNELS:
            result[o].setdefault(ch, {})

    return result

PROC_DATA = build_proc_data()

def rep_rows():
    out = []
    sorted_reps = sorted(REPS_RAW, key=lambda r: (
        r.get('office') or 'zzz',
        -(float(r.get('pct_utilizacao') or 0))
    ))
    for r in sorted_reps:
        ldap   = r['ldap']
        sen    = r.get('seniority','')
        conv   = int(r.get('conversas_cop',0) or 0)
        pct_u  = float(r.get('pct_utilizacao',0) or 0)
        office = r.get('office','—') or '—'
        tl     = r.get('tl_ldap','—') or '—'
        p_abr  = int(r.get('pesq_abr',0) or 0)
        n_abr  = r.get('nps_abr')
        p_mai  = int(r.get('pesq_mai',0) or 0)
        n_mai  = r.get('nps_mai')
        sen_badge = '<span class="sen-e">E</span>' if sen=='EXPERT' else '<span class="sen-n">N</span>'
        bar_w = min(pct_u, 100)
        bar_col = '#10b981' if pct_u >= 30 else ('#f59e0b' if pct_u >= 10 else '#ef4444')
        util_cell = (f'<div class="util-bar"><div class="util-fill" style="width:{bar_w}%;background:{bar_col}"></div>'
                     f'</div><span class="util-val">{pct_u:.0f}%</span>')
        abr_cell = f'{fmt_nps(n_abr)} <span class="n-small">({p_abr})</span>' if p_abr else '<span class="sd">—</span>'
        mai_cell = f'{fmt_nps(n_mai)} <span class="n-small">({p_mai})</span>' if p_mai else '<span class="sd">—</span>'
        out.append(
            f'<tr data-sen="{sen}" data-office="{office}">'
            f'<td class="rep-name">{ldap} {sen_badge}</td>'
            f'<td>{office}</td>'
            f'<td class="n-small" style="color:#475569">{tl}</td>'
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
# DSET_OPC — comparação por uso do Copiloto (FLAG_COPILOT)
# DSET_OPC[opcao][office][channel] = {metric: {com/sem: {m/w: [...]}}}
# Opção A: apenas 209 reps treatment (scope='A')
# Opção B: todo time BR_ME (scope='A' + 'B_only')
# ═══════════════════════════════════════════════════════════════════════

def build_dset_opc():
    with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_opc_nps.json', encoding='utf-8') as f:
        nps_raw = json.load(f)
    with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_opc_tmo.json', encoding='utf-8') as f:
        tmo_raw = json.load(f)
    with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_opc_tdi.json', encoding='utf-8') as f:
        tdi_raw = json.load(f)
    with open(r'c:\Users\allabriola\PROJETO CLAUDINHO\_opc_rec.json', encoding='utf-8') as f:
        rec_raw = json.load(f)

    def by_scope(rows, opcao):
        # A: só treatment reps; B: todo time
        if opcao == 'A':
            return [r for r in rows if r.get('opcao_scope') == 'A']
        return rows  # B = A + B_only

    def by_oc(rows, office, channel):
        if office != 'ALL':
            rows = [r for r in rows if r.get('office') == office]
        if channel != 'ALL':
            rows = [r for r in rows if r.get('channel') == channel]
        return rows

    def flag_key(r, col='FLAG_CASE_COPILOT'):
        return str(r.get(col, r.get('flag_copilot', r.get('FLAG_COPILOT', '0'))))

    def rnd(lst, d=1):
        return [round(v, d) if v is not None else None for v in lst]

    def calc_opc(nps_s, tmo_s, tdi_s, rec_s):
        result = {}
        # NPS
        nps_com_m, nps_sem_m, nps_com_w, nps_sem_w = [], [], [], []
        for m in MONTHS:
            for flag, lst in [('1', nps_com_m), ('0', nps_sem_m)]:
                rows = [r for r in nps_s if flag_key(r,'FLAG_CASE_COPILOT')==flag and r.get('mes')==m]
                ag = _agg(rows, ['prom','det','pesquisas'])
                lst.append(_safe((ag['prom']-ag['det'])*100, ag['pesquisas']))
        for w in WEEKS:
            for flag, lst in [('1', nps_com_w), ('0', nps_sem_w)]:
                rows = [r for r in nps_s if flag_key(r,'FLAG_CASE_COPILOT')==flag and r.get('semana')==w]
                ag = _agg(rows, ['prom','det','pesquisas'])
                lst.append(_safe((ag['prom']-ag['det'])*100, ag['pesquisas']))
        result['nps'] = {'com':{'m':rnd(nps_com_m),'w':rnd(nps_com_w)},
                         'sem':{'m':rnd(nps_sem_m),'w':rnd(nps_sem_w)}}
        # TMO
        tmo_com_m, tmo_sem_m, tmo_com_w, tmo_sem_w = [], [], [], []
        for m in MONTHS:
            for flag, lst in [('1', tmo_com_m), ('0', tmo_sem_m)]:
                rows = [r for r in tmo_s if flag_key(r,'FLAG_COPILOT')==flag and r.get('mes')==m]
                ag = _agg(rows, ['tmo_outgoing_seg','outgoing'])
                lst.append(_safe(ag['tmo_outgoing_seg'], ag['outgoing']*60) if ag['outgoing'] else None)
        for w in WEEKS:
            for flag, lst in [('1', tmo_com_w), ('0', tmo_sem_w)]:
                rows = [r for r in tmo_s if flag_key(r,'FLAG_COPILOT')==flag and r.get('semana')==w]
                ag = _agg(rows, ['tmo_outgoing_seg','outgoing'])
                lst.append(_safe(ag['tmo_outgoing_seg'], ag['outgoing']*60) if ag['outgoing'] else None)
        result['tmo'] = {'com':{'m':rnd(tmo_com_m),'w':rnd(tmo_com_w)},
                         'sem':{'m':rnd(tmo_sem_m),'w':rnd(tmo_sem_w)}}
        result['prod'] = {'com':{'m':[None]*5,'w':[None]*8}, 'sem':{'m':[None]*5,'w':[None]*8}}  # n/a
        # TDI
        tdi_com_m, tdi_sem_m, tdi_com_w, tdi_sem_w = [], [], [], []
        for m in MONTHS:
            for flag, lst in [('1', tdi_com_m), ('0', tdi_sem_m)]:
                rows = [r for r in tdi_s if flag_key(r,'flag_copilot')==flag and r.get('mes')==m]
                ag = _agg(rows, ['deriv','tdi_incorretas'])
                lst.append(_safe(ag['tdi_incorretas']*100, ag['deriv']) if ag['deriv'] else None)
        for w in WEEKS:
            for flag, lst in [('1', tdi_com_w), ('0', tdi_sem_w)]:
                rows = [r for r in tdi_s if flag_key(r,'flag_copilot')==flag and r.get('semana')==w]
                ag = _agg(rows, ['deriv','tdi_incorretas'])
                lst.append(_safe(ag['tdi_incorretas']*100, ag['deriv']) if ag['deriv'] else None)
        result['tdi'] = {'com':{'m':rnd(tdi_com_m),'w':rnd(tdi_com_w)},
                         'sem':{'m':rnd(tdi_sem_m),'w':rnd(tdi_sem_w)}}
        # REC
        rec_com_m, rec_sem_m, rec_com_w, rec_sem_w = [], [], [], []
        for m in MONTHS:
            for flag, lst in [('1', rec_com_m), ('0', rec_sem_m)]:
                rows = [r for r in rec_s if flag_key(r,'flag_copilot')==flag and r.get('mes')==m]
                ag = _agg(rows, ['atrib','recontatos'])
                lst.append(_safe(ag['recontatos']*100, ag['atrib']) if ag['atrib'] else None)
        for w in WEEKS:
            for flag, lst in [('1', rec_com_w), ('0', rec_sem_w)]:
                rows = [r for r in rec_s if flag_key(r,'flag_copilot')==flag and r.get('semana')==w]
                ag = _agg(rows, ['atrib','recontatos'])
                lst.append(_safe(ag['recontatos']*100, ag['atrib']) if ag['atrib'] else None)
        result['rec'] = {'com':{'m':rnd(rec_com_m),'w':rnd(rec_com_w)},
                         'sem':{'m':rnd(rec_sem_m),'w':rnd(rec_sem_w)}}
        return result

    DSET_OPC = {}
    for opcao in ['A', 'B']:
        DSET_OPC[opcao] = {}
        nps_s  = by_scope(nps_raw, opcao)
        tmo_s  = by_scope(tmo_raw, opcao)
        tdi_s  = by_scope(tdi_raw, opcao)
        rec_s  = by_scope(rec_raw, opcao)
        for office in OFFICES:
            DSET_OPC[opcao][office] = {}
            for channel in CHANNELS:
                nps_oc = by_oc(nps_s, office, channel)
                tmo_oc = by_oc(tmo_s, office, channel)
                tdi_oc = by_oc(tdi_s, office, channel)
                rec_oc = by_oc(rec_s, office, channel)
                DSET_OPC[opcao][office][channel] = calc_opc(nps_oc, tmo_oc, tdi_oc, rec_oc)
    return DSET_OPC

DSET_OPC = build_dset_opc()

# ═══════════════════════════════════════════════════════════════════════

dset_json       = json.dumps(DSET,      ensure_ascii=False)
dset_opc_json   = json.dumps(DSET_OPC,  ensure_ascii=False)
proc_data_json  = json.dumps(PROC_DATA, ensure_ascii=False)
proc_names_json = json.dumps({str(k): v for k, v in PROC_NAMES.items()}, ensure_ascii=False)

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
.ch-grid-5.compact{{gap:6px;margin-top:6px}}
.ch-grid-5.compact .cc{{padding:7px 9px 6px}}
.ch-grid-5.compact .cc h3{{font-size:10px}}
.ch-grid-5.compact .cc p{{font-size:8.5px;margin:1px 0 5px}}
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
/* Office filter buttons */
.office-filter{{display:flex;gap:5px;margin-bottom:14px;align-items:center;flex-wrap:wrap}}
.office-btn{{padding:5px 16px;border-radius:7px;border:1px solid #e2e8f0;cursor:pointer;font-size:11px;font-weight:600;background:white;color:#64748b;transition:.15s}}
.office-btn.active{{background:#0f172a;color:white;border-color:#0f172a}}
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

  <!-- FILTROS GLOBAIS -->
  <div class="office-filter">
    <span style="font-size:11px;font-weight:700;color:#374151;margin-right:4px">Oficina:</span>
    <button class="office-btn active" onclick="setOffice('ALL',this)">Todas</button>
    <button class="office-btn" onclick="setOffice('ATE',this)">ATE</button>
    <button class="office-btn" onclick="setOffice('KTA_BRASIL',this)">KTA</button>
    <button class="office-btn" onclick="setOffice('AEC',this)">AEC</button>
    <button class="office-btn" onclick="setOffice('CTX',this)">CTX</button>
    <span style="font-size:11px;font-weight:700;color:#374151;margin-left:14px;margin-right:4px">Canal:</span>
    <button class="office-btn active channel-btn" onclick="setChannel('ALL',this)">Todos</button>
    <button class="office-btn channel-btn" onclick="setChannel('MULTICANAL CHAT',this)">Chat</button>
    <button class="office-btn channel-btn" onclick="setChannel('MULTICANAL C2C',this)">C2C</button>
  </div>

  <!-- TABS SENIORIDADE -->
  <div class="tabs">
    <button class="tab-btn active" onclick="setTab('geral',this)">Geral</button>
    <button class="tab-btn" onclick="setTab('expert',this)">Expert</button>
    <button class="tab-btn" onclick="setTab('newbie',this)">Newbie</button>
    <span style="width:1px;background:#e2e8f0;margin:0 4px"></span>
    <button class="tab-btn" onclick="setTab('opcA',this)" title="Casos dos 209 reps com Copilot: usaram vs não usaram">Opção A</button>
    <button class="tab-btn" onclick="setTab('opcB',this)" title="Todo o time BR_ME: casos com Copilot vs sem Copilot">Opção B</button>
  </div>

  <!-- TAB GERAL -->
  <div class="tab-pane active" id="tab-geral">
    <div class="section-lbl">Evolução Mensal — Jan a Mai/2026</div>
    <div class="ch-grid-5 compact">
      <div class="cc"><h3>NPS ↑</h3><p>% · Mar–Mai</p><canvas id="mNPS_geral"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="mTMO_geral"></canvas></div>
      <div class="cc"><h3>Produtividade ↑</h3><p>at/h</p><canvas id="mPROD_geral"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>% · Abr–Mai</p><canvas id="mTDI_geral"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>% · Mar–Mai</p><canvas id="mREC_geral"></canvas></div>
    </div>
    <div class="section-lbl">Evolução Semanal — 8 Semanas (30/03–18/05)</div>
    <div class="ch-grid-5 compact">
      <div class="cc"><h3>NPS ↑</h3><p>%</p><canvas id="wNPS_geral"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="wTMO_geral"></canvas></div>
      <div class="cc"><h3>Produtividade ↑</h3><p>at/h</p><canvas id="wPROD_geral"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>%</p><canvas id="wTDI_geral"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>%</p><canvas id="wREC_geral"></canvas></div>
    </div>
  </div>

  <!-- TAB EXPERT -->
  <div class="tab-pane" id="tab-expert">
    <div class="note warn" style="margin-bottom:10px">Experts: NPS superiores desde a ativação. TDI Expert com Copiloto apresenta melhora contínua. Controle = todos os Experts sem Copiloto.</div>
    <div class="section-lbl">Evolução Mensal — Jan a Mai/2026</div>
    <div class="ch-grid-5">
      <div class="cc"><h3>NPS ↑</h3><p>% · Mar–Mai</p><canvas id="mNPS_expert"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="mTMO_expert"></canvas></div>
      <div class="cc"><h3>Produtividade ↑</h3><p>at/h</p><canvas id="mPROD_expert"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>% · Abr–Mai</p><canvas id="mTDI_expert"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>% · Mar–Mai</p><canvas id="mREC_expert"></canvas></div>
    </div>
    <div class="section-lbl">Evolução Semanal — 8 Semanas (30/03–18/05)</div>
    <div class="ch-grid-5">
      <div class="cc"><h3>NPS ↑</h3><p>%</p><canvas id="wNPS_expert"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="wTMO_expert"></canvas></div>
      <div class="cc"><h3>Produtividade ↑</h3><p>at/h</p><canvas id="wPROD_expert"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>%</p><canvas id="wTDI_expert"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>%</p><canvas id="wREC_expert"></canvas></div>
    </div>
  </div>

  <!-- TAB NEWBIE -->
  <div class="tab-pane" id="tab-newbie">
    <div class="note warn" style="margin-bottom:10px">Newbies: NPS crescendo rapidamente. TDI era alto em Abr mas caiu em Mai. Controle = baseline Expert (sem split de senioridade disponível para o grupo controle).</div>
    <div class="section-lbl">Evolução Mensal — Jan a Mai/2026</div>
    <div class="ch-grid-5">
      <div class="cc"><h3>NPS ↑</h3><p>% · Mar–Mai</p><canvas id="mNPS_newbie"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="mTMO_newbie"></canvas></div>
      <div class="cc"><h3>Produtividade ↑</h3><p>at/h</p><canvas id="mPROD_newbie"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>% · Abr–Mai</p><canvas id="mTDI_newbie"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>% · Mar–Mai</p><canvas id="mREC_newbie"></canvas></div>
    </div>
    <div class="section-lbl">Evolução Semanal — 8 Semanas (30/03–18/05)</div>
    <div class="ch-grid-5">
      <div class="cc"><h3>NPS ↑</h3><p>%</p><canvas id="wNPS_newbie"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="wTMO_newbie"></canvas></div>
      <div class="cc"><h3>Produtividade ↑</h3><p>at/h</p><canvas id="wPROD_newbie"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>%</p><canvas id="wTDI_newbie"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>%</p><canvas id="wREC_newbie"></canvas></div>
    </div>
  </div>

  <!-- OPÇÃO A -->
  <div class="tab-pane" id="tab-opcA">
    <div class="note warn" style="margin-bottom:10px"><strong>Opção A — Por uso do Copiloto (mesmo grupo de reps):</strong> compara os <em>casos</em> dos 209 reps com Copilot onde o assistente foi acionado (FLAG_COPILOT=1) vs casos do mesmo grupo onde não foi acionado (FLAG_COPILOT=0). Elimina o viés de seleção de reps.</div>
    <div class="section-lbl">Evolução Mensal — Jan a Mai/2026</div>
    <div class="ch-grid-5 compact">
      <div class="cc"><h3>NPS ↑</h3><p>%</p><canvas id="mNPS_opcA"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="mTMO_opcA"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>% · Abr–Mai</p><canvas id="mTDI_opcA"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>%</p><canvas id="mREC_opcA"></canvas></div>
    </div>
    <div class="section-lbl">Evolução Semanal — 8 Semanas (30/03–18/05)</div>
    <div class="ch-grid-5 compact">
      <div class="cc"><h3>NPS ↑</h3><p>%</p><canvas id="wNPS_opcA"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="wTMO_opcA"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>%</p><canvas id="wTDI_opcA"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>%</p><canvas id="wREC_opcA"></canvas></div>
    </div>
  </div>

  <!-- OPÇÃO B -->
  <div class="tab-pane" id="tab-opcB">
    <div class="note warn" style="margin-bottom:10px"><strong>Opção B — Por uso do Copiloto (time completo):</strong> compara todos os casos do time BR_ME onde o Copilot foi acionado vs todos os casos onde não foi, independente do rep. Inclui reps sem acesso ao Copilot no grupo "sem".</div>
    <div class="section-lbl">Evolução Mensal — Jan a Mai/2026</div>
    <div class="ch-grid-5 compact">
      <div class="cc"><h3>NPS ↑</h3><p>%</p><canvas id="mNPS_opcB"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="mTMO_opcB"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>% · Abr–Mai</p><canvas id="mTDI_opcB"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>%</p><canvas id="mREC_opcB"></canvas></div>
    </div>
    <div class="section-lbl">Evolução Semanal — 8 Semanas (30/03–18/05)</div>
    <div class="ch-grid-5 compact">
      <div class="cc"><h3>NPS ↑</h3><p>%</p><canvas id="wNPS_opcB"></canvas></div>
      <div class="cc"><h3>TMO ↓</h3><p>min</p><canvas id="wTMO_opcB"></canvas></div>
      <div class="cc"><h3>TDI ↓</h3><p>%</p><canvas id="wTDI_opcB"></canvas></div>
      <div class="cc"><h3>Recontato ↓</h3><p>%</p><canvas id="wREC_opcB"></canvas></div>
    </div>
  </div>

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
      <tbody id="proc-tbody"></tbody>
    </table>
  </div>

  <hr class="div">

  <!-- TABELA POR REP -->
  <div class="section-lbl">Representantes com Copiloto — {len(REPS_RAW)} reps · Filtro por Senioridade e Oficina</div>
  <div class="note" style="margin-bottom:8px">
    <strong>% Utilização:</strong> conversas Copilot / total casos atendidos (Abr–Mai) ·
    <strong>NPS:</strong> verde ≥65% · amarelo 50–65% · vermelho &lt;50% · (n) = pesquisas ·
    <span class="sen-e">E</span> Expert &nbsp; <span class="sen-n">N</span> Newbie
  </div>
  <div class="sen-filter">
    <span style="font-size:11px;font-weight:600;color:#64748b">Senioridade:</span>
    <button class="sen-btn active" data-filter="sen" data-val="ALL" onclick="applyFilter(this)">Todos</button>
    <button class="sen-btn" data-filter="sen" data-val="EXPERT" onclick="applyFilter(this)">Expert</button>
    <button class="sen-btn" data-filter="sen" data-val="NEWBIE" onclick="applyFilter(this)">Newbie</button>
    <span style="font-size:11px;font-weight:600;color:#64748b;margin-left:12px">Oficina:</span>
    <button class="sen-btn active" data-filter="office" data-val="ALL" onclick="applyFilter(this)">Todas</button>
    <button class="sen-btn" data-filter="office" data-val="ATE" onclick="applyFilter(this)">ATE</button>
    <button class="sen-btn" data-filter="office" data-val="KTA_BRASIL" onclick="applyFilter(this)">KTA</button>
    <input id="rep-search" type="text" placeholder="Buscar LDAP..." style="padding:4px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:11px;margin-left:8px;">
  </div>
  <div class="proc-table-wrap">
    <table class="rt" id="rep-table">
      <thead>
        <tr>
          <th class="left">Representante</th>
          <th>Oficina</th>
          <th>Líder</th>
          <th>Conversas Copilot</th>
          <th style="min-width:110px">% Utilização</th>
          <th>NPS Abril</th>
          <th>NPS Maio*</th>
        </tr>
      </thead>
      <tbody>{rep_rows()}</tbody>
    </table>
  </div>
  <div class="note" style="margin-top:8px">Reps sem NPS: sem pesquisas respondidas no período. Ordenado por Oficina A-Z e depois por % Utilização desc.</div>

  <div class="footer">Gerado em <span id="ts2"></span> · Fonte: BT_CX_COPILOT_METRICS · DM_CX_NPS_Y20_DETAIL · BT_CX_CXCOPILOT_TMO · BT_CX_TDI · BT_CX_BASIC_CS_RECONTACTS · BR_ME_Sellers_Longtail</div>
</div>

<script>
// ── Dados ──────────────────────────────────────────────────────────────
const DSET      = {dset_json};
const DSET_OPC  = {dset_opc_json};
const PROC_DATA  = {proc_data_json};
const PROC_NAMES = {proc_names_json};
const MONTH_LABELS = {json.dumps(MONTH_LABELS)};
const WEEK_LABELS  = {json.dumps(WEEK_LABELS)};

// ── Estado ────────────────────────────────────────────────────────────
const CHARTS = {{}};
let currentOffice  = 'ALL';
let currentChannel = 'ALL';
let currentTab     = 'geral';
const TABS_CREATED = {{'geral':false,'expert':false,'newbie':false,'opcA':false,'opcB':false}};
const OPC_METRICS  = ['nps','tmo','tdi','rec'];  // Opção A/B não tem Produtividade

// ── Chart helpers ─────────────────────────────────────────────────────
function ds(data, color, label, dashed) {{
  return {{
    label, data,
    borderColor: color,
    backgroundColor: color + '18',
    borderWidth: dashed ? 1.5 : 2.5,
    pointRadius: 3,
    tension: 0.35,
    spanGaps: true,
    borderDash: dashed ? [6,4] : []
  }};
}}

function mkChart(id, labels, tData, cData, yLabel, yMin, yMax, aspectRatio) {{
  if (CHARTS[id]) {{
    updateChart(id, tData, cData);
    return;
  }}
  const el = document.getElementById(id);
  if (!el) return;
  CHARTS[id] = new Chart(el, {{
    type: 'line',
    data: {{
      labels,
      datasets: [
        ds(tData, '#2563EB', 'Com Copiloto', false),
        ds(cData, '#9CA3AF', 'Sem Copiloto', true)
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: aspectRatio,
      plugins: {{
        legend: {{
          position: 'bottom',
          labels: {{ font: {{size: 9}}, padding: 6, usePointStyle: true, pointStyleWidth: 5 }}
        }},
        tooltip: {{
          callbacks: {{
            label: c => c.parsed.y == null ? null : ` ${{c.dataset.label}}: ${{c.parsed.y.toFixed(1)}} ${{yLabel}}`
          }}
        }}
      }},
      scales: {{
        y: {{ suggestedMin: yMin, suggestedMax: yMax, grid: {{color:'#f1f5f9'}}, ticks: {{font:{{size:9}}}} }},
        x: {{ grid: {{display:false}}, ticks: {{font:{{size:9}}}} }}
      }}
    }}
  }});
}}

function updateChart(id, tData, cData) {{
  const ch = CHARTS[id];
  if (!ch) return;
  ch.data.datasets[0].data = tData;
  ch.data.datasets[1].data = cData;
  ch.update();
}}

// ── Criação / atualização de gráficos de uma tab ──────────────────────
// ── Opção A / B — render/update ────────────────────────────────────────
function renderOpcCharts(tab, office, channel) {{
  const opcao = tab === 'opcA' ? 'A' : 'B';
  const d = DSET_OPC[opcao][office][channel];
  const ar = 2.6;
  const lbl = tab === 'opcA' ? 'Usou Copiloto' : 'Com Copiloto';
  const lbl2 = 'Sem Copiloto';
  function mkO(id, labels, com, sem, yLbl, yMin, yMax) {{
    if (!CHARTS[id]) {{
      CHARTS[id] = new Chart(document.getElementById(id), {{type:'line',
        data:{{labels,datasets:[
          {{label:lbl,data:com,borderColor:'#2563EB',backgroundColor:'#2563EB18',borderWidth:2.5,pointRadius:3,tension:0.35,spanGaps:true}},
          {{label:lbl2,data:sem,borderColor:'#9CA3AF',backgroundColor:'#9CA3AF18',borderWidth:2,pointRadius:3,tension:0.35,borderDash:[6,4],spanGaps:true}}
        ]}},
        options:{{responsive:true,maintainAspectRatio:true,aspectRatio:ar,
          plugins:{{legend:{{position:'bottom',labels:{{font:{{size:9}},padding:6,usePointStyle:true,pointStyleWidth:5}}}},
            tooltip:{{callbacks:{{label:c=>c.parsed.y==null?null:` ${{c.dataset.label}}: ${{c.parsed.y.toFixed(1)}} ${{yLbl}}`}}}}}},
          scales:{{y:{{suggestedMin:yMin,suggestedMax:yMax,grid:{{color:'#f1f5f9'}},ticks:{{font:{{size:9}}}}}},x:{{grid:{{display:false}},ticks:{{font:{{size:9}}}}}}}}}}
      }});
    }} else {{
      CHARTS[id].data.datasets[0].data = com;
      CHARTS[id].data.datasets[1].data = sem;
      CHARTS[id].update();
    }}
  }}
  mkO('mNPS_'+tab, MONTH_LABELS, d.nps.com.m, d.nps.sem.m, '%',   40, 85);
  mkO('mTMO_'+tab, MONTH_LABELS, d.tmo.com.m, d.tmo.sem.m, 'min', 22, 45);
  mkO('mTDI_'+tab, MONTH_LABELS, d.tdi.com.m, d.tdi.sem.m, '%',   2,  18);
  mkO('mREC_'+tab, MONTH_LABELS, d.rec.com.m, d.rec.sem.m, '%',   0,  30);
  mkO('wNPS_'+tab, WEEK_LABELS,  d.nps.com.w, d.nps.sem.w, '%',   40, 85);
  mkO('wTMO_'+tab, WEEK_LABELS,  d.tmo.com.w, d.tmo.sem.w, 'min', 22, 45);
  mkO('wTDI_'+tab, WEEK_LABELS,  d.tdi.com.w, d.tdi.sem.w, '%',   2,  18);
  mkO('wREC_'+tab, WEEK_LABELS,  d.rec.com.w, d.rec.sem.w, '%',   0,  10);
}}

function renderTabCharts(tab, office, channel) {{
  if (tab === 'opcA' || tab === 'opcB') {{ renderOpcCharts(tab, office, channel); return; }}
  const d = DSET[office][channel][tab];
  const isGeral = (tab === 'geral');
  const arM = isGeral ? 2.6 : 1.55;
  const arW = isGeral ? 2.6 : 1.55;

  mkChart('mNPS_'  + tab, MONTH_LABELS, d.nps.t.m,  d.nps.c.m,  '%',    40,  85,  arM);
  mkChart('mTMO_'  + tab, MONTH_LABELS, d.tmo.t.m,  d.tmo.c.m,  'min',  22,  45,  arM);
  mkChart('mPROD_' + tab, MONTH_LABELS, d.prod.t.m, d.prod.c.m, 'at/h', 0.8, 1.8, arM);
  mkChart('mTDI_'  + tab, MONTH_LABELS, d.tdi.t.m,  d.tdi.c.m,  '%',    2,   18,  arM);
  mkChart('mREC_'  + tab, MONTH_LABELS, d.rec.t.m,  d.rec.c.m,  '%',    0,   30,  arM);

  mkChart('wNPS_'  + tab, WEEK_LABELS,  d.nps.t.w,  d.nps.c.w,  '%',    40,  85,  arW);
  mkChart('wTMO_'  + tab, WEEK_LABELS,  d.tmo.t.w,  d.tmo.c.w,  'min',  24,  44,  arW);
  mkChart('wPROD_' + tab, WEEK_LABELS,  d.prod.t.w, d.prod.c.w, 'at/h', 0.75,1.5, arW);
  mkChart('wTDI_'  + tab, WEEK_LABELS,  d.tdi.t.w,  d.tdi.c.w,  '%',    2,   18,  arW);
  mkChart('wREC_'  + tab, WEEK_LABELS,  d.rec.t.w,  d.rec.c.w,  '%',    0,   10,  arW);
}}

function updateTabCharts(tab, office, channel) {{
  if (tab === 'opcA' || tab === 'opcB') {{ renderOpcCharts(tab, office, channel); return; }}
  const d = DSET[office][channel][tab];
  updateChart('mNPS_'  + tab, d.nps.t.m,  d.nps.c.m);
  updateChart('mTMO_'  + tab, d.tmo.t.m,  d.tmo.c.m);
  updateChart('mPROD_' + tab, d.prod.t.m, d.prod.c.m);
  updateChart('mTDI_'  + tab, d.tdi.t.m,  d.tdi.c.m);
  updateChart('mREC_'  + tab, d.rec.t.m,  d.rec.c.m);
  updateChart('wNPS_'  + tab, d.nps.t.w,  d.nps.c.w);
  updateChart('wTMO_'  + tab, d.tmo.t.w,  d.tmo.c.w);
  updateChart('wPROD_' + tab, d.prod.t.w, d.prod.c.w);
  updateChart('wTDI_'  + tab, d.tdi.t.w,  d.tdi.c.w);
  updateChart('wREC_'  + tab, d.rec.t.w,  d.rec.c.w);
}}

// ── refreshAllCharts — chamado após mudança de office ou channel ──────
// ── renderProcTable — tabela TMO por processo dinâmica ────────────────
function renderProcTable(office, channel) {{
  const data = PROC_DATA[office]?.[channel] || {{}};
  const order = Object.keys(PROC_NAMES).map(Number)
    .sort((a,b) => {{
      const na = (data[a]?.com?.[1]||0)+(data[a]?.sem?.[1]||0);
      const nb = (data[b]?.com?.[1]||0)+(data[b]?.sem?.[1]||0);
      return nb - na;
    }});
  const rows = order.map(pid => {{
    const nm  = PROC_NAMES[pid];
    const d   = data[pid];
    if (!d) return '';
    const com = d.com || [null, 0];
    const sem = d.sem || [null, 0];
    const tco = com[0], nco = com[1];
    const tse = sem[0], nse = sem[1];
    if (!tco && !tse) return '';
    const delta = (tco != null && tse != null) ? (tco - tse).toFixed(1) : '—';
    const sign  = parseFloat(delta) > 0 ? '+' : '';
    const cls   = parseFloat(delta) > 2 ? 'rc' : (parseFloat(delta) < -2 ? 'gc' : 'neu-cell');
    const ncoFmt = nco ? nco.toLocaleString('pt-BR') : '—';
    const nseFmt = nse ? nse.toLocaleString('pt-BR') : '—';
    const tcoFmt = tco != null ? tco.toFixed(1) : '—';
    const tseFmt = tse != null ? tse.toFixed(1) : '—';
    const deltaCell = tco != null && tse != null
      ? `<span class="${{cls}}">${{sign}}${{delta}} min</span>` : '<span class="sd">—</span>';
    return `<tr><td class="rep-name">${{nm}}</td><td>${{tcoFmt}}</td><td class="n-small">${{ncoFmt}}</td><td>${{tseFmt}}</td><td class="n-small">${{nseFmt}}</td><td>${{deltaCell}}</td></tr>`;
  }}).filter(Boolean);
  document.getElementById('proc-tbody').innerHTML = rows.join('');
}}

function refreshAllCharts() {{
  ['geral','expert','newbie'].forEach(tab => {{
    if (TABS_CREATED[tab]) updateTabCharts(tab, currentOffice, currentChannel);
  }});
  renderProcTable(currentOffice, currentChannel);
}}

// ── setOffice ─────────────────────────────────────────────────────────
function setOffice(office, btn) {{
  currentOffice = office;
  document.querySelectorAll('.office-btn:not(.channel-btn)').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  refreshAllCharts();
}}

// ── setChannel ────────────────────────────────────────────────────────
function setChannel(channel, btn) {{
  currentChannel = channel;
  document.querySelectorAll('.channel-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  refreshAllCharts();
}}

// ── setTab — cria charts se necessário ───────────────────────────────
function setTab(id, btn) {{
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  btn.classList.add('active');
  currentTab = id;
  if (!TABS_CREATED[id]) {{
    renderTabCharts(id, currentOffice, currentChannel);
    TABS_CREATED[id] = true;
  }} else {{
    updateTabCharts(id, currentOffice, currentChannel);
  }}
}}

// ── Seniority / office filter na tabela de reps ───────────────────────
function applyFilter(btn) {{
  const group = btn.dataset.filter;
  document.querySelectorAll(`.sen-btn[data-filter="${{group}}"]`).forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  runFilter();
}}
function runFilter() {{
  const sen    = (document.querySelector('.sen-btn[data-filter="sen"].active')    || {{}}).dataset?.val || 'ALL';
  const office = (document.querySelector('.sen-btn[data-filter="office"].active') || {{}}).dataset?.val || 'ALL';
  const q = document.getElementById('rep-search').value.toLowerCase();
  document.querySelectorAll('#rep-table tbody tr').forEach(r => {{
    const okSen    = sen    === 'ALL' || r.dataset.sen    === sen;
    const okOffice = office === 'ALL' || r.dataset.office === office;
    const okSearch = !q || r.textContent.toLowerCase().includes(q);
    r.style.display = okSen && okOffice && okSearch ? '' : 'none';
  }});
}}
document.getElementById('rep-search').addEventListener('input', runFilter);

// ── Init ──────────────────────────────────────────────────────────────
document.getElementById('ts').textContent  = new Date().toLocaleDateString('pt-BR');
document.getElementById('ts2').textContent = new Date().toLocaleDateString('pt-BR');

// Criar charts da tab geral (visível inicialmente)
renderTabCharts('geral', 'ALL', 'ALL');
renderProcTable('ALL', 'ALL');
TABS_CREATED['geral'] = true;
</script>
</body>
</html>'''

out_path = r'c:\Users\allabriola\PROJETO CLAUDINHO\copiloto_analise_me.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Gerado: {out_path}  ({len(html)//1024} KB)')
print(f'Reps na tabela: {len(REPS_RAW)}')
