#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Para cada driver prioritário, busca CAS_CASE_IDs dos CDUs com maior
aumento e maior queda, depois puxa transcrições do BT_CX_TRANSCRIPT.
"""
import sys, json, math
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
client = bigquery.Client(project="meli-bi-data")

S1_START, S1_END = "2026-04-27", "2026-05-03"

with open("dd_breakdown.json", encoding="utf-8") as f:
    DD = json.load(f)

def get_procs(driver):
    p = DD.get(driver, {}).get("P", {})
    procs = set()
    for pd in p.values():
        procs.update(pd.keys())
    return list(procs)

# Drivers prioritários e seus CDU/solução alvo
TARGETS = {
    "ME Vendedor Seller Dev": {
        "queda": ("Problemas para despachar un paquete/producto", "Desativar ME"),
        "alta":  ("Reclama por el costo de envío", "Envio pelo V"),
    },
    "Partners": {
        "queda": ("Tiene problemas durante la creacion de la cuenta", "ME Extra: conflito"),
        "alta":  ("Tiene problemas durante la creacion de la cuenta", "ME Extra: consulta"),
    },
    "Publicaciones Seller Dev": {
        "queda": ("Configuración y funcionalidades", "Afiliados - Programa de criadores"),
        "alta":  ("Activar/desactivar", "Afiliados - Como ativar"),
    },
    "Post Venta Seller Dev": {
        "queda": ("Reclamos", "Analisamos reputação - Reclamação não afeta"),
        "alta":  ("Reclamos", "Analisamos reputação - Reclamação afeta"),
    },
    "PCF Vendedor Seller Dev": {
        "queda": ("Mediación abierta", "Mediação aberta com IA"),
        "alta":  ("Devoluciones", "Devolução - Recebeu devolução fallida"),
    },
}

def get_case_ids(driver, cdu_prefix, sol_prefix, limit=30):
    """Busca CAS_CASE_IDs para CDU+solução em S1."""
    procs = get_procs(driver)
    if not procs:
        return []
    procs_in = "'" + "','".join(p.replace("'","''") for p in procs[:20]) + "'"
    q = f"""
    SELECT CAST(CAS_CASE_ID AS STRING) AS cid, NPS, CDU, CX_SOL_NAME, PROMOTER, DETRACTOR
    FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
    WHERE SIT_SITE_ID = 'MLB'
      AND SURVEY_CENTER = 'BR'
      AND SURVEY_DATE_SURVEY BETWEEN '{S1_START}' AND '{S1_END}'
      AND PRO_PROCESS_NAME IN ({procs_in})
      AND CDU LIKE '%{cdu_prefix[:30]}%'
      AND CX_SOL_NAME LIKE '%{sol_prefix[:30]}%'
    ORDER BY RAND()
    LIMIT {limit}
    """
    rows = list(client.query(q).result())
    return [{"cid": r.cid, "nps": int(r.NPS or 0),
             "cdu": r.CDU, "sol": r.CX_SOL_NAME,
             "promoter": int(r.PROMOTER or 0), "detractor": int(r.DETRACTOR or 0)} for r in rows]

def get_transcripts(case_ids, limit_per_case=6):
    """Busca transcrições em batch de CAS_CASE_IDs."""
    if not case_ids:
        return {}
    ids_str = ",".join(case_ids[:200])
    q = f"""
    SELECT
      CAST(CAS_CASE_ID AS STRING) AS cid,
      SPEAKER_ROLE,
      SUBSTR(COALESCE(OBFUSCATED_MESSAGE_CONTENT,''),1,300) AS msg,
      INITIAL_DTTM
    FROM `meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT`
    WHERE CAS_CASE_ID IN ({ids_str})
      AND SPEAKER_ROLE IN ('USER','REP')
    ORDER BY CAS_CASE_ID, INITIAL_DTTM
    """
    rows = list(client.query(q).result())
    by_case = {}
    for r in rows:
        cid = r.cid
        if cid not in by_case:
            by_case[cid] = []
        by_case[cid].append(f"[{r.SPEAKER_ROLE}] {r.msg}")
    return {cid: "\n".join(msgs[:limit_per_case]) for cid, msgs in by_case.items()}

# ── MAIN ──────────────────────────────────────────────────────────────────────
all_results = {}

for driver, targets in TARGETS.items():
    print(f"\n{'='*60}")
    print(f"Driver: {driver}")
    print(f"{'='*60}")
    driver_result = {}

    for direction, (cdu_pfx, sol_pfx) in targets.items():
        print(f"\n  [{direction.upper()}] CDU: '{cdu_pfx[:40]}' | Sol: '{sol_pfx[:40]}'")
        cases = get_case_ids(driver, cdu_pfx, sol_pfx, limit=25)
        print(f"  Cases encontrados: {len(cases)}")
        if not cases:
            driver_result[direction] = {"cases": [], "transcripts": {}}
            continue

        # Separar promotores e detratores
        promotores = [c for c in cases if c["promoter"] == 1]
        detratores = [c for c in cases if c["detractor"] == 1]
        print(f"  Promotores: {len(promotores)} | Detratores: {len(detratores)}")

        # Buscar transcriptions
        all_ids = [c["cid"] for c in cases]
        transcripts = get_transcripts(all_ids)
        print(f"  Transcricoes encontradas: {len(transcripts)}")

        # Montar resultado
        cases_with_transcripts = []
        for c in cases:
            t = transcripts.get(c["cid"], "")
            if t:
                cases_with_transcripts.append({
                    "cid": c["cid"],
                    "nps": c["nps"],
                    "tipo": "promotor" if c["promoter"] == 1 else ("detrator" if c["detractor"] == 1 else "passivo"),
                    "cdu": c["cdu"],
                    "sol": c["sol"],
                    "transcript": t
                })

        driver_result[direction] = {
            "cdu": cdu_pfx,
            "sol": sol_pfx,
            "n_cases": len(cases),
            "n_promotores": len(promotores),
            "n_detratores": len(detratores),
            "cases": cases_with_transcripts,
        }

        # Print sample transcripts
        for c in cases_with_transcripts[:3]:
            print(f"\n    [{c['tipo'].upper()}] Case {c['cid']} (NPS={c['nps']}):")
            for line in c["transcript"].split("\n")[:4]:
                print(f"      {line[:120]}")

    all_results[driver] = driver_result

with open("_transcripts_by_driver.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
print(f"\n\nSalvo em _transcripts_by_driver.json")
