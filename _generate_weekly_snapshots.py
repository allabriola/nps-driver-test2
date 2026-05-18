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

_SD_DRIVERS = ['Experiencia Impositiva Seller Dev','ME Vendedor Seller Dev',
               'PCF Vendedor Seller Dev','Post Venta Seller Dev',
               'Publicaciones Seller Dev','Partners']

def cons_nps_wk(lbl):
    tp = sum(weekly_history.get(d,{}).get(lbl,(0,0,0))[0] for d in _SD_DRIVERS)
    td = sum(weekly_history.get(d,{}).get(lbl,(0,0,0))[1] for d in _SD_DRIVERS)
    ts = sum(weekly_history.get(d,{}).get(lbl,(0,0,0))[2] for d in _SD_DRIVERS)
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

    # ── Determina M1/M2 corretos baseados no mês da semana ────────────
    # M1 = mês do início da semana S1, M2 = mês anterior
    MONTH_KEY = {
        '30/mar': ('Mar', 'Fev', 'Marco 2026',    'Fevereiro 2026'),
        '06/abr': ('Abr', 'Mar', 'Abril 2026',    'Marco 2026'),
        '13/abr': ('Abr', 'Mar', 'Abril 2026',    'Marco 2026'),
        '20/abr': ('Abr', 'Mar', 'Abril 2026',    'Marco 2026'),
        '27/abr': ('Abr', 'Mar', 'Abril 2026',    'Marco 2026'),
        '04/mai': ('Mai', 'Abr', 'Maio 2026',     'Abril 2026'),
        '11/mai': ('Mai', 'Abr', 'Maio 2026',     'Abril 2026'),
    }
    m1_key, m2_key, m1_label, m2_label = MONTH_KEY.get(s1_lbl, ('Mai','Abr','Maio 2026','Abril 2026'))
    month_order = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    m1_idx = month_order.index(m1_key) if m1_key in month_order else 99

    print(f"  [{i+1}/{len(WEEK_LABELS)}] {snap_name} | S1={s1_lbl} M1={m1_key} M2={m2_key} NPS={nps_s1}% surv={surv_s1:,}...")

    # ── Modifica temporariamente generate_html_gerencia.py ────────────
    mod_src = gerencia_src

    # ── Labels de semana ──────────────────────────────────────────────
    mod_src = re.sub(r'(S1_LABEL\s*=\s*)"[^"]*"',  r'\g<1>"' + s1_lbl + '"',  mod_src)
    mod_src = re.sub(r'(S2_LABEL\s*=\s*)"[^"]*"',  r'\g<1>"' + s2_lbl + '"',  mod_src)

    # ── Labels de mês: M1 e M2 corretos para o período ────────────────
    mod_src = re.sub(r'(M1_LABEL\s*=\s*)"[^"]*"', r'\g<1>"' + m1_label + '"', mod_src)
    mod_src = re.sub(r'(M2_LABEL\s*=\s*)"[^"]*"', r'\g<1>"' + m2_label + '"', mod_src)

    # ── MONTH_LABELS: trunca até m1_key (mês atual do snapshot) ───────
    # Garante que mon_cons[-1] = m1_key e mon_cons[-2] = m2_key
    all_month_labels = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    month_labels_until_m1 = [m for m in all_month_labels
                              if all_month_labels.index(m) <= all_month_labels.index(m1_key)]
    import json as _json_snap
    mod_src = re.sub(r'(MONTH_LABELS\s*=\s*)\[.*?\]',
                     r'\g<1>' + _json_snap.dumps(month_labels_until_m1), mod_src)

    # ── WEEK_LABELS: trunca até s1_lbl (semana atual do snapshot) ─────
    # Garante que o gráfico de linha só vai até a semana selecionada
    s1_idx_in_wk = WEEK_LABELS.index(s1_lbl) if s1_lbl in WEEK_LABELS else len(WEEK_LABELS)-1
    week_labels_until_s1 = WEEK_LABELS[:s1_idx_in_wk+1]
    mod_src = re.sub(r'(WEEK_LABELS\s*=\s*)\[.*?\]',
                     r'\g<1>' + _json_snap.dumps(week_labels_until_s1), mod_src)
    mod_src = re.sub(r'(VIG_LABEL\s*=\s*)"[^"]*"',    r'\g<1>""',              mod_src)
    mod_src = re.sub(r'(REPORT_DATE\s*=\s*)"[^"]*"', r'\g<1>"' + snap_date + '"', mod_src)

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

    # Mapeia mês → prefixo para identificar semanas daquele mês
    M_PREFIX = {'Jan':'jan','Fev':'fev','Mar':'mar','Abr':'abr','Mai':'mai'}
    m1_prefix = M_PREFIX.get(m1_key, m1_key.lower())

    mr_hist = {}
    all_months = list(mr_current.keys())
    month_order = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

    for lbl in all_months:
        lbl_idx    = month_order.index(lbl) if lbl in month_order else 99
        m1_idx     = month_order.index(m1_key) if m1_key in month_order else 99
        if lbl_idx < m1_idx:
            # Mês anterior a M1 → mantém completo
            mr_hist[lbl] = mr_current[lbl]
        elif lbl == m1_key:
            # M1 → acumula semanas desse mês até s1_lbl
            m1_weeks = [w for w in WEEK_LABELS
                        if w.split('/')[1].lower().startswith(m1_prefix)
                        and WEEK_LABELS.index(w) <= WEEK_LABELS.index(s1_lbl)]
            mr_hist[lbl] = {}
            for drv in mr_current.get(lbl, {}).keys():
                tp = sum(weekly_history.get(drv,{}).get(w,(0,0,0))[0] for w in m1_weeks)
                td = sum(weekly_history.get(drv,{}).get(w,(0,0,0))[1] for w in m1_weeks)
                ts = sum(weekly_history.get(drv,{}).get(w,(0,0,0))[2] for w in m1_weeks)
                mr_hist[lbl][drv] = [tp, td, ts]
        else:
            # Mês posterior a M1 → zera (ainda não aconteceu)
            mr_hist[lbl] = {drv: [0,0,0] for drv in mr_current.get(lbl,{}).keys()}

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

    # Constrói _monthly_breakdown.json com meses corretos para o período
    mb_mod = json.loads(json.dumps(mb_curr))

    # Popula m1_key com dados históricos do s1_lbl (processo/canal/office/seniority)
    if s1_hist:
        if m1_key not in mb_mod: mb_mod[m1_key] = {}
        for drv, dims in s1_hist.items():
            mb_mod[m1_key][drv] = {dim: dims[dim] for dim in ('P','C','O','T','Sr') if dim in dims}

    # Zera meses posteriores ao M1 (ainda não aconteceram)
    for lbl in list(mb_mod.keys()):
        if lbl in month_order:
            lbl_idx = month_order.index(lbl)
            if lbl_idx > m1_idx:
                del mb_mod[lbl]

    # Remapeia S1/S2 com dados históricos corretos
    for period_key, hist_lbl in [('S1', s1_lbl), ('S2', s2_lbl)]:
        hist_data = bh.get(hist_lbl, {}) if hist_lbl else {}
        if hist_data:
            mb_mod[period_key] = {}
            for drv, dims in hist_data.items():
                mb_mod[period_key][drv] = {dim: dims[dim] for dim in ('P','C','O','T','Sr') if dim in dims}

    with open(mb_path, 'w', encoding='utf-8') as f:
        json.dump(mb_mod, f, ensure_ascii=False)

    # Salva com backup
    bak_path    = os.path.join(BASE_DIR, '_gerencia_bak.py')
    bak_exec_m  = os.path.join(BASE_DIR, '_exec_summary_sd_bak.html')
    bak_exec_wk = os.path.join(BASE_DIR, '_exec_summary_wk_sd_bak.html')
    exec_m_path  = os.path.join(BASE_DIR, '_exec_summary_sd.html')
    exec_wk_path = os.path.join(BASE_DIR, '_exec_summary_wk_sd.html')

    shutil.copy2(os.path.join(BASE_DIR, 'generate_html_gerencia.py'), bak_path)
    if os.path.exists(exec_m_path):  shutil.copy2(exec_m_path,  bak_exec_m)
    if os.path.exists(exec_wk_path): shutil.copy2(exec_wk_path, bak_exec_wk)

    with open(os.path.join(BASE_DIR, 'generate_html_gerencia.py'), 'w', encoding='utf-8') as f:
        f.write(mod_src)

    exec_sd_path = os.path.join(BASE_DIR, '_build_exec_sd.py')

    try:
        # Gera exec summaries para este período histórico, depois monta o HTML
        helper = f"""
import sys, subprocess
sys.path.insert(0, r'{BASE_DIR}')
# Gera resumo executivo para o período do snapshot
subprocess.run([sys.executable, r'{exec_sd_path}'],
    capture_output=True, cwd=r'{BASE_DIR}')
# Monta snapshot
import generate_html_seller_dev as gsd
html = gsd.build()
with open(r'{snap_path}', 'w', encoding='utf-8') as f:
    f.write(html)
print("OK")
"""
        result = subprocess.run(
            [sys.executable, '-c', helper],
            capture_output=True, text=True, timeout=180,
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
            print(f"    ERRO: {result.stderr[:300]}")
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
        if os.path.exists(bak_exec_m):
            shutil.copy2(bak_exec_m, exec_m_path)
            os.remove(bak_exec_m)
        if os.path.exists(bak_exec_wk):
            shutil.copy2(bak_exec_wk, exec_wk_path)
            os.remove(bak_exec_wk)

# ── Atualiza index ────────────────────────────────────────────────────
index.sort(key=lambda e: e.get("file",""), reverse=True)
if index: index[0]["most_recent"] = True

with open(SD_INDEX, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"\nConcluído: {len(index)} snapshots em history_sd/")
for e in index:
    print(f"  {e['file']} | NPS={e.get('nps_s1')}%")
