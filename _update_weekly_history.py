#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza weekly_history em generate_html_gerencia.py com dados BQ corretos."""
import re, json

with open('_weekly_history_bq.json', encoding='utf-8') as f:
    bq_data = json.load(f)

with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()

stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)
ALL_DRIVERS = list(ns['monthly_history'].keys())

# Mapeamento data BQ -> label
MONTH_MAP = {'01':'jan','02':'fev','03':'mar','04':'abr','05':'mai','06':'jun'}
def bq_to_lbl(date_str):
    parts = date_str.split('-')
    return parts[2] + '/' + MONTH_MAP[parts[1]]

HIST_WEEKS = ['2026-03-02','2026-03-09','2026-03-16','2026-03-23','2026-03-30',
              '2026-04-06','2026-04-13','2026-04-20','2026-04-27']
WEEK_LABELS_NEW = [bq_to_lbl(w) for w in HIST_WEEKS]

# Constroi novo weekly_history
new_wh = {}
for drv in ALL_DRIVERS:
    new_wh[drv] = {}
    for w in HIST_WEEKS:
        lbl = bq_to_lbl(w)
        v = bq_data.get(w, {}).get(drv, [0,0,0])
        new_wh[drv][lbl] = (int(v[0]), int(v[1]), int(v[2]))

# Formata blocos
def fmt_t(p,d,s): return '(' + str(p) + ',' + str(d) + ',' + str(s) + ')'
def pad_name(name, w=42):
    spaces = max(1, w - len(name))
    return '"' + name + '":' + (' ' * spaces)

lines = ['weekly_history = {']
for drv in ALL_DRIVERS:
    parts = []
    for lbl in WEEK_LABELS_NEW:
        t = new_wh[drv].get(lbl, (0,0,0))
        parts.append('"' + lbl + '":' + fmt_t(*t))
    lines.append('    ' + pad_name(drv) + '{' + ', '.join(parts) + '},')
lines.append('}')
new_block = '\n'.join(lines)

# Substitui no arquivo
old_start = src.find('weekly_history = {')
old_end   = src.find('\n}', old_start) + 2
src = src[:old_start] + new_block + src[old_end:]

# Atualiza WEEK_LABELS
wl_str = '[' + ', '.join('"' + l + '"' for l in WEEK_LABELS_NEW) + ']'
src = re.sub(r'(WEEK_LABELS\s*=\s*)\[.*?\]', r'\g<1>' + wl_str, src)

with open('generate_html_gerencia.py', 'w', encoding='utf-8') as f:
    f.write(src)

# Validacao
stop2 = re.search(r'# SECTION 3', src)
ns2 = {}
exec(compile(src[:stop2.start()], 'g', 'exec'), ns2)
wh2 = ns2['weekly_history']
EXCL = {'CBT','PDD DS&XD - Vendedor','PDD FBM - Vendedor','PDD Fotos - Vendedor',
        'PDD MP,FLEX & CBT - Vendedor','PNR ME - Vendedor','PNR MP - Vendedor'}
sem_med = [d for d in wh2 if d not in EXCL]

print('=== VALIDACAO SEMANAL (sem mediacao) ===')
print('{:<12} {:>8} {:>10}'.format('Semana','Surv','NPS'))
print('-'*33)
for lbl in WEEK_LABELS_NEW:
    p  = sum(wh2[d].get(lbl,(0,0,0))[0] for d in sem_med)
    dt = sum(wh2[d].get(lbl,(0,0,0))[1] for d in sem_med)
    s  = sum(wh2[d].get(lbl,(0,0,0))[2] for d in sem_med)
    nps = round(100*(p-dt)/s,2) if s else 0
    print('{:<12} {:>8,} {:>10.2f}%'.format(lbl, s, nps))

print()
print('Referencia Tableau (sem med):')
print('02/mar=62.5 | 16/mar=63.8 | 23/mar=61.4 | 30/mar=60.4')
print('06/abr=62.5 | 20/abr=64.9 | 27/abr=65.1')
