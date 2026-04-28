#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_driver_impact.py  v2
Single page: scorecards + waterfall charts (MoM | WoW | vs Target)
Gera: driver_impact.html
"""
import json
from datetime import datetime

# ─── METADATA ────────────────────────────────────────────────────────────────
M1_LABEL          = "Abril 2026"
M2_LABEL          = "Marco 2026"
S1_LABEL          = "20/abr - 26/abr"
S2_LABEL          = "13/abr - 19/abr"
NPS_TARGET_CONSOL = 52.22
REPORT_DATE       = datetime.now().strftime("%d/%m/%Y %H:%M")

# ─── CATEGORIAS ──────────────────────────────────────────────────────────────
_CATS = {
    "Longtail": [
        "Experiencia Impositiva Seller Dev", "ME Vendedor Seller Dev", "Partners",
        "PCF Vendedor Seller Dev", "Post Venta Seller Dev", "Publicaciones Seller Dev",
    ],
    "Mature": [
        "Experiencia Impositiva Mature", "ME Vendedor Mature", "PCF Vendedor Mature",
        "Post Venta Mature", "Publicaciones Mature",
    ],
    "Meli Pro": [
        "Experiencia Impositiva Meli Pro", "ME Vendedor Meli Pro", "PCF Vendedor Meli Pro",
        "Post Venta Meli Pro", "Publicaciones Meli Pro",
    ],
    "Buyers": [
        "CBT", "PDD DS&XD - Vendedor", "PDD FBM - Vendedor", "PDD Fotos - Vendedor",
        "PDD MP,FLEX & CBT - Vendedor", "PNR ME - Vendedor", "PNR MP - Vendedor",
    ],
    "FBM":      ["FBM-S Mature", "FBM-S Meli Pro", "FBM-S Seller Dev"],
    "Otros CV": ["Otros CV"],
}
CAT = {d: c for c, ds in _CATS.items() for d in ds}

# ─── TARGETS ─────────────────────────────────────────────────────────────────
DRIVER_TARGETS = {
    "CBT": 74.63,
    "Experiencia Impositiva Mature": 53.63,
    "Experiencia Impositiva Meli Pro": 38.57,
    "Experiencia Impositiva Seller Dev": 59.03,
    "FBM-S Mature": 19.60,
    "FBM-S Meli Pro": 48.70,
    "FBM-S Seller Dev": 42.07,
    "ME Vendedor Mature": 48.99,
    "ME Vendedor Meli Pro": 81.60,
    "ME Vendedor Seller Dev": 57.80,
    "Otros CV": 53.77,
    "PCF Vendedor Mature": 28.27,
    "PCF Vendedor Meli Pro": 63.57,
    "PCF Vendedor Seller Dev": 39.93,
    "PDD DS&XD - Vendedor": 16.40,
    "PDD FBM - Vendedor": 40.67,
    "PDD Fotos - Vendedor": 33.13,
    "PDD MP,FLEX & CBT - Vendedor": 12.33,
    "PNR ME - Vendedor": 27.23,
    "PNR MP - Vendedor": 29.57,
    "Partners": 70.19,
    "Post Venta Mature": 50.10,
    "Post Venta Meli Pro": 87.77,
    "Post Venta Seller Dev": 53.40,
    "Publicaciones Mature": 47.37,
    "Publicaciones Meli Pro": 81.43,
    "Publicaciones Seller Dev": 52.87,
}

# ─── DADOS ───────────────────────────────────────────────────────────────────
monthly_driver = {
    "CBT":                               {"M2": (323, 58, 395),    "M1": (306, 47, 359)},
    "Experiencia Impositiva Mature":     {"M2": (45, 20, 72),      "M1": (23, 7, 35)},
    "Experiencia Impositiva Meli Pro":   {"M2": (8, 4, 13),        "M1": (8, 1, 11)},
    "Experiencia Impositiva Seller Dev": {"M2": (312, 108, 469),   "M1": (364, 106, 519)},
    "FBM-S Mature":                      {"M2": (130, 45, 203),    "M1": (87, 25, 120)},
    "FBM-S Meli Pro":                    {"M2": (11, 8, 22),       "M1": (40, 8, 52)},
    "FBM-S Seller Dev":                  {"M2": (347, 125, 524),   "M1": (280, 95, 414)},
    "ME Vendedor Mature":                {"M2": (1618, 314, 2184), "M1": (916, 184, 1180)},
    "ME Vendedor Meli Pro":              {"M2": (60, 10, 75),      "M1": (210, 22, 241)},
    "ME Vendedor Seller Dev":            {"M2": (4958, 754, 6266), "M1": (4502, 642, 5654)},
    "Otros CV":                          {"M2": (775, 182, 1047),  "M1": (616, 209, 877)},
    "PCF Vendedor Mature":               {"M2": (332, 85, 467),    "M1": (202, 62, 294)},
    "PCF Vendedor Meli Pro":             {"M2": (32, 8, 44),       "M1": (181, 30, 240)},
    "PCF Vendedor Seller Dev":           {"M2": (536, 166, 790),   "M1": (324, 93, 466)},
    "PDD DS&XD - Vendedor":              {"M2": (645, 486, 1280),  "M1": (458, 355, 904)},
    "PDD FBM - Vendedor":                {"M2": (193, 89, 306),    "M1": (145, 79, 247)},
    "PDD Fotos - Vendedor":              {"M2": (46, 22, 72),      "M1": (30, 22, 56)},
    "PDD MP,FLEX & CBT - Vendedor":      {"M2": (87, 58, 166),     "M1": (52, 37, 101)},
    "PNR ME - Vendedor":                 {"M2": (103, 71, 193),    "M1": (117, 71, 202)},
    "PNR MP - Vendedor":                 {"M2": (140, 90, 266),    "M1": (136, 65, 217)},
    "Partners":                          {"M2": (2228, 337, 2806), "M1": (1867, 287, 2369)},
    "Post Venta Mature":                 {"M2": (392, 76, 520),    "M1": (259, 45, 335)},
    "Post Venta Meli Pro":               {"M2": (70, 10, 81),      "M1": (282, 8, 298)},
    "Post Venta Seller Dev":             {"M2": (929, 178, 1186),  "M1": (709, 99, 874)},
    "Publicaciones Mature":              {"M2": (258, 51, 345),    "M1": (167, 35, 235)},
    "Publicaciones Meli Pro":            {"M2": (18, 7, 26),       "M1": (104, 10, 119)},
    "Publicaciones Seller Dev":          {"M2": (2639, 374, 3309), "M1": (1765, 310, 2267)},
}

weekly_driver = {
    "CBT":                               {"S2": (87, 15, 102),    "S1": (75, 16, 94)},
    "Experiencia Impositiva Mature":     {"S2": (6, 2, 8),        "S1": (2, 0, 4)},
    "Experiencia Impositiva Meli Pro":   {"S2": (2, 1, 4),        "S1": (3, 0, 3)},
    "Experiencia Impositiva Seller Dev": {"S2": (112, 33, 160),   "S1": (57, 23, 88)},
    "FBM-S Mature":                      {"S2": (23, 4, 29),      "S1": (17, 4, 21)},
    "FBM-S Meli Pro":                    {"S2": (14, 6, 20),      "S1": (17, 0, 20)},
    "FBM-S Seller Dev":                  {"S2": (68, 24, 101),    "S1": (85, 29, 121)},
    "ME Vendedor Mature":                {"S2": (222, 44, 286),   "S1": (146, 34, 186)},
    "ME Vendedor Meli Pro":              {"S2": (76, 4, 83),      "S1": (104, 10, 120)},
    "ME Vendedor Seller Dev":            {"S2": (1154, 178, 1482),"S1": (1058, 152, 1308)},
    "Otros CV":                          {"S2": (158, 56, 230),   "S1": (181, 68, 258)},
    "PCF Vendedor Mature":               {"S2": (51, 19, 81),     "S1": (21, 9, 34)},
    "PCF Vendedor Meli Pro":             {"S2": (67, 12, 89),     "S1": (101, 14, 131)},
    "PCF Vendedor Seller Dev":           {"S2": (95, 28, 137),    "S1": (82, 30, 129)},
    "PDD DS&XD - Vendedor":              {"S2": (135, 107, 261),  "S1": (110, 71, 205)},
    "PDD FBM - Vendedor":                {"S2": (38, 25, 72),     "S1": (41, 24, 71)},
    "PDD Fotos - Vendedor":              {"S2": (8, 8, 17),       "S1": (10, 7, 19)},
    "PDD MP,FLEX & CBT - Vendedor":      {"S2": (21, 11, 39),     "S1": (8, 10, 19)},
    "PNR ME - Vendedor":                 {"S2": (23, 10, 37),     "S1": (59, 38, 103)},
    "PNR MP - Vendedor":                 {"S2": (32, 13, 49),     "S1": (27, 24, 54)},
    "Partners":                          {"S2": (575, 85, 725),   "S1": (567, 85, 719)},
    "Post Venta Mature":                 {"S2": (76, 11, 97),     "S1": (46, 6, 58)},
    "Post Venta Meli Pro":               {"S2": (104, 5, 112),    "S1": (149, 1, 152)},
    "Post Venta Seller Dev":             {"S2": (194, 23, 233),   "S1": (177, 18, 209)},
    "Publicaciones Mature":              {"S2": (37, 14, 57),     "S1": (25, 3, 30)},
    "Publicaciones Meli Pro":            {"S2": (37, 4, 44),      "S1": (59, 4, 64)},
    "Publicaciones Seller Dev":          {"S2": (453, 80, 587),   "S1": (398, 75, 511)},
}

# ─── CALCULOS ────────────────────────────────────────────────────────────────
def nps(p, d, s):
    return round(100.0 * (p - d) / s, 2) if s > 0 else None

def mix_neto(data, pa, pb, surv_a, surv_b, nps_b_tot):
    out = {}
    for drv, pd in data.items():
        a = pd.get(pa, (0, 0, 0))
        b = pd.get(pb, (0, 0, 0))
        na = nps(*a)
        nb = nps(*b)
        sha = a[2] / surv_a if surv_a else 0
        shb = b[2] / surv_b if surv_b else 0
        nt = round(sha * (nb - na), 2) if na is not None and nb is not None else 0.0
        mx = round((shb - sha) * (nb - nps_b_tot), 2) if nb is not None else 0.0
        out[drv] = dict(
            surv_a=a[2], nps_a=na, share_a=round(sha * 100, 1),
            surv_b=b[2], nps_b=nb, share_b=round(shb * 100, 1),
            neto=nt, mix=mx, var=round(nt + mx, 2),
        )
    return out

# Monthly
sM2  = sum(v["M2"][2] for v in monthly_driver.values())
sM1  = sum(v["M1"][2] for v in monthly_driver.values())
nM2  = nps(sum(v["M2"][0] for v in monthly_driver.values()),
           sum(v["M2"][1] for v in monthly_driver.values()), sM2)
nM1  = nps(sum(v["M1"][0] for v in monthly_driver.values()),
           sum(v["M1"][1] for v in monthly_driver.values()), sM1)
dM   = round(nM1 - nM2, 2)
mD   = mix_neto(monthly_driver, "M2", "M1", sM2, sM1, nM1)

# Weekly
sS2  = sum(v["S2"][2] for v in weekly_driver.values())
sS1  = sum(v["S1"][2] for v in weekly_driver.values())
nS2  = nps(sum(v["S2"][0] for v in weekly_driver.values()),
           sum(v["S2"][1] for v in weekly_driver.values()), sS2)
nS1  = nps(sum(v["S1"][0] for v in weekly_driver.values()),
           sum(v["S1"][1] for v in weekly_driver.values()), sS1)
dW   = round(nS1 - nS2, 2)
wD   = mix_neto(weekly_driver, "S2", "S1", sS2, sS1, nS1)

# vs Target — waterfall: theoretical_target -> drivers -> nM1
# theoretical_target = SUM(TARGET_driver * share_M1) — baseline if all hit target
theoretical_target = round(
    sum(DRIVER_TARGETS[drv] * (monthly_driver[drv]["M1"][2] / sM1) for drv in monthly_driver), 2
)
gap_consol = round(nM1 - NPS_TARGET_CONSOL, 2)

# (NPS_driver - TARGET_driver) * share: positive = driver above target, negative = drag
vt_impacts = {}
for drv in monthly_driver:
    b   = monthly_driver[drv]["M1"]
    nb  = nps(*b)
    tgt = DRIVER_TARGETS.get(drv)
    sh  = b[2] / sM1 if sM1 else 0
    gap_d = round(nb - tgt, 2) if nb is not None and tgt is not None else 0.0
    vt_impacts[drv] = {"var": round(gap_d * sh, 2), "nps": nb, "target": tgt,
                       "gap": gap_d, "share": round(sh * 100, 1)}

# ─── HELPERS JS ──────────────────────────────────────────────────────────────
def sorted_impacts(decomp):
    """Sort: maiores ganhos primeiro ate maiores perdas por ultimo (decrescente)."""
    items = [{"label": d, "v": round(r["var"], 3), "cat": CAT.get(d, "?")}
             for d, r in decomp.items()]
    return sorted(items, key=lambda x: -x["v"])

def calc_y_base(start, drivers):
    """Minimum running value minus padding, used as bar anchor for start/end."""
    running = start
    vals = [start]
    for d in drivers:
        running += d["v"]
        vals.append(running)
    return round(min(vals) - 3, 1)

mom_drivers = sorted_impacts(mD)
wow_drivers = sorted_impacts(wD)
vt_drivers  = sorted_impacts(vt_impacts)

mom_ybase = calc_y_base(nM2, mom_drivers)
wow_ybase = calc_y_base(nS2, wow_drivers)
vt_ybase  = calc_y_base(theoretical_target, vt_drivers)

# ─── HTML ─────────────────────────────────────────────────────────────────────
def sc(label, val_main, val_sub=None, delta=None, surveys=None):
    sign = "+" if delta and delta > 0 else ""
    delta_cls = "delta-pos" if delta and delta > 0 else ("delta-neg" if delta and delta < 0 else "delta-neu")
    delta_html = f'<div class="sc-delta {delta_cls}">{sign}{delta:+.2f} pp</div>' if delta is not None else ""
    sub_html   = f'<div class="sc-sub">{val_sub}</div>' if val_sub else ""
    surv_html  = f'<div class="sc-surv">{surveys:,} surveys</div>' if surveys else ""
    return f"""<div class="sc">
  <div class="sc-label">{label}</div>
  <div class="sc-val">{val_main:.1f}%</div>
  {delta_html}{sub_html}{surv_html}
