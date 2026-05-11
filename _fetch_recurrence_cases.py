#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca casos de exemplo de detratores (NPS=-1) por processo top ofensor,
cruza com BT_CX_TRANSCRIPT e salva em _recurrence_cases.json.
Usado por generate_html_tendencias.py e generate_html_seller_dev.py.
"""
import json, time, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
bq = bigquery.Client(project="meli-bi-data")

# ── Carrega top processos negativos de _process_analysis.json ──────────
with open('_process_analysis.json', encoding='utf-8') as f:
    PA = json.load(f)

# Datas dos períodos
with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)
S1_LABEL = ns.get('S1_LABEL', '')

# Extrai datas S1 do label (ex: "04/mai – 10/mai")
MON_NUM = {"jan":"01","fev":"02","mar":"03","abr":"04","mai":"05",
           "jun":"06","jul":"07","ago":"08","set":"09","out":"10","nov":"11","dez":"12"}
def parse_label_date(lbl_part, year="2026"):
    lbl_part = lbl_part.strip().replace("‪","").replace("‎","").strip()
    parts = lbl_part.split("/")
    if len(parts) == 2:
        day, mon = parts[0].strip().zfill(2), parts[1].strip().lower()
        return f"{year}-{MON_NUM.get(mon,'05')}-{day}"
    return None

if S1_LABEL and "–" in S1_LABEL:
    s1_parts = S1_LABEL.split("–")
    S1_START = parse_label_date(s1_parts[0]) or "2026-05-04"
    S1_END   = parse_label_date(s1_parts[1]) or "2026-05-10"
else:
    S1_START, S1_END = "2026-05-04", "2026-05-10"

MON_START, MON_END = "2026-05-01", "2026-05-11"
ABR_START, ABR_END = "2026-04-01", "2026-04-30"

print(f"S1: {S1_START} a {S1_END}")
print(f"Mai MTD: {MON_START} a {MON_END}")

# ── Grupos de drivers e seus processos top ofensores ───────────────────
DRIVER_GROUPS_ALL = {
    "ME Vendedor":     ["ME Vendedor Seller Dev","ME Vendedor Mature","ME Vendedor Meli Pro"],
    "Exp. Impositiva": ["Experiencia Impositiva Seller Dev","Experiencia Impositiva Mature","Experiencia Impositiva Meli Pro"],
    "PCF Vendedor":    ["PCF Vendedor Seller Dev","PCF Vendedor Mature","PCF Vendedor Meli Pro"],
    "Post Venta":      ["Post Venta Seller Dev","Post Venta Mature","Post Venta Meli Pro"],
    "Publicaciones":   ["Publicaciones Seller Dev","Publicaciones Mature","Publicaciones Meli Pro"],
    "Partners":        ["Partners"],
    "Otros CV":        ["Otros CV"],
}

# ── SQLs ───────────────────────────────────────────────────────────────
SQL_CASE_IDS = """
SELECT CAST(CAS_CASE_ID AS STRING) AS case_id
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID = 'MLB'
  AND SURVEY_CENTER = 'BR'
  AND DETRACTOR = 1
  AND NPS = -1
  AND PRO_PROCESS_NAME = '{proc}'
  AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
  AND CAS_CASE_ID IS NOT NULL
ORDER BY RAND()
LIMIT 25
"""

SQL_TRX = """
SELECT
  CAST(CAS_CASE_ID AS STRING) AS cid,
  SPEAKER_ROLE,
  SUBSTR(COALESCE(OBFUSCATED_MESSAGE_CONTENT,''), 1, 350) AS msg,
  INITIAL_DTTM
FROM `meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT`
WHERE CAS_CASE_ID IN ({ids})
  AND SPEAKER_ROLE IN ('USER','REP')
