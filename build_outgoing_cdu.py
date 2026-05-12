#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_outgoing_cdu.py
Volume Outgoing por CDU — Facturación e Emissão de Nota Fiscal (MLB)

Gera HTML com:
  • Aba 1: Facturación
  • Aba 2: Emissão de Nota Fiscal
  Cada aba: gráfico mensal (Jan–Mai), gráfico semanal (8 semanas),
             destaque top CDU + tabela de ranking, análise de transcrições
"""
import sys, json, re, os
sys.stdout.reconfigure(encoding="utf-8")

from google.cloud import bigquery
from collections import Counter
from datetime import date, timedelta

# ── Configuração ────────────────────────────────────────────────────────────
PROJECT   = "meli-bi-data"
SITE      = "MLB"
TOP_CDUS  = 8   # máximo de CDUs mostrados nos gráficos

# Chave = CX_PR_NAME_HSP em LK_CX_PROCESS_ADM | Valor = label exibido no HTML
PROCESSES = {
    "Facturación":            "Facturación",
    "Emision de Nota Fiscal": "Emissão de Nota Fiscal",
}

TODAY           = date.today()
START_YEAR      = date(TODAY.year, 1, 1)
EIGHT_WEEKS_AGO = TODAY - timedelta(weeks=8)
TRANSCRIPT_DAYS = 90

MES_PT = {
    "01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr",
    "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago",
    "09": "Set", "10": "Out", "11": "Nov", "12": "Dez",
}

PALETTE = [
    "#4472C4", "#ED7D31", "#70AD47", "#FFC000", "#E05252",
    "#9B59B6", "#255E91", "#c45f00", "#3aaa72", "#b38600",
]
OUTROS_COLOR = "#BBBBBB"

STOPWORDS = set("""
de da do que em para com um uma os as o a e é se não por mais ele ela
nao na no ao dos das me você oi ola sim bom dia boa tarde noite obrigado
obrigada ok isso este esta esse essa meu minha seu sua foi ser ter estou
esta tenho preciso posso pode como quando onde qual quais aqui ja mais
mas ou pois ate sobre mesmo tambem agora ainda depois antes entao porque
pelo pela pelos pelas hello hi the and for are this that with xxx xx x
null none true false nbsp nao nps vou temos voce vc eles elas nos vos
sendo tendo fazendo sou chamo nome meu minha representante espero esteja
bem hoje agradeço agradeco obrigad atendimento auxiliar auxiliarei
ajudar ajudarei ajudo mercado livre meli vendedor comprador seller
silence seconds silence email recipient num date hour url tramite
andamento abertura reclamacao reclamação interacao interação autor
descricao descrição fornecedor protocolo origem destino cola derivar
derivaçao processo justificacao equipe venda anuncio pedido caso
informo informei verifico verifiquei entendo entendi identifico identificamos
peço peco solicito solicitou infelizmente lamentamos desculpas
""".split())

# ── BigQuery client ─────────────────────────────────────────────────────────
client = bigquery.Client(project=PROJECT)

def run(sql: str, retries: int = 5) -> list[dict]:
    import time
    for attempt in range(retries):
        try:
            return [dict(r) for r in client.query(sql).result()]
        except Exception as e:
            if "Quota exceeded" in str(e) and attempt < retries - 1:
                wait = 20 * (attempt + 1)
                print(f"   [quota] aguardando {wait}s (tentativa {attempt+1}/{retries})…")
                time.sleep(wait)
            else:
                raise

# ── Queries ─────────────────────────────────────────────────────────────────
# Fonte principal: DM_CX_OUTGOING_GESTION_DETAIL (tabela oficial de outgoing)
# Transcrições: BT_CX_TRANSCRIPT via CAS_CASE_ID de BT_CX_CASE_INTERACTION

TABLE_OG = f"`{PROJECT}.WHOWNER.DM_CX_OUTGOING_GESTION_DETAIL`"
TABLE_CI = f"`{PROJECT}.WHOWNER.BT_CX_CASE_INTERACTION`"
TABLE_TR = f"`{PROJECT}.WHOWNER.BT_CX_TRANSCRIPT`"

EVENT_FILTER = "CI_EVENT_NAME IN ('OUTGOING_CONTACT','OUTGOING_FIRST_CONTACT')"
CDU_EXPR     = "COALESCE(NULLIF(CDU,''), 'Sem CDU')"

def q_monthly() -> str:
    procs = "','".join(PROCESSES)
    return f"""
    SELECT
      FORMAT_DATE('%Y-%m', OUTGOING_DATE)   AS month,
      PRO_PROCESS_NAME                      AS process,
      {CDU_EXPR}                            AS cdu,
      SUM(CANT_OUTGOING)                    AS volume
    FROM {TABLE_OG}
    WHERE SIT_SITE_ID       = '{SITE}'
      AND {EVENT_FILTER}
      AND PRO_PROCESS_NAME  IN ('{procs}')
      AND OUTGOING_DATE BETWEEN '{START_YEAR}' AND '{TODAY}'
    GROUP BY 1, 2, 3
    ORDER BY 1, 2, 4 DESC
    """

def q_weekly() -> str:
    procs = "','".join(PROCESSES)
    return f"""
    SELECT
      DATE_TRUNC(OUTGOING_DATE, ISOWEEK)    AS week_start,
      PRO_PROCESS_NAME                      AS process,
      {CDU_EXPR}                            AS cdu,
      SUM(CANT_OUTGOING)                    AS volume
    FROM {TABLE_OG}
    WHERE SIT_SITE_ID       = '{SITE}'
      AND {EVENT_FILTER}
      AND PRO_PROCESS_NAME  IN ('{procs}')
      AND OUTGOING_DATE >= '{EIGHT_WEEKS_AGO}'
    GROUP BY 1, 2, 3
    ORDER BY 1, 2, 4 DESC
    """

def q_case_ids(process: str, cdu: str) -> str:
    """Case IDs via BT_CX_CASE_INTERACTION filtrado pelo SOLUTION_ID do CDU."""
    cutoff    = TODAY - timedelta(days=TRANSCRIPT_DAYS)
    cdu_safe  = cdu.replace("'", "''")
    proc_safe = process.replace("'", "''")
    return f"""
    SELECT DISTINCT i.CAS_CASE_ID
    FROM {TABLE_CI} i
    WHERE i.SIT_SITE_ID          = '{SITE}'
      AND i.FLAG_OUTGOING_GESTION = 1
      AND i.CI_PROCESS_ID IN (
          SELECT DISTINCT CI_PROCESS_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID = '{SITE}' AND PRO_PROCESS_NAME = '{proc_safe}'
      )
      AND i.WCM_CONT_ID IN (
          SELECT DISTINCT SOLUTION_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID = '{SITE}'
            AND PRO_PROCESS_NAME = '{proc_safe}'
            AND {CDU_EXPR} = '{cdu_safe}'
      )
      AND CAST(i.CI_CREATED_DATE AS DATE) >= '{cutoff}'
    LIMIT 1000
    """

def q_sample_cases(process: str, cdu: str, n: int = 8) -> str:
    """Retorna exemplos recentes de CAS_CASE_ID + data para exibir no HTML."""
    cutoff    = TODAY - timedelta(days=60)
    cdu_safe  = cdu.replace("'", "''")
    proc_safe = process.replace("'", "''")
    return f"""
    SELECT
      CAST(i.CAS_CASE_ID AS STRING) AS case_id,
      CAST(i.CI_CREATED_DATE AS DATE) AS date
    FROM {TABLE_CI} i
    WHERE i.SIT_SITE_ID          = '{SITE}'
      AND i.FLAG_OUTGOING_GESTION = 1
      AND i.CI_PROCESS_ID IN (
          SELECT DISTINCT CI_PROCESS_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID = '{SITE}' AND PRO_PROCESS_NAME = '{proc_safe}'
      )
      AND i.WCM_CONT_ID IN (
          SELECT DISTINCT SOLUTION_ID FROM {TABLE_OG}
          WHERE SIT_SITE_ID = '{SITE}'
            AND PRO_PROCESS_NAME = '{proc_safe}'
            AND {CDU_EXPR} = '{cdu_safe}'
      )
      AND CAST(i.CI_CREATED_DATE AS DATE) >= '{cutoff}'
    ORDER BY i.CI_CREATED_DATE DESC
    LIMIT {n}
    """

def q_transcripts_with_case(case_ids: list[str]) -> str:
    ids = ",".join(case_ids)
    return f"""
    SELECT
      CAST(CAS_CASE_ID AS STRING)    AS case_id,
      OBFUSCATED_MESSAGE_CONTENT     AS msg
    FROM {TABLE_TR}
    WHERE CAS_CASE_ID IN ({ids})
      AND OBFUSCATED_MESSAGE_CONTENT IS NOT NULL
      AND LENGTH(OBFUSCATED_MESSAGE_CONTENT) > 20
    """

# ── Temas curados manualmente (análise de 40 casos por CDU) ─────────────────
# Chave: (proc_key, top_cdu)
CURATED_THEMES: dict[tuple[str, str], list[dict]] = {
    ("Facturación", "Dudas sobre cargos facturados"): [
        {
            "name": "Débito automático de fatura vencida",
            "pct": 35,
            "case_ids": ["450596238", "450254304", "453189041"],
            "summary": (
                "Sellers são surpreendidos com débito automático de faturas vencidas do "
                "Mercado Livre descontado do saldo em conta, sem reconhecer a origem do valor."
            ),
        },
        {
            "name": "Cobrança de publicidade — Mercado Ads",
            "pct": 25,
            "case_ids": ["449223681", "450388418", "438822396"],
            "summary": (
                "Sellers questionam cobranças de campanhas de publicidade (Display Ads, "
                "Product Ads), frequentemente por não reconhecerem a tarifa ou acreditarem "
                "estar em período de teste gratuito."
            ),
        },
        {
            "name": "Tarifa cobrada em venda cancelada ou devolvida",
            "pct": 20,
            "case_ids": ["448026895", "447986958", "436559907"],
            "summary": (
                "Sellers solicitam estorno de tarifas cobradas sobre vendas canceladas ou "
                "com devolução, esperando que o valor seja revertido automaticamente após o cancelamento."
            ),
        },
        {
            "name": '"Minha Página" — cobrança não reconhecida',
            "pct": 10,
            "case_ids": ["438951678", "451099545", "436543608"],
            "summary": (
                "Sellers contestam a tarifa de manutenção da 'Minha Página', afirmando não "
                "ter contratado o serviço. Alguns relatam suspeita de uso indevido ou invasão da conta."
            ),
        },
        {
            "name": "Interpretação e reconciliação de fatura",
            "pct": 10,
            "case_ids": ["450135341", "436722229", "447448743"],
            "summary": (
                "Sellers solicitam detalhamento dos itens da fatura para conciliação financeira, "
                "com dúvidas sobre divergências entre o valor faturado e o esperado no período."
            ),
        },
    ],
    ("Emision de Nota Fiscal", "Faturador MeLi"): [
        {
            "name": "Bloqueio na emissão — NF pendente impede envio",
            "pct": 30,
            "case_ids": ["449061727", "451571088", "452567701"],
            "summary": (
                "Sellers não conseguem emitir NF-e e o envio fica bloqueado. Causas frequentes: "
                "pendências no SEFAZ, série não exclusiva para o ML ou instabilidade no sistema fiscal."
            ),
        },
        {
            "name": "Credenciamento e dados fiscais incorretos",
            "pct": 25,
            "case_ids": ["449585495", "448557710", "452942438"],
            "summary": (
                "Sellers têm emissão bloqueada por Inscrição Estadual incorreta, CNPJ não "
                "credenciado no SEFAZ ou dados fiscais desatualizados na conta do Mercado Livre."
            ),
        },
        {
            "name": "Erros de configuração da NF-e (quantidade, NCM, CFOP)",
            "pct": 20,
            "case_ids": ["439223431", "442031708", "450379451"],
            "summary": (
                "Sellers relatam discrepâncias entre a NF emitida e o produto real: "
                "quantidade divergente, NCM ausente ou CFOP inválido para operação interestadual."
            ),
        },
        {
            "name": "Vendas não aparecem no painel para emissão",
            "pct": 15,
            "case_ids": ["447058713", "436230190", "449061727"],
            "summary": (
                "Sellers relatam que vendas não aparecem na listagem de NF-e pendentes, "
                "impedindo a emissão em massa. Em alguns casos causado por filtro ativo no painel."
            ),
        },
        {
            "name": "Primeiros passos — novo vendedor sem histórico de emissão",
            "pct": 10,
            "case_ids": ["448868937", "452942438", "454506635"],
            "summary": (
                "Sellers novos ou sem experiência buscam orientação completa: como habilitar "
                "o Faturador MeLi, requisitos legais (PJ, certificado A1) e como emitir a primeira NF-e."
            ),
        },
    ],
    # ── Bugs ──────────────────────────────────────────────────────────────────
    ("Facturación", "Bugs"): [
        {
            "name": "Instabilidade no sistema de faturamento",
            "pct": 32,
            "case_ids": ["450587452", "449307556", "440196017"],
            "summary": (
                "Sellers reportam erros e instabilidades no painel de faturamento — "
                "valores que não atualizam, NF em loop de carregamento ou informações "
                "incorretas exibidas pelo sistema."
            ),
        },
        {
            "name": "Divergência entre comissão cobrada e NF de serviço emitida",
            "pct": 26,
            "case_ids": ["441387270", "450054579", "436230186"],
            "summary": (
                "Sellers identificam que o total de comissões e tarifas cobradas "
                "não corresponde ao valor das notas fiscais de serviço emitidas pela plataforma."
            ),
        },
        {
            "name": "Cobrança indevida por serviço inativo ou cancelado",
            "pct": 20,
            "case_ids": ["433474508", "444756802", "441997784"],
            "summary": (
                "Sellers contestam cobranças de serviços que afirmam não estar ativos — "
                "como 'Minha Página', tarifas Full ou campanhas — e solicitam estorno do valor."
            ),
        },
        {
            "name": "Dados fiscais incorretos ou bloqueados em anúncios",
            "pct": 14,
            "case_ids": ["436570008", "447901186", "445587512"],
            "summary": (
                "Sellers encontram erros nos dados fiscais dos anúncios: endereço incorreto "
                "nas NFs emitidas, campos de NCM/CFOP bloqueados ou regras tributárias com falha."
            ),
        },
        {
            "name": "Escalonamento via Gov/Procon/Reclame Aqui",
            "pct": 8,
            "case_ids": ["435786889", "447132994", "447288327"],
            "summary": (
                "Sellers que não obtiveram resolução pelo canal direto escalaram a disputa de "
                "faturamento para órgãos regulatórios (Consumidor.gov, Procon, Reclame Aqui)."
            ),
        },
    ],
    ("Emision de Nota Fiscal", "Bugs"): [
        {
            "name": "Emissor de NF-e travado ou sem carregar",
            "pct": 30,
            "case_ids": ["452942113", "455852256", "446580215"],
            "summary": (
                "Sellers não conseguem emitir NF-e porque o emissor fica em loop de "
                "carregamento, a tela de configuração não abre, ou a opção de emissão em "
                "lote desapareceu do painel."
            ),
        },
        {
            "name": "CNPJ não habilitado na SEFAZ / certificado digital com erro",
            "pct": 25,
            "case_ids": ["448593810", "447706064", "443778897"],
            "summary": (
                "Sellers recebem o erro 'CNPJ não habilitado na SEFAZ' mesmo após "
                "credenciamento confirmado, ou o certificado digital A1 expirou ou foi "
                "exportado sem a chave privada, impedindo a emissão."
            ),
        },
        {
            "name": "Incidente ativo de instabilidade na emissão de NF",
            "pct": 20,
            "case_ids": ["438061015", "445223547", "451516035"],
            "summary": (
                "O sistema do Mercado Livre apresenta instabilidade conhecida que impede "
                "a emissão ou visualização de NF-es. Equipe de tecnologia já acionada, "
                "sellers orientados a aguardar normalização."
            ),
        },
        {
            "name": "Inscrição Estadual incorreta ou duplicada no cadastro",
            "pct": 15,
            "case_ids": ["437266535", "435786880", "455587095"],
            "summary": (
                "Sellers têm Inscrição Estadual (IE) errada ou duplicada na conta do "
                "Mercado Livre — divergência com dados da SEFAZ que bloqueia a emissão de NF-e."
            ),
        },
        {
            "name": "Nova exigência fiscal da SEFAZ (CBENEF, CFOP, rejeições)",
            "pct": 10,
            "case_ids": ["455195008", "450980551", "454779889"],
            "summary": (
                "Rejeições de NF-e causadas por novas exigências fiscais da SEFAZ: "
                "código CBENEF obrigatório, rejeição de CT-e, ou CFOP inválido para "
                "operações interestaduais após mudança de regime."
            ),
        },
    ],

    # ── Facturación — outros CDUs ─────────────────────────────────────────────
    ("Facturación", "Generales"): [
        {
            "name": "Cobrança inesperada de 'Minha Página' ou campanha não autorizada",
            "pct": 30,
            "case_ids": ["438599910", "445309408", "447711579"],
            "summary": (
                "Sellers contestam cobranças mensais da assinatura 'Minha Página' ou de "
                "campanhas de publicidade que afirmam não ter contratado ou ativado."
            ),
        },
        {
            "name": "Débito automático de fatura vencida em conta vinculada",
            "pct": 25,
            "case_ids": ["440490409", "439233988", "452080824"],
            "summary": (
                "Sellers são surpreendidos com débito automático de faturas vencidas em "
                "conta do Mercado Pago vinculada, sem reconhecer a origem da cobrança."
            ),
        },
        {
            "name": "Divergência entre valor cobrado e extrato esperado",
            "pct": 20,
            "case_ids": ["443542893", "444683513", "453746958"],
            "summary": (
                "Sellers identificam diferenças entre o valor de tarifas cobrado e o "
                "esperado — juros, multas ou descontos que não correspondem ao histórico."
            ),
        },
        {
            "name": "Bloqueio fiscal impedindo envio ou entrada no Full",
            "pct": 15,
            "case_ids": ["444857940", "453738125", "444829921"],
            "summary": (
                "Dados fiscais incompletos ou inconsistentes bloqueiam o planejamento "
                "de envios ao Full ou impedem a emissão de NF-e em vendas específicas."
            ),
        },
        {
            "name": "Dificuldade para encerrar conta com pendências alegadas",
            "pct": 10,
            "case_ids": ["448385295", "438567236", "451066099"],
            "summary": (
                "Sellers tentam encerrar a conta mas o sistema exibe 'pendências' ou "
                "'faturas em aberto' mesmo sem dívidas confirmadas, impedindo o cancelamento."
            ),
        },
    ],
    ("Facturación", "Dudas sobre documentos fiscales y reportes"): [
        {
            "name": "Como baixar relatórios de vendas, NF-e e XML do faturamento",
            "pct": 35,
            "case_ids": ["438579265", "446880330", "449196481"],
            "summary": (
                "Sellers buscam orientação para baixar relatórios de vendas, XMLs de "
                "NF-e, extratos de faturamento e documentos fiscais emitidos na plataforma."
            ),
        },
        {
            "name": "Divergência entre NF de serviço emitida e comissão cobrada",
            "pct": 25,
            "case_ids": ["439531044", "440989575", "443076071"],
            "summary": (
                "O total de comissões cobradas pelo Mercado Livre não coincide com o "
                "valor das NFS-e de serviço emitidas — dificultando a conciliação contábil."
            ),
        },
        {
            "name": "Dados incorretos em NF já emitida (endereço, valor, CFOP)",
            "pct": 20,
            "case_ids": ["436570008", "453691837", "444042106"],
            "summary": (
                "Sellers precisam corrigir NF-e já emitida com dados errados — endereço "
                "do tomador, valor divergente ou CFOP inválido — e não sabem como cancelar e reemitir."
            ),
        },
        {
            "name": "NF de devolução emitida automaticamente pelo Full sem autorização",
            "pct": 12,
            "case_ids": ["448257564", "436253303", "450849617"],
            "summary": (
                "O Full emite NF-e de devolução automaticamente, gerando documentos "
                "fiscais que o seller não solicitou e não sabe como contestar ou regularizar."
            ),
        },
        {
            "name": "DIFAL e impostos estaduais aparecendo no relatório de faturamento",
            "pct": 8,
            "case_ids": ["444776794", "439806044", "448699099"],
            "summary": (
                "Sellers questionam cobranças de DIFAL e outros impostos estaduais que "
                "aparecem no relatório de faturamento sem explicação clara da origem."
            ),
        },
    ],
    ("Facturación", "Dudas sobre Deuda /Débito (Automático o forzado)"): [
        {
            "name": "Débito automático de fatura vencida não reconhecido",
            "pct": 38,
            "case_ids": ["448117533", "447907663", "455340536"],
            "summary": (
                "Sellers são debitados automaticamente por faturas vencidas do Mercado "
                "Livre e não entendem a origem do valor, solicitando explicação e estorno."
            ),
        },
        {
            "name": "Débito em conta do Mercado Pago por dívida em conta vinculada",
            "pct": 22,
            "case_ids": ["440396595", "442768416", "439889946"],
            "summary": (
                "O saldo do Mercado Pago é debitado automaticamente para quitar dívida "
                "de outra conta vinculada ao mesmo CPF/CNPJ, sem aviso prévio ao seller."
            ),
        },
        {
            "name": "Campanha de Product Ads debitada sem autorização",
            "pct": 20,
            "case_ids": ["435898726", "442544341", "443341885"],
            "summary": (
                "Sellers contestam débito de campanhas de Product Ads que afirmam não "
                "ter ativado ou que pausaram, mas a cobrança continua aparecendo na fatura."
            ),
        },
        {
            "name": "Pagamento realizado mas saldo não abatido da dívida",
            "pct": 12,
            "case_ids": ["439853086", "449802030", "438589091"],
            "summary": (
                "Sellers realizaram pagamento via PIX ou antecipação de saldo para quitar "
                "fatura, mas o valor não foi debitado e a dívida continua aparecendo."
            ),
        },
        {
            "name": "Dívida por reclamações e devoluções contestada",
            "pct": 8,
            "case_ids": ["448854786", "453529930", "451470832"],
            "summary": (
                "Sellers contestam débitos gerados por reclamações e devoluções de "
                "compradores, alegando que o produto foi enviado corretamente ou devolvido com dano."
            ),
        },
    ],
    ("Facturación", "Generales Facturación"): [
        {
            "name": "Contestação formal de cobrança indevida",
            "pct": 30,
            "case_ids": ["455819252", "443209665", "451983284"],
            "summary": (
                "Sellers formalizam contestação de cobranças que consideram indevidas, "
                "solicitando baixa definitiva de débito, cessação de cobranças ou revisão técnica."
            ),
        },
        {
            "name": "Divergência entre valor líquido recebido e esperado na venda",
            "pct": 25,
            "case_ids": ["443572586", "441037567", "450130574"],
            "summary": (
                "Sellers identificam que o valor recebido na venda é diferente do "
                "esperado após tarifas, estornos e descontos aplicados automaticamente."
            ),
        },
        {
            "name": "Tarifas de devolução e custo de envio de retorno",
            "pct": 22,
            "case_ids": ["440751626", "446451726", "444998630"],
            "summary": (
                "Sellers questionam cobranças de tarifa de devolução e frete de retorno "
                "sobre vendas canceladas ou com reclamação, solicitando estorno dos valores."
            ),
        },
        {
            "name": "Regras fiscais bloqueando anúncios ou entrada no Full",
            "pct": 13,
            "case_ids": ["447949258", "440978009", "454850574"],
            "summary": (
                "Inconsistências nos dados fiscais da conta geram restrições que pausam "
                "anúncios ou impedem o envio de estoque para centros do Full."
            ),
        },
        {
            "name": "Atualização de dados cadastrais e endereço fiscal nas NF-e",
            "pct": 10,
            "case_ids": ["435795487", "436963050", "444982420"],
            "summary": (
                "Sellers precisam atualizar endereço fiscal, razão social ou dados "
                "do emitente nas NFS-e de serviço emitidas pelo Mercado Livre."
            ),
        },
    ],
    ("Facturación", "Dudas sobre datos de facturación"): [
        {
            "name": "Como visualizar tarifas, extratos e movimentos do faturamento",
            "pct": 35,
            "case_ids": ["448187409", "450864940", "449664098"],
            "summary": (
                "Sellers buscam orientação para acessar o painel de faturamento, "
                "entender os movimentos do período atual e verificar o detalhamento das tarifas."
            ),
        },
        {
            "name": "Divergência no valor líquido recebido por venda",
            "pct": 25,
            "case_ids": ["441110596", "451138028", "442977040"],
            "summary": (
                "Sellers percebem que o valor recebido por uma venda difere do esperado "
                "e buscam entender quais tarifas, rebates ou estornos causaram a diferença."
            ),
        },
        {
            "name": "Dados fiscais incorretos ou erro ao identificar cobrança",
            "pct": 20,
            "case_ids": ["448863348", "455567489", "450888563"],
            "summary": (
                "Sellers enfrentam erros por dados fiscais desatualizados — regime "
                "tributário incorreto, CNPJs não reconhecidos ou cobranças sem detalhamento visível."
            ),
        },
        {
            "name": "Antecipação de saldo e controle do ciclo de faturamento",
            "pct": 12,
            "case_ids": ["440418508", "447427082", "452923645"],
            "summary": (
                "Sellers querem antecipar pagamento de fatura, alterar a data de "
                "vencimento ou entender por que o ciclo de cobrança pega dois meses distintos."
            ),
        },
        {
            "name": "Migração de regime fiscal ou tipo de conta (CPF→CNPJ, MEI→Simples)",
            "pct": 8,
            "case_ids": ["448843887", "442195125", "454226250"],
            "summary": (
                "Sellers precisam migrar de CPF para CNPJ, de MEI para Simples Nacional "
                "ou atualizar o regime tributário na conta, mas encontram bloqueios no processo."
            ),
        },
    ],
    ("Facturación", "Dudas sobre Impuestos"): [
        {
            "name": "Cobrança de DIFAL/ICMS na fatura e como pagar a GNRE",
            "pct": 38,
            "case_ids": ["442489337", "440120779", "452871485"],
            "summary": (
                "Sellers recebem cobrança de DIFAL na fatura por vendas interestaduais e "
                "buscam entender como calcular, emitir e pagar a GNRE para o estado de destino."
            ),
        },
        {
            "name": "Duplicidade de cobrança de DIFAL (já pagou GNRE e ML cobrou novamente)",
            "pct": 25,
            "case_ids": ["452713284", "443691226", "451928378"],
            "summary": (
                "Sellers que já pagaram a GNRE identificam cobrança do mesmo DIFAL "
                "no faturamento do Mercado Livre, configurando possível duplicidade de pagamento."
            ),
        },
        {
            "name": "DIFAL indevido para optantes do Simples Nacional",
            "pct": 18,
            "case_ids": ["442955621", "438132468", "452961236"],
            "summary": (
                "Empresas do Simples Nacional contestam a cobrança de DIFAL, "
                "alegando imunidade fiscal e solicitando orientação sobre como bloquear "
                "ou contestar o imposto cobrado pelo estado de destino."
            ),
        },
        {
            "name": "Informe de rendimentos e IR divergente do esperado",
            "pct": 12,
            "case_ids": ["451525089", "446695760", "449423763"],
            "summary": (
                "Sellers questionam divergências no informe de rendimentos anual ou "
                "nas alíquotas de IR aplicadas sobre o Cofrinho, não entendendo o cálculo."
            ),
        },
        {
            "name": "Comprovante de GNRE e mercadoria bloqueada na SEFAZ",
            "pct": 7,
            "case_ids": ["456077828", "452511411", "444824695"],
            "summary": (
                "Mercadoria retida na SEFAZ por falta ou inconsistência do comprovante "
                "de GNRE — seller busca orientação para anexar o documento e liberar o envio."
            ),
        },
    ],

    # ── Emissão de Nota Fiscal — outros CDUs ─────────────────────────────────
    ("Emision de Nota Fiscal", "Impuesto para facturar"): [
        {
            "name": "Configuração de regras tributárias nos anúncios (NCM, CFOP, CSOSN)",
            "pct": 35,
            "case_ids": ["447406666", "444064516", "451564085"],
            "summary": (
                "Sellers precisam configurar regras tributárias nos anúncios — NCM, "
                "CFOP, CSOSN e regime tributário — para habilitar a emissão de NF-e e "
                "enviar estoque para o Full."
            ),
        },
        {
            "name": "CBENEF obrigatório — código de benefício fiscal não configurado",
            "pct": 25,
            "case_ids": ["448111076", "454268638", "448186992"],
            "summary": (
                "A SEFAZ passou a exigir o CBENEF para emissão de NF-e em determinados "
                "CSTs/CSOSNs. Sellers recebem bloqueio e buscam entender como configurar "
                "o código no faturador sem alterar indevidamente o regime tributário."
            ),
        },
        {
            "name": "DIFAL e GNRE em vendas interestaduais via faturamento",
            "pct": 18,
            "case_ids": ["436219608", "444824695", "437752896"],
            "summary": (
                "Sellers questionam cobranças automáticas de DIFAL por vendas interestaduais "
                "e buscam entender como emitir e pagar a GNRE corretamente antes do envio."
            ),
        },
        {
            "name": "Regime tributário desatualizado (MEI, Simples, Lucro Real)",
            "pct": 14,
            "case_ids": ["439078207", "447685979", "448112779"],
            "summary": (
                "O regime tributário cadastrado no Mercado Livre diverge do regime "
                "atual do CNPJ, gerando rejeições de NF-e ou bloqueio de anúncios até "
                "a atualização dos dados fiscais."
            ),
        },
        {
            "name": "Como emitir Carta de Correção e baixar XML de documentos fiscais",
            "pct": 8,
            "case_ids": ["437826880", "449365655", "448091962"],
            "summary": (
                "Sellers precisam de orientação para emitir Carta de Correção Eletrônica "
                "ou baixar XML de notas já emitidas no faturador do Mercado Livre."
            ),
        },
    ],
    ("Emision de Nota Fiscal", "Restricción fiscal"): [
        {
            "name": "Conta suspensa por dados fiscais incorretos ou IE desabilitada",
            "pct": 35,
            "case_ids": ["436054322", "444306755", "436138023"],
            "summary": (
                "A conta é suspensa parcialmente porque a Inscrição Estadual está "
                "desabilitada na SEFAZ ou o regime tributário mudou e os dados no "
                "Mercado Livre não foram atualizados."
            ),
        },
        {
            "name": "Restrição 'seller invoices shipping fiscal' bloqueando anúncios",
            "pct": 28,
            "case_ids": ["439456956", "442706636", "450629810"],
            "summary": (
                "Anúncios são pausados pela restrição fiscal de emissão de NF-e para "
                "envios, impedindo despachos até que os dados fiscais sejam regularizados."
            ),
        },
        {
            "name": "NF rejeitada por dados incorretos do emitente ou destinatário",
            "pct": 20,
            "case_ids": ["441827322", "455393583", "446137783"],
            "summary": (
                "Rejeições de NF-e por IE do emitente ou destinatário inválida, série "
                "não exclusiva ou valor da nota divergente do valor real da venda."
            ),
        },
        {
            "name": "Instabilidade no sistema impedindo emissão e geração de etiqueta",
            "pct": 10,
            "case_ids": ["453816596", "451143265", "451500923"],
            "summary": (
                "O sistema do Mercado Livre apresenta instabilidade que bloqueia a emissão "
                "de NF-e, impedindo a geração da etiqueta de envio mesmo com dados corretos."
            ),
        },
        {
            "name": "Cancelamento ou substituição de NF já emitida",
            "pct": 7,
            "case_ids": ["455879792", "449456347", "452302610"],
            "summary": (
                "Sellers precisam cancelar ou substituir NF-e já emitida por dados "
                "incorretos (CPF/CNPJ do comprador, valor, produto) e não conseguem "
                "realizar o processo pelo faturador."
            ),
        },
    ],
    ("Emision de Nota Fiscal", "Emissor externo"): [
        {
            "name": "XML de emissor externo (ERP/Bling/Tiny) rejeitado pelo Mercado Livre",
            "pct": 35,
            "case_ids": ["441428470", "438099472", "448651118"],
            "summary": (
                "Sellers que emitem NF-e pelo ERP ou emissor externo (Bling, Tiny, Omie) "
                "não conseguem fazer o upload do XML — o arquivo é recusado ou a venda "
                "continua com status 'aguardando nota fiscal'."
            ),
        },
        {
            "name": "Divergência entre valor da NF emitida e valor real da venda",
            "pct": 25,
            "case_ids": ["443749160", "446131198", "449244979"],
            "summary": (
                "O valor total da NF-e emitida pelo ERP diverge do valor registrado na "
                "venda do Mercado Livre — geralmente por desconto ou cupom não refletido "
                "no XML."
            ),
        },
        {
            "name": "IE do destinatário inválida ou não cadastrada bloqueando emissão",
            "pct": 18,
            "case_ids": ["453147656", "449083998", "454754309"],
            "summary": (
                "A NF-e é rejeitada pela SEFAZ com erro de IE do destinatário inválida "
                "ou não cadastrada — situação comum em vendas para PJ com IE irregular."
            ),
        },
        {
            "name": "Como baixar XML e NF-e do Full no sistema externo",
            "pct": 12,
            "case_ids": ["448589066", "435900289", "451169828"],
            "summary": (
                "Sellers que vendem pelo Full buscam orientação para baixar os XMLs das "
                "NF-e emitidas automaticamente pela plataforma e integrá-los ao ERP próprio."
            ),
        },
        {
            "name": "Configuração de endereço e dados do emitente no emissor externo",
            "pct": 10,
            "case_ids": ["448883901", "436727610", "438992300"],
            "summary": (
                "O emissor externo está configurado com endereço ou dados fiscais "
                "diferentes do registrado na SEFAZ, gerando rejeições na emissão da NF-e "
                "para vendas do Mercado Livre."
            ),
        },
    ],
    ("Emision de Nota Fiscal", "Optin"): [
        {
            "name": "Ativação do faturador MeLi (pré-requisitos, certificado A1, passo a passo)",
            "pct": 38,
            "case_ids": ["453926604", "448660294", "443011009"],
            "summary": (
                "Sellers tentam ativar o faturador gratuito do Mercado Livre para emissão "
                "automática de NF-e, mas encontram dificuldades com os pré-requisitos: "
                "PJ, certificado A1 e CNPJ credenciado na SEFAZ."
            ),
        },
        {
            "name": "Credenciamento CNPJ/SEFAZ incompleto ou não reconhecido pelo ML",
            "pct": 28,
            "case_ids": ["441479018", "452207784", "449932099"],
            "summary": (
                "O CNPJ foi credenciado na SEFAZ mas o Mercado Livre ainda não reconhece "
                "o credenciamento — o sistema continua exibindo 'CNPJ não habilitado', "
                "impedindo a emissão de NF-e."
            ),
        },
        {
            "name": "Configuração de série exclusiva para NF-e no faturador",
            "pct": 15,
            "case_ids": ["441401029", "444328504", "448643486"],
            "summary": (
                "O faturador exige uma série de NF-e exclusiva para vendas no Mercado "
                "Livre, diferente da série usada no ERP externo, para evitar conflitos "
                "de numeração."
            ),
        },
        {
            "name": "Desativação ou inativação do emissor de NF-e",
            "pct": 10,
            "case_ids": ["438965586", "443697967", "445092679"],
            "summary": (
                "Sellers que não querem mais usar o faturador do Mercado Livre buscam "
                "como desativar a emissão automática de NF-e ou remover o certificado "
                "digital da plataforma."
            ),
        },
        {
            "name": "Anúncios pausados por opt-in fiscal pendente",
            "pct": 9,
            "case_ids": ["444897407", "446589739", "448825976"],
            "summary": (
                "Anúncios são desativados pelo Mercado Livre porque o opt-in de emissão "
                "de NF-e ainda não foi concluído, exigindo que o seller complete o "
                "credenciamento para reativar as publicações."
            ),
        },
    ],
    ("Emision de Nota Fiscal", "Error en el facturador o anexar XML"): [
        {
            "name": "NF-e pendente por instabilidade SEFAZ — etiqueta bloqueada",
            "pct": 35,
            "case_ids": ["452054417", "449324494", "449042479"],
            "summary": (
                "A NF-e fica com status 'pendente' ou 'processando' por instabilidade "
                "entre o sistema do Mercado Livre e a SEFAZ, bloqueando a liberação da "
                "etiqueta de envio."
            ),
        },
        {
            "name": "Rejeição de NF-e por NCM incorreto ou obrigatório ausente",
            "pct": 25,
            "case_ids": ["445517003", "451760725", "436757607"],
            "summary": (
                "A emissão é rejeitada porque o NCM do produto está ausente, inválido "
                "ou não corresponde ao produto real — exige correção no cadastro do "
                "anúncio antes de reemitir."
            ),
        },
        {
            "name": "Rejeição por IE do emitente ou destinatário inválida",
            "pct": 20,
            "case_ids": ["449083998", "455432285", "450648033"],
            "summary": (
                "A SEFAZ rejeita a NF-e informando que a Inscrição Estadual do emitente "
                "ou do destinatário está inválida, inexistente ou diverge do CNPJ cadastrado."
            ),
        },
        {
            "name": "Erro ao anexar XML de emissor externo — venda bloqueada",
            "pct": 12,
            "case_ids": ["447939394", "448119407", "441748928"],
            "summary": (
                "Sellers que emitem NF-e fora da plataforma não conseguem anexar o XML "
                "à venda no Mercado Livre — o arquivo é recusado e a etiqueta não é "
                "liberada para envio."
            ),
        },
        {
            "name": "NF não reconhecida pelo ML após emissão no ERP",
            "pct": 8,
            "case_ids": ["448592335", "450602646", "436068408"],
            "summary": (
                "A NF-e foi emitida no ERP e autorizada pela SEFAZ, mas o Mercado Livre "
                "ainda mostra a venda como 'aguardando nota fiscal' e não libera a etiqueta."
            ),
        },
    ],
    ("Emision de Nota Fiscal", "Temporal"): [
        {
            "name": "NCM incorreto, inválido ou obrigatório bloqueando emissão de NF",
            "pct": 35,
            "case_ids": ["440879541", "438452710", "436757607"],
            "summary": (
                "A emissão de NF-e é bloqueada porque o NCM do produto está ausente, "
                "inválido para o estado ou precisa ser atualizado após mudança na tabela "
                "da SEFAZ (ex.: reforma tributária)."
            ),
        },
        {
            "name": "NF-e automática do Full com dados divergentes (peso, quantidade, valor)",
            "pct": 25,
            "case_ids": ["453767268", "455358449", "455813230"],
            "summary": (
                "O Full emite NF-e automaticamente com peso bruto/líquido, quantidade "
                "ou valor divergentes do pedido real, gerando inconsistências fiscais "
                "que o seller precisa corrigir."
            ),
        },
        {
            "name": "Instabilidade na emissão — NF pendente aguardando SEFAZ",
            "pct": 20,
            "case_ids": ["449200234", "448858307", "439349361"],
            "summary": (
                "A NF-e fica com status 'pendente' por instabilidade no sistema fiscal, "
                "impedindo a impressão da etiqueta de envio enquanto a SEFAZ não autoriza "
                "o documento."
            ),
        },
        {
            "name": "Configuração de regras tributárias e planilha fiscal",
            "pct": 12,
            "case_ids": ["436569415", "439066379", "450610410"],
            "summary": (
                "Sellers precisam configurar ou atualizar a planilha tributária da conta "
                "para vincular regras fiscais corretas aos anúncios e habilitar a emissão "
                "automática de NF-e."
            ),
        },
        {
            "name": "Cancelamento ou correção de NF-e já emitida",
            "pct": 8,
            "case_ids": ["452304416", "446334383", "439102772"],
            "summary": (
                "Sellers precisam cancelar ou corrigir NF-e já emitida por dados errados "
                "(NCM, valor, quantidade) mas enfrentam restrições no faturador ou prazo "
                "de cancelamento expirado."
            ),
        },
    ],
}

# ── Theme analysis via TF-IDF + KMeans ──────────────────────────────────────
def analyze_themes(
    case_transcripts: dict[str, list[str]],
    top_cdu: str,
    proc_label: str,
    total_cases: int,
    n_themes: int = 5,
) -> list[dict]:
    """Clusteriza transcrições em temas usando TF-IDF + KMeans (sem API externa)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    import numpy as np

    case_list = list(case_transcripts.items())[:300]
    case_ids  = [c[0] for c in case_list]

    # Padrões de ruído a remover antes do TF-IDF
    _NOISE = [
        re.compile(r"recipient\s*:\s*%\w+\.?\s*email\s*:", re.I),  # cabeçalhos de email
        re.compile(r"andamento\s*:\s*tramite.*?descri[çc][aã]o\s*:", re.DOTALL | re.I),
        re.compile(r"tipo\s+de\s+intera[çc][aã]o\s*:.*?hora\s*:", re.DOTALL | re.I),
        re.compile(r"%\w+"),                      # %num %date %hour %email %url
        re.compile(r"\bsilence\b.*?\bseconds?\b", re.I),
        re.compile(r"\bof\s+seconds?\b", re.I),
        re.compile(r"\brecipient\b", re.I),
        re.compile(r"\bemail\b", re.I),
        re.compile(r"\bwww\S+|\bhttp\S+"),
        re.compile(r"\b(sao|sou|meu|nome|chamo|representante|mercado livre|espero|esteja|bem|hoje|obrigad\w*|agradeç\w*|atend\w*|auxili\w*)\b", re.I),
    ]

    def clean_text(txt: str) -> str:
        for p in _NOISE:
            txt = p.sub(" ", txt)
        txt = re.sub(r"[^a-záéíóúàâêôãõç\s]", " ", txt.lower())
        return re.sub(r"\s+", " ", txt).strip()

    # Texto por caso: até 4 mensagens, limpar
    texts = []
    for _, msgs in case_list:
        combined = " ".join(m.strip() for m in msgs[:4])
        texts.append(clean_text(combined))

    n = min(n_themes, len(texts))
    if n < 2:
        return []

    # TF-IDF com bigramas, ignorando stopwords do projeto
    vect = TfidfVectorizer(
        max_features=1500,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.90,
        stop_words=list(STOPWORDS),
        sublinear_tf=True,
    )
    try:
        X = vect.fit_transform(texts)
    except ValueError:
        return []

    km = KMeans(n_clusters=n, random_state=42, n_init=10, max_iter=300)
    labels = km.fit_predict(X)
    feat   = vect.get_feature_names_out()

    themes = []
    for cid in range(n):
        mask     = np.array(labels) == cid
        c_ids    = [case_ids[i] for i, m in enumerate(mask) if m]
        count    = int(mask.sum())
        pct      = int(round(count / len(texts) * 100))
        if count == 0:
            continue

        # Top termos do centróide (excluindo stopwords curtos)
        center   = km.cluster_centers_[cid]
        top_idx  = center.argsort()[-15:][::-1]
        top_terms = [feat[i] for i in top_idx
                     if feat[i] not in STOPWORDS and len(feat[i]) >= 4]

        bigrams   = [t for t in top_terms if " " in t][:3]
        unigrams  = [t for t in top_terms if " " not in t][:4]

        # Nome do tema: preferir bigramas (mais descritivos)
        name_parts = (bigrams[:2] + unigrams[:2]) if bigrams else unigrams[:3]
        name = " · ".join(name_parts[:3]).title()

        # Resumo baseado nos termos dominantes
        all_terms = (bigrams + unigrams)[:5]
        summary = (
            f"Casos concentrados em: {', '.join(all_terms[:4])}. "
            f"{count} atendimentos no período analisado."
        )

        themes.append({
            "name":     name,
            "pct":      pct,
            "case_ids": c_ids[:3],
            "summary":  summary,
        })

    themes.sort(key=lambda x: x["pct"], reverse=True)
    return themes

