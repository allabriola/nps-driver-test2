#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_outgoing_cdu.py
Volume Outgoing por CDU — Facturación e Emissão de Nota Fiscal (MLB)

Gera HTML com:
  • Aba 1: Facturación
  • Aba 2: Emissão de Nota Fiscal
  Cada aba: gráfico mensal (Jan–Mai), gráfico semanal (8 semanas),
             destaque top CDU + tabela de ranking, análise de transcrições
"""
import sys, json, re, os
sys.stdout.reconfigure(encoding="utf-8")

from google.cloud import bigquery
from collections import Counter
from datetime import date, timedelta

# ── Configuração ────────────────────────────────────────────────────────────
PROJECT   = "meli-bi-data"
SITE      = "MLB"
TOP_CDUS  = 8   # máximo de CDUs mostrados nos gráficos

# Chave = CX_PR_NAME_HSP em LK_CX_PROCESS_ADM | Valor = label exibido no HTML
PROCESSES = {
    "Facturación":            "Facturación",
    "Emision de Nota Fiscal": "Emissão de Nota Fiscal",
}

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
OUTROS_COLOR = "#BBBBBB"

STOPWORDS = set("""
de da do que em para com um uma os as o a e é se não por mais ele ela
nao na no ao dos das me você oi ola sim bom dia boa tarde noite obrigado
obrigada ok isso este esta esse essa meu minha seu sua foi ser ter estou
esta tenho preciso posso pode como quando onde qual quais aqui ja mais
mas ou pois ate sobre mesmo tambem agora ainda depois antes entao porque
pelo pela pelos pelas hello hi the and for are this that with vendedor
comprador mercado livre meli suporte atendimento conta xxx xx x null none
true false nbsp ola oi nao nps vou temos voce vc eles elas nos vos
sendo sendo tendo fazendo
""".split())

# ── BigQuery client ─────────────────────────────────────────────────────────
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

# ── Queries ─────────────────────────────────────────────────────────────────
# Fonte principal: DM_CX_OUTGOING_GESTION_DETAIL (tabela oficial de outgoing)
# Transcrições: BT_CX_TRANSCRIPT via CAS_CASE_ID de BT_CX_CASE_INTERACTION

TABLE_OG = f"`{PROJECT}.WHOWNER.DM_CX_OUTGOING_GESTION_DETAIL`"
TABLE_CI = f"`{PROJECT}.WHOWNER.BT_CX_CASE_INTERACTION`"
TABLE_TR = f"`{PROJECT}.WHOWNER.BT_CX_TRANSCRIPT`"

EVENT_FILTER = "CI_EVENT_NAME IN ('OUTGOING_CONTACT','OUTGOING_FIRST_CONTACT')"
CDU_EXPR     = "COALESCE(NULLIF(CDU,''), 'Sem CDU')"

def q_monthly() -> str:
    procs = "','".join(PROCESSES)
    return f"""
    SELECT
      FORMAT_DATE('%Y-%m', OUTGOING_DATE)   AS month,
      PRO_PROCESS_NAME                      AS process,
      {CDU_EXPR}                            AS cdu,
      SUM(CANT_OUTGOING)                    AS volume
    FROM {TABLE_OG}
    WHERE SIT_SITE_ID       = '{SITE}'
      AND {EVENT_FILTER}
      AND PRO_PROCESS_NAME  IN ('{procs}')
      AND OUTGOING_DATE BETWEEN '{START_YEAR}' AND '{TODAY}'
    GROUP BY 1, 2, 3
    ORDER BY 1, 2, 4 DESC
    """

def q_weekly() -> str:
    procs = "','".join(PROCESSES)
    return f"""
    SELECT
      DATE_TRUNC(OUTGOING_DATE, ISOWEEK)    AS week_start,
      PRO_PROCESS_NAME                      AS process,
      {CDU_EXPR}                            AS cdu,
      SUM(CANT_OUTGOING)                    AS volume
    FROM {TABLE_OG}
    WHERE SIT_SITE_ID       = '{SITE}'
      AND {EVENT_FILTER}
      AND PRO_PROCESS_NAME  IN ('{procs}')
      AND OUTGOING_DATE >= '{EIGHT_WEEKS_AGO}'
    GROUP BY 1, 2, 3
    ORDER BY 1, 2, 4 DESC
    """

def q_case_ids(process: str, cdu: str) -> str:
    """Case IDs via BT_CX_CASE_INTERACTION filtrado pelo SOLUTION_ID do CDU."""
    cutoff    = TODAY - timedelta(days=TRANSCRIPT_DAYS)
    cdu_safe  = cdu.replace("'", "''")
    proc_safe = process.replace("'", "''")
    return f"""
    SELECT DISTINCT i.CAS_CASE_ID
    FROM {TABLE_CI} i
    WHERE i.SIT_SITE_ID          = '{SITE}'
      AND i.FLAG_OUTGOING_GESTION = 1
      AND i.CI_PROCESS_ID IN (
          SELECT DISTINCT CI_PROCESS_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID = '{SITE}' AND PRO_PROCESS_NAME = '{proc_safe}'
      )
      AND i.WCM_CONT_ID IN (
          SELECT DISTINCT SOLUTION_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID = '{SITE}'
            AND PRO_PROCESS_NAME = '{proc_safe}'
            AND {CDU_EXPR} = '{cdu_safe}'
      )
      AND CAST(i.CI_CREATED_DATE AS DATE) >= '{cutoff}'
    LIMIT 1000
    """

def q_sample_cases(process: str, cdu: str, n: int = 8) -> str:
    """Retorna exemplos recentes de CAS_CASE_ID + data para exibir no HTML."""
    cutoff    = TODAY - timedelta(days=60)
    cdu_safe  = cdu.replace("'", "''")
    proc_safe = process.replace("'", "''")
    return f"""
    SELECT
      CAST(i.CAS_CASE_ID AS STRING) AS case_id,
      CAST(i.CI_CREATED_DATE AS DATE) AS date
    FROM {TABLE_CI} i
    WHERE i.SIT_SITE_ID          = '{SITE}'
      AND i.FLAG_OUTGOING_GESTION = 1
      AND i.CI_PROCESS_ID IN (
          SELECT DISTINCT CI_PROCESS_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID = '{SITE}' AND PRO_PROCESS_NAME = '{proc_safe}'
      )
      AND i.WCM_CONT_ID IN (
          SELECT DISTINCT SOLUTION_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID = '{SITE}'
            AND PRO_PROCESS_NAME = '{proc_safe}'
            AND {CDU_EXPR} = '{cdu_safe}'
      )
      AND CAST(i.CI_CREATED_DATE AS DATE) >= '{cutoff}'
    ORDER BY i.CI_CREATED_DATE DESC
    LIMIT {n}
    """

def q_transcripts_with_case(case_ids: list[str]) -> str:
    ids = ",".join(case_ids)
    return f"""
    SELECT
      CAST(CAS_CASE_ID AS STRING)    AS case_id,
      OBFUSCATED_MESSAGE_CONTENT     AS msg
    FROM {TABLE_TR}
    WHERE CAS_CASE_ID IN ({ids})
      AND OBFUSCATED_MESSAGE_CONTENT IS NOT NULL
      AND LENGTH(OBFUSCATED_MESSAGE_CONTENT) > 20
    """

# ── Temas curados manualmente (análise de 40 casos por CDU) ─────────────────
# Chave: (proc_key, top_cdu)
CURATED_THEMES: dict[tuple[str, str], list[dict]] = {
    ("Facturación", "Dudas sobre cargos facturados"): [
        {
            "name": "Débito automático de fatura vencida",
            "pct": 35,
            "case_ids": ["450596238", "450254304", "453189041"],
            "summary": (
                "Sellers são surpreendidos com débito automático de faturas vencidas do "
                "Mercado Livre descontado do saldo em conta, sem reconhecer a origem do valor."
            ),
        },
        {
            "name": "Cobrança de publicidade — Mercado Ads",
            "pct": 25,
            "case_ids": ["449223681", "450388418", "438822396"],
            "summary": (
                "Sellers questionam cobranças de campanhas de publicidade (Display Ads, "
                "Product Ads), frequentemente por não reconhecerem a tarifa ou acreditarem "
                "estar em período de teste gratuito."
            ),
        },
        {
            "name": "Tarifa cobrada em venda cancelada ou devolvida",
            "pct": 20,
            "case_ids": ["448026895", "447986958", "436559907"],
            "summary": (
                "Sellers solicitam estorno de tarifas cobradas sobre vendas canceladas ou "
                "com devolução, esperando que o valor seja revertido automaticamente após o cancelamento."
            ),
        },
        {
            "name": '"Minha Página" — cobrança não reconhecida',
            "pct": 10,
            "case_ids": ["438951678", "451099545", "436543608"],
            "summary": (
                "Sellers contestam a tarifa de manutenção da 'Minha Página', afirmando não "
                "ter contratado o serviço. Alguns relatam suspeita de uso indevido ou invasão da conta."
            ),
        },
        {
            "name": "Interpretação e reconciliação de fatura",
            "pct": 10,
            "case_ids": ["450135341", "436722229", "447448743"],
            "summary": (
                "Sellers solicitam detalhamento dos itens da fatura para conciliação financeira, "
                "com dúvidas sobre divergências entre o valor faturado e o esperado no período."
            ),
        },
    ],
    ("Emision de Nota Fiscal", "Faturador MeLi"): [
        {
            "name": "Bloqueio na emissão — NF pendente impede envio",
            "pct": 30,
            "case_ids": ["449061727", "451571088", "452567701"],
            "summary": (
                "Sellers não conseguem emitir NF-e e o envio fica bloqueado. Causas frequentes: "
                "pendências no SEFAZ, série não exclusiva para o ML ou instabilidade no sistema fiscal."
            ),
        },
        {
            "name": "Credenciamento e dados fiscais incorretos",
            "pct": 25,
            "case_ids": ["449585495", "448557710", "452942438"],
            "summary": (
                "Sellers têm emissão bloqueada por Inscrição Estadual incorreta, CNPJ não "
                "credenciado no SEFAZ ou dados fiscais desatualizados na conta do Mercado Livre."
            ),
        },
        {
            "name": "Erros de configuração da NF-e (quantidade, NCM, CFOP)",
            "pct": 20,
            "case_ids": ["439223431", "442031708", "450379451"],
            "summary": (
                "Sellers relatam discrepâncias entre a NF emitida e o produto real: "
                "quantidade divergente, NCM ausente ou CFOP inválido para operação interestadual."
            ),
        },
        {
            "name": "Vendas não aparecem no painel para emissão",
            "pct": 15,
            "case_ids": ["447058713", "436230190", "449061727"],
            "summary": (
                "Sellers relatam que vendas não aparecem na listagem de NF-e pendentes, "
                "impedindo a emissão em massa. Em alguns casos causado por filtro ativo no painel."
            ),
        },
        {
            "name": "Primeiros passos — novo vendedor sem histórico de emissão",
            "pct": 10,
            "case_ids": ["448868937", "452942438", "454506635"],
            "summary": (
                "Sellers novos ou sem experiência buscam orientação completa: como habilitar "
                "o Faturador MeLi, requisitos legais (PJ, certificado A1) e como emitir a primeira NF-e."
            ),
        },
    ],
}

# ── Theme analysis via TF-IDF + KMeans ──────────────────────────────────────
def analyze_themes(
    case_transcripts: dict[str, list[str]],
    top_cdu: str,
    proc_label: str,
    total_cases: int,
    n_themes: int = 5,
) -> list[dict]:
    """Clusteriza transcrições em temas usando TF-IDF + KMeans (sem API externa)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    import numpy as np

    case_list = list(case_transcripts.items())[:300]
    case_ids  = [c[0] for c in case_list]

    # Texto por caso: até 4 mensagens, limpar e normalizar
    texts = []
    for _, msgs in case_list:
        combined = " ".join(m.strip() for m in msgs[:4])
        combined = re.sub(r"[^a-záéíóúàâêôãõç\s]", " ", combined.lower())
        combined = re.sub(r"\s+", " ", combined).strip()
        texts.append(combined)

    n = min(n_themes, len(texts))
    if n < 2:
        return []

    # TF-IDF com bigramas, ignorando stopwords do projeto
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

        # Top termos do centróide (excluindo stopwords curtos)
        center   = km.cluster_centers_[cid]
        top_idx  = center.argsort()[-15:][::-1]
        top_terms = [feat[i] for i in top_idx
                     if feat[i] not in STOPWORDS and len(feat[i]) >= 4]

        bigrams   = [t for t in top_terms if " " in t][:3]
        unigrams  = [t for t in top_terms if " " not in t][:4]

        # Nome do tema: preferir bigramas (mais descritivos)
        name_parts = (bigrams[:2] + unigrams[:2]) if bigrams else unigrams[:3]
        name = " · ".join(name_parts[:3]).title()

        # Resumo baseado nos termos dominantes
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

