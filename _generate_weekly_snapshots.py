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

    # ── Labels de semana ──────────────────────────────────────────────
    mod_src = re.sub(r'(S1_LABEL\s*=\s*)"[^"]*"',  f'\\1"{s1_lbl}"',  mod_src)
    mod_src = re.sub(r'(S2_LABEL\s*=\s*)"[^"]*"',  f'\\1"{s2_lbl}"',  mod_src)
    mod_src = re.sub(r'(VIG_LABEL\s*=\s*)"[^"]*"', f'\\1""',           mod_src)
    mod_src = re.sub(r'(REPORT_DATE\s*=\s*)"[^"]*"', f'\\1"{snap_date}"', mod_src)

    # ── weekly_driver: usa dados da semana histórica correta ──────────
    # Constrói novo bloco weekly_driver com S1=s1_lbl, S2=s2_lbl
    all_drvs = list(weekly_history.keys())
    def fmt3(t): return f"({t[0]},{t[1]},{t[2]})"
    wd_lines = ['weekly_driver = {']
    for drv in all_drvs:
        s2_t = weekly_history[drv].get(s2_lbl, (0,0,0)) if s2_lbl else (0,0,0)
        s1_t = weekly_history[drv].get(s1_lbl, (0,0,0))
        pad  = ' ' * max(1, 42 - len(drv))
        wd_lines.append(f'    "{drv}":{pad}{{"S2":{fmt3(s2_t)}, "S1":{fmt3(s1_t)}}},')
    wd_lines.append('}')
    # Substitui bloco weekly_driver no source
    old_wd_start = mod_src.find('weekly_driver = {')
    old_wd_end   = mod_src.find('\n}', old_wd_start) + 2
    mod_src = mod_src[:old_wd_start] + '\n'.join(wd_lines) + mod_src[old_wd_end:]

    # ── drivers_vigente: zera (sem VIG para semanas históricas) ───────
    old_vg_start = mod_src.find('drivers_vigente = {')
    old_vg_end   = mod_src.find('\n}', old_vg_start) + 2
    vg_lines = ['drivers_vigente = {']
    for drv in all_drvs:
        pad = ' ' * max(1, 42 - len(drv))
        vg_lines.append(f'    "{drv}":{pad}(0,0,0),')
    vg_lines.append('}')
    mod_src = mod_src[:old_vg_start] + '\n'.join(vg_lines) + mod_src[old_vg_end:]

    # ── _monthly_result.json temporário com dados até o fim da semana ──
    # generate_html_seller_dev.py sobrescreve monthly_history com este arquivo,
    # então preciso criar uma versão histórica que só tem dados até s1_lbl.
    monthly_result_path = os.path.join(BASE_DIR, '_monthly_result.json')
    bak_mr_path = os.path.join(BASE_DIR, '_monthly_result_bak.json')
    shutil.copy2(monthly_result_path, bak_mr_path)

    # Carrega _monthly_result.json atual e constrói versão histórica
    with open(monthly_result_path, encoding='utf-8') as f:
        mr_current = json.load(f)

    mr_hist = {}
    all_months = list(mr_current.keys())  # ["Jan","Fev","Mar","Abr","Mai"]

    for lbl in all_months:
        if lbl == 'Mai':
            # Maio: soma apenas semanas até s1_lbl
            mai_weeks_until = [w for w in WEEK_LABELS
                               if lbl_to_month(w).startswith('Maio')
                               and WEEK_LABELS.index(w) <= WEEK_LABELS.index(s1_lbl)]
            mr_hist['Mai'] = {}
            for drv in mr_current.get('Mai', {}).keys():
                tp = sum(weekly_history.get(drv, {}).get(w,(0,0,0))[0] for w in mai_weeks_until)
                td = sum(weekly_history.get(drv, {}).get(w,(0,0,0))[1] for w in mai_weeks_until)
                ts = sum(weekly_history.get(drv, {}).get(w,(0,0,0))[2] for w in mai_weeks_until)
                mr_hist['Mai'][drv] = [tp, td, ts]
        else:
            # Meses anteriores a Maio: mantém dados originais
            mr_hist[lbl] = mr_current[lbl]

    with open(monthly_result_path, 'w', encoding='utf-8') as f:
        json.dump(mr_hist, f, ensure_ascii=False)

    # ── dd_breakdown.json e _monthly_breakdown.json com dados históricos ─
    dd_path  = os.path.join(BASE_DIR, 'dd_breakdown.json')
    bak_dd   = os.path.join(BASE_DIR, '_dd_bak.json')
    mb_path  = os.path.join(BASE_DIR, '_monthly_breakdown.json')
    bak_mb   = os.path.join(BASE_DIR, '_mb_bak.json')
    shutil.copy2(dd_path, bak_dd)
    shutil.copy2(mb_path, bak_mb)

    with open(dd_path, encoding='utf-8') as f: dd_curr = json.load(f)
    with open(mb_path, encoding='utf-8') as f: mb_curr = json.load(f)

    # Carrega dados históricos por semana
    bh_path = os.path.join(BASE_DIR, '_breakdown_historical.json')
    bh = {}
    if os.path.exists(bh_path):
        with open(bh_path, encoding='utf-8') as f: bh = json.load(f)

    def _bh_to_dd_period(week_lbl):
        """Converte breakdown histórico para o formato de período do dd_breakdown."""
        wk_data = bh.get(week_lbl, {})
        if not wk_data: return {}
        # dd_breakdown[drv][dim][period_key] = {value: {p,d,s,nps}}
        # bh[week][drv][dim] = {value: {p,d,s,nps}}
        result = {}
        for drv, dims in wk_data.items():
            result[drv] = {}
            for dim, values in dims.items():
                if dim in ('P','C','O','Sr','T'):
                    result[drv][dim] = values
        return result

    s1_hist = _bh_to_dd_period(s1_lbl)
    s2_hist = _bh_to_dd_period(s2_lbl) if s2_lbl else {}

    # Constrói dd_breakdown modificado com S1/S2 históricos
    dd_mod = json.loads(json.dumps(dd_curr))
    dims_map = {'P':'P','C':'C','O':'O','Sr':'Sr','Sr_P':'Sr','C_Sr':'C','O_Sr':'O','P_C':'P','P_O':'P'}
    for drv in dd_mod:
        for dd_dim in list(dd_mod[drv].keys()):
            base_dim = dims_map.get(dd_dim, dd_dim)
            s1_d = s1_hist.get(drv, {}).get(base_dim, {})
            s2_d = s2_hist.get(drv, {}).get(base_dim, {})
            dd_mod[drv][dd_dim]['S1']  = s1_d
            dd_mod[drv][dd_dim]['S2']  = s2_d
            dd_mod[drv][dd_dim]['VIG'] = {}
            dd_mod[drv][dd_dim]['M1']  = s1_d  # mensal M1 = S1 histórico
            dd_mod[drv][dd_dim]['M2']  = s2_d
    with open(dd_path, 'w', encoding='utf-8') as f:
        json.dump(dd_mod, f, ensure_ascii=False)

    # Constrói _monthly_breakdown.json modificado
    mb_mod = json.loads(json.dumps(mb_curr))
    for period_key, hist_lbl in [('S1', s1_lbl), ('S2', s2_lbl)]:
        if not hist_lbl: continue
        hist_data = bh.get(hist_lbl, {})
        if not hist_data: continue
        for drv, dims in hist_data.items():
            if period_key not in mb_mod: mb_mod[period_key] = {}
            mb_mod[period_key][drv] = {}
            for dim in ('P','C','O','T','Sr'):
                if dim in dims:
                    mb_mod[period_key][drv][dim] = dims[dim]
    with open(mb_path, 'w', encoding='utf-8') as f:
        json.dump(mb_mod, f, ensure_ascii=False)

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
        # Sempre restaura todos os arquivos originais
        shutil.copy2(bak_path, os.path.join(BASE_DIR, 'generate_html_gerencia.py'))
        os.remove(bak_path)
        if os.path.exists(bak_mr_path):
            shutil.copy2(bak_mr_path, monthly_result_path)
            os.remove(bak_mr_path)
        if os.path.exists(bak_dd):
            shutil.copy2(bak_dd, dd_path)
            os.remove(bak_dd)
        if os.path.exists(bak_mb):
            shutil.copy2(bak_mb, mb_path)
            os.remove(bak_mb)

# ── Atualiza index ────────────────────────────────────────────────────
index.sort(key=lambda e: e.get("file",""), reverse=True)
if index: index[0]["most_recent"] = True

with open(SD_INDEX, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"\nConcluído: {len(index)} snapshots em history_sd/")
for e in index:
    print(f"  {e['file']} | NPS={e.get('nps_s1')}%")
