#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera _exec_summary_sd.html com análise automática baseada nos dados reais do dashboard.
Estrutura: Sellers (segmentos) | Partners | Publicaciones | Exp. Impositiva
"""
import json, re, sys, html as _html
sys.stdout.reconfigure(encoding='utf-8')
def esc(s): return _html.escape(str(s))

# ── Carrega dados ─────────────────────────────────────────────────────
with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)
mh = ns['monthly_history']
nt = ns['NPS_TARGET']
ml = ns['MONTH_LABELS']

with open('_monthly_result.json', encoding='utf-8') as f:
    mr = json.load(f)
for lbl, dm in mr.items():
    for drv, vals in dm.items():
        mh.setdefault(drv, {})[lbl] = tuple(vals)

with open('_period_targets_sd.json', encoding='utf-8') as f:
    pt = json.load(f)
with open('_monthly_breakdown.json', encoding='utf-8') as f:
    mb = json.load(f)
with open('_process_analysis.json', encoding='utf-8') as f:
    pa = json.load(f)

import os
rc = {}
if os.path.exists('_recurrence_cases.json'):
    with open('_recurrence_cases.json', encoding='utf-8') as f:
        rc = json.load(f)

# Transcrições S1 para extrair motivos de detratores
_trx_s1 = {}
if os.path.exists('_trx_s1.json'):
    with open('_trx_s1.json', encoding='utf-8') as f:
        _trx_s1 = json.load(f)

_CONTACT_KWS = {
    'envio e logística':      ['envio','entrega','logistica','transportadora','frete','rastreio','prazo'],
    'devolução e reembolso':  ['devolucao','devolver','reembolso','cancelamento','estorno'],
    'cobrança e faturamento': ['cobranca','nota fiscal','fatura','pagamento','taxa','imposto'],
    'mediação e disputa':     ['mediacao','disputa','reclamacao','procon','ouvidoria'],
    'produto e qualidade':    ['produto','qualidade','defeito','quebrado','errado'],
    'plataforma e sistema':   ['plataforma','sistema','erro','bug','acesso','login'],
}
_PAIN_KWS = {
    'urgência não atendida':  ['urgente','preciso','urgencia','imediato','agora'],
    'falta de solução':       ['sem solucao','nao resolveu','nao ajudou','continua'],
    'atendimento ruim':       ['mal atendido','grosseiro','descaso','ignorado'],
}

def _get_det_themes(grp):
    """Extrai motivos de contato dos detratores via _trx_s1.json."""
    gdata = _trx_s1.get(grp, {})
    det = gdata.get('detrator', gdata)
    if not det: return [], [], 0
    n = len(det)
    c_cnt = {k: 0 for k in _CONTACT_KWS}
    p_cnt = {k: 0 for k in _PAIN_KWS}
    for cid, msgs in det.items():
        user_t = ' '.join(m.get('msg','').lower() for m in msgs if m.get('role')=='USER')
        for cat, kws in _CONTACT_KWS.items():
            if any(k in user_t for k in kws): c_cnt[cat] += 1
        for pat, kws in _PAIN_KWS.items():
            if any(k in user_t for k in kws): p_cnt[pat] += 1
    contacts = [(c,v) for c,v in sorted(c_cnt.items(), key=lambda x:-x[1]) if v>0]
    pains    = [(p,v) for p,v in sorted(p_cnt.items(), key=lambda x:-x[1]) if v>0]
    return contacts, pains, n

lC, lP = ml[-1], ml[-2]  # Mai, Abr

# ── Helpers ───────────────────────────────────────────────────────────
def nps(p, d, s): return round(100*(p-d)/s, 2) if s > 0 else None

def fn(v, dec=1):
    if v is None: return '—'
    return f'{round(v, dec):.{dec}f}'.replace('.', ',')

def sign(v):
    return '+' if v is not None and v >= 0 else ''

def grp_nps(drvs, lbl):
    p   = sum(mh.get(d,{}).get(lbl,(0,0,0))[0] for d in drvs)
    det = sum(mh.get(d,{}).get(lbl,(0,0,0))[1] for d in drvs)
    s   = sum(mh.get(d,{}).get(lbl,(0,0,0))[2] for d in drvs)
    return nps(p, det, s), s

def tgt_weighted(drvs, period='Mai'):
    drv_tgts = pt.get('monthly', {}).get(period, {}).get('drivers', {})
    wn = sum(mh.get(d,{}).get(period,(0,0,0))[2] * drv_tgts.get(d, nt)
             for d in drvs if drv_tgts.get(d))
    wd = sum(mh.get(d,{}).get(period,(0,0,0))[2] for d in drvs if drv_tgts.get(d))
    return round(wn/wd, 2) if wd else nt

def seniority(drvs, period):
    """Retorna dict {senioridade: {nps, s, share_pct}}"""
    sr = {}
    for drv in drvs:
        for k, v in mb.get(period, {}).get(drv, {}).get('Sr', {}).items():
            if k in ('(sem senior)', '(sem seniority)', 'UNAVAILABLE', 'unavailable'):
                continue
            r = sr.setdefault(k, {'p':0,'d':0,'s':0})
            r['p'] += v.get('p',0); r['d'] += v.get('d',0); r['s'] += v.get('s',0)
    total = sum(v['s'] for v in sr.values())
    for v in sr.values():
        v['nps']   = nps(v['p'], v['d'], v['s'])
        v['share'] = round(100*v['s']/total) if total else 0
    return sr

def channel(drvs, period):
    """Retorna dict {canal: {nps, s, share_pct}}"""
    ch = {}
    for drv in drvs:
        for k, v in mb.get(period, {}).get(drv, {}).get('C', {}).items():
            if '(sem' in k.lower(): continue
            norm = {'MULTICANAL CHAT':'CHAT','MULTICANAL C2C':'C2C',
                    'MULTICANAL OFFLINE':'OFFLINE','Chat':'CHAT','Chat ':'CHAT'}.get(k, k)
            r = ch.setdefault(norm, {'p':0,'d':0,'s':0})
            r['p'] += v.get('p',0); r['d'] += v.get('d',0); r['s'] += v.get('s',0)
    total = sum(v['s'] for v in ch.values())
    for v in ch.values():
        v['nps']   = nps(v['p'], v['d'], v['s'])
        v['share'] = round(100*v['s']/total) if total else 0
    return ch

def office_summary(drvs, period):
    """Retorna top 3 oficinas por volume, com NPS e MoM."""
    off = {}; off_abr = {}
    for drv in drvs:
        for k, v in mb.get(period,{}).get(drv,{}).get('O',{}).items():
            if k.startswith('(sem'): continue
            r = off.setdefault(k, {'p':0,'d':0,'s':0})
            r['p']+=v.get('p',0); r['d']+=v.get('d',0); r['s']+=v.get('s',0)
        for k, v in mb.get('Abr',{}).get(drv,{}).get('O',{}).items():
            if k.startswith('(sem'): continue
            r = off_abr.setdefault(k, {'p':0,'d':0,'s':0})
            r['p']+=v.get('p',0); r['d']+=v.get('d',0); r['s']+=v.get('s',0)
    total = sum(v['s'] for v in off.values())
    result = []
    for k, v in sorted(off.items(), key=lambda x: -x[1]['s'])[:3]:
        nc2 = nps(v['p'],v['d'],v['s'])
        abr_v = off_abr.get(k,{})
        np2 = nps(abr_v.get('p',0),abr_v.get('d',0),abr_v.get('s',1)) if abr_v.get('s') else None
        mom2 = round(nc2-np2,1) if nc2 is not None and np2 is not None else None
        result.append({'name': k, 'nps': nc2, 'mom': mom2, 'share': round(100*v['s']/total) if total else 0})
    return result

# ── Dados por driver ──────────────────────────────────────────────────
SD = {
    'ME Vendedor':     ['ME Vendedor Seller Dev'],
    'PCF Vendedor':    ['PCF Vendedor Seller Dev'],
    'Post Venta':      ['Post Venta Seller Dev'],
    'Publicaciones':   ['Publicaciones Seller Dev'],
    'Exp. Impositiva': ['Experiencia Impositiva Seller Dev'],
    'Partners':        ['Partners'],
}
SEG = {
    'LT':      ['ME Vendedor Seller Dev','PCF Vendedor Seller Dev','Post Venta Seller Dev',
                'Publicaciones Seller Dev','Experiencia Impositiva Seller Dev'],
    'Mature':  ['ME Vendedor Mature','PCF Vendedor Mature','Post Venta Mature',
                'Publicaciones Mature','Experiencia Impositiva Mature'],
    'MeliPro': ['ME Vendedor Meli Pro','PCF Vendedor Meli Pro','Post Venta Meli Pro',
                'Publicaciones Meli Pro','Experiencia Impositiva Meli Pro'],
}

# Consolidado SD
cons_tgt = pt.get('monthly', {}).get('Mai', {}).get('consolidated', nt)
all_sd = [d for drvs in SD.values() for d in drvs]
nc_cons, sc_cons = grp_nps(all_sd, lC)
np_cons, _       = grp_nps(all_sd, lP)
gap_cons         = round(nc_cons - cons_tgt, 2) if nc_cons else None
mom_cons         = round(nc_cons - np_cons, 2)  if nc_cons and np_cons else None

# Segmentos
seg_data = {}
for seg, drvs in SEG.items():
    nc, sc = grp_nps(drvs, lC)
    np2, _ = grp_nps(drvs, lP)
    tg     = tgt_weighted(drvs)
    seg_data[seg] = {
        'nc': nc, 'np': np2, 'sc': sc, 'tgt': tg,
        'gap': round(nc - tg, 2) if nc else None,
        'mom': round(nc - np2, 2) if nc and np2 else None,
    }

# Drivers individuais
drv_data = {}
for grp, drvs in SD.items():
    nc, sc = grp_nps(drvs, lC)
    np2, _ = grp_nps(drvs, lP)
    tg     = tgt_weighted(drvs)
    drv_data[grp] = {
        'nc': nc, 'np': np2, 'sc': sc, 'tgt': tg,
        'gap': round(nc - tg, 2) if nc else None,
        'mom': round(nc - np2, 2) if nc and np2 else None,
        'sr_mai': seniority(drvs, 'Mai'),
        'sr_abr': seniority(drvs, 'Abr'),
        'ch_mai': channel(drvs, 'Mai'),
        'off_mai': office_summary(drvs, 'Mai'),
        'top_proc': pa.get(grp, {}).get('top_neg', {}).get('proc', ''),
        'top_cdu': (rc.get(grp, {}).get('categories_mon') or [{}])[0].get('sub_pattern', ''),
    }

# ── Análise computada ─────────────────────────────────────────────────

# Segmentos acima/abaixo da meta
segs_above = [s for s, v in seg_data.items() if (v['gap'] or 0) >= 0]
segs_below = [s for s, v in seg_data.items() if (v['gap'] or 0) < 0]

# WTF contribuição de cada segmento para o consolidado (aprox. por share × MoM)
def wtf_contrib(drvs, all_drvs):
    sA = sum(mh.get(d,{}).get(lP,(0,0,0))[2] for d in all_drvs)
    sB = sum(mh.get(d,{}).get(lC,(0,0,0))[2] for d in all_drvs)
    pA = sum(mh.get(d,{}).get(lP,(0,0,0))[0] for d in drvs)
    dA = sum(mh.get(d,{}).get(lP,(0,0,0))[1] for d in drvs)
    saG= sum(mh.get(d,{}).get(lP,(0,0,0))[2] for d in drvs)
    pB = sum(mh.get(d,{}).get(lC,(0,0,0))[0] for d in drvs)
    dB = sum(mh.get(d,{}).get(lC,(0,0,0))[1] for d in drvs)
    sbG= sum(mh.get(d,{}).get(lC,(0,0,0))[2] for d in drvs)
    na = nps(pA,dA,saG) or 0; nb = nps(pB,dB,sbG) or 0
    sha = saG/sA if sA else 0; shb = sbG/sB if sB else 0
    return round(sha*(nb-na) + (shb-sha)*(nb-(nc_cons or 0)), 2)

seg_contrib = {s: wtf_contrib(SEG[s], all_sd) for s in SEG}

# ── Helpers de texto ──────────────────────────────────────────────────
def sr_summary(grp, key_sr='Newbie'):
    sr_mai = drv_data[grp]['sr_mai']
    sr_abr = drv_data[grp]['sr_abr']
    sr_key = next((k for k in sr_mai if key_sr.lower() in k.lower()), None)
    if not sr_key:
        return None
    vmai = sr_mai[sr_key]
    vabr = sr_abr.get(next((k for k in sr_abr if key_sr.lower() in k.lower()), ''), {})
    mom_sr = round(vmai['nps'] - vabr.get('nps', vmai['nps']), 1) if vabr else None
    gap_sr = round(vmai['nps'] - drv_data[grp]['tgt'], 1) if vmai['nps'] is not None else None
    return {'nps': vmai['nps'], 'share': vmai['share'], 'mom': mom_sr, 'gap_tgt': gap_sr}

def sr_gap_expert_newbie(grp):
    sr = drv_data[grp]['sr_mai']
    exp_k = next((k for k in sr if 'expert' in k.lower()), None)
    new_k = next((k for k in sr if 'newbie' in k.lower()), None)
    if exp_k and new_k and sr[exp_k]['nps'] and sr[new_k]['nps']:
        return round(sr[exp_k]['nps'] - sr[new_k]['nps'], 1)
    return None

def ch_summary(grp, canal='C2C'):
    ch = drv_data[grp]['ch_mai']
    ch_k = next((k for k in ch if canal.upper() in k.upper()), None)
    if not ch_k: return None
    return {'nps': ch[ch_k]['nps'], 'share': ch[ch_k]['share']}

def cdu_narrative(grp):
    """Retorna a narrativa do top CDU do processo principal (de _recurrence_cases.json)."""
    cats = rc.get(grp, {}).get('categories_mon') or []
    if not cats: return None, None, 0
    top = cats[0]
    return top.get('sub_pattern',''), top.get('narrative',''), top.get('share_pct',0)

# ── Monta headline ────────────────────────────────────────────────────
d_pub = drv_data['Publicaciones']
d_ei  = drv_data['Exp. Impositiva']
d_par = drv_data['Partners']

ei_newbie  = sr_summary('Exp. Impositiva', 'Newbie')
pub_newbie = sr_summary('Publicaciones',   'Newbie')
par_newbie = sr_summary('Partners',        'Newbie')

ei_gap_sen = sr_gap_expert_newbie('Exp. Impositiva')
pub_c2c    = ch_summary('Publicaciones', 'C2C')

mom_dir = "alta" if (mom_cons or 0) > 0 else "queda"
headline = (
    f"NPS de {fn(nc_cons)}% — "
    f"{sign(gap_cons)}{fn(gap_cons)} pp vs. meta ({fn(cons_tgt)}%) "
    f"e {sign(mom_cons)}{fn(mom_cons)} pp MoM ({lP} → {lC})"
)

# ── Monta bullets ─────────────────────────────────────────────────────

# Bullet Destaques Positivos — drivers com melhor evolução MoM e/ou maior folga vs meta
# Ordena todos os drivers por: (acima da meta E MoM positivo) > (acima da meta) > (MoM positivo)
def destaque_score(grp):
    v = drv_data[grp]
    gap = v['gap'] or 0
    mom = v['mom'] or 0
    return (1 if gap >= 0 else 0) * 100 + mom

destaques = sorted(drv_data.keys(), key=lambda g: -destaque_score(g))
destaques_pos = [g for g in destaques
                 if (drv_data[g]['gap'] or 0) >= 0 or (drv_data[g]['mom'] or 0) > 1][:3]

def build_narrative(grp, icon):
    """Gera parágrafo narrativo corrido (sem tópicos) com todos os dados compilados."""
    v = drv_data[grp]

    # Senioridade
    sr = v['sr_mai']; sr_abr = v['sr_abr']
    exp_k = next((k for k in sr if 'expert' in k.lower()), None)
    new_k = next((k for k in sr if 'newbie' in k.lower()), None)
    exp_v = sr.get(exp_k, {}); new_v = sr.get(new_k, {})
    exp_abr = sr_abr.get(next((k for k in sr_abr if 'expert' in k.lower()), ''), {})
    new_abr = sr_abr.get(next((k for k in sr_abr if 'newbie' in k.lower()), ''), {})
    exp_mom = round(exp_v['nps']-exp_abr['nps'],1) if exp_v.get('nps') and exp_abr.get('nps') else None
    new_mom = round(new_v['nps']-new_abr['nps'],1) if new_v.get('nps') and new_abr.get('nps') else None
    gap_sen = round(exp_v['nps']-new_v['nps'],1) if exp_v.get('nps') and new_v.get('nps') else None

    # Oficinas
    offs = v.get('off_mai', [])
    top_off   = offs[0] if offs else None
    worst_off = min(offs, key=lambda x: x['nps'] if x['nps'] is not None else 999) if offs else None

    # CDU + processo
    cdu_name, cdu_narr, cdu_share = cdu_narrative(grp)
    proc = v.get('top_proc', '')
    cdu_first = cdu_narr.split('. ')[0] if cdu_narr and '. ' in cdu_narr else (cdu_narr or '')

    # Constrói texto corrido
    gap = v['gap'] or 0; mom = v['mom'] or 0

    # Abertura: NPS + status vs meta + MoM (independentes)
    status_txt = (f"<strong>{sign(gap)}{fn(gap)} pp acima da meta</strong>"
                  if gap >= 0 else
                  f"<strong>{fn(abs(gap))} pp abaixo da meta</strong>")

    if mom > 0.5:
        trend_txt = f"Alta de <strong>+{fn(mom)} pp MoM</strong>. "
    elif mom < -0.5:
        trend_txt = f"Queda de <strong>{fn(mom)} pp MoM</strong>. "
    else:
        trend_txt = "Performance estável no período. "

    text = (f"{icon} <strong>{grp}</strong>: NPS de <strong>{fn(v['nc'])}%</strong>, "
            f"{status_txt} ({fn(v['tgt'])}%). {trend_txt}")

    # Senioridade
    if exp_v.get('nps') and new_v.get('nps'):
        if gap < 0 and gap_sen and gap_sen > 15:
            # Gap crítico: foco no problema de Newbies
            text += (f"O gap de senioridade é expressivo: Experts chegam a {fn(exp_v['nps'])}% "
                     f"({exp_v.get('share',0)}% das pesquisas"
                     f"{f', {sign(exp_mom)}{fn(exp_mom)} pp MoM' if exp_mom is not None else ''})"
                     f", enquanto Newbies registram apenas {fn(new_v['nps'])}% "
                     f"({new_v.get('share',0)}% das pesquisas"
                     f"{f', {sign(new_mom)}{fn(new_mom)} pp MoM' if new_mom is not None else ''}"
                     f") — gap de <strong>{fn(gap_sen)} pp</strong> apontando lacuna de capacitação. ")
        elif gap >= 0 and exp_v.get('nps'):
            # Performance boa: destaca que ambos contribuem
            contrib_new = f" e Newbies em {fn(new_v['nps'])}% ({new_v.get('share',0)}%{f', {sign(new_mom)}{fn(new_mom)} pp MoM' if new_mom is not None else ''})" if new_v.get('nps') else ""
            text += (f"Performance sustentada por Experts em {fn(exp_v['nps'])}% "
                     f"({exp_v.get('share',0)}% das pesquisas"
                     f"{f', {sign(exp_mom)}{fn(exp_mom)} pp MoM' if exp_mom is not None else ''})"
                     f"{contrib_new}. ")

    # Oficinas
    def off_mom_str(o):
        if o['mom'] is None: return ''
        return f', {sign(o["mom"])}{fn(o["mom"])} pp MoM'

    if top_off and worst_off and worst_off['name'] != top_off['name'] and \
       (worst_off['nps'] or 100) < (top_off['nps'] or 0) - 10:
        text += (f"Por oficina, <strong>{top_off['name']}</strong> lidera em volume "
                 f"({top_off['share']}%, NPS {fn(top_off['nps'])}%{off_mom_str(top_off)})"
                 f", enquanto <strong>{worst_off['name']}</strong> concentra a maior detração "
                 f"({worst_off['share']}%, NPS {fn(worst_off['nps'])}%{off_mom_str(worst_off)}). ")
    elif top_off:
        offs_txt = ', '.join(
            f"<strong>{o['name']}</strong>: {fn(o['nps'])}% ({o['share']}%{off_mom_str(o)})"
            for o in offs[:2])
        text += f"Principais oficinas: {offs_txt}. "

    # Processo + CDU
    if proc and cdu_name and cdu_first:
        text += (f"No processo <strong>{proc}</strong>, a CDU com maior peso é "
                 f"<strong>{cdu_name}</strong> ({cdu_share}% das pesquisas): {cdu_first}.")
    elif cdu_name and cdu_first:
        text += f"CDU dominante: <strong>{cdu_name}</strong> ({cdu_share}% das pesquisas) — {cdu_first}."

    return f'<p style="font-size:13px;line-height:1.9;margin-bottom:10px;color:#333">{text}</p>'

# Destaques positivos
bullet_sellers = ''.join(build_narrative(grp, '🟢') for grp in destaques_pos)

# Bullets negativos
par_icon = '🟡' if (d_par['gap'] or 0) < 0 else '🟢'
pub_icon = '🔴' if (d_pub['mom'] or 0) < -2 else '🟡'
ei_icon  = '🔴'

bullet_partners = build_narrative('Partners',        par_icon)
bullet_pub      = build_narrative('Publicaciones',   pub_icon)
bullet_ei       = build_narrative('Exp. Impositiva', ei_icon)

# ── Next steps ────────────────────────────────────────────────────────
next_steps_parts = []
if (d_ei['gap'] or 0) < -10:
    next_steps_parts.append(
        f"Capacitação prioritária para Newbies em <strong>Exp. Impositiva</strong> — "
        f"gap de {fn(ei_gap_sen)} pp vs. Veteranos indica necessidade de treino em "
        f"{d_ei['top_proc'] or 'temas do processo top'}."
    )
if d_pub['mom'] and d_pub['mom'] < -2:
    c2c_str = f" e atendimento em C2C (NPS {fn(pub_c2c['nps'])}%)" if pub_c2c else ""
    next_steps_parts.append(
        f"Plano de ação para <strong>Publicaciones</strong> — queda de "
        f"{fn(d_pub['mom'])} pp MoM em {d_pub['top_proc'] or 'processo Afiliados'}"
        f"{c2c_str}."
    )
if par_newbie and (par_newbie['mom'] or 0) < -1:
    next_steps_parts.append(
        f"Gestão de capacitação Newbies em <strong>Partners</strong> — "
        f"{par_newbie['share']}% das consultas com queda de {fn(par_newbie['mom'])} pp MoM."
    )
if not next_steps_parts:
    next_steps_parts.append(
        "Manter monitoramento dos drivers acima da meta e investigar causas das quedas pontuais."
    )

# ── Monta HTML ────────────────────────────────────────────────────────
html = f'''<div style="border-left:4px solid #F39C12;padding-left:14px;margin-bottom:20px">
  <div style="font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">Highlights &amp; Análise</div>

  <p style="font-size:15px;font-weight:700;color:#222;margin-bottom:16px">
    {headline}
  </p>

  <p style="font-size:13px;font-weight:700;color:#333;margin-bottom:10px">Análise por driver:</p>

  {bullet_sellers}
  {bullet_partners}
  {bullet_pub}
  {bullet_ei}

  <p style="font-size:13px;font-weight:700;color:#333;margin-bottom:10px">Next steps:</p>

  <p style="font-size:13px;line-height:1.9;color:#444">
    {'<br><br>'.join(next_steps_parts)}
  </p>
</div>'''

with open('_exec_summary_sd.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('=== PREVIEW ===')
print(f'Headline: {headline}')
print(f'\nSellers: {bullet_sellers[:200]}...')
print(f'\nPartners: {bullet_partners[:200]}...')
print(f'\nPublicaciones: {bullet_pub[:200]}...')
print(f'\nExp. Impositiva: {bullet_ei[:200]}...')
print(f'\nNext steps: {next_steps_parts[0][:150]}...')
print('\nSalvo em _exec_summary_sd.html')

# ══════════════════════════════════════════════════════════════════════
# VERSÃO SEMANAL — _exec_summary_wk_sd.html (S1 vs S2)
# ══════════════════════════════════════════════════════════════════════
wh = ns.get('weekly_history', {})   # {driver: {label: (p,d,s)}}
wd_drv = ns.get('weekly_driver', {})
S1_LBL = ns.get('S1_LABEL', 'S1')
S2_LBL = ns.get('S2_LABEL', 'S2')

# Labels das semanas (últimas duas entradas de WEEK_LABELS)
wk_labels = ns.get('WEEK_LABELS', [])
wk_s1 = wk_labels[-1] if wk_labels else 'S1'
wk_s2 = wk_labels[-2] if len(wk_labels) >= 2 else 'S2'

def grp_nps_wk(drvs, lbl):
    p   = sum(wh.get(d,{}).get(lbl,(0,0,0))[0] for d in drvs)
    det = sum(wh.get(d,{}).get(lbl,(0,0,0))[1] for d in drvs)
    s   = sum(wh.get(d,{}).get(lbl,(0,0,0))[2] for d in drvs)
    return nps(p, det, s), s

def tgt_wk(drvs):
    drv_tgts = pt.get('weekly', {}).get(wk_s1, {}).get('drivers', {})
    wn = sum(wh.get(d,{}).get(wk_s1,(0,0,0))[2] * drv_tgts.get(d, nt)
             for d in drvs if drv_tgts.get(d))
    wd2 = sum(wh.get(d,{}).get(wk_s1,(0,0,0))[2] for d in drvs if drv_tgts.get(d))
    return round(wn/wd2, 2) if wd2 else nt

def _proc_wk_change(drvs):
    """Encontra o processo com maior queda WoW (S1 vs S2) a partir do mb."""
    p_s1, p_s2 = {}, {}
    for drv in drvs:
        for proc, v in mb.get('S1', {}).get(drv, {}).get('P', {}).items():
            r = p_s1.setdefault(proc, {'p':0,'d':0,'s':0})
            r['p']+=v.get('p',0); r['d']+=v.get('d',0); r['s']+=v.get('s',0)
        for proc, v in mb.get('S2', {}).get(drv, {}).get('P', {}).items():
            r = p_s2.setdefault(proc, {'p':0,'d':0,'s':0})
            r['p']+=v.get('p',0); r['d']+=v.get('d',0); r['s']+=v.get('s',0)
    changes = []
    total_s1 = sum(v['s'] for v in p_s1.values()) or 1
    for proc in p_s1:
        if proc not in p_s2 or p_s1[proc]['s'] < 10: continue
        n1 = nps(p_s1[proc]['p'], p_s1[proc]['d'], p_s1[proc]['s'])
        n2 = nps(p_s2[proc]['p'], p_s2[proc]['d'], p_s2[proc]['s'])
        if n1 is not None and n2 is not None:
            changes.append({'proc': proc, 'nps_s1': n1, 'nps_s2': n2,
                            'delta': round(n1-n2, 1),
                            'vol': round(100*p_s1[proc]['s']/total_s1, 0)})
    if not changes: return None
    changes.sort(key=lambda x: x['delta'])
    return changes[0]  # maior queda

# NPS semanal por grupo
wk_drv_data = {}
for grp, drvs in SD.items():
    nc, sc = grp_nps_wk(drvs, wk_s1)
    np2, _ = grp_nps_wk(drvs, wk_s2)
    tg     = tgt_wk(drvs)
    _pa_neg = pa.get(grp, {}).get('top_neg', {})
    wk_drv_data[grp] = {
        'nc': nc, 'np': np2, 'sc': sc, 'tgt': tg,
        'gap': round(nc - tg, 1) if nc is not None else None,
        'mom': round(nc - np2, 1) if nc is not None and np2 is not None else None,
        'sr_mai': seniority(drvs, 'S1'),   # breakdown S1
        'sr_abr': seniority(drvs, 'S2'),   # breakdown S2
        'off_mai': office_summary(drvs, 'S1'),
        'top_proc': _pa_neg.get('proc', ''),
        'top_proc_cdu': _pa_neg.get('detail', {}).get('cdu', {}),
        'top_proc_wk': _proc_wk_change(drvs),
    }

def cdu_narrative_wk(grp):
    cats = rc.get(grp, {}).get('categories_wk') or rc.get(grp, {}).get('categories_mon') or []
    if not cats: return None, None, 0
    top = cats[0]
    return top.get('sub_pattern',''), top.get('narrative',''), top.get('share_pct',0)

def build_narrative_wk(grp, icon):
    v = wk_drv_data[grp]
    if v['nc'] is None:
        return ''

    status = (f"<strong>{sign(v['gap'])}{fn(v['gap'])} pp acima da meta</strong>"
              if (v['gap'] or 0) >= 0 else
              f"<strong>{fn(abs(v['gap']))} pp abaixo da meta</strong>")
    if   (v['mom'] or 0) > 0.5:  trend_txt = f"Alta de <strong>+{fn(v['mom'])} pp WoW</strong>. "
    elif (v['mom'] or 0) < -0.5: trend_txt = f"Queda de <strong>{fn(v['mom'])} pp WoW</strong>. "
    else:                         trend_txt = "Performance estável na semana. "

    text = (f"{icon} <strong>{esc(grp)}</strong>: NPS de <strong>{fn(v['nc'])}%</strong>, "
            f"{status} ({fn(v['tgt'])}%). {trend_txt}")

    sr = v['sr_mai']; sr_abr = v['sr_abr']
    exp_k = next((k for k in sr if 'expert' in k.lower()), None)
    new_k = next((k for k in sr if 'newbie' in k.lower()), None)
    if exp_k and new_k:
        ev = sr[exp_k]; nv = sr[new_k]
        ea = sr_abr.get(next((k for k in sr_abr if 'expert' in k.lower()),''), {})
        na2 = sr_abr.get(next((k for k in sr_abr if 'newbie' in k.lower()),''), {})
        tot = sum(x.get('s',0) for x in sr.values()) or 1
        es = round(100*ev['s']/tot) if ev.get('s') else 0
        ns_ = round(100*nv['s']/tot) if nv.get('s') else 0
        em = round(ev['nps']-ea['nps'],1) if ev.get('nps') and ea.get('nps') else None
        nm = round(nv['nps']-na2['nps'],1) if nv.get('nps') and na2.get('nps') else None
        gs = round(ev['nps']-nv['nps'],1) if ev.get('nps') and nv.get('nps') else None
        if gs and gs > 15 and (v['gap'] or 0) < 0:
            text += (f"Gap de senioridade: Experts {fn(ev['nps'])}% ({es}%"
                     f"{f', {sign(em)}{fn(em)} pp WoW' if em is not None else ''})"
                     f" vs. Newbies {fn(nv['nps'])}% ({ns_}%"
                     f"{f', {sign(nm)}{fn(nm)} pp WoW' if nm is not None else ''})"
                     f" — gap de <strong>{fn(gs)} pp</strong>. ")
        else:
            text += (f"Experts: {fn(ev['nps'])}% ({es}%"
                     f"{f', {sign(em)}{fn(em)} pp WoW' if em is not None else ''})"
                     f"; Newbies: {fn(nv['nps'])}% ({ns_}%"
                     f"{f', {sign(nm)}{fn(nm)} pp WoW' if nm is not None else ''})"
                     f"{f' — gap de {fn(gs)} pp' if gs is not None else ''}. ")

    offs = v.get('off_mai', [])
    if offs:
        def _oms(o):
            m = f", {sign(o['mom'])}{fn(o['mom'])} pp WoW" if o['mom'] is not None else ""
            return f"{o['share']}%, NPS {fn(o['nps'])}%{m}"
        worst = min(offs, key=lambda x: x['nps'] if x['nps'] is not None else 999)
        top_o = offs[0]
        if worst['name'] != top_o['name'] and (worst['nps'] or 100) < (top_o['nps'] or 0) - 10:
            text += (f"Por oficina, <strong>{top_o['name']}</strong> lidera ({_oms(top_o)})"
                     f", maior detração em <strong>{worst['name']}</strong> ({_oms(worst)}). ")
        else:
            text += "Principais oficinas: " + "; ".join(
                f"<strong>{o['name']}</strong>: {fn(o['nps'])}% ({o['share']}%"
                f"{', ' + sign(o['mom']) + fn(o['mom']) + ' pp WoW' if o['mom'] is not None else ''})"
                for o in offs[:2]) + ". "

    # Processo que mais caiu WoW + CDU vinculado a ele
    top_wk   = v.get('top_proc_wk')    # {'proc', 'nps_s1', 'nps_s2', 'delta', 'vol'}
    top_proc = v.get('top_proc', '')   # processo top_neg mensal (tem CDU detalhado)
    proc_cdu = v.get('top_proc_cdu', {})  # CDUs do processo top_neg

    if top_wk and (v['mom'] or 0) < -0.5:
        # Queda WoW — mostrar processo responsável + motivos dos detratores
        proc_wk_name = top_wk['proc']
        delta_wk     = top_wk['delta']
        vol_wk       = top_wk['vol']
        text += (f"O processo <strong>{esc(proc_wk_name)}</strong> foi o principal vetor "
                 f"da queda ({int(vol_wk)}% do vol, <strong>{fn(delta_wk)} pp WoW</strong>). ")

        # Tentar obter CDU do PRÓPRIO processo de queda (se coincide com top_neg)
        if proc_wk_name == top_proc and proc_cdu:
            top_cdu_item = sorted(proc_cdu.items(), key=lambda x: -x[1].get('s', 0))
            if top_cdu_item:
                cdu_n, cdu_v = top_cdu_item[0]
                cdu_s_tot = sum(c.get('s',0) for c in proc_cdu.values()) or 1
                cdu_share_v = round(100 * cdu_v.get('s', 0) / cdu_s_tot, 0)
                text += (f"No processo, o principal motivo dos detratores é "
                         f"<strong>{esc(cdu_n)}</strong> "
                         f"({int(cdu_share_v)}% das pesquisas).")
        else:
            # Processo WoW ≠ top_neg: usar motivos de transcrições dos detratores
            contacts, pains, n_det = _get_det_themes(grp)
            if contacts and n_det > 0:
                mot_parts = [f"<strong>{esc(c[0])}</strong> ({c[1]}/{n_det})" for c in contacts[:2]]
                mot_str = " e ".join(mot_parts)
                pain_str = (f" — <strong>{esc(pains[0][0])}</strong> como dor dominante"
                            if pains else "")
                text += (f"Detratores do driver apontam: {mot_str}{pain_str}.")
            else:
                # Fallback: CDU sem atribuição enganosa ao processo de queda
                cats = rc.get(grp, {}).get('categories_wk') or rc.get(grp, {}).get('categories_mon') or []
                if cats:
                    top_cat = cats[0]
                    cdu_n   = top_cat.get('sub_pattern', '')
                    cdu_pct = top_cat.get('share_pct', 0)
                    cdu_narr = (top_cat.get('narrative', '') or '').split('. ')[0]
                    if cdu_n:
                        text += (f"Principal CDU do driver: <strong>{esc(cdu_n)}</strong> "
                                 f"({cdu_pct}% das pesquisas)"
                                 f"{f' — {esc(cdu_narr)}' if cdu_narr else ''}.")
    else:
        # Sem queda significativa — mostrar CDU vinculado ao processo correto
        cdu_name, cdu_narr, cdu_share = cdu_narrative_wk(grp)
        if cdu_name and cdu_narr:
            cdu_desc = cdu_narr.split('. ')[0] if '. ' in cdu_narr else cdu_narr
            proc_str = (f" no processo <strong>{esc(top_proc)}</strong>" if top_proc else "")
            text += (f"CDU dominante{proc_str}: <strong>{esc(cdu_name)}</strong> "
                     f"({cdu_share}% das pesquisas) — {esc(cdu_desc)}.")

    return f'<p style="font-size:13px;line-height:1.9;margin-bottom:10px;color:#333">{text}</p>'

# Consolida semanal
all_sd_wk = [d for drvs in SD.values() for d in drvs]
nc_cons_wk, _ = grp_nps_wk(all_sd_wk, wk_s1)
np_cons_wk, _ = grp_nps_wk(all_sd_wk, wk_s2)
cons_tgt_wk   = pt.get('weekly', {}).get(wk_s1, {}).get('consolidated', nt)
gap_cons_wk   = round(nc_cons_wk - cons_tgt_wk, 2) if nc_cons_wk else None
mom_cons_wk   = round(nc_cons_wk - np_cons_wk, 2)  if nc_cons_wk and np_cons_wk else None

headline_wk = (f"NPS de {fn(nc_cons_wk)}% — "
               f"{sign(gap_cons_wk)}{fn(gap_cons_wk)} pp vs. meta ({fn(cons_tgt_wk)}%) "
               f"e {sign(mom_cons_wk)}{fn(mom_cons_wk)} pp WoW ({S2_LBL} → {S1_LBL})")

# Destaques e drivers negativos (mesma lógica do mensal)
def wk_score(grp):
    v = wk_drv_data[grp]
    return (1 if (v['gap'] or 0) >= 0 else 0) * 100 + (v['mom'] or 0)

# Drivers com bullets próprios — não entram em wk_pos para evitar duplicatas
_WK_FIXED = {'Partners', 'Publicaciones', 'Exp. Impositiva'}
wk_destaques = sorted(
    [g for g in wk_drv_data.keys() if g not in _WK_FIXED],
    key=lambda g: -wk_score(g)
)
wk_pos = [g for g in wk_destaques
          if (wk_drv_data[g]['gap'] or 0) >= 0 or (wk_drv_data[g]['mom'] or 0) > 1][:3]

bullet_sellers_wk  = ''.join(build_narrative_wk(g, '🟢') for g in wk_pos)
bullet_partners_wk = build_narrative_wk('Partners',        '🟡' if (wk_drv_data['Partners']['gap'] or 0) < 0 else '🟢')
bullet_pub_wk      = build_narrative_wk('Publicaciones',   '🔴' if (wk_drv_data['Publicaciones']['mom'] or 0) < -2 else '🟡')
bullet_ei_wk       = build_narrative_wk('Exp. Impositiva', '🔴')

# Next steps semanal
wk_next = []
ei_wk = wk_drv_data['Exp. Impositiva']
pub_wk = wk_drv_data['Publicaciones']
par_wk = wk_drv_data['Partners']
ei_gs_wk = None
ei_sr = ei_wk.get('sr_mai', {})
exp_k2 = next((k for k in ei_sr if 'expert' in k.lower()), None)
new_k2 = next((k for k in ei_sr if 'newbie' in k.lower()), None)
if exp_k2 and new_k2 and ei_sr.get(exp_k2, {}).get('nps') and ei_sr.get(new_k2, {}).get('nps'):
    ei_gs_wk = round(ei_sr[exp_k2]['nps'] - ei_sr[new_k2]['nps'], 1)

if (ei_wk['gap'] or 0) < -10:
    wk_next.append(f"Capacitação Newbies em <strong>Exp. Impositiva</strong>"
                   + (f" — gap de {fn(ei_gs_wk)} pp vs. Veteranos." if ei_gs_wk else "."))
if (pub_wk['mom'] or 0) < -2:
    wk_next.append(f"Monitorar queda de <strong>Publicaciones</strong> "
                   f"({fn(pub_wk['mom'])} pp WoW) — processo {pub_wk.get('top_proc','Afiliados ML')}.")
if not wk_next:
    wk_next.append("Manter monitoramento semanal e investigar causas de queda.")

html_wk = f'''<div style="border-left:4px solid #F39C12;padding-left:14px;margin-bottom:20px">
  <div style="font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">Highlights &amp; Análise — Semana</div>

  <p style="font-size:15px;font-weight:700;color:#222;margin-bottom:16px">
    {headline_wk}
  </p>

  <p style="font-size:13px;font-weight:700;color:#333;margin-bottom:10px">Análise por driver:</p>

  {bullet_sellers_wk}
  {bullet_partners_wk}
  {bullet_pub_wk}
  {bullet_ei_wk}

  <p style="font-size:13px;font-weight:700;color:#333;margin-bottom:10px">Next steps:</p>

  <p style="font-size:13px;line-height:1.9;color:#444">
    {'<br><br>'.join(wk_next)}
  </p>
</div>'''

with open('_exec_summary_wk_sd.html', 'w', encoding='utf-8') as f:
    f.write(html_wk)

print(f'\nSemanal Headline: {headline_wk}')
print('Salvo em _exec_summary_wk_sd.html')

# ── VIG exec summary (VIG vs S1) ─────────────────────────────────────
dv      = ns.get('drivers_vigente', {})
VIG_LBL = ns.get('VIG_LABEL', '')
all_sd_vig_drvs = [d for drvs in SD.values() for d in drvs]
sv_total = sum(dv.get(d,(0,0,0))[2] for d in all_sd_vig_drvs)

if VIG_LBL and sv_total > 0:
    # Constrói vig_drv_data: NPS VIG + contexto de breakdown do S1
    vig_drv_data = {}
    for grp, drvs in SD.items():
        p   = sum(dv.get(d,(0,0,0))[0] for d in drvs)
        det = sum(dv.get(d,(0,0,0))[1] for d in drvs)
        s   = sum(dv.get(d,(0,0,0))[2] for d in drvs)
        nc  = nps(p, det, s)
        nc_s1, _ = grp_nps_wk(drvs, wk_s1)
        tg = tgt_wk(drvs)
        vig_drv_data[grp] = {
            'nc': nc, 'np': nc_s1 or 0, 'sc': s, 'tgt': tg,
            'gap':  round(nc - tg, 1)           if nc is not None else None,
            'mom':  round(nc - (nc_s1 or 0), 1) if nc is not None else None,
            'sr_mai':  seniority(drvs, 'S1'),   # breakdown S1 como referência
            'sr_abr':  seniority(drvs, 'S2'),
            'off_mai': office_summary(drvs, 'S1'),
            'top_proc': pa.get(grp, {}).get('top_neg', {}).get('proc', ''),
        }

    # Consolida VIG
    pv   = sum(dv.get(d,(0,0,0))[0] for d in all_sd_vig_drvs)
    dv2  = sum(dv.get(d,(0,0,0))[1] for d in all_sd_vig_drvs)
    nc_cons_vig = nps(pv, dv2, sv_total)
    tgt_vig     = pt.get('weekly', {}).get(wk_s1, {}).get('consolidated', nt)
    gap_vig     = round(nc_cons_vig - tgt_vig, 2) if nc_cons_vig else None
    mom_vig     = round(nc_cons_vig - (nc_cons_wk or 0), 2) if nc_cons_vig and nc_cons_wk else None

    headline_vig = (f"NPS de {fn(nc_cons_vig)}% — "
                    f"{sign(gap_vig)}{fn(gap_vig)} pp vs. meta ({fn(tgt_vig)}%) "
                    f"e {sign(mom_vig)}{fn(mom_vig)} pp WoW ({S1_LBL} → {VIG_LBL})")

    # Gera bullets reaproveitando build_narrative_wk com vig_drv_data
    _saved = dict(wk_drv_data)
    wk_drv_data.clear(); wk_drv_data.update(vig_drv_data)

    _vig_destaques = sorted(
        [g for g in vig_drv_data if g not in _WK_FIXED],
        key=lambda g: -((1 if (vig_drv_data[g]['gap'] or 0) >= 0 else 0)*100 + (vig_drv_data[g]['mom'] or 0))
    )
    _vig_pos = [g for g in _vig_destaques
                if (vig_drv_data[g]['gap'] or 0) >= 0 or (vig_drv_data[g]['mom'] or 0) > 1][:3]

    b_sell = ''.join(build_narrative_wk(g, '🟢') for g in _vig_pos)
    b_par  = build_narrative_wk('Partners',        '🟡' if (vig_drv_data['Partners']['gap'] or 0) < 0 else '🟢')
    b_pub  = build_narrative_wk('Publicaciones',   '🔴' if (vig_drv_data['Publicaciones']['mom'] or 0) < -2 else '🟡')
    b_ei   = build_narrative_wk('Exp. Impositiva', '🔴')

    wk_drv_data.clear(); wk_drv_data.update(_saved)

    # Next steps VIG
    ei_v = vig_drv_data['Exp. Impositiva']; pub_v = vig_drv_data['Publicaciones']
    ei_gs_v = None
    ei_sr_v = ei_v.get('sr_mai', {})
    exp_kv = next((k for k in ei_sr_v if 'expert' in k.lower()), None)
    new_kv = next((k for k in ei_sr_v if 'newbie' in k.lower()), None)
    if exp_kv and new_kv and ei_sr_v.get(exp_kv,{}).get('nps') and ei_sr_v.get(new_kv,{}).get('nps'):
        ei_gs_v = round(ei_sr_v[exp_kv]['nps'] - ei_sr_v[new_kv]['nps'], 1)
    vig_next = []
    if (ei_v['gap'] or 0) < -10:
        vig_next.append(f"Capacitação Newbies em <strong>Exp. Impositiva</strong>"
                        + (f" — gap de {fn(ei_gs_v)} pp vs. Veteranos indica necessidade de treino." if ei_gs_v else "."))
    if (pub_v['mom'] or 0) < -2:
        vig_next.append(f"Monitorar queda de <strong>Publicaciones</strong> "
                        f"({fn(pub_v['mom'])} pp WoW) — processo {pub_v.get('top_proc','Afiliados ML')}.")
    if not vig_next:
        vig_next.append("Semana vigente em andamento — manter monitoramento diário.")

    html_vig = f'''<div style="border-left:4px solid #F39C12;padding-left:14px;margin-bottom:20px">
  <div style="font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">Highlights &amp; Análise — Semana Vigente</div>

  <p style="font-size:15px;font-weight:700;color:#222;margin-bottom:16px">
    {headline_vig}
  </p>

  <p style="font-size:13px;font-weight:700;color:#333;margin-bottom:10px">Análise por driver:</p>

  {b_sell}
  {b_par}
  {b_pub}
  {b_ei}

  <p style="font-size:13px;font-weight:700;color:#333;margin-bottom:10px">Next steps:</p>

  <p style="font-size:13px;line-height:1.9;color:#444">
    {"<br><br>".join(vig_next)}
  </p>
</div>'''

    with open('_exec_summary_vig_sd.html', 'w', encoding='utf-8') as f:
        f.write(html_vig)
    print(f'VIG Headline: {headline_vig}')
    print('Salvo em _exec_summary_vig_sd.html')
