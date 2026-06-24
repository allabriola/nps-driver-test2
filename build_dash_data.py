"""
Script de processamento: lê CSVs de processo e dados de driver,
calcula variações, identifica best/worst por time, monta PROC_REGISTRY
e atualiza generate_nps_driver_dash.py.
"""
import csv, io, json

# ── Dados de driver (copiados dos resultados das queries) ──────────────────
M1_RAW = """driver,team_type,p_m1,d_m1,s_m1
Experiencia Impositiva Mature,Mature,15,4,22
FBM-S Mature,Mature,43,15,63
ME Vendedor Mature,Mature,502,84,634
PCF Vendedor Mature,Mature,123,30,165
Post Venta Mature,Mature,120,28,161
Publicaciones Mature,Mature,90,17,131
Experiencia Impositiva Meli Pro,Meli Pro,3,0,4
FBM-S Meli Pro,Meli Pro,8,1,9
ME Vendedor Meli Pro,Meli Pro,24,6,30
PCF Vendedor Meli Pro,Meli Pro,12,3,18
Post Venta Meli Pro,Meli Pro,26,2,31
Publicaciones Meli Pro,Meli Pro,7,1,9
Otros CV,Outros,233,68,327
Partners,Outros,593,98,765
Experiencia Impositiva Seller Dev,Seller Dev,163,45,227
FBM-S Seller Dev,Seller Dev,110,36,164
ME Vendedor Seller Dev,Seller Dev,1940,274,2448
PCF Vendedor Seller Dev,Seller Dev,118,27,162
Post Venta Seller Dev,Seller Dev,271,54,354
Publicaciones Seller Dev,Seller Dev,712,119,911"""

M2_RAW = """driver,team_type,p_m2,d_m2,s_m2
Experiencia Impositiva Mature,Mature,45,20,72
FBM-S Mature,Mature,130,45,203
ME Vendedor Mature,Mature,1618,314,2184
PCF Vendedor Mature,Mature,332,85,467
Post Venta Mature,Mature,392,76,520
Publicaciones Mature,Mature,258,51,345
Experiencia Impositiva Meli Pro,Meli Pro,8,4,13
FBM-S Meli Pro,Meli Pro,11,8,22
ME Vendedor Meli Pro,Meli Pro,60,10,75
PCF Vendedor Meli Pro,Meli Pro,32,8,44
Post Venta Meli Pro,Meli Pro,70,10,81
Publicaciones Meli Pro,Meli Pro,18,7,26
Otros CV,Outros,800,194,1087
Partners,Outros,2228,337,2806
Experiencia Impositiva Seller Dev,Seller Dev,312,108,469
FBM-S Seller Dev,Seller Dev,347,125,524
ME Vendedor Seller Dev,Seller Dev,4958,754,6266
PCF Vendedor Seller Dev,Seller Dev,536,166,790
Post Venta Seller Dev,Seller Dev,929,178,1186
Publicaciones Seller Dev,Seller Dev,2639,374,3309"""

S1_RAW = """driver,team_type,p_s1,d_s1,s_s1
Experiencia Impositiva Mature,Mature,9,2,12
FBM-S Mature,Mature,24,5,33
ME Vendedor Mature,Mature,328,60,418
PCF Vendedor Mature,Mature,90,20,117
Post Venta Mature,Mature,72,15,98
Publicaciones Mature,Mature,57,11,84
Experiencia Impositiva Meli Pro,Meli Pro,1,0,2
FBM-S Meli Pro,Meli Pro,8,1,9
ME Vendedor Meli Pro,Meli Pro,18,4,22
PCF Vendedor Meli Pro,Meli Pro,12,2,17
Post Venta Meli Pro,Meli Pro,22,2,26
Publicaciones Meli Pro,Meli Pro,5,0,6
Otros CV,Outros,132,44,189
Partners,Outros,328,57,427
Experiencia Impositiva Seller Dev,Seller Dev,118,31,164
FBM-S Seller Dev,Seller Dev,57,18,87
ME Vendedor Seller Dev,Seller Dev,1326,186,1690
PCF Vendedor Seller Dev,Seller Dev,69,21,98
Post Venta Seller Dev,Seller Dev,172,35,223
Publicaciones Seller Dev,Seller Dev,405,67,511"""

