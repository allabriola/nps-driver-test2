#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera snapshots históricos do dashboard Seller Dev para cada semana em WEEK_LABELS.
Para cada semana W: define S1=W, S2=semana anterior, VIG=vazio.
Gera o HTML completo e salva em history_sd/semana_YYYY-MM-DD.html.
"""
import re, json, sys, shutil, os, subprocess
from datetime import date
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SD_DIR   = os.path.join(BASE_DIR, "history_sd")
SD_INDEX = os.path.join(SD_DIR, "index.json")
os.makedirs(SD_DIR, exist_ok=True)

# ── Carrega metadados ─────────────────────────────────────────────────
with open(os.path.join(BASE_DIR, 'generate_html_gerencia.py'), 'r', encoding='utf-8') as f:
    gerencia_src = f.read()

stop = re.search(r'# SECTION 3', gerencia_src)
ns = {}
exec(compile(gerencia_src[:stop.start()], 'generate_html_gerencia.py', 'exec'), ns)

WEEK_LABELS    = ns['WEEK_LABELS']
weekly_history = ns['weekly_history']

MON_NUM   = {"jan":"01","fev":"02","mar":"03","abr":"04","mai":"05",
             "jun":"06","jul":"07","ago":"08","set":"09","out":"10","nov":"11","dez":"12"}
MON_NAMES = {'jan':'Janeiro','fev':'Fevereiro','mar':'Marco','abr':'Abril',
             'mai':'Maio','jun':'Junho','jul':'Julho','ago':'Agosto',
             'set':'Setembro','out':'Outubro','nov':'Novembro','dez':'Dezembro'}

def lbl_to_date(lbl):
    parts = lbl.strip().split('/')
    if len(parts)==2:
        day, mon = parts[0].zfill(2), parts[1].lower().strip()
        return f"2026-{MON_NUM.get(mon,'01')}-{day}"
    return None

def lbl_to_month(lbl):
    parts = lbl.split('/')
    if len(parts)==2:
        mon = parts[1].lower().strip()
        return f"{MON_NAMES.get(mon, mon.capitalize())} 2026"
    return "2026"

def cons_nps_wk(lbl):
    tp = sum(weekly_history[d].get(lbl,(0,0,0))[0] for d in weekly_history)
    td = sum(weekly_history[d].get(lbl,(0,0,0))[1] for d in weekly_history)
    ts = sum(weekly_history[d].get(lbl,(0,0,0))[2] for d in weekly_history)
    return round(100*(tp-td)/ts, 2) if ts > 0 else None, ts

# ── Carrega index existente ────────────────────────────────────────────
today_str = str(date.today())
index = []
if os.path.exists(SD_INDEX):
    with open(SD_INDEX, encoding='utf-8') as f:
        try: index = json.load(f)
        except: index = []
existing_files = {e['file'] for e in index}

# ── Gera snapshot para cada semana ────────────────────────────────────
print(f"Gerando snapshots para {len(WEEK_LABELS)} semanas...\n")

for i, s1_lbl in enumerate(WEEK_LABELS):
    snap_date = lbl_to_date(s1_lbl)
    if not snap_date:
        print(f"  SKIP {s1_lbl} — data inválida")
        continue

    snap_name = f"semana_{snap_date}.html"
    snap_path = os.path.join(SD_DIR, snap_name)
    s2_lbl    = WEEK_LABELS[i-1] if i > 0 else ""
    nps_s1, surv_s1 = cons_nps_wk(s1_lbl)

    print(f"  [{i+1}/{len(WEEK_LABELS)}] {snap_name} | S1={s1_lbl} NPS={nps_s1}% surv={surv_s1:,}...")

    # Modifica temporariamente generate_html_gerencia.py
    mod_src = gerencia_src
    mod_src = re.sub(r'(S1_LABEL\s*=\s*)"[^"]*"',  f'\\1"{s1_lbl}"',  mod_src)
    mod_src = re.sub(r'(S2_LABEL\s*=\s*)"[^"]*"',  f'\\1"{s2_lbl}"',  mod_src)
    mod_src = re.sub(r'(VIG_LABEL\s*=\s*)"[^"]*"', f'\\1""',           mod_src)
    mod_src = re.sub(r'(REPORT_DATE\s*=\s*)"[^"]*"', f'\\1"{snap_date}"', mod_src)

    # Salva com backup
    bak_path = os.path.join(BASE_DIR, '_gerencia_bak.py')
    shutil.copy2(os.path.join(BASE_DIR, 'generate_html_gerencia.py'), bak_path)
    with open(os.path.join(BASE_DIR, 'generate_html_gerencia.py'), 'w', encoding='utf-8') as f:
        f.write(mod_src)

    try:
        # Roda generate_html_seller_dev.py com OUTPUT redirecionado para history_sd/
        # Usa um script auxiliar mínimo
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
            capture_output=True, text=True, timeout=120,
            cwd=BASE_DIR
        )
        if result.returncode == 0:
            print(f"    ✓ Gerado")
            ent = {
                "label":       f"Semana {s1_lbl}",
                "archived_at": today_str,
                "file":        snap_name,
                "s1_label":    s1_lbl,
                "s2_label":    s2_lbl,
                "vig_label":   "",
                "month":       lbl_to_month(s1_lbl),
                "nps_s1":      nps_s1,
                "most_recent": False,
                "has_sd":      True,
            }
            index = [e for e in index if e.get("file") != snap_name]
            index.append(ent)
        else:
            print(f"    ERRO: {result.stderr[:200]}")
    except Exception as e:
        print(f"    EXCEÇÃO: {e}")
    finally:
        # Sempre restaura o original
        shutil.copy2(bak_path, os.path.join(BASE_DIR, 'generate_html_gerencia.py'))
        os.remove(bak_path)

# ── Atualiza index ────────────────────────────────────────────────────
index.sort(key=lambda e: e.get("file",""), reverse=True)
if index: index[0]["most_recent"] = True

with open(SD_INDEX, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"\nConcluído: {len(index)} snapshots em history_sd/")
for e in index:
    print(f"  {e['file']} | NPS={e.get('nps_s1')}%")
