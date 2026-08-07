#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csat_fetch.py — Busca dados de CSAT do BigQuery e salva em _csat_data.json

Tabela principal: meli-bi-data.WHOWNER.DM_CX_CSAT_Y20_DETAIL
Equipes: BR_ME_Sellers_Longtail, BR_Publicaciones_Sellers_Longtail,
         BR_Ventas_Sellers_Longtail, MLB_ExpImpo

Saída: _csat_data.json
"""
import sys, json, re, time
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
    'BR_Publicaciones_Sellers_Longtail',
    'BR_Ventas_Sellers_Longtail',
    'MLB_ExpImpo',
]
TEAMS_SQL = ", ".join(f"'{t}'" for t in TEAMS)

TABLE_Y20    = "`meli-bi-data.WHOWNER.DM_CX_CSAT_Y20_DETAIL`"
TABLE_CSAT   = "`meli-bi-data.WHOWNER.DM_CX_CSAT`"
TABLE_TR     = "`meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT_CHATS`"
TABLE_BT     = "`meli-bi-data.WHOWNER.BT_CX_CSAT_DETAIL`"
TABLE_HALO   = "`meli-bi-data.WHOWNER.DM_CX_HALO`"
TABLE_SEG    = "`meli-bi-data.WHOWNER.LK_CX_SEGMENTO_SELLERS_PHOTO`"

BASE_FILTER = f"""
    y.IS_ANSWERED = TRUE
    AND y.ELIGIBLE_CS = TRUE
    AND COALESCE(y.IS_EXCLUDED, FALSE) = FALSE
    AND COALESCE(y.KM_STATUS, 'NEWBIE') NOT IN ('TRAINING', 'UNAVAILABLE')
    AND y.KM_SEGMENT IS NOT NULL
    AND y.AGENT_TEAM_NAME IN ({TEAMS_SQL})
"""

# ── Helper ─────────────────────────────────────────────────────────────────────
def run(sql: str, retries: int = 4, label: str = "") -> list[dict]:
    for attempt in range(retries):
        try:
            rows = [dict(r) for r in client.query(sql).result()]
            # Converte tipos não-serializáveis (Date, Decimal, etc.)
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
    """Roda query; retorna [] em caso de erro (para queries opcionais)."""
    try:
        return run(sql, label=label)
    except Exception as e:
        print(f"   ! {label} falhou (skip): {e}")
        return []

def csat(satisfied, total):
    if total and total > 0:
        return round(float(satisfied) / float(total) * 100, 2)
    return None

def target(target_sum, total):
    if total and total > 0:
        return round(float(target_sum) / float(total) * 100, 2)
    return None

def gap(c, t):
    if c is not None and t is not None:
        return round(c - t, 2)
    return None

def agg(rows, group_keys):
    """Agrega linhas por group_keys, somando total/satisfied/target_sum."""
    bucket = defaultdict(lambda: {"total": 0, "satisfied": 0.0, "target_sum": 0.0})
    for r in rows:
        key = tuple(str(r.get(k) or "") for k in group_keys)
        bucket[key]["total"]      += int(r.get("total") or 0)
        bucket[key]["satisfied"]  += float(r.get("satisfied") or 0)
        bucket[key]["target_sum"] += float(r.get("target_sum") or 0)
    out = []
    for key, v in bucket.items():
        t_ = v["total"]
        c_ = csat(v["satisfied"], t_)
        tg = target(v["target_sum"], t_)
        item = {k: key[i] for i, k in enumerate(group_keys)}
        item.update({"total": t_, "csat": c_, "target": tg, "gap": gap(c_, tg)})
        out.append(item)
    return sorted(out, key=lambda x: -x["total"])

# ── Query 1: Dados mensais (raw — todas as dimensões num único scan) ───────────
print("\n[1/8] Dados mensais (raw)…")
SQL_MONTHLY_RAW = f"""
SELECT
    FORMAT_DATE('%Y-%m', DATE(y.ANSWERED_DTTM))                 AS month,
    y.AGENT_TEAM_NAME                                            AS team,
    COALESCE(NULLIF(TRIM(y.PROCESS_NAME), ''), '(sem processo)') AS process,
    COALESCE(y.CX_USER_EXPERIENCE, 'NEWBIE')                     AS seniority,
    y.KM_SEGMENT                                                 AS km_segment,
    COUNT(*)                                                     AS total,
    CAST(SUM(y.SATISFIED) AS FLOAT64)                            AS satisfied,
    CAST(SUM(y.SURVEY_TARGET_VALUE) AS FLOAT64)                  AS target_sum
