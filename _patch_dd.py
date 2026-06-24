#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injeta executive_analysis para 5 drivers prioritários em dd_summaries.json."""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open("dd_summaries.json", encoding="utf-8") as f:
    s = json.load(f)

def ensure_wow(driver):
    if driver not in s:
        s[driver] = {}
    w = s[driver].get("wow", {})
    if isinstance(w, str):
        s[driver]["wow"] = {"bullets_legado": w}
    elif not isinstance(w, dict):
        s[driver]["wow"] = {}

def ea(drv, **kw):
    ensure_wow(drv)
    s[drv]["wow"]["executive_analysis"] = kw

ea("ME Vendedor Seller Dev",
  periodo="S1 27/abr-03/mai vs S2 20/abr-26/abr",
  resumo_executivo=(
    "ME Vendedor Seller Dev fechou a semana com NPS de 72.7% (+3.4pp WoW), 10.9pp acima do target de 57.8% "
    "— quarto periodo consecutivo acima da meta. Volume cresceu 8.6% WoW (1.420 surveys). A melhora foi "
    "puxada pelo canal Multicanal Chat (+3.1pp) e pelo perfil Newbie (+5.2pp), que pela primeira vez "
    "convergiu para o nivel Expert. Dois riscos: (1) CDU Desativar ME caiu 30pp — barreiras sistemicas "
    "sem solucao pelo agente; (2) IA gerando respostas circulares criando detratores explicitos nos comentarios."
  ),
  destaques_positivos=[
    "WoW +3.4pp: terceiro ganho WoW seguido — aceleracao consistente",
    "Newbie +5.2pp WoW: reversao estrutural — junior convergindo para Expert (67.0% vs 70.8%)",
    "CDU Envio pelo V categorias especiais +53pp: educacao proativa sobre custo gera alta fidelizacao",
    "Volume +8.6% com NPS crescente: expansao sem diluicao de qualidade",
    "Reputacao ME mantém NPS 85.5% — processo ancora com 34% do volume",
  ],
  destaques_negativos=[
    "CDU Desativar ME -30pp: agente sem acesso a solucao sistemica — frustracao inevitavel",
    "Expert -0.5pp WoW: leve deterioracao com risco de cruzamento negativo com Newbie",
    "IA com respostas circulares — 4 de 20 detratores citam IA explicitamente nos comentarios",
    "Despacho Ventas y Publicacoes estagnado em 59.6% — maior processo de volume apos Rep. ME",
    "Sem dados VIG para monitoramento intradiario desta semana",
  ],
  impacto_estrategico=(
    "CLIENTE: Vendedores com restricoes ME percebem atendimento como impotente — risco de churn. "
    "OPERACAO: Newbie em ascensao reduz custo de treinamento. "
    "MARCA: IA com respostas circulares gerando detratores — risco reputacional se escalar. "
    "EFICIENCIA: CDU categorias especiais com +53pp mostra ROI alto de educacao proativa com baixo custo."
  ),
  voc_positivos=(
    "Promotores elogiam resolucao rapida via WhatsApp (sem stress). Frase representativa: "
    "tudo ficou resolvido rapidamente, sem stress. Expert Ronsangela citada como referencia de excelencia. "
    "Canal Chat associado a experiencias positivas quando agente tem ferramenta e autonomia."
  ),
  voc_negativos=(
    "Detratores: (1) IA como barreira — esse IA nao funciona, so da transtorno; muitas questoes com IA, "
    "fica complicado obter resposta assertiva. (2) Falta de resolucao — demora e nunca resolvem. "
    "(3) Questoes sistemicas sem saida. Emocao predominante: impotencia com o sistema, nao com o agente."
  ),
  causas_raiz=[
    dict(
      problema="IA com respostas circulares e sem resolucao",
      evidencia_quant="CDU Desativar ME -30pp; 4/20 detratores citam IA explicitamente",
      evidencia_qual="Esse IA nao funciona / respostas redundantes sem resolucao",
      causa="Modelo de IA calibrado para deflexao, nao resolucao — gaps em configuracao ME",
      impacto="Detratores estruturais mesmo com agente posterior incapaz de reverter",
      urgencia="Alta",
      acao="Mapear fluxos IA com maior escalada nao resolvida; recalibrar para CDU Desativar ME"
    ),
    dict(
      problema="Despacho Ventas y Publicacoes estagnado em 59.6%",
      evidencia_quant="314 surveys S1, NPS flat WoW — maior processo por volume apos Rep. ME",
      evidencia_qual="Restricoes logisticas sistemicas — agente sem autonomia para resolver",
      causa="Sem script de compensacao para categorias especiais de envio",
      impacto="Limita crescimento do NPS mesmo com Reputacao ME saudavel",
      urgencia="Media",
      acao="Script de educacao proativa sobre categorias especiais + workshop de capacitacao"
    ),
    dict(
      problema="Expert com leve deterioracao enquanto Newbie cresce",
      evidencia_quant="Expert: 70.8% flat com leve queda; Newbie: 61.8% para 67.0%",
      evidencia_qual="Experts lidam com casos escalados de maior complexidade sem ferramentas adequadas",
      causa="Distribuicao de casos por complexidade nao calibrada — Experts absorvem casos sem saida",
      impacto="Risco de inversao de tendencia impactando NPS geral se nao monitorado",
      urgencia="Baixa — monitorar",
      acao="Analise de distribuicao de casos complexidade vs senioridade para proteger Experts"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="Script de educacao proativa para CDU categorias especiais de envio", impacto="+3-5pp NPS no processo", facilidade="Alta", prioridade="1"),
    dict(acao="Mapear fluxos IA com maior escalada e reportar para Produto com evidencias", impacto="Reducao de detratores sistemicos", facilidade="Media", prioridade="2"),
    dict(acao="Replicar boas praticas do canal WhatsApp para outros canais de atendimento", impacto="+2pp NPS medio", facilidade="Media", prioridade="3"),
  ],
  recomendacoes_medio=[
    dict(acao="Recalibrar IA para CDUs de configuracao ME com satisfacao abaixo de 40%", impacto="Eliminacao de categoria de detratores estruturais", facilidade="Baixa", prioridade="1"),
    dict(acao="Programa de coaching para Experts expostos a casos sistemicos sem saida", impacto="Estabilizacao e crescimento do NPS Expert", facilidade="Media", prioridade="2"),
  ],
  resumo_diretoria=(
    "ME Vendedor Seller Dev atingiu NPS 72.7% esta semana, +3.4pp vs semana anterior e 10.9pp acima da meta. "
    "O driver responde por 30% do volume e esta performando acima do target ha quatro semanas consecutivas. "
    "O crescimento Newbie (+5.2pp) sugere maturacao da operacao. "
    "Ponto critico: IA gerando detratores explicitos em comentarios — acao imediata de produto necessaria. "
    "CDU categorias especiais com +53pp e a maior oportunidade de replicacao desta semana."
  ),
  conclusao_estrategica=(
    "ME Vendedor Seller Dev consolida posicao como motor do NPS Sellers, 10.9pp acima da meta com trajetoria "
    "ascendente. O risco principal nao e de performance — e sistemico: IA criando detratores que o agente nao "
    "consegue reverter. Se nao corrigida, pode neutralizar os ganhos operacionais. A oportunidade imediata: "
    "educacao proativa sobre categorias especiais — alta facilidade, alto retorno em NPS."
  ),
  ganhos_a_escalar=[
    "Educacao proativa sobre categorias especiais de envio — +53pp no CDU correspondente",
    "Resolucao rapida via WhatsApp pelo agente humano — fidelizacao e promotores explicitos",
    "Metodologia de desenvolvimento de Newbie — +5.2pp em uma semana",
  ],
  problemas_a_corrigir=[
    "IA com respostas circulares e sem saida para casos de configuracao ME — prioridade de produto",
    "Despacho estagnado — restricoes sistemicas sem script de compensacao adequado",
    "Expert levemente em queda absorvendo casos mais complexos — risco de inversao",
  ],
  acoes_30_dias=[
    "Script de educacao proativa para categorias especiais de envio com deploy imediato em Chat",
    "Mapeamento top 5 fluxos IA com maior taxa de detrator — report para Produto com evidencias reais",
    "Analise de distribuicao de casos complexos vs senioridade para reduzir pressao sobre Experts",
  ],
  alertas_criticos=(
    "ATENCAO: IA gerando detratores explicitos em 4 de 20 amostras — risco de escala se nao tratado. "
    "ATENCAO: CDU Desativar ME caiu 30pp — friccao sistemica sem solucao pelo agente atual."
  ),
  gerado_em="2026-05-04 — S1 27/abr-03/mai",
)