# ── Data processing ──────────────────────────────────────────────────────────
def month_label(ym: str) -> str:
    return MES_PT.get(ym.split("-")[1], ym)

SEM_CDU = "Sem CDU"

def _build_datasets(top_cdus, by_cdu, keys, sem_cdu_data, all_rows, key_field):
    """Monta datasets: top CDUs com CDU real + 'Sem CDU' + 'Outros' ao final."""
    datasets = []
    for cdu in top_cdus:
        datasets.append({"label": cdu,
                         "data": [by_cdu.get(cdu, {}).get(k, 0) for k in keys]})
    # "Sem CDU" como faixa dedicada
    if any(v > 0 for v in sem_cdu_data):
        datasets.append({"label": SEM_CDU, "data": sem_cdu_data})
    # "Outros" = com CDU mas fora do top N
    outros = [
        sum(r["volume"] for r in all_rows if r[key_field] == k
            and r["cdu"] not in top_cdus and r["cdu"] != SEM_CDU)
        for k in keys
    ]
    if any(v > 0 for v in outros):
        datasets.append({"label": "Outros", "data": outros})
    return datasets

def process_monthly(raw: list[dict]) -> dict:
    result = {}
    for proc_key in PROCESSES:
        rows = [r for r in raw if r["process"] == proc_key]
        months_sorted = sorted(set(r["month"] for r in rows))

        cdu_totals: Counter = Counter()
        by_cdu: dict = {}
        for r in rows:
            cdu = r["cdu"]
            cdu_totals[cdu] += r["volume"]
            by_cdu.setdefault(cdu, {})[r["month"]] = r["volume"]

        # top CDUs excluindo "Sem CDU" (vai como faixa separada)
        top_cdus = [c for c, _ in cdu_totals.most_common()
                    if c != SEM_CDU][:TOP_CDUS]
        top_cdu  = top_cdus[0] if top_cdus else None

        sem_cdu_data = [by_cdu.get(SEM_CDU, {}).get(m, 0) for m in months_sorted]
        datasets = _build_datasets(top_cdus, by_cdu, months_sorted,
                                   sem_cdu_data, rows, "month")

        result[proc_key] = {
            "months":     [month_label(m) for m in months_sorted],
            "top_cdus":   top_cdus,
            "top_cdu":    top_cdu,
            "datasets":   datasets,
            "cdu_totals": {k: v for k, v in cdu_totals.items() if k != SEM_CDU},
            "sem_cdu_vol": cdu_totals.get(SEM_CDU, 0),
            "total_vol":   sum(cdu_totals.values()),
        }
    return result