FROM {TABLE_Y20} y
WHERE DATE(y.ANSWERED_DTTM) BETWEEN DATE('{DATA_START}') AND DATE('{YESTERDAY}')
  AND {BASE_FILTER}
GROUP BY 1, 2, 3, 4, 5
ORDER BY 1, 2, total DESC
"""
monthly_raw = run(SQL_MONTHLY_RAW, label="monthly_raw")

# ── Query 2: Dados semanais (raw) ─────────────────────────────────────────────
print("\n[2/8] Dados semanais (raw)…")
SQL_WEEKLY_RAW = f"""
SELECT
    y.AGENT_TEAM_NAME                                            AS team,
    COALESCE(NULLIF(TRIM(y.PROCESS_NAME), ''), '(sem processo)') AS process,
    COALESCE(y.CX_USER_EXPERIENCE, 'NEWBIE')                     AS seniority,
    y.KM_SEGMENT                                                 AS km_segment,
    COUNT(*)                                                     AS total,
    CAST(SUM(y.SATISFIED) AS FLOAT64)                            AS satisfied,
    CAST(SUM(y.SURVEY_TARGET_VALUE) AS FLOAT64)                  AS target_sum
FROM {TABLE_Y20} y
WHERE DATE(y.ANSWERED_DTTM) BETWEEN DATE('{WEEK_START}') AND DATE('{YESTERDAY}')
  AND {BASE_FILTER}
GROUP BY 1, 2, 3, 4
ORDER BY 1, total DESC
"""
weekly_raw = run(SQL_WEEKLY_RAW, label="weekly_raw")

# ── Query 3: Response Rate mensal ─────────────────────────────────────────────
print("\n[3/8] Response Rate mensal…")
SQL_RR_MONTHLY = f"""
SELECT
    FORMAT_DATE('%Y-%m', DATE(b.SENT_DTTM)) AS month,
    b.AGENT_TEAM_NAME                        AS team,
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
print("\n[4/8] Response Rate semanal…")
SQL_RR_WEEKLY = f"""
SELECT
    b.AGENT_TEAM_NAME AS team,
    COUNT(*)          AS sent,
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

# ── Query 5: HALO KPIs mensal ─────────────────────────────────────────────────
# NOTA: Nomes de campo podem precisar de ajuste se a query falhar.
# Campos assumidos: TDI, RECONTACT_RATE, IXC, ESTILO_MELI (+ sufixos _GOAL)
print("\n[5/8] HALO KPIs mensal…")
SQL_HALO_MONTHLY = f"""
SELECT
    h.AGENT_TEAM_NAME                            AS team,
    ROUND(AVG(h.TDI), 4)                         AS tdi,
    ROUND(AVG(h.TDI_GOAL), 4)                    AS tdi_goal,
    ROUND(AVG(h.RECONTACT_RATE) * 100, 2)        AS recontact_pct,
    ROUND(AVG(h.RECONTACT_RATE_GOAL) * 100, 2)   AS recontact_goal,
    ROUND(AVG(h.IXC), 2)                         AS ixc,
    ROUND(AVG(h.IXC_GOAL), 2)                    AS ixc_goal,
    ROUND(AVG(h.ESTILO_MELI), 2)                 AS estilo_meli,
    ROUND(AVG(h.ESTILO_MELI_GOAL), 2)            AS estilo_meli_goal
FROM {TABLE_HALO} h
WHERE h.TIME_WINDOW = 'MONTH_ID'
  AND h.DTTM_ID = DATE_TRUNC(DATE('{YESTERDAY}'), MONTH)
  AND h.AGENT_TEAM_NAME IN ({TEAMS_SQL})
GROUP BY 1
"""
halo_monthly = safe_run(SQL_HALO_MONTHLY, label="halo_monthly")

# ── Query 6: HALO KPIs semanal ────────────────────────────────────────────────
print("\n[6/8] HALO KPIs semanal…")
SQL_HALO_WEEKLY = f"""
SELECT
    h.AGENT_TEAM_NAME                            AS team,
    ROUND(AVG(h.TDI), 4)                         AS tdi,
    ROUND(AVG(h.TDI_GOAL), 4)                    AS tdi_goal,
    ROUND(AVG(h.RECONTACT_RATE) * 100, 2)        AS recontact_pct,
    ROUND(AVG(h.RECONTACT_RATE_GOAL) * 100, 2)   AS recontact_goal,
    ROUND(AVG(h.IXC), 2)                         AS ixc,
    ROUND(AVG(h.IXC_GOAL), 2)                    AS ixc_goal,
    ROUND(AVG(h.ESTILO_MELI), 2)                 AS estilo_meli,
    ROUND(AVG(h.ESTILO_MELI_GOAL), 2)            AS estilo_meli_goal
