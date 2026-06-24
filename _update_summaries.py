#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injeta executive_analysis MoM (mom bucket) em dd_summaries.json para 5 drivers."""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open("dd_summaries.json", encoding="utf-8") as f:
    s = json.load(f)

def ensure_mom(driver):
    if driver not in s:
        s[driver] = {}
    m = s[driver].get("mom", {})
    if isinstance(m, str):
        s[driver]["mom"] = {"bullets_legado": m}
    elif not isinstance(m, dict):
        s[driver]["mom"] = {}

def ea_mom(drv, **kw):
    ensure_mom(drv)
    s[drv]["mom"]["executive_analysis"] = kw

# ── ME VENDEDOR SELLER DEV — MoM ──────────────────────────────────────────────
ea_mom("ME Vendedor Seller Dev",
  periodo="MoM: Marco 2026 vs Abril 2026",
  resumo_executivo=(
    "ME Vendedor Seller Dev fechou Abril com NPS de 68.2% (+1.1pp MoM vs Marco 67.1%), "
    "10.4pp acima do target de 57.8% — quinto mes consecutivo acima da meta. Volume mensal "
    "de 6.196 surveys (+2.1% vs Marco). A melhora mensal foi modesta mas consistente, sustentada "
    "por Reputacao ME (NPS 82.9% em Abril). Dois movimentos a monitorar: (1) CDU 'Desativar ME' "
    "caiu 14.9pp MoM (85.3%→70.4%) — tendencia de deterioracao que se acelerou na semana; "
    "(2) CDU 'Reputacao ME Vendas: Logistica Places' reverteu de negativo para +34.8% NPS, "
    "sinalizando melhora de qualidade no segmento de integracao com Places."
  ),
  destaques_positivos=[
    "MoM +1.1pp: evolucao consistente — quinto mes acima do target",
    "Acima do target em +10.4pp — maior margem de seguranca no historico recente",
    "CDU Reputacao ME Vendas Logistica Places reverteu: de -13.2% para +34.8% NPS (+48pp MoM)",
    "Volume +2.1% MoM: crescimento saudavel sem diluicao de qualidade",
    "Reputacao ME mantém lideranca: NPS 82.9% e processo mais promotor do driver",
  ],
  destaques_negativos=[
    "CDU Desativar ME -14.9pp MoM (85.3%→70.4%): deterioracao acumulada com aceleracao na semana",
    "Despacho Ventas y Publicacoes (maior processo por volume apos Rep. ME) ainda abaixo do otimo",
    "Melhora mensal de +1.1pp e modesta versus o potencial do driver — ainda ha aceleracao possivel",
    "Sem dados de senioridade comparativos MoM disponiveis neste relatorio",
  ],
  impacto_estrategico=(
    "CLIENTE: O driver e o maior responsavel pela experiencia de Sellers com o Mercado Envios — "
    "qualquer deterioracao tem impacto direto no ecossistema de vendas. "
    "OPERACAO: Tendencia de queda em Desativar ME ao longo do mes exige correcao sistemica. "
    "MARCA: Reputacao ME com NPS alto sustenta a percepcao de qualidade do servico ME junto a vendedores. "
    "EFICIENCIA: O CDU Logistica Places subiu 48pp — validar se mudanca operacional sustenta a melhora."
  ),
  voc_positivos=(
    "Padrao mensal de promotores: resolucao rapida, agentes com conhecimento do processo e clareza "
    "na comunicacao de status de envio. Reputacao ME e o processo com maior reconhecimento de qualidade "
    "pelos vendedores — NPS 82.9% consistente ao longo do mes."
  ),
  voc_negativos=(
    "Detratores de Desativar ME: vendedores buscando desativar configuracoes de envio encontram "
    "restricoes sistemicas que o agente nao consegue resolver. Frustracao acumulada ao longo do mes — "
    "nao com o atendente, mas com a ferramenta e o processo."
  ),
  causas_raiz=[
    dict(
      problema="CDU Desativar ME com deterioracao acumulada de -14.9pp MoM",
      evidencia_quant="CDU caiu de 85.3% (Marco) para 70.4% (Abril) — 54 surveys afetados",
      evidencia_qual="Vendedores buscando desativar ME encontram restricoes sistemicas sem saida",
      causa="Restricao de produto: desativacao de ME nao e disponivel em todos os cenarios e o agente nao tem tool adequada",
      impacto="Deterioracao mes a mes — risco de cruzar abaixo de 60% se tendencia continuar em Maio",
      urgencia="Alta",
      acao="Mapear cenarios de desativacao de ME e criar tool especifica para o agente resolver on-the-spot"
    ),
    dict(
      problema="Melhora mensal modesta (+1.1pp) em relacao ao potencial do driver",
      evidencia_quant="Driver opera 10.4pp acima do target mas cresce apenas 1pp/mes",
      evidencia_qual="Sem aceleracao visivel nos processos de medio NPS (Despacho, Reversa)",
      causa="Potencial de crescimento concentrado em processos que nao tem atencao operacional dedicada",
      impacto="Oportunidade de ganho de 3-5pp adicional nao aproveitada",
      urgencia="Media",
      acao="Revisao de processos de NPS 55-65% (Despacho, Viaje Vendedor) para identificar quick wins"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="Tool especifica para cenarios de desativacao de ME — eliminar principal CDU de queda", impacto="+5pp no CDU afetado", facilidade="Baixa", prioridade="1"),
    dict(acao="Investigar causa da melhora em Logistica Places (+48pp) para replicar", impacto="Confirmar se melhora e sustentavel", facilidade="Alta", prioridade="2"),
    dict(acao="Revisao de qualidade em Despacho Ventas y Publicacoes — maior processo de volume", impacto="+2pp NPS no processo", facilidade="Media", prioridade="3"),
  ],
  resumo_diretoria=(
    "ME Vendedor Seller Dev fechou Abril com NPS 68.2% (+1.1pp MoM), 10.4pp acima da meta. "
    "O driver e o maior por volume (6.196 surveys) e opera consistentemente acima do target ha 5 meses. "
    "Ponto de atencao: CDU Desativar ME acumulou -14.9pp de queda ao longo do mes — deterioracao sistemica. "
    "Destaque positivo: CDU Logistica Places reverteu de negativo para NPS 34.8% (+48pp). "
    "Acao prioritaria: criar tool para agente resolver cenarios de desativacao ME on-the-spot."
  ),
  conclusao_estrategica=(
    "ME Vendedor Seller Dev consolida posicao de lideranca com 10.4pp acima da meta, mas o crescimento "
    "mensal modesto (+1.1pp) indica que ha potencial nao aproveitado. A prioridade de Maio deve ser "
    "dupla: corrigir a deterioracao em Desativar ME antes que cruce abaixo de 60%, e investigar a "
    "melhora em Logistica Places para confirmar se e estrutural e replicavel."
  ),
  ganhos_a_escalar=[
    "Reputacao ME com NPS 82.9% como processo de referencia — identificar boas praticas e escalar",
    "CDU Logistica Places reverteu +48pp MoM — investigar e replicar o que mudou operacionalmente",
    "Modelo de atendimento ME consolidado: 5 meses acima do target — documentar como best practice",
  ],
  problemas_a_corrigir=[
    "CDU Desativar ME em deterioracao acumulada -14.9pp MoM — exige tool especifica de produto",
    "Crescimento modesto de +1.1pp vs potencial maior — revisar processos de NPS 55-65%",
    "Despacho Ventas y Publicacoes sem evolucao visivel no mes",
  ],
  acoes_30_dias=[
    "Mapear cenarios de desativacao de ME e criar tool para agente resolver os principais on-the-spot",
    "Investigar melhora em Logistica Places (+48pp MoM): mudanca operacional ou variacao de amostra?",
    "Revisao de qualidade em Despacho Ventas y Publicacoes — maior processo de volume apos Rep. ME",
  ],
  alertas_criticos=(
    "ATENCAO: CDU Desativar ME acumulou -14.9pp MoM — se tendencia continuar em Maio, pode cruzar "
    "abaixo de 60% NPS e tornar-se driver de queda sistematica. Requer acao antes do proximo relatorio mensal."
  ),
  gerado_em="2026-05-04 — MoM Marco vs Abril 2026",
)

