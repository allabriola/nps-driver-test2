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
S1_LABEL          = "27/abr - 03/mai"
S2_LABEL          = "20/abr - 26/abr"
VIG_LABEL         = "04/mai"             # semana atual (parcial)
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
    "CBT":                               {"M2": (323, 58, 395),    "M1": (327, 50, 383)},
    "Experiencia Impositiva Mature":     {"M2": (45, 20, 72),      "M1": (26, 7, 38)},
    "Experiencia Impositiva Meli Pro":   {"M2": (8, 4, 13),        "M1": (13, 2, 17)},
    "Experiencia Impositiva Seller Dev": {"M2": (312, 108, 469),   "M1": (382, 108, 544)},
    "FBM-S Mature":                      {"M2": (130, 45, 203),    "M1": (93, 27, 129)},
    "FBM-S Meli Pro":                    {"M2": (11, 8, 22),       "M1": (48, 9, 62)},
    "FBM-S Seller Dev":                  {"M2": (347, 125, 524),   "M1": (312, 105, 458)},
    "ME Vendedor Mature":                {"M2": (1618, 314, 2184), "M1": (952, 198, 1234)},
    "ME Vendedor Meli Pro":              {"M2": (60, 10, 75),      "M1": (285, 25, 322)},
    "ME Vendedor Seller Dev":            {"M2": (4958, 754, 6266), "M1": (4932, 706, 6196)},
    "Otros CV":                          {"M2": (775, 182, 1047),  "M1": (683, 224, 966)},
    "PCF Vendedor Mature":               {"M2": (332, 85, 467),    "M1": (213, 64, 310)},
    "PCF Vendedor Meli Pro":             {"M2": (32, 8, 44),       "M1": (223, 37, 293)},
    "PCF Vendedor Seller Dev":           {"M2": (536, 166, 790),   "M1": (356, 106, 512)},
    "PDD DS&XD - Vendedor":              {"M2": (645, 486, 1280),  "M1": (492, 387, 973)},
    "PDD FBM - Vendedor":                {"M2": (193, 89, 306),    "M1": (159, 85, 269)},
    "PDD Fotos - Vendedor":              {"M2": (46, 22, 72),      "M1": (31, 23, 59)},
    "PDD MP,FLEX & CBT - Vendedor":      {"M2": (87, 58, 166),     "M1": (56, 41, 110)},
    "PNR ME - Vendedor":                 {"M2": (103, 71, 193),    "M1": (139, 83, 238)},
    "PNR MP - Vendedor":                 {"M2": (140, 90, 266),    "M1": (148, 67, 236)},
    "Partners":                          {"M2": (2228, 337, 2806), "M1": (2070, 333, 2638)},
    "Post Venta Mature":                 {"M2": (392, 76, 520),    "M1": (275, 45, 354)},
    "Post Venta Meli Pro":               {"M2": (70, 10, 81),      "M1": (334, 13, 357)},
    "Post Venta Seller Dev":             {"M2": (929, 178, 1186),  "M1": (780, 111, 967)},
    "Publicaciones Mature":              {"M2": (258, 51, 345),    "M1": (177, 36, 247)},
    "Publicaciones Meli Pro":            {"M2": (18, 7, 26),       "M1": (145, 15, 167)},
    "Publicaciones Seller Dev":          {"M2": (2639, 374, 3309), "M1": (1898, 334, 2439)},
}

