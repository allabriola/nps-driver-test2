import csv, json, re, shutil
from datetime import datetime

# ── Dados NPS (8 semanas) × 10 = % ──────────────────────────
WKL8 = ['06/abr','13/abr','20/abr','27/abr','04/mai','11/mai','18/mai','25/mai*']

NPS = {
    ('ME','Reputacion'):    [71.7,72.6,79.4,70.0,81.1,67.1,75.0,88.2],
    ('Pub','Reputacion'):   [75.8,67.7,92.5,72.5,85.2,76.6,82.7,81.8],
    ('Ventas','Reputacion'):[64.8,73.5,71.6,75.3,67.6,74.0,70.4,81.1],
    ('ME','Rep ME'):    [66.9,80.9,82.9,78.1,84.8,83.3,88.8,87.5],
    ('Pub','Rep ME'):   [64.1,75.8,84.2,68.5,84.3,87.6,90.2,85.1],
    ('Ventas','Rep ME'):[85.4,86.9,87.5,94.2,90.2,91.7,87.2,85.7],
}
EXCL_RATE = {
    ('ME','Reputacion'):    [75.5,67.4,72.2,76.7,64.4,77.2,76.4,70.6],
    ('Pub','Reputacion'):   [60.6,72.6,75.5,69.6,74.1,70.1,81.6,74.2],
    ('Ventas','Reputacion'):[63.5,71.4,64.8,80.5,73.2,63.0,70.4,83.8],
    ('ME','Rep ME'):    [89.0,84.5,87.4,94.3,91.9,92.6,91.6,95.0],
    ('Pub','Rep ME'):   [76.6,90.9,86.0,83.3,86.3,90.7,87.0,91.0],
    ('Ventas','Rep ME'):[86.4,97.0,92.9,91.9,93.9,93.8,94.2,94.3],
}
CDU = {
    ('Reputacion','reclamos'):    [71.0,68.0,84.0,75.0,83.0,72.0,81.0,85.0],
    ('Reputacion','cancelaciones'):[78.0,80.0,75.0,76.0,85.0,77.0,76.0,82.0],
    ('Reputacion','consultas'):   [43.0,60.0,74.0,45.5,39.3,74.0,63.0,None],
    ('Rep ME','ht_ventas'):   [77.0,86.0,87.0,82.0,88.0,88.0,89.0,91.0],
    ('Rep ME','ht_coleta'):   [72.0,20.0,75.0,92.0,75.0,91.0,82.0,None],
    ('Rep ME','bugs'):        [None,None,None,None,58.0,None,None,None],
}
EXCL_ROWS = {
    ('ME','AEC','C2C','Rep ME'):    [377,23,30,68,69,55,63,15],
    ('ME','ATE','C2C','Rep ME'):    [392,215,531,339,630,312,128,204],
    ('ME','ATE','Chat','Rep ME'):   [1022,250,313,222,199,329,353,106],
    ('ME','CTX','Chat','Rep ME'):   [368,169,165,16,0,0,0,0],
    ('ME','KTA','Chat','Rep ME'):   [619,206,406,259,401,649,637,275],
    ('Pub','AEC','C2C','Rep ME'):   [1167,232,539,403,403,823,861,461],
    ('Pub','AEC','Chat','Rep ME'):  [463,147,174,132,204,268,113,72],
    ('Pub','KTA','Chat','Rep ME'):  [1425,195,451,216,446,660,746,446],
    ('Pub','KTA','Offline','Rep ME'):[0,0,0,0,56,1,0,0],
    ('Ventas','AEC','Chat','Rep ME'):[4964,593,755,581,473,826,945,473],
    ('Ventas','CTX','C2C','Rep ME'):[1650,120,106,92,0,0,0,0],
    ('Ventas','KTA','C2C','Rep ME'):[1223,253,280,230,427,570,378,256],
    ('ME','AEC','C2C','Rep'):       [103,85,86,79,88,66,80,40],
    ('ME','ATE','C2C','Rep'):       [80,112,130,119,132,129,114,0],
    ('ME','ATE','Chat','Rep'):      [931,1136,945,799,655,704,705,0],
    ('ME','CTX','Chat','Rep'):      [127,155,158,118,0,0,0,0],
    ('ME','KTA','Chat','Rep'):      [538,791,947,799,510,641,548,0],
    ('Pub','AEC','C2C','Rep'):      [1574,2346,2089,2256,2777,3075,2460,0],
    ('Pub','AEC','Chat','Rep'):     [440,589,516,593,920,1002,472,0],
    ('Pub','KTA','Chat','Rep'):     [1077,1313,1244,1347,2033,1935,2086,0],
    ('Pub','KTA','Offline','Rep'):  [0,1,1,0,0,0,0,0],
    ('Ventas','AEC','C2C','Rep'):   [0,0,0,5,1,0,0,0],
    ('Ventas','AEC','Chat','Rep'):  [1388,1243,1378,1383,1167,1216,1075,0],
    ('Ventas','CTX','C2C','Rep'):   [1055,891,652,445,0,0,0,0],
    ('Ventas','KTA','C2C','Rep'):   [1419,1564,1331,1698,1604,1472,1312,0],
    ('Ventas','MELICIDADE','Chat','Rep'):[0,0,0,0,4,3,0,0],
}
EXCL2_MAP = list(EXCL_ROWS.keys())

