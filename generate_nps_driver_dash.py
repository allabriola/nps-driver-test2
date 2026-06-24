#!/usr/bin/env python3
"""
Dashboard NPS Driver BR — Todos os Times (Seller Dev, Mature, Meli Pro, FBM)
Gerado automaticamente pelo skill /metrics-cx:nps-driver-br-dash
"""

import json

# ============================================================
# SECTION 1 — Metadata (atualizado pelo skill)
# ============================================================
M1_LABEL = "April 2026"
M2_LABEL = "March 2026"
S1_LABEL = "06-10 Apr 2026"
S2_LABEL = "30 Mar - 05 Apr 2026"

# ============================================================
# SECTION 2 — Dados mensais por driver (atualizado pelo skill)
# Formato: {"driver": str, "team_type": str,
#            "p_m1": int, "d_m1": int, "s_m1": int,
#            "p_m2": int, "d_m2": int, "s_m2": int}
# ============================================================
MONTHLY_DRIVERS = [
    {
        "driver": "Experiencia Impositiva Mature",
        "team_type": "Mature",
        "p_m1": 15,
        "d_m1": 4,
        "s_m1": 22,
        "p_m2": 45,
        "d_m2": 20,
        "s_m2": 72
    },
    {
        "driver": "Experiencia Impositiva Meli Pro",
        "team_type": "Meli Pro",
        "p_m1": 3,
        "d_m1": 0,
        "s_m1": 4,
        "p_m2": 8,
        "d_m2": 4,
        "s_m2": 13
    },
    {
        "driver": "Experiencia Impositiva Seller Dev",
        "team_type": "Seller Dev",
        "p_m1": 163,
        "d_m1": 45,
        "s_m1": 227,
        "p_m2": 312,
        "d_m2": 108,
        "s_m2": 469
    },
    {
        "driver": "FBM-S Mature",
        "team_type": "FBM",
        "p_m1": 43,
        "d_m1": 15,
        "s_m1": 63,
        "p_m2": 130,
        "d_m2": 45,
        "s_m2": 203
    },
    {
        "driver": "FBM-S Meli Pro",
        "team_type": "FBM",
        "p_m1": 8,
        "d_m1": 1,
        "s_m1": 9,
        "p_m2": 11,
        "d_m2": 8,
        "s_m2": 22
    },
    {
        "driver": "FBM-S Seller Dev",
        "team_type": "FBM",
        "p_m1": 110,
        "d_m1": 36,
        "s_m1": 164,
        "p_m2": 347,
        "d_m2": 125,
        "s_m2": 524
    },
    {
        "driver": "ME Vendedor Mature",
        "team_type": "Mature",
        "p_m1": 502,
        "d_m1": 84,
        "s_m1": 634,
        "p_m2": 1618,
        "d_m2": 314,
        "s_m2": 2184
    },
    {
        "driver": "ME Vendedor Meli Pro",
        "team_type": "Meli Pro",
        "p_m1": 24,
        "d_m1": 6,
        "s_m1": 30,
        "p_m2": 60,
        "d_m2": 10,
        "s_m2": 75
    },
    {
        "driver": "ME Vendedor Seller Dev",
        "team_type": "Seller Dev",
        "p_m1": 1940,
        "d_m1": 274,
        "s_m1": 2448,
        "p_m2": 4958,
        "d_m2": 754,
        "s_m2": 6266
    },
    {
        "driver": "PCF Vendedor Mature",
        "team_type": "Mature",
        "p_m1": 123,
        "d_m1": 30,
        "s_m1": 165,
        "p_m2": 332,
        "d_m2": 85,
        "s_m2": 467
    },
    {
        "driver": "PCF Vendedor Meli Pro",
        "team_type": "Meli Pro",
        "p_m1": 12,
        "d_m1": 3,
        "s_m1": 18,
        "p_m2": 32,
        "d_m2": 8,
        "s_m2": 44
    },
    {
        "driver": "PCF Vendedor Seller Dev",
        "team_type": "Seller Dev",
        "p_m1": 118,
        "d_m1": 27,
        "s_m1": 162,
        "p_m2": 536,
        "d_m2": 166,
        "s_m2": 790
    },
    {
        "driver": "Partners",
        "team_type": "Seller Dev",
        "p_m1": 593,
        "d_m1": 98,
        "s_m1": 765,
        "p_m2": 2228,
        "d_m2": 337,
        "s_m2": 2806
    },
    {
        "driver": "Post Venta Mature",
        "team_type": "Mature",
        "p_m1": 120,
        "d_m1": 28,
        "s_m1": 161,
        "p_m2": 392,
        "d_m2": 76,
        "s_m2": 520
    },
    {
        "driver": "Post Venta Meli Pro",
        "team_type": "Meli Pro",
        "p_m1": 26,
        "d_m1": 2,
        "s_m1": 31,
        "p_m2": 70,
        "d_m2": 10,
        "s_m2": 81
    },
    {
        "driver": "Post Venta Seller Dev",
        "team_type": "Seller Dev",
        "p_m1": 271,
        "d_m1": 54,
        "s_m1": 354,
        "p_m2": 929,
        "d_m2": 178,
        "s_m2": 1186
    },
    {
        "driver": "Publicaciones Mature",
        "team_type": "Mature",
        "p_m1": 90,
        "d_m1": 17,
        "s_m1": 131,
        "p_m2": 258,
        "d_m2": 51,
        "s_m2": 345
    },
    {
        "driver": "Publicaciones Meli Pro",
        "team_type": "Meli Pro",
        "p_m1": 7,
        "d_m1": 1,
        "s_m1": 9,
        "p_m2": 18,
        "d_m2": 7,
        "s_m2": 26
    },
    {
        "driver": "Publicaciones Seller Dev",
        "team_type": "Seller Dev",
        "p_m1": 712,
        "d_m1": 119,
        "s_m1": 911,
        "p_m2": 2639,
        "d_m2": 374,
        "s_m2": 3309
    }
]