ea("Partners",
  periodo="S1 27/abr-03/mai vs S2 20/abr-26/abr",
  resumo_executivo=(
    "Partners recuou -4.4pp WoW, fechando em 62.6% — 7.6pp abaixo do target de 70.2%. Em base mensal, "
    "mostra recuperacao consistente (+5.4pp MoM). Volume estavel (717 surveys). Queda concentra-se em "
    "CDU critico: conflito de servicos (-48.5pp), onde o agente nao tem ferramenta para resolver o bloqueio "
    "de conta. Em contraste, casos de consulta sobre documentacao mantém NPS 91.7%. O gap de 7.6pp vs "
    "target exige acao estrutural em produto, nao apenas em atendimento."
  ),
  destaques_positivos=[
    "MoM +5.4pp (Marco 57.8% para Abril 63.2%): tendencia mensal positiva estrutural",
    "CDU consulta sobre documentacao ME Extra com NPS 91.7% — benchmark de excelencia no driver",
    "Time reconhecido como profissional e atencioso — qualidade operacional acima da media",
    "11 de 12 promotores em casos de orientacao de documentacao: processo mais resolutivo do driver",
  ],
  destaques_negativos=[
    "WoW -4.4pp: reversao de semana forte anterior (S2 foi 67.0%)",
    "7.6pp abaixo do target — segundo maior gap negativo entre os drivers prioritarios",
    "CDU Conflito de servicos ME Extra -48.5pp: agente sem caminho de resolucao disponivel",
    "VoC: passou por 3 atendimentos e encerraram sem resolver — escalada sem desfecho",
    "Newbies dominam casos de conflito — inexperiencia amplificada por complexidade sistemica",
  ],
  impacto_estrategico=(
    "CLIENTE: Motoristas com conflito de conta atendidos multiplas vezes sem resolucao — churn de parceiros. "
    "OPERACAO: Sem ferramenta, agente gasta tempo sem desfecho. "
    "MARCA: Prazo longo citado como problema — risco de viralizacao em grupos de motoristas. "
    "EFICIENCIA: Os dois CDUs opostos mostram que o problema e sistemico, nao operacional."
  ),
  voc_positivos=(
    "Promotores reconhecem atencao e profissionalismo de forma consistente. Casos de documentacao "
    "resolvidos na primeira interacao. Comentario: atenciosa me ajudou na minha solicitacao. "
    "O time tem qualidade reconhecida — o problema esta nos casos sem ferramenta."
  ),
  voc_negativos=(
    "O solicitante fica refem do processo do ML, sem processo claro, resposta objetiva ou acesso "
    "a informacao relevante. Passou por 3 atendimentos e encerraram sem resolver. O atendimento "
    "foi otimo, o problema e o prazo para resolver uma coisa simples. Emocao: abandono e impotencia."
  ),
  causas_raiz=[
    dict(
      problema="Conflito de identidade entre contas sem ferramenta de resolucao para o agente",
      evidencia_quant="CDU -48.5pp; 4 de 12 cases com escalada multipla",
      evidencia_qual="Nao consigo fazer cadastro — bloqueado por dados em outra conta",
      causa="Sistema vincula documentos a conta errada sem fluxo de correcao disponivel ao agente",
      impacto="Motoristas bloqueados de operar — churn de parceiros ativos",
      urgencia="Alta",
      acao="Criar fluxo de desvinculacao de conta com autonomia para o agente e SLA de 24h"
    ),
    dict(
      problema="Multi-atendimento sem ownership — casos reabertos sem contexto",
      evidencia_quant="2 detratores citam 3 ou mais atendimentos sem resolucao",
      evidencia_qual="Passou por 3 atendimentos e encerraram sem resolver",
      causa="Ausencia de ownership de caso — cada atendente recomeca do zero",
      impacto="NPS deteriora a cada contato nao-resolutivo; custo operacional sem retorno",
      urgencia="Alta",
      acao="Case ownership com transferencia de contexto completo para casos ME Extra"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="Especificacao de produto: fluxo de desvinculacao de conta com SLA de 24 horas", impacto="+8-10pp no CDU de conflito", facilidade="Baixa", prioridade="1"),
    dict(acao="Case ownership em casos reabertos com historico completo visivel", impacto="Eliminar detratores por multi-atendimento", facilidade="Media", prioridade="2"),
    dict(acao="Publicar SLA oficial de resolucao para conflito de conta", impacto="Reducao de expectativa frustrada", facilidade="Alta", prioridade="3"),
  ],
  resumo_diretoria=(
    "Partners fechou em 62.6% NPS esta semana (-4.4pp WoW), 7.6pp abaixo da meta de 70.2%. "
    "Em base mensal, o driver esta em recuperacao (+5.4pp MoM). O gap vs target e estrutural: "
    "conflito de conta bloqueia o agente de resolver o problema raiz. Casos de documentacao com "
    "NPS 91.7% — o time sabe atender quando tem ferramenta. Acao prioritaria: criar fluxo de "
    "resolucao de conflito de conta com SLA definido."
  ),
  conclusao_estrategica=(
    "Partners opera com dois regimes: documentacao (NPS 91.7%) versus conflito de conta (NPS 33%). "
    "O gap de 58pp indica problema sistemico, nao operacional. A acao de maior retorno esta em "
    "produto: criar o fluxo de desvinculacao de conta, nao em treinamento de agentes que ja "
    "performam bem quando têm acesso as ferramentas corretas."
  ),
  ganhos_a_escalar=[
    "Orientacao de documentacao ME Extra com NPS 91.7% — replicar script para todos os canais",
    "Qualidade operacional do time — capturar e padronizar boas praticas dos promotores",
    "Tendencia MoM positiva (+5.4pp): manter foco em documentacao e novos cadastros",
  ],
  problemas_a_corrigir=[
    "Fluxo de conflito de conta sem resolucao disponivel — gargalo de produto urgente",
    "Multi-atendimento sem context pass — cada interacao comeca do zero piorando o NPS",
    "Prazo de resolucao percebido como longo — SLA nao comunicado ou nao cumprido",
  ],
  acoes_30_dias=[
    "Especificacao de produto: fluxo de desvinculacao de conta em conflito com autonomia para o agente",
    "Implementar transfer de contexto em casos reabertos de ME Extra com historico visivel",
    "Publicar SLA oficial de resolucao para conflito de conta e comunicar ativamente ao parceiro",
  ],
  alertas_criticos=(
    "ALERTA: 7.6pp abaixo do target com tendencia WoW negativa — risco de sair do range de meta em Maio. "
    "ALERTA: Conflito de conta gera casos reabertos e cada reabertura adiciona um detrator."
  ),
  gerado_em="2026-05-04 — S1 27/abr-03/mai",
)

