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
import sys, json, re
sys.stdout.reconfigure(encoding="utf-8")

from google.cloud import bigquery
from collections import Counter
from datetime import date, timedelta

# ── Configuração ────────────────────────────────────────────────────────────
PROJECT   = "meli-bi-data"
SITE      = "MLB"
CENTER    = "BR"
TOP_CDUS  = 8   # máximo de CDUs mostrados nos gráficos

PROCESSES = {
    "Facturación":          "Facturación",
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

def run(sql: str) -> list[dict]:
    return [dict(r) for r in client.query(sql).result()]

# ── Queries ─────────────────────────────────────────────────────────────────
def q_monthly() -> str:
    procs = "','".join(PROCESSES)
    return f"""
    SELECT
      SUBSTR(SURVEY_DATE_SURVEY, 1, 7)          AS month,
      PRO_PROCESS_NAME                          AS process,
      COALESCE(NULLIF(CDU, ''), 'Sem CDU')      AS cdu,
      COUNT(*)                                  AS volume
    FROM `{PROJECT}.WHOWNER.DM_CX_NPS_Y20_DETAIL`
    WHERE SIT_SITE_ID        = '{SITE}'
      AND SURVEY_CENTER      = '{CENTER}'
      AND PRO_PROCESS_NAME  IN ('{procs}')
      AND SURVEY_DATE_SURVEY BETWEEN '{START_YEAR}' AND '{TODAY}'
    GROUP BY 1, 2, 3
    ORDER BY 1, 2, 4 DESC
    """

def q_weekly() -> str:
    procs = "','".join(PROCESSES)
    return f"""
    SELECT
      DATE_TRUNC(PARSE_DATE('%Y-%m-%d', SURVEY_DATE_SURVEY), ISOWEEK) AS week_start,
      PRO_PROCESS_NAME                          AS process,
      COALESCE(NULLIF(CDU, ''), 'Sem CDU')      AS cdu,
      COUNT(*)                                  AS volume
    FROM `{PROJECT}.WHOWNER.DM_CX_NPS_Y20_DETAIL`
    WHERE SIT_SITE_ID        = '{SITE}'
      AND SURVEY_CENTER      = '{CENTER}'
      AND PRO_PROCESS_NAME  IN ('{procs}')
      AND SURVEY_DATE_SURVEY >= '{EIGHT_WEEKS_AGO}'
    GROUP BY 1, 2, 3
    ORDER BY 1, 2, 4 DESC
    """

def q_case_ids(process: str, cdu: str) -> str:
    cutoff = TODAY - timedelta(days=TRANSCRIPT_DAYS)
    cdu_safe = cdu.replace("'", "''")
    proc_safe = process.replace("'", "''")
    return f"""
    SELECT DISTINCT CAS_CASE_ID
    FROM `{PROJECT}.WHOWNER.DM_CX_NPS_Y20_DETAIL`
    WHERE SIT_SITE_ID        = '{SITE}'
      AND SURVEY_CENTER      = '{CENTER}'
      AND PRO_PROCESS_NAME   = '{proc_safe}'
      AND COALESCE(NULLIF(CDU, ''), 'Sem CDU') = '{cdu_safe}'
      AND SURVEY_DATE_SURVEY >= '{cutoff}'
    LIMIT 1000
    """

def q_transcripts(case_ids: list[str]) -> str:
    ids = ",".join(case_ids)  # CAS_CASE_ID is NUMERIC — no quotes
    return f"""
    SELECT OBFUSCATED_MESSAGE_CONTENT AS msg
    FROM `{PROJECT}.WHOWNER.BT_CX_TRANSCRIPT`
    WHERE CAS_CASE_ID IN ({ids})
      AND OBFUSCATED_MESSAGE_CONTENT IS NOT NULL
      AND LENGTH(OBFUSCATED_MESSAGE_CONTENT) > 15
    """

# ── Keyword extraction ───────────────────────────────────────────────────────
def extract_keywords(messages: list[str], top_n: int = 20) -> list[tuple[str, int]]:
    words: Counter = Counter()
    for msg in messages:
        txt = msg.lower()
        txt = re.sub(r"[^a-záéíóúàâêôãõç\s]", " ", txt)
        for w in txt.split():
            if len(w) >= 4 and w not in STOPWORDS:
                words[w] += 1
    return words.most_common(top_n)

# ── Data processing ──────────────────────────────────────────────────────────
def month_label(ym: str) -> str:
    return MES_PT.get(ym.split("-")[1], ym)

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

        top_cdus = [c for c, _ in cdu_totals.most_common(TOP_CDUS)]
        top_cdu  = top_cdus[0] if top_cdus else None

        datasets = []
        for cdu in top_cdus:
            datasets.append({"label": cdu,
                             "data": [by_cdu.get(cdu, {}).get(m, 0) for m in months_sorted]})

        outros = [
            sum(r["volume"] for r in rows if r["month"] == m) -
            sum(by_cdu.get(c, {}).get(m, 0) for c in top_cdus)
            for m in months_sorted
        ]
        if any(v > 0 for v in outros):
            datasets.append({"label": "Outros", "data": outros})

        result[proc_key] = {
            "months":    [month_label(m) for m in months_sorted],
            "top_cdus":  top_cdus,
            "top_cdu":   top_cdu,
            "datasets":  datasets,
            "cdu_totals": dict(cdu_totals),
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

        top_cdus = [c for c, _ in cdu_totals.most_common(TOP_CDUS)]

        datasets = []
        for cdu in top_cdus:
            datasets.append({"label": cdu,
                             "data": [by_cdu.get(cdu, {}).get(w, 0) for w in weeks_sorted]})

        outros = [
            sum(r["volume"] for r in rows if r["week_start"] == w) -
            sum(by_cdu.get(c, {}).get(w, 0) for c in top_cdus)
            for w in weeks_sorted
        ]
        if any(v > 0 for v in outros):
            datasets.append({"label": "Outros", "data": outros})

        result[proc_key] = {
            "weeks":    weeks_labels,
            "top_cdus": top_cdus,
            "datasets": datasets,
        }
    return result

def fetch_transcripts(proc_key: str, top_cdu: str) -> list[tuple[str, int]]:
    if not top_cdu:
        return []
    print(f"   Buscando case IDs para '{top_cdu}'…")
    ids = [str(int(r["CAS_CASE_ID"])) for r in run(q_case_ids(proc_key, top_cdu))
           if r.get("CAS_CASE_ID") is not None]
    if not ids:
        print("   Nenhum case ID encontrado.")
        return []
    print(f"   {len(ids)} casos. Buscando transcrições…")
    messages = []
    for i in range(0, len(ids), 1000):
        batch = ids[i:i + 1000]
        rows  = run(q_transcripts(batch))
        messages.extend(r["msg"] for r in rows if r.get("msg"))
    print(f"   {len(messages)} mensagens. Extraindo keywords…")
    return extract_keywords(messages, top_n=20)

def build_all():
    print("▸ Volume mensal…")
    monthly_raw = run(q_monthly())
    print("▸ Volume semanal (8 semanas)…")
    weekly_raw  = run(q_weekly())

    monthly = process_monthly(monthly_raw)
    weekly  = process_weekly(weekly_raw)

    keywords = {}
    for proc_key, proc_label in PROCESSES.items():
        top_cdu = monthly[proc_key]["top_cdu"]
        print(f"\n▸ Transcrições [{proc_label}] top CDU: {top_cdu}")
        keywords[proc_key] = fetch_transcripts(proc_key, top_cdu)

    return monthly, weekly, keywords

# ── HTML helpers ─────────────────────────────────────────────────────────────
def jd(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)

def palette_for(datasets: list[dict]) -> list[str]:
    out = []
    idx = 0
    for ds in datasets:
        if ds["label"] == "Outros":
            out.append(OUTROS_COLOR)
        else:
            out.append(PALETTE[idx % len(PALETTE)])
            idx += 1
    return out

def make_kw_html(kws: list[tuple[str, int]], top_cdu: str) -> str:
    if not kws:
        return '<p class="no-data">Sem dados de transcrição disponíveis.</p>'
    max_c = kws[0][1] if kws else 1
    items = "".join(
        f'<div class="kw-item">'
        f'<div class="kw-row"><span class="kw-word">{w}</span>'
        f'<span class="kw-cnt">{c:,}</span></div>'
        f'<div class="kw-bg"><div class="kw-fill" style="width:{int(c/max_c*100)}%"></div></div>'
        f'</div>'
        for w, c in kws
    )
    return (
        f'<div class="kw-hdr">'
        f'<span class="kw-title">Análise de Transcrições</span>'
        f'<span class="kw-sub"> · CDU: <strong>{top_cdu}</strong>'
        f' · palavras mais frequentes (últimos {TRANSCRIPT_DAYS} dias)</span>'
        f'</div>'
        f'<div class="kw-grid">{items}</div>'
    )

def make_tab(idx: int, proc_key: str, proc_label: str,
             monthly: dict, weekly: dict, kws: list) -> tuple[str, str]:
    """Returns (tab_html, chart_js_body)"""
    m  = monthly[proc_key]
    w  = weekly[proc_key]
    mi = f"cM{idx}"   # canvas id monthly
    wi = f"cW{idx}"   # canvas id weekly
    active = "active" if idx == 0 else ""

    top_cdu  = m["top_cdu"] or "—"
    total_v  = sum(m["cdu_totals"].values())
    top_vol  = m["cdu_totals"].get(top_cdu, 0)
    top_pct  = f"{top_vol / total_v * 100:.1f}%" if total_v else "—"

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

    kw_html = make_kw_html(kws, top_cdu)

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
        <div class="hl-sub">{top_vol:,} pesquisas · {top_pct} do total · {proc_label}</div>
      </div>
      <table class="rtable">
        <thead><tr><th>CDU</th><th>Volume</th><th>%</th></tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>

    <div class="card kw-card">{kw_html}</div>
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

/* ── Ranking table ── */
.rtable{width:100%;border-collapse:collapse;font-size:12px}
.rtable th{background:#f8f9fa;padding:7px 12px;text-align:left;font-weight:700;
           color:#888;text-transform:uppercase;font-size:10px;letter-spacing:.6px;
           border-bottom:1px solid #eee}
.rtable td{padding:7px 12px;border-bottom:1px solid #f5f5f5;vertical-align:middle}
.rtable .tr0{background:#fffde7;font-weight:600}
.vn{text-align:right;font-variant-numeric:tabular-nums}
.vp{text-align:right;color:#888}

/* ── Keywords ── */
.kw-hdr{margin-bottom:14px}
.kw-title{font-size:13px;font-weight:700}
.kw-sub{font-size:11px;color:#888}
.kw-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}
.kw-item{}
.kw-row{display:flex;justify-content:space-between;margin-bottom:3px}
.kw-word{font-size:12px;font-weight:600}
.kw-cnt{font-size:11px;color:#888;font-variant-numeric:tabular-nums}
.kw-bg{background:#f0f0f0;border-radius:3px;height:5px}
.kw-fill{background:#ffe600;border-radius:3px;height:5px}
.no-data{font-size:12px;color:#999}
"""

def generate_html(monthly: dict, weekly: dict, keywords: dict) -> str:
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
            monthly, weekly, keywords.get(proc_key, [])
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
    <p>MLB · Jan–Mai 2026 · Atualizado em {now_str}</p>
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
              ` ${{ctx.dataset.label}}: ${{ctx.parsed.y.toLocaleString('pt-BR')}} pesquisas`
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

{''.join(chart_jss)}

// Init aba 0 imediatamente
if (initFns[0]) {{ initFns[0](); initFns[0] = null; }}
</script>
</body>
</html>"""

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        monthly, weekly, keywords = build_all()
        html = generate_html(monthly, weekly, keywords)
        out  = "outgoing_cdu_analysis.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n✓ Gerado: {out}")
    except Exception as e:
        print(f"\nERRO: {e}")
        raise