# ============================================================
# SECTION 3 — Dados semanais por driver (atualizado pelo skill)
# Formato: {"driver": str, "team_type": str,
#            "p_s1": int, "d_s1": int, "s_s1": int,
#            "p_s2": int, "d_s2": int, "s_s2": int}
# ============================================================
WEEKLY_DRIVERS = [
    {
        "driver": "Experiencia Impositiva Mature",
        "team_type": "Mature",
        "p_s1": 9,
        "d_s1": 2,
        "s_s1": 12,
        "p_s2": 12,
        "d_s2": 5,
        "s_s2": 20
    },
    {
        "driver": "Experiencia Impositiva Meli Pro",
        "team_type": "Meli Pro",
        "p_s1": 1,
        "d_s1": 0,
        "s_s1": 2,
        "p_s2": 2,
        "d_s2": 1,
        "s_s2": 3
    },
    {
        "driver": "Experiencia Impositiva Seller Dev",
        "team_type": "Seller Dev",
        "p_s1": 118,
        "d_s1": 31,
        "s_s1": 164,
        "p_s2": 66,
        "d_s2": 25,
        "s_s2": 100
    },
    {
        "driver": "FBM-S Mature",
        "team_type": "FBM",
        "p_s1": 24,
        "d_s1": 5,
        "s_s1": 33,
        "p_s2": 30,
        "d_s2": 13,
        "s_s2": 48
    },
    {
        "driver": "FBM-S Meli Pro",
        "team_type": "FBM",
        "p_s1": 8,
        "d_s1": 1,
        "s_s1": 9,
        "p_s2": 0,
        "d_s2": 2,
        "s_s2": 2
    },
    {
        "driver": "FBM-S Seller Dev",
        "team_type": "FBM",
        "p_s1": 57,
        "d_s1": 18,
        "s_s1": 87,
        "p_s2": 73,
        "d_s2": 23,
        "s_s2": 104
    },
    {
        "driver": "ME Vendedor Mature",
        "team_type": "Mature",
        "p_s1": 328,
        "d_s1": 60,
        "s_s1": 418,
        "p_s2": 340,
        "d_s2": 56,
        "s_s2": 438
    },
    {
        "driver": "ME Vendedor Meli Pro",
        "team_type": "Meli Pro",
        "p_s1": 18,
        "d_s1": 4,
        "s_s1": 22,
        "p_s2": 10,
        "d_s2": 6,
        "s_s2": 17
    },
    {
        "driver": "ME Vendedor Seller Dev",
        "team_type": "Seller Dev",
        "p_s1": 1326,
        "d_s1": 186,
        "s_s1": 1690,
        "p_s2": 1016,
        "d_s2": 158,
        "s_s2": 1270
    },
    {
        "driver": "PCF Vendedor Mature",
        "team_type": "Mature",
        "p_s1": 90,
        "d_s1": 20,
        "s_s1": 117,
        "p_s2": 68,
        "d_s2": 14,
        "s_s2": 91
    },
    {
        "driver": "PCF Vendedor Meli Pro",
        "team_type": "Meli Pro",
        "p_s1": 12,
        "d_s1": 2,
        "s_s1": 17,
        "p_s2": 4,
        "d_s2": 3,
        "s_s2": 7
    },
    {
        "driver": "PCF Vendedor Seller Dev",
        "team_type": "Seller Dev",
        "p_s1": 69,
        "d_s1": 21,
        "s_s1": 98,
        "p_s2": 84,
        "d_s2": 23,
        "s_s2": 125
    },
    {
        "driver": "Partners",
        "team_type": "Seller Dev",
        "p_s1": 328,
        "d_s1": 57,
        "s_s1": 427,
        "p_s2": 448,
        "d_s2": 77,
        "s_s2": 574
    },
    {
        "driver": "Post Venta Mature",
        "team_type": "Mature",
        "p_s1": 72,
        "d_s1": 15,
        "s_s1": 98,
        "p_s2": 88,
        "d_s2": 20,
        "s_s2": 114
    },
    {
        "driver": "Post Venta Meli Pro",
        "team_type": "Meli Pro",
        "p_s1": 22,
        "d_s1": 2,
        "s_s1": 26,
        "p_s2": 8,
        "d_s2": 0,
        "s_s2": 9
    },
    {
        "driver": "Post Venta Seller Dev",
        "team_type": "Seller Dev",
        "p_s1": 172,
        "d_s1": 35,
        "s_s1": 223,
        "p_s2": 176,
        "d_s2": 39,
        "s_s2": 233
    },
    {
        "driver": "Publicaciones Mature",
        "team_type": "Mature",
        "p_s1": 57,
        "d_s1": 11,
        "s_s1": 84,
        "p_s2": 61,
        "d_s2": 13,
        "s_s2": 87
    },
    {
        "driver": "Publicaciones Meli Pro",
        "team_type": "Meli Pro",
        "p_s1": 5,
        "d_s1": 0,
        "s_s1": 6,
        "p_s2": 6,
        "d_s2": 1,
        "s_s2": 8
    },
    {
        "driver": "Publicaciones Seller Dev",
        "team_type": "Seller Dev",
        "p_s1": 405,
        "d_s1": 67,
        "s_s1": 511,
        "p_s2": 502,
        "d_s2": 88,
        "s_s2": 653
    }
]

