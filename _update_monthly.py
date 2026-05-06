#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza generate_html_gerencia.py com dados mensais finais.
- Abril: substitui dados parciais pelos dados finais do BQ
- Maio: adiciona dados WTD (1-5/mai)
"""
import json, re

with open('_monthly_result.json', encoding='utf-8') as f:
    monthly_data = json.load(f)

ABR = monthly_data['Abr_final']   # dados finais de Abril
MAI = monthly_data['Mai_wtd']     # dados WTD de Maio

with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()

# ── 1. Labels SECTION 1 ──────────────────────────────────────────
src = re.sub(r'(M1_LABEL\s*=\s*)"[^"]*"', r'\1"Maio 2026"', src)
src = re.sub(r'(M2_LABEL\s*=\s*)"[^"]*"', r'\1"Abril 2026"', src)

# ── 2. MONTH_LABELS ──────────────────────────────────────────────
src = re.sub(
    r'(MONTH_LABELS\s*=\s*)\[.*?\]',
    r'\1["Jan", "Fev", "Mar", "Abr", "Mai"]',
    src
)

# ── 3. Helpers ───────────────────────────────────────────────────
def fmt_tuple(p, d, s):
    return f"({p},{d},{s})"

def pad(name, width=42):
    return f'"{name}":{" " * max(1, width - len(name))}'

# ── 4. monthly_driver  (M2=Abr final, M1=Mai WTD) ────────────────
# Reconstrói o bloco inteiro
stop3 = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop3.start()], 'g', 'exec'), ns)

old_md = src[src.find('monthly_driver = {'):src.find('\n}', src.find('monthly_driver = {'))+2]

lines_md = ['monthly_driver = {']
for drv in ns['monthly_driver']:
    p_abr, d_abr, s_abr = ABR.get(drv, (0,0,0))
    p_mai, d_mai, s_mai = MAI.get(drv, (0,0,0))
    lines_md.append(f'    {pad(drv)}{{"M2":{fmt_tuple(p_abr,d_abr,s_abr)}, "M1":{fmt_tuple(p_mai,d_mai,s_mai)}}},')
lines_md.append('}')
new_md = '\n'.join(lines_md)
src = src.replace(old_md, new_md)

# ── 5. monthly_history  (substitui Abr, acrescenta Mai) ──────────
old_mh_start = src.find('monthly_history = {')
old_mh_end   = src.find('\n}', old_mh_start) + 2
old_mh = src[old_mh_start:old_mh_end]

mh = ns['monthly_history']
month_lbls_old = ns['MONTH_LABELS']  # antes da edição do src acima
# Recalcula MONTH_LABELS com Mai incluído
MONTH_LABELS_NEW = ["Jan", "Fev", "Mar", "Abr", "Mai"]

lines_mh = ['monthly_history = {']
for drv in mh:
    parts = []
    for lbl in MONTH_LABELS_NEW:
        if lbl == 'Abr':
            t = ABR.get(drv, (0,0,0))
        elif lbl == 'Mai':
            t = MAI.get(drv, (0,0,0))
        else:
            t = mh[drv].get(lbl, (0,0,0))
        p_fmt = f'"{lbl}":{fmt_tuple(*t)}'
        parts.append(p_fmt)
    lines_mh.append(f'    {pad(drv)}{{{", ".join(parts)}}},')
lines_mh.append('}')
new_mh = '\n'.join(lines_mh)
src = src.replace(old_mh, new_mh)

with open('generate_html_gerencia.py', 'w', encoding='utf-8') as f:
    f.write(src)

# ── Validação rápida ─────────────────────────────────────────────
stop3b = re.search(r'# SECTION 3', src)
ns2 = {}
exec(compile(src[:stop3b.start()], 'g', 'exec'), ns2)

mh2 = ns2['monthly_history']
lB  = 'Abr'
tp = sum(mh2[d][lB][0] for d in mh2)
td = sum(mh2[d][lB][1] for d in mh2)
ts = sum(mh2[d][lB][2] for d in mh2)
nps_abr = round(100*(tp-td)/ts, 2) if ts else 0

lM = 'Mai'
tp2 = sum(mh2[d][lM][0] for d in mh2)
td2 = sum(mh2[d][lM][1] for d in mh2)
ts2 = sum(mh2[d][lM][2] for d in mh2)
nps_mai = round(100*(tp2-td2)/ts2, 2) if ts2 else 0

print("=== VALIDAÇÃO PÓS-UPDATE ===")
print(f"Abril  : {ts:,} pesquisas  NPS {nps_abr:.2f}%  (oficial: 18.291 / 58,7%)")
print(f"Maio   : {ts2:,} pesquisas  NPS {nps_mai:.2f}%")
print(f"MONTH_LABELS: {ns2['MONTH_LABELS']}")
print(f"M1_LABEL: {ns2['M1_LABEL']}")
print(f"M2_LABEL: {ns2['M2_LABEL']}")
print("\nArquivo atualizado: generate_html_gerencia.py")
