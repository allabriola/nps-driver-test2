#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_driver_impact.py  v2
Single page: scorecards + waterfall charts (MoM | WoW | vs Target)
Gera: driver_impact.html
"""
import json
import os
from datetime import datetime

# ─── METADATA ────────────────────────────────────────────────────────────────
M1_LABEL          = "Abril 2026"
M2_LABEL          = "Marco 2026"
S1_LABEL          = "20/abr - 26/abr"
S2_LABEL          = "13/abr - 19/abr"
NPS_TARGET_ALL = 52.49   # SUM(NUM_TARGET)/SUM(DENOM_TARGET) — 27 drivers — Abril 2026
NPS_TARGET_SEL = 56.04   # SUM(NUM_TARGET)/SUM(DENOM_TARGET) — 20 drivers (sem Med) — Abril 2026
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
    "CBT":                               {"M2": (323, 58, 395),    "M1": (322, 49, 377)},
    "Experiencia Impositiva Mature":     {"M2": (45, 20, 72),      "M1": (25, 7, 37)},
    "Experiencia Impositiva Meli Pro":   {"M2": (8, 4, 13),        "M1": (10, 2, 14)},
    "Experiencia Impositiva Seller Dev": {"M2": (312, 108, 469),   "M1": (368, 107, 527)},
    "FBM-S Mature":                      {"M2": (130, 45, 203),    "M1": (88, 26, 123)},
    "FBM-S Meli Pro":                    {"M2": (11, 8, 22),       "M1": (44, 8, 56)},
    "FBM-S Seller Dev":                  {"M2": (347, 125, 524),   "M1": (295, 100, 435)},
    "ME Vendedor Mature":                {"M2": (1618, 314, 2184), "M1": (930, 188, 1202)},
    "ME Vendedor Meli Pro":              {"M2": (60, 10, 75),      "M1": (247, 24, 282)},
    "ME Vendedor Seller Dev":            {"M2": (4958, 754, 6266), "M1": (4756, 676, 5968)},
    "Otros CV":                          {"M2": (775, 182, 1047),  "M1": (648, 216, 918)},
    "PCF Vendedor Mature":               {"M2": (332, 85, 467),    "M1": (207, 63, 301)},
    "PCF Vendedor Meli Pro":             {"M2": (32, 8, 44),       "M1": (204, 35, 270)},
    "PCF Vendedor Seller Dev":           {"M2": (536, 166, 790),   "M1": (338, 98, 485)},
    "PDD DS&XD - Vendedor":              {"M2": (645, 486, 1280),  "M1": (476, 377, 947)},
    "PDD FBM - Vendedor":                {"M2": (193, 89, 306),    "M1": (157, 82, 263)},
    "PDD Fotos - Vendedor":              {"M2": (46, 22, 72),      "M1": (30, 22, 57)},
    "PDD MP,FLEX & CBT - Vendedor":      {"M2": (87, 58, 166),     "M1": (55, 39, 107)},
    "PNR ME - Vendedor":                 {"M2": (103, 71, 193),    "M1": (132, 78, 226)},
    "PNR MP - Vendedor":                 {"M2": (140, 90, 266),    "M1": (143, 66, 228)},
    "Partners":                          {"M2": (2228, 337, 2806), "M1": (1986, 311, 2523)},
    "Post Venta Mature":                 {"M2": (392, 76, 520),    "M1": (269, 45, 346)},
    "Post Venta Meli Pro":               {"M2": (70, 10, 81),      "M1": (310, 11, 329)},
    "Post Venta Seller Dev":             {"M2": (929, 178, 1186),  "M1": (747, 106, 924)},
    "Publicaciones Mature":              {"M2": (258, 51, 345),    "M1": (173, 35, 241)},
    "Publicaciones Meli Pro":            {"M2": (18, 7, 26),       "M1": (119, 12, 138)},
    "Publicaciones Seller Dev":          {"M2": (2639, 374, 3309), "M1": (1844, 323, 2366)},
}

weekly_driver = {
    "CBT":                               {"S2": (87, 15, 102),    "S1": (77, 16, 96)},
    "Experiencia Impositiva Mature":     {"S2": (6, 2, 8),        "S1": (2, 0, 4)},
    "Experiencia Impositiva Meli Pro":   {"S2": (2, 1, 4),        "S1": (3, 0, 3)},
    "Experiencia Impositiva Seller Dev": {"S2": (112, 33, 160),   "S1": (57, 23, 88)},
    "FBM-S Mature":                      {"S2": (23, 4, 29),      "S1": (17, 4, 21)},
    "FBM-S Meli Pro":                    {"S2": (14, 6, 20),      "S1": (17, 0, 20)},
    "FBM-S Seller Dev":                  {"S2": (68, 24, 101),    "S1": (85, 29, 121)},
    "ME Vendedor Mature":                {"S2": (222, 44, 286),   "S1": (146, 34, 186)},
    "ME Vendedor Meli Pro":              {"S2": (76, 4, 83),      "S1": (104, 10, 120)},
    "ME Vendedor Seller Dev":            {"S2": (1154, 178, 1482),"S1": (1058, 152, 1308)},
    "Otros CV":                          {"S2": (158, 56, 230),   "S1": (182, 68, 259)},
    "PCF Vendedor Mature":               {"S2": (51, 19, 81),     "S1": (21, 9, 34)},
    "PCF Vendedor Meli Pro":             {"S2": (67, 12, 89),     "S1": (101, 14, 131)},
    "PCF Vendedor Seller Dev":           {"S2": (95, 28, 137),    "S1": (82, 30, 129)},
    "PDD DS&XD - Vendedor":              {"S2": (135, 107, 261),  "S1": (112, 75, 210)},
    "PDD FBM - Vendedor":                {"S2": (38, 25, 72),     "S1": (43, 25, 74)},
    "PDD Fotos - Vendedor":              {"S2": (8, 8, 17),       "S1": (10, 7, 20)},
    "PDD MP,FLEX & CBT - Vendedor":      {"S2": (21, 11, 39),     "S1": (8, 10, 19)},
    "PNR ME - Vendedor":                 {"S2": (23, 10, 37),     "S1": (62, 39, 107)},
    "PNR MP - Vendedor":                 {"S2": (32, 13, 49),     "S1": (27, 24, 54)},
    "Partners":                          {"S2": (575, 85, 725),   "S1": (567, 85, 719)},
    "Post Venta Mature":                 {"S2": (76, 11, 97),     "S1": (46, 6, 58)},
    "Post Venta Meli Pro":               {"S2": (104, 5, 112),    "S1": (149, 1, 152)},
    "Post Venta Seller Dev":             {"S2": (194, 23, 233),   "S1": (177, 18, 209)},
    "Publicaciones Mature":              {"S2": (37, 14, 57),     "S1": (25, 3, 30)},
    "Publicaciones Meli Pro":            {"S2": (37, 4, 44),      "S1": (59, 4, 64)},
    "Publicaciones Seller Dev":          {"S2": (453, 80, 587),   "S1": (398, 75, 511)},
}

# Histórico mensal (Jan-Fev para chart do Deep Dive; Mar=M2, Abr=M1 já existem)
monthly_hist_extra = {
    "CBT":                               {"Jan":(481,57,549),    "Fev":(224,27,254)},
    "Experiencia Impositiva Mature":     {"Jan":(81,18,113),     "Fev":(49,14,70)},
    "Experiencia Impositiva Meli Pro":   {"Jan":(8,6,16),        "Fev":(1,3,5)},
    "Experiencia Impositiva Seller Dev": {"Jan":(574,111,744),   "Fev":(350,86,477)},
    "FBM-S Mature":                      {"Jan":(197,94,320),    "Fev":(135,61,216)},
    "FBM-S Meli Pro":                    {"Jan":(33,5,42),       "Fev":(20,6,27)},
    "FBM-S Seller Dev":                  {"Jan":(537,168,793),   "Fev":(340,109,501)},
    "ME Vendedor Mature":                {"Jan":(2084,422,2688), "Fev":(1558,342,2082)},
    "ME Vendedor Meli Pro":              {"Jan":(126,17,149),    "Fev":(93,9,109)},
    "ME Vendedor Seller Dev":            {"Jan":(8138,1110,9984),"Fev":(5136,734,6390)},
    "Otros CV":                          {"Jan":(935,420,1472),  "Fev":(844,241,1206)},
    "PCF Vendedor Mature":               {"Jan":(306,122,482),   "Fev":(324,90,464)},
    "PCF Vendedor Meli Pro":             {"Jan":(57,8,75),       "Fev":(57,11,73)},
    "PCF Vendedor Seller Dev":           {"Jan":(697,244,1059),  "Fev":(529,173,768)},
    "PDD DS&XD - Vendedor":              {"Jan":(406,324,830),   "Fev":(452,332,906)},
    "PDD FBM - Vendedor":                {"Jan":(93,39,153),     "Fev":(101,40,160)},
    "PDD Fotos - Vendedor":              {"Jan":(35,18,59),      "Fev":(31,18,61)},
    "PDD MP,FLEX & CBT - Vendedor":      {"Jan":(59,56,124),     "Fev":(75,61,151)},
    "PNR ME - Vendedor":                 {"Jan":(83,64,169),     "Fev":(86,79,186)},
    "PNR MP - Vendedor":                 {"Jan":(122,85,239),    "Fev":(147,88,258)},
    "Partners":                          {"Jan":(1793,251,2254), "Fev":(1808,217,2198)},
    "Post Venta Mature":                 {"Jan":(403,114,543),   "Fev":(363,85,493)},
    "Post Venta Meli Pro":               {"Jan":(115,11,128),    "Fev":(88,9,101)},
    "Post Venta Seller Dev":             {"Jan":(1206,265,1585), "Fev":(983,209,1291)},
    "Publicaciones Mature":              {"Jan":(321,73,429),    "Fev":(286,47,362)},
    "Publicaciones Meli Pro":            {"Jan":(43,8,53),       "Fev":(34,2,40)},
    "Publicaciones Seller Dev":          {"Jan":(3396,475,4216), "Fev":(2581,381,3231)},
}

# Semanas extras para Deep Dive (16/mar e 23/mar)
weekly_hist_extra2 = {
    "CBT":                               {"16/mar":(46,11,58),   "23/mar":(47,11,60)},
    "Experiencia Impositiva Mature":     {"16/mar":(10,4,18),    "23/mar":(9,4,15)},
    "Experiencia Impositiva Meli Pro":   {"16/mar":(2,0,2),      "23/mar":(2,1,3)},
    "Experiencia Impositiva Seller Dev": {"16/mar":(82,20,113),  "23/mar":(60,19,90)},
    "FBM-S Mature":                      {"16/mar":(25,9,38),    "23/mar":(34,7,46)},
    "FBM-S Meli Pro":                    {"16/mar":(3,4,9),      "23/mar":(2,0,2)},
    "FBM-S Seller Dev":                  {"16/mar":(75,26,114),  "23/mar":(76,25,115)},
    "ME Vendedor Mature":                {"16/mar":(396,78,540), "23/mar":(394,84,536)},
    "ME Vendedor Meli Pro":              {"16/mar":(14,2,18),    "23/mar":(15,1,17)},
    "ME Vendedor Seller Dev":            {"16/mar":(1130,152,1420),"23/mar":(1088,164,1358)},
    "Otros CV":                          {"16/mar":(175,43,235), "23/mar":(170,59,253)},
    "PCF Vendedor Mature":               {"16/mar":(98,24,136),  "23/mar":(66,19,96)},
    "PCF Vendedor Meli Pro":             {"16/mar":(11,3,15),    "23/mar":(3,1,6)},
    "PCF Vendedor Seller Dev":           {"16/mar":(121,31,168), "23/mar":(113,38,167)},
    "PDD DS&XD - Vendedor":              {"16/mar":(149,115,305),"23/mar":(134,146,304)},
    "PDD FBM - Vendedor":                {"16/mar":(33,14,55),   "23/mar":(45,26,76)},
    "PDD Fotos - Vendedor":              {"16/mar":(11,6,17),    "23/mar":(12,7,21)},
    "PDD MP,FLEX & CBT - Vendedor":      {"16/mar":(25,14,45),   "23/mar":(12,13,32)},
    "PNR ME - Vendedor":                 {"16/mar":(34,19,58),   "23/mar":(12,13,27)},
    "PNR MP - Vendedor":                 {"16/mar":(33,25,63),   "23/mar":(22,23,51)},
    "Partners":                          {"16/mar":(528,69,659), "23/mar":(450,75,573)},
    "Post Venta Mature":                 {"16/mar":(94,12,113),  "23/mar":(91,15,119)},
    "Post Venta Meli Pro":               {"16/mar":(15,3,19),    "23/mar":(18,3,21)},
    "Post Venta Seller Dev":             {"16/mar":(215,28,261), "23/mar":(214,41,280)},
    "Publicaciones Mature":              {"16/mar":(61,16,85),   "23/mar":(56,11,73)},
    "Publicaciones Meli Pro":            {"16/mar":(4,1,5),      "23/mar":(3,2,5)},
    "Publicaciones Seller Dev":          {"16/mar":(591,92,748), "23/mar":(574,74,718)},
}

# S3 = 06/abr-12/abr  |  S4 = 30/mar-05/abr  (histórico fechado)
weekly_hist_extra = {
    "CBT":                               {"S3": (87, 12, 101),   "S4": (75, 9, 86)},
    "Experiencia Impositiva Mature":     {"S3": (9, 3, 13),      "S4": (12, 5, 20)},
    "Experiencia Impositiva Meli Pro":   {"S3": (1, 0, 2),       "S4": (2, 1, 3)},
    "Experiencia Impositiva Seller Dev": {"S3": (150, 36, 208),  "S4": (66, 25, 100)},
    "FBM-S Mature":                      {"S3": (28, 7, 40),     "S4": (30, 13, 48)},
    "FBM-S Meli Pro":                    {"S3": (9, 2, 12),      "S4": (0, 2, 2)},
    "FBM-S Seller Dev":                  {"S3": (74, 24, 115),   "S4": (73, 23, 104)},
    "ME Vendedor Mature":                {"S3": (374, 82, 492),  "S4": (340, 56, 438)},
    "ME Vendedor Meli Pro":              {"S3": (24, 6, 30),     "S4": (10, 6, 17)},
    "ME Vendedor Seller Dev":            {"S3": (1676, 224, 2106),"S4": (1016, 158, 1270)},
    "Otros CV":                          {"S3": (181, 63, 259),  "S4": (139, 36, 195)},
    "PCF Vendedor Mature":               {"S3": (97, 24, 131),   "S4": (68, 14, 91)},
    "PCF Vendedor Meli Pro":             {"S3": (13, 3, 19),     "S4": (4, 3, 7)},
    "PCF Vendedor Seller Dev":           {"S3": (98, 29, 136),   "S4": (84, 23, 125)},
    "PDD DS&XD - Vendedor":              {"S3": (113, 95, 236),  "S4": (136, 106, 275)},
    "PDD FBM - Vendedor":                {"S3": (40, 18, 65),    "S4": (45, 16, 63)},
    "PDD Fotos - Vendedor":              {"S3": (7, 5, 12),      "S4": (9, 5, 15)},
    "PDD MP,FLEX & CBT - Vendedor":      {"S3": (16, 9, 28),     "S4": (14, 7, 24)},
    "PNR ME - Vendedor":                 {"S3": (21, 15, 38),    "S4": (18, 9, 30)},
    "PNR MP - Vendedor":                 {"S3": (54, 16, 74),    "S4": (33, 15, 56)},
    "Partners":                          {"S3": (460, 76, 587),  "S4": (448, 77, 574)},
    "Post Venta Mature":                 {"S3": (89, 15, 117),   "S4": (88, 20, 114)},
    "Post Venta Meli Pro":               {"S3": (25, 2, 29),     "S4": (8, 0, 9)},
    "Post Venta Seller Dev":             {"S3": (239, 39, 301),  "S4": (176, 39, 233)},
    "Publicaciones Mature":              {"S3": (72, 12, 101),   "S4": (61, 13, 87)},
    "Publicaciones Meli Pro":            {"S3": (6, 1, 8),       "S4": (6, 1, 8)},
    "Publicaciones Seller Dev":          {"S3": (607, 103, 769), "S4": (502, 88, 653)},
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

def compute_view(monthly_data, weekly_data, nps_target_consol):
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

    # NPS consolidado de S3 e S4 (para recorrência semanal)
    def consol_week(key):
        p = sum(weekly_hist_extra[d][key][0] for d in monthly_data if d in weekly_hist_extra)
        det = sum(weekly_hist_extra[d][key][1] for d in monthly_data if d in weekly_hist_extra)
        s = sum(weekly_hist_extra[d][key][2] for d in monthly_data if d in weekly_hist_extra)
        return nps(p, det, s)

    nS3_ = consol_week("S3")
    nS4_ = consol_week("S4")

    def drv_nps_w(drv, key):
        src = weekly_data if key in ("S1", "S2") else weekly_hist_extra
        t = src.get(drv, {}).get(key)
        return nps(*t) if t and t[2] > 0 else None

    def recurrence(drv):
        """
        Retorna dois dicts com flags de recorrencia:
        vs_target: {months: int (0-2), weeks: int (0-4)}
        trend:     {months: int (0=sem queda, 1=queda M2->M1),
                    weeks: int (0-3 semanas consecutivas de queda a partir de S1)}
        """
        tgt = DRIVER_TARGETS.get(drv)

        nm1 = nps(*monthly_data[drv]["M1"]) if monthly_data[drv]["M1"][2] > 0 else None
        nm2 = nps(*monthly_data[drv]["M2"]) if monthly_data[drv]["M2"][2] > 0 else None
        ns  = {k: drv_nps_w(drv, k) for k in ("S1", "S2", "S3", "S4")}

        # vs Target: periodos abaixo do target proprio do driver
        below_m = sum(1 for nd in [nm1, nm2] if nd is not None and tgt and nd < tgt)
        below_w = sum(1 for nd in ns.values() if nd is not None and tgt and nd < tgt)

        # Tendencia: queda consecutiva a partir do periodo mais recente
        # Mensal: queda M2->M1 = 1 comparacao
        trend_m = 1 if (nm1 is not None and nm2 is not None and nm1 < nm2) else 0

        # Semanal: quantas semanas consecutivas de queda a partir de S1
        consec_w = 0
        for older, newer in [("S2","S1"), ("S3","S2"), ("S4","S3")]:
            n_old, n_new = ns[older], ns[newer]
            if n_old is not None and n_new is not None and n_new < n_old:
                consec_w += 1
            else:
                break

        return {"below_m": below_m, "below_w": below_w,
                "trend_m": trend_m, "consec_w": consec_w}

    # Sorted for charts
    md_ = sorted_impacts(mD_); wd_ = sorted_impacts(wD_); vd_ = sorted_impacts(vt_)

    worst_mom_ = min(mD_, key=lambda d: mD_[d]["var"])
    best_mom_  = max(mD_, key=lambda d: mD_[d]["var"])
    worst_wow_ = min(wD_, key=lambda d: wD_[d]["var"])
    best_wow_  = max(wD_, key=lambda d: wD_[d]["var"])

    return dict(
        nM1=nM1_, nM2=nM2_, dM=dM_, sM1=sM1_, sM2=sM2_,
        nS1=nS1_, nS2=nS2_, dW=dW_, sS1=sS1_, sS2=sS2_,
        nps_target=nps_target_consol,
        vs_tgt_mom=round(nM1_ - nps_target_consol, 2),
        vs_tgt_wow=round(nS1_ - nps_target_consol, 2),
        surv_mom_var=round((sM1_ - sM2_) / sM2_ * 100, 1) if sM2_ else 0,
        surv_wow_var=round((sS1_ - sS2_) / sS2_ * 100, 1) if sS2_ else 0,
        mD=mD_, wD=wD_, vt=vt_, tt=tt_,
        worst_mom=worst_mom_, best_mom=best_mom_,
        worst_wow=worst_wow_, best_wow=best_wow_,
        rec_worst_mom=recurrence(worst_mom_),
        rec_best_mom =recurrence(best_mom_),
        rec_worst_wow=recurrence(worst_wow_),
        rec_best_wow =recurrence(best_wow_),
        mom_json=json.dumps(md_), wow_json=json.dumps(wd_), vt_json=json.dumps(vd_),
        mom_ybase=calc_y_base(nM2_, md_),
        wow_ybase=calc_y_base(nS2_, wd_),
        vt_ybase =calc_y_base(tt_, vd_),
    )

V_ALL = compute_view(monthly_driver,     weekly_driver,     NPS_TARGET_ALL)
V_SEL = compute_view(monthly_driver_sel, weekly_driver_sel, NPS_TARGET_SEL)

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
              p1_label, p1_var, p2_label, p2_var, tgt_gap,
              rec, is_worst):
    """rec = dict com below_m, below_w, trend_m, consec_w"""
    below_m  = rec["below_m"]   # 0-2 meses abaixo do target
    below_w  = rec["below_w"]   # 0-4 semanas abaixo do target
    trend_m  = rec["trend_m"]   # 1 se NPS caiu M2->M1
    consec_w = rec["consec_w"]  # 0-3 semanas consecutivas de queda a partir de S1

    # Bullet vs Target
    def tgt_bullet():
        alert_m = below_m == 2
        alert_w = below_w >= 3
        if alert_m and alert_w:
            cls = "neg" if is_worst else "pos"
            icon = "&#9660;" if is_worst else "&#9650;"
            return f'<div class="bullet {cls} rec-full">{icon} vs Target: {below_m}/2 meses &middot; {below_w}/4 semanas</div>'
        elif alert_m or alert_w:
            m_str = f"{below_m}/2 meses" if alert_m else f"{below_m}/2 meses"
            w_str = f"{below_w}/4 semanas"
            return f'<div class="bullet rec-partial">&#9654; vs Target: {m_str} &middot; {w_str}</div>'
        else:
            return f'<div class="bullet rec-none">&#8212; vs Target: {below_m}/2 meses &middot; {below_w}/4 semanas</div>'

    # Bullet Tendência
    def trend_bullet():
        alert_m = trend_m == 1
        alert_w = consec_w >= 3
        trend_m_str = "queda MoM" if trend_m else "sem queda MoM"
        trend_w_str = f"queda {consec_w} sem. consec." if consec_w > 0 else "sem queda semanal"
        if alert_m and alert_w:
            cls = "neg" if is_worst else "neg"
            return f'<div class="bullet {cls} rec-full">&#9660; Tendencia: {trend_m_str} &middot; {trend_w_str}</div>'
        elif alert_m or consec_w >= 2:
            return f'<div class="bullet rec-partial">&#9654; Tendencia: {trend_m_str} &middot; {trend_w_str}</div>'
        else:
            return f'<div class="bullet rec-none">&#8212; Tendencia: {trend_m_str} &middot; {trend_w_str}</div>'

    return f"""<div class="sc sc-driver-card">
  <div class="sc-label">{title}</div>
  <div class="sc-driver-name">{drv}</div>
  <div class="sc-driver-meta">{nps_val:.1f}% NPS &middot; {share_val:.1f}% vol.</div>
  <div class="sc-bar-wrap"><div class="sc-bar" style="width:{share_val:.1f}%"></div></div>
  <hr class="sc-sep">
  <div class="bullet {_cls(p1_var)}">{_arr(p1_var)} {_pp(p1_var)} impacto {p1_label}</div>
  <div class="bullet {_cls(p2_var)}">{_arr(p2_var)} {_pp(p2_var)} impacto {p2_label}</div>
  <div class="bullet {_cls(tgt_gap)}">{_arr(tgt_gap)} {_pp(tgt_gap)} vs target driver</div>
  <hr class="sc-sep">
  {tgt_bullet()}
  {trend_bullet()}