ea("Publicaciones Seller Dev",
  periodo="S1 27/abr-03/mai vs S2 20/abr-26/abr",
  resumo_executivo=(
    "Publicaciones Seller Dev recuou -6.2pp WoW (de 62.9% para 56.7%), mas mantém +3.8pp acima do target "
    "de 52.9%. Segundo maior volume do grupo (517 surveys). Queda concentrou-se no CDU Afiliados/Criadores "
    "(-53.9pp): criadores reclamam de campanhas de video que desaparecem sem feedback e metricas de comissao "
    "nao contabilizadas. Em contraste, ativacao de afiliados mantém NPS 85.7% (+27.4pp) — o problema "
    "esta na fase pos-ativacao, nao no onboarding."
  ),
  destaques_positivos=[
    "Acima do target em +3.8pp — buffer de seguranca mantido mesmo com queda WoW",
    "CDU Como ativar afiliados com NPS 85.7% e +27.4pp WoW: onboarding funcionando com excelencia",
    "Promotores destacam clareza e agilidade — qualidade do time reconhecida consistentemente",
    "MoM em recuperacao (+1.6pp Marco para Abril)",
  ],
  destaques_negativos=[
    "WoW -6.2pp: queda mais acentuada entre os drivers prioritarios desta semana",
    "CDU Afiliados Programa de Criadores -53.9pp: colapso de NPS em CDU especifico",
    "Metricas de afiliados nao contabilizadas — impacto em receita de criadores ativos",
    "VoC: nao resolvem, respondem com redundancia — falha de qualidade em casos pos-ativacao",
    "Buffer vs target de apenas 3.8pp — nova queda WoW cruzaria abaixo da meta",
  ],
  impacto_estrategico=(
    "CLIENTE: Criadores com campanhas bloqueadas perdem receita sem previsao de resolucao. "
    "OPERACAO: Agente nao tem mais informacao do que em moderacao. "
    "MARCA: Criadores insatisfeitos podem migrar para plataformas concorrentes em 30 dias. "
    "EFICIENCIA: Gap de 40pp entre onboarding e pos-ativacao revela lacuna critica de produto."
  ),
  voc_positivos=(
    "Promotores: sempre deixa tudo muito bem claro (Expert) / muito agil e inteligente. "
    "Casos de configuracao basica resolvidos na primeira interacao com alta satisfacao. "
    "Padrao: quando o agente tem clareza e ferramenta, a experiencia e excelente."
  ),
  voc_negativos=(
    "Porcentagens nao entraram e alegaram que eram pessoas da minha lista de contato. "
    "Nao fizeram questao de resolver e me enrolaram. Respondem com redundancia e o problema "
    "nunca e solucionado de forma eficiente. Padrao: descaso e frustracao no pos-ativacao."
  ),
  causas_raiz=[
    dict(
      problema="Campanhas de video em moderacao sem visibilidade de prazo para o criador",
      evidencia_quant="CDU -53.9pp; videos sumindo sem SLA visivel no app",
      evidencia_qual="Campanhas sumindo; rep responde em moderacao sem prazo nem acao",
      causa="Produto nao oferece dashboard de status de moderacao para o criador",
      impacto="Criadores com campanhas bloqueadas perdem receita sem previsao de resolucao",
      urgencia="Alta",
      acao="Implementar notificacao proativa de status de moderacao com prazo maximo visivel no app"
    ),
    dict(
      problema="Metricas de afiliados nao contabilizadas — criterios de elegibilidade opacos",
      evidencia_quant="2 ou mais detratores com comentario direto sobre comissoes",
      evidencia_qual="Porcentagens nao entraram; alegaram que eram pessoas da lista de contato",
      causa="Elegibilidade de indicacoes com criterios nao comunicados proativamente",
      impacto="Perda de confianca no programa de afiliados; risco de saida de criadores ativos",
      urgencia="Alta",
      acao="FAQ publico sobre elegibilidade + notificacao quando comissao nao e contabilizada e por que"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="Produto: notificacao proativa com prazo de moderacao para campanhas de video", impacto="Eliminacao da principal causa de detrator", facilidade="Media", prioridade="1"),
    dict(acao="FAQ publico sobre elegibilidade de indicacoes com exemplos praticos", impacto="Reducao de insatisfacao por expectativa de comissao", facilidade="Alta", prioridade="2"),
    dict(acao="Coaching de qualidade para Newbies em casos de Afiliados", impacto="+2pp NPS no CDU", facilidade="Alta", prioridade="3"),
  ],
  resumo_diretoria=(
    "Publicaciones Seller Dev esta 3.8pp acima do target, mas recuou -6.2pp WoW. A queda vem do programa "
    "de Afiliados/Criadores: campanhas sumindo sem SLA visivel e comissoes nao contabilizadas. O processo "
    "de ativacao esta saudavel (NPS 85.7%). O problema esta no pos-ativacao. Acao prioritaria: dashboard "
    "de status de moderacao e FAQ de elegibilidade de afiliados."
  ),
  conclusao_estrategica=(
    "O driver tem dois mundos: onboarding (NPS 85.7%) versus pos-ativacao (NPS 46.1%). A queda WoW "
    "sinaliza problemas estruturais de produto no programa Criadores. Sem intervencao em 30 dias, o "
    "buffer de 3.8pp pode ser consumido se o CDU de Criadores continuar em deterioracao."
  ),
  ganhos_a_escalar=[
    "Script de ativacao de afiliados com NPS 85.7% — replicar em todos os canais de entrada",
    "Clareza e agilidade de Experts como benchmark de qualidade — documentar e escalar",
    "Processo de onboarding como referencia para reducao de friccao nos demais CDUs",
  ],
  problemas_a_corrigir=[
    "Moderacao de videos sem SLA visivel — criadores sem previsao de publicacao de campanhas",
    "Metricas de afiliados com elegibilidade opaca — perda de receita e confianca de criadores",
    "Resposta redundante e sem resolucao em casos complexos de Newbies",
  ],
  acoes_30_dias=[
    "Produto: notificacao proativa com prazo de moderacao para campanhas de video no app",
    "FAQ publico sobre elegibilidade de indicacoes no programa Afiliados com exemplos praticos",
    "Coaching de Newbies em casos de Afiliados — foco em resolucao vs redundancia",
  ],
  alertas_criticos=(
    "ALERTA: Buffer vs target de apenas 3.8pp com WoW negativo de -6.2pp — risco de cruzar abaixo da "
    "meta na proxima semana. ALERTA: Criadores com comissoes nao contabilizadas podem migrar em 30 dias."
  ),
  gerado_em="2026-05-04 — S1 27/abr-03/mai",
)