MEDIAS_CFG = {
    ('BR_ME_Sellers_Longtail','MULTICANAL C2C'): 'ME LT|C2C',
    ('BR_ME_Sellers_Longtail','MULTICANAL CHAT'):'ME LT|Chat',
    ('BR_ME_Sellers_Longtail','CHAT'):           'ME LT|CHAT',
    ('BR_Publicaciones_Sellers_Longtail','MULTICANAL C2C'):  'Pub LT|C2C',
    ('BR_Publicaciones_Sellers_Longtail','MULTICANAL CHAT'): 'Pub LT|Chat',
    ('BR_Publicaciones_Sellers_Longtail','OFFLINE'):         'Pub LT|Offline',
    ('BR_Ventas_Sellers_Longtail','MULTICANAL C2C'):  'Ventas LT|C2C',
    ('BR_Ventas_Sellers_Longtail','MULTICANAL CHAT'): 'Ventas LT|Chat',
}
def eq_s(e): return e.replace('BR_ME_Sellers_Longtail','ME LT').replace('BR_Ventas_Sellers_Longtail','Ventas LT').replace('BR_Publicaciones_Sellers_Longtail','Pub LT')
def can_s(c): return c.replace('MULTICANAL C2C','C2C').replace('MULTICANAL CHAT','Chat')