# ── PARTNERS — MoM ────────────────────────────────────────────────────────────
ea_mom("Partners",
  periodo="MoM: Marco 2026 vs Abril 2026",
  resumo_executivo=(
    "Partners fechou Abril com NPS de 65.8% (-1.5pp MoM vs Marco 67.4%), 4.3pp abaixo do target "
    "de 70.2%. O volume mensal e de 2.638 surveys. O recuo mensal e o segundo consecutivo abaixo "
    "do target — o driver nunca atingiu a meta em 2026. CDU mais critico: 'Pago de ruta / ME Extra: "
    "pagamento nao realizado' despencou 60pp MoM (86.7%→26.7%). Em contraste, CDU 'ME Places: "
    "Situacao atual do seu Place' subiu +35.7pp, sinalizando que o segmento de Places responde bem "
    "quando a informacao e clara e objetiva."
  ),
  destaques_positivos=[
    "CDU ME Places: Situacao atual do Place +35.7pp MoM (55.6%→91.3%): best practice do driver no mes",
    "Volume mensal estavel (2.638 surveys vs 2.806 em Marco — -6%)",
    "Qualidade do time reconhecida consistentemente nos promotores ao longo do mes",
    "Segmento Places com NPS 91.3% em Abril — maior subgrupo de satisfacao do driver",
  ],
  destaques_negativos=[
    "MoM -1.5pp: segundo mes seguido em queda — tendencia de deterioracao mensal",
    "4.3pp abaixo do target — driver sem meta atingida em nenhum mes de 2026",
    "CDU Pago de ruta / Pagamento nao realizado -60pp MoM: colapso em CDU de alto volume",
    "Partners opera abaixo do target enquanto outros drivers do grupo superam com folga",
    "Volume caindo -6% MoM — base menor amplifica volatilidade",
  ],
  impacto_estrategico=(
    "CLIENTE: Motoristas com pagamento nao realizado ficam sem renda — urgencia financeira maxima. "
    "OPERACAO: Dois meses consecutivos abaixo do target sem acao corretiva visivel — risco de consolidacao. "
    "MARCA: Partners e o driver mais proximo do cliente final (entregador) — insatisfacao tem impacto "
    "em qualidade de entrega e reputacao do servico como um todo. "
    "FINANCEIRO: Pagamento nao realizado e uma reclamacao de impacto direto na renda do parceiro."
  ),
  voc_positivos=(
    "Promotores do segmento Places: informacao clara sobre situacao do ponto de entrega resolve na "
    "primeira interacao (NPS 91.3%). O driver tem capacidade tecnica de excelencia quando o agente "
    "tem a informacao e a ferramenta corretas."
  ),
  voc_negativos=(
    "O CDU de pagamento nao realizado traz relatos de motoristas com rota concluida mas sem recebimento. "
    "Sem transparencia sobre o processo de correcao e sem prazo de resolucao. Frustracao financeira "
    "direta — o impacto e na renda do parceiro, nao apenas na experiencia."
  ),
  causas_raiz=[
    dict(
      problema="CDU Pago de ruta / ME Extra Pagamento nao realizado colapsou -60pp MoM",
      evidencia_quant="CDU: 86.7% (Marco)→26.7% (Abril) — 15 surveys; pior CDU mensal do driver",
      evidencia_qual="Motoristas com rota concluida sem recebimento — impacto financeiro direto",
      causa="Falha no processo de liberacao de pagamento de rotas — seja sistematica ou por criterios opacos de aprovacao",
      impacto="Motorista sem renda esperada — risco de desengajamento imediato e churn",
      urgencia="Critica",
      acao="Investigar root cause do bloqueio de pagamento de rotas em Abril — e criar SLA de resolucao em 48h"
    ),
    dict(
      problema="Driver sem meta atingida em nenhum mes de 2026 com tendencia de queda MoM",
      evidencia_quant="Janeiro: ~65%, Fevereiro: ~67%, Marco: 67.4%, Abril: 65.8% — sem meta em 2026",
      evidencia_qual="Gap estrutural de 4.3pp vs target — nao e questao operacional pontual",
      causa="Target de 70.2% acima da capacidade atual do driver sem acao estrutural de produto",
      impacto="Risco de consolidacao do gap como gap permanente se nao tratado",
      urgencia="Alta",
      acao="Revisao do target vs capacidade ou plano de melhoria estrutural com prazo definido"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="Investigar e corrigir processo de pagamento nao realizado — SLA de resolucao 48h", impacto="Recuperacao do CDU que colapsou -60pp", facilidade="Media", prioridade="1"),
    dict(acao="Replicar script do CDU ME Places (NPS 91.3%) para outros CDUs de informacao", impacto="+5pp em CDUs de consulta", facilidade="Alta", prioridade="2"),
    dict(acao="Criar ownership de casos de pagamento para garantir resolucao sem multi-atendimento", impacto="Reducao de detratores por escalada sem resolucao", facilidade="Media", prioridade="3"),
  ],
  resumo_diretoria=(
    "Partners fechou Abril com NPS 65.8% (-1.5pp MoM), 4.3pp abaixo da meta — segundo mes seguido abaixo do target. "
    "CDU mais critico: pagamento de rota nao realizado colapsou 60pp no mes — impacto financeiro direto no parceiro. "
    "Contraponto: CDU ME Places com NPS 91.3% (+35.7pp) mostra que o time tem excelencia quando tem ferramenta. "
    "Acao prioritaria: investigar e corrigir o processo de pagamento de rotas antes do relatorio de Maio."
  ),
  conclusao_estrategica=(
    "Partners e o unico driver prioritario sem meta atingida em 2026, com tendencia de queda consecutiva. "
    "O gap nao e operacional — e de produto: o agente performa com excelencia (91.3% em Places) quando tem "
    "ferramenta, mas fica paralisado em pagamentos e conflitos de conta. A prioridade maxima de Maio e "
    "resolver o CDU de pagamento de rota que colapsou 60pp — impacto financeiro direto no parceiro."
  ),
  ganhos_a_escalar=[
    "CDU ME Places com NPS 91.3% (+35.7pp MoM) — identificar o que mudou e replicar em outros CDUs",
    "Qualidade do time quando tem ferramenta — ampliar tool coverage para CDUs criticos",
    "Segmento de consulta sobre status tem melhor performance — padronizar fluxo de informacao",
  ],
  problemas_a_corrigir=[
    "Pagamento de rota nao realizado colapsou -60pp — investigacao urgente de root cause",
    "Driver sem meta atingida em 2026 — plano estrutural necessario",
    "Volume caindo -6% MoM — base menor amplifica volatilidade do NPS",
  ],
  acoes_30_dias=[
    "URGENTE: Investigar root cause do bloqueio de pagamento de rotas em Abril e criar SLA de 48h",
    "Replicar script e fluxo do CDU ME Places (NPS 91.3%) para CDUs de informacao e status",
    "Revisao do plano de atingimento do target: o que precisa mudar para chegar a 70%+ em Junho",
  ],
  alertas_criticos=(
    "CRITICO: Pagamento de rota nao realizado com NPS 26.7% — impacto financeiro direto no parceiro "
    "e risco de churn de motoristas se nao resolvido em 30 dias. "
    "ATENCAO: Segundo mes consecutivo abaixo do target com tendencia de queda — risco de consolidacao do gap."
  ),
  gerado_em="2026-05-04 — MoM Marco vs Abril 2026",
)