ea("Post Venta Seller Dev",
  periodo="S1 27/abr-03/mai vs S2 20/abr-26/abr",
  resumo_executivo=(
    "Post Venta Seller Dev recuou -4.2pp WoW (de 76.1% para 71.9%), mas opera com 18.5pp acima do target "
    "de 53.4% — maior margem de seguranca vs meta entre os drivers prioritarios. A queda vem de um "
    "paradoxo: vendedores informados de que a reclamacao nao afeta a reputacao geram mais detratores, "
    "pois a expectativa criada vai alem — o vendedor ainda absorve o custo do reembolso. Em contraste, "
    "casos onde a reclamacao AFETA a reputacao têm NPS +23pp quando o rep oferece suporte ativo de mitigacao."
  ),
  destaques_positivos=[
    "+18.5pp vs target — maior margem de seguranca entre os drivers prioritarios",
    "CDU Reclamacao afeta reputacao +23pp WoW: honestidade e suporte ativo superam boa noticia passiva",
    "Time reconhecido: reps elogiados nominalmente como referencia de qualidade",
    "Volume crescente (+3.8% WoW) com NPS acima de 70%",
    "Padrao validado: suporte ativo de mitigacao gera mais promotores do que passividade informativa",
  ],
  destaques_negativos=[
    "WoW -4.2pp: queda consecutiva — era 76.1% em S2",
    "CDU Reclamacao nao afeta reputacao -43pp: paradoxo de expectativa frustrada",
    "Multi-atendimento: 8 atendentes sem resolucao relatado — escalada ineficiente",
    "VoC: falta de transparencia e incoerencia sistemica como tema dominante",
    "Newbies com menor qualidade em casos complexos de mediacao",
  ],
  impacto_estrategico=(
    "CLIENTE: Expectativa de protecao total nao cumprida — vendedor ainda absorve reembolso. "
    "OPERACAO: Multi-atendimento sem ownership gasta recurso sem desfecho. "
    "MARCA: Incoerencia entre o que e dito e feito cria detratores vocais e persistentes. "
    "EFICIENCIA: Gap de comunicacao e corrigivel com baixo custo — alto ROI potencial imediato."
  ),
  voc_positivos=(
    "Promotores elogiam relacionamento e atendimento resolutivo. Destaque: nao sei se era operador "
    "bom ou IA boa, mas o atendimento foi otimo — qualidade percebida sem distincao de canal. "
    "Padrao: quando ha empatia e resolucao ativa, o promotor e fiel."
  ),
  voc_negativos=(
    "Incoerentes. Falam uma coisa pela plataforma e depois fazem. / sem transparencia com o vendedor. "
    "Alem de 8 atendentes ninguem resolve e so me falam coisas que ja sei. Traicao de expectativa: "
    "foi informado que nao afeta reputacao mas ainda sofre consequencias financeiras."
  ),
  causas_raiz=[
    dict(
      problema="Comunicacao nao afeta reputacao cria expectativa de protecao total nao cumprida",
      evidencia_quant="CDU -43pp; NPS caiu de 90.9% para 47.8% em uma semana neste CDU",
      evidencia_qual="Falam uma coisa e depois fazem; vendedor ainda absorve reembolso",
      causa="A mensagem nao afeta reputacao e interpretada como resolucao total pelo vendedor",
      impacto="Detratores em casos onde o resultado ja e o melhor possivel — ineficiencia de alto impacto",
      urgencia="Alta",
      acao="Reformular comunicacao de desfecho: explicitar o que NAO afeta E o que AINDA ocorre"
    ),
    dict(
      problema="Multi-atendimento sem ownership em casos de mediacao",
      evidencia_quant="2 detratores citam 8 e 3 ou mais atendimentos sem resolucao",
      evidencia_qual="Alem de 8 atendentes ninguem resolve e so me falam coisas que ja sei",
      causa="Ausencia de ownership de caso — transferencia sem contexto a cada interacao",
      impacto="NPS deteriora exponencialmente apos terceira interacao sem resolucao",
      urgencia="Media",
      acao="Case lock em casos de mediacao: mesmo agente ate resolucao definitiva"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="Reescrever script de desfecho: explicitar o que nao afeta E o que ainda ocorre com suporte", impacto="Eliminacao do principal CDU de queda — alto ROI de comunicacao", facilidade="Alta", prioridade="1"),
    dict(acao="Case ownership em mediacoes: bloquear transferencia apos segunda abertura do caso", impacto="Eliminar detratores por multi-atendimento sem resolucao", facilidade="Media", prioridade="2"),
    dict(acao="Workshop de transparencia ativa com verbatins reais dos detratores desta semana", impacto="+2-3pp NPS geral no driver", facilidade="Alta", prioridade="3"),
  ],
  resumo_diretoria=(
    "Post Venta Seller Dev opera com 18.5pp de folga vs target (71.9%), mas cedeu -4.2pp nesta semana. "
    "A causa e um gap de comunicacao: nao afeta reputacao cria expectativa de protecao total nao cumprida "
    "— gerando detratores em casos com desfecho positivo. Quando o rep e honesto E oferece suporte de "
    "mitigacao, o NPS sobe +23pp. Acao de alto ROI e baixo custo: reformular a comunicacao de desfecho."
  ),
  conclusao_estrategica=(
    "Post Venta tem a maior margem vs target e a melhor qualidade operacional entre os drivers analisados. "
    "A queda WoW e corrigivel sem investimento operacional — e um problema de comunicacao de expectativa, "
    "nao de execucao. Replicar o padrao honestidade mais suporte ativo como script padrao."
  ),
  ganhos_a_escalar=[
    "Script de honestidade mais suporte ativo de mitigacao — +23pp vs abordagem passiva",
    "Qualidade Expert como benchmark — capturar e documentar melhores praticas para escalar",
    "Margem de +18.5pp vs target: usar como base para elevar target e aumentar exigencia operacional",
  ],
  problemas_a_corrigir=[
    "Comunicacao de desfecho cria expectativa nao gerenciada — reescrever script urgentemente",
    "Multi-atendimento sem ownership em casos complexos — case lock necessario",
    "Transparencia percebida como baixa — incoerencia entre o que e dito e o que ocorre",
  ],
  acoes_30_dias=[
    "Reescrever script: a reclamacao nao afeta sua reputacao, mas o reembolso ainda ocorre — vamos ver o que mais podemos fazer",
    "Case ownership em mediacoes: bloquear transferencia apos segunda abertura do mesmo caso",
    "Workshop de transparencia ativa usando verbatins reais dos detratores desta semana",
  ],
  alertas_criticos=(
    "ALERTA: Queda WoW consecutive de -4.2pp — pode erodir margem vs target em 2-3 semanas se nao corrigida. "
    "ALERTA: Gap de comunicacao e escalavel: mais reclamacoes implica impacto no NPS proporcionalmente maior."
  ),
  gerado_em="2026-05-04 — S1 27/abr-03/mai",
)