# ── Data processing ──────────────────────────────────────────────────────────
def month_label(ym: str) -> str:
    return MES_PT.get(ym.split("-")[1], ym)

SEM_CDU = "Sem CDU"

def _build_datasets(top_cdus, by_cdu, keys, sem_cdu_data, all_rows, key_field):
    """Monta datasets: top CDUs com CDU real + 'Sem CDU' + 'Outros' ao final."""
    datasets = []
    for cdu in top_cdus:
        datasets.append({"label": cdu,
                         "data": [by_cdu.get(cdu, {}).get(k, 0) for k in keys]})
    # "Sem CDU" como faixa dedicada
    if any(v > 0 for v in sem_cdu_data):
        datasets.append({"label": SEM_CDU, "data": sem_cdu_data})
    # "Outros" = com CDU mas fora do top N
    outros = [
        sum(r["volume"] for r in all_rows if r[key_field] == k
            and r["cdu"] not in top_cdus and r["cdu"] != SEM_CDU)
        for k in keys
    ]
    if any(v > 0 for v in outros):
        datasets.append({"label": "Outros", "data": outros})
    return datasets

def process_monthly(raw: list[dict]) -> dict:
    result = {}
    for proc_key in PROCESSES:
        rows = [r for r in raw if r["process"] == proc_key]
        months_sorted = sorted(set(r["month"] for r in rows))

        cdu_totals: Counter = Counter()
        by_cdu: dict = {}
        for r in rows:
            cdu = r["cdu"]
            cdu_totals[cdu] += r["volume"]
            by_cdu.setdefault(cdu, {})[r["month"]] = r["volume"]

        # top CDUs excluindo "Sem CDU" (vai como faixa separada)
        top_cdus = [c for c, _ in cdu_totals.most_common()
                    if c != SEM_CDU][:TOP_CDUS]
        top_cdu  = top_cdus[0] if top_cdus else None

        sem_cdu_data = [by_cdu.get(SEM_CDU, {}).get(m, 0) for m in months_sorted]
        datasets = _build_datasets(top_cdus, by_cdu, months_sorted,
                                   sem_cdu_data, rows, "month")

        result[proc_key] = {
            "months":     [month_label(m) for m in months_sorted],
            "top_cdus":   top_cdus,
            "top_cdu":    top_cdu,
            "datasets":   datasets,
            "cdu_totals": {k: v for k, v in cdu_totals.items() if k != SEM_CDU},
            "sem_cdu_vol": cdu_totals.get(SEM_CDU, 0),
            "total_vol":   sum(cdu_totals.values()),
        }
    return result