# ── PUBLICACIONES SELLER DEV — MoM ───────────────────────────────────────────
ea_mom("Publicaciones Seller Dev",
  periodo="MoM: Marco 2026 vs Abril 2026",
  resumo_executivo=(
    "Publicaciones Seller Dev fechou Abril com NPS 64.1% (-4.3pp MoM vs Marco 68.5%), mas mantém "
    "+11.3pp acima do target de 52.9% — maior margem positiva entre os drivers analisados. "
    "Volume mensal: 2.439 surveys (-26% vs Marco — queda relevante de base). A queda mensal de "
    "-4.3pp e a maior entre os drivers prioritarios em Abril. CDU mais critico: 'Clips / "
    "Potencializador (Clips) - Como funciona' colapsou -52.9pp MoM. Em contraste, funcionalidade "
    "'Preco por variacao' subiu +39pp, indicando que features de pricing melhoradas geram alta satisfacao."
  ),
  destaques_positivos=[
    "+11.3pp vs target — maior margem positiva entre os drivers prioritarios de Abril",
    "CDU Funcionalidade Preco por variacao +39.1pp MoM (25%→64.1%): feature de pricing em ascensao",
    "Driver acima do target ha todos os meses de 2026 — consistencia estrategica",
    "Margem de 11.3pp oferece buffer para absorver variacao sem risco de ruptura de meta",
  ],
  destaques_negativos=[
    "MoM -4.3pp: maior queda mensal entre os drivers prioritarios em Abril",
    "CDU Clips / Potencializador Como funciona -52.9pp MoM (82.9%→30%): colapso em feature especifica",
    "Volume -26% MoM (2.439 vs 3.309): queda significativa de base — monitorar continuidade",
    "A queda -4.3pp no mes anticipa a queda -6.2pp na semana — tendencia de deterioracao acelerada",
  ],
  impacto_estrategico=(
    "CLIENTE: Criadores de conteudo com Clips nao entendendo como a ferramenta funciona perdem receita. "
    "PRODUTO: A queda em Clips sugere mudanca recente na feature (nova UX, nova politica) sem treinamento adequado. "
    "MARCA: Publicacoes e o driver com mais contato com criadores — insatisfacao aqui impacta o ecossistema "
    "de conteudo do ML. EFICIENCIA: Feature de Preco por variacao com +39pp mostra que quando o produto "
    "e bem explicado, a satisfacao e alta."
  ),
  voc_positivos=(
    "Promotores de funcionalidades de pricing: quando o agente explica claramente as vantagens da "
    "funcionalidade (preco por variacao, categorias de produto), o vendedor fica satisfeito e promove "
    "o servico. Padrao: educacao proativa sobre features monetarias gera alto NPS."
  ),
  voc_negativos=(
    "Detratores de Clips: vendedores/criadores que nao entendem como funciona o Potencializador de Clips "
    "— seja porque a feature mudou, porque o agente tambem nao sabe, ou porque a UX e confusa. "
    "Expectativa de receita via Clips nao sendo cumprida."
  ),
  causas_raiz=[
    dict(
      problema="CDU Clips / Potencializador Como funciona colapsou -52.9pp MoM",
      evidencia_quant="CDU: 82.9% (Marco)→30% (Abril) — 20 surveys; maior queda de CDU no mes",
      evidencia_qual="Criadores com duvidas sobre funcionamento do Clips/Potencializador sem resposta adequada",
      causa="Possivelmente mudanca na feature ou nova politica de Clips sem treinamento do time de atendimento",
      impacto="Criadores de conteudo insatisfeitos — risco de reducao de producao de Clips",
      urgencia="Alta",
      acao="Verificar se houve mudanca de produto em Clips/Potencializador em Abril e atualizar script de atendimento"
    ),
    dict(
      problema="Volume mensal caiu -26% (2.439 vs 3.309 surveys em Marco)",
      evidencia_quant="-870 surveys MoM — queda abrupta de base",
      evidencia_qual="Pode indicar reducao real de volume de contatos ou mudanca de roteamento",
      causa="Reduzao de contatos de moderacao (menor volume de anuncios criados) ou deflexao aumentada",
      impacto="Base menor amplifica volatilidade — variacao de 10 cases pode mover o NPS 1pp",
      urgencia="Media",
      acao="Verificar se queda de volume e estrutural ou pontual — analisar origem dos contatos"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="Verificar mudanca de produto em Clips em Abril e atualizar script de atendimento urgentemente", impacto="Recuperacao do CDU que colapsou -52.9pp", facilidade="Alta", prioridade="1"),
    dict(acao="Replicar abordagem de educacao proativa de features de pricing (Preco por variacao)", impacto="+5pp em CDUs de funcionalidade", facilidade="Media", prioridade="2"),
    dict(acao="Investigar queda de volume -26% MoM — estrutural ou pontual", impacto="Estabilidade da base para calculos de NPS", facilidade="Alta", prioridade="3"),
  ],
  resumo_diretoria=(
    "Publicaciones Seller Dev fechou Abril com NPS 64.1% (-4.3pp MoM), 11.3pp acima da meta. "
    "E o driver com maior margem vs target, mas tambem com a maior queda mensal em Abril. "
    "O CDU Clips/Potencializador colapsou -52.9pp — possivelmente mudanca de produto sem treinamento adequado. "
    "Preco por variacao subiu +39pp — quando o produto e bem explicado, a satisfacao e alta. "
    "Acao prioritaria: verificar mudanca em Clips em Abril e atualizar script do time."
  ),
  conclusao_estrategica=(
    "Publicaciones Seller Dev tem a maior margem vs target (11.3pp) e pode absorver variacao, "
    "mas a queda mensal de -4.3pp seguida pela queda semanal de -6.2pp sinaliza tendencia de deterioracao. "
    "O CDU Clips e o epicentro — uma mudanca de produto nao comunicada ao atendimento e a causa mais "
    "provavel. Corrigindo este ponto, o driver pode reverter a tendencia em 30 dias."
  ),
  ganhos_a_escalar=[
    "CDU Preco por variacao +39.1pp MoM — replicar script de educacao proativa de features de pricing",
    "Margem de +11.3pp vs target: usar como base para elevar exigencia operacional",
    "Consistencia acima do target em todo o historico de 2026 — padrao a manter",
  ],
  problemas_a_corrigir=[
    "CDU Clips/Potencializador colapsou -52.9pp MoM — mudanca de produto sem treinamento do time",
    "Queda consecutiva: -4.3pp MoM seguido de -6.2pp WoW — tendencia de aceleracao negativa",
    "Volume -26% MoM — verificar se e estrutural ou pontual",
  ],
  acoes_30_dias=[
    "Verificar se houve mudanca em Clips/Potencializador em Abril e atualizar script urgentemente",
    "Replicar abordagem proativa de features de pricing para outros CDUs de funcionalidade",
    "Monitorar volume semanal de Publicacoes em Maio — confirmar se queda e estrutural",
  ],
  alertas_criticos=(
    "ATENCAO: Queda acelerada — -4.3pp MoM seguido de -6.2pp WoW — se tendencia continuar, "
    "driver pode cruzar abaixo do target em Junho. CDU Clips com NPS 30% e o sinal mais critico do mes."
  ),
  gerado_em="2026-05-04 — MoM Marco vs Abril 2026",
)

