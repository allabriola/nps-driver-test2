#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Salva o fechamento mensal do dashboard Seller Dev.
Rodar no final de cada mês (ou logo após o mês fechar).
Salva em history_sd/mensal_YYYY-MM.html e atualiza history_sd/mensal_index.json.

Uso: python _save_monthly_snapshot.py
"""
import re, json, os, sys, shutil, subprocess
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SD_DIR   = os.path.join(BASE_DIR, "history_sd")
MENSAL_INDEX = os.path.join(SD_DIR, "mensal_index.json")
os.makedirs(SD_DIR, exist_ok=True)

# ── Carrega contexto do mês fechado ──────────────────────────────────
with open(os.path.join(BASE_DIR, 'generate_html_gerencia.py'), 'r', encoding='utf-8') as f:
    src = f.read()
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'generate_html_gerencia.py', 'exec'), ns)

M1_LABEL = ns.get('M1_LABEL', 'Mês')  # ex: "Maio 2026"
M2_LABEL = ns.get('M2_LABEL', '')
REPORT_DATE = ns.get('REPORT_DATE', str(date.today()))

# Slug do mês para nome do arquivo
MON_ABBR = {'Janeiro':'01','Fevereiro':'02','Marco':'03','Abril':'04',
            'Maio':'05','Junho':'06','Julho':'07','Agosto':'08',
            'Setembro':'09','Outubro':'10','Novembro':'11','Dezembro':'12'}
parts = M1_LABEL.split()  # ["Abril", "2026"]
mon_num = MON_ABBR.get(parts[0], '00') if parts else '00'
year    = parts[1] if len(parts) > 1 else '2026'
snap_slug = f"mensal_{year}-{mon_num}"
snap_name = f"{snap_slug}.html"
snap_path = os.path.join(SD_DIR, snap_name)

print(f"Salvando fechamento mensal: {M1_LABEL} → {snap_name}")

# ── Gera o snapshot com os dados do mês fechado ───────────────────────
helper = f"""
import sys
sys.path.insert(0, r'{BASE_DIR}')
import generate_html_seller_dev as gsd
html = gsd.build()
with open(r'{snap_path}', 'w', encoding='utf-8') as f:
    f.write(html)
print("OK")
"""
result = subprocess.run(
    [sys.executable, '-c', helper],
    capture_output=True, text=True, timeout=180, cwd=BASE_DIR
)
if result.returncode == 0:
    print(f"  ✓ Snapshot salvo: {snap_path}")
else:
    print(f"  ERRO: {result.stderr[:300]}")
    sys.exit(1)

# ── Calcula NPS mensal consolidado ────────────────────────────────────
with open(os.path.join(BASE_DIR, '_monthly_result.json'), encoding='utf-8') as f:
    mr = json.load(f)

SD_DRIVERS = [
    'Experiencia Impositiva Seller Dev', 'ME Vendedor Seller Dev',
    'PCF Vendedor Seller Dev', 'Post Venta Seller Dev',
    'Publicaciones Seller Dev', 'Partners',
]
MONTH_KEY = {'January':'Jan','Fevereiro':'Fev','Marco':'Mar','Abril':'Abr',
             'Maio':'Mai','Junho':'Jun','Julho':'Jul','Agosto':'Ago',
             'Setembro':'Set','Outubro':'Out','Novembro':'Nov','Dezembro':'Dez'}
m_key = MONTH_KEY.get(parts[0], parts[0][:3]) if parts else ''
mon_data = mr.get(m_key, {})
tp = sum(mon_data.get(d, [0,0,0])[0] for d in SD_DRIVERS if isinstance(mon_data.get(d), list))
td = sum(mon_data.get(d, [0,0,0])[1] for d in SD_DRIVERS if isinstance(mon_data.get(d), list))
ts = sum(mon_data.get(d, [0,0,0])[2] for d in SD_DRIVERS if isinstance(mon_data.get(d), list))
nps_mes = round(100*(tp-td)/ts, 2) if ts > 0 else None

# ── Atualiza mensal_index.json ────────────────────────────────────────
index = []
if os.path.exists(MENSAL_INDEX):
    with open(MENSAL_INDEX, encoding='utf-8') as f:
        try: index = json.load(f)
        except: index = []

index = [e for e in index if e.get('file') != snap_name]
index.insert(0, {
    "label":        M1_LABEL,
    "file":         snap_name,
    "month_label":  M1_LABEL,
    "prev_label":   M2_LABEL,
    "nps_mes":      nps_mes,
    "surveys":      ts,
    "archived_at":  str(date.today()),
    "most_recent":  True,
})
for i, e in enumerate(index):
    e["most_recent"] = (i == 0)

with open(MENSAL_INDEX, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"  ✓ Index atualizado: {len(index)} fechamentos")
print(f"  NPS {M1_LABEL}: {nps_mes}% ({ts:,} pesquisas)")
