#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_driver_impact.py
Visões de impacto NPS por driver: MoM | WoW | vs Target
Gera: driver_impact.html
"""
from datetime import datetime

# ─── METADATA ────────────────────────────────────────────────────────────────
M1_LABEL          = "Abril 2026"
M2_LABEL          = "Março 2026"
S1_LABEL          = "20/abr – 26/abr"
S2_LABEL          = "13/abr – 19/abr"
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
    "FBM": ["FBM-S Mature", "FBM-S Meli Pro", "FBM-S Seller Dev"],
    "Otros CV": ["Otros CV"],
}
CAT = {d: c for c, ds in _CATS.items() for d in ds}

CAT_COLOR = {
    "Longtail": "#1a73e8",
    "Mature":   "#e37400",
    "Meli Pro": "#1e8e3e",
    "Buyers":   "#7b1fa2",
    "FBM":      "#c62828",
    "Otros CV": "#546e7a",
}

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

# ─── CÁLCULOS ────────────────────────────────────────────────────────────────
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

# vs Target
gap_consol = round(nM1 - NPS_TARGET_CONSOL, 2)
tD = {}
for drv in monthly_driver:
    b   = monthly_driver[drv]["M1"]
    nb  = nps(*b)
    tgt = DRIVER_TARGETS.get(drv)
    sh  = b[2] / sM1 if sM1 else 0
    gap_d = round(nb - tgt, 2) if nb is not None and tgt is not None else None
    imp   = round(gap_d * sh, 2) if gap_d is not None else None
    opp   = round(-gap_d * sh, 2) if (gap_d is not None and gap_d < 0) else 0.0
    tD[drv] = dict(nps=nb, target=tgt, gap=gap_d,
                   share=round(sh * 100, 1), impact=imp, opportunity=opp)

# ─── HELPERS HTML ────────────────────────────────────────────────────────────
def fmt_nps(v):
    if v is None:
        return "—"
    return f"{v:.1f}%"

def fmt_delta(v, decimals=2):
    if v is None:
        return "—"
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.{decimals}f} pp"

def impact_class(v, thresh_hi=0.3, thresh_lo=-0.3):
    if v is None:
        return ""
    if v >= thresh_hi:
        return "pos-hi"
    if v > 0:
        return "pos-lo"
    if v <= thresh_lo:
        return "neg-hi"
    if v < 0:
        return "neg-lo"
    return "neutral"

def delta_class(v):
    if v is None:
        return ""
    return "pos-hi" if v > 0 else ("neg-hi" if v < 0 else "neutral")

def cat_badge(drv):
    c = CAT.get(drv, "?")
    col = CAT_COLOR.get(c, "#888")
    return f'<span class="badge" style="background:{col}">{c}</span>'

def bar_html(v, max_abs, width=80):
    if v is None or max_abs == 0:
        return ""
    pct = abs(v) / max_abs * width
    color = "#1b5e20" if v >= 0 else "#b71c1c"
    direction = "left" if v < 0 else "right"
    align = "right" if v < 0 else "left"
    return (f'<div style="display:flex;align-items:center;gap:4px;justify-content:{align}">'
            f'<div style="width:{pct:.0f}px;height:10px;background:{color};'
            f'border-radius:2px"></div></div>')

def scorecard(label, value, sub=None, cls=""):
    sub_html = f'<div class="sc-sub">{sub}</div>' if sub else ""
    return f'<div class="sc {cls}"><div class="sc-label">{label}</div><div class="sc-value">{value}</div>{sub_html}</div>'

# ─── TABELAS ─────────────────────────────────────────────────────────────────
def table_impact(decomp, label_a, label_b, delta_total):
    rows = sorted(decomp.items(), key=lambda x: abs(x[1]["var"]), reverse=True)
    max_abs = max(abs(r["var"]) for _, r in rows) or 1

    hdr = f"""<thead><tr>
      <th>Driver</th><th>Categoria</th>
      <th>{label_a}</th><th>{label_b}</th>
      <th>Δ Driver</th><th>Surveys</th><th>Share</th>
      <th>NETO</th><th>MIX</th>
      <th class="col-impact">Impacto Consol</th>
      <th>Barra</th>
    </tr></thead>"""

    body_rows = []
    for drv, r in rows:
        na  = r["nps_a"]
        nb  = r["nps_b"]
        d_drv = round(nb - na, 2) if na is not None and nb is not None else None
        var = r["var"]
        body_rows.append(f"""<tr>
          <td class="drv-name">{drv}</td>
          <td>{cat_badge(drv)}</td>
          <td class="num">{fmt_nps(na)}</td>
          <td class="num">{fmt_nps(nb)}</td>
          <td class="num {delta_class(d_drv)}">{fmt_delta(d_drv)}</td>
          <td class="num">{r['surv_b']:,}</td>
          <td class="num">{r['share_b']:.1f}%</td>
          <td class="num {impact_class(r['neto'],0.15,-0.15)}">{fmt_delta(r['neto'])}</td>
          <td class="num {impact_class(r['mix'],0.15,-0.15)}">{fmt_delta(r['mix'])}</td>
          <td class="num bold {impact_class(var)}">{fmt_delta(var)}</td>
          <td>{bar_html(var, max_abs)}</td>
        </tr>""")

    # Totais
    tot_surv = sum(r["surv_b"] for _, r in rows)
    tot_var  = round(sum(r["var"] for _, r in rows), 2)
    tot_neto = round(sum(r["neto"] for _, r in rows), 2)
    tot_mix  = round(sum(r["mix"] for _, r in rows), 2)
    body_rows.append(f"""<tr class="total-row">
      <td colspan="5"><strong>Total consolidado</strong></td>
      <td class="num">{tot_surv:,}</td>
      <td class="num">100%</td>
      <td class="num {impact_class(tot_neto)}">{fmt_delta(tot_neto)}</td>
      <td class="num {impact_class(tot_mix)}">{fmt_delta(tot_mix)}</td>
      <td class="num bold {impact_class(delta_total)}">{fmt_delta(delta_total)}</td>
      <td></td>
    </tr>""")

    return f'<table class="impact-table">{hdr}<tbody>{"".join(body_rows)}</tbody></table>'


def table_target():
    rows = sorted(tD.items(), key=lambda x: x[1]["opportunity"], reverse=True)
    max_opp = max(r["opportunity"] for _, r in rows) or 1

    hdr = """<thead><tr>
      <th>Driver</th><th>Categoria</th>
      <th>NPS Abr</th><th>Target</th>
      <th>Gap vs Target</th><th>Share</th>
      <th>Impacto no Consol</th>
      <th class="col-impact">Oportunidade</th>
      <th>Potencial</th>
    </tr></thead>"""

    body_rows = []
    for drv, r in rows:
        gap = r["gap"]
        imp = r["impact"]
        opp = r["opportunity"]
        body_rows.append(f"""<tr>
          <td class="drv-name">{drv}</td>
          <td>{cat_badge(drv)}</td>
          <td class="num">{fmt_nps(r['nps'])}</td>
          <td class="num">{fmt_nps(r['target'])}</td>
          <td class="num {delta_class(gap)}">{fmt_delta(gap)}</td>
          <td class="num">{r['share']:.1f}%</td>
          <td class="num {impact_class(imp)}">{fmt_delta(imp)}</td>
          <td class="num bold {'opp-cell' if opp > 0 else 'neutral'}">{fmt_delta(opp) if opp > 0 else '—'}</td>
          <td>{bar_html(opp, max_opp) if opp > 0 else ''}</td>
        </tr>""")

    tot_imp  = round(sum(r["impact"] for _, r in rows if r["impact"] is not None), 2)
    tot_opp  = round(sum(r["opportunity"] for _, r in rows), 2)
    body_rows.append(f"""<tr class="total-row">
      <td colspan="6"><strong>Total potencial se todos drivers atingissem target</strong></td>
      <td class="num {impact_class(tot_imp)}">{fmt_delta(tot_imp)}</td>
      <td class="num bold opp-cell">{fmt_delta(tot_opp)}</td>
      <td></td>
    </tr>""")

    return f'<table class="impact-table">{hdr}<tbody>{"".join(body_rows)}</tbody></table>'


# ─── HTML ─────────────────────────────────────────────────────────────────────
CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #f0f2f5; color: #1a1a2e; font-size: 13px; }

header { background: #1a1e3c; color: #fff; padding: 16px 24px;
         display: flex; align-items: center; justify-content: space-between; }
header h1 { font-size: 18px; font-weight: 700; }
header .meta { font-size: 11px; color: #aab4d4; }

.tabs { display: flex; gap: 2px; padding: 16px 24px 0; background: #f0f2f5; }
.tab-btn { padding: 10px 24px; border: none; border-radius: 8px 8px 0 0; cursor: pointer;
           font-size: 13px; font-weight: 600; background: #d8dce8; color: #555; transition: .15s; }
.tab-btn.active { background: #fff; color: #1a1e3c; box-shadow: 0 -2px 8px rgba(0,0,0,.06); }
.tab-btn:hover:not(.active) { background: #c8cdd8; }

.tab-content { display: none; padding: 0 24px 32px; background: #f0f2f5; }
.tab-content.active { display: block; }

.scorecards { display: flex; gap: 12px; padding: 20px 0 16px; flex-wrap: wrap; }
.sc { background: #fff; border-radius: 10px; padding: 16px 20px; min-width: 160px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08); border-top: 3px solid #c8cdd8; }
.sc.pos { border-top-color: #1b5e20; }
.sc.neg { border-top-color: #b71c1c; }
.sc.neutral-sc { border-top-color: #1a73e8; }
.sc-label { font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 6px; }
.sc-value { font-size: 26px; font-weight: 700; color: #1a1e3c; }
.sc.pos .sc-value { color: #1b5e20; }
.sc.neg .sc-value { color: #b71c1c; }
.sc-sub { font-size: 11px; color: #888; margin-top: 4px; }

.section-title { font-size: 13px; font-weight: 700; color: #1a1e3c; text-transform: uppercase;
                 letter-spacing: .6px; padding: 8px 0 10px; border-bottom: 2px solid #1a1e3c;
                 margin-bottom: 12px; }
.note { font-size: 11px; color: #888; margin-bottom: 10px; }

.table-wrap { overflow-x: auto; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
table.impact-table { width: 100%; border-collapse: collapse; background: #fff; }
table.impact-table th { background: #1a1e3c; color: #fff; padding: 9px 10px;
                         text-align: left; font-size: 11px; font-weight: 600;
                         text-transform: uppercase; letter-spacing: .4px; white-space: nowrap; }
table.impact-table td { padding: 7px 10px; border-bottom: 1px solid #f0f0f0;
                         vertical-align: middle; }
table.impact-table tr:hover td { background: #fafbff; }
table.impact-table tr.total-row td { background: #f5f5f5; font-weight: 600;
                                      border-top: 2px solid #ddd; }
.col-impact { background: #2d3277 !important; }

.drv-name { font-weight: 500; min-width: 200px; }
.num { text-align: right; white-space: nowrap; }
.bold { font-weight: 700; }

.badge { display: inline-block; padding: 2px 7px; border-radius: 10px; font-size: 10px;
         font-weight: 600; color: #fff; white-space: nowrap; }

.pos-hi  { background: #e8f5e9; color: #1b5e20 !important; }
.pos-lo  { background: #f1f8e9; color: #33691e !important; }
.neg-hi  { background: #ffebee; color: #b71c1c !important; }
.neg-lo  { background: #fff3f3; color: #c62828 !important; }
.neutral { color: #555 !important; }
.opp-cell { background: #e3f2fd !important; color: #0d47a1 !important; }

.legend { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #555; }
.legend-dot { width: 10px; height: 10px; border-radius: 2px; }
"""

