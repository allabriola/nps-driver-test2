#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_outgoing_drivers.py
Volume Outgoing por CDU — Processo Drivers — BR_ME Sellers Longtail (MLB)

Gera HTML com:
  • Gráfico mensal (Jan–Mai)
  • Gráfico semanal (8 semanas)
  • Ranking top CDUs + análise de transcrições
"""
import sys, json, re, os
sys.stdout.reconfigure(encoding="utf-8")

from google.cloud import bigquery
from collections import Counter
from datetime import date, timedelta

# ── Configuração ────────────────────────────────────────────────────────────
PROJECT   = "meli-bi-data"
SITE      = "MLB"
TOP_CDUS  = 12

PROCESS_KEY   = "Drivers"
PROCESS_LABEL = "Drivers"

TEAMS = ("BR_ME_Sellers_Longtail", "BR_ME_Pre-Despacho_Offline")

TODAY           = date.today()
START_YEAR      = date(TODAY.year, 1, 1)
EIGHT_WEEKS_AGO = TODAY - timedelta(weeks=8)
TRANSCRIPT_DAYS = 90

MES_PT = {
    "01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr",
    "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago",
    "09": "Set", "10": "Out", "11": "Nov", "12": "Dez",
}

PALETTE = [
    "#4472C4", "#ED7D31", "#70AD47", "#FFC000", "#E05252",
    "#9B59B6", "#255E91", "#c45f00", "#3aaa72", "#b38600",
]
OUTROS_COLOR  = "#BBBBBB"
SEM_CDU_COLOR = "#D0D0D0"
SEM_CDU       = "Sem CDU"
ACCENT_COLORS = ["#4472C4", "#ED7D31", "#70AD47", "#E05252", "#9B59B6"]

STOPWORDS = set("""
de da do que em para com um uma os as o a e é se não por mais ele ela
nao na no ao dos das me você oi ola sim bom dia boa tarde noite obrigado
obrigada ok isso este esta esse essa meu minha seu sua foi ser ter estou
esta tenho preciso posso pode como quando onde qual quais aqui ja mais
mas ou pois ate sobre mesmo tambem agora ainda depois antes entao porque
pelo pela pelos pelas hello hi the and for are this that with xxx xx x
null none true false nbsp nao nps vou temos voce vc eles elas nos vos
sendo tendo fazendo sou chamo nome meu minha representante espero esteja
bem hoje agradeço agradeco obrigad atendimento auxiliar auxiliarei
ajudar ajudarei ajudo mercado livre meli vendedor comprador seller
silence seconds silence email recipient num date hour url tramite
andamento abertura reclamacao reclamação interacao interação autor
descricao descrição fornecedor protocolo origem destino cola derivar
derivaçao processo justificacao equipe venda anuncio pedido caso
informo informei verifico verifiquei entendo entendi identifico identificamos
peço peco solicito solicitou infelizmente lamentamos desculpas
""".split())

# ── BigQuery ─────────────────────────────────────────────────────────────────
client = bigquery.Client(project=PROJECT)

def run(sql: str, retries: int = 5) -> list[dict]:
    import time
    for attempt in range(retries):
        try:
            return [dict(r) for r in client.query(sql).result()]
        except Exception as e:
            if "Quota exceeded" in str(e) and attempt < retries - 1:
                wait = 20 * (attempt + 1)
                print(f"   [quota] aguardando {wait}s (tentativa {attempt+1}/{retries})…")
                time.sleep(wait)
            else:
                raise

# ── Queries ──────────────────────────────────────────────────────────────────
TABLE_OG  = f"`{PROJECT}.WHOWNER.DM_CX_OUTGOING_GESTION_DETAIL`"
TABLE_CI  = f"`{PROJECT}.WHOWNER.BT_CX_CASE_INTERACTION`"
TABLE_TR  = f"`{PROJECT}.WHOWNER.BT_CX_TRANSCRIPT`"
TABLE_NPS = f"`{PROJECT}.WHOWNER.DM_CX_NPS_Y20_DETAIL`"

EVENT_FILTER  = "CI_EVENT_NAME IN ('OUTGOING_CONTACT','OUTGOING_FIRST_CONTACT')"
CDU_EXPR      = "COALESCE(NULLIF(TRIM(CDU),''), 'Sem CDU')"
SOL_EXPR      = "COALESCE(NULLIF(TRIM(SOLUTION_NAME),''), 'Sem Solução')"
TEAMS_FILTER  = "USER_TEAM_NAME IN ('" + "','".join(TEAMS) + "')"
TOP_SOLUTIONS = 10
DAILY_DAYS    = 30

def q_monthly() -> str:
    return f"""
    SELECT
      FORMAT_DATE('%Y-%m', OUTGOING_DATE) AS month,
      {CDU_EXPR}                          AS cdu,
      SUM(CANT_OUTGOING)                  AS volume
    FROM {TABLE_OG}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND {EVENT_FILTER}
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND OUTGOING_DATE BETWEEN '{START_YEAR}' AND '{TODAY}'
    GROUP BY 1, 2
    ORDER BY 1, 3 DESC
    """

def q_weekly() -> str:
    return f"""
    SELECT
      DATE_TRUNC(OUTGOING_DATE, ISOWEEK) AS week_start,
      {CDU_EXPR}                         AS cdu,
      SUM(CANT_OUTGOING)                 AS volume
    FROM {TABLE_OG}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND {EVENT_FILTER}
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND OUTGOING_DATE >= '{EIGHT_WEEKS_AGO}'
    GROUP BY 1, 2
    ORDER BY 1, 3 DESC
    """

def q_daily() -> str:
    daily_start = TODAY - timedelta(days=DAILY_DAYS)
    return f"""
    SELECT
      OUTGOING_DATE              AS day,
      {CDU_EXPR}                 AS cdu,
      SUM(CANT_OUTGOING)         AS volume
    FROM {TABLE_OG}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND {EVENT_FILTER}
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND OUTGOING_DATE >= '{daily_start}'
    GROUP BY 1, 2
    ORDER BY 1, 3 DESC
    """

def q_solutions() -> str:
    return f"""
    SELECT
      {SOL_EXPR}          AS solution,
      SUM(CANT_OUTGOING)  AS volume
    FROM {TABLE_OG}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND {EVENT_FILTER}
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND OUTGOING_DATE BETWEEN '{START_YEAR}' AND '{TODAY}'
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT {TOP_SOLUTIONS}
    """

NPS_FILTER = "FLAG_NOT_EXCLUDED_SURVEY IS TRUE AND FLAG_ACTIVE_TEAM IS TRUE"

def q_nps_by_cdu() -> str:
    return f"""
    SELECT
      COALESCE(NULLIF(TRIM(CDU),''), 'Sem CDU')              AS cdu,
      COUNT(*)                                               AS surveys,
      SUM(PROMOTER)                                          AS promoters,
      SUM(DETRACTOR)                                         AS detractors,
      ROUND(100.0*(SUM(PROMOTER)-SUM(DETRACTOR))/COUNT(*), 1) AS nps,
      ROUND(AVG(SURVEY_TARGET_VALUE), 2)                     AS target
    FROM {TABLE_NPS}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND SURVEY_CENTER    = 'BR'
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND SURVEY_DATE_SURVEY BETWEEN '{START_YEAR}' AND '{TODAY}'
      AND {NPS_FILTER}
    GROUP BY 1
    HAVING COUNT(*) >= 5
    ORDER BY surveys DESC
    """

def q_nps_monthly() -> str:
    return f"""
    SELECT
      FORMAT_DATE('%Y-%m', CAST(SURVEY_DATE_SURVEY AS DATE)) AS month,
      COALESCE(NULLIF(TRIM(CDU),''), 'Sem CDU')              AS cdu,
      COUNT(*)                                               AS surveys,
      SUM(PROMOTER)                                          AS promoters,
      SUM(DETRACTOR)                                         AS detractors,
      ROUND(AVG(SURVEY_TARGET_VALUE), 2)                     AS target
    FROM {TABLE_NPS}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND SURVEY_CENTER    = 'BR'
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND SURVEY_DATE_SURVEY BETWEEN '{START_YEAR}' AND '{TODAY}'
      AND {NPS_FILTER}
    GROUP BY 1, 2
    HAVING COUNT(*) >= 5
    ORDER BY 1, surveys DESC
    """

def q_nps_weekly_by_cdu() -> str:
    return f"""
    SELECT
      DATE_TRUNC(CAST(SURVEY_DATE_SURVEY AS DATE), ISOWEEK) AS week_start,
      COALESCE(NULLIF(TRIM(CDU),''), 'Sem CDU')             AS cdu,
      COUNT(*)                                              AS surveys,
      SUM(PROMOTER)                                         AS promoters,
      SUM(DETRACTOR)                                        AS detractors,
      ROUND(AVG(SURVEY_TARGET_VALUE), 2)                    AS target
    FROM {TABLE_NPS}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND SURVEY_CENTER    = 'BR'
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND CAST(SURVEY_DATE_SURVEY AS DATE) >= '{EIGHT_WEEKS_AGO}'
      AND {NPS_FILTER}
    GROUP BY 1, 2
    HAVING COUNT(*) >= 3
    ORDER BY 1, surveys DESC
    """

def q_nps_weekly() -> str:
    return f"""
    SELECT
      DATE_TRUNC(CAST(SURVEY_DATE_SURVEY AS DATE), ISOWEEK) AS week_start,
      COUNT(*)                                              AS surveys,
      SUM(PROMOTER)                                         AS promoters,
      SUM(DETRACTOR)                                        AS detractors
    FROM {TABLE_NPS}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND SURVEY_CENTER    = 'BR'
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND CAST(SURVEY_DATE_SURVEY AS DATE) >= '{EIGHT_WEEKS_AGO}'
      AND {NPS_FILTER}
    GROUP BY 1
    HAVING COUNT(*) >= 5
    ORDER BY 1
    """

def q_nps_daily() -> str:
    daily_start = TODAY - timedelta(days=DAILY_DAYS)
    return f"""
    SELECT
      CAST(SURVEY_DATE_SURVEY AS DATE)  AS day,
      COUNT(*)                          AS surveys,
      SUM(PROMOTER)                     AS promoters,
      SUM(DETRACTOR)                    AS detractors
    FROM {TABLE_NPS}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND SURVEY_CENTER    = 'BR'
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND CAST(SURVEY_DATE_SURVEY AS DATE) >= '{daily_start}'
      AND {NPS_FILTER}
    GROUP BY 1
    HAVING COUNT(*) >= 3
    ORDER BY 1
    """

def q_detractor_comments(cdu: str, days: int = 90) -> str:
    cutoff   = TODAY - timedelta(days=days)
    cdu_safe = cdu.replace("'", "''")
    return f"""
    SELECT
      SUBSTR(COALESCE(COMMENTS,''), 1, 400)                     AS comment,
      COALESCE(RES_DETRACTION_REASON, 'Não informado')          AS reason,
      CAST(SURVEY_DATE_SURVEY AS DATE)                          AS dt
    FROM {TABLE_NPS}
    WHERE SIT_SITE_ID      = '{SITE}'
      AND SURVEY_CENTER    = 'BR'
      AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
      AND {TEAMS_FILTER}
      AND COALESCE(NULLIF(TRIM(CDU),''), 'Sem CDU') = '{cdu_safe}'
      AND DETRACTOR        = 1
      AND COMMENTS         IS NOT NULL
      AND LENGTH(TRIM(COMMENTS)) > 10
      AND CAST(SURVEY_DATE_SURVEY AS DATE) >= '{cutoff}'
    ORDER BY dt DESC
    LIMIT 300
    """

def q_case_ids(cdu: str) -> str:
    cutoff   = TODAY - timedelta(days=TRANSCRIPT_DAYS)
    cdu_safe = cdu.replace("'", "''")
    return f"""
    SELECT DISTINCT i.CAS_CASE_ID
    FROM {TABLE_CI} i
    WHERE i.SIT_SITE_ID          = '{SITE}'
      AND i.FLAG_OUTGOING_GESTION = 1
      AND i.CI_PROCESS_ID IN (
          SELECT DISTINCT CI_PROCESS_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID      = '{SITE}'
            AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
            AND {TEAMS_FILTER}
      )
      AND i.WCM_CONT_ID IN (
          SELECT DISTINCT SOLUTION_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID      = '{SITE}'
            AND PRO_PROCESS_NAME = '{PROCESS_KEY}'
            AND {TEAMS_FILTER}
            AND {CDU_EXPR}       = '{cdu_safe}'
      )
      AND CAST(i.CI_CREATED_DATE AS DATE) >= '{cutoff}'
    LIMIT 1000
    """

def q_transcripts(case_ids: list[str]) -> str:
    ids = ",".join(case_ids)
    return f"""
    SELECT
      CAST(CAS_CASE_ID AS STRING)  AS case_id,
      OBFUSCATED_MESSAGE_CONTENT   AS msg
    FROM {TABLE_TR}
    WHERE CAS_CASE_ID IN ({ids})
      AND OBFUSCATED_MESSAGE_CONTENT IS NOT NULL
      AND LENGTH(OBFUSCATED_MESSAGE_CONTENT) > 20
    """

# ── TF-IDF + KMeans ──────────────────────────────────────────────────────────
def analyze_themes(case_transcripts: dict[str, list[str]], n_themes: int = 5) -> list[dict]:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    import numpy as np

    case_list = list(case_transcripts.items())[:300]
    case_ids  = [c[0] for c in case_list]

    _NOISE = [
        re.compile(r"recipient\s*:\s*%\w+\.?\s*email\s*:", re.I),
        re.compile(r"andamento\s*:\s*tramite.*?descri[çc][aã]o\s*:", re.DOTALL | re.I),
        re.compile(r"tipo\s+de\s+intera[çc][aã]o\s*:.*?hora\s*:", re.DOTALL | re.I),
        re.compile(r"%\w+"),
        re.compile(r"\bsilence\b.*?\bseconds?\b", re.I),
        re.compile(r"\bof\s+seconds?\b", re.I),
        re.compile(r"\brecipient\b", re.I),
        re.compile(r"\bemail\b", re.I),
        re.compile(r"\bwww\S+|\bhttp\S+"),
        re.compile(r"\b(sao|sou|meu|nome|chamo|representante|mercado livre|espero|esteja|bem|hoje|obrigad\w*|agradeç\w*|atend\w*|auxili\w*)\b", re.I),
    ]

    def clean_text(txt: str) -> str:
        for p in _NOISE:
            txt = p.sub(" ", txt)
        txt = re.sub(r"[^a-záéíóúàâêôãõç\s]", " ", txt.lower())
        return re.sub(r"\s+", " ", txt).strip()

    texts = []
    for _, msgs in case_list:
        combined = " ".join(m.strip() for m in msgs[:4])
        texts.append(clean_text(combined))

    n = min(n_themes, len(texts))
    if n < 2:
        return []

    vect = TfidfVectorizer(
        max_features=1500,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.90,
        stop_words=list(STOPWORDS),
        sublinear_tf=True,
    )
    try:
        X = vect.fit_transform(texts)
    except ValueError:
        return []

    km = KMeans(n_clusters=n, random_state=42, n_init=10, max_iter=300)
    labels = km.fit_predict(X)
    feat   = vect.get_feature_names_out()

    themes = []
    for cid in range(n):
        mask     = np.array(labels) == cid
        c_ids    = [case_ids[i] for i, m in enumerate(mask) if m]
        count    = int(mask.sum())
        pct      = int(round(count / len(texts) * 100))
        if count == 0:
            continue

        center    = km.cluster_centers_[cid]
        top_idx   = center.argsort()[-15:][::-1]
        top_terms = [feat[i] for i in top_idx
                     if feat[i] not in STOPWORDS and len(feat[i]) >= 4]

        bigrams   = [t for t in top_terms if " " in t][:3]
        unigrams  = [t for t in top_terms if " " not in t][:4]
        name_parts = (bigrams[:2] + unigrams[:2]) if bigrams else unigrams[:3]
        name = " · ".join(name_parts[:3]).title()

        all_terms = (bigrams + unigrams)[:5]
        summary = (
            f"Casos concentrados em: {', '.join(all_terms[:4])}. "
            f"{count} atendimentos no período analisado."
        )

        themes.append({
            "name":     name,
            "pct":      pct,
            "case_ids": c_ids[:3],
            "summary":  summary,
        })

    themes.sort(key=lambda x: x["pct"], reverse=True)
    return themes

# ── Cache ─────────────────────────────────────────────────────────────────────
CACHE_MAX_AGE_H = 24

def _cache_path(cdu: str = "", charts: bool = False) -> str:
    if charts:
        return "_cache_drivers_charts.json"
    safe_c = re.sub(r"[^a-zA-Z0-9]", "_", cdu)[:30]
    return f"_tr_cache_Drivers_{safe_c}.json"

def _load_cache(cdu: str = "", charts: bool = False):
    import time as _t
    path = _cache_path(cdu, charts)
    if not os.path.exists(path):
        return None
    age_h = (_t.time() - os.path.getmtime(path)) / 3600
    if age_h > CACHE_MAX_AGE_H:
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    print(f"   [cache] {path} ({age_h:.1f}h)")
    return data

def _save_cache(data, cdu: str = "", charts: bool = False) -> None:
    path = _cache_path(cdu, charts)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, default=str)
    print(f"   [cache] salvo {path}")

# ── Processamento ─────────────────────────────────────────────────────────────
def month_label(ym: str) -> str:
    return MES_PT.get(ym.split("-")[1], ym)

def _build_datasets(top_cdus, by_cdu, keys, sem_cdu_data, all_rows, key_field):
    datasets = []
    for cdu in top_cdus:
        datasets.append({"label": cdu,
                         "data": [by_cdu.get(cdu, {}).get(k, 0) for k in keys]})
    if any(v > 0 for v in sem_cdu_data):
        datasets.append({"label": SEM_CDU, "data": sem_cdu_data})
    outros = [
        sum(r["volume"] for r in all_rows if r[key_field] == k
            and r["cdu"] not in top_cdus and r["cdu"] != SEM_CDU)
        for k in keys
    ]
    if any(v > 0 for v in outros):
        datasets.append({"label": "Outros", "data": outros})
    return datasets

def process_monthly(raw: list[dict]) -> dict:
    months_sorted = sorted(set(r["month"] for r in raw))
    cdu_totals: Counter = Counter()
    by_cdu: dict = {}
    for r in raw:
        cdu = r["cdu"]
        cdu_totals[cdu] += r["volume"]
        by_cdu.setdefault(cdu, {})[r["month"]] = r["volume"]

    top_cdus = [c for c, _ in cdu_totals.most_common() if c != SEM_CDU][:TOP_CDUS]
    top_cdu  = top_cdus[0] if top_cdus else None

    sem_cdu_data = [by_cdu.get(SEM_CDU, {}).get(m, 0) for m in months_sorted]
    datasets = _build_datasets(top_cdus, by_cdu, months_sorted, sem_cdu_data, raw, "month")

    return {
        "months":     [month_label(m) for m in months_sorted],
        "top_cdus":   top_cdus,
        "top_cdu":    top_cdu,
        "datasets":   datasets,
        "cdu_totals": {k: v for k, v in cdu_totals.items() if k != SEM_CDU},
        "sem_cdu_vol": cdu_totals.get(SEM_CDU, 0),
        "total_vol":   sum(cdu_totals.values()),
    }

def process_daily(raw: list[dict]) -> dict:
    days_sorted = sorted(set(r["day"] for r in raw))
    days_labels = [
        d.strftime("%d/%m") if hasattr(d, "strftime") else str(d)[5:].replace("-", "/")
        for d in days_sorted
    ]
    cdu_totals: Counter = Counter()
    by_cdu: dict = {}
    for r in raw:
        cdu = r["cdu"]
        cdu_totals[cdu] += r["volume"]
        by_cdu.setdefault(cdu, {})[r["day"]] = r["volume"]

    top_cdus     = [c for c, _ in cdu_totals.most_common() if c != SEM_CDU][:TOP_CDUS]
    sem_cdu_data = [by_cdu.get(SEM_CDU, {}).get(d, 0) for d in days_sorted]
    datasets     = _build_datasets(top_cdus, by_cdu, days_sorted, sem_cdu_data, raw, "day")

    return {"days": days_labels, "top_cdus": top_cdus, "datasets": datasets}

def process_weekly(raw: list[dict]) -> dict:
    weeks_sorted = sorted(set(r["week_start"] for r in raw))
    weeks_labels = [w.strftime("%d/%m") if hasattr(w, "strftime") else str(w)[:10][5:].replace("-", "/") for w in weeks_sorted]
    cdu_totals: Counter = Counter()
    by_cdu: dict = {}
    for r in raw:
        cdu = r["cdu"]
        cdu_totals[cdu] += r["volume"]
        by_cdu.setdefault(cdu, {})[r["week_start"]] = r["volume"]

    top_cdus = [c for c, _ in cdu_totals.most_common() if c != SEM_CDU][:TOP_CDUS]

    sem_cdu_data = [by_cdu.get(SEM_CDU, {}).get(w, 0) for w in weeks_sorted]
    datasets = _build_datasets(top_cdus, by_cdu, weeks_sorted, sem_cdu_data, raw, "week_start")

    return {
        "weeks":    weeks_labels,
        "top_cdus": top_cdus,
        "datasets": datasets,
    }

def nps_color(nps) -> str:
    if nps is None: return "#ccc"
    if nps >= 50:   return "#70AD47"
    if nps >= 0:    return "#FFC000"
    if nps >= -20:  return "#ED7D31"
    return "#E05252"

def _calc_nps(p, d, s) -> float | None:
    return round(100.0 * (p - d) / s, 1) if s >= 5 else None

def process_nps_by_cdu(raw: list[dict]) -> list[dict]:
    return [
        {"cdu":     r["cdu"],
         "surveys": int(r["surveys"] or 0),
         "nps":     _calc_nps(int(r["promoters"] or 0), int(r["detractors"] or 0), int(r["surveys"] or 0)),
         "target":  round(float(r["target"]) * 100, 1) if r.get("target") is not None else None}
        for r in raw
    ]

def process_nps_monthly(raw: list[dict], months: list[str]) -> dict:
    agg: dict[str, dict] = {}
    by_cdu_month: dict[str, dict] = {}
    for r in raw:
        m = r["month"]
        p, d, s = int(r["promoters"] or 0), int(r["detractors"] or 0), int(r["surveys"] or 0)
        tgt = round(float(r["target"]) * 100, 1) if r.get("target") is not None else None
        agg.setdefault(m, {"p": 0, "d": 0, "s": 0})
        agg[m]["p"] += p; agg[m]["d"] += d; agg[m]["s"] += s
        by_cdu_month.setdefault(r["cdu"], {})[m] = {"nps": _calc_nps(p, d, s), "target": tgt, "s": s, "p": p, "d": d}

    monthly_nps = []
    for m in months:
        ym = next((k for k in agg if month_label(k) == m), None)
        monthly_nps.append(_calc_nps(agg[ym]["p"], agg[ym]["d"], agg[ym]["s"]) if ym else None)
    return {"monthly_nps": monthly_nps, "by_cdu_month": by_cdu_month}

def process_nps_weekly_by_cdu(raw: list[dict], weekly_weeks: list[str]) -> dict:
    """Retorna {cdu: [nps_w1, ..., nps_wN]} alinhado com weekly_weeks (dd/mm)."""
    by_cdu: dict[str, dict] = {}
    for r in raw:
        ws = r["week_start"]
        lbl = ws.strftime("%d/%m") if hasattr(ws, "strftime") else str(ws)[8:10] + "/" + str(ws)[5:7]
        p, d, s = int(r["promoters"] or 0), int(r["detractors"] or 0), int(r["surveys"] or 0)
        tgt = round(float(r["target"]) * 100, 1) if r.get("target") is not None else None
        by_cdu.setdefault(r["cdu"], {})[lbl] = {
            "nps": _calc_nps(p, d, s), "target": tgt, "s": s
        }
    result = {}
    for cdu, weeks in by_cdu.items():
        result[cdu] = [weeks.get(w) for w in weekly_weeks]
    return result

def _wf_bars(anchor_start_lbl, anchor_start_val,
             contribs,  # list of (label, value, extra_dict)
             anchor_end_lbl, anchor_end_val, anchor_color="#4472C4"):
    """Builds waterfall bar data: [{label, spacer, bar, color, isAnchor, ...}]."""
    bars = [{"label": anchor_start_lbl, "spacer": 0, "bar": round(anchor_start_val, 2),
             "isAnchor": True, "color": anchor_color, "contrib": None}]
    running = anchor_start_val
    for lbl, v, extra in contribs:
        v = round(v, 2)
        spacer = round(running + v, 2) if v < 0 else round(running, 2)
        bars.append({"label": lbl[:32], "spacer": spacer, "bar": abs(v),
                     "isAnchor": False, "contrib": v,
                     "color": "#70AD47cc" if v >= 0 else "#E05252cc", **extra})
        running = round(running + v, 2)
    bars.append({"label": anchor_end_lbl, "spacer": 0, "bar": round(anchor_end_val, 2),
                 "isAnchor": True, "color": anchor_color, "contrib": None})
    return bars

def compute_waterfalls(nps_by_cdu: list, nps_monthly: dict) -> dict:
    by_cdu_month = nps_monthly.get("by_cdu_month", {})
    month_keys   = sorted({k for v in by_cdu_month.values() for k in v})

    # ── Target único do processo (média ponderada por pesquisas) ──────────────
    valid_tgt = [r for r in nps_by_cdu
                 if r["nps"] is not None and r["target"] is not None
                 and r["cdu"] != "Sem CDU" and r["surveys"] >= 10]
    total_s = sum(r["surveys"] for r in valid_tgt)
    if total_s and valid_tgt:
        # Target do processo = média ponderada dos targets por CDU
        process_target = round(sum(r["target"] * r["surveys"] for r in valid_tgt) / total_s, 1)
        actual_wt      = round(sum(r["nps"]    * r["surveys"] for r in valid_tgt) / total_s, 1)
        total_gap      = round(actual_wt - process_target, 1)

        # Impacto por CDU = (NPS_cdu - target_processo) × peso_cdu
        # soma de todos os impactos = gap total (NPS real - target)
        contribs = [
            (r["cdu"],
             round((r["nps"] - process_target) * r["surveys"] / total_s, 2),
             {"nps": r["nps"], "target_proc": process_target,
              "weight": round(r["surveys"] / total_s * 100, 1),
              "surveys": r["surveys"]})
            for r in valid_tgt
        ]
        pos = sorted([c for c in contribs if c[1] >= 0], key=lambda x: -x[1])
        neg = sorted([c for c in contribs if c[1] <  0], key=lambda x: -x[1])
        cascata = _wf_bars(
            f"Target Drivers ({process_target:.1f})", process_target,
            pos + neg,
            f"NPS Real ({actual_wt:.1f})", actual_wt)
        tgt_wt = process_target
    else:
        cascata, tgt_wt, actual_wt, total_gap, process_target = [], None, None, None, None

    # ── WTF MoM ──────────────────────────────────────────────────────────────
    if len(month_keys) >= 2:
        mk1, mk0 = month_keys[-1], month_keys[-2]
        # aggregate per month
        def _agg(mk):
            tot = {"p": 0, "d": 0, "s": 0}
            per_cdu = {}
            for cdu, mdata in by_cdu_month.items():
                e = mdata.get(mk, {})
                if not isinstance(e, dict): continue
                p, d, s = e.get("p", 0), e.get("d", 0), e.get("s", 0)
                tot["p"] += p; tot["d"] += d; tot["s"] += s
                if s > 0:
                    per_cdu[cdu] = {"nps": _calc_nps(p, d, s), "s": s, "p": p, "d": d}
            nps_agg = _calc_nps(tot["p"], tot["d"], tot["s"])
            return nps_agg, per_cdu, tot["s"]

        nps_m1, cdus_m1, total_m1 = _agg(mk1)
        nps_m0, cdus_m0, total_m0 = _agg(mk0)

        if nps_m1 is not None and nps_m0 is not None and total_m1 and total_m0:
            all_cdus = set(cdus_m1) | set(cdus_m0)
            contribs_wtf = []
            for cdu in all_cdus:
                if cdu == "Sem CDU": continue
                e1 = cdus_m1.get(cdu, {"nps": 0, "s": 0})
                e0 = cdus_m0.get(cdu, {"nps": 0, "s": 0})
                contrib = round((e1["nps"] or 0) * e1["s"] / total_m1
                               - (e0["nps"] or 0) * e0["s"] / total_m0, 2)
                if abs(contrib) >= 0.05:
                    contribs_wtf.append((cdu, contrib,
                                        {"nps_m1": e1["nps"], "nps_m0": e0["nps"]}))
            pos_w = sorted([c for c in contribs_wtf if c[1] >= 0], key=lambda x: -x[1])
            neg_w = sorted([c for c in contribs_wtf if c[1] <  0], key=lambda x: -x[1])
            wtf = _wf_bars(f"{month_label(mk0)} ({nps_m0:.1f})", nps_m0,
                           pos_w + neg_w,
                           f"{month_label(mk1)} ({nps_m1:.1f})", nps_m1)
            wtf_labels = (month_label(mk0), month_label(mk1))
        else:
            wtf, wtf_labels = [], ("—", "—")
    else:
        wtf, wtf_labels = [], ("—", "—")

    return {"cascata": cascata, "wtf": wtf, "wtf_labels": wtf_labels,
            "tgt_wt": tgt_wt, "actual_wt": actual_wt,
            "process_target": process_target,
            "total_gap": total_gap}

def analyze_detractor_comments(raw: list[dict]) -> dict:
    """Analisa comentários de detratores: razões + temas TF-IDF + amostras."""
    from collections import Counter

    if not raw:
        return {"reasons": [], "themes": [], "samples": [], "total": 0}

    # Razões estruturadas
    reason_counts = Counter(r["reason"] for r in raw if r.get("reason"))
    reasons = [{"reason": k, "count": v}
               for k, v in reason_counts.most_common(8)]

    # Amostras (10 mais recentes com comentário substancial)
    samples = [r["comment"] for r in raw
               if r.get("comment") and len(r["comment"].strip()) > 30][:12]

    # Temas via TF-IDF + KMeans (reusa STOPWORDS do script)
    texts = [r["comment"] for r in raw if r.get("comment") and len(r["comment"].strip()) > 20]
    themes = []
    if len(texts) >= 10:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.cluster import KMeans
            import numpy as np, re

            _NOISE = [
                re.compile(r"%\w+"),
                re.compile(r"\bsilence\b.*?\bseconds?\b", re.I),
                re.compile(r"\bhttp\S+|\bwww\S+"),
            ]
            def clean(t):
                for p in _NOISE: t = p.sub(" ", t)
                t = re.sub(r"[^a-záéíóúàâêôãõç\s]", " ", t.lower())
                return re.sub(r"\s+", " ", t).strip()

            cleaned = [clean(t) for t in texts]
            n = min(5, len(cleaned))
            vect = TfidfVectorizer(max_features=800, ngram_range=(1, 2),
                                   min_df=2, max_df=0.9,
                                   stop_words=list(STOPWORDS), sublinear_tf=True)
            X = vect.fit_transform(cleaned)
            km = KMeans(n_clusters=n, random_state=42, n_init=10, max_iter=200)
            labels = km.fit_predict(X)
            feat   = vect.get_feature_names_out()

            for cid in range(n):
                mask  = np.array(labels) == cid
                count = int(mask.sum())
                if count == 0: continue
                pct   = int(round(count / len(cleaned) * 100))
                center = km.cluster_centers_[cid]
                top_idx= center.argsort()[-12:][::-1]
                top_terms = [feat[i] for i in top_idx
                             if feat[i] not in STOPWORDS and len(feat[i]) >= 4]
                bigrams  = [t for t in top_terms if " " in t][:2]
                unigrams = [t for t in top_terms if " " not in t][:3]
                name_parts = (bigrams[:1] + unigrams[:2]) if bigrams else unigrams[:3]
                name = " · ".join(name_parts).title()
                # sample comment from this cluster
                c_samples = [texts[i] for i, m in enumerate(mask) if m][:2]
                themes.append({"name": name, "pct": pct, "count": count,
                               "samples": c_samples})

            themes.sort(key=lambda x: x["pct"], reverse=True)
        except Exception:
            pass

    return {"reasons": reasons, "themes": themes,
            "samples": samples, "total": len(raw)}

def compute_mom_scorecard(monthly: dict, nps_monthly: dict, nps_by_cdu: list,
                          process_target: float | None = None) -> list[dict]:
    """Por CDU: NPS e volume do último mês, variação MoM, target e gap."""
    by_cdu_month = nps_monthly.get("by_cdu_month", {})
    nps_ytd_map  = {r["cdu"]: r for r in nps_by_cdu}
    months_keys  = sorted({k for v in by_cdu_month.values() for k in v})

    last_mk  = months_keys[-1]  if len(months_keys) >= 1 else None
    prev_mk  = months_keys[-2]  if len(months_keys) >= 2 else None
    last_mlbl = month_label(last_mk) if last_mk else "—"
    prev_mlbl = month_label(prev_mk) if prev_mk else "—"

    # outgoing volume by CDU per month (from monthly datasets)
    vol_by_cdu: dict[str, list] = {}
    for ds in monthly["datasets"]:
        if ds["label"] not in ("Sem CDU", "Outros"):
            vol_by_cdu[ds["label"]] = ds["data"]
    n_months = len(monthly["months"])

    rows = []
    for cdu in monthly["top_cdus"]:
        cdu_nps_month = by_cdu_month.get(cdu, {})
        last_entry = cdu_nps_month.get(last_mk, {}) if last_mk else {}
        prev_entry = cdu_nps_month.get(prev_mk, {}) if prev_mk else {}

        nps_last = last_entry.get("nps")  if isinstance(last_entry, dict) else last_entry
        nps_prev = prev_entry.get("nps")  if isinstance(prev_entry, dict) else prev_entry
        tgt_last = last_entry.get("target") if isinstance(last_entry, dict) else None

        # fallback target from YTD
        if tgt_last is None:
            tgt_last = nps_ytd_map.get(cdu, {}).get("target")

        nps_mom   = round(nps_last - nps_prev, 1) if (nps_last is not None and nps_prev is not None) else None
        ref_tgt   = process_target if process_target is not None else tgt_last
        gap       = round(nps_last - ref_tgt, 1) if (nps_last is not None and ref_tgt is not None) else None

        vols = vol_by_cdu.get(cdu, [])
        vol_last = vols[-1] if vols else 0
        vol_prev = vols[-2] if len(vols) >= 2 else 0
        vol_mom_pct = round((vol_last - vol_prev) / vol_prev * 100, 1) if vol_prev else None

        rows.append({
            "cdu":         cdu,
            "nps_last":    nps_last,
            "nps_prev":    nps_prev,
            "nps_mom":     nps_mom,
            "target":      tgt_last,
            "gap":         gap,
            "vol_last":    vol_last,
            "vol_prev":    vol_prev,
            "vol_mom_pct": vol_mom_pct,
            "last_mlbl":   last_mlbl,
            "prev_mlbl":   prev_mlbl,
        })
    return rows

def process_nps_agg(raw: list[dict], labels: list[str], key_field: str) -> list:
    """Agrega NPS por período (weekly ou daily), alinhado com labels."""
    agg: dict = {}
    for r in raw:
        k = str(r[key_field])
        p, d, s = int(r["promoters"] or 0), int(r["detractors"] or 0), int(r["surveys"] or 0)
        agg.setdefault(k, {"p": 0, "d": 0, "s": 0})
        agg[k]["p"] += p; agg[k]["d"] += d; agg[k]["s"] += s

    result = []
    for lbl in labels:
        # labels são dd/mm — chave ISO é yyyy-mm-dd, converter para dd/mm
        match = next((k for k in agg
                      if (len(k) == 10 and k[8:10] + "/" + k[5:7] == lbl)
                      or k == lbl), None)
        if match:
            result.append(_calc_nps(agg[match]["p"], agg[match]["d"], agg[match]["s"]))
        else:
            result.append(None)
    return result

def fetch_themes(cdu: str) -> list[dict]:
    if not cdu or cdu == SEM_CDU:
        return []

    cached = _load_cache(cdu)
    if cached is None:
        print(f"   [BQ] '{cdu}': buscando case IDs…")
        try:
            raw_ids = run(q_case_ids(cdu))
            ids = [str(int(r["CAS_CASE_ID"])) for r in raw_ids if r.get("CAS_CASE_ID") is not None]
        except Exception as e:
            print(f"   [quota] '{cdu}' ignorado: {e}")
            return []
        if not ids:
            return []

        print(f"   [BQ] '{cdu}': {len(ids)} casos, buscando transcrições…")
        case_transcripts: dict[str, list[str]] = {}
        try:
            for i in range(0, len(ids), 1000):
                rows = run(q_transcripts(ids[i:i + 1000]))
                for r in rows:
                    cid, msg = r.get("case_id"), r.get("msg")
                    if cid and msg:
                        case_transcripts.setdefault(cid, []).append(msg)
            _save_cache(case_transcripts, cdu)
        except Exception as e:
            print(f"   [quota] transcrições de '{cdu}' ignoradas: {e}")
            return []
    else:
        case_transcripts = cached

    themes = analyze_themes(case_transcripts)
    print(f"   [TF-IDF] '{cdu}': {len(themes)} temas")
    return themes

def build_all(html_only: bool = False):
    if html_only:
        print("▸ Modo --html-only: usando cache de gráficos…")
        cached = _load_cache(charts=True)
        if cached is None:
            raise RuntimeError("Cache não encontrado. Rode sem --html-only primeiro.")
        monthly       = cached["monthly"]
        weekly        = cached["weekly"]
        daily         = cached.get("daily", {"days": [], "top_cdus": [], "datasets": []})
        solutions     = cached.get("solutions", [])
        themes_by_cdu = cached.get("themes_by_cdu", {})
        nps_by_cdu    = cached.get("nps_by_cdu", [])
        nps_monthly   = cached.get("nps_monthly", {"monthly_nps": [], "by_cdu_month": {}})
        nps_weekly         = cached.get("nps_weekly", [])
        nps_daily          = cached.get("nps_daily", [])
        nps_weekly_by_cdu  = cached.get("nps_weekly_by_cdu", {})
        waterfalls         = cached.get("waterfalls") or compute_waterfalls(nps_by_cdu, nps_monthly)
        mom_scorecard      = cached.get("mom_scorecard") or compute_mom_scorecard(
            monthly, nps_monthly, nps_by_cdu, waterfalls.get("process_target"))
        detractor_analysis = cached.get("detractor_analysis", {})
        return monthly, weekly, daily, themes_by_cdu, solutions, nps_by_cdu, nps_monthly, nps_weekly, nps_daily, nps_weekly_by_cdu, waterfalls, mom_scorecard, detractor_analysis

    print("▸ Volume mensal…")
    monthly_raw = run(q_monthly())
    print("▸ Volume semanal (8 semanas)…")
    weekly_raw  = run(q_weekly())
    print(f"▸ Volume diário (últimos {DAILY_DAYS} dias)…")
    daily_raw   = run(q_daily())
    print("▸ Top soluções…")
    solutions_raw = run(q_solutions())
    print("▸ NPS por CDU…")
    nps_cdu_raw = run(q_nps_by_cdu())
    print("▸ NPS mensal…")
    nps_month_raw = run(q_nps_monthly())
    print("▸ NPS semanal…")
    nps_week_raw = run(q_nps_weekly())
    print("▸ NPS semanal por CDU…")
    nps_week_cdu_raw = run(q_nps_weekly_by_cdu())
    print("▸ NPS diário…")
    nps_day_raw = run(q_nps_daily())

    monthly   = process_monthly(monthly_raw)
    weekly    = process_weekly(weekly_raw)
    daily     = process_daily(daily_raw)
    solutions = [{"solution": r["solution"], "volume": r["volume"]} for r in solutions_raw]
    nps_by_cdu  = process_nps_by_cdu(nps_cdu_raw)
    nps_monthly = process_nps_monthly(nps_month_raw, monthly["months"])
    nps_weekly       = process_nps_agg(nps_week_raw, weekly["weeks"], "week_start")
    nps_daily        = process_nps_agg(nps_day_raw,  daily["days"],  "day")
    nps_weekly_by_cdu = process_nps_weekly_by_cdu(nps_week_cdu_raw, weekly["weeks"])
    waterfalls       = compute_waterfalls(nps_by_cdu, nps_monthly)
    mom_scorecard    = compute_mom_scorecard(monthly, nps_monthly, nps_by_cdu,
                                             waterfalls.get("process_target"))

    # CDU mais ofensor = pior impacto negativo na cascata
    casc_bars = waterfalls.get("cascata", [])
    worst_cdu = min(
        (b for b in casc_bars if not b.get("isAnchor") and b.get("contrib") is not None),
        key=lambda b: b["contrib"], default={}
    ).get("label", "").rstrip("…")
    # CDU mais representativo = maior volume outgoing
    top_og_cdu = monthly["top_cdu"] or ""
    # busca CDU completo pelo prefixo truncado na cascata
    worst_cdu_full = next(
        (r["cdu"] for r in nps_by_cdu if r["cdu"].startswith(worst_cdu[:20])), worst_cdu
    )

    print(f"▸ Comentários detratores: '{worst_cdu_full[:40]}' e '{top_og_cdu[:40]}'…")
    det_worst_raw  = run(q_detractor_comments(worst_cdu_full))
    det_top_og_raw = run(q_detractor_comments(top_og_cdu)) if top_og_cdu != worst_cdu_full else det_worst_raw

    det_worst  = analyze_detractor_comments(det_worst_raw)
    det_top_og = analyze_detractor_comments(det_top_og_raw)
    detractor_analysis = {
        "worst_cdu":  {"cdu": worst_cdu_full,  **det_worst},
        "top_og_cdu": {"cdu": top_og_cdu,       **det_top_og},
    }

    themes_by_cdu: dict[str, list] = {}
    top_cdus = monthly["top_cdus"]
    print(f"\n▸ Análise temática Drivers ({len(top_cdus)} CDUs)…")
    for cdu in top_cdus:
        themes_by_cdu[cdu] = fetch_themes(cdu)

    _save_cache({"monthly": monthly, "weekly": weekly, "daily": daily,
                 "solutions": solutions, "themes_by_cdu": themes_by_cdu,
                 "nps_by_cdu": nps_by_cdu, "nps_monthly": nps_monthly,
                 "nps_weekly": nps_weekly, "nps_daily": nps_daily,
                 "nps_weekly_by_cdu": nps_weekly_by_cdu,
                 "waterfalls": waterfalls,
                 "mom_scorecard": mom_scorecard,
                 "detractor_analysis": detractor_analysis}, charts=True)
    return monthly, weekly, daily, themes_by_cdu, solutions, nps_by_cdu, nps_monthly, nps_weekly, nps_daily, nps_weekly_by_cdu, waterfalls, mom_scorecard, detractor_analysis

# ── HTML ──────────────────────────────────────────────────────────────────────
def jd(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)

def palette_for(datasets: list[dict]) -> list[str]:
    out = []
    idx = 0
    for ds in datasets:
        if ds["label"] == "Outros":
            out.append(OUTROS_COLOR)
        elif ds["label"] == SEM_CDU:
            out.append(SEM_CDU_COLOR)
        else:
            out.append(PALETTE[idx % len(PALETTE)])
            idx += 1
    return out

def _render_theme_cards(themes: list[dict]) -> str:
    if not themes:
        return (
            '<div class="no-data-block">'
            '<span class="no-data-icon">🔒</span>'
            '<div><strong>Análise de transcrições indisponível</strong><br>'
            'O usuário atual não tem acesso à tabela <code>BT_CX_TRANSCRIPT</code>. '
            'Para habilitar esta seção, solicite permissão de leitura à equipe de dados '
            'ou adicione temas curados manualmente no dicionário <code>CURATED_THEMES</code> do script.'
            '</div></div>'
        )
    cards = ""
    for i, t in enumerate(themes):
        color = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        chips = "".join(f'<span class="case-chip">#{c}</span>' for c in t.get("case_ids", []))
        cards += (
            f'<div class="theme-card" style="border-left-color:{color}">'
            f'<div class="tc-header">'
            f'<span class="tc-name">{t.get("name","—")}</span>'
            f'<span class="tc-badge" style="background:{color}22;color:{color}">'
            f'{t.get("pct",0)}% dos casos</span>'
            f'</div>'
            f'<p class="tc-summary">{t.get("summary","")}</p>'
            f'<div class="tc-chips">{chips}</div>'
            f'</div>'
        )
    return f'<div class="themes-list">{cards}</div>'

def _period_totals(datasets: list[dict], n: int) -> list[int]:
    """Soma todos os datasets para cada período (índice)."""
    if not datasets or not datasets[0]["data"]:
        return []
    return [sum(ds["data"][i] for ds in datasets if i < len(ds["data"])) for i in range(n)]

def generate_exec_summary(monthly: dict, weekly: dict, daily: dict, solutions: list) -> str:
    total_v   = monthly["total_vol"]
    named_v   = sum(monthly["cdu_totals"].values())
    sem_cdu_v = monthly["sem_cdu_vol"]
    top_cdu   = monthly["top_cdu"] or "—"
    top_vol   = monthly["cdu_totals"].get(top_cdu, 0)
    top_pct   = top_vol / total_v * 100 if total_v else 0
    id_rate   = named_v / total_v * 100 if total_v else 0
    n_months  = len(monthly["months"])

    # monthly totals per period
    m_totals = _period_totals(monthly["datasets"], n_months)
    last_m   = m_totals[-1] if m_totals else 0
    prev_m   = m_totals[-2] if len(m_totals) >= 2 else 0
    m_delta  = (last_m - prev_m) / prev_m * 100 if prev_m else 0
    m_arrow  = "↑" if m_delta > 1 else ("↓" if m_delta < -1 else "→")
    m_color  = "#E05252" if m_delta > 1 else ("#70AD47" if m_delta < -1 else "#888")
    m_lbl    = monthly["months"][-1] if monthly["months"] else "—"
    m_prev   = monthly["months"][-2] if len(monthly["months"]) >= 2 else "—"

    # per-CDU growth Jan→latest (only CDUs present all months)
    cdu_growth = {}
    for ds in monthly["datasets"]:
        if ds["label"] in ("Sem CDU", "Outros"):
            continue
        d = ds["data"]
        if len(d) == n_months and d[0] > 0:
            cdu_growth[ds["label"]] = (d[-1] - d[0]) / d[0] * 100
    fastest_cdu = max(cdu_growth, key=cdu_growth.get) if cdu_growth else None
    fastest_pct = cdu_growth.get(fastest_cdu, 0) if fastest_cdu else 0
    # monthly values of fastest CDU
    fastest_ds  = next((ds for ds in monthly["datasets"] if ds["label"] == fastest_cdu), None)

    # top CDU monthly values for trend sentence
    top_cdu_ds = next((ds for ds in monthly["datasets"] if ds["label"] == top_cdu), None)
    top_first  = top_cdu_ds["data"][0]  if top_cdu_ds and top_cdu_ds["data"] else 0
    top_peak_i = top_cdu_ds["data"].index(max(top_cdu_ds["data"])) if top_cdu_ds else 0
    top_peak_m = monthly["months"][top_peak_i] if top_cdu_ds else "—"
    top_peak_v = max(top_cdu_ds["data"]) if top_cdu_ds else 0
    top_yoy    = (top_vol - top_first) / top_first * 100 if top_first else 0

    # top 2 solutions combined
    sol_top2_vol = sum(s["volume"] for s in solutions[:2]) if len(solutions) >= 2 else 0
    sol_top2_pct = sol_top2_vol / total_v * 100 if total_v else 0
    sol1         = solutions[0]["solution"] if solutions else "—"
    sol1_vol     = solutions[0]["volume"]   if solutions else 0
    sol1_pct     = sol1_vol / total_v * 100 if total_v else 0
    sol2         = solutions[1]["solution"] if len(solutions) > 1 else "—"
    sol2_vol     = solutions[1]["volume"]   if len(solutions) > 1 else 0

    # daily peak detection
    daily_peak_vol, daily_peak_day = 0, "—"
    if daily["days"] and daily["datasets"]:
        daily_totals = _period_totals(daily["datasets"], len(daily["days"]))
        daily_peak_vol = max(daily_totals)
        daily_peak_day = daily["days"][daily_totals.index(daily_peak_vol)]
    daily_avg = sum(_period_totals(daily["datasets"], len(daily["days"]))) / len(daily["days"]) if daily["days"] else 0
    peak_ratio = daily_peak_vol / daily_avg if daily_avg else 0

    # ── Metric cards ──────────────────────────────────────────────────────────
    cards = [
        ("Volume YTD",         f"{total_v:,}",
         "atendimentos outgoing"),
        ("CDU Principal",      top_cdu[:38] + ("…" if len(top_cdu) > 38 else ""),
         f"{top_pct:.1f}% do volume total"),
        ("Solução Top 1",      sol1[:38] + ("…" if len(sol1) > 38 else ""),
         f"{sol1_pct:.1f}% do volume total"),
        (f"Tendência {m_lbl}", f"<span style='color:{m_color}'>{m_arrow} {abs(m_delta):.1f}%</span>",
         f"vs {m_prev}"),
    ]
    cards_html = "".join(
        f'<div class="ex-card">'
        f'<div class="ex-lbl">{lbl}</div>'
        f'<div class="ex-val">{val}</div>'
        f'<div class="ex-sub">{sub}</div>'
        f'</div>'
        for lbl, val, sub in cards
    )

    # ── Bullets ───────────────────────────────────────────────────────────────
    bullets = []

    # 1. Conta inativa — dominância e trajetória
    bullets.append(
        f"<strong>Conta inativa domina o volume e não está melhorando:</strong> "
        f"<em>{top_cdu}</em> concentra <strong>{top_pct:.0f}%</strong> de todo o outgoing "
        f"({top_vol:,} contatos). O pico foi em <strong>{top_peak_m}</strong> ({top_peak_v:,} contatos), "
        f"e o volume acumulado no período é <strong>{top_yoy:+.0f}%</strong> acima de "
        f"{monthly['months'][0] if monthly['months'] else '—'}. "
        f"O padrão sistêmico é confirmado pela solução mais usada: <em>{sol1}</em> "
        f"aplicada <strong>{sol1_vol:,} vezes</strong> ({sol1_pct:.0f}% do total)."
    )

    # 2. Top 2 solutions = 1/3 of all volume
    if sol_top2_pct > 20:
        bullets.append(
            f"<strong>Concentração crítica nas soluções:</strong> apenas as 2 primeiras soluções "
            f"(<em>{sol1}</em> e <em>{sol2}</em>) somam <strong>{sol_top2_vol:,} atendimentos "
            f"({sol_top2_pct:.0f}% do total)</strong> — ou seja, 1 em cada "
            f"{int(100/sol_top2_pct)} contatos resolve com a mesma resposta. "
            f"Isso representa uma <strong>oportunidade clara de deflexão via autoatendimento.</strong>"
        )

    # 3. Fastest growing CDU
    if fastest_cdu and fastest_pct > 50 and fastest_cdu != top_cdu:
        f_first = fastest_ds["data"][0] if fastest_ds else 0
        f_last  = fastest_ds["data"][-1] if fastest_ds else 0
        bullets.append(
            f"<strong>CDU em aceleração — sinal de alerta:</strong> "
            f"<em>{fastest_cdu}</em> cresceu <strong>{fastest_pct:.0f}%</strong> de "
            f"{monthly['months'][0]} ({f_first:,}) a {m_lbl} ({f_last:,}). "
            f"Crescimento consistente mês a mês sem sinais de desaceleração."
        )

    # 4. Daily peak anomaly
    if peak_ratio >= 2.0 and daily_peak_day != "—":
        bullets.append(
            f"<strong>Pico atípico em {daily_peak_day}:</strong> {daily_peak_vol:,} contatos "
            f"em um único dia — <strong>{peak_ratio:.1f}x acima da média diária</strong> "
            f"({daily_avg:.0f} contatos/dia). Provável evento de bloqueio em massa "
            f"ou instabilidade de sistema nessa data."
        )

    # 5. CDU coverage / sem CDU
    if sem_cdu_v > 0:
        bullets.append(
            f"<strong>{sem_cdu_v:,} atendimentos sem CDU identificado</strong> "
            f"({100 - id_rate:.0f}% do total) — baixo impacto, mas indica oportunidade "
            f"pontual de melhoria na marcação dos agentes."
        )

    bullets_html = "".join(f'<li class="ex-li">{b}</li>' for b in bullets)

    return f"""
  <div class="card ex-block">
    <div class="ex-title">Resumo Executivo</div>
    <div class="ex-cards">{cards_html}</div>
    <ul class="ex-bullets">{bullets_html}</ul>
  </div>"""

def _nps_cell(val) -> str:
    if val is None:
        return '<td class="vn" style="color:#ccc">—</td>'
    c = nps_color(val)
    sign = "+" if val > 0 else ""
    return f'<td class="vn" style="color:{c};font-weight:700">{sign}{val:.1f}</td>'

def _render_cdu_nps_table(monthly: dict, weekly: dict,
                          nps_by_cdu: list, nps_monthly: dict) -> str:
    nps_ytd_map   = {r["cdu"]: r["nps"] for r in nps_by_cdu}
    by_cdu_month  = nps_monthly.get("by_cdu_month", {})
    last_month_key = None
    if monthly["months"]:
        lm_label = monthly["months"][-1]
        # find the YYYY-MM key that matches this label
        last_month_key = next(
            (k for k in by_cdu_month.get(list(by_cdu_month.keys())[0] if by_cdu_month else "", {})
             if month_label(k) == lm_label), None
        ) if by_cdu_month else None
        if last_month_key is None:
            # fallback: scan all keys
            all_keys = set()
            for v in by_cdu_month.values():
                all_keys.update(v.keys())
            last_month_key = next((k for k in sorted(all_keys, reverse=True)
                                   if month_label(k) == lm_label), None)

    # last week index
    last_w_idx = len(weekly["weeks"]) - 1

    rows = ""
    for i, cdu in enumerate(monthly["top_cdus"]):
        # monthly outgoing (last month)
        m_ds   = next((ds for ds in monthly["datasets"] if ds["label"] == cdu), None)
        m_vol  = m_ds["data"][-1] if m_ds and m_ds["data"] else 0
        # weekly outgoing (last week)
        w_ds   = next((ds for ds in weekly["datasets"] if ds["label"] == cdu), None)
        w_vol  = w_ds["data"][last_w_idx] if w_ds and len(w_ds["data"]) > last_w_idx else 0
        # YTD outgoing
        ytd_vol = monthly["cdu_totals"].get(cdu, 0)
        # NPS
        m_nps  = by_cdu_month.get(cdu, {}).get(last_month_key) if last_month_key else None
        nps_ytd = nps_ytd_map.get(cdu)

        rc  = ' class="tr0"' if i == 0 else ""
        rows += (
            f'<tr{rc}><td>{cdu}</td>'
            f'<td class="vn">{m_vol:,}</td>{_nps_cell(m_nps)}'
            f'<td class="vn">{w_vol:,}</td>{_nps_cell(None)}'
            f'<td class="vn">{ytd_vol:,}</td>{_nps_cell(nps_ytd)}'
            f'</tr>'
        )
    return rows

def _render_mom_scorecard(rows: list) -> str:
    if not rows:
        return '<tr><td colspan="8" style="text-align:center;color:#aaa">Sem dados</td></tr>'

    last_mlbl = rows[0]["last_mlbl"] if rows else "—"
    prev_mlbl = rows[0]["prev_mlbl"] if rows else "—"

    def arrow(val, invert=False):
        if val is None: return ""
        up = val > 0
        if invert: up = not up
        color = "#70AD47" if up else "#E05252"
        sym   = "▲" if val > 0 else "▼"
        return f'<span style="color:{color}">{sym}</span>'

    def fmt_delta(val, pct=False):
        if val is None: return '<span style="color:#ccc">—</span>'
        sign  = "+" if val > 0 else ""
        color = "#70AD47" if val > 0 else "#E05252"
        suf   = "%" if pct else "pt"
        return f'<span style="color:{color};font-weight:700">{sign}{val:.1f}{suf}</span>'

    def gap_cell(gap):
        if gap is None: return '<td style="text-align:center;color:#ccc">—</td>'
        c    = nps_color(gap + 50 if gap >= 0 else gap + 50)   # reuse color scale
        c    = "#70AD47" if gap >= 0 else ("#ED7D31" if gap >= -10 else "#E05252")
        sign = "+" if gap >= 0 else ""
        return f'<td style="text-align:center;font-weight:700;color:{c}">{sign}{gap:.1f}pt</td>'

    html  = f"""<thead><tr>
      <th>CDU</th>
      <th style="text-align:center">NPS {last_mlbl}</th>
      <th style="text-align:center">Target</th>
      <th style="text-align:center">Gap vs Target</th>
      <th style="text-align:center">MoM NPS<br><small style="font-weight:400">{prev_mlbl}→{last_mlbl}</small></th>
      <th style="text-align:center">Vol. {last_mlbl}</th>
      <th style="text-align:center">MoM Vol.</th>
    </tr></thead><tbody>"""

    for i, r in enumerate(rows):
        rc  = ' class="tr0"' if i == 0 else ""
        nps = r["nps_last"]
        tgt = r["target"]
        gap = r["gap"]
        nps_str = f'<span class="nps-pill" style="background:{nps_color(nps)}22;color:{nps_color(nps)}">{("+" if nps>0 else "")}{nps:.1f}</span>' if nps is not None else "—"
        tgt_str = f'{tgt:.1f}' if tgt is not None else "—"
        html += (
            f'<tr{rc}>'
            f'<td>{r["cdu"]}</td>'
            f'<td style="text-align:center">{nps_str}</td>'
            f'<td style="text-align:center;color:#888">{tgt_str}</td>'
            f'{gap_cell(gap)}'
            f'<td style="text-align:center">{arrow(r["nps_mom"])} {fmt_delta(r["nps_mom"])}</td>'
            f'<td style="text-align:right;font-variant-numeric:tabular-nums">{r["vol_last"]:,}</td>'
            f'<td style="text-align:center">{arrow(r["vol_mom_pct"], invert=True)} {fmt_delta(r["vol_mom_pct"], pct=True)}</td>'
            f'</tr>'
        )
    html += "</tbody>"
    return html

def _render_detractor_card(data: dict, label: str, nps_val, impact_val=None,
                            combo_data: dict = None, combo_id: str = "") -> str:
    cdu      = data.get("cdu", "—")
    total    = data.get("total", 0)
    themes   = data.get("themes", [])
    samples  = data.get("samples", [])

    if not total:
        return (f'<div class="card det-card">'
                f'<div class="det-header"><span class="det-badge">{label}</span>'
                f'<span class="det-cdu">{cdu}</span></div>'
                f'<p style="color:#999;font-size:12px">Sem comentários de detratores no período.</p>'
                f'</div>')

    nps_c   = nps_color(nps_val) if nps_val is not None else "#888"
    nps_str = f"{nps_val:.1f}" if nps_val is not None else "—"
    imp_str = ""
    if impact_val is not None:
        ic = "#70AD47" if impact_val >= 0 else "#E05252"
        imp_str = f'<span style="color:{ic};font-size:11px;font-weight:700">{"+" if impact_val>=0 else ""}{impact_val:.2f}pp impacto</span>'

    # Gráfico combo Outgoing + NPS (substitui razões de detração)
    combo_html = ""
    if combo_data and combo_id:
        combo_html = f'<div class="cw" style="height:200px"><canvas id="{combo_id}"></canvas></div>'

    # Temas TF-IDF
    themes_html = ""
    if themes:
        themes_html = '<div class="det-themes">' + "".join(
            f'<div class="det-theme-chip" style="background:{ACCENT_COLORS[i%len(ACCENT_COLORS)]}18;'
            f'border-left:3px solid {ACCENT_COLORS[i%len(ACCENT_COLORS)]}">'
            f'<span class="det-theme-name">{t["name"]}</span>'
            f'<span class="det-theme-pct" style="color:{ACCENT_COLORS[i%len(ACCENT_COLORS)]}">{t["pct"]}%</span>'
            f'<p class="det-theme-sample">{t["samples"][0][:180] if t["samples"] else ""}…</p>'
            f'</div>'
            for i, t in enumerate(themes)
        ) + '</div>'

    # Amostras
    samples_html = ""
    if samples:
        samples_html = '<div class="det-samples-label">Amostras de comentários</div><div class="det-samples">' + "".join(
            f'<div class="det-sample">" {s[:200]} "</div>'
            for s in samples[:6]
        ) + '</div>'

    return f"""