reps = []; totals_by_gc = {}
with open('C:/claudinho/_reps_atual.csv', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('REP') or 'Waiting' in line or 'status' in line:
            continue
        parts = line.split(',')
        if len(parts) < 7: continue
        try:
            rep,lider,eq,off,can = parts[0],parts[1],parts[2],parts[3],parts[4]
            me,rep_v = int(parts[5] or 0),int(parts[6] or 0)
        except: continue
        mk = MEDIAS_CFG.get((eq,can))
        if mk:
            totals_by_gc.setdefault(mk,[]).append(me+rep_v)
        reps.append([rep,lider,eq_s(eq),off,can_s(can),me,rep_v,0.0])

medias_final = {k: round(sum(v)/len(v),1) for k,v in totals_by_gc.items() if v}
for r in reps:
    eq_full = ('BR_ME_Sellers_Longtail' if r[2]=='ME LT' else
               'BR_Ventas_Sellers_Longtail' if r[2]=='Ventas LT' else
               'BR_Publicaciones_Sellers_Longtail')
    can_full = 'MULTICANAL C2C' if r[4]=='C2C' else 'MULTICANAL CHAT' if r[4]=='Chat' else r[4]
    mk = MEDIAS_CFG.get((eq_full, can_full))
    r[7] = medias_final.get(mk, 0.0)
print(f'Reps: {len(reps)} | Medias: {medias_final}')

html_path = 'C:/claudinho/reputacion_longtail_abr_mai_2026.html'
with open(html_path, encoding='utf-8') as f:
    html = f.read()

def build_arr(d):
    parts = []
    for v in d:
        parts.append('null' if v is None else str(round(v,1)))
    return '[' + ','.join(parts) + ']'

# 1. WK (semanal tab)
old_wk = "const WK = ['20/abr','27/abr','04/mai','11/mai','18/mai'];"
new_wk  = "const WK = ['06/abr','13/abr','20/abr','27/abr','04/mai','11/mai','18/mai','25/mai*'];"
html = html.replace(old_wk, new_wk, 1)

# 2. wNPS
m = re.search(r'const wNPS = \{.*?\};', html, re.DOTALL)
if m:
    html = html[:m.start()] + f"""const wNPS = {{
  rep: {{
    me:     {build_arr(NPS[('ME','Reputacion')])},
    ventas: {build_arr(NPS[('Ventas','Reputacion')])},
    pub:    {build_arr(NPS[('Pub','Reputacion')])}
  }},
  repme: {{
    me:     {build_arr(NPS[('ME','Rep ME')])},
    ventas: {build_arr(NPS[('Ventas','Rep ME')])},
    pub:    {build_arr(NPS[('Pub','Rep ME')])}
  }}
}};""" + html[m.end():]
    print('wNPS OK')

# 3. wExcl
m = re.search(r'const wExcl = \{.*?\};', html, re.DOTALL)
if m:
    html = html[:m.start()] + f"""const wExcl = {{
  rep: {{
    me:     {build_arr(EXCL_RATE[('ME','Reputacion')])},
    ventas: {build_arr(EXCL_RATE[('Ventas','Reputacion')])},
    pub:    {build_arr(EXCL_RATE[('Pub','Reputacion')])}
  }},
  repme: {{
    me:     {build_arr(EXCL_RATE[('ME','Rep ME')])},
    ventas: {build_arr(EXCL_RATE[('Ventas','Rep ME')])},
    pub:    {build_arr(EXCL_RATE[('Pub','Rep ME')])}
  }}
}};""" + html[m.end():]
    print('wExcl OK')

# 4. wCDU
m = re.search(r'const wCDU = \{.*?\};', html, re.DOTALL)
if m:
    html = html[:m.start()] + f"""const wCDU = {{
  rep: {{
    reclamos:     {build_arr(CDU[('Reputacion','reclamos')])},
    cancelaciones:{build_arr(CDU[('Reputacion','cancelaciones')])},
    consultas:    {build_arr(CDU[('Reputacion','consultas')])}
  }},
  repme: {{
    ht_ventas:    {build_arr(CDU[('Rep ME','ht_ventas')])},
    ht_coleta:    {build_arr(CDU[('Rep ME','ht_coleta')])},
    bugs:         {build_arr(CDU[('Rep ME','bugs')])}
  }}
}};""" + html[m.end():]
    print('wCDU OK')

# 5. EXCL2
m = re.search(r'const EXCL2 = \[.*?\];', html, re.DOTALL)
if m:
    old_rows = re.findall(r"\['(?:ME|Pub|Ventas)'[^\]]+\]", m.group())
    lines2 = []
    for i, key in enumerate(EXCL2_MAP):
        eq,off,can,tipo = key
        # mensais do HTML existente
        try:
            nums = re.findall(r'[-\d]+', old_rows[i])[4:9]
            jan,fev,mar,abr,mai = [int(n) for n in nums[:5]]
        except:
            jan,fev,mar,abr,mai = 0,0,0,0,0
        ws = EXCL_ROWS[key][:8]
        lines2.append(f"  ['{eq}','{off}','{can}','{tipo}', {jan},{fev},{mar},{abr},{mai}, {','.join(map(str,ws))}]")
    html = html[:m.start()] + 'const EXCL2 = [\n' + ',\n'.join(lines2) + '\n];' + html[m.end():]
    print('EXCL2 OK')

# 6. REPS_RAW2
m = re.search(r'// ── Tabela de reps ──.*?const REPS_RAW2 = \[.*?\];', html, re.DOTALL)
if m:
    ts_q = datetime.now().strftime('%d/%b/%Y').replace('May','mai').replace('Jun','jun').replace('Apr','abr').replace('Mar','mar')
    reps_str = ',\n'.join('  '+json.dumps(r) for r in reps)
    html = html[:m.start()] + f'// ── Tabela de reps ── {ts_q} | {len(reps)} reps\nconst REPS_RAW2 = [\n{reps_str}\n];' + html[m.end():]
    print(f'REPS_RAW2 OK ({len(reps)} reps)')

# 7. REP_MEDIAS
m = re.search(r'const REP_MEDIAS = \{[^}]+\};', html)
if m and medias_final:
    html = html[:m.start()] + 'const REP_MEDIAS = {' + ', '.join(f"'{k}':{v}" for k,v in medias_final.items()) + '};' + html[m.end():]
    print('REP_MEDIAS OK')

# 8. Timestamp
now = datetime.now()
ts = now.strftime('%d/%b/%Y as %H:%M').replace('May','mai').replace('Jun','jun').replace('Apr','abr').replace('Mar','mar').replace(' as ',' as ')
ts = ts.replace(' as ', ' às ')
html = re.sub(r'Atualizado: [\d]+/\w+/[\d]+ às [\d]+:[\d]+', f'Atualizado: {ts}', html)
print(f'Timestamp: {ts}')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
shutil.copy(html_path, 'C:/claudinho/reputacion_lt_v2.html')
print(f'Salvo: {len(html)} chars')