ORDER BY CAS_CASE_ID, INITIAL_DTTM
"""

def fetch_case_ids(proc, start, end):
    sql = SQL_CASE_IDS.format(
        proc=proc.replace("'","''"), start=start, end=end)
    try:
        rows = list(bq.query(sql).result())
        return [r.case_id for r in rows if r.case_id]
    except Exception as e:
        print(f"    WARN case_ids: {e}")
        return []

def fetch_transcripts(case_ids, batch=900):
    result = {}
    for i in range(0, len(case_ids), batch):
        chunk = case_ids[i:i+batch]
        ids_str = ",".join(chunk)
        sql = SQL_TRX.format(ids=ids_str)
        try:
            rows = list(bq.query(sql).result())
            for r in rows:
                cid = r.cid
                if cid not in result:
                    result[cid] = []
                result[cid].append({"role": r.SPEAKER_ROLE, "msg": r.msg})
        except Exception as e:
            print(f"    WARN transcripts batch {i}: {e}")
        time.sleep(0.3)
    return result

def summarize_case(msgs):
    """Extrai o relato principal do seller e a resposta do atendente."""
    user_msgs = [m["msg"] for m in msgs if m["role"] == "USER" and len(m["msg"].strip()) > 25]
    rep_msgs  = [m["msg"] for m in msgs if m["role"] == "REP"  and len(m["msg"].strip()) > 25]
    # Filtra saudações genéricas
    skip = ["tudo bem","bom dia","boa tarde","quero falar","falar com atendente",
            "falar com um","assistente","preciso falar","queria falar"]
    meaningful_user = [m for m in user_msgs
                       if not any(s in m.lower() for s in skip)]
    complaint = meaningful_user[0] if meaningful_user else (user_msgs[0] if user_msgs else "")
    last_rep  = rep_msgs[-1] if rep_msgs else ""
    return {"complaint": complaint[:300], "last_rep": last_rep[:200],
            "n_msgs": len(msgs)}

# ── Principal ──────────────────────────────────────────────────────────
result = {}

for grp, drvs in DRIVER_GROUPS_ALL.items():
    neg = PA.get(grp, {}).get("top_neg", {})
    top_proc = neg.get("proc")
    if not top_proc:
        print(f"[{grp}] sem top_neg — pulando")
        continue

    print(f"\n{'='*60}")
    print(f"[{grp}] Top processo: {top_proc}")
    result[grp] = {"top_proc": top_proc, "weekly": {}, "monthly": {}}

    # S1 semanal
    print(f"  S1 ({S1_START} a {S1_END})...")
    wk_ids = fetch_case_ids(top_proc, S1_START, S1_END)
    print(f"    {len(wk_ids)} casos encontrados")
    time.sleep(0.5)

    if wk_ids:
        wk_trx = fetch_transcripts(wk_ids[:20])
        print(f"    {len(wk_trx)} transcrições")
        for cid, msgs in wk_trx.items():
            result[grp]["weekly"][cid] = summarize_case(msgs)

    # Mai mensal
    print(f"  Mai ({MON_START} a {MON_END})...")
    mon_ids = fetch_case_ids(top_proc, MON_START, MON_END)
    print(f"    {len(mon_ids)} casos encontrados")
    time.sleep(0.5)

    if mon_ids:
        mon_trx = fetch_transcripts(mon_ids[:20])
        print(f"    {len(mon_trx)} transcrições")
        for cid, msgs in mon_trx.items():
            result[grp]["monthly"][cid] = summarize_case(msgs)

    # Abr (mês anterior) — para validar recorrência
    print(f"  Abr ({ABR_START} a {ABR_END})...")
    abr_ids = fetch_case_ids(top_proc, ABR_START, ABR_END)
    print(f"    {len(abr_ids)} casos encontrados")
    time.sleep(0.5)
    result[grp]["abr_ids"] = abr_ids[:10]  # só IDs, sem transcrição completa

with open("_recurrence_cases.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n\nSalvo em _recurrence_cases.json")
print("Resumo:")
for grp, data in result.items():
    print(f"  {grp}: proc={data['top_proc']} | S1={len(data['weekly'])} | Mai={len(data['monthly'])} | Abr={len(data['abr_ids'])}")
