#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NPS Gerência Sellers BR — Dashboard Gerencial
Filtros: CENTER=BR, MP_ON_FLAG=E-Commerce, QUE_QUEUE_TYPE=VALID_CS, NPS_TARGET_DRIVER_GROUP=Sellers
Sem abertura por processo. Rodar: python generate_html_gerencia.py
"""

# ═══════════════════════════════════════════════════════════════
# SECTION 1: METADATA  ← skill atualiza esta seção
# ═══════════════════════════════════════════════════════════════
from datetime import datetime as _dt
import json as _json

REPORT_DATE = _dt.now().strftime("%d/%m/%Y")
REPORT_TIME = _dt.now().strftime("%H:%M")
S1_LABEL  = "08/jun – 14/jun"
S2_LABEL  = "01/jun – 07/jun"
VIG_LABEL = "15/jun – 18/jun"
M1_LABEL  = "Maio 2026"
M2_LABEL  = "Abril 2026"
NPS_TARGET = 56.61  # SUM(NUM_TARGET_NPS)/SUM(DENOM_TARGET_NPS) via LK JOIN — Abril/2026 (~52,5% oficial)

DRIVER_TARGETS = {   # SUM(NUM_TARGET_NPS)/SUM(DENOM_TARGET_NPS) por driver — Mai/2026
    "CBT":                                          74.63,
    "Experiencia Impositiva Mature":                53.97,
    "Experiencia Impositiva Meli Pro":              38.73,
    "Experiencia Impositiva Seller Dev":            59.67,
    "FBM-S Mature":                                 20.0,
    "FBM-S Meli Pro":                               49.1,
    "FBM-S Seller Dev":                             43.36,
    "ME Vendedor Mature":                           50.0,
    "ME Vendedor Meli Pro":                         81.93,
    "ME Vendedor Seller Dev":                       58.3,
    "Otros CV":                                     53.93,
    "PCF Vendedor Mature":                          29.28,
    "PCF Vendedor Meli Pro":                        63.93,
    "PCF Vendedor Seller Dev":                      40.52,
    "PDD DS&XD - Vendedor":                         16.4,
    "PDD FBM - Vendedor":                           40.67,
    "PDD Fotos - Vendedor":                         33.13,
    "PDD MP,FLEX & CBT - Vendedor":                 12.33,
    "PNR ME - Vendedor":                            27.23,
    "PNR MP - Vendedor":                            29.57,
    "Partners":                                     70.61,
    "Post Venta Mature":                            50.8,
    "Post Venta Meli Pro":                          88.11,
    "Post Venta Seller Dev":                        54.0,
    "Publicaciones Mature":                         47.73,
    "Publicaciones Meli Pro":                       81.77,
    "Publicaciones Seller Dev":                     53.36,
}

# ═══════════════════════════════════════════════════════════════
# SECTION 2: DATA  ← skill atualiza esta seção (tuplas: promoters, detractors, surveys)
# ═══════════════════════════════════════════════════════════════
weekly_driver = {
    "CBT":                                       {"S2":(75,12,90), "S1":(100,12,116)},
    "Experiencia Impositiva Mature":             {"S2":(4,2,6), "S1":(3,0,3)},
    "Experiencia Impositiva Meli Pro":           {"S2":(5,4,9), "S1":(5,0,5)},
    "Experiencia Impositiva Seller Dev":         {"S2":(75,17,97), "S1":(105,31,147)},
    "FBM-S Mature":                              {"S2":(9,5,16), "S1":(10,4,15)},
    "FBM-S Meli Pro":                            {"S2":(16,3,19), "S1":(11,1,13)},
    "FBM-S Seller Dev":                          {"S2":(73,26,105), "S1":(78,30,124)},
    "ME Vendedor Mature":                        {"S2":(69,6,82), "S1":(53,8,68)},
    "ME Vendedor Meli Pro":                      {"S2":(93,10,105), "S1":(114,9,131)},
    "ME Vendedor Seller Dev":                    {"S2":(779,76,912), "S1":(756,77,912)},
    "Otros CV":                                  {"S2":(75,52,137), "S1":(70,47,124)},
    "PCF Vendedor Mature":                       {"S2":(20,7,32), "S1":(19,10,33)},
    "PCF Vendedor Meli Pro":                     {"S2":(85,15,106), "S1":(75,8,87)},
    "PCF Vendedor Seller Dev":                   {"S2":(73,18,104), "S1":(110,31,151)},
    "PDD DS&XD - Vendedor":                      {"S2":(145,91,257), "S1":(121,85,234)},
    "PDD FBM - Vendedor":                        {"S2":(57,25,86), "S1":(34,16,62)},
    "PDD Fotos - Vendedor":                      {"S2":(5,3,9), "S1":(4,0,5)},
    "PDD MP,FLEX & CBT - Vendedor":              {"S2":(18,11,34), "S1":(18,15,36)},
    "PNR ME - Vendedor":                         {"S2":(40,20,67), "S1":(23,15,40)},
    "PNR MP - Vendedor":                         {"S2":(21,12,44), "S1":(29,20,55)},
    "Partners":                                  {"S2":(442,65,554), "S1":(494,75,624)},
    "Post Venta Mature":                         {"S2":(51,1,53), "S1":(54,9,67)},
    "Post Venta Meli Pro":                       {"S2":(192,9,206), "S1":(193,5,201)},
    "Post Venta Seller Dev":                     {"S2":(181,18,218), "S1":(235,24,284)},
    "Publicaciones Mature":                      {"S2":(27,4,32), "S1":(21,2,25)},
    "Publicaciones Meli Pro":                    {"S2":(68,3,80), "S1":(43,1,44)},
    "Publicaciones Seller Dev":                  {"S2":(416,78,554), "S1":(458,97,601)},
}

monthly_driver = {
    "CBT":                                       {"M2":(345,54,405), "M1":(104,14,122)},
    "Experiencia Impositiva Mature":             {"M2":(28,7,40), "M1":(5,0,5)},
    "Experiencia Impositiva Meli Pro":           {"M2":(13,3,18), "M1":(2,1,3)},
    "Experiencia Impositiva Seller Dev":         {"M2":(404,113,572), "M1":(82,42,133)},
    "FBM-S Mature":                              {"M2":(100,28,140), "M1":(9,4,20)},
    "FBM-S Meli Pro":                            {"M2":(53,9,70), "M1":(9,6,16)},
    "FBM-S Seller Dev":                          {"M2":(344,114,500), "M1":(84,30,125)},
    "ME Vendedor Mature":                        {"M2":(504,103,652), "M1":(77,10,92)},
    "ME Vendedor Meli Pro":                      {"M2":(320,26,361), "M1":(140,11,157)},
    "ME Vendedor Seller Dev":                    {"M2":(2710,375,3392), "M1":(863,121,1085)},
    "Otros CV":                                  {"M2":(754,244,1068), "M1":(188,54,263)},
    "PCF Vendedor Mature":                       {"M2":(225,68,326), "M1":(30,9,43)},
    "PCF Vendedor Meli Pro":                     {"M2":(272,42,351), "M1":(113,20,157)},
    "PCF Vendedor Seller Dev":                   {"M2":(395,118,569), "M1":(104,29,154)},
    "PDD DS&XD - Vendedor":                      {"M2":(533,409,1041), "M1":(166,147,361)},
    "PDD FBM - Vendedor":                        {"M2":(167,90,285), "M1":(47,34,87)},
    "PDD Fotos - Vendedor":                      {"M2":(36,23,64), "M1":(14,9,28)},
    "PDD MP,FLEX & CBT - Vendedor":              {"M2":(62,43,122), "M1":(30,16,48)},
    "PNR ME - Vendedor":                         {"M2":(150,90,258), "M1":(33,26,64)},
    "PNR MP - Vendedor":                         {"M2":(156,71,251), "M1":(49,26,85)},
    "Partners":                                  {"M2":(2229,360,2847), "M1":(699,100,878)},
    "Post Venta Mature":                         {"M2":(298,53,389), "M1":(43,8,56)},
    "Post Venta Meli Pro":                       {"M2":(416,15,447), "M1":(201,9,214)},
    "Post Venta Seller Dev":                     {"M2":(857,116,1059), "M1":(243,20,282)},
    "Publicaciones Mature":                      {"M2":(185,36,256), "M1":(23,4,31)},
    "Publicaciones Meli Pro":                    {"M2":(185,15,208), "M1":(96,5,104)},
    "Publicaciones Seller Dev":                  {"M2":(2000,374,2600), "M1":(515,125,703)},
}

drivers_vigente = {
    "CBT":                                       (0,0,0),
    "Experiencia Impositiva Mature":             (0,0,0),
    "Experiencia Impositiva Meli Pro":           (0,0,0),
    "Experiencia Impositiva Seller Dev":         (0,0,0),
    "FBM-S Mature":                              (0,0,0),
    "FBM-S Meli Pro":                            (0,0,0),
    "FBM-S Seller Dev":                          (0,0,0),
    "ME Vendedor Mature":                        (0,0,0),
    "ME Vendedor Meli Pro":                      (0,0,0),
    "ME Vendedor Seller Dev":                    (0,0,0),
    "Otros CV":                                  (0,0,0),
    "PCF Vendedor Mature":                       (0,0,0),
    "PCF Vendedor Meli Pro":                     (0,0,0),
    "PCF Vendedor Seller Dev":                   (0,0,0),
    "PDD DS&XD - Vendedor":                      (0,0,0),
    "PDD FBM - Vendedor":                        (0,0,0),
    "PDD Fotos - Vendedor":                      (0,0,0),
    "PDD MP,FLEX & CBT - Vendedor":              (0,0,0),
    "PNR ME - Vendedor":                         (0,0,0),
    "PNR MP - Vendedor":                         (0,0,0),
    "Partners":                                  (0,0,0),
    "Post Venta Mature":                         (0,0,0),
    "Post Venta Meli Pro":                       (0,0,0),
    "Post Venta Seller Dev":                     (0,0,0),
    "Publicaciones Mature":                      (0,0,0),
    "Publicaciones Meli Pro":                    (0,0,0),
    "Publicaciones Seller Dev":                  (0,0,0),
}

# ═══════════════════════════════════════════════════════════════
# SECTION 2C: HISTORICAL DATA
# ═══════════════════════════════════════════════════════════════
MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
WEEK_LABELS  = ["30/mar", "06/abr", "13/abr", "20/abr", "27/abr", "04/mai", "11/mai", "18/mai", "25/mai", "01/jun", "08/jun"]

monthly_history = {
    "CBT":                                       {"Jan":(481,57,549), "Fev":(224,27,254), "Mar":(323,58,395), "Abr":(345,54,405), "Mai":(66,11,80)},
    "Experiencia Impositiva Mature":             {"Jan":(81,18,113), "Fev":(49,14,70), "Mar":(45,20,72), "Abr":(28,7,40), "Mai":(5,0,5)},
    "Experiencia Impositiva Meli Pro":           {"Jan":(8,6,16), "Fev":(1,3,5), "Mar":(8,4,13), "Abr":(13,3,18), "Mai":(2,1,3)},
    "Experiencia Impositiva Seller Dev":         {"Jan":(574,111,744), "Fev":(350,86,477), "Mar":(312,108,469), "Abr":(404,113,572), "Mai":(63,32,101)},
    "FBM-S Mature":                              {"Jan":(197,94,320), "Fev":(135,61,216), "Mar":(130,45,203), "Abr":(100,28,140), "Mai":(9,4,19)},
    "FBM-S Meli Pro":                            {"Jan":(33,5,42), "Fev":(20,6,27), "Mar":(11,8,22), "Abr":(53,9,70), "Mai":(5,5,10)},
    "FBM-S Seller Dev":                          {"Jan":(537,168,793), "Fev":(340,109,501), "Mar":(347,125,524), "Abr":(344,114,500), "Mai":(74,25,107)},
    "ME Vendedor Mature":                        {"Jan":(2084,422,2688), "Fev":(1558,342,2082), "Mar":(809,157,1092), "Abr":(504,103,652), "Mai":(65,9,78)},
    "ME Vendedor Meli Pro":                      {"Jan":(126,17,149), "Fev":(93,9,109), "Mar":(60,10,75), "Abr":(320,26,361), "Mai":(111,10,126)},
    "ME Vendedor Seller Dev":                    {"Jan":(8138,1110,9984), "Fev":(5136,734,6390), "Mar":(2479,377,3133), "Abr":(2710,375,3392), "Mai":(682,96,854)},
    "Otros CV":                                  {"Jan":(935,420,1472), "Fev":(844,241,1206), "Mar":(775,182,1047), "Abr":(754,244,1068), "Mai":(140,38,197)},
    "PCF Vendedor Mature":                       {"Jan":(306,122,482), "Fev":(324,90,464), "Mar":(332,85,467), "Abr":(225,68,326), "Mai":(26,6,36)},
    "PCF Vendedor Meli Pro":                     {"Jan":(57,8,75), "Fev":(57,11,73), "Mar":(32,8,44), "Abr":(272,42,351), "Mai":(90,13,122)},
    "PCF Vendedor Seller Dev":                   {"Jan":(697,244,1059), "Fev":(529,173,768), "Mar":(536,166,790), "Abr":(395,118,569), "Mai":(79,21,118)},
    "PDD DS&XD - Vendedor":                      {"Jan":(406,324,830), "Fev":(452,332,906), "Mar":(645,486,1280), "Abr":(533,409,1041), "Mai":(115,102,245)},
    "PDD FBM - Vendedor":                        {"Jan":(93,39,153), "Fev":(101,40,160), "Mar":(193,89,306), "Abr":(167,90,285), "Mai":(38,23,66)},
    "PDD Fotos - Vendedor":                      {"Jan":(35,18,59), "Fev":(31,18,61), "Mar":(46,22,72), "Abr":(36,23,64), "Mai":(6,4,14)},
    "PDD MP,FLEX & CBT - Vendedor":              {"Jan":(59,56,124), "Fev":(75,61,151), "Mar":(87,58,166), "Abr":(62,43,122), "Mai":(21,11,33)},
    "PNR ME - Vendedor":                         {"Jan":(83,64,169), "Fev":(86,79,186), "Mar":(103,71,193), "Abr":(150,90,258), "Mai":(25,19,47)},
    "PNR MP - Vendedor":                         {"Jan":(122,85,239), "Fev":(147,88,258), "Mar":(140,90,266), "Abr":(156,71,251), "Mai":(35,18,61)},
    "Partners":                                  {"Jan":(1793,251,2254), "Fev":(1808,217,2198), "Mar":(2228,337,2806), "Abr":(2229,360,2847), "Mai":(527,80,670)},
    "Post Venta Mature":                         {"Jan":(403,114,543), "Fev":(363,85,493), "Mar":(392,76,520), "Abr":(298,53,389), "Mai":(38,6,49)},
    "Post Venta Meli Pro":                       {"Jan":(115,11,128), "Fev":(88,9,101), "Mar":(70,10,81), "Abr":(416,15,447), "Mai":(156,8,168)},
    "Post Venta Seller Dev":                     {"Jan":(1206,265,1585), "Fev":(983,209,1291), "Mar":(929,178,1186), "Abr":(857,116,1059), "Mai":(191,17,222)},
    "Publicaciones Mature":                      {"Jan":(321,73,429), "Fev":(286,47,362), "Mar":(258,51,345), "Abr":(185,36,256), "Mai":(18,3,25)},
    "Publicaciones Meli Pro":                    {"Jan":(43,8,53), "Fev":(34,2,40), "Mar":(18,7,26), "Abr":(185,15,208), "Mai":(79,4,85)},
    "Publicaciones Seller Dev":                  {"Jan":(3396,475,4216), "Fev":(2581,381,3231), "Mar":(2639,374,3309), "Abr":(2000,374,2600), "Mai":(396,91,534)},
}

weekly_history = {
    "CBT":                                       {"30/mar":(75,9,86), "06/abr":(87,12,101), "13/abr":(87,15,102), "20/abr":(77,16,96), "27/abr":(56,10,67), "04/mai":(85,12,100), "11/mai":(59,14,75), "18/mai":(98,23,122), "25/mai":(98,12,111), "01/jun":(75,12,90), "08/jun":(100,12,116)},
    "Experiencia Impositiva Mature":             {"30/mar":(12,5,20), "06/abr":(9,3,13), "13/abr":(6,2,8), "20/abr":(2,0,4), "27/abr":(5,0,5), "04/mai":(5,0,5), "11/mai":(4,1,5), "18/mai":(2,1,3), "25/mai":(0,2,3), "01/jun":(4,2,6), "08/jun":(3,0,3)},
    "Experiencia Impositiva Meli Pro":           {"30/mar":(2,1,3), "06/abr":(1,0,2), "13/abr":(2,1,4), "20/abr":(3,0,3), "27/abr":(5,2,7), "04/mai":(2,1,3), "11/mai":(4,0,5), "18/mai":(7,2,10), "25/mai":(0,3,4), "01/jun":(5,4,9), "08/jun":(5,0,5)},
    "Experiencia Impositiva Seller Dev":         {"30/mar":(66,25,100), "06/abr":(150,36,208), "13/abr":(112,33,160), "20/abr":(57,23,88), "27/abr":(50,13,70), "04/mai":(72,36,116), "11/mai":(67,30,104), "18/mai":(89,20,118), "25/mai":(106,19,139), "01/jun":(75,17,97), "08/jun":(105,31,147)},
    "FBM-S Mature":                              {"30/mar":(30,13,48), "06/abr":(28,7,40), "13/abr":(23,4,29), "20/abr":(17,4,21), "27/abr":(13,3,20), "04/mai":(9,4,20), "11/mai":(12,11,25), "18/mai":(6,3,10), "25/mai":(12,2,16), "01/jun":(9,5,16), "08/jun":(10,4,15)},
    "FBM-S Meli Pro":                            {"30/mar":(0,2,2), "06/abr":(9,2,12), "13/abr":(14,6,20), "20/abr":(17,0,20), "27/abr":(13,1,18), "04/mai":(9,6,16), "11/mai":(19,1,22), "18/mai":(21,2,26), "25/mai":(18,5,29), "01/jun":(16,3,19), "08/jun":(11,1,13)},
    "FBM-S Seller Dev":                          {"30/mar":(73,23,104), "06/abr":(74,24,115), "13/abr":(68,24,101), "20/abr":(85,29,121), "27/abr":(79,25,107), "04/mai":(69,24,104), "11/mai":(74,27,104), "18/mai":(73,24,104), "25/mai":(60,20,90), "01/jun":(73,26,105), "08/jun":(78,30,124)},
    "ME Vendedor Mature":                        {"30/mar":(170,28,219), "06/abr":(187,41,246), "13/abr":(111,22,143), "20/abr":(73,17,93), "27/abr":(48,11,65), "04/mai":(75,10,89), "11/mai":(53,16,72), "18/mai":(74,10,91), "25/mai":(67,14,85), "01/jun":(69,6,82), "08/jun":(53,8,68)},
    "ME Vendedor Meli Pro":                      {"30/mar":(10,6,17), "06/abr":(24,6,30), "13/abr":(76,4,83), "20/abr":(104,10,120), "27/abr":(110,4,120), "04/mai":(140,11,157), "11/mai":(114,12,134), "18/mai":(127,12,143), "25/mai":(95,9,107), "01/jun":(93,10,105), "08/jun":(114,9,131)},
    "ME Vendedor Seller Dev":                    {"30/mar":(508,79,635), "06/abr":(838,112,1053), "13/abr":(577,89,741), "20/abr":(529,76,654), "27/abr":(583,67,710), "04/mai":(739,108,940), "11/mai":(748,64,887), "18/mai":(742,74,880), "25/mai":(759,70,911), "01/jun":(779,76,912), "08/jun":(756,77,912)},
    "Otros CV":                                  {"30/mar":(139,36,195), "06/abr":(181,63,259), "13/abr":(158,56,230), "20/abr":(183,68,260), "27/abr":(159,44,223), "04/mai":(165,47,231), "11/mai":(223,88,329), "18/mai":(162,77,259), "25/mai":(168,78,265), "01/jun":(75,52,137), "08/jun":(70,47,124)},
    "PCF Vendedor Mature":                       {"30/mar":(68,14,91), "06/abr":(97,24,131), "13/abr":(51,19,81), "20/abr":(21,9,34), "27/abr":(23,7,33), "04/mai":(30,8,42), "11/mai":(18,8,28), "18/mai":(34,9,44), "25/mai":(19,5,28), "01/jun":(20,7,32), "08/jun":(19,10,33)},
    "PCF Vendedor Meli Pro":                     {"30/mar":(4,3,7), "06/abr":(13,3,19), "13/abr":(67,12,89), "20/abr":(101,14,131), "27/abr":(91,12,111), "04/mai":(113,20,157), "11/mai":(111,10,130), "18/mai":(118,18,145), "25/mai":(116,13,137), "01/jun":(85,15,106), "08/jun":(75,8,87)},
    "PCF Vendedor Seller Dev":                   {"30/mar":(84,23,125), "06/abr":(98,29,136), "13/abr":(95,28,137), "20/abr":(82,30,129), "27/abr":(81,26,119), "04/mai":(94,28,138), "11/mai":(82,29,123), "18/mai":(75,32,116), "25/mai":(79,29,123), "01/jun":(73,18,104), "08/jun":(110,31,151)},
    "PDD DS&XD - Vendedor":                      {"30/mar":(136,106,275), "06/abr":(113,95,236), "13/abr":(135,107,261), "20/abr":(115,76,214), "27/abr":(118,96,229), "04/mai":(122,104,268), "11/mai":(115,111,249), "18/mai":(129,100,254), "25/mai":(125,115,275), "01/jun":(145,91,257), "08/jun":(121,85,234)},
    "PDD FBM - Vendedor":                        {"30/mar":(45,16,63), "06/abr":(40,18,65), "13/abr":(38,25,72), "20/abr":(43,25,74), "27/abr":(39,18,64), "04/mai":(31,26,61), "11/mai":(33,23,61), "18/mai":(62,25,95), "25/mai":(67,20,95), "01/jun":(57,25,86), "08/jun":(34,16,62)},
    "PDD Fotos - Vendedor":                      {"30/mar":(9,5,15), "06/abr":(7,5,12), "13/abr":(8,8,17), "20/abr":(10,7,20), "27/abr":(7,2,12), "04/mai":(14,8,24), "11/mai":(7,3,11), "18/mai":(12,4,16), "25/mai":(8,6,17), "01/jun":(5,3,9), "08/jun":(4,0,5)},
    "PDD MP,FLEX & CBT - Vendedor":              {"30/mar":(14,7,24), "06/abr":(16,9,28), "13/abr":(21,11,39), "20/abr":(8,10,19), "27/abr":(19,13,38), "04/mai":(21,9,31), "11/mai":(25,9,38), "18/mai":(20,10,31), "25/mai":(17,12,32), "01/jun":(18,11,34), "08/jun":(18,15,36)},
    "PNR ME - Vendedor":                         {"30/mar":(18,9,30), "06/abr":(21,15,38), "13/abr":(23,10,37), "20/abr":(63,41,110), "27/abr":(38,25,68), "04/mai":(26,18,48), "11/mai":(22,26,59), "18/mai":(24,11,39), "25/mai":(35,16,57), "01/jun":(40,20,67), "08/jun":(23,15,40)},
    "PNR MP - Vendedor":                         {"30/mar":(33,15,56), "06/abr":(54,16,74), "13/abr":(32,13,49), "20/abr":(28,25,57), "27/abr":(38,13,62), "04/mai":(30,18,54), "11/mai":(33,17,59), "18/mai":(26,9,44), "25/mai":(30,21,62), "01/jun":(21,12,44), "08/jun":(29,20,55)},
    "Partners":                                  {"30/mar":(448,77,574), "06/abr":(460,76,587), "13/abr":(575,85,725), "20/abr":(567,85,719), "27/abr":(548,99,717), "04/mai":(516,74,642), "11/mai":(588,87,741), "18/mai":(520,70,660), "25/mai":(505,65,637), "01/jun":(442,65,554), "08/jun":(494,75,624)},
    "Post Venta Mature":                         {"30/mar":(88,20,114), "06/abr":(89,15,117), "13/abr":(76,11,97), "20/abr":(46,6,58), "27/abr":(42,8,57), "04/mai":(40,8,53), "11/mai":(62,3,71), "18/mai":(50,10,66), "25/mai":(61,7,72), "01/jun":(51,1,53), "08/jun":(54,9,67)},
    "Post Venta Meli Pro":                       {"30/mar":(8,0,9), "06/abr":(25,2,29), "13/abr":(104,5,112), "20/abr":(149,1,152), "27/abr":(135,7,150), "04/mai":(200,9,213), "11/mai":(179,8,191), "18/mai":(211,8,227), "25/mai":(178,10,193), "01/jun":(192,9,206), "08/jun":(193,5,201)},
    "Post Venta Seller Dev":                     {"30/mar":(176,39,233), "06/abr":(239,39,301), "13/abr":(194,23,233), "20/abr":(177,18,209), "27/abr":(176,20,219), "04/mai":(215,18,249), "11/mai":(194,24,235), "18/mai":(181,19,210), "25/mai":(204,12,236), "01/jun":(181,18,218), "08/jun":(235,24,284)},
    "Publicaciones Mature":                      {"30/mar":(61,13,87), "06/abr":(72,12,101), "13/abr":(37,14,57), "20/abr":(25,3,30), "27/abr":(19,1,22), "04/mai":(22,4,30), "11/mai":(27,5,32), "18/mai":(21,3,29), "25/mai":(19,5,24), "01/jun":(27,4,32), "08/jun":(21,2,25)},
    "Publicaciones Meli Pro":                    {"30/mar":(6,1,8), "06/abr":(6,1,8), "13/abr":(37,4,44), "20/abr":(59,4,64), "27/abr":(81,5,89), "04/mai":(96,5,104), "11/mai":(89,3,92), "18/mai":(88,1,90), "25/mai":(87,4,95), "01/jun":(68,3,80), "08/jun":(43,1,44)},
    "Publicaciones Seller Dev":                  {"30/mar":(502,88,653), "06/abr":(607,103,769), "13/abr":(453,80,587), "20/abr":(398,76,512), "27/abr":(381,88,517), "04/mai":(370,100,520), "11/mai":(371,81,493), "18/mai":(378,96,510), "25/mai":(476,104,649), "01/jun":(416,78,554), "08/jun":(458,97,601)},
}

weekly_history_vig = {drv: {**weekly_history[drv], "27/abr ⚡": drivers_vigente[drv]} for drv in weekly_history}
WEEK_LABELS_VIG = WEEK_LABELS + ["27/abr ⚡"]

# ═══════════════════════════════════════════════════════════════
# SECTION 3: CALCULATIONS
# ═══════════════════════════════════════════════════════════════
def nps(p, d, s): return round(100.0 * (p - d) / s, 2) if s > 0 else 0.0

def mix_neto(data, pa, pb, surv_a_tot, surv_b_tot, nps_b_tot):
    out = {}
    for drv, periods in data.items():
        a = periods.get(pa, (0,0,0)); b = periods.get(pb, (0,0,0))
        na = nps(*a); nb = nps(*b)
        sha = a[2]/surv_a_tot if surv_a_tot else 0
        shb = b[2]/surv_b_tot if surv_b_tot else 0
        nt = round(sha*(nb-na), 2); mx = round((shb-sha)*(nb-nps_b_tot), 2)
        out[drv] = {"surv_a": a[2], "nps_a": na, "share_a": round(sha*100,1),
                    "surv_b": b[2], "nps_b": nb, "share_b": round(shb*100,1),
                    "neto": nt, "mix": mx, "var": round(nt+mx, 2)}
    return out

sS2 = sum(v["S2"][2] for v in weekly_driver.values())
sS1 = sum(v["S1"][2] for v in weekly_driver.values())
pS2 = sum(v["S2"][0] for v in weekly_driver.values()); dS2 = sum(v["S2"][1] for v in weekly_driver.values())
pS1 = sum(v["S1"][0] for v in weekly_driver.values()); dS1 = sum(v["S1"][1] for v in weekly_driver.values())
nS2 = nps(pS2,dS2,sS2); nS1 = nps(pS1,dS1,sS1); dW = round(nS1-nS2, 2)
wD  = mix_neto(weekly_driver, "S2", "S1", sS2, sS1, nS1)

sM2 = sum(v["M2"][2] for v in monthly_driver.values())
sM1 = sum(v["M1"][2] for v in monthly_driver.values())
pM2 = sum(v["M2"][0] for v in monthly_driver.values()); dM2x = sum(v["M2"][1] for v in monthly_driver.values())
pM1 = sum(v["M1"][0] for v in monthly_driver.values()); dM1x = sum(v["M1"][1] for v in monthly_driver.values())
nM2 = nps(pM2,dM2x,sM2); nM1 = nps(pM1,dM1x,sM1); dM = round(nM1-nM2, 2)
mD  = mix_neto(monthly_driver, "M2", "M1", sM2, sM1, nM1)

sVig  = sum(v[2] for v in drivers_vigente.values())
pVig  = sum(v[0] for v in drivers_vigente.values()); dVig_s = sum(v[1] for v in drivers_vigente.values())
nVig  = nps(pVig, dVig_s, sVig); dVW = round(nVig-nS1, 2)
wDv   = {drv: {"S1": weekly_driver[drv]["S1"], "Vig": drivers_vigente.get(drv,(0,0,0))} for drv in weekly_driver}
vD    = mix_neto(wDv, "S1", "Vig", sS1, sVig or 1, nVig)

# ═══════════════════════════════════════════════════════════════
# SECTION 4: HELPERS
# ═══════════════════════════════════════════════════════════════
DRIVER_COLORS = {
    "CBT":                              "#1ABC9C",
    "Experiencia Impositiva Mature":    "#5DADE2",
    "Experiencia Impositiva Meli Pro":  "#2E86C1",
    "Experiencia Impositiva Seller Dev":"#3483FA",
    "FBM-S Mature":                     "#E59866",
    "FBM-S Meli Pro":                   "#CA6F1E",
    "FBM-S Seller Dev":                 "#F39C12",
    "ME Vendedor Mature":               "#58D68D",
    "ME Vendedor Meli Pro":             "#1E8449",
    "ME Vendedor Seller Dev":           "#00A650",
    "Otros CV":                         "#95A5A6",
    "PCF Vendedor Mature":              "#F1948A",
    "PCF Vendedor Meli Pro":            "#C0392B",
    "PCF Vendedor Seller Dev":          "#FF7733",
    "PDD DS&XD - Vendedor":             "#A569BD",
    "PDD FBM - Vendedor":               "#7D3C98",
    "PDD Fotos - Vendedor":             "#C39BD3",
    "PDD MP,FLEX & CBT - Vendedor":     "#D7BDE2",
    "PNR ME - Vendedor":                "#17A589",
    "PNR MP - Vendedor":                "#0E6655",
    "Partners":                         "#9B59B6",
    "Post Venta Mature":                "#F1948A",
    "Post Venta Meli Pro":              "#EC7063",
    "Post Venta Seller Dev":            "#E84142",
    "Publicaciones Mature":             "#F9E79F",
    "Publicaciones Meli Pro":           "#D4AC0D",
    "Publicaciones Seller Dev":         "#B7950B",
}

DRIVER_SHORT = {
    "CBT":                              "CBT",
    "Experiencia Impositiva Mature":    "ExpImp Mat",
    "Experiencia Impositiva Meli Pro":  "ExpImp Pro",
    "Experiencia Impositiva Seller Dev":"ExpImp Dev",
    "FBM-S Mature":                     "FBM-S Mat",
    "FBM-S Meli Pro":                   "FBM-S Pro",
    "FBM-S Seller Dev":                 "FBM-S Dev",
    "ME Vendedor Mature":               "ME Mat",
    "ME Vendedor Meli Pro":             "ME Pro",
    "ME Vendedor Seller Dev":           "ME Dev",
    "Otros CV":                         "Otros CV",
    "PCF Vendedor Mature":              "PCF Mat",
    "PCF Vendedor Meli Pro":            "PCF Pro",
    "PCF Vendedor Seller Dev":          "PCF Dev",
    "PDD DS&XD - Vendedor":             "PDD DS&XD",
    "PDD FBM - Vendedor":               "PDD FBM",
    "PDD Fotos - Vendedor":             "PDD Fotos",
    "PDD MP,FLEX & CBT - Vendedor":     "PDD MP/CBT",
    "PNR ME - Vendedor":                "PNR ME",
    "PNR MP - Vendedor":                "PNR MP",
    "Partners":                         "Partners",
    "Post Venta Mature":                "PV Mat",
    "Post Venta Meli Pro":              "PV Pro",
    "Post Venta Seller Dev":            "PV Dev",
    "Publicaciones Mature":             "Publi Mat",
    "Publicaciones Meli Pro":           "Publi Pro",
    "Publicaciones Seller Dev":         "Publi Dev",
}

def fn(v): return f"{v:.2f}".replace(".", ",")
def fi(v): return f"{int(v):,}".replace(",", ".")
def arrow(v): return "▲" if v >= 0 else "▼"
def dc(v): return "pos" if v >= 0 else "neg"

def chip(v):
    sign = "+" if v > 0 else ""
    cls  = "chip-pos" if v > 0 else ("chip-neg" if v < 0 else "chip-neu")
    return f'<span class="chip {cls}">{sign}{fn(v)}</span>'

def _nps_series(history, labels):
    out = {}
    for drv in history:
        out[drv] = [round(100.0*(history[drv][l][0]-history[drv][l][1])/history[drv][l][2], 2)
                    if history[drv].get(l,(0,0,0))[2] > 0 else None for l in labels]
    return out

def _consolidated_series(history, labels):
    series = []
    for l in labels:
        tp = sum(history[drv].get(l,(0,0,0))[0] for drv in history)
        td = sum(history[drv].get(l,(0,0,0))[1] for drv in history)
        ts = sum(history[drv].get(l,(0,0,0))[2] for drv in history)
        series.append(round(100.0*(tp-td)/ts, 2) if ts > 0 else None)
    return series

def consolidated_chart_block(chart_id, labels, cons_series, target):
    fmt_js = 'function(v){return v!=null?v.toFixed(1).replace(".",",")+"%":""}'
    datasets = [
        {"type":"bar","label":"NPS Consolidado","data":cons_series,
         "backgroundColor":"#3483FAcc","borderColor":"#3483FA","borderWidth":1,
         "borderRadius":4,"datalabels":{"display":True,"anchor":"end","align":"end",
         "offset":3,"color":"#333","font":{"size":10,"weight":"700"},"formatter":"__FMT__"}},
        {"type":"line","label":f"Target ({str(target).replace('.',',')}%)","data":[target]*len(labels),
         "borderColor":"#e84142","borderDash":[6,3],"borderWidth":2,"pointRadius":0,
         "fill":False,"datalabels":{"display":False}},
    ]
    cfg = {"type":"bar","data":{"labels":labels,"datasets":datasets},
           "options":{"responsive":True,"maintainAspectRatio":False,
                      "layout":{"padding":{"top":24,"bottom":4}},
                      "plugins":{"legend":{"position":"bottom","labels":{"boxWidth":10,"padding":8,"font":{"size":10}}},
                                 "datalabels":{}},
                      "scales":{"y":{"min":-20,"max":100,"ticks":{"stepSize":10},"grid":{"color":"#f0f0f0"}},
                                "x":{"grid":{"display":False}}}}}
    cfg_json = _json.dumps(cfg).replace('"__FMT__"', fmt_js)
    return (
        f'<div style="position:relative;height:210px;">'
        f'<canvas id="{chart_id}"></canvas></div>'
        f'<script>new Chart(document.getElementById("{chart_id}"),{cfg_json});</script>'
    )

def waterfall_block(chart_id, label_a, nps_a, label_b, nps_b, d_dict, name_map=None, chart_height=320):
    _nm = name_map if name_map is not None else DRIVER_SHORT
    sorted_drvs = sorted(d_dict.keys(), key=lambda d: -d_dict[d]['var'])
    y_min = -20
    labels, bars, bg_colors, deltas_js = [label_a], [], [], [None]
    bars.append([y_min, round(nps_a, 2)])
    bg_colors.append('#3483FAcc')
    running = nps_a
    for drv in sorted_drvs:
        v = round(d_dict[drv]['var'], 2)
        labels.append(_nm.get(drv, drv))
        lo, hi = round(min(running, running+v), 2), round(max(running, running+v), 2)
        bars.append([lo, hi])
        bg_colors.append('#00a650cc' if v >= 0 else '#e84142cc')
        deltas_js.append(v)
        running += v
    labels.append(label_b)
    bars.append([y_min, round(nps_b, 2)])
    bg_colors.append('#3483FAcc')
    deltas_js.append(None)

    nps_a_str = f'{nps_a:.1f}'.replace('.', ',') + '%'
    nps_b_str = f'{nps_b:.1f}'.replace('.', ',') + '%'
    n_last    = len(labels) - 1
    deltas_arr = _json.dumps(deltas_js)
    lbl_cfg = {"display":True,"anchor":"end","align":"end","offset":3,
               "color":"#333","font":{"size":8,"weight":"600"},"formatter":"__WF_FMT__"}
    dataset = {"type":"bar","data":bars,"backgroundColor":bg_colors,
               "borderRadius":2,"borderSkipped":False,"datalabels":lbl_cfg}
    cfg = {
        "type":"bar","data":{"labels":labels,"datasets":[dataset]},
        "options":{
            "responsive":True,"maintainAspectRatio":False,
            "layout":{"padding":{"top":24,"bottom":4}},
            "plugins":{
                "legend":{"display":False},"datalabels":{},
                "title":{"display":True,"text":f"Impacto — Abertura Driver ({label_a} → {label_b})",
                         "align":"start","color":"#555","font":{"size":12,"weight":"600"},"padding":{"bottom":10}},
            },
            "scales":{
                "y":{"min":y_min,"max":100,"ticks":{"stepSize":10},"grid":{"color":"#f0f0f0"}},
                "x":{"grid":{"display":False},"ticks":{"maxRotation":45,"font":{"size":8}}},
            }
        }
    }
    fmt_js = (
        f'function(v,ctx){{'
        f'var i=ctx.dataIndex,dl={deltas_arr};'
        f'if(i===0)return"{nps_a_str}";'
        f'if(i==={n_last})return"{nps_b_str}";'
        f'var d=dl[i];return(d>=0?"+":"")+d.toFixed(2).replace(".",",")+"%";'
        f'}}'
    )
    cfg_json = _json.dumps(cfg).replace('"__WF_FMT__"', fmt_js)
    tbl_rows = ""
    for drv in sorted_drvs:
        v   = d_dict[drv]['var']; na = d_dict[drv]['nps_a']; nb = d_dict[drv]['nps_b']
        clr = "var(--green)" if v >= 0 else "var(--red)"
        bgc = "var(--light-green)" if v >= 0 else "var(--light-red)"
        sign = "+" if v >= 0 else ""
        tbl_rows += (
            f'<tr>'
            f'<td style="font-size:11px;font-weight:600;padding:4px 8px;border-bottom:1px solid #f5f5f5;">{_nm.get(drv, drv)}</td>'
            f'<td style="font-size:11px;text-align:right;padding:4px 8px;border-bottom:1px solid #f5f5f5;color:#888;">{fn(na)}</td>'
            f'<td style="font-size:11px;text-align:right;padding:4px 8px;border-bottom:1px solid #f5f5f5;color:#888;">{fn(nb)}</td>'
            f'<td style="text-align:right;padding:4px 8px;border-bottom:1px solid #f5f5f5;">'
            f'<span style="background:{bgc};color:{clr};font-size:10px;font-weight:700;padding:2px 6px;border-radius:8px;">{sign}{fn(v)}</span>'
            f'</td></tr>'
        )
    side_table = (
        f'<div style="display:flex;flex-direction:column;justify-content:flex-start;overflow-y:auto;max-height:420px;'
        f'background:#fff;border-radius:10px;border:1px solid var(--border);padding:12px 16px;">'
        f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#888;margin-bottom:8px;">Variação por Driver</div>'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<thead><tr>'
        f'<th style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;text-align:left;border-bottom:2px solid #f0f0f0;">Driver</th>'
        f'<th style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;text-align:right;border-bottom:2px solid #f0f0f0;">Ant.</th>'
        f'<th style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;text-align:right;border-bottom:2px solid #f0f0f0;">Atual</th>'
        f'<th style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;text-align:right;border-bottom:2px solid #f0f0f0;">VAR</th>'
        f'</tr></thead><tbody>{tbl_rows}</tbody></table></div>'
    )
    return (
        f'<div style="background:#fff;border-radius:8px;border:1px solid var(--border);padding:14px 16px;">'
        f'<div style="position:relative;height:{chart_height}px;">'
        f'<canvas id="{chart_id}"></canvas></div></div>'
        f'<script>new Chart(document.getElementById("{chart_id}"),{cfg_json});</script>'
        , side_table
    )

def _forecast(vals):
    nv = [(i,v) for i,v in enumerate(vals) if v is not None]
    if len(nv) < 2: return None
    n  = len(nv); xs = [p[0] for p in nv]; ys = [p[1] for p in nv]
    sx = sum(xs); sy = sum(ys); sxy = sum(x*y for x,y in zip(xs,ys)); sx2 = sum(x*x for x in xs)
    den = n*sx2 - sx*sx
    return round((n*sxy - sx*sy)/den, 2) if den else None

def _trend(vals):
    nv = [v for v in vals if v is not None]
    if len(nv) < 2: return "— Sem dados", "#888", "#f5f5f5"
    d1 = nv[-1]-nv[-2]; d2 = nv[-2]-nv[-3] if len(nv) >= 3 else None
    both_up   = d2 is not None and d1>0 and d2>0
    both_down = d2 is not None and d1<0 and d2<0
    if both_up and d1>1.5:    return "↑↑ Em alta",  "var(--green)", "var(--light-green)"
    elif d1>0.5:               return "↑ Evolução",  "var(--green)", "var(--light-green)"
    elif abs(d1)<=0.5:         return "→ Estável",   "#666",         "#f0f0f0"
    elif both_down and d1<-1.5:return "↓↓ Em queda", "var(--red)",   "var(--light-red)"
    else:                      return "↓ Queda",     "var(--red)",   "var(--light-red)"

def driver_history_table(history, labels, drv_targets, delta_label="ΔMoM", name_map=None):
    cell   = 'style="font-size:11px;padding:4px 8px;text-align:right;border-bottom:1px solid #f5f5f5;"'
    cell_l = 'style="font-size:11px;padding:4px 8px;font-weight:600;border-bottom:1px solid #f5f5f5;white-space:nowrap;"'
    th     = 'style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:5px 8px;text-align:right;border-bottom:2px solid #f0f0f0;white-space:nowrap;"'
    th_l   = 'style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:5px 8px;text-align:left;border-bottom:2px solid #f0f0f0;"'

    def nps_from(drv, lbl):
        d = history[drv].get(lbl,(0,0,0))
        return round(100*(d[0]-d[1])/d[2], 2) if d[2]>0 else None

    def chip_cell(v):
        if v is None: return f'<td {cell}>—</td>'
        clr = "var(--green)" if v>=0 else "var(--red)"
        bg  = "var(--light-green)" if v>=0 else "var(--light-red)"
        s   = "+" if v>=0 else ""
        return (f'<td {cell}><span style="background:{bg};color:{clr};font-size:10px;'
                f'font-weight:700;padding:2px 6px;border-radius:8px;">{s}{fn(v)}</span></td>')

    header = (f'<tr><th {th_l}>Driver</th>'
              + ''.join(f'<th {th}>{l}</th>' for l in labels)
              + f'<th {th}>{delta_label}</th><th {th}>vs Target</th>'
              + f'<th {th}>Tendência</th><th {th}>Forecast</th></tr>')

    _nm = name_map if name_map is not None else DRIVER_SHORT
    rows = ""
    for drv in sorted(history.keys()):
        vals    = [nps_from(drv,l) for l in labels]
        cur     = vals[-1]; prev = vals[-2] if len(vals)>=2 else None
        delta_v = round(cur-prev,2) if cur is not None and prev is not None else None
        tgt_v   = round(cur-drv_targets.get(drv,0),2) if cur is not None else None
        tlabel, tclr, tbg = _trend(vals)
        trend_cell = (f'<td {cell}><span style="background:{tbg};color:{tclr};font-size:10px;'
                      f'font-weight:700;padding:2px 8px;border-radius:8px;white-space:nowrap;">'
                      f'{tlabel}</span></td>')
        fc = _forecast(vals)
        if fc is not None:
            fc_clr = "var(--green)" if fc>=0 else "var(--red)"
            fc_bg  = "var(--light-green)" if fc>=0 else "var(--light-red)"
            fc_s   = "+" if fc>=0 else ""
            forecast_cell = (f'<td {cell}><span style="background:{fc_bg};color:{fc_clr};'
                             f'font-size:10px;font-weight:700;padding:2px 8px;border-radius:8px;">'
                             f'{fc_s}{fn(fc)} pp</span></td>')
        else:
            forecast_cell = f'<td {cell}>—</td>'
        val_cells = "".join(f'<td {cell}>{fn(v) if v is not None else "—"}</td>' for v in vals)
        rows += (f'<tr><td {cell_l}>{_nm.get(drv, drv)}</td>'
                 + val_cells + chip_cell(delta_v) + chip_cell(tgt_v)
                 + trend_cell + forecast_cell + '</tr>')

    return (
        f'<div style="margin-top:16px;overflow-x:auto;">'
        f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;'
        f'color:#888;margin-bottom:6px;">NPS por Driver — Histórico</div>'
        f'<table style="width:100%;border-collapse:collapse;background:#fff;">'
        f'<thead>{header}</thead><tbody>{rows}</tbody></table></div>'
    )

def kpi_cards(nps_b, surv_b, label_b, delta, nps_a, surv_a, label_a, target=NPS_TARGET):
    gap = round(nps_b-target, 2)
    gap_cls  = "var(--green)" if gap>=0 else "var(--red)"
    gap_sign = "+" if gap>=0 else ""
    gap_label = "acima do target" if gap>=0 else "abaixo do target"
    vol_delta = surv_b-surv_a; vol_pct = round(100*vol_delta/surv_a,1) if surv_a else 0
    return (
        f'<div class="kpi-grid">'
        f'<div class="kpi-card"><div class="label">NPS — {label_b}</div>'
        f'<div class="value" style="color:{"var(--green)" if delta>=0 else "var(--red)"};">{fn(nps_b)}</div>'
        f'<div class="sub">{fi(surv_b)} pesquisas</div>'
        f'<div class="delta {dc(delta)}">{arrow(delta)} {("+" if delta>=0 else "")}{fn(delta)} pp vs período anterior</div></div>'
        f'<div class="kpi-card"><div class="label">NPS — {label_a}</div>'
        f'<div class="value" style="color:var(--blue);">{fn(nps_a)}</div>'
        f'<div class="sub">{fi(surv_a)} pesquisas</div></div>'
        f'<div class="kpi-card"><div class="label">Volume — {label_b}</div>'
        f'<div class="value" style="color:var(--dark);font-size:22px;">{fi(surv_b)}</div>'
        f'<div class="sub">vs {fi(surv_a)} no período anterior</div>'
        f'<div class="delta {dc(vol_delta)}">{arrow(vol_delta)} {fi(abs(vol_delta))} ({("+" if vol_delta>=0 else "")}{vol_pct:.1f}%)</div></div>'
        f'<div class="kpi-card" style="border-top:3px solid {gap_cls};">'
        f'<div class="label">Target Q2\'26</div>'
        f'<div class="value" style="color:var(--dark);font-size:26px;">{fn(target)}</div>'
        f'<div class="sub">Meta consolidada do período</div>'
        f'<div class="delta" style="color:{gap_cls};">{arrow(gap)} {gap_sign}{fn(gap)} pp {gap_label}</div>'
        f'</div></div>'
    )

def driver_table(d_dict, surv_a, nps_a, surv_b, nps_b, delta, lbl_a, lbl_b):
    rows = ""
    for drv, v in sorted(d_dict.items(), key=lambda x: -abs(x[1]['var'])):
        rows += (
            f'<tr><td>{drv}</td>'
            f'<td>{fi(v["surv_a"])}</td><td>{fn(v["nps_a"])}</td>'
            f'<td>{fi(v["surv_b"])}</td><td>{fn(v["nps_b"])}</td>'
            f'<td>{v["share_a"]}%</td><td>{v["share_b"]}%</td>'
            f'<td>{chip(v["mix"])}</td><td>{chip(v["neto"])}</td>'
            f'<td>{chip(v["var"])}</td></tr>'
        )
    sm = round(sum(v['mix'] for v in d_dict.values()), 2)
    sn = round(sum(v['neto'] for v in d_dict.values()), 2)
    rows += (
        f'<tr class="total-row"><td>TOTAL</td>'
        f'<td>{fi(surv_a)}</td><td>{fn(nps_a)}</td>'
        f'<td>{fi(surv_b)}</td><td>{fn(nps_b)}</td>'
        f'<td>100%</td><td>100%</td>'
        f'<td>{fn(sm)}</td><td>{fn(sn)}</td>'
        f'<td>{chip(delta)}</td></tr>'
    )
    return (
        f'<div class="card">'
        f'<div class="card-header">Drivers — {lbl_a} → {lbl_b} <span class="badge">MIX + NETO = VAR</span></div>'
        f'<table><thead><tr>'
        f'<th>Driver</th><th>Pesq. {lbl_a}</th><th>NPS {lbl_a}</th>'
        f'<th>Pesq. {lbl_b}</th><th>NPS {lbl_b}</th>'
        f'<th>Share {lbl_a}</th><th>Share {lbl_b}</th>'
        f'<th>MIX (pp)</th><th>NETO (pp)</th><th>VAR (pp)</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div>'
    )

def _rich_summary(d_dict, nps_b, delta, label_a, label_b, diagnostic_html="", top_n=4,
                  name_map=None, targets_dict=None):
    _nm  = name_map    if name_map    is not None else DRIVER_SHORT
    _tgt = targets_dict if targets_dict is not None else DRIVER_TARGETS
    sorted_d  = sorted(d_dict.items(), key=lambda x: -x[1]['var'])
    positivos = [(d,v) for d,v in sorted_d if v['var'] > 0][:top_n]
    negativos = [(d,v) for d,v in reversed(sorted_d) if v['var'] < 0][:top_n]
    def _row(d, v, pos):
        clr  = "var(--green)" if pos else "var(--red)"
        bg   = "rgba(0,166,80,.07)" if pos else "rgba(232,65,66,.06)"
        sign = "+" if pos else ""
        tgt  = _tgt.get(d)
        vs   = (f' &nbsp;<span style="color:{clr};font-size:10px;">vs target {round(v["nps_b"]-tgt,1):+.1f} pp</span>'
                if tgt else '')
        return (
            f'<div style="padding:5px 0;border-bottom:1px solid #eee;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="font-size:12px;font-weight:600;">{_nm.get(d,d)}</span>'
            f'<span style="background:{bg};color:{clr};font-size:11px;font-weight:700;padding:2px 8px;border-radius:8px;">'
            f'{sign}{fn(v["var"])} pp</span></div>'
            f'<div style="font-size:11px;color:#888;margin-top:1px;">'
            f'NPS {fn(v["nps_a"])} → <strong style="color:#333;">{fn(v["nps_b"])}</strong>{vs} · {fi(v["surv_b"])} surv</div>'
            f'</div>')
    pos_rows = "".join(_row(d,v,True)  for d,v in positivos) or '<div style="font-size:12px;color:#aaa;padding:8px 0;">Nenhum driver positivo</div>'
    neg_rows = "".join(_row(d,v,False) for d,v in negativos) or '<div style="font-size:12px;color:#aaa;padding:8px 0;">Nenhum driver negativo</div>'
    grid = (
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;">'
        f'<div style="background:rgba(0,166,80,.06);border-radius:8px;border-left:4px solid var(--green);padding:10px 14px;">'
        f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--green);margin-bottom:6px;">▲ Maiores altas — {label_b}</div>'
        f'{pos_rows}</div>'
        f'<div style="background:rgba(232,65,66,.06);border-radius:8px;border-left:4px solid var(--red);padding:10px 14px;">'
        f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--red);margin-bottom:6px;">▼ Maiores quedas — {label_b}</div>'
        f'{neg_rows}</div>'
        f'</div>'
    )
    diag = ""
    if diagnostic_html:
        diag = (
            f'<div style="background:#f4f8ff;border-radius:8px;border-left:4px solid var(--blue);'
            f'padding:12px 16px;">'
            f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;'
            f'color:var(--blue);margin-bottom:6px;">📋 Diagnóstico para Gestão</div>'
            f'<p style="font-size:12px;color:#333;line-height:1.75;margin:0;">{diagnostic_html}</p>'
            f'</div>'
        )
    return grid + diag

def tab_content(tab_id, nps_b, surv_b, label_b, delta, nps_a, surv_a, label_a,
                d_dict, wf_html="", wf_side="", cons_html="", hist_table="",
                extra_html="", rich_summary="", summary_right="",
                cat_filter_bar="", cat_views_html=""):
    _right = summary_right if summary_right else wf_side
    charts_grid = ""
    if cons_html or _right:
        charts_grid = (
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px;">'
            f'<div style="background:#fff;border-radius:8px;border:1px solid var(--border);padding:14px 16px;">'
            f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#888;margin-bottom:4px;">NPS Consolidado vs Target</div>'
            + cons_html +
            f'</div>'
            + (_right if _right else '')
            + f'</div>'
        )
    body_text = (rich_summary if rich_summary else
                 f'<p class="summary-text">{label_b} encerrou em <strong>NPS {fn(nps_b)} ({("+" if delta>=0 else "")}{fn(delta)} pp)</strong> '
                 f'vs período anterior ({fn(nps_a)}, {fi(surv_a)} pesquisas). Atual: {fi(surv_b)} pesquisas.</p>')
    summary = (
        f'<div class="summary-box">'
        f'<div class="summary-header">'
        f'<div><div class="summary-title">Resumo Executivo</div>'
        f'<div class="summary-sub">{label_b}</div></div>'
        f'<span class="nps-badge" style="background:{"var(--light-green)" if delta>=0 else "var(--light-red)"};color:{"var(--green)" if delta>=0 else "var(--red)"};">'
        f'NPS {fn(nps_b)} {arrow(delta)} {("+" if delta>=0 else "")}{fn(delta)} pp</span>'
        f'</div><hr class="divider">'
        + body_text
        + charts_grid + hist_table +
        f'</div>'
    )
    all_view = (
        f'<div id="tab-{tab_id}-cat-all" class="cat-view">'
        f'<div class="section-title">KPIs</div>'
        + kpi_cards(nps_b, surv_b, label_b, delta, nps_a, surv_a, label_a)
        + summary
        + extra_html
        + f'</div>'
    )
    return (
        f'<div id="tab-{tab_id}" class="tab-content">'
        + (cat_filter_bar if cat_filter_bar else '')
        + all_view
        + (cat_views_html if cat_views_html else '')
        + f'</div>'
    )

# ═══════════════════════════════════════════════════════════════
# SECTION 4B: CATEGORIAS
# ═══════════════════════════════════════════════════════════════
DRIVER_CATEGORIA = {
    "CBT":                              "Buyers",
    "Experiencia Impositiva Mature":    "Mature",
    "Experiencia Impositiva Meli Pro":  "Meli Pro",
    "Experiencia Impositiva Seller Dev":"Longtail",
    "FBM-S Mature":                     "FBM",
    "FBM-S Meli Pro":                   "FBM",
    "FBM-S Seller Dev":                 "FBM",
    "ME Vendedor Mature":               "Mature",
    "ME Vendedor Meli Pro":             "Meli Pro",
    "ME Vendedor Seller Dev":           "Longtail",
    "Otros CV":                         "Otros CV",
    "PCF Vendedor Mature":              "Mature",
    "PCF Vendedor Meli Pro":            "Meli Pro",
    "PCF Vendedor Seller Dev":          "Longtail",
    "PDD DS&XD - Vendedor":             "Buyers",
    "PDD FBM - Vendedor":               "Buyers",
    "PDD Fotos - Vendedor":             "Buyers",
    "PDD MP,FLEX & CBT - Vendedor":     "Buyers",
    "PNR ME - Vendedor":                "Buyers",
    "PNR MP - Vendedor":                "Buyers",
    "Partners":                         "Longtail",
    "Post Venta Mature":                "Mature",
    "Post Venta Meli Pro":              "Meli Pro",
    "Post Venta Seller Dev":            "Longtail",
    "Publicaciones Mature":             "Mature",
    "Publicaciones Meli Pro":           "Meli Pro",
    "Publicaciones Seller Dev":         "Longtail",
}

CAT_ORDER  = ["Longtail", "Mature", "Meli Pro", "Buyers", "FBM", "Otros CV"]
CAT_SHORT  = {c: c for c in CAT_ORDER}
CAT_COLORS = {
    "Longtail": "#E84142",
    "Mature":   "#00A650",
    "Meli Pro": "#9B59B6",
    "Buyers":   "#3483FA",
    "FBM":      "#F39C12",
    "Otros CV": "#95A5A6",
}

def _agg_driver_dict_by_cat(driver_dict, cat_map):
    """Agrega {driver: {period: (p,d,s)}} → {cat: {period: (p,d,s)}}"""
    out = {}
    for drv, periods in driver_dict.items():
        cat = cat_map.get(drv, "Otros CV")
        for period, (p, d, s) in periods.items():
            out.setdefault(cat, {}).setdefault(period, (0,0,0))
            pp, dd, ss = out[cat][period]
            out[cat][period] = (pp+p, dd+d, ss+s)
    return out

def _agg_history_by_cat(history, labels, cat_map):
    """Agrega weekly/monthly history por categoria"""
    out = {}
    for drv, lbl_dict in history.items():
        cat = cat_map.get(drv, "Otros CV")
        for l in labels:
            t = lbl_dict.get(l, (0,0,0))
            out.setdefault(cat, {}).setdefault(l, (0,0,0))
            pp, dd, ss = out[cat][l]
            out[cat][l] = (pp+t[0], dd+t[1], ss+t[2])
    return out

def _cat_targets(cat_map, drv_targets, monthly_drv):
    """Target por categoria = média ponderada dos targets dos drivers (peso = surveys M1)"""
    num = {}; den = {}
    for drv, tgt in drv_targets.items():
        cat = cat_map.get(drv, "Otros CV")
        w   = monthly_drv.get(drv, {}).get("M1", (0,0,0))[2]
        num[cat] = num.get(cat, 0) + tgt * w
        den[cat] = den.get(cat, 0) + w
    return {cat: round(num[cat]/den[cat], 2) if den.get(cat,0)>0 else 0.0 for cat in num}

# ═══════════════════════════════════════════════════════════════
# SECTION 4C: DEEP DIVE & ALERTAS
# ═══════════════════════════════════════════════════════════════

# ── Semana Fechada ──────────────────────────────────────────────
DEEP_DIVE_DATE   = "20/04/2026"
DEEP_DIVE_POS_DRIVER   = "Post Venta Seller Dev"
DEEP_DIVE_POS_VAR      = "+6,94 pp"
DEEP_DIVE_POS_PROC     = "Reputación: NPS 66,67% → 72,57% (+5,90 pp) | 288 → 226 surveys | amostra 30% analisada"
DEEP_DIVE_POS_INSIGHTS = [
    "Atendimento humanizado nomeado é o diferencial: Lucas, Vitor, Israelly, Davison citados nominalmente — padrão: solicita Pack ID, analisa rapidamente e exclui impacto no 1º contato. Resolução FCR é o gatilho do NPS 10.",
    "Exclusão do impacto ('Excluimos') gera promotores imediatos: maioria dos NPS 9–10 está associada a essa solução — quando o atendente remove o impacto, o vendedor dá nota máxima independente da complexidade.",
    "IA frustra antes do humano: promotores relatam 'passar raiva com o assistente virtual' antes do atendimento humano — o humano salva a experiência mas o custo de jornada é alto.",
    "Detratores: manutenção de impacto percebida como injusta + ligações caídas sem retorno + respostas genéricas da IA — política rígida e canal IA ineficaz são as duas causas raiz.",
]
DEEP_DIVE_NEG_DRIVER   = "PCF Vendedor (todos os segmentos)"
DEEP_DIVE_NEG_VAR      = "−16,22 pp (Mature) · −1,83 pp (Seller Dev) · +9,17 pp (Meli Pro)"
DEEP_DIVE_NEG_PROC     = "Post Compra Funcionalidades Vendedor: NPS 50,74% → 39,51% (Mature) | queda crítica puxada por mediações e devoluções sem resolução"
DEEP_DIVE_NEG_INSIGHTS = [
    "Mediação IA encerra sem dar defesa ao vendedor: 'mediação encerrada com IA – desacordo com a resolução' é o padrão dominante — vendedor sente que é sempre responsabilizado sem análise do caso (#450865558: 'O VENDEDOR SEMPRE É LESADO').",
    "Devolução falida e prazos vencidos: produto retorna quebrado ou não retorna — ML não reembolsa e ainda cobre o frete (#450483254: 'cadê meus produtos ou dinheiro das vendas'); múltiplos protocolos sem resposta (#450981598: 'mais de 5 protocolos e nada').",
    "Ticket encerrado sem confirmação: 'mesmo respondendo, me foi enviado que não interagi e encerrou o contato' (#450025591) — padrão sistêmico de timeout forçado na mediação.",
    "IA no fluxo de mediação é o principal detrator: 'robô com atendimento ridículo, não resolve nada, caminho difícil para falar com humano' (#450049295) — promotores citam atendentes humanos nomeados (Ruanna, Rose, Gabriela, Emerson) como únicos que resolvem.",
]
DCEV_ACOES_SF = [
    "Criar revisão humana obrigatória antes de fechar mediação contra o vendedor — IA não deve ter poder de fallo sem análise de evidências.",
    "Proibir encerramento de ticket por timeout sem confirmação ativa do cliente que o problema foi resolvido.",
    "Para PCF Mature: expandir atendentes com perfil humanizado (Rose, Ruanna) como referência — NPS 10 tem nome de atendente em 100% dos casos.",
    "Para Reputação: criar bypass rápido para atendente humano — eliminar IA do fluxo inicial de impacto de reputação.",
]

# ── Mensal ──────────────────────────────────────────────────────
DD_MES_DATE      = "20/04/2026"
DD_MES_POS_DRIVER   = "Experiencia Impositiva Seller Dev"
DD_MES_POS_VAR      = "+8,59 pp"
DD_MES_POS_PROC     = "Facturación: NPS 28,51% → 44,29% (+15,78 pp) | 242 → 140 surveys (parcial Abr)"
DD_MES_POS_INSIGHTS = [
    "Atendentes nomeados geram NPS 10 sistematicamente: Lucas, Junior, Matheus, Cláudio, Tamires — resolução técnica precisa de cobranças e relatórios fiscais com escuta ativa é o diferencial do processo.",
    "Gestão humanizada de resposta negativa mantém NPS 10: 'mesmo a resposta sendo negativa, ótimo atendimento do Cláudio' — empatia e clareza compensam o limite do sistema.",
    "Detratores: cobranças automáticas não autorizadas (Ads ativados sem consentimento, Minha Página cobrada indevidamente) + 6–7 transferências sem resolução + meses de espera sem SLA.",
    "Melhora em Faturação reflete maior volume de atendimentos resolutivos em download de documentos fiscais (NF-e, relatórios), onde o FCR é alto.",
]
DD_MES_NEG_DRIVER   = "Otros CV"
DD_MES_NEG_VAR      = "−9,14 pp"
DD_MES_NEG_PROC     = "KYC Services (42% do volume): NPS 44,35% Abr | 619 surveys acumulados"
DD_MES_NEG_INSIGHTS = [
    "KYC Services é o processo dominante (262/619 surveys = 42%): vendedores bloqueados por challenge de verificação de identidade pendente ou recusado — processo burocrático sem clareza sobre o que enviar ou por que foi recusado.",
    "Informações contraditórias entre atendentes: 'cada atendente me responde algo distinto, nunca sei como se resolveu o caso' — falta de padronização do fluxo KYC gera recontatos e NPS 0.",
    "KYC surprise sem comunicação prévia: 'não solicitei abertura de conta, agora tenho que arrumar milhões de documentos' — desafio ativado sem aviso prévio trava a conta do vendedor inesperadamente.",
    "Challenge recusado sem feedback específico: 'dificultam o óbvio' — usuário não sabe o que corrigir e repete o processo indefinidamente, acumulando frustração.",
]
DD_MES_ACO = [
    "Criar comunicação proativa antes de ativar challenge KYC — aviso com 72h de antecedência e instrução clara dos documentos necessários.",
    "Padronizar resposta do fluxo KYC entre atendentes: criar trilha única de decisão para challenge pendente e recusado.",
    "Para PCF Mediações: criar protocolo anti-fallo-automático — mediação IA só pode encerrar após 24h de tentativa de contato com o vendedor sem resposta.",
    "Para Facturación: expandir atendentes com perfil Cláudio/Rose — atendentes técnicos com escuta ativa são o único vetor de NPS 10 em processos fiscais complexos.",
]

# ── Alertas SF ──────────────────────────────────────────────────
ALERT_ANALYSIS = {
    "Otros CV": {
        "cdu_breakdown": [
            {"cdu": "KYC Challenge Pendente (sem documento)", "top_sol": "KYC - Challenge Pendente: enviamos link",    "n": 7,  "pct": 58.3},
            {"cdu": "KYC Challenge Recusado",                 "top_sol": "KYC - Challenge Recusado",                   "n": 3,  "pct": 25.0},
            {"cdu": "Blanqueo / Representante Legal",         "top_sol": "Blanqueo representante legal: alteração",    "n": 1,  "pct":  8.3},
            {"cdu": "Registro (cadastro ML)",                  "top_sol": "Autogestão - Como se cadastrar no ML",       "n": 1,  "pct":  8.3},
        ],
        "user_themes": [
            "Challenge ativado sem aviso prévio: conta bloqueada inesperadamente sem comunicação (#450841895: 'não solicitei abertura de conta, agora tenho que arrumar documentos')",
            "Informações contraditórias entre atendentes: nunca sabe o status real do caso (#449734598: 'cada atendente responde algo distinto')",
            "Challenge recusado sem feedback: usuário não sabe o que corrigir e repete sem sucesso (#450137943)",
            "Processo de representante legal inflexível: procuração enviada não aceita, conta congelada (#450112980)",
        ],
        "rep_themes": [
            "REP envia link de challenge sem explicar o motivo do bloqueio — vendedor fica confuso sobre o que enviar",
            "REP informa 'challenge recusado' sem detalhar o documento específico que falhou",
            "REP sem poder de decisão: não pode reverter challenge — encaminha para 'equipe interna' sem SLA",
            "Informações divergentes entre atendentes sobre o mesmo caso — falta de histórico persistente",
        ],
    },
    "Experiencia Impositiva Seller Dev": {
        "cdu_breakdown": [
            {"cdu": "DCe obrigatório — apenas via desktop",       "top_sol": "DCe para sellers (mobile bloqueado)",        "n": 6, "pct": 26.1},
            {"cdu": "Emissor externo — XML recusado/não informado","top_sol": "Emissor externo: como informar XML na venda", "n": 4, "pct": 17.4},
            {"cdu": "Faturador indisponível / não emite NF",       "top_sol": "Emissão de NF: funcionalidade indisponível",  "n": 2, "pct":  8.7},
            {"cdu": "Instabilidade SEFAZ",                         "top_sol": "Emissão de NF: instabilidade SEFAZ",          "n": 2, "pct":  8.7},
        ],
        "user_themes": [
            "Seller mobile-only não consegue emitir DCe: 'a 10 anos só pelo celular, agora não tenho mais como' (#450436581)",
            "Recontatos em loop: 15+ atendentes em 3 dias sem resolução; quem resolveu foi o suporte do Bling (#450946548)",
            "Encerramento de ticket por timeout: atendente fecha sem aguardar confirmação do cliente (#450867735)",
            "IA passa informação incorreta por dias antes do humano corrigir — impacto na reputação já registrado (#450184747)",
        ],
        "rep_themes": [
            "REP orienta DCe corretamente mas não resolve bloqueio mobile — seller fica sem despachar",
            "REP encerra ticket por timeout de 5 minutos mesmo com problema aberto",
            "Múltiplas transferências sem owner — cada atendente reinicia sem ler histórico",
            "IA de 1ª linha repete informação incorreta; humano corrige tarde demais",
        ],
    },
    "CBT": {
        "cdu_breakdown": [
            {"cdu": "CBT Reputação (reclamações de compradores)",  "top_sol": "CBT - Reputation: reclamações",      "n": 7, "pct": 63.6},
            {"cdu": "CBT - ME Reputation (reputação ME)",          "top_sol": "CBT - ME Reputation",               "n": 1, "pct":  9.1},
            {"cdu": "CBT - MP Withdrawals (saques)",               "top_sol": "CBT MP Retiros",                     "n": 1, "pct":  9.1},
            {"cdu": "CBT - Package journey (rastreio/demoras)",    "top_sol": "CBT - Demoras",                      "n": 1, "pct":  9.1},
        ],
        "user_themes": [
            "Seller cross-border recebe reclamações de compradores por produto com avaliação negativa — reputação impactada sem recurso adequado",
            "Falta de continuidade de contexto entre atendentes: 'redirected to different agents, same info repeated multiple times' (#451109305)",
            "Reclamações de compradores percebidas como maliciosas para obter reembolso: 'muitas reclamações não são problema do produto' (#451009352)",
            "Barreira de idioma: sellers CBT em inglês/mandarim, suporte principal em português — gaps de comunicação",
        ],
        "rep_themes": [
            "REP sem ownership do caso: redireciona para outro agente sem briefing — seller repete informação do início",
            "REP sem ferramenta para reverter impacto de reputação CBT de reclamações percebidas como fraudulentas",
            "Resposta genérica sem interpretação do contexto cross-border — políticas locais aplicadas a operação internacional",
            "Falta de canal em inglês/espanhol com SLA dedicado para CBT — suporte generalista sem domínio do segmento",
        ],
    },
    "PDD DS&XD - Vendedor": {
        "cdu_breakdown": [
            {"cdu": "Devolução efetiva — geramos código",         "top_sol": "MED PDD Devolução efetiva: geramos código",    "n": 186, "pct": 35.1},
            {"cdu": "Devolução não efetiva — fallo vendedor",     "top_sol": "Devolução expirada: fallo V (Auto)",           "n":  99, "pct": 18.7},
            {"cdu": "Devolução efetiva — confirmada (CG auto)",   "top_sol": "Mediação encerrada: C devolveu (fallo C Auto)","n":  46, "pct":  8.7},
            {"cdu": "PNR — acordo entre partes",                   "top_sol": "Mediação: comprador encerra por V resolveu",   "n":  38, "pct":  7.2},
            {"cdu": "Parcial — reembolso parcial ao comprador",    "top_sol": "Mediação: reembolso parcial retirando do V",   "n":  34, "pct":  6.4},
        ],
        "user_themes": [
            "Código de devolução expirado: 'código estava expirado quando fui ao correio devolver' (#448544440) — prazo curto não compatível com logística",
            "Comprador sem acessibilidade para devoluções: 'sou PCD, obrigam me a ir a agência a 1,5km' (#448602536) — política rígida de localização de ponto de devolução",
            "Fallo automático do vendedor percebido como injusto: anúncio correto, comprador insatisfeito, mas vendedor é responsabilizado (#449642517)",
            "IA automática sem qualidade: 'inteligência artificial não ajudou, muito confuso' (#446771367) — mediações PDD com alto grau de automação geram NPS 0",
        ],
        "rep_themes": [
            "Sistema automático (Auto) fecha medição contra o vendedor sem análise humana — fallo V gerado por algoritmo",
            "REP sem poder de reverter fallo automático: encaminha para 'área interna' sem garantia de revisão",
            "Código de devolução gerado sem checagem de prazo viável para logística do comprador",
            "Falta de canal humano para casos de PDD com impacto relevante — automação sem escape para revisão",
        ],
    },
    "Partners": {
        "cdu_breakdown": [
            {"cdu": "Dúvidas pagamentos/NF (regularização Places)", "top_sol": "ME Places: regularização e emissão de NF",  "n": 10, "pct": 26.3},
            {"cdu": "Calendário de pagamento Places",               "top_sol": "ME Places: calendário de pagamento",        "n":  3, "pct":  7.9},
            {"cdu": "Cadastro como Agência MELI",                   "top_sol": "ME Places: como iniciar cadastro",          "n":  3, "pct":  7.9},
            {"cdu": "Gestão de conta Places (dados no app)",        "top_sol": "ME Places: atualização de dados no app",    "n":  3, "pct":  7.9},
            {"cdu": "Reportar incidente (motorista/QR Code)",       "top_sol": "ME Places: como avaliar coleta ou reportar","n":  3, "pct":  7.9},
        ],
        "user_themes": [
            "Agente Places com dificuldades de regularização e emissão de NF — CDU dominante, bloqueia operação (#Tiene dudas pagos/facturas)",
            "Problemas no processo de cadastro como Agência MELI — barreira de entrada para novos Places Kangu",
            "Dificuldades operacionais: QR Code para recebimento de sacas, coletas extras, dados desatualizados no app",
            "Queda progressiva: Jan 68,41 → Fev 72,38 → Mar 67,39 → Abr 67,04 — tendência de declínio confirmada",
        ],
        "rep_themes": [
            "REP orienta regularização de NF mas não resolve em tempo real — agente fica bloqueado sem operar",
            "REP encaminha cadastro de agência sem acompanhar follow-up — seller fica sem retorno",
            "REP sem ferramenta para problemas operacionais do app Places — responde com 'aguardar análise'",
            "Ausência de canal dedicado Places com SLA definido — generalistas sem domínio do segmento",
        ],
    },
    "PNR MP - Vendedor": {
        "cdu_breakdown": [
            {"cdu": "PNR - Acuerdo entre partes",            "top_sol": "Mediação encerrada: comprador encerra — fallo V (Auto)",         "n": 15, "pct": 36.6},
            {"cdu": "PNR Envío extraviado",                  "top_sol": "Mediação encerrada: produto extraviado (fallo C)",               "n": 12, "pct": 29.3},
            {"cdu": "PNR - Producto en devolución al V",     "top_sol": "Mediação encerrada: produto em devolução ao remetente (fallo C)","n":  9, "pct": 22.0},
            {"cdu": "PNR C no responde",                     "top_sol": "Mediação encerrada: C não responde — fallo V (Auto)",            "n":  7, "pct": 17.1},
        ],
        "user_themes": [
            "Fallo automático percebido como injusto: 'o vendedor fica bloqueado por timeout mesmo com problema aberto' (#452451807) — mediação IA encerra sem analisar contexto real",
            "Cancelamento de compra antes do envio não processado corretamente: 'fiz cancelamento antes do envio e agora estou sendo notificado que recebi o produto' (#451197728)",
            "Reembolso adiado com vendedor redefinindo prazos livremente: 'atendentes falando que deveria pagar frete na próxima vez, ignorando frete grátis original' (#450703692)",
            "IA não tem olhar no detalhe: 'segunda conta que assumo prejuízo que não é da minha responsabilidade' (#452364267) — automação gera injustiça sistemática",
        ],
        "rep_themes": [
            "Sistema Auto fecha mediação contra V sem verificar evidências — fallo V por timeout ou acordo forçado",
            "REP sem poder de reverter fallo automático de PNR — escala para equipe interna sem SLA",
            "Informações contraditórias sobre frete e reembolso entre atendentes — sem histórico persistente",
            "Comunicação genérica sem leitura do contexto: 'deixaram na mão, cancelaram pedido sem consultar' (#450163022)",
        ],
    },
    "ME Vendedor Meli Pro": {
        "cdu_breakdown": [
            {"cdu": "HT - Ventas (impacto reputação vendas)", "top_sol": "Reputação ME Vendas: Cross Docking — Excluimos",    "n": 5, "pct": 50.0},
            {"cdu": "HT - Ventas (Flex não excluído)",        "top_sol": "Reputação ME Vendas: Logistica Flex — Não excluimos","n": 1, "pct": 10.0},
            {"cdu": "HT - Coleta XD",                         "top_sol": "Reputação ME Coleta XD: Coleta pendente",           "n": 1, "pct": 10.0},
            {"cdu": "HT - Informativas",                      "top_sol": "Reputação ME Informativas: Como melhorar HT",       "n": 1, "pct": 10.0},
        ],
        "user_themes": [
            "Erro sistêmico: anúncio ativado com envio próprio gera penalidades de reputação — 'trabalho 8 anos com vocês, está cada vez pior' (#452686699)",
            "Problema não resolvido mesmo com atendente classificado como bom: 'atendente ótima, porém problema não resolvido' (#452506896) — sistema não permite exclusão em todos os casos",
            "Falhas de coleta Cross Docking sem proteção automática de reputação: 'ficam me obrigando a cancelar, o que afeta ainda mais a reputação' (#452686699)",
            "Emissão de etiquetas e NF bloqueada afeta HT: 'não consegui emitir etiquetas e blindar minha reputação' (#452276788) — duplo impacto operacional + reputacional",
        ],
        "rep_themes": [
            "REP exclui impacto quando tem poder mas muitos casos de Flex não são excluídos — critério de exclusão inconsistente",
            "REP sem poder de excluir Flex — encaminha para equipe interna sem prazo claro",
            "Atendente responde script sem ler mensagens: 'scriptado, parece que não lê as mensagens de fato' (#452486199)",
            "REP não entra em contato proativamente como deveria: 'não entrou em contato como deveria, só fez perder meu tempo' (#452829234)",
        ],
    },
    "PNR ME - Vendedor": {
        "cdu_breakdown": [
            {"cdu": "PNR ME — produto não recebido via ME",  "top_sol": "Mediação: comprador não recebeu via Mercado Envios", "n": 8, "pct": 40.0},
            {"cdu": "PNR ME — envio extraviado/atraso",      "top_sol": "Mediação: produto extraviado em trânsito",           "n": 6, "pct": 30.0},
            {"cdu": "PNR ME — fallo V por inação",           "top_sol": "Mediação encerrada: V não responde — fallo V",       "n": 4, "pct": 20.0},
            {"cdu": "PNR ME — produto retornou ao V",        "top_sol": "Mediação: produto em devolução ao remetente",        "n": 2, "pct": 10.0},
        ],
        "user_themes": [
            "Queda significativa de -14,75 pp em S1 com volume crescente (37 → 103 surveys) — indicador de deterioração real no processo PNR via ME",
            "Extravios em trânsito via ME geram fallos automáticos — vendedor responsabilizado por problema logístico da transportadora",
            "Prazo de resposta do vendedor insuficiente antes do fallo automático — sellers Mobile-first com dificuldade de acessar painel a tempo",
            "Padrão de queda consistente: NPS 35,14% (S2) → 20,39% (S1) — requer investigação aprofundada de fallos automáticos em PNR ME",
        ],
        "rep_themes": [
            "REP sem poder de reverter fallo em PNR ME com extravio confirmado — encaminha sem garantia de resultado",
            "Sistema Auto encerra mediação contra V por timeout de resposta — prazo insuficiente para vendedores com acesso limitado",
            "Falta de proatividade no contato: vendedor não é notificado adequadamente sobre prazo de mediação aberta",
            "Ausência de canal específico PNR ME com SLA diferenciado — processo generalista não atende complexidade logística",
        ],
    },
}

ALERT_SF = [
    {
        "drv": "Experiencia Impositiva Seller Dev", "proc": "Emision de Nota Fiscal",
        "nps_cur": 38.64, "nps_tgt": 59.03, "delta_tgt": -20.39, "trend": "↓↓ Em queda",
        "insights": [
            "DCe obrigatório apenas via desktop bloqueia sellers mobile-only: 'a 10 anos só pelo celular, agora não tenho mais como' (#450436581) — queda acumulada de −10,74 pp vs semana anterior.",
            "15+ recontatos em 3 dias sem resolução (#450946548) — cada atendente reinicia sem ler histórico; quem resolveu foi o suporte do Bling.",
            "Encerramento de ticket por timeout de 5 minutos mesmo com problema aberto (#450867735).",
            "IA passa informação incorreta por dias antes do humano corrigir — impacto na reputação já registrado (#450184747).",
        ],
        "acoes": [
            "Habilitar emissão de DCe pelo app mobile — bloqueante para sellers sem computador.",
            "Implementar histórico persistente de contexto entre atendentes.",
            "Proibir encerramento de ticket sem confirmação ativa do cliente.",
            "Desativar IA de Emissão NF até correção das informações — encaminhar para humano.",
        ],
    },
    {
        "drv": "PNR MP - Vendedor", "proc": "PNR - MP (Mediações PNR sem ME)",
        "nps_cur": 5.56, "nps_tgt": 29.57, "delta_tgt": -24.01, "trend": "↓↓ Em queda",
        "insights": [
            "Fallo automático percebido como injusto: mediação IA encerra por acordo forçado ou timeout sem analisar contexto real — maior CDU (36,6% dos detratores) (#452451807).",
            "Cancelamento de compra antes do envio não processado corretamente: 'fiz cancelamento antes do envio e agora estou sendo notificado que recebi o produto' (#451197728).",
            "Reembolso adiado com vendedor redefinindo prazos livremente: atendentes orientam pagamento de frete extra ignorando frete grátis original (#450703692).",
            "IA não tem olhar no detalhe: 'segunda conta que assumo prejuízo que não é da minha responsabilidade' (#452364267) — automação gera injustiça sistemática em casos de PNR.",
        ],
        "acoes": [
            "Criar revisão humana antes de fallo automático em PNR — IA não deve ter poder de fallo final sem análise de evidências.",
            "Implementar alerta proativo para cancelamento de compra pré-envio — evitar conflito entre cancelamento e entrega.",
            "Corrigir comunicação de frete: atendentes não podem sugerir custo extra quando pedido original tinha frete grátis.",
            "Aumentar prazo de resposta do vendedor antes do fallo automático — mínimo 48h com notificação reforçada.",
        ],
    },
    {
        "drv": "PNR ME - Vendedor", "proc": "PNR via Mercado Envios",
        "nps_cur": 20.39, "nps_tgt": 27.23, "delta_tgt": -6.84, "trend": "↓↓ Em queda",
        "insights": [
            "Queda significativa de −14,75 pp vs semana anterior com volume crescente (37 → 103 surveys) — indica deterioração real no processo PNR via ME.",
            "Extravios em trânsito via ME geram fallos automáticos — vendedor responsabilizado por problema logístico da transportadora sem análise de evidência.",
            "Prazo de resposta do vendedor insuficiente antes do fallo automático — sellers mobile-first com dificuldade de acessar painel a tempo.",
            "Padrão de queda consistente: NPS 35,14% (S2) → 20,39% (S1) — requer investigação aprofundada de fallos automáticos em PNR ME.",
        ],
        "acoes": [
            "Reverter fallos automáticos em PNR ME quando extravio foi confirmado pela transportadora — vendedor não é responsável.",
            "Ampliar prazo de resposta em mediações PNR ME para 72h com notificação via app e email.",
            "Criar canal específico PNR ME com SLA diferenciado — processo logístico é mais complexo que PNR sem ME.",
            "Implementar análise automática de histórico de entrega antes de gerar fallo V em extravios.",
        ],
    },
    {
        "drv": "CBT", "proc": "CBT - Reputation / CBT - ME Reputation",
        "nps_cur": 62.77, "nps_tgt": 74.63, "delta_tgt": -11.86, "trend": "↓↓ Em queda",
        "insights": [
            "Queda de −7,82 pp vs semana anterior (70,59% → 62,77%) — terceiro mês consecutivo abaixo do target de 74,63%.",
            "Sellers cross-border impactados por reclamações de compradores percebidas como oportunistas — reputação afetada sem mecanismo adequado de defesa para o segmento internacional.",
            "Falta de continuidade de contexto: 'redirected to different agents, same info repeated multiple times' (#451109305) — suporte generalista sem ownership do caso CBT.",
            "Barreira de idioma e política: sellers em inglês/mandarim com suporte principalmente em português, políticas locais aplicadas à operação cross-border.",
        ],
        "acoes": [
            "Criar canal dedicado CBT com atendentes bilíngues (português/inglês/espanhol) e SLA diferenciado.",
            "Desenvolver fluxo de revisão de reputação específico para CBT — políticas de reclamação cross-border são diferentes.",
            "Implementar histórico de caso vinculado ao seller CBT — eliminar o padrão de 'repassar para outro agente'.",
            "Revisar critérios de fallo automático em mediações PDD para sellers CBT com operação internacional.",
        ],
    },
    {
        "drv": "Otros CV", "proc": "KYC Services",
        "nps_cur": 43.80, "nps_tgt": 53.77, "delta_tgt": -9.97, "trend": "↓ Queda",
        "insights": [
            "KYC challenge ativado sem aviso prévio bloqueia conta do vendedor inesperadamente — 'não solicitei abertura de conta, agora tenho que arrumar milhões de documentos' (#450841895).",
            "Challenge recusado sem feedback específico: usuário não sabe qual documento corrigir e repete o processo indefinidamente (#450137943, #450937557).",
            "Informações contraditórias entre atendentes: 'cada atendente responde algo distinto, nunca sei como se resolveu' (#449734598) — falta de histórico persistente.",
            "Processo de representante legal inflexível: procuração enviada não aceita, conta congelada sem canal de recurso (#450112980).",
        ],
        "acoes": [
            "Comunicação proativa 72h antes de ativar challenge KYC — aviso com instrução clara dos documentos aceitos.",
            "Feedback específico no challenge recusado: indicar exatamente qual campo/documento falhou.",
            "Padronizar resposta entre atendentes com trilha única para challenge pendente/recusado.",
            "Criar canal de recurso para representante legal com SLA de 48h e acesso a especialista.",
        ],
    },
    {
        "drv": "ME Vendedor Meli Pro", "proc": "Reputación ME (HT - Ventas / Coleta)",
        "nps_cur": 78.33, "nps_tgt": 81.60, "delta_tgt": -3.27, "trend": "↓ Queda",
        "insights": [
            "Erro sistêmico: anúncio ativado com envio próprio gera penalidades de reputação — 'trabalho 8 anos com vocês, está cada vez pior' (#452686699). Queda de −8,42 pp vs S2.",
            "Problema não resolvido mesmo com atendente bem avaliado: 'atendente ótima, porém problema não resolvido' (#452506896) — exclusão de impacto Flex não ocorre automaticamente.",
            "Falhas de coleta Cross Docking sem proteção automática de reputação: seller obrigado a cancelar venda e ainda afeta mais a reputação (#452686699).",
            "Emissão de etiquetas e NF bloqueada afeta HT simultaneamente: 'não consegui emitir etiquetas e blindar minha reputação' (#452276788) — duplo impacto operacional + reputacional.",
        ],
        "acoes": [
            "Expandir critérios de exclusão automática para falhas Flex e Cross Docking — atendente não deve precisar escalar para equipe interna.",
            "Criar protocolo anti-loop para sellers que ativam envio próprio por erro sistêmico — exclusão imediata do impacto.",
            "Garantir emissão de etiqueta como pré-requisito antes de gerar impacto de HT por atraso de envio.",
            "Treinar atendentes com script específico para Meli Pro: sellers de alto volume exigem resolução FCR no 1º contato.",
        ],
    },
    {
        "drv": "Partners", "proc": "Places Kangu / Drivers",
        "nps_cur": 67.04, "nps_tgt": 70.19, "delta_tgt": -3.15, "trend": "↓ Queda",
        "insights": [
            "Regularização e emissão de NF é o CDU dominante (10 casos): agente Places bloqueado por pendência fiscal sem resolução em tempo real.",
            "Processo de cadastro como Agência MELI é barreira de entrada: 3 casos sem conseguir finalizar — suporte orienta mas não acompanha follow-up.",
            "Queda progressiva: Jan 68,41 → Fev 72,38 → Mar 67,39 → Abr 67,04 — abaixo do target de 70,19 pela segunda semana consecutiva.",
            "Atendentes sem ferramentas para resolver problemas operacionais do app Places em tempo real — resposta genérica de 'aguardar análise interna'.",
        ],
        "acoes": [
            "Criar canal direto de suporte fiscal para agentes Places Kangu com SLA de 24h.",
            "Revisar fluxo de cadastro de nova agência com acompanhamento automático de status.",
            "Capacitar atendentes Places com acesso às ferramentas do app de gestão.",
            "Escalar NPS Places Kangu para revisão de produto — queda consistente há 3 semanas com tendência confirmada.",
        ],
    },
]

ALERT_VA = []

ALERT_MES = [
    {
        "drv": "Otros CV", "proc": "KYC Services",
        "nps_cur": 46.41, "nps_tgt": 53.77, "delta_tgt": -7.36, "trend": "↓↓ Em queda",
        "insights": [
            "KYC Services domina o volume de Otros CV com queda de −10,23 pp vs Março — processo de verificação de identidade é o principal vetor de insatisfação na categoria.",
            "Challenge recusado sem feedback específico: usuário repete o processo indefinidamente sem saber o que corrigir (#450137943, #450937557).",
            "Ativação de challenge sem aviso prévio bloqueia conta inesperadamente — experiência traumática para seller que não entende o motivo (#450841895).",
            "Proceso de representante legal com múltiplos atendentes dando informações contraditórias (#449734598) — sem padronização nem SLA.",
        ],
        "acoes": [
            "Comunicação proativa 72h antes de ativar challenge KYC com instrução clara.",
            "Feedback específico no challenge recusado indicando exatamente o campo/documento falho.",
            "Padronizar fluxo KYC com trilha única entre atendentes — eliminar divergências de informação.",
            "SLA de 24h para casos de representante legal com acesso a especialista.",
        ],
    },
    {
        "drv": "PDD FBM - Vendedor", "proc": "Mediações FBM (Defectuoso/Arrepentimento/Diferente)",
        "nps_cur": 26.72, "nps_tgt": 40.67, "delta_tgt": -13.95, "trend": "↓↓ Em queda",
        "insights": [
            "Queda de −7,27 pp vs Março (33,99% → 26,72%) com 306 → 247 surveys — volume menor mas queda mais intensa, indica deterioração real no processo.",
            "Fallo automático percebido como injusto é a causa raiz: mediações FBM encerradas por IA sem análise humana do caso específico.",
            "Código de devolução expirado: prazo logístico real incompatível com o prazo gerado pelo sistema — compradores não conseguem devolver no prazo (#448544440).",
            "IA automática sem qualidade nas mediações: alto grau de automação nas mediações PDD FBM gera NPS 0 sistemático — 'inteligência artificial muito confusa' (#446771367).",
        ],
        "acoes": [
            "Criar revisão humana obrigatória para fallos automáticos em mediações PDD FBM — IA não deve ter poder de fallo final sem escalada.",
            "Aumentar prazo de código de devolução alinhado com logística FBM — prazos FBM são diferentes do XD.",
            "Implementar checkpoint humano antes do encerramento de mediações FBM de alto valor.",
            "Revisar critério de fallo V por atraso de despacho em FBM — verificar se é erro sistêmico ou comportamental.",
        ],
    },
    {
        "drv": "PDD DS&XD - Vendedor", "proc": "Mediações XD e DS (Defectuoso/Arrepentimento/Diferente)",
        "nps_cur": 11.39, "nps_tgt": 16.40, "delta_tgt": -5.01, "trend": "↓ Queda",
        "insights": [
            "Queda de −1,03 pp vs Março (12,42% → 11,39%) — volume alto (904 surveys) confirma tendência de deterioração no processo de mediação automática.",
            "Fallo automático do vendedor sem análise humana é a causa raiz: 'mediação encerrada automaticamente como fallo V' (#443401768) — sistema de mediação PDD é percebido como injusto e sem defesa.",
            "Código de devolução expirado: 'código estava expirado quando fui ao correio devolver' (#448544440) — prazo logístico real incompatível com o prazo gerado pelo sistema.",
            "Comprador com acessibilidade limitada forçado a ponto de devolução distante: 'sou PCD, obrigam me a ir a 1,5km' (#448602536) — política rígida sem exceção para casos especiais.",
        ],
        "acoes": [
            "Criar revisão humana obrigatória para fallos automáticos em mediações PDD — IA não deve ter poder de fallo final sem escalada.",
            "Aumentar prazo de código de devolução alinhado com a logística real de cada região.",
            "Criar exceção de acessibilidade para pontos de devolução — coleta em domicílio para PCD ou regiões sem pontos.",
            "Reduzir automação nas mediações PDD de alto valor — implementar checkpoint humano antes do encerramento.",
        ],
    },
    {
        "drv": "Partners", "proc": "Places Kangu",
        "nps_cur": 66.70, "nps_tgt": 70.19, "delta_tgt": -3.49, "trend": "↓ Queda",
        "insights": [
            "Regularização e emissão de NF é o CDU dominante (10 casos): agente Places bloqueado por pendência fiscal sem resolução em tempo real.",
            "Processo de cadastro como Agência MELI é barreira de entrada: 3 casos sem conseguir finalizar — suporte orienta mas não acompanha follow-up.",
            "Tendência de queda progressiva: Jan 68,41 → Fev 72,38 → Mar 67,39 → Abr 66,70 — abaixo do target de 70,19 pela terceira semana consecutiva.",
            "Atendentes sem ferramentas para resolver problemas operacionais do app Places em tempo real — resposta genérica de 'aguardar análise interna'.",
        ],
        "acoes": [
            "Criar canal direto de suporte fiscal para agentes Places Kangu com SLA de 24h.",
            "Revisar fluxo de cadastro de nova agência com acompanhamento automático de status.",
            "Capacitar atendentes Places com acesso às ferramentas do app de gestão.",
            "Escalar NPS Places Kangu para revisão de produto — queda consistente há 3 meses com tendência confirmada.",
        ],
    },
]

def dd_block(date_lbl, pos_drv, pos_var, pos_proc, pos_insights,
             neg_drv, neg_var, neg_proc, neg_insights, acoes_list):
    acoes_below = ""
    if acoes_list:
        items = "".join(
            f'<li style="font-size:12px;color:#444;line-height:1.6;padding:6px 0 6px 16px;'
            f'border-bottom:1px solid #f5f5f5;position:relative;">'
            f'<span style="position:absolute;left:0;color:var(--blue);font-weight:700;">•</span>{a}</li>'
            for a in acoes_list
        )
        acoes_below = (
            f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);'
            f'border-top:3px solid var(--blue);padding:14px 20px;margin-top:10px;margin-bottom:14px;">'
            f'<div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;'
            f'color:var(--blue);margin-bottom:8px;">Ações Recomendadas</div>'
            f'<ul style="list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:0 24px;">{items}</ul>'
            f'</div>'
        )
    return (
        f'<div class="section-title">Deep Dive Qualitativo — {date_lbl}</div>'
        f'<div class="deep-dive-grid">'
        f'<div class="deep-dive-card deep-dive-card-pos">'
        f'<div class="deep-dive-header"><div class="dd-title" style="color:var(--green);">&#9650; Maior Alta — {pos_drv} ({pos_var})</div>'
        f'<div class="dd-proc">{pos_proc}</div></div>'
        f'<div class="deep-dive-body"><ul>' + "".join(f'<li class="pos-li">{i}</li>' for i in pos_insights) + f'</ul></div></div>'
        f'<div class="deep-dive-card deep-dive-card-neg">'
        f'<div class="deep-dive-header"><div class="dd-title" style="color:var(--red);">&#9660; Alerta — {neg_drv} ({neg_var})</div>'
        f'<div class="dd-proc">{neg_proc}</div></div>'
        f'<div class="deep-dive-body"><ul>' + "".join(f'<li class="neg-li">{i}</li>' for i in neg_insights) + f'</ul></div></div>'
        f'</div>'
        + acoes_below
    )

def alert_dd_block(alerts, date_lbl):
    if not alerts:
        return ""

    def _quant_section(drv_key):
        aq = ALERT_ANALYSIS.get(drv_key, {})
        if not aq:
            return ""
        cdu_rows = ""
        for row in aq.get("cdu_breakdown", []):
            cdu_rows += (
                f'<tr><td style="font-size:10px;padding:4px 8px;border-bottom:1px solid #f5f5f5;">{row["cdu"]}</td>'
                f'<td style="font-size:10px;padding:4px 8px;border-bottom:1px solid #f5f5f5;color:#888;">{row["top_sol"]}</td>'
                f'<td style="font-size:10px;padding:4px 8px;border-bottom:1px solid #f5f5f5;text-align:right;font-weight:700;">{row["n"]}</td>'
                f'<td style="font-size:10px;padding:4px 8px;border-bottom:1px solid #f5f5f5;text-align:right;">'
                f'<span style="background:var(--light-red);color:var(--red);font-size:9px;font-weight:700;padding:1px 5px;border-radius:6px;">{str(row["pct"]).replace(".",",")}%</span>'
                f'</td></tr>'
            )
        th = 'style="font-size:9px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;border-bottom:2px solid #f0f0f0;"'
        cdu_table = (
            f'<div style="margin-top:10px;">'
            f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#FF7733;margin-bottom:6px;">Top CDUs / Soluções — Detratores</div>'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<thead><tr><th {th} style="text-align:left;">CDU</th><th {th} style="text-align:left;">Solução</th>'
            f'<th {th}>Casos</th><th {th}>% Det</th></tr></thead>'
            f'<tbody>{cdu_rows}</tbody></table></div>'
        )
        user_html = "".join(
            f'<li style="font-size:11px;padding:4px 0 4px 14px;border-bottom:1px solid #f5f5f5;position:relative;line-height:1.5;">'
            f'<span style="position:absolute;left:0;color:var(--blue);font-weight:700;">U</span>{t}</li>'
            for t in aq.get("user_themes", []))
        rep_html = "".join(
            f'<li style="font-size:11px;padding:4px 0 4px 14px;border-bottom:1px solid #f5f5f5;position:relative;line-height:1.5;">'
            f'<span style="position:absolute;left:0;color:#888;font-weight:700;">R</span>{t}</li>'
            for t in aq.get("rep_themes", []))
        themes = (
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px;">'
            f'<div><div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--blue);margin-bottom:6px;">Temas recorrentes — USER</div>'
            f'<ul style="list-style:none;padding:0;">{user_html}</ul></div>'
            f'<div><div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#888;margin-bottom:6px;">Padrão de resposta — REP</div>'
            f'<ul style="list-style:none;padding:0;">{rep_html}</ul></div>'
            f'</div>'
        )
        return cdu_table + themes

    cards = ""
    for a in alerts:
        gap_str    = f'{a["delta_tgt"]:+.2f}'.replace(".", ",")
        ins_html   = "".join(f'<li class="neg-li">{i}</li>' for i in a["insights"])
        acoes_html = "".join(f'<li style="color:var(--blue);" class="neg-li">{ac}</li>' for ac in a.get("acoes", []))
        quant_html = _quant_section(a["drv"])
        cards += (
            f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);border-top:4px solid #FF7733;overflow:hidden;">'
            f'<div style="padding:14px 18px;border-bottom:1px solid var(--border);background:#fff8f0;">'
            f'<div style="font-weight:800;font-size:14px;color:#FF7733;">&#9888; {a["drv"]}</div>'
            f'<div style="font-size:12px;color:#666;margin-top:3px;">{a["proc"]} · NPS {str(a["nps_cur"]).replace(".",",")}% vs Target {str(a["nps_tgt"]).replace(".",",")}% '
            f'({gap_str} pp) · {a["trend"]}</div></div>'
            f'<div style="padding:14px 18px;">'
            + quant_html +
            f'<div style="margin-top:12px;border-top:1px solid #f0f0f0;padding-top:10px;">'
            f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--red);margin-bottom:6px;">Insights — Comentários Detratores</div>'
            f'<ul class="deep-dive-body" style="padding:0;list-style:none;">{ins_html}</ul></div>'
            + (f'<div style="margin-top:10px;border-top:1px solid #f0f0f0;padding-top:10px;">'
               f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--blue);margin-bottom:6px;">Ações Recomendadas</div>'
               f'<ul style="list-style:none;padding:0;">{acoes_html}</ul></div>' if acoes_html else '') +
            f'</div></div>'
        )
    n = len(alerts)
    cols = "1fr " * n if n <= 2 else "1fr 1fr"
    return (
        f'<div class="section-title" style="border-left-color:#FF7733;">&#9888; Alerta Automático — Drivers Abaixo do Target em Queda — {date_lbl}</div>'
        f'<div style="display:grid;grid-template-columns:{cols};gap:16px;margin-bottom:14px;">{cards}</div>'
    )

deep_dive_sf_html = (
    dd_block(DEEP_DIVE_DATE, DEEP_DIVE_POS_DRIVER, DEEP_DIVE_POS_VAR, DEEP_DIVE_POS_PROC, DEEP_DIVE_POS_INSIGHTS,
             DEEP_DIVE_NEG_DRIVER, DEEP_DIVE_NEG_VAR, DEEP_DIVE_NEG_PROC, DEEP_DIVE_NEG_INSIGHTS, DCEV_ACOES_SF)
    + alert_dd_block(ALERT_SF, DEEP_DIVE_DATE)
)

deep_dive_mes_html = (
    dd_block(DD_MES_DATE, DD_MES_POS_DRIVER, DD_MES_POS_VAR, DD_MES_POS_PROC, DD_MES_POS_INSIGHTS,
             DD_MES_NEG_DRIVER, DD_MES_NEG_VAR, DD_MES_NEG_PROC, DD_MES_NEG_INSIGHTS, DD_MES_ACO)
    + alert_dd_block(ALERT_MES, DD_MES_DATE)
)

diag_va = (
    "Semana vigente {VIG_LABEL} — dados parciais (seg–qui). "
    "<strong>Post Venta Meli Pro</strong> lidera com NPS 96,43% (+8,04 pp vs S1): atendentes nomeados "
    "(Aline, Emanuel, Jennifer, Kathlen, Vitória) excluindo impacto de reputação no 1º contato são o driver exclusivo do NPS 10. "
    "<strong>Post Venta Seller Dev</strong> mantém evolução positiva (+4,16 pp, NPS 77,55%). "
    "Ponto crítico: <strong>Experiencia Impositiva Seller Dev</strong> despenca −17,94 pp (NPS 31,75%), a maior queda da semana — "
    "NF com número de série divergente travou anúncios full por 4 dias (#451516035); ligações caindo sem retorno sistematicamente. "
    "<strong>CBT</strong> recua −7,50 pp (NPS 62,50%) e <strong>Otros CV</strong> mantém pressão de KYC Services (challenge recusado + pendente). "
    "Partners e ME Vendedor estáveis. Alertas SF continuam válidos e se intensificam para ExpImp."
).replace("{VIG_LABEL}", VIG_LABEL)

exec_va = _rich_summary(vD, nVig, dVW, f"S1 ({S1_LABEL})", f"Vig ({VIG_LABEL})", diagnostic_html=diag_va)

# ── Deep Dive VIG completo ──────────────────────────────────────
DD_VIG_POS_DRIVER  = "Post Venta Meli Pro"
DD_VIG_POS_VAR     = "+8,98 pp"
DD_VIG_POS_PROC    = "Reputación: NPS 88,39% (S2) → 97,37% (S1) | 112 surveys S2 → 152 surveys S1 | análise baseada em S1 (VIG 27/abr sem dados)"
DD_VIG_POS_INSIGHTS = [
    "NPS 96,43% é o mais alto da gerência na semana vigente: atendentes nomeados (Aline, Emanuel, Jennifer, Cristiane, Gabriel, Kathlen, Vitória) aparecem em 100% dos NPS 10 — padrão consistente: exclusão do impacto de reputação no 1º contato (#451515923, #451575344, #452364055).",
    "Velocidade como fator crítico de NPS 10: 'rapidez extraordinária', 'em minutos', 'rápida e eficiente' — quando o atendente resolve FCR (First Contact Resolution), o vendedor dá nota máxima independente da situação de reputação.",
    "Atendimento humanizado pós-IA como diferencial: 'simples erro de IA fez cancelar uma venda' (#452029584) — o humano reverte a experiência negativa da IA e gera NPS 10.",
    "Padrão de solução dominante: 'Excluimos' (cancelamento/reclamação não afeta a reputação) — quando o atendente tem poder de excluir o impacto, o resultado é promotor consistente.",
]
DD_VIG_NEG_DRIVER  = "Experiencia Impositiva Seller Dev"
DD_VIG_NEG_VAR     = "-10,74 pp"
DD_VIG_NEG_PROC    = "Emision de Nota Fiscal + Facturação: NPS 49,38% (S2) → 38,64% (S1) | queda crítica — análise baseada em S1 (VIG 27/abr sem dados)"
DD_VIG_NEG_INSIGHTS = [
    "NF com número de série divergente travou TODOS os anúncios full do seller por 4 dias (17/04 a 21/04): 'perda de vendas pois todos os anúncios full ficaram inativos' (#451516035) — problema reportado em 17/4 resolvido apenas em 21/4 após 3 chamados.",
    "Ligações caindo sem retorno — padrão sistêmico: 3 casos independentes de ligação encerrada sem callback (#452209783, #452034621, #451602973, #452252733: 'desligou a ligação pela segunda vez sem resolver').",
    "NF pendente/cancelada/rejeitada sem resolução rápida: 'desde sábado 18/04 aguardando a etiqueta, não sai ainda!' (#452205687) — sellers bloqueados por dias sem conseguir despachar produtos.",
    "Cobranças automáticas (Faturamento Dívida/Débito) mantêm pressão: 'banco que permite desconto do governo sem aviso e sem consentimento' (#451743811) — problema estrutural de Facturação que persiste semana a semana.",
]
DD_VIG_ACO = [
    "Criar protocolo de callback obrigatório: quando ligação cai durante análise de Emissão NF, atendente deve retornar em até 10 minutos.",
    "SLA de emergência para NF com erro de série: problema de número de série de NF deve ser resolvido em até 4 horas — anúncios full não podem ficar inativos por dias.",
    "Habilitar emissão de DCe pelo app mobile — sellers continuam bloqueados pela limitação de desktop.",
    "Criar canal de prioridade para cobranças automáticas contestadas (Faturamento Dívida) — atendente precisa de poder de estorno para resolver no 1º contato.",
]

ALERT_ANALYSIS_VA = {
    "Experiencia Impositiva Seller Dev": {
        "cdu_breakdown": [
            {"cdu": "Faturador MeLi — NF pendente/cancelada/rejeitada",    "top_sol": "Invoice Pending / Faturador: Geral",              "n": 10, "pct": 43.5},
            {"cdu": "Faturamento — Dívida ou débito automático",             "top_sol": "Faturamento: Dívida ou débito",                   "n":  4, "pct": 17.4},
            {"cdu": "NF sem CDU (encerramento sem resolução)",               "top_sol": "Ticket encerrado sem resolução",                  "n":  5, "pct": 21.7},
            {"cdu": "Temporal / DCe para sellers",                           "top_sol": "DCe: Declaração de Conteúdo Eletrônica",          "n":  1, "pct":  4.3},
        ],
        "user_themes": [
            "NF com número de série divergente trava anúncios full por dias — '4 dias inativos' (#451516035)",
            "Ligação cai e nenhum atendente retorna — 3+ casos independentes de ligação encerrada sem callback",
            "NF pendente/rejeitada desde 18/04 aguardando etiqueta — seller bloqueado para despachar (#452205687)",
            "Cobrança automática sem consentimento + sem poder de estorno no 1º atendimento (#451743811)",
        ],
        "rep_themes": [
            "REP encerra ligação (2ª vez) sem resolver — 'desligou a ligação pela segunda vez' (#452252733)",
            "REP repassa para múltiplos atendentes sem histórico: 'repassado para 3 atendentes não preparados' (#451518459)",
            "REP sem poder de resolver erro de NF de série — escala para equipe interna sem SLA",
            "REP responde pergunta diferente da solicitada: 'responderam uma solicitação nada a ver com o que mandei' (#452023484)",
        ],
    },
    "Otros CV": {
        "cdu_breakdown": [
            {"cdu": "KYC Challenge Recusado",                  "top_sol": "KYC - Challenge Recusado",                       "n": 4, "pct": 57.1},
            {"cdu": "KYC Challenge Pendente (sem documento)",  "top_sol": "KYC - Challenge Pendente: enviamos link",        "n": 3, "pct": 42.9},
        ],
        "user_themes": [
            "Challenge recusado sem feedback específico — usuário repete sem saber o que corrigir",
            "Challenge pendente: documento enviado não aceito — conta travada sem instrução clara",
            "Padrão se mantém desde S1: KYC Services é o CDU dominante de Otros CV",
            "Processo não melhora semana a semana — ausência de SLA de resolução visível para o seller",
        ],
        "rep_themes": [
            "REP envia link de challenge sem explicar o que mudou vs tentativa anterior",
            "REP informa 'challenge recusado' sem detalhar o campo/documento específico que falhou",
            "REP sem poder de revisão manual — escala para equipe de segurança sem garantia de SLA",
            "Falta de histórico entre atendentes — cada contato reexplica o mesmo challenge",
        ],
    },
    "CBT": {
        "cdu_breakdown": [
            {"cdu": "CBT Reputação (reclamações compradores)", "top_sol": "CBT - Reputation: reclamações", "n": 7, "pct": 70.0},
            {"cdu": "CBT - Package journey / demoras",          "top_sol": "CBT - Demoras",                "n": 2, "pct": 20.0},
            {"cdu": "CBT - ME Reputation",                      "top_sol": "CBT - ME Reputation",          "n": 1, "pct": 10.0},
        ],
        "user_themes": [
            "Sellers cross-border impactados por reclamações de compradores percebidas como oportunistas",
            "Falta de continuidade de contexto: 'redirected to different agents, same info repeated' (#451109305)",
            "Barreira de idioma: sellers em inglês/mandarim sem canal dedicado em português",
            "CBT recua -7,50 pp vs S1 que já havia caído -4,26 pp — tendência de queda confirmada 2 semanas consecutivas",
        ],
        "rep_themes": [
            "REP sem ownership: redireciona para outro agente sem briefing",
            "REP sem ferramenta para reverter impacto de reputação de reclamações cross-border",
            "Políticas locais aplicadas a operação internacional — sem adaptação para CBT",
            "Falta de canal bilíngue com SLA dedicado para CBT — suporte generalista",
        ],
    },
}

ALERT_VA = []  # VIG 27/abr sem dados (início de semana)

def _alert_analysis_va(drv_key):
    return ALERT_ANALYSIS_VA.get(drv_key, ALERT_ANALYSIS.get(drv_key, {}))

def alert_dd_block_va(alerts, date_lbl):
    if not alerts: return ""
    def _quant_section(drv_key):
        aq = _alert_analysis_va(drv_key)
        if not aq: return ""
        cdu_rows = ""
        for row in aq.get("cdu_breakdown", []):
            cdu_rows += (
                f'<tr><td style="font-size:10px;padding:4px 8px;border-bottom:1px solid #f5f5f5;">{row["cdu"]}</td>'
                f'<td style="font-size:10px;padding:4px 8px;border-bottom:1px solid #f5f5f5;color:#888;">{row["top_sol"]}</td>'
                f'<td style="font-size:10px;padding:4px 8px;border-bottom:1px solid #f5f5f5;text-align:right;font-weight:700;">{row["n"]}</td>'
                f'<td style="font-size:10px;padding:4px 8px;border-bottom:1px solid #f5f5f5;text-align:right;">'
                f'<span style="background:var(--light-red);color:var(--red);font-size:9px;font-weight:700;padding:1px 5px;border-radius:6px;">{str(row["pct"]).replace(".",",")}%</span>'
                f'</td></tr>'
            )
        th = 'style="font-size:9px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;border-bottom:2px solid #f0f0f0;"'
        cdu_table = (
            f'<div style="margin-top:10px;">'
            f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#FF7733;margin-bottom:6px;">Top CDUs / Soluções — Detratores</div>'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<thead><tr><th {th} style="text-align:left;">CDU</th><th {th} style="text-align:left;">Solução</th>'
            f'<th {th}>Casos</th><th {th}>% Det</th></tr></thead><tbody>{cdu_rows}</tbody></table></div>'
        )
        user_html = "".join(
            f'<li style="font-size:11px;padding:4px 0 4px 14px;border-bottom:1px solid #f5f5f5;position:relative;line-height:1.5;">'
            f'<span style="position:absolute;left:0;color:var(--blue);font-weight:700;">U</span>{t}</li>'
            for t in aq.get("user_themes", []))
        rep_html = "".join(
            f'<li style="font-size:11px;padding:4px 0 4px 14px;border-bottom:1px solid #f5f5f5;position:relative;line-height:1.5;">'
            f'<span style="position:absolute;left:0;color:#888;font-weight:700;">R</span>{t}</li>'
            for t in aq.get("rep_themes", []))
        themes = (
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px;">'
            f'<div><div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--blue);margin-bottom:6px;">Temas recorrentes — USER</div>'
            f'<ul style="list-style:none;padding:0;">{user_html}</ul></div>'
            f'<div><div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#888;margin-bottom:6px;">Padrão de resposta — REP</div>'
            f'<ul style="list-style:none;padding:0;">{rep_html}</ul></div>'
            f'</div>'
        )
        return cdu_table + themes
    cards = ""
    for a in alerts:
        gap_str    = f'{a["delta_tgt"]:+.2f}'.replace(".", ",")
        ins_html   = "".join(f'<li class="neg-li">{i}</li>' for i in a["insights"])
        acoes_html = "".join(f'<li style="color:var(--blue);" class="neg-li">{ac}</li>' for ac in a.get("acoes", []))
        quant_html = _quant_section(a["drv"])
        cards += (
            f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);border-top:4px solid #FF7733;overflow:hidden;">'
            f'<div style="padding:14px 18px;border-bottom:1px solid var(--border);background:#fff8f0;">'
            f'<div style="font-weight:800;font-size:14px;color:#FF7733;">&#9888; {a["drv"]}</div>'
            f'<div style="font-size:12px;color:#666;margin-top:3px;">{a["proc"]} · NPS {str(a["nps_cur"]).replace(".",",")}% vs Target {str(a["nps_tgt"]).replace(".",",")}% '
            f'({gap_str} pp) · {a["trend"]}</div></div>'
            f'<div style="padding:14px 18px;">'
            + quant_html +
            f'<div style="margin-top:12px;border-top:1px solid #f0f0f0;padding-top:10px;">'
            f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--red);margin-bottom:6px;">Insights — Comentários Detratores</div>'
            f'<ul class="deep-dive-body" style="padding:0;list-style:none;">{ins_html}</ul></div>'
            + (f'<div style="margin-top:10px;border-top:1px solid #f0f0f0;padding-top:10px;">'
               f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--blue);margin-bottom:6px;">Ações Recomendadas</div>'
               f'<ul style="list-style:none;padding:0;">{acoes_html}</ul></div>' if acoes_html else '') +
            f'</div></div>'
        )
    n = len(alerts); cols = "1fr " * n if n <= 2 else "1fr 1fr"
    return (
        f'<div class="section-title" style="border-left-color:#FF7733;">&#9888; Alerta Automático — Drivers Abaixo do Target em Queda — {date_lbl}</div>'
        f'<div style="display:grid;grid-template-columns:{cols};gap:16px;margin-bottom:14px;">{cards}</div>'
    )

vigente_dd_html = (
    dd_block(
        "24/04/2026",
        DD_VIG_POS_DRIVER, DD_VIG_POS_VAR, DD_VIG_POS_PROC, DD_VIG_POS_INSIGHTS,
        DD_VIG_NEG_DRIVER, DD_VIG_NEG_VAR, DD_VIG_NEG_PROC, DD_VIG_NEG_INSIGHTS,
        DD_VIG_ACO
    )
    + alert_dd_block_va(ALERT_VA, VIG_LABEL)
)

vigente_banner_va = (
    f'<div class="vigente-banner">'
    f'<div style="font-size:12px;font-weight:700;color:#FFE600;text-transform:uppercase;letter-spacing:.6px;">Semana em andamento</div>'
    f'<div style="font-size:15px;font-weight:800;margin-top:3px;">{VIG_LABEL} (seg–qui)</div>'
    f'<div style="font-size:12px;color:#aaa;margin-top:2px;">Comparado com semana fechada: {S1_LABEL} · Dados parciais</div>'
    f'</div>'
    + vigente_dd_html
)

# ── Summaries para abas Acumuladas ──────────────────────────────
diag_sem_ac = (
    "Visão consolidada por categoria — semana fechada {S2_LABEL} → {S1_LABEL}. "
    "<strong>Longtail</strong> é a categoria de maior volume e seu movimento determina o consolidado da gerência. "
    "As categorias <strong>Meli Pro</strong> e <strong>Mature</strong> tendem a mostrar variações mais amplas por menor volume de surveys. "
    "<strong>Buyers</strong> (CBT + PDDs) concentra processos de mediação automatizada com NPS estruturalmente baixo — "
    "o movimento desta categoria reflete mudanças nas políticas de mediação, não na qualidade do atendimento isoladamente. "
    "<strong>FBM</strong> acompanha o ciclo operacional do fulfillment. "
    "Para diagnóstico detalhado por driver dentro de cada categoria, consulte a aba <strong>Semana Fechada</strong> com os filtros de categoria."
).replace("{S2_LABEL}", S2_LABEL).replace("{S1_LABEL}", S1_LABEL)

diag_mes_ac = (
    "Visão consolidada por categoria — mês a mês {M2_LABEL} → {M1_LABEL} (parcial Abril). "
    "<strong>Longtail</strong> concentra os maiores volumes e drivers estratégicos (ME Dev, Partners, Publi Dev, PCF Dev). "
    "<strong>Meli Pro</strong> e <strong>Mature</strong> mostram movimentos menores em volume mas podem sinalizar tendências de segmento. "
    "<strong>Buyers</strong> tem NPS estruturalmente baixo (mediações PDD): monitorar evolução mês a mês do delta, não o nível absoluto. "
    "<strong>FBM</strong> e <strong>Otros CV</strong> têm comportamento mais errático por volume reduzido — "
    "usar com cautela em análises mensais. "
    "Para diagnóstico qualitativo completo, consulte a aba <strong>Mensal</strong>."
).replace("{M2_LABEL}", M2_LABEL).replace("{M1_LABEL}", M1_LABEL)

# exec_sem_ac e exec_mes_ac serão gerados após cálculo das categorias (SECTION 5)

# ═══════════════════════════════════════════════════════════════
# SECTION 4D: CATEGORY FILTER HELPERS
# ═══════════════════════════════════════════════════════════════
DRIVERS_EXCLUIDOS_MED = frozenset([
    "CBT", "PDD DS&XD - Vendedor", "PDD FBM - Vendedor",
    "PDD Fotos - Vendedor", "PDD MP,FLEX & CBT - Vendedor",
    "PNR ME - Vendedor", "PNR MP - Vendedor",
])

CATS_FILTER = ["All Drivers", "Sem Med"] + CAT_ORDER
CAT_SLUG    = {c: c.replace(" ","_") for c in CATS_FILTER}
CAT_SLUG["All Drivers"] = "all"
CAT_SLUG["Sem Med"]     = "sem_med"

CAT_BTN_COLORS = {
    "All Drivers": "#1a1a2e",
    "Sem Med":     "#2C3E50",
    "Longtail":    "#E84142",
    "Mature":      "#00A650",
    "Meli Pro":    "#9B59B6",
    "Buyers":      "#3483FA",
    "FBM":         "#F39C12",
    "Otros CV":    "#7F8C8D",
}

def build_cat_filter_bar(tab_id):
    btns = ""
    for i, cat in enumerate(CATS_FILTER):
        slug   = CAT_SLUG[cat]
        clr    = CAT_BTN_COLORS.get(cat, "#666")
        active = ' active' if i == 0 else ''
        btns += (
            f'<button class="cat-btn{active}" '
            f'style="--cat-clr:{clr};" '
            f'onclick="selectCat(\'{tab_id}\',\'{slug}\',this)">'
            f'{cat}</button>'
        )
    return f'<div class="cat-filter-bar">{btns}</div>'

def _auto_diag_cat(cat, d_dict, label_a, label_b):
    """Gera diagnóstico automático para a visão filtrada de uma categoria."""
    sd = sorted(d_dict.items(), key=lambda x: -x[1]['var'])
    positivos = [(d,v) for d,v in sd if v['var'] > 0.5]
    negativos = [(d,v) for d,v in reversed(sd) if v['var'] < -0.5]
    alerts    = [(d,v) for d,v in sd if v['nps_b'] < DRIVER_TARGETS.get(d, 999) and v['var'] < -0.5]
    lines = []
    if positivos:
        best_d, best_v = positivos[0]
        lines.append(
            f'<strong>{DRIVER_SHORT.get(best_d, best_d)}</strong> foi o maior destaque positivo dentro de '
            f'<strong>{cat}</strong> ({("+" if best_v["var"]>=0 else "")}{fn(best_v["var"])} pp, '
            f'NPS {fn(best_v["nps_b"])}, {fi(best_v["surv_b"])} surveys).'
        )
    if negativos:
        worst_d, worst_v = negativos[0]
        lines.append(
            f'<strong>{DRIVER_SHORT.get(worst_d, worst_d)}</strong> registrou a maior queda '
            f'({fn(worst_v["var"])} pp, NPS {fn(worst_v["nps_b"])}).'
        )
    if alerts:
        alert_names = ', '.join(f'<strong>{DRIVER_SHORT.get(d,d)}</strong>' for d,_ in alerts[:3])
        gaps = ', '.join(f'{fn(round(v["nps_b"]-DRIVER_TARGETS.get(d,0),1))} pp' for d,v in alerts[:3])
        lines.append(f'Drivers abaixo do target em queda: {alert_names} (gaps vs target: {gaps}).')
    lines.append(
        f'Para análise qualitativa completa desta categoria (comentários, transcrições, CDU breakdown e ações), '
        f'consulte a aba <strong>Semana Fechada → All Drivers</strong>.'
    )
    return ' '.join(lines)

def _cat_dd_block(cat, d_dict, label_a, label_b, alerts_list):
    """Deep Dive simplificado para visão por categoria — quantitativo + referência qualitativa."""
    sd = sorted(d_dict.items(), key=lambda x: -x[1]['var'])
    positivos = [x for x in sd if x[1]['var'] > 0]
    negativos = list(reversed([x for x in sd if x[1]['var'] < 0]))
    best_d, best_v   = positivos[0]  if positivos else (None, {})
    worst_d, worst_v = negativos[0]  if negativos else (None, {})

    def _drv_card(drv, v, pos):
        if drv is None: return ''
        clr  = "var(--green)" if pos else "var(--red)"
        sign = "+" if pos else ""
        tgt  = DRIVER_TARGETS.get(drv, None)
        vs_t = (f'<div style="margin-top:4px;font-size:11px;color:{clr};">vs target: '
                f'{round(v["nps_b"]-tgt,2):+.2f} pp</div>') if tgt else ''
        rows_html = ""
        peers = [(d2, v2) for d2, v2 in (sd if pos else reversed(sd)) if d2 != drv][:3]
        for pd, pv in peers:
            pc  = "var(--green)" if pv['var']>=0 else "var(--red)"
            ps  = "+" if pv['var']>=0 else ""
            rows_html += (
                f'<div style="padding:4px 0;border-bottom:1px solid #eee;font-size:11px;">'
                f'<span style="color:#444;">{DRIVER_SHORT.get(pd,pd)}</span>'
                f' <span style="float:right;color:{pc};font-weight:700;">{ps}{fn(pv["var"])} pp</span>'
                f'<br><span style="color:#aaa;font-size:10px;">NPS {fn(pv["nps_a"])} → {fn(pv["nps_b"])} · {fi(pv["surv_b"])} surv</span>'
                f'</div>'
            )
        return (
            f'<div style="padding:14px 16px;">'
            f'<div style="font-weight:700;font-size:13px;color:{clr};">{DRIVER_SHORT.get(drv,drv)}</div>'
            f'<div style="font-size:12px;color:#555;margin-top:2px;">'
            f'NPS {fn(v["nps_a"])} → <strong>{fn(v["nps_b"])}</strong> ({sign}{fn(v["var"])} pp) · {fi(v["surv_b"])} surveys'
            f'</div>'
            + vs_t +
            (f'<div style="margin-top:10px;font-size:10px;font-weight:800;text-transform:uppercase;'
             f'letter-spacing:.5px;color:#aaa;margin-bottom:4px;">Outros drivers na categoria</div>'
             + rows_html if rows_html else '') +
            f'<div style="margin-top:10px;padding:8px 10px;background:#f8f9fa;border-radius:6px;'
            f'font-size:11px;color:#666;border-left:3px solid #ddd;">'
            f'📋 Para análise qualitativa deste driver (comentários, CDUs, ações), '
            f'consulte <strong>All Drivers → Deep Dive</strong>.'
            f'</div>'
            f'</div>'
        )

    cat_alerts = [a for a in alerts_list if DRIVER_CATEGORIA.get(a['drv']) == cat]
    alert_html = alert_dd_block(cat_alerts, label_b) if cat_alerts else ""

    return (
        f'<div class="section-title">Deep Dive — {cat} | {label_b}</div>'
        f'<div class="deep-dive-grid">'
        f'<div class="deep-dive-card deep-dive-card-pos">'
        f'<div class="deep-dive-header"><div class="dd-title" style="color:var(--green);">▲ Maior Alta — {cat}</div>'
        f'<div class="dd-proc">{label_a} → {label_b}</div></div>'
        + _drv_card(best_d, best_v, True) +
        f'</div>'
        f'<div class="deep-dive-card deep-dive-card-neg">'
        f'<div class="deep-dive-header"><div class="dd-title" style="color:var(--red);">▼ Maior Queda — {cat}</div>'
        f'<div class="dd-proc">{label_a} → {label_b}</div></div>'
        + _drv_card(worst_d, worst_v, False) +
        f'</div>'
        f'</div>'
        + alert_html
    )

def build_cat_view(tab_id, cat, pa, pb, label_a, label_b,
                   period_dict, hist_dict, hist_labels, is_weekly=True, alerts_list=None,
                   drivers_override=None, tgt_override=None, extra_html=""):
    slug      = CAT_SLUG[cat]
    drivers   = drivers_override if drivers_override is not None else [d for d, c in DRIVER_CATEGORIA.items() if c == cat]
    flt_p     = {d: period_dict[d] for d in drivers if d in period_dict}
    flt_h     = {d: hist_dict[d]   for d in drivers if d in hist_dict}
    tgt       = tgt_override if tgt_override is not None else cat_targets.get(cat, NPS_TARGET)
    dlbl      = "ΔWoW" if is_weekly else "ΔMoM"
    _alerts   = alerts_list or []

    if not flt_p:
        return (f'<div id="tab-{tab_id}-cat-{slug}" class="cat-view" style="display:none;">'
                f'<p style="padding:40px;color:#aaa;text-align:center;">Sem dados para esta categoria.</p></div>')

    sa  = sum(flt_p[d].get(pa,(0,0,0))[2] for d in flt_p)
    sb  = sum(flt_p[d].get(pb,(0,0,0))[2] for d in flt_p)
    pa_ = sum(flt_p[d].get(pa,(0,0,0))[0] for d in flt_p)
    da_ = sum(flt_p[d].get(pa,(0,0,0))[1] for d in flt_p)
    pb_ = sum(flt_p[d].get(pb,(0,0,0))[0] for d in flt_p)
    db_ = sum(flt_p[d].get(pb,(0,0,0))[1] for d in flt_p)
    na  = nps(pa_, da_, sa)
    nb  = nps(pb_, db_, sb)
    dlt = round(nb - na, 2)
    d_dict = mix_neto(flt_p, pa, pb, sa or 1, sb or 1, nb)

    cid_c  = f"cons_{tab_id}_{slug}"
    cid_wf = f"wf_{tab_id}_{slug}"
    cons_s = _consolidated_series(flt_h, hist_labels)
    cons_c = consolidated_chart_block(cid_c, hist_labels, cons_s, tgt)
    htbl   = driver_history_table(flt_h, hist_labels, DRIVER_TARGETS, delta_label=dlbl)

    if sb > 0:
        wf_c, _ = waterfall_block(cid_wf, label_a, na, label_b, nb, d_dict, chart_height=260)
        second_col = wf_c
    else:
        second_col = (
            f'<div style="background:#fff;border-radius:8px;border:1px solid var(--border);'
            f'padding:14px 16px;display:flex;align-items:center;justify-content:center;">'
            f'<span style="color:#bbb;font-size:13px;">Vigente sem dados — aguardar atualização</span></div>'
        )

    auto_diag  = _auto_diag_cat(cat, d_dict, label_a, label_b) if d_dict else ""
    rich_sum   = _rich_summary(d_dict, nb, dlt, label_a, label_b, diagnostic_html=auto_diag)
    dd_section = _cat_dd_block(cat, d_dict, label_a, label_b, _alerts) if d_dict else ""

    content = (
        kpi_cards(nb, sb or 0, f"{label_b} · {cat}", dlt, na, sa or 0, f"{label_a} · {cat}", target=tgt)
        + f'<div class="summary-box">'
        + f'<div class="summary-header">'
        + f'<div><div class="summary-title">Resumo — {cat}</div>'
        + f'<div class="summary-sub">{label_b}</div></div>'
        + f'<span class="nps-badge" style="background:{"var(--light-green)" if dlt>=0 else "var(--light-red)"};'
        + f'color:{"var(--green)" if dlt>=0 else "var(--red)"};">'
        + f'NPS {fn(nb)} {arrow(dlt)} {("+" if dlt>=0 else "")}{fn(dlt)} pp</span>'
        + f'</div><hr class="divider">'
        + rich_sum
        + f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px;">'
        + f'<div style="background:#fff;border-radius:8px;border:1px solid var(--border);padding:14px 16px;">'
        + f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#888;margin-bottom:4px;">NPS Consolidado vs Target</div>'
        + cons_c
        + f'</div>'
        + second_col
        + f'</div>'
        + htbl
        + f'</div>'
        + dd_section
        + extra_html
    )
    return f'<div id="tab-{tab_id}-cat-{slug}" class="cat-view" style="display:none;">{content}</div>'

# ═══════════════════════════════════════════════════════════════
# SECTION 5: BUILD TABS
# ═══════════════════════════════════════════════════════════════
_cons_w = _consolidated_series(weekly_history,     WEEK_LABELS)
_cons_v = _consolidated_series(weekly_history_vig, WEEK_LABELS_VIG)
_cons_m = _consolidated_series(monthly_history,    MONTH_LABELS)

cons_sf  = consolidated_chart_block("cons_sf",  WEEK_LABELS,     _cons_w, NPS_TARGET)
cons_va  = consolidated_chart_block("cons_va",  WEEK_LABELS_VIG, _cons_v, NPS_TARGET)
cons_mes = consolidated_chart_block("cons_mes", MONTH_LABELS,    _cons_m, NPS_TARGET)

htbl_sf  = driver_history_table(weekly_history,     WEEK_LABELS,     DRIVER_TARGETS, delta_label="ΔWoW")
htbl_va  = driver_history_table(weekly_history_vig, WEEK_LABELS_VIG, DRIVER_TARGETS, delta_label="ΔWoW")
htbl_mes = driver_history_table(monthly_history,    MONTH_LABELS,    DRIVER_TARGETS, delta_label="ΔMoM")

wf_sf_chart, wf_sf_side   = waterfall_block("wf_sf",  "S2", nS2, "S1",   nS1, wD)
wf_mes_chart, wf_mes_side  = waterfall_block("wf_mes", M2_LABEL[:3], nM2, M1_LABEL[:3], nM1, mD)

diag_sf = (
    "A semana 20–26/abr encerrou com alta de +1,42 pp, puxada principalmente pelo "
    "<strong>ME Vendedor Seller Dev</strong> (maior volume da gerência: 1.308 surveys, +3,41 pp) e "
    "<strong>Publicaciones Meli Pro</strong> (maior alta: +10,94 pp, NPS 85,94%). "
    "<strong>Experiencia Impositiva Seller Dev</strong> registrou queda crítica de −10,74 pp (NPS 38,64% vs target 59,03%) — "
    "DCe bloqueado em mobile, ligações caindo sem callback e IA com informações incorretas são as causas raiz. "
    "<strong>PNR MP</strong> e <strong>PNR ME</strong> em alerta: quedas de −33 pp e −14,75 pp respectivamente — "
    "fallos automáticos sem análise humana e prazos insuficientes de resposta geram insatisfação severa. "
    "<strong>CBT</strong> segue abaixo do target (NPS 62,77%, −7,82 pp): queda acumulada há 3 semanas, "
    "agravada por barreira de idioma e ausência de canal dedicado para sellers cross-border. "
    "<strong>Ação prioritária:</strong> habilitação de DCe via mobile para ExpImp + revisão de fallos automáticos em PNR."
)

diag_mes = (
    "Abril acumula +1,55 pp vs Março (59,91% vs 58,36%), mas esconde divergências significativas. "
    "<strong>Post Venta Meli Pro</strong> lidera a alta (+17,88 pp, NPS 91,95%) e <strong>Publi Meli Pro</strong> "
    "sobe +36,68 pp com crescimento acelerado de volume — segmento Meli Pro com forte melhora em Abril. "
    "Em contrapartida, <strong>Otros CV</strong> cai −10,23 pp (maior queda absoluta da gerência no mês): KYC Services "
    "ativa challenge sem aviso e sem feedback claro, travando contas de vendedores. "
    "<strong>PDD FBM</strong> (−7,27 pp, 247 surveys) em alerta crítico: mediações automáticas com fallo do vendedor sem "
    "revisão humana — queda mais intensa que PDD DS&XD apesar do menor volume. "
    "<strong>Partners/Places Kangu</strong> em queda progressiva há 4 meses (Jan 68,4 → Abr 66,7%), abaixo do target "
    "de 70,19%: regularização de NF fiscal é a principal barreira para agentes Places. "
    "<strong>Ação prioritária:</strong> comunicação proativa de KYC (72h de antecedência) + revisão de fallos "
    "automáticos em PDD FBM + canal fiscal dedicado para Places Kangu."
)

# ── Helper: bullet row para resumos executivos ──────────────────
def _bullet(icon, icon_bg, icon_color, title, title_color, meta_text,
            highlight_label, highlight_color, highlight_bg, highlight_text,
            body_items, body_text=""):
    icon_html = (f'<span style="display:inline-flex;align-items:center;justify-content:center;'
                 f'width:26px;height:26px;border-radius:50%;background:{icon_bg};color:{icon_color};'
                 f'font-size:12px;font-weight:900;flex-shrink:0;margin-top:1px;">{icon}</span>')
    meta = (f'<div style="font-size:11px;color:#999;margin-top:3px;font-style:italic;">{meta_text}</div>'
            if meta_text else '')
    btext = (f'<div style="font-size:12px;color:#555;line-height:1.55;margin-top:4px;">{body_text}</div>'
             if body_text else '')
    highlight = ""
    if highlight_label and highlight_text:
        highlight = (f'<div style="font-size:12px;background:{highlight_bg};border-left:3px solid {highlight_color};'
                     f'padding:6px 10px;border-radius:0 4px 4px 0;margin-top:5px;color:#444;line-height:1.55;">'
                     f'<span style="font-weight:700;color:{highlight_color};">{highlight_label} </span>{highlight_text}</div>')
    items_html = ""
    if body_items:
        items_html = "".join(
            f'<li style="font-size:12px;color:#555;line-height:1.55;padding:3px 0 3px 14px;'
            f'border-bottom:1px solid #fafafa;position:relative;">'
            f'<span style="position:absolute;left:0;color:{icon_color};font-weight:700;">›</span>{it}</li>'
            for it in body_items
        )
        items_html = f'<ul style="list-style:none;padding:0;margin-top:6px;">{items_html}</ul>'
    content = (f'<div style="font-size:13px;font-weight:700;color:#1a1a2e;line-height:1.4;">'
               f'<span style="color:{title_color};">{title}</span></div>'
               + meta + btext + highlight + items_html)
    return (f'<div style="display:grid;grid-template-columns:auto 1fr;gap:14px;'
            f'padding:12px 0;border-bottom:1px solid #f5f5f5;align-items:start;">'
            f'{icon_html}<div>{content}</div></div>')

_GREEN = "var(--green)"; _RED = "var(--red)"; _ORA = "#FF7733"
_LG = "rgba(0,166,80,.08)"; _LR = "#fdecea"; _LO = "#fff8f0"

exec_sf  = _rich_summary(wD,  nS1, dW,  f"S2 ({S2_LABEL})", f"S1 ({S1_LABEL})", diagnostic_html=diag_sf)
exec_mes = _rich_summary(mD,  nM1, dM,  M2_LABEL,            M1_LABEL,           diagnostic_html=diag_mes)

# ── Resumo Executivo Mensal com bullets qualitativos ────────────
_pv_pro_m2 = nps(*monthly_driver["Post Venta Meli Pro"]["M2"])
_pv_pro_m1 = nps(*monthly_driver["Post Venta Meli Pro"]["M1"])
_pb_pro_m2 = nps(*monthly_driver["Publicaciones Meli Pro"]["M2"])
_pb_pro_m1 = nps(*monthly_driver["Publicaciones Meli Pro"]["M1"])
_ei_m2     = nps(*monthly_driver["Experiencia Impositiva Seller Dev"]["M2"])
_ei_m1     = nps(*monthly_driver["Experiencia Impositiva Seller Dev"]["M1"])
_ocv_m2    = nps(*monthly_driver["Otros CV"]["M2"])
_ocv_m1    = nps(*monthly_driver["Otros CV"]["M1"])
_pdd_fbm_m2 = nps(*monthly_driver["PDD FBM - Vendedor"]["M2"])
_pdd_fbm_m1 = nps(*monthly_driver["PDD FBM - Vendedor"]["M1"])
_par_m2    = nps(*monthly_driver["Partners"]["M2"])
_par_m1    = nps(*monthly_driver["Partners"]["M1"])

_mes_drv_bullets = (
    _bullet("↑","rgba(0,166,80,.12)",_GREEN,
            f"NPS {fn(nM1)}% &nbsp;·&nbsp; {'+' if dM>=0 else ''}{fn(dM)} pp vs {M2_LABEL} &nbsp;·&nbsp; {fi(sM1)} pesquisas",
            _GREEN, None, None, None, None, None,
            [f"Consolidado: {fn(nM2)}% (Mar) → <strong>{fn(nM1)}%</strong> (Abr) &nbsp;·&nbsp; Meta: {fn(NPS_TARGET)}% &nbsp;·&nbsp; Gap vs target: {round(nM1-NPS_TARGET,2):+.2f} pp"])
    + _bullet("↑",_LG,_GREEN,
            "Post Venta Meli Pro", _GREEN,
            f"Reputación: NPS {fn(_pv_pro_m2)}% (Mar) → {fn(_pv_pro_m1)}% (Abr) | {monthly_driver['Post Venta Meli Pro']['M2'][2]} → {monthly_driver['Post Venta Meli Pro']['M1'][2]} surveys | +{fn(round(_pv_pro_m1-_pv_pro_m2,2))} pp",
            None, None, None, None, [],
            body_text=f"NPS 91,95% é o mais alto da gerência em Abril: exclusão de impacto de reputação com FCR no 1º contato por atendentes nomeados (Felipe, Aline, Elisama). 'Excelente atendimento do Felipe, esclareceu todas as minhas dúvidas' (#452065891). Meli Pro: seller 8 anos na plataforma reconhece qualidade do atendimento mesmo quando o problema é sistêmico — 'ótima atendente, problema não resolvido mas nota 10' (#452506896).")
    + _bullet("↑","rgba(0,166,80,.08)",_GREEN,
            "Publicaciones Meli Pro", _GREEN,
            f"Gestión de Publicación / DC-e: NPS {fn(_pb_pro_m2)}% (Mar) → {fn(_pb_pro_m1)}% (Abr) | {monthly_driver['Publicaciones Meli Pro']['M2'][2]} → {monthly_driver['Publicaciones Meli Pro']['M1'][2]} surveys | +{fn(round(_pb_pro_m1-_pb_pro_m2,2))} pp",
            None, None, None, None,
            [f"Crescimento de volume 4,6x ({monthly_driver['Publicaciones Meli Pro']['M2'][2]}→{monthly_driver['Publicaciones Meli Pro']['M1'][2]} surveys) confirma expansão do segmento Meli Pro em Publicaciones.",
             "FCR em DC-e e configuração de anúncio é o driver dominante de NPS 10: Luziene (#451941610) resolve declaração de conteúdo com seller no correio, passo-a-passo."])
    + _bullet("↓","var(--light-red)",_RED,
            "Otros CV", _RED,
            f"KYC Services: NPS {fn(_ocv_m2)}% (Mar) → {fn(_ocv_m1)}% (Abr) | {fi(monthly_driver['Otros CV']['M1'][2])} surveys | {fn(round(_ocv_m1-_ocv_m2,2))} pp",
            "Por que caiu:", _RED, _LR,
            "Challenge KYC ativado sem aviso bloqueia conta inesperadamente — desafio recusado sem feedback específico do campo que falhou. Informações contraditórias entre atendentes: 'cada atendente responde algo distinto, nunca sei como se resolveu o caso' (#449734598). Representante legal com procuração não aceita e conta congelada (#450112980).",
            [f"Maior queda mensal da gerência: −{fn(abs(round(_ocv_m1-_ocv_m2,2)))} pp (Mar {fn(_ocv_m2)}% → Abr {fn(_ocv_m1)}%). Deteriação acelerada sem melhora com ações de curto prazo.",
             "Ação prioritária: comunicação proativa 72h antes de ativar KYC + feedback específico do documento que falhou."])
    + _bullet("↓","var(--light-red)",_RED,
            "PDD FBM - Vendedor", _RED,
            f"Mediações FBM (Defectuoso/Arrepentimento/Diferente): NPS {fn(_pdd_fbm_m2)}% (Mar) → {fn(_pdd_fbm_m1)}% (Abr) | {fi(monthly_driver['PDD FBM - Vendedor']['M1'][2])} surveys | {fn(round(_pdd_fbm_m1-_pdd_fbm_m2,2))} pp",
            "Por que caiu:", _RED, _LR,
            "Fallo automático do vendedor sem análise humana é a causa raiz: mediação FBM encerrada por IA com fallo V sem verificação do prazo logístico real. Código de devolução expira antes do comprador conseguir chegar ao ponto de devolução (#448544440).",
            [f"Queda de −{fn(abs(round(_pdd_fbm_m1-_pdd_fbm_m2,2)))} pp em {fi(monthly_driver['PDD FBM - Vendedor']['M1'][2])} surveys — segunda maior queda mensal da gerência.",
             "Ação prioritária: checkpoint humano antes de encerrar mediação FBM automática + revisão do prazo de código de devolução."])
    + _bullet("⚠","#FF773322",_ORA,
            f"Partners &nbsp;<span style='font-size:11px;color:#888;font-weight:400;'>· NPS {fn(_par_m1)}% vs target {DRIVER_TARGETS['Partners']}% · {fn(round(_par_m1-_par_m2,2))} pp · ↓ Queda</span>",
            _ORA,
            f"Places Kangu / Drivers: NPS {fn(_par_m2)}% (Mar) → {fn(_par_m1)}% (Abr) | {fi(monthly_driver['Partners']['M1'][2])} surveys",
            "Por que está abaixo do target:", _ORA, _LO,
            "CDU dominante é regularização de NF para agentes Places (26,3% detratores): atendente orienta corretamente mas sem ferramenta para resolver pendência fiscal em tempo real — agente Places fica bloqueado sem operar.",
            ["Queda progressiva: Jan 68,41% → Fev 72,38% → Mar 67,39% → Abr 66,70% — 4 meses consecutivos abaixo do target de 70,19%.",
             "Ação prioritária: canal de suporte fiscal dedicado para Places Kangu com SLA 24h + acompanhamento automático de cadastro de nova agência."])
)

exec_mes_bullets = (
    f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);'
    f'border-left:4px solid var(--yellow);padding:18px 24px;margin-top:14px;">'
    f'<div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;'
    f'color:#888;margin-bottom:4px;">Análise por Driver — Transcrições + Comentários</div>'
    f'<div style="font-size:12px;color:#bbb;margin-bottom:12px;">{M2_LABEL} → {M1_LABEL}</div>'
    + _mes_drv_bullets +
    f'</div>'
)
exec_mes += exec_mes_bullets

_pnr_mp_key = "PNR MP - Vendedor"
_sf_bullets = (
    _bullet("↑","rgba(0,166,80,.12)",_GREEN,
            f"NPS {fn(nS1)}% &nbsp;·&nbsp; {'+' if dW>=0 else ''}{fn(dW)} pp vs {S2_LABEL} &nbsp;·&nbsp; {fi(sS1)} pesquisas",
            _GREEN, None, None, None, None, None,
            [f"Consolidado: {fn(nS2)}% (S2) → <strong>{fn(nS1)}%</strong> (S1) &nbsp;·&nbsp; Meta: {fn(NPS_TARGET)}% &nbsp;·&nbsp; Gap vs target: {round(nS1-NPS_TARGET,2):+.2f} pp"])
    + _bullet("↑",_LG,_GREEN,
            "Publicaciones Meli Pro", _GREEN,
            f"Gestión de Publicación / DC-e: NPS {fn(wD['Publicaciones Meli Pro']['nps_a'])}% (S2) → {fn(wD['Publicaciones Meli Pro']['nps_b'])}% (S1) | {fi(wD['Publicaciones Meli Pro']['surv_b'])} surveys",
            None, None, None, None, [],
            body_text="Atendentes humanizadas com FCR em Declaração de Conteúdo eletrônica (DC-e) geram NPS 10 consistentemente: vendedora no correio recebe instrução passo-a-passo da Luziene e resolve sem sair do chat — 'pode ficar despreocupada, estou aqui para lhe ajudar no que for preciso' (#451941610). Resolução completa no 1º contato, sem transferência.")
    + _bullet("↑","rgba(0,166,80,.08)",_GREEN,
            "ME Vendedor Seller Dev", _GREEN,
            f"Despacho Ventas y Publicaciones / Gestiones Operativas: NPS {fn(wD['ME Vendedor Seller Dev']['nps_a'])}% → {fn(wD['ME Vendedor Seller Dev']['nps_b'])}% | {fi(wD['ME Vendedor Seller Dev']['surv_b'])} surveys (maior volume da gerência)",
            None, None, None, None,
            ["Alta de +3,41 pp no driver de maior volume (1.308 surveys) confirma melhora real e sustentada na semana.",
             "Padrão promotor: exclusão de impacto de reputação no 1º contato com atendente nomeado — FCR é o único vetor de NPS 10 em ME."])
    + _bullet("↓","var(--light-red)",_RED,
            "Experiencia Impositiva Seller Dev", _RED,
            f"Emision de Nota Fiscal + Facturación: NPS {fn(wD['Experiencia Impositiva Seller Dev']['nps_a'])}% → {fn(wD['Experiencia Impositiva Seller Dev']['nps_b'])}% | {fi(wD['Experiencia Impositiva Seller Dev']['surv_b'])} surveys",
            "Por que caiu:", _RED, _LR,
            "NF emitida com série DIVERGENTE bloqueia venda: Lucas (REP) reconhece 'instabilidade técnica' no chat → escala para email → equipe responde 'não se trata de um erro' e encerra o caso sem ação (#452297712). Vendedor impedido de concluir a venda.",
            [f"NPS caiu de {fn(wD['Experiencia Impositiva Seller Dev']['nps_a'])}% (S2) para {fn(wD['Experiencia Impositiva Seller Dev']['nps_b'])}% (S1) — 2ª semana consecutiva de queda.",
             "Por que está abaixo do target (59,03%): DCe obrigatório só via desktop bloqueia sellers mobile-only; ticket fechado por timeout mesmo com problema aberto (#450867735); IA com informação incorreta por dias antes do humano corrigir.",
             "Padrão sistêmico: atendente reconhece o problema → escala para email → email responde 'não é um erro' → caso encerrado. Vendedor fica sem resolução."])
    + _bullet("↓","var(--light-red)",_RED,
            "PNR MP - Vendedor", _RED,
            f"PNR - MP (Produto Não Recebido via MP): NPS {fn(wD[_pnr_mp_key]['nps_a'])}% → {fn(wD[_pnr_mp_key]['nps_b'])}% | {fi(wD[_pnr_mp_key]['surv_b'])} surveys",
            "Por que caiu:", _RED, _LR,
            "Fallo automático mesmo com evidências apresentadas: 'Apesar de eu ter feito um texto explicando que o produto foi entregue em mãos e de ter anexado fotos comprovando a conversa, a mediação foi encerrada abruptamente, retirando meu dinheiro e minha reputação. Deveriam ter analisado melhor o meu caso.' (#451397873).",
            ["Volume pequeno (54 surveys) amplia volatilidade, mas o padrão é sistêmico: IA encerra mediação contra V mesmo quando seller apresenta provas.",
             "CDU dominante: 'PNR - Acuerdo entre partes' fallo V automático (36,6% dos detratores) — acordo forçado percebido como injusto."])
    + _bullet("⚠","#FF773322",_ORA,
            f"CBT &nbsp;<span style='font-size:11px;color:#888;font-weight:400;'>· NPS {fn(wD['CBT']['nps_b'])}% vs target {DRIVER_TARGETS['CBT']}% · −{fn(abs(wD['CBT']['var']))} pp · ↓ Queda</span>",
            _ORA,
            f"CBT - Reputation / CBT - ME Reputation: NPS {fn(wD['CBT']['nps_a'])}% → {fn(wD['CBT']['nps_b'])}% | {fi(wD['CBT']['surv_b'])} surveys",
            "Por que está abaixo do target:", _ORA, _LO,
            "Resolução automática (reembolso) aplicada sem consultar comprador sobre preferência: 'simplesmente devolveu parte do valor e encerrou o contato com o vendedor sem autorização. Quero receber o produto e não parte do dinheiro' (#452394026). Custos de importação não reembolsados agravam a insatisfação.",
            [f"3ª semana consecutiva abaixo do target de {DRIVER_TARGETS['CBT']}% — queda acumulada de −7,82 pp vs S2.",
             "Contexto cross-border sem continuidade: 'redirected to different agents, same info repeated' (#451109305) — suporte generalista sem ownership do caso CBT.",
             "Barreira de idioma: sellers em inglês/mandarim sem canal dedicado; políticas locais aplicadas à operação cross-border."])
    + _bullet("⚠","#FF773322",_ORA,
            f"Partners &nbsp;<span style='font-size:11px;color:#888;font-weight:400;'>· NPS {fn(wD['Partners']['nps_b'])}% vs target {DRIVER_TARGETS['Partners']}% · −{fn(abs(wD['Partners']['var']))} pp · ↓ Queda</span>",
            _ORA,
            f"Drivers / Places Kangu: NPS {fn(wD['Partners']['nps_a'])}% → {fn(wD['Partners']['nps_b'])}% | {fi(wD['Partners']['surv_b'])} surveys",
            "Por que está abaixo do target:", _ORA, _LO,
            "CDU dominante é regularização de NF para agentes Places (26,3% dos detratores): atendente orienta mas não tem ferramenta para resolver pendência fiscal em tempo real — agente Places fica bloqueado sem operar.",
            ["Queda progressiva: Jan 68,41% → Fev 72,38% → Mar 67,39% → Abr 67,04% — 3ª semana abaixo do target de 70,19%.",
             "Processo de cadastro como Agência MELI é barreira de entrada: 3 casos sem finalizar, suporte orienta mas não acompanha follow-up."])
)

exec_sf_bullets = (
    f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);'
    f'border-left:4px solid var(--yellow);padding:18px 24px;margin-top:14px;">'
    f'<div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;'
    f'color:#888;margin-bottom:4px;">Análise por Driver — Transcrições + Comentários</div>'
    f'<div style="font-size:12px;color:#bbb;margin-bottom:12px;">{S1_LABEL}</div>'
    + _sf_bullets +
    f'</div>'
)

exec_sf += exec_sf_bullets

# cat_targets precisa estar disponível antes de build_cat_view
cat_targets = _cat_targets(DRIVER_CATEGORIA, DRIVER_TARGETS, monthly_driver)

# ── Category filter views ───────────────────────────────────────
sf_filter  = build_cat_filter_bar("fechada")
mes_filter = build_cat_filter_bar("mensal")
va_filter  = build_cat_filter_bar("vigente")

wDv_per = {d: {"S1": weekly_driver[d]["S1"], "Vig": drivers_vigente.get(d,(0,0,0))} for d in weekly_driver}

sf_cat_views  = "".join(
    build_cat_view("fechada", cat, "S2", "S1",
                   f"S2 ({S2_LABEL})", f"S1 ({S1_LABEL})",
                   weekly_driver, weekly_history, WEEK_LABELS,
                   is_weekly=True, alerts_list=ALERT_SF)
    for cat in CAT_ORDER
)
mes_cat_views = "".join(
    build_cat_view("mensal", cat, "M2", "M1",
                   M2_LABEL, M1_LABEL,
                   monthly_driver, monthly_history, MONTH_LABELS,
                   is_weekly=False, alerts_list=ALERT_MES)
    for cat in CAT_ORDER
)

# ── Sem Med: drivers sem mediações (excluindo 7 drivers Buyers) ──
_drv_sm = [d for d in DRIVER_CATEGORIA if d not in DRIVERS_EXCLUIDOS_MED]
_wd_sm  = {d: weekly_driver[d]  for d in _drv_sm}
_md_sm  = {d: monthly_driver[d] for d in _drv_sm}
_wh_sm  = {d: weekly_history[d] for d in _drv_sm}
_mh_sm  = {d: monthly_history[d] for d in _drv_sm}

# NPS Sem Med para bullets
_sms1p=sum(v["S1"][0] for v in _wd_sm.values()); _sms1d=sum(v["S1"][1] for v in _wd_sm.values()); _sms1s=sum(v["S1"][2] for v in _wd_sm.values())
_sms2p=sum(v["S2"][0] for v in _wd_sm.values()); _sms2d=sum(v["S2"][1] for v in _wd_sm.values()); _sms2s=sum(v["S2"][2] for v in _wd_sm.values())
_smm1p=sum(v["M1"][0] for v in _md_sm.values()); _smm1d=sum(v["M1"][1] for v in _md_sm.values()); _smm1s=sum(v["M1"][2] for v in _md_sm.values())
_smm2p=sum(v["M2"][0] for v in _md_sm.values()); _smm2d=sum(v["M2"][1] for v in _md_sm.values()); _smm2s=sum(v["M2"][2] for v in _md_sm.values())
_sm_nS1=nps(_sms1p,_sms1d,_sms1s); _sm_nS2=nps(_sms2p,_sms2d,_sms2s); _sm_dW=round(_sm_nS1-_sm_nS2,2)
_sm_nM1=nps(_smm1p,_smm1d,_smm1s); _sm_nM2=nps(_smm2p,_smm2d,_smm2s); _sm_dM=round(_sm_nM1-_sm_nM2,2)
_sm_tgt_sf  = round(sum(DRIVER_TARGETS[d]*v["S1"][2] for d,v in _wd_sm.items() if d in DRIVER_TARGETS) / max(_sms1s,1), 2)
_sm_tgt_mes = round(sum(DRIVER_TARGETS[d]*v["M1"][2] for d,v in _md_sm.items() if d in DRIVER_TARGETS) / max(_smm1s,1), 2)

def _sem_med_bullets(is_weekly):
    n1 = _sm_nS1 if is_weekly else _sm_nM1
    n2 = _sm_nS2 if is_weekly else _sm_nM2
    dlt= _sm_dW  if is_weekly else _sm_dM
    s1 = _sms1s  if is_weekly else _smm1s
    lbl_a = S2_LABEL if is_weekly else M2_LABEL
    lbl_b = S1_LABEL if is_weekly else M1_LABEL
    tgt   = _sm_tgt_sf if is_weekly else _sm_tgt_mes
    return (
        _bullet("↑","rgba(0,166,80,.12)",_GREEN,
                f"NPS Sem Med {fn(n1)}% &nbsp;·&nbsp; {'+' if dlt>=0 else ''}{fn(dlt)} pp vs {lbl_a} &nbsp;·&nbsp; {fi(s1)} pesquisas",
                _GREEN, None, None, None, None, None,
                [f"Consolidado sem mediações: {fn(n2)}% → <strong>{fn(n1)}%</strong> &nbsp;·&nbsp; Meta ponderada: {fn(tgt)}% &nbsp;·&nbsp; Gap vs target: {round(n1-tgt,2):+.2f} pp",
                 f"Excluídos: CBT · PDD DS&XD · PDD FBM · PDD Fotos · PDD MP/FLEX · PNR ME · PNR MP — categorias com mediações automáticas percebidas como injustas"])
        + _bullet("↑",_LG,_GREEN,
                "Publicaciones Meli Pro" if is_weekly else "Post Venta Meli Pro", _GREEN,
                (f"DC-e: {fn(wD['Publicaciones Meli Pro']['nps_a'])}% → {fn(wD['Publicaciones Meli Pro']['nps_b'])}% | +{fn(round(wD['Publicaciones Meli Pro']['var'],2))} pp"
                 if is_weekly else
                 f"Reputación: {fn(_pv_pro_m2)}% → {fn(_pv_pro_m1)}% | +{fn(round(_pv_pro_m1-_pv_pro_m2,2))} pp"),
                None, None, None, None, [],
                body_text=("FCR em DC-e e configuração de anúncio gera NPS 10: Luziene resolve declaração de conteúdo com seller no correio passo-a-passo (#451941610)."
                           if is_weekly else
                           "NPS 91,95% é o mais alto da gerência em Abril: exclusão de impacto de reputação com FCR por atendentes nomeados (Felipe, Elisama, Aline). 'Excelente atendimento do Felipe, esclareceu todas as minhas dúvidas' (#452065891)."))
        + _bullet("↓","var(--light-red)",_RED,
                "Experiencia Impositiva Seller Dev", _RED,
                (f"Emision de Nota Fiscal + Facturación: {fn(wD['Experiencia Impositiva Seller Dev']['nps_a'])}% → {fn(wD['Experiencia Impositiva Seller Dev']['nps_b'])}% | {fi(wD['Experiencia Impositiva Seller Dev']['surv_b'])} surveys"
                 if is_weekly else
                 f"Emision de Nota Fiscal: {fn(_ei_m2)}% (Mar) → {fn(_ei_m1)}% (Abr) | {fi(monthly_driver['Experiencia Impositiva Seller Dev']['M1'][2])} surveys"),
                "Por que caiu:" if is_weekly else "Por que está abaixo do target:",
                _RED, _LR,
                ("NF emitida com série DIVERGENTE bloqueia venda: Lucas (REP) reconhece instabilidade técnica no chat → escala para email → equipe responde 'não se trata de um erro' e encerra sem ação (#452297712)."
                 if is_weekly else
                 "Target: 59,03%. DCe obrigatório só via desktop, ligação cai sem retorno, IA com informação incorreta por dias antes de humano corrigir. 'A 10 anos só pelo celular, agora não tenho mais como' (#450436581)."),
                (["NPS 38,64% vs target 59,03% — gap de −20,39 pp. 2ª semana consecutiva de queda.",
                  "Padrão: atendente reconhece → email diz 'não é um erro' → caso encerrado. Vendedor fica sem resolução."]
                 if is_weekly else
                 [f"NPS {fn(_ei_m1)}% vs target 59,03% — crônico, sem melhora sustentada em Abril.",
                  "Ticket fechado por timeout sem resolução (#450867735) — padrão estrutural."]))
        + _bullet("⚠","#FF773322",_ORA,
                f"Otros CV &nbsp;<span style='font-size:11px;color:#888;font-weight:400;'>· NPS {fn(_ocv_m1 if not is_weekly else wD['Otros CV']['nps_b'])}% · abaixo do target</span>",
                _ORA,
                (f"KYC Services: {fn(wD['Otros CV']['nps_a'])}% → {fn(wD['Otros CV']['nps_b'])}% | {fi(wD['Otros CV']['surv_b'])} surveys"
                 if is_weekly else
                 f"KYC Services: {fn(_ocv_m2)}% (Mar) → {fn(_ocv_m1)}% (Abr) | {fi(monthly_driver['Otros CV']['M1'][2])} surveys"),
                "Por que está abaixo do target:", _ORA, _LO,
                "Challenge KYC ativado sem aviso bloqueia conta — desafio recusado sem feedback do campo que falhou. 'Cada atendente responde algo distinto, nunca sei como se resolveu' (#449734598).",
                ["Ação: comunicação proativa 72h antes de ativar KYC + trilha única padronizada entre atendentes.",
                 "Partners também abaixo do target: regularização NF bloqueia agentes Places, queda progressiva há 4 meses."])
    )

def _sem_med_bullets_html(is_weekly):
    lbl = S1_LABEL if is_weekly else f"{M2_LABEL} → {M1_LABEL}"
    return (
        f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);'
        f'border-left:4px solid var(--yellow);padding:18px 24px;margin-top:14px;">'
        f'<div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;'
        f'color:#888;margin-bottom:4px;">Análise Sem Med — Transcrições + Comentários</div>'
        f'<div style="font-size:12px;color:#bbb;margin-bottom:12px;">{lbl}</div>'
        + _sem_med_bullets(is_weekly) +
        f'</div>'
    )

sf_cat_views += build_cat_view(
    "fechada", "Sem Med", "S2", "S1",
    f"S2 ({S2_LABEL})", f"S1 ({S1_LABEL})",
    _wd_sm, _wh_sm, WEEK_LABELS,
    is_weekly=True, alerts_list=ALERT_SF,
    drivers_override=_drv_sm, tgt_override=_sm_tgt_sf,
    extra_html=_sem_med_bullets_html(True)
)
mes_cat_views += build_cat_view(
    "mensal", "Sem Med", "M2", "M1",
    M2_LABEL, M1_LABEL,
    _md_sm, _mh_sm, MONTH_LABELS,
    is_weekly=False, alerts_list=ALERT_MES,
    drivers_override=_drv_sm, tgt_override=_sm_tgt_mes,
    extra_html=_sem_med_bullets_html(False)
)
va_cat_views  = "".join(
    build_cat_view("vigente", cat, "S1", "Vig",
                   f"S1 ({S1_LABEL})", f"Vig ({VIG_LABEL})",
                   wDv_per, weekly_history_vig, WEEK_LABELS_VIG,
                   is_weekly=True, alerts_list=ALERT_VA)
    for cat in CAT_ORDER
)

tab_sf = tab_content(
    "fechada", nS1, sS1, f"S1 ({S1_LABEL})", dW, nS2, sS2, f"S2 ({S2_LABEL})",
    wD, wf_html=wf_sf_chart, wf_side=wf_sf_side, cons_html=cons_sf, hist_table=htbl_sf,
    extra_html=deep_dive_sf_html, rich_summary=exec_sf,
    cat_filter_bar=sf_filter, cat_views_html=sf_cat_views
)
tab_va = tab_content(
    "vigente", nVig, sVig or 0, f"Vig ({VIG_LABEL})", dVW, nS1, sS1, f"S1 ({S1_LABEL})",
    vD, cons_html=cons_va, hist_table=htbl_va, extra_html=vigente_banner_va,
    rich_summary=exec_va,
    cat_filter_bar=va_filter, cat_views_html=va_cat_views
)
tab_mes = tab_content(
    "mensal", nM1, sM1, M1_LABEL, dM, nM2, sM2, M2_LABEL,
    mD, wf_html=wf_mes_chart, wf_side=wf_mes_side, cons_html=cons_mes, hist_table=htbl_mes,
    extra_html=deep_dive_mes_html, rich_summary=exec_mes,
    cat_filter_bar=mes_filter, cat_views_html=mes_cat_views
)

# ── Abas Acumuladas por Categoria ───────────────────────────────
# (cat_targets já calculado acima)

# Dados semanais por categoria
cat_weekly   = _agg_driver_dict_by_cat(weekly_driver, DRIVER_CATEGORIA)
cat_sS2 = sum(cat_weekly[c]["S2"][2] for c in cat_weekly)
cat_sS1 = sum(cat_weekly[c]["S1"][2] for c in cat_weekly)
cat_pS2 = sum(cat_weekly[c]["S2"][0] for c in cat_weekly)
cat_dS2 = sum(cat_weekly[c]["S2"][1] for c in cat_weekly)
cat_pS1 = sum(cat_weekly[c]["S1"][0] for c in cat_weekly)
cat_dS1 = sum(cat_weekly[c]["S1"][1] for c in cat_weekly)
cat_nS2  = nps(cat_pS2, cat_dS2, cat_sS2)
cat_nS1  = nps(cat_pS1, cat_dS1, cat_sS1)
cat_dW   = round(cat_nS1 - cat_nS2, 2)
cat_wD   = mix_neto(cat_weekly, "S2", "S1", cat_sS2, cat_sS1, cat_nS1)

# Dados mensais por categoria
cat_monthly  = _agg_driver_dict_by_cat(monthly_driver, DRIVER_CATEGORIA)
cat_sM2 = sum(cat_monthly[c]["M2"][2] for c in cat_monthly)
cat_sM1 = sum(cat_monthly[c]["M1"][2] for c in cat_monthly)
cat_pM2 = sum(cat_monthly[c]["M2"][0] for c in cat_monthly)
cat_dM2 = sum(cat_monthly[c]["M2"][1] for c in cat_monthly)
cat_pM1 = sum(cat_monthly[c]["M1"][0] for c in cat_monthly)
cat_dM1 = sum(cat_monthly[c]["M1"][1] for c in cat_monthly)
cat_nM2  = nps(cat_pM2, cat_dM2, cat_sM2)
cat_nM1  = nps(cat_pM1, cat_dM1, cat_sM1)
cat_dM   = round(cat_nM1 - cat_nM2, 2)
cat_mD   = mix_neto(cat_monthly, "M2", "M1", cat_sM2, cat_sM1, cat_nM1)

# Histórico por categoria
cat_week_hist = _agg_history_by_cat(weekly_history,  WEEK_LABELS,  DRIVER_CATEGORIA)
cat_mon_hist  = _agg_history_by_cat(monthly_history, MONTH_LABELS, DRIVER_CATEGORIA)
_cons_cw = _consolidated_series(cat_week_hist,  WEEK_LABELS)
_cons_cm = _consolidated_series(cat_mon_hist,   MONTH_LABELS)

cons_sem_ac  = consolidated_chart_block("cons_sem_ac",  WEEK_LABELS,  _cons_cw, NPS_TARGET)
cons_mes_ac  = consolidated_chart_block("cons_mes_ac",  MONTH_LABELS, _cons_cm, NPS_TARGET)
htbl_sem_ac  = driver_history_table(cat_week_hist, WEEK_LABELS,  cat_targets, delta_label="ΔWoW", name_map=CAT_SHORT)
htbl_mes_ac  = driver_history_table(cat_mon_hist,  MONTH_LABELS, cat_targets, delta_label="ΔMoM", name_map=CAT_SHORT)
wf_sem_chart, wf_sem_side = waterfall_block("wf_sem_ac", "S2", cat_nS2, "S1",  cat_nS1, cat_wD, name_map=CAT_SHORT)
wf_mac_chart, wf_mac_side = waterfall_block("wf_mes_ac", M2_LABEL[:3], cat_nM2, M1_LABEL[:3], cat_nM1, cat_mD, name_map=CAT_SHORT)

exec_sem_ac = _rich_summary(cat_wD, cat_nS1, cat_dW,
                             f"S2 ({S2_LABEL})", f"S1 ({S1_LABEL})",
                             diagnostic_html=diag_sem_ac,
                             name_map=CAT_SHORT, targets_dict=cat_targets)
exec_mes_ac = _rich_summary(cat_mD, cat_nM1, cat_dM,
                             M2_LABEL, M1_LABEL,
                             diagnostic_html=diag_mes_ac,
                             name_map=CAT_SHORT, targets_dict=cat_targets)

# ── Resumo Executivo Semanal Acumulado (por categoria) ──────────
def _cat_pds(period_key):
    r={}
    for c in ["Longtail","Mature","Meli Pro","Buyers","FBM","Otros CV"]:
        ps=[v[period_key] for d,v in weekly_driver.items() if DRIVER_CATEGORIA.get(d)==c]
        tp=sum(x[0] for x in ps); td=sum(x[1] for x in ps); ts=sum(x[2] for x in ps)
        r[c]=(nps(tp,td,ts), ts)
    return r
_cw_s1 = _cat_pds("S1"); _cw_s2 = _cat_pds("S2")

def _cat_pds_m(period_key):
    r={}
    for c in ["Longtail","Mature","Meli Pro","Buyers","FBM","Otros CV"]:
        ps=[v[period_key] for d,v in monthly_driver.items() if DRIVER_CATEGORIA.get(d)==c]
        tp=sum(x[0] for x in ps); td=sum(x[1] for x in ps); ts=sum(x[2] for x in ps)
        r[c]=(nps(tp,td,ts), ts)
    return r
_cm_m1 = _cat_pds_m("M1"); _cm_m2 = _cat_pds_m("M2")

_sem_bullets = (
    _bullet("↑","rgba(0,166,80,.12)",_GREEN,
            f"NPS {fn(cat_nS1)}% &nbsp;·&nbsp; {'+' if cat_dW>=0 else ''}{fn(cat_dW)} pp vs {S2_LABEL} &nbsp;·&nbsp; {fi(cat_sS1)} pesquisas",
            _GREEN, None, None, None, None, None,
            [f"Todas as categorias consolidadas: Longtail {fn(_cw_s1['Longtail'][0])}% &nbsp;·&nbsp; Mature {fn(_cw_s1['Mature'][0])}% &nbsp;·&nbsp; Meli Pro {fn(_cw_s1['Meli Pro'][0])}% &nbsp;·&nbsp; FBM {fn(_cw_s1['FBM'][0])}% &nbsp;·&nbsp; Buyers {fn(_cw_s1['Buyers'][0])}% &nbsp;·&nbsp; Otros CV {fn(_cw_s1['Otros CV'][0])}%"])
    + _bullet("↑",_LG,_GREEN,
            "Meli Pro", _GREEN,
            f"NPS {fn(_cw_s2['Meli Pro'][0])}% (S2) → {fn(_cw_s1['Meli Pro'][0])}% (S1) | {fi(_cw_s1['Meli Pro'][1])} surveys | +{fn(round(_cw_s1['Meli Pro'][0]-_cw_s2['Meli Pro'][0],2))} pp",
            None, None, None, None, [],
            body_text="Todos os 5 drivers Meli Pro melhoraram em S1: Post Venta +8,98 pp (97,37%), Publicaciones +10,94 pp (85,94%), PCF +4,62 pp (66,41%), ME +8,42 pp invertido (+8,42 pp de queda — ver alerta). NPS Meli Pro é o mais alto da gerência. FCR de atendentes humanizados (Felipe, Luziene) é o diferencial — 'Excelente atendimento do Felipe, esclareceu todas as minhas dúvidas' (#452065891).")
    + _bullet("↑","rgba(0,166,80,.06)",_GREEN,
            "FBM", _GREEN,
            f"NPS {fn(_cw_s2['FBM'][0])}% (S2) → {fn(_cw_s1['FBM'][0])}% (S1) | {fi(_cw_s1['FBM'][1])} surveys | +{fn(round(_cw_s1['FBM'][0]-_cw_s2['FBM'][0],2))} pp",
            None, None, None, None,
            ["FBM-S Meli Pro: NPS 40,00% → 85,00% (+45 pp) com 20 surveys — pequeno volume mas sinal positivo.",
             "FBM-S Seller Dev: NPS 43,56% → 46,28% (+2,72 pp, 121 surveys) — melhora consistente no maior driver FBM."])
    + _bullet("↓","var(--light-red)",_RED,
            "Buyers", _RED,
            f"NPS {fn(_cw_s2['Buyers'][0])}% (S2) → {fn(_cw_s1['Buyers'][0])}% (S1) | {fi(_cw_s1['Buyers'][1])} surveys | {fn(round(_cw_s1['Buyers'][0]-_cw_s2['Buyers'][0],2))} pp",
            "Por que caiu:", _RED, _LR,
            "PNR MP puxa a categoria para baixo: queda de −33,22 pp (NPS 5,56%) com fallo automático mesmo após vendedor apresentar fotos e texto provando entrega em mãos (#451397873). CBT também cai −7,82 pp com reembolso automático aplicado sem perguntar ao comprador se preferia o produto (#452394026).",
            [f"Buyers é a categoria com NPS mais baixo da gerência ({fn(_cw_s1['Buyers'][0])}%) — 7 drivers com mediações automatizadas percebidas como injustas.",
             "PNR ME também em queda: −14,75 pp (NPS 20,39%) com extravios em trânsito gerando fallo V sem análise de responsabilidade logística.",
             "Ação prioritária: revisão de fallos automáticos em PNR MP e ME — IA não deve ter poder de fallo final sem análise de evidências."])
    + _bullet("⚠","#FF773322",_ORA,
            f"Otros CV &nbsp;<span style='font-size:11px;color:#888;font-weight:400;'>· NPS {fn(_cw_s1['Otros CV'][0])}% · −{fn(abs(round(_cw_s1['Otros CV'][0]-_cw_s2['Otros CV'][0],2)))} pp · ↓ Queda</span>",
            _ORA,
            f"KYC Services: NPS {fn(_cw_s2['Otros CV'][0])}% → {fn(_cw_s1['Otros CV'][0])}% | {fi(_cw_s1['Otros CV'][1])} surveys",
            "Por que está abaixo do target:", _ORA, _LO,
            "Challenge KYC ativado sem aviso bloqueia conta do vendedor inesperadamente — desafio recusado sem feedback específico sobre o campo/documento que falhou (#450841895, #450137943). Processo de representante legal inflexível sem SLA de revisão (#450112980).",
            ["Padrão sistêmico: cada atendente responde algo distinto sobre o mesmo challenge — 'cada atendente responde algo distinto, nunca sei como se resolveu' (#449734598).",
             "Ação prioritária: comunicação proativa 72h antes de ativar challenge KYC + feedback específico do campo que falhou."])
)

exec_sem_ac_bullets = (
    f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);'
    f'border-left:4px solid var(--yellow);padding:18px 24px;margin-top:14px;">'
    f'<div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;'
    f'color:#888;margin-bottom:4px;">Análise por Categoria — Transcrições + Comentários</div>'
    f'<div style="font-size:12px;color:#bbb;margin-bottom:12px;">{S1_LABEL}</div>'
    + _sem_bullets +
    f'</div>'
)
exec_sem_ac += exec_sem_ac_bullets

# ── Resumo Executivo Mensal Acumulado (por categoria) ───────────
_mes_bullets = (
    _bullet("↑","rgba(0,166,80,.12)",_GREEN,
            f"NPS {fn(cat_nM1)}% &nbsp;·&nbsp; {'+' if cat_dM>=0 else ''}{fn(cat_dM)} pp vs {M2_LABEL} &nbsp;·&nbsp; {fi(cat_sM1)} pesquisas",
            _GREEN, None, None, None, None, None,
            [f"Todas as categorias: Longtail {fn(_cm_m1['Longtail'][0])}% &nbsp;·&nbsp; Mature {fn(_cm_m1['Mature'][0])}% &nbsp;·&nbsp; Meli Pro {fn(_cm_m1['Meli Pro'][0])}% &nbsp;·&nbsp; FBM {fn(_cm_m1['FBM'][0])}% &nbsp;·&nbsp; Buyers {fn(_cm_m1['Buyers'][0])}% &nbsp;·&nbsp; Otros CV {fn(_cm_m1['Otros CV'][0])}%"])
    + _bullet("↑",_LG,_GREEN,
            "Meli Pro", _GREEN,
            f"NPS {fn(_cm_m2['Meli Pro'][0])}% (Mar) → {fn(_cm_m1['Meli Pro'][0])}% (Abr) | surveys: {fi(_cm_m2['Meli Pro'][1])} → {fi(_cm_m1['Meli Pro'][1])} | +{fn(round(_cm_m1['Meli Pro'][0]-_cm_m2['Meli Pro'][0],2))} pp",
            "Por que subiu:", _GREEN, "rgba(0,166,80,.08)",
            "Volume Meli Pro cresceu 280% em Abril (239→909 surveys): sellers Meli Pro passaram a acionar o suporte com muito mais frequência, e o NPS elevado confirma qualidade do atendimento. PCF Meli Pro cresceu de 44→240 surveys com NPS 54,55%→62,92% — atendentes técnicos como Lucas resolvem mediações complexas de Full no 1º contato (#449408844).",
            [f"Post Venta Meli Pro: {fn(nps(*monthly_driver['Post Venta Meli Pro']['M2']))}% (Mar) → {fn(nps(*monthly_driver['Post Venta Meli Pro']['M1']))}% (Abr) | +{fn(round(nps(*monthly_driver['Post Venta Meli Pro']['M1'])-nps(*monthly_driver['Post Venta Meli Pro']['M2']),2))} pp, {fi(monthly_driver['Post Venta Meli Pro']['M1'][2])} surveys — exclusão de impacto de reputação com FCR é o driver dominante.",
             f"Publicaciones Meli Pro: {fn(nps(*monthly_driver['Publicaciones Meli Pro']['M2']))}% → {fn(nps(*monthly_driver['Publicaciones Meli Pro']['M1']))}% | volume {monthly_driver['Publicaciones Meli Pro']['M2'][2]}→{monthly_driver['Publicaciones Meli Pro']['M1'][2]} surveys — crescimento acelerado com NPS alto indica expansão do segmento.",
             "Empatia como NPS 10 mesmo sem ferramentas: 'A atendente foi ótima. Espero que desta vez o caso seja avaliado pela equipe de mediação' (#450128941) — acolhimento gera promotor mesmo quando a resolução depende de equipe interna."])
    + _bullet("↑","rgba(0,166,80,.06)",_GREEN,
            "FBM", _GREEN,
            f"NPS {fn(_cm_m2['FBM'][0])}% (Mar) → {fn(_cm_m1['FBM'][0])}% (Abr) | surveys: {fi(_cm_m2['FBM'][1])} → {fi(_cm_m1['FBM'][1])} | +{fn(round(_cm_m1['FBM'][0]-_cm_m2['FBM'][0],2))} pp",
            None, None, None, None,
            ["FBM-S Meli Pro: NPS 13,64% (Mar) → 61,54% (Abr) — forte recuperação no menor segmento FBM.",
             "FBM-S Seller Dev: NPS 42,37% → 44,69% (+2,32 pp) com 524→414 surveys — volume reduzido mas manutenção de NPS positivo."])
    + _bullet("↓","var(--light-red)",_RED,
            "Otros CV", _RED,
            f"NPS {fn(_cm_m2['Otros CV'][0])}% (Mar) → {fn(_cm_m1['Otros CV'][0])}% (Abr) | {fi(_cm_m1['Otros CV'][1])} surveys | {fn(round(_cm_m1['Otros CV'][0]-_cm_m2['Otros CV'][0],2))} pp",
            "Por que caiu:", _RED, _LR,
            "Queda de −10,23 pp é a maior da gerência no mês: KYC Services concentra o volume de Otros CV com challenge ativado sem aviso, recusado sem feedback específico e representante legal com informações contraditórias entre atendentes.",
            ["Challenge KYC dominante: 'KYC Services: proceso de verificação de identidade sem clareza gera loop de recontatos — cada atendente informa uma coisa diferente' (#449734598, #450841895).",
             "Padrão mensal: Marzo 56,64% → Abril 46,41% (−10,23 pp) — deterioração acelerada, sem melhora com as ações de curto prazo.",
             "Ação prioritária: comunicação proativa 72h antes de ativar challenge + padronização do fluxo KYC entre atendentes."])
    + _bullet("⚠","#FF773322",_ORA,
            f"Buyers &nbsp;<span style='font-size:11px;color:#888;font-weight:400;'>· NPS {fn(_cm_m1['Buyers'][0])}% · abaixo do target cronicamente · +{fn(round(_cm_m1['Buyers'][0]-_cm_m2['Buyers'][0],2))} pp MoM</span>",
            _ORA,
            f"NPS {fn(_cm_m2['Buyers'][0])}% (Mar) → {fn(_cm_m1['Buyers'][0])}% (Abr) | {fi(_cm_m1['Buyers'][1])} surveys",
            "Por que está abaixo do target:", _ORA, _LO,
            "Buyers é a categoria cronicamente mais baixa da gerência (~27%) puxada por mediações automáticas (PDD DS&XD: 11,39%, PDD FBM: 26,72%, PNR ME: 22,77%, PNR MP: 32,72%) onde o vendedor perde sem análise humana das evidências.",
            [f"PDD FBM: {fn(nps(*monthly_driver['PDD FBM - Vendedor']['M2']))}% (Mar) → {fn(nps(*monthly_driver['PDD FBM - Vendedor']['M1']))}% (Abr) | queda de −7,27 pp — maior deterioração mensal da categoria Buyers.",
             "CBT: {fn(nps(*monthly_driver['CBT']['M2']))}% (Mar) → {fn(nps(*monthly_driver['CBT']['M1']))}% (Abr) | melhora de +5,06 pp mas ainda −2,48 pp vs target de 74,63% — reembolsos automáticos CBT sem consultar compradores.",
             "Ação prioritária: checkpoint humano antes de fallo automático em PDD FBM + revisão de critérios CBT cross-border."])
)

exec_mes_ac_bullets = (
    f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);'
    f'border-left:4px solid var(--yellow);padding:18px 24px;margin-top:14px;">'
    f'<div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;'
    f'color:#888;margin-bottom:4px;">Análise por Categoria — Transcrições + Comentários</div>'
    f'<div style="font-size:12px;color:#bbb;margin-bottom:12px;">{M2_LABEL} → {M1_LABEL}</div>'
    + _mes_bullets +
    f'</div>'
)
exec_mes_ac += exec_mes_ac_bullets

tab_sem_ac = tab_content(
    "sem_ac", cat_nS1, cat_sS1, f"S1 ({S1_LABEL})", cat_dW, cat_nS2, cat_sS2, f"S2 ({S2_LABEL})",
    cat_wD, cons_html=cons_sem_ac, hist_table=htbl_sem_ac,
    summary_right=wf_sem_chart, rich_summary=exec_sem_ac
)
tab_mes_ac = tab_content(
    "mes_ac", cat_nM1, cat_sM1, M1_LABEL, cat_dM, cat_nM2, cat_sM2, M2_LABEL,
    cat_mD, cons_html=cons_mes_ac, hist_table=htbl_mes_ac,
    summary_right=wf_mac_chart, rich_summary=exec_mes_ac
)

# ═══════════════════════════════════════════════════════════════
# SECTION 6: CSS + HTML
# ═══════════════════════════════════════════════════════════════
CSS = """:root{--yellow:#FFE600;--dark:#1a1a2e;--gray:#f5f5f5;--border:#e0e0e0;--green:#00a650;--red:#e84142;--blue:#3483fa;--text:#333;--light-green:#e6f7ee;--light-red:#fdecea;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Proxima Nova',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:var(--text);font-size:14px;}
.header{background:var(--dark);color:#fff;padding:24px 40px;display:flex;align-items:center;justify-content:space-between;}
.header-left h1{font-size:22px;font-weight:800;letter-spacing:-.3px;}
.header-left p{font-size:13px;color:#aaa;margin-top:4px;}
.header-badge{background:var(--yellow);color:#000;font-weight:700;font-size:12px;padding:6px 14px;border-radius:20px;}
.container{max-width:1400px;margin:0 auto;padding:28px 24px 60px;}
.tabs{display:flex;gap:4px;border-bottom:3px solid var(--border);margin-bottom:28px;}
.tab-btn{padding:13px 32px;border:none;background:#fff;font-size:14px;font-weight:700;color:#999;cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-3px;border-radius:8px 8px 0 0;transition:all .15s;border:1px solid var(--border);border-bottom:3px solid transparent;}
.tab-btn.active{color:var(--dark);border-bottom-color:var(--yellow);background:#fff;border-color:var(--border);border-bottom-color:var(--yellow);}
.tab-btn:hover:not(.active){color:var(--dark);background:#f5f5f5;}
.tab-badge{display:inline-block;margin-left:8px;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;}
.tab-content{display:none;}.tab-content.active{display:block;}
.section-title{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#888;margin:32px 0 14px;border-left:3px solid var(--yellow);padding-left:10px;}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px;}
.kpi-card{background:#fff;border-radius:10px;padding:18px 20px;border:1px solid var(--border);}
.kpi-card .label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;color:#999;margin-bottom:6px;}
.kpi-card .value{font-size:28px;font-weight:800;line-height:1;}
.kpi-card .sub{font-size:12px;color:#888;margin-top:6px;}
.kpi-card .delta{display:inline-flex;align-items:center;gap:4px;font-size:13px;font-weight:700;margin-top:6px;}
.pos{color:var(--green);}.neg{color:var(--red);}
.summary-box{background:#fff;border-radius:10px;border:1px solid var(--border);padding:24px 28px;margin-bottom:24px;}
.summary-header{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:18px;}
.summary-title{font-size:17px;font-weight:800;color:var(--dark);}
.summary-sub{font-size:13px;color:#888;margin-top:3px;}
.nps-badge{font-weight:800;font-size:15px;padding:6px 16px;border-radius:8px;}
.divider{border:none;border-top:1px solid var(--border);margin-bottom:18px;}
.summary-text{font-size:13px;color:#444;line-height:1.6;margin-bottom:14px;}
.card{background:#fff;border-radius:10px;border:1px solid var(--border);overflow:hidden;margin-bottom:14px;}
.card-header{padding:14px 18px;border-bottom:1px solid var(--border);font-weight:700;font-size:14px;display:flex;align-items:center;gap:10px;}
.badge{background:var(--gray);color:#666;font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;}
table{width:100%;border-collapse:collapse;}
th{background:#fafafa;padding:9px 14px;text-align:right;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:#888;border-bottom:1px solid var(--border);}
th:first-child{text-align:left;}
td{padding:9px 14px;text-align:right;border-bottom:1px solid #f5f5f5;font-size:13px;}
td:first-child{text-align:left;font-weight:600;}
tr:last-child td{border-bottom:none;}
tr.total-row td{background:#fafafa;font-weight:700;border-top:2px solid var(--border);}
tr:hover td{background:#fafbff;}
.chip{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;}
.chip-pos{background:var(--light-green);color:var(--green);}
.chip-neg{background:var(--light-red);color:var(--red);}
.chip-neu{background:#f5f5f5;color:#888;}
.vigente-banner{background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;border-radius:10px;padding:16px 22px;margin-bottom:20px;}
.cat-filter-bar{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:22px;}
.cat-btn{padding:5px 16px;border:2px solid #ddd;background:#fff;font-size:12px;font-weight:700;color:#666;cursor:pointer;border-radius:20px;transition:all .15s;line-height:1.4;}
.cat-btn:hover{border-color:var(--cat-clr,var(--dark));color:var(--cat-clr,var(--dark));}
.cat-btn.active{background:var(--cat-clr,var(--dark));color:#fff;border-color:var(--cat-clr,var(--dark));}
.cat-view{display:block;}
.deep-dive-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px;margin-bottom:14px;}
.deep-dive-card{border-radius:10px;border:1px solid var(--border);overflow:hidden;}
.deep-dive-card-pos{border-top:4px solid var(--green);}
.deep-dive-card-neg{border-top:4px solid var(--red);}
.deep-dive-header{padding:14px 18px;border-bottom:1px solid var(--border);background:#fff;}
.dd-title{font-weight:800;font-size:14px;margin-bottom:4px;}
.dd-proc{font-size:12px;color:#666;margin-top:2px;}
.deep-dive-body{padding:14px 18px;background:#fff;}
.deep-dive-body ul{list-style:none;padding:0;}
.deep-dive-body ul li{font-size:12px;color:#444;line-height:1.6;padding:6px 0 6px 16px;border-bottom:1px solid #f5f5f5;position:relative;}
.deep-dive-body ul li:last-child{border-bottom:none;}
.deep-dive-body ul li::before{content:"•";position:absolute;left:0;font-weight:700;}
.pos-li::before{color:var(--green)!important;}
.neg-li::before{color:var(--red)!important;}
"""

def tab_btn(tab_id, label, delta):
    badge_cls = "background:var(--light-green);color:var(--green)" if delta>=0 else "background:var(--light-red);color:var(--red)"
    sign = "+" if delta>=0 else ""
    return (
        f'<button class="tab-btn" id="btn-{tab_id}" onclick="showTab(\'{tab_id}\')">'
        f'{label}'
        f'<span class="tab-badge" style="{badge_cls};">{sign}{fn(delta)} pp</span>'
        f'</button>'
    )

tabs_nav = (
    f'<div class="tabs">'
    + tab_btn("fechada",  "Semana Fechada",    dW)
    + tab_btn("vigente",  "Semana Atual",      dVW)
    + tab_btn("mensal",   "Mensal",            dM)
    + tab_btn("sem_ac",   "Semanal Acumulado", cat_dW)
    + tab_btn("mes_ac",   "Mensal Acumulado",  cat_dM)
    + f'</div>'
)

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>NPS Gerência Sellers BR — {REPORT_DATE}</title>
<style>{CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<script>Chart.register(ChartDataLabels);</script>
</head>
<body>
<div class="header">
  <div class="header-left">
    <h1>NPS Gerência — Sellers Brasil</h1>
    <p>Fechada: {S1_LABEL} · Vigente: {VIG_LABEL} · {M1_LABEL} · CENTER=BR · MP_ON_FLAG=E-Commerce · QUE_QUEUE_TYPE=VALID_CS · NPS_TARGET_DRIVER_GROUP=Sellers</p>
  </div>
  <div class="header-badge" style="text-align:right;line-height:1.4;">
    <div style="font-size:10px;font-weight:600;opacity:.8;letter-spacing:.3px;">Última atualização</div>
    <div>{REPORT_TIME} | {REPORT_DATE}</div>
  </div>
</div>
<div class="container">
{tabs_nav}
{tab_sf}
{tab_va}
{tab_mes}
{tab_sem_ac}
{tab_mes_ac}
</div>
<script>
function showTab(name) {{
  document.querySelectorAll('.tab-content').forEach(function(el) {{ el.classList.remove('active'); }});
  document.querySelectorAll('.tab-btn').forEach(function(el) {{ el.classList.remove('active'); }});
  document.getElementById('tab-' + name).classList.add('active');
  document.getElementById('btn-' + name).classList.add('active');
}}
function selectCat(tabId, cat, btn) {{
  document.querySelectorAll('#tab-' + tabId + ' .cat-view').forEach(function(el) {{
    el.style.display = 'none';
  }});
  var target = document.getElementById('tab-' + tabId + '-cat-' + cat);
  if (target) target.style.display = 'block';
  document.querySelectorAll('#tab-' + tabId + ' .cat-btn').forEach(function(b) {{
    b.classList.remove('active');
  }});
  if (btn) btn.classList.add('active');
}}
document.getElementById('btn-fechada').classList.add('active');
document.getElementById('tab-fechada').classList.add('active');
</script>
</body>
</html>"""

OUTPUT = r"c:\Users\allabriola\PROJETO CLAUDINHO\nps_gerencia_sellers_br.html"
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

import subprocess, shutil, os, tempfile

GITHUB_REPO = "https://github.com/allabriola/nps-driver-all-seller.git"
try:
    tmp = tempfile.mkdtemp()
    subprocess.run(["git","clone","--depth=1",GITHUB_REPO,tmp], check=True, capture_output=True)
    shutil.copy(OUTPUT, os.path.join(tmp,"nps_gerencia_sellers_br.html"))
    subprocess.run(["git","-C",tmp,"add","nps_gerencia_sellers_br.html"], check=True)
    subprocess.run(["git","-C",tmp,"-c","user.email=andre.labriola@mercadolivre.com",
                    "-c","user.name=Andre Labriola",
                    "commit","-m",f"Atualiza NPS Gerencia Sellers BR — {REPORT_DATE}"], check=True)
    subprocess.run(["git","-C",tmp,"push","origin","main"], check=True, capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"GitHub Pages: OK -> https://allabriola.github.io/nps-driver-all-seller/nps_gerencia_sellers_br.html")
except Exception as e:
    print(f"GitHub Pages: erro -> {e}")

print(f"HTML: {OUTPUT}")
print(f"S1={fn(nS1)} ({'+' if dW>=0 else ''}{fn(dW)}pp) | {M1_LABEL[:3]}={fn(nM1)} ({'+' if dM>=0 else ''}{fn(dM)}pp)")