def process_weekly(raw: list[dict]) -> dict:
    result = {}
    for proc_key in PROCESSES:
        rows = [r for r in raw if r["process"] == proc_key]
        weeks_sorted = sorted(set(r["week_start"] for r in rows))
        weeks_labels = [w.strftime("%d/%m") for w in weeks_sorted]

        cdu_totals: Counter = Counter()
        by_cdu: dict = {}
        for r in rows:
            cdu = r["cdu"]
            cdu_totals[cdu] += r["volume"]
            by_cdu.setdefault(cdu, {})[r["week_start"]] = r["volume"]

        top_cdus = [c for c, _ in cdu_totals.most_common()
                    if c != SEM_CDU][:TOP_CDUS]

        sem_cdu_data = [by_cdu.get(SEM_CDU, {}).get(w, 0) for w in weeks_sorted]
        datasets = _build_datasets(top_cdus, by_cdu, weeks_sorted,
                                   sem_cdu_data, rows, "week_start")

        result[proc_key] = {
            "weeks":    weeks_labels,
            "top_cdus": top_cdus,
            "datasets": datasets,
        }
    return result

CACHE_MAX_AGE_H = 24  # horas antes de re-consultar o BQ

def _cache_path(proc_key: str, cdu: str = "") -> str:
    safe_p = proc_key.replace(" ", "_").replace("/", "_")
    if cdu:
        safe_c = re.sub(r"[^a-zA-Z0-9]", "_", cdu)[:30]
        return f"_tr_cache_{safe_p}_{safe_c}.json"
    return f"_tr_cache_{safe_p}.json"