weekly_driver = {
    "CBT":                               {"S2": (77, 16, 96),     "S1": (56, 10, 67),     "VIG": (0, 0, 0)},
    "Experiencia Impositiva Mature":     {"S2": (2, 0, 4),        "S1": (5, 0, 5),        "VIG": (0, 0, 0)},
    "Experiencia Impositiva Meli Pro":   {"S2": (3, 0, 3),        "S1": (5, 2, 7),        "VIG": (0, 0, 0)},
    "Experiencia Impositiva Seller Dev": {"S2": (57, 23, 88),     "S1": (50, 13, 70),     "VIG": (0, 0, 0)},
    "FBM-S Mature":                      {"S2": (17, 4, 21),      "S1": (13, 3, 20),      "VIG": (0, 0, 0)},
    "FBM-S Meli Pro":                    {"S2": (17, 0, 20),      "S1": (13, 1, 18),      "VIG": (0, 0, 0)},
    "FBM-S Seller Dev":                  {"S2": (85, 29, 121),    "S1": (79, 25, 107),    "VIG": (0, 0, 0)},
    "ME Vendedor Mature":                {"S2": (146, 34, 186),   "S1": (96, 22, 130),    "VIG": (0, 0, 0)},
    "ME Vendedor Meli Pro":              {"S2": (104, 10, 120),   "S1": (110, 4, 120),    "VIG": (0, 0, 0)},
    "ME Vendedor Seller Dev":            {"S2": (1058, 152, 1308),"S1": (1166, 134, 1420),"VIG": (0, 0, 0)},
    "Otros CV":                          {"S2": (183, 68, 260),   "S1": (159, 41, 220),   "VIG": (0, 0, 0)},
    "PCF Vendedor Mature":               {"S2": (21, 9, 34),      "S1": (23, 7, 33),      "VIG": (0, 0, 0)},
    "PCF Vendedor Meli Pro":             {"S2": (101, 14, 131),   "S1": (91, 12, 111),    "VIG": (0, 0, 0)},
    "PCF Vendedor Seller Dev":           {"S2": (82, 30, 129),    "S1": (81, 26, 119),    "VIG": (0, 0, 0)},
    "PDD DS&XD - Vendedor":              {"S2": (115, 76, 214),   "S1": (111, 94, 219),   "VIG": (0, 0, 0)},
    "PDD FBM - Vendedor":                {"S2": (43, 25, 74),     "S1": (38, 18, 63),     "VIG": (0, 0, 0)},
    "PDD Fotos - Vendedor":              {"S2": (10, 7, 20),      "S1": (7, 2, 12),       "VIG": (0, 0, 0)},
    "PDD MP,FLEX & CBT - Vendedor":      {"S2": (8, 10, 19),      "S1": (19, 12, 37),     "VIG": (0, 0, 0)},
    "PNR ME - Vendedor":                 {"S2": (63, 41, 110),    "S1": (37, 24, 66),     "VIG": (0, 0, 0)},
    "PNR MP - Vendedor":                 {"S2": (28, 25, 57),     "S1": (38, 12, 61),     "VIG": (0, 0, 0)},
    "Partners":                          {"S2": (567, 85, 719),   "S1": (548, 99, 717),   "VIG": (0, 0, 0)},
    "Post Venta Mature":                 {"S2": (46, 6, 58),      "S1": (42, 8, 57),      "VIG": (0, 0, 0)},
    "Post Venta Meli Pro":               {"S2": (149, 1, 152),    "S1": (135, 7, 150),    "VIG": (0, 0, 0)},
    "Post Venta Seller Dev":             {"S2": (177, 18, 209),   "S1": (175, 19, 217),   "VIG": (0, 0, 0)},
    "Publicaciones Mature":              {"S2": (25, 3, 30),      "S1": (19, 1, 22),      "VIG": (0, 0, 0)},
    "Publicaciones Meli Pro":            {"S2": (59, 4, 64),      "S1": (81, 5, 89),      "VIG": (0, 0, 0)},
    "Publicaciones Seller Dev":          {"S2": (398, 76, 512),   "S1": (381, 88, 517),   "VIG": (0, 0, 0)},
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

# S2_old=13/abr-19/abr | S3=06/abr-12/abr | S4=30/mar-05/abr  (histórico fechado)
weekly_hist_extra = {
    "CBT":                               {"S2_old": (87, 15, 102),  "S3": (87, 12, 101),   "S4": (75, 9, 86)},
    "Experiencia Impositiva Mature":     {"S2_old": (6, 2, 8),      "S3": (9, 3, 13),      "S4": (12, 5, 20)},
    "Experiencia Impositiva Meli Pro":   {"S2_old": (2, 1, 4),      "S3": (1, 0, 2),       "S4": (2, 1, 3)},
    "Experiencia Impositiva Seller Dev": {"S2_old": (112, 33, 160), "S3": (150, 36, 208),  "S4": (66, 25, 100)},
    "FBM-S Mature":                      {"S2_old": (23, 4, 29),    "S3": (28, 7, 40),     "S4": (30, 13, 48)},
    "FBM-S Meli Pro":                    {"S2_old": (14, 6, 20),    "S3": (9, 2, 12),      "S4": (0, 2, 2)},
    "FBM-S Seller Dev":                  {"S2_old": (68, 24, 101),  "S3": (74, 24, 115),   "S4": (73, 23, 104)},
    "ME Vendedor Mature":                {"S2_old": (222, 44, 286), "S3": (374, 82, 492),  "S4": (340, 56, 438)},
    "ME Vendedor Meli Pro":              {"S2_old": (76, 4, 83),    "S3": (24, 6, 30),     "S4": (10, 6, 17)},
    "ME Vendedor Seller Dev":            {"S2_old": (1154,178,1482),"S3": (1676,224,2106), "S4": (1016,158,1270)},
    "Otros CV":                          {"S2_old": (158, 56, 230), "S3": (181, 63, 259),  "S4": (139, 36, 195)},
    "PCF Vendedor Mature":               {"S2_old": (51, 19, 81),   "S3": (97, 24, 131),   "S4": (68, 14, 91)},
    "PCF Vendedor Meli Pro":             {"S2_old": (67, 12, 89),   "S3": (13, 3, 19),     "S4": (4, 3, 7)},
    "PCF Vendedor Seller Dev":           {"S2_old": (95, 28, 137),  "S3": (98, 29, 136),   "S4": (84, 23, 125)},
    "PDD DS&XD - Vendedor":              {"S2_old": (135,107, 261), "S3": (113, 95, 236),  "S4": (136,106, 275)},
    "PDD FBM - Vendedor":                {"S2_old": (38, 25, 72),   "S3": (40, 18, 65),    "S4": (45, 16, 63)},
    "PDD Fotos - Vendedor":              {"S2_old": (8, 8, 17),     "S3": (7, 5, 12),      "S4": (9, 5, 15)},
    "PDD MP,FLEX & CBT - Vendedor":      {"S2_old": (21, 11, 39),   "S3": (16, 9, 28),     "S4": (14, 7, 24)},
    "PNR ME - Vendedor":                 {"S2_old": (23, 10, 37),   "S3": (21, 15, 38),    "S4": (18, 9, 30)},
    "PNR MP - Vendedor":                 {"S2_old": (32, 13, 49),   "S3": (54, 16, 74),    "S4": (33, 15, 56)},
    "Partners":                          {"S2_old": (575, 85, 725), "S3": (460, 76, 587),  "S4": (448, 77, 574)},
    "Post Venta Mature":                 {"S2_old": (76, 11, 97),   "S3": (89, 15, 117),   "S4": (88, 20, 114)},
    "Post Venta Meli Pro":               {"S2_old": (104, 5, 112),  "S3": (25, 2, 29),     "S4": (8, 0, 9)},
    "Post Venta Seller Dev":             {"S2_old": (194, 23, 233), "S3": (239, 39, 301),  "S4": (176, 39, 233)},
    "Publicaciones Mature":              {"S2_old": (37, 14, 57),   "S3": (72, 12, 101),   "S4": (61, 13, 87)},
    "Publicaciones Meli Pro":            {"S2_old": (37, 4, 44),    "S3": (6, 1, 8),       "S4": (6, 1, 8)},
    "Publicaciones Seller Dev":          {"S2_old": (453, 80, 587), "S3": (607,103, 769),  "S4": (502, 88, 653)},
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
    dW_  = round((nS1_ or 0) - (nS2_ or 0), 2)
    wD_  = mix_neto(weekly_data, "S2", "S1", sS2_, sS1_, nS1_ or 0)

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
        vs_tgt_mom=round((nM1_ or 0) - nps_target_consol, 2),
        vs_tgt_wow=round((nS1_ or 0) - nps_target_consol, 2),
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

# View VIGENTE: usa VIG como periodo "atual" comparado com S1
def compute_vig(monthly_data, weekly_data, nps_target_consol):
    """Calcula NPS vigente (semana atual parcial) vs S1 (semana fechada)."""
    def nps_s(p, d, s): return round(100*(p-d)/s, 2) if s > 0 else None
    pVig = sum(weekly_data[d]["VIG"][0] for d in weekly_data if "VIG" in weekly_data[d])
    dVig = sum(weekly_data[d]["VIG"][1] for d in weekly_data if "VIG" in weekly_data[d])
    sVig = sum(weekly_data[d]["VIG"][2] for d in weekly_data if "VIG" in weekly_data[d])
    pS1  = sum(weekly_data[d]["S1"][2] and weekly_data[d]["S1"][0] for d in weekly_data)
    dS1  = sum(weekly_data[d]["S1"][1] for d in weekly_data)
    sS1  = sum(weekly_data[d]["S1"][2] for d in weekly_data)
    nVig = nps_s(pVig, dVig, sVig)
    nS1  = nps_s(sum(weekly_data[d]["S1"][0] for d in weekly_data), dS1, sS1)
    dW   = round(nVig - nS1, 2) if nVig is not None and nS1 is not None else 0
    mD   = mix_neto({d: {"M2": monthly_data[d]["M2"], "M1": monthly_data[d]["M1"]}
                     for d in monthly_data}, "M2", "M1",
                    sum(monthly_data[d]["M2"][2] for d in monthly_data),
                    sum(monthly_data[d]["M1"][2] for d in monthly_data),
                    nps_s(sum(monthly_data[d]["M1"][0] for d in monthly_data),
                          sum(monthly_data[d]["M1"][1] for d in monthly_data),
                          sum(monthly_data[d]["M1"][2] for d in monthly_data)))
    # WoW vigente: VIG vs S1
    wD_vig = {}
    for d in weekly_data:
        if "VIG" not in weekly_data[d]: continue
        vig = weekly_data[d]["VIG"]; s1 = weekly_data[d]["S1"]
        nv = nps_s(*vig); ns = nps_s(*s1)
        sha_s = s1[2]/sS1 if sS1 else 0; sha_v = vig[2]/sVig if sVig else 0
        nt = round(sha_s*(nv-ns), 2) if nv is not None and ns is not None else 0.0
        mx = round((sha_v-sha_s)*(nv-nVig), 2) if nv is not None and nVig is not None else 0.0
        wD_vig[d] = dict(surv_a=s1[2], nps_a=ns, share_a=round(sha_s*100,1),
                         surv_b=vig[2], nps_b=nv, share_b=round(sha_v*100,1),
                         neto=nt, mix=mx, var=round(nt+mx,2))
    tt = round(sum(DRIVER_TARGETS[d] * (monthly_data[d]["M1"][2] /
               sum(monthly_data[d]["M1"][2] for d in monthly_data))
               for d in monthly_data if d in DRIVER_TARGETS), 2)
    vt = {}
    sM1 = sum(monthly_data[d]["M1"][2] for d in monthly_data)
    nM1 = nps_s(sum(monthly_data[d]["M1"][0] for d in monthly_data),
                sum(monthly_data[d]["M1"][1] for d in monthly_data), sM1)
    for drv in monthly_data:
        b = monthly_data[drv]["M1"]; nb = nps_s(*b)
        tgt = DRIVER_TARGETS.get(drv); sh = b[2]/sM1 if sM1 else 0
        gap_d = round(nb - tgt, 2) if nb is not None and tgt is not None else 0.0
        vt[drv] = {"var": round(gap_d * sh, 2), "nps": nb, "target": tgt,
                   "gap": gap_d, "share": round(sh * 100, 1)}
    wd_sorted = sorted_impacts(wD_vig)
    return dict(
        nM1=nM1, nM2=nps_s(sum(monthly_data[d]["M2"][0] for d in monthly_data),
                            sum(monthly_data[d]["M2"][1] for d in monthly_data),
                            sum(monthly_data[d]["M2"][2] for d in monthly_data)),
        dM=round(nM1 - nps_s(sum(monthly_data[d]["M2"][0] for d in monthly_data),
                              sum(monthly_data[d]["M2"][1] for d in monthly_data),
                              sum(monthly_data[d]["M2"][2] for d in monthly_data)), 2)
            if nM1 is not None else 0,
        sM1=sM1, sM2=sum(monthly_data[d]["M2"][2] for d in monthly_data),
        nS1=nVig, nS2=nS1, dW=dW, sS1=sVig, sS2=sS1,
        nps_target=nps_target_consol,
        vs_tgt_mom=round(nM1 - nps_target_consol, 2) if nM1 is not None else 0,
        vs_tgt_wow=round(nVig - nps_target_consol, 2) if nVig is not None else 0,
        surv_mom_var=0, surv_wow_var=round((sVig - sS1)/sS1*100, 1) if sS1 else 0,
        mD=mD, wD=wD_vig, vt=vt, tt=tt,
        worst_mom=min(mD, key=lambda d: mD[d]["var"]),
        best_mom =max(mD, key=lambda d: mD[d]["var"]),
        worst_wow=min(wD_vig, key=lambda d: wD_vig[d]["var"]) if wD_vig else next(iter(monthly_data)),
        best_wow =max(wD_vig, key=lambda d: wD_vig[d]["var"]) if wD_vig else next(iter(monthly_data)),
        rec_worst_mom={"below_m":0,"below_w":0,"trend_m":0,"consec_w":0},
        rec_best_mom ={"below_m":0,"below_w":0,"trend_m":0,"consec_w":0},
        rec_worst_wow={"below_m":0,"below_w":0,"trend_m":0,"consec_w":0},
        rec_best_wow ={"below_m":0,"below_w":0,"trend_m":0,"consec_w":0},
        mom_json=json.dumps(sorted_impacts(mD), ensure_ascii=False),
        wow_json=json.dumps(wd_sorted, ensure_ascii=False),
        vt_json =json.dumps(sorted_impacts(vt),  ensure_ascii=False),
        mom_ybase=calc_y_base(nps_s(sum(monthly_data[d]["M2"][0] for d in monthly_data),
                                    sum(monthly_data[d]["M2"][1] for d in monthly_data),
                                    sum(monthly_data[d]["M2"][2] for d in monthly_data)) or 50,
                              sorted_impacts(mD)),
        wow_ybase=calc_y_base(nS1 or 50, wd_sorted),
        vt_ybase =calc_y_base(tt, sorted_impacts(vt)),
    )

# Para a view vigente: S1=VIG (semana atual), S2=S1 (semana fechada) - reutiliza compute_view
weekly_driver_vig     = {d: {"S1": v.get("VIG",(0,0,0)), "S2": v.get("S1",(0,0,0))} for d,v in weekly_driver.items()}
weekly_driver_sel_vig = {d: v for d,v in weekly_driver_vig.items() if d not in DRIVERS_EXCLUIDOS}
V_ALL_VIG = compute_view(monthly_driver,     weekly_driver_vig,     NPS_TARGET_ALL)
V_SEL_VIG = compute_view(monthly_driver_sel, weekly_driver_sel_vig, NPS_TARGET_SEL)

# ─── HTML ─────────────────────────────────────────────────────────────────────
def _arr(v): return "&#9650;" if v >= 0 else "&#9660;"
def _cls(v): return "pos" if v >= 0 else "neg"
def _pp(v):  return f"{v:+.2f} pp"
def _pct(v): return f"{v:+.1f}%"

def sc_nps(label, val, vs_tgt, vs_prev, prev_label, period_sub):
    if val is None:
        return f"""<div class="sc">
  <div class="sc-label">{label}</div>
  <div class="sc-val" style="color:#999">—</div>
  <hr class="sc-sep">
  <div class="sc-sub">Sem dados ainda</div>
  <div class="sc-sub">{period_sub}</div>
</div>"""
    val_color = "#1a7a1a" if (vs_tgt or 0) >= 0 else "#c0321a"
    return f"""<div class="sc">
  <div class="sc-label">{label}</div>
  <div class="sc-val" style="color:{val_color}">{val:.1f}%</div>
  <hr class="sc-sep">
  <div class="bullet {_cls(vs_tgt)}">{_arr(vs_tgt)} {_pp(vs_tgt)} gap vs target</div>
  <div class="bullet {_cls(vs_prev)}">{_arr(vs_prev)} {_pp(vs_prev)} vs {prev_label}</div>
  <div class="sc-sub">{period_sub}</div>
</div>"""

def sc_target(val, label, current_nps=None):
    if current_nps is not None:
        gap = round(current_nps - val, 2)
        if gap >= 0:
            status_html = f'<div style="margin-top:6px;padding:5px 10px;border-radius:6px;background:#e8f5e9;color:#1b5e20;font-size:11px;font-weight:700;text-align:center">&#9989; Dentro da meta (+{gap:.1f}pp)</div>'
        else:
            status_html = f'<div style="margin-top:6px;padding:5px 10px;border-radius:6px;background:#ffebee;color:#b71c1c;font-size:11px;font-weight:700;text-align:center">&#9888; Fora da meta ({gap:.1f}pp)</div>'
    else:
        status_html = ''
    return f"""<div class="sc">
  <div class="sc-label">TARGET</div>
  <div class="sc-val">{val:.1f}%</div>
  <hr class="sc-sep">
  <div class="sc-sub">meta do periodo</div>
  <div class="sc-sub">{label}</div>
  {status_html}
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
            ("06/abr", weekly_hist_extra,  "S3"),
            ("13/abr", weekly_hist_extra,  "S2_old"),
            ("20/abr", weekly_driver,      "S2"),
            ("27/abr", weekly_driver,      "S1"),
        ]:
            t = src.get(drv, {}).get(key, (0,0,0))
            weekly.append({"label": label, "nps": nps_s(*t), "s": t[2]})
        # Vigente: S1=VIG, S2=S1 (para o historico da aba vigente)
        t_vig = weekly_driver.get(drv, {}).get("VIG", (0,0,0))
        t_s1  = weekly_driver.get(drv, {}).get("S1",  (0,0,0))
        weekly_vig = [
            {"label": "27/abr (S1)", "nps": nps_s(*t_s1),  "s": t_s1[2]},
            {"label": VIG_LABEL,     "nps": nps_s(*t_vig), "s": t_vig[2]},
        ]
        result[drv] = {"monthly": monthly, "weekly": weekly, "weekly_vig": weekly_vig,
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
        ("23/mar", weekly_hist_extra2, "23/mar"),("06/abr", weekly_hist_extra,  "S3"),
        ("13/abr", weekly_hist_extra,  "S2_old"),("20/abr", weekly_driver,      "S2"),
        ("27/abr", weekly_driver,      "S1"),
    ]:
        p   = sum(src.get(d,{}).get(key,(0,0,0))[0] for d in drivers)
        det = sum(src.get(d,{}).get(key,(0,0,0))[1] for d in drivers)
        s   = sum(src.get(d,{}).get(key,(0,0,0))[2] for d in drivers)
        weekly.append({"label": label, "nps": nps_safe(p,det,s), "s": s})
    return {"monthly": monthly, "weekly": weekly}

def make_panes(pfx, v, is_vig=False):
    """Gera os panes para um conjunto de dados. is_vig=True para semana vigente."""
    mD, wD, vt = v["mD"], v["wD"], v["vt"]

    def cards_mes():
        wm = v["worst_mom"]; bm = v["best_mom"]
        return (
            sc_nps("NPS CONSOLIDADO", v["nM1"], v["vs_tgt_mom"], v["dM"], "mes ant.", M1_LABEL) +
            sc_target(v["nps_target"], M1_LABEL, v["nM1"]) +
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
            sc_target(v["nps_target"], M1_LABEL, v["nS1"]) +
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
    <div id="strategic-{pfx}-mes"></div>
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
    <div class="chart-section">
      <div class="chart-title">NPS por Driver — Evolucao Mensal (Fev / Mar / Abr)</div>
      <div class="chart-sub">NPS por driver nos ultimos 3 meses | target consolidado: {v['nps_target']:.1f}%</div>
      <div id="evol-mes-{pfx}"></div>
    </div>
  </div>
  <div id="pane-{pfx}-sem" class="tab-pane">
    <div class="sc-grid">{cards_sem()}</div>
    <div id="strategic-{pfx}-sem"></div>
    <div class="chart-section">
      <div class="chart-title">Impacto WoW - Abertura Driver</div>
      <div class="chart-sub">Contribuicao de cada driver (pp) na variacao consolidada {S2_LABEL} &rarr; {S1_LABEL}.</div>
      <div class="chart-wrap"><canvas id="c-{pfx}-wow"></canvas></div>
    </div>
    <div class="chart-section">
      <div class="chart-title">NPS por Driver — Evolucao Semanal (23/mar – 20/abr)</div>
      <div class="chart-sub">NPS por driver nas ultimas 5 semanas | target consolidado: {v['nps_target']:.1f}%</div>
      <div id="evol-sem-{pfx}"></div>
    </div>
  </div>
"""

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
        ("23/mar", "23/mar",  weekly_hist_extra2),
        ("06/abr", "S3",      weekly_hist_extra),
        ("13/abr", "S2_old",  weekly_hist_extra),
        ("20/abr", "S2",      weekly_driver),
        ("27/abr", "S1",      weekly_driver),
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
    def make_vig_pane(view, v):
        # If no VIG data yet (start of week), show placeholder
        if v["sS1"] == 0:
            return f"""
  <div id="pane-{view}-vig" class="tab-pane">
    <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:16px;margin-bottom:12px;font-size:13px;color:#f57f17;text-align:center">
      &#9889; <strong>Semana vigente {VIG_LABEL}</strong> — Dados ainda nao disponiveis (inicio da semana).<br>
      Verifique novamente mais tarde.
    </div>
  </div>"""
        wm = v["worst_wow"]; bm = v["best_wow"]
        wD, mD, vt = v["wD"], v["mD"], v["vt"]
        cards = (
            sc_nps("NPS VIGENTE", v["nS1"], v["vs_tgt_wow"], v["dW"], "sem. fechada", VIG_LABEL) +
            sc_target(v["nps_target"], M1_LABEL, v["nS1"]) +
            sc_surveys(v["sS1"], v["surv_wow_var"], VIG_LABEL) +
            sc_driver("DRIVER MAIS OFENSOR", wm,
                      wD[wm]["nps_b"], wD[wm]["share_b"],
                      "VIG", wD[wm]["var"], "S1 fechada", mD.get(wm,{}).get("var",0), vt.get(wm,{}).get("gap",0),
                      v["rec_worst_wow"], is_worst=True) +
            sc_driver("DRIVER MAIS PROMOTOR", bm,
                      wD[bm]["nps_b"], wD[bm]["share_b"],
                      "VIG", wD[bm]["var"], "S1 fechada", mD.get(bm,{}).get("var",0), vt.get(bm,{}).get("gap",0),
                      v["rec_best_wow"], is_worst=False)
        )
        return f"""
  <div id="pane-{view}-vig" class="tab-pane">
    <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:8px 16px;margin-bottom:12px;font-size:12px;color:#f57f17">
      &#9889; <strong>Semana vigente parcial</strong> — {VIG_LABEL} ({v['sS1']:,} surveys. Dados em tempo real, podem variar ao longo da semana.)
    </div>
    <div class="sc-grid">{cards}</div>
    <div id="strategic-{view}-vig"></div>
    <div class="chart-section">
      <div class="chart-title">Impacto WoW — Semana Vigente vs Fechada</div>
      <div class="chart-sub">Contribuicao de cada driver (pp): {S1_LABEL} (fechada) &rarr; {VIG_LABEL} (vigente).</div>
      <div class="chart-wrap"><canvas id="c-{view}-vig-wow"></canvas></div>
    </div>
  </div>"""

    panes_all_vig = make_vig_pane("all", V_ALL_VIG)
    panes_sel_vig = make_vig_pane("sel", V_SEL_VIG)

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
var PERIOD_LABELS={{mes:'{M1_LABEL}',sem:'{S1_LABEL}',vig:'{VIG_LABEL} &#9889;'}};
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
    // Sincronizar driver selecionado entre abas
    var periods=['mes','sem','vig'];
    var curDrv='';
    periods.forEach(function(p){{var el=document.getElementById('dd-select-'+p);if(el&&el.value)curDrv=el.value;}});
    if(sel&&curDrv){{sel.value=curDrv;if(typeof renderDD!=='undefined')renderDD(currentPeriod);}}
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
.exec-brief{{background:#fff;border-radius:12px;overflow:hidden;
             box-shadow:0 2px 8px rgba(0,0,0,.1);margin-bottom:20px}}
.exec-brief-header{{background:#1a1e3c;color:#fff;padding:16px 20px}}
.exec-brief-header-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}}
.exec-brief-driver{{font-size:15px;font-weight:700}}
.exec-brief-period{{font-size:11px;color:#aab4d4}}
.exec-brief-kpis{{display:flex;gap:10px;flex-wrap:wrap}}
.exec-brief-kpi{{background:rgba(255,255,255,.12);border-radius:7px;padding:7px 14px;
                 display:flex;flex-direction:column;gap:2px}}
.exec-brief-kpi-label{{font-size:9px;color:#aab4d4;text-transform:uppercase;letter-spacing:.5px}}
.exec-brief-kpi-val{{font-size:18px;font-weight:700;line-height:1}}
.exec-brief-kpi-val.pos{{color:#69f0ae}}.exec-brief-kpi-val.neg{{color:#ff8a80}}
.exec-brief-kpi-val.neutral{{color:#fff}}
.exec-brief-body{{display:grid;grid-template-columns:1fr 1fr;}}
.exec-section{{padding:14px 18px;border-bottom:1px solid #f0f2f5;border-right:1px solid #f0f2f5}}
.exec-section:nth-child(even){{border-right:none}}
.exec-section.full-width{{grid-column:1/-1;border-right:none}}
.exec-section:last-child,.exec-section:nth-last-child(2){{border-bottom:none}}
.exec-section-title{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;
                     margin-bottom:8px;display:flex;align-items:center;gap:5px}}
.es-mom{{color:#1a73e8}}.es-tgt{{color:#bf5c00}}.es-canal{{color:#7b1fa2}}
.es-office{{color:#546e7a}}.es-client{{color:#c0321a}}.es-rep{{color:#e65100}}
.es-opp{{color:#1b5e20}}
.exec-item{{font-size:11.5px;color:#333;line-height:1.55;margin-bottom:5px;
            display:flex;align-items:flex-start;gap:5px}}
.exec-item-icon{{flex-shrink:0;font-weight:700;min-width:14px}}
.exec-item b{{color:#1a1e3c}}
.exec-narrative{{font-size:12.5px;color:#333;line-height:1.65;margin:0 0 6px 0}}
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
      <button class="period-btn"        data-period="vig" onclick="setPeriod(this)" style="background:#ff8f00;color:#fff">&#9889; VIGENTE</button>
    </div>
    <div class="period-label" id="period-label">{M1_LABEL}</div>
  </div>
</div>

<div class="page">
  {panes_all}
  {panes_sel}
  {panes_all_vig}
  {panes_sel_vig}

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

  <div id="pane-dd-vig" class="tab-pane">
    <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:7px 14px;margin-bottom:12px;font-size:12px;color:#f57f17">
      &#9889; <strong>Semana vigente ({VIG_LABEL})</strong> — Resumo executivo usa dados VIG vs S1. Breakdowns detalhados usam S1/S2 como referencia.
    </div>
    <div class="dd-bar">
      <label class="dd-label">Driver</label>
      <select id="dd-select-vig" class="dd-select" onchange="callRenderDD('vig')">
        <option value="">Selecione um driver...</option>
        {options_html}
      </select>
    </div>
    <div id="dd-content-vig" class="dd-placeholder">
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

function buildStrategicSummary(containerId, period, drvData, vtData, npsB, npsA, tgt) {{
  // drvData e vtData sao arrays [{{label, v}}] do sorted_impacts
  // drvData[i].v = contribuicao ao NPS consolidado (negativo = em queda)
  // vtData[i].v  = gap*share vs target (negativo = abaixo do target com peso de volume)
  var el = document.getElementById(containerId);
  if (!el) return;

  function nS(v){{ return (v!==null&&v!==undefined)?v.toFixed(1)+'%':'—'; }}
  function dS(v){{ return v!==null?(v>=0?'+':'')+v.toFixed(2)+'pp':'—'; }}

  // Converter arrays para mapas por label
  var drvMap = {{}}, vtMap = {{}};
  if(Array.isArray(drvData)) drvData.forEach(function(d){{ drvMap[d.label]=d.v; }});
  if(Array.isArray(vtData))  vtData.forEach(function(d){{ vtMap[d.label]=d.v; }});

  // Drivers abaixo do target (vtMap[d] < 0) E em queda (drvMap[d] < -0.5)
  var allLabels = Array.from(new Set(Object.keys(drvMap).concat(Object.keys(vtMap))));
  var atRisk = allLabels.filter(function(d){{
    return vtMap[d]<0 && (drvMap[d]||0)<-0.5;
  }}).sort(function(a,b){{ return (vtMap[a]||0)-(vtMap[b]||0); }});

  // Watch list: abaixo target mas estavel
  var watchList = allLabels.filter(function(d){{
    return vtMap[d]<0 && (drvMap[d]===undefined||(drvMap[d]||0)>=-0.5);
  }}).sort(function(a,b){{ return (vtMap[a]||0)-(vtMap[b]||0); }}).slice(0,4);

  // Extrair insight do Deep Dive de cada driver
  function extractInsight(drv) {{
    var sumObj=(typeof DD_SUMMARIES!=='undefined'?DD_SUMMARIES:{{}})[drv]||{{}};
    var key=period==='mes'?'mom':'wow';
    var raw=sumObj[key]||sumObj.mom||null;
    var txt=(typeof raw==='object'&&raw)?(raw.bullets_legado||''):(raw||'');
    var lines=txt.split('\\n').map(function(b){{return b.replace(/^[\s▶•]+/,'').trim();}}).filter(function(b){{return b.length>20;}});
    return lines[0]||null;
  }}

  var delta=npsB!==null&&npsA!==null?Math.round((npsB-npsA)*100)/100:null;
  var gapCons=npsB!==null&&tgt?Math.round((npsB-tgt)*100)/100:null;
  var lPeriod=period==='mes'?'MoM ('+M2_LABEL+' → '+M1_LABEL+')':period==='sem'?'WoW ('+S2_LABEL+' → '+S1_LABEL+')':'VIG ⚡ ('+S1_LABEL+' → '+VIG_LABEL+')';
  var lAtual=period==='mes'?M1_LABEL:period==='sem'?S1_LABEL:VIG_LABEL+' ⚡';

  var hColor=atRisk.length>0?'#b71c1c':watchList.length>0?'#e65100':'#1b5e20';
  var hMsg=atRisk.length>0?atRisk.length+' driver'+(atRisk.length>1?'s':'')+' abaixo do target e em queda':
    watchList.length>0?watchList.length+' driver'+(watchList.length>1?'s':'')+' abaixo do target (estável)':
    'Todos os drivers acima do target ✔';

  var html='<div style="margin:16px 0;border:2px solid '+hColor+';border-radius:12px;overflow:hidden">'+
    '<div style="background:'+hColor+';padding:10px 16px;display:flex;align-items:center;justify-content:space-between">'+
      '<div style="display:flex;align-items:center;gap:8px">'+
        '<span style="font-size:15px">'+(atRisk.length>0?'⚠️':'◎')+'</span>'+
        '<span style="color:#fff;font-weight:700;font-size:13px">Visão Estratégica — Drivers Sellers</span>'+
        '<span style="color:rgba(255,255,255,.75);font-size:11px">'+lPeriod+'</span>'+
      '</div>'+
      '<div style="color:#fff;font-size:11px;font-weight:600">'+hMsg+'</div>'+
    '</div>'+
    '<div style="padding:12px 16px;background:#fafafa">'+
    '<div style="display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap">'+
      '<div style="background:#fff;padding:7px 12px;border-radius:8px;border:1px solid #e0e0e0">'+
        '<div style="font-size:10px;color:#888;font-weight:600">NPS '+lAtual+'</div>'+
        '<div style="font-size:17px;font-weight:700;color:'+(gapCons!==null&&gapCons>=0?'#1b5e20':'#b71c1c')+'">'+nS(npsB)+'</div>'+
        '<div style="font-size:11px;color:#666">'+dS(delta)+' vs período ant.</div>'+
      '</div>'+
      '<div style="background:#fff;padding:7px 12px;border-radius:8px;border:1px solid #e0e0e0">'+
        '<div style="font-size:10px;color:#888;font-weight:600">Vs Target ('+nS(tgt)+')</div>'+
        '<div style="font-size:17px;font-weight:700;color:'+(gapCons!==null&&gapCons>=0?'#1b5e20':'#b71c1c')+'">'+dS(gapCons)+'</div>'+
        '<div style="font-size:11px;color:#666">'+(gapCons!==null&&gapCons>=0?'Acima da meta':'Abaixo da meta')+'</div>'+
      '</div>'+
      (atRisk.length>0?'<div style="background:#ffebee;padding:7px 12px;border-radius:8px;border:1px solid #ef9a9a">'+
        '<div style="font-size:10px;color:#b71c1c;font-weight:600">Alerta crítico</div>'+
        '<div style="font-size:17px;font-weight:700;color:#b71c1c">'+atRisk.length+'</div>'+
        '<div style="font-size:11px;color:#b71c1c">abaixo target + queda</div>'+
      '</div>':'')+
    '</div>';

  // Cards dos drivers em risco
  if(atRisk.length>0){{
    html+='<div style="font-size:10px;font-weight:700;color:#b71c1c;margin-bottom:6px">⚠ DRIVERS EM ALERTA (Abaixo do Target + Em Queda)</div>'+
      '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px;margin-bottom:12px">';
    atRisk.forEach(function(drv){{
      var impact=drvMap[drv]||0;
      var vtImp=vtMap[drv]||0;
      var severity=vtImp<-2?'#b71c1c':vtImp<-0.5?'#e65100':'#f57f17';
      var insight=extractInsight(drv);
      html+='<div style="background:#fff;border-radius:8px;padding:9px 12px;border:1px solid #e0e0e0;border-left:4px solid '+severity+'">'+
        '<div style="font-size:12px;font-weight:700;color:#1a1e3c;margin-bottom:4px">'+drv+'</div>'+
        '<div style="display:flex;gap:10px;flex-wrap:wrap;font-size:11px;margin-bottom:4px">'+
          '<span>Contrib. per.: <b style="color:#b71c1c">'+(impact>=0?'+':'')+impact.toFixed(2)+'pp</b></span>'+
          '<span>Impacto target: <b style="color:#b71c1c">'+(vtImp>=0?'+':'')+vtImp.toFixed(2)+'pp</b></span>'+
        '</div>'+
        (insight?'<div style="font-size:11px;color:#555;font-style:italic;border-top:1px solid #f5f5f5;padding-top:4px">▶ '+insight+'</div>':'')+
      '</div>';
    }});
    html+='</div>';
  }}

  // Watch list
  if(watchList.length>0){{
    html+='<div style="font-size:10px;font-weight:700;color:#e65100;margin-bottom:5px">● MONITORAR: Abaixo do Target (Tendência Estável)</div>'+
      '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">';
    watchList.forEach(function(drv){{
      var vtImp=vtMap[drv]||0;
      html+='<div style="background:#fff8e1;border:1px solid #ffe082;border-radius:6px;padding:4px 10px;font-size:11px">'+
        '<b>'+drv+'</b> &nbsp;<span style="color:#e65100">'+( vtImp>=0?'+':'')+vtImp.toFixed(2)+'pp vs target</span></div>';
    }});
    html+='</div>';
  }}

  // Conclusao
  var concl=atRisk.length===0&&watchList.length===0
    ? '✅ Todos os drivers estão acima do target neste período. Manter monitoramento semanal.'
    : 'Prioridade: <b>'+atRisk.slice(0,2).join(' e ')+(atRisk.length>2?' e mais '+(atRisk.length-2):'')+
      '</b>. Acesse o Deep Dive de cada driver para causa-raiz e plano de ação.'+
      (watchList.length>0?' Em observação: '+watchList.slice(0,2).join(', ')+'.':'');
  html+='<div style="background:#e8f5e9;border-radius:8px;padding:8px 12px;border:1px solid #a5d6a7">'+
    '<div style="font-size:10px;font-weight:700;color:#1b5e20;margin-bottom:3px">◎ CONCLUSÃO ESTRATÉGICA</div>'+
    '<div style="font-size:11px;color:#1a3c1a;line-height:1.5">'+concl+'</div>'+
  '</div>';

  html+='</div></div>';
  el.innerHTML=html;
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
  drvData.sort(function(a,b){{ var sa=a.pts[a.pts.length-1]?a.pts[a.pts.length-1].s||0:0; var sb=b.pts[b.pts.length-1]?b.pts[b.pts.length-1].s||0:0; return sb-sa; }});  // maior share primeiro

  // Calcular share do ultimo periodo
  var totalS = drvData.reduce(function(acc,r){{ var last=r.pts[r.pts.length-1]; return acc+(last?last.s||0:0); }},0);
  drvData.forEach(function(r){{
    var last=r.pts[r.pts.length-1];
    r.share = (totalS>0&&last&&last.s)? Math.round(last.s/totalS*1000)/10 : null;
  }});

  // Cabeçalho
  var colW = Math.floor(30/periods.length);
  var colgroup = '<col style="width:20%">';
  periods.forEach(function(){{ colgroup+='<col style="width:'+colW+'%">'; }});
  colgroup += '<col style="width:7%"><col style="width:9%"><col style="width:11%"><col style="width:11%"><col style="width:12%">';
  var head = '<tr><th class="col-name">Driver</th>';
  periods.forEach(function(p){{ head+='<th>'+p+'</th>'; }});
  head += '<th>Share</th><th>Delta</th><th>vs Tgt Driver</th><th>vs Tgt Consol</th><th>Recorr.</th></tr>';

  var rows = drvData.map(function(r){{
    var cells = '';
    r.pts.forEach(function(p){{ cells+='<td>'+(p.nps!==null?p.nps.toFixed(1)+'%':'&mdash;')+'</td>'; }});
    var last = r.pts[r.pts.length-1];
    var shareCell = r.share!==null ? '<span class="bk-surv">'+r.share.toFixed(1)+'%</span>' : '&mdash;';
    return '<tr>'+
      '<td class="col-name">'+r.d+'</td>'+
      cells+
      '<td>'+shareCell+'</td>'+
      '<td>'+pDelta(r.delta)+'</td>'+
      '<td>'+pTgt(last?last.nps:null, r.tgt)+'</td>'+
      '<td>'+pTgt(last?last.nps:null, consolTarget)+'</td>'+
      '<td>'+pRec(r.below, r.pts.length, r.consec)+'</td>'+
      '</tr>';
  }}).join('');

  // Linha total com share 100%
  var totalRow='<tr class="bk-total"><td class="col-name">Total</td>';
  periods.forEach(function(){{ totalRow+='<td></td>'; }});
  totalRow+='<td><span class="bk-surv">100%</span></td><td colspan="4"></td></tr>';

  el.innerHTML='<div class="bk-wrap" style="overflow-x:auto"><table class="bk-table">'+
    '<colgroup>'+colgroup+'</colgroup>'+
    '<thead>'+head+'</thead><tbody>'+rows+totalRow+'</tbody></table></div>';
}}

// Navegacao ja definida no head
updatePanes();
// Graficos: requestAnimationFrame garante que o layout foi processado antes de renderizar
try {{ Chart.register(ChartDataLabels); }} catch(e) {{ console.warn('Chart.register:', e); }}
requestAnimationFrame(function() {{
  requestAnimationFrame(function() {{
    {js_charts("all", V_ALL)}{js_charts("sel", V_SEL)}
    try {{ buildWaterfall('c-all-vig-wow',{V_ALL_VIG['nS2']},{V_ALL_VIG['nS1']},'{S1_LABEL}','{VIG_LABEL} ⚡',{V_ALL_VIG['wow_json']},{V_ALL_VIG['wow_ybase']}); }} catch(e) {{}}
    try {{ buildWaterfall('c-sel-vig-wow',{V_SEL_VIG['nS2']},{V_SEL_VIG['nS1']},'{S1_LABEL}','{VIG_LABEL} ⚡',{V_SEL_VIG['wow_json']},{V_SEL_VIG['wow_ybase']}); }} catch(e) {{}}
    var allDrvs = Object.keys(DRV_HIST);
    var selDrvs = allDrvs.filter(function(d){{ return {json.dumps(list(monthly_driver_sel.keys()))}.indexOf(d)>=0; }});
    try {{ buildEvolTable('evol-mes-all', allDrvs, 'monthly', {V_ALL['nps_target']}); }} catch(e) {{ console.warn('evol-mes-all',e); }}
    try {{ buildEvolTable('evol-sem-all', allDrvs, 'weekly',  {V_ALL['nps_target']}); }} catch(e) {{ console.warn('evol-sem-all',e); }}
    try {{ buildEvolTable('evol-mes-sel', selDrvs, 'monthly', {V_SEL['nps_target']}); }} catch(e) {{ console.warn('evol-mes-sel',e); }}
    try {{ buildEvolTable('evol-sem-sel', selDrvs, 'weekly',  {V_SEL['nps_target']}); }} catch(e) {{ console.warn('evol-sem-sel',e); }}
    // Visao Estrategica — inicializar apos graficos
    try {{ buildStrategicSummary('strategic-sel-mes','mes',{V_SEL['mom_json']},{V_SEL['vt_json']},{V_SEL['nM1']},{V_SEL['nM2']},{V_SEL['nps_target']}); }} catch(e) {{}}
    try {{ buildStrategicSummary('strategic-sel-sem','sem',{V_SEL['wow_json']},{V_SEL['vt_json']},{V_SEL['nS1']},{V_SEL['nS2']},{V_SEL['nps_target']}); }} catch(e) {{}}
    try {{ buildStrategicSummary('strategic-sel-vig','vig',{V_SEL_VIG['wow_json']},{V_SEL_VIG['vt_json']},{V_SEL_VIG['nS1']},{V_SEL_VIG['nS2']},{V_SEL_VIG['nps_target']}); }} catch(e) {{}}
    try {{ buildStrategicSummary('strategic-all-mes','mes',{V_ALL['mom_json']},{V_ALL['vt_json']},{V_ALL['nM1']},{V_ALL['nM2']},{V_ALL['nps_target']}); }} catch(e) {{}}
    try {{ buildStrategicSummary('strategic-all-sem','sem',{V_ALL['wow_json']},{V_ALL['vt_json']},{V_ALL['nS1']},{V_ALL['nS2']},{V_ALL['nps_target']}); }} catch(e) {{}}
    try {{ buildStrategicSummary('strategic-all-vig','vig',{V_ALL_VIG['wow_json']},{V_ALL_VIG['vt_json']},{V_ALL_VIG['nS1']},{V_ALL_VIG['nS2']},{V_ALL_VIG['nps_target']}); }} catch(e) {{}}
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
var VIG_LABEL = '{VIG_LABEL}';
var ddCharts = {{}};

function buildExecutiveBrief(drv, period, drvData, bkData) {{
  var isMes = period === 'mes';
  var isVigPeriod = period === 'vig';
  var lA = isMes?M2_LABEL:(isVigPeriod?S1_LABEL:S2_LABEL);
  var lB = isMes?M1_LABEL:(isVigPeriod?VIG_LABEL:S1_LABEL);
  var tgt = drvData?drvData.target:null;
  var cat = DRV_HIST[drv]?DRV_HIST[drv].cat:'';

  // NPS geral
  var hist = DRV_HIST[drv];
  var npsB=null, npsA=null;
  if(hist){{ var arr=isMes?hist.monthly:(period==='vig'?hist.weekly_vig:hist.weekly); if(arr&&arr.length>=2){{npsB=arr[arr.length-1].nps; npsA=arr[arr.length-2].nps;}} }}
  var delta = (npsA!==null&&npsB!==null) ? Math.round((npsB-npsA)*100)/100 : null;
  var gapTgt = (tgt!==null&&npsB!==null) ? Math.round((npsB-tgt)*100)/100 : null;

  function kpiCls(v){{ return v===null?'neutral':v>=0?'pos':'neg'; }}
  function fV(v,dec){{ return v!==null?(v>=0?'+':'')+v.toFixed(dec||1)+'pp':'—'; }}

  // Para VIG: usar S1 como base e VIG como atual (se disponivel); senao S2/S1
  var hasVigBk = isVigPeriod && bkData && bkData['P'] && bkData['P']['VIG'];
  var pA = isMes ? 'M2' : (isVigPeriod ? (hasVigBk ? 'S1' : 'S2') : 'S2');
  var pB = isMes ? 'M1' : (isVigPeriod ? (hasVigBk ? 'VIG' : 'S1') : 'S1');

  // ── DADOS QUANTITATIVOS (estrutura correta: bkData[dim][periodo][nome]) ──
  function getDimData(dim) {{
    var dd = (bkData||{{}})[dim] || {{}};
    var dA = dd[pA] || {{}};  // {{nome_processo: {{p,d,s,nps}}}}
    var dB = dd[pB] || {{}};
    var keys = Object.keys(Object.assign({{}}, dA, dB));
    var totSA=0, totSB=0, totPB=0, totDB=0;
    keys.forEach(function(k){{
      var a=dA[k]||{{p:0,d:0,s:0}}; var b=dB[k]||{{p:0,d:0,s:0}};
      totSA+=a.s||0; totSB+=b.s||0; totPB+=b.p||0; totDB+=b.d||0;
    }});
    var npsAllB = totSB>0 ? (totPB-totDB)/totSB*100 : null;
    return keys.map(function(k){{
      var a=dA[k]||{{p:0,d:0,s:0,nps:null}}; var b=dB[k]||{{p:0,d:0,s:0,nps:null}};
      var shaA=totSA>0?(a.s||0)/totSA:0; var shaB=totSB>0?(b.s||0)/totSB:0;
      var nA=a.nps, nB=b.nps;
      var neto=(shaA>0&&nA!==null&&nB!==null)?shaA*(nB-nA):0;
      var mix=(nB!==null&&npsAllB!==null)?(shaB-shaA)*(nB-npsAllB):0;
      var impact=Math.round((neto+mix)*100)/100;
      var gapT=(tgt!==null&&nB!==null)?Math.round((nB-tgt)*100)/100:null;
      var delta=(nA!==null&&nB!==null)?Math.round((nB-nA)*100)/100:null;
      return {{k:k, nA:nA, nB:nB, shaB:Math.round(shaB*1000)/10, impact:impact, gapT:gapT, delta:delta, sB:b.s||0}};
    }}).filter(function(x){{return x.sB>0||x.nB!==null;}}).sort(function(a,b){{return a.impact-b.impact;}});
  }}
  var procs   = getDimData('P');
  var chans   = getDimData('C');
  var offices = getDimData('O');

  // Separar NETO (qualidade) e MIX (volume) para mix de pesquisas
  function getMixData(dim) {{
    var dd=(bkData||{{}})[dim]||{{}};
    var dA=dd[pA]||{{}}, dB=dd[pB]||{{}};
    var keys=Object.keys(Object.assign({{}},dA,dB));
    var totSA=0,totSB=0,totPB=0,totDB=0;
    keys.forEach(function(k){{var a=dA[k]||{{s:0}};var b=dB[k]||{{s:0,p:0,d:0}};totSA+=a.s||0;totSB+=b.s||0;totPB+=b.p||0;totDB+=b.d||0;}});
    var npsConsol=totSB>0?(totPB-totDB)/totSB*100:null;
    return keys.map(function(k){{
      var a=dA[k]||{{s:0,nps:null}};var b=dB[k]||{{s:0,nps:null}};
      var shaA=totSA>0?(a.s||0)/totSA:0;var shaB=totSB>0?(b.s||0)/totSB:0;
      var deltaSha=Math.round((shaB-shaA)*1000)/10;  // mudanca de share em pp
      var nA=a.nps,nB=b.nps;
      var neto=shaA>0&&nA!==null&&nB!==null?Math.round(shaA*(nB-nA)*100)/100:0;
      var mix=nB!==null&&npsConsol!==null?Math.round((shaB-shaA)*(nB-npsConsol)*100)/100:0;
      return {{k:k,nA:nA,nB:nB,shaA:Math.round(shaA*1000)/10,shaB:Math.round(shaB*1000)/10,
               deltaSha:deltaSha,neto:neto,mix:mix,sB:b.s||0,
               aboveAvg:nB!==null&&npsConsol!==null?nB>npsConsol:null}};
    }}).filter(function(x){{return x.sB>0||x.nB!==null;}});
  }}
  var procsMix = getMixData('P');

  // ── BULLETS QUALITATIVOS ──
  var sumKey = isMes?'mom':(isVigPeriod?'wow':'wow');
  var sumObj = DD_SUMMARIES[drv];
  var sumRaw = sumObj&&sumObj[sumKey]?sumObj[sumKey]:(sumObj&&sumObj.mom?sumObj.mom:null);
  // Suporte a novo formato (objeto) e legado (string)
  var isNewFormat = sumRaw && typeof sumRaw === 'object';
  var sumText = isNewFormat ? (sumRaw.bullets_legado||'') : (sumRaw||'');
  var sumNew  = isNewFormat ? sumRaw : null;
  var bullets = sumText.split('\\n').map(function(b){{return b.replace(/^[\s▶•]+/,'').trim();}}).filter(function(b){{return b.length>15;}});
  function getBullet(kws){{
    for(var i=0;i<bullets.length;i++){{ var bl=bullets[i].toLowerCase(); for(var j=0;j<kws.length;j++){{if(bl.indexOf(kws[j])>=0) return bullets[i];}} }}
    return null;
  }}
  var bVar = getBullet(['varia','queda','alta','subiu','caiu','processo']);
  var bDor = getBullet(['dor','cliente','reclam','vendedor','insatisf']);
  var bRep = getBullet(['representante','rep ','atendente','comportamento','transfere','padrao','agente']);
  var bPos = getBullet(['positivo','funciona','promotor','acima','cresceu','melhora']);
  var bOpp = getBullet(['oportunidade','acao','padronizar','implementar','prioridade','melhoria']);
  if(!bVar&&bullets.length>0) bVar=bullets[0];

  // ── HELPERS ──
  function kpiCls(v){{ return v===null?'neutral':v>=0?'pos':'neg'; }}
  function fV(v){{ return v!==null?(v>=0?'+':'')+v.toFixed(2)+'pp':'—'; }}
  function clr(v){{ return v>=0?'#1a7a1a':'#c0321a'; }}
  function arrow(v){{ return v>=0?'&#8679;':'&#8681;'; }}
  function nStr(v){{ return v!==null?v.toFixed(1)+'%':'—'; }}
  function tag(v,dec){{
    var s=(v>=0?'+':'')+v.toFixed(dec||2)+' pp';
    return '<span style="font-weight:700;color:'+clr(v)+'">'+s+'</span>';
  }}
  function pill(v,dec){{
    var s=(v>=0?'+':'')+v.toFixed(dec||1)+' pp';
    var c=v>=1?'pill-pos-hi':v>=0?'pill-pos-lo':v>=-1?'pill-dn1':'pill-neg-hi';
    return '<span class="pill '+c+'">'+s+'</span>';
  }}

  // ── HEADER ──
  var html='<div class="exec-brief">'+
    '<div class="exec-brief-header">'+
      '<div class="exec-brief-driver">Resumo Executivo Driver</div>'+
      '<div class="exec-brief-period">'+drv+' &middot; '+cat+' &middot; '+lA+' &rarr; '+lB+'</div>'+
    '</div>'+
    '<div class="exec-brief-body">';

  // ── 1: VARIACAO MOM/WOW — narrativa executiva ──
  var s1Title = isMes ? 'Variacao MoM' : (isVigPeriod ? 'Variacao VIG vs S1 &#9889;' : 'Variacao WoW');
  var s1='<div class="exec-section-title" style="color:#555">&#128201; '+s1Title+'</div>';
  var top3neg = procs.filter(function(p){{return p.impact<0;}}).slice(0,3);
  var top2pos = procs.filter(function(p){{return p.impact>0;}}).slice(-2).reverse();
  if(procs.length>0){{
    s1+='<p class="exec-narrative">O NPS do driver '+(delta!==null?(delta>=0?'subiu':'caiu')+' '+Math.abs(delta).toFixed(2)+'pp':'variou')+
        ' de '+nStr(npsA)+' ('+lA+') para '+nStr(npsB)+' ('+lB+')</b>.';
    if(isVigPeriod && !hasVigBk){{
      s1+=' <em style="color:#888">(Breakdown VIG indisponivel — referencia: '+S2_LABEL+' &rarr; '+S1_LABEL+')</em></p>';
      if(top3neg.length>0){{
        s1+='<p class="exec-narrative"><b>Processos de atencao (S1 fechada):</b> ';
        s1+=top3neg.map(function(p){{
          return '<b>'+p.k+'</b> (NPS '+nStr(p.nB)+', '+p.shaB+'% vol)';
        }}).join('; ')+'.';
        s1+='</p>';
      }}
    }} else {{
      if(top3neg.length>0){{
        s1+=' Os principais fatores que puxaram para baixo foram: ';
        s1+=top3neg.map(function(p){{
          return '<b>'+p.k+'</b> ('+tag(p.impact)+' de impacto, NPS '+nStr(p.nB)+', '+p.shaB+'% vol)';
        }}).join('; ')+'.';
      }}
      if(top2pos.length>0){{
        s1+=' Compensaram positivamente: ';
        s1+=top2pos.map(function(p){{
          return '<b>'+p.k+'</b> ('+tag(p.impact)+', NPS '+nStr(p.nB)+')';
        }}).join(' e ')+'.';
      }}
      s1+='</p>';
    }}
  }} else {{
    s1+='<p class="exec-narrative" style="color:#aaa">Sem dados de processo para este periodo.</p>';
  }}

  // ── 2: VS TARGET — narrativa executiva ──
  var tgtPeriodNote = isVigPeriod ? (hasVigBk ? ' (NPS VIG &#9889;)' : ' (NPS VIG)') : '';
  var s2='<div class="exec-section-title" style="color:#555">&#127919; Analise vs Target'+tgtPeriodNote+'</div>';
  if(procs.length>0&&tgt!==null){{
    var abTgt=procs.filter(function(p){{return p.gapT!==null&&p.gapT<0;}}).sort(function(a,b){{return a.gapT-b.gapT;}});
    var acTgt=procs.filter(function(p){{return p.gapT!==null&&p.gapT>=0;}}).sort(function(a,b){{return b.gapT-a.gapT;}});
    s2+='<p class="exec-narrative">O driver esta '+
        (gapTgt>=0?'<b style="color:#1a7a1a">'+fV(gapTgt)+' acima do target</b>':'<b style="color:#c0321a">'+fV(gapTgt)+' abaixo do target</b>')+
        ' ('+tgt.toFixed(1)+'%).';
    if(abTgt.length>0){{
      s2+=(isVigPeriod?' Processos abaixo do target na S1 (ref. fechada): ':' Processos que mais pressionam o gap: ');
      s2+=abTgt.slice(0,3).map(function(p){{
        return '<b>'+p.k+'</b> ('+p.gapT.toFixed(1)+'pp abaixo, NPS '+nStr(p.nB)+')';
      }}).join('; ')+'.';
    }}
    if(acTgt.length>0&&abTgt.length>0){{
      s2+=' Compensam positivamente: ';
      s2+=acTgt.slice(0,2).map(function(p){{
        return '<b>'+p.k+'</b> (+'+p.gapT.toFixed(1)+'pp)';
      }}).join(', ')+'.';
    }}
    if(abTgt.length===0) s2+=' Todos os processos estao acima do target.';
    s2+='</p>';
  }} else {{
    s2+='<p class="exec-narrative" style="color:#aaa">'+(tgt===null?'Target nao definido para este driver.':'Sem dados de processo.')+'</p>';
  }}

  html+='<div class="exec-section">'+s1+'</div>';
  html+='<div class="exec-section">'+s2+'</div>';

  // ── 3: CANAL — narrativa ──
  var canalNote = isVigPeriod ? (hasVigBk ? ' (VIG &#9889;)' : ' (ref. S1 fechada)') : '';
  var s3='<div class="exec-section-title" style="color:#555">&#128241; Canal'+canalNote+'</div>';
  if(chans.length>0){{
    var chSort=chans.slice().sort(function(a,b){{return b.sB-a.sB;}}).slice(0,4);
    s3+='<p class="exec-narrative">';
    chSort.forEach(function(c,i){{
      var d2=c.delta;
      s3+=(i>0?'. ':'')+'<b>'+c.k+'</b>: NPS '+nStr(c.nB)+
          (d2!==null?' ('+tag(d2,1)+')':'')+ ' — '+c.shaB+'% do volume';
    }});
    s3+='.</p>';
  }} else s3+='<p class="exec-narrative" style="color:#aaa">Sem dados de canal.</p>';

  // ── 4: OFICINA — narrativa ──
  var oficNote = isVigPeriod ? (hasVigBk ? ' (VIG &#9889;)' : ' (ref. S1 fechada)') : '';
  var s4='<div class="exec-section-title" style="color:#555">&#127970; Oficina'+oficNote+'</div>';
  if(offices.length>0){{
    var oSort=offices.slice().sort(function(a,b){{return b.sB-a.sB;}}).slice(0,4);
    var oBest=offices.slice().sort(function(a,b){{return (b.nB||0)-(a.nB||0);}})[0];
    s4+='<p class="exec-narrative">';
    oSort.forEach(function(o,i){{
      var d2=o.delta;
      s4+=(i>0?'. ':'')+'<b>'+o.k+'</b>: NPS '+nStr(o.nB)+
          (d2!==null?' ('+tag(d2,1)+')':'')+ ' — '+o.shaB+'% vol';
    }});
    s4+='.</p>';
  }} else s4+='<p class="exec-narrative" style="color:#aaa">Sem dados de oficina.</p>';

  html+='<div class="exec-section">'+s3+'</div>';
  html+='<div class="exec-section">'+s4+'</div>';

  // ── 5-7: QUALITATIVO — full width ──
  function qualSection(icon, title, cls, text, iconColor){{
    return '<div class="exec-section full-width">'+
      '<div class="exec-section-title" style="color:#555">'+icon+' '+title+'</div>'+
      '<p class="exec-narrative">'+text+'</p>'+
    '</div>';
  }}


  // ── MIX DE PESQUISAS + SENIORIDADE (grid 2 colunas, junto aos outros impactos) ──
  var badMixItems=procsMix.filter(function(p){{return p.deltaSha>0.5&&p.aboveAvg===false&&p.mix<-0.05;}}).sort(function(a,b){{return a.mix-b.mix;}}).slice(0,3);
  var goodMixItems=procsMix.filter(function(p){{return p.deltaSha<-0.5&&p.aboveAvg===true&&p.mix<-0.05;}}).sort(function(a,b){{return a.mix-b.mix;}}).slice(0,2);
  var totalMix=Math.round(procsMix.reduce(function(s,p){{return s+p.mix;}},0)*100)/100;
  var totalNeto=Math.round(procsMix.reduce(function(s,p){{return s+p.neto;}},0)*100)/100;

  var s5='<div class="exec-section-title" style="color:#555">&#128257; Mix de Pesquisas — Efeito Volume</div>';
  s5+='<p class="exec-narrative">NETO (qualidade): <strong style="color:'+(totalNeto>=0?'#1a7a1a':'#c0321a')+'">'+(totalNeto>=0?'+':'')+totalNeto.toFixed(2)+'pp</strong> &nbsp;|&nbsp; MIX (volume): <strong style="color:'+(totalMix>=0?'#1a7a1a':'#c0321a')+'">'+(totalMix>=0?'+':'')+totalMix.toFixed(2)+'pp</strong>.';
  if(badMixItems.length>0) s5+=' Volume cresceu em processos abaixo da media: '+badMixItems.map(function(p){{return '<b>'+p.k.substring(0,30)+'</b> (+'+p.deltaSha.toFixed(1)+'pp share) &rarr; '+tag(p.mix);}}).join('; ')+'.';
  if(goodMixItems.length>0) s5+=' Volume caiu em processos acima da media: '+goodMixItems.map(function(p){{return '<b>'+p.k.substring(0,30)+'</b> ('+p.deltaSha.toFixed(1)+'pp share) &rarr; '+tag(p.mix);}}).join('; ')+'.';
  if(badMixItems.length===0&&goodMixItems.length===0) s5+=' Sem redistribuicao significativa de volume neste periodo.';
  s5+='</p>';

  // Senioridade
  var srData = (bkData&&bkData.Sr)||{{}};
  var srA = srData[pA]||{{}}, srB = srData[pB]||{{}};
  var expA=srA['Expert']||{{nps:null,s:0}}, expB=srB['Expert']||{{nps:null,s:0}};
  var nbA=srA['Newbie']||{{nps:null,s:0}},  nbB=srB['Newbie']||{{nps:null,s:0}};
  var expDelta=(expA.nps!==null&&expB.nps!==null)?Math.round((expB.nps-expA.nps)*100)/100:null;
  var nbDelta=(nbA.nps!==null&&nbB.nps!==null)?Math.round((nbB.nps-nbA.nps)*100)/100:null;
  var gapA=(expA.nps!==null&&nbA.nps!==null)?Math.round((expA.nps-nbA.nps)*100)/100:null;
  var gapB=(expB.nps!==null&&nbB.nps!==null)?Math.round((expB.nps-nbB.nps)*100)/100:null;
  var gapDelta=(gapA!==null&&gapB!==null)?Math.round((gapB-gapA)*100)/100:null;

  var s6='<div class="exec-section-title" style="color:#555">&#127891; Impacto Senioridade — Expert vs Newbie</div>';
  if(expB.nps!==null||nbB.nps!==null){{
    s6+='<p class="exec-narrative">'+
      '&#127775; <b>Expert</b>: NPS '+(expB.nps!==null?expB.nps.toFixed(1)+'%':'—')+
      (expDelta!==null?' ('+tag(expDelta,1)+' vs '+lA+')':'')+
      ' &nbsp;&bull;&nbsp; <span class="bk-surv">'+expB.s.toLocaleString('pt-BR')+' surveys</span>'+
    '</p>'+
    '<p class="exec-narrative">'+
      '&#128164; <b>Newbie</b>: NPS '+(nbB.nps!==null?nbB.nps.toFixed(1)+'%':'—')+
      (nbDelta!==null?' ('+tag(nbDelta,1)+' vs '+lA+')':'')+
      ' &nbsp;&bull;&nbsp; <span class="bk-surv">'+nbB.s.toLocaleString('pt-BR')+' surveys</span>'+
    '</p>'+
    '<p class="exec-narrative">'+
      'Gap Expert&minus;Newbie: <strong style="color:'+(gapB!==null&&Math.abs(gapB)>5?'#c0321a':'#1a7a1a')+'">'+(gapB!==null?(gapB>=0?'+':'')+gapB.toFixed(1)+'pp':'—')+'</strong>'+
      (gapDelta!==null?' &nbsp;(gap '+(gapDelta>=0?'ampliou':'reduziu')+' '+Math.abs(gapDelta).toFixed(1)+'pp vs '+lA+')':'')+
    '</p>';
  }} else {{
    s6+='<p class="exec-narrative" style="color:#aaa">Sem dados de senioridade para este periodo.</p>';
  }}

  html+='<div class="exec-section">'+s5+'</div>';
  html+='<div class="exec-section">'+s6+'</div>';

  // ── RECORRENCIA DAS CAUSAS ──
  // Periodos historicos do driver (3 meses ou 4 semanas)
  var drvHistArr = DRV_HIST[drv] ? (isMes ? DRV_HIST[drv].monthly : DRV_HIST[drv].weekly) : [];
  var nPeriods = isMes ? 3 : 4;
  var histWindow = drvHistArr.slice(-nPeriods);  // ultimos N periodos
  var periodLabel = isMes ? '3 meses' : '4 semanas';

  // Contar quantos periodos o DRIVER como um todo ficou abaixo da media historica
  var histAvg = histWindow.reduce(function(s,p){{return s+(p.nps||0);}},0)/(histWindow.length||1);
  var driverBelowCount = histWindow.filter(function(p){{return p.nps!==null&&p.nps<histAvg;}}).length;

  // Recorrencia de PROCESSO: combina dado dos 2 periodos disponiveis + tendencia do driver
  function procRecurrence(p) {{
    var belowA = p.nA!==null&&npsA!==null&&p.nA<npsA;  // abaixo da media do driver no periodo A
    var belowB = p.nB!==null&&npsB!==null&&p.nB<npsB;  // abaixo da media do driver no periodo B
    var worsening = p.delta!==null&&p.delta<-1.5;
    var driverTrend = driverBelowCount >= (isMes?2:3);  // driver tbm estava mal nos periodos historicos
    if(belowA&&belowB&&worsening)   return {{tag:'&#9888; Recorrente e piorando',cls:'pill-neg-hi',detail:'processo abaixo da media em ambos os periodos e piorando'}};
    if(belowA&&belowB)               return {{tag:'&#128260; Recorrente ('+periodLabel+')',cls:'pill-dn1',detail:'processo abaixo da media nos 2 periodos avaliados'}};
    if(!belowA&&belowB&&driverTrend) return {{tag:'&#128993; Em queda recente',cls:'pill-dn1',detail:'novo no periodo atual; driver ja estava pressionado'}};
    if(!belowA&&belowB)              return {{tag:'&#128993; Pontual (apenas '+lB+')',cls:'pill-flat',detail:'apareceu apenas no periodo mais recente'}};
    return {{tag:'&#9989; Sem recorrencia',cls:'pill-pos-lo',detail:'NPS acima da media do driver'}};
  }}

  // Recorrencia de TEMAS QUALITATIVOS: compara bullets mom vs wow
  function themeRecurrence(momText, wowText, themeKeywords) {{
    if(!momText&&!wowText) return null;
    var mLow=(momText||'').toLowerCase();
    var wLow=(wowText||'').toLowerCase();
    var shared=themeKeywords.filter(function(k){{return mLow.indexOf(k)>=0&&wLow.indexOf(k)>=0;}});
    var inMom=themeKeywords.filter(function(k){{return mLow.indexOf(k)>=0;}}).length;
    var inWow=themeKeywords.filter(function(k){{return wLow.indexOf(k)>=0;}}).length;
    if(shared.length>=2) return {{tag:'&#128260; Recorrente (mes e semana)',cls:'pill-neg-hi',themes:shared.slice(0,3)}};
    if(shared.length===1) return {{tag:'&#9888; Parcialmente recorrente',cls:'pill-dn1',themes:shared}};
    if(inMom>0&&inWow===0) return {{tag:'&#128993; Apenas no mes',cls:'pill-flat',themes:[]}};
    if(inMom===0&&inWow>0) return {{tag:'&#128993; Apenas na semana',cls:'pill-flat',themes:[]}};
    return {{tag:'&#9989; Nao recorrente',cls:'pill-pos-lo',themes:[]}};
  }}

  var sumDrv = DD_SUMMARIES[drv]||{{}};
  // sumDrv.wow pode ser string (legado) ou objeto (novo formato) — extrair texto para toLowerCase
  function extractText(v){{ return typeof v==='object'&&v!==null?(v.bullets_legado||''):((v||'')); }}
  var momAllText = extractText(sumDrv.mom).toLowerCase();
  var wowAllText = extractText(sumDrv.wow).toLowerCase();

  var dorKeywords=['rastreio','entrega','cancelad','foto','nota fiscal','suspen','bloqueio','restrict','devolu','conta inativ','prazo','demora'];
  var repKeywords=['transfere','transferencia','verifica sistema','nao encontra','padrao','sem ferramenta','aguardar','encaminh','sem soluc','repete'];
  var dorRec = themeRecurrence(bDor, getBullet(['dor','cliente','reclam','vendedor']), dorKeywords);
  var repRec = themeRecurrence(bRep, getBullet(['representante','rep ','comportamento']), repKeywords);

  var recHtml='<div class="exec-section-title" style="color:#555">&#128260; Recorrencia das Causas &nbsp;<span class="bk-surv">('+periodLabel+')</span></div>';

  var negProcs = procs.filter(function(p){{return p.impact<-0.05;}}).slice(0,4);

  if(negProcs.length===0&&!bDor&&!bRep){{
    recHtml+='<p class="exec-narrative" style="color:#aaa">Nenhuma causa relevante identificada.</p>';
  }} else {{
    recHtml+='<div style="display:flex;flex-direction:column;gap:12px;margin-top:8px">';

    // ── CARD PRINCIPAL UNIFICADO: top processo + dor + rep (mesma raiz) ──
    var mainProc = negProcs[0];
    if(mainProc||(bDor||bRep)){{
      var mRec = mainProc?procRecurrence(mainProc):null;
      var borderColor = mRec&&mRec.cls==='pill-neg-hi'?'#ef5350':mRec&&mRec.cls==='pill-dn1'?'#ff9800':'#bdbdbd';
      var headerBg = mRec&&mRec.cls==='pill-neg-hi'?'#ffebee':mRec&&mRec.cls==='pill-dn1'?'#fff8e1':'#f5f5f5';

      recHtml+='<div style="border:1px solid #e0e0e0;border-left:5px solid '+borderColor+';border-radius:10px;overflow:hidden">';

      // Header do card unificado
      if(mainProc){{
        recHtml+='<div style="background:'+headerBg+';padding:10px 14px;display:flex;align-items:center;justify-content:space-between">'+
          '<div>'+
            '<span style="font-size:10px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.4px">&#9881; Processo Principal</span>'+
            '<div style="font-size:13px;font-weight:700;color:#1a1e3c;margin-top:2px">'+mainProc.k.substring(0,45)+'</div>'+
            '<div style="font-size:11px;color:#666;margin-top:2px">'+
              'NPS <b>'+mainProc.nB.toFixed(1)+'%</b> &nbsp;&bull;&nbsp; '+
              'Impacto <b style="color:'+(mainProc.impact<0?'#c0321a':'#1a7a1a')+'">'+(mainProc.impact>=0?'+':'')+mainProc.impact.toFixed(2)+'pp</b> &nbsp;&bull;&nbsp; '+
              '<span class="bk-surv">'+mainProc.shaB+'% vol</span>'+
            '</div>'+
          '</div>'+
          (mRec?'<span class="pill '+mRec.cls+'" style="font-size:10.5px;flex-shrink:0;margin-left:10px">'+mRec.tag+'</span>':'')+
        '</div>';
      }}

      // Secoes internas do card
      var innerSections = '';

      // Dor do Cliente
      if(bDor){{
        var dorText = bDor.replace(/^dor do cliente[^:]*:\s*/i,'').replace(/^dor[^:]*:\s*/i,'');
        innerSections+=
          '<div style="padding:10px 14px;border-top:1px solid #eeeeee">'+
            '<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:10px">'+
              '<div style="flex:1">'+
                '<div style="font-size:10px;font-weight:700;color:#c0321a;text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">&#128139; O que o cliente relata</div>'+
                '<p style="font-size:12px;color:#333;line-height:1.55;margin:0">'+dorText+'</p>'+
                (dorRec&&dorRec.themes.length>0?'<p style="font-size:10.5px;color:#888;margin:4px 0 0 0">Temas recorrentes: <em>'+dorRec.themes.join(', ')+'</em></p>':'')+
              '</div>'+
              (dorRec?'<span class="pill '+dorRec.cls+'" style="font-size:10.5px;flex-shrink:0;margin-top:2px">'+dorRec.tag+'</span>':'')+
            '</div>'+
          '</div>';
      }}

      // Comportamento REP
      if(bRep){{
        var repText = bRep.replace(/^comportamento rep[^:]*:\s*/i,'').replace(/^comportamento[^:]*:\s*/i,'');
        innerSections+=
          '<div style="padding:10px 14px;border-top:1px solid #eeeeee">'+
            '<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:10px">'+
              '<div style="flex:1">'+
                '<div style="font-size:10px;font-weight:700;color:#e65100;text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">&#129309; Comportamento observado no atendimento</div>'+
                '<p style="font-size:12px;color:#333;line-height:1.55;margin:0">'+repText+'</p>'+
                (repRec&&repRec.themes.length>0?'<p style="font-size:10.5px;color:#888;margin:4px 0 0 0">Padroes recorrentes: <em>'+repRec.themes.join(', ')+'</em></p>':'')+
              '</div>'+
              (repRec?'<span class="pill '+repRec.cls+'" style="font-size:10.5px;flex-shrink:0;margin-top:2px">'+repRec.tag+'</span>':'')+
            '</div>'+
          '</div>';
      }}

      if(innerSections) recHtml+=innerSections;
      recHtml+='</div>';
    }}

    // ── CARDS SECUNDARIOS: processos adicionais (menores, sem qualitativo) ──
    if(negProcs.length>1){{
      recHtml+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px">';
      negProcs.slice(1).forEach(function(p){{
        var rec=procRecurrence(p);
        var bc=rec.cls==='pill-neg-hi'?'#ef5350':rec.cls==='pill-dn1'?'#ff9800':'#bdbdbd';
        recHtml+=
          '<div style="border:1px solid #e0e0e0;border-left:4px solid '+bc+';border-radius:8px;padding:10px 12px;background:#fafafa">'+
            '<div style="font-size:10px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.4px;margin-bottom:4px">&#9881; Processo Adicional</div>'+
            '<div style="font-size:12px;font-weight:600;color:#1a1e3c;margin-bottom:4px">'+p.k.substring(0,38)+'</div>'+
            '<div style="font-size:11px;color:#666;margin-bottom:8px">'+
              'NPS '+p.nB.toFixed(1)+'% &nbsp;&bull;&nbsp; '+
              '<span style="color:'+(p.impact<0?'#c0321a':'#1a7a1a')+';font-weight:600">'+(p.impact>=0?'+':'')+p.impact.toFixed(2)+'pp</span>'+
              ' &nbsp;&bull;&nbsp; <span class="bk-surv">'+p.shaB+'% vol</span>'+
            '</div>'+
            '<span class="pill '+rec.cls+'" style="font-size:10.5px">'+rec.tag+'</span>'+
          '</div>';
      }});
      recHtml+='</div>';
    }}

    recHtml+='</div>';
  }}

  html+='<div class="exec-section full-width">'+recHtml+'</div>';

  // ── PLANO DE ACOES ──
  var acoes=[];
  // Acao 1: do bullet de oportunidade
  if(bOpp) acoes.push({{acao:bOpp.replace(/^oportunidade[^:]*:\s*/i,'').replace(/^oportunidade\s*/i,''),prioridade:'Alta',tipo:'Qualitativa'}});
  // Acoes derivadas dos piores processos vs target
  procs.filter(function(p){{return p.gapT!==null&&p.gapT<-3;}}).slice(0,2).forEach(function(p){{
    acoes.push({{acao:'Investigar causa raiz de '+p.k+' (NPS '+p.nB.toFixed(1)+'%, '+p.gapT.toFixed(1)+'pp abaixo do target). Revisar CDU e comportamento do REP.',prioridade:p.gapT<-10?'Alta':'Media',tipo:'Operacional'}});
  }});
  // Acao de mix se efeito negativo
  if(totalMix<-0.1) acoes.push({{acao:'Avaliar redistribuicao de demanda: volume esta crescendo em processos de baixo NPS. Verificar filas e regras de roteamento.',prioridade:'Media',tipo:'Estrutural'}});
  // Acao de canal se algum canal em queda significativa
  var chanFalling=chans.filter(function(c){{return c.delta!==null&&c.delta<-3&&c.shaB>5;}}).slice(0,1);
  if(chanFalling.length>0) acoes.push({{acao:'Canal '+chanFalling[0].k+' com queda de '+chanFalling[0].delta.toFixed(1)+'pp. Checar experiencia e SLA deste canal.',prioridade:'Media',tipo:'Canal'}});

  if(acoes.length>0){{
    var acoesHtml='<div class="exec-section-title" style="color:#555">&#9989; Plano de Acoes</div>'+
      '<table style="width:100%;border-collapse:collapse;font-size:11.5px">'+
      '<thead><tr style="background:#f5f6fa"><th style="text-align:left;padding:6px 10px;color:#666;font-weight:700;font-size:10px;text-transform:uppercase">Acao</th>'+
      '<th style="padding:6px 8px;color:#666;font-weight:700;font-size:10px;text-transform:uppercase;white-space:nowrap">Prioridade</th>'+
      '<th style="padding:6px 8px;color:#666;font-weight:700;font-size:10px;text-transform:uppercase">Tipo</th>'+
      '<th style="padding:6px 8px;color:#666;font-weight:700;font-size:10px;text-transform:uppercase">Status</th></tr></thead><tbody>';
    acoes.forEach(function(a,i){{
      var prioCls=a.prioridade==='Alta'?'pill-neg-hi':'pill-dn1';
      acoesHtml+='<tr style="border-bottom:1px solid #f0f0f0">'+
        '<td style="padding:7px 10px;line-height:1.5">'+a.acao+'</td>'+
        '<td style="padding:7px 8px;text-align:center"><span class="pill '+prioCls+'">'+a.prioridade+'</span></td>'+
        '<td style="padding:7px 8px;text-align:center"><span class="pill pill-flat" style="font-size:10px">'+a.tipo+'</span></td>'+
        '<td style="padding:7px 8px;text-align:center"><span class="pill pill-dn1">Pendente</span></td>'+
      '</tr>';
    }});
    acoesHtml+='</tbody></table>';
    html+='<div class="exec-section full-width">'+acoesHtml+'</div>';
  }}

  html+='</div></div>';

  // ── PROJEÇÃO DE GANHO NPS (todas as abas, todos os drivers) ──
  (function() {{
    // Processos abaixo do target: se chegassem ao target, quanto ganharíamos?
    var belowTgt = procs.filter(function(p){{return p.gapT!==null&&p.gapT<0&&p.shaB>0;}});
    if(belowTgt.length===0||!tgt) return;

    // Ganho potencial = sum(shaB/100 * |gapT|) para processos abaixo do target
    var gainTotal = 0;
    belowTgt.forEach(function(p){{gainTotal += (p.shaB/100)*Math.abs(p.gapT);}});
    gainTotal = Math.round(gainTotal*100)/100;

    // Ganho se resolvêssemos só o top 2 piores
    var top2 = belowTgt.slice(0,2);
    var gainTop2 = 0;
    top2.forEach(function(p){{gainTop2 += (p.shaB/100)*Math.abs(p.gapT);}});
    gainTop2 = Math.round(gainTop2*100)/100;

    var npsAtual = npsB !== null ? npsB : 0;
    var npsComGain = Math.round((npsAtual+gainTotal)*10)/10;
    var npsComTop2 = Math.round((npsAtual+gainTop2)*10)/10;
    var atingeMeta = (npsAtual+gainTotal) >= tgt;

    var projHtml = '<div style="margin-top:14px;background:#e8f5e9;border:1px solid #a5d6a7;border-radius:10px;padding:12px 16px">'+
      '<div style="font-size:10px;font-weight:700;color:#1b5e20;margin-bottom:6px">&#128200; PROJEÇÃO DE GANHO DE NPS</div>'+
      '<p style="font-size:12px;color:#1b5e20;margin:0 0 6px">'+
        'Se os <b>'+belowTgt.length+' processo'+(belowTgt.length>1?'s':'')+' abaixo do target</b> atingissem '+tgt.toFixed(1)+'% (meta do driver), '+
        'o NPS consolidado subiria <b>+'+gainTotal.toFixed(2)+'pp</b> (de '+npsAtual.toFixed(1)+'% → <b>'+npsComGain+'%</b>).'+
        (atingeMeta?' <b style="color:#2e7d32">&#10003; Suficiente para superar a meta.</b>':' <span style="color:#e65100">Ainda '+Math.abs(Math.round((npsComGain-tgt)*100)/100).toFixed(2)+'pp abaixo da meta.</span>')+
      '</p>'+
      '<p style="font-size:11px;color:#2e7d32;margin:0">'+
        '&#128204; <b>Foco nos top 2:</b> '+top2.map(function(p){{return p.k+' ('+tag(Math.abs(p.gapT)).replace('<span','<span').replace('</span>','pp</span>')+')';}}).join(' e ')+
        ' representaria +'+gainTop2.toFixed(2)+'pp e NPS de '+npsComTop2+'%.'+
      '</p>'+
    '</div>';
    html += projHtml;
  }})();

  // ── ANÁLISE ESTRATÉGICA — Claude (novo formato) ou Quantitativa (todos os drivers) ──
  try {{
    if (sumNew) {{
      html += buildAnaliseEstrategica(sumNew, lA, lB, drv);
    }} else {{
      html += buildAnaliseQuant({{
        drv:drv, isMes:isMes, lA:lA, lB:lB,
        procs:procs, chans:chans, offices:offices, procsMix:procsMix,
        npsA:npsA, npsB:npsB, delta:delta, gapTgt:gapTgt, tgt:tgt,
        bVar:bVar, bDor:bDor, bRep:bRep, bPos:bPos, bOpp:bOpp,
        cat:cat, bkData:bkData, pA:pA, pB:pB
      }});
    }}
  }} catch(e) {{
    html += '<div style="padding:8px;background:#ffebee;border-radius:6px;font-size:11px;color:#c62828;margin-top:8px">Erro Análise: '+e.message+'</div>';
  }}

  return html;
}}

// ── CDU Insight: top CDU de queda e alta com conclusão de transcrições ─────────
function buildCDUInsight(drv, lA, lB) {{
  var sumObj = (typeof DD_SUMMARIES !== 'undefined' ? DD_SUMMARIES : {{}})[drv];
  if (!sumObj) return '';
  var wow = sumObj.wow || sumObj;
  if (!wow || typeof wow !== 'object') return '';
  var cdqD = wow.cdu_queda || null;
  var cdqA = wow.cdu_alta  || null;
  if (!cdqD && !cdqA) return '';

  function nS(v) {{ return v !== null && v !== undefined ? parseFloat(v).toFixed(1)+'%' : '—'; }}
  function dS(v) {{ return v !== null ? (v >= 0 ? '+' : '') + parseFloat(v).toFixed(2) + 'pp' : '—'; }}

  function cardCDU(item, isQueda) {{
    if (!item) return '';
    var bColor  = isQueda ? '#b71c1c'  : '#1b5e20';
    var bgColor = isQueda ? '#fff5f5'  : '#f1f8f3';
    var bdrColor= isQueda ? '#ffcdd2'  : '#c8e6c9';
    var icon    = isQueda ? '&#128201;' : '&#128200;';
    var titulo  = isQueda ? 'MAIOR QUEDA' : 'MAIOR AUMENTO';
    var delta   = item.delta != null ? parseFloat(item.delta) : null;
    var hasTranscr = item.conclusao && item.conclusao.length > 80 &&
                     item.conclusao.indexOf('Análise qualitativa pendente') < 0;
    return (
      '<div style="background:'+bgColor+';border-radius:9px;padding:11px 13px;border:1px solid '+bdrColor+'">'+
        '<div style="display:flex;align-items:center;gap:6px;margin-bottom:7px">'+
          '<span style="font-size:13px">'+icon+'</span>'+
          '<span style="font-size:10px;font-weight:700;color:'+bColor+'">'+titulo+'</span>'+
          (delta !== null ?
            '<span style="font-size:10px;color:'+bColor+';font-weight:600;margin-left:auto">'+
            dS(delta)+'</span>' : '')+
        '</div>'+
        '<div style="font-size:11px;font-weight:600;color:#1a1e3c;margin-bottom:3px">'+
          (item.cdu || '')+'</div>'+
        '<div style="font-size:10px;color:#555;margin-bottom:7px">'+
          (item.sol ? item.sol.substring(0,70)+(item.sol.length>70?'…':'') : '')+
          (item.nps_s2 != null && item.nps_s1 != null ?
            ' &nbsp;&middot;&nbsp; NPS: '+nS(item.nps_s2)+' → <b style="color:'+bColor+'">'+nS(item.nps_s1)+'</b>':'')+
          (item.surveys ? ' &nbsp;&middot;&nbsp; '+item.surveys+' surveys' : '')+
        '</div>'+
        (item.conclusao ?
          '<div style="font-size:11px;color:#1a1e3c;line-height:1.6;background:#fff;border-radius:6px;padding:7px 10px;border-left:3px solid '+bColor+'">'+
            (hasTranscr ?
              '<span style="font-size:9px;font-weight:700;color:#888;display:block;margin-bottom:3px">ANÁLISE DE TRANSCRIÇÕES</span>' : '')+
            item.conclusao+
          '</div>' : '')+
        (item.padrao && hasTranscr ?
          '<div style="margin-top:6px;font-size:10px;color:'+bColor+';font-style:italic;border-top:1px dashed '+bdrColor+';padding-top:5px">'+
            '&#128270; Padrão: '+item.padrao+
          '</div>' : '')+
      '</div>'
    );
  }}

  return (
    '<div style="margin-top:14px;border:2px solid #5c6bc0;border-radius:12px;overflow:hidden">'+
    '<div style="background:#5c6bc0;padding:9px 16px;display:flex;align-items:center;gap:8px">'+
      '<span style="font-size:14px">&#128172;</span>'+
      '<span style="color:#fff;font-weight:700;font-size:12px">Conclus&#227;o por CDU &mdash; Transcri&#231;&#245;es</span>'+
      '<span style="color:#c5cae9;font-size:11px">'+lA+' &rarr; '+lB+'</span>'+
    '</div>'+
    '<div style="padding:12px 16px;background:#f5f6ff">'+
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">'+
      cardCDU(cdqD, true)+
      cardCDU(cdqA, false)+
    '</div>'+
    '</div></div>'
  );
}}

function buildAnaliseQuant(o) {{
  var drv=o.drv, isMes=o.isMes, lA=o.lA, lB=o.lB;
  var procs=o.procs, chans=o.chans, offices=o.offices;
  var npsA=o.npsA, npsB=o.npsB, delta=o.delta, gapTgt=o.gapTgt, tgt=o.tgt;
  var bVar=o.bVar, bDor=o.bDor, bRep=o.bRep, bPos=o.bPos, bOpp=o.bOpp, cat=o.cat;
  var bkData=o.bkData||null, pA=o.pA||'S2', pB=o.pB||'S1';

  function priTag(p) {{
    var c=p==='Alta'?'#b71c1c':p==='Media'?'#e65100':'#388e3c';
    return '<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;background:'+c+'22;color:'+c+'">'+p+'</span>';
  }}
  function nS(v){{ return (v!==null&&v!==undefined)?v.toFixed(1)+'%':'—'; }}
  function dS(v){{ return v!==null?(v>=0?'+':'')+v.toFixed(2)+'pp':'—'; }}
  function clr(v){{ return v>=0?'#1b5e20':'#b71c1c'; }}

  var top3neg = procs.filter(function(p){{return p.impact<0;}}).slice(0,3);
  var top2pos = procs.filter(function(p){{return p.impact>0;}}).slice(-2).reverse();
  var abaixoTgt = procs.filter(function(p){{return p.gapT!==null&&p.gapT<0;}});
  var acimaTgt  = procs.filter(function(p){{return p.gapT!==null&&p.gapT>=0;}});

  // ── Panorama Executivo (quantitativo) ──
  var situacao = (gapTgt!==null&&gapTgt>=0)
    ? '<b style="color:#1b5e20">+'+gapTgt.toFixed(2)+'pp acima da meta</b>'
    : '<b style="color:#b71c1c">'+Math.abs(gapTgt!==null?gapTgt:0).toFixed(2)+'pp abaixo da meta</b>';
  var tendencia = delta===null?'estável':(delta>1?'em alta ('+dS(delta)+')':delta<-1?'em queda ('+dS(delta)+')':'estável ('+dS(delta)+')');
  var panorama = 'O driver '+drv+' ('+cat+') apresentou NPS de '+nS(npsB)+' em '+lB+', variação de '+(delta!==null?dS(delta):'—')+' vs '+lA+', e encontra-se '+situacao+' de '+nS(tgt)+'. '+
    'Tendência: '+tendencia+'. '+
    (top3neg.length>0
      ? 'Principais processos pressionando para baixo: '+top3neg.slice(0,2).map(function(p){{return p.k+' ('+nS(p.nB)+', '+dS(p.impact)+')';}}).join(' e ')+'.'
      : 'Nenhum processo com impacto negativo relevante no período.');

  var out = '<div style="margin-top:14px;border:2px solid #3949ab;border-radius:12px;overflow:hidden">'+
    '<div style="background:#3949ab;padding:10px 16px;display:flex;align-items:center;gap:8px">'+
      '<span style="font-size:15px">&#128202;</span>'+
      '<span style="color:#fff;font-weight:700;font-size:13px">Análise Estratégica</span>'+
      '<span style="color:#9fa8da;font-size:11px;margin-left:4px">— '+lA+' → '+lB+'</span>'+
    '</div>'+
    '<div style="padding:14px 16px;background:#f8f9ff">';

  // Panorama
  out += '<div style="background:#fff;border-radius:8px;padding:11px 14px;margin-bottom:12px;border-left:4px solid #3949ab">'+
    '<div style="font-size:10px;font-weight:700;color:#3949ab;margin-bottom:4px">&#128203; PANORAMA EXECUTIVO</div>'+
    '<p style="font-size:12px;color:#2d3561;line-height:1.6;margin:0">'+panorama+'</p>'+
  '</div>';

  // ── Senioridade (Expert / Newbie) via bkData.Sr ──────────────────────────
  var srPer = (bkData && bkData['Sr']) ? bkData['Sr'] : null;
  var srA = srPer ? (srPer[pA]||{{}}) : {{}};
  var srB = srPer ? (srPer[pB]||{{}}) : {{}};
  var expA=srA['Expert']||null, expB=srB['Expert']||null;
  var nwbA=srA['Newbie']||null, nwbB=srB['Newbie']||null;
  var expDelta=(expA&&expB&&expA.nps!==null&&expB.nps!==null)?Math.round((expB.nps-expA.nps)*100)/100:null;
  var nwbDelta=(nwbA&&nwbB&&nwbA.nps!==null&&nwbB.nps!==null)?Math.round((nwbB.nps-nwbA.nps)*100)/100:null;

  // Canal por direção
  var canalNeg = chans.filter(function(c){{return c.delta!==null&&c.delta<0&&c.sB>=5;}})
                      .sort(function(a,b){{return a.impact-b.impact;}}).slice(0,3);
  var canalPos = chans.filter(function(c){{return c.delta!==null&&c.delta>0&&c.sB>=5;}})
                      .sort(function(a,b){{return b.impact-a.impact;}}).slice(0,3);

  // ── GRID SIMÉTRICO: QUEDA | AUMENTO ──────────────────────────────────────
  var hasQueda  = top3neg.length>0 || canalNeg.length>0 || (expDelta!==null&&expDelta<0) || (nwbDelta!==null&&nwbDelta<0);
  var hasAumento= top2pos.length>0 || canalPos.length>0 || (expDelta!==null&&expDelta>0) || (nwbDelta!==null&&nwbDelta>0);

  if (hasQueda || hasAumento) {{
    out += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px">';

    // ── Coluna QUEDA ──
    out += '<div style="border:1px solid #ef9a9a;border-radius:10px;overflow:hidden">';
    out += '<div style="background:#b71c1c;padding:8px 12px">'+
      '<span style="color:#fff;font-weight:700;font-size:11px">&#128308; TOP FATORES DE QUEDA</span>'+
    '</div><div style="padding:10px 12px;display:flex;flex-direction:column;gap:7px">';

    // Processos em queda
    if (top3neg.length > 0) {{
      out += '<div style="font-size:10px;font-weight:700;color:#b71c1c;margin-bottom:2px">Processos</div>';
      top3neg.forEach(function(p) {{
        var pri=Math.abs(p.impact)>0.3?'Alta':Math.abs(p.impact)>0.1?'Media':'Baixa';
        out += '<div style="background:#fff5f5;border-radius:7px;padding:7px 10px;border:1px solid #ffcdd2">'+
          '<div style="display:flex;align-items:center;gap:5px;margin-bottom:3px">'+priTag(pri)+
            '<span style="font-size:11px;font-weight:600;color:#1a1e3c">'+p.k+'</span>'+
          '</div>'+
          '<div style="font-size:10px;color:#555;line-height:1.5">'+
            'NPS&nbsp;<b>'+nS(p.nB)+'</b>&nbsp;<span style="color:#b71c1c">('+dS(p.delta)+')</span>'+
            '&nbsp;&middot;&nbsp;Impacto:&nbsp;<b style="color:#b71c1c">'+dS(p.impact)+'</b>'+
            '&nbsp;&middot;&nbsp;'+p.shaB+'%&nbsp;vol'+
            (p.gapT!==null?'&nbsp;&middot;&nbsp;Gap:&nbsp;<b style="color:#b71c1c">'+p.gapT.toFixed(2)+'pp</b>':'')+
          '</div>'+
        '</div>';
      }});
    }}

    // Canal em queda
    if (canalNeg.length > 0) {{
      out += '<div style="font-size:10px;font-weight:700;color:#b71c1c;margin:4px 0 2px">Canal</div>';
      canalNeg.forEach(function(c) {{
        out += '<div style="background:#fff5f5;border-radius:6px;padding:5px 9px;border:1px solid #ffcdd2;font-size:10px;color:#333">'+
          '<b>'+c.k+'</b>: NPS&nbsp;'+nS(c.nB)+'&nbsp;<span style="color:#b71c1c">('+dS(c.delta)+')</span>'+
          '&nbsp;&middot;&nbsp;'+c.shaB+'%&nbsp;vol&nbsp;&middot;&nbsp;Impacto:&nbsp;<b style="color:#b71c1c">'+dS(c.impact)+'</b>'+
        '</div>';
      }});
    }}

    // Senioridade em queda
    var srNegLines = [];
    if(expDelta!==null&&expDelta<0) srNegLines.push('<b>Expert</b>: '+nS(expB?expB.nps:null)+'&nbsp;<span style="color:#b71c1c">('+dS(expDelta)+')</span>&nbsp;&middot;&nbsp;'+(expB?expB.s||0:0)+'&nbsp;pesq.');
    if(nwbDelta!==null&&nwbDelta<0) srNegLines.push('<b>Newbie</b>: '+nS(nwbB?nwbB.nps:null)+'&nbsp;<span style="color:#b71c1c">('+dS(nwbDelta)+')</span>&nbsp;&middot;&nbsp;'+(nwbB?nwbB.s||0:0)+'&nbsp;pesq.');
    if(srNegLines.length>0) {{
      out += '<div style="font-size:10px;font-weight:700;color:#b71c1c;margin:4px 0 2px">Senioridade</div>';
      srNegLines.forEach(function(l) {{
        out += '<div style="background:#fff5f5;border-radius:6px;padding:5px 9px;border:1px solid #ffcdd2;font-size:10px;color:#333">'+l+'</div>';
      }});
    }}

    if(!hasQueda) out += '<div style="font-size:11px;color:#888;padding:4px 0">Nenhum fator negativo relevante.</div>';
    out += '</div></div>'; // fim coluna queda

    // ── Coluna AUMENTO ──
    out += '<div style="border:1px solid #a5d6a7;border-radius:10px;overflow:hidden">';
    out += '<div style="background:#1b5e20;padding:8px 12px">'+
      '<span style="color:#fff;font-weight:700;font-size:11px">&#128994; TOP FATORES DE AUMENTO</span>'+
    '</div><div style="padding:10px 12px;display:flex;flex-direction:column;gap:7px">';

    // Processos em alta
    if (top2pos.length > 0) {{
      out += '<div style="font-size:10px;font-weight:700;color:#1b5e20;margin-bottom:2px">Processos</div>';
      top2pos.forEach(function(p) {{
        var pri=Math.abs(p.impact)>0.3?'Alta':Math.abs(p.impact)>0.1?'Media':'Baixa';
        var priGreen=p==='Alta'?'#1b5e20':p==='Media'?'#2e7d32':'#388e3c';
        var priTagG='<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;background:#1b5e2022;color:#1b5e20">'+pri+'</span>';
        out += '<div style="background:#f1f8f3;border-radius:7px;padding:7px 10px;border:1px solid #c8e6c9">'+
          '<div style="display:flex;align-items:center;gap:5px;margin-bottom:3px">'+priTagG+
            '<span style="font-size:11px;font-weight:600;color:#1a1e3c">'+p.k+'</span>'+
          '</div>'+
          '<div style="font-size:10px;color:#555;line-height:1.5">'+
            'NPS&nbsp;<b>'+nS(p.nB)+'</b>&nbsp;<span style="color:#1b5e20">('+dS(p.delta)+')</span>'+
            '&nbsp;&middot;&nbsp;Impacto:&nbsp;<b style="color:#1b5e20">'+dS(p.impact)+'</b>'+
            '&nbsp;&middot;&nbsp;'+p.shaB+'%&nbsp;vol'+
            (p.gapT!==null?'&nbsp;&middot;&nbsp;Gap:&nbsp;<b style="color:'+(p.gapT>=0?'#1b5e20':'#b71c1c')+'">'+p.gapT.toFixed(2)+'pp</b>':'')+
          '</div>'+
        '</div>';
      }});
    }}

    // Canal em alta
    if (canalPos.length > 0) {{
      out += '<div style="font-size:10px;font-weight:700;color:#1b5e20;margin:4px 0 2px">Canal</div>';
      canalPos.forEach(function(c) {{
        out += '<div style="background:#f1f8f3;border-radius:6px;padding:5px 9px;border:1px solid #c8e6c9;font-size:10px;color:#333">'+
          '<b>'+c.k+'</b>: NPS&nbsp;'+nS(c.nB)+'&nbsp;<span style="color:#1b5e20">('+dS(c.delta)+')</span>'+
          '&nbsp;&middot;&nbsp;'+c.shaB+'%&nbsp;vol&nbsp;&middot;&nbsp;Impacto:&nbsp;<b style="color:#1b5e20">'+dS(c.impact)+'</b>'+
        '</div>';
      }});
    }}

    // Senioridade em alta
    var srPosLines = [];
    if(expDelta!==null&&expDelta>0) srPosLines.push('<b>Expert</b>: '+nS(expB?expB.nps:null)+'&nbsp;<span style="color:#1b5e20">('+dS(expDelta)+')</span>&nbsp;&middot;&nbsp;'+(expB?expB.s||0:0)+'&nbsp;pesq.');
    if(nwbDelta!==null&&nwbDelta>0) srPosLines.push('<b>Newbie</b>: '+nS(nwbB?nwbB.nps:null)+'&nbsp;<span style="color:#1b5e20">('+dS(nwbDelta)+')</span>&nbsp;&middot;&nbsp;'+(nwbB?nwbB.s||0:0)+'&nbsp;pesq.');
    if(srPosLines.length>0) {{
      out += '<div style="font-size:10px;font-weight:700;color:#1b5e20;margin:4px 0 2px">Senioridade</div>';
      srPosLines.forEach(function(l) {{
        out += '<div style="background:#f1f8f3;border-radius:6px;padding:5px 9px;border:1px solid #c8e6c9;font-size:10px;color:#333">'+l+'</div>';
      }});
    }}

    // Fator positivo qualitativo (transcrições / promotores)
    if (bPos) {{
      out += '<div style="font-size:10px;font-weight:700;color:#1b5e20;margin:4px 0 2px">Fator Positivo (Transcri&#231;&#245;es)</div>'+
        '<div style="background:#f1f8f3;border-radius:6px;padding:6px 9px;border:1px solid #c8e6c9;font-size:11px;color:#1a3c1a;line-height:1.5">'+bPos+'</div>';
    }}

    if(!hasAumento) out += '<div style="font-size:11px;color:#888;padding:4px 0">Nenhum fator positivo relevante.</div>';
    out += '</div></div>'; // fim coluna aumento

    out += '</div>'; // fim grid
  }}

  // Sumário para diretoria + Conclusão (gerados quantitativamente)
  var piorProc = top3neg[0]?top3neg[0].k:'N/A';
  var melhorProc = top2pos[0]?top2pos[0].k:'N/A';
  var sumLines = [
    'NPS '+nS(npsB)+' em '+lB+', variação de '+dS(delta)+' vs '+lA+'.',
    abaixoTgt.length>0 ? abaixoTgt.length+' processo(s) abaixo do target ('+nS(tgt)+'): '+abaixoTgt.slice(0,2).map(function(p){{return p.k;}})+'.':
      'Todos os processos acima do target de '+nS(tgt)+'.',
    top3neg.length>0 ? 'Principal fator de queda: '+piorProc+' (impacto '+dS(top3neg[0].impact)+', NPS '+nS(top3neg[0].nB)+').' : 'Nenhum processo com impacto negativo relevante.',
    top2pos.length>0 ? 'Principal fator positivo: '+melhorProc+' (impacto '+dS(top2pos[0].impact)+', NPS '+nS(top2pos[0].nB)+').' : 'Volume positivo distribuído entre os processos.',
    bOpp ? bOpp : 'Priorizar ações nos processos com maior gap vs target e maior volume.'
  ];
  var conclusao = (gapTgt!==null&&gapTgt<0)
    ? 'Driver opera '+Math.abs(gapTgt).toFixed(2)+'pp abaixo da meta. '+
      (top3neg.length>0?'Resolver '+piorProc+' é a ação de maior retorno individual.':'Ação distribuída entre múltiplos processos.')+
      ' Sem intervenção nos próximos 30 dias, tendência se consolida.'
    : 'Driver acima da meta em '+gapTgt.toFixed(2)+'pp. Manter '+melhorProc+' como referência e monitorar processos em queda.';

  out += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">'+
    '<div style="background:#f3e5f5;border-radius:7px;padding:9px 12px;border:1px solid #ce93d8">'+
      '<div style="font-size:10px;font-weight:700;color:#6a1a6a;margin-bottom:6px">&#127970; SUMÁRIO PARA DIRETORIA</div>'+
      sumLines.map(function(l,i){{return '<div style="font-size:11px;color:#2d1259;margin-bottom:3px"><b>'+(i+1)+'.</b> '+l+'</div>';}}).join('')+
    '</div>'+
    '<div style="background:#e8f5e9;border-radius:7px;padding:9px 12px;border:1px solid #a5d6a7">'+
      '<div style="font-size:10px;font-weight:700;color:#1b5e20;margin-bottom:4px">&#127919; CONCLUSÃO ESTRATÉGICA</div>'+
      '<p style="font-size:11px;color:#1a3c1a;line-height:1.5;margin:0">'+conclusao+'</p>'+
    '</div>'+
  '</div>';

  out += '</div></div>';

  // ── CDU Insights (de DD_SUMMARIES se disponível) ────────────────────────────
  out += buildCDUInsight(drv, lA, lB);

  return out;
}}

function buildAnaliseEstrategica(s, lA, lB, drv) {{
  function priTag(p) {{
    var c = p==='Alta'?'#b71c1c':p==='Media'?'#e65100':'#388e3c';
    return '<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;background:'+c+'22;color:'+c+'">'+p+'</span>';
  }}
  function freqTag(f) {{
    var c = f==='alta'?'#6a1a6a':f==='media'?'#1a5276':'#1a6a2a';
    var l = f==='alta'?'Alta':f==='media'?'Média':'Baixa';
    return '<span style="display:inline-block;padding:2px 6px;border-radius:8px;font-size:10px;background:'+c+'18;color:'+c+';font-weight:600">'+l+'</span>';
  }}
  function respTag(r) {{
    var c = r==='Produto'?'#1a237e':r==='Gestao'?'#4a148c':'#006064';
    return '<span style="display:inline-block;padding:2px 6px;border-radius:8px;font-size:10px;background:'+c+'18;color:'+c+';font-weight:600">'+r+'</span>';
  }}

  var out = '<div style="margin-top:18px;border:2px solid #3949ab;border-radius:12px;overflow:hidden">'+
    '<div style="background:#3949ab;padding:10px 16px;display:flex;align-items:center;gap:8px">'+
      '<span style="font-size:15px">&#128202;</span>'+
      '<span style="color:#fff;font-weight:700;font-size:13px">Análise Estratégica</span>'+
      '<span style="color:#9fa8da;font-size:11px;margin-left:4px">— novo framework analítico (teste)</span>'+
    '</div>'+
    '<div style="padding:14px 16px;background:#f8f9ff">';

  // Resumo Executivo
  if(s.resumo_executivo) {{
    out += '<div style="background:#fff;border-radius:8px;padding:12px 14px;margin-bottom:12px;border-left:4px solid #3949ab">'+
      '<div style="font-size:10px;font-weight:700;color:#3949ab;margin-bottom:4px">&#128203; PANORAMA EXECUTIVO</div>'+
      '<p style="font-size:12px;color:#2d3561;line-height:1.6;margin:0">'+s.resumo_executivo+'</p>'+
    '</div>';
  }}

  // Alertas Críticos
  if(s.alertas_criticos && s.alertas_criticos.length) {{
    out += '<div style="background:#fff8e1;border:1px solid #ff8f00;border-radius:8px;padding:10px 14px;margin-bottom:12px">';
    out += '<div style="font-size:10px;font-weight:700;color:#e65100;margin-bottom:6px">&#9888; ALERTAS CRÍTICOS</div>';
    s.alertas_criticos.forEach(function(a) {{
      out += '<div style="font-size:11px;color:#5d3b00;margin-bottom:4px">• '+a+'</div>';
    }});
    out += '</div>';
  }}

  // Top Detratores
  if(s.top_detratores && s.top_detratores.length) {{
    out += '<div style="margin-bottom:12px">'+
      '<div style="font-size:10px;font-weight:700;color:#b71c1c;margin-bottom:6px">&#128308; TOP CAUSAS DE INSATISFAÇÃO</div>'+
      '<div style="display:flex;flex-direction:column;gap:6px">';
    s.top_detratores.forEach(function(d) {{
      out += '<div style="background:#fff;border-radius:7px;padding:9px 12px;border:1px solid #e0e0e0">'+
        '<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">'+
          priTag(d.prioridade||'Media')+' '+freqTag(d.frequencia||'media')+
          '<span style="font-size:11px;font-weight:600;color:#1a1e3c;flex:1">'+d.causa+'</span>'+
        '</div>'+
        '<div style="font-size:11px;color:#555;margin-bottom:3px"><b>Impacto:</b> '+d.impacto+'</div>'+
        '<div style="font-size:11px;color:#1a5276"><b>&#9679; Sugestão:</b> '+d.sugestao+'</div>'+
      '</div>';
    }});
    out += '</div></div>';
  }}

  // Top Promotores
  if(s.top_promotores && s.top_promotores.length) {{
    out += '<div style="margin-bottom:12px">'+
      '<div style="font-size:10px;font-weight:700;color:#1b5e20;margin-bottom:6px">&#128994; TOP DRIVERS DE SATISFAÇÃO</div>'+
      '<div style="display:flex;flex-direction:column;gap:6px">';
    s.top_promotores.forEach(function(p) {{
      out += '<div style="background:#fff;border-radius:7px;padding:8px 12px;border:1px solid #e0e0e0">'+
        '<div style="font-size:11px;font-weight:600;color:#1b5e20;margin-bottom:2px">'+p.causa+'</div>'+
        '<div style="font-size:11px;color:#555">'+p.impacto+'</div>'+
      '</div>';
    }});
    out += '</div></div>';
  }}

  // Grid: Padrões + Senioridade
  var hasPatterns = s.padroes_operacionais || s.senioridade_insight;
  if(hasPatterns) {{
    out += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px">';
    if(s.padroes_operacionais) {{
      out += '<div style="background:#fff;border-radius:7px;padding:9px 12px;border:1px solid #e0e0e0">'+
        '<div style="font-size:10px;font-weight:700;color:#4a148c;margin-bottom:4px">&#128241; PADRÕES OPERACIONAIS</div>'+
        '<p style="font-size:11px;color:#333;line-height:1.5;margin:0">'+s.padroes_operacionais+'</p>'+
      '</div>';
    }}
    if(s.senioridade_insight) {{
      out += '<div style="background:#fff;border-radius:7px;padding:9px 12px;border:1px solid #e0e0e0">'+
        '<div style="font-size:10px;font-weight:700;color:#01579b;margin-bottom:4px">&#127775; SENIORIDADE</div>'+
        '<p style="font-size:11px;color:#333;line-height:1.5;margin:0">'+s.senioridade_insight+'</p>'+
      '</div>';
    }}
    out += '</div>';
  }}

  // Ações 30 Dias
  if(s.acoes_30_dias && s.acoes_30_dias.length) {{
    out += '<div style="margin-bottom:12px">'+
      '<div style="font-size:10px;font-weight:700;color:#1a237e;margin-bottom:6px">&#128203; AÇÕES PRIORITÁRIAS — 30 DIAS</div>'+
      '<div style="display:flex;flex-direction:column;gap:5px">';
    s.acoes_30_dias.forEach(function(a,i) {{
      out += '<div style="background:#fff;border-radius:6px;padding:8px 12px;border:1px solid #e0e0e0;display:flex;align-items:flex-start;gap:8px">'+
        '<span style="font-weight:700;color:#3949ab;min-width:14px">'+(i+1)+'.</span>'+
        '<div style="flex:1">'+
          '<span style="font-size:11px;color:#1a1e3c">'+a.acao+'</span>'+
          '<span style="margin-left:8px">'+priTag(a.prioridade||'')+'</span>'+
          '<span style="margin-left:4px">'+respTag(a.responsavel||'')+'</span>'+
        '</div>'+
      '</div>';
    }});
    out += '</div></div>';
  }}

  // Sumário + Conclusão (grid 2 colunas)
  if(s.sumario_diretoria || s.conclusao_estrategica) {{
    out += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">';
    if(s.sumario_diretoria) {{
      var lines = s.sumario_diretoria.split('\\n').filter(function(l){{return l.trim();}});
      out += '<div style="background:#f3e5f5;border-radius:7px;padding:9px 12px;border:1px solid #ce93d8">'+
        '<div style="font-size:10px;font-weight:700;color:#6a1a6a;margin-bottom:6px">&#127970; SUMÁRIO PARA DIRETORIA</div>'+
        lines.map(function(l,i){{
          return '<div style="font-size:11px;color:#2d1259;margin-bottom:3px"><b>'+(i+1)+'.</b> '+l.trim()+'</div>';
        }}).join('')+
      '</div>';
    }}
    if(s.conclusao_estrategica) {{
      out += '<div style="background:#e8f5e9;border-radius:7px;padding:9px 12px;border:1px solid #a5d6a7">'+
        '<div style="font-size:10px;font-weight:700;color:#1b5e20;margin-bottom:4px">&#127919; CONCLUSÃO ESTRATÉGICA</div>'+
        '<p style="font-size:11px;color:#1a3c1a;line-height:1.5;margin:0">'+s.conclusao_estrategica+'</p>'+
      '</div>';
    }}
    out += '</div>';
  }}

  out += '</div></div>';

  // ── CDU Insights ────────────────────────────────────────────────────────────
  if (drv) out += buildCDUInsight(drv, lA, lB);

  return out;
}}

function buildAnalysisCards(drv, period, drvData, bkData) {{
  var isMes = period === 'mes';
  var pA = isMes ? 'M2' : 'S2';
  var pB = isMes ? 'M1' : 'S1';
  var lA = isMes ? M2_LABEL : S2_LABEL;
  var lB = isMes ? M1_LABEL : S1_LABEL;
  var tgt = drvData ? drvData.target : null;

  // NPS geral do driver nos dois periodos
  var hist = DRV_HIST[drv];
  var npsB = null, npsA = null;
  if (hist) {{
    var arr = isMes ? hist.monthly : hist.weekly;
    if (arr && arr.length >= 2) {{
      npsB = arr[arr.length-1].nps;  // periodo atual
      npsA = arr[arr.length-2].nps;  // periodo anterior
    }}
  }}
  var deltaNps = (npsA!==null&&npsB!==null) ? Math.round((npsB-npsA)*100)/100 : null;
  var gapTgt   = (tgt&&npsB!==null) ? Math.round((npsB-tgt)*100)/100 : null;

  function pill(v, isGap) {{
    if(v===null||v===undefined) return '<span class="pill pill-neu">&mdash;</span>';
    var s=(v>=0?'+':'')+v.toFixed(2)+' pp';
    var c=v>=1?'pill-pos-hi':v>=0?'pill-pos-lo':v>=-1?'pill-dn1':'pill-neg-hi';
    return '<span class="pill '+c+'">'+s+'</span>';
  }}

  // Processos mais impactados (por variacao de NPS)
  var procData = bkData && bkData.P ? bkData.P : {{}};
  var procItems = [];
  Object.keys(procData).forEach(function(p){{
    var dA = procData[p][pA]; var dB = procData[p][pB];
    if(!dA||!dB||dA.nps===null||dB.nps===null) return;
    var delta = Math.round((dB.nps-dA.nps)*100)/100;
    var w = dB.s||0;
    procItems.push({{name:p, npsB:dB.nps, npsA:dA.nps, delta:delta, s:w}});
  }});
  procItems.sort(function(a,b){{return a.delta-b.delta;}});
  var worst3 = procItems.slice(0,3);
  var best3  = procItems.slice(-3).reverse();

  // Processos vs target
  var vsTargetItems = [];
  procItems.forEach(function(p){{
    if(tgt===null||tgt===undefined) return;
    vsTargetItems.push({{name:p.name, nps:p.npsB, gap:Math.round((p.npsB-tgt)*100)/100, s:p.s}});
  }});
  vsTargetItems.sort(function(a,b){{return a.gap-b.gap;}});
  var worstVsTgt = vsTargetItems.slice(0,3);
  var bestVsTgt  = vsTargetItems.slice(-3).reverse();

  function procLine(p, showDelta) {{
    var icon = (showDelta&&p.delta<0)||(!showDelta&&p.gap<0) ? '&#8681;' : '&#8679;';
    var cls  = (showDelta&&p.delta<0)||(!showDelta&&p.gap<0) ? 'color:#c0321a' : 'color:#1a7a1a';
    var val  = showDelta ? p.delta : p.gap;
    var valStr = (val>=0?'+':'')+val.toFixed(1)+' pp';
    return '<div class="analysis-item">'+
      '<span class="analysis-icon" style="'+cls+'">'+icon+'</span>'+
      '<span><strong>'+p.name.substring(0,35)+'</strong> — NPS '+(showDelta?p.npsB.toFixed(1):p.nps.toFixed(1))+'% '+
      '<span style="'+cls+';font-weight:600">'+valStr+'</span>'+
      ' <span class="bk-surv">('+p.s.toLocaleString('pt-BR')+')</span></span>'+
      '</div>';
  }}

  // Card MoM
  var cardMom = '<div class="analysis-card card-mom">'+
    '<div class="analysis-card-title">'+
      (deltaNps===null?'Variacao '+lA+' vs '+lB:
       (deltaNps>=0?'&#8679; Por que subimos MoM?':'&#8681; Por que caimos MoM?'))+
    '</div>'+
    '<div class="analysis-item"><span style="font-size:12px">Variacao consolidada '+lA+' &rarr; '+lB+': '+
      (deltaNps!==null?'<strong>'+pill(deltaNps)+'</strong>':'sem dados')+
      (npsA!==null&&npsB!==null?' &nbsp;('+npsA.toFixed(1)+'% &rarr; '+npsB.toFixed(1)+'%)':'')+
    '</span></div>';

  if(worst3.length>0) {{
    cardMom += '<div class="analysis-label">Processos que mais puxaram para baixo</div>';
    worst3.forEach(function(p){{ cardMom+=procLine(p,true); }});
  }}
  if(best3.length>0) {{
    cardMom += '<div class="analysis-label">Processos que mais compensaram</div>';
    best3.forEach(function(p){{ cardMom+=procLine(p,true); }});
  }}
  cardMom += '</div>';

  // Card vs Target
  var cardTgt = '<div class="analysis-card card-tgt">'+
    '<div class="analysis-card-title">'+
      (gapTgt===null?'Por que nao entregamos vs target?':
       (gapTgt>=0?'&#8679; Por que estamos acima do target?':'&#8681; Por que nao entregamos vs target?'))+
    '</div>'+
    '<div class="analysis-item"><span style="font-size:12px">NPS atual vs target driver'+
      (tgt?' ('+tgt.toFixed(1)+'%)':'')+': '+
      (gapTgt!==null?'<strong>'+pill(gapTgt,true)+'</strong>':'sem target definido')+
    '</span></div>';

  if(worstVsTgt.length>0&&tgt!==null) {{
    cardTgt += '<div class="analysis-label">Processos mais abaixo do target</div>';
    worstVsTgt.forEach(function(p){{ cardTgt+=procLine(p,false); }});
  }}
  if(bestVsTgt.length>0&&tgt!==null) {{
    cardTgt += '<div class="analysis-label">Processos acima do target (favoraveis)</div>';
    bestVsTgt.forEach(function(p){{ cardTgt+=procLine(p,false); }});
  }}
  cardTgt += '</div>';

  return '<div class="analysis-cards">'+cardMom+cardTgt+'</div>';
}}

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

function renderBreakdownTables(el) {{
  var drv    = el.getAttribute('data-drv');
  var period = el.getAttribute('data-period');
  var pA     = el.getAttribute('data-pa');
  var pB     = el.getAttribute('data-pb');
  var tgtStr = el.getAttribute('data-tgt');
  var tgt    = tgtStr !== '' ? parseFloat(tgtStr) : null;
  var lSuf   = el.getAttribute('data-lsuf') || 'WoW';
  var lWoW   = el.getAttribute('data-lwow') || '';
  var proc   = el.value;
  var cont   = document.getElementById('bk-tables-' + period);
  if (!cont) return;

  var bk  = DD_BREAKDOWN[drv];
  var html = '';

  // Tabela de Processos: sempre nivel driver (independente do filtro)
  html += '<div class="dd-section-title">Processos — '+(lWoW||lSuf)+'</div>';
  html += buildBreakdownTable(bk, 'P', pA, pB, tgt, 'Processo');

  if (!proc) {{
    // Sem filtro: nivel driver
    html += '<div class="dd-section-title">Canal — '+lSuf+'</div>';
    html += buildBreakdownTable(bk, 'C', pA, pB, tgt, 'Canal');
    html += '<div class="dd-section-title">Oficina — '+lSuf+'</div>';
    html += buildBreakdownTable(bk, 'O', pA, pB, tgt, 'Oficina');
    html += '<div class="dd-section-title">Senioridade por processo — '+lSuf+'</div>';
    html += buildSeniorityTable(bk, pA, pB, tgt);
  }} else {{
    // Com filtro: usar P_C / P_O / Sr_P para o processo selecionado
    var pcA = (bk&&bk['P_C']&&bk['P_C'][pA]&&bk['P_C'][pA][proc]) ? bk['P_C'][pA][proc] : {{}};
    var pcB = (bk&&bk['P_C']&&bk['P_C'][pB]&&bk['P_C'][pB][proc]) ? bk['P_C'][pB][proc] : {{}};
    var poA = (bk&&bk['P_O']&&bk['P_O'][pA]&&bk['P_O'][pA][proc]) ? bk['P_O'][pA][proc] : {{}};
    var poB = (bk&&bk['P_O']&&bk['P_O'][pB]&&bk['P_O'][pB][proc]) ? bk['P_O'][pB][proc] : {{}};
    var srA = (bk&&bk['Sr_P']&&bk['Sr_P'][pA]&&bk['Sr_P'][pA][proc]) ? bk['Sr_P'][pA][proc] : {{}};
    var srB = (bk&&bk['Sr_P']&&bk['Sr_P'][pB]&&bk['Sr_P'][pB][proc]) ? bk['Sr_P'][pB][proc] : {{}};

    // Mock objects para reutilizar buildBreakdownTable (Canal e Oficina)
    var mockC  = {{C: {{}}}};  mockC.C[pA] = pcA;  mockC.C[pB] = pcB;
    var mockO  = {{O: {{}}}};  mockO.O[pA] = poA;  mockO.O[pB] = poB;

    html += '<div class="dd-section-title">Canal — '+proc+' ('+lSuf+')</div>';
    html += buildBreakdownTable(mockC, 'C', pA, pB, tgt, 'Canal');
    html += '<div class="dd-section-title">Oficina — '+proc+' ('+lSuf+')</div>';
    html += buildBreakdownTable(mockO, 'O', pA, pB, tgt, 'Oficina');
    html += '<div class="dd-section-title">Senioridade — '+proc+' ('+lSuf+')</div>';
    // Renderizar Expert/Newbie diretamente para evitar ambiguidade no mockSr
    html += (function() {{
      var lSrA = pA==='M2'?M2_LABEL:(pA==='S2'?S2_LABEL:(pA==='S1'?S1_LABEL:pA));
      var lSrB = pB==='M1'?M1_LABEL:(pB==='S1'?S1_LABEL:(pB==='VIG'?VIG_LABEL+' ⚡':pB));
      function nS(v){{ return (v!==null&&v!==undefined)?v.toFixed(1)+'%':'&mdash;'; }}
      function pD2(v){{
        if(v===null||v===undefined) return '<span class="pill pill-neu">&mdash;</span>';
        var s=(v>=0?'+':'')+v.toFixed(2)+' pp';
        var c=v>=1?'pill-pos-hi':v>=0?'pill-pos-lo':v>=-1?'pill-dn1':'pill-neg-hi';
        return '<span class="pill '+c+'">'+s+'</span>';
      }}
      function pVS(nps2){{
        if(nps2===null||!tgt) return '<span class="pill pill-neu">&mdash;</span>';
        var g=nps2-tgt; return '<span class="pill '+(g>=0?'pill-pos-hi':'pill-neg-hi')+'">'+(g>=0?'+':'')+g.toFixed(2)+' pp</span>';
      }}
      var rows = ['Expert','Newbie'];
      var icons = {{Expert:'&#127775;',Newbie:'&#128164;'}};
      var tbl = '<div class="bk-wrap"><table class="bk-table">'+
        '<colgroup><col style="width:20%"><col style="width:13%"><col style="width:13%"><col style="width:13%"><col style="width:10%"><col style="width:13%"></colgroup>'+
        '<thead><tr><th class="col-name">Senioridade</th><th>'+lSrA+'</th><th>'+lSrB+'</th>'+
        '<th>&Delta; NPS</th><th>Surveys</th><th>vs Target</th></tr></thead><tbody>';
      var expB = (srB['Expert']||{{}}), nwbB = (srB['Newbie']||{{}});
      var expA = (srA['Expert']||{{}}), nwbA = (srA['Newbie']||{{}});
      var data = [{{k:'Expert',a:expA,b:expB}},{{k:'Newbie',a:nwbA,b:nwbB}}];
      data.forEach(function(r){{
        var npsA2 = (r.a.nps!==undefined?r.a.nps:null);
        var npsB2 = (r.b.nps!==undefined?r.b.nps:null);
        var delta2 = (npsA2!==null&&npsB2!==null)?Math.round((npsB2-npsA2)*100)/100:null;
        tbl += '<tr><td class="col-name">'+(icons[r.k]||'')+' '+r.k+'</td>'+
          '<td>'+nS(npsA2)+'</td><td>'+nS(npsB2)+'</td>'+
          '<td>'+pD2(delta2)+'</td>'+
          '<td class="bk-surv">'+(r.b.s||0)+'</td>'+
          '<td>'+pVS(npsB2)+'</td></tr>';
      }});
      // Gap Expert - Newbie
      var gE = expB.nps!==undefined?expB.nps:null, gN = nwbB.nps!==undefined?nwbB.nps:null;
      var gap = (gE!==null&&gN!==null)?Math.round((gE-gN)*100)/100:null;
      tbl += '<tr class="bk-total"><td class="col-name">Gap E&minus;N ('+lSrB+')</td>'+
        '<td colspan="2" style="font-weight:600;color:'+(gap!==null&&Math.abs(gap)>10?'#b71c1c':gap!==null&&Math.abs(gap)>5?'#e65100':'#2e7d32')+'">'+
        (gap!==null?(gap>=0?'+':'')+gap.toFixed(1)+'pp':'&mdash;')+'</td><td colspan="3"></td></tr>';
      return tbl+'</tbody></table></div>';
    }})();
  }}

  cont.innerHTML = html;
}}

function renderDD(period) {{
  var selectId = 'dd-select-' + period;
  var contentId = 'dd-content-' + period;
  var drv = document.getElementById(selectId).value;
  var content = document.getElementById(contentId);

  // Sincronizar todos os selects (mes, sem, vig)
  ['mes','sem','vig'].forEach(function(p) {{
    var el = document.getElementById('dd-select-' + p);
    if (el && p !== period) el.value = drv;
  }});

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

  try {{
  if (period === 'mes') {{
    var pts = d.monthly;
    var cur = pts[pts.length-1];
    var prev = pts[pts.length-2];
    var nCur  = cur.nps;
    var nPrev = prev.nps;
    var delta = (nCur !== null && nPrev !== null) ? parseFloat((nCur - nPrev).toFixed(2)) : null;
    var gapTgt = (nCur !== null && tgt) ? parseFloat((nCur - tgt).toFixed(2)) : null;

    var bkMesDD = DD_BREAKDOWN[drv];
    content.innerHTML =
      '<div class="dd-sc-grid">' +
        sc_dd('NPS '+cur.label, fmtNPS(nCur), null, nCur, tgt) +
        sc_dd('NPS '+prev.label, fmtNPS(nPrev), null, nPrev, tgt) +
        sc_dd('Variacao MoM', fmtDelta(delta), delta, null, null) +
        sc_dd('Target', tgt ? tgt.toFixed(1)+'%' : '—', null, null, null) +
        sc_dd('Gap vs Target', fmtDelta(gapTgt), gapTgt, null, null) +
      '</div>' +
      buildExecutiveBrief(drv,'mes',d,bkMesDD) +
      '<div class="dd-chart-section">' +
        '<div class="dd-chart-title">Historico Mensal — '+drv+'</div>' +
        '<div class="dd-chart-sub">NPS mensal Jan–Abr 2026 vs target do driver</div>' +
        '<div class="dd-chart-wrap"><canvas id="c-dd-mes-chart"></canvas></div>' +
      '</div>' +
      (function() {{
        var bkM = bkMesDD;
        var procKeysMes = (bkM && bkM['P_C'] && bkM['P_C']['M1']) ? Object.keys(bkM['P_C']['M1']).sort() :
                          ((bkM && bkM['P'] && bkM['P']['M1']) ? Object.keys(bkM['P']['M1']).sort() : []);
        var filterOptsMes = '<option value="">Todos os processos</option>' +
          procKeysMes.map(function(p){{ return '<option value="'+p.replace(/"/g,"&quot;")+'">'+p+'</option>'; }}).join('');
        var filterBarMes = '<div style="display:flex;align-items:center;gap:10px;margin:14px 0 4px;padding:8px 12px;background:#f5f7ff;border-radius:8px;border:1px solid #dde2f0">'+
          '<span style="font-size:12px;font-weight:600;color:#3a3f6b;white-space:nowrap">&#128269; Filtrar por processo:</span>'+
          '<select class="dd-select" style="flex:1;max-width:320px" '+
            'onchange="renderBreakdownTables(this)" '+
            'data-drv="'+drv+'" data-period="mes" '+
            'data-pa="M2" data-pb="M1" '+
            'data-tgt="'+(d.target!=null?d.target:'')+'" '+
            'data-lsuf="MoM" data-lwow="'+M2_LABEL+' vs '+M1_LABEL+'">'+
            filterOptsMes+
          '</select></div>';
        var initTablesMes =
          '<div class="dd-section-title">Processos — MoM ('+M2_LABEL+' vs '+M1_LABEL+')</div>'+
          buildBreakdownTable(bkM,'P','M2','M1',d.target,'Processo')+
          '<div class="dd-section-title">Canal — MoM</div>'+
          buildBreakdownTable(bkM,'C','M2','M1',d.target,'Canal')+
          '<div class="dd-section-title">Oficina — MoM</div>'+
          buildBreakdownTable(bkM,'O','M2','M1',d.target,'Oficina')+
          '<div class="dd-section-title">Senioridade por processo — MoM</div>'+
          buildSeniorityTable(bkM,'M2','M1',d.target);
        return filterBarMes + '<div id="bk-tables-mes">'+initTablesMes+'</div>';
      }})()

    var labels = pts.map(function(p){{ return p.label; }});
    var values = pts.map(function(p){{ return p.nps; }});
    var colors = values.map(function(v){{ return (tgt && v !== null && v < tgt) ? 'rgba(210,45,45,0.82)' : 'rgba(30,65,150,0.82)'; }});
    ddCharts[period].push(buildDDChart('c-dd-mes-chart', labels, values, colors, tgt, 'mensal'));

  }} else {{
    var isVig = period === 'vig';
    // VIG: scorecards e chart usam weekly_vig (20/abr → VIG); 'sem' usa weekly (6 semanas)
    var vigData = (DRV_HIST[drv] && DRV_HIST[drv].weekly_vig) ? DRV_HIST[drv].weekly_vig : [];
    var pts    = isVig ? vigData : d.weekly;
    var cur    = pts[pts.length-1];
    var prev   = pts[pts.length-2];
    var nCur   = cur ? cur.nps : null;
    var nPrev  = prev ? prev.nps : null;
    var delta  = (nCur !== null && nPrev !== null) ? parseFloat((nCur - nPrev).toFixed(2)) : null;
    var gapTgt = (nCur !== null && tgt) ? parseFloat((nCur - tgt).toFixed(2)) : null;

    // Para o chart vigente: histograma semanal completo + ponto VIG no final
    var weeklyFull = (DRV_HIST[drv] && DRV_HIST[drv].weekly) ? DRV_HIST[drv].weekly : d.weekly;
    var chartPts = isVig
      ? weeklyFull.concat([{{label: VIG_LABEL+' ⚡', nps: nCur, s: cur ? cur.s : 0}}])
      : d.weekly;

    var vigNote = isVig
      ? '<div style="margin:6px 0 14px;padding:6px 12px;background:#fff8e1;border:1px solid #ffe082;border-radius:6px;font-size:11px;color:#f57f17">&#9889; Vigente parcial ({VIG_LABEL}). Breakdowns mostram semana fechada (S1 vs S2).</div>'
      : '';

    var bkSemDD = DD_BREAKDOWN[drv];
    content.innerHTML =
      '<div class="dd-sc-grid">' +
        sc_dd('NPS '+(cur?cur.label:''), fmtNPS(nCur), null, nCur, tgt) +
        sc_dd('NPS '+(prev?prev.label:''), fmtNPS(nPrev), null, nPrev, tgt) +
        sc_dd(isVig?'Variacao VIG vs S1':'Variacao WoW', fmtDelta(delta), delta, null, null) +
        sc_dd('Target', tgt ? tgt.toFixed(1)+'%' : '—', null, null, null) +
        sc_dd('Gap vs Target', fmtDelta(gapTgt), gapTgt, null, null) +
      '</div>' +
      buildExecutiveBrief(drv,period,d,bkSemDD) +
      '<div class="dd-chart-section">' +
        '<div class="dd-chart-title">Historico Semanal — '+drv+(isVig?' + Vigente':'')+'</div>' +
        '<div class="dd-chart-sub">NPS semanal vs target do driver'+(isVig?' | ⚡ = vigente parcial ({VIG_LABEL})':'')+'</div>' +
        '<div class="dd-chart-wrap"><canvas id="c-dd-'+period+'-chart"></canvas></div>' +
      '</div>' +
      vigNote +
      (function() {{
        var bk     = bkSemDD;
        var hasVig = isVig && bk && bk['P'] && bk['P']['VIG'];
        var pA_bk  = isVig ? (hasVig ? 'S1' : 'S2') : 'S2';
        var pB_bk  = isVig ? (hasVig ? 'VIG' : 'S1') : 'S1';
        var lWoW   = isVig ? (hasVig ? S1_LABEL+' &rarr; '+VIG_LABEL+' &#9889;' : 'Ref. S1 ('+S2_LABEL+' &rarr; '+S1_LABEL+')') : S2_LABEL+' vs '+S1_LABEL;
        var lSufS  = isVig ? (hasVig ? 'VIG &#9889;' : 'Ref. S1') : 'WoW';

        // Opcoes de processo para o filtro
        var procKeys = (bk && bk['P_C'] && bk['P_C'][pB_bk]) ? Object.keys(bk['P_C'][pB_bk]).sort() :
                       ((bk && bk['P'] && bk['P'][pB_bk]) ? Object.keys(bk['P'][pB_bk]).sort() : []);
        var filterOpts = '<option value="">Todos os processos</option>' +
          procKeys.map(function(p){{ return '<option value="'+p.replace(/"/g,"&quot;")+'">'+p+'</option>'; }}).join('');
        var filterBar = '<div style="display:flex;align-items:center;gap:10px;margin:14px 0 4px;padding:8px 12px;background:#f5f7ff;border-radius:8px;border:1px solid #dde2f0">'+
          '<span style="font-size:12px;font-weight:600;color:#3a3f6b;white-space:nowrap">&#128269; Filtrar por processo:</span>'+
          '<select class="dd-select" style="flex:1;max-width:320px" '+
            'onchange="renderBreakdownTables(this)" '+
            'data-drv="'+drv+'" data-period="'+period+'" '+
            'data-pa="'+pA_bk+'" data-pb="'+pB_bk+'" '+
            'data-tgt="'+(d.target!=null?d.target:'')+'" '+
            'data-lsuf="'+lSufS+'" data-lwow="'+lWoW.replace(/"/g,"&quot;")+'">'+
            filterOpts+
          '</select>'+
          '</div>';

        // Tabelas iniciais (sem filtro de processo = nivel driver)
        var initTables =
          '<div class="dd-section-title">Processos — '+(isVig ? lWoW : 'WoW ('+lWoW+')')+'</div>'+
          buildBreakdownTable(bk,'P',pA_bk,pB_bk,d.target,'Processo')+
          '<div class="dd-section-title">Canal — '+lSufS+'</div>'+
          buildBreakdownTable(bk,'C',pA_bk,pB_bk,d.target,'Canal')+
          '<div class="dd-section-title">Oficina — '+lSufS+'</div>'+
          buildBreakdownTable(bk,'O',pA_bk,pB_bk,d.target,'Oficina')+
          '<div class="dd-section-title">Senioridade por processo — '+lSufS+'</div>'+
          buildSeniorityTable(bk,pA_bk,pB_bk,d.target);

        return filterBar +
          '<div id="bk-tables-'+period+'">'+initTables+'</div>';
      }})()

    var labels = chartPts.map(function(p){{ return p.label; }});
    var values = chartPts.map(function(p){{ return p.nps; }});
    var colors = values.map(function(v,i){{
      if(isVig && i===chartPts.length-1) return 'rgba(230,130,0,0.85)';
      return (tgt && v !== null && v < tgt) ? 'rgba(210,45,45,0.82)' : 'rgba(30,65,150,0.82)';
    }});
    ddCharts[period].push(buildDDChart('c-dd-'+period+'-chart', labels, values, colors, tgt, 'semanal'));
  }}
  }} catch(e) {{
    content.innerHTML = '<div style="padding:16px;margin:12px;background:#ffebee;border:1px solid #ef9a9a;border-radius:8px;font-size:12px;color:#c62828">' +
      '<b>Erro ao renderizar Deep Dive:</b> ' + e.message + '<br><small>' + (e.stack||'').split('\\n').slice(0,3).join(' | ') + '</small></div>';
  }}
}}

function buildSeniorityTable(drvData, periodA, periodB, drvTarget) {{
  function nStr(v){{ return v!==null&&v!==undefined?v.toFixed(1)+'%':'&mdash;'; }}
  function pDelta(v){{
    if(v===null||v===undefined) return '<span class="pill pill-neu">&mdash;</span>';
    var s=(v>=0?'+':'')+v.toFixed(2)+' pp';
    var c=v>=1?'pill-pos-hi':v>0?'pill-pos-lo':v>=-1?'pill-dn1':'pill-neg-hi';
    return '<span class="pill '+c+'">'+s+'</span>';
  }}
  function pTgt(nps,tgt){{
    if(nps===null||!tgt) return '<span class="pill pill-neu">&mdash;</span>';
    var g=nps-tgt; var s=(g>=0?'+':'')+g.toFixed(2)+' pp';
    return '<span class="pill '+(g>=0?'pill-pos-hi':'pill-neg-hi')+'">'+s+'</span>';
  }}
  function pGap(g){{
    if(g===null||g===undefined) return '<span style="color:#888">&mdash;</span>';
    var abs = Math.abs(g);
    var col = abs > 10 ? '#b71c1c' : abs > 5 ? '#e65100' : '#2e7d32';
    return '<span style="font-weight:600;color:'+col+'">'+(g>=0?'+':'')+g.toFixed(1)+'pp</span>';
  }}
  var lA = periodA==='M2'?M2_LABEL:(periodA==='S2'?S2_LABEL:(periodA==='S1'?S1_LABEL:periodA));
  var lB = periodB==='M1'?M1_LABEL:(periodB==='S1'?S1_LABEL:(periodB==='VIG'?VIG_LABEL+'&#9889;':periodB));

  // Usar Sr_P (por processo) se disponivel; senao Sr (geral)
  var srP = (drvData&&drvData.Sr_P)||{{}};
  var srPb = srP[periodB]||{{}};
  var srPa = srP[periodA]||{{}};
  var hasSrP = Object.keys(srPb).length > 0;

  if (hasSrP) {{
    // Vista por processo: cada linha = 1 processo, colunas Expert/Newbie no periodo atual
    var procs = Object.keys(srPb).sort(function(a,b){{
      var sA = ((srPb[a]['Expert']||{{}}).s||0) + ((srPb[a]['Newbie']||{{}}).s||0);
      var sB = ((srPb[b]['Expert']||{{}}).s||0) + ((srPb[b]['Newbie']||{{}}).s||0);
      return sB - sA;
    }});

    var html = '<div class="bk-wrap"><table class="bk-table">'+
      '<colgroup><col style="width:26%"><col style="width:11%"><col style="width:7%">'+
      '<col style="width:11%"><col style="width:7%"><col style="width:10%">'+
      '<col style="width:10%"><col style="width:10%"></colgroup>'+
      '<thead><tr>'+
      '<th class="col-name">Processo</th>'+
      '<th>&#127775; Expert NPS</th><th>Surv.</th>'+
      '<th>&#128164; Newbie NPS</th><th>Surv.</th>'+
      '<th>Gap E&minus;N</th><th>&Delta; Expert</th><th>&Delta; Newbie</th>'+
      '</tr></thead><tbody>';

    var totEp=0,totEd=0,totEs=0,totNp=0,totNd=0,totNs=0;
    procs.forEach(function(proc){{
      var cur = srPb[proc]||{{}};
      var prev = srPa[proc]||{{}};
      var eB = cur['Expert']||{{}}, nB = cur['Newbie']||{{}};
      var eA = prev['Expert']||{{}}, nA = prev['Newbie']||{{}};
      var eNps = eB.nps, nNps = nB.nps;
      var eNpsA = eA.nps, nNpsA = nA.nps;
      var gap = (eNps!==null&&eNps!==undefined&&nNps!==null&&nNps!==undefined) ? Math.round((eNps-nNps)*100)/100 : null;
      var dE = (eNpsA!==null&&eNpsA!==undefined&&eNps!==null&&eNps!==undefined) ? Math.round((eNps-eNpsA)*100)/100 : null;
      var dN = (nNpsA!==null&&nNpsA!==undefined&&nNps!==null&&nNps!==undefined) ? Math.round((nNps-nNpsA)*100)/100 : null;
      var rowBg = (gap!==null&&Math.abs(gap)>10)?'background:#fff3e0;':'';
      totEp+=eB.p||0; totEd+=eB.d||0; totEs+=eB.s||0;
      totNp+=nB.p||0; totNd+=nB.d||0; totNs+=nB.s||0;
      html+='<tr style="'+rowBg+'">'+
        '<td class="col-name">'+proc+'</td>'+
        '<td>'+nStr(eNps)+'</td><td class="bk-surv">'+(eB.s||0)+'</td>'+
        '<td>'+nStr(nNps)+'</td><td class="bk-surv">'+(nB.s||0)+'</td>'+
        '<td>'+pGap(gap)+'</td>'+
        '<td>'+pDelta(dE)+'</td>'+
        '<td>'+pDelta(dN)+'</td>'+
      '</tr>';
    }});

    // Linha total
    function npsCalc(p,d,s){{ return s>0?Math.round(100*(p-d)/s*10)/10:null; }}
    var eNpsT=npsCalc(totEp,totEd,totEs), nNpsT=npsCalc(totNp,totNd,totNs);
    var gapT=(eNpsT!==null&&nNpsT!==null)?Math.round((eNpsT-nNpsT)*100)/100:null;
    html+='<tr class="bk-total">'+
      '<td class="col-name">Total Driver</td>'+
      '<td>'+nStr(eNpsT)+'</td><td class="bk-surv">'+totEs+'</td>'+
      '<td>'+nStr(nNpsT)+'</td><td class="bk-surv">'+totNs+'</td>'+
      '<td>'+pGap(gapT)+'</td><td></td><td></td>'+
    '</tr>';

    return html+'</tbody></table></div>';
  }}

  // Fallback: tabela geral Expert vs Newbie (sem Sr_P disponivel)
  var sr = (drvData&&drvData.Sr)||{{}};
  var dA = sr[periodA]||{{}}, dB = sr[periodB]||{{}};
  var npsExp = {{a:(dA['Expert']||{{}}).nps, b:(dB['Expert']||{{}}).nps, sB:(dB['Expert']||{{}}).s||0}};
  var npsNwb = {{a:(dA['Newbie']||{{}}).nps, b:(dB['Newbie']||{{}}).nps, sB:(dB['Newbie']||{{}}).s||0}};
  var html = '<div class="bk-wrap"><table class="bk-table">'+
    '<colgroup><col style="width:22%"><col style="width:12%"><col style="width:12%">'+
    '<col style="width:12%"><col style="width:10%"><col style="width:13%"></colgroup>'+
    '<thead><tr>'+
    '<th class="col-name">Senioridade</th><th>'+lA+'</th><th>'+lB+'</th>'+
    '<th>&Delta; NPS</th><th>Surveys</th><th>vs Target</th>'+
    '</tr></thead><tbody>';
  [{{k:'&#127775; Expert',d:npsExp}},{{k:'&#128164; Newbie',d:npsNwb}}].forEach(function(r){{
    var d=r.d;
    var delta=(d.a!==null&&d.b!==null)?Math.round((d.b-d.a)*100)/100:null;
    html+='<tr><td class="col-name">'+r.k+'</td><td>'+nStr(d.a)+'</td><td>'+nStr(d.b)+'</td>'+
      '<td>'+pDelta(delta)+'</td><td class="bk-surv">'+d.sB+'</td><td>'+pTgt(d.b,drvTarget)+'</td></tr>';
  }});
  var gapB=(npsExp.b!==null&&npsNwb.b!==null)?Math.round((npsExp.b-npsNwb.b)*100)/100:null;
  html+='<tr class="bk-total"><td class="col-name">Gap E&minus;N ('+lB+')</td>'+
    '<td colspan="2" style="font-weight:600">'+pGap(gapB)+'</td><td colspan="3"></td></tr>';
  return html+'</tbody></table></div>';
}}

function buildBreakdownTable(drvData, dim, periodA, periodB, drvTarget, dimLabel) {{
    if (!drvData || !drvData[dim]) return '<div class="dd-hint">Sem dados</div>';

    var dataA = drvData[dim][periodA] || {{}};
    var dataB = drvData[dim][periodB] || {{}};
    var keys  = Array.from(new Set(Object.keys(dataA).concat(Object.keys(dataB))));
    if (keys.length === 0) return '<div class="dd-hint">Sem dados para este periodo</div>';

    var lA = periodA==='M2'?M2_LABEL:(periodA==='S2'?S2_LABEL:(periodA==='S1'?S1_LABEL:periodA));
    var lB = periodB==='M1'?M1_LABEL:(periodB==='S1'?S1_LABEL:(periodB==='VIG'?VIG_LABEL+' &#9889;':periodB));

    // Helpers
    function fN(v) {{ return v!==null&&v!==undefined ? v.toFixed(1)+'%' : '&mdash;'; }}
    function pD(v) {{
        if(v===null||v===undefined) return '<span class="pill pill-neu">&mdash;</span>';
        var s=(v>=0?'+':'')+v.toFixed(2)+' pp';
        var c=v>=1?'pill-pos-hi':v>=0?'pill-pos-lo':v>=-1?'pill-dn1':'pill-neg-hi';
        return '<span class="pill '+c+'">'+s+'</span>';
    }}
    function pVT(nps) {{
        if(nps===null||drvTarget===null||drvTarget===undefined) return '<span class="pill pill-neu">&mdash;</span>';
        var g=nps-drvTarget; var s=(g>=0?'+':'')+g.toFixed(2)+' pp';
        return '<span class="pill '+(g>=0?'pill-pos-hi':'pill-neg-hi')+'">'+s+'</span>';
    }}
    function pGap2(g) {{
        if(g===null||g===undefined) return '<span style="color:#888">&mdash;</span>';
        var abs=Math.abs(g), col=abs>10?'#b71c1c':abs>5?'#e65100':'#2e7d32';
        return '<span style="font-weight:600;color:'+col+'">'+(g>=0?'+':'')+g.toFixed(1)+'pp</span>';
    }}

    // Totais para NPS consolidado
    var totA={{p:0,d:0,s:0}}, totB={{p:0,d:0,s:0}};
    keys.forEach(function(k) {{
        var a=dataA[k]||{{}}; var b=dataB[k]||{{}};
        totA.p+=a.p||0; totA.d+=a.d||0; totA.s+=a.s||0;
        totB.p+=b.p||0; totB.d+=b.d||0; totB.s+=b.s||0;
    }});
    var npsA_tot=totA.s>0?(totA.p-totA.d)/totA.s*100:null;
    var npsB_tot=totB.s>0?(totB.p-totB.d)/totB.s*100:null;
    var totDelta=(npsA_tot!==null&&npsB_tot!==null)?Math.round((npsB_tot-npsA_tot)*100)/100:null;

    // Formato padrão para todos os dims (P, C, O)
    var npsB_totF = npsB_tot;
    var items2 = keys.map(function(k) {{
        var a=dataA[k]||{{p:0,d:0,s:0,nps:null}};
        var b=dataB[k]||{{p:0,d:0,s:0,nps:null}};
        var shaA=totA.s>0?a.s/totA.s:0, shaB=totB.s>0?b.s/totB.s:0;
        var nA=a.nps, nB=b.nps;
        var neto=(shaA>0&&nA!==null&&nB!==null)?shaA*(nB-nA):0;
        var mix=(nB!==null&&npsB_totF!==null)?(shaB-shaA)*(nB-npsB_totF):0;
        return {{k:k,a:a,b:b,shaB:shaB,impact:Math.round((neto+mix)*100)/100}};
    }});
    items2.sort(function(x,y){{ return Math.abs(y.impact)-Math.abs(x.impact); }});

    function pillImpacto(v) {{
        if(v===0) return '<span class="pill pill-neu">0,00 pp</span>';
        var s=(v>=0?'+':'')+v.toFixed(2)+' pp';
        var c=v>=0.3?'pill-pos-hi':v>=0.05?'pill-pos-lo':v<=-0.3?'pill-neg-hi':v<=-0.05?'pill-dn1':'pill-neu';
        return '<span class="pill '+c+'">'+s+'</span>';
    }}
    function pillTend(delta) {{
        if(delta===null) return '<span class="pill pill-neu">&mdash;</span>';
        if(delta>=3)   return '<span class="pill pill-up2">&#8679;&#8679; Em alta</span>';
        if(delta>=0.5) return '<span class="pill pill-up1">&#8679; Evolucao</span>';
        if(delta>-0.5) return '<span class="pill pill-flat">&#8594; Estavel</span>';
        if(delta>-3)   return '<span class="pill pill-dn1">&#8681; Queda</span>';
        return '<span class="pill pill-dn2">&#8681;&#8681; Em queda</span>';
    }}

    var html2 = '<div class="bk-wrap"><table class="bk-table">' +
        '<colgroup><col style="width:24%"><col style="width:8%"><col style="width:8%">' +
        '<col style="width:11%"><col style="width:8%"><col style="width:6%">' +
        '<col style="width:11%"><col style="width:12%"><col style="width:12%"></colgroup>' +
        '<thead><tr><th class="col-name">'+(dimLabel||'Dimensao')+'</th>' +
        '<th>'+lA+'</th><th>'+lB+'</th>' +
        '<th>&Delta; NPS</th><th>Surveys</th><th>Share</th>' +
        '<th>Impacto</th><th>VS Target</th><th>Tendencia</th>' +
        '</tr></thead><tbody>';

    var totImpact=0;
    items2.forEach(function(item) {{
        var a=item.a, b=item.b;
        var delta=(a.nps!==null&&b.nps!==null)?Math.round((b.nps-a.nps)*100)/100:null;
        totImpact+=item.impact;
        html2 += '<tr>'+
            '<td class="col-name">'+item.k+'</td>'+
            '<td>'+fN(a.nps)+'</td><td>'+fN(b.nps)+'</td>'+
            '<td>'+pD(delta)+'</td>'+
            '<td class="bk-surv">'+(b.s||0).toLocaleString('pt-BR')+'</td>'+
            '<td class="bk-surv">'+(item.shaB*100).toFixed(1)+'%</td>'+
            '<td>'+pillImpacto(item.impact)+'</td>'+
            '<td>'+pVT(b.nps)+'</td>'+
            '<td>'+pillTend(delta)+'</td></tr>';
    }});
    totImpact=Math.round(totImpact*100)/100;
    html2 += '<tr class="bk-total"><td class="col-name">Total driver</td>'+
        '<td>'+fN(npsA_tot)+'</td><td>'+fN(npsB_tot)+'</td>'+
        '<td>'+pD(totDelta)+'</td>'+
        '<td class="bk-surv">'+totB.s.toLocaleString('pt-BR')+'</td>'+
        '<td class="bk-surv">100%</td>'+
        '<td>'+pillImpacto(totImpact)+'</td>'+
        '<td>'+pVT(npsB_tot)+'</td>'+
        '<td>'+pillTend(totDelta)+'</td></tr>';
    return html2+'</tbody></table></div>';
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