# ── POST VENTA SELLER DEV — MoM ───────────────────────────────────────────────
ea_mom("Post Venta Seller Dev",
  periodo="MoM: Marco 2026 vs Abril 2026",
  resumo_executivo=(
    "Post Venta Seller Dev fechou Abril com NPS 69.2% (+5.9pp MoM vs Marco 63.3%), "
    "15.8pp acima do target de 53.4% — melhor resultado mensal do driver em 2026. "
    "Volume mensal de 967 surveys (-18% vs Marco). O crescimento mensal foi o maior entre "
    "os drivers prioritarios. CDU mais positivo: 'Analisamos reputacao - Reclamacao revisada' "
    "+42.5pp (13.2%→55.7%, 61 surveys) — revisao de reclamacoes com criterio justo gera alto impacto. "
    "CDU em queda: 'Criterios de reputacao - Como ser Loja Oficial' -26.7pp — expectativa de ascensao "
    "de status nao cumprida."
  ),
  destaques_positivos=[
    "MoM +5.9pp: maior crescimento mensal entre os drivers prioritarios em Abril",
    "CDU Reclamacao revisada +42.5pp MoM (13.2%→55.7%): revisao justa de reclamacoes gera alto NPS",
    "+15.8pp vs target — segundo maior gap positivo vs meta",
    "Melhor resultado mensal de 2026 para o driver — trajetoria ascendente confirmada",
    "Revisao de reclamacoes como driver de satisfacao: quando o vendedor ve justicia, promove o servico",
  ],
  destaques_negativos=[
    "CDU Criterios de reputacao - Como ser Loja Oficial -26.7pp MoM: expectativa de progressao nao cumprida",
    "Volume -18% MoM (967 vs 1.186): queda de base — monitorar continuidade",
    "Queda WoW subsequente de -4.2pp sugere que o crescimento mensal pode estar arrefecendo",
    "Newbies com menor qualidade em casos complexos de mediacao ao longo do mes",
  ],
  impacto_estrategico=(
    "CLIENTE: Revisao justa de reclamacoes e um poderoso gerador de confianca do vendedor no ML. "
    "OPERACAO: O resultado positivo do mes valida que o processo de revisao de reclamacoes esta funcionando. "
    "MARCA: Vendedor que teve reclamacao revisada justa torna-se advogado da marca — alto potencial de "
    "NPS positive. EFICIENCIA: O CDU de Loja Oficial sugere oportunidade de criar programa de orientacao "
    "de progressao de status."
  ),
  voc_positivos=(
    "Promotores do CDU Reclamacao revisada: vendedores que tiveram reclamacoes revisadas de forma justa "
    "expressam gratidao e confianca no processo do ML. A percepcao de justicia e o principal driver "
    "de satisfacao neste CDU. Quando o vendedor sente que o ML esta do seu lado, o NPS e muito alto."
  ),
  voc_negativos=(
    "CDU Loja Oficial: vendedores que querem entender os criterios para se tornar Loja Oficial encontram "
    "barreiras ou criterios vagos. A expectativa de progressao nao cumprida e o principal gerador de "
    "frustracoes neste CDU — o vendedor sente que a meta nao e clara."
  ),
  causas_raiz=[
    dict(
      problema="CDU Como ser Loja Oficial -26.7pp MoM: expectativa de progressao de status frustrada",
      evidencia_quant="CDU: 84.6% (Marco)→57.9% (Abril) — 19 surveys",
      evidencia_qual="Vendedores buscando criterios de Loja Oficial encontram informacao vaga ou barreiras",
      causa="Criterios de progressao de status de vendedor nao comunicados com clareza e objetividade",
      impacto="Vendedores que aspiram crescer no ML insatisfeitos — risco de reducao de engajamento",
      urgencia="Media",
      acao="Criar FAQ claro sobre criterios de progressao para Loja Oficial com exemplos e prazos"
    ),
    dict(
      problema="Volume -18% MoM — base menor pode amplificar volatilidade",
      evidencia_quant="967 surveys em Abril vs 1.186 em Marco",
      evidencia_qual="Reducao de volume pode indicar deflexao aumentada ou sazonalidade",
      causa="Possivelmente deflexao mais eficaz ou sazonalidade de reclamacoes pos-periodo de alta",
      impacto="Menor base torna o NPS mais sensivel a variacao pontual",
      urgencia="Baixa — monitorar",
      acao="Monitorar volume em Maio para confirmar se e tendencia ou sazonalidade"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="Criar FAQ claro de criterios de progressao para Loja Oficial com exemplos e prazos", impacto="Recuperacao do CDU -26.7pp", facilidade="Alta", prioridade="1"),
    dict(acao="Escalar o modelo de revisao justa de reclamacoes como best practice de atendimento", impacto="Replicar o +42.5pp do CDU de revisao", facilidade="Media", prioridade="2"),
    dict(acao="Monitorar volume em Maio — confirmar se queda de -18% e tendencia estrutural", impacto="Estabilidade da base de calculo", facilidade="Alta", prioridade="3"),
  ],
  resumo_diretoria=(
    "Post Venta Seller Dev fechou Abril com NPS 69.2% (+5.9pp MoM), 15.8pp acima da meta — melhor resultado do driver em 2026. "
    "O crescimento foi liderado pelo CDU Reclamacao Revisada (+42.5pp): vendedores que recebem revisao justa tornam-se promotores fortes. "
    "Ponto de atencao: criterios de Loja Oficial com queda de -26.7pp — expectativa de progressao de status nao cumprida. "
    "Acao prioritaria: FAQ claro de criterios de Loja Oficial com exemplos e prazos."
  ),
  conclusao_estrategica=(
    "Post Venta Seller Dev confirma em Abril que revisao justa de reclamacoes e o maior driver de satisfacao "
    "neste processo — +42.5pp no CDU correspondente. O driver opera 15.8pp acima da meta com trajetoria "
    "ascendente. O foco de Maio deve ser manter o padrao de revisao justa e corrigir o CDU de Loja Oficial "
    "antes que a queda acumule mais."
  ),
  ganhos_a_escalar=[
    "Modelo de revisao justa de reclamacoes — +42.5pp MoM: documentar e escalar como best practice",
    "Trajetoria de crescimento MoM (+5.9pp): identificar o que mudou operacionalmente em Abril",
    "Margem de +15.8pp vs target: usar como base para elevar target em Julho",
  ],
  problemas_a_corrigir=[
    "CDU Criterios Loja Oficial -26.7pp MoM: expectativa de progressao de status sem informacao clara",
    "Queda WoW subsequente de -4.2pp: monitorar se crescimento mensal esta arrefecendo",
    "Volume -18% MoM: confirmar se e estrutural ou sazonalidade",
  ],
  acoes_30_dias=[
    "Criar FAQ claro de criterios de progressao para Loja Oficial com exemplos concretos e prazos",
    "Documentar o processo de revisao justa de reclamacoes que gerou +42.5pp e escalar para todo o time",
    "Monitorar volume de contatos em Maio — confirmar se queda de -18% e tendencia estrutural",
  ],
  alertas_criticos=(
    "ATENCAO: Queda WoW de -4.2pp logo apos melhor mes do driver — monitorar se e reversao de tendencia "
    "ou correcao pontual. Se WoW seguir negativo, o crescimento mensal pode ser neutralizado em Maio."
  ),
  gerado_em="2026-05-04 — MoM Marco vs Abril 2026",
)

