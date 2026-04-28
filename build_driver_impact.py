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

# ─── FILTRO SELLERS (sem drivers de mediacao) ────────────────────────────────
DRIVERS_EXCLUIDOS = {
    "CBT", "PDD DS&XD - Vendedor", "PDD FBM - Vendedor",
    "PDD Fotos - Vendedor", "PNR ME - Vendedor", "PNR MP - Vendedor",
    "PDD MP,FLEX & CBT - Vendedor",
}
monthly_driver_sel = {d: v for d, v in monthly_driver.items() if d not in DRIVERS_EXCLUIDOS}
weekly_driver_sel  = {d: v for d, v in weekly_driver.items()  if d not in DRIVERS_EXCLUIDOS}

# ─── CALCULOS ────────────────────────────────────────────────────────────────
def nps(p, d, s):
    return round(100.0 * (p - d) / s, 2) if s > 0 else None

def mix_neto(data, pa, pb, surv_a, surv_b, nps_b_tot):
    out = {}
    for drv, pd in data.items():
        a = pd.get(pa, (0, 0, 0)); b = pd.get(pb, (0, 0, 0))
        na = nps(*a); nb = nps(*b)
        sha = a[2] / surv_a if surv_a else 0
        shb = b[2] / surv_b if surv_b else 0
        nt = round(sha * (nb - na), 2) if na is not None and nb is not None else 0.0
        mx = round((shb - sha) * (nb - nps_b_tot), 2) if nb is not None else 0.0
        out[drv] = dict(surv_a=a[2], nps_a=na, share_a=round(sha*100,1),
                        surv_b=b[2], nps_b=nb, share_b=round(shb*100,1),
                        neto=nt, mix=mx, var=round(nt+mx,2))
    return out

def sorted_impacts(decomp):
    items = [{"label": d, "v": round(r["var"], 3)} for d, r in decomp.items()]
    return sorted(items, key=lambda x: -x["v"])

def calc_y_base(start, drivers):
    running, vals = start, [start]
    for d in drivers:
        running += d["v"]; vals.append(running)
    return round(min(vals) - 3, 1)

def compute_view(monthly_data, weekly_data):
    """Calcula todos os valores para um conjunto de drivers."""
    # Monthly
    sM2_ = sum(v["M2"][2] for v in monthly_data.values())
    sM1_ = sum(v["M1"][2] for v in monthly_data.values())
    nM2_ = nps(sum(v["M2"][0] for v in monthly_data.values()),
               sum(v["M2"][1] for v in monthly_data.values()), sM2_)
    nM1_ = nps(sum(v["M1"][0] for v in monthly_data.values()),
               sum(v["M1"][1] for v in monthly_data.values()), sM1_)
    dM_  = round(nM1_ - nM2_, 2)
    mD_  = mix_neto(monthly_data, "M2", "M1", sM2_, sM1_, nM1_)

    # Weekly
    sS2_ = sum(v["S2"][2] for v in weekly_data.values())
    sS1_ = sum(v["S1"][2] for v in weekly_data.values())
    nS2_ = nps(sum(v["S2"][0] for v in weekly_data.values()),
               sum(v["S2"][1] for v in weekly_data.values()), sS2_)
    nS1_ = nps(sum(v["S1"][0] for v in weekly_data.values()),
               sum(v["S1"][1] for v in weekly_data.values()), sS1_)
    dW_  = round(nS1_ - nS2_, 2)
    wD_  = mix_neto(weekly_data, "S2", "S1", sS2_, sS1_, nS1_)

    # vs Target
    tt_ = round(sum(DRIVER_TARGETS[d] * (monthly_data[d]["M1"][2] / sM1_)
                    for d in monthly_data if d in DRIVER_TARGETS), 2)
    vt_ = {}
    for drv in monthly_data:
        b = monthly_data[drv]["M1"]; nb = nps(*b)
        tgt = DRIVER_TARGETS.get(drv); sh = b[2] / sM1_ if sM1_ else 0
        gap_d = round(nb - tgt, 2) if nb is not None and tgt is not None else 0.0
        vt_[drv] = {"var": round(gap_d * sh, 2), "nps": nb, "target": tgt,
                    "gap": gap_d, "share": round(sh * 100, 1)}

    # Sorted for charts
    md_ = sorted_impacts(mD_); wd_ = sorted_impacts(wD_); vd_ = sorted_impacts(vt_)

    return dict(
        nM1=nM1_, nM2=nM2_, dM=dM_, sM1=sM1_, sM2=sM2_,
        nS1=nS1_, nS2=nS2_, dW=dW_, sS1=sS1_, sS2=sS2_,
        vs_tgt_mom=round(nM1_ - NPS_TARGET_CONSOL, 2),
        vs_tgt_wow=round(nS1_ - NPS_TARGET_CONSOL, 2),
        surv_mom_var=round((sM1_ - sM2_) / sM2_ * 100, 1) if sM2_ else 0,
        surv_wow_var=round((sS1_ - sS2_) / sS2_ * 100, 1) if sS2_ else 0,
        mD=mD_, wD=wD_, vt=vt_, tt=tt_,
        worst_mom=min(mD_, key=lambda d: mD_[d]["var"]),
        best_mom =max(mD_, key=lambda d: mD_[d]["var"]),
        worst_wow=min(wD_, key=lambda d: wD_[d]["var"]),
        best_wow =max(wD_, key=lambda d: wD_[d]["var"]),
        mom_json=json.dumps(md_), wow_json=json.dumps(wd_), vt_json=json.dumps(vd_),
        mom_ybase=calc_y_base(nM2_, md_),
        wow_ybase=calc_y_base(nS2_, wd_),
        vt_ybase =calc_y_base(tt_, vd_),
    )

