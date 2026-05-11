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

# Identifica quem está acima/abaixo da meta para o headline
above_tgt = [g for g, v in drv_data.items() if (v['gap'] or 0) >= 0]
below_tgt = [g for g, v in drv_data.items() if (v['gap'] or 0) < 0]

headline_pos = ', '.join(above_tgt[:3]) if above_tgt else 'múltiplos drivers'
headline_neg = ' e '.join(below_tgt) if below_tgt else ''

if headline_neg:
    headline = (f"{sign(gap_cons)}{fn(gap_cons)} pp vs. meta | "
                f"{headline_pos} sustentam resultado — atenção em {headline_neg}")
else:
    headline = (f"{sign(gap_cons)}{fn(gap_cons)} pp vs. meta | "
                f"Todos os drivers acima da meta — monitorar tendências de queda")

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

def build_bullet(grp, icon):
    """Monta bullet completo com NPS + senioridade + oficina + CDU."""
    v = drv_data[grp]
    # ── Linha principal
    main = (f"{icon} <strong>{grp}</strong> — NPS <strong>{fn(v['nc'])}%</strong> "
            f"({sign(v['gap'])}{fn(v['gap'])} pp vs. meta, MoM {sign(v['mom'])}{fn(v['mom'])} pp).")
    parts = [main]

    # ── Senioridade
    sr = v['sr_mai']
    sr_abr = v['sr_abr']
    exp_k = next((k for k in sr if 'expert' in k.lower()), None)
    new_k = next((k for k in sr if 'newbie' in k.lower()), None)
    if exp_k and new_k:
        exp_v = sr[exp_k]; new_v = sr[new_k]
        exp_abr = sr_abr.get(next((k for k in sr_abr if 'expert' in k.lower()), ''), {})
        new_abr = sr_abr.get(next((k for k in sr_abr if 'newbie' in k.lower()), ''), {})
        exp_mom = round(exp_v['nps']-exp_abr['nps'],1) if exp_v.get('nps') and exp_abr.get('nps') else None
        new_mom = round(new_v['nps']-new_abr['nps'],1) if new_v.get('nps') and new_abr.get('nps') else None
        gap_sen = round(exp_v['nps']-new_v['nps'],1) if exp_v.get('nps') and new_v.get('nps') else None
        sr_line = (f"Senioridade: Expert {fn(exp_v['nps'])}% ({exp_v['share']}% do vol"
                   f"{f', MoM {sign(exp_mom)}{fn(exp_mom)} pp' if exp_mom is not None else ''})"
                   f" | Newbie {fn(new_v['nps'])}% ({new_v['share']}% do vol"
                   f"{f', MoM {sign(new_mom)}{fn(new_mom)} pp' if new_mom is not None else ''})"
                   f"{f' — gap de {fn(gap_sen)} pp' if gap_sen is not None else ''}.")
        parts.append(sr_line)

    # ── Oficinas
    offs = v.get('off_mai', [])
    if offs:
        top_off = offs[0]
        worst_off = min(offs, key=lambda x: x['nps'] if x['nps'] is not None else 999)

        def off_detail(o):
            m = f", MoM {sign(o['mom'])}{fn(o['mom'])} pp" if o['mom'] is not None else ""
            return f"{o['share']}%, NPS {fn(o['nps'])}%{m}"

        if worst_off['name'] != top_off['name'] and (worst_off['nps'] or 100) < (top_off['nps'] or 0) - 10:
            off_line = (f"Oficinas: maior volume em <strong>{top_off['name']}</strong> "
                        f"({off_detail(top_off)})"
                        f"; maior detração em <strong>{worst_off['name']}</strong> "
                        f"({off_detail(worst_off)}).")
        else:
            off_parts = [f"<strong>{o['name']}</strong>: {fn(o['nps'])}% ({o['share']}%"
                         f"{', ' + sign(o['mom']) + fn(o['mom']) + ' pp MoM' if o['mom'] is not None else ''})"
                         for o in offs[:2]]
            off_line = f"Oficinas: {'; '.join(off_parts)}."
        parts.append(off_line)

    # ── CDU resumo do processo top
    cdu_name, cdu_narr, cdu_share = cdu_narrative(grp)
    if cdu_name and cdu_narr:
        proc = v.get('top_proc','')
        proc_str = f" ({proc})" if proc else ""
        # Remove a parte operacional da narrativa para não repetir
        cdu_desc = cdu_narr.split('. ')[0] if '. ' in cdu_narr else cdu_narr
        cdu_line = (f"Principal CDU{proc_str}: <strong>{cdu_name}</strong> "
                    f"({cdu_share}% das pesquisas) — {cdu_desc}.")
        parts.append(cdu_line)

    # Formata como parágrafos aninhados
    return (f'<p style="font-size:13px;line-height:1.8;margin-bottom:4px">{parts[0]}</p>'
            + ''.join(f'<p style="font-size:12px;line-height:1.7;margin-bottom:2px;margin-left:14px;color:#444">'
                      f'↳ {p}</p>' for p in parts[1:]))

# Destaques positivos
destaque_lines = []
for grp in destaques_pos:
    destaque_lines.append(build_bullet(grp, '🟢'))

top_destaque = destaques_pos[0] if destaques_pos else None
top_v = drv_data[top_destaque] if top_destaque else {}
top_mom_str = f", maior alta do período com +{fn(top_v.get('mom'))} pp MoM" if (top_v.get('mom') or 0) > 3 else ""

bullet_sellers = (
    f'<p style="font-size:13px;font-weight:700;color:#1a7a42;margin-bottom:8px">'
    f'🟢 Destaques positivos{top_mom_str}</p>'
    + ''.join(destaque_lines)
)

# Bullets negativos — usa o mesmo build_bullet
par_icon = '🟡' if (d_par['gap'] or 0) < 0 else '🟢'
pub_icon = '🔴' if (d_pub['mom'] or 0) < -2 else '🟡'
ei_icon  = '🔴'

bullet_partners = build_bullet('Partners',        par_icon)
bullet_pub      = build_bullet('Publicaciones',   pub_icon)
bullet_ei       = build_bullet('Exp. Impositiva', ei_icon)

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
def driver_block(bullet_html, border_color):
    return (f'<div style="margin-bottom:14px;padding:10px 14px;background:#fafbfc;'
            f'border-left:3px solid {border_color};border-radius:0 6px 6px 0">'
            f'{bullet_html}</div>')

# Cor por status
par_color  = '#F39C12' if (d_par['gap'] or 0) < 0 else '#00A650'
pub_color  = '#E84142' if (d_pub['mom'] or 0) < -2 else '#F39C12'
ei_color   = '#E84142'
pos_color  = '#00A650'

html = f'''<div style="border-left:4px solid #F39C12;padding-left:14px;margin-bottom:20px">
  <div style="font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">Highlights &amp; Análise</div>

  <p style="font-size:15px;font-weight:700;color:#222;margin-bottom:16px">
    {headline}
  </p>

  <p style="font-size:13px;font-weight:700;color:#333;margin-bottom:10px">Análise por driver:</p>

  {driver_block(bullet_sellers,  pos_color)}
  {driver_block(bullet_partners, par_color)}
  {driver_block(bullet_pub,      pub_color)}
  {driver_block(bullet_ei,       ei_color)}

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