def process_weekly(raw: list[dict]) -> dict:
    result = {}
    for proc_key in PROCESSES:
        rows = [r for r in raw if r["process"] == proc_key]
        weeks_sorted = sorted(set(r["week_start"] for r in rows))
        weeks_labels = [w.strftime("%d/%m") for w in weeks_sorted]

        cdu_totals: Counter = Counter()
        by_cdu: dict = {}
        for r in rows:
            cdu = r["cdu"]
            cdu_totals[cdu] += r["volume"]
            by_cdu.setdefault(cdu, {})[r["week_start"]] = r["volume"]

        top_cdus = [c for c, _ in cdu_totals.most_common()
                    if c != SEM_CDU][:TOP_CDUS]

        sem_cdu_data = [by_cdu.get(SEM_CDU, {}).get(w, 0) for w in weeks_sorted]
        datasets = _build_datasets(top_cdus, by_cdu, weeks_sorted,
                                   sem_cdu_data, rows, "week_start")

        result[proc_key] = {
            "weeks":    weeks_labels,
            "top_cdus": top_cdus,
            "datasets": datasets,
        }
    return result

CACHE_MAX_AGE_H = 24  # horas antes de re-consultar o BQ

def _cache_path(proc_key: str) -> str:
    safe = proc_key.replace(" ", "_").replace("/", "_")
    return f"_tr_cache_{safe}.json"