V_ALL = compute_view(monthly_driver,     weekly_driver)
V_SEL = compute_view(monthly_driver_sel, weekly_driver_sel)

# ─── HTML ─────────────────────────────────────────────────────────────────────
def _arr(v): return "&#9650;" if v >= 0 else "&#9660;"
def _cls(v): return "pos" if v >= 0 else "neg"
def _pp(v):  return f"{v:+.2f} pp"
def _pct(v): return f"{v:+.1f}%"

def sc_nps(label, val, vs_tgt, vs_prev, prev_label, period_sub):
    val_color = "#1a7a1a" if vs_tgt >= 0 else "#c0321a"
    return f"""<div class="sc">
  <div class="sc-label">{label}</div>
  <div class="sc-val" style="color:{val_color}">{val:.1f}%</div>
  <hr class="sc-sep">
  <div class="bullet {_cls(vs_tgt)}">{_arr(vs_tgt)} {_pp(vs_tgt)} gap vs target</div>
  <div class="bullet {_cls(vs_prev)}">{_arr(vs_prev)} {_pp(vs_prev)} vs {prev_label}</div>
  <div class="sc-sub">{period_sub}</div>
</div>"""

def sc_target(val, label):
    return f"""<div class="sc">
  <div class="sc-label">TARGET</div>
  <div class="sc-val">{val:.1f}%</div>
  <hr class="sc-sep">
  <div class="sc-sub">meta do periodo</div>
  <div class="sc-sub">{label}</div>
</div>"""

def sc_surveys(surveys, var_pct, period_sub):
    return f"""<div class="sc">
  <div class="sc-label">PESQUISAS</div>
  <div class="sc-val sc-val-int">{surveys:,}</div>
  <hr class="sc-sep">
  <div class="bullet {_cls(var_pct)}">{_arr(var_pct)} {_pct(var_pct)} vs periodo ant.</div>
  <div class="sc-sub">{period_sub}</div>
</div>"""

def sc_driver(title, drv, nps_val, share_val,
              p1_label, p1_var, p2_label, p2_var, tgt_gap):
    return f"""<div class="sc sc-driver-card">
  <div class="sc-label">{title}</div>
  <div class="sc-driver-name">{drv}</div>
  <div class="sc-driver-meta">{nps_val:.1f}% NPS &middot; {share_val:.1f}% vol.</div>
  <div class="sc-bar-wrap"><div class="sc-bar" style="width:{share_val:.1f}%"></div></div>
  <hr class="sc-sep">
  <div class="bullet {_cls(p1_var)}">{_arr(p1_var)} {_pp(p1_var)} impacto {p1_label}</div>
  <div class="bullet {_cls(p2_var)}">{_arr(p2_var)} {_pp(p2_var)} impacto {p2_label}</div>
  <div class="bullet {_cls(tgt_gap)}">{_arr(tgt_gap)} {_pp(tgt_gap)} vs target</div>
</div>"""