<div class="card det-card">
  <div class="det-header">
    <span class="det-badge">{label}</span>
    <div>
      <div class="det-cdu">{cdu}</div>
      <div style="display:flex;gap:10px;align-items:center;margin-top:2px">
        <span style="font-size:18px;font-weight:900;color:{nps_c}">NPS {nps_str}</span>
        {imp_str}
        <span style="font-size:11px;color:#888">{total} detratores analisados (últimos 90 dias)</span>
      </div>
    </div>
  </div>
  <div class="det-grid">
    <div>
      <p class="det-section-title">Outgoing × NPS Mensal</p>
      {combo_html}
    </div>
    <div>
      <p class="det-section-title">Principais Temas nos Comentários</p>
      {themes_html or '<p style="font-size:12px;color:#999">Sem temas identificados (poucos comentários).</p>'}
    </div>
  </div>
  {samples_html}
</div>"""

def _cascata_title(tgt, actual, gap) -> str:
    if not tgt:
        return "Impacto CDU vs Target Drivers · YTD"
    gap_html = ""
    if gap is not None:
        c = "#70AD47" if gap >= 0 else "#E05252"
        gap_html = f' <span style="color:{c};font-weight:700">{"+" if gap>=0 else ""}{gap}pp</span>'
    return (f'Impacto CDU vs Target Drivers · YTD'
            f'<span style="font-size:11px;font-weight:400;color:#888;margin-left:6px">'
            f'Target {tgt} → Real {actual}{gap_html}</span>')

def _render_mini_card(c: dict) -> str:
    nps    = c["nps"]
    gap    = c["gap"]
    impact = c["impact"]
    mom    = c["mom"]
    weight = c["weight"]
    border = nps_color(nps) if nps is not None else "#ccc"
    nps_str    = f"{nps:.1f}" if nps is not None else "—"
    mom_str    = (f'<span style="color:{"#70AD47" if mom>=0 else "#E05252"};font-size:12px;font-weight:700">'
                  f'{"+" if mom>=0 else ""}{mom:.1f}pp MoM</span>') if mom is not None else ""
    gap_color  = "#70AD47" if (gap or 0) >= 0 else "#E05252"
    gap_str    = (f'<span style="color:{gap_color};font-weight:700">'
                  f'{"+" if gap>=0 else ""}{gap:.1f}pp vs tgt</span>') if gap is not None else "—"
    imp_color  = "#70AD47" if (impact or 0) >= 0 else "#E05252"
    imp_str    = (f'<span style="color:{imp_color};font-weight:700">'
                  f'{"+" if impact>=0 else ""}{impact:.2f}pp impacto</span>') if impact is not None else ""
    short_cdu  = c["cdu"][:36] + ("…" if len(c["cdu"]) > 36 else "")
    return (
        f'<div class="mini-card" style="border-top:3px solid {border}">'
        f'<div class="mc-title">{short_cdu}</div>'
        f'<div class="mc-row">'
        f'<span class="mc-nps" style="color:{border}">{nps_str}</span>'
        f'<span style="font-size:10px;color:#888;margin-left:4px">tgt {c["target"]:.1f} · {weight:.0f}%</span>'
        f'</div>'
        f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:4px">'
        f'{gap_str}&nbsp;·&nbsp;{imp_str}'
        f'</div>'
        f'<div style="margin-bottom:4px">{mom_str}</div>'
        f'<div class="cw" style="height:100px"><canvas id="{c["id"]}"></canvas></div>'
        f'</div>'
    )

def _render_nps_monthly_table(top_cdus: list, nps_monthly: dict, nps_by_cdu: list) -> str:
    by_cdu_month = nps_monthly.get("by_cdu_month", {})
    ytd_map      = {r["cdu"]: (r["nps"], r["surveys"]) for r in nps_by_cdu}

    # collect all month keys present, sorted
    all_keys: set = set()
    for v in by_cdu_month.values():
        all_keys.update(v.keys())
    month_keys = sorted(all_keys)

    header = "<thead><tr><th>CDU</th>"
    for k in month_keys:
        header += f"<th style='text-align:center'>{month_label(k)}</th>"
    header += "<th style='text-align:center'>YTD</th><th style='text-align:center'>Pesquisas YTD</th></tr></thead>"

    rows = "<tbody>"
    for i, cdu in enumerate(top_cdus):
        rc = ' class="tr0"' if i == 0 else ""
        rows += f'<tr{rc}><td>{cdu}</td>'
        for k in month_keys:
            entry = by_cdu_month.get(cdu, {}).get(k)
            v = entry.get("nps") if isinstance(entry, dict) else entry
            if v is not None:
                c    = nps_color(v)
                sign = "+" if v > 0 else ""
                rows += f'<td style="text-align:center"><span class="nps-pill" style="background:{c}22;color:{c}">{sign}{v:.1f}</span></td>'
            else:
                rows += '<td style="text-align:center;color:#ccc">—</td>'
        ytd_nps, ytd_s = ytd_map.get(cdu, (None, 0))
        if ytd_nps is not None:
            c    = nps_color(ytd_nps)
            sign = "+" if ytd_nps > 0 else ""
            rows += f'<td style="text-align:center"><span class="nps-pill" style="background:{c}22;color:{c};font-size:12px">{sign}{ytd_nps:.1f}</span></td>'
            rows += f'<td style="text-align:center;color:#888">{ytd_s:,}</td>'
        else:
            rows += '<td style="text-align:center;color:#ccc">—</td><td style="text-align:center;color:#ccc">—</td>'
        rows += "</tr>"
    rows += "</tbody>"
    return header + rows

def _render_solutions(solutions: list, total_v: int) -> str:
    rows = ""
    for i, s in enumerate(solutions):
        vol = s["volume"]
        pct = f"{vol / total_v * 100:.1f}%" if total_v else "—"
        rc  = ' class="tr0"' if i == 0 else ""
        rows += (
            f'<tr{rc}><td class="sol-num">{i+1}</td>'
            f'<td class="sol-name">{s["solution"]}</td>'
            f'<td class="vn">{vol:,}</td>'
            f'<td class="vp">{pct}</td></tr>'
        )
    return rows

def generate_html(monthly: dict, weekly: dict, daily: dict, themes_by_cdu: dict,
                  solutions: list, nps_by_cdu: list, nps_monthly: dict,
                  nps_weekly: list, nps_daily: list,
                  nps_weekly_by_cdu: dict, waterfalls: dict,
                  mom_scorecard: list, detractor_analysis: dict) -> str:
    now_str = TODAY.strftime("%d/%m/%Y")

    top_cdu   = monthly["top_cdu"] or "—"
    total_v   = monthly["total_vol"]
    named_v   = sum(monthly["cdu_totals"].values())
    sem_cdu_v = monthly["sem_cdu_vol"]
    top_vol   = monthly["cdu_totals"].get(top_cdu, 0)
    top_pct   = f"{top_vol / total_v * 100:.1f}%" if total_v else "—"

    rows_html = ""
    for i, cdu in enumerate(monthly["top_cdus"][:12]):
        vol  = monthly["cdu_totals"].get(cdu, 0)
        pct  = f"{vol / total_v * 100:.1f}%" if total_v else "—"
        star = "⭐ " if i == 0 else f"{i+1}. "
        rc   = ' class="tr0"' if i == 0 else ""
        rows_html += (
            f'<tr{rc}><td>{star}{cdu}</td>'
            f'<td class="vn">{vol:,}</td>'
            f'<td class="vp">{pct}</td></tr>'
        )
    sem_pct = f"{sem_cdu_v / total_v * 100:.1f}%" if total_v else "—"
    rows_html += (
        f'<tr class="sem-cdu-row"><td>— Sem CDU</td>'
        f'<td class="vn">{sem_cdu_v:,}</td>'
        f'<td class="vp">{sem_pct}</td></tr>'
    )

    # Selector de CDU para análise de transcrições
    options = "".join(
        f'<option value="{cdu}"{" selected" if cdu == top_cdu else ""}>{cdu}</option>'
        for cdu in themes_by_cdu
    )
    initial_themes_html = _render_theme_cards(themes_by_cdu.get(top_cdu, []))

    # Charts JS
    m_colors = palette_for(monthly["datasets"])
    m_ds = ",".join(
        f"{{label:{jd(ds['label'])},data:{jd(ds['data'])},"
        f"backgroundColor:{jd(m_colors[i])},borderRadius:4,stack:'s'}}"
        for i, ds in enumerate(monthly["datasets"])
    )
    w_colors = palette_for(weekly["datasets"])
    w_ds = ",".join(
        f"{{label:{jd(ds['label'])},data:{jd(ds['data'])},"
        f"backgroundColor:{jd(w_colors[i])},borderRadius:4,stack:'s'}}"
        for i, ds in enumerate(weekly["datasets"])
    )
    d_colors = palette_for(daily["datasets"])
    d_ds = ",".join(
        f"{{label:{jd(ds['label'])},data:{jd(ds['data'])},"
        f"backgroundColor:{jd(d_colors[i])},borderRadius:4,stack:'s'}}"
        for i, ds in enumerate(daily["datasets"])
    )

    teams_label = " · ".join(TEAMS)

    # ── NPS tab data ──────────────────────────────────────────────────────────
    nps_sorted   = sorted(
        [r for r in nps_by_cdu if r["nps"] is not None and r["cdu"] != "Sem CDU"],
        key=lambda x: x["nps"], reverse=True
    )
    nps_bar_labels  = [r["cdu"]     for r in nps_sorted]
    nps_bar_values  = [r["nps"]     for r in nps_sorted]
    nps_bar_colors  = [nps_color(v) for v in nps_bar_values]
    nps_bar_surveys = [r["surveys"] for r in nps_sorted]

    # CDU × NPS monthly table
    nps_table_html = _render_nps_monthly_table(monthly["top_cdus"], nps_monthly, nps_by_cdu)

    # MoM scorecard table
    scorecard_html = _render_mom_scorecard(mom_scorecard)

    last_mlbl = mom_scorecard[0]["last_mlbl"] if mom_scorecard else "—"
    prev_mlbl = mom_scorecard[0]["prev_mlbl"] if mom_scorecard else "—"

    # Weighted average target for evolution charts
    total_s = sum(r["surveys"] for r in nps_by_cdu if r["target"] is not None)
    avg_target = round(
        sum((r["target"] or 0) * r["surveys"] for r in nps_by_cdu if r["target"] is not None)
        / total_s, 1
    ) if total_s else None

    # Detractor analysis cards
    nps_map_det = {r["cdu"]: r for r in nps_by_cdu}
    casc_bars_det = waterfalls.get("cascata", [])
    det_worst_data  = detractor_analysis.get("worst_cdu",  {})
    det_top_og_data = detractor_analysis.get("top_og_cdu", {})
    worst_nps    = nps_map_det.get(det_worst_data.get("cdu", ""),  {}).get("nps")
    top_og_nps   = nps_map_det.get(det_top_og_data.get("cdu", ""), {}).get("nps")
    worst_impact = next(
        (b["contrib"] for b in casc_bars_det
         if not b.get("isAnchor") and det_worst_data.get("cdu","")[:20] in b.get("label","") + b.get("label","")[:20]),
        None
    )
    def _cdu_combo_data(cdu):
        og_ds  = next((ds for ds in monthly["datasets"] if ds["label"] == cdu), None)
        og_vals = og_ds["data"] if og_ds else []
        nps_vals = []
        by_m = nps_monthly.get("by_cdu_month", {}).get(cdu, {})
        mk_sorted = sorted(by_m.keys())
        for m in monthly["months"]:
            ym = next((k for k in mk_sorted if month_label(k) == m), None)
            entry = by_m.get(ym, {}) if ym else {}
            nps_vals.append(entry.get("nps") if isinstance(entry, dict) else entry)
        tgt = nps_map_det.get(cdu, {}).get("target") or process_target
        return {"labels": monthly["months"], "og": og_vals, "nps": nps_vals, "target": tgt}

    combo_worst  = _cdu_combo_data(det_worst_data.get("cdu", ""))
    combo_top_og = _cdu_combo_data(det_top_og_data.get("cdu", ""))

    det_worst_card  = _render_detractor_card(det_worst_data,  "CDU Mais Ofensor",          worst_nps,  worst_impact, combo_worst,  "cDetWorst")
    det_top_og_card = _render_detractor_card(det_top_og_data, "CDU Maior Volume Outgoing", top_og_nps, None,         combo_top_og, "cDetTopOg")

    # Waterfall data
    casc  = waterfalls.get("cascata", [])
    wtf   = waterfalls.get("wtf", [])
    wtf_labels = waterfalls.get("wtf_labels", ("—", "—"))
    tgt_wt         = waterfalls.get("tgt_wt")
    actual_wt      = waterfalls.get("actual_wt")
    process_target = waterfalls.get("process_target") or tgt_wt
    total_gap      = waterfalls.get("total_gap")

    # Mini cards per CDU
    nps_ytd_map = {r["cdu"]: r for r in nps_by_cdu}
    mini_cards  = []
    for i, cdu in enumerate(monthly["top_cdus"]):
        ytd = nps_ytd_map.get(cdu, {})
        sc  = next((r for r in mom_scorecard if r["cdu"] == cdu), {})
        wk_data = nps_weekly_by_cdu.get(cdu, [None] * len(weekly["weeks"]))
        wk_nps = [e.get("nps") if isinstance(e, dict) else None for e in wk_data]
        nps_val = ytd.get("nps")
        gap_proc = round(nps_val - process_target, 1) if (nps_val is not None and process_target is not None) else None
        # impact = gap × weight (quanto este CDU contribui para o gap total)
        weight   = round(ytd.get("surveys", 0) / total_s * 100, 1) if total_s else 0
        impact   = round(gap_proc * weight / 100, 2) if gap_proc is not None else None
        mini_cards.append({
            "id":      f"cMini{i}",
            "cdu":     cdu,
            "nps":     nps_val,
            "target":  process_target,
            "gap":     gap_proc,
            "impact":  impact,
            "weight":  weight,
            "mom":     sc.get("nps_mom"),
            "weeks":   weekly["weeks"],
            "wk_nps":  wk_nps,
        })

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Outgoing Drivers | NPS | MLB</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:#f0f2f5;color:#1a1a2e;min-height:100vh}}
.hd{{background:linear-gradient(135deg,#ffe600,#f5c800);
    padding:14px 28px;display:flex;align-items:center;gap:14px;
    box-shadow:0 2px 8px rgba(0,0,0,.12)}}
.logo{{background:#1a1a2e;color:#ffe600;font-weight:900;font-size:13px;
      border-radius:7px;padding:5px 10px;letter-spacing:-.5px;line-height:1.2}}
.hd h1{{font-size:15px;font-weight:800;color:#1a1a2e}}
.hd p{{font-size:11px;color:#555;margin-top:2px}}
.main{{max-width:1500px;margin:0 auto;padding:22px 24px;
       display:flex;flex-direction:column;gap:18px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
@media(max-width:820px){{.grid2{{grid-template-columns:1fr}}}}
.card{{background:#fff;border-radius:12px;padding:20px;
      box-shadow:0 1px 4px rgba(0,0,0,.07)}}
.chart-title{{font-size:12px;font-weight:700;color:#444;
             text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px}}
.cw{{position:relative}}
.tab-nav{{display:flex;gap:3px;background:#fff;border-radius:10px;
         padding:4px;width:fit-content;
         box-shadow:0 1px 4px rgba(0,0,0,.08)}}
.tab-btn{{border:none;background:transparent;border-radius:7px;
         padding:8px 28px;font-size:13px;font-weight:700;color:#666;
         cursor:pointer;transition:all .15s}}
.tab-btn.active{{background:#ffe600;color:#1a1a2e;box-shadow:0 1px 4px rgba(0,0,0,.1)}}
.tab-pane{{display:none;flex-direction:column;gap:18px}}
.tab-pane.active{{display:flex}}
.hl-card{{display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:start}}
@media(max-width:680px){{.hl-card{{grid-template-columns:1fr}}}}
.hl-box{{background:linear-gradient(135deg,#ffe600,#f5c800);border-radius:10px;
        padding:20px 24px;text-align:center;min-width:240px}}
.hl-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;
        letter-spacing:1px;color:#666;margin-bottom:8px}}
.hl-val{{font-size:17px;font-weight:900;color:#1a1a2e;margin-bottom:6px;line-height:1.2}}
.hl-sub{{font-size:11px;color:#555}}
.hl-sub2{{font-size:10px;color:#888;margin-top:4px}}
.rtable{{width:100%;border-collapse:collapse;font-size:12px}}
.rtable th{{background:#f8f9fa;padding:7px 12px;text-align:left;font-weight:700;
           color:#888;text-transform:uppercase;font-size:10px;letter-spacing:.6px;
           border-bottom:1px solid #eee}}
.rtable td{{padding:7px 12px;border-bottom:1px solid #f5f5f5;vertical-align:middle}}
.rtable .tr0{{background:#fffde7;font-weight:600}}
.rtable .sem-cdu-row{{color:#aaa;font-style:italic;border-top:1px solid #eee}}
.hl-right{{display:flex;flex-direction:column;gap:14px}}
.vn{{text-align:right;font-variant-numeric:tabular-nums}}
.vp{{text-align:right;color:#888}}
.no-data{{font-size:12px;color:#999;padding:8px 0}}
.th-hdr{{margin-bottom:16px}}
.th-title-row{{display:flex;align-items:baseline;gap:6px;flex-wrap:wrap;margin-bottom:3px}}
.th-label{{font-size:13px;font-weight:700;white-space:nowrap}}
.cdu-sel{{font-size:14px;font-weight:800;color:#c89600;background:transparent;
         border:none;border-bottom:2px solid #e8b000;cursor:pointer;padding:0 4px 1px;
         outline:none;font-family:inherit;max-width:480px}}
.cdu-sel:focus{{border-bottom-color:#4472C4}}
.cdu-sel option{{color:#1a1a2e;font-weight:600;background:#fff}}
.th-sub{{font-size:11px;color:#888;display:block}}
.themes-list{{display:flex;flex-direction:column;gap:12px}}
.theme-card{{border-left:3px solid #ccc;padding:13px 16px;
            background:#fafafa;border-radius:0 8px 8px 0}}
.tc-header{{display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap}}
.tc-name{{font-size:13px;font-weight:700;color:#1a1a2e}}
.tc-badge{{font-size:11px;font-weight:700;padding:2px 10px;border-radius:20px;white-space:nowrap}}
.tc-summary{{font-size:12px;color:#555;line-height:1.55;margin-bottom:8px}}
.tc-chips{{display:flex;flex-wrap:wrap;gap:6px}}
.case-chip{{font-size:11px;font-family:monospace;background:#eef2ff;
           color:#4472C4;padding:2px 9px;border-radius:12px}}
.sol-table .sol-num{{width:32px;text-align:center;color:#aaa;font-size:11px}}
.sol-table .sol-name{{max-width:520px}}
.ex-block{{}}
.ex-title{{font-size:12px;font-weight:700;color:#444;text-transform:uppercase;
           letter-spacing:.5px;margin-bottom:14px}}
.ex-cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}}
@media(max-width:820px){{.ex-cards{{grid-template-columns:repeat(2,1fr)}}}}
.ex-card{{background:#f8f9fa;border-radius:8px;padding:12px 16px}}
.ex-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;
         color:#888;margin-bottom:4px}}
.ex-val{{font-size:16px;font-weight:900;color:#1a1a2e;line-height:1.2;margin-bottom:2px}}
.ex-sub{{font-size:11px;color:#666}}
.ex-bullets{{padding-left:18px;display:flex;flex-direction:column;gap:6px}}
.ex-bullets li{{font-size:13px;color:#333;line-height:1.55}}
.ex-li{{padding:6px 0;border-bottom:1px solid #f0f2f5}}
.ex-li:last-child{{border-bottom:none}}
.no-data-block{{display:flex;gap:12px;align-items:flex-start;padding:14px 16px;
               background:#fff8e1;border-radius:8px;border-left:3px solid #FFC000}}
.no-data-block .no-data-icon{{font-size:20px;line-height:1}}
.no-data-block strong{{font-size:13px;color:#1a1a2e}}
.no-data-block code{{font-size:11px;background:#f0f0f0;padding:1px 5px;border-radius:3px}}
.no-data-block div{{font-size:12px;color:#555;line-height:1.55}}
.nps-pill{{display:inline-block;font-size:11px;font-weight:800;padding:2px 10px;
          border-radius:20px;white-space:nowrap}}
.mini-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}
.det-card{{}}
.det-header{{display:flex;gap:14px;align-items:flex-start;margin-bottom:16px;flex-wrap:wrap}}
.det-badge{{background:#1a1a2e;color:#ffe600;font-size:10px;font-weight:800;
           padding:4px 10px;border-radius:20px;white-space:nowrap;height:fit-content;margin-top:2px}}
.det-cdu{{font-size:14px;font-weight:800;color:#1a1a2e;line-height:1.3}}
.det-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:16px}}
@media(max-width:820px){{.det-grid{{grid-template-columns:1fr}}}}
.det-section-title{{font-size:11px;font-weight:700;text-transform:uppercase;
                   letter-spacing:.5px;color:#888;margin-bottom:10px}}
.det-reason-row{{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:12px}}
.det-reason-lbl{{min-width:200px;max-width:200px;color:#333;overflow:hidden;
                text-overflow:ellipsis;white-space:nowrap}}
.det-bar-wrap{{flex:1;background:#f0f2f5;border-radius:4px;height:8px}}
.det-bar{{height:8px;background:#E05252;border-radius:4px;transition:width .3s}}
.det-reason-n{{font-weight:700;color:#666;min-width:28px;text-align:right}}
.det-themes{{display:flex;flex-direction:column;gap:8px}}
.det-theme-chip{{padding:10px 12px;border-radius:0 8px 8px 0}}
.det-theme-name{{font-size:12px;font-weight:700;color:#1a1a2e}}
.det-theme-pct{{font-size:11px;font-weight:700;margin-left:8px}}
.det-theme-sample{{font-size:11px;color:#666;margin-top:4px;line-height:1.4;
                  font-style:italic;border-left:2px solid #ddd;padding-left:8px}}
.det-samples-label{{font-size:11px;font-weight:700;text-transform:uppercase;
                   letter-spacing:.5px;color:#888;margin-bottom:8px}}
.det-samples{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:8px}}
.det-sample{{font-size:12px;color:#444;background:#fafafa;border-radius:8px;
            padding:10px 14px;border-left:3px solid #e0e0e0;line-height:1.5;font-style:italic}}
.mini-card{{background:#fff;border-radius:10px;padding:14px 14px 10px;
           box-shadow:0 1px 4px rgba(0,0,0,.07)}}
.mc-title{{font-size:11px;font-weight:700;color:#444;margin-bottom:6px;
          white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.mc-row{{display:flex;align-items:baseline;gap:8px;margin-bottom:2px}}
.mc-nps{{font-size:20px;font-weight:900;line-height:1}}
.mc-mom{{font-size:12px;font-weight:700}}
.mc-gap{{font-size:11px;color:#666;margin-bottom:6px}}
</style>
</head>
<body>

<header class="hd">
  <div class="logo">ML</div>
  <div>
    <h1>Processo Drivers — Outgoing &amp; NPS</h1>
    <p>MLB · {teams_label} · Jan–Mai 2026 · Atualizado em {now_str}</p>
  </div>
</header>

<main class="main">

  {generate_exec_summary(monthly, weekly, daily, solutions)}

  <nav class="tab-nav">
    <button class="tab-btn active" onclick="goTab(0)">Outgoing</button>
    <button class="tab-btn"        onclick="goTab(1)">NPS</button>
  </nav>

  <!-- ── ABA OUTGOING ─────────────────────────────────────────── -->
  <div class="tab-pane active" id="tp0">

    <div class="grid2">
      <div class="card">
        <p class="chart-title">Volume mensal por CDU</p>
        <div class="cw" style="height:420px"><canvas id="cM"></canvas></div>
      </div>
      <div class="card">
        <p class="chart-title">Volume semanal por CDU · últimas 8 semanas</p>
        <div class="cw" style="height:420px"><canvas id="cW"></canvas></div>
      </div>
    </div>

    <div class="card">
      <p class="chart-title">Volume diário por CDU · últimos {DAILY_DAYS} dias</p>
      <div class="cw" style="height:420px"><canvas id="cD"></canvas></div>
    </div>

    <div class="card hl-card">
      <div class="hl-box">
        <div class="hl-lbl">CDU com Maior Volume</div>
        <div class="hl-val">{top_cdu}</div>
        <div class="hl-sub">{top_vol:,} atendimentos · {top_pct} do total identificado</div>
        <div class="hl-sub2">Total outgoing: {total_v:,} · Com CDU: {named_v:,} ({named_v/total_v*100:.0f}%)</div>
      </div>
      <div class="hl-right">
        <table class="rtable">
          <thead><tr><th>CDU</th><th>Volume</th><th>%</th></tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <p class="chart-title">Top {TOP_SOLUTIONS} Soluções</p>
      <table class="rtable sol-table">
        <thead><tr><th>#</th><th>Solução</th><th>Volume</th><th>%</th></tr></thead>
        <tbody>{_render_solutions(solutions, total_v)}</tbody>
      </table>
    </div>

    <div class="card">
      <div class="th-hdr">
        <div class="th-title-row">
          <span class="th-label">Análise de Transcrições · CDU:</span>
          <select class="cdu-sel" id="cduSel" onchange="selectCDU(this.value)">
            {options}
          </select>
        </div>
        <span class="th-sub">Motivos de contato identificados (últimos {TRANSCRIPT_DAYS} dias)</span>
      </div>
      <div id="themesBox">{initial_themes_html}</div>
    </div>

  </div><!-- /tp0 -->

  <!-- ── ABA NPS ───────────────────────────────────────────────── -->
  <div class="tab-pane" id="tp1">

    <!-- Mini cards por CDU -->
    <div class="mini-grid">
      {''.join(_render_mini_card(c) for c in mini_cards)}
    </div>

    <!-- Cascatas -->
    <div class="card">
      <p class="chart-title">WTF MoM · {wtf_labels[0]} → {wtf_labels[1]}</p>
      <div class="cw" style="height:480px"><canvas id="cWtf"></canvas></div>
    </div>

    <div class="card">
      <p class="chart-title">{_cascata_title(tgt_wt, actual_wt, total_gap)}</p>
      <div class="cw" style="height:480px"><canvas id="cCascade"></canvas></div>
    </div>

    <!-- Análise de Detratores -->
    <div class="card" style="padding:0;overflow:hidden">
      <div style="background:#1a1a2e;padding:14px 20px">
        <span style="color:#ffe600;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.5px">
          Voz dos Detratores · Últimos 90 dias
        </span>
      </div>
      <div style="padding:20px;display:flex;flex-direction:column;gap:20px">
        {det_worst_card}
        {det_top_og_card}
      </div>
    </div>

    <!-- Evolução com target -->
    <div class="card">
      <p class="chart-title">Evolução Mensal NPS + Target</p>
      <div class="cw" style="height:400px"><canvas id="cNpsMon"></canvas></div>
    </div>

    <div class="card">
      <p class="chart-title">Evolução Semanal NPS + Target</p>
      <div class="cw" style="height:400px"><canvas id="cNpsWk"></canvas></div>
    </div>

    <div class="card">
      <p class="chart-title">Scorecard MoM por CDU · {prev_mlbl} → {last_mlbl}</p>
      <table class="rtable">{scorecard_html}</table>
    </div>

    <div class="card">
      <p class="chart-title">CDU × NPS Lineal por mês</p>
      <table class="rtable">{nps_table_html}</table>
    </div>

  </div><!-- /tp1 -->

</main>

<script>
const ACCENT = {jd(ACCENT_COLORS)};
const ALL_THEMES = {jd(themes_by_cdu)};

// ── Tab ──────────────────────────────────────────────────────────────────────
let npsInited = false;
function goTab(n) {{
  document.querySelectorAll('.tab-btn').forEach((b,i) => b.classList.toggle('active', i===n));
  document.querySelectorAll('.tab-pane').forEach((p,i) => p.classList.toggle('active', i===n));
  if (n === 1 && !npsInited) {{ initNpsCharts(); npsInited = true; }}
}}

// ── Plugins ──────────────────────────────────────────────────────────────────
const stackedTotalsPlugin = {{
  id: 'stackedTotals',
  afterDatasetsDraw(chart) {{
    const {{ ctx, data }} = chart;
    const lastMeta = chart.getDatasetMeta(data.datasets.length - 1);
    ctx.save();
    ctx.font = 'bold 11px -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif';
    ctx.fillStyle = '#444';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    lastMeta.data.forEach((bar, i) => {{
      const total = data.datasets.reduce((sum, ds) => sum + (ds.data[i] || 0), 0);
      ctx.fillText(total.toLocaleString('pt-BR'), bar.x, bar.y - 4);
    }});
    ctx.restore();
  }}
}};

const innerPctPlugin = {{
  id: 'innerPct',
  afterDatasetsDraw(chart) {{
    const {{ ctx, data }} = chart;
    data.datasets.forEach((ds, dsIdx) => {{
      const meta = chart.getDatasetMeta(dsIdx);
      if (meta.hidden) return;
      meta.data.forEach((bar, i) => {{
        const value = ds.data[i] || 0;
        if (!value) return;
        const total = data.datasets.reduce((sum, d) => sum + (d.data[i] || 0), 0);
        const pct = Math.round(value / total * 100);
        if (pct < 6) return;
        const h = Math.abs(bar.base - bar.y);
        if (h < 14) return;
        ctx.save();
        ctx.font = 'bold 10px -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif';
        ctx.fillStyle = 'rgba(255,255,255,0.88)';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(pct + '%', bar.x, bar.y + h / 2);
        ctx.restore();
      }});
    }});
  }}
}};

// ── Outgoing charts ───────────────────────────────────────────────────────────
function bar(id, labels, datasets, showTotals=false, showPct=false) {{
  const plugins = [];
  if (showTotals) plugins.push(stackedTotalsPlugin);
  if (showPct)    plugins.push(innerPctPlugin);
  new Chart(document.getElementById(id), {{
    type: 'bar',
    data: {{ labels, datasets }},
    plugins,
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      layout: {{ padding: {{ top: showTotals ? 20 : 0 }} }},
      plugins: {{
        legend: {{ position: 'bottom',
                  labels: {{ boxWidth: 12, padding: 10, font: {{ size: 11 }} }} }},
        tooltip: {{
          callbacks: {{
            label: ctx => ` ${{ctx.dataset.label}}: ${{ctx.parsed.y.toLocaleString('pt-BR')}} atendimentos`
          }}
        }}
      }},
      scales: {{
        x: {{ stacked: true, grid: {{ display: false }}, ticks: {{ font: {{ size: 11 }} }} }},
        y: {{ stacked: true, grid: {{ color: '#f0f2f5' }},
              ticks: {{ font: {{ size: 11 }}, callback: v => v.toLocaleString('pt-BR') }} }}
      }}
    }}
  }});
}}

bar('cM', {jd(monthly['months'])}, [{m_ds}], true, true);
bar('cW', {jd(weekly['weeks'])},   [{w_ds}], true, true);
bar('cD', {jd(daily['days'])},     [{d_ds}], true, true);

// ── NPS charts (lazy — init on tab switch) ────────────────────────────────────
function npsColor(v) {{
  if (v === null || v === undefined) return '#ccc';
  if (v >= 50)  return '#70AD47';
  if (v >= 0)   return '#FFC000';
  if (v >= -20) return '#ED7D31';
  return '#E05252';
}}

function initNpsCharts() {{
  // NPS por CDU — horizontal bar (mantido para referência nos tooltips)
  const npsLabels  = {jd(nps_bar_labels)};
  const npsValues  = {jd(nps_bar_values)};
  const npsColors  = {jd(nps_bar_colors)};
  const npsSurveys = {jd(nps_bar_surveys)};
  if (document.getElementById('cNpsCdu')) new Chart(document.getElementById('cNpsCdu'), {{
    type: 'bar',
    data: {{ labels: npsLabels, datasets: [{{
      label: 'NPS Lineal',
      data: npsValues,
      backgroundColor: npsColors,
      borderRadius: 4,
    }}] }},
    plugins: [{{
      id: 'npsBarLabels',
      afterDatasetsDraw(chart) {{
        const {{ ctx, data }} = chart;
        const meta = chart.getDatasetMeta(0);
        ctx.save();
        ctx.font = 'bold 11px -apple-system, sans-serif';
        ctx.textBaseline = 'middle';
        meta.data.forEach((bar, i) => {{
          const v = data.datasets[0].data[i];
          const lbl = (v > 0 ? '+' : '') + v;
          const x   = v >= 0 ? bar.x + 6 : bar.x - 6;
          ctx.textAlign  = v >= 0 ? 'left' : 'right';
          ctx.fillStyle  = npsColors[i];
          ctx.fillText(lbl, x, bar.y);
        }});
        ctx.restore();
      }}
    }}],
    options: {{
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      layout: {{ padding: {{ right: 40 }} }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{
            label: ctx => ` NPS: ${{ctx.parsed.x > 0 ? '+' : ''}}${{ctx.parsed.x}}  (${{npsSurveys[ctx.dataIndex].toLocaleString('pt-BR')}} pesquisas)`
          }}
        }}
      }},
      scales: {{
        x: {{ min: -100, max: 100,
              grid: {{ color: ctx => ctx.tick.value === 0 ? '#aaa' : '#f0f2f5' }},
              ticks: {{ font: {{ size: 11 }}, callback: v => (v > 0 ? '+' : '') + v }} }},
        y: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 11 }} }} }}
      }}
    }}
  }}); // end cNpsCdu

  // ── Mini cards: weekly NPS por CDU ────────────────────────────────────────
  const miniCards = {jd(mini_cards)};
  miniCards.forEach(c => {{
    const el = document.getElementById(c.id);
    if (!el) return;
    const vals    = c.wk_nps;
    const tgt     = c.target;
    const hasData = vals.some(v => v !== null && v !== undefined);

    // Fallback: sem dados semanais → linha horizontal no NPS YTD
    const displayVals = hasData ? vals : vals.map(() => null);
    const ytdLine = !hasData && c.nps != null ? vals.map(() => c.nps) : null;

    const colors  = displayVals.map(v => v === null ? '#ddd' : npsColor(v));
    const tgtLine = vals.map(() => tgt);
    const datasets = [
      {{ data: displayVals, backgroundColor: colors, borderRadius: 3, barPercentage: 0.7 }},
      {{ type: 'line', data: tgtLine, borderColor: '#E05252', borderDash: [4,3],
         borderWidth: 1.5, pointRadius: 0, fill: false, spanGaps: true }},
    ];
    if (ytdLine) datasets.push({{
      type: 'line', data: ytdLine, borderColor: npsColor(c.nps),
      borderWidth: 1.5, pointRadius: 0, fill: false, spanGaps: true,
      borderDash: [3,2], label: `NPS YTD (${{c.nps}})`,
    }});
    new Chart(el, {{
      type: 'bar',
      data: {{ labels: c.weeks, datasets }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{ callbacks: {{ label: ctx =>
            ctx.datasetIndex === 0
              ? ` NPS: ${{ctx.parsed.y !== null ? (ctx.parsed.y>0?'+':'')+ctx.parsed.y : '—'}}`
              : ` Target: ${{ctx.parsed.y}}`
          }} }}
        }},
        scales: {{
          x: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 9 }}, maxRotation: 0 }} }},
          y: {{ grid: {{ color: '#f5f5f5' }},
                ticks: {{ font: {{ size: 9 }}, callback: v => v }},
                suggestedMin: tgt ? tgt - 20 : undefined }}
        }}
      }}
    }});
  }});

  // ── Helper: waterfall chart ────────────────────────────────────────────────
  function waterfallChart(id, bars) {{
    if (!bars.length || !document.getElementById(id)) return;
    const labels  = bars.map(b => b.label);
    const spacers = bars.map(b => b.spacer);
    const values  = bars.map(b => b.bar);
    const colors  = bars.map(b => b.color);
    new Chart(document.getElementById(id), {{
      type: 'bar',
      data: {{ labels, datasets: [
        {{ label: '_spacer', data: spacers,
           backgroundColor: 'transparent', borderColor: 'transparent', stack: 's' }},
        {{ label: 'value',   data: values,
           backgroundColor: colors, borderRadius: 3, stack: 's',
           borderColor: colors.map(c => c.replace('cc','')),
           borderWidth: 1 }},
      ] }},
      plugins: [{{
        id: 'wfLabels',
        afterDatasetsDraw(chart) {{
          const {{ ctx, data }} = chart;
          const metaV = chart.getDatasetMeta(1);
          ctx.save();
          ctx.font = 'bold 10px -apple-system, sans-serif';
          ctx.textAlign = 'center';
          metaV.data.forEach((bar, i) => {{
            const contrib = bars[i].contrib;
            if (contrib === null || contrib === undefined) return;
            const lbl = (contrib > 0 ? '+' : '') + contrib.toFixed(1) + 'pp';
            ctx.fillStyle = bars[i].isAnchor ? '#555' : (contrib >= 0 ? '#2d7d2d' : '#b71c1c');
            ctx.textBaseline = 'bottom';
            ctx.fillText(lbl, bar.x, bar.y - 3);
          }});
          ctx.restore();
        }}
      }}],
      options: {{
        responsive: true, maintainAspectRatio: false,
        layout: {{ padding: {{ top: 22 }} }},
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: ctx => {{
                if (ctx.datasetIndex === 0) return null;
                const b = bars[ctx.dataIndex];
                if (b.isAnchor) return ` NPS: ${{b.bar.toFixed(1)}}`;
                const lines = [` Impacto: ${{(b.contrib>=0?'+':'')}}${{b.contrib.toFixed(2)}}pp`];
                if (b.nps !== undefined) lines.push(` NPS CDU: ${{b.nps}}  Target processo: ${{b.target_proc ?? b.target}}`);
                if (b.weight !== undefined) lines.push(` Peso no processo: ${{b.weight}}%`);
                if (b.nps_m1 !== undefined) lines.push(` ${{b.nps_m1}} (atual) vs ${{b.nps_m0}} (ant.)`);
                return lines;
              }}
            }}
          }}
        }},
        scales: {{
          x: {{ stacked: true, grid: {{ display: false }},
                ticks: {{ font: {{ size: 10 }}, maxRotation: 30 }} }},
          y: {{ stacked: true,
                grid: {{ color: '#f0f2f5' }},
                ticks: {{ font: {{ size: 11 }}, callback: v => v.toFixed(0) }} }}
        }}
      }}
    }});
  }}

  waterfallChart('cWtf',     {jd(wtf)});
  waterfallChart('cCascade', {jd(casc)});

  // helper: linha de evolução + target tracejado
  function npsEvoChart(id, labels, npsVals, targetVal) {{
    const tgtData = labels.map(() => targetVal);
    const ptColors = npsVals.map(v => npsColor(v));
    new Chart(document.getElementById(id), {{
      type: 'line',
      data: {{ labels, datasets: [
        {{
          label: 'NPS Lineal',
          data: npsVals,
          borderColor: '#4472C4',
          backgroundColor: 'rgba(68,114,196,0.07)',
          pointBackgroundColor: ptColors,
          pointBorderColor: ptColors,
          pointRadius: 6,
          pointHoverRadius: 8,
          borderWidth: 2.5,
          tension: 0.3,
          fill: true,
          spanGaps: true,
          order: 1,
        }},
        {{
          label: 'Target',
          data: tgtData,
          borderColor: '#E05252',
          borderDash: [6, 4],
          borderWidth: 2,
          pointRadius: 0,
          fill: false,
          spanGaps: true,
          order: 2,
        }},
      ] }},
      plugins: [{{
        id: 'npsEvoLabels',
        afterDatasetsDraw(chart) {{
          const {{ ctx, data }} = chart;
          const meta = chart.getDatasetMeta(0);
          ctx.save();
          ctx.font = 'bold 11px -apple-system, sans-serif';
          ctx.textAlign = 'center';
          meta.data.forEach((pt, i) => {{
            const v = data.datasets[0].data[i];
            if (v === null || v === undefined) return;
            ctx.fillStyle = ptColors[i];
            ctx.textBaseline = 'bottom';
            ctx.fillText((v>0?'+':'') + v, pt.x, pt.y - 8);
          }});
          ctx.restore();
        }}
      }}],
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        layout: {{ padding: {{ top: 28 }} }},
        plugins: {{
          legend: {{ position: 'bottom', labels: {{ boxWidth: 14, padding: 10, font: {{ size: 11 }} }} }},
          tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label === 'Target'
            ? ` Target: ${{ctx.parsed.y}}`
            : ` NPS: ${{(ctx.parsed.y>0?'+':'')}}${{ctx.parsed.y}}` }} }}
        }},
        scales: {{
          x: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 11 }} }} }},
          y: {{
            grid: {{ color: ctx => ctx.tick.value === 0 ? '#aaa' : '#f0f2f5' }},
            ticks: {{ callback: v => (v>0?'+':'') + v, font: {{ size: 11 }} }}
          }}
        }}
      }}
    }});
  }}

  npsEvoChart('cNpsMon', {jd(monthly['months'])}, {jd(nps_monthly['monthly_nps'])}, {jd(avg_target)});
  npsEvoChart('cNpsWk',  {jd(weekly['weeks'])},   {jd(nps_weekly)}, {jd(avg_target)});

  // Combo Outgoing + NPS por CDU (cards de detratores)
  function detCombo(id, combo) {{
    if (!document.getElementById(id) || !combo) return;
    const ptC = combo.nps.map(v => npsColor(v));
    new Chart(document.getElementById(id), {{
      type: 'bar',
      data: {{ labels: combo.labels, datasets: [
        {{
          type: 'bar',
          label: 'Outgoing',
          data: combo.og,
          backgroundColor: 'rgba(68,114,196,0.25)',
          borderColor: '#4472C4',
          borderWidth: 1.5,
          borderRadius: 4,
          yAxisID: 'yOg',
          order: 2,
        }},
        {{
          type: 'line',
          label: 'NPS',
          data: combo.nps,
          borderColor: '#1a1a2e',
          pointBackgroundColor: ptC,
          pointBorderColor: ptC,
          pointRadius: 5,
          borderWidth: 2,
          tension: 0.3,
          yAxisID: 'yNps',
          spanGaps: true,
          order: 1,
        }},
        {{
          type: 'line',
          label: 'Target',
          data: combo.labels.map(() => combo.target),
          borderColor: '#E05252',
          borderDash: [5,3],
          borderWidth: 1.5,
          pointRadius: 0,
          yAxisID: 'yNps',
          spanGaps: true,
          order: 3,
        }},
      ] }},
      plugins: [{{
        id: 'detNpsLabels',
        afterDatasetsDraw(chart) {{
          const {{ ctx, data }} = chart;
          const meta = chart.getDatasetMeta(1);
          ctx.save();
          ctx.font = 'bold 10px -apple-system, sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'bottom';
          meta.data.forEach((pt, i) => {{
            const v = data.datasets[1].data[i];
            if (v === null || v === undefined) return;
            ctx.fillStyle = ptC[i];
            ctx.fillText((v>0?'+':'')+v, pt.x, pt.y - 4);
          }});
          ctx.restore();
        }}
      }}],
      options: {{
        responsive: true, maintainAspectRatio: false,
        layout: {{ padding: {{ top: 18 }} }},
        plugins: {{
          legend: {{ position: 'bottom', labels: {{ boxWidth: 12, padding: 8, font: {{ size: 10 }} }} }},
          tooltip: {{ callbacks: {{ label: ctx =>
            ctx.dataset.label === 'Outgoing'
              ? ` Outgoing: ${{ctx.parsed.y.toLocaleString('pt-BR')}}`
              : ` ${{ctx.dataset.label}}: ${{(ctx.parsed.y>0?'+':'')+ctx.parsed.y}}`
          }} }}
        }},
        scales: {{
          x: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 10 }} }} }},
          yOg: {{ position: 'left', grid: {{ color: '#f0f2f5' }},
                  ticks: {{ font: {{ size: 9 }}, callback: v => v.toLocaleString('pt-BR') }} }},
          yNps: {{ position: 'right', grid: {{ display: false }},
                   ticks: {{ font: {{ size: 9 }}, callback: v => (v>0?'+':'')+v }},
                   suggestedMin: combo.target ? combo.target - 30 : undefined }}
        }}
      }}
    }});
  }}

  detCombo('cDetWorst',  {jd(combo_worst)});
  detCombo('cDetTopOg',  {jd(combo_top_og)});

}}

// ── Transcriptions ────────────────────────────────────────────────────────────
function buildCard(t, i) {{
  const c = ACCENT[i % ACCENT.length];
  const chips = (t.case_ids||[]).map(id=>`<span class="case-chip">#${{id}}</span>`).join('');
  return `<div class="theme-card" style="border-left-color:${{c}}">
    <div class="tc-header">
      <span class="tc-name">${{t.name}}</span>
      <span class="tc-badge" style="background:${{c}}22;color:${{c}}">${{t.pct}}% dos casos</span>
    </div>
    <p class="tc-summary">${{t.summary}}</p>
    <div class="tc-chips">${{chips}}</div>
  </div>`;
}}

function selectCDU(cdu) {{
  const themes = ALL_THEMES[cdu] || [];
  const el = document.getElementById('themesBox');
  if (!themes.length) {{
    el.innerHTML = '<div class="no-data-block"><span class="no-data-icon">🔒</span><div><strong>Análise de transcrições indisponível</strong><br>Sem acesso à tabela BT_CX_TRANSCRIPT. Adicione temas curados manualmente no script para habilitar esta seção.</div></div>';
  }} else {{
    el.innerHTML = '<div class="themes-list">'+themes.map((t,i)=>buildCard(t,i)).join('')+'</div>';
  }}
}}
</script>
</body>
</html>"""

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    html_only = "--html-only" in sys.argv
    try:
        monthly, weekly, daily, themes_by_cdu, solutions, nps_by_cdu, nps_monthly, nps_weekly, nps_daily, nps_weekly_by_cdu, waterfalls, mom_scorecard, detractor_analysis = build_all(html_only=html_only)
        html = generate_html(monthly, weekly, daily, themes_by_cdu, solutions, nps_by_cdu, nps_monthly, nps_weekly, nps_daily, nps_weekly_by_cdu, waterfalls, mom_scorecard, detractor_analysis)
        out  = "outgoing_drivers_analysis.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n✓ Gerado: {out}")
    except Exception as e:
        print(f"\nERRO: {e}")
        raise