def _load_cache(proc_key: str) -> dict | None:
    import time as _t
    path = _cache_path(proc_key)
    if not os.path.exists(path):
        return None
    age_h = (_t.time() - os.path.getmtime(path)) / 3600
    if age_h > CACHE_MAX_AGE_H:
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    print(f"   [cache] carregado de {path} ({age_h:.1f}h atrás)")
    return data

def _save_cache(proc_key: str, data: dict) -> None:
    path = _cache_path(proc_key)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"   [cache] salvo em {path}")

def fetch_analysis(proc_key: str, top_cdu: str) -> list[dict]:
    """Retorna lista de temas para o top CDU.
    Prioridade: 1) temas curados manualmente, 2) TF-IDF+KMeans do cache."""
    if not top_cdu:
        return []

    # 1) Temas curados — retorna imediatamente, sem precisar do BQ
    curated = CURATED_THEMES.get((proc_key, top_cdu))
    if curated:
        print(f"   [curado] usando {len(curated)} temas manuais para '{top_cdu}'")
        return curated

    # Tenta carregar transcrições do cache
    cached = _load_cache(proc_key)
    if cached is None:
        print(f"   Buscando case IDs para '{top_cdu}'…")
        raw_ids = run(q_case_ids(proc_key, top_cdu))
        ids = [str(int(r["CAS_CASE_ID"])) for r in raw_ids if r.get("CAS_CASE_ID") is not None]
        if not ids:
            print("   Nenhum case ID encontrado.")
            return []

        print(f"   {len(ids)} casos. Buscando transcrições…")
        case_transcripts: dict[str, list[str]] = {}
        try:
            for i in range(0, len(ids), 1000):
                batch = ids[i:i + 1000]
                rows  = run(q_transcripts_with_case(batch))
                for r in rows:
                    cid = r.get("case_id")
                    msg = r.get("msg")
                    if cid and msg:
                        case_transcripts.setdefault(cid, []).append(msg)
            _save_cache(proc_key, case_transcripts)
        except Exception as e:
            print(f"   [aviso] erro ao buscar transcrições: {e}")
            print("   HTML gerado sem análise temática (rode novamente quando quota resetar).")
            return []
    else:
        case_transcripts = cached

    print(f"   {len(case_transcripts)} casos com transcrição. Clusterizando…")
    proc_label = PROCESSES[proc_key]
    themes = analyze_themes(case_transcripts, top_cdu, proc_label, len(case_transcripts))
    print(f"   {len(themes)} temas identificados.")
    return themes