ea("PCF Vendedor Seller Dev",
  periodo="S1 27/abr-03/mai vs S2 20/abr-26/abr",
  resumo_executivo=(
    "PCF Vendedor Seller Dev foi o driver com maior crescimento WoW entre os prioritarios: +5.9pp "
    "(de 40.3% para 46.2%), agora 6.3pp acima do target de 39.9%. O crescimento veio de um CDU "
    "especifico: devolucoes fallidas tratadas por agentes humanos com NPS +65pp e 90.9% promotores. "
    "Em paralelo, CDU de Mediacao por IA caiu -60pp: decisoes incorretas da IA sem mecanismo de "
    "reversao para o agente. Este e o driver com maior variancia: +65pp e -60pp no mesmo periodo."
  ),
  destaques_positivos=[
    "WoW +5.9pp — maior crescimento WoW entre os drivers prioritarios desta semana",
    "CDU Devolucao fallida com NPS +65pp e 90.9% promotores: recuperacao de falha como fidelizacao",
    "Acima do target em +6.3pp apos semanas abaixo da meta",
    "Time com cordialidade e atencao consistentes — elogiados em 100% dos promotores amostrados",
    "Agente humano como diferencial competitivo: quando intervem, quase garante promotor",
  ],
  destaques_negativos=[
    "CDU Mediacao aberta com IA -60pp: maior queda de CDU em valor absoluto entre todos os drivers",
    "IA com decisoes incorretas: orientou Correios (processo errado); encerrou mediacao indevidamente",
    "Agente sem ferramenta para reverter decisao da IA — vendedor fica preso sem saida",
    "VoC: totalmente insatisfeito com tudo; taxa absurda e retem dinheiro do cliente",
    "Volume caindo 7.8% WoW — base menor amplifica volatilidade do NPS",
  ],
  impacto_estrategico=(
    "CLIENTE: Vendedor com dinheiro retido e mediacao incorreta pela IA sem caminho de reversao — impotencia. "
    "OPERACAO: Agente gasta tempo sem desfecho em casos de IA incorreta. "
    "JURIDICO: IA com impacto financeiro direto sem mecanismo de correcao — risco juridico e reputacional. "
    "EFICIENCIA: Recuperacao humana de falha logistica e o maior gerador de NPS do driver."
  ),
  voc_positivos=(
    "Promotores elogiam cordialidade e atencao consistentes. Vendedores novos expressam gratidao. "
    "Quando a recuperacao de falha e bem executada, o vendedor torna-se promotor vocal e fiel de longo prazo."
  ),
  voc_negativos=(
    "Totalmente insatisfeito com tudo. Taxa absurda e ainda fica com o dinheiro do cliente retido. "
    "Nada e resolvido quando estamos sem retorno de mediacao com o prazo ja expirado. "
    "Tema dominante: impotencia — dinheiro retido, mediacao incorreta pela IA e sem caminho de reversao."
  ),
  causas_raiz=[
    dict(
      problema="IA de mediacao com decisoes incorretas sem mecanismo de reversao para o agente",
      evidencia_quant="CDU -60pp; IA orientou Correios (processo incorreto); encerrou mediacao indevidamente",
      evidencia_qual="Assistente de IA orientou cliente a enviar microondas via Correios incorretamente; encerrou porque nao respondeu no prazo mas havia respondido",
      causa="Modelo sem threshold de confianca para casos logisticos complexos; agente sem tool de override",
      impacto="Detrator quase garantido com possivel perda financeira para o vendedor",
      urgencia="Critica",
      acao="Tool de override de decisao de IA para agente em casos com flag de complexidade logistica; escalar casos desta semana imediatamente"
    ),
    dict(
      problema="Dinheiro do cliente retido sem SLA de liberacao comunicado proativamente",
      evidencia_quant="2 detratores mencionam dinheiro retido diretamente nos comentarios",
      evidencia_qual="Taxa absurda e ainda fica com o dinheiro do cliente retido",
      causa="Processo de retencao de valores em mediacao sem comunicacao proativa de prazo de liberacao",
      impacto="Vendedor com fluxo de caixa afetado — risco de churn de sellers de pequeno porte",
      urgencia="Alta",
      acao="Comunicacao proativa com SLA de liberacao de valores retidos ao iniciar processo de mediacao"
    ),
  ],
  recomendacoes_curto=[
    dict(acao="URGENTE: Tool de override de decisao de IA para agente em casos com flag de complexidade logistica", impacto="Eliminacao do principal CDU de queda (-60pp)", facilidade="Baixa", prioridade="1"),
    dict(acao="Escalar para Produto os casos de IA desta semana: Correios (processo errado) e encerramento incorreto", impacto="Correcao do modelo IA para os casos-tipo identificados", facilidade="Alta", prioridade="2"),
    dict(acao="Comunicacao proativa de SLA de liberacao de valores retidos em toda mediacao", impacto="Reducao de detratores por expectativa financeira frustrada", facilidade="Media", prioridade="3"),
  ],
  resumo_diretoria=(
    "PCF Vendedor Seller Dev foi o destaque positivo da semana com +5.9pp WoW, ultrapassando o target. "
    "Motor da melhora: agentes humanos resolvendo devolucoes fallidas com excelencia (90.9% NPS). "
    "Risco critico: IA de mediacao com decisoes incorretas e sem mecanismo de reversao — 60pp de queda "
    "no CDU, com evidencia de dano financeiro ao vendedor. Acao urgente: tool de override para o agente."
  ),
  conclusao_estrategica=(
    "PCF demonstra que recuperacao de falha operacional e o caminho mais eficiente para NPS alto neste "
    "driver: 90.9% quando o agente humano resolve o erro da IA. Estrategia dual: corrigir IA na origem "
    "e capacitar agentes para recuperacao ativa. Com IA corrigida, driver pode atingir 50%+ NPS."
  ),
  ganhos_a_escalar=[
    "Recuperacao ativa de devolucao fallida por agente humano — +65pp e 90.9% NPS — protocolo a replicar",
    "Cordialidade e atencao do time como diferencial competitivo — capturar e padronizar",
    "Protocolo de orientacao para vendedores novos gera fidelidade — criar onboarding de PCF",
  ],
  problemas_a_corrigir=[
    "IA de mediacao com decisoes incorretas em casos logisticos — prioridade critica de produto",
    "Agente sem ferramenta de override de IA — gargalo com impacto financeiro direto ao vendedor",
    "Valores retidos sem SLA de liberacao comunicado — risco de churn de sellers pequenos",
  ],
  acoes_30_dias=[
    "URGENTE: Tool de override de decisao de IA para agente em casos de mediacao com complexidade logistica",
    "Escalar para Produto os casos de IA desta semana: processo Correios e encerramento com prazo incorreto",
    "Criar protocolo proativo de SLA de liberacao de valores retidos no inicio de toda mediacao",
  ],
  alertas_criticos=(
    "CRITICO: IA com impacto financeiro direto para o vendedor sem mecanismo de correcao — risco juridico "
    "e reputacional se escalar. ALERTA: Volume caindo -7.8% WoW com NPS volatil — 5-10 casos ruins "
    "podem mover o NPS 5pp negativamente."
  ),
  gerado_em="2026-05-04 — S1 27/abr-03/mai",
)

with open("dd_summaries.json", "w", encoding="utf-8") as f:
    json.dump(s, f, ensure_ascii=False, indent=2)
print("OK — dd_summaries.json atualizado com executive_analysis para 5 drivers.")