</div>"""

def build_html():
    mom_json = json.dumps(mom_drivers)
    wow_json = json.dumps(wow_drivers)
    vt_json  = json.dumps(vt_drivers)

    sc_mom = (
        sc(M2_LABEL, nM2, surveys=sM2) +
        sc(M1_LABEL, nM1, surveys=sM1) +
        sc("Variacao MoM", nM1, val_sub=f"{M2_LABEL} vs {M1_LABEL}", delta=dM)
    )
    sc_wow = (
        sc(S2_LABEL, nS2, surveys=sS2) +
        sc(S1_LABEL, nS1, surveys=sS1) +
        sc("Variacao WoW", nS1, val_sub=f"{S2_LABEL} vs {S1_LABEL}", delta=dW)
    )
    sc_vt = (
        sc(f"NPS {M1_LABEL}", nM1, surveys=sM1) +
        sc("Target Abril (consol)", NPS_TARGET_CONSOL) +
        sc("Gap vs Target", nM1, val_sub="NPS atual vs target consolidado", delta=gap_consol)
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NPS Driver Impact - All Sellers BR</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#eef0f5;color:#1a1e3c;font-size:13px}}
header{{background:#1a1e3c;color:#fff;padding:14px 24px;display:flex;align-items:center;justify-content:space-between}}
header h1{{font-size:17px;font-weight:700}}
.meta{{font-size:11px;color:#aab4d4}}
.page{{padding:20px 24px;display:flex;flex-direction:column;gap:28px}}

/* Scorecards */
.sc-group{{display:flex;gap:12px;flex-wrap:wrap}}
.sc{{background:#fff;border-radius:10px;padding:14px 18px;min-width:155px;
     box-shadow:0 1px 4px rgba(0,0,0,.08);border-top:3px solid #9099c8}}
.sc-label{{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px}}
.sc-val{{font-size:28px;font-weight:700;color:#1a1e3c;line-height:1}}
.sc-delta{{font-size:15px;font-weight:700;margin-top:4px}}
.delta-pos{{color:#1b5e20}}.delta-neg{{color:#b71c1c}}.delta-neu{{color:#555}}
.sc-sub{{font-size:10px;color:#aaa;margin-top:2px}}
.sc-surv{{font-size:10px;color:#bbb;margin-top:1px}}

/* Chart sections */
.chart-section{{background:#fff;border-radius:12px;padding:20px 24px;
                box-shadow:0 1px 4px rgba(0,0,0,.08)}}
.chart-title{{font-size:13px;font-weight:700;color:#1a1e3c;margin-bottom:4px}}
.chart-sub{{font-size:11px;color:#888;margin-bottom:14px}}
.chart-wrap{{position:relative;height:320px;width:100%}}
</style>
</head>
<body>
<header>
  <div>
    <h1>NPS Driver Impact - All Sellers BR</h1>
    <div class="meta">27 drivers | Sellers | CENTER=BR | E-Commerce</div>
  </div>
  <div class="meta" style="text-align:right">Gerado em {REPORT_DATE}</div>
</header>

<div class="page">

  <!-- MoM -->
  <section>
    <div class="sc-group">{sc_mom}</div>
  </section>
  <div class="chart-section">
    <div class="chart-title">Impacto MoM - Abertura Driver</div>
    <div class="chart-sub">Contribuicao de cada driver (pp) para a variacao consolidada {M2_LABEL} vs {M1_LABEL}. Ordenado: maiores ganhos primeiro, maiores quedas por ultimo.</div>
    <div class="chart-wrap"><canvas id="c-mom"></canvas></div>
  </div>

  <!-- WoW -->
  <section>
    <div class="sc-group">{sc_wow}</div>
  </section>
  <div class="chart-section">
    <div class="chart-title">Impacto WoW - Abertura Driver</div>
    <div class="chart-sub">Contribuicao de cada driver (pp) para a variacao consolidada {S2_LABEL} vs {S1_LABEL}.</div>
    <div class="chart-wrap"><canvas id="c-wow"></canvas></div>
  </div>

  <!-- vs Target -->
  <section>
    <div class="sc-group">{sc_vt}</div>
  </section>
  <div class="chart-section">
    <div class="chart-title">vs Target - Abertura Driver</div>
    <div class="chart-sub">Cada driver contribui com (NPS_driver - Target_driver) x share para o desvio em relacao ao target ponderado ({theoretical_target:.1f}%). Negativo = abaixo do target = oportunidade.</div>
    <div class="chart-wrap"><canvas id="c-vt"></canvas></div>
  </div>

</div>

<script>
Chart.register(ChartDataLabels);

const BLUE   = 'rgba(30,65,150,0.88)';
const GREEN  = 'rgba(30,160,80,0.88)';
const RED    = 'rgba(210,45,45,0.88)';
const BLUE_S = 'rgba(30,65,150,0.55)';

function shorten(s, n) {{
  n = n || 10;
  return s.length > n ? s.slice(0, n) + '...' : s;
}}

function buildWaterfall(canvasId, startVal, endVal, startLabel, endLabel, drivers, yBase) {{
  const labels = [startLabel];
  const floatData  = [[yBase, startVal]];
  const bgColors   = [BLUE];
  const dlValues   = [startVal.toFixed(1) + '%'];

  let running = startVal;
  drivers.forEach(function(d) {{
    labels.push(shorten(d.label, 11));
    floatData.push([running, running + d.v]);
    bgColors.push(d.v >= 0 ? GREEN : RED);
    dlValues.push((d.v >= 0 ? '+' : '') + d.v.toFixed(2) + '%');
    running += d.v;
  }});

  labels.push(endLabel);
  floatData.push([yBase, endVal]);
  bgColors.push(BLUE);
  dlValues.push(endVal.toFixed(1) + '%');

  const allVals = floatData.map(function(p) {{ return [p[0], p[1]]; }}).flat();
  const yMax = Math.max.apply(null, allVals) + 3;

  new Chart(document.getElementById(canvasId), {{
    type: 'bar',
    plugins: [ChartDataLabels],
    data: {{
      labels: labels,
      datasets: [{{
        data: floatData,
        backgroundColor: bgColors,
        borderWidth: 0,
        borderRadius: 2,
        barPercentage: 0.85,
        categoryPercentage: 0.9,
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{ enabled: false }},
        datalabels: {{
          formatter: function(val, ctx) {{ return dlValues[ctx.dataIndex]; }},
          anchor: function(ctx) {{
            var p = floatData[ctx.dataIndex];
            return p[1] >= p[0] ? 'end' : 'start';
          }},
          align: function(ctx) {{
            var p = floatData[ctx.dataIndex];
            return p[1] >= p[0] ? 'top' : 'bottom';
          }},
          font: {{ size: 9.5, weight: '600' }},
          color: '#333',
          padding: {{ top: 2, bottom: 2 }},
          clip: false,
        }}
      }},
      layout: {{ padding: {{ top: 28, bottom: 4 }} }},
      scales: {{
        y: {{
          min: yBase,
          max: yMax,
          display: false,
        }},
        x: {{
          ticks: {{
            maxRotation: 60,
            minRotation: 45,
            font: {{ size: 9.5 }},
            color: '#555',
          }},
          grid: {{ display: false }},
          border: {{ display: false }},
        }}
      }}
    }}
  }});
}}

// MoM
buildWaterfall('c-mom', {nM2}, {nM1}, '{M2_LABEL}', '{M1_LABEL}',
  {mom_json}, {mom_ybase});

// WoW
buildWaterfall('c-wow', {nS2}, {nS1}, '{S2_LABEL}', '{S1_LABEL}',
  {wow_json}, {wow_ybase});

// vs Target
buildWaterfall('c-vt', {theoretical_target}, {nM1}, 'Target Pond.', '{M1_LABEL}',
  {vt_json}, {vt_ybase});
</script>
</body>
</html>"""

if __name__ == "__main__":
    html = build_html()
    with open("driver_impact.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("OK driver_impact.html gerado -", REPORT_DATE)
    print("  MoM:", nM2, "->", nM1, "(", dM, "pp)")
    print("  WoW:", nS2, "->", nS1, "(", dW, "pp)")
    print("  vs Target: atual", nM1, "| target consol", NPS_TARGET_CONSOL,
          "| target pond.", theoretical_target)
