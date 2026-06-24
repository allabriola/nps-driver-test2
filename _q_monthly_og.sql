-- Outgoing mensal por CDU — CDUs de dor — Drivers — BR_ME_Sellers_Longtail
SELECT
  FORMAT_DATE('%Y-%m', OUTGOING_DATE) AS mes,
  CDU,
  SUM(CANT_OUTGOING) AS outgoing
FROM `meli-bi-data.WHOWNER.DM_CX_OUTGOING_GESTION_DETAIL`
WHERE SIT_SITE_ID = 'MLB'
  AND CI_EVENT_NAME IN ('OUTGOING_CONTACT','OUTGOING_FIRST_CONTACT')
  AND PRO_PROCESS_NAME = 'Drivers'
  AND USER_TEAM_NAME IN ('BR_ME_Sellers_Longtail','BR_ME_Pre-Despacho_Offline')
  AND CDU IN (
    'Tiene un inconviente con sus metricas de Nivel de Lealtad',
    'Quiere reclamar por inconvenientes en el recorrido o en el service center',
    'Tiene problemas durante la creacion de la cuenta',
    'Quiere saber porque no le pagaron una ruta'
  )
  AND OUTGOING_DATE BETWEEN '2026-02-01' AND CURRENT_DATE() - 1
GROUP BY mes, CDU
ORDER BY CDU, mes
