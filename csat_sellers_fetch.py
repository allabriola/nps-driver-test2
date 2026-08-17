#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csat_sellers_fetch.py — Busca dados de CSAT dos 13 times FBM Sellers BR do BigQuery

Tabela principal: meli-bi-data.WHOWNER.BT_CX_CSAT_DETAIL
  (diferente da Longtail que usa DM_CX_CSAT_Y20_DETAIL — esses times não têm
   KM_SEGMENT / CX_USER_EXPERIENCE / SURVEY_TARGET_VALUE nessa tabela)

Colunas usadas:
  CSAT_TEAM, PROCESO_AGRUPADO_CSAT, ANSWERED_DATE, ANSWERED_MONTH,
  SATISFIED, ANSWER_SCORE, ELIGIBLE_CS, IS_EXCLUDED, IS_ANSWERED

Equipes: BR_FBM_Seller_Offline_Premium, BR_ME_Sellers_Longtail, MELI_PRO_MLB,
         BR_FBM_Seller_SML, BR_FBM_Seller_Longtail, BR_FBM_Seller_Xdock,
         BR_Shipping_Sellers, BR_ME_Seller_Complaint, BR_FBM_Coletar,
         BR_Seller_FulfFlex, BR_FBM_Seller_Meli_Delivery,
         BR_ME_Sellers_Xdock_FBM, BR_ME_Sellers_Xdock_Marketplace

Saída: _csat_sellers_data.json
"""
import sys, json, time
from datetime import date, timedelta
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

from google.cloud import bigquery
client = bigquery.Client(project="meli-bi-data")

# ── Datas ─────────────────────────────────────────────────────────────────────
TODAY     = date.today()
YESTERDAY = TODAY - timedelta(days=1)
MONTH_START = date(TODAY.year, TODAY.month, 1)

# Segunda-feira da semana vigente (do D-1)
WEEK_START = YESTERDAY - timedelta(days=YESTERDAY.weekday())

# Histórico semanal: últimas 12 semanas
HIST_START = WEEK_START - timedelta(weeks=11)

# Janela: 3 meses (mês corrente + 2 anteriores)
if MONTH_START.month >= 3:
    DATA_START = date(MONTH_START.year, MONTH_START.month - 2, 1)
elif MONTH_START.month == 2:
    DATA_START = date(MONTH_START.year - 1, 12, 1)
else:  # janeiro
    DATA_START = date(MONTH_START.year - 1, 11, 1)

MES_PT = {"01":"jan","02":"fev","03":"mar","04":"abr","05":"mai","06":"jun",
          "07":"jul","08":"ago","09":"set","10":"out","11":"nov","12":"dez"}

# ── Configuração ──────────────────────────────────────────────────────────────
TEAMS = [
    'BR_ME_Sellers_Longtail',
    'BR_Ventas_Sellers_Longtail',
    'BR_Publicaciones_Sellers_Longtail',
]
TEAMS_SQL = ", ".join(f"'{t}'" for t in TEAMS)

TABLE_BT   = "`meli-bi-data.WHOWNER.BT_CX_CSAT_DETAIL`"
TABLE_HALO = "`meli-bi-data.WHOWNER.DM_CX_HALO`"
TABLE_TR   = "`meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT_CHATS`"

# BT_CX_CSAT_DETAIL: sem KM_STATUS / KM_SEGMENT / CX_USER_EXPERIENCE
BASE_FILTER = f"""
    b.IS_ANSWERED = TRUE
    AND b.ELIGIBLE_CS = TRUE
    AND COALESCE(b.IS_EXCLUDED, FALSE) = FALSE
    AND b.AGENT_TEAM_NAME IN ({TEAMS_SQL})