FROM {TABLE_HALO} h
WHERE h.TIME_WINDOW = 'WEEK_ID'
  AND h.DTTM_ID = DATE('{WEEK_START}')
  AND h.AGENT_TEAM_NAME IN ({TEAMS_SQL})
GROUP BY 1
"""
halo_weekly = safe_run(SQL_HALO_WEEKLY, label="halo_weekly")

# ── Query 7: Diagnóstico (comentários + transcrições detratores) ──────────────
# Roda para MÊS corrente e SEMANA corrente separadamente.
print("\n[7/8] Diagnóstico (comentários + transcrições)…")

def q_diagnostic(date_start, date_end, label="diag"):
    return f"""
    WITH all_insatisf AS (
        SELECT
            y.CAS_CASE_ID,
            y.AGENT_TEAM_NAME                                             AS team,
            COALESCE(NULLIF(TRIM(y.PROCESS_NAME),''),'(sem processo)')   AS process,
            y.ANSWER_SCORE                                                AS score,
            REPLACE(COALESCE(y.ANSWER_COMMENT, ''), '"', ' ')            AS comentario,
            ROW_NUMBER() OVER (
                PARTITION BY y.AGENT_TEAM_NAME, y.PROCESS_NAME
                ORDER BY RAND()
            )                                                             AS rn
        FROM {TABLE_Y20} y
        WHERE DATE(y.ANSWERED_DTTM) BETWEEN DATE('{date_start}') AND DATE('{date_end}')
          AND {BASE_FILTER}
          AND y.ANSWER_SCORE IN (1, 2, 3)
    ),
    sampled AS (SELECT * FROM all_insatisf WHERE rn <= 30),
    msgs AS (
        SELECT
            t.CAS_CASE_ID,
            REPLACE(COALESCE(t.CHAT_TRANSCRIPTION_OBFUSCATED, ''), '"', ' ') AS msg,
            t.CHAT_MESSAGE_DTTM,
            ROW_NUMBER() OVER (PARTITION BY t.CAS_CASE_ID ORDER BY t.CHAT_MESSAGE_DTTM) AS rn_msg
        FROM {TABLE_TR} t
        INNER JOIN sampled s ON s.CAS_CASE_ID = t.CAS_CASE_ID
        WHERE t.CHAT_TRANSCRIPTION_OBFUSCATED IS NOT NULL
    ),
    transcricoes AS (
        SELECT
            CAS_CASE_ID,
            SUBSTR(STRING_AGG(msg, ' ' ORDER BY CHAT_MESSAGE_DTTM), 1, 800) AS transcricao
        FROM msgs
        WHERE rn_msg <= 20
        GROUP BY CAS_CASE_ID
    )
    SELECT
        s.team,
        s.process,
        s.score,
        s.comentario,
        COALESCE(tr.transcricao, '') AS transcricao
    FROM sampled s
    LEFT JOIN transcricoes tr ON s.CAS_CASE_ID = tr.CAS_CASE_ID
    WHERE LENGTH(TRIM(COALESCE(s.comentario, ''))) > 5
       OR tr.transcricao IS NOT NULL
    ORDER BY s.team, s.process, s.score
    """

diag_monthly = safe_run(q_diagnostic(MONTH_START, YESTERDAY), label="diag_monthly")
diag_weekly  = safe_run(q_diagnostic(WEEK_START,  YESTERDAY), label="diag_weekly")

# ── Query 8: Segmentação de seller (ExpImpo) + comparativo fiscal ─────────────
print("\n[8/8] Segmentação seller (ExpImpo) + comparativo fiscal…")

SQL_SEG_MONTHLY = f"""
SELECT
    FORMAT_DATE('%Y-%m', DATE(y.ANSWERED_DTTM)) AS month,
    COALESCE(s.SELLER_SEGMENT_CX, 'Não classificado') AS seller_segment,
    COUNT(*)                                     AS total,
    CAST(SUM(y.SATISFIED) AS FLOAT64)            AS satisfied,
    CAST(SUM(y.SURVEY_TARGET_VALUE) AS FLOAT64)  AS target_sum
