import sys, csv
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CSV_PATH = r"c:\Users\allabriola\Downloads\DD Mgmt - General vs Target_Datos completos_data (32).csv"
BQ_PATH  = r"C:\claudinho\bq_cdu_data.csv"

TEAMS = {"BR_Ventas_Sellers_Longtail", "BR_Publicaciones_Sellers_Longtail", "BR_ME_Sellers_Longtail"}
OFFICES_RAW = {"ATE", "CTX", "KTA_BRASIL", "AEC"}  # as they appear in CSV
OFFICES_DISPLAY = {"ATE", "CTX", "KTA"}  # normalized display names
WEEK_S2, WEEK_S1 = "30 Mar 26", "6 Apr 26"

# Office normalization: both CSV KTA_BRASIL and BQ KTA_BRASIL → KTA
def norm_office(o):
    o = o.strip()
    if o.startswith("KTA"): return "KTA"
    if o.startswith("ATE"): return "ATE"
    if o.startswith("CTX"): return "CTX"
    return o

# --- 1. Read CSV: case_id -> (week, office) ---
case_info = {}
with open(CSV_PATH, encoding='utf-8-sig', newline='') as f:
    for row in csv.DictReader(f, delimiter=';'):
        team   = row.get("USER_TEAM_NAME", "").strip()
        office = row.get("USER_OFFICE", "").strip()
        week   = row.get("OPEN_BY_DATE_FORMATTED", "").strip()
        cid    = row.get("CAS_CASE_ID", "").strip()
        norm_off = norm_office(office)
        if team not in TEAMS or norm_off not in OFFICES_DISPLAY or week not in (WEEK_S2, WEEK_S1) or not cid:
            continue
        case_info[cid] = {"week": "S2" if week == WEEK_S2 else "S1", "office": norm_off}

print(f"CSV cases: {len(case_info)}")

# --- 2. Read BQ data: case_id -> (CDU, office, det, prom) ---
bq_data = {}
first = True
with open(BQ_PATH, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if first and not line[0].isdigit():
            first = False
            continue  # skip header line if any
        first = False
        parts = line.split(',')
        if len(parts) < 5: continue
        cid = parts[0].strip()
        cdu = parts[1].strip()
        off = norm_office(parts[2])
        det = int(parts[3].strip())
        prom = int(parts[4].strip())
        bq_data[cid] = {"CDU": cdu, "office": off, "det": det, "prom": prom}

print(f"BQ rows: {len(bq_data)}")

# --- 3. Compute NPS per (office, CDU, week) ---
stats = defaultdict(lambda: {"n": 0, "det": 0, "prom": 0})
unmatched = 0
for cid, info in case_info.items():
    if cid not in bq_data:
        unmatched += 1
        continue
    bq = bq_data[cid]
    key = (info["office"], bq["CDU"], info["week"])
    stats[key]["n"]    += 1
    stats[key]["det"]  += bq["det"]
    stats[key]["prom"] += bq["prom"]

print(f"Unmatched cases (in CSV but not in BQ): {unmatched}\n")

def nps(s):
    if s["n"] == 0: return None
    return round((s["prom"] - s["det"]) / s["n"] * 100, 1)

# --- 4. Print & collect table data per office ---
result = {}  # office -> list of row dicts
for office in sorted(OFFICES_DISPLAY):
    cdus = sorted({cdu for (o, cdu, w) in stats if o == office})
    rows = []
    for cdu in cdus:
        s2 = stats.get((office, cdu, "S2"), {"n":0,"det":0,"prom":0})
        s1 = stats.get((office, cdu, "S1"), {"n":0,"det":0,"prom":0})
        n2, n1 = nps(s2), nps(s1)
        var = round(n1 - n2, 1) if n2 is not None and n1 is not None else None
        rows.append({"cdu": cdu,
                     "s2_n": s2["n"], "s2_det": s2["det"], "s2_nps": n2,
                     "s1_n": s1["n"], "s1_det": s1["det"], "s1_nps": n1,
                     "var": var})
    rows.sort(key=lambda r: (r["var"] if r["var"] is not None else 0))
    result[office] = rows

    print(f"\n=== {office} ===")
    hdr = f"{'CDU':<32} {'S2 Pesq':>8} {'S2 Det':>7} {'S2 NPS':>8} {'S1 Pesq':>8} {'S1 Det':>7} {'S1 NPS':>8} {'Var':>8}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        s2nps = f"{r['s2_nps']:.1f}" if r['s2_nps'] is not None else "N/A"
        s1nps = f"{r['s1_nps']:.1f}" if r['s1_nps'] is not None else "N/A"
        var   = f"{r['var']:+.1f}"   if r['var']    is not None else "N/A"
        print(f"{r['cdu']:<32} {r['s2_n']:>8} {r['s2_det']:>7} {s2nps:>8} {r['s1_n']:>8} {r['s1_det']:>7} {s1nps:>8} {var:>8}")

print("\nDone.")