</div>"""

def compute_driver_history():
    """Historico NPS por driver: 3 meses (Fev/Mar/Abr) e 5 semanas (23/mar-20/abr)."""
    def nps_s(p, d, s): return round(100*(p-d)/s, 2) if s > 0 else None
    result = {}
    for drv in monthly_driver:
        monthly = []
        for label, key in [("Fev","Fev"),("Mar","M2"),("Abr","M1")]:
            if key in ("M1","M2"):
                t = monthly_driver[drv][key]
            else:
                t = monthly_hist_extra.get(drv, {}).get(key, (0,0,0))
            monthly.append({"label": label, "nps": nps_s(*t), "s": t[2]})
        weekly = []
        for label, src, key in [
            ("23/mar", weekly_hist_extra2, "23/mar"),
            ("30/mar", weekly_hist_extra,  "S4"),
            ("06/abr", weekly_hist_extra,  "S3"),
            ("13/abr", weekly_driver,      "S2"),
            ("20/abr", weekly_driver,      "S1"),
        ]:
            t = src.get(drv, {}).get(key, (0,0,0))
            weekly.append({"label": label, "nps": nps_s(*t), "s": t[2]})
        result[drv] = {"monthly": monthly, "weekly": weekly,
                       "target": DRIVER_TARGETS.get(drv), "cat": CAT.get(drv,"?")}
    return result

def compute_history(drivers):
    """Calcula historico NPS mensal (Jan-Abr) e semanal (6 semanas) para um conjunto de drivers."""
    def nps_safe(p, d, s): return round(100*(p-d)/s, 2) if s > 0 else None
    monthly = []
    for label, key in [("Jan","Jan"),("Fev","Fev"),("Mar","M2"),("Abr","M1")]:
        if key in ("M1","M2"):
            p   = sum(monthly_driver[d][key][0] for d in drivers)
            det = sum(monthly_driver[d][key][1] for d in drivers)
            s   = sum(monthly_driver[d][key][2] for d in drivers)
        else:
            p   = sum(monthly_hist_extra.get(d,{}).get(key,(0,0,0))[0] for d in drivers)
            det = sum(monthly_hist_extra.get(d,{}).get(key,(0,0,0))[1] for d in drivers)
            s   = sum(monthly_hist_extra.get(d,{}).get(key,(0,0,0))[2] for d in drivers)
        monthly.append({"label": label, "nps": nps_safe(p,det,s), "s": s})
    weekly = []
    for label, src, key in [
        ("16/mar", weekly_hist_extra2, "16/mar"),("23/mar", weekly_hist_extra2, "23/mar"),
        ("30/mar", weekly_hist_extra,  "S4"),    ("06/abr", weekly_hist_extra,  "S3"),
        ("13/abr", weekly_driver,      "S2"),    ("20/abr", weekly_driver,      "S1"),
    ]:
        p   = sum(src.get(d,{}).get(key,(0,0,0))[0] for d in drivers)
        det = sum(src.get(d,{}).get(key,(0,0,0))[1] for d in drivers)
        s   = sum(src.get(d,{}).get(key,(0,0,0))[2] for d in drivers)
        weekly.append({"label": label, "nps": nps_safe(p,det,s), "s": s})
    return {"monthly": monthly, "weekly": weekly}

def make_panes(pfx, v):
    """Gera os dois panes (MES + SEMANA) para um conjunto de dados."""
    mD, wD, vt = v["mD"], v["wD"], v["vt"]

    def cards_mes():
        wm = v["worst_mom"]; bm = v["best_mom"]
        return (
            sc_nps("NPS CONSOLIDADO", v["nM1"], v["vs_tgt_mom"], v["dM"], "mes ant.", M1_LABEL) +
            sc_target(v["nps_target"], M1_LABEL) +
            sc_surveys(v["sM1"], v["surv_mom_var"], M1_LABEL) +
            sc_driver("DRIVER MAIS OFENSOR", wm,
                      mD[wm]["nps_b"], mD[wm]["share_b"],
                      "MoM", mD[wm]["var"], "WoW", wD[wm]["var"], vt[wm]["gap"],
                      v["rec_worst_mom"], is_worst=True) +
            sc_driver("DRIVER MAIS PROMOTOR", bm,
                      mD[bm]["nps_b"], mD[bm]["share_b"],
                      "MoM", mD[bm]["var"], "WoW", wD[bm]["var"], vt[bm]["gap"],
                      v["rec_best_mom"], is_worst=False)
        )

    def cards_sem():
        ww = v["worst_wow"]; bw = v["best_wow"]
        return (
            sc_nps("NPS CONSOLIDADO", v["nS1"], v["vs_tgt_wow"], v["dW"], "sem. ant.", S1_LABEL) +
            sc_target(v["nps_target"], M1_LABEL) +
            sc_surveys(v["sS1"], v["surv_wow_var"], S1_LABEL) +
            sc_driver("DRIVER MAIS OFENSOR", ww,
                      wD[ww]["nps_b"], wD[ww]["share_b"],
                      "WoW", wD[ww]["var"], "MoM", mD[ww]["var"], vt[ww]["gap"],
                      v["rec_worst_wow"], is_worst=True) +
            sc_driver("DRIVER MAIS PROMOTOR", bw,
                      wD[bw]["nps_b"], wD[bw]["share_b"],
                      "WoW", wD[bw]["var"], "MoM", mD[bw]["var"], vt[bw]["gap"],
                      v["rec_best_wow"], is_worst=False)
        )

    tt = v["tt"]
    initial_class = " active" if pfx == "all" else ""
    return f"""
  <div id="pane-{pfx}-mes" class="tab-pane{initial_class}">
    <div class="sc-grid">{cards_mes()}</div>
    <div class="chart-section">
      <div class="chart-title">NPS por Driver — Evolucao Mensal (Fev / Mar / Abr)</div>
      <div class="chart-sub">NPS por driver nos ultimos 3 meses | target consolidado: {v['nps_target']:.1f}%</div>
      <div id="evol-mes-{pfx}"></div>
    </div>
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
      <div class="chart-title">NPS por Driver — Evolucao Semanal (23/mar – 20/abr)</div>
      <div class="chart-sub">NPS por driver nas ultimas 5 semanas | target consolidado: {v['nps_target']:.1f}%</div>
      <div id="evol-sem-{pfx}"></div>
    </div>
    <div class="chart-section">
      <div class="chart-title">Impacto WoW - Abertura Driver</div>
      <div class="chart-sub">Contribuicao de cada driver (pp) na variacao consolidada {S2_LABEL} &rarr; {S1_LABEL}.</div>
      <div class="chart-wrap"><canvas id="c-{pfx}-wow"></canvas></div>
    </div>
  </div>"""

def build_html():

    dd_breakdown_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dd_breakdown.json')
    with open(dd_breakdown_path, encoding='utf-8') as f:
        dd_breakdown = json.load(f)
    dd_breakdown_json = json.dumps(dd_breakdown, ensure_ascii=False)

    dd_summaries_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dd_summaries.json')
    dd_summaries = {}
    if os.path.exists(dd_summaries_path):
        with open(dd_summaries_path, encoding='utf-8') as f:
            dd_summaries = json.load(f)
    dd_summaries_json = json.dumps(dd_summaries, ensure_ascii=False)

    def nps_safe(p, d, s):
        return round(100.0*(p-d)/s, 2) if s > 0 else None

    # Montar DD_DATA: por driver, dados mensais (Jan-Abr) e semanais (6 semanas)
    dd_data = {}
    MONTH_KEYS = [("Jan","Jan"),("Fev","Fev"),("Mar","M2"),("Abr","M1")]
    WEEK_KEYS  = [
        ("16/mar", "16/mar", weekly_hist_extra2),
        ("23/mar", "23/mar", weekly_hist_extra2),
        ("30/mar", "S4",     weekly_hist_extra),
        ("06/abr", "S3",     weekly_hist_extra),
        ("13/abr", "S2",     weekly_driver),
        ("20/abr", "S1",     weekly_driver),
    ]

    for drv in monthly_driver:
        monthly_pts = []
        for label, key in MONTH_KEYS:
            if key in ("M1","M2"):
                t = monthly_driver[drv][key]
            else:
                t = monthly_hist_extra.get(drv, {}).get(key, (0,0,0))
            n = nps_safe(*t)
            monthly_pts.append({"label": label, "p": t[0], "d": t[1], "s": t[2], "nps": n})

        weekly_pts = []
        for label, key, src in WEEK_KEYS:
            t = src.get(drv, {}).get(key, (0,0,0))
            n = nps_safe(*t)
            weekly_pts.append({"label": label, "p": t[0], "d": t[1], "s": t[2], "nps": n})

        dd_data[drv] = {
            "cat": CAT.get(drv, "?"),
            "target": DRIVER_TARGETS.get(drv),
            "monthly": monthly_pts,
            "weekly": weekly_pts,
        }

    dd_json = json.dumps(dd_data, ensure_ascii=False)

    # Gerar options HTML agrupado por categoria
    from collections import defaultdict
    cat_drivers = defaultdict(list)
    for drv in sorted(monthly_driver.keys()):
        cat_drivers[CAT.get(drv,"?")].append(drv)
    options_html = ""
    for cat in ["Longtail","Mature","Meli Pro","FBM","Buyers","Otros CV"]:
        drvs = cat_drivers.get(cat, [])
        if drvs:
            options_html += f'<optgroup label="{cat}">'
            for d in drvs:
                options_html += f'<option value="{d}">{d}</option>'
            options_html += '</optgroup>'

    panes_all = make_panes("all", V_ALL)
    panes_sel = make_panes("sel", V_SEL)

    # Historico NPS consolidado para os graficos de evolucao
    hist_all = compute_history(list(monthly_driver.keys()))
    hist_sel = compute_history([d for d in monthly_driver if d not in DRIVERS_EXCLUIDOS])
    hist_all_json = json.dumps(hist_all, ensure_ascii=False)
    hist_sel_json = json.dumps(hist_sel, ensure_ascii=False)

    drv_hist      = compute_driver_history()
    drv_hist_json = json.dumps(drv_hist, ensure_ascii=False)

    # js chart calls para os 6 graficos
    def js_charts(pfx, v):
        def safe(call):
            return f"try {{ {call} }} catch(e) {{ console.warn('chart {pfx}:', e); }}\n"
        return (
            safe(f"buildWaterfall('c-{pfx}-mom',{v['nM2']},{v['nM1']},'{M2_LABEL}','{M1_LABEL}',"
                 f"{v['mom_json']},{v['mom_ybase']});") +
            safe(f"buildWaterfall('c-{pfx}-wow',{v['nS2']},{v['nS1']},'{S2_LABEL}','{S1_LABEL}',"
                 f"{v['wow_json']},{v['wow_ybase']});") +
            safe(f"buildWaterfall('c-{pfx}-vt',{v['tt']},{v['nM1']},'Target Pond.','{M1_LABEL}',"
                 f"{v['vt_json']},{v['vt_ybase']});")
        )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NPS Driver Impact - All Sellers BR</title>
<script>
/* NAV: este bloco nao depende de Chart.js nem de dados externos */
var currentView='all',currentPeriod='mes';
var PERIOD_LABELS={{mes:'{M1_LABEL}',sem:'{S1_LABEL}'}};
function updatePanes(){{
  document.querySelectorAll('.tab-pane').forEach(function(p){{p.classList.remove('active');}});
  var el=document.getElementById('pane-'+currentView+'-'+currentPeriod);
  if(el)el.classList.add('active');
  var pl=document.getElementById('period-label');
  if(pl)pl.textContent=PERIOD_LABELS[currentPeriod]||'';
}}
function setView(btn){{
  currentView=btn.getAttribute('data-view');
  document.querySelectorAll('.view-btn').forEach(function(b){{b.classList.remove('active');}});
  btn.classList.add('active');
  updatePanes();
}}
function setPeriod(btn){{
  currentPeriod=btn.getAttribute('data-period');
  document.querySelectorAll('.period-btn').forEach(function(b){{b.classList.remove('active');}});
  btn.classList.add('active');
  updatePanes();
  if(currentView==='dd'){{
    var sel=document.getElementById('dd-select-'+currentPeriod);
    var other=document.getElementById('dd-select-'+(currentPeriod==='mes'?'sem':'mes'));
    if(sel&&other&&other.value){{sel.value=other.value;if(typeof renderDD!=='undefined')renderDD(currentPeriod);}}
  }}
}}
document.addEventListener('DOMContentLoaded',function(){{updatePanes();}});
// Wrapper seguro para renderDD — chama a funcao quando disponivel
function callRenderDD(period){{
  var cont=document.getElementById('dd-content-'+period);
  if(typeof renderDD==='undefined'){{
    if(cont)cont.innerHTML='<div style="padding:16px;color:#b71c1c;background:#ffebee;border-radius:8px">Erro: renderDD nao definido. Tente recarregar a pagina (Ctrl+Shift+R).</div>';
    return;
  }}
  renderDD(period);
}}
</script>
<script>{open('chartjs.min.js',encoding='utf-8').read()}</script>
<script>{open('chartjs-datalabels.min.js',encoding='utf-8').read()}</script>
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
.rec-full{{font-weight:700!important}}
.rec-partial{{color:#8a6000!important;font-weight:600}}
.rec-none{{color:#aaa!important;font-weight:400}}

/* ── Charts ── */
.chart-section{{background:#fff;border-radius:12px;padding:18px 22px;
                box-shadow:0 1px 4px rgba(0,0,0,.07)}}
.chart-title{{font-size:13px;font-weight:700;color:#1a1e3c;margin-bottom:3px}}
.chart-sub{{font-size:11px;color:#888;margin-bottom:12px}}
.chart-wrap{{position:relative;height:310px;width:100%}}

/* ── Deep Dive ── */
.dd-bar{{display:flex;align-items:center;gap:10px;margin-bottom:16px}}
.dd-label{{font-size:11px;font-weight:700;color:#555;text-transform:uppercase;letter-spacing:.5px}}
.dd-select{{padding:7px 12px;border:1px solid #d0d5e0;border-radius:7px;font-size:13px;
            background:#fff;color:#1a1e3c;min-width:280px;cursor:pointer}}
.dd-placeholder{{background:#fff;border-radius:12px;padding:40px;text-align:center;
                 box-shadow:0 1px 4px rgba(0,0,0,.07)}}
.dd-hint{{color:#aaa;font-size:13px}}
.dd-sc-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px}}
.dd-chart-section{{background:#fff;border-radius:12px;padding:18px 22px;
                   box-shadow:0 1px 4px rgba(0,0,0,.07);margin-bottom:16px}}
.dd-chart-title{{font-size:13px;font-weight:700;color:#1a1e3c;margin-bottom:3px}}
.dd-chart-sub{{font-size:11px;color:#888;margin-bottom:12px}}
.dd-chart-wrap{{position:relative;height:260px}}
.exec-summary{{background:#fff;border-radius:10px;padding:18px 20px;
               box-shadow:0 1px 4px rgba(0,0,0,.07);margin-bottom:16px;
               border-left:4px solid #1a1e3c}}
.exec-summary-title{{font-size:10px;font-weight:700;color:#1a1e3c;text-transform:uppercase;
                     letter-spacing:.7px;margin-bottom:10px}}
.exec-bullet{{font-size:12px;color:#333;line-height:1.6;margin-bottom:6px;
              padding-left:4px}}
.exec-bullet strong{{color:#1a1e3c}}
.exec-na{{font-size:12px;color:#aaa;font-style:italic}}
.dd-section-title{{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;
                   letter-spacing:.6px;margin:20px 0 10px;padding-bottom:6px;
                   border-bottom:1px solid #eee}}
.bk-wrap{{overflow-x:auto;margin-bottom:12px;border-radius:8px;
          box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.bk-table{{width:100%;border-collapse:collapse;background:#fff;
          font-size:12px;table-layout:fixed}}
.bk-table thead tr{{background:#f5f6fa;border-bottom:2px solid #e0e2ee}}
.bk-table thead th{{color:#666;padding:8px 10px;font-size:10px;font-weight:700;
                   text-transform:uppercase;letter-spacing:.5px;
                   white-space:nowrap;text-align:center}}
.bk-table thead th.col-name{{text-align:left;color:#1a1e3c}}
.bk-table tbody td{{padding:7px 10px;border-bottom:1px solid #f2f2f5;
                   vertical-align:middle;white-space:nowrap;
                   text-align:center;font-variant-numeric:tabular-nums;color:#333}}
.bk-table tbody td.col-name{{text-align:left;white-space:normal;
                             word-break:break-word;color:#1a1e3c;font-weight:500}}
.bk-table tbody tr:hover td{{background:#fafbff}}
.bk-table tbody tr.bk-total td{{background:#f0f2f8;font-weight:700;
                                border-top:2px solid #dde0ea;color:#1a1e3c}}
.bk-surv{{color:#bbb!important;font-size:11px!important}}
/* Pills */
.pill{{display:inline-block;padding:2px 9px;border-radius:12px;
       font-weight:700;font-size:11px;white-space:nowrap}}
.pill-pos-hi{{background:#e8f5e9;color:#1b5e20}}
.pill-pos-lo{{background:#f1f8e9;color:#33691e}}
.pill-neg-hi{{background:#ffebee;color:#b71c1c}}
.pill-neg-lo{{background:#fff3e0;color:#e65100}}
.pill-neu{{background:#f5f5f5;color:#777}}
.pill-up2{{background:#e8f5e9;color:#1b5e20}}
.pill-up1{{background:#f1f8e9;color:#33691e}}
.pill-flat{{background:#f5f5f5;color:#777}}
.pill-dn1{{background:#fff3e0;color:#e65100}}
.pill-dn2{{background:#ffebee;color:#b71c1c}}
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
    <button class="view-btn"        data-view="dd"  onclick="setView(this)">Deep Dive</button>
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

  <!-- ── DEEP DIVE ──────────────────────────────────────────────── -->
  <div id="pane-dd-mes" class="tab-pane">
    <div class="dd-bar">
      <label class="dd-label">Driver</label>
      <select id="dd-select-mes" class="dd-select" onchange="callRenderDD('mes')">
        <option value="">Selecione um driver...</option>
        {options_html}
      </select>
    </div>
    <div id="dd-content-mes" class="dd-placeholder">
      <div class="dd-hint">Selecione um driver acima para ver o detalhamento</div>
    </div>
  </div>

  <div id="pane-dd-sem" class="tab-pane">
    <div class="dd-bar">
      <label class="dd-label">Driver</label>
      <select id="dd-select-sem" class="dd-select" onchange="callRenderDD('sem')">
        <option value="">Selecione um driver...</option>
        {options_html}
      </select>
    </div>
    <div id="dd-content-sem" class="dd-placeholder">
      <div class="dd-hint">Selecione um driver acima para ver o detalhamento</div>
    </div>
  </div>
</div>

<script type="application/json" id="_dd_data">{dd_json}</script>
<script type="application/json" id="_dd_breakdown">{dd_breakdown_json}</script>
<script type="application/json" id="_dd_summaries">{dd_summaries_json}</script>
<script type="application/json" id="_hist_all">{hist_all_json}</script>
<script type="application/json" id="_hist_sel">{hist_sel_json}</script>
<script type="application/json" id="_drv_hist">{drv_hist_json}</script>
<script>
/* Funcoes de chart e deep dive */

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

function buildEvolTable(containerId, drivers, periodType, consolTarget) {{
  // drivers: array de strings (nomes dos drivers)
  // periodType: 'monthly' (3 cols: Fev/Mar/Abr) ou 'weekly' (5 cols: 23/mar-20/abr)
  var el = document.getElementById(containerId);
  if (!el) return;

  function pDelta(v) {{
    if(v===null||v===undefined) return '<span class="pill pill-neu">&mdash;</span>';
    var s=(v>=0?'+':'')+v.toFixed(2)+' pp';
    var c=v>=1?'pill-pos-hi':v>0?'pill-pos-lo':v>=-1?'pill-dn1':'pill-neg-hi';
    return '<span class="pill '+c+'">'+s+'</span>';
  }}
  function pTgt(nps, tgt) {{
    if(nps===null||!tgt) return '<span class="pill pill-neu">&mdash;</span>';
    var g=nps-tgt; var s=(g>=0?'+':'')+g.toFixed(2)+' pp';
    return '<span class="pill '+(g>=0?'pill-pos-hi':'pill-neg-hi')+'">'+s+'</span>';
  }}
  function pTend(d) {{
    if(d===null||d===undefined) return '<span class="pill pill-neu">&mdash;</span>';
    if(d>=3)  return '<span class="pill pill-up2">&#8679;&#8679; Em alta</span>';
    if(d>=0.5)return '<span class="pill pill-up1">&#8679; Evolucao</span>';
    if(d>-0.5)return '<span class="pill pill-flat">&#8594; Estavel</span>';
    if(d>-3)  return '<span class="pill pill-dn1">&#8681; Queda</span>';
    return '<span class="pill pill-dn2">&#8681;&#8681; Em queda</span>';
  }}
  function pRec(belowN, total, consecN) {{
    var tgtC = belowN===total?'pill-neg-hi':belowN>0?'pill-dn1':'pill-pos-hi';
    var tendC = consecN>=3?'pill-neg-hi':consecN>=2?'pill-dn1':'pill-flat';
    return '<span class="pill '+tgtC+'" title="Abaixo target">'+belowN+'/'+total+'</span>'+
           '&nbsp;<span class="pill '+tendC+'" title="Queda consecutiva">'+
           (consecN>0?consecN+' queda':'estavel')+'</span>';
  }}

  // Calcular colunas de periodo
  var cols = [];
  if (periodType === 'monthly') {{
    cols = drivers.map(function(d){{ return DRV_HIST[d]?DRV_HIST[d].monthly:[]; }});
  }} else {{
    cols = drivers.map(function(d){{ return DRV_HIST[d]?DRV_HIST[d].weekly:[]; }});
  }}
  if (!cols.length || !cols[0].length) {{ el.innerHTML='<div class="dd-hint">Sem dados</div>'; return; }}
  var periods = cols[0].map(function(p){{ return p.label; }});

  // Ordenar drivers por gap vs target do ultimo periodo (mais critico primeiro)
  var drvData = drivers.map(function(d,i){{
    var pts = cols[i];
    var last = pts[pts.length-1];
    var prev = pts[pts.length-2];
    var delta = (last&&prev&&last.nps!==null&&prev.nps!==null)?Math.round((last.nps-prev.nps)*100)/100:null;
    var tgt = DRV_HIST[d]?DRV_HIST[d].target:null;
    var gap = (last&&last.nps!==null&&tgt)?last.nps-tgt:null;
    // Recorrencia
    var below=0, consec=0;
    pts.forEach(function(p){{ if(p.nps!==null&&tgt&&p.nps<tgt) below++; }});
    for(var j=pts.length-1;j>0;j--){{
      if(pts[j].nps!==null&&pts[j-1].nps!==null&&pts[j].nps<pts[j-1].nps) consec++;
      else break;
    }}
    return {{d:d, pts:pts, delta:delta, gap:gap, tgt:tgt, below:below, consec:consec}};
  }});
  drvData.sort(function(a,b){{ return (a.gap||99)-(b.gap||99); }});  // mais abaixo do target primeiro

  // Cabeçalho
  var colW = Math.floor(35/periods.length);
  var colgroup = '<col style="width:22%">';
  periods.forEach(function(){{ colgroup+='<col style="width:'+colW+'%">'; }});
  colgroup += '<col style="width:10%"><col style="width:12%"><col style="width:12%"><col style="width:14%">';
  var head = '<tr><th class="col-name">Driver</th>';
  periods.forEach(function(p){{ head+='<th>'+p+'</th>'; }});
  head += '<th>Delta</th><th>vs Tgt Driver</th><th>vs Tgt Consol</th><th>Recorr.</th></tr>';

  var rows = drvData.map(function(r){{
    var cells = '';
    r.pts.forEach(function(p){{ cells+='<td>'+(p.nps!==null?p.nps.toFixed(1)+'%':'&mdash;')+'</td>'; }});
    var last = r.pts[r.pts.length-1];
    return '<tr>'+
      '<td class="col-name">'+r.d+'</td>'+
      cells+
      '<td>'+pDelta(r.delta)+'</td>'+
      '<td>'+pTgt(last?last.nps:null, r.tgt)+'</td>'+
      '<td>'+pTgt(last?last.nps:null, consolTarget)+'</td>'+
      '<td>'+pRec(r.below, r.pts.length, r.consec)+'</td>'+
      '</tr>';
  }}).join('');

  el.innerHTML='<div class="bk-wrap" style="overflow-x:auto"><table class="bk-table">'+
    '<colgroup>'+colgroup+'</colgroup>'+
    '<thead>'+head+'</thead><tbody>'+rows+'</tbody></table></div>';
}}

// Navegacao ja definida no head
updatePanes();
// Graficos: requestAnimationFrame garante que o layout foi processado antes de renderizar
try {{ Chart.register(ChartDataLabels); }} catch(e) {{ console.warn('Chart.register:', e); }}
requestAnimationFrame(function() {{
  requestAnimationFrame(function() {{
    {js_charts("all", V_ALL)}{js_charts("sel", V_SEL)}
    var allDrvs = Object.keys(DRV_HIST);
    var selDrvs = allDrvs.filter(function(d){{ return {json.dumps(list(monthly_driver_sel.keys()))}.indexOf(d)>=0; }});
    try {{ buildEvolTable('evol-mes-all', allDrvs, 'monthly', {V_ALL['nps_target']}); }} catch(e) {{ console.warn('evol-mes-all',e); }}
    try {{ buildEvolTable('evol-sem-all', allDrvs, 'weekly',  {V_ALL['nps_target']}); }} catch(e) {{ console.warn('evol-sem-all',e); }}
    try {{ buildEvolTable('evol-mes-sel', selDrvs, 'monthly', {V_SEL['nps_target']}); }} catch(e) {{ console.warn('evol-mes-sel',e); }}
    try {{ buildEvolTable('evol-sem-sel', selDrvs, 'weekly',  {V_SEL['nps_target']}); }} catch(e) {{ console.warn('evol-sem-sel',e); }}
  }});
}});

// Carregar dados dos elementos JSON (evita problemas de parsing JS com caracteres especiais)
var DD_DATA      = JSON.parse(document.getElementById('_dd_data').textContent);
var DD_BREAKDOWN = JSON.parse(document.getElementById('_dd_breakdown').textContent);
var DD_SUMMARIES = JSON.parse(document.getElementById('_dd_summaries').textContent);
var HIST_ALL     = JSON.parse(document.getElementById('_hist_all').textContent);
var HIST_SEL     = JSON.parse(document.getElementById('_hist_sel').textContent);
var DRV_HIST     = JSON.parse(document.getElementById('_drv_hist').textContent);
var M1_LABEL = '{M1_LABEL}';
var M2_LABEL = '{M2_LABEL}';
var S1_LABEL = '{S1_LABEL}';
var S2_LABEL = '{S2_LABEL}';
var ddCharts = {{}};

function buildExecSummary(drv, period) {{
  var s = DD_SUMMARIES[drv];
  var key = period === 'mes' ? 'mom' : 'wow';
  var text = s && s[key] ? s[key] : null;
  var title = period === 'mes' ? 'Resumo Executivo — MoM (Marco vs Abril 2026)' : 'Resumo Executivo — WoW (13-19/abr vs 20-26/abr)';
  if (!text) {{
    var fallback = (period === 'sem' && s && s['mom'])
      ? '<div class="exec-na">⚠ Resumo WoW nao gerado ainda. Exibindo analise MoM como referencia.</div>' + s['mom']
      : null;
    if (!fallback) {{
      return '<div class="exec-summary"><div class="exec-summary-title">' + title + '</div>' +
             '<div class="exec-na">Analise qualitativa nao disponivel para este driver.</div></div>';
    }}
    text = fallback;
  }}
  var bullets = text.split('\\n').filter(function(l){{ return l.trim(); }});
  var html = '<div class="exec-summary"><div class="exec-summary-title">' + title + '</div>';
  bullets.forEach(function(b) {{
    var clean = b.replace(/^[▶\s]+/, '').trim();
    if (!clean) return;
    // Destaque da primeira parte antes do ':'
    var colon = clean.indexOf(':');
    if (colon > 0 && colon < 40) {{
      clean = '<strong>' + clean.substring(0, colon+1) + '</strong>' + clean.substring(colon+1);
    }}
    html += '<div class="exec-bullet">▶ ' + clean + '</div>';
  }});
  html += '</div>';
  return html;
}}

function renderDD(period) {{
  var selectId = 'dd-select-' + period;
  var contentId = 'dd-content-' + period;
  var drv = document.getElementById(selectId).value;
  var content = document.getElementById(contentId);

  // Sincronizar selects
  var otherPeriod = period === 'mes' ? 'sem' : 'mes';
  var otherSelect = document.getElementById('dd-select-' + otherPeriod);
  if (otherSelect) otherSelect.value = drv;

  if (!drv || !DD_DATA[drv]) {{
    content.innerHTML = '<div class="dd-placeholder"><div class="dd-hint">Selecione um driver acima para ver o detalhamento</div></div>';
    return;
  }}

  var d = DD_DATA[drv];
  var tgt = d.target;

  // Destruir charts antigos deste period
  if (ddCharts[period]) {{ ddCharts[period].forEach(function(c){{ if(c) c.destroy(); }}); }}
  ddCharts[period] = [];

  function fmtNPS(v) {{ return v !== null ? v.toFixed(1)+'%' : '—'; }}
  function fmtDelta(v) {{ if(v===null||v===undefined) return '—'; var s=v>=0?'+':''; return s+v.toFixed(2)+' pp'; }}

  if (period === 'mes') {{
    var pts = d.monthly;
    var cur = pts[pts.length-1];
    var prev = pts[pts.length-2];
    var nCur  = cur.nps;
    var nPrev = prev.nps;
    var delta = (nCur !== null && nPrev !== null) ? parseFloat((nCur - nPrev).toFixed(2)) : null;
    var gapTgt = (nCur !== null && tgt) ? parseFloat((nCur - tgt).toFixed(2)) : null;

    content.innerHTML =
      '<div class="dd-sc-grid">' +
        sc_dd('NPS '+cur.label, fmtNPS(nCur), null, nCur, tgt) +
        sc_dd('NPS '+prev.label, fmtNPS(nPrev), null, nPrev, tgt) +
        sc_dd('Variacao MoM', fmtDelta(delta), delta, null, null) +
        sc_dd('Target', tgt ? tgt.toFixed(1)+'%' : '—', null, null, null) +
        sc_dd('Gap vs Target', fmtDelta(gapTgt), gapTgt, null, null) +
      '</div>' +
      '<div class="dd-chart-section">' +
        '<div class="dd-chart-title">Historico Mensal — '+drv+'</div>' +
        '<div class="dd-chart-sub">NPS mensal Jan–Abr 2026 vs target do driver</div>' +
        '<div class="dd-chart-wrap"><canvas id="c-dd-mes-chart"></canvas></div>' +
      '</div>' +
      buildExecSummary(drv, 'mes') +
      '<div class="dd-section-title">Processos — MoM (' + M2_LABEL + ' vs ' + M1_LABEL + ')</div>' +
      buildBreakdownTable(DD_BREAKDOWN[drv], 'P', 'M2', 'M1', d.target, 'Processo') +
      '<div class="dd-section-title">Canal — MoM</div>' +
      buildBreakdownTable(DD_BREAKDOWN[drv], 'C', 'M2', 'M1', d.target, 'Canal') +
      '<div class="dd-section-title">Oficina — MoM</div>' +
      buildBreakdownTable(DD_BREAKDOWN[drv], 'O', 'M2', 'M1', d.target, 'Oficina');

    var labels = pts.map(function(p){{ return p.label; }});
    var values = pts.map(function(p){{ return p.nps; }});
    var colors = values.map(function(v){{ return (tgt && v !== null && v < tgt) ? 'rgba(210,45,45,0.82)' : 'rgba(30,65,150,0.82)'; }});
    ddCharts[period].push(buildDDChart('c-dd-mes-chart', labels, values, colors, tgt, 'mensal'));

  }} else {{
    var pts = d.weekly;
    var cur = pts[pts.length-1];
    var prev = pts[pts.length-2];
    var nCur  = cur.nps;
    var nPrev = prev.nps;
    var delta = (nCur !== null && nPrev !== null) ? parseFloat((nCur - nPrev).toFixed(2)) : null;
    var gapTgt = (nCur !== null && tgt) ? parseFloat((nCur - tgt).toFixed(2)) : null;

    content.innerHTML =
      '<div class="dd-sc-grid">' +
        sc_dd('NPS '+cur.label, fmtNPS(nCur), null, nCur, tgt) +
        sc_dd('NPS '+prev.label, fmtNPS(nPrev), null, nPrev, tgt) +
        sc_dd('Variacao WoW', fmtDelta(delta), delta, null, null) +
        sc_dd('Target', tgt ? tgt.toFixed(1)+'%' : '—', null, null, null) +
        sc_dd('Gap vs Target', fmtDelta(gapTgt), gapTgt, null, null) +
      '</div>' +
      '<div class="dd-chart-section">' +
        '<div class="dd-chart-title">Historico Semanal — '+drv+'</div>' +
        '<div class="dd-chart-sub">NPS semanal 6 semanas vs target do driver</div>' +
        '<div class="dd-chart-wrap"><canvas id="c-dd-sem-chart"></canvas></div>' +
      '</div>' +
      buildExecSummary(drv, 'sem') +
      '<div class="dd-section-title">Processos — WoW (' + S2_LABEL + ' vs ' + S1_LABEL + ')</div>' +
      buildBreakdownTable(DD_BREAKDOWN[drv], 'P', 'S2', 'S1', d.target, 'Processo') +
      '<div class="dd-section-title">Canal — WoW</div>' +
      buildBreakdownTable(DD_BREAKDOWN[drv], 'C', 'S2', 'S1', d.target, 'Canal') +
      '<div class="dd-section-title">Oficina — WoW</div>' +
      buildBreakdownTable(DD_BREAKDOWN[drv], 'O', 'S2', 'S1', d.target, 'Oficina');

    var labels = pts.map(function(p){{ return p.label; }});
    var values = pts.map(function(p){{ return p.nps; }});
    var colors = values.map(function(v){{ return (tgt && v !== null && v < tgt) ? 'rgba(210,45,45,0.82)' : 'rgba(30,65,150,0.82)'; }});
    ddCharts[period].push(buildDDChart('c-dd-sem-chart', labels, values, colors, tgt, 'semanal'));
  }}
}}

function buildBreakdownTable(drvData, dim, periodA, periodB, drvTarget, dimLabel) {{
    if (!drvData || !drvData[dim]) return '<div class="dd-hint">Sem dados</div>';

    var dataA = drvData[dim][periodA] || {{}};
    var dataB = drvData[dim][periodB] || {{}};
    var keys  = Array.from(new Set(Object.keys(dataA).concat(Object.keys(dataB))));
    if (keys.length === 0) return '<div class="dd-hint">Sem dados para este periodo</div>';

    // Totais para share e NPS consolidado do driver
    var totA={{p:0,d:0,s:0}}, totB={{p:0,d:0,s:0}};
    keys.forEach(function(k) {{
        var a=dataA[k]||{{}}; var b=dataB[k]||{{}};
        totA.p+=a.p||0; totA.d+=a.d||0; totA.s+=a.s||0;
        totB.p+=b.p||0; totB.d+=b.d||0; totB.s+=b.s||0;
    }});
    var npsA_tot = totA.s>0 ? (totA.p-totA.d)/totA.s*100 : null;
    var npsB_tot = totB.s>0 ? (totB.p-totB.d)/totB.s*100 : null;

    // MIX+NETO por item
    var items = keys.map(function(k) {{
        var a=dataA[k]||{{p:0,d:0,s:0,nps:null}};
        var b=dataB[k]||{{p:0,d:0,s:0,nps:null}};
        var shaA=totA.s>0?a.s/totA.s:0, shaB=totB.s>0?b.s/totB.s:0;
        var nA=a.nps, nB=b.nps;
        var neto=(shaA>0&&nA!==null&&nB!==null)?shaA*(nB-nA):0;
        var mix=(nB!==null&&npsB_tot!==null)?(shaB-shaA)*(nB-npsB_tot):0;
        return {{k:k,a:a,b:b,shaB:shaB,
                 impact:Math.round((neto+mix)*100)/100}};
    }});
    items.sort(function(x,y){{ return Math.abs(y.impact)-Math.abs(x.impact); }});

    var lA = periodA==='M2'?'Mar/26':(periodA==='S2'?'13/abr':periodA);
    var lB = periodB==='M1'?'Abr/26':(periodB==='S1'?'20/abr':periodB);

    // Helpers visuais
    function fN(v) {{ return v!==null ? v.toFixed(2) : '&mdash;'; }}
    function pillDelta(v) {{
        if(v===null) return '<span class="pill pill-neu">&mdash;</span>';
        var s=(v>=0?'+':'')+v.toFixed(2)+' pp';
        var c=v>=1?'pill-pos-hi':v>=0?'pill-pos-lo':v>=-1?'pill-dn1':'pill-neg-hi';
        return '<span class="pill '+c+'">'+s+'</span>';
    }}
    function pillVsTarget(nps) {{
        if(nps===null||drvTarget===null||drvTarget===undefined)
            return '<span class="pill pill-neu">&mdash;</span>';
        var g=nps-drvTarget;
        var s=(g>=0?'+':'')+g.toFixed(2)+' pp';
        var c=g>=0?'pill-pos-hi':'pill-neg-hi';
        return '<span class="pill '+c+'">'+s+'</span>';
    }}
    function pillImpacto(v) {{
        if(v===0) return '<span class="pill pill-neu">0,00 pp</span>';
        var s=(v>=0?'+':'')+v.toFixed(2)+' pp';
        var c=v>=0.3?'pill-pos-hi':v>=0.05?'pill-pos-lo':v<=-0.3?'pill-neg-hi':v<=-0.05?'pill-dn1':'pill-neu';
        return '<span class="pill '+c+'">'+s+'</span>';
    }}
    function pillTendencia(delta) {{
        if(delta===null) return '<span class="pill pill-neu">&mdash;</span>';
        if(delta>=3)  return '<span class="pill pill-up2">&#8679;&#8679; Em alta</span>';
        if(delta>=0.5)return '<span class="pill pill-up1">&#8679; Evolucao</span>';
        if(delta>-0.5)return '<span class="pill pill-flat">&#8594; Estavel</span>';
        if(delta>-3)  return '<span class="pill pill-dn1">&#8681; Queda</span>';
        return '<span class="pill pill-dn2">&#8681;&#8681; Em queda</span>';
    }}

    var html = '<div class="bk-wrap"><table class="bk-table">' +
        '<colgroup>' +
        '<col style="width:24%"><col style="width:8%"><col style="width:8%">' +
        '<col style="width:11%"><col style="width:8%"><col style="width:6%">' +
        '<col style="width:11%"><col style="width:12%"><col style="width:12%">' +
        '</colgroup>' +
        '<thead><tr>' +
        '<th class="col-name">' + (dimLabel||'Dimensao') + '</th>' +
        '<th>' + lA + '</th><th>' + lB + '</th>' +
        '<th>&Delta; NPS</th><th>Surveys</th><th>Share</th>' +
        '<th>Impacto</th><th>VS Target</th><th>Tendencia</th>' +
        '</tr></thead><tbody>';

    var totImpact=0;
    items.forEach(function(item) {{
        var a=item.a, b=item.b;
        var delta=(a.nps!==null&&b.nps!==null)?Math.round((b.nps-a.nps)*100)/100:null;
        totImpact+=item.impact;
        html += '<tr>' +
            '<td class="col-name">' + item.k + '</td>' +
            '<td>' + fN(a.nps) + '</td>' +
            '<td>' + fN(b.nps) + '</td>' +
            '<td>' + pillDelta(delta) + '</td>' +
            '<td class="bk-surv">' + (b.s||0).toLocaleString('pt-BR') + '</td>' +
            '<td class="bk-surv">' + (item.shaB*100).toFixed(1)+'%</td>' +
            '<td>' + pillImpacto(item.impact) + '</td>' +
            '<td>' + pillVsTarget(b.nps) + '</td>' +
            '<td>' + pillTendencia(delta) + '</td>' +
            '</tr>';
    }});

    var totDelta=(npsA_tot!==null&&npsB_tot!==null)?Math.round((npsB_tot-npsA_tot)*100)/100:null;
    totImpact=Math.round(totImpact*100)/100;
    html += '<tr class="bk-total">' +
        '<td class="col-name">Total driver</td>' +
        '<td>' + fN(npsA_tot) + '</td>' +
        '<td>' + fN(npsB_tot) + '</td>' +
        '<td>' + pillDelta(totDelta) + '</td>' +
        '<td class="bk-surv">' + totB.s.toLocaleString('pt-BR') + '</td>' +
        '<td class="bk-surv">100%</td>' +
        '<td>' + pillImpacto(totImpact) + '</td>' +
        '<td>' + pillVsTarget(npsB_tot) + '</td>' +
        '<td>' + pillTendencia(totDelta) + '</td>' +
        '</tr>';

    html += '</tbody></table></div>';
    return html;
}}

function sc_dd(label, val, delta, npsVal, tgt) {{
  var valColor = '';
  if (npsVal !== null && tgt !== null && tgt !== undefined) {{
    valColor = npsVal >= tgt ? 'color:#1a7a1a' : 'color:#c0321a';
  }} else if (delta !== null && delta !== undefined) {{
    valColor = delta >= 0 ? 'color:#1a7a1a' : 'color:#c0321a';
  }} else {{
    valColor = 'color:#bf5c00';
  }}
  return '<div class="sc">' +
    '<div class="sc-label">'+label+'</div>' +
    '<div class="sc-val" style="font-size:24px;'+valColor+'">'+val+'</div>' +
  '</div>';
}}

function buildDDChart(canvasId, labels, values, colors, target, type) {{
  var datasets = [{{
    label: 'NPS', data: values,
    backgroundColor: colors, borderWidth: 0, borderRadius: 3
  }}];
  if (target) {{
    datasets.push({{
      label: 'Target', data: Array(labels.length).fill(target),
      type: 'line', borderColor: 'rgba(191,92,0,0.9)', borderWidth: 2,
      borderDash: [5,4], pointRadius: 0, fill: false,
      tension: 0
    }});
  }}
  var allVals = values.filter(function(v){{ return v !== null; }}).concat(target ? [target] : []);
  var yMin = allVals.length ? Math.floor(Math.min.apply(null,allVals)) - 5 : 0;
  var yMax = allVals.length ? Math.ceil(Math.max.apply(null,allVals)) + 5 : 100;

  return new Chart(document.getElementById(canvasId), {{
    type: 'bar',
    plugins: [ChartDataLabels],
    data: {{ labels: labels, datasets: datasets }},
    options: {{
      responsive: true, maintainAspectRatio: false, animation: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{ enabled: true }},
        datalabels: {{
          display: function(ctx){{ return ctx.dataset.type !== 'line'; }},
          formatter: function(v){{ return v !== null ? v.toFixed(1)+'%' : ''; }},
          anchor: 'end', align: 'top',
          font: {{ size: 10, weight: '600' }}, color: '#333', padding: 2
        }}
      }},
      layout: {{ padding: {{ top: 24 }} }},
      scales: {{
        y: {{ min: yMin, max: yMax, display: true,
              ticks: {{ callback: function(v){{ return v+'%'; }}, font: {{ size: 10 }} }},
              grid: {{ color: '#f0f0f0' }} }},
        x: {{ ticks: {{ font: {{ size: 10 }}, color: '#555' }},
              grid: {{ display: false }}, border: {{ display: false }} }}
      }}
    }}
  }});
}}

// updatePanes() ja foi chamado antes dos graficos acima
</script>
<script>
// Diagnostico: roda DEPOIS do script principal, em bloco separado
(function() {{
  var st = [];
  st.push('renderDD=' + typeof renderDD);
  st.push('DD_DATA=' + typeof DD_DATA);
  st.push('DD_BREAKDOWN=' + typeof DD_BREAKDOWN);
  st.push('DD_SUMMARIES=' + typeof DD_SUMMARIES);
  st.push('buildWaterfall=' + typeof buildWaterfall);
  var msg = st.join(' | ');
  var div = document.createElement('div');
  div.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#1a1e3c;color:#aab4d4;padding:6px 12px;font-size:11px;font-family:monospace;z-index:9999';
  div.textContent = msg;
  document.body.appendChild(div);
}})();
</script>
</body>
</html>"""