def _load_cache(proc_key: str, cdu: str = "") -> dict | None:
    import time as _t
    path = _cache_path(proc_key, cdu)
    if not os.path.exists(path):
        return None
    age_h = (_t.time() - os.path.getmtime(path)) / 3600
    if age_h > CACHE_MAX_AGE_H:
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    print(f"   [cache] {path} ({age_h:.1f}h)")
    return data

def _save_cache(proc_key: str, data: dict, cdu: str = "") -> None:
    path = _cache_path(proc_key, cdu)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"   [cache] salvo {path}")

def fetch_analysis(proc_key: str, cdu: str) -> list[dict]:
    """Retorna temas para um CDU.
    Prioridade: 1) curado manual, 2) cache local + TF-IDF, 3) BQ + TF-IDF."""
    if not cdu:
        return []

    # 1) Curado manual
    curated = CURATED_THEMES.get((proc_key, cdu))
    if curated:
        print(f"   [curado] '{cdu}': {len(curated)} temas")
        return curated

    # 2) Cache local
    cached = _load_cache(proc_key, cdu)
    if cached is None:
        print(f"   [BQ] '{cdu}': buscando case IDs…")
        try:
            raw_ids = run(q_case_ids(proc_key, cdu))
            ids = [str(int(r["CAS_CASE_ID"])) for r in raw_ids if r.get("CAS_CASE_ID") is not None]
        except Exception as e:
            print(f"   [quota] '{cdu}' ignorado: {e}")
            return []
        if not ids:
            return []

        print(f"   [BQ] '{cdu}': {len(ids)} casos, buscando transcrições…")
        case_transcripts: dict[str, list[str]] = {}
        try:
            for i in range(0, len(ids), 1000):
                rows = run(q_transcripts_with_case(ids[i:i + 1000]))
                for r in rows:
                    cid, msg = r.get("case_id"), r.get("msg")
                    if cid and msg:
                        case_transcripts.setdefault(cid, []).append(msg)
            _save_cache(proc_key, case_transcripts, cdu)
        except Exception as e:
            print(f"   [quota] transcrições de '{cdu}' ignoradas: {e}")
            return []
    else:
        case_transcripts = cached

    proc_label = PROCESSES[proc_key]
    themes = analyze_themes(case_transcripts, cdu, proc_label, len(case_transcripts))
    print(f"   [TF-IDF] '{cdu}': {len(themes)} temas")
    return themes