"""

# ── Helper ─────────────────────────────────────────────────────────────────────
def run(sql: str, retries: int = 4, label: str = "") -> list[dict]:
    for attempt in range(retries):
        try:
            rows = [dict(r) for r in client.query(sql).result()]
            for r in rows:
                for k, v in r.items():
                    if hasattr(v, 'isoformat'):
                        r[k] = v.isoformat()
                    elif hasattr(v, '__float__'):
                        r[k] = float(v)
            print(f"   ✓ {label or 'query'}: {len(rows)} linhas")
            return rows
        except Exception as e:
            if "Quota" in str(e) and attempt < retries - 1:
                wait = 30 * (attempt + 1)
                print(f"   [quota] {label} — aguardando {wait}s…")
                time.sleep(wait)
            else:
                print(f"   ✗ {label}: {e}")
                raise

def safe_run(sql: str, label: str = "") -> list[dict]:
    try:
        return run(sql, label=label)
    except Exception as e:
        print(f"   ! {label} falhou (skip): {e}")
        return []

def csat_val(satisfied, total):
    if total and total > 0:
        return round(float(satisfied) / float(total) * 100, 2)
    return None

def gap(c, t):
    if c is not None and t is not None:
        return round(c - t, 2)
    return None

def agg(rows, group_keys):
    """Agrega por group_keys. Sem target (BT não tem SURVEY_TARGET_VALUE)."""
    bucket = defaultdict(lambda: {"total": 0, "satisfied": 0.0, "bottom_box": 0})
    for r in rows:
        key = tuple(str(r.get(k) or "") for k in group_keys)
        bucket[key]["total"]      += int(r.get("total") or 0)
        bucket[key]["satisfied"]  += float(r.get("satisfied") or 0)
        bucket[key]["bottom_box"] += int(r.get("bottom_box") or 0)
    out = []
    for key, v in bucket.items():
        t_  = v["total"]
        bb_ = v["bottom_box"]
        c_  = csat_val(v["satisfied"], t_)
        bb_pct = round(bb_ / t_ * 100, 1) if t_ else None
        item = {k: key[i] for i, k in enumerate(group_keys)}
        item.update({"total": t_, "csat": c_, "target": None, "gap": None,
                     "bottom_box": bb_, "bottom_box_pct": bb_pct})
        out.append(item)
    return sorted(out, key=lambda x: -x["total"])

# ── Query 1: Dados mensais ────────────────────────────────────────────────────
print("\n[1/5] Dados mensais (raw)…")
SQL_MONTHLY_RAW = f"""
SELECT
    FORMAT_DATE('%Y-%m', DATE(b.ANSWERED_DTTM))                    AS month,
    b.AGENT_TEAM_NAME                                              AS team,
    COALESCE(NULLIF(TRIM(b.PROCESO_AGRUPADO_CSAT),''),'(sem proc)') AS process,
    COUNT(*)                                                       AS total,
    CAST(SUM(b.SATISFIED) AS FLOAT64)                              AS satisfied,
    COUNTIF(CAST(b.ANSWER_SCORE AS INT64) <= 2)                    AS bottom_box
FROM {TABLE_BT} b
WHERE DATE(b.ANSWERED_DTTM) BETWEEN DATE('{DATA_START}') AND DATE('{YESTERDAY}')
  AND {BASE_FILTER}
GROUP BY 1, 2, 3
ORDER BY 1, 2, total DESC
"""
monthly_raw = run(SQL_MONTHLY_RAW, label="monthly_raw")

# ── Query 2: Dados semanais ───────────────────────────────────────────────────
print("\n[2/5] Dados semanais (raw)…")
SQL_WEEKLY_RAW = f"""
SELECT
    b.AGENT_TEAM_NAME                                              AS team,
    COALESCE(NULLIF(TRIM(b.PROCESO_AGRUPADO_CSAT),''),'(sem proc)') AS process,
    COUNT(*)                                                       AS total,
    CAST(SUM(b.SATISFIED) AS FLOAT64)                              AS satisfied,
    COUNTIF(CAST(b.ANSWER_SCORE AS INT64) <= 2)                    AS bottom_box
FROM {TABLE_BT} b
WHERE DATE(b.ANSWERED_DTTM) BETWEEN DATE('{WEEK_START}') AND DATE('{YESTERDAY}')
  AND {BASE_FILTER}
GROUP BY 1, 2
ORDER BY 1, total DESC
"""
weekly_raw = run(SQL_WEEKLY_RAW, label="weekly_raw")

# ── Query 2.5: Histórico semanal (últimas 12 semanas por equipe) ──────────────
print(f"\n[2.5/5] Histórico semanal ({HIST_START} → {YESTERDAY})…")
SQL_WEEKLY_HIST = f"""
SELECT
    DATE_TRUNC(DATE(b.ANSWERED_DTTM), WEEK(MONDAY)) AS week_start,
    b.AGENT_TEAM_NAME                                              AS team,
    COUNT(*)                                                       AS total,
    CAST(SUM(b.SATISFIED) AS FLOAT64)                              AS satisfied,
    COUNTIF(CAST(b.ANSWER_SCORE AS INT64) <= 2)                    AS bottom_box