def escape_nonascii_in_scripts(html):
    """Escapa chars nao-ASCII dentro de blocos <script> (exceto application/json)."""
    import re
    def fix_block(m):
        tag_open = m.group(1)
        content  = m.group(2)
        # Escapar todo char > 127 como \uXXXX
        safe = ''.join(
            c if ord(c) <= 127 else '\\u{:04x}'.format(ord(c))
            for c in content
        )
        return tag_open + safe + '</script>'
    # Apenas scripts sem type (ou type diferente de application/json)
    return re.sub(
        r'(<script(?! src| type)[^>]*>)(.*?)</script>',
        fix_block,
        html,
        flags=re.DOTALL
    )

if __name__ == "__main__":
    html = build_html()
    html = escape_nonascii_in_scripts(html)
    with open("driver_impact.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("OK driver_impact.html gerado -", REPORT_DATE)
    print("  [ALL] MoM:", V_ALL["nM2"], "->", V_ALL["nM1"], "(", V_ALL["dM"], "pp)")
    print("  [ALL] WoW:", V_ALL["nS2"], "->", V_ALL["nS1"], "(", V_ALL["dW"], "pp)")
    print("  [SEL] MoM:", V_SEL["nM2"], "->", V_SEL["nM1"], "(", V_SEL["dM"], "pp)")
    print("  [SEL] WoW:", V_SEL["nS2"], "->", V_SEL["nS1"], "(", V_SEL["dW"], "pp)")
