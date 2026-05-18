#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Salva um snapshot semanal do dashboard em history/ e atualiza o index.json.
Chamado automaticamente pelo skill toda segunda-feira após o update semanal.
Uso: python _save_snapshot.py
"""
import json, re, shutil, os, sys
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')

DASHBOARD    = "nps_tendencias_gerencia.html"
DASHBOARD_SD = "nps_tendencias_seller_dev.html"   # também salva seller dev
HISTORY_DIR  = "history"
HISTORY_SD   = "history_sd"
INDEX_FILE   = os.path.join(HISTORY_DIR, "index.json")
INDEX_SD     = os.path.join(HISTORY_SD,  "index.json")

# ── Lê dados do generate_html_gerencia.py ──────────────────────────
with open("generate_html_gerencia.py", "r", encoding="utf-8") as f:
    src = f.read()

stop = re.search(r"# SECTION 3", src)
ns = {}
exec(compile(src[:stop.start()], "g", "exec"), ns)

S1_LABEL  = ns.get("S1_LABEL",  "S1")
S2_LABEL  = ns.get("S2_LABEL",  "S2")
VIG_LABEL = ns.get("VIG_LABEL", "VIG")
M1_LABEL  = ns.get("M1_LABEL",  "")

# Calcula NPS consolidado S1 sem mediação
EXCL = {"CBT","PDD DS&XD - Vendedor","PDD FBM - Vendedor","PDD Fotos - Vendedor",
        "PDD MP,FLEX & CBT - Vendedor","PNR ME - Vendedor","PNR MP - Vendedor"}
wd = ns.get("weekly_driver", {})
pp = sum(wd.get(d,{}).get("S1",(0,0,0))[0] for d in wd if d not in EXCL)
dd = sum(wd.get(d,{}).get("S1",(0,0,0))[1] for d in wd if d not in EXCL)
ss = sum(wd.get(d,{}).get("S1",(0,0,0))[2] for d in wd if d not in EXCL)
nps_s1 = round(100*(pp-dd)/ss, 2) if ss else None

# ── Nome do arquivo snapshot ────────────────────────────────────────
today_str = str(date.today())
# Usa data de início da S1 como identificador (extrai do S1_LABEL)
try:
    parts = S1_LABEL.split("–")[0].strip()  # "27/abr"
    day, mon_str = parts.split("/")
    MON_NUM = {"jan":"01","fev":"02","mar":"03","abr":"04","mai":"05","jun":"06",
               "jul":"07","ago":"08","set":"09","out":"10","nov":"11","dez":"12"}
    mon_num = MON_NUM.get(mon_str.strip().lower(), "05")
    snap_id = f"2026-{mon_num}-{day.strip().zfill(2)}"
except:
    snap_id = today_str

snapshot_name = f"semana_{snap_id}.html"
snapshot_path = os.path.join(HISTORY_DIR, snapshot_name)

def save_snapshot_to(dashboard_file, history_dir, index_file, label_prefix=""):
    if not os.path.exists(dashboard_file):
        print(f"  AVISO: {dashboard_file} não encontrado — pulando.")
        return None
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    snap_path = os.path.join(history_dir, snapshot_name)
    shutil.copy2(dashboard_file, snap_path)
    print(f"Snapshot salvo: {snap_path}")

    idx = []
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            try: idx = json.load(f)
            except: idx = []
    idx = [e for e in idx if e.get("file") != snapshot_name]
    for e in idx: e["most_recent"] = False
    ent = {
        "label":       f"Semana {S1_LABEL}",
        "archived_at": today_str,
        "file":        snapshot_name,
        "s1_label":    S1_LABEL,
        "s2_label":    S2_LABEL,
        "vig_label":   VIG_LABEL,
        "month":       M1_LABEL,
        "nps_s1":      nps_s1,
        "most_recent": True,
    }
    idx.insert(0, ent)
    idx = idx[:52]
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)
    print(f"  Index: {len(idx)} snapshots | NPS S1={nps_s1}%")
    return ent

# ── Salva ambos os dashboards ─────────────────────────────────────
save_snapshot_to(DASHBOARD,    HISTORY_DIR, INDEX_FILE)
save_snapshot_to(DASHBOARD_SD, HISTORY_SD,  INDEX_SD)

print(f"\nEntrada: {S1_LABEL} | {today_str}")
