-- Case IDs via NPS table (mais rápido que o JOIN com CI)
SELECT
  CDU,
  CAST(CAS_CASE_ID AS STRING) AS case_id
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE
  RES_END_DATE >= '2026-02-01'
  AND RES_END_DATE <= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND ANTIGUEDAD_REP IN ('EXPERT','NEWBIE')
  AND FLAG_NOT_EXCLUDED_SURVEY IS TRUE
  AND FLAG_ACTIVE_TEAM IS TRUE
  AND USER_TEAM_NAME IN ('BR_ME_Sellers_Longtail','BR_ME_Pre-Despacho_Offline')
  AND PRO_PROCESS_NAME = 'Drivers'
  AND CDU IN (
    'Tiene un inconviente con sus metricas de Nivel de Lealtad',
    'Quiere reclamar por inconvenientes en el recorrido o en el service center',
    'Tiene problemas durante la creacion de la cuenta',
    'Quiere saber porque no le pagaron una ruta',
    'Quiere saber porqué se inactivó su cuenta'
  )
  AND CAS_CASE_ID IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY CDU ORDER BY RES_END_DATE DESC) <= 150