# ============================================================
# SECTION 4 — Registry de processos (atualizado pelo skill)
#
# Keyed by period_type ("monthly" / "weekly") e depois por
# team_filter ("all", "Seller Dev", "Mature", "Meli Pro", "FBM").
#
# best_curr / best_prev / worst_curr / worst_prev sao listas de
# {"process": str, "promoters": int, "detractors": int, "surveys": int}
# onde curr = periodo mais recente (M1 ou S1) e prev = anterior (M2 ou S2).
# ============================================================
PROC_REGISTRY = {
    "monthly": {
        "all": {
            "best_driver": "FBM-S Meli Pro",
            "worst_driver": "ME Vendedor Meli Pro",
            "best_curr": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 3,
                    "detractors": 0,
                    "surveys": 3
                },
                {
                    "process": "FBM - Inventario",
                    "promoters": 2,
                    "detractors": 1,
                    "surveys": 3
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "best_prev": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 4,
                    "detractors": 1,
                    "surveys": 7
                },
                {
                    "process": "FBM - Post Inbound",
                    "promoters": 1,
                    "detractors": 2,
                    "surveys": 4
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 1,
                    "detractors": 2,
                    "surveys": 3
                },
                {
                    "process": "FBM - Inventario",
                    "promoters": 1,
                    "detractors": 2,
                    "surveys": 3
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                },
                {
                    "process": "FBM - Retiro de Stock - Cx One",
                    "promoters": 1,
                    "detractors": 1,
                    "surveys": 2
                },
                {
                    "process": "FBM - Outbound",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "worst_curr": [
                {
                    "process": "Reputación ME",
                    "promoters": 10,
                    "detractors": 1,
                    "surveys": 11
                },
                {
                    "process": "Despacho Ventas y Publicaciones",
                    "promoters": 8,
                    "detractors": 1,
                    "surveys": 9
                },
                {
                    "process": "Reversa",
                    "promoters": 2,
                    "detractors": 3,
                    "surveys": 5
                },
                {
                    "process": "Gestiones Operativas",
                    "promoters": 2,
                    "detractors": 1,
                    "surveys": 3
                },
                {
                    "process": "Viaje del paquete - Vendedor",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                }
            ],
            "worst_prev": [
                {
                    "process": "Reputación ME",
                    "promoters": 29,
                    "detractors": 5,
                    "surveys": 35
                },
                {
                    "process": "Despacho Ventas y Publicaciones",
                    "promoters": 7,
                    "detractors": 3,
                    "surveys": 13
                },
                {
                    "process": "Reversa",
                    "promoters": 11,
                    "detractors": 1,
                    "surveys": 12
                },
                {
                    "process": "Gestiones Operativas",
                    "promoters": 7,
                    "detractors": 1,
                    "surveys": 8
                },
                {
                    "process": "Viaje del paquete - Vendedor",
                    "promoters": 6,
                    "detractors": 0,
                    "surveys": 7
                }
            ]
        },
        "Seller Dev": {
            "best_driver": "PCF Vendedor Seller Dev",
            "worst_driver": "Publicaciones Seller Dev",
            "best_curr": [
                {
                    "process": "Post Compra Funcionalidades Vendedor",
                    "promoters": 118,
                    "detractors": 27,
                    "surveys": 162
                }
            ],
            "best_prev": [
                {
                    "process": "Post Compra Funcionalidades Vendedor",
                    "promoters": 536,
                    "detractors": 166,
                    "surveys": 790
                }
            ],
            "worst_curr": [
                {
                    "process": "Afiliados ML",
                    "promoters": 343,
                    "detractors": 47,
                    "surveys": 429
                },
                {
                    "process": "Gestión de Publicación",
                    "promoters": 73,
                    "detractors": 11,
                    "surveys": 92
                },
                {
                    "process": "PR - Técnica prohibida",
                    "promoters": 75,
                    "detractors": 9,
                    "surveys": 90
                },
                {
                    "process": "PR - Propiedad intelectual",
                    "promoters": 58,
                    "detractors": 16,
                    "surveys": 76
                },
                {
                    "process": "Potenciar Ventas",
                    "promoters": 47,
                    "detractors": 12,
                    "surveys": 69
                },
                {
                    "process": "Antes de publicar",
                    "promoters": 47,
                    "detractors": 4,
                    "surveys": 60
                },
                {
                    "process": "PR - Artículos prohibidos",
                    "promoters": 36,
                    "detractors": 10,
                    "surveys": 48
                },
                {
                    "process": "Denuncia de usuario",
                    "promoters": 24,
                    "detractors": 3,
                    "surveys": 30
                },
                {
                    "process": "Calidad de foto",
                    "promoters": 6,
                    "detractors": 3,
                    "surveys": 10
                },
                {
                    "process": "PR - Datos Personales",
                    "promoters": 3,
                    "detractors": 4,
                    "surveys": 7
                }
            ],
            "worst_prev": [
                {
                    "process": "Afiliados ML",
                    "promoters": 1362,
                    "detractors": 180,
                    "surveys": 1687
                },
                {
                    "process": "PR - Técnica prohibida",
                    "promoters": 235,
                    "detractors": 25,
                    "surveys": 286
                },
                {
                    "process": "Gestión de Publicación",
                    "promoters": 213,
                    "detractors": 39,
                    "surveys": 284
                },
                {
                    "process": "Antes de publicar",
                    "promoters": 219,
                    "detractors": 19,
                    "surveys": 267
                },
                {
                    "process": "Potenciar Ventas",
                    "promoters": 196,
                    "detractors": 43,
                    "surveys": 265
                },
                {
                    "process": "PR - Propiedad intelectual",
                    "promoters": 198,
                    "detractors": 25,
                    "surveys": 235
                },
                {
                    "process": "PR - Artículos prohibidos",
                    "promoters": 77,
                    "detractors": 25,
                    "surveys": 113
                },
                {
                    "process": "Denuncia de usuario",
                    "promoters": 85,
                    "detractors": 12,
                    "surveys": 109
                },
                {
                    "process": "Calidad de foto",
                    "promoters": 43,
                    "detractors": 2,
                    "surveys": 47
                },
                {
                    "process": "PR - Datos Personales",
                    "promoters": 11,
                    "detractors": 4,
                    "surveys": 15
                },
                {
                    "process": "Asignación del Contáctanos - Prustomer",
                    "promoters": 0,
                    "detractors": 0,
                    "surveys": 1
                }
            ]
        },
        "Mature": {
            "best_driver": "Experiencia Impositiva Mature",
            "worst_driver": "Publicaciones Mature",
            "best_curr": [
                {
                    "process": "Emision de Nota Fiscal",
                    "promoters": 11,
                    "detractors": 3,
                    "surveys": 16
                },
                {
                    "process": "Facturación",
                    "promoters": 3,
                    "detractors": 1,
                    "surveys": 4
                },
                {
                    "process": "Datos fiscales",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 2
                }
            ],
            "best_prev": [
                {
                    "process": "Emision de Nota Fiscal",
                    "promoters": 24,
                    "detractors": 12,
                    "surveys": 42
                },
                {
                    "process": "Facturación",
                    "promoters": 20,
                    "detractors": 8,
                    "surveys": 29
                },
                {
                    "process": "Datos fiscales",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "worst_curr": [
                {
                    "process": "PR - Técnica prohibida",
                    "promoters": 25,
                    "detractors": 3,
                    "surveys": 33
                },
                {
                    "process": "Gestión de Publicación",
                    "promoters": 19,
                    "detractors": 3,
                    "surveys": 29
                },
                {
                    "process": "PR - Propiedad intelectual",
                    "promoters": 14,
                    "detractors": 2,
                    "surveys": 21
                },
                {
                    "process": "Potenciar Ventas",
                    "promoters": 10,
                    "detractors": 4,
                    "surveys": 18
                },
                {
                    "process": "PR - Artículos prohibidos",
                    "promoters": 10,
                    "detractors": 3,
                    "surveys": 14
                },
                {
                    "process": "Calidad de foto",
                    "promoters": 5,
                    "detractors": 0,
                    "surveys": 5
                },
                {
                    "process": "PR - Datos Personales",
                    "promoters": 3,
                    "detractors": 1,
                    "surveys": 5
                },
                {
                    "process": "Antes de publicar",
                    "promoters": 2,
                    "detractors": 1,
                    "surveys": 4
                },
                {
                    "process": "Denuncia de usuario",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                }
            ],
            "worst_prev": [
                {
                    "process": "PR - Técnica prohibida",
                    "promoters": 76,
                    "detractors": 8,
                    "surveys": 96
                },
                {
                    "process": "PR - Propiedad intelectual",
                    "promoters": 60,
                    "detractors": 10,
                    "surveys": 76
                },
                {
                    "process": "Gestión de Publicación",
                    "promoters": 48,
                    "detractors": 16,
                    "surveys": 72
                },
                {
                    "process": "Potenciar Ventas",
                    "promoters": 37,
                    "detractors": 9,
                    "surveys": 54
                },
                {
                    "process": "PR - Artículos prohibidos",
                    "promoters": 15,
                    "detractors": 1,
                    "surveys": 16
                },
                {
                    "process": "Calidad de foto",
                    "promoters": 10,
                    "detractors": 1,
                    "surveys": 13
                },
                {
                    "process": "Antes de publicar",
                    "promoters": 5,
                    "detractors": 3,
                    "surveys": 8
                },
                {
                    "process": "Denuncia de usuario",
                    "promoters": 2,
                    "detractors": 3,
                    "surveys": 5
                },
                {
                    "process": "Afiliados ML",
                    "promoters": 3,
                    "detractors": 0,
                    "surveys": 3
                },
                {
                    "process": "PR - Datos Personales",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                }
            ]
        },
        "Meli Pro": {
            "best_driver": "Experiencia Impositiva Meli Pro",
            "worst_driver": "ME Vendedor Meli Pro",
            "best_curr": [
                {
                    "process": "Facturación",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 3
                },
                {
                    "process": "Emision de Nota Fiscal",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "best_prev": [
                {
                    "process": "Facturación",
                    "promoters": 4,
                    "detractors": 3,
                    "surveys": 8
                },
                {
                    "process": "Emision de Nota Fiscal",
                    "promoters": 4,
                    "detractors": 1,
                    "surveys": 5
                }
            ],
            "worst_curr": [
                {
                    "process": "Reputación ME",
                    "promoters": 10,
                    "detractors": 1,
                    "surveys": 11
                },
                {
                    "process": "Despacho Ventas y Publicaciones",
                    "promoters": 8,
                    "detractors": 1,
                    "surveys": 9
                },
                {
                    "process": "Reversa",
                    "promoters": 2,
                    "detractors": 3,
                    "surveys": 5
                },
                {
                    "process": "Gestiones Operativas",
                    "promoters": 2,
                    "detractors": 1,
                    "surveys": 3
                },
                {
                    "process": "Viaje del paquete - Vendedor",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                }
            ],
            "worst_prev": [
                {
                    "process": "Reputación ME",
                    "promoters": 29,
                    "detractors": 5,
                    "surveys": 35
                },
                {
                    "process": "Despacho Ventas y Publicaciones",
                    "promoters": 7,
                    "detractors": 3,
                    "surveys": 13
                },
                {
                    "process": "Reversa",
                    "promoters": 11,
                    "detractors": 1,
                    "surveys": 12
                },
                {
                    "process": "Gestiones Operativas",
                    "promoters": 7,
                    "detractors": 1,
                    "surveys": 8
                },
                {
                    "process": "Viaje del paquete - Vendedor",
                    "promoters": 6,
                    "detractors": 0,
                    "surveys": 7
                }
            ]
        },
        "FBM": {
            "best_driver": "FBM-S Meli Pro",
            "worst_driver": "FBM-S Mature",
            "best_curr": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 3,
                    "detractors": 0,
                    "surveys": 3
                },
                {
                    "process": "FBM - Inventario",
                    "promoters": 2,
                    "detractors": 1,
                    "surveys": 3
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "best_prev": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 4,
                    "detractors": 1,
                    "surveys": 7
                },
                {
                    "process": "FBM - Post Inbound",
                    "promoters": 1,
                    "detractors": 2,
                    "surveys": 4
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 1,
                    "detractors": 2,
                    "surveys": 3
                },
                {
                    "process": "FBM - Inventario",
                    "promoters": 1,
                    "detractors": 2,
                    "surveys": 3
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                },
                {
                    "process": "FBM - Retiro de Stock - Cx One",
                    "promoters": 1,
                    "detractors": 1,
                    "surveys": 2
                },
                {
                    "process": "FBM - Outbound",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "worst_curr": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 17,
                    "detractors": 4,
                    "surveys": 24
                },
                {
                    "process": "FBM - Inventario",
                    "promoters": 9,
                    "detractors": 5,
                    "surveys": 16
                },
                {
                    "process": "FBM - Retiro de Stock - Cx One",
                    "promoters": 8,
                    "detractors": 2,
                    "surveys": 10
                },
                {
                    "process": "FBM - Post Inbound",
                    "promoters": 6,
                    "detractors": 4,
                    "surveys": 10
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "worst_prev": [
                {
                    "process": "FBM - Inventario",
                    "promoters": 32,
                    "detractors": 18,
                    "surveys": 60
                },
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 36,
                    "detractors": 12,
                    "surveys": 59
                },
                {
                    "process": "FBM - Post Inbound",
                    "promoters": 24,
                    "detractors": 5,
                    "surveys": 31
                },
                {
                    "process": "FBM - Retiro de Stock - Cx One",
                    "promoters": 20,
                    "detractors": 5,
                    "surveys": 30
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 7,
                    "detractors": 4,
                    "surveys": 11
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 9,
                    "detractors": 1,
                    "surveys": 10
                },
                {
                    "process": "FBM - Outbound",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                },
                {
                    "process": "Asignación del Contáctanos FBM",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ]
        }
    },
    "weekly": {
        "all": {
            "best_driver": "FBM-S Meli Pro",
            "worst_driver": "Post Venta Meli Pro",
            "best_curr": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 3,
                    "detractors": 0,
                    "surveys": 3
                },
                {
                    "process": "FBM - Inventario",
                    "promoters": 2,
                    "detractors": 1,
                    "surveys": 3
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "best_prev": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 0,
                    "detractors": 1,
                    "surveys": 1
                },
                {
                    "process": "FBM - Post Inbound",
                    "promoters": 0,
                    "detractors": 1,
                    "surveys": 1
                }
            ],
            "worst_curr": [
                {
                    "process": "Reputación",
                    "promoters": 21,
                    "detractors": 2,
                    "surveys": 25
                },
                {
                    "process": "Anulación de Venta",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "worst_prev": [
                {
                    "process": "Reputación",
                    "promoters": 8,
                    "detractors": 0,
                    "surveys": 9
                }
            ]
        },
        "Seller Dev": {
            "best_driver": "Experiencia Impositiva Seller Dev",
            "worst_driver": "Partners",
            "best_curr": [
                {
                    "process": "Emision de Nota Fiscal",
                    "promoters": 75,
                    "detractors": 21,
                    "surveys": 105
                },
                {
                    "process": "Facturación",
                    "promoters": 33,
                    "detractors": 8,
                    "surveys": 45
                },
                {
                    "process": "Datos fiscales",
                    "promoters": 10,
                    "detractors": 2,
                    "surveys": 14
                }
            ],
            "best_prev": [
                {
                    "process": "Emision de Nota Fiscal",
                    "promoters": 37,
                    "detractors": 8,
                    "surveys": 50
                },
                {
                    "process": "Facturación",
                    "promoters": 24,
                    "detractors": 14,
                    "surveys": 41
                },
                {
                    "process": "Datos fiscales",
                    "promoters": 5,
                    "detractors": 3,
                    "surveys": 9
                }
            ],
            "worst_curr": [
                {
                    "process": "Drivers",
                    "promoters": 224,
                    "detractors": 41,
                    "surveys": 299
                },
                {
                    "process": "Places Kangu",
                    "promoters": 104,
                    "detractors": 16,
                    "surveys": 128
                }
            ],
            "worst_prev": [
                {
                    "process": "Drivers",
                    "promoters": 357,
                    "detractors": 66,
                    "surveys": 466
                },
                {
                    "process": "Places Kangu",
                    "promoters": 91,
                    "detractors": 11,
                    "surveys": 108
                }
            ]
        },
        "Mature": {
            "best_driver": "Experiencia Impositiva Mature",
            "worst_driver": "Post Venta Mature",
            "best_curr": [
                {
                    "process": "Emision de Nota Fiscal",
                    "promoters": 7,
                    "detractors": 1,
                    "surveys": 9
                },
                {
                    "process": "Facturación",
                    "promoters": 1,
                    "detractors": 1,
                    "surveys": 2
                },
                {
                    "process": "Datos fiscales",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "best_prev": [
                {
                    "process": "Emision de Nota Fiscal",
                    "promoters": 7,
                    "detractors": 5,
                    "surveys": 14
                },
                {
                    "process": "Facturación",
                    "promoters": 5,
                    "detractors": 0,
                    "surveys": 5
                },
                {
                    "process": "Datos fiscales",
                    "promoters": 0,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "worst_curr": [
                {
                    "process": "Reputación",
                    "promoters": 71,
                    "detractors": 13,
                    "surveys": 95
                },
                {
                    "process": "Anulación de Venta",
                    "promoters": 1,
                    "detractors": 2,
                    "surveys": 3
                }
            ],
            "worst_prev": [
                {
                    "process": "Reputación",
                    "promoters": 88,
                    "detractors": 20,
                    "surveys": 114
                }
            ]
        },
        "Meli Pro": {
            "best_driver": "PCF Vendedor Meli Pro",
            "worst_driver": "Post Venta Meli Pro",
            "best_curr": [
                {
                    "process": "Post Compra Funcionalidades Vendedor",
                    "promoters": 12,
                    "detractors": 2,
                    "surveys": 17
                }
            ],
            "best_prev": [
                {
                    "process": "Post Compra Funcionalidades Vendedor",
                    "promoters": 4,
                    "detractors": 3,
                    "surveys": 7
                }
            ],
            "worst_curr": [
                {
                    "process": "Reputación",
                    "promoters": 21,
                    "detractors": 2,
                    "surveys": 25
                },
                {
                    "process": "Anulación de Venta",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "worst_prev": [
                {
                    "process": "Reputación",
                    "promoters": 8,
                    "detractors": 0,
                    "surveys": 9
                }
            ]
        },
        "FBM": {
            "best_driver": "FBM-S Meli Pro",
            "worst_driver": "FBM-S Seller Dev",
            "best_curr": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 3,
                    "detractors": 0,
                    "surveys": 3
                },
                {
                    "process": "FBM - Inventario",
                    "promoters": 2,
                    "detractors": 1,
                    "surveys": 3
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 2,
                    "detractors": 0,
                    "surveys": 2
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "best_prev": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 0,
                    "detractors": 1,
                    "surveys": 1
                },
                {
                    "process": "FBM - Post Inbound",
                    "promoters": 0,
                    "detractors": 1,
                    "surveys": 1
                }
            ],
            "worst_curr": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 16,
                    "detractors": 5,
                    "surveys": 24
                },
                {
                    "process": "FBM - Post Inbound",
                    "promoters": 13,
                    "detractors": 5,
                    "surveys": 20
                },
                {
                    "process": "FBM - Inventario",
                    "promoters": 11,
                    "detractors": 5,
                    "surveys": 18
                },
                {
                    "process": "FBM - Retiro de Stock - Cx One",
                    "promoters": 7,
                    "detractors": 0,
                    "surveys": 11
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 8,
                    "detractors": 1,
                    "surveys": 9
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 1,
                    "detractors": 2,
                    "surveys": 4
                },
                {
                    "process": "Asignación del Contáctanos FBM",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ],
            "worst_prev": [
                {
                    "process": "FBM - Pre Inbound",
                    "promoters": 35,
                    "detractors": 12,
                    "surveys": 51
                },
                {
                    "process": "FBM - Inventario",
                    "promoters": 11,
                    "detractors": 5,
                    "surveys": 19
                },
                {
                    "process": "FBM - Post Inbound",
                    "promoters": 11,
                    "detractors": 3,
                    "surveys": 15
                },
                {
                    "process": "FBM - Retiro de Stock - Cx One",
                    "promoters": 9,
                    "detractors": 3,
                    "surveys": 12
                },
                {
                    "process": "FBM - Funcionalidades",
                    "promoters": 3,
                    "detractors": 0,
                    "surveys": 3
                },
                {
                    "process": "FBM - Devoluciones",
                    "promoters": 3,
                    "detractors": 0,
                    "surveys": 3
                },
                {
                    "process": "FBM - Outbound",
                    "promoters": 1,
                    "detractors": 0,
                    "surveys": 1
                }
            ]
        }
    }
}


# ============================================================
# Helpers
# ============================================================
def nps(p, d, s):
    return round(100.0 * (p - d) / s, 2) if s else None


def build_driver_rows(drivers, pk1, dk1, sk1, pk2, dk2, sk2, nk1, nk2):
    rows = []
    for d in drivers:
        n1 = nps(d[pk1], d[dk1], d[sk1])
        n2 = nps(d[pk2], d[dk2], d[sk2])
        var = round(n1 - n2, 2) if n1 is not None and n2 is not None else None
        rows.append({**d, nk1: n1, nk2: n2, "var": var})
    return rows


def build_proc_data(proc_curr, proc_prev):
    """Merge process data and compute NPS + variation. Output uses curr/prev keys."""
    merged = {}
    for p in proc_curr:
        merged[p["process"]] = {
            "process": p["process"],
            "p_curr": p["promoters"], "d_curr": p["detractors"], "s_curr": p["surveys"],
        }
    for p in proc_prev:
        if p["process"] not in merged:
            merged[p["process"]] = {"process": p["process"]}
        merged[p["process"]].update({
            "p_prev": p["promoters"], "d_prev": p["detractors"], "s_prev": p["surveys"],
        })
    rows = []
    for proc, data in merged.items():
        n_curr = nps(data.get("p_curr", 0), data.get("d_curr", 0), data.get("s_curr", 0))
        n_prev = nps(data.get("p_prev", 0), data.get("d_prev", 0), data.get("s_prev", 0))
        var = round(n_curr - n_prev, 2) if n_curr is not None and n_prev is not None else None
        rows.append({
            "process": proc,
            "nps_curr": n_curr, "nps_prev": n_prev, "var": var,
            "s_curr": data.get("s_curr", 0),
        })
    return sorted(rows, key=lambda x: x["var"] if x["var"] is not None else 0, reverse=True)


def build_proc_registry_js():
    """Build serialized PROC_REGISTRY with processed proc data."""
    result = {}
    for period in ("monthly", "weekly"):
        result[period] = {}
        for team in ("all", "Seller Dev", "Mature", "Meli Pro", "FBM"):
            entry = PROC_REGISTRY[period][team]
            result[period][team] = {
                "best_driver":  entry["best_driver"],
                "worst_driver": entry["worst_driver"],
                "best_procs":   build_proc_data(entry["best_curr"], entry["best_prev"]),
                "worst_procs":  build_proc_data(entry["worst_curr"], entry["worst_prev"]),
            }
    return result


def generate_html():
    monthly_rows = build_driver_rows(
        MONTHLY_DRIVERS, "p_m1", "d_m1", "s_m1", "p_m2", "d_m2", "s_m2", "nps_m1", "nps_m2"
    )
    weekly_rows = build_driver_rows(
        WEEKLY_DRIVERS, "p_s1", "d_s1", "s_s1", "p_s2", "d_s2", "s_s2", "nps_s1", "nps_s2"
    )
    proc_reg = build_proc_registry_js()

    data_js = (
        f"const MONTHLY_DRIVERS = {json.dumps(monthly_rows)};\n"
        f"const WEEKLY_DRIVERS   = {json.dumps(weekly_rows)};\n"
        f"const PROC_REGISTRY    = {json.dumps(proc_reg)};\n"
        f"const M1_LABEL = {json.dumps(M1_LABEL)};\n"
        f"const M2_LABEL = {json.dumps(M2_LABEL)};\n"
        f"const S1_LABEL = {json.dumps(S1_LABEL)};\n"
        f"const S2_LABEL = {json.dumps(S2_LABEL)};\n"
    )

    html = HTML_TEMPLATE.replace("__DATA_JS__", data_js)
    return html


# ============================================================
# HTML Template
# ============================================================
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NPS Driver BR</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
.container { max-width: 1400px; margin: 0 auto; padding: 24px; }
h1 { font-size: 1.4rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }
.subtitle { color: #64748b; font-size: 0.82rem; margin-bottom: 20px; }

.filter-bar { display: flex; gap: 8px; margin-bottom: 28px; flex-wrap: wrap; align-items: center; }
.filter-label { color: #475569; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-right: 2px; }
.filter-btn {
  padding: 7px 20px; border-radius: 20px; border: 1px solid #334155;
  background: #1e293b; color: #94a3b8; cursor: pointer;
  font-size: 0.82rem; transition: all 0.18s;
}
.filter-btn.active { background: #3b82f6; color: #fff; border-color: #3b82f6; font-weight: 600; }
.filter-btn:hover:not(.active) { background: #273549; color: #e2e8f0; }

.section { margin-bottom: 32px; }
.section-title {
  font-size: 0.78rem; font-weight: 700; color: #64748b;
  margin-bottom: 14px; padding-bottom: 8px;
  border-bottom: 1px solid #1e293b;
  display: flex; align-items: center; gap: 8px;
  text-transform: uppercase; letter-spacing: 0.07em;
}
.period-badge {
  font-size: 0.72rem; font-weight: 500; padding: 2px 10px;
  border-radius: 10px; background: #1e293b; color: #475569;
  text-transform: none; letter-spacing: 0;
}

.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 20px; }
.card { background: #1e293b; border-radius: 12px; padding: 16px 18px; border: 1px solid #334155; }
.card-label { font-size: 0.72rem; color: #475569; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.06em; }
.card-value { font-size: 1.55rem; font-weight: 700; }
.card-sub { font-size: 0.75rem; color: #475569; margin-top: 4px; }

.table-wrap { overflow-x: auto; border-radius: 10px; border: 1px solid #1e293b; }
table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
thead th {
  background: #1e293b; color: #475569; text-align: left;
  padding: 9px 14px; font-weight: 600; font-size: 0.72rem;
  text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap;
}
tbody tr { border-bottom: 1px solid #0f172a; transition: background 0.12s; }
tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: rgba(30,41,59,0.5); }
td { padding: 9px 14px; color: #cbd5e1; white-space: nowrap; }
td.dn { font-weight: 500; color: #f1f5f9; white-space: normal; max-width: 260px; min-width: 160px; }
.empty-msg { padding: 20px; color: #475569; font-size: 0.82rem; text-align: center; }

.team-tag { display: inline-block; padding: 2px 9px; border-radius: 10px; font-size: 0.68rem; font-weight: 700; white-space: nowrap; }
.tag-sd { background: rgba(29,78,216,0.15); color: #60a5fa; border: 1px solid rgba(29,78,216,0.3); }
.tag-mt { background: rgba(146,64,14,0.15); color: #fbbf24; border: 1px solid rgba(146,64,14,0.3); }
.tag-mp { background: rgba(6,95,70,0.15); color: #34d399; border: 1px solid rgba(6,95,70,0.3); }
.tag-fb { background: rgba(76,29,149,0.15); color: #a78bfa; border: 1px solid rgba(76,29,149,0.3); }
.tag-ot { background: #1e293b; color: #64748b; border: 1px solid #334155; }

.bar-wrap { display: flex; align-items: center; gap: 8px; }
.bar { height: 6px; border-radius: 3px; min-width: 2px; }
.bar-pos { background: #22c55e; }
.bar-neg { background: #ef4444; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 860px) { .two-col { grid-template-columns: 1fr; } }
.proc-card { background: #1e293b; border-radius: 10px; border: 1px solid #334155; overflow: hidden; }
.proc-card-header { padding: 11px 16px; border-bottom: 1px solid #0f172a; font-size: 0.78rem; font-weight: 700; }
.proc-card-header.best { color: #22c55e; }
.proc-card-header.worst { color: #ef4444; }
</style>
</head>
<body>
<div class="container">
  <h1>NPS Driver BR — Dashboard</h1>
  <p class="subtitle">
    Mensal: <strong id="lbl-m1"></strong> vs <strong id="lbl-m2"></strong>
    &nbsp;·&nbsp;
    Semanal: <strong id="lbl-s1"></strong> vs <strong id="lbl-s2"></strong>
  </p>

  <div class="filter-bar">
    <span class="filter-label">Time:</span>
    <button class="filter-btn active" data-team="all">Todos</button>
    <button class="filter-btn" data-team="Seller Dev">Seller Dev</button>
    <button class="filter-btn" data-team="Mature">Mature</button>
    <button class="filter-btn" data-team="Meli Pro">Meli Pro</button>
    <button class="filter-btn" data-team="FBM">FBM</button>
  </div>

  <!-- MENSAL -->
  <div class="section">
    <div class="section-title">NPS Mensal <span class="period-badge" id="badge-m"></span></div>
    <div class="cards" id="cards-m"></div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Driver</th><th>Time</th>
          <th id="th-m1">M1</th><th id="th-m2">M2</th>
          <th>Variação</th><th>Respostas M1</th>
        </tr></thead>
        <tbody id="tb-m"></tbody>
      </table>
    </div>
  </div>

  <!-- IMPACTO MENSAL -->
  <div class="section">
    <div class="section-title">Contribuição dos Drivers — NPS Mensal</div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Driver</th><th>Time</th>
          <th>Contribuição</th><th>Impacto</th>
          <th id="th-im1">NPS M1</th><th id="th-im2">NPS M2</th><th>Variação</th>
        </tr></thead>
        <tbody id="tb-im"></tbody>
      </table>
    </div>
  </div>

  <!-- PROCESSOS MENSAIS -->
  <div class="section">
    <div class="section-title">Breakdown de Processos — Mensal</div>
    <div class="two-col">
      <div class="proc-card">
        <div class="proc-card-header best">▲ Maior alta: <span id="ph-mb"></span></div>
        <div class="table-wrap"><table>
          <thead><tr><th>Processo</th><th id="th-pb-m1">NPS M1</th><th id="th-pb-m2">NPS M2</th><th>Var.</th><th>Resp.</th></tr></thead>
          <tbody id="tb-pmb"></tbody>
        </table></div>
      </div>
      <div class="proc-card">
        <div class="proc-card-header worst">▼ Maior queda: <span id="ph-mw"></span></div>
        <div class="table-wrap"><table>
          <thead><tr><th>Processo</th><th>NPS M1</th><th>NPS M2</th><th>Var.</th><th>Resp.</th></tr></thead>
          <tbody id="tb-pmw"></tbody>
        </table></div>
      </div>
    </div>
  </div>

  <!-- SEMANAL -->
  <div class="section">
    <div class="section-title">NPS Semanal <span class="period-badge" id="badge-s"></span></div>
    <div class="cards" id="cards-s"></div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Driver</th><th>Time</th>
          <th id="th-s1">S1</th><th id="th-s2">S2</th>
          <th>Variação</th><th>Respostas S1</th>
        </tr></thead>
        <tbody id="tb-s"></tbody>
      </table>
    </div>
  </div>

  <!-- IMPACTO SEMANAL -->
  <div class="section">
    <div class="section-title">Contribuição dos Drivers — NPS Semanal</div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Driver</th><th>Time</th>
          <th>Contribuição</th><th>Impacto</th>
          <th id="th-is1">NPS S1</th><th id="th-is2">NPS S2</th><th>Variação</th>
        </tr></thead>
        <tbody id="tb-is"></tbody>
      </table>
    </div>
  </div>

  <!-- PROCESSOS SEMANAIS -->
  <div class="section">
    <div class="section-title">Breakdown de Processos — Semanal</div>
    <div class="two-col">
      <div class="proc-card">
        <div class="proc-card-header best">▲ Maior alta: <span id="ph-sb"></span></div>
        <div class="table-wrap"><table>
          <thead><tr><th>Processo</th><th id="th-pb-s1">NPS S1</th><th id="th-pb-s2">NPS S2</th><th>Var.</th><th>Resp.</th></tr></thead>
          <tbody id="tb-psb"></tbody>
        </table></div>
      </div>
      <div class="proc-card">
        <div class="proc-card-header worst">▼ Maior queda: <span id="ph-sw"></span></div>
        <div class="table-wrap"><table>
          <thead><tr><th>Processo</th><th>NPS S1</th><th>NPS S2</th><th>Var.</th><th>Resp.</th></tr></thead>
          <tbody id="tb-psw"></tbody>
        </table></div>
      </div>
    </div>
  </div>
</div>

<script>
__DATA_JS__

let currentFilter = 'all';

const F  = v => v !== null && v !== undefined ? (v > 0 ? '+' : '') + v.toFixed(1) : '—';
const VC = v => v === null || v === undefined ? '#64748b' : v > 0 ? '#22c55e' : v < 0 ? '#ef4444' : '#94a3b8';
const AR = v => v === null || v === undefined ? '' : v > 0 ? '▲ ' : v < 0 ? '▼ ' : '';
const N  = v => v !== null && v !== undefined ? v : 0;
const LOC = n => N(n).toLocaleString('pt-BR');

function teamTag(t) {
  const m = {'Seller Dev':'tag-sd','Mature':'tag-mt','Meli Pro':'tag-mp','FBM':'tag-fb'};
  return `<span class="team-tag ${m[t]||'tag-ot'}">${t}</span>`;
}
function fil(arr) {
  return currentFilter === 'all' ? arr : arr.filter(d => d.team_type === currentFilter);
}
function totals(arr, pk, dk, sk) {
  const f = fil(arr);
  const p = f.reduce((a, d) => a + N(d[pk]), 0);
  const di = f.reduce((a, d) => a + N(d[dk]), 0);
  const s  = f.reduce((a, d) => a + N(d[sk]), 0);
  return {p, d:di, s, nps: s ? 100*(p-di)/s : null};
}

function renderCards(id, n1, n2, s1, s2, l1, l2) {
  const vr = n1 !== null && n2 !== null ? n1 - n2 : null;
  document.getElementById(id).innerHTML = `
    <div class="card">
      <div class="card-label">NPS ${l1}</div>
      <div class="card-value" style="color:${VC(n1)}">${F(n1)}</div>
      <div class="card-sub">${LOC(s1)} respostas</div>
    </div>
    <div class="card">
      <div class="card-label">NPS ${l2}</div>
      <div class="card-value" style="color:${VC(n2)}">${F(n2)}</div>
      <div class="card-sub">${LOC(s2)} respostas</div>
    </div>
    <div class="card">
      <div class="card-label">Variação</div>
      <div class="card-value" style="color:${VC(vr)}">${AR(vr)}${F(vr)}</div>
      <div class="card-sub">pontos</div>
    </div>`;
}

function renderDriverTable(tbodyId, arr, nk1, nk2, sk1) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = '';
  const rows = fil(arr);
  if (!rows.length) { tbody.innerHTML = `<tr><td colspan="6" class="empty-msg">Sem dados para o filtro selecionado</td></tr>`; return; }
  rows.forEach(d => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="dn">${d.driver}</td>
      <td>${teamTag(d.team_type)}</td>
      <td style="color:${VC(d[nk1])};font-weight:600">${F(d[nk1])}</td>
      <td style="color:${VC(d[nk2])}">${F(d[nk2])}</td>
      <td style="color:${VC(d.var)};font-weight:700">${AR(d.var)}${F(d.var)}</td>
      <td style="color:#475569">${LOC(d[sk1])}</td>`;
    tbody.appendChild(tr);
  });
}

function renderImpact(tbodyId, arr, pk1, dk1, sk1, pk2, dk2, sk2, nk1, nk2) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = '';
  const f = fil(arr);
  if (!f.length) { tbody.innerHTML = `<tr><td colspan="7" class="empty-msg">Sem dados para o filtro selecionado</td></tr>`; return; }

  const ts1 = f.reduce((a, d) => a + N(d[sk1]), 0);
  const ts2 = f.reduce((a, d) => a + N(d[sk2]), 0);

  const wc = f.map(d => {
    let c = null;
    const s1 = N(d[sk1]), s2 = N(d[sk2]);
    if (ts1 && ts2 && s1 && s2) {
      const n1 = 100 * (N(d[pk1]) - N(d[dk1])) / s1;
      const n2 = 100 * (N(d[pk2]) - N(d[dk2])) / s2;
      c = Math.round((n1 * s1/ts1 - n2 * s2/ts2) * 100) / 100;
    }
    return {...d, _c: c};
  }).sort((a, b) => N(b._c) - N(a._c));

  const mx = Math.max(...wc.map(d => Math.abs(d._c || 0)), 0.01);

  wc.forEach(d => {
    const c = d._c;
    const bw = Math.round(80 * Math.abs(c || 0) / mx);
    const bc = (c || 0) >= 0 ? 'bar-pos' : 'bar-neg';
    const cs = c !== null ? (c > 0 ? '+' : '') + c.toFixed(2) + ' pts' : '—';
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="dn">${d.driver}</td>
      <td>${teamTag(d.team_type)}</td>
      <td style="color:${VC(c)};font-weight:700">${cs}</td>
      <td><div class="bar-wrap"><div class="bar ${bc}" style="width:${bw}px"></div><span style="color:${VC(c)};font-size:0.75rem;font-weight:600">&nbsp;${c !== null ? (c>=0?'+':'')+c.toFixed(2) : ''}</span></div></td>
      <td style="color:${VC(d[nk1])};font-weight:600">${F(d[nk1])}</td>
      <td style="color:${VC(d[nk2])}">${F(d[nk2])}</td>
      <td style="color:${VC(d.var)}">${AR(d.var)}${F(d.var)}</td>`;
    tbody.appendChild(tr);
  });
}

function renderProc(tbodyId, procs) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = '';
  if (!procs || !procs.length) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-msg">Sem dados de processo</td></tr>`;
    return;
  }
  procs.forEach(p => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="color:#f1f5f9;font-weight:500;white-space:normal;max-width:220px">${p.process}</td>
      <td style="color:${VC(p.nps_curr)};font-weight:600">${F(p.nps_curr)}</td>
      <td style="color:${VC(p.nps_prev)}">${F(p.nps_prev)}</td>
      <td style="color:${VC(p.var)};font-weight:700">${AR(p.var)}${F(p.var)}</td>
      <td style="color:#475569">${LOC(p.s_curr)}</td>`;
    tbody.appendChild(tr);
  });
}

function renderProcSection(period) {
  const reg = PROC_REGISTRY[period][currentFilter] || PROC_REGISTRY[period]['all'];
  if (period === 'monthly') {
    document.getElementById('ph-mb').textContent = reg.best_driver || '—';
    document.getElementById('ph-mw').textContent = reg.worst_driver || '—';
    renderProc('tb-pmb', reg.best_procs);
    renderProc('tb-pmw', reg.worst_procs);
  } else {
    document.getElementById('ph-sb').textContent = reg.best_driver || '—';
    document.getElementById('ph-sw').textContent = reg.worst_driver || '—';
    renderProc('tb-psb', reg.best_procs);
    renderProc('tb-psw', reg.worst_procs);
  }
}

function renderAll() {
  // Static labels
  document.getElementById('lbl-m1').textContent = M1_LABEL;
  document.getElementById('lbl-m2').textContent = M2_LABEL;
  document.getElementById('lbl-s1').textContent = S1_LABEL;
  document.getElementById('lbl-s2').textContent = S2_LABEL;
  document.getElementById('badge-m').textContent = M1_LABEL + ' vs ' + M2_LABEL;
  document.getElementById('badge-s').textContent = S1_LABEL + ' vs ' + S2_LABEL;
  ['th-m1','th-im1'].forEach(id => document.getElementById(id).textContent = M1_LABEL);
  ['th-m2','th-im2'].forEach(id => document.getElementById(id).textContent = M2_LABEL);
  ['th-s1','th-is1'].forEach(id => document.getElementById(id).textContent = S1_LABEL);
  ['th-s2','th-is2'].forEach(id => document.getElementById(id).textContent = S2_LABEL);
  document.getElementById('th-pb-m1').textContent = 'NPS ' + M1_LABEL;
  document.getElementById('th-pb-m2').textContent = 'NPS ' + M2_LABEL;
  document.getElementById('th-pb-s1').textContent = 'NPS ' + S1_LABEL;
  document.getElementById('th-pb-s2').textContent = 'NPS ' + S2_LABEL;

  // Monthly
  const mt1 = totals(MONTHLY_DRIVERS, 'p_m1', 'd_m1', 's_m1');
  const mt2 = totals(MONTHLY_DRIVERS, 'p_m2', 'd_m2', 's_m2');
  renderCards('cards-m', mt1.nps, mt2.nps, mt1.s, mt2.s, M1_LABEL, M2_LABEL);
  renderDriverTable('tb-m', MONTHLY_DRIVERS, 'nps_m1', 'nps_m2', 's_m1');
  renderImpact('tb-im', MONTHLY_DRIVERS, 'p_m1','d_m1','s_m1','p_m2','d_m2','s_m2','nps_m1','nps_m2');
  renderProcSection('monthly');

  // Weekly
  const wt1 = totals(WEEKLY_DRIVERS, 'p_s1', 'd_s1', 's_s1');
  const wt2 = totals(WEEKLY_DRIVERS, 'p_s2', 'd_s2', 's_s2');
  renderCards('cards-s', wt1.nps, wt2.nps, wt1.s, wt2.s, S1_LABEL, S2_LABEL);
  renderDriverTable('tb-s', WEEKLY_DRIVERS, 'nps_s1', 'nps_s2', 's_s1');
  renderImpact('tb-is', WEEKLY_DRIVERS, 'p_s1','d_s1','s_s1','p_s2','d_s2','s_s2','nps_s1','nps_s2');
  renderProcSection('weekly');
}

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.team;
    renderAll();
  });
});

renderAll();
</script>
</body>
</html>"""


if __name__ == "__main__":
    html = generate_html()
    out = "nps_driver_dash.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Gerado: {out}")