def make_panes(pfx, v):
    """Gera os dois panes (MES + SEMANA) para um conjunto de dados."""
    mD, wD, vt = v["mD"], v["wD"], v["vt"]

    def cards_mes():
        wm = v["worst_mom"]; bm = v["best_mom"]
        return (
            sc_nps("NPS CONSOLIDADO", v["nM1"], v["vs_tgt_mom"], v["dM"], "mes ant.", M1_LABEL) +
            sc_target(NPS_TARGET_CONSOL, M1_LABEL) +
            sc_surveys(v["sM1"], v["surv_mom_var"], M1_LABEL) +
            sc_driver("DRIVER MAIS OFENSOR", wm,
                      mD[wm]["nps_b"], mD[wm]["share_b"],
                      "MoM", mD[wm]["var"], "WoW", wD[wm]["var"], vt[wm]["gap"]) +
            sc_driver("DRIVER MAIS PROMOTOR", bm,
                      mD[bm]["nps_b"], mD[bm]["share_b"],
                      "MoM", mD[bm]["var"], "WoW", wD[bm]["var"], vt[bm]["gap"])
        )

    def cards_sem():
        ww = v["worst_wow"]; bw = v["best_wow"]
        return (
            sc_nps("NPS CONSOLIDADO", v["nS1"], v["vs_tgt_wow"], v["dW"], "sem. ant.", S1_LABEL) +
            sc_target(NPS_TARGET_CONSOL, M1_LABEL) +
            sc_surveys(v["sS1"], v["surv_wow_var"], S1_LABEL) +
            sc_driver("DRIVER MAIS OFENSOR", ww,
                      wD[ww]["nps_b"], wD[ww]["share_b"],
                      "WoW", wD[ww]["var"], "MoM", mD[ww]["var"], vt[ww]["gap"]) +
            sc_driver("DRIVER MAIS PROMOTOR", bw,
                      wD[bw]["nps_b"], wD[bw]["share_b"],
                      "WoW", wD[bw]["var"], "MoM", mD[bw]["var"], vt[bw]["gap"])
        )

    tt = v["tt"]
    return f"""
  <div id="pane-{pfx}-mes" class="tab-pane">
    <div class="sc-grid">{cards_mes()}</div>
    <div class="chart-section">
      <div class="chart-title">Impacto MoM - Abertura Driver</div>
      <div class="chart-sub">Contribuicao de cada driver (pp) na variacao consolidada {M2_LABEL} &rarr; {M1_LABEL}.</div>
      <div class="chart-wrap"><canvas id="c-{pfx}-mom"></canvas></div>
    </div>
    <div class="chart-section">
      <div class="chart-title">vs Target - Abertura Driver</div>
      <div class="chart-sub">Partindo do target ponderado por volume ({tt:.1f}%), cada driver mostra seu desvio ate o NPS real de {v['nM1']:.1f}%. Negativo = abaixo do target.</div>
      <div class="chart-wrap"><canvas id="c-{pfx}-vt"></canvas></div>
    </div>
  </div>
  <div id="pane-{pfx}-sem" class="tab-pane">
    <div class="sc-grid">{cards_sem()}</div>
    <div class="chart-section">
      <div class="chart-title">Impacto WoW - Abertura Driver</div>
      <div class="chart-sub">Contribuicao de cada driver (pp) na variacao consolidada {S2_LABEL} &rarr; {S1_LABEL}.</div>
      <div class="chart-wrap"><canvas id="c-{pfx}-wow"></canvas></div>
    </div>
  </div>"""

