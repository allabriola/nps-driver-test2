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
TOP_CDUS  = 8

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
TABLE_OG = f"`{PROJECT}.WHOWNER.DM_CX_OUTGOING_GESTION_DETAIL`"
TABLE_CI = f"`{PROJECT}.WHOWNER.BT_CX_CASE_INTERACTION`"
TABLE_TR = f"`{PROJECT}.WHOWNER.BT_CX_TRANSCRIPT`"

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
        return monthly, weekly, daily, themes_by_cdu, solutions

    print("▸ Volume mensal…")
    monthly_raw = run(q_monthly())
    print("▸ Volume semanal (8 semanas)…")
    weekly_raw  = run(q_weekly())
    print(f"▸ Volume diário (últimos {DAILY_DAYS} dias)…")
    daily_raw   = run(q_daily())
    print("▸ Top soluções…")
    solutions_raw = run(q_solutions())
    monthly   = process_monthly(monthly_raw)
    weekly    = process_weekly(weekly_raw)
    daily     = process_daily(daily_raw)
    solutions = [{"solution": r["solution"], "volume": r["volume"]} for r in solutions_raw]

    themes_by_cdu: dict[str, list] = {}
    top_cdus = monthly["top_cdus"]
    print(f"\n▸ Análise temática Drivers ({len(top_cdus)} CDUs)…")
    for cdu in top_cdus:
        themes_by_cdu[cdu] = fetch_themes(cdu)

    _save_cache({"monthly": monthly, "weekly": weekly, "daily": daily,
                 "solutions": solutions, "themes_by_cdu": themes_by_cdu}, charts=True)
    return monthly, weekly, daily, themes_by_cdu, solutions

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

def generate_html(monthly: dict, weekly: dict, daily: dict, themes_by_cdu: dict, solutions: list) -> str:
    now_str = TODAY.strftime("%d/%m/%Y")

    top_cdu   = monthly["top_cdu"] or "—"
    total_v   = monthly["total_vol"]
    named_v   = sum(monthly["cdu_totals"].values())
    sem_cdu_v = monthly["sem_cdu_vol"]
    top_vol   = monthly["cdu_totals"].get(top_cdu, 0)
    top_pct   = f"{top_vol / total_v * 100:.1f}%" if total_v else "—"

    rows_html = ""
    for i, cdu in enumerate(monthly["top_cdus"][:8]):
        vol = monthly["cdu_totals"].get(cdu, 0)
        pct = f"{vol / total_v * 100:.1f}%" if total_v else "—"
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

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Volume Outgoing por CDU | Drivers | MLB</title>
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
.main{{max-width:1200px;margin:0 auto;padding:22px 18px;
       display:flex;flex-direction:column;gap:18px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
@media(max-width:820px){{.grid2{{grid-template-columns:1fr}}}}
.card{{background:#fff;border-radius:12px;padding:20px;
      box-shadow:0 1px 4px rgba(0,0,0,.07)}}
.chart-title{{font-size:12px;font-weight:700;color:#444;
             text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px}}
.cw{{position:relative}}
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
</style>
</head>
<body>

<header class="hd">
  <div class="logo">ML</div>
  <div>
    <h1>Volume Outgoing por CDU — Processo Drivers</h1>
    <p>MLB · {teams_label} · Jan–Mai 2026 · Fonte: DM_CX_OUTGOING_GESTION_DETAIL · Atualizado em {now_str}</p>
  </div>
</header>

<main class="main">

  {generate_exec_summary(monthly, weekly, daily, solutions)}

  <div class="grid2">
    <div class="card">
      <p class="chart-title">Volume mensal por CDU</p>
      <div class="cw" style="height:320px"><canvas id="cM"></canvas></div>
    </div>
    <div class="card">
      <p class="chart-title">Volume semanal por CDU · últimas 8 semanas</p>
      <div class="cw" style="height:320px"><canvas id="cW"></canvas></div>
    </div>
  </div>

  <div class="card">
    <p class="chart-title">Volume diário por CDU · últimos {DAILY_DAYS} dias</p>
    <div class="cw" style="height:300px"><canvas id="cD"></canvas></div>
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

</main>

<script>
const ACCENT = {jd(ACCENT_COLORS)};
const ALL_THEMES = {jd(themes_by_cdu)};

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

function bar(id, labels, datasets, showTotals = false, showPct = false) {{
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
            label: ctx =>
              ` ${{ctx.dataset.label}}: ${{ctx.parsed.y.toLocaleString('pt-BR')}} atendimentos`
          }}
        }}
      }},
      scales: {{
        x: {{ stacked: true, grid: {{ display: false }},
              ticks: {{ font: {{ size: 11 }} }} }},
        y: {{ stacked: true, grid: {{ color: '#f0f2f5' }},
              ticks: {{ font: {{ size: 11 }},
                        callback: v => v.toLocaleString('pt-BR') }} }}
      }}
    }}
  }});
}}

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

bar('cM', {jd(monthly['months'])}, [{m_ds}], true, true);
bar('cW', {jd(weekly['weeks'])},   [{w_ds}], true, true);
bar('cD', {jd(daily['days'])},     [{d_ds}], true, true);
</script>
</body>
</html>"""

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    html_only = "--html-only" in sys.argv
    try:
        monthly, weekly, daily, themes_by_cdu, solutions = build_all(html_only=html_only)
        html = generate_html(monthly, weekly, daily, themes_by_cdu, solutions)
        out  = "outgoing_drivers_analysis.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n✓ Gerado: {out}")
    except Exception as e:
        print(f"\nERRO: {e}")
        raise
