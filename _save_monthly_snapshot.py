#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Salva o fechamento mensal (aba "Fechamentos Mensais") do dashboard Seller Dev.

Snapshota o ÚLTIMO MÊS FECHADO (mês calendário anterior a hoje) com os dados
COMPLETOS, gerando history_sd/mensal_YYYY-MM.html e atualizando mensal_index.json.

Roda TODO dia (no bat): enquanto o dado do mês recém-fechado ainda assenta, o
snapshot é regenerado; depois estabiliza. O MÊS CORRENTE não entra nesta aba —
ele é acompanhado nas abas Exec/Mensal/Vigente (M1 = mês corrente MTD).

Como gera o snapshot com o mês fechado como foco: força temporariamente o
generate_html_gerencia.py com `_update_monthly.py --force-m1=<mes>`, gera o HTML e
SEMPRE restaura o estado live (mês corrente como M1) no finally.

Uso: python _save_monthly_snapshot.py
"""
import re, json, os, sys, subprocess
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SD_DIR   = os.path.join(BASE_DIR, "history_sd")
MENSAL_INDEX = os.path.join(SD_DIR, "mensal_index.json")
os.makedirs(SD_DIR, exist_ok=True)

MONTH_ABBR  = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
MONTH_NAMES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
               "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
SD_DRIVERS  = [
    'Experiencia Impositiva Seller Dev', 'ME Vendedor Seller Dev',
    'PCF Vendedor Seller Dev', 'Post Venta Seller Dev',
    'Publicaciones Seller Dev', 'Partners',
]

# ── Último mês FECHADO = mês calendário anterior a hoje ───────────────
today      = date.today()
first_this = date(today.year, today.month, 1)
last_prev  = date.fromordinal(first_this.toordinal() - 1)   # último dia do mês anterior
cy, cm     = last_prev.year, last_prev.month
closed_abbr = MONTH_ABBR[cm - 1]
closed_name = f"{MONTH_NAMES[cm - 1]} {cy}"
snap_name   = f"mensal_{cy}-{cm:02d}.html"
snap_path   = os.path.join(SD_DIR, snap_name)

# mês anterior ao fechado (label de comparação)
pm = 12 if cm == 1 else cm - 1
py = cy - 1 if cm == 1 else cy
prev_name = f"{MONTH_NAMES[pm - 1]} {py}"

# ── Confere se há dados do mês fechado ────────────────────────────────
with open(os.path.join(BASE_DIR, '_monthly_result.json'), encoding='utf-8') as f:
    mr = json.load(f)
mon_data = mr.get(closed_abbr, {})

def _sd_sum(idx):
    return sum(mon_data.get(d, [0, 0, 0])[idx] for d in SD_DRIVERS
               if isinstance(mon_data.get(d), list))

ts = _sd_sum(2)
if ts == 0:
    print(f"Sem dados p/ {closed_name} em _monthly_result.json — nada a fazer.")
    sys.exit(0)

tp, td  = _sd_sum(0), _sd_sum(1)
nps_mes = round(100 * (tp - td) / ts, 2) if ts else None
print(f"Fechamento mensal: {closed_name} → {snap_name}  ({ts:,} pesquisas, NPS {nps_mes}%)")


def _run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True,
                       timeout=300, cwd=BASE_DIR)
    if r.returncode != 0:
        print(f"  ERRO em {' '.join(args)}: {(r.stderr or r.stdout)[:400]}")
    return r.returncode


# ── Gera o snapshot com o mês fechado como M1 (força + SEMPRE restaura) ─
try:
    if _run(['_update_monthly.py', f'--force-m1={closed_abbr}']) != 0:
        sys.exit(1)
    helper = (
        "import sys\n"
        f"sys.path.insert(0, r'{BASE_DIR}')\n"
        "import generate_html_seller_dev as gsd\n"
        f"open(r'{snap_path}','w',encoding='utf-8').write(gsd.build())\n"
        "print('OK')\n"
    )
    r = subprocess.run([sys.executable, '-c', helper], capture_output=True,
                       text=True, timeout=300, cwd=BASE_DIR)
    if r.returncode != 0:
        print(f"  ERRO build: {(r.stderr or r.stdout)[:400]}")
        sys.exit(1)
    print(f"  ✓ Snapshot salvo: {snap_name}")
finally:
    # SEMPRE restaura o estado live (mês corrente como M1)
    _run(['_update_monthly.py'])

# ── Atualiza mensal_index.json: só meses FECHADOS (sem o mês corrente) ─
index = []
if os.path.exists(MENSAL_INDEX):
    try:
        index = json.load(open(MENSAL_INDEX, encoding='utf-8'))
    except Exception:
        index = []

def _entry_ym(e):
    m = re.search(r'mensal_(\d{4})-(\d{2})', e.get('file', ''))
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)

cur_ym = (today.year, today.month)
# remove o próprio mês fechado (será reinserido) e QUALQUER mês >= corrente
index = [e for e in index if _entry_ym(e) < cur_ym and e.get('file') != snap_name]
index.append({
    "label":       closed_name,
    "file":        snap_name,
    "month_label": closed_name,
    "prev_label":  prev_name,
    "nps_mes":     nps_mes,
    "surveys":     ts,
    "archived_at": str(today),
    "most_recent": True,
})
index.sort(key=_entry_ym, reverse=True)
for i, e in enumerate(index):
    e["most_recent"] = (i == 0)

with open(MENSAL_INDEX, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"  ✓ Index atualizado: {len(index)} fechamentos (só meses fechados)")