def build_html():

    panes_all = make_panes("all", V_ALL)
    panes_sel = make_panes("sel", V_SEL)

    # js chart calls para os 6 graficos
    def js_charts(pfx, v):
        return (
            f"buildWaterfall('c-{pfx}-mom',{v['nM2']},{v['nM1']},'{M2_LABEL}','{M1_LABEL}',"
            f"{v['mom_json']},{v['mom_ybase']});\n"
            f"buildWaterfall('c-{pfx}-wow',{v['nS2']},{v['nS1']},'{S2_LABEL}','{S1_LABEL}',"
            f"{v['wow_json']},{v['wow_ybase']});\n"
            f"buildWaterfall('c-{pfx}-vt',{v['tt']},{v['nM1']},'Target Pond.','{M1_LABEL}',"
            f"{v['vt_json']},{v['vt_ybase']});\n"
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
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
      background:#eef0f5;color:#1a1e3c;font-size:13px}}
header{{background:#1a1e3c;color:#fff;padding:13px 24px;
        display:flex;align-items:center;justify-content:space-between}}
header h1{{font-size:16px;font-weight:700}}
.hd-meta{{font-size:11px;color:#aab4d4}}

/* ── Barra de navegacao ── */
.nav-bar{{background:#eef0f5;padding:14px 24px 0;
          display:flex;align-items:flex-end;justify-content:space-between;gap:12px}}
.view-tabs{{display:flex;gap:3px;background:#d0d5e2;border-radius:8px;padding:3px}}
.view-btn{{border:none;cursor:pointer;padding:7px 22px;border-radius:6px;
           font-size:12px;font-weight:700;background:transparent;color:#555;transition:.15s}}
.view-btn.active{{background:#1a1e3c;color:#fff;box-shadow:0 1px 4px rgba(0,0,0,.2)}}
.right-nav{{display:flex;align-items:center;gap:8px}}
.period-tabs{{display:flex;gap:3px;background:#d0d5e2;border-radius:8px;padding:3px}}
.period-btn{{border:none;cursor:pointer;padding:6px 18px;border-radius:6px;
             font-size:12px;font-weight:700;background:transparent;color:#555;transition:.15s}}
.period-btn.active{{background:#bf5c00;color:#fff;box-shadow:0 1px 4px rgba(0,0,0,.15)}}
.period-label{{font-size:12px;color:#666;background:#fff;border:1px solid #d0d5e0;
               border-radius:6px;padding:5px 12px}}

/* ── Page ── */
.page{{padding:16px 24px;display:flex;flex-direction:column;gap:20px}}
.tab-pane{{display:none}}.tab-pane.active{{display:flex;flex-direction:column;gap:20px}}

/* ── Scorecards ── */
.sc-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.sc{{background:#fff;border-radius:10px;padding:16px 18px;
     box-shadow:0 1px 4px rgba(0,0,0,.07);border-top:3px solid #c8cdd8}}
.sc-label{{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:.6px;
           margin-bottom:6px;font-weight:700}}
.sc-val{{font-size:30px;font-weight:700;color:#bf5c00;line-height:1.1}}
.sc-val-int{{font-size:28px;font-weight:700;color:#bf5c00;line-height:1.1}}
.sc-sep{{border:none;border-top:1px solid #eee;margin:8px 0}}
.sc-sub{{font-size:10px;color:#aaa;margin-top:3px}}
.bullet{{font-size:11px;font-weight:600;margin-top:4px;line-height:1.4}}
.bullet.pos{{color:#1a7a1a}}.bullet.neg{{color:#c0321a}}
.sc-driver-name{{font-size:13px;font-weight:700;color:#1a1e3c;margin-bottom:2px}}
.sc-driver-meta{{font-size:11px;color:#777;margin-bottom:4px}}
.sc-bar-wrap{{height:4px;background:#eee;border-radius:2px;margin-bottom:2px}}
.sc-bar{{height:4px;background:#9099c8;border-radius:2px}}

/* ── Charts ── */
.chart-section{{background:#fff;border-radius:12px;padding:18px 22px;
                box-shadow:0 1px 4px rgba(0,0,0,.07)}}
.chart-title{{font-size:13px;font-weight:700;color:#1a1e3c;margin-bottom:3px}}
.chart-sub{{font-size:11px;color:#888;margin-bottom:12px}}
.chart-wrap{{position:relative;height:310px;width:100%}}
</style>
</head>
<body>

<header>
  <div>
    <h1>NPS Driver Impact - All Sellers BR</h1>
    <div class="hd-meta">Sellers | CENTER=BR | E-Commerce</div>
  </div>
  <div class="hd-meta" style="text-align:right">Gerado em {REPORT_DATE}</div>
</header>

<div class="nav-bar">
  <div class="view-tabs">
    <button class="view-btn active" data-view="all" onclick="setView(this)">All Drivers</button>
    <button class="view-btn"        data-view="sel" onclick="setView(this)">Drivers Sellers</button>
  </div>
  <div class="right-nav">
    <div class="period-tabs">
      <button class="period-btn active" data-period="mes" onclick="setPeriod(this)">MES</button>
      <button class="period-btn"        data-period="sem" onclick="setPeriod(this)">SEMANA</button>
    </div>
    <div class="period-label" id="period-label">{M1_LABEL}</div>
  </div>
</div>

<div class="page">
  {panes_all}
  {panes_sel}
</div>

<script>
Chart.register(ChartDataLabels);
var currentView = 'all', currentPeriod = 'mes';
var PERIOD_LABELS = {{ mes: '{M1_LABEL}', sem: '{S1_LABEL}' }};

function updatePanes() {{
  document.querySelectorAll('.tab-pane').forEach(function(p) {{ p.classList.remove('active'); }});
  var id = 'pane-' + currentView + '-' + currentPeriod;
  var el = document.getElementById(id);
  if (el) el.classList.add('active');
  document.getElementById('period-label').textContent = PERIOD_LABELS[currentPeriod] || '';
}}
function setView(btn) {{
  currentView = btn.getAttribute('data-view');
  document.querySelectorAll('.view-btn').forEach(function(b) {{ b.classList.remove('active'); }});
  btn.classList.add('active');
  updatePanes();
}}
function setPeriod(btn) {{
  currentPeriod = btn.getAttribute('data-period');
  document.querySelectorAll('.period-btn').forEach(function(b) {{ b.classList.remove('active'); }});
  btn.classList.add('active');
  updatePanes();
}}

function shorten(s, n) {{
  n = n || 11;
  return s.length > n ? s.slice(0, n) + '...' : s;
}}
function buildWaterfall(canvasId, startVal, endVal, startLabel, endLabel, drivers, yBase) {{
  var labels = [startLabel], floatData = [[yBase, startVal]],
      bgColors = ['rgba(30,65,150,0.88)'], dlValues = [startVal.toFixed(1) + '%'];
  var running = startVal;
  drivers.forEach(function(d) {{
    labels.push(shorten(d.label));
    floatData.push([running, running + d.v]);
    bgColors.push(d.v >= 0 ? 'rgba(30,160,80,0.88)' : 'rgba(210,45,45,0.88)');
    dlValues.push((d.v >= 0 ? '+' : '') + d.v.toFixed(2) + '%');
    running += d.v;
  }});
  labels.push(endLabel); floatData.push([yBase, endVal]);
  bgColors.push('rgba(30,65,150,0.88)'); dlValues.push(endVal.toFixed(1) + '%');
  var allVals = floatData.reduce(function(a,p){{return a.concat([p[0],p[1]]);}},[]);
  var yMax = Math.max.apply(null, allVals) + 3;
  new Chart(document.getElementById(canvasId), {{
    type: 'bar', plugins: [ChartDataLabels],
    data: {{ labels: labels, datasets: [{{
      data: floatData, backgroundColor: bgColors,
      borderWidth: 0, borderRadius: 2, barPercentage: 0.85, categoryPercentage: 0.9
    }}] }},
    options: {{
      responsive: true, maintainAspectRatio: false, animation: false,
      plugins: {{
        legend: {{ display: false }}, tooltip: {{ enabled: false }},
        datalabels: {{
          formatter: function(val,ctx){{ return dlValues[ctx.dataIndex]; }},
          anchor: function(ctx){{ var p=floatData[ctx.dataIndex]; return p[1]>=p[0]?'end':'start'; }},
          align:  function(ctx){{ var p=floatData[ctx.dataIndex]; return p[1]>=p[0]?'top':'bottom'; }},
          font: {{ size: 9.5, weight: '600' }}, color: '#333', padding: 2, clip: false
        }}
      }},
      layout: {{ padding: {{ top: 28, bottom: 4 }} }},
      scales: {{
        y: {{ min: yBase, max: yMax, display: false }},
        x: {{ ticks: {{ maxRotation: 60, minRotation: 45, font: {{ size: 9.5 }}, color: '#555' }},
              grid: {{ display: false }}, border: {{ display: false }} }}
      }}
    }}
  }});
}}

{js_charts("all", V_ALL)}{js_charts("sel", V_SEL)}
</script>
</body>
</html>"""

if __name__ == "__main__":
    html = build_html()
    with open("driver_impact.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("OK driver_impact.html gerado -", REPORT_DATE)
    print("  [ALL] MoM:", V_ALL["nM2"], "->", V_ALL["nM1"], "(", V_ALL["dM"], "pp)")
    print("  [ALL] WoW:", V_ALL["nS2"], "->", V_ALL["nS1"], "(", V_ALL["dW"], "pp)")
    print("  [SEL] MoM:", V_SEL["nM2"], "->", V_SEL["nM1"], "(", V_SEL["dM"], "pp)")
    print("  [SEL] WoW:", V_SEL["nS2"], "->", V_SEL["nS1"], "(", V_SEL["dW"], "pp)")