S2_RAW = """driver,team_type,p_s2,d_s2,s_s2
Experiencia Impositiva Mature,Mature,12,5,20
FBM-S Mature,Mature,30,13,48
ME Vendedor Mature,Mature,340,56,438
PCF Vendedor Mature,Mature,68,14,91
Post Venta Mature,Mature,88,20,114
Publicaciones Mature,Mature,61,13,87
Experiencia Impositiva Meli Pro,Meli Pro,2,1,3
FBM-S Meli Pro,Meli Pro,0,2,2
ME Vendedor Meli Pro,Meli Pro,10,6,17
PCF Vendedor Meli Pro,Meli Pro,4,3,7
Post Venta Meli Pro,Meli Pro,8,0,9
Publicaciones Meli Pro,Meli Pro,6,1,8
Otros CV,Outros,144,38,203
Partners,Outros,448,77,574
Experiencia Impositiva Seller Dev,Seller Dev,66,25,100
FBM-S Seller Dev,Seller Dev,73,23,104
ME Vendedor Seller Dev,Seller Dev,1016,158,1270
PCF Vendedor Seller Dev,Seller Dev,84,23,125
Post Venta Seller Dev,Seller Dev,176,39,233
Publicaciones Seller Dev,Seller Dev,502,88,653"""


def team_type(driver):
    if driver.startswith('FBM'):
        return 'FBM'
    if driver.endswith('Seller Dev') or driver == 'Partners':
        return 'Seller Dev'
    if driver.endswith('Mature'):
        return 'Mature'
    if driver.endswith('Meli Pro'):
        return 'Meli Pro'
    return 'Outros'


def parse_drivers(raw, pk, dk, sk):
    rows = {}
    for r in csv.DictReader(io.StringIO(raw.strip())):
        d = r['driver']
        rows[d] = {
            'driver': d,
            'team_type': team_type(d),
            pk: int(r[pk]), dk: int(r[dk]), sk: int(r[sk]),
        }
    return rows


m1 = parse_drivers(M1_RAW, 'p_m1', 'd_m1', 's_m1')
m2 = parse_drivers(M2_RAW, 'p_m2', 'd_m2', 's_m2')
s1 = parse_drivers(S1_RAW, 'p_s1', 'd_s1', 's_s1')
s2 = parse_drivers(S2_RAW, 'p_s2', 'd_s2', 's_s2')

EXCLUDE_DRIVERS = {'Otros CV'}

all_m = sorted(d for d in set(list(m1) + list(m2)) if d not in EXCLUDE_DRIVERS)
all_s = sorted(d for d in set(list(s1) + list(s2)) if d not in EXCLUDE_DRIVERS)

monthly_drivers = []
for d in all_m:
    r1, r2 = m1.get(d, {}), m2.get(d, {})
    monthly_drivers.append({
        'driver': d, 'team_type': team_type(d),
        'p_m1': r1.get('p_m1', 0), 'd_m1': r1.get('d_m1', 0), 's_m1': r1.get('s_m1', 0),
        'p_m2': r2.get('p_m2', 0), 'd_m2': r2.get('d_m2', 0), 's_m2': r2.get('s_m2', 0),
    })

weekly_drivers = []
for d in all_s:
    r1, r2 = s1.get(d, {}), s2.get(d, {})
    weekly_drivers.append({
        'driver': d, 'team_type': team_type(d),
        'p_s1': r1.get('p_s1', 0), 'd_s1': r1.get('d_s1', 0), 's_s1': r1.get('s_s1', 0),
        'p_s2': r2.get('p_s2', 0), 'd_s2': r2.get('d_s2', 0), 's_s2': r2.get('s_s2', 0),
    })


def nps(p, d, s):
    return round(100 * (p - d) / s, 2) if s else None


def var_list(drivers, pk1, dk1, sk1, pk2, dk2, sk2):
    res = []
    for d in drivers:
        n1 = nps(d[pk1], d[dk1], d[sk1])
        n2 = nps(d[pk2], d[dk2], d[sk2])
        v = round(n1 - n2, 2) if n1 is not None and n2 is not None else None
        res.append({**d, 'nps1': n1, 'nps2': n2, 'var': v})
    return res


monthly_var = var_list(monthly_drivers, 'p_m1', 'd_m1', 's_m1', 'p_m2', 'd_m2', 's_m2')
weekly_var  = var_list(weekly_drivers,  'p_s1', 'd_s1', 's_s1', 'p_s2', 'd_s2', 's_s2')

TEAMS = ['all', 'Seller Dev', 'Mature', 'Meli Pro', 'FBM']


def best_worst(vlist, team):
    sub = vlist if team == 'all' else [d for d in vlist if d['team_type'] == team]
    sub = [d for d in sub if d['var'] is not None]
    if not sub:
        return None, None
    best  = max(sub, key=lambda d: d['var'])
    worst = min(sub, key=lambda d: d['var'])
    return best['driver'], worst['driver']


print("=== MONTHLY BEST/WORST ===")
monthly_bw = {}
for t in TEAMS:
    b, w = best_worst(monthly_var, t)
    monthly_bw[t] = (b, w)
    print(f"  {t:15}: best={b}  worst={w}")

print("\n=== WEEKLY BEST/WORST ===")
weekly_bw = {}
for t in TEAMS:
    b, w = best_worst(weekly_var, t)
    weekly_bw[t] = (b, w)
    print(f"  {t:15}: best={b}  worst={w}")