def build_all():
    print("▸ Volume mensal…")
    monthly_raw = run(q_monthly())
    print("▸ Volume semanal (8 semanas)…")
    weekly_raw  = run(q_weekly())

    monthly = process_monthly(monthly_raw)
    weekly  = process_weekly(weekly_raw)

    # Para cada processo, monta dict cdu → temas para todos os top CDUs
    themes_by_cdu: dict[str, dict[str, list]] = {}
    for proc_key, proc_label in PROCESSES.items():
        top_cdus = monthly[proc_key]["top_cdus"]
        top_cdu  = monthly[proc_key]["top_cdu"]
        themes_by_cdu[proc_key] = {}

        for cdu in top_cdus:
            if cdu == top_cdu:
                # Análise completa (curada ou TF-IDF) só para o top CDU
                print(f"\n▸ Análise temática [{proc_label}] top CDU: {cdu}")
                themes_by_cdu[proc_key][cdu] = fetch_analysis(proc_key, cdu)
            else:
                # Para os demais, só usa temas curados se existirem (sem BQ)
                themes_by_cdu[proc_key][cdu] = CURATED_THEMES.get((proc_key, cdu), [])

    return monthly, weekly, themes_by_cdu

# ── HTML helpers ─────────────────────────────────────────────────────────────
def jd(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)

SEM_CDU_COLOR = "#D0D0D0"   # cinza claro — "Sem CDU"

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

ACCENT_COLORS = ["#4472C4", "#ED7D31", "#70AD47", "#E05252", "#9B59B6"]

def _render_theme_cards_html(themes: list[dict]) -> str:
    """Renderiza os cards de temas diretamente em HTML (sem JS)."""
    if not themes:
        return '<p class="no-data">Análise não disponível para este CDU — execute o script para gerar os temas.</p>'
    cards = ""
    for i, t in enumerate(themes):
        color  = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        chips  = "".join(f'<span class="case-chip">#{c}</span>' for c in t.get("case_ids", []))
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

