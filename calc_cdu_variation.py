import sys
import csv
import subprocess
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CSV_PATH = r"c:\Users\allabriola\Downloads\DD Mgmt - General vs Target_Datos completos_data (32).csv"

TEAMS = {
    "BR_Ventas_Sellers_Longtail",
    "BR_Publicaciones_Sellers_Longtail",
    "BR_ME_Sellers_Longtail",
}
OFFICES = {"ATE", "CTX", "KTA"}

# Week labels: OPEN_BY_DATE_FORMATTED
WEEK_S2 = "30 Mar 26"
WEEK_S1 = "6 Apr 26"

# --- 1. Read CSV ---
case_info = {}  # CAS_CASE_ID -> {week, office}

with open(CSV_PATH, encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        team = row.get("USER_TEAM_NAME", "").strip()
        office = row.get("USER_OFFICE", "").strip()
        week = row.get("OPEN_BY_DATE_FORMATTED", "").strip()
        case_id = row.get("CAS_CASE_ID", "").strip()

        if team not in TEAMS:
            continue
        if office not in OFFICES:
            continue
        if week not in (WEEK_S2, WEEK_S1):
            continue
        if not case_id:
            continue

        case_info[case_id] = {
            "week": "S2" if week == WEEK_S2 else "S1",
            "office": office,
        }

print(f"Cases found in CSV: {len(case_info)}")

if not case_info:
    print("No cases found. Check CSV path and filters.")
    sys.exit(1)

# --- 2. Build BigQuery query ---
ids_list = ", ".join(str(int(cid)) for cid in case_info.keys() if cid.isdigit())
query = f"""
SELECT
  CAS_CASE_ID,
  CDU,
  CX_USER_OFFICE,
  DETRACTOR,
  PROMOTER
FROM `meli-bi-data.WHOWNER.BT_CX_NPS_DETAIL`
WHERE CAS_CASE_ID IN ({ids_list})
  AND PRO_PROCESS_NAME = 'Reputación ME'
"""

# Save query to temp file to avoid shell quoting issues
query_file = r"C:\claudinho\tmp_cdu_query.sql"
with open(query_file, 'w', encoding='utf-8') as f:
    f.write(query)

print("Running BigQuery query...")
BQ_CMD = r"C:\Users\allabriola\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"
result = subprocess.run(
    [BQ_CMD, "query", "--use_legacy_sql=false", "--format=json", "--max_rows=10000",
     "--project_id=meli-bi-data"],
    input=open(query_file, encoding='utf-8').read(),
    capture_output=True, text=True, encoding='utf-8', errors='replace',
    shell=True
)

if result.returncode != 0:
    print("BQ ERROR:", result.stderr)
    sys.exit(1)

# --- 3. Parse BQ results ---
bq_rows = json.loads(result.stdout)
print(f"BQ rows returned: {len(bq_rows)}")

# Map CAS_CASE_ID -> {CDU, DETRACTOR, PROMOTER}
bq_data = {}
for row in bq_rows:
    cid = str(row.get("CAS_CASE_ID", "")).strip()
    bq_data[cid] = {
        "CDU": str(row.get("CDU", "N/A")).strip(),
        "DETRACTOR": int(row.get("DETRACTOR", 0) or 0),
        "PROMOTER": int(row.get("PROMOTER", 0) or 0),
    }

# --- 4. Calculate NPS per (office, CDU, week) ---
# Structure: stats[(office, cdu, week)] = {surveys, detractors, promoters}
stats = defaultdict(lambda: {"surveys": 0, "detractors": 0, "promoters": 0})

for case_id, info in case_info.items():
    if case_id not in bq_data:
        # Case not in BQ — skip (might have no NPS record)
        continue
    bq = bq_data[case_id]
    key = (info["office"], bq["CDU"], info["week"])
    stats[key]["surveys"] += 1
    stats[key]["detractors"] += bq["DETRACTOR"]
    stats[key]["promoters"] += bq["PROMOTER"]

# --- 5. Print tables per office ---
def calc_nps(s):
    n = s["surveys"]
    if n == 0:
        return None
    return round((s["promoters"] - s["detractors"]) / n * 100, 1)

for office in sorted(OFFICES):
    # Collect all CDUs for this office
    cdus = set()
    for (o, cdu, w) in stats:
        if o == office:
            cdus.add(cdu)

    print(f"\n=== {office} ===")
    print(f"{'CDU':<35} {'S2 Pesq':>8} {'S2 Det':>7} {'S2 NPS':>8} {'S1 Pesq':>8} {'S1 Det':>7} {'S1 NPS':>8} {'Var':>8}")
    print("-" * 100)

    rows = []
    for cdu in sorted(cdus):
        s2 = stats.get((office, cdu, "S2"), {"surveys": 0, "detractors": 0, "promoters": 0})
        s1 = stats.get((office, cdu, "S1"), {"surveys": 0, "detractors": 0, "promoters": 0})
        nps_s2 = calc_nps(s2)
        nps_s1 = calc_nps(s1)
        if nps_s2 is not None and nps_s1 is not None:
            var = round(nps_s1 - nps_s2, 1)
        else:
            var = None
        rows.append((cdu, s2, s1, nps_s2, nps_s1, var))

    # Sort by absolute variation (biggest drop first)
    rows.sort(key=lambda r: (r[5] if r[5] is not None else 0))

    for (cdu, s2, s1, nps_s2, nps_s1, var) in rows:
        nps_s2_str = f"{nps_s2:.1f}" if nps_s2 is not None else "N/A"
        nps_s1_str = f"{nps_s1:.1f}" if nps_s1 is not None else "N/A"
        var_str = f"{var:+.1f}" if var is not None else "N/A"
        print(f"{cdu:<35} {s2['surveys']:>8} {s2['detractors']:>7} {nps_s2_str:>8} {s1['surveys']:>8} {s1['detractors']:>7} {nps_s1_str:>8} {var_str:>8}")

print("\nDone.")
