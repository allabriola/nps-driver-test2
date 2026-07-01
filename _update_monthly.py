#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza generate_html_gerencia.py com dados mensais frescos do _monthly_result.json.
M1 = mês atual MTD, M2 = mês anterior fechado.
Os labels são detectados automaticamente a partir das chaves do JSON.
"""
import json, re
from datetime import date

MONTH_ABBR   = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
MONTH_NAMES  = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

today = date.today()

def _month_meta(year, month):
    return MONTH_ABBR[month - 1], f"{MONTH_NAMES[month - 1]} {year}"

# ── Carrega resultado BQ ──────────────────────────────────────────────────────
with open('_monthly_result.json', encoding='utf-8') as f:
    monthly_data = json.load(f)

all_lbls = list(monthly_data.keys())   # ex: ["Fev","Mar","Abr","Mai","Jun","Jul"]

def _total(lbl):
    return sum(v[2] for v in monthly_data.get(lbl, {}).values())

# M1 = mês mais recente COM dado (trava de virada): se o mês corrente ainda
# está vazio por lag da fonte, mantém o mês anterior como manchete em vez de
# mostrar um mês em branco. Caminha pra trás a partir do mês atual.
y, m = today.year, today.month
for _ in range(6):
    abbr, _ = _month_meta(y, m)
    if _total(abbr) > 0:
        break
    m -= 1
    if m == 0:
        m, y = 12, y - 1
lbl_m1, name_m1 = _month_meta(y, m)

# M2 = mês imediatamente anterior a M1
my, mm = (y - 1, 12) if m == 1 else (y, m - 1)
lbl_m2, name_m2 = _month_meta(my, mm)

print(f"M1 = {name_m1} ({lbl_m1})")
print(f"M2 = {name_m2} ({lbl_m2})")

M1_DATA = monthly_data.get(lbl_m1, {})
M2_DATA = monthly_data.get(lbl_m2, {})

# Validação rápida
total_m1 = sum(v[2] for v in M1_DATA.values())
total_m2 = sum(v[2] for v in M2_DATA.values())
print(f"  {name_m1}: {total_m1:,} surveys")
print(f"  {name_m2}: {total_m2:,} surveys")

# ── Lê generate_html_gerencia.py ─────────────────────────────────────────────
with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()

# ── 1. Labels SECTION 1 ──────────────────────────────────────────────────────
src = re.sub(r'(M1_LABEL\s*=\s*)"[^"]*"', rf'\1"{name_m1}"', src)
src = re.sub(r'(M2_LABEL\s*=\s*)"[^"]*"', rf'\1"{name_m2}"', src)

# ── 2. MONTH_LABELS (últimos 6 meses COM dado — não mostra mês vazio) ─────────
labeled_lbls = [l for l in all_lbls if _total(l) > 0][-6:]
new_month_labels = json.dumps(labeled_lbls)
src = re.sub(r'(MONTH_LABELS\s*=\s*)\[.*?\]', rf'\1{new_month_labels}', src)

# ── 3. Helpers ───────────────────────────────────────────────────────────────
def fmt_tuple(p, d, s): return f"({p},{d},{s})"
def pad(name, width=42): return f'"{name}":{" " * max(1, width - len(name))}'

# ── 4. monthly_driver (M2=mês anterior, M1=mês atual) ────────────────────────
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)

old_md_start = src.find('monthly_driver = {')
old_md_end   = src.find('\n}', old_md_start) + 2

lines_md = ['monthly_driver = {']
for drv in ns['monthly_driver']:
    p2,d2,s2 = M2_DATA.get(drv, (0,0,0))
    p1,d1,s1 = M1_DATA.get(drv, (0,0,0))
    lines_md.append(f'    {pad(drv)}{{"M2":{fmt_tuple(p2,d2,s2)}, "M1":{fmt_tuple(p1,d1,s1)}}},')
lines_md.append('}')
src = src[:old_md_start] + '\n'.join(lines_md) + src[old_md_end:]

# ── 5. monthly_history (todos os meses do JSON) ───────────────────────────────
stop2 = re.search(r'# SECTION 3', src)
ns2 = {}
exec(compile(src[:stop2.start()], 'g', 'exec'), ns2)

old_mh_start = src.find('monthly_history = {')
old_mh_end   = src.find('\n}', old_mh_start) + 2

month_lbls_to_use = labeled_lbls

lines_mh = ['monthly_history = {']
for drv in ns2['monthly_history']:
    parts = []
    for lbl in month_lbls_to_use:
        t = monthly_data[lbl].get(drv, (0,0,0))
        parts.append(f'"{lbl}":{fmt_tuple(*t)}')
    lines_mh.append(f'    {pad(drv)}{{{", ".join(parts)}}},')
lines_mh.append('}')
src = src[:old_mh_start] + '\n'.join(lines_mh) + src[old_mh_end:]

with open('generate_html_gerencia.py', 'w', encoding='utf-8') as f:
    f.write(src)

# ── Validação ─────────────────────────────────────────────────────────────────
stop3 = re.search(r'# SECTION 3', src)
ns3 = {}
exec(compile(src[:stop3.start()], 'g', 'exec'), ns3)

def nps_total(mh, lbl):
    tp = sum(mh[d].get(lbl,(0,0,0))[0] for d in mh)
    td = sum(mh[d].get(lbl,(0,0,0))[1] for d in mh)
    ts = sum(mh[d].get(lbl,(0,0,0))[2] for d in mh)
    return round(100*(tp-td)/ts,2) if ts else 0, ts

nps1, s1 = nps_total(ns3['monthly_history'], lbl_m1)
nps2, s2 = nps_total(ns3['monthly_history'], lbl_m2)

print(f"\n=== VALIDAÇÃO PÓS-UPDATE ===")
print(f"{name_m1} (M1): {s1:,} surveys  NPS {nps1:.2f}%")
print(f"{name_m2} (M2): {s2:,} surveys  NPS {nps2:.2f}%")
print(f"MONTH_LABELS: {ns3['MONTH_LABELS']}")
print(f"M1_LABEL: {ns3['M1_LABEL']}")
print(f"M2_LABEL: {ns3['M2_LABEL']}")
print("\nArquivo atualizado: generate_html_gerencia.py")
