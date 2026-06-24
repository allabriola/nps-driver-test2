#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualiza generate_html_gerencia.py com dados semanais frescos.
Le datas de _fetch_weekly_data.py e dados de _new_weekly_data.json.
"""
import re, json, sys
from datetime import datetime

# ── 1. Le datas de _fetch_weekly_data.py ──────────────────────────────
with open('_fetch_weekly_data.py', encoding='utf-8') as f:
    fw_src = f.read()

periods_match = re.search(r'PERIODS\s*=\s*\{(.+?)\}', fw_src, re.DOTALL)
periods_raw = periods_match.group(1)

def extract_period(name):
    m = re.search(rf'"{name}".*?"(\d{{4}}-\d{{2}}-\d{{2}})".*?"(\d{{4}}-\d{{2}}-\d{{2}})"', periods_raw)
    return m.group(1), m.group(2)

s1_start, s1_end = extract_period("S1_new")
s2_start, s2_end = extract_period("S2_new")
vig_start, vig_end = extract_period("VIG_new")

def fmt_label(d): return datetime.strptime(d, "%Y-%m-%d").strftime("%-d/%b").replace(".", "").lower().replace("jan","jan").replace("feb","fev").replace("mar","mar").replace("apr","abr").replace("may","mai").replace("jun","jun").replace("jul","jul").replace("aug","ago").replace("sep","set").replace("oct","out").replace("nov","nov").replace("dec","dez")

# Windows nao suporta "%-d", usa "%#d"
try:
    s1_lbl  = f"{fmt_label(s1_start)} – {fmt_label(s1_end)}"
    s2_lbl  = f"{fmt_label(s2_start)} – {fmt_label(s2_end)}"
    vig_lbl = f"{fmt_label(vig_start)} – {fmt_label(vig_end)}"
    s1_short = fmt_label(s1_start)
except ValueError:
    def fmt_label_win(d):
        dt = datetime.strptime(d, "%Y-%m-%d")
        months = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
        return f"{dt.day}/{months[dt.month-1]}"
    s1_lbl  = f"{fmt_label_win(s1_start)} – {fmt_label_win(s1_end)}"
    s2_lbl  = f"{fmt_label_win(s2_start)} – {fmt_label_win(s2_end)}"
    vig_lbl = f"{fmt_label_win(vig_start)} – {fmt_label_win(vig_end)}"
    s1_short = fmt_label_win(s1_start)

# Redefine para Windows
def fmt_label_win(d):
    dt = datetime.strptime(d, "%Y-%m-%d")
    months = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    return f"{dt.day:02d}/{months[dt.month-1]}"

s1_lbl  = f"{fmt_label_win(s1_start)} – {fmt_label_win(s1_end)}"
s2_lbl  = f"{fmt_label_win(s2_start)} – {fmt_label_win(s2_end)}"
vig_lbl = f"{fmt_label_win(vig_start)} – {fmt_label_win(vig_end)}"
s1_short = fmt_label_win(s1_start)

print(f"S1:  {s1_lbl}  ({s1_start} - {s1_end})")
print(f"S2:  {s2_lbl}  ({s2_start} - {s2_end})")
print(f"VIG: {vig_lbl}  ({vig_start} - {vig_end})")

# ── 2. Le dados do JSON ───────────────────────────────────────────────
with open('_new_weekly_data.json', encoding='utf-8') as f:
    wd = json.load(f)

S1  = wd['S1_new']
S2  = wd['S2_new']
VIG = wd['VIG_new']

# ── 3. Atualiza generate_html_gerencia.py ────────────────────────────
with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()

# Labels
src = re.sub(r'(S1_LABEL\s*=\s*)"[^"]*"',  rf'\1"{s1_lbl}"', src)
src = re.sub(r'(S2_LABEL\s*=\s*)"[^"]*"',  rf'\1"{s2_lbl}"', src)
src = re.sub(r'(VIG_LABEL\s*=\s*)"[^"]*"', rf'\1"{vig_lbl}"', src)

# Carrega estado atual para saber os drivers
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)
ALL_DRIVERS = list(ns['monthly_history'].keys())

def fmt(p, d, s): return f"({p},{d},{s})"
def pad(name, w=42): return f'"{name}":{" "*(max(1,w-len(name)))}'

# weekly_driver
old_wd_start = src.find('weekly_driver = {')
old_wd_end   = src.find('\n}', old_wd_start) + 2
lines = ['weekly_driver = {']
for drv in ALL_DRIVERS:
    s2v = S2.get(drv, (0,0,0))
    s1v = S1.get(drv, (0,0,0))
    lines.append(f'    {pad(drv)}{{"S2":{fmt(*s2v)}, "S1":{fmt(*s1v)}}},')
lines.append('}')
src = src[:old_wd_start] + '\n'.join(lines) + src[old_wd_end:]

# drivers_vigente
old_vg_start = src.find('drivers_vigente = {')
old_vg_end   = src.find('\n}', old_vg_start) + 2
lines_v = ['drivers_vigente = {']
for drv in ALL_DRIVERS:
    v = VIG.get(drv, (0,0,0))
    lines_v.append(f'    {pad(drv)}{fmt(*v)},')
lines_v.append('}')
src = src[:old_vg_start] + '\n'.join(lines_v) + src[old_vg_end:]

# weekly_history — adiciona nova semana S1
stop2 = re.search(r'# SECTION 3', src)
ns2 = {}
exec(compile(src[:stop2.start()], 'g', 'exec'), ns2)
wh_hist  = ns2['weekly_history']
old_lbls = list(ns2['WEEK_LABELS'])

if s1_short not in old_lbls:
    old_wh_start = src.find('weekly_history = {')
    old_wh_end   = src.find('\n}', old_wh_start) + 2
    lines_wh = ['weekly_history = {']
    for drv in ALL_DRIVERS:
        existing = dict(wh_hist.get(drv, {}))
        existing[s1_short] = S1.get(drv, (0,0,0))
        ordered_keys = [k for k in old_lbls + [s1_short] if k in existing]
        parts = [f'"{k}":{fmt(*existing[k])}' for k in ordered_keys[-8:]]
        lines_wh.append(f'    {pad(drv)}{{{", ".join(parts)}}},')
    lines_wh.append('}')
    src = src[:old_wh_start] + '\n'.join(lines_wh) + src[old_wh_end:]

    new_lbls = (old_lbls + [s1_short])[-8:]
    src = re.sub(r'(WEEK_LABELS\s*=\s*)\[.*?\]', f'\\1{json.dumps(new_lbls)}', src)

with open('generate_html_gerencia.py', 'w', encoding='utf-8') as f:
    f.write(src)

# ── Validacao ─────────────────────────────────────────────────────────
stop3 = re.search(r'# SECTION 3', src)
ns3 = {}
exec(compile(src[:stop3.start()], 'g', 'exec'), ns3)

def cons(data, lbl):
    tp = sum(data[d].get(lbl,(0,0,0))[0] for d in data)
    td = sum(data[d].get(lbl,(0,0,0))[1] for d in data)
    ts = sum(data[d].get(lbl,(0,0,0))[2] for d in data)
    return round(100*(tp-td)/ts, 2) if ts else 0, ts

vg = ns3['drivers_vigente']
ts_vg = sum(v[2] for v in vg.values())
nps_vg = round(100*(sum(v[0] for v in vg.values())-sum(v[1] for v in vg.values()))/ts_vg, 2) if ts_vg else 0

print(f"\n=== VALIDAÇÃO ===")
print(f"S1  {s1_lbl}: {cons(ns3['weekly_driver'],'S1')[1]:,} surv  NPS {cons(ns3['weekly_driver'],'S1')[0]:.2f}%")
print(f"VIG {vig_lbl}: {ts_vg:,} surv  NPS {nps_vg:.2f}%")
print(f"WEEK_LABELS: {ns3['WEEK_LABELS']}")
print("generate_html_gerencia.py atualizado OK")