FROM {TABLE_Y20} y
LEFT JOIN {TABLE_SEG} s
    ON y.CUS_CUST_ID = s.CUS_CUST_ID_SEL
    AND s.PHOTO_ID = DATE_TRUNC(DATE(y.ANSWERED_DTTM), MONTH)
    AND s.SIT_SITE_ID = 'MLB'
WHERE DATE(y.ANSWERED_DTTM) BETWEEN DATE('{DATA_START}') AND DATE('{YESTERDAY}')
  AND y.AGENT_TEAM_NAME = 'MLB_ExpImpo'
  AND y.IS_ANSWERED = TRUE
  AND y.ELIGIBLE_CS = TRUE
  AND COALESCE(y.IS_EXCLUDED, FALSE) = FALSE
  AND COALESCE(y.KM_STATUS, 'NEWBIE') NOT IN ('TRAINING', 'UNAVAILABLE')
  AND y.KM_SEGMENT IS NOT NULL
GROUP BY 1, 2
ORDER BY 1, 3 DESC
"""
seg_monthly = safe_run(SQL_SEG_MONTHLY, label="seller_seg_monthly")

SQL_SEG_WEEKLY = f"""
SELECT
    COALESCE(s.SELLER_SEGMENT_CX, 'Não classificado') AS seller_segment,
    COUNT(*)                                     AS total,
    CAST(SUM(y.SATISFIED) AS FLOAT64)            AS satisfied,
    CAST(SUM(y.SURVEY_TARGET_VALUE) AS FLOAT64)  AS target_sum
FROM {TABLE_Y20} y
LEFT JOIN {TABLE_SEG} s
    ON y.CUS_CUST_ID = s.CUS_CUST_ID_SEL
    AND s.PHOTO_ID = DATE_TRUNC(DATE(y.ANSWERED_DTTM), MONTH)
    AND s.SIT_SITE_ID = 'MLB'
WHERE DATE(y.ANSWERED_DTTM) BETWEEN DATE('{WEEK_START}') AND DATE('{YESTERDAY}')
  AND y.AGENT_TEAM_NAME = 'MLB_ExpImpo'
  AND y.IS_ANSWERED = TRUE
  AND y.ELIGIBLE_CS = TRUE
  AND COALESCE(y.IS_EXCLUDED, FALSE) = FALSE
  AND COALESCE(y.KM_STATUS, 'NEWBIE') NOT IN ('TRAINING', 'UNAVAILABLE')
  AND y.KM_SEGMENT IS NOT NULL
GROUP BY 1
ORDER BY 3 DESC
"""
seg_weekly = safe_run(SQL_SEG_WEEKLY, label="seller_seg_weekly")

# Comparativo processos fiscais (ExpImpo vs Ventas — match dinâmico)
SQL_FISCAL = f"""
WITH expimpo_procs AS (
    SELECT DISTINCT PROCESS_NAME
    FROM {TABLE_Y20}
    WHERE AGENT_TEAM_NAME = 'MLB_ExpImpo'
      AND DATE(ANSWERED_DTTM) BETWEEN DATE('{DATA_START}') AND DATE('{YESTERDAY}')
      AND IS_ANSWERED = TRUE AND ELIGIBLE_CS = TRUE
      AND COALESCE(IS_EXCLUDED, FALSE) = FALSE
      AND COALESCE(KM_STATUS, 'NEWBIE') NOT IN ('TRAINING', 'UNAVAILABLE')
      AND KM_SEGMENT IS NOT NULL
)
SELECT
    FORMAT_DATE('%Y-%m', DATE(y.ANSWERED_DTTM))                  AS month,
    y.AGENT_TEAM_NAME                                             AS team,
    COALESCE(NULLIF(TRIM(y.PROCESS_NAME), ''), '(sem processo)')  AS process,
    COUNT(*)                                                      AS total,
    CAST(SUM(y.SATISFIED) AS FLOAT64)                             AS satisfied,
    CAST(SUM(y.SURVEY_TARGET_VALUE) AS FLOAT64)                   AS target_sum
