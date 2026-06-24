#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
client = bigquery.Client(project="meli-bi-data")

# Test DM_CX_NPS_COMMERCE_DETAIL for weekly data
q1 = """
SELECT TIPO_USUARIO, SEGMENTO_SELLER, COUNT(*) as cnt
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_COMMERCE_DETAIL`
WHERE SIT_SITE_ID = 'MLB'
  AND RES_END_DATE BETWEEN '2026-04-27' AND '2026-05-03'
GROUP BY TIPO_USUARIO, SEGMENTO_SELLER
ORDER BY cnt DESC
"""
print("=== TIPO_USUARIO + SEGMENTO_SELLER (commerce, 27abr-03mai) ===")
for r in client.query(q1).result():
    print(f"  tipo={r.TIPO_USUARIO} | seg={r.SEGMENTO_SELLER} | cnt={r.cnt}")

# Check ME processes for Vendedor Seller dev
q2 = """
SELECT
  PRO_PROCESS_NAME,
  SEGMENTO_SELLER,
  SUM(PROMOTERS) as p, SUM(DETRACTORS) as d, COUNT(*) as s
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_COMMERCE_DETAIL`
WHERE SIT_SITE_ID = 'MLB'
  AND RES_END_DATE BETWEEN '2026-04-27' AND '2026-05-03'
  AND TIPO_USUARIO = 'Vendedor'
  AND PRO_PROCESS_NAME IN (
    'Reputación ME', 'Despacho Ventas y Publicaciones',
    'Gestiones Operativas', 'Reversa', 'Viaje del paquete - Vendedor', 'Suspensiones ME'
  )
GROUP BY PRO_PROCESS_NAME, SEGMENTO_SELLER
ORDER BY PRO_PROCESS_NAME, SEGMENTO_SELLER
"""
print("\n=== ME Vendedor processes by segment ===")
for r in client.query(q2).result():
    nps = round(100*(r.p-r.d)/r.s, 1) if r.s else 0
    print(f"  {r.PRO_PROCESS_NAME} | {r.SEGMENTO_SELLER}: p={r.p} d={r.d} s={r.s} NPS={nps}")

# Check total for all Vendedores (to cross with build_driver_impact VIG data)
q3 = """
SELECT
  SEGMENTO_SELLER,
  SUM(PROMOTERS) as p, SUM(DETRACTORS) as d, COUNT(*) as s
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_COMMERCE_DETAIL`
WHERE SIT_SITE_ID = 'MLB'
  AND RES_END_DATE BETWEEN '2026-04-27' AND '2026-04-29'
  AND TIPO_USUARIO = 'Vendedor'
  AND PRO_PROCESS_NAME IN (
    'Reputación ME', 'Despacho Ventas y Publicaciones',
    'Gestiones Operativas', 'Reversa', 'Viaje del paquete - Vendedor', 'Suspensiones ME'
  )
GROUP BY SEGMENTO_SELLER
"""
print("\n=== ME total for VIG (27-29abr) by segment — should match build_driver_impact ===")
print("  build_driver_impact VIG: Seller Dev=(430,64,542) / Mature=(36,14,54) / Meli Pro=(75,3,81)")
for r in client.query(q3).result():
    nps = round(100*(r.p-r.d)/r.s, 1) if r.s else 0
    print(f"  {r.SEGMENTO_SELLER}: p={r.p} d={r.d} s={r.s} NPS={nps}")