# ── PCF VENDEDOR SELLER DEV — MoM ─────────────────────────────────────────────
ea_mom("PCF Vendedor Seller Dev",
  periodo="MoM: Marco 2026 vs Abril 2026",
  resumo_executivo=(
    "PCF Vendedor Seller Dev fechou Abril com NPS 48.8% (+2.0pp MoM vs Marco 46.8%), "
    "8.9pp acima do target de 39.9%. Volume mensal: 512 surveys (-35% vs Marco). "
    "O crescimento mensal de +2pp e o segundo menor entre os drivers prioritarios, mas "
    "a trajetoria e positiva: o driver estava abaixo do target em Janeiro e agora opera "
    "com folga de 8.9pp. CDU de maior queda: 'Devolucoes - Dentro da promessa de entrega' "
    "-47.5pp MoM (69.2%→21.7%) — devolucoes dentro do prazo mas com problemas de execucao. "
    "CDU de maior alta: 'Mediacao encerrada - Produto danificado' +40.6pp — quando a mediacao "
    "de produto danificado e resolvida com criterio claro, o vendedor promove."
  ),
  destaques_positivos=[
    "MoM +2.0pp: segundo mes positivo seguido — trajetoria ascendente consolidada",
    "+8.9pp vs target — driver operando acima da meta apos historico de dificuldades",
    "CDU Mediacao encerrada Produto danificado +40.6pp MoM (0%→40.6%): resolucao clara de mediacao gera alto NPS",
    "Volume estavel no segmento principal — base suficiente para analise confiavel",
    "Trajetoria: de abaixo do target em Jan/Fev para +8.9pp em Abril — melhora estrutural",
  ],
  destaques_negativos=[
    "CDU Devolucoes dentro da promessa -47.5pp MoM (69.2%→21.7%): colapso em devolucoes teoricamente ok",
    "Volume -35% MoM (512 vs 790 surveys): queda acentuada de base em um mes",
    "NPS absoluto de 48.8% ainda e o mais baixo entre os cinco drivers prioritarios",
    "Base de 512 surveys e a menor entre os prioritarios — volatilidade amplificada",
    "Sem dados de canal e senioridade comparativos MoM para analise completa",
  ],
  impacto_estrategico=(
    "CLIENTE: Devolucao dentro do prazo mas com problemas de execucao frustra o vendedor que esperava "
    "resolucao automatica — expectativa vs realidade. "
    "OPERACAO: Mediacao de produto danificado com criterio claro gera alto NPS — validar e escalar. "
    "FINANCEIRO: CDU devolucao impacta diretamente o fluxo de caixa do vendedor. "
    "EFICIENCIA: O +40.6pp em mediacao de produto danificado mostra que criterio claro e comunicado "
    "tem alto impacto com baixo custo operacional."
  ),
  voc_positivos=(
    "Promotores de mediacao de produto danificado: quando a mediacao e encerrada com criterio explicito "
    "e justo (produto danificado com evidencias = responsabilidade clara), o vendedor aceita o desfecho "
    "e promove o servico. A transparencia no criterio e o driver principal."
  ),
  voc_negativos=(
    "Detratores de devolucoes dentro da promessa: a devolucao 'dentro do prazo' nao significa resolucao "
    "satisfatoria — o vendedor recebe produto de volta mas com danos, embalagem errada ou processo "
    "confuso. A promessa de 'dentro do prazo' cria expectativa de resolucao perfeita que nao se cumpre."
  ),
  causas_raiz=[
    dict(
      problema="CDU Devolucoes dentro da promessa de entrega colapsou -47.5pp MoM",
      evidencia_quant="CDU: 69.2% (Marco)→21.7% (Abril) — 23 surveys",
      evidencia_qual="Devolucao 'dentro do prazo' mas com problemas de execucao (produto danificado, embalagem errada)",
      causa="Expectativa criada pelo SLA 'dentro da promessa' nao corresponde a qualidade de execucao da devolucao",
      impacto="Vendedor com produto devolvido com avaria ou processo confuso — impacto financeiro direto",
      urgencia="Alta",
      acao="Revisar criterios de qualidade na execucao de devolucoes dentro do prazo — nao apenas o prazo, mas a integridade"
    ),
    dict(
      problema="Volume -35% MoM (512 vs 790 surveys) — queda acentuada de base",
      evidencia_quant="-278 surveys em um mes — queda estatisticamente relevante",
      evidencia_qual="Pode indicar deflexao aumentada, reducao de contatos ou mudanca de roteamento",
      causa="Possivel melhora de deflexao no processo de devolucao ou sazonalidade",
      impacto="Base pequena de 512 surveys amplifica volatilidade — variacao de 15 cases muda NPS 3pp",
      urgencia="Media",
      acao="Investigar causa da queda de volume — confirmar se e deflexao real ou mudanca de roteamento"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="Revisar criterios de qualidade na execucao de devolucoes: integridade do produto, embalagem e processo", impacto="Recuperacao do CDU que colapsou -47.5pp", facilidade="Media", prioridade="1"),
    dict(acao="Documentar e escalar o modelo de mediacao de produto danificado que gerou +40.6pp", impacto="Replicar best practice de criterio claro em outros CDUs de mediacao", facilidade="Alta", prioridade="2"),
    dict(acao="Investigar causa da queda de volume -35% em Abril", impacto="Estabilidade da base de analise", facilidade="Alta", prioridade="3"),
  ],
  resumo_diretoria=(
    "PCF Vendedor Seller Dev fechou Abril com NPS 48.8% (+2.0pp MoM), 8.9pp acima da meta — segundo mes positivo seguido. "
    "CDU critico: Devolucoes dentro da promessa colapsou -47.5pp — devolucao 'no prazo' mas com execucao problemática. "
    "CDU positivo: Mediacao de produto danificado +40.6pp — criterio claro de resolucao gera alto NPS. "
    "Acao prioritaria: revisar criterios de qualidade na execucao de devolucoes."
  ),
  conclusao_estrategica=(
    "PCF Vendedor Seller Dev confirma trajetoria positiva em Abril (+2pp MoM, +8.9pp vs target). "
    "A melhora estrutural vem de mediacoes com criterio claro — o time sabe atender quando o processo "
    "e bem definido. O proximo nivel de crescimento exige resolver a qualidade de execucao das devolucoes, "
    "que colapsou 47.5pp no mes e pode erodir os ganhos conquistados."
  ),
  ganhos_a_escalar=[
    "Modelo de mediacao com criterio claro: +40.6pp MoM — documentar e escalar para todo o time",
    "Trajetoria positiva de 3 meses: de abaixo do target para +8.9pp — identificar o que mudou",
    "Criterio explicito de resolucao de produto danificado como best practice de mediacao",
  ],
  problemas_a_corrigir=[
    "Devolucoes dentro do prazo mas com execucao problematica: integridade do produto e processo confuso",
    "Volume -35% MoM: confirmar se deflexao e estrutural ou pontual",
    "NPS absoluto de 48.8% ainda e o mais baixo entre os prioritarios — espaco para crescimento",
  ],
  acoes_30_dias=[
    "Revisar qualidade de execucao de devolucoes: integridade do produto devolvido e clareza do processo",
    "Documentar modelo de mediacao de produto danificado que gerou +40.6pp e escalar",
    "Investigar queda de volume -35% em Abril — confirmar se e deflexao ou mudanca de roteamento",
  ],
  alertas_criticos=(
    "ATENCAO: CDU Devolucoes dentro da promessa colapsou -47.5pp MoM — se a queda continuar em Maio, "
    "pode neutralizar a trajetoria positiva mensal. O criterio de qualidade de execucao de devolucoes "
    "precisa ser revisado antes do proximo ciclo de relatorios."
  ),
  gerado_em="2026-05-04 — MoM Marco vs Abril 2026",
)

with open("dd_summaries.json", "w", encoding="utf-8") as f:
    json.dump(s, f, ensure_ascii=False, indent=2)
print("OK — dd_summaries.json atualizado com mom.executive_analysis para 5 drivers.")
for drv in ["ME Vendedor Seller Dev","Partners","Publicaciones Seller Dev","Post Venta Seller Dev","PCF Vendedor Seller Dev"]:
    has_mom_ea = isinstance(s.get(drv,{}).get("mom",{}), dict) and "executive_analysis" in s[drv]["mom"]
    has_wow_ea = isinstance(s.get(drv,{}).get("wow",{}), dict) and "executive_analysis" in s[drv]["wow"]
    print(f"  {drv}: mom_ea={has_mom_ea} wow_ea={has_wow_ea}")
