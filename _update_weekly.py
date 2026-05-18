#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza generate_html_gerencia.py com os novos dados semanais.
S1 = 04/mai-10/mai | S2 = 27/abr-03/mai | VIG = 11/mai-11/mai
"""
import re, json

with open('_new_weekly_data.json', encoding='utf-8') as f:
    wd = json.load(f)

S1  = wd['S1_new']   # 04/mai-10/mai
S2  = wd['S2_new']   # 27/abr-03/mai
VIG = wd['VIG_new']  # 11/mai-11/mai

with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()

# ── 1. Labels ────────────────────────────────────────────────────────
src = re.sub(r'(S1_LABEL\s*=\s*)"[^"]*"',  r'\1"11/mai – 17/mai"', src)
src = re.sub(r'(S2_LABEL\s*=\s*)"[^"]*"',  r'\1"04/mai – 10/mai"', src)
src = re.sub(r'(VIG_LABEL\s*=\s*)"[^"]*"', r'\1"18/mai – 18/mai"', src)

# ── 2. weekly_driver ─────────────────────────────────────────────────
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)
ALL_DRIVERS = list(ns['monthly_history'].keys())

def fmt(p, d, s): return f"({p},{d},{s})"
def pad(name, w=42): return f'"{name}":{" "*(max(1,w-len(name)))}'

# Rebuild weekly_driver block
old_wd_start = src.find('weekly_driver = {')
old_wd_end   = src.find('\n}', old_wd_start) + 2
lines = ['weekly_driver = {']
for drv in ALL_DRIVERS:
    s2 = S2.get(drv, (0,0,0))
    s1 = S1.get(drv, (0,0,0))
    lines.append(f'    {pad(drv)}{{"S2":{fmt(*s2)}, "S1":{fmt(*s1)}}},')
lines.append('}')
src = src[:old_wd_start] + '\n'.join(lines) + src[old_wd_end:]

# ── 3. drivers_vigente ───────────────────────────────────────────────
old_vg_start = src.find('drivers_vigente = {')
old_vg_end   = src.find('\n}', old_vg_start) + 2
lines_v = ['drivers_vigente = {']
for drv in ALL_DRIVERS:
    v = VIG.get(drv, (0,0,0))
    lines_v.append(f'    {pad(drv)}{fmt(*v)},')
lines_v.append('}')
src = src[:old_vg_start] + '\n'.join(lines_v) + src[old_vg_end:]

# ── 4. weekly_history — adiciona nova S1 label ──────────────────────
old_wh_start = src.find('weekly_history = {')
old_wh_end   = src.find('\n}', old_wh_start) + 2

wh_hist = ns['weekly_history']
old_lbls = ns['WEEK_LABELS']

# Label da nova S1: extrai "11/mai" de S1_LABEL "11/mai – 17/mai"
_s1_lbl_raw = re.search(r'"(S1_LABEL\s*=\s*)"[^"]*"', src)
NEW_LBL_WH = S1_LABEL_NEW = "11/mai"   # início da nova semana S1

lines_wh = ['weekly_history = {']
for drv in ALL_DRIVERS:
    existing = dict(wh_hist.get(drv, {}))
    existing[NEW_LBL_WH] = S1.get(drv, (0,0,0))
    # Keep last 7 weeks max
    ordered_keys = [k for k in list(old_lbls) + [NEW_LBL_WH] if k in existing]
    parts = [f'"{k}":{fmt(*existing[k])}' for k in ordered_keys[-7:]]
    lines_wh.append(f'    {pad(drv)}{{{", ".join(parts)}}},')
lines_wh.append('}')
src = src[:old_wh_start] + '\n'.join(lines_wh) + src[old_wh_end:]

# ── 5. WEEK_LABELS ───────────────────────────────────────────────────
stop2 = re.search(r'# SECTION 3', src)
ns2 = {}
exec(compile(src[:stop2.start()], 'g', 'exec'), ns2)
old_lbls2 = ns2['WEEK_LABELS']
if NEW_LBL_WH not in old_lbls2:
    new_lbls = (old_lbls2 + [NEW_LBL_WH])[-7:]
    src = re.sub(r'(WEEK_LABELS\s*=\s*)\[.*?\]',
                 f'\\1{json.dumps(new_lbls)}', src)

with open('generate_html_gerencia.py', 'w', encoding='utf-8') as f:
    f.write(src)

# ── Validação ─────────────────────────────────────────────────────────
stop3 = re.search(r'# SECTION 3', src)
ns3 = {}
exec(compile(src[:stop3.start()], 'g', 'exec'), ns3)

def cons_wk(data, lbl):
    tp=sum(data[d].get(lbl,(0,0,0))[0] for d in data)
    td=sum(data[d].get(lbl,(0,0,0))[1] for d in data)
    ts=sum(data[d].get(lbl,(0,0,0))[2] for d in data)
    return round(100*(tp-td)/ts,2) if ts else 0, ts

wd_data = ns3['weekly_driver']
nps_s1, ts_s1 = cons_wk(wd_data, 'S1')
nps_s2, ts_s2 = cons_wk(wd_data, 'S2')
vg_data = ns3['drivers_vigente']
ts_vg = sum(v[2] for v in vg_data.values())
tp_vg = sum(v[0] for v in vg_data.values())
td_vg = sum(v[1] for v in vg_data.values())
nps_vg = round(100*(tp_vg-td_vg)/ts_vg, 2) if ts_vg else 0

print('=== VALIDAÇÃO ===')
print(f'S1  (04/mai-10/mai): {ts_s1:,} surv  NPS {nps_s1:.2f}%')
print(f'S2  (27/abr-03/mai): {ts_s2:,} surv  NPS {nps_s2:.2f}%')
print(f'VIG (11/mai-11/mai): {ts_vg:,} surv  NPS {nps_vg:.2f}%')
print(f'WEEK_LABELS: {ns3["WEEK_LABELS"]}')
print(f'S1_LABEL: {ns3["S1_LABEL"]}')
print(f'VIG_LABEL: {ns3["VIG_LABEL"]}')
print('\nArquivo atualizado: generate_html_gerencia.py')