JS = """
function showTab(id) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelector('[data-tab="'+id+'"]').classList.add('active');
}
"""


def build_html():
    sc_mom = (
        scorecard(M2_LABEL, fmt_nps(nM2), f"{sM2:,} surveys", "neutral-sc") +
        scorecard(M1_LABEL, fmt_nps(nM1), f"{sM1:,} surveys", "neutral-sc") +
        scorecard("Variação MoM", fmt_delta(dM), None, "pos" if dM >= 0 else "neg")
    )
    sc_wow = (
        scorecard(S2_LABEL, fmt_nps(nS2), f"{sS2:,} surveys", "neutral-sc") +
        scorecard(S1_LABEL, fmt_nps(nS1), f"{sS1:,} surveys", "neutral-sc") +
        scorecard("Variação WoW", fmt_delta(dW), None, "pos" if dW >= 0 else "neg")
    )
    sc_tgt = (
        scorecard(f"NPS {M1_LABEL}", fmt_nps(nM1), f"{sM1:,} surveys", "neutral-sc") +
        scorecard("Target Abril", fmt_nps(NPS_TARGET_CONSOL), "SUM(NUM)/SUM(DEN)", "neutral-sc") +
        scorecard("Gap vs Target", fmt_delta(gap_consol), None, "pos" if gap_consol >= 0 else "neg")
    )

    legend = """<div class="legend">
      <span class="legend-item"><span class="legend-dot" style="background:#1b5e20"></span>Impacto positivo forte (&ge; +0.30pp)</span>
      <span class="legend-item"><span class="legend-dot" style="background:#a5d6a7"></span>Impacto positivo leve (&lt; +0.30pp)</span>
      <span class="legend-item"><span class="legend-dot" style="background:#ef9a9a"></span>Impacto negativo leve (&gt; -0.30pp)</span>
      <span class="legend-item"><span class="legend-dot" style="background:#b71c1c"></span>Impacto negativo forte (&le; -0.30pp)</span>
      <span class="legend-item"><span class="legend-dot" style="background:#1565c0"></span>Oportunidade (abaixo do target)</span>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NPS Driver Impact — All Sellers BR</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <div>
    <h1>NPS Driver Impact — All Sellers BR</h1>
    <div class="meta">27 drivers | Sellers | CENTER=BR | E-Commerce</div>
  </div>
  <div class="meta" style="text-align:right">Gerado em {REPORT_DATE}</div>
</header>

<div class="tabs">
  <button class="tab-btn active" data-tab="mom" onclick="showTab('mom')">MoM — Mês a Mês</button>
  <button class="tab-btn" data-tab="wow" onclick="showTab('wow')">WoW — Semana a Semana</button>
  <button class="tab-btn" data-tab="target">vs Target — Oportunidade</button>
</div>

<!-- ── TAB MoM ─────────────────────────────────────────────────────────────-->
<div id="mom" class="tab-content active">
  <div class="scorecards">{sc_mom}</div>
  <div class="section-title">Impacto por Driver — {M2_LABEL} → {M1_LABEL}</div>
  <p class="note">Impacto Consol = quanto cada driver contribuiu (em pp) para a variação do NPS consolidado.
  NETO = efeito de qualidade (variação interna do driver ponderada pelo share). MIX = efeito de redistribuição de volume entre drivers.
  Ordenado por |Impacto| decrescente.</p>
  {legend}
  <div class="table-wrap">
    {table_impact(mD, M2_LABEL, M1_LABEL, dM)}
  </div>
</div>

<!-- ── TAB WoW ─────────────────────────────────────────────────────────────-->
<div id="wow" class="tab-content">
  <div class="scorecards">{sc_wow}</div>
  <div class="section-title">Impacto por Driver — {S2_LABEL} → {S1_LABEL}</div>
  <p class="note">Impacto Consol = quanto cada driver contribuiu (em pp) para a variação do NPS consolidado semana a semana.
  Ordenado por |Impacto| decrescente.</p>
  {legend}
  <div class="table-wrap">
    {table_impact(wD, S2_LABEL, S1_LABEL, dW)}
  </div>
</div>

<!-- ── TAB vs Target ────────────────────────────────────────────────────────-->
<div id="target" class="tab-content">
  <div class="scorecards">{sc_tgt}</div>
  <div class="section-title">Oportunidade por Driver vs Target — {M1_LABEL}</div>
  <p class="note">Gap vs Target = NPS driver − Target driver.
  Impacto no Consol = quanto cada driver está arrastando (ou puxando) o NPS consolidado em relação ao target consolidado.
  Oportunidade = pp que o consolidado ganharia se esse driver atingisse seu target.
  Ordenado por Oportunidade decrescente.</p>
  {legend}
  <div class="table-wrap">
    {table_target()}
  </div>
</div>

<script>{JS}</script>
<script>
  document.querySelector('[data-tab="target"]').addEventListener('click', function() {{ showTab('target'); }});
</script>
</body>
</html>"""


if __name__ == "__main__":
    html = build_html()
    with open("driver_impact.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK driver_impact.html gerado - {REPORT_DATE}")
    print(f"  MoM: {fmt_nps(nM2)} -> {fmt_nps(nM1)} ({fmt_delta(dM)})")
    print(f"  WoW: {fmt_nps(nS2)} -> {fmt_nps(nS1)} ({fmt_delta(dW)})")
    print(f"  vs Target: {fmt_nps(nM1)} vs {fmt_nps(NPS_TARGET_CONSOL)} ({fmt_delta(gap_consol)})")