CHARTS_CACHE = "_cache_charts.json"

def _save_charts_cache(monthly: dict, weekly: dict) -> None:
    """Serializa monthly/weekly para disco (valores date → str)."""
    def convert(obj):
        import datetime
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return obj

    payload = {"monthly": monthly, "weekly": weekly}
    # weekly tem week_start como date nos datasets — já estão como strings nos labels
    with open(CHARTS_CACHE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, default=convert)
    print(f"[cache] gráficos salvos em {CHARTS_CACHE}")

def _load_charts_cache():
    if not os.path.exists(CHARTS_CACHE):
        return None, None
    with open(CHARTS_CACHE, encoding="utf-8") as f:
        p = json.load(f)
    print(f"[cache] gráficos carregados de {CHARTS_CACHE}")
    return p["monthly"], p["weekly"]

def build_all(html_only: bool = False):
    if html_only:
        print("▸ Modo --html-only: usando cache de gráficos…")
        monthly, weekly = _load_charts_cache()
        if monthly is None:
            raise RuntimeError("Cache de gráficos não encontrado. Rode sem --html-only primeiro.")
    else:
        print("▸ Volume mensal…")
        monthly_raw = run(q_monthly())
        print("▸ Volume semanal (8 semanas)…")
        weekly_raw  = run(q_weekly())
        monthly = process_monthly(monthly_raw)
        weekly  = process_weekly(weekly_raw)
        _save_charts_cache(monthly, weekly)

    # Para cada processo, roda fetch_analysis para TODOS os top CDUs
    themes_by_cdu: dict[str, dict[str, list]] = {}
    for proc_key, proc_label in PROCESSES.items():
        top_cdus = monthly[proc_key]["top_cdus"]
        themes_by_cdu[proc_key] = {}
        print(f"\n▸ Análise temática [{proc_label}] ({len(top_cdus)} CDUs)…")
        for cdu in top_cdus:
            themes_by_cdu[proc_key][cdu] = fetch_analysis(proc_key, cdu)

    return monthly, weekly, themes_by_cdu

