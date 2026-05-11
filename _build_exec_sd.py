#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera _exec_summary_sd.html com análise automática baseada nos dados reais do dashboard.
Estrutura: Sellers (segmentos) | Partners | Publicaciones | Exp. Impositiva
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

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
    if not cats: return None, None
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