def make_themes_section(idx: int, cdu_themes: dict[str, list], top_cdu: str) -> str:
    """Gera o card de análise com <select> de CDU.
    Conteúdo inicial renderizado em Python; trocas via JS."""
    options = "".join(
        f'<option value="{cdu}"{" selected" if cdu == top_cdu else ""}>{cdu}</option>'
        for cdu in cdu_themes
    )
    # Renderiza HTML inicial do top CDU diretamente (não depende de JS)
    initial_html = _render_theme_cards_html(cdu_themes.get(top_cdu, []))

    return f"""
    <div class="th-hdr">
      <div class="th-title-row">
        <span class="th-label">Análise de Transcrições · CDU:</span>
        <select class="cdu-sel" id="sel{idx}" onchange="selectCDU({idx},this.value)">
          {options}
        </select>
      </div>
      <span class="th-sub">Motivos de contato identificados (últimos {TRANSCRIPT_DAYS} dias)</span>
    </div>
    <div id="themes{idx}">{initial_html}</div>"""

def make_tab(idx: int, proc_key: str, proc_label: str,
             monthly: dict, weekly: dict,
             cdu_themes: dict[str, list]) -> tuple[str, str]:
    """Returns (tab_html, chart_js_body)"""
    m  = monthly[proc_key]
    w  = weekly[proc_key]
    mi = f"cM{idx}"   # canvas id monthly
    wi = f"cW{idx}"   # canvas id weekly
    active = "active" if idx == 0 else ""

    top_cdu   = m["top_cdu"] or "—"
    total_v   = m["total_vol"]           # inclui Sem CDU
    named_v   = sum(m["cdu_totals"].values())  # só com CDU identificado
    sem_cdu_v = m["sem_cdu_vol"]
    top_vol   = m["cdu_totals"].get(top_cdu, 0)
    top_pct   = f"{top_vol / total_v * 100:.1f}%" if total_v else "—"

    rows_html = ""
    for i, cdu in enumerate(m["top_cdus"][:8]):
        vol  = m["cdu_totals"].get(cdu, 0)
        pct  = f"{vol / total_v * 100:.1f}%" if total_v else "—"
        star = "⭐ " if i == 0 else f"{i+1}. "
        rc   = ' class="tr0"' if i == 0 else ""
        rows_html += (
            f'<tr{rc}><td>{star}{cdu}</td>'
            f'<td class="vn">{vol:,}</td>'
            f'<td class="vp">{pct}</td></tr>'
        )
    # linha Sem CDU ao final da tabela
    sem_pct = f"{sem_cdu_v / total_v * 100:.1f}%" if total_v else "—"
    rows_html += (
        f'<tr class="sem-cdu-row"><td>— Sem CDU</td>'
        f'<td class="vn">{sem_cdu_v:,}</td>'
        f'<td class="vp">{sem_pct}</td></tr>'
    )

    themes_html = make_themes_section(idx, cdu_themes, top_cdu)

    tab_html = f"""
  <div class="tab-pane {active}" id="tp{idx}">
    <div class="grid2">
      <div class="card chart-card">
        <p class="chart-title">Volume mensal por CDU</p>
        <div class="cw" style="height:320px"><canvas id="{mi}"></canvas></div>
      </div>
      <div class="card chart-card">
        <p class="chart-title">Volume semanal por CDU · últimas 8 semanas</p>
        <div class="cw" style="height:320px"><canvas id="{wi}"></canvas></div>
      </div>
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

    <div class="card">{themes_html}</div>
  </div>"""

    # Chart JS
    m_colors = palette_for(m["datasets"])
    m_ds = ",".join(
        f"{{label:{jd(ds['label'])},data:{jd(ds['data'])},"
        f"backgroundColor:{jd(m_colors[i])},borderRadius:4,stack:'s'}}"
        for i, ds in enumerate(m["datasets"])
    )
    w_colors = palette_for(w["datasets"])
    w_ds = ",".join(
        f"{{label:{jd(ds['label'])},data:{jd(ds['data'])},"
        f"backgroundColor:{jd(w_colors[i])},borderRadius:4,stack:'s'}}"
        for i, ds in enumerate(w["datasets"])
    )

    js = f"""
  initFns[{idx}] = function() {{
    bar('{mi}', {jd(m['months'])}, [{m_ds}]);
    bar('{wi}', {jd(w['weeks'])},  [{w_ds}]);
  }};"""

    return tab_html, js

