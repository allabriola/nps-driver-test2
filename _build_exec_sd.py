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

# Bullet Sellers (segmentos LT/Mature/MeliPro)
seg_lines = []
for seg in ['LT', 'Mature', 'MeliPro']:
    v = seg_data[seg]
    c = seg_contrib[seg]
    status = 'acima' if (v['gap'] or 0) >= 0 else 'abaixo'
    seg_lines.append(
        f"<strong>{seg} {sign(c)}{fn(c)} pp</strong> (NPS {fn(v['nc'])}%, "
        f"{sign(v['gap'])}{fn(v['gap'])} pp vs. meta, MoM {sign(v['mom'])}{fn(v['mom'])} pp)"
    )
n_above_seg = sum(1 for s in SEG if (seg_data[s]['gap'] or 0) >= 0)
bullet_sellers = (
    f"🟢 <strong>Sellers</strong> — Evolução MoM com {n_above_seg} segmento{'s' if n_above_seg>1 else ''} "
    f"acima da meta. Consolidado SD: <strong>{fn(nc_cons)}%</strong> "
    f"({sign(gap_cons)}{fn(gap_cons)} pp vs. meta, MoM {sign(mom_cons)}{fn(mom_cons)} pp). "
    f"Impacto no período: {'; '.join(seg_lines)}."
)

# Bullet Partners
par_new = par_newbie
par_exp_nps = drv_data['Partners']['sr_mai'].get(
    next((k for k in drv_data['Partners']['sr_mai'] if 'expert' in k.lower()),''), {}).get('nps')
par_exp_nps_abr = drv_data['Partners']['sr_abr'].get(
    next((k for k in drv_data['Partners']['sr_abr'] if 'expert' in k.lower()),''), {}).get('nps')

par_icon = '🟡' if (d_par['gap'] or 0) < 0 else '🟢'
bullet_partners = (
    f"{par_icon} <strong>Partners</strong> — "
    f"<strong>{sign(d_par['gap'])}{fn(d_par['gap'])} pp vs. meta</strong> e "
    f"MoM <strong>{sign(d_par['mom'])}{fn(d_par['mom'])} pp</strong>. "
)
if d_par['mom'] and d_par['mom'] > 0:
    bullet_partners += f"Evolução positiva no período. "
if par_new:
    par_gap_tgt_new = round(par_new['nps'] - d_par['tgt'], 1) if par_new['nps'] else None
    bullet_partners += (
        f"Newbies representam <strong>{par_new['share']}% das consultas</strong> "
        f"com NPS de {fn(par_new['nps'])}% "
        f"({sign(par_new['mom'])}{fn(par_new['mom'])} pp MoM, "
        f"{sign(par_gap_tgt_new) if par_gap_tgt_new else ''}{fn(par_gap_tgt_new)} pp vs. meta). "
    )
if drv_data['Partners']['top_cdu']:
    bullet_partners += f"Principal CDU de detratores: <em>{drv_data['Partners']['top_cdu']}</em>."

# Bullet Publicaciones
pub_icon = '🟡' if (d_pub['gap'] or 0) >= 0 else '🔴'
if d_pub['mom'] and d_pub['mom'] < -2:
    pub_icon = '🔴'
bullet_pub = (
    f"{pub_icon} <strong>Publicaciones</strong> — "
    f"<strong>{sign(d_pub['gap'])}{fn(d_pub['gap'])} pp vs. meta</strong> e "
    f"MoM <strong>{sign(d_pub['mom'])}{fn(d_pub['mom'])} pp</strong>. "
    f"Queda no principal processo: <em>{d_pub['top_proc']}</em>. "
)
if pub_newbie:
    pub_gap_tgt = round(pub_newbie['nps'] - d_pub['tgt'], 1) if pub_newbie['nps'] else None
    bullet_pub += (
        f"Newbies representam <strong>{pub_newbie['share']}%</strong> do volume "
        f"com queda de <strong>{sign(pub_newbie['mom'])}{fn(pub_newbie['mom'])} pp MoM</strong>"
    )
    if pub_gap_tgt is not None:
        bullet_pub += f" e {sign(pub_gap_tgt)}{fn(pub_gap_tgt)} pp vs. meta"
    bullet_pub += ". "
if pub_c2c:
    bullet_pub += (
        f"Principal oportunidade em <strong>C2C ({pub_c2c['share']}% do volume, "
        f"NPS {fn(pub_c2c['nps'])}%)</strong> — gap expressivo vs. CHAT. "
    )
    if drv_data['Publicaciones']['top_cdu']:
        bullet_pub += f"CDU dominante: <em>{drv_data['Publicaciones']['top_cdu']}</em>."

# Bullet Exp. Impositiva
ei_icon = '🔴' if (d_ei['gap'] or 0) < -5 else '🟡'
bullet_ei = (
    f"{ei_icon} <strong>Exp. Impositiva</strong> — "
    f"<strong>{sign(d_ei['gap'])}{fn(d_ei['gap'])} pp vs. meta</strong> e "
    f"MoM <strong>{sign(d_ei['mom'])}{fn(d_ei['mom'])} pp</strong>. "
)
if ei_newbie and ei_gap_sen:
    bullet_ei += (
        f"Queda concentrada em Newbies "
        f"(<strong>{sign(ei_newbie['mom'])}{fn(ei_newbie['mom'])} pp MoM</strong>, "
        f"gap de <strong>{fn(ei_gap_sen)} pp vs. Veteranos</strong>), "
        f"com {fn(ei_newbie['nps'])}% vs. meta de {fn(d_ei['tgt'])}%. "
    )
ei_c2c = ch_summary('Exp. Impositiva', 'C2C')
if ei_c2c:
    bullet_ei += (
        f"Canal C2C ({ei_c2c['share']}% do volume) com NPS de {fn(ei_c2c['nps'])}%, "
        f"concentrando os principais casos de detração. "
    )
if d_ei['top_proc']:
    bullet_ei += f"Processo mais ofensor: <em>{d_ei['top_proc']}</em>."

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
if par_new and (par_new['mom'] or 0) < -1:
    next_steps_parts.append(
        f"Gestão de capacitação Newbies em <strong>Partners</strong> — "
        f"{par_new['share']}% das consultas com queda de {fn(par_new['mom'])} pp MoM."
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

  <p style="font-size:13px;line-height:1.8;margin-bottom:10px">
    {bullet_sellers}
  </p>

  <p style="font-size:13px;line-height:1.8;margin-bottom:10px">
    {bullet_partners}
  </p>

  <p style="font-size:13px;line-height:1.8;margin-bottom:10px">
    {bullet_pub}
  </p>

  <p style="font-size:13px;line-height:1.8;margin-bottom:20px">
    {bullet_ei}
  </p>

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