# ── HTML helpers ─────────────────────────────────────────────────────────────
def jd(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)

SEM_CDU_COLOR = "#D0D0D0"   # cinza claro — "Sem CDU"

def palette_for(datasets: list[dict]) -> list[str]:
    out = []
    idx = 0
    for ds in datasets:
        if ds["label"] == "Outros":
            out.append(OUTROS_COLOR)
        elif ds["label"] == SEM_CDU:
            out.append(SEM_CDU_COLOR)
        else:
            out.append(PALETTE[idx % len(PALETTE)])
            idx += 1
    return out

ACCENT_COLORS = ["#4472C4", "#ED7D31", "#70AD47", "#E05252", "#9B59B6"]

def _render_theme_cards_html(themes: list[dict]) -> str:
    """Renderiza os cards de temas diretamente em HTML (sem JS)."""
    if not themes:
        return '<p class="no-data">Análise não disponível para este CDU — execute o script para gerar os temas.</p>'
    cards = ""
    for i, t in enumerate(themes):
        color  = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        chips  = "".join(f'<span class="case-chip">#{c}</span>' for c in t.get("case_ids", []))
        cards += (
            f'<div class="theme-card" style="border-left-color:{color}">'
            f'<div class="tc-header">'
            f'<span class="tc-name">{t.get("name","—")}</span>'
            f'<span class="tc-badge" style="background:{color}22;color:{color}">'
            f'{t.get("pct",0)}% dos casos</span>'
            f'</div>'
            f'<p class="tc-summary">{t.get("summary","")}</p>'
            f'<div class="tc-chips">{chips}</div>'
            f'</div>'
        )
    return f'<div class="themes-list">{cards}</div>'

