-- Case IDs de outgoing para CDUs críticas — Drivers — BR_ME_Sellers_Longtail
SELECT
  CDU,
  CAST(i.CAS_CASE_ID AS STRING) AS case_id
FROM `meli-bi-data.WHOWNER.BT_CX_CASE_INTERACTION` i
INNER JOIN `meli-bi-data.WHOWNER.DM_CX_OUTGOING_GESTION_DETAIL` og
  ON i.WCM_CONT_ID = og.SOLUTION_ID
  AND i.SIT_SITE_ID = og.SIT_SITE_ID
WHERE i.SIT_SITE_ID = 'MLB'
  AND i.FLAG_OUTGOING_GESTION = 1
  AND og.PRO_PROCESS_NAME = 'Drivers'
  AND og.USER_TEAM_NAME IN ('BR_ME_Sellers_Longtail','BR_ME_Pre-Despacho_Offline')
  AND og.CDU IN (
    'Tiene un inconviente con sus metricas de Nivel de Lealtad',
    'Quiere reclamar por inconvenientes en el recorrido o en el service center',
    'Tiene problemas durante la creacion de la cuenta',
    'Quiere saber porque no le pagaron una ruta',
    'Quiere saber porqué se inactivó su cuenta'
  )
  AND CAST(i.CI_CREATED_DATE AS DATE) >= '2026-02-01'
QUALIFY ROW_NUMBER() OVER (PARTITION BY og.CDU ORDER BY i.CI_CREATED_DATE DESC) <= 120