FROM {TABLE_BT} b
WHERE DATE(b.ANSWERED_DTTM) BETWEEN DATE('{HIST_START}') AND DATE('{YESTERDAY}')
  AND {BASE_FILTER}
GROUP BY 1, 2
ORDER BY 1, 2
"""
weekly_hist_raw = safe_run(SQL_WEEKLY_HIST, label="weekly_history")

# ── Query 3: Response Rate mensal ─────────────────────────────────────────────
print("\n[3/5] Response Rate mensal…")
SQL_RR_MONTHLY = f"""
SELECT
    FORMAT_DATE('%Y-%m', DATE(b.SENT_DTTM)) AS month,
    b.AGENT_TEAM_NAME                              AS team,
    COUNT(*)                                 AS sent,
    COUNTIF(b.IS_ANSWERED = TRUE)            AS answered
FROM {TABLE_BT} b
WHERE b.HAS_HUMAN_INTERACTION = TRUE
  AND b.ELIGIBLE_CS = TRUE
  AND b.AGENT_TEAM_NAME IN ({TEAMS_SQL})
  AND DATE(b.SENT_DTTM) BETWEEN DATE('{DATA_START}') AND DATE('{YESTERDAY}')
GROUP BY 1, 2
ORDER BY 1, 2
"""
rr_monthly = safe_run(SQL_RR_MONTHLY, label="response_rate_monthly")

# ── Query 4: Response Rate semanal ────────────────────────────────────────────
print("\n[4/5] Response Rate semanal…")
SQL_RR_WEEKLY = f"""
SELECT
    b.AGENT_TEAM_NAME AS team,
    COUNT(*)     AS sent,
    COUNTIF(b.IS_ANSWERED = TRUE) AS answered
FROM {TABLE_BT} b
WHERE b.HAS_HUMAN_INTERACTION = TRUE
  AND b.ELIGIBLE_CS = TRUE
  AND b.AGENT_TEAM_NAME IN ({TEAMS_SQL})
  AND DATE(b.SENT_DTTM) BETWEEN DATE('{WEEK_START}') AND DATE('{YESTERDAY}')