def make_themes_section(idx: int, cdu_themes: dict[str, list], top_cdu: str) -> str:
    """Gera o card de análise com <select> de CDU.
    Conteúdo inicial renderizado em Python; trocas via JS."""
    options = "".join(
        f'<option value="{cdu}"{" selected" if cdu == top_cdu else ""}>{cdu}</option>'
        for cdu in cdu_themes
    )
    # Renderiza HTML inicial do top CDU diretamente (não depende de JS)
    initial_html = _render_theme_cards_html(cdu_themes.get(top_cdu, []))

    return f"""
    <div class="th-hdr">
      <div class="th-title-row">
        <span class="th-label">Análise de Transcrições · CDU:</span>
        <select class="cdu-sel" id="sel{idx}" onchange="selectCDU({idx},this.value)">
          {options}
        </select>
      </div>
      <span class="th-sub">Motivos de contato identificados (últimos {TRANSCRIPT_DAYS} dias)</span>
    </div>
    <div id="themes{idx}">{initial_html}</div>"""

def make_tab(idx: int, proc_key: str, proc_label: str,
             monthly: dict, weekly: dict,
             cdu_themes: dict[str, list]) -> tuple[str, str]:
    """Returns (tab_html, chart_js_body)"""
    m  = monthly[proc_key]
    w  = weekly[proc_key]
    mi = f"cM{idx}"   # canvas id monthly
    wi = f"cW{idx}"   # canvas id weekly
    active = "active" if idx == 0 else ""

    top_cdu   = m["top_cdu"] or "—"
    total_v   = m["total_vol"]           # inclui Sem CDU
    named_v   = sum(m["cdu_totals"].values())  # só com CDU identificado
    sem_cdu_v = m["sem_cdu_vol"]
    top_vol   = m["cdu_totals"].get(top_cdu, 0)
    top_pct   = f"{top_vol / total_v * 100:.1f}%" if total_v else "—"

    rows_html = ""
    for i, cdu in enumerate(m["top_cdus"][:8]):
        vol  = m["cdu_totals"].get(cdu, 0)
        pct  = f"{vol / total_v * 100:.1f}%" if total_v else "—"
        star = "⭐ " if i == 0 else f"{i+1}. "
        rc   = ' class="tr0"' if i == 0 else ""
        rows_html += (
            f'<tr{rc}><td>{star}{cdu}</td>'
            f'<td class="vn">{vol:,}</td>'
            f'<td class="vp">{pct}</td></tr>'
        )
    # linha Sem CDU ao final da tabela
    sem_pct = f"{sem_cdu_v / total_v * 100:.1f}%" if total_v else "—"
    rows_html += (
        f'<tr class="sem-cdu-row"><td>— Sem CDU</td>'
        f'<td class="vn">{sem_cdu_v:,}</td>'
        f'<td class="vp">{sem_pct}</td></tr>'
    )

    themes_html = make_themes_section(idx, cdu_themes, top_cdu)

    tab_html = f"""
  <div class="tab-pane {active}" id="tp{idx}">
    <div class="grid2">
      <div class="card chart-card">
        <p class="chart-title">Volume mensal por CDU</p>
        <div class="cw" style="height:320px"><canvas id="{mi}"></canvas></div>
      </div>
      <div class="card chart-card">
        <p class="chart-title">Volume semanal por CDU · últimas 8 semanas</p>
        <div class="cw" style="height:320px"><canvas id="{wi}"></canvas></div>
      </div>
    </div>

    <div class="card hl-card">
      <div class="hl-box">
        <div class="hl-lbl">CDU com Maior Volume</div>
        <div class="hl-val">{top_cdu}</div>
        <div class="hl-sub">{top_vol:,} atendimentos · {top_pct} do total identificado</div>
        <div class="hl-sub2">Total outgoing: {total_v:,} · Com CDU: {named_v:,} ({named_v/total_v*100:.0f}%)</div>
      </div>
      <div class="hl-right">
        <table class="rtable">
          <thead><tr><th>CDU</th><th>Volume</th><th>%</th></tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </div>

    <div class="card">{themes_html}</div>
  </div>"""

    # Chart JS
    m_colors = palette_for(m["datasets"])
    m_ds = ",".join(
        f"{{label:{jd(ds['label'])},data:{jd(ds['data'])},"
        f"backgroundColor:{jd(m_colors[i])},borderRadius:4,stack:'s'}}"
        for i, ds in enumerate(m["datasets"])
    )
    w_colors = palette_for(w["datasets"])
    w_ds = ",".join(
        f"{{label:{jd(ds['label'])},data:{jd(ds['data'])},"
        f"backgroundColor:{jd(w_colors[i])},borderRadius:4,stack:'s'}}"
        for i, ds in enumerate(w["datasets"])
    )

    js = f"""
  initFns[{idx}] = function() {{
    bar('{mi}', {jd(m['months'])}, [{m_ds}]);
    bar('{wi}', {jd(w['weeks'])},  [{w_ds}]);
  }};"""

    return tab_html, js

# ── HTML template ─────────────────────────────────────────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:#f0f2f5;color:#1a1a2e;min-height:100vh}