FROM {TABLE_Y20} y
INNER JOIN expimpo_procs ep ON y.PROCESS_NAME = ep.PROCESS_NAME
WHERE DATE(y.ANSWERED_DTTM) BETWEEN DATE('{DATA_START}') AND DATE('{YESTERDAY}')
  AND y.AGENT_TEAM_NAME IN ('MLB_ExpImpo', 'BR_Ventas_Sellers_Longtail')
  AND y.IS_ANSWERED = TRUE AND y.ELIGIBLE_CS = TRUE
  AND COALESCE(y.IS_EXCLUDED, FALSE) = FALSE
  AND COALESCE(y.KM_STATUS, 'NEWBIE') NOT IN ('TRAINING', 'UNAVAILABLE')
  AND y.KM_SEGMENT IS NOT NULL
GROUP BY 1, 2, 3
ORDER BY 1, 3, 2
"""
fiscal = safe_run(SQL_FISCAL, label="fiscal_comparison")

# ── Agrega dados em Python ─────────────────────────────────────────────────────
print("\nAgregando dados…")

def build_monthly_aggs(raw):
    return {
        "by_team":      agg(raw, ["month", "team"]),
        "by_process":   agg(raw, ["month", "team", "process"]),
        "by_seniority": agg(raw, ["month", "team", "seniority"]),
        "by_segment":   agg(raw, ["month", "team", "km_segment"]),
    }

def build_weekly_aggs(raw):
    return {
        "by_team":      agg(raw, ["team"]),
        "by_process":   agg(raw, ["team", "process"]),
        "by_seniority": agg(raw, ["team", "seniority"]),
        "by_segment":   agg(raw, ["team", "km_segment"]),
    }

def process_rr(rows, keys):
    """Converte response rate para % e adiciona campo rr_pct."""
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
    """Estrutura: {team: {process: [{score, comentario, transcricao}]}}"""
    idx = defaultdict(lambda: defaultdict(list))
    for r in rows:
        idx[r["team"]][r["process"]].append({
            "score":      int(r.get("score") or 0),
            "comentario": str(r.get("comentario") or "").strip(),
            "transcricao": str(r.get("transcricao") or "").strip(),
        })
    # Converte para dict normal (json-serializable)
    return {t: dict(procs) for t, procs in idx.items()}

def process_seller_seg_monthly(rows):
    """Agrega segmentação por mês e calcula CSAT."""
    out = []
    for r in rows:
        t_ = int(r.get("total") or 0)
        c_ = csat(r.get("satisfied"), t_)
        tg = target(r.get("target_sum"), t_)
        out.append({
            "month": r["month"],
            "seller_segment": r["seller_segment"],
            "total": t_, "csat": c_, "target": tg, "gap": gap(c_, tg)
        })
    return out

def process_seller_seg_weekly(rows):
    out = []
    for r in rows:
        t_ = int(r.get("total") or 0)
        c_ = csat(r.get("satisfied"), t_)
        tg = target(r.get("target_sum"), t_)
        out.append({
            "seller_segment": r["seller_segment"],
            "total": t_, "csat": c_, "target": tg, "gap": gap(c_, tg)
        })
    return out

def process_fiscal(rows):
    """Agrega dados fiscais por mês+processo+equipe."""
    out = []
    for r in rows:
        t_ = int(r.get("total") or 0)
        c_ = csat(r.get("satisfied"), t_)
        tg = target(r.get("target_sum"), t_)
        out.append({
            "month": r["month"],
            "team": r["team"],
            "process": r["process"],
            "total": t_, "csat": c_, "target": tg, "gap": gap(c_, tg)
        })
    return out

# ── Monta estrutura final ──────────────────────────────────────────────────────
# Calcula meses disponíveis
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

    "monthly":  build_monthly_aggs(monthly_raw),
    "weekly":   build_weekly_aggs(weekly_raw),

    "response_rate": {
        "monthly": process_rr(rr_monthly, ["month", "team"]),
        "weekly":  process_rr(rr_weekly,  ["team"]),
    },

    "halo": {
        "monthly": halo_monthly,
        "weekly":  halo_weekly,
    },

    "diagnostic_raw": {
        "monthly": build_diag_index(diag_monthly),
        "weekly":  build_diag_index(diag_weekly),
    },

    "seller_segment": {
        "monthly": process_seller_seg_monthly(seg_monthly),
        "weekly":  process_seller_seg_weekly(seg_weekly),
    },

    "fiscal_comparison": process_fiscal(fiscal),
}

# ── Salva JSON ─────────────────────────────────────────────────────────────────
OUT = "_csat_data.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

print(f"\n✅ Salvo: {OUT}")
print(f"   Período mensal : {DATA_START} → {YESTERDAY}")
print(f"   Período semanal: {WEEK_START} → {YESTERDAY}")
print(f"   Meses          : {months_avail}")
