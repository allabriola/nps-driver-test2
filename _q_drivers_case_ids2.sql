-- Case IDs via DM_CX_OUTGOING — mais simples e rápido
SELECT
  CDU,
  CAST(CAS_CASE_ID AS STRING) AS case_id
FROM `meli-bi-data.WHOWNER.DM_CX_OUTGOING_GESTION_DETAIL`
WHERE SIT_SITE_ID = 'MLB'
  AND CI_EVENT_NAME IN ('OUTGOING_CONTACT','OUTGOING_FIRST_CONTACT')
  AND PRO_PROCESS_NAME = 'Drivers'
  AND USER_TEAM_NAME IN ('BR_ME_Sellers_Longtail','BR_ME_Pre-Despacho_Offline')
  AND CDU IN (
    'Tiene un inconviente con sus metricas de Nivel de Lealtad',
    'Quiere reclamar por inconvenientes en el recorrido o en el service center',
    'Tiene problemas durante la creacion de la cuenta',
    'Quiere saber porque no le pagaron una ruta',
    'Quiere saber porqué se inactivó su cuenta'
  )
  AND OUTGOING_DATE >= '2026-03-01'
  AND CAS_CASE_ID IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY CDU ORDER BY OUTGOING_DATE DESC) <= 80