def load_proc(path):
    data = {}
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            d = r['driver']
            if d not in data:
                data[d] = []
            data[d].append({
                'process': r['process'],
                'promoters': int(r['promoters']),
                'detractors': int(r['detractors']),
                'surveys': int(r['surveys']),
            })
    return data


pm1 = load_proc('proc_m1.csv')
pm2 = load_proc('proc_m2.csv')
ps1 = load_proc('proc_s1.csv')
ps2 = load_proc('proc_s2.csv')

# Build PROC_REGISTRY
reg = {'monthly': {}, 'weekly': {}}
for t in TEAMS:
    b, w = monthly_bw[t]
    reg['monthly'][t] = {
        'best_driver':  b or '',
        'worst_driver': w or '',
        'best_curr':    pm1.get(b, []) if b else [],
        'best_prev':    pm2.get(b, []) if b else [],
        'worst_curr':   pm1.get(w, []) if w else [],
        'worst_prev':   pm2.get(w, []) if w else [],
    }
    b, w = weekly_bw[t]
    reg['weekly'][t] = {
        'best_driver':  b or '',
        'worst_driver': w or '',
        'best_curr':    ps1.get(b, []) if b else [],
        'best_prev':    ps2.get(b, []) if b else [],
        'worst_curr':   ps1.get(w, []) if w else [],
        'worst_prev':   ps2.get(w, []) if w else [],
    }

# ── Reconstruir generate_nps_driver_dash.py ───────────────────────────────
# Estratégia: preservar a parte fixa (Helpers + funções + HTML_TEMPLATE)
# e reconstruir apenas as seções de dados.

script_path = 'generate_nps_driver_dash.py'
with open(script_path, encoding='utf-8') as f:
    src = f.read()

# A parte fixa começa no marcador "# Helpers"
FIXED_MARKER = '# ============================================================\n# Helpers\n# ============================================================'
fixed_idx = src.find(FIXED_MARKER)
assert fixed_idx != -1, "Marcador 'Helpers' não encontrado no script"
fixed_part = src[fixed_idx:]

# Montar o novo cabeçalho com as seções de dados
new_header = (
    '#!/usr/bin/env python3\n'
    '"""\n'
    'Dashboard NPS Driver BR — Todos os Times (Seller Dev, Mature, Meli Pro, FBM)\n'
    'Gerado automaticamente pelo skill /metrics-cx:nps-driver-br-dash\n'
    '"""\n\n'
    'import json\n\n'
    '# ============================================================\n'
    '# SECTION 1 — Metadata (atualizado pelo skill)\n'
    '# ============================================================\n'
    'M1_LABEL = "April 2026"\n'
    'M2_LABEL = "March 2026"\n'
    'S1_LABEL = "06-10 Apr 2026"\n'
    'S2_LABEL = "30 Mar - 05 Apr 2026"\n\n'
    '# ============================================================\n'
    '# SECTION 2 — Dados mensais por driver (atualizado pelo skill)\n'
    '# Formato: {"driver": str, "team_type": str,\n'
    '#            "p_m1": int, "d_m1": int, "s_m1": int,\n'
    '#            "p_m2": int, "d_m2": int, "s_m2": int}\n'
    '# ============================================================\n'
    'MONTHLY_DRIVERS = ' + json.dumps(monthly_drivers, indent=4, ensure_ascii=False) + '\n\n'
    '# ============================================================\n'
    '# SECTION 3 — Dados semanais por driver (atualizado pelo skill)\n'
    '# Formato: {"driver": str, "team_type": str,\n'
    '#            "p_s1": int, "d_s1": int, "s_s1": int,\n'
    '#            "p_s2": int, "d_s2": int, "s_s2": int}\n'
    '# ============================================================\n'
    'WEEKLY_DRIVERS = ' + json.dumps(weekly_drivers, indent=4, ensure_ascii=False) + '\n\n'
    '# ============================================================\n'
    '# SECTION 4 — Registry de processos (atualizado pelo skill)\n'
    '#\n'
    '# Keyed by period_type ("monthly" / "weekly") e depois por\n'
    '# team_filter ("all", "Seller Dev", "Mature", "Meli Pro", "FBM").\n'
    '#\n'
    '# best_curr / best_prev / worst_curr / worst_prev sao listas de\n'
    '# {"process": str, "promoters": int, "detractors": int, "surveys": int}\n'
    '# onde curr = periodo mais recente (M1 ou S1) e prev = anterior (M2 ou S2).\n'
    '# ============================================================\n'
    'PROC_REGISTRY = ' + json.dumps(reg, indent=4, ensure_ascii=False) + '\n\n\n'
)

new_src = new_header + fixed_part

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(new_src)

print("\ngenerate_nps_driver_dash.py atualizado com sucesso.")