GROUP BY 1
ORDER BY 1
"""
rr_weekly = safe_run(SQL_RR_WEEKLY, label="response_rate_weekly")

# ── Query 5: Diagnóstico (comentários detratores) ─────────────────────────────
# BT não tem transcrições; usamos apenas ANSWER_COMMENT
print("\n[5/5] Diagnóstico (comentários detratores)…")

def q_diagnostic(date_start, date_end, label="diag"):
    return f"""
    SELECT
        b.AGENT_TEAM_NAME                                              AS team,
        COALESCE(NULLIF(TRIM(b.PROCESO_AGRUPADO_CSAT),''),'(sem proc)') AS process,
        CAST(b.ANSWER_SCORE AS INT64)                                  AS score,
        REPLACE(COALESCE(CAST(b.ANSWER_COMMENT AS STRING), ''), '"', ' ') AS comentario,
        ''                                                             AS transcricao
    FROM {TABLE_BT} b
    WHERE DATE(b.ANSWERED_DTTM) BETWEEN DATE('{date_start}') AND DATE('{date_end}')
      AND {BASE_FILTER}
      AND CAST(b.ANSWER_SCORE AS INT64) <= 2
      AND CAST(b.ANSWER_COMMENT AS STRING) IS NOT NULL
      AND LENGTH(TRIM(CAST(b.ANSWER_COMMENT AS STRING))) > 5
    ORDER BY b.AGENT_TEAM_NAME, b.PROCESO_AGRUPADO_CSAT, b.ANSWER_SCORE
    LIMIT 2000
    """

diag_monthly = safe_run(q_diagnostic(MONTH_START, YESTERDAY), label="diag_monthly")
diag_weekly  = safe_run(q_diagnostic(WEEK_START,  YESTERDAY), label="diag_weekly")

# ── Agrega dados em Python ─────────────────────────────────────────────────────
print("\nAgregando dados…")

def build_monthly_aggs(raw):
    return {
        "by_team":    agg(raw, ["month", "team"]),
        "by_process": agg(raw, ["month", "team", "process"]),
        # sem seniority/km_segment — BT não tem essas colunas
        "by_seniority": [],
        "by_segment":   [],
    }

def build_weekly_aggs(raw):
    return {
        "by_team":      agg(raw, ["team"]),
        "by_process":   agg(raw, ["team", "process"]),
        "by_seniority": [],
        "by_segment":   [],
    }

def build_weekly_hist(raw):
    """Retorna lista de {week_start, week_label, team, total, csat, bottom_box, bottom_box_pct}."""
    out = []
    for r in raw:
        t_ = int(r.get("total") or 0)
        sat_ = float(r.get("satisfied") or 0)
        bb_ = int(r.get("bottom_box") or 0)
        c_ = csat_val(sat_, t_)
        bb_pct = round(bb_ / t_ * 100, 1) if t_ else None
        ws = str(r.get("week_start") or "")
        # Formata label "dd/mm" a partir de "yyyy-mm-dd"
        wlbl = ws[8:10] + "/" + ws[5:7] if len(ws) >= 10 else ws
        out.append({
            "week_start":    ws,
            "week_label":    wlbl,
            "team":          str(r.get("team") or ""),
            "total":         t_,
            "csat":          c_,
            "bottom_box":    bb_,
            "bottom_box_pct": bb_pct,
        })
    return out

def process_rr(rows, keys):
    out = []
    for r in rows:
        sent = int(r.get("sent") or 0)
        answered = int(r.get("answered") or 0)
        item = {k: r.get(k) for k in keys}
        item["sent"]     = sent
        item["answered"] = answered
        item["rr_pct"]   = round(answered / sent * 100, 1) if sent else None
        out.append(item)
    return out

def build_diag_index(rows):
    idx = defaultdict(lambda: defaultdict(list))
    for r in rows:
        idx[r["team"]][r["process"]].append({
            "score":      int(r.get("score") or 0),
            "comentario": str(r.get("comentario") or "").strip(),
            "transcricao": "",
        })
    return {t: dict(procs) for t, procs in idx.items()}

# ── Monta estrutura final ──────────────────────────────────────────────────────
months_avail = sorted({r["month"] for r in monthly_raw})
month_labels = {m: f"{MES_PT.get(m.split('-')[1], m.split('-')[1])}/{m.split('-')[0][2:]}"
                for m in months_avail}

week_label = f"{WEEK_START.strftime('%d/%m')}–{YESTERDAY.strftime('%d/%m')}"
month_cur_label = f"{MES_PT.get(MONTH_START.strftime('%m'), '')} MTD"

data = {
    "updated_at":       YESTERDAY.isoformat(),
    "today":            TODAY.isoformat(),
    "month_start":      MONTH_START.isoformat(),
    "week_start":       WEEK_START.isoformat(),
    "yesterday":        YESTERDAY.isoformat(),
    "month_cur":        MONTH_START.strftime("%Y-%m"),
    "month_cur_label":  month_cur_label,
    "week_label":       week_label,
    "months":           months_avail,
    "month_labels":     month_labels,
    "teams":            TEAMS,

    "monthly":        build_monthly_aggs(monthly_raw),
    "weekly":         build_weekly_aggs(weekly_raw),
    "weekly_history": build_weekly_hist(weekly_hist_raw),

    "response_rate": {
        "monthly": process_rr(rr_monthly, ["month", "team"]),
        "weekly":  process_rr(rr_weekly,  ["team"]),
    },

    # HALO: tentamos direto via BT — times FBM podem não ter HALO
    "halo": {"monthly": [], "weekly": []},

    "diagnostic_raw": {
        "monthly": build_diag_index(diag_monthly),
        "weekly":  build_diag_index(diag_weekly),
    },
}

# ── Salva JSON ─────────────────────────────────────────────────────────────────
OUT = "_csat_sellers_data.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

print(f"\n✅ Salvo: {OUT}")
print(f"   Tabela fonte    : BT_CX_CSAT_DETAIL (CSAT_TEAM / PROCESO_AGRUPADO_CSAT)")
print(f"   Período mensal  : {DATA_START} → {YESTERDAY}")
print(f"   Período semanal : {WEEK_START} → {YESTERDAY}")
print(f"   Meses           : {months_avail}")
print(f"   Equipes c/dados : {[r['team'] for r in data['monthly']['by_team']]}")