# ── HTML template ─────────────────────────────────────────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:#f0f2f5;color:#1a1a2e;min-height:100vh}

/* ── Header ── */
.hd{background:linear-gradient(135deg,#ffe600,#f5c800);
    padding:14px 28px;display:flex;align-items:center;gap:14px;
    box-shadow:0 2px 8px rgba(0,0,0,.12)}
.logo{background:#1a1a2e;color:#ffe600;font-weight:900;font-size:13px;
      border-radius:7px;padding:5px 10px;letter-spacing:-.5px;line-height:1.2}
.hd h1{font-size:15px;font-weight:800;color:#1a1a2e}
.hd p{font-size:11px;color:#555;margin-top:2px}

/* ── Layout ── */
.main{max-width:1200px;margin:0 auto;padding:22px 18px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}

/* ── Tabs ── */
.tab-nav{display:flex;gap:3px;background:#fff;border-radius:10px;
         padding:4px;width:fit-content;margin-bottom:18px;
         box-shadow:0 1px 4px rgba(0,0,0,.08)}
.tab-btn{border:none;background:transparent;border-radius:7px;
         padding:8px 22px;font-size:13px;font-weight:600;color:#666;
         cursor:pointer;transition:all .15s}
.tab-btn.active{background:#ffe600;color:#1a1a2e;
                box-shadow:0 1px 4px rgba(0,0,0,.1)}
.tab-pane{display:none;flex-direction:column;gap:18px}
.tab-pane.active{display:flex}

/* ── Cards ── */
.card{background:#fff;border-radius:12px;padding:20px;
      box-shadow:0 1px 4px rgba(0,0,0,.07)}
.chart-card{}
.chart-title{font-size:12px;font-weight:700;color:#444;
             text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px}
.cw{position:relative}

/* ── Highlight card ── */
.hl-card{display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:start}
@media(max-width:680px){.hl-card{grid-template-columns:1fr}}
.hl-box{background:linear-gradient(135deg,#ffe600,#f5c800);border-radius:10px;
        padding:20px 24px;text-align:center;min-width:240px}
.hl-lbl{font-size:10px;font-weight:700;text-transform:uppercase;
        letter-spacing:1px;color:#666;margin-bottom:8px}
.hl-val{font-size:17px;font-weight:900;color:#1a1a2e;margin-bottom:6px;
        line-height:1.2}
.hl-sub{font-size:11px;color:#555}
.hl-sub2{font-size:10px;color:#888;margin-top:4px}

/* ── Ranking table ── */
.rtable{width:100%;border-collapse:collapse;font-size:12px}
.rtable th{background:#f8f9fa;padding:7px 12px;text-align:left;font-weight:700;
           color:#888;text-transform:uppercase;font-size:10px;letter-spacing:.6px;
           border-bottom:1px solid #eee}
.rtable td{padding:7px 12px;border-bottom:1px solid #f5f5f5;vertical-align:middle}
.rtable .tr0{background:#fffde7;font-weight:600}
.rtable .sem-cdu-row{color:#aaa;font-style:italic;border-top:1px solid #eee}
.hl-right{display:flex;flex-direction:column;gap:14px}
.vn{text-align:right;font-variant-numeric:tabular-nums}
.vp{text-align:right;color:#888}
/* ── Themes ── */
.no-data{font-size:12px;color:#999;padding:8px 0}
.th-hdr{margin-bottom:16px}
.th-title-row{display:flex;align-items:baseline;gap:6px;flex-wrap:wrap;margin-bottom:3px}
.th-label{font-size:13px;font-weight:700;white-space:nowrap}
.cdu-sel{font-size:14px;font-weight:800;color:#c89600;background:transparent;
         border:none;border-bottom:2px solid #e8b000;cursor:pointer;padding:0 4px 1px;
         outline:none;font-family:inherit;max-width:480px}
.cdu-sel:focus{border-bottom-color:#4472C4}
.cdu-sel option{color:#1a1a2e;font-weight:600;background:#fff}
.th-sub{font-size:11px;color:#888;display:block}
.themes-list{display:flex;flex-direction:column;gap:12px}
.theme-card{border-left:3px solid #ccc;padding:13px 16px;
            background:#fafafa;border-radius:0 8px 8px 0}
.tc-header{display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap}
.tc-name{font-size:13px;font-weight:700;color:#1a1a2e}
.tc-badge{font-size:11px;font-weight:700;padding:2px 10px;border-radius:20px;white-space:nowrap}
.tc-summary{font-size:12px;color:#555;line-height:1.55;margin-bottom:8px}
.tc-chips{display:flex;flex-wrap:wrap;gap:6px}
.case-chip{font-size:11px;font-family:monospace;background:#eef2ff;
           color:#4472C4;padding:2px 9px;border-radius:12px}
"""

def generate_html(monthly: dict, weekly: dict, themes_by_cdu: dict) -> str:
    now_str = TODAY.strftime("%d/%m/%Y")
    tab_btns  = []
    tab_panes = []
    chart_jss = []

    for idx, (proc_key, proc_label) in enumerate(PROCESSES.items()):
        active = "active" if idx == 0 else ""
        tab_btns.append(
            f'<button class="tab-btn {active}" onclick="go({idx})">{proc_label}</button>'
        )
        pane, js = make_tab(
            idx, proc_key, proc_label,
            monthly, weekly,
            themes_by_cdu.get(proc_key, {})
        )
        tab_panes.append(pane)
        chart_jss.append(js)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Volume Outgoing por CDU | Facturación &amp; Emissão NF | MLB</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>{CSS}</style>
</head>
<body>

<header class="hd">
  <div class="logo">ML</div>
  <div>
    <h1>Volume Outgoing por CDU — Facturación &amp; Emissão de Nota Fiscal</h1>
    <p>MLB · Jan–Mai 2026 · Fonte: DM_CX_OUTGOING_GESTION_DETAIL · Atualizado em {now_str}</p>
  </div>
</header>

<main class="main">
  <nav class="tab-nav">{''.join(tab_btns)}</nav>
  {''.join(tab_panes)}
</main>

<script>
const initFns = [];

function bar(id, labels, datasets) {{
  new Chart(document.getElementById(id), {{
    type: 'bar',
    data: {{ labels, datasets }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{
          position: 'bottom',
          labels: {{ boxWidth: 12, padding: 10, font: {{ size: 11 }} }}
        }},
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

function go(n) {{
  document.querySelectorAll('.tab-btn').forEach((b, i) =>
    b.classList.toggle('active', i === n));
  document.querySelectorAll('.tab-pane').forEach((p, i) =>
    p.classList.toggle('active', i === n));
  if (initFns[n]) {{ initFns[n](); initFns[n] = null; }}
}}

// ── CDU selector ──────────────────────────────────────────────────────────
const ACCENT = {jd(ACCENT_COLORS)};

const ALL_THEMES = {jd({str(i): {cdu: t for cdu, t in themes_by_cdu.get(proc_key, {}).items()}
    for i, proc_key in enumerate(PROCESSES)})};

function buildThemeCard(t, i) {{
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

function renderThemes(tabIdx, cdu) {{
  const themes = (ALL_THEMES[tabIdx]||{{}})[cdu] || [];
  const el = document.getElementById('themes'+tabIdx);
  if (!el) return;
  if (!themes.length) {{
    el.innerHTML = '<p class="no-data">Análise não disponível para este CDU — execute o script para gerar os temas.</p>';
  }} else {{
    el.innerHTML = '<div class="themes-list">'+themes.map((t,i)=>buildThemeCard(t,i)).join('')+'</div>';
  }}
}}

function selectCDU(tabIdx, cdu) {{ renderThemes(tabIdx, cdu); }}

{''.join(chart_jss)}

// Init aba 0 imediatamente
if (initFns[0]) {{ initFns[0](); initFns[0] = null; }}
</script>
</body>
</html>"""

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        monthly, weekly, themes_by_cdu = build_all()
        html = generate_html(monthly, weekly, themes_by_cdu)
        out  = "outgoing_cdu_analysis.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n✓ Gerado: {out}")
    except Exception as e:
        print(f"\nERRO: {e}")
        raise