/* ── Header ── */
.hd{background:linear-gradient(135deg,#ffe600,#f5c800);
    padding:14px 28px;display:flex;align-items:center;gap:14px;
    box-shadow:0 2px 8px rgba(0,0,0,.12)}
.logo{background:#1a1a2e;color:#ffe600;font-weight:900;font-size:13px;
      border-radius:7px;padding:5px 10px;letter-spacing:-.5px;line-height:1.2}
.hd h1{font-size:15px;font-weight:800;color:#1a1a2e}
.hd p{font-size:11px;color:#555;margin-top:2px}

/* ── Layout ── */
.main{max-width:1200px;margin:0 auto;padding:22px 18px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}

/* ── Tabs ── */
.tab-nav{display:flex;gap:3px;background:#fff;border-radius:10px;
         padding:4px;width:fit-content;margin-bottom:18px;
         box-shadow:0 1px 4px rgba(0,0,0,.08)}
.tab-btn{border:none;background:transparent;border-radius:7px;
         padding:8px 22px;font-size:13px;font-weight:600;color:#666;
         cursor:pointer;transition:all .15s}
.tab-btn.active{background:#ffe600;color:#1a1a2e;
                box-shadow:0 1px 4px rgba(0,0,0,.1)}
.tab-pane{display:none;flex-direction:column;gap:18px}
.tab-pane.active{display:flex}

/* ── Cards ── */
.card{background:#fff;border-radius:12px;padding:20px;
      box-shadow:0 1px 4px rgba(0,0,0,.07)}
.chart-card{}
.chart-title{font-size:12px;font-weight:700;color:#444;
             text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px}
.cw{position:relative}

/* ── Highlight card ── */
.hl-card{display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:start}
@media(max-width:680px){.hl-card{grid-template-columns:1fr}}
.hl-box{background:linear-gradient(135deg,#ffe600,#f5c800);border-radius:10px;
        padding:20px 24px;text-align:center;min-width:240px}
.hl-lbl{font-size:10px;font-weight:700;text-transform:uppercase;
        letter-spacing:1px;color:#666;margin-bottom:8px}
.hl-val{font-size:17px;font-weight:900;color:#1a1a2e;margin-bottom:6px;
        line-height:1.2}
.hl-sub{font-size:11px;color:#555}
.hl-sub2{font-size:10px;color:#888;margin-top:4px}

/* ── Ranking table ── */
.rtable{width:100%;border-collapse:collapse;font-size:12px}
.rtable th{background:#f8f9fa;padding:7px 12px;text-align:left;font-weight:700;
           color:#888;text-transform:uppercase;font-size:10px;letter-spacing:.6px;
           border-bottom:1px solid #eee}
.rtable td{padding:7px 12px;border-bottom:1px solid #f5f5f5;vertical-align:middle}
.rtable .tr0{background:#fffde7;font-weight:600}
.rtable .sem-cdu-row{color:#aaa;font-style:italic;border-top:1px solid #eee}
.hl-right{display:flex;flex-direction:column;gap:14px}
.vn{text-align:right;font-variant-numeric:tabular-nums}
.vp{text-align:right;color:#888}
/* ── Themes ── */
.no-data{font-size:12px;color:#999;padding:8px 0}
.th-hdr{margin-bottom:16px}
.th-title-row{display:flex;align-items:baseline;gap:6px;flex-wrap:wrap;margin-bottom:3px}
.th-label{font-size:13px;font-weight:700;white-space:nowrap}
.cdu-sel{font-size:14px;font-weight:800;color:#c89600;background:transparent;
         border:none;border-bottom:2px solid #e8b000;cursor:pointer;padding:0 4px 1px;
         outline:none;font-family:inherit;max-width:480px}
.cdu-sel:focus{border-bottom-color:#4472C4}
.cdu-sel option{color:#1a1a2e;font-weight:600;background:#fff}
.th-sub{font-size:11px;color:#888;display:block}
.themes-list{display:flex;flex-direction:column;gap:12px}
.theme-card{border-left:3px solid #ccc;padding:13px 16px;
            background:#fafafa;border-radius:0 8px 8px 0}
.tc-header{display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap}
.tc-name{font-size:13px;font-weight:700;color:#1a1a2e}
.tc-badge{font-size:11px;font-weight:700;padding:2px 10px;border-radius:20px;white-space:nowrap}
.tc-summary{font-size:12px;color:#555;line-height:1.55;margin-bottom:8px}
.tc-chips{display:flex;flex-wrap:wrap;gap:6px}
.case-chip{font-size:11px;font-family:monospace;background:#eef2ff;
           color:#4472C4;padding:2px 9px;border-radius:12px}
"""

def generate_html(monthly: dict, weekly: dict, themes_by_cdu: dict) -> str:
    now_str = TODAY.strftime("%d/%m/%Y")
    tab_btns  = []
    tab_panes = []
    chart_jss = []

    for idx, (proc_key, proc_label) in enumerate(PROCESSES.items()):
        active = "active" if idx == 0 else ""
        tab_btns.append(
            f'<button class="tab-btn {active}" onclick="go({idx})">{proc_label}</button>'
        )
        pane, js = make_tab(
            idx, proc_key, proc_label,
            monthly, weekly,
            themes_by_cdu.get(proc_key, {})
        )
        tab_panes.append(pane)
        chart_jss.append(js)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Volume Outgoing por CDU | Facturación &amp; Emissão NF | MLB</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>{CSS}</style>
</head>
<body>

<header class="hd">
  <div class="logo">ML</div>
  <div>
    <h1>Volume Outgoing por CDU — Facturación &amp; Emissão de Nota Fiscal</h1>
    <p>MLB · Jan–Mai 2026 · Fonte: DM_CX_OUTGOING_GESTION_DETAIL · Atualizado em {now_str}</p>
  </div>
</header>

<main class="main">
  <nav class="tab-nav">{''.join(tab_btns)}</nav>
  {''.join(tab_panes)}
</main>

<script>
const initFns = [];

function bar(id, labels, datasets) {{
  new Chart(document.getElementById(id), {{
    type: 'bar',
    data: {{ labels, datasets }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{
          position: 'bottom',
          labels: {{ boxWidth: 12, padding: 10, font: {{ size: 11 }} }}
        }},
        tooltip: {{
          callbacks: {{
            label: ctx =>
              ` ${{ctx.dataset.label}}: ${{ctx.parsed.y.toLocaleString('pt-BR')}} atendimentos`
          }}
        }}
      }},
      scales: {{
        x: {{ stacked: true, grid: {{ display: false }},
              ticks: {{ font: {{ size: 11 }} }} }},
        y: {{ stacked: true, grid: {{ color: '#f0f2f5' }},
              ticks: {{ font: {{ size: 11 }},
                        callback: v => v.toLocaleString('pt-BR') }} }}
      }}
    }}
  }});
}}

function go(n) {{
  document.querySelectorAll('.tab-btn').forEach((b, i) =>
    b.classList.toggle('active', i === n));
  document.querySelectorAll('.tab-pane').forEach((p, i) =>
    p.classList.toggle('active', i === n));
  if (initFns[n]) {{ initFns[n](); initFns[n] = null; }}
}}

// ── CDU selector ──────────────────────────────────────────────────────────
const ACCENT = {jd(ACCENT_COLORS)};

const ALL_THEMES = {jd({str(i): {cdu: t for cdu, t in themes_by_cdu.get(proc_key, {}).items()}
    for i, proc_key in enumerate(PROCESSES)})};

function buildThemeCard(t, i) {{
  const c = ACCENT[i % ACCENT.length];
  const chips = (t.case_ids||[]).map(id=>`<span class="case-chip">#${{id}}</span>`).join('');
  return `<div class="theme-card" style="border-left-color:${{c}}">
    <div class="tc-header">
      <span class="tc-name">${{t.name}}</span>
      <span class="tc-badge" style="background:${{c}}22;color:${{c}}">${{t.pct}}% dos casos</span>
    </div>
    <p class="tc-summary">${{t.summary}}</p>
    <div class="tc-chips">${{chips}}</div>
  </div>`;
}}

function renderThemes(tabIdx, cdu) {{
  const themes = (ALL_THEMES[tabIdx]||{{}})[cdu] || [];
  const el = document.getElementById('themes'+tabIdx);
  if (!el) return;
  if (!themes.length) {{
    el.innerHTML = '<p class="no-data">Análise não disponível para este CDU — execute o script para gerar os temas.</p>';
  }} else {{
    el.innerHTML = '<div class="themes-list">'+themes.map((t,i)=>buildThemeCard(t,i)).join('')+'</div>';
  }}
}}

function selectCDU(tabIdx, cdu) {{ renderThemes(tabIdx, cdu); }}

{''.join(chart_jss)}

// Init aba 0 imediatamente
if (initFns[0]) {{ initFns[0](); initFns[0] = null; }}
</script>
</body>
</html>"""

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys as _sys
    html_only = "--html-only" in _sys.argv
    try:
        monthly, weekly, themes_by_cdu = build_all(html_only=html_only)
        html = generate_html(monthly, weekly, themes_by_cdu)
        out  = "outgoing_cdu_analysis.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n✓ Gerado: {out}")
    except Exception as e:
        print(f"\nERRO: {e}")
        raise
