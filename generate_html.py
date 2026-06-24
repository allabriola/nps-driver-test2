#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NPS Seller Dev BR — Daily Report Generator
Atualizado automaticamente pelo skill /metrics-cx:nps-seller-dev-br-daily
Rodar: python generate_html.py
"""

# ═══════════════════════════════════════════════════════════════
# SECTION 1: METADATA  ← skill atualiza esta seção
# ═══════════════════════════════════════════════════════════════
from datetime import datetime as _dt
REPORT_DATE = _dt.now().strftime("%d/%m/%Y")
REPORT_TIME = _dt.now().strftime("%H:%M")
S1_LABEL = "20/abr – 26/abr"
S2_LABEL = "13/abr – 19/abr"
VIG_LABEL = "27/abr – 27/abr"
M1_LABEL = "Abril 2026"
M2_LABEL = "Março 2026"
NPS_TARGET = 59.19  # SUM(NUM_TARGET_NPS)/SUM(DENOM_TARGET_NPS) via LK JOIN — Abril/2026
DRIVER_TARGETS = {   # SUM(NUM_TARGET_NPS)/SUM(DENOM_TARGET_NPS) por driver via LK JOIN — Abril/2026
    "Experiencia Impositiva Seller Dev": 59.03,
    "ME Vendedor Seller Dev":            57.80,
    "PCF Vendedor Seller Dev":           39.93,
    "Partners":                          70.19,
    "Post Venta Seller Dev":             53.40,
    "Publicaciones Seller Dev":          52.87,
}

# ═══════════════════════════════════════════════════════════════
# SECTION 1B: DEEP DIVE  ← atualizar manualmente após análise qualitativa
# ═══════════════════════════════════════════════════════════════
DEEP_DIVE_DATE = "04/05/2026"
DEEP_DIVE_POS_DRIVER = "ME Vendedor Seller Dev"
DEEP_DIVE_POS_VAR = "+1,42 pp"
DEEP_DIVE_POS_PROC = "Gestiones Operativas: NPS 53,03% (S2) → 63,93% (S1) (+10,90 pp) | 132 → 122 surveys | Reputación ME estável em 82,94% (S2) → 85,54% (S1) | âncora do driver"
DEEP_DIVE_POS_INSIGHTS = [
    "Gestiones Operativas lidera a alta em ME Vendedor: NPS subiu de 53,03% (13/abr) para 63,93% (20/abr), +10,90 pp — CDUs de onboarding logístico (ativar ME, ME Flex, ME Places) com atendimento consultivo gerando NPS 10 sistemático.",
    "Reputación ME é o processo âncora: NPS 82,94% (S2) → 85,54% (S1) em ~500 surveys por semana — atendentes nomeados (Rafael, Lidiane, Lucas) com resolução no 1º contato e escuta ativa geram menção nominal e NPS 10.",
    "Despacho Ventas y Publicaciones cresce: NPS 59,02% → 59,85% (+0,83 pp) — melhora discreta mas volume alto (654 surveys) confirma tendência positiva no canal de despacho.",
    "Detratores concentrados em bug de peso/dimensão: sistema assume peso de categoria sem permitir correção pelo atendente — 'tenho produto de 29kg cadastrado como 8kg, Correios não aceitam e atendente não consegue corrigir' — estrutural.",
]
DEEP_DIVE_NEG_DRIVER = "PCF Vendedor Seller Dev"
DEEP_DIVE_NEG_VAR = "-0,42 pp"
DEEP_DIVE_NEG_WHY = "PCF Vendedor caiu de 49,09% (S2) para 40,31% (S1), -8,78 pp em 129 surveys. Devolução falha é o maior gerador de detratores: produto retornado pelo comprador mas não chegou ao vendedor, ou chegou danificado — atendente orienta reclamação mas não tem poder de resolver a mediação."
DEEP_DIVE_NEG_PROC = "Post Compra Funcionalidades Vendedor: NPS 49,09% (S2) → 40,31% (S1) (-8,78 pp) | 137 → 129 surveys | único processo do driver"
DEEP_DIVE_NEG_INSIGHTS = [
    "Motivo de contato dominante (transcrições): devolução solicitada pelo comprador mas não realizada — prazo expirado, vendedor sem produto E sem pagamento retido por mediação em andamento. REP empático mas sem poder de ação: 'não consigo fechar essa mediação, não é a minha equipe que trata'.",
    "Múltiplas datas prometidas sem cumprimento: vendedor aguardou 4 datas remarcadas pelo ML sem resolução — '25/abr, 28/abr, 30/abr e agora 2/mai!' — sem comunicação proativa e sem owner fixo do caso.",
    "Transferências em cadeia sem resolução: mesmo caso passou por 4 atendentes distintos (Pablo → Jennifer → Kelly → Lucas) sem nenhum deles conseguir fechar a mediação — atendente herda problema mas não tem ferramenta para resolver.",
    "Impossibilidade de falar na mediação agrava a frustração: vendedor bloqueado de enviar mensagens enquanto aguarda resposta do comprador — 'a mediação é uma piada, eles nos bloqueiam e ficamos de mãos atadas'.",
]
DCEV_DETRATORES = [
    "USER — Devolução não realizada pelo comprador: prazo expirou, vendedor sem produto E com pagamento retido por mediação aberta — 'já aguardei 4 datas que vocês marcaram e nada foi resolvido' — frustração máxima com prejuízo duplo.",
    "USER — Impossibilidade de comunicação na mediação: vendedor bloqueado de enviar mensagens enquanto aguarda resposta do comprador — 'a mediação é uma piada, nos bloqueiam e ficamos de mãos atadas'.",
    "REP — Sem ferramenta para fechar mediação: 'não consigo fechar essa mediação, não é a minha equipe que trata' — transfere 3-4x sem resolução (Pablo → Jennifer → Kelly → Lucas).",
    "REP — Múltiplas datas sem cumprimento e sem comunicação proativa: ML remarca prazos sem notificar o vendedor — seller descobre pela própria planilha que o prazo passou sem resolução.",
]
DCEV_PROMOTORES = [
    "Atendentes com escuta ativa em casos de devolução: quando o atendente lê o histórico antes de responder e propõe ação concreta (mesmo que registrar para equipe especialista), o vendedor percebe o esforço — NPS 7-8.",
    "Resolução no 1º contato em casos simples (antes do reclamo): orientação de 'como ajudar o comprador' com passos claros gera FCR e NPS 9-10.",
    "Post Venta/Reputação dentro do driver (crossover): casos que chegam ao Reputación antes de virar mediação recebem exclusão de impacto com empatia — 'mesmo não podendo remover, foi ótimo atendimento' — NPS alto.",
]
DCEV_ACOES = [
    "Criar owner fixo para mediações com prazo de devolução expirado: atendente deve poder fechar a mediação e liberar o pagamento quando o prazo do comprador vencer — hoje nenhum atendente tem essa ferramenta.",
    "Implementar comunicação proativa do ML para vendedor quando prazo de mediação é remarcado — eliminar o padrão de 'descobri que não resolveram porque vi na planilha'.",
    "Limitar transferências em casos de mediação: máximo 2 transferências — após a 2ª, criar owner fixo com SLA de 24h para resolver.",
    "Criar fast track de ativação logística (ME/Flex) para sellers com histórico de vendas — reduzir frustração da espera de ativação mensal que gera NPS 0.",
]

# ═══════════════════════════════════════════════════════════════
# SECTION 1D: DEEP DIVE — SEMANA VIGENTE  ← atualizar após análise qualitativa
# ═══════════════════════════════════════════════════════════════
DD_VIG_DATE = "04/05/2026"
DD_VIG_POS_DRIVER = "ME Vendedor Seller Dev"
DD_VIG_POS_VAR = "+1,42 pp"
DD_VIG_POS_PROC = "Gestiones Operativas: 53,03% → 63,93% (+10,90 pp) | Reputación ME: 82,94% → 85,54% (+2,60 pp) | referência semana fechada S1 (20/abr–26/abr)"
DD_VIG_POS_INSIGHTS = [
    "Semana vigente (27/abr+) sem dados — exibindo referência da semana fechada S1 (20/abr–26/abr). ME Vendedor foi o maior driver positivo no fechamento de Abril (+1,42 pp MIX+NETO).",
    "Gestiones Operativas liderou a alta: +10,90 pp em 122 surveys — CDUs de onboarding logístico (ME, ME Flex, ME Places) com atendimento consultivo gerando NPS 10 sistemático.",
    "Reputación ME é o processo âncora: NPS 85,54% em 484 surveys — consistência histórica acima de 82% por múltiplas semanas seguidas.",
    "A monitorar na abertura de Maio: se ME Vendedor mantiver NPS >68% com Gestiones acima de 60%, confirma tendência de melhora operacional.",
]
DD_VIG_NEG_DRIVER = "PCF Vendedor Seller Dev"
DD_VIG_NEG_VAR = "-0,42 pp"
DD_VIG_NEG_WHY = "PCF Vendedor caiu de 49,09% (13/abr) para 40,31% (20/abr), -8,78 pp: único processo (Post Compra Funcionalidades) com padrão recorrente de devolução falha e mediação sem ferramenta de encerramento para o atendente."
DD_VIG_NEG_PROC = "Post Compra Funcionalidades Vendedor: NPS 49,09% (S2) → 40,31% (S1) (-8,78 pp) | 137 → 129 surveys"
DD_VIG_NEG_INSIGHTS = [
    "PCF Vendedor abaixo do target de 39,93%: NPS atual 40,31% vs 49,09% anterior — queda de -8,78 pp em volume estável (~130 surveys/semana).",
    "Devolução falha é a causa raiz dominante: produto não chegou após retorno ou chegou danificado — atendente orienta reclamação mas não pode resolver a mediação nem liberar o pagamento.",
    "Transferências em cadeia sem owner (Pablo → Jennifer → Kelly → Lucas) — cada atendente herda o problema mas não tem ferramenta para fechar a mediação.",
    "Ação prioritária: criar owner fixo para mediações com prazo expirado com ferramenta de encerramento — CDU de maior impacto negativo em PCF há múltiplas semanas.",
]
DD_VIG_DET = [
    "Suspensão preventiva sem justificativa: motorista com histórico impecável suspenso por 7 dias — atendente confirma mas não pode reverter (#452908085).",
    "Métricas caindo sem acesso: 'se houve reclamação, só o centro logístico tem acesso' (#452936125) — atendente sem visibilidade.",
    "Erros técnicos sem owner: rota concluída não aparece no desafio, case passou por 4 atendentes sem resolução (#452921370).",
    "Sentimento de abandono: 'estamos à deriva sem ninguém por nós no mercado livre' (#452936125) — motoristas questionam rentabilidade.",
]
DD_VIG_PRO = [
    "ME Vendedor/Despacho com forte melhora em S1: NPS 69,14% impulsionado por FCR e atendimento humanizado — atendentes nomeados (Josi, Kenia, Ana Paula) gerando NPS 10 sistemático.",
    "Post Venta Seller Dev estável em 71,89% (S1, 217 surveys) — Reputação com padrão positivo consistente.",
    "Exp. Impositiva em recuperação: fechou S1 em 52,86% vs 38,64% (S2) — monitorar se mantém acima de 59,67% (target) ao longo da semana.",
]
DD_VIG_ACO = [
    "Criar ferramenta de reversão de suspensão preventiva para atendente Partners — CDU dominante em Drivers sem resolução há múltiplas semanas.",
    "Dar acesso ao log de métricas ao atendente — eliminar resposta 'só o centro logístico tem acesso' que gera NPS 0.",
    "Monitorar ME Vendedor/Despacho ao longo da semana — se mantiver 65%+ confirma tendência de melhora operacional.",
    "Acompanhar Exp. Impositiva: fechou S1 em 52,86% (abaixo do target de 59,67%) mas em forte recuperação vs S2 (38,64%) — monitorar se confirma ou reverte.",
]

# ═══════════════════════════════════════════════════════════════
# SECTION 1E: DEEP DIVE — MENSAL  ← atualizar após análise qualitativa
# ═══════════════════════════════════════════════════════════════
DD_MES_DATE = "04/05/2026"
DD_MES_POS_DRIVER = "ME Vendedor Seller Dev"
DD_MES_POS_VAR = "+0,91 pp"
DD_MES_POS_PROC = "Despacho Ventas y Publicaciones: NPS 56,25% (Mar) → 59,91% (Abr) (+3,66 pp) | 2.062 → 3.020 surveys | Reversa: 50,90% → 60,28% (+9,38 pp) | Reputación ME estável em 82,39% | 2.226 surveys"
DD_MES_POS_INSIGHTS = [
    "ME Vendedor é o maior driver positivo do mês (+0,91 pp MIX+NETO): NPS subiu de 67,05% (Mar) para 68,84% (Abr) em 6.784 surveys — maior volume absoluto do portfólio, melhora distribuída entre processos de logística.",
    "Despacho Ventas y Publicaciones lidera a melhora: +3,66 pp em 3.020 surveys (Mar: 2.062) — maior processo do driver, subiu de 56,25% para 59,91% — sinal de melhora operacional em despachos e publicações vendedores.",
    "Reputación ME estável em alta: 82,84% (Abr, 2.424 surveys) → 78,05% (Mai, 82 surveys) — processo âncora do driver mantendo consistência histórica.",
    "Atenção: M1 (Maio) tem apenas 290 surveys para ME Vendedor vs 6.784 em Abril — NPS de mai/26 reflete apenas os primeiros 4 dias úteis, deve ser monitorado ao longo do mês para confirmar tendência.",
]
DD_MES_NEG_DRIVER = "Publicaciones Seller Dev"
DD_MES_NEG_VAR = "-1,19 pp"
DD_MES_NEG_WHY = "Publicaciones caiu de 68,45% (Mar) para 62,54% (Abr), MIX+NETO -1,19 pp em 2.600 surveys. Afiliados ML (-5,44 pp, 1.227 surveys) e Potenciar Ventas (-22,96 pp, 196 surveys) puxam a queda. IA de detecção de PI comete erros de classificação e atendentes passam informações contraditórias."
DD_MES_NEG_PROC = "Afiliados ML: NPS 70,07% (Mar) → 64,63% (Abr) (-5,44 pp) | 1.687 → 1.227 surveys (maior volume do driver) | Potenciar Ventas: 72,45% → 49,49% (-22,96 pp) | 265 → 196 surveys"
DD_MES_NEG_INSIGHTS = [
    "Afiliados ML com maior impacto absoluto em Publicaciones: MIX+NETO -2,85 pp — NPS caiu de 70,07% (Mar) para 64,63% (Abr) em 1.227 surveys (47% do volume do driver).",
    "Potenciar Ventas com maior queda percentual: NPS 72,45% (Mar) → 49,49% (Abr), -22,96 pp em 196 surveys — abaixo do target de 52,87% — processo que precisa de atenção imediata.",
    "PR - Propiedad intelectual com queda relevante: NPS 73,62% (Mar) → 64,25% (Abr) em 207 surveys — IA de detecção de PI com erros de classificação, atendentes passam informações contraditórias entre si.",
    "PR - Artículos prohibidos e Gestión de Publicación também em queda — múltiplos processos deteriorando simultaneamente sustentam o MIX+NETO -1,19 pp do driver.",
]
DD_MES_DET = [
    "Afiliados ML — maior volume e impacto: NPS caindo de 70,07% → 64,63% (-5,44 pp) — 47% do volume do driver, queda sustentada em 1.227 surveys de Abril.",
    "Potenciar Ventas — maior queda percentual: NPS -22,96 pp; abaixo do target de 52,87% — processo prioritário para ação.",
    "PR - Propiedad intelectual — IA acusa falsamente de violação — vendedor com NF da fabricante sem recurso eficiente; informações contraditórias entre analistas.",
    "PR-Técnica prohibida e Gestión de Publicación: queda de -4,88 pp e -4,23 pp respectivamente — múltiplos processos em queda simultânea.",
]
DD_MES_PRO = [
    "Atendentes nomeados em Reputação (Post Venta): Lidiane, Lucas, Daiane, Cicera, Mariana, Yasmin — resolução no 1º contato com exclusão de impacto gera NPS 10 consistente.",
    "Gestão humanizada de resposta negativa em Reputação: 'mesmo não podendo remover o impacto, foi ótimo atendimento' — empatia mantém NPS alto mesmo sem solução favorável.",
    "Afiliados ML e Antes de publicar mantêm Publicaciones com NPS > target de 52,87% apesar das quedas em outros processos.",
]
DD_MES_ACO = [
    "Revisão do motor de IA de detecção de PI: criar processo de recurso com análise humana obrigatória antes do bloqueio — erro de classificação em Propiedad intelectual gera NPS 0 e perda de vendedor.",
    "Padronizar resposta de atendentes para casos de PI com trilhas de decisão — eliminar informações contraditórias entre analistas.",
    "Para Afiliados ML e Potenciar Ventas: investigar causa da queda progressiva de NPS em Abril — se sazonalidade ou mudança de produto, tratar antes de virar tendência em Maio.",
    "Expandir atendimento humanizado de Reputação (Post Venta) como modelo: escuta ativa + exclusão de impacto no 1º contato é o padrão que gera NPS 70%+ — replicar para outros drivers.",
]

# ═══════════════════════════════════════════════════════════════
# SECTION 1F: ALERT DEEP DIVES  ← auto-detectado (negativo vs target + tendência de queda)
# ═══════════════════════════════════════════════════════════════
# ─── Análise Quantitativa por CDU/Processo/Solução (extraída de BT_CX_TRANSCRIPT)
ALERT_ANALYSIS = {
    "Experiencia Impositiva Seller Dev": {
        "cdu_breakdown": [
            {"cdu": "Temporal/DCe — obrigatório só via desktop",      "top_sol": "DCe para sellers (mobile bloqueado)",                "n":  6, "pct": 26.1},
            {"cdu": "Emissor externo — XML recusado/não informado",   "top_sol": "Emissor externo: como informar XML na venda",         "n":  4, "pct": 17.4},
            {"cdu": "Faturador indisponível / não emite/cancela NF",  "top_sol": "Emissão de NF: funcionalidade indisponível",          "n":  2, "pct":  8.7},
            {"cdu": "Faturador — não gera documentos / relatório",    "top_sol": "Faturador: gerar documentos / relatório",             "n":  4, "pct": 17.4},
            {"cdu": "Instabilidade SEFAZ",                            "top_sol": "Emissão de NF: instabilidade SEFAZ",                  "n":  2, "pct":  8.7},
        ],
        "user_themes": [
            "Encerramento sem resolução e reabertura sem contexto: ticket fechado sem aguardar confirmação, seller retorna do zero para o próximo atendente (#450867735, #447992026)",
            "NF pendente bloqueando anúncios FULL: '#451516035 — 3 chamados, 4 dias de bloqueio, perda mensurável de vendas' — SLA ausente",
            "IA passa informação errada por dias antes do humano corrigir — impacto na reputação do seller antes da correção (#450184747)",
            "Certificado digital não renovado bloqueando emissão: fora dos padrões do suporte — 'os problemas não respeitam os padrões' (#454075257)",
        ],
        "rep_themes": [
            "REP encerra ticket por timeout mesmo com problema aberto — seller retorna sem contexto (#450867735)",
            "REP passa o caso para equipe especialista gerando nova fila de espera — múltiplas transferências sem owner",
            "IA de 1ª linha repete informação incorreta; humano corrige tarde demais — impacto na reputação já registrado (#450184747)",
            "REP orienta corretamente mas não tem ferramenta para resolver bloqueios técnicos — empático mas sem ação (#452685429)",
        ],
    },
    "Partners": {
        "cdu_breakdown": [
            {"cdu": "Métricas / Nível de Lealdade",                        "top_sol": "ME Extra: motorista reclama sobre suas métricas / nível",  "n": 17, "pct": 20.5},
            {"cdu": "Dúvidas sobre funcionamento do Envios Extra",          "top_sol": "ME Extra: como funciona / como recebo pagamento",          "n": 12, "pct": 14.5},
            {"cdu": "Criação de conta / CNPJ / conflito de serviços",       "top_sol": "ME Extra: problemas com CNPJ / veículo / app",             "n": 11, "pct": 13.3},
            {"cdu": "Conta pausada / inativa sem justificativa",            "top_sol": "ME Extra: pausado — conta ativa / não houve visita",        "n":  9, "pct": 10.8},
            {"cdu": "Reclamação Service Center / inconveniência em rota",   "top_sol": "ME Extra: reclamação do Service Center / baixa pacote",     "n":  8, "pct":  9.6},
            {"cdu": "Oferta de rotas / sem rotas disponíveis",              "top_sol": "ME Extra: oferta de rotas",                                "n":  5, "pct":  6.0},
        ],
        "user_themes": [
            "Métricas/nível caindo sem acesso a detalhes: 'se houve reclamação, só o centro logístico tem acesso' (#452936125) — motoristas sem entender o motivo real da queda de nível",
            "Suspensão preventiva sem justificativa: 'não fiz nada de errado, tenho tudo registrado e mesmo assim fui penalizado' (#452908085) — motoristas com histórico impecável suspensos por 7 dias",
            "Erros técnicos sem owner: rota concluída não contabiliza no desafio, percurso some após confirmação — case #452921370 passou por 4 atendentes sem resolução",
            "Sentimento de abandono: 'sensação que temos é estamos à deriva sem ninguém por nós no mercado livre' (#452936125) — valores de rotas diminuíram, rentabilidade questionada",
        ],
        "rep_themes": [
            "REP sem visibilidade: 'não temos acesso às tarifas' e 'sobre reclamações, só o centro logístico tem acesso' (#452936125) — atendente empático mas bloqueado estruturalmente",
            "REP confirma suspensão mas não pode reverter: 'fique tranquilo, apos o período sua conta será reativada automaticamente' (#452908085) — sem ação no 1º contato",
            "REP múltiplo sem continuidade: cada atendente recomeça do zero pedindo as mesmas informações (#452921370: Mari → Claudemiro → Josué → Matheus)",
            "REP encerra com script 'aguardar análise interna' sem SLA — padrão sistêmico que gera NPS 0 para problemas estruturais",
        ],
    },
}

ALERT_SF = [
    {
        "drv": "Experiencia Impositiva Seller Dev", "proc": "Emision de Nota Fiscal",
        "nps_cur": 38.64, "nps_tgt": 59.03, "delta_tgt": -20.39, "trend": "↓↓ Em queda",
        "why": "Exp. Impositiva despencou de 49,38% (S2=13/abr) para 38,64% (S1=20/abr), -10,74 pp. KTA Newbie no canal C2C concentra a queda: Emissão NF KTA NPS negativo. SLA ausente e encerramento sem resolução como causas estruturais.",
        "insights": [
            "Exp. Impositiva com NPS 38,64% vs target 59,03% (-20,39 pp) — queda acelerada: 49,38% (13/abr) → 38,64% (20/abr), tendência 'em queda' confirmada.",
            "Ligação caindo sem retorno é causa estrutural recorrente: canal C2C com instabilidade persistente sem callback automático.",
            "NF pendente por 4+ dias com anúncios FULL inativos: impacto financeiro direto mensurável — SLA ausente.",
            "Respostas desconexas e encerramento sem resolução: IA repete informação incorreta antes do humano corrigir.",
        ],
        "acoes": [
            "Corrigir instabilidade do canal telefônico de Emissão NF — callback obrigatório em até 5 minutos após queda de ligação.",
            "Criar SLA de 24h para NF pendente com anúncio FULL ativo — prioridade máxima de resolução.",
            "Implementar histórico obrigatório no contexto do atendente antes de responder.",
            "Habilitar DCe no app mobile — canal desktop-only bloqueante para sellers mobile.",
        ],
    },
    {
        "drv": "Partners", "proc": "Drivers",
        "nps_cur": 67.04, "nps_tgt": 70.19, "delta_tgt": -3.15, "trend": "↓ Queda",
        "why": "Partners/Drivers com NPS 67,04% (S1=20/abr) vs target 70,19% (-3,15 pp). Contas pausadas sem ferramenta de reversão + bug de notificação de rotas dominam os detratores.",
        "insights": [
            "Partners/Drivers NPS 67,04% vs target 70,19% — tendência de queda: 67,59% (13/abr) → 67,04% (20/abr).",
            "Conta pausada sem justificativa: motorista inativado sem explicação — atendente registra mas não reativa.",
            "Bug de rotas: app mostra notificação mas ao abrir nenhuma rota aparece — problema sistêmico sem correção.",
            "Atendentes sem ferramentas: padrão 'aguardar análise interna' sem SLA — NPS 0 sistematicamente.",
        ],
        "acoes": [
            "Criar ferramenta para atendente reativar conta pausada por Digital Account.",
            "Corrigir bug de notificação de rotas no app — problema persistente há múltiplas semanas.",
            "Capacitar atendentes Drivers com acesso ao sistema de conta e rotas.",
            "Revisar política de pausa com contestação de SLA de 24h.",
        ],
    },
]

ALERT_VA = []

ALERT_MES = [
    {
        "drv": "Partners", "proc": "Drivers",
        "nps_cur": 65.65, "nps_tgt": 70.19, "delta_tgt": -4.54, "trend": "↓ Queda",
        "why": "Partners NPS 65,65% (Abril) vs target 70,19% (-4,54 pp) — 2º mês consecutivo abaixo do target: Fev 72,38% → Mar 67,39% → Abr 65,65%. Conta pausada por Digital Account e bug de rotas como CDUs dominantes sem solução técnica.",
        "insights": [
            "Partners NPS 65,65% vs target 70,19% (-4,54 pp) — queda de Mar 67,39% → Abr 65,65% (-1,74 pp), abaixo do target pelo segundo mês consecutivo.",
            "Conta pausada sem justificativa é CDU dominante em Drivers: motoristas com conta desativada por Digital Account sem ferramenta de reativação pelo atendente.",
            "Bug de rotas persiste: app mostra notificação disponível mas rota não aparece — problema sistêmico sem correção há múltiplas semanas.",
            "Atendentes sem ferramentas: padrão de 'aguardar análise interna' sem SLA — NPS 0 sistematicamente.",
        ],
        "acoes": [
            "Criar ferramenta para atendente reativar conta pausada por Digital Account — causa raiz do CDU dominante.",
            "Corrigir bug de notificação de rotas no app com prioridade — problema sistêmico presente há mais de 2 semanas.",
            "Criar canal de suporte dedicado para Partners/Drivers com ferramentas de acesso.",
            "Monitorar NPS Drivers mensalmente — 2º mês abaixo do target, escalar para revisão de produto antes do M3.",
        ],
    },
]

# ═══════════════════════════════════════════════════════════════
# SECTION 1G: DRIVER INSIGHTS — análise executiva completa por driver (WoW + MoM)
# Framework: consultivo estratégico, baseado em evidências, orientado a decisão
# ═══════════════════════════════════════════════════════════════
DRIVER_INSIGHTS_WOW = {
    "Experiencia Impositiva Seller Dev": [
        "NPS 38,64% (20/abr) vs 49,38% (13/abr): queda de -10,74 pp — pior variação semanal do portfólio, -20,39 pp abaixo do target de 59,03%; risco de fechamento de Maio negativo se padrão persistir.",
        "Emissão NF lidera a deterioração: NPS 34,69% em 49 surveys (-13,04 pp vs S2) — NF pendente bloqueia anúncios FULL sem SLA; atendente registra mas não resolve; CDU de maior impacto no driver.",
        "Facturación em queda paralela: NPS 32,26% (-14,29 pp vs S2 46,55%) em 31 surveys — IA de 1ª linha repete informação incorreta por múltiplos contatos antes de correção humana; encerramento por timeout sem confirmação do vendedor.",
        "Dados Fiscais estável em alta (87,5%, 8 surveys) — único processo com performance acima do target; orientação direta no 1º contato via chat; base de boas práticas para benchmarking.",
        "Ação imediata: SLA 24h para NF com FULL ativo + callback C2C obrigatório em até 5 min após queda de ligação; habilitar DCe no app mobile elimina CDU dominante de acesso restrito a desktop.",
    ],
    "ME Vendedor Seller Dev": [
        "NPS 69,27% (20/abr) vs 65,86% (13/abr): alta de +3,41 pp — maior driver positivo da semana, +11,47 pp acima do target de 57,80%; 1.308 surveys com solidez operacional comprovada.",
        "Gestiones Operativas lidera: NPS 63,93% (+10,90 pp vs S2 53,03%) em 122 surveys — CDUs de ativação logística (ME Flex, ME Places) com atendimento consultivo; NPS 10 sistemático por atendentes nomeados.",
        "Reputación ME processo âncora: NPS 85,54% (+5,31 pp vs S2 80,23%) em 484 surveys — FCR + escuta ativa + exclusão de impacto com empatia como padrão operacional; acima de 80% por múltiplas semanas consecutivas.",
        "Reversa em forte recuperação: NPS 53,49% (+9,63 pp vs S2 43,86%) em 86 surveys — melhora na gestão de retorno de pacotes com comunicação proativa reduzindo detratores por falta de acompanhamento.",
        "Atenção: Viaje del paquete com leve queda (58,97%, -4,67 pp vs S2) em 78 surveys — volume pequeno, monitorar tendência; detector de bug de rastreamento como causa provável.",
        "Oportunidade estratégica: modelo de atendimento de Reputación (owner fixo + empatia + FCR) é o padrão que gera NPS 85%+ — replicar para Exp. Impositiva e Partners pode gerar lift de 10-15 pp.",
    ],
    "PCF Vendedor Seller Dev": [
        "NPS 40,31% (20/abr) vs 48,91% (13/abr): queda de -8,60 pp — driver com único processo (Post Compra Funcionalidades Vendedor), 129 surveys; apenas +0,38 pp acima do target de 39,93%.",
        "Margem zero vs target: qualquer queda adicional coloca PCF abaixo da meta em Maio — cenário de risco real considerando a tendência de -8,60 pp na semana atual.",
        "Causa dominante: devolução solicitada pelo comprador não realizada — prazo expirado, vendedor sem produto E com pagamento retido por mediação ativa; atendente empático mas sem ferramenta para fechar a mediação.",
        "Transferência em cadeia sem owner: casos passam por 3-4 atendentes distintos (Pablo → Jennifer → Kelly → Lucas) sem continuidade — cada atendente recomeça do zero pedindo as mesmas informações; NPS 0 recorrente.",
        "Ação prioritária: criar ferramenta de encerramento de mediação para atendentes PCF com SLA de 24h após prazo de devolução expirado; limitar transferências a máximo 2 com owner fixo obrigatório após a 2ª.",
    ],
    "Partners": [
        "NPS 67,04% (20/abr) vs 67,59% (13/abr): queda de -0,55 pp — deterioração marginal mas confirma tendência de declínio; -3,15 pp abaixo do target de 70,19% pelo 2º mês consecutivo.",
        "Drivers processo dominante: NPS 65,97% (-0,48 pp vs S2), 626 surveys — conta pausada por Digital Account sem ferramenta de reativação é CDU principal; atendente confirma a suspensão mas não pode reverter no 1º contato.",
        "Places Kangu estável e acima do target: NPS 74,19% (+0,69 pp vs S2), 93 surveys — única âncora positiva do driver; padrão de atendimento logístico funcionando bem; base para benchmarking interno.",
        "Bug sistêmico persistente: app exibe notificação de rota disponível mas ao abrir não há rotas — problema sem correção técnica há mais de 2 semanas; gera NPS 0 recorrente e sentimento de abandono nos motoristas.",
        "Risco estratégico: motoristas questionando rentabilidade ('estamos à deriva') — sem solução de produto para suspensão e bug de rotas, churn de parceiros logísticos é risco de médio prazo com impacto na capacidade de entrega.",
        "Ação prioritária: criar ferramenta de reativação de conta para atendente + corrigir bug de notificação de rotas — ambas as CDUs dominantes requerem solução de produto, não apenas melhoria de atendimento.",
    ],
    "Post Venta Seller Dev": [
        "NPS 76,08% (20/abr) vs 73,39% (13/abr): alta de +2,69 pp — melhor NPS absoluto semanal do portfólio, +22,68 pp acima do target de 53,40%; excelência operacional consistente.",
        "Reputación ME processo âncora: NPS 77,11% (+4,54 pp vs S2 72,57%) em 201 surveys — exclusão de impacto com empatia no 1º contato; atendentes nomeados (Lidiane, Lucas, Daiane) com alta frequência de menção positiva em surveys.",
        "Padrão replicável: FCR + escuta ativa + resolução sem transferência são os 3 drivers de promotores em Reputación — resultado direto de treinamento diferenciado vs outros drivers do portfólio.",
        "Anulación de Venta com oscilação pontual (50,00%, 8 surveys) — volume muito pequeno, sem significância estatística; padrão semanal anterior era 100% (13/abr).",
        "Oportunidade de escala: documentar e sistematizar protocolo de atendimento de Reputación como benchmark; exportar para Exp. Impositiva e Partners é a maior oportunidade de lift NPS cross-driver do portfólio.",
    ],
    "Publicaciones Seller Dev": [
        "NPS 62,89% (20/abr) vs 63,55% (13/abr): leve queda de -0,66 pp — driver mantém boa posição relativa (+10,02 pp vs target de 52,87%) mas com processos específicos em deterioração acelerada.",
        "Potenciar Ventas em colapso pontual: NPS 35,48% (-34,29 pp vs S2 69,77%) em 31 surveys — maior queda percentual da semana; funcionalidades de impulsionamento com erro de precificação/resultado entregue vs prometido.",
        "PR - Artículos prohibidos deteriora: NPS 38,24% (-6,59 pp vs S2), 34 surveys — classificação incorreta de produto pelo sistema sem recurso eficiente; atendente orienta mas não tem ferramenta para reversão imediata.",
        "Gestión de Publicación em recuperação: NPS 61,29% (+13,92 pp vs S2 47,37%) em 62 surveys — orientação proativa com checklist funciona; padrão positivo emergente a ser replicado.",
        "Processos premium sustentam o driver: Antes de publicar (86,84%), PR Propiedad intelectual (77,27%) e PR Técnica (72,00%) com alta performance — ancoragem do NPS total acima do target.",
    ],
}

DRIVER_INSIGHTS_MOM = {
    "Experiencia Impositiva Seller Dev": [
        "NPS 50,87% (Abril) vs 43,50% (Março): recuperação de +7,37 pp — melhora substancial mas ainda -8,16 pp abaixo do target de 59,03%; 572 surveys; tendência de melhora precisa consolidar.",
        "Facturación sustenta a melhora: NPS 43,75% (+15,24 pp vs Março 28,51%) em 192 surveys — recuperação expressiva via canal Chat; indica que canais de atendimento alternativo ao C2C funcionam melhor.",
        "Emissão NF em queda contínua: NPS 53,61% (-4,58 pp vs Março 58,19%) em 332 surveys — processo de maior volume do driver; CDUs estruturais não resolvidos (NF pendente + SLA ausente) geram deterioração progressiva.",
        "Dados Fiscais estável: NPS 60,42% vs Março 64,00% (-3,58 pp), 48 surveys — ligeiro declínio em volume pequeno; processo administrável com resolução consistente no 1º contato.",
        "Risco em Maio: se Emissão NF não recuperar para 58%+ (nível de Março) e Facturación consolidar a melhora, driver pode fechar Maio ainda abaixo do target; DCe mobile e SLA de NF são desbloqueadores críticos.",
    ],
    "ME Vendedor Seller Dev": [
        "NPS 68,84% (Abril) vs 67,09% (Março): alta de +1,75 pp — maior volume do portfólio (6.784 surveys), +11,04 pp acima do target de 57,80%; solidez estrutural em todos os principais processos.",
        "Reversa em forte recuperação: NPS 60,79% (+9,89 pp vs Março 50,90%) em 482 surveys — gestão de logística reversa com comunicação mais proativa; menos detratores por falta de acompanhamento de retorno.",
        "Despacho cresce com volume: NPS 60,93% (+4,68 pp vs Março 56,25%) em 3.020 surveys — maior processo do driver em volume; tendência positiva sustentada com FCR e orientação humanizada.",
        "Reputación ME processo âncora: NPS 82,84% (+2,41 pp vs Março 80,43%) em 2.424 surveys — acima de 80% por 2 meses consecutivos; modelo de excelência operacional com atendentes nomeados e NPS 10 sistemático.",
        "Gestiones Operativas com leve queda: NPS 62,13% (-6,08 pp vs Março 68,21%) e Viaje paquete: 60,26% (-8,69 pp) — monitorar se deterioração em onboarding e rastreamento é sazonalidade ou estrutural; volume menor em Abril.",
        "Prioridade estratégica: documentar protocolo de Reputación (owner fixo + empatia + FCR) como benchmark cross-driver — maior impacto potencial com menor investimento no portfólio.",
    ],
    "PCF Vendedor Seller Dev": [
        "NPS 48,68% (Abril) vs 46,84% (Março): leve melhora de +1,84 pp — +8,75 pp acima do target de 39,93%; volume de 569 surveys em Abril vs 790 em Março (-27,9% de redução de volume).",
        "Redução de volume pode mascarar melhora real: -221 surveys podem indicar migração para self-service ou resolução upstream do problema — investigar se a queda de volume é estrutural ou sazonalidade.",
        "Processo único (Post Compra Funcionalidades Vendedor) com causa-raiz estável e não resolvida: devolução falha + mediação sem owner + múltiplas remarcações de prazo — problemas estruturais persistem sem solução de produto.",
        "Sinal de alerta semanal: queda de -8,60 pp em S1 (20/abr) para 40,31% — margem zero vs target mensal; se padrão semanal persistir, PCF pode fechar Maio negativo vs target.",
        "Ação de produto: fast-track de mediação para casos com prazo de devolução expirado + liberar pagamento do vendedor após comprovação de não retorno do produto — impacto financeiro direto e mensurável para o seller.",
    ],
    "Partners": [
        "NPS 65,65% (Abril) vs 67,39% (Março): queda de -1,74 pp — 3º mês consecutivo abaixo do target; trajetória: Fev 72,38% → Mar 67,39% → Abr 65,65% — tendência de deterioração estrutural confirmada.",
        "Drivers em queda: NPS 64,86% (-1,85 pp vs Março 66,71%) em 2.339 surveys — conta pausada por Digital Account e bug de rotas persistem sem solução técnica; atendente sem ferramentas é o padrão dominante.",
        "Places Kangu acompanha queda: NPS 69,29% (-1,03 pp vs Março 70,32%) em 508 surveys — ainda acima do target, mas 2º mês em declínio; risco de cruzar o target negativo em Maio se tendência continuar.",
        "Impacto estratégico: motoristas com sentimento de abandono e questionando rentabilidade ('estamos à deriva sem ninguém por nós') — risco de churn de parceiros logísticos com impacto direto na capacidade de entrega MeLi.",
        "Escalada necessária: 3 meses abaixo do target confirma que solução operacional não é suficiente — requer revisão de produto com prioridade para: (1) reativação de conta pelo atendente, (2) correção do bug de rotas.",
    ],
    "Post Venta Seller Dev": [
        "NPS 69,97% (Abril) vs 63,32% (Março): maior evolução MoM do portfólio em +6,65 pp — 1.059 surveys, +16,57 pp acima do target de 53,40%; excelência operacional com melhor performance mensal do quarter.",
        "Reputación sustenta e cresce: NPS 70,03% (+5,82 pp vs Março 64,21%) em 1.023 surveys — 97% do volume do driver; atendentes nomeados (Lidiane, Daiane, Cicera, Yasmin) com FCR e exclusão de impacto no 1º contato.",
        "Anulación de Venta em forte recuperação: NPS 69,44% (+28,14 pp vs Março 41,30%) em 36 surveys — volume pequeno mas recuperação expressiva; gestão de venda cancelada com comunicação mais eficaz e expectativa alinhada.",
        "Modelo de excelência replicável: 2 meses consecutivos acima de 63% confirmam que o protocolo de atendimento de Reputación (escuta ativa + empatia + SLA definido + owner fixo) é o driver de promotores mais consistente do portfólio.",
        "Prioridade estratégica: mapear e documentar o protocolo completo de Reputación (Post Venta) como benchmark corporativo; piloto de replicação para Exp. Impositiva tem potencial de lift de 10-15 pp no driver de maior gap vs target.",
    ],
    "Publicaciones Seller Dev": [
        "NPS 62,54% (Abril) vs 68,45% (Março): maior queda MoM do portfólio em -5,91 pp — 2.600 surveys (vs Março 3.309 = -21,5% de volume); ainda +9,67 pp acima do target de 52,87%, mas trajetória preocupante.",
        "Afiliados ML principal vetor da queda: NPS 64,63% (-5,44 pp vs Março 70,07%) em 1.227 surveys (47% do driver) — maior impacto absoluto; queda sustentada em volume alto indica mudança estrutural, não sazonalidade pontual.",
        "Potenciar Ventas em deterioração acelerada: NPS 49,49% (-7,87 pp vs Março 57,36%) em 196 surveys — abaixo do target de 52,87%; funcionalidades de impulsionamento com maior frustração; expectativa de resultado vs entregue é causa-raiz provável.",
        "PR Propiedad Intelectual cai -9,37 pp: NPS 64,25% (207 surveys) — IA de detecção de PI com erros de classificação gerando bloqueios indevidos; atendentes com informações contraditórias entre si; risco reputacional direto para sellers legítimos.",
        "Antes de publicar estável: NPS 76,41% (+1,50 pp vs Março) em 195 surveys — único processo em crescimento; orientação consultiva e proativa funciona; benchmark positivo interno do driver.",
        "Ação prioritária: revisão do motor de IA de PI + investigação de causa-raiz em Afiliados ML; padronizar resposta para casos de PI com trilhas de decisão claras para eliminar contradições entre atendentes.",
    ],
}

# ═══════════════════════════════════════════════════════════════
# SECTION 2: DATA  ← skill atualiza esta seção (tuplas: promoters, detractors, surveys)
# ═══════════════════════════════════════════════════════════════
weekly_driver = {
    "Experiencia Impositiva Seller Dev": {"S2":(112,33,160),    "S1":(57,23,88)},
    "ME Vendedor Seller Dev":            {"S2":(1154,178,1482), "S1":(1058,152,1308)},
    "PCF Vendedor Seller Dev":           {"S2":(95,28,137),     "S1":(82,30,129)},
    "Partners":                          {"S2":(575,85,725),    "S1":(567,85,719)},
    "Post Venta Seller Dev":             {"S2":(194,23,233),    "S1":(177,18,209)},
    "Publicaciones Seller Dev":          {"S2":(453,80,587),    "S1":(398,76,512)},
}
monthly_driver = {
    "Experiencia Impositiva Seller Dev": {"M2":(312,108,469),   "M1":(404,113,572)},
    "ME Vendedor Seller Dev":            {"M2":(4958,754,6266), "M1":(5420,750,6784)},
    "PCF Vendedor Seller Dev":           {"M2":(536,166,790),   "M1":(395,118,569)},
    "Partners":                          {"M2":(2228,337,2806), "M1":(2229,360,2847)},
    "Post Venta Seller Dev":             {"M2":(929,178,1186),  "M1":(857,116,1059)},
    "Publicaciones Seller Dev":          {"M2":(2639,374,3309), "M1":(2000,374,2600)},
}
weekly_proc = {
    "Experiencia Impositiva Seller Dev":{
        "S2":{"Datos fiscales":(12,2,14),"Emision de Nota Fiscal":(61,19,88),"Facturación":(39,12,58)},
        "S1":{"Datos fiscales":(7,0,8),"Emision de Nota Fiscal":(31,14,49),"Facturación":(19,9,31)},
    },
    "ME Vendedor Seller Dev":{
        "S2":{"Despacho Ventas y Publicaciones":(476,90,654),"Gestiones Operativas":(96,26,132),"Reputación ME":(454,26,516),"Reversa":(78,28,114),"Viaje del paquete - Vendedor":(50,8,66)},
        "S1":{"Despacho Ventas y Publicaciones":(402,80,538),"Gestiones Operativas":(94,16,122),"Reputación ME":(440,26,484),"Reversa":(64,18,86),"Viaje del paquete - Vendedor":(58,12,78)},
    },
    "PCF Vendedor Seller Dev":{
        "S2":{"Post Compra Funcionalidades Vendedor":(95,28,137)},
        "S1":{"Post Compra Funcionalidades Vendedor":(82,30,129)},
    },
    "Partners":{
        "S2":{"Drivers":(478,74,608),"Places Kangu":(97,11,117)},
        "S1":{"Drivers":(489,76,626),"Places Kangu":(78,9,93)},
    },
    "Post Venta Seller Dev":{
        "S2":{"Anulación de Venta":(7,0,7),"Reputación":(187,23,226)},
        "S1":{"Anulación de Venta":(6,2,8),"Reputación":(171,16,201)},
    },
    "Publicaciones Seller Dev":{
        "S2":{"Afiliados ML":(220,43,284),"Antes de publicar":(44,3,50),"Calidad de foto":(5,0,6),"Denuncia de usuario":(10,1,12),"Gestión de Publicación":(37,10,57),"PR - Artículos prohibidos":(20,7,29),"PR - Datos Personales":(1,0,1),"PR - Propiedad intelectual":(41,5,51),"PR - Técnica prohibida":(39,5,54),"Potenciar Ventas":(36,6,43)},
        "S1":{"Afiliados ML":(165,32,214),"Antes de publicar":(34,1,38),"Calidad de foto":(6,0,6),"Denuncia de usuario":(9,3,13),"Gestión de Publicación":(46,8,62),"PR - Artículos prohibidos":(22,9,34),"PR - Datos Personales":(6,0,6),"PR - Propiedad intelectual":(38,4,44),"PR - Técnica prohibida":(43,7,50),"Potenciar Ventas":(29,12,45)},
    },
}
monthly_proc = {
    "Experiencia Impositiva Seller Dev":{
        "M2":{"Datos fiscales":(39,7,50),"Emision de Nota Fiscal":(129,26,177),"Facturación":(144,75,242)},
        "M1":{"Datos fiscales":(36,7,48),"Emision de Nota Fiscal":(240,62,332),"Facturación":(128,44,192)},
    },
    "ME Vendedor Seller Dev":{
        "M2":{"Despacho Ventas y Publicaciones":(1520,360,2062),"Gestiones Operativas":(546,74,692),"Reputación ME":(2080,148,2402),"Reversa":(468,128,668),"Suspensiones ME":(0,2,4),"Viaje del paquete - Vendedor":(344,42,438)},
        "M1":{"Despacho Ventas y Publicaciones":(2268,428,3020),"Gestiones Operativas":(414,76,544),"Reputación ME":(2142,134,2424),"Reversa":(366,72,482),"Suspensiones ME":(2,0,2),"Viaje del paquete - Vendedor":(228,40,312)},
    },
    "PCF Vendedor Seller Dev":{
        "M2":{"Post Compra Funcionalidades Vendedor":(536,166,790)},
        "M1":{"Post Compra Funcionalidades Vendedor":(395,118,569)},
    },
    "Partners":{
        "M2":{"Drivers":(1797,278,2277),"Places Kangu":(431,59,529)},
        "M1":{"Drivers":(1819,302,2339),"Places Kangu":(410,58,508)},
    },
    "Post Venta Seller Dev":{
        "M2":{"Anulación de Venta":(30,11,46),"Reputación":(899,167,1140)},
        "M1":{"Anulación de Venta":(30,5,36),"Reputación":(827,111,1023)},
    },
    "Publicaciones Seller Dev":{
        "M2":{"Afiliados ML":(1362,180,1687),"Antes de publicar":(219,19,267),"Asignación del Contáctanos - Prustomer":(0,0,1),"Calidad de foto":(43,2,47),"Denuncia de usuario":(85,12,109),"Gestión de Publicación":(213,39,284),"PR - Artículos prohibidos":(77,25,113),"PR - Datos Personales":(11,4,15),"PR - Propiedad intelectual":(198,25,235),"PR - Técnica prohibida":(235,25,286),"Potenciar Ventas":(196,43,265)},
        "M1":{"Afiliados ML":(959,166,1227),"Antes de publicar":(162,14,195),"Calidad de foto":(18,5,25),"Denuncia de usuario":(54,12,71),"Gestión de Publicación":(196,42,270),"PR - Artículos prohibidos":(98,31,137),"PR - Datos Personales":(11,6,18),"PR - Propiedad intelectual":(164,31,207),"PR - Técnica prohibida":(203,28,254),"Potenciar Ventas":(135,39,196)},
    },
}

# ═══════════════════════════════════════════════════════════════
# SECTION 2B: VIGENTE DATA  ← skill atualiza esta seção
# ═══════════════════════════════════════════════════════════════
drivers_vigente = {
    "Experiencia Impositiva Seller Dev": (0,0,0),
    "ME Vendedor Seller Dev":            (0,0,0),
    "PCF Vendedor Seller Dev":           (0,0,0),
    "Partners":                          (0,0,0),
    "Post Venta Seller Dev":             (0,0,0),
    "Publicaciones Seller Dev":          (0,0,0),
}
proc_vigente = {
    "Experiencia Impositiva Seller Dev": {},
    "ME Vendedor Seller Dev":            {},
    "PCF Vendedor Seller Dev":           {},
    "Partners":                          {},
    "Post Venta Seller Dev":             {},
    "Publicaciones Seller Dev":          {},
}

# ═══════════════════════════════════════════════════════════════
# SECTION 2C: HISTORICAL DATA  ← skill atualiza esta seção
# ═══════════════════════════════════════════════════════════════
MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr"]
WEEK_LABELS  = ["16/mar", "23/mar", "30/mar", "06/abr", "13/abr", "20/abr"]

monthly_history = {
    "Experiencia Impositiva Seller Dev": {"Jan":(574,111,744),  "Fev":(350,86,477),   "Mar":(312,108,469),  "Abr":(404,113,572)},
    "ME Vendedor Seller Dev":            {"Jan":(8138,1110,9984),"Fev":(5136,734,6390),"Mar":(4958,754,6266),"Abr":(5420,750,6784)},
    "PCF Vendedor Seller Dev":           {"Jan":(697,244,1059),  "Fev":(529,173,768),  "Mar":(536,166,790),  "Abr":(395,118,569)},
    "Partners":                          {"Jan":(1793,251,2254), "Fev":(1808,217,2198),"Mar":(2228,337,2806),"Abr":(2229,360,2847)},
    "Post Venta Seller Dev":             {"Jan":(1206,265,1585), "Fev":(983,209,1291), "Mar":(929,178,1186), "Abr":(857,116,1059)},
    "Publicaciones Seller Dev":          {"Jan":(3396,475,4216), "Fev":(2581,381,3231),"Mar":(2639,374,3309),"Abr":(2000,374,2600)},
}
weekly_history = {
    "Experiencia Impositiva Seller Dev": {"16/mar":(82,20,113),  "23/mar":(60,19,90),   "30/mar":(66,25,100),  "06/abr":(150,36,208), "13/abr":(112,33,160), "20/abr":(57,23,88)},
    "ME Vendedor Seller Dev":            {"16/mar":(1130,152,1420),"23/mar":(1088,164,1358),"30/mar":(1016,158,1270),"06/abr":(1676,224,2106),"13/abr":(1154,178,1482),"20/abr":(1058,152,1308)},
    "PCF Vendedor Seller Dev":           {"16/mar":(121,31,168), "23/mar":(113,38,167), "30/mar":(84,23,125),  "06/abr":(98,29,136),  "13/abr":(95,28,137),  "20/abr":(82,30,129)},
    "Partners":                          {"16/mar":(528,69,659), "23/mar":(450,75,573), "30/mar":(448,77,574), "06/abr":(460,76,587),  "13/abr":(575,85,725), "20/abr":(567,85,719)},
    "Post Venta Seller Dev":             {"16/mar":(215,28,261), "23/mar":(214,41,280), "30/mar":(176,39,233), "06/abr":(239,39,301),  "13/abr":(194,23,233), "20/abr":(177,18,209)},
    "Publicaciones Seller Dev":          {"16/mar":(591,92,748), "23/mar":(574,74,718), "30/mar":(502,88,653), "06/abr":(607,103,769), "13/abr":(453,80,587), "20/abr":(398,76,512)},
}
# Vigente (parcial — adicionado à série semanal na aba Semana Atual)
weekly_history_vig = {drv: {**weekly_history[drv], "27/abr ⚡": drivers_vigente[drv]} for drv in weekly_history}
WEEK_LABELS_VIG = WEEK_LABELS + ["27/abr ⚡"]

# ═══════════════════════════════════════════════════════════════
# SECTION 2D: SENIORITY DATA  ← skill atualiza esta seção
# Fonte: DM_CX_NPS_Y20_DETAIL + LK_CX_PLANNING_GROUP (FLAG_PLANNING="true")
# Tuplas: (promoters, detractors, surveys) — mesma convenção das demais seções
# ═══════════════════════════════════════════════════════════════
seniority_weekly = {
    "Experiencia Impositiva Seller Dev": {
        "S2": {"EXPERT":(40,7,48),    "NEWBIE":(27,17,53)},
        "S1": {"EXPERT":(57,15,79),   "NEWBIE":(71,24,104)},
    },
    "ME Vendedor Seller Dev": {
        "S2": {"EXPERT":(387,53,472), "NEWBIE":(329,54,412)},
        "S1": {"EXPERT":(468,52,565), "NEWBIE":(300,56,397)},
    },
    "PCF Vendedor Seller Dev": {
        "S2": {"EXPERT":(146,31,203), "NEWBIE":(58,23,92)},
        "S1": {"EXPERT":(170,43,243), "NEWBIE":(40,19,65)},
    },
    "Partners": {
        "S2": {"EXPERT":(234,41,306), "NEWBIE":(339,46,422)},
        "S1": {"EXPERT":(320,34,378), "NEWBIE":(237,41,314)},
    },
    "Post Venta Seller Dev": {
        "S2": {"EXPERT":(212,15,239), "NEWBIE":(162,10,182)},
        "S1": {"EXPERT":(227,24,272), "NEWBIE":(143,15,166)},
    },
    "Publicaciones Seller Dev": {
        "S2": {"EXPERT":(158,17,185), "NEWBIE":(335,69,437)},
        "S1": {"EXPERT":(206,26,251), "NEWBIE":(335,79,460)},
    },
}
seniority_monthly = {
    "Experiencia Impositiva Seller Dev": {"EXPERT":(202,41,263),  "NEWBIE":(204,80,321)},
    "ME Vendedor Seller Dev":            {"EXPERT":(1719,235,2119),"NEWBIE":(1215,188,1542)},
    "PCF Vendedor Seller Dev":           {"EXPERT":(539,126,748), "NEWBIE":(166,65,256)},
    "Partners":                          {"EXPERT":(990,125,1213),"NEWBIE":(848,145,1105)},
    "Post Venta Seller Dev":             {"EXPERT":(731,86,879),  "NEWBIE":(512,57,609)},
    "Publicaciones Seller Dev":          {"EXPERT":(715,76,853),  "NEWBIE":(1351,285,1809)},
}

# ═══════════════════════════════════════════════════════════════
# SECTION 2E: CANAL DATA  ← skill atualiza (CX_USER_TEAM_CHANNEL)
# ═══════════════════════════════════════════════════════════════
canal_weekly = {
    "Experiencia Impositiva Seller Dev": {
        "S2": {"MULTICANAL C2C":(31,17,49), "MULTICANAL CHAT":(81,15,110)},
        "S1": {"MULTICANAL C2C":(10,17,28), "MULTICANAL CHAT":(47,6,60)},
    },
    "ME Vendedor Seller Dev": {
        "S2": {"MULTICANAL C2C":(212,36,272), "MULTICANAL CHAT":(932,138,1194)},
        "S1": {"MULTICANAL C2C":(182,30,224), "MULTICANAL CHAT":(876,122,1084)},
    },
    "PCF Vendedor Seller Dev": {
        "S2": {"MULTICANAL C2C":(23,9,33),  "MULTICANAL CHAT":(69,18,100)},
        "S1": {"MULTICANAL C2C":(30,18,50),  "MULTICANAL CHAT":(52,12,79)},
    },
    "Partners": {
        "S2": {"MULTICANAL C2C":(61,16,83), "MULTICANAL CHAT":(510,69,637)},
        "S1": {"MULTICANAL C2C":(67,20,102), "MULTICANAL CHAT":(499,65,616)},
    },
    "Post Venta Seller Dev": {
        "S2": {"MULTICANAL C2C":(60,8,70),   "MULTICANAL CHAT":(133,15,162)},
        "S1": {"MULTICANAL C2C":(32,9,43),   "MULTICANAL CHAT":(145,9,166)},
    },
    "Publicaciones Seller Dev": {
        "S2": {"MULTICANAL C2C":(49,29,83),  "MULTICANAL CHAT":(404,51,503)},
        "S1": {"MULTICANAL C2C":(54,33,89),  "MULTICANAL CHAT":(343,43,422)},
    },
}
canal_monthly = {
    "Experiencia Impositiva Seller Dev": {
        "M2": {"MULTICANAL C2C":(55,31,96),    "MULTICANAL CHAT":(232,64,333)},
        "M1": {"MULTICANAL C2C":(91,66,166),   "MULTICANAL CHAT":(313,45,404)},
    },
    "ME Vendedor Seller Dev": {
        "M2": {"MULTICANAL C2C":(734,210,1030), "MULTICANAL CHAT":(3808,472,4694)},
        "M1": {"MULTICANAL C2C":(940,204,1242),"MULTICANAL CHAT":(4468,534,5516)},
    },
    "PCF Vendedor Seller Dev": {
        "M2": {"MULTICANAL C2C":(121,52,194),  "MULTICANAL CHAT":(378,100,537)},
        "M1": {"MULTICANAL C2C":(112,51,172),  "MULTICANAL CHAT":(280,66,393)},
    },
    "Partners": {
        "M2": {"MULTICANAL C2C":(305,89,435),  "MULTICANAL CHAT":(1712,218,2108)},
        "M1": {"MULTICANAL C2C":(277,78,400),  "MULTICANAL CHAT":(1947,281,2440)},
    },
    "Post Venta Seller Dev": {
        "M2": {"MULTICANAL C2C":(150,49,216),  "MULTICANAL CHAT":(703,115,875)},
        "M1": {"MULTICANAL C2C":(199,35,251),  "MULTICANAL CHAT":(657,81,807)},
    },
    "Publicaciones Seller Dev": {
        "M2": {"MULTICANAL C2C":(283,86,405),  "MULTICANAL CHAT":(2115,254,2596)},
        "M1": {"MULTICANAL C2C":(213,130,372), "MULTICANAL CHAT":(1786,242,2224)},
    },
}

# ═══════════════════════════════════════════════════════════════
# SECTION 2F: OFICINA DATA  ← skill atualiza (CX_USER_OFFICE)
# ═══════════════════════════════════════════════════════════════
oficina_weekly = {
    "Experiencia Impositiva Seller Dev": {
        "S2": {"AEC":(81,15,110), "CTX":(17,2,19), "KTA_BRASIL":(14,15,30)},
        "S1": {"AEC":(47,6,60), "CTX":(5,3,8), "KTA_BRASIL":(5,14,20)},
    },
    "ME Vendedor Seller Dev": {
        "S2": {"AEC":(224,20,264),"ATE":(484,58,614),"CTX":(144,18,176),"KTA_BRASIL":(300,78,422),"MELICIDADE":(2,0,2)},
        "S1": {"AEC":(248,16,278),"ATE":(374,64,478),"CTX":(88,18,118),"KTA_BRASIL":(346,54,432),"MELICIDADE":(2,0,2)},
    },
    "PCF Vendedor Seller Dev": {
        "S2": {"AEC":(20,7,30), "ATE":(46,10,65),"CTX":(5,2,8),  "KTA_BRASIL":(13,7,21), "MELICIDADE":(10,2,12)},
        "S1": {"AEC":(14,5,25), "ATE":(33,10,46),"CTX":(5,3,10), "KTA_BRASIL":(28,11,45),"MELICIDADE":(2,1,3)},
    },
    "Partners": {
        "S2": {"AEC":(27,4,32),  "ATE":(317,46,389),"CTX":(75,9,95), "KTA_BRASIL":(156,26,209)},
        "S1": {"AEC":(25,7,37),  "ATE":(286,33,344),"CTX":(42,9,58), "KTA_BRASIL":(213,36,279)},
    },
    "Post Venta Seller Dev": {
        "S2": {"AEC":(67,10,79),  "ATE":(48,5,61), "CTX":(24,2,29), "KTA_BRASIL":(55,6,64)},
        "S1": {"AEC":(72,8,83),  "ATE":(34,3,40), "CTX":(6,2,9),  "KTA_BRASIL":(65,5,77)},
    },
    "Publicaciones Seller Dev": {
        "S2": {"AEC":(294,38,363),"CTX":(23,8,33), "KTA_BRASIL":(134,34,188),"MELICIDADE":(2,0,2)},
        "S1": {"AEC":(245,34,301),"CTX":(23,6,30), "KTA_BRASIL":(129,36,180)},
    },
}
oficina_monthly = {
    "Experiencia Impositiva Seller Dev": {
        "M2": {"AEC":(252,68,359),"CTX":(36,16,57),"KTA_BRASIL":(23,20,48),"MELICIDADE":(1,2,3)},
        "M1": {"AEC":(313,44,403),"CTX":(42,13,56),"KTA_BRASIL":(49,54,111)},
    },
    "ME Vendedor Seller Dev": {
        "M2": {"AEC":(1196,112,1414),"ATE":(2376,380,3012),"CTX":(534,80,684),"KTA_BRASIL":(780,168,1052),"MELICIDADE":(70,12,98)},
        "M1": {"AEC":(1234,86,1404),"ATE":(2184,330,2808),"CTX":(514,78,644),"KTA_BRASIL":(1474,244,1902),"MELICIDADE":(12,2,14)},
    },
    "PCF Vendedor Seller Dev": {
        "M2": {"AEC":(177,40,242),"ATE":(195,67,305),"CTX":(49,20,77),"KTA_BRASIL":(55,22,79),"MELICIDADE":(60,16,86)},
        "M1": {"AEC":(93,35,144),"ATE":(166,37,225),"CTX":(28,13,44),"KTA_BRASIL":(79,28,118),"MELICIDADE":(28,5,37)},
    },
    "Partners": {
        "M2": {"AEC":(137,35,189),"ATE":(1400,193,1741),"CTX":(382,45,465),"KTA_BRASIL":(309,63,409)},
        "M1": {"AEC":(95,26,135),"ATE":(1202,164,1485),"CTX":(244,45,322),"KTA_BRASIL":(687,124,903)},
    },
    "Post Venta Seller Dev": {
        "M2": {"AEC":(337,74,436),"ATE":(308,44,378),"CTX":(106,29,148),"KTA_BRASIL":(154,24,192),"MELICIDADE":(23,6,30)},
        "M1": {"AEC":(326,48,400),"ATE":(183,18,227),"CTX":(73,12,94),"KTA_BRASIL":(270,38,333),"MELICIDADE":(5,0,5)},
    },
    "Publicaciones Seller Dev": {
        "M2": {"AEC":(1406,181,1746),"CTX":(830,118,1023),"KTA_BRASIL":(377,66,500),"MELICIDADE":(25,4,33)},
        "M1": {"AEC":(1282,177,1585),"CTX":(94,29,134),"KTA_BRASIL":(618,166,871),"MELICIDADE":(5,0,5)},
    },
}


# ════════════════════════════════════════════════════════════════
# SECTION 2G: P×CANAL DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_TEAM_CHANNEL)
# ════════════════════════════════════════════════════════════════
p_c_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (5, 0, 6)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (7, 10, 18), 'MULTICANAL CHAT': (24, 4, 31)},
            'Facturación': {'MULTICANAL C2C': (1, 7, 8), 'MULTICANAL CHAT': (18, 2, 23)},
        },
        'S1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 4)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (10, 4, 16), 'MULTICANAL CHAT': (19, 1, 22)},
            'Facturación': {'MULTICANAL C2C': (4, 5, 9), 'MULTICANAL CHAT': (14, 2, 17)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (70, 12, 92), 'MULTICANAL CHAT': (332, 68, 446)},
            'Gestiones Operativas': {'MULTICANAL C2C': (26, 4, 32), 'MULTICANAL CHAT': (68, 12, 90)},
            'Reputación ME': {'MULTICANAL C2C': (64, 8, 72), 'MULTICANAL CHAT': (376, 18, 412)},
            'Reversa': {'MULTICANAL C2C': (12, 4, 16), 'MULTICANAL CHAT': (52, 14, 70)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (48, 10, 66)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (92, 22, 126), 'MULTICANAL CHAT': (446, 50, 548)},
            'Gestiones Operativas': {'MULTICANAL C2C': (16, 0, 16), 'MULTICANAL CHAT': (66, 12, 84)},
            'Reputación ME': {'MULTICANAL C2C': (66, 12, 82), 'MULTICANAL CHAT': (352, 14, 396)},
            'Reversa': {'MULTICANAL C2C': (12, 10, 24), 'MULTICANAL CHAT': (66, 8, 82)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 0, 14), 'MULTICANAL CHAT': (40, 6, 48)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (30, 18, 50), 'MULTICANAL CHAT': (52, 12, 79)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (22, 14, 41), 'MULTICANAL CHAT': (59, 12, 78)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'MULTICANAL C2C': (60, 19, 93), 'MULTICANAL CHAT': (428, 57, 532)},
            'Places Kangu': {'MULTICANAL C2C': (7, 1, 9), 'MULTICANAL CHAT': (71, 8, 84)},
        },
        'S1': {
            'Drivers': {'MULTICANAL C2C': (55, 21, 81), 'MULTICANAL CHAT': (420, 69, 543)},
            'Places Kangu': {'MULTICANAL C2C': (13, 3, 19), 'MULTICANAL CHAT': (59, 6, 73)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'MULTICANAL C2C': (2, 1, 3), 'MULTICANAL CHAT': (4, 1, 5)},
            'Reputación': {'MULTICANAL C2C': (30, 8, 40), 'MULTICANAL CHAT': (141, 8, 161)},
        },
        'S1': {
            'Anulación de Venta': {'MULTICANAL CHAT': (3, 0, 3)},
            'Reputación': {'MULTICANAL C2C': (41, 4, 48), 'MULTICANAL CHAT': (131, 15, 166)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'MULTICANAL C2C': (19, 21, 41), 'MULTICANAL CHAT': (146, 11, 173)},
            'Antes de publicar': {'MULTICANAL C2C': (6, 1, 8), 'MULTICANAL CHAT': (28, 0, 30)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 0, 1), 'MULTICANAL CHAT': (5, 0, 5)},
            'Denuncia de usuario': {'MULTICANAL C2C': (3, 1, 4), 'MULTICANAL CHAT': (5, 2, 8)},
            'Gestión de Publicación': {'MULTICANAL C2C': (14, 3, 17), 'MULTICANAL CHAT': (32, 5, 45)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (21, 8, 32)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (6, 0, 6)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (38, 4, 44)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (5, 2, 7), 'MULTICANAL CHAT': (38, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 9), 'MULTICANAL CHAT': (24, 8, 36)},
        },
        'S1': {
            'Afiliados ML': {'MULTICANAL C2C': (23, 21, 47), 'MULTICANAL CHAT': (166, 14, 199)},
            'Antes de publicar': {'MULTICANAL C2C': (5, 1, 6), 'MULTICANAL CHAT': (21, 2, 26)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 1, 2), 'MULTICANAL CHAT': (12, 2, 15)},
            'Denuncia de usuario': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (4, 2, 6)},
            'Gestión de Publicación': {'MULTICANAL C2C': (5, 3, 9), 'MULTICANAL CHAT': (29, 7, 40)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (22, 5, 31)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (5, 1, 7)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (27, 10, 40)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (4, 2, 7), 'MULTICANAL CHAT': (35, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 11), 'MULTICANAL CHAT': (14, 4, 20)},
        },
    },
}
p_c_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'MULTICANAL C2C': (8, 4, 13), 'MULTICANAL CHAT': (28, 3, 35)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (60, 37, 103), 'MULTICANAL CHAT': (180, 24, 228)},
            'Facturación': {'MULTICANAL C2C': (23, 25, 50), 'MULTICANAL CHAT': (105, 18, 141)},
        },
        'M1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (6, 0, 7)},
            'Facturación': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (1, 1, 2)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (370, 110, 532), 'MULTICANAL CHAT': (1894, 308, 2472)},
            'Gestiones Operativas': {'MULTICANAL C2C': (98, 22, 126), 'MULTICANAL CHAT': (312, 52, 412)},
            'Reputación ME': {'MULTICANAL C2C': (356, 46, 422), 'MULTICANAL CHAT': (1784, 88, 2000)},
            'Reversa': {'MULTICANAL C2C': (70, 18, 92), 'MULTICANAL CHAT': (294, 54, 388)},
            'Suspensiones ME': {'MULTICANAL C2C': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (44, 8, 68), 'MULTICANAL CHAT': (184, 32, 244)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (30, 6, 36), 'MULTICANAL CHAT': (118, 4, 130)},
            'Gestiones Operativas': {'MULTICANAL CHAT': (20, 0, 20)},
            'Reputación ME': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (60, 4, 70)},
            'Reversa': {'MULTICANAL C2C': (0, 4, 4), 'MULTICANAL CHAT': (8, 4, 14)},
            'Viaje del paquete - Vendedor': {'MULTICANAL CHAT': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (112, 51, 172), 'MULTICANAL CHAT': (280, 66, 393)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (1, 1, 4), 'MULTICANAL CHAT': (9, 0, 12)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'MULTICANAL C2C': (222, 65, 328), 'MULTICANAL CHAT': (1592, 236, 2004)},
            'Places Kangu': {'MULTICANAL C2C': (55, 13, 72), 'MULTICANAL CHAT': (355, 45, 436)},
        },
        'M1': {
            'Drivers': {'MULTICANAL C2C': (23, 4, 29), 'MULTICANAL CHAT': (148, 22, 193)},
            'Places Kangu': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (14, 0, 15)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'MULTICANAL C2C': (6, 2, 9), 'MULTICANAL CHAT': (24, 3, 27)},
            'Reputación': {'MULTICANAL C2C': (193, 33, 242), 'MULTICANAL CHAT': (633, 78, 780)},
        },
        'M1': {
            'Reputación': {'MULTICANAL C2C': (3, 1, 5), 'MULTICANAL CHAT': (24, 1, 27)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'MULTICANAL C2C': (87, 79, 182), 'MULTICANAL CHAT': (872, 87, 1045)},
            'Antes de publicar': {'MULTICANAL C2C': (28, 4, 35), 'MULTICANAL CHAT': (134, 9, 159)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (17, 4, 23)},
            'Denuncia de usuario': {'MULTICANAL C2C': (15, 5, 21), 'MULTICANAL CHAT': (38, 7, 49)},
            'Gestión de Publicación': {'MULTICANAL C2C': (34, 17, 53), 'MULTICANAL CHAT': (162, 24, 216)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (7, 4, 11), 'MULTICANAL CHAT': (91, 27, 125)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (11, 6, 18)},
            'PR - Propiedad intelectual': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (160, 29, 201)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (14, 6, 21), 'MULTICANAL CHAT': (189, 22, 233)},
            'Potenciar Ventas': {'MULTICANAL C2C': (23, 12, 41), 'MULTICANAL CHAT': (112, 27, 155)},
        },
        'M1': {
            'Afiliados ML': {'MULTICANAL C2C': (9, 3, 12), 'MULTICANAL CHAT': (77, 5, 89)},
            'Antes de publicar': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (3, 0, 3)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (11, 1, 13)},
            'Denuncia de usuario': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 2)},
            'Gestión de Publicación': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (10, 1, 11)},
            'PR - Artículos prohibidos': {'MULTICANAL CHAT': (8, 1, 12)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (4, 0, 4)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (8, 5, 14)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (7, 2, 10)},
            'Potenciar Ventas': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (3, 2, 5)},
        },
    },
}

# ════════════════════════════════════════════════════════════════
# SECTION 2H: P×OFICINA DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_OFFICE)
# ════════════════════════════════════════════════════════════════
p_o_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'AEC': (5, 0, 6), 'CTX': (1, 0, 1), 'KTA_BRASIL': (1, 0, 1)},
            'Emision de Nota Fiscal': {'AEC': (24, 4, 31), 'CTX': (4, 3, 7), 'KTA_BRASIL': (3, 7, 11)},
            'Facturación': {'AEC': (18, 2, 23), 'KTA_BRASIL': (1, 7, 8)},
        },
        'S1': {
            'Datos fiscales': {'AEC': (2, 0, 4), 'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (19, 1, 22), 'CTX': (2, 1, 3), 'KTA_BRASIL': (8, 3, 13)},
            'Facturación': {'AEC': (14, 2, 17), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 4, 8)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'AEC': (24, 4, 30), 'ATE': (188, 34, 248), 'CTX': (50, 12, 72), 'KTA_BRASIL': (140, 30, 188)},
            'Gestiones Operativas': {'AEC': (14, 0, 16), 'ATE': (48, 8, 64), 'CTX': (8, 2, 10), 'KTA_BRASIL': (24, 6, 32)},
            'Reputación ME': {'AEC': (196, 8, 214), 'ATE': (84, 6, 92), 'CTX': (26, 4, 32), 'KTA_BRASIL': (134, 8, 146)},
            'Reversa': {'AEC': (6, 2, 8), 'ATE': (26, 6, 34), 'KTA_BRASIL': (30, 10, 42), 'MELICIDADE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (8, 2, 10), 'ATE': (28, 10, 40), 'CTX': (4, 0, 4), 'KTA_BRASIL': (18, 0, 24)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'AEC': (26, 8, 38), 'ATE': (288, 34, 352), 'CTX': (54, 6, 62), 'KTA_BRASIL': (168, 24, 220), 'MELICIDADE': (2, 0, 2)},
            'Gestiones Operativas': {'AEC': (2, 0, 2), 'ATE': (54, 0, 56), 'CTX': (10, 4, 16), 'KTA_BRASIL': (16, 8, 26)},
            'Reputación ME': {'AEC': (184, 6, 200), 'ATE': (86, 8, 102), 'CTX': (12, 0, 14), 'KTA_BRASIL': (136, 12, 162)},
            'Reversa': {'AEC': (8, 6, 16), 'ATE': (38, 8, 48), 'KTA_BRASIL': (32, 4, 42)},
            'Viaje del paquete - Vendedor': {'AEC': (2, 0, 4), 'ATE': (22, 4, 28), 'CTX': (4, 0, 4), 'KTA_BRASIL': (22, 2, 26)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (14, 5, 25), 'ATE': (33, 10, 46), 'CTX': (5, 3, 10), 'KTA_BRASIL': (28, 11, 45), 'MELICIDADE': (2, 1, 3)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (30, 10, 43), 'ATE': (21, 6, 31), 'CTX': (5, 4, 9), 'KTA_BRASIL': (22, 6, 33), 'MELICIDADE': (3, 0, 3)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'AEC': (23, 7, 35), 'ATE': (240, 29, 290), 'CTX': (35, 8, 49), 'KTA_BRASIL': (190, 32, 251)},
            'Places Kangu': {'AEC': (2, 0, 2), 'ATE': (46, 4, 54), 'CTX': (7, 1, 9), 'KTA_BRASIL': (23, 4, 28)},
        },
        'S1': {
            'Drivers': {'AEC': (16, 7, 24), 'ATE': (228, 35, 287), 'CTX': (34, 8, 51), 'KTA_BRASIL': (197, 40, 262)},
            'Places Kangu': {'AEC': (4, 1, 6), 'ATE': (35, 3, 42), 'CTX': (5, 4, 11), 'KTA_BRASIL': (28, 1, 33)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'AEC': (1, 1, 2), 'ATE': (1, 0, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Reputación': {'AEC': (71, 7, 81), 'ATE': (33, 3, 39), 'CTX': (6, 2, 9), 'KTA_BRASIL': (61, 4, 72)},
        },
        'S1': {
            'Anulación de Venta': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 0, 1)},
            'Reputación': {'AEC': (70, 9, 85), 'ATE': (29, 4, 41), 'CTX': (8, 0, 8), 'KTA_BRASIL': (65, 6, 80)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'AEC': (146, 11, 173), 'CTX': (6, 3, 9), 'KTA_BRASIL': (13, 18, 32)},
            'Antes de publicar': {'AEC': (15, 1, 17), 'CTX': (4, 0, 5), 'KTA_BRASIL': (15, 0, 16)},
            'Calidad de foto': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'Denuncia de usuario': {'AEC': (5, 2, 8), 'CTX': (3, 0, 3), 'KTA_BRASIL': (0, 1, 1)},
            'Gestión de Publicación': {'AEC': (24, 3, 30), 'CTX': (6, 1, 7), 'KTA_BRASIL': (16, 4, 25)},
            'PR - Artículos prohibidos': {'AEC': (7, 5, 12), 'KTA_BRASIL': (15, 4, 22)},
            'PR - Datos Personales': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'PR - Propiedad intelectual': {'AEC': (22, 0, 22), 'KTA_BRASIL': (16, 4, 22)},
            'PR - Técnica prohibida': {'AEC': (16, 6, 22), 'KTA_BRASIL': (27, 1, 28)},
            'Potenciar Ventas': {'AEC': (8, 6, 15), 'CTX': (4, 2, 6), 'KTA_BRASIL': (17, 4, 24)},
        },
        'S1': {
            'Afiliados ML': {'AEC': (166, 14, 199), 'CTX': (3, 1, 5), 'KTA_BRASIL': (20, 20, 42)},
            'Antes de publicar': {'AEC': (6, 2, 8), 'CTX': (2, 0, 2), 'KTA_BRASIL': (18, 1, 22)},
            'Calidad de foto': {'AEC': (3, 1, 5), 'KTA_BRASIL': (9, 2, 12)},
            'Denuncia de usuario': {'AEC': (4, 2, 6), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Gestión de Publicación': {'AEC': (11, 3, 16), 'CTX': (3, 0, 3), 'KTA_BRASIL': (20, 7, 30)},
            'PR - Artículos prohibidos': {'AEC': (4, 3, 9), 'KTA_BRASIL': (18, 3, 23)},
            'PR - Datos Personales': {'AEC': (0, 1, 1), 'KTA_BRASIL': (5, 0, 6)},
            'PR - Propiedad intelectual': {'AEC': (10, 3, 13), 'KTA_BRASIL': (17, 7, 27)},
            'PR - Técnica prohibida': {'AEC': (21, 3, 24), 'ATE': (0, 0, 1), 'KTA_BRASIL': (18, 4, 25)},
            'Potenciar Ventas': {'AEC': (5, 6, 12), 'CTX': (2, 1, 4), 'KTA_BRASIL': (11, 1, 14), 'MELICIDADE': (1, 0, 1)},
        },
    },
}
p_o_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'AEC': (28, 3, 35), 'CTX': (4, 1, 5), 'KTA_BRASIL': (4, 3, 8)},
            'Emision de Nota Fiscal': {'AEC': (180, 23, 227), 'CTX': (29, 9, 39), 'KTA_BRASIL': (31, 29, 65)},
            'Facturación': {'AEC': (105, 18, 141), 'CTX': (9, 3, 12), 'KTA_BRASIL': (14, 22, 38)},
        },
        'M1': {
            'Datos fiscales': {'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (6, 0, 7), 'KTA_BRASIL': (1, 2, 3)},
            'Facturación': {'AEC': (1, 1, 2), 'KTA_BRASIL': (1, 2, 3)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'AEC': (146, 36, 196), 'ATE': (1214, 212, 1618), 'CTX': (302, 56, 386), 'KTA_BRASIL': (598, 116, 804), 'MELICIDADE': (6, 0, 6)},
            'Gestiones Operativas': {'AEC': (34, 8, 46), 'ATE': (244, 32, 306), 'CTX': (54, 12, 74), 'KTA_BRASIL': (80, 22, 114), 'MELICIDADE': (2, 0, 2)},
            'Reputación ME': {'AEC': (996, 28, 1084), 'ATE': (426, 30, 490), 'CTX': (134, 10, 160), 'KTA_BRASIL': (584, 64, 686), 'MELICIDADE': (2, 2, 4)},
            'Reversa': {'AEC': (34, 10, 46), 'ATE': (178, 30, 222), 'KTA_BRASIL': (152, 32, 212), 'MELICIDADE': (2, 0, 2)},
            'Suspensiones ME': {'ATE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (24, 4, 32), 'ATE': (120, 26, 170), 'CTX': (24, 0, 24), 'KTA_BRASIL': (60, 10, 86)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'AEC': (4, 2, 6), 'ATE': (86, 6, 96), 'KTA_BRASIL': (58, 2, 64)},
            'Gestiones Operativas': {'ATE': (16, 0, 16), 'KTA_BRASIL': (4, 0, 4)},
            'Reputación ME': {'AEC': (18, 2, 24), 'ATE': (26, 0, 26), 'KTA_BRASIL': (26, 4, 32)},
            'Reversa': {'ATE': (2, 6, 8), 'KTA_BRASIL': (6, 2, 10)},
            'Viaje del paquete - Vendedor': {'ATE': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (93, 35, 144), 'ATE': (166, 37, 225), 'CTX': (28, 13, 44), 'KTA_BRASIL': (79, 28, 118), 'MELICIDADE': (28, 5, 37)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (4, 0, 5), 'ATE': (2, 1, 4), 'KTA_BRASIL': (4, 0, 7)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'AEC': (74, 23, 110), 'ATE': (987, 137, 1223), 'CTX': (180, 36, 241), 'KTA_BRASIL': (577, 105, 763)},
            'Places Kangu': {'AEC': (21, 3, 25), 'ATE': (215, 27, 262), 'CTX': (64, 9, 81), 'KTA_BRASIL': (110, 19, 140)},
        },
        'M1': {
            'Drivers': {'AEC': (8, 1, 10), 'ATE': (93, 8, 112), 'KTA_BRASIL': (70, 17, 100)},
            'Places Kangu': {'ATE': (7, 0, 8), 'KTA_BRASIL': (7, 0, 8)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'AEC': (16, 2, 18), 'ATE': (6, 1, 7), 'CTX': (3, 0, 4), 'KTA_BRASIL': (5, 2, 7)},
            'Reputación': {'AEC': (310, 46, 382), 'ATE': (177, 17, 220), 'CTX': (70, 12, 90), 'KTA_BRASIL': (265, 36, 326), 'MELICIDADE': (5, 0, 5)},
        },
        'M1': {
            'Reputación': {'AEC': (8, 1, 9), 'ATE': (8, 1, 10), 'KTA_BRASIL': (11, 0, 13)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'AEC': (871, 87, 1044), 'CTX': (30, 11, 44), 'KTA_BRASIL': (57, 68, 138), 'MELICIDADE': (1, 0, 1)},
            'Antes de publicar': {'AEC': (70, 5, 84), 'CTX': (17, 2, 21), 'KTA_BRASIL': (75, 6, 89)},
            'Calidad de foto': {'AEC': (3, 2, 7), 'KTA_BRASIL': (15, 3, 18)},
            'Denuncia de usuario': {'AEC': (38, 7, 49), 'CTX': (7, 2, 10), 'KTA_BRASIL': (8, 3, 11)},
            'Gestión de Publicación': {'AEC': (62, 18, 88), 'CTX': (23, 8, 31), 'KTA_BRASIL': (111, 15, 150)},
            'PR - Artículos prohibidos': {'AEC': (31, 15, 48), 'CTX': (1, 0, 1), 'KTA_BRASIL': (66, 16, 87)},
            'PR - Datos Personales': {'AEC': (3, 1, 4), 'KTA_BRASIL': (8, 5, 14)},
            'PR - Propiedad intelectual': {'AEC': (65, 10, 79), 'KTA_BRASIL': (99, 21, 128)},
            'PR - Técnica prohibida': {'AEC': (95, 15, 116), 'ATE': (0, 0, 1), 'KTA_BRASIL': (105, 13, 134), 'MELICIDADE': (3, 0, 3)},
            'Potenciar Ventas': {'AEC': (44, 17, 66), 'CTX': (16, 6, 27), 'KTA_BRASIL': (74, 16, 102), 'MELICIDADE': (1, 0, 1)},
        },
        'M1': {
            'Afiliados ML': {'AEC': (77, 5, 89), 'KTA_BRASIL': (9, 3, 12)},
            'Antes de publicar': {'AEC': (0, 1, 1), 'KTA_BRASIL': (3, 0, 3)},
            'Calidad de foto': {'AEC': (3, 0, 4), 'KTA_BRASIL': (8, 1, 10)},
            'Denuncia de usuario': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 1, 2)},
            'Gestión de Publicación': {'AEC': (6, 1, 7), 'KTA_BRASIL': (4, 1, 5)},
            'PR - Artículos prohibidos': {'AEC': (1, 0, 2), 'KTA_BRASIL': (7, 1, 10)},
            'PR - Datos Personales': {'KTA_BRASIL': (4, 0, 4)},
            'PR - Propiedad intelectual': {'AEC': (3, 1, 4), 'KTA_BRASIL': (5, 4, 10)},
            'PR - Técnica prohibida': {'AEC': (5, 0, 5), 'KTA_BRASIL': (4, 2, 7)},
            'Potenciar Ventas': {'AEC': (2, 3, 5), 'KTA_BRASIL': (2, 1, 3)},
        },
    },
}


# ════════════════════════════════════════════════════════════════
# SECTION 2G: P×CANAL DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_TEAM_CHANNEL)
# ════════════════════════════════════════════════════════════════
p_c_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (5, 0, 6)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (7, 10, 18), 'MULTICANAL CHAT': (24, 4, 31)},
            'Facturación': {'MULTICANAL C2C': (1, 7, 8), 'MULTICANAL CHAT': (18, 2, 23)},
        },
        'S1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 4)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (10, 4, 16), 'MULTICANAL CHAT': (19, 1, 22)},
            'Facturación': {'MULTICANAL C2C': (4, 5, 9), 'MULTICANAL CHAT': (14, 2, 17)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (70, 12, 92), 'MULTICANAL CHAT': (332, 68, 446)},
            'Gestiones Operativas': {'MULTICANAL C2C': (26, 4, 32), 'MULTICANAL CHAT': (68, 12, 90)},
            'Reputación ME': {'MULTICANAL C2C': (64, 8, 72), 'MULTICANAL CHAT': (376, 18, 412)},
            'Reversa': {'MULTICANAL C2C': (12, 4, 16), 'MULTICANAL CHAT': (52, 14, 70)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (48, 10, 66)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (92, 22, 126), 'MULTICANAL CHAT': (446, 50, 548)},
            'Gestiones Operativas': {'MULTICANAL C2C': (16, 0, 16), 'MULTICANAL CHAT': (66, 12, 84)},
            'Reputación ME': {'MULTICANAL C2C': (66, 12, 82), 'MULTICANAL CHAT': (352, 14, 396)},
            'Reversa': {'MULTICANAL C2C': (12, 10, 24), 'MULTICANAL CHAT': (66, 8, 82)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 0, 14), 'MULTICANAL CHAT': (40, 6, 48)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (30, 18, 50), 'MULTICANAL CHAT': (52, 12, 79)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (22, 14, 41), 'MULTICANAL CHAT': (59, 12, 78)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'MULTICANAL C2C': (60, 19, 93), 'MULTICANAL CHAT': (428, 57, 532)},
            'Places Kangu': {'MULTICANAL C2C': (7, 1, 9), 'MULTICANAL CHAT': (71, 8, 84)},
        },
        'S1': {
            'Drivers': {'MULTICANAL C2C': (55, 21, 81), 'MULTICANAL CHAT': (420, 69, 543)},
            'Places Kangu': {'MULTICANAL C2C': (13, 3, 19), 'MULTICANAL CHAT': (59, 6, 73)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'MULTICANAL C2C': (2, 1, 3), 'MULTICANAL CHAT': (4, 1, 5)},
            'Reputación': {'MULTICANAL C2C': (30, 8, 40), 'MULTICANAL CHAT': (141, 8, 161)},
        },
        'S1': {
            'Anulación de Venta': {'MULTICANAL CHAT': (3, 0, 3)},
            'Reputación': {'MULTICANAL C2C': (41, 4, 48), 'MULTICANAL CHAT': (131, 15, 166)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'MULTICANAL C2C': (19, 21, 41), 'MULTICANAL CHAT': (146, 11, 173)},
            'Antes de publicar': {'MULTICANAL C2C': (6, 1, 8), 'MULTICANAL CHAT': (28, 0, 30)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 0, 1), 'MULTICANAL CHAT': (5, 0, 5)},
            'Denuncia de usuario': {'MULTICANAL C2C': (3, 1, 4), 'MULTICANAL CHAT': (5, 2, 8)},
            'Gestión de Publicación': {'MULTICANAL C2C': (14, 3, 17), 'MULTICANAL CHAT': (32, 5, 45)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (21, 8, 32)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (6, 0, 6)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (38, 4, 44)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (5, 2, 7), 'MULTICANAL CHAT': (38, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 9), 'MULTICANAL CHAT': (24, 8, 36)},
        },
        'S1': {
            'Afiliados ML': {'MULTICANAL C2C': (23, 21, 47), 'MULTICANAL CHAT': (166, 14, 199)},
            'Antes de publicar': {'MULTICANAL C2C': (5, 1, 6), 'MULTICANAL CHAT': (21, 2, 26)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 1, 2), 'MULTICANAL CHAT': (12, 2, 15)},
            'Denuncia de usuario': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (4, 2, 6)},
            'Gestión de Publicación': {'MULTICANAL C2C': (5, 3, 9), 'MULTICANAL CHAT': (29, 7, 40)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (22, 5, 31)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (5, 1, 7)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (27, 10, 40)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (4, 2, 7), 'MULTICANAL CHAT': (35, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 11), 'MULTICANAL CHAT': (14, 4, 20)},
        },
    },
}
p_c_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'MULTICANAL C2C': (8, 4, 13), 'MULTICANAL CHAT': (28, 3, 35)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (60, 37, 103), 'MULTICANAL CHAT': (180, 24, 228)},
            'Facturación': {'MULTICANAL C2C': (23, 25, 50), 'MULTICANAL CHAT': (105, 18, 141)},
        },
        'M1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (6, 0, 7)},
            'Facturación': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (1, 1, 2)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (370, 110, 532), 'MULTICANAL CHAT': (1894, 308, 2472)},
            'Gestiones Operativas': {'MULTICANAL C2C': (98, 22, 126), 'MULTICANAL CHAT': (312, 52, 412)},
            'Reputación ME': {'MULTICANAL C2C': (356, 46, 422), 'MULTICANAL CHAT': (1784, 88, 2000)},
            'Reversa': {'MULTICANAL C2C': (70, 18, 92), 'MULTICANAL CHAT': (294, 54, 388)},
            'Suspensiones ME': {'MULTICANAL C2C': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (44, 8, 68), 'MULTICANAL CHAT': (184, 32, 244)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (30, 6, 36), 'MULTICANAL CHAT': (118, 4, 130)},
            'Gestiones Operativas': {'MULTICANAL CHAT': (20, 0, 20)},
            'Reputación ME': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (60, 4, 70)},
            'Reversa': {'MULTICANAL C2C': (0, 4, 4), 'MULTICANAL CHAT': (8, 4, 14)},
            'Viaje del paquete - Vendedor': {'MULTICANAL CHAT': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (112, 51, 172), 'MULTICANAL CHAT': (280, 66, 393)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (1, 1, 4), 'MULTICANAL CHAT': (9, 0, 12)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'MULTICANAL C2C': (222, 65, 328), 'MULTICANAL CHAT': (1592, 236, 2004)},
            'Places Kangu': {'MULTICANAL C2C': (55, 13, 72), 'MULTICANAL CHAT': (355, 45, 436)},
        },
        'M1': {
            'Drivers': {'MULTICANAL C2C': (23, 4, 29), 'MULTICANAL CHAT': (148, 22, 193)},
            'Places Kangu': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (14, 0, 15)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'MULTICANAL C2C': (6, 2, 9), 'MULTICANAL CHAT': (24, 3, 27)},
            'Reputación': {'MULTICANAL C2C': (193, 33, 242), 'MULTICANAL CHAT': (633, 78, 780)},
        },
        'M1': {
            'Reputación': {'MULTICANAL C2C': (3, 1, 5), 'MULTICANAL CHAT': (24, 1, 27)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'MULTICANAL C2C': (87, 79, 182), 'MULTICANAL CHAT': (872, 87, 1045)},
            'Antes de publicar': {'MULTICANAL C2C': (28, 4, 35), 'MULTICANAL CHAT': (134, 9, 159)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (17, 4, 23)},
            'Denuncia de usuario': {'MULTICANAL C2C': (15, 5, 21), 'MULTICANAL CHAT': (38, 7, 49)},
            'Gestión de Publicación': {'MULTICANAL C2C': (34, 17, 53), 'MULTICANAL CHAT': (162, 24, 216)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (7, 4, 11), 'MULTICANAL CHAT': (91, 27, 125)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (11, 6, 18)},
            'PR - Propiedad intelectual': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (160, 29, 201)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (14, 6, 21), 'MULTICANAL CHAT': (189, 22, 233)},
            'Potenciar Ventas': {'MULTICANAL C2C': (23, 12, 41), 'MULTICANAL CHAT': (112, 27, 155)},
        },
        'M1': {
            'Afiliados ML': {'MULTICANAL C2C': (9, 3, 12), 'MULTICANAL CHAT': (77, 5, 89)},
            'Antes de publicar': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (3, 0, 3)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (11, 1, 13)},
            'Denuncia de usuario': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 2)},
            'Gestión de Publicación': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (10, 1, 11)},
            'PR - Artículos prohibidos': {'MULTICANAL CHAT': (8, 1, 12)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (4, 0, 4)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (8, 5, 14)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (7, 2, 10)},
            'Potenciar Ventas': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (3, 2, 5)},
        },
    },
}

# ════════════════════════════════════════════════════════════════
# SECTION 2H: P×OFICINA DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_OFFICE)
# ════════════════════════════════════════════════════════════════
p_o_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'AEC': (5, 0, 6), 'CTX': (1, 0, 1), 'KTA_BRASIL': (1, 0, 1)},
            'Emision de Nota Fiscal': {'AEC': (24, 4, 31), 'CTX': (4, 3, 7), 'KTA_BRASIL': (3, 7, 11)},
            'Facturación': {'AEC': (18, 2, 23), 'KTA_BRASIL': (1, 7, 8)},
        },
        'S1': {
            'Datos fiscales': {'AEC': (2, 0, 4), 'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (19, 1, 22), 'CTX': (2, 1, 3), 'KTA_BRASIL': (8, 3, 13)},
            'Facturación': {'AEC': (14, 2, 17), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 4, 8)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'AEC': (24, 4, 30), 'ATE': (188, 34, 248), 'CTX': (50, 12, 72), 'KTA_BRASIL': (140, 30, 188)},
            'Gestiones Operativas': {'AEC': (14, 0, 16), 'ATE': (48, 8, 64), 'CTX': (8, 2, 10), 'KTA_BRASIL': (24, 6, 32)},
            'Reputación ME': {'AEC': (196, 8, 214), 'ATE': (84, 6, 92), 'CTX': (26, 4, 32), 'KTA_BRASIL': (134, 8, 146)},
            'Reversa': {'AEC': (6, 2, 8), 'ATE': (26, 6, 34), 'KTA_BRASIL': (30, 10, 42), 'MELICIDADE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (8, 2, 10), 'ATE': (28, 10, 40), 'CTX': (4, 0, 4), 'KTA_BRASIL': (18, 0, 24)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'AEC': (26, 8, 38), 'ATE': (288, 34, 352), 'CTX': (54, 6, 62), 'KTA_BRASIL': (168, 24, 220), 'MELICIDADE': (2, 0, 2)},
            'Gestiones Operativas': {'AEC': (2, 0, 2), 'ATE': (54, 0, 56), 'CTX': (10, 4, 16), 'KTA_BRASIL': (16, 8, 26)},
            'Reputación ME': {'AEC': (184, 6, 200), 'ATE': (86, 8, 102), 'CTX': (12, 0, 14), 'KTA_BRASIL': (136, 12, 162)},
            'Reversa': {'AEC': (8, 6, 16), 'ATE': (38, 8, 48), 'KTA_BRASIL': (32, 4, 42)},
            'Viaje del paquete - Vendedor': {'AEC': (2, 0, 4), 'ATE': (22, 4, 28), 'CTX': (4, 0, 4), 'KTA_BRASIL': (22, 2, 26)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (14, 5, 25), 'ATE': (33, 10, 46), 'CTX': (5, 3, 10), 'KTA_BRASIL': (28, 11, 45), 'MELICIDADE': (2, 1, 3)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (30, 10, 43), 'ATE': (21, 6, 31), 'CTX': (5, 4, 9), 'KTA_BRASIL': (22, 6, 33), 'MELICIDADE': (3, 0, 3)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'AEC': (23, 7, 35), 'ATE': (240, 29, 290), 'CTX': (35, 8, 49), 'KTA_BRASIL': (190, 32, 251)},
            'Places Kangu': {'AEC': (2, 0, 2), 'ATE': (46, 4, 54), 'CTX': (7, 1, 9), 'KTA_BRASIL': (23, 4, 28)},
        },
        'S1': {
            'Drivers': {'AEC': (16, 7, 24), 'ATE': (228, 35, 287), 'CTX': (34, 8, 51), 'KTA_BRASIL': (197, 40, 262)},
            'Places Kangu': {'AEC': (4, 1, 6), 'ATE': (35, 3, 42), 'CTX': (5, 4, 11), 'KTA_BRASIL': (28, 1, 33)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'AEC': (1, 1, 2), 'ATE': (1, 0, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Reputación': {'AEC': (71, 7, 81), 'ATE': (33, 3, 39), 'CTX': (6, 2, 9), 'KTA_BRASIL': (61, 4, 72)},
        },
        'S1': {
            'Anulación de Venta': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 0, 1)},
            'Reputación': {'AEC': (70, 9, 85), 'ATE': (29, 4, 41), 'CTX': (8, 0, 8), 'KTA_BRASIL': (65, 6, 80)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'AEC': (146, 11, 173), 'CTX': (6, 3, 9), 'KTA_BRASIL': (13, 18, 32)},
            'Antes de publicar': {'AEC': (15, 1, 17), 'CTX': (4, 0, 5), 'KTA_BRASIL': (15, 0, 16)},
            'Calidad de foto': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'Denuncia de usuario': {'AEC': (5, 2, 8), 'CTX': (3, 0, 3), 'KTA_BRASIL': (0, 1, 1)},
            'Gestión de Publicación': {'AEC': (24, 3, 30), 'CTX': (6, 1, 7), 'KTA_BRASIL': (16, 4, 25)},
            'PR - Artículos prohibidos': {'AEC': (7, 5, 12), 'KTA_BRASIL': (15, 4, 22)},
            'PR - Datos Personales': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'PR - Propiedad intelectual': {'AEC': (22, 0, 22), 'KTA_BRASIL': (16, 4, 22)},
            'PR - Técnica prohibida': {'AEC': (16, 6, 22), 'KTA_BRASIL': (27, 1, 28)},
            'Potenciar Ventas': {'AEC': (8, 6, 15), 'CTX': (4, 2, 6), 'KTA_BRASIL': (17, 4, 24)},
        },
        'S1': {
            'Afiliados ML': {'AEC': (166, 14, 199), 'CTX': (3, 1, 5), 'KTA_BRASIL': (20, 20, 42)},
            'Antes de publicar': {'AEC': (6, 2, 8), 'CTX': (2, 0, 2), 'KTA_BRASIL': (18, 1, 22)},
            'Calidad de foto': {'AEC': (3, 1, 5), 'KTA_BRASIL': (9, 2, 12)},
            'Denuncia de usuario': {'AEC': (4, 2, 6), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Gestión de Publicación': {'AEC': (11, 3, 16), 'CTX': (3, 0, 3), 'KTA_BRASIL': (20, 7, 30)},
            'PR - Artículos prohibidos': {'AEC': (4, 3, 9), 'KTA_BRASIL': (18, 3, 23)},
            'PR - Datos Personales': {'AEC': (0, 1, 1), 'KTA_BRASIL': (5, 0, 6)},
            'PR - Propiedad intelectual': {'AEC': (10, 3, 13), 'KTA_BRASIL': (17, 7, 27)},
            'PR - Técnica prohibida': {'AEC': (21, 3, 24), 'ATE': (0, 0, 1), 'KTA_BRASIL': (18, 4, 25)},
            'Potenciar Ventas': {'AEC': (5, 6, 12), 'CTX': (2, 1, 4), 'KTA_BRASIL': (11, 1, 14), 'MELICIDADE': (1, 0, 1)},
        },
    },
}
p_o_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'AEC': (28, 3, 35), 'CTX': (4, 1, 5), 'KTA_BRASIL': (4, 3, 8)},
            'Emision de Nota Fiscal': {'AEC': (180, 23, 227), 'CTX': (29, 9, 39), 'KTA_BRASIL': (31, 29, 65)},
            'Facturación': {'AEC': (105, 18, 141), 'CTX': (9, 3, 12), 'KTA_BRASIL': (14, 22, 38)},
        },
        'M1': {
            'Datos fiscales': {'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (6, 0, 7), 'KTA_BRASIL': (1, 2, 3)},
            'Facturación': {'AEC': (1, 1, 2), 'KTA_BRASIL': (1, 2, 3)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'AEC': (146, 36, 196), 'ATE': (1214, 212, 1618), 'CTX': (302, 56, 386), 'KTA_BRASIL': (598, 116, 804), 'MELICIDADE': (6, 0, 6)},
            'Gestiones Operativas': {'AEC': (34, 8, 46), 'ATE': (244, 32, 306), 'CTX': (54, 12, 74), 'KTA_BRASIL': (80, 22, 114), 'MELICIDADE': (2, 0, 2)},
            'Reputación ME': {'AEC': (996, 28, 1084), 'ATE': (426, 30, 490), 'CTX': (134, 10, 160), 'KTA_BRASIL': (584, 64, 686), 'MELICIDADE': (2, 2, 4)},
            'Reversa': {'AEC': (34, 10, 46), 'ATE': (178, 30, 222), 'KTA_BRASIL': (152, 32, 212), 'MELICIDADE': (2, 0, 2)},
            'Suspensiones ME': {'ATE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (24, 4, 32), 'ATE': (120, 26, 170), 'CTX': (24, 0, 24), 'KTA_BRASIL': (60, 10, 86)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'AEC': (4, 2, 6), 'ATE': (86, 6, 96), 'KTA_BRASIL': (58, 2, 64)},
            'Gestiones Operativas': {'ATE': (16, 0, 16), 'KTA_BRASIL': (4, 0, 4)},
            'Reputación ME': {'AEC': (18, 2, 24), 'ATE': (26, 0, 26), 'KTA_BRASIL': (26, 4, 32)},
            'Reversa': {'ATE': (2, 6, 8), 'KTA_BRASIL': (6, 2, 10)},
            'Viaje del paquete - Vendedor': {'ATE': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (93, 35, 144), 'ATE': (166, 37, 225), 'CTX': (28, 13, 44), 'KTA_BRASIL': (79, 28, 118), 'MELICIDADE': (28, 5, 37)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (4, 0, 5), 'ATE': (2, 1, 4), 'KTA_BRASIL': (4, 0, 7)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'AEC': (74, 23, 110), 'ATE': (987, 137, 1223), 'CTX': (180, 36, 241), 'KTA_BRASIL': (577, 105, 763)},
            'Places Kangu': {'AEC': (21, 3, 25), 'ATE': (215, 27, 262), 'CTX': (64, 9, 81), 'KTA_BRASIL': (110, 19, 140)},
        },
        'M1': {
            'Drivers': {'AEC': (8, 1, 10), 'ATE': (93, 8, 112), 'KTA_BRASIL': (70, 17, 100)},
            'Places Kangu': {'ATE': (7, 0, 8), 'KTA_BRASIL': (7, 0, 8)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'AEC': (16, 2, 18), 'ATE': (6, 1, 7), 'CTX': (3, 0, 4), 'KTA_BRASIL': (5, 2, 7)},
            'Reputación': {'AEC': (310, 46, 382), 'ATE': (177, 17, 220), 'CTX': (70, 12, 90), 'KTA_BRASIL': (265, 36, 326), 'MELICIDADE': (5, 0, 5)},
        },
        'M1': {
            'Reputación': {'AEC': (8, 1, 9), 'ATE': (8, 1, 10), 'KTA_BRASIL': (11, 0, 13)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'AEC': (871, 87, 1044), 'CTX': (30, 11, 44), 'KTA_BRASIL': (57, 68, 138), 'MELICIDADE': (1, 0, 1)},
            'Antes de publicar': {'AEC': (70, 5, 84), 'CTX': (17, 2, 21), 'KTA_BRASIL': (75, 6, 89)},
            'Calidad de foto': {'AEC': (3, 2, 7), 'KTA_BRASIL': (15, 3, 18)},
            'Denuncia de usuario': {'AEC': (38, 7, 49), 'CTX': (7, 2, 10), 'KTA_BRASIL': (8, 3, 11)},
            'Gestión de Publicación': {'AEC': (62, 18, 88), 'CTX': (23, 8, 31), 'KTA_BRASIL': (111, 15, 150)},
            'PR - Artículos prohibidos': {'AEC': (31, 15, 48), 'CTX': (1, 0, 1), 'KTA_BRASIL': (66, 16, 87)},
            'PR - Datos Personales': {'AEC': (3, 1, 4), 'KTA_BRASIL': (8, 5, 14)},
            'PR - Propiedad intelectual': {'AEC': (65, 10, 79), 'KTA_BRASIL': (99, 21, 128)},
            'PR - Técnica prohibida': {'AEC': (95, 15, 116), 'ATE': (0, 0, 1), 'KTA_BRASIL': (105, 13, 134), 'MELICIDADE': (3, 0, 3)},
            'Potenciar Ventas': {'AEC': (44, 17, 66), 'CTX': (16, 6, 27), 'KTA_BRASIL': (74, 16, 102), 'MELICIDADE': (1, 0, 1)},
        },
        'M1': {
            'Afiliados ML': {'AEC': (77, 5, 89), 'KTA_BRASIL': (9, 3, 12)},
            'Antes de publicar': {'AEC': (0, 1, 1), 'KTA_BRASIL': (3, 0, 3)},
            'Calidad de foto': {'AEC': (3, 0, 4), 'KTA_BRASIL': (8, 1, 10)},
            'Denuncia de usuario': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 1, 2)},
            'Gestión de Publicación': {'AEC': (6, 1, 7), 'KTA_BRASIL': (4, 1, 5)},
            'PR - Artículos prohibidos': {'AEC': (1, 0, 2), 'KTA_BRASIL': (7, 1, 10)},
            'PR - Datos Personales': {'KTA_BRASIL': (4, 0, 4)},
            'PR - Propiedad intelectual': {'AEC': (3, 1, 4), 'KTA_BRASIL': (5, 4, 10)},
            'PR - Técnica prohibida': {'AEC': (5, 0, 5), 'KTA_BRASIL': (4, 2, 7)},
            'Potenciar Ventas': {'AEC': (2, 3, 5), 'KTA_BRASIL': (2, 1, 3)},
        },
    },
}


# ════════════════════════════════════════════════════════════════
# SECTION 2G: P×CANAL DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_TEAM_CHANNEL)
# ════════════════════════════════════════════════════════════════
p_c_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (5, 0, 6)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (7, 10, 18), 'MULTICANAL CHAT': (24, 4, 31)},
            'Facturación': {'MULTICANAL C2C': (1, 7, 8), 'MULTICANAL CHAT': (18, 2, 23)},
        },
        'S1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 4)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (10, 4, 16), 'MULTICANAL CHAT': (19, 1, 22)},
            'Facturación': {'MULTICANAL C2C': (4, 5, 9), 'MULTICANAL CHAT': (14, 2, 17)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (70, 12, 92), 'MULTICANAL CHAT': (332, 68, 446)},
            'Gestiones Operativas': {'MULTICANAL C2C': (26, 4, 32), 'MULTICANAL CHAT': (68, 12, 90)},
            'Reputación ME': {'MULTICANAL C2C': (64, 8, 72), 'MULTICANAL CHAT': (376, 18, 412)},
            'Reversa': {'MULTICANAL C2C': (12, 4, 16), 'MULTICANAL CHAT': (52, 14, 70)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (48, 10, 66)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (92, 22, 126), 'MULTICANAL CHAT': (446, 50, 548)},
            'Gestiones Operativas': {'MULTICANAL C2C': (16, 0, 16), 'MULTICANAL CHAT': (66, 12, 84)},
            'Reputación ME': {'MULTICANAL C2C': (66, 12, 82), 'MULTICANAL CHAT': (352, 14, 396)},
            'Reversa': {'MULTICANAL C2C': (12, 10, 24), 'MULTICANAL CHAT': (66, 8, 82)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 0, 14), 'MULTICANAL CHAT': (40, 6, 48)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (30, 18, 50), 'MULTICANAL CHAT': (52, 12, 79)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (22, 14, 41), 'MULTICANAL CHAT': (59, 12, 78)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'MULTICANAL C2C': (60, 19, 93), 'MULTICANAL CHAT': (428, 57, 532)},
            'Places Kangu': {'MULTICANAL C2C': (7, 1, 9), 'MULTICANAL CHAT': (71, 8, 84)},
        },
        'S1': {
            'Drivers': {'MULTICANAL C2C': (55, 21, 81), 'MULTICANAL CHAT': (420, 69, 543)},
            'Places Kangu': {'MULTICANAL C2C': (13, 3, 19), 'MULTICANAL CHAT': (59, 6, 73)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'MULTICANAL C2C': (2, 1, 3), 'MULTICANAL CHAT': (4, 1, 5)},
            'Reputación': {'MULTICANAL C2C': (30, 8, 40), 'MULTICANAL CHAT': (141, 8, 161)},
        },
        'S1': {
            'Anulación de Venta': {'MULTICANAL CHAT': (3, 0, 3)},
            'Reputación': {'MULTICANAL C2C': (41, 4, 48), 'MULTICANAL CHAT': (131, 15, 166)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'MULTICANAL C2C': (19, 21, 41), 'MULTICANAL CHAT': (146, 11, 173)},
            'Antes de publicar': {'MULTICANAL C2C': (6, 1, 8), 'MULTICANAL CHAT': (28, 0, 30)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 0, 1), 'MULTICANAL CHAT': (5, 0, 5)},
            'Denuncia de usuario': {'MULTICANAL C2C': (3, 1, 4), 'MULTICANAL CHAT': (5, 2, 8)},
            'Gestión de Publicación': {'MULTICANAL C2C': (14, 3, 17), 'MULTICANAL CHAT': (32, 5, 45)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (21, 8, 32)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (6, 0, 6)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (38, 4, 44)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (5, 2, 7), 'MULTICANAL CHAT': (38, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 9), 'MULTICANAL CHAT': (24, 8, 36)},
        },
        'S1': {
            'Afiliados ML': {'MULTICANAL C2C': (23, 21, 47), 'MULTICANAL CHAT': (166, 14, 199)},
            'Antes de publicar': {'MULTICANAL C2C': (5, 1, 6), 'MULTICANAL CHAT': (21, 2, 26)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 1, 2), 'MULTICANAL CHAT': (12, 2, 15)},
            'Denuncia de usuario': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (4, 2, 6)},
            'Gestión de Publicación': {'MULTICANAL C2C': (5, 3, 9), 'MULTICANAL CHAT': (29, 7, 40)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (22, 5, 31)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (5, 1, 7)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (27, 10, 40)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (4, 2, 7), 'MULTICANAL CHAT': (35, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 11), 'MULTICANAL CHAT': (14, 4, 20)},
        },
    },
}
p_c_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'MULTICANAL C2C': (8, 4, 13), 'MULTICANAL CHAT': (28, 3, 35)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (60, 37, 103), 'MULTICANAL CHAT': (180, 24, 228)},
            'Facturación': {'MULTICANAL C2C': (23, 25, 50), 'MULTICANAL CHAT': (105, 18, 141)},
        },
        'M1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (6, 0, 7)},
            'Facturación': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (1, 1, 2)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (370, 110, 532), 'MULTICANAL CHAT': (1894, 308, 2472)},
            'Gestiones Operativas': {'MULTICANAL C2C': (98, 22, 126), 'MULTICANAL CHAT': (312, 52, 412)},
            'Reputación ME': {'MULTICANAL C2C': (356, 46, 422), 'MULTICANAL CHAT': (1784, 88, 2000)},
            'Reversa': {'MULTICANAL C2C': (70, 18, 92), 'MULTICANAL CHAT': (294, 54, 388)},
            'Suspensiones ME': {'MULTICANAL C2C': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (44, 8, 68), 'MULTICANAL CHAT': (184, 32, 244)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (30, 6, 36), 'MULTICANAL CHAT': (118, 4, 130)},
            'Gestiones Operativas': {'MULTICANAL CHAT': (20, 0, 20)},
            'Reputación ME': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (60, 4, 70)},
            'Reversa': {'MULTICANAL C2C': (0, 4, 4), 'MULTICANAL CHAT': (8, 4, 14)},
            'Viaje del paquete - Vendedor': {'MULTICANAL CHAT': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (112, 51, 172), 'MULTICANAL CHAT': (280, 66, 393)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (1, 1, 4), 'MULTICANAL CHAT': (9, 0, 12)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'MULTICANAL C2C': (222, 65, 328), 'MULTICANAL CHAT': (1592, 236, 2004)},
            'Places Kangu': {'MULTICANAL C2C': (55, 13, 72), 'MULTICANAL CHAT': (355, 45, 436)},
        },
        'M1': {
            'Drivers': {'MULTICANAL C2C': (23, 4, 29), 'MULTICANAL CHAT': (148, 22, 193)},
            'Places Kangu': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (14, 0, 15)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'MULTICANAL C2C': (6, 2, 9), 'MULTICANAL CHAT': (24, 3, 27)},
            'Reputación': {'MULTICANAL C2C': (193, 33, 242), 'MULTICANAL CHAT': (633, 78, 780)},
        },
        'M1': {
            'Reputación': {'MULTICANAL C2C': (3, 1, 5), 'MULTICANAL CHAT': (24, 1, 27)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'MULTICANAL C2C': (87, 79, 182), 'MULTICANAL CHAT': (872, 87, 1045)},
            'Antes de publicar': {'MULTICANAL C2C': (28, 4, 35), 'MULTICANAL CHAT': (134, 9, 159)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (17, 4, 23)},
            'Denuncia de usuario': {'MULTICANAL C2C': (15, 5, 21), 'MULTICANAL CHAT': (38, 7, 49)},
            'Gestión de Publicación': {'MULTICANAL C2C': (34, 17, 53), 'MULTICANAL CHAT': (162, 24, 216)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (7, 4, 11), 'MULTICANAL CHAT': (91, 27, 125)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (11, 6, 18)},
            'PR - Propiedad intelectual': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (160, 29, 201)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (14, 6, 21), 'MULTICANAL CHAT': (189, 22, 233)},
            'Potenciar Ventas': {'MULTICANAL C2C': (23, 12, 41), 'MULTICANAL CHAT': (112, 27, 155)},
        },
        'M1': {
            'Afiliados ML': {'MULTICANAL C2C': (9, 3, 12), 'MULTICANAL CHAT': (77, 5, 89)},
            'Antes de publicar': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (3, 0, 3)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (11, 1, 13)},
            'Denuncia de usuario': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 2)},
            'Gestión de Publicación': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (10, 1, 11)},
            'PR - Artículos prohibidos': {'MULTICANAL CHAT': (8, 1, 12)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (4, 0, 4)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (8, 5, 14)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (7, 2, 10)},
            'Potenciar Ventas': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (3, 2, 5)},
        },
    },
}

# ════════════════════════════════════════════════════════════════
# SECTION 2H: P×OFICINA DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_OFFICE)
# ════════════════════════════════════════════════════════════════
p_o_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'AEC': (5, 0, 6), 'CTX': (1, 0, 1), 'KTA_BRASIL': (1, 0, 1)},
            'Emision de Nota Fiscal': {'AEC': (24, 4, 31), 'CTX': (4, 3, 7), 'KTA_BRASIL': (3, 7, 11)},
            'Facturación': {'AEC': (18, 2, 23), 'KTA_BRASIL': (1, 7, 8)},
        },
        'S1': {
            'Datos fiscales': {'AEC': (2, 0, 4), 'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (19, 1, 22), 'CTX': (2, 1, 3), 'KTA_BRASIL': (8, 3, 13)},
            'Facturación': {'AEC': (14, 2, 17), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 4, 8)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'AEC': (24, 4, 30), 'ATE': (188, 34, 248), 'CTX': (50, 12, 72), 'KTA_BRASIL': (140, 30, 188)},
            'Gestiones Operativas': {'AEC': (14, 0, 16), 'ATE': (48, 8, 64), 'CTX': (8, 2, 10), 'KTA_BRASIL': (24, 6, 32)},
            'Reputación ME': {'AEC': (196, 8, 214), 'ATE': (84, 6, 92), 'CTX': (26, 4, 32), 'KTA_BRASIL': (134, 8, 146)},
            'Reversa': {'AEC': (6, 2, 8), 'ATE': (26, 6, 34), 'KTA_BRASIL': (30, 10, 42), 'MELICIDADE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (8, 2, 10), 'ATE': (28, 10, 40), 'CTX': (4, 0, 4), 'KTA_BRASIL': (18, 0, 24)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'AEC': (26, 8, 38), 'ATE': (288, 34, 352), 'CTX': (54, 6, 62), 'KTA_BRASIL': (168, 24, 220), 'MELICIDADE': (2, 0, 2)},
            'Gestiones Operativas': {'AEC': (2, 0, 2), 'ATE': (54, 0, 56), 'CTX': (10, 4, 16), 'KTA_BRASIL': (16, 8, 26)},
            'Reputación ME': {'AEC': (184, 6, 200), 'ATE': (86, 8, 102), 'CTX': (12, 0, 14), 'KTA_BRASIL': (136, 12, 162)},
            'Reversa': {'AEC': (8, 6, 16), 'ATE': (38, 8, 48), 'KTA_BRASIL': (32, 4, 42)},
            'Viaje del paquete - Vendedor': {'AEC': (2, 0, 4), 'ATE': (22, 4, 28), 'CTX': (4, 0, 4), 'KTA_BRASIL': (22, 2, 26)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (14, 5, 25), 'ATE': (33, 10, 46), 'CTX': (5, 3, 10), 'KTA_BRASIL': (28, 11, 45), 'MELICIDADE': (2, 1, 3)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (30, 10, 43), 'ATE': (21, 6, 31), 'CTX': (5, 4, 9), 'KTA_BRASIL': (22, 6, 33), 'MELICIDADE': (3, 0, 3)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'AEC': (23, 7, 35), 'ATE': (240, 29, 290), 'CTX': (35, 8, 49), 'KTA_BRASIL': (190, 32, 251)},
            'Places Kangu': {'AEC': (2, 0, 2), 'ATE': (46, 4, 54), 'CTX': (7, 1, 9), 'KTA_BRASIL': (23, 4, 28)},
        },
        'S1': {
            'Drivers': {'AEC': (16, 7, 24), 'ATE': (228, 35, 287), 'CTX': (34, 8, 51), 'KTA_BRASIL': (197, 40, 262)},
            'Places Kangu': {'AEC': (4, 1, 6), 'ATE': (35, 3, 42), 'CTX': (5, 4, 11), 'KTA_BRASIL': (28, 1, 33)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'AEC': (1, 1, 2), 'ATE': (1, 0, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Reputación': {'AEC': (71, 7, 81), 'ATE': (33, 3, 39), 'CTX': (6, 2, 9), 'KTA_BRASIL': (61, 4, 72)},
        },
        'S1': {
            'Anulación de Venta': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 0, 1)},
            'Reputación': {'AEC': (70, 9, 85), 'ATE': (29, 4, 41), 'CTX': (8, 0, 8), 'KTA_BRASIL': (65, 6, 80)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'AEC': (146, 11, 173), 'CTX': (6, 3, 9), 'KTA_BRASIL': (13, 18, 32)},
            'Antes de publicar': {'AEC': (15, 1, 17), 'CTX': (4, 0, 5), 'KTA_BRASIL': (15, 0, 16)},
            'Calidad de foto': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'Denuncia de usuario': {'AEC': (5, 2, 8), 'CTX': (3, 0, 3), 'KTA_BRASIL': (0, 1, 1)},
            'Gestión de Publicación': {'AEC': (24, 3, 30), 'CTX': (6, 1, 7), 'KTA_BRASIL': (16, 4, 25)},
            'PR - Artículos prohibidos': {'AEC': (7, 5, 12), 'KTA_BRASIL': (15, 4, 22)},
            'PR - Datos Personales': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'PR - Propiedad intelectual': {'AEC': (22, 0, 22), 'KTA_BRASIL': (16, 4, 22)},
            'PR - Técnica prohibida': {'AEC': (16, 6, 22), 'KTA_BRASIL': (27, 1, 28)},
            'Potenciar Ventas': {'AEC': (8, 6, 15), 'CTX': (4, 2, 6), 'KTA_BRASIL': (17, 4, 24)},
        },
        'S1': {
            'Afiliados ML': {'AEC': (166, 14, 199), 'CTX': (3, 1, 5), 'KTA_BRASIL': (20, 20, 42)},
            'Antes de publicar': {'AEC': (6, 2, 8), 'CTX': (2, 0, 2), 'KTA_BRASIL': (18, 1, 22)},
            'Calidad de foto': {'AEC': (3, 1, 5), 'KTA_BRASIL': (9, 2, 12)},
            'Denuncia de usuario': {'AEC': (4, 2, 6), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Gestión de Publicación': {'AEC': (11, 3, 16), 'CTX': (3, 0, 3), 'KTA_BRASIL': (20, 7, 30)},
            'PR - Artículos prohibidos': {'AEC': (4, 3, 9), 'KTA_BRASIL': (18, 3, 23)},
            'PR - Datos Personales': {'AEC': (0, 1, 1), 'KTA_BRASIL': (5, 0, 6)},
            'PR - Propiedad intelectual': {'AEC': (10, 3, 13), 'KTA_BRASIL': (17, 7, 27)},
            'PR - Técnica prohibida': {'AEC': (21, 3, 24), 'ATE': (0, 0, 1), 'KTA_BRASIL': (18, 4, 25)},
            'Potenciar Ventas': {'AEC': (5, 6, 12), 'CTX': (2, 1, 4), 'KTA_BRASIL': (11, 1, 14), 'MELICIDADE': (1, 0, 1)},
        },
    },
}
p_o_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'AEC': (28, 3, 35), 'CTX': (4, 1, 5), 'KTA_BRASIL': (4, 3, 8)},
            'Emision de Nota Fiscal': {'AEC': (180, 23, 227), 'CTX': (29, 9, 39), 'KTA_BRASIL': (31, 29, 65)},
            'Facturación': {'AEC': (105, 18, 141), 'CTX': (9, 3, 12), 'KTA_BRASIL': (14, 22, 38)},
        },
        'M1': {
            'Datos fiscales': {'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (6, 0, 7), 'KTA_BRASIL': (1, 2, 3)},
            'Facturación': {'AEC': (1, 1, 2), 'KTA_BRASIL': (1, 2, 3)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'AEC': (146, 36, 196), 'ATE': (1214, 212, 1618), 'CTX': (302, 56, 386), 'KTA_BRASIL': (598, 116, 804), 'MELICIDADE': (6, 0, 6)},
            'Gestiones Operativas': {'AEC': (34, 8, 46), 'ATE': (244, 32, 306), 'CTX': (54, 12, 74), 'KTA_BRASIL': (80, 22, 114), 'MELICIDADE': (2, 0, 2)},
            'Reputación ME': {'AEC': (996, 28, 1084), 'ATE': (426, 30, 490), 'CTX': (134, 10, 160), 'KTA_BRASIL': (584, 64, 686), 'MELICIDADE': (2, 2, 4)},
            'Reversa': {'AEC': (34, 10, 46), 'ATE': (178, 30, 222), 'KTA_BRASIL': (152, 32, 212), 'MELICIDADE': (2, 0, 2)},
            'Suspensiones ME': {'ATE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (24, 4, 32), 'ATE': (120, 26, 170), 'CTX': (24, 0, 24), 'KTA_BRASIL': (60, 10, 86)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'AEC': (4, 2, 6), 'ATE': (86, 6, 96), 'KTA_BRASIL': (58, 2, 64)},
            'Gestiones Operativas': {'ATE': (16, 0, 16), 'KTA_BRASIL': (4, 0, 4)},
            'Reputación ME': {'AEC': (18, 2, 24), 'ATE': (26, 0, 26), 'KTA_BRASIL': (26, 4, 32)},
            'Reversa': {'ATE': (2, 6, 8), 'KTA_BRASIL': (6, 2, 10)},
            'Viaje del paquete - Vendedor': {'ATE': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (93, 35, 144), 'ATE': (166, 37, 225), 'CTX': (28, 13, 44), 'KTA_BRASIL': (79, 28, 118), 'MELICIDADE': (28, 5, 37)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (4, 0, 5), 'ATE': (2, 1, 4), 'KTA_BRASIL': (4, 0, 7)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'AEC': (74, 23, 110), 'ATE': (987, 137, 1223), 'CTX': (180, 36, 241), 'KTA_BRASIL': (577, 105, 763)},
            'Places Kangu': {'AEC': (21, 3, 25), 'ATE': (215, 27, 262), 'CTX': (64, 9, 81), 'KTA_BRASIL': (110, 19, 140)},
        },
        'M1': {
            'Drivers': {'AEC': (8, 1, 10), 'ATE': (93, 8, 112), 'KTA_BRASIL': (70, 17, 100)},
            'Places Kangu': {'ATE': (7, 0, 8), 'KTA_BRASIL': (7, 0, 8)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'AEC': (16, 2, 18), 'ATE': (6, 1, 7), 'CTX': (3, 0, 4), 'KTA_BRASIL': (5, 2, 7)},
            'Reputación': {'AEC': (310, 46, 382), 'ATE': (177, 17, 220), 'CTX': (70, 12, 90), 'KTA_BRASIL': (265, 36, 326), 'MELICIDADE': (5, 0, 5)},
        },
        'M1': {
            'Reputación': {'AEC': (8, 1, 9), 'ATE': (8, 1, 10), 'KTA_BRASIL': (11, 0, 13)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'AEC': (871, 87, 1044), 'CTX': (30, 11, 44), 'KTA_BRASIL': (57, 68, 138), 'MELICIDADE': (1, 0, 1)},
            'Antes de publicar': {'AEC': (70, 5, 84), 'CTX': (17, 2, 21), 'KTA_BRASIL': (75, 6, 89)},
            'Calidad de foto': {'AEC': (3, 2, 7), 'KTA_BRASIL': (15, 3, 18)},
            'Denuncia de usuario': {'AEC': (38, 7, 49), 'CTX': (7, 2, 10), 'KTA_BRASIL': (8, 3, 11)},
            'Gestión de Publicación': {'AEC': (62, 18, 88), 'CTX': (23, 8, 31), 'KTA_BRASIL': (111, 15, 150)},
            'PR - Artículos prohibidos': {'AEC': (31, 15, 48), 'CTX': (1, 0, 1), 'KTA_BRASIL': (66, 16, 87)},
            'PR - Datos Personales': {'AEC': (3, 1, 4), 'KTA_BRASIL': (8, 5, 14)},
            'PR - Propiedad intelectual': {'AEC': (65, 10, 79), 'KTA_BRASIL': (99, 21, 128)},
            'PR - Técnica prohibida': {'AEC': (95, 15, 116), 'ATE': (0, 0, 1), 'KTA_BRASIL': (105, 13, 134), 'MELICIDADE': (3, 0, 3)},
            'Potenciar Ventas': {'AEC': (44, 17, 66), 'CTX': (16, 6, 27), 'KTA_BRASIL': (74, 16, 102), 'MELICIDADE': (1, 0, 1)},
        },
        'M1': {
            'Afiliados ML': {'AEC': (77, 5, 89), 'KTA_BRASIL': (9, 3, 12)},
            'Antes de publicar': {'AEC': (0, 1, 1), 'KTA_BRASIL': (3, 0, 3)},
            'Calidad de foto': {'AEC': (3, 0, 4), 'KTA_BRASIL': (8, 1, 10)},
            'Denuncia de usuario': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 1, 2)},
            'Gestión de Publicación': {'AEC': (6, 1, 7), 'KTA_BRASIL': (4, 1, 5)},
            'PR - Artículos prohibidos': {'AEC': (1, 0, 2), 'KTA_BRASIL': (7, 1, 10)},
            'PR - Datos Personales': {'KTA_BRASIL': (4, 0, 4)},
            'PR - Propiedad intelectual': {'AEC': (3, 1, 4), 'KTA_BRASIL': (5, 4, 10)},
            'PR - Técnica prohibida': {'AEC': (5, 0, 5), 'KTA_BRASIL': (4, 2, 7)},
            'Potenciar Ventas': {'AEC': (2, 3, 5), 'KTA_BRASIL': (2, 1, 3)},
        },
    },
}


# ════════════════════════════════════════════════════════════════
# SECTION 2G: P×CANAL DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_TEAM_CHANNEL)
# ════════════════════════════════════════════════════════════════
p_c_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (5, 0, 6)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (7, 10, 18), 'MULTICANAL CHAT': (24, 4, 31)},
            'Facturación': {'MULTICANAL C2C': (1, 7, 8), 'MULTICANAL CHAT': (18, 2, 23)},
        },
        'S1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 4)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (10, 4, 16), 'MULTICANAL CHAT': (19, 1, 22)},
            'Facturación': {'MULTICANAL C2C': (4, 5, 9), 'MULTICANAL CHAT': (14, 2, 17)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (70, 12, 92), 'MULTICANAL CHAT': (332, 68, 446)},
            'Gestiones Operativas': {'MULTICANAL C2C': (26, 4, 32), 'MULTICANAL CHAT': (68, 12, 90)},
            'Reputación ME': {'MULTICANAL C2C': (64, 8, 72), 'MULTICANAL CHAT': (376, 18, 412)},
            'Reversa': {'MULTICANAL C2C': (12, 4, 16), 'MULTICANAL CHAT': (52, 14, 70)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (48, 10, 66)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (92, 22, 126), 'MULTICANAL CHAT': (446, 50, 548)},
            'Gestiones Operativas': {'MULTICANAL C2C': (16, 0, 16), 'MULTICANAL CHAT': (66, 12, 84)},
            'Reputación ME': {'MULTICANAL C2C': (66, 12, 82), 'MULTICANAL CHAT': (352, 14, 396)},
            'Reversa': {'MULTICANAL C2C': (12, 10, 24), 'MULTICANAL CHAT': (66, 8, 82)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 0, 14), 'MULTICANAL CHAT': (40, 6, 48)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (30, 18, 50), 'MULTICANAL CHAT': (52, 12, 79)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (22, 14, 41), 'MULTICANAL CHAT': (59, 12, 78)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'MULTICANAL C2C': (60, 19, 93), 'MULTICANAL CHAT': (428, 57, 532)},
            'Places Kangu': {'MULTICANAL C2C': (7, 1, 9), 'MULTICANAL CHAT': (71, 8, 84)},
        },
        'S1': {
            'Drivers': {'MULTICANAL C2C': (55, 21, 81), 'MULTICANAL CHAT': (420, 69, 543)},
            'Places Kangu': {'MULTICANAL C2C': (13, 3, 19), 'MULTICANAL CHAT': (59, 6, 73)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'MULTICANAL C2C': (2, 1, 3), 'MULTICANAL CHAT': (4, 1, 5)},
            'Reputación': {'MULTICANAL C2C': (30, 8, 40), 'MULTICANAL CHAT': (141, 8, 161)},
        },
        'S1': {
            'Anulación de Venta': {'MULTICANAL CHAT': (3, 0, 3)},
            'Reputación': {'MULTICANAL C2C': (41, 4, 48), 'MULTICANAL CHAT': (131, 15, 166)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'MULTICANAL C2C': (19, 21, 41), 'MULTICANAL CHAT': (146, 11, 173)},
            'Antes de publicar': {'MULTICANAL C2C': (6, 1, 8), 'MULTICANAL CHAT': (28, 0, 30)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 0, 1), 'MULTICANAL CHAT': (5, 0, 5)},
            'Denuncia de usuario': {'MULTICANAL C2C': (3, 1, 4), 'MULTICANAL CHAT': (5, 2, 8)},
            'Gestión de Publicación': {'MULTICANAL C2C': (14, 3, 17), 'MULTICANAL CHAT': (32, 5, 45)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (21, 8, 32)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (6, 0, 6)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (38, 4, 44)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (5, 2, 7), 'MULTICANAL CHAT': (38, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 9), 'MULTICANAL CHAT': (24, 8, 36)},
        },
        'S1': {
            'Afiliados ML': {'MULTICANAL C2C': (23, 21, 47), 'MULTICANAL CHAT': (166, 14, 199)},
            'Antes de publicar': {'MULTICANAL C2C': (5, 1, 6), 'MULTICANAL CHAT': (21, 2, 26)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 1, 2), 'MULTICANAL CHAT': (12, 2, 15)},
            'Denuncia de usuario': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (4, 2, 6)},
            'Gestión de Publicación': {'MULTICANAL C2C': (5, 3, 9), 'MULTICANAL CHAT': (29, 7, 40)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (22, 5, 31)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (5, 1, 7)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (27, 10, 40)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (4, 2, 7), 'MULTICANAL CHAT': (35, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 11), 'MULTICANAL CHAT': (14, 4, 20)},
        },
    },
}
p_c_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'MULTICANAL C2C': (8, 4, 13), 'MULTICANAL CHAT': (28, 3, 35)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (60, 37, 103), 'MULTICANAL CHAT': (180, 24, 228)},
            'Facturación': {'MULTICANAL C2C': (23, 25, 50), 'MULTICANAL CHAT': (105, 18, 141)},
        },
        'M1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (6, 0, 7)},
            'Facturación': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (1, 1, 2)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (370, 110, 532), 'MULTICANAL CHAT': (1894, 308, 2472)},
            'Gestiones Operativas': {'MULTICANAL C2C': (98, 22, 126), 'MULTICANAL CHAT': (312, 52, 412)},
            'Reputación ME': {'MULTICANAL C2C': (356, 46, 422), 'MULTICANAL CHAT': (1784, 88, 2000)},
            'Reversa': {'MULTICANAL C2C': (70, 18, 92), 'MULTICANAL CHAT': (294, 54, 388)},
            'Suspensiones ME': {'MULTICANAL C2C': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (44, 8, 68), 'MULTICANAL CHAT': (184, 32, 244)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (30, 6, 36), 'MULTICANAL CHAT': (118, 4, 130)},
            'Gestiones Operativas': {'MULTICANAL CHAT': (20, 0, 20)},
            'Reputación ME': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (60, 4, 70)},
            'Reversa': {'MULTICANAL C2C': (0, 4, 4), 'MULTICANAL CHAT': (8, 4, 14)},
            'Viaje del paquete - Vendedor': {'MULTICANAL CHAT': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (112, 51, 172), 'MULTICANAL CHAT': (280, 66, 393)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (1, 1, 4), 'MULTICANAL CHAT': (9, 0, 12)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'MULTICANAL C2C': (222, 65, 328), 'MULTICANAL CHAT': (1592, 236, 2004)},
            'Places Kangu': {'MULTICANAL C2C': (55, 13, 72), 'MULTICANAL CHAT': (355, 45, 436)},
        },
        'M1': {
            'Drivers': {'MULTICANAL C2C': (23, 4, 29), 'MULTICANAL CHAT': (148, 22, 193)},
            'Places Kangu': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (14, 0, 15)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'MULTICANAL C2C': (6, 2, 9), 'MULTICANAL CHAT': (24, 3, 27)},
            'Reputación': {'MULTICANAL C2C': (193, 33, 242), 'MULTICANAL CHAT': (633, 78, 780)},
        },
        'M1': {
            'Reputación': {'MULTICANAL C2C': (3, 1, 5), 'MULTICANAL CHAT': (24, 1, 27)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'MULTICANAL C2C': (87, 79, 182), 'MULTICANAL CHAT': (872, 87, 1045)},
            'Antes de publicar': {'MULTICANAL C2C': (28, 4, 35), 'MULTICANAL CHAT': (134, 9, 159)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (17, 4, 23)},
            'Denuncia de usuario': {'MULTICANAL C2C': (15, 5, 21), 'MULTICANAL CHAT': (38, 7, 49)},
            'Gestión de Publicación': {'MULTICANAL C2C': (34, 17, 53), 'MULTICANAL CHAT': (162, 24, 216)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (7, 4, 11), 'MULTICANAL CHAT': (91, 27, 125)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (11, 6, 18)},
            'PR - Propiedad intelectual': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (160, 29, 201)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (14, 6, 21), 'MULTICANAL CHAT': (189, 22, 233)},
            'Potenciar Ventas': {'MULTICANAL C2C': (23, 12, 41), 'MULTICANAL CHAT': (112, 27, 155)},
        },
        'M1': {
            'Afiliados ML': {'MULTICANAL C2C': (9, 3, 12), 'MULTICANAL CHAT': (77, 5, 89)},
            'Antes de publicar': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (3, 0, 3)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (11, 1, 13)},
            'Denuncia de usuario': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 2)},
            'Gestión de Publicación': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (10, 1, 11)},
            'PR - Artículos prohibidos': {'MULTICANAL CHAT': (8, 1, 12)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (4, 0, 4)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (8, 5, 14)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (7, 2, 10)},
            'Potenciar Ventas': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (3, 2, 5)},
        },
    },
}

# ════════════════════════════════════════════════════════════════
# SECTION 2H: P×OFICINA DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_OFFICE)
# ════════════════════════════════════════════════════════════════
p_o_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'AEC': (5, 0, 6), 'CTX': (1, 0, 1), 'KTA_BRASIL': (1, 0, 1)},
            'Emision de Nota Fiscal': {'AEC': (24, 4, 31), 'CTX': (4, 3, 7), 'KTA_BRASIL': (3, 7, 11)},
            'Facturación': {'AEC': (18, 2, 23), 'KTA_BRASIL': (1, 7, 8)},
        },
        'S1': {
            'Datos fiscales': {'AEC': (2, 0, 4), 'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (19, 1, 22), 'CTX': (2, 1, 3), 'KTA_BRASIL': (8, 3, 13)},
            'Facturación': {'AEC': (14, 2, 17), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 4, 8)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'AEC': (24, 4, 30), 'ATE': (188, 34, 248), 'CTX': (50, 12, 72), 'KTA_BRASIL': (140, 30, 188)},
            'Gestiones Operativas': {'AEC': (14, 0, 16), 'ATE': (48, 8, 64), 'CTX': (8, 2, 10), 'KTA_BRASIL': (24, 6, 32)},
            'Reputación ME': {'AEC': (196, 8, 214), 'ATE': (84, 6, 92), 'CTX': (26, 4, 32), 'KTA_BRASIL': (134, 8, 146)},
            'Reversa': {'AEC': (6, 2, 8), 'ATE': (26, 6, 34), 'KTA_BRASIL': (30, 10, 42), 'MELICIDADE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (8, 2, 10), 'ATE': (28, 10, 40), 'CTX': (4, 0, 4), 'KTA_BRASIL': (18, 0, 24)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'AEC': (26, 8, 38), 'ATE': (288, 34, 352), 'CTX': (54, 6, 62), 'KTA_BRASIL': (168, 24, 220), 'MELICIDADE': (2, 0, 2)},
            'Gestiones Operativas': {'AEC': (2, 0, 2), 'ATE': (54, 0, 56), 'CTX': (10, 4, 16), 'KTA_BRASIL': (16, 8, 26)},
            'Reputación ME': {'AEC': (184, 6, 200), 'ATE': (86, 8, 102), 'CTX': (12, 0, 14), 'KTA_BRASIL': (136, 12, 162)},
            'Reversa': {'AEC': (8, 6, 16), 'ATE': (38, 8, 48), 'KTA_BRASIL': (32, 4, 42)},
            'Viaje del paquete - Vendedor': {'AEC': (2, 0, 4), 'ATE': (22, 4, 28), 'CTX': (4, 0, 4), 'KTA_BRASIL': (22, 2, 26)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (14, 5, 25), 'ATE': (33, 10, 46), 'CTX': (5, 3, 10), 'KTA_BRASIL': (28, 11, 45), 'MELICIDADE': (2, 1, 3)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (30, 10, 43), 'ATE': (21, 6, 31), 'CTX': (5, 4, 9), 'KTA_BRASIL': (22, 6, 33), 'MELICIDADE': (3, 0, 3)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'AEC': (23, 7, 35), 'ATE': (240, 29, 290), 'CTX': (35, 8, 49), 'KTA_BRASIL': (190, 32, 251)},
            'Places Kangu': {'AEC': (2, 0, 2), 'ATE': (46, 4, 54), 'CTX': (7, 1, 9), 'KTA_BRASIL': (23, 4, 28)},
        },
        'S1': {
            'Drivers': {'AEC': (16, 7, 24), 'ATE': (228, 35, 287), 'CTX': (34, 8, 51), 'KTA_BRASIL': (197, 40, 262)},
            'Places Kangu': {'AEC': (4, 1, 6), 'ATE': (35, 3, 42), 'CTX': (5, 4, 11), 'KTA_BRASIL': (28, 1, 33)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'AEC': (1, 1, 2), 'ATE': (1, 0, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Reputación': {'AEC': (71, 7, 81), 'ATE': (33, 3, 39), 'CTX': (6, 2, 9), 'KTA_BRASIL': (61, 4, 72)},
        },
        'S1': {
            'Anulación de Venta': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 0, 1)},
            'Reputación': {'AEC': (70, 9, 85), 'ATE': (29, 4, 41), 'CTX': (8, 0, 8), 'KTA_BRASIL': (65, 6, 80)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'AEC': (146, 11, 173), 'CTX': (6, 3, 9), 'KTA_BRASIL': (13, 18, 32)},
            'Antes de publicar': {'AEC': (15, 1, 17), 'CTX': (4, 0, 5), 'KTA_BRASIL': (15, 0, 16)},
            'Calidad de foto': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'Denuncia de usuario': {'AEC': (5, 2, 8), 'CTX': (3, 0, 3), 'KTA_BRASIL': (0, 1, 1)},
            'Gestión de Publicación': {'AEC': (24, 3, 30), 'CTX': (6, 1, 7), 'KTA_BRASIL': (16, 4, 25)},
            'PR - Artículos prohibidos': {'AEC': (7, 5, 12), 'KTA_BRASIL': (15, 4, 22)},
            'PR - Datos Personales': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'PR - Propiedad intelectual': {'AEC': (22, 0, 22), 'KTA_BRASIL': (16, 4, 22)},
            'PR - Técnica prohibida': {'AEC': (16, 6, 22), 'KTA_BRASIL': (27, 1, 28)},
            'Potenciar Ventas': {'AEC': (8, 6, 15), 'CTX': (4, 2, 6), 'KTA_BRASIL': (17, 4, 24)},
        },
        'S1': {
            'Afiliados ML': {'AEC': (166, 14, 199), 'CTX': (3, 1, 5), 'KTA_BRASIL': (20, 20, 42)},
            'Antes de publicar': {'AEC': (6, 2, 8), 'CTX': (2, 0, 2), 'KTA_BRASIL': (18, 1, 22)},
            'Calidad de foto': {'AEC': (3, 1, 5), 'KTA_BRASIL': (9, 2, 12)},
            'Denuncia de usuario': {'AEC': (4, 2, 6), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Gestión de Publicación': {'AEC': (11, 3, 16), 'CTX': (3, 0, 3), 'KTA_BRASIL': (20, 7, 30)},
            'PR - Artículos prohibidos': {'AEC': (4, 3, 9), 'KTA_BRASIL': (18, 3, 23)},
            'PR - Datos Personales': {'AEC': (0, 1, 1), 'KTA_BRASIL': (5, 0, 6)},
            'PR - Propiedad intelectual': {'AEC': (10, 3, 13), 'KTA_BRASIL': (17, 7, 27)},
            'PR - Técnica prohibida': {'AEC': (21, 3, 24), 'ATE': (0, 0, 1), 'KTA_BRASIL': (18, 4, 25)},
            'Potenciar Ventas': {'AEC': (5, 6, 12), 'CTX': (2, 1, 4), 'KTA_BRASIL': (11, 1, 14), 'MELICIDADE': (1, 0, 1)},
        },
    },
}
p_o_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'AEC': (28, 3, 35), 'CTX': (4, 1, 5), 'KTA_BRASIL': (4, 3, 8)},
            'Emision de Nota Fiscal': {'AEC': (180, 23, 227), 'CTX': (29, 9, 39), 'KTA_BRASIL': (31, 29, 65)},
            'Facturación': {'AEC': (105, 18, 141), 'CTX': (9, 3, 12), 'KTA_BRASIL': (14, 22, 38)},
        },
        'M1': {
            'Datos fiscales': {'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (6, 0, 7), 'KTA_BRASIL': (1, 2, 3)},
            'Facturación': {'AEC': (1, 1, 2), 'KTA_BRASIL': (1, 2, 3)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'AEC': (146, 36, 196), 'ATE': (1214, 212, 1618), 'CTX': (302, 56, 386), 'KTA_BRASIL': (598, 116, 804), 'MELICIDADE': (6, 0, 6)},
            'Gestiones Operativas': {'AEC': (34, 8, 46), 'ATE': (244, 32, 306), 'CTX': (54, 12, 74), 'KTA_BRASIL': (80, 22, 114), 'MELICIDADE': (2, 0, 2)},
            'Reputación ME': {'AEC': (996, 28, 1084), 'ATE': (426, 30, 490), 'CTX': (134, 10, 160), 'KTA_BRASIL': (584, 64, 686), 'MELICIDADE': (2, 2, 4)},
            'Reversa': {'AEC': (34, 10, 46), 'ATE': (178, 30, 222), 'KTA_BRASIL': (152, 32, 212), 'MELICIDADE': (2, 0, 2)},
            'Suspensiones ME': {'ATE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (24, 4, 32), 'ATE': (120, 26, 170), 'CTX': (24, 0, 24), 'KTA_BRASIL': (60, 10, 86)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'AEC': (4, 2, 6), 'ATE': (86, 6, 96), 'KTA_BRASIL': (58, 2, 64)},
            'Gestiones Operativas': {'ATE': (16, 0, 16), 'KTA_BRASIL': (4, 0, 4)},
            'Reputación ME': {'AEC': (18, 2, 24), 'ATE': (26, 0, 26), 'KTA_BRASIL': (26, 4, 32)},
            'Reversa': {'ATE': (2, 6, 8), 'KTA_BRASIL': (6, 2, 10)},
            'Viaje del paquete - Vendedor': {'ATE': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (93, 35, 144), 'ATE': (166, 37, 225), 'CTX': (28, 13, 44), 'KTA_BRASIL': (79, 28, 118), 'MELICIDADE': (28, 5, 37)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (4, 0, 5), 'ATE': (2, 1, 4), 'KTA_BRASIL': (4, 0, 7)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'AEC': (74, 23, 110), 'ATE': (987, 137, 1223), 'CTX': (180, 36, 241), 'KTA_BRASIL': (577, 105, 763)},
            'Places Kangu': {'AEC': (21, 3, 25), 'ATE': (215, 27, 262), 'CTX': (64, 9, 81), 'KTA_BRASIL': (110, 19, 140)},
        },
        'M1': {
            'Drivers': {'AEC': (8, 1, 10), 'ATE': (93, 8, 112), 'KTA_BRASIL': (70, 17, 100)},
            'Places Kangu': {'ATE': (7, 0, 8), 'KTA_BRASIL': (7, 0, 8)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'AEC': (16, 2, 18), 'ATE': (6, 1, 7), 'CTX': (3, 0, 4), 'KTA_BRASIL': (5, 2, 7)},
            'Reputación': {'AEC': (310, 46, 382), 'ATE': (177, 17, 220), 'CTX': (70, 12, 90), 'KTA_BRASIL': (265, 36, 326), 'MELICIDADE': (5, 0, 5)},
        },
        'M1': {
            'Reputación': {'AEC': (8, 1, 9), 'ATE': (8, 1, 10), 'KTA_BRASIL': (11, 0, 13)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'AEC': (871, 87, 1044), 'CTX': (30, 11, 44), 'KTA_BRASIL': (57, 68, 138), 'MELICIDADE': (1, 0, 1)},
            'Antes de publicar': {'AEC': (70, 5, 84), 'CTX': (17, 2, 21), 'KTA_BRASIL': (75, 6, 89)},
            'Calidad de foto': {'AEC': (3, 2, 7), 'KTA_BRASIL': (15, 3, 18)},
            'Denuncia de usuario': {'AEC': (38, 7, 49), 'CTX': (7, 2, 10), 'KTA_BRASIL': (8, 3, 11)},
            'Gestión de Publicación': {'AEC': (62, 18, 88), 'CTX': (23, 8, 31), 'KTA_BRASIL': (111, 15, 150)},
            'PR - Artículos prohibidos': {'AEC': (31, 15, 48), 'CTX': (1, 0, 1), 'KTA_BRASIL': (66, 16, 87)},
            'PR - Datos Personales': {'AEC': (3, 1, 4), 'KTA_BRASIL': (8, 5, 14)},
            'PR - Propiedad intelectual': {'AEC': (65, 10, 79), 'KTA_BRASIL': (99, 21, 128)},
            'PR - Técnica prohibida': {'AEC': (95, 15, 116), 'ATE': (0, 0, 1), 'KTA_BRASIL': (105, 13, 134), 'MELICIDADE': (3, 0, 3)},
            'Potenciar Ventas': {'AEC': (44, 17, 66), 'CTX': (16, 6, 27), 'KTA_BRASIL': (74, 16, 102), 'MELICIDADE': (1, 0, 1)},
        },
        'M1': {
            'Afiliados ML': {'AEC': (77, 5, 89), 'KTA_BRASIL': (9, 3, 12)},
            'Antes de publicar': {'AEC': (0, 1, 1), 'KTA_BRASIL': (3, 0, 3)},
            'Calidad de foto': {'AEC': (3, 0, 4), 'KTA_BRASIL': (8, 1, 10)},
            'Denuncia de usuario': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 1, 2)},
            'Gestión de Publicación': {'AEC': (6, 1, 7), 'KTA_BRASIL': (4, 1, 5)},
            'PR - Artículos prohibidos': {'AEC': (1, 0, 2), 'KTA_BRASIL': (7, 1, 10)},
            'PR - Datos Personales': {'KTA_BRASIL': (4, 0, 4)},
            'PR - Propiedad intelectual': {'AEC': (3, 1, 4), 'KTA_BRASIL': (5, 4, 10)},
            'PR - Técnica prohibida': {'AEC': (5, 0, 5), 'KTA_BRASIL': (4, 2, 7)},
            'Potenciar Ventas': {'AEC': (2, 3, 5), 'KTA_BRASIL': (2, 1, 3)},
        },
    },
}


# ════════════════════════════════════════════════════════════════
# SECTION 2G: P×CANAL DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_TEAM_CHANNEL)
# ════════════════════════════════════════════════════════════════
p_c_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (5, 0, 6)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (7, 10, 18), 'MULTICANAL CHAT': (24, 4, 31)},
            'Facturación': {'MULTICANAL C2C': (1, 7, 8), 'MULTICANAL CHAT': (18, 2, 23)},
        },
        'S1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 4)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (10, 4, 16), 'MULTICANAL CHAT': (19, 1, 22)},
            'Facturación': {'MULTICANAL C2C': (4, 5, 9), 'MULTICANAL CHAT': (14, 2, 17)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (70, 12, 92), 'MULTICANAL CHAT': (332, 68, 446)},
            'Gestiones Operativas': {'MULTICANAL C2C': (26, 4, 32), 'MULTICANAL CHAT': (68, 12, 90)},
            'Reputación ME': {'MULTICANAL C2C': (64, 8, 72), 'MULTICANAL CHAT': (376, 18, 412)},
            'Reversa': {'MULTICANAL C2C': (12, 4, 16), 'MULTICANAL CHAT': (52, 14, 70)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (48, 10, 66)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (92, 22, 126), 'MULTICANAL CHAT': (446, 50, 548)},
            'Gestiones Operativas': {'MULTICANAL C2C': (16, 0, 16), 'MULTICANAL CHAT': (66, 12, 84)},
            'Reputación ME': {'MULTICANAL C2C': (66, 12, 82), 'MULTICANAL CHAT': (352, 14, 396)},
            'Reversa': {'MULTICANAL C2C': (12, 10, 24), 'MULTICANAL CHAT': (66, 8, 82)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 0, 14), 'MULTICANAL CHAT': (40, 6, 48)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (30, 18, 50), 'MULTICANAL CHAT': (52, 12, 79)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (22, 14, 41), 'MULTICANAL CHAT': (59, 12, 78)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'MULTICANAL C2C': (60, 19, 93), 'MULTICANAL CHAT': (428, 57, 532)},
            'Places Kangu': {'MULTICANAL C2C': (7, 1, 9), 'MULTICANAL CHAT': (71, 8, 84)},
        },
        'S1': {
            'Drivers': {'MULTICANAL C2C': (55, 21, 81), 'MULTICANAL CHAT': (420, 69, 543)},
            'Places Kangu': {'MULTICANAL C2C': (13, 3, 19), 'MULTICANAL CHAT': (59, 6, 73)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'MULTICANAL C2C': (2, 1, 3), 'MULTICANAL CHAT': (4, 1, 5)},
            'Reputación': {'MULTICANAL C2C': (30, 8, 40), 'MULTICANAL CHAT': (141, 8, 161)},
        },
        'S1': {
            'Anulación de Venta': {'MULTICANAL CHAT': (3, 0, 3)},
            'Reputación': {'MULTICANAL C2C': (41, 4, 48), 'MULTICANAL CHAT': (131, 15, 166)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'MULTICANAL C2C': (19, 21, 41), 'MULTICANAL CHAT': (146, 11, 173)},
            'Antes de publicar': {'MULTICANAL C2C': (6, 1, 8), 'MULTICANAL CHAT': (28, 0, 30)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 0, 1), 'MULTICANAL CHAT': (5, 0, 5)},
            'Denuncia de usuario': {'MULTICANAL C2C': (3, 1, 4), 'MULTICANAL CHAT': (5, 2, 8)},
            'Gestión de Publicación': {'MULTICANAL C2C': (14, 3, 17), 'MULTICANAL CHAT': (32, 5, 45)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (21, 8, 32)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (6, 0, 6)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (38, 4, 44)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (5, 2, 7), 'MULTICANAL CHAT': (38, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 9), 'MULTICANAL CHAT': (24, 8, 36)},
        },
        'S1': {
            'Afiliados ML': {'MULTICANAL C2C': (23, 21, 47), 'MULTICANAL CHAT': (166, 14, 199)},
            'Antes de publicar': {'MULTICANAL C2C': (5, 1, 6), 'MULTICANAL CHAT': (21, 2, 26)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 1, 2), 'MULTICANAL CHAT': (12, 2, 15)},
            'Denuncia de usuario': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (4, 2, 6)},
            'Gestión de Publicación': {'MULTICANAL C2C': (5, 3, 9), 'MULTICANAL CHAT': (29, 7, 40)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (22, 5, 31)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (5, 1, 7)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (27, 10, 40)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (4, 2, 7), 'MULTICANAL CHAT': (35, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 11), 'MULTICANAL CHAT': (14, 4, 20)},
        },
    },
}
p_c_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'MULTICANAL C2C': (8, 4, 13), 'MULTICANAL CHAT': (28, 3, 35)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (60, 37, 103), 'MULTICANAL CHAT': (180, 24, 228)},
            'Facturación': {'MULTICANAL C2C': (23, 25, 50), 'MULTICANAL CHAT': (105, 18, 141)},
        },
        'M1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (6, 0, 7)},
            'Facturación': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (1, 1, 2)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (370, 110, 532), 'MULTICANAL CHAT': (1894, 308, 2472)},
            'Gestiones Operativas': {'MULTICANAL C2C': (98, 22, 126), 'MULTICANAL CHAT': (312, 52, 412)},
            'Reputación ME': {'MULTICANAL C2C': (356, 46, 422), 'MULTICANAL CHAT': (1784, 88, 2000)},
            'Reversa': {'MULTICANAL C2C': (70, 18, 92), 'MULTICANAL CHAT': (294, 54, 388)},
            'Suspensiones ME': {'MULTICANAL C2C': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (44, 8, 68), 'MULTICANAL CHAT': (184, 32, 244)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (30, 6, 36), 'MULTICANAL CHAT': (118, 4, 130)},
            'Gestiones Operativas': {'MULTICANAL CHAT': (20, 0, 20)},
            'Reputación ME': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (60, 4, 70)},
            'Reversa': {'MULTICANAL C2C': (0, 4, 4), 'MULTICANAL CHAT': (8, 4, 14)},
            'Viaje del paquete - Vendedor': {'MULTICANAL CHAT': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (112, 51, 172), 'MULTICANAL CHAT': (280, 66, 393)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (1, 1, 4), 'MULTICANAL CHAT': (9, 0, 12)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'MULTICANAL C2C': (222, 65, 328), 'MULTICANAL CHAT': (1592, 236, 2004)},
            'Places Kangu': {'MULTICANAL C2C': (55, 13, 72), 'MULTICANAL CHAT': (355, 45, 436)},
        },
        'M1': {
            'Drivers': {'MULTICANAL C2C': (23, 4, 29), 'MULTICANAL CHAT': (148, 22, 193)},
            'Places Kangu': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (14, 0, 15)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'MULTICANAL C2C': (6, 2, 9), 'MULTICANAL CHAT': (24, 3, 27)},
            'Reputación': {'MULTICANAL C2C': (193, 33, 242), 'MULTICANAL CHAT': (633, 78, 780)},
        },
        'M1': {
            'Reputación': {'MULTICANAL C2C': (3, 1, 5), 'MULTICANAL CHAT': (24, 1, 27)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'MULTICANAL C2C': (87, 79, 182), 'MULTICANAL CHAT': (872, 87, 1045)},
            'Antes de publicar': {'MULTICANAL C2C': (28, 4, 35), 'MULTICANAL CHAT': (134, 9, 159)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (17, 4, 23)},
            'Denuncia de usuario': {'MULTICANAL C2C': (15, 5, 21), 'MULTICANAL CHAT': (38, 7, 49)},
            'Gestión de Publicación': {'MULTICANAL C2C': (34, 17, 53), 'MULTICANAL CHAT': (162, 24, 216)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (7, 4, 11), 'MULTICANAL CHAT': (91, 27, 125)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (11, 6, 18)},
            'PR - Propiedad intelectual': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (160, 29, 201)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (14, 6, 21), 'MULTICANAL CHAT': (189, 22, 233)},
            'Potenciar Ventas': {'MULTICANAL C2C': (23, 12, 41), 'MULTICANAL CHAT': (112, 27, 155)},
        },
        'M1': {
            'Afiliados ML': {'MULTICANAL C2C': (9, 3, 12), 'MULTICANAL CHAT': (77, 5, 89)},
            'Antes de publicar': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (3, 0, 3)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (11, 1, 13)},
            'Denuncia de usuario': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 2)},
            'Gestión de Publicación': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (10, 1, 11)},
            'PR - Artículos prohibidos': {'MULTICANAL CHAT': (8, 1, 12)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (4, 0, 4)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (8, 5, 14)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (7, 2, 10)},
            'Potenciar Ventas': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (3, 2, 5)},
        },
    },
}

# ════════════════════════════════════════════════════════════════
# SECTION 2H: P×OFICINA DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_OFFICE)
# ════════════════════════════════════════════════════════════════
p_o_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'AEC': (5, 0, 6), 'CTX': (1, 0, 1), 'KTA_BRASIL': (1, 0, 1)},
            'Emision de Nota Fiscal': {'AEC': (24, 4, 31), 'CTX': (4, 3, 7), 'KTA_BRASIL': (3, 7, 11)},
            'Facturación': {'AEC': (18, 2, 23), 'KTA_BRASIL': (1, 7, 8)},
        },
        'S1': {
            'Datos fiscales': {'AEC': (2, 0, 4), 'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (19, 1, 22), 'CTX': (2, 1, 3), 'KTA_BRASIL': (8, 3, 13)},
            'Facturación': {'AEC': (14, 2, 17), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 4, 8)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'AEC': (24, 4, 30), 'ATE': (188, 34, 248), 'CTX': (50, 12, 72), 'KTA_BRASIL': (140, 30, 188)},
            'Gestiones Operativas': {'AEC': (14, 0, 16), 'ATE': (48, 8, 64), 'CTX': (8, 2, 10), 'KTA_BRASIL': (24, 6, 32)},
            'Reputación ME': {'AEC': (196, 8, 214), 'ATE': (84, 6, 92), 'CTX': (26, 4, 32), 'KTA_BRASIL': (134, 8, 146)},
            'Reversa': {'AEC': (6, 2, 8), 'ATE': (26, 6, 34), 'KTA_BRASIL': (30, 10, 42), 'MELICIDADE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (8, 2, 10), 'ATE': (28, 10, 40), 'CTX': (4, 0, 4), 'KTA_BRASIL': (18, 0, 24)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'AEC': (26, 8, 38), 'ATE': (288, 34, 352), 'CTX': (54, 6, 62), 'KTA_BRASIL': (168, 24, 220), 'MELICIDADE': (2, 0, 2)},
            'Gestiones Operativas': {'AEC': (2, 0, 2), 'ATE': (54, 0, 56), 'CTX': (10, 4, 16), 'KTA_BRASIL': (16, 8, 26)},
            'Reputación ME': {'AEC': (184, 6, 200), 'ATE': (86, 8, 102), 'CTX': (12, 0, 14), 'KTA_BRASIL': (136, 12, 162)},
            'Reversa': {'AEC': (8, 6, 16), 'ATE': (38, 8, 48), 'KTA_BRASIL': (32, 4, 42)},
            'Viaje del paquete - Vendedor': {'AEC': (2, 0, 4), 'ATE': (22, 4, 28), 'CTX': (4, 0, 4), 'KTA_BRASIL': (22, 2, 26)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (14, 5, 25), 'ATE': (33, 10, 46), 'CTX': (5, 3, 10), 'KTA_BRASIL': (28, 11, 45), 'MELICIDADE': (2, 1, 3)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (30, 10, 43), 'ATE': (21, 6, 31), 'CTX': (5, 4, 9), 'KTA_BRASIL': (22, 6, 33), 'MELICIDADE': (3, 0, 3)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'AEC': (23, 7, 35), 'ATE': (240, 29, 290), 'CTX': (35, 8, 49), 'KTA_BRASIL': (190, 32, 251)},
            'Places Kangu': {'AEC': (2, 0, 2), 'ATE': (46, 4, 54), 'CTX': (7, 1, 9), 'KTA_BRASIL': (23, 4, 28)},
        },
        'S1': {
            'Drivers': {'AEC': (16, 7, 24), 'ATE': (228, 35, 287), 'CTX': (34, 8, 51), 'KTA_BRASIL': (197, 40, 262)},
            'Places Kangu': {'AEC': (4, 1, 6), 'ATE': (35, 3, 42), 'CTX': (5, 4, 11), 'KTA_BRASIL': (28, 1, 33)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'AEC': (1, 1, 2), 'ATE': (1, 0, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Reputación': {'AEC': (71, 7, 81), 'ATE': (33, 3, 39), 'CTX': (6, 2, 9), 'KTA_BRASIL': (61, 4, 72)},
        },
        'S1': {
            'Anulación de Venta': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 0, 1)},
            'Reputación': {'AEC': (70, 9, 85), 'ATE': (29, 4, 41), 'CTX': (8, 0, 8), 'KTA_BRASIL': (65, 6, 80)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'AEC': (146, 11, 173), 'CTX': (6, 3, 9), 'KTA_BRASIL': (13, 18, 32)},
            'Antes de publicar': {'AEC': (15, 1, 17), 'CTX': (4, 0, 5), 'KTA_BRASIL': (15, 0, 16)},
            'Calidad de foto': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'Denuncia de usuario': {'AEC': (5, 2, 8), 'CTX': (3, 0, 3), 'KTA_BRASIL': (0, 1, 1)},
            'Gestión de Publicación': {'AEC': (24, 3, 30), 'CTX': (6, 1, 7), 'KTA_BRASIL': (16, 4, 25)},
            'PR - Artículos prohibidos': {'AEC': (7, 5, 12), 'KTA_BRASIL': (15, 4, 22)},
            'PR - Datos Personales': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'PR - Propiedad intelectual': {'AEC': (22, 0, 22), 'KTA_BRASIL': (16, 4, 22)},
            'PR - Técnica prohibida': {'AEC': (16, 6, 22), 'KTA_BRASIL': (27, 1, 28)},
            'Potenciar Ventas': {'AEC': (8, 6, 15), 'CTX': (4, 2, 6), 'KTA_BRASIL': (17, 4, 24)},
        },
        'S1': {
            'Afiliados ML': {'AEC': (166, 14, 199), 'CTX': (3, 1, 5), 'KTA_BRASIL': (20, 20, 42)},
            'Antes de publicar': {'AEC': (6, 2, 8), 'CTX': (2, 0, 2), 'KTA_BRASIL': (18, 1, 22)},
            'Calidad de foto': {'AEC': (3, 1, 5), 'KTA_BRASIL': (9, 2, 12)},
            'Denuncia de usuario': {'AEC': (4, 2, 6), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Gestión de Publicación': {'AEC': (11, 3, 16), 'CTX': (3, 0, 3), 'KTA_BRASIL': (20, 7, 30)},
            'PR - Artículos prohibidos': {'AEC': (4, 3, 9), 'KTA_BRASIL': (18, 3, 23)},
            'PR - Datos Personales': {'AEC': (0, 1, 1), 'KTA_BRASIL': (5, 0, 6)},
            'PR - Propiedad intelectual': {'AEC': (10, 3, 13), 'KTA_BRASIL': (17, 7, 27)},
            'PR - Técnica prohibida': {'AEC': (21, 3, 24), 'ATE': (0, 0, 1), 'KTA_BRASIL': (18, 4, 25)},
            'Potenciar Ventas': {'AEC': (5, 6, 12), 'CTX': (2, 1, 4), 'KTA_BRASIL': (11, 1, 14), 'MELICIDADE': (1, 0, 1)},
        },
    },
}
p_o_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'AEC': (28, 3, 35), 'CTX': (4, 1, 5), 'KTA_BRASIL': (4, 3, 8)},
            'Emision de Nota Fiscal': {'AEC': (180, 23, 227), 'CTX': (29, 9, 39), 'KTA_BRASIL': (31, 29, 65)},
            'Facturación': {'AEC': (105, 18, 141), 'CTX': (9, 3, 12), 'KTA_BRASIL': (14, 22, 38)},
        },
        'M1': {
            'Datos fiscales': {'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (6, 0, 7), 'KTA_BRASIL': (1, 2, 3)},
            'Facturación': {'AEC': (1, 1, 2), 'KTA_BRASIL': (1, 2, 3)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'AEC': (146, 36, 196), 'ATE': (1214, 212, 1618), 'CTX': (302, 56, 386), 'KTA_BRASIL': (598, 116, 804), 'MELICIDADE': (6, 0, 6)},
            'Gestiones Operativas': {'AEC': (34, 8, 46), 'ATE': (244, 32, 306), 'CTX': (54, 12, 74), 'KTA_BRASIL': (80, 22, 114), 'MELICIDADE': (2, 0, 2)},
            'Reputación ME': {'AEC': (996, 28, 1084), 'ATE': (426, 30, 490), 'CTX': (134, 10, 160), 'KTA_BRASIL': (584, 64, 686), 'MELICIDADE': (2, 2, 4)},
            'Reversa': {'AEC': (34, 10, 46), 'ATE': (178, 30, 222), 'KTA_BRASIL': (152, 32, 212), 'MELICIDADE': (2, 0, 2)},
            'Suspensiones ME': {'ATE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (24, 4, 32), 'ATE': (120, 26, 170), 'CTX': (24, 0, 24), 'KTA_BRASIL': (60, 10, 86)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'AEC': (4, 2, 6), 'ATE': (86, 6, 96), 'KTA_BRASIL': (58, 2, 64)},
            'Gestiones Operativas': {'ATE': (16, 0, 16), 'KTA_BRASIL': (4, 0, 4)},
            'Reputación ME': {'AEC': (18, 2, 24), 'ATE': (26, 0, 26), 'KTA_BRASIL': (26, 4, 32)},
            'Reversa': {'ATE': (2, 6, 8), 'KTA_BRASIL': (6, 2, 10)},
            'Viaje del paquete - Vendedor': {'ATE': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (93, 35, 144), 'ATE': (166, 37, 225), 'CTX': (28, 13, 44), 'KTA_BRASIL': (79, 28, 118), 'MELICIDADE': (28, 5, 37)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (4, 0, 5), 'ATE': (2, 1, 4), 'KTA_BRASIL': (4, 0, 7)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'AEC': (74, 23, 110), 'ATE': (987, 137, 1223), 'CTX': (180, 36, 241), 'KTA_BRASIL': (577, 105, 763)},
            'Places Kangu': {'AEC': (21, 3, 25), 'ATE': (215, 27, 262), 'CTX': (64, 9, 81), 'KTA_BRASIL': (110, 19, 140)},
        },
        'M1': {
            'Drivers': {'AEC': (8, 1, 10), 'ATE': (93, 8, 112), 'KTA_BRASIL': (70, 17, 100)},
            'Places Kangu': {'ATE': (7, 0, 8), 'KTA_BRASIL': (7, 0, 8)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'AEC': (16, 2, 18), 'ATE': (6, 1, 7), 'CTX': (3, 0, 4), 'KTA_BRASIL': (5, 2, 7)},
            'Reputación': {'AEC': (310, 46, 382), 'ATE': (177, 17, 220), 'CTX': (70, 12, 90), 'KTA_BRASIL': (265, 36, 326), 'MELICIDADE': (5, 0, 5)},
        },
        'M1': {
            'Reputación': {'AEC': (8, 1, 9), 'ATE': (8, 1, 10), 'KTA_BRASIL': (11, 0, 13)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'AEC': (871, 87, 1044), 'CTX': (30, 11, 44), 'KTA_BRASIL': (57, 68, 138), 'MELICIDADE': (1, 0, 1)},
            'Antes de publicar': {'AEC': (70, 5, 84), 'CTX': (17, 2, 21), 'KTA_BRASIL': (75, 6, 89)},
            'Calidad de foto': {'AEC': (3, 2, 7), 'KTA_BRASIL': (15, 3, 18)},
            'Denuncia de usuario': {'AEC': (38, 7, 49), 'CTX': (7, 2, 10), 'KTA_BRASIL': (8, 3, 11)},
            'Gestión de Publicación': {'AEC': (62, 18, 88), 'CTX': (23, 8, 31), 'KTA_BRASIL': (111, 15, 150)},
            'PR - Artículos prohibidos': {'AEC': (31, 15, 48), 'CTX': (1, 0, 1), 'KTA_BRASIL': (66, 16, 87)},
            'PR - Datos Personales': {'AEC': (3, 1, 4), 'KTA_BRASIL': (8, 5, 14)},
            'PR - Propiedad intelectual': {'AEC': (65, 10, 79), 'KTA_BRASIL': (99, 21, 128)},
            'PR - Técnica prohibida': {'AEC': (95, 15, 116), 'ATE': (0, 0, 1), 'KTA_BRASIL': (105, 13, 134), 'MELICIDADE': (3, 0, 3)},
            'Potenciar Ventas': {'AEC': (44, 17, 66), 'CTX': (16, 6, 27), 'KTA_BRASIL': (74, 16, 102), 'MELICIDADE': (1, 0, 1)},
        },
        'M1': {
            'Afiliados ML': {'AEC': (77, 5, 89), 'KTA_BRASIL': (9, 3, 12)},
            'Antes de publicar': {'AEC': (0, 1, 1), 'KTA_BRASIL': (3, 0, 3)},
            'Calidad de foto': {'AEC': (3, 0, 4), 'KTA_BRASIL': (8, 1, 10)},
            'Denuncia de usuario': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 1, 2)},
            'Gestión de Publicación': {'AEC': (6, 1, 7), 'KTA_BRASIL': (4, 1, 5)},
            'PR - Artículos prohibidos': {'AEC': (1, 0, 2), 'KTA_BRASIL': (7, 1, 10)},
            'PR - Datos Personales': {'KTA_BRASIL': (4, 0, 4)},
            'PR - Propiedad intelectual': {'AEC': (3, 1, 4), 'KTA_BRASIL': (5, 4, 10)},
            'PR - Técnica prohibida': {'AEC': (5, 0, 5), 'KTA_BRASIL': (4, 2, 7)},
            'Potenciar Ventas': {'AEC': (2, 3, 5), 'KTA_BRASIL': (2, 1, 3)},
        },
    },
}


# ════════════════════════════════════════════════════════════════
# SECTION 2G: P×CANAL DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_TEAM_CHANNEL)
# ════════════════════════════════════════════════════════════════
p_c_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (5, 0, 6)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (7, 10, 18), 'MULTICANAL CHAT': (24, 4, 31)},
            'Facturación': {'MULTICANAL C2C': (1, 7, 8), 'MULTICANAL CHAT': (18, 2, 23)},
        },
        'S1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 4)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (10, 4, 16), 'MULTICANAL CHAT': (19, 1, 22)},
            'Facturación': {'MULTICANAL C2C': (4, 5, 9), 'MULTICANAL CHAT': (14, 2, 17)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (70, 12, 92), 'MULTICANAL CHAT': (332, 68, 446)},
            'Gestiones Operativas': {'MULTICANAL C2C': (26, 4, 32), 'MULTICANAL CHAT': (68, 12, 90)},
            'Reputación ME': {'MULTICANAL C2C': (64, 8, 72), 'MULTICANAL CHAT': (376, 18, 412)},
            'Reversa': {'MULTICANAL C2C': (12, 4, 16), 'MULTICANAL CHAT': (52, 14, 70)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (48, 10, 66)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (92, 22, 126), 'MULTICANAL CHAT': (446, 50, 548)},
            'Gestiones Operativas': {'MULTICANAL C2C': (16, 0, 16), 'MULTICANAL CHAT': (66, 12, 84)},
            'Reputación ME': {'MULTICANAL C2C': (66, 12, 82), 'MULTICANAL CHAT': (352, 14, 396)},
            'Reversa': {'MULTICANAL C2C': (12, 10, 24), 'MULTICANAL CHAT': (66, 8, 82)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 0, 14), 'MULTICANAL CHAT': (40, 6, 48)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (30, 18, 50), 'MULTICANAL CHAT': (52, 12, 79)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (22, 14, 41), 'MULTICANAL CHAT': (59, 12, 78)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'MULTICANAL C2C': (60, 19, 93), 'MULTICANAL CHAT': (428, 57, 532)},
            'Places Kangu': {'MULTICANAL C2C': (7, 1, 9), 'MULTICANAL CHAT': (71, 8, 84)},
        },
        'S1': {
            'Drivers': {'MULTICANAL C2C': (55, 21, 81), 'MULTICANAL CHAT': (420, 69, 543)},
            'Places Kangu': {'MULTICANAL C2C': (13, 3, 19), 'MULTICANAL CHAT': (59, 6, 73)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'MULTICANAL C2C': (2, 1, 3), 'MULTICANAL CHAT': (4, 1, 5)},
            'Reputación': {'MULTICANAL C2C': (30, 8, 40), 'MULTICANAL CHAT': (141, 8, 161)},
        },
        'S1': {
            'Anulación de Venta': {'MULTICANAL CHAT': (3, 0, 3)},
            'Reputación': {'MULTICANAL C2C': (41, 4, 48), 'MULTICANAL CHAT': (131, 15, 166)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'MULTICANAL C2C': (19, 21, 41), 'MULTICANAL CHAT': (146, 11, 173)},
            'Antes de publicar': {'MULTICANAL C2C': (6, 1, 8), 'MULTICANAL CHAT': (28, 0, 30)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 0, 1), 'MULTICANAL CHAT': (5, 0, 5)},
            'Denuncia de usuario': {'MULTICANAL C2C': (3, 1, 4), 'MULTICANAL CHAT': (5, 2, 8)},
            'Gestión de Publicación': {'MULTICANAL C2C': (14, 3, 17), 'MULTICANAL CHAT': (32, 5, 45)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (21, 8, 32)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (6, 0, 6)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (38, 4, 44)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (5, 2, 7), 'MULTICANAL CHAT': (38, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 9), 'MULTICANAL CHAT': (24, 8, 36)},
        },
        'S1': {
            'Afiliados ML': {'MULTICANAL C2C': (23, 21, 47), 'MULTICANAL CHAT': (166, 14, 199)},
            'Antes de publicar': {'MULTICANAL C2C': (5, 1, 6), 'MULTICANAL CHAT': (21, 2, 26)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 1, 2), 'MULTICANAL CHAT': (12, 2, 15)},
            'Denuncia de usuario': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (4, 2, 6)},
            'Gestión de Publicación': {'MULTICANAL C2C': (5, 3, 9), 'MULTICANAL CHAT': (29, 7, 40)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (22, 5, 31)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (5, 1, 7)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (27, 10, 40)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (4, 2, 7), 'MULTICANAL CHAT': (35, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 11), 'MULTICANAL CHAT': (14, 4, 20)},
        },
    },
}
p_c_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'MULTICANAL C2C': (8, 4, 13), 'MULTICANAL CHAT': (28, 3, 35)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (60, 37, 103), 'MULTICANAL CHAT': (180, 24, 228)},
            'Facturación': {'MULTICANAL C2C': (23, 25, 50), 'MULTICANAL CHAT': (105, 18, 141)},
        },
        'M1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (6, 0, 7)},
            'Facturación': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (1, 1, 2)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (370, 110, 532), 'MULTICANAL CHAT': (1894, 308, 2472)},
            'Gestiones Operativas': {'MULTICANAL C2C': (98, 22, 126), 'MULTICANAL CHAT': (312, 52, 412)},
            'Reputación ME': {'MULTICANAL C2C': (356, 46, 422), 'MULTICANAL CHAT': (1784, 88, 2000)},
            'Reversa': {'MULTICANAL C2C': (70, 18, 92), 'MULTICANAL CHAT': (294, 54, 388)},
            'Suspensiones ME': {'MULTICANAL C2C': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (44, 8, 68), 'MULTICANAL CHAT': (184, 32, 244)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (30, 6, 36), 'MULTICANAL CHAT': (118, 4, 130)},
            'Gestiones Operativas': {'MULTICANAL CHAT': (20, 0, 20)},
            'Reputación ME': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (60, 4, 70)},
            'Reversa': {'MULTICANAL C2C': (0, 4, 4), 'MULTICANAL CHAT': (8, 4, 14)},
            'Viaje del paquete - Vendedor': {'MULTICANAL CHAT': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (112, 51, 172), 'MULTICANAL CHAT': (280, 66, 393)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (1, 1, 4), 'MULTICANAL CHAT': (9, 0, 12)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'MULTICANAL C2C': (222, 65, 328), 'MULTICANAL CHAT': (1592, 236, 2004)},
            'Places Kangu': {'MULTICANAL C2C': (55, 13, 72), 'MULTICANAL CHAT': (355, 45, 436)},
        },
        'M1': {
            'Drivers': {'MULTICANAL C2C': (23, 4, 29), 'MULTICANAL CHAT': (148, 22, 193)},
            'Places Kangu': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (14, 0, 15)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'MULTICANAL C2C': (6, 2, 9), 'MULTICANAL CHAT': (24, 3, 27)},
            'Reputación': {'MULTICANAL C2C': (193, 33, 242), 'MULTICANAL CHAT': (633, 78, 780)},
        },
        'M1': {
            'Reputación': {'MULTICANAL C2C': (3, 1, 5), 'MULTICANAL CHAT': (24, 1, 27)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'MULTICANAL C2C': (87, 79, 182), 'MULTICANAL CHAT': (872, 87, 1045)},
            'Antes de publicar': {'MULTICANAL C2C': (28, 4, 35), 'MULTICANAL CHAT': (134, 9, 159)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (17, 4, 23)},
            'Denuncia de usuario': {'MULTICANAL C2C': (15, 5, 21), 'MULTICANAL CHAT': (38, 7, 49)},
            'Gestión de Publicación': {'MULTICANAL C2C': (34, 17, 53), 'MULTICANAL CHAT': (162, 24, 216)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (7, 4, 11), 'MULTICANAL CHAT': (91, 27, 125)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (11, 6, 18)},
            'PR - Propiedad intelectual': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (160, 29, 201)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (14, 6, 21), 'MULTICANAL CHAT': (189, 22, 233)},
            'Potenciar Ventas': {'MULTICANAL C2C': (23, 12, 41), 'MULTICANAL CHAT': (112, 27, 155)},
        },
        'M1': {
            'Afiliados ML': {'MULTICANAL C2C': (9, 3, 12), 'MULTICANAL CHAT': (77, 5, 89)},
            'Antes de publicar': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (3, 0, 3)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (11, 1, 13)},
            'Denuncia de usuario': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 2)},
            'Gestión de Publicación': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (10, 1, 11)},
            'PR - Artículos prohibidos': {'MULTICANAL CHAT': (8, 1, 12)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (4, 0, 4)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (8, 5, 14)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (7, 2, 10)},
            'Potenciar Ventas': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (3, 2, 5)},
        },
    },
}

# ════════════════════════════════════════════════════════════════
# SECTION 2H: P×OFICINA DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_OFFICE)
# ════════════════════════════════════════════════════════════════
p_o_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'AEC': (5, 0, 6), 'CTX': (1, 0, 1), 'KTA_BRASIL': (1, 0, 1)},
            'Emision de Nota Fiscal': {'AEC': (24, 4, 31), 'CTX': (4, 3, 7), 'KTA_BRASIL': (3, 7, 11)},
            'Facturación': {'AEC': (18, 2, 23), 'KTA_BRASIL': (1, 7, 8)},
        },
        'S1': {
            'Datos fiscales': {'AEC': (2, 0, 4), 'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (19, 1, 22), 'CTX': (2, 1, 3), 'KTA_BRASIL': (8, 3, 13)},
            'Facturación': {'AEC': (14, 2, 17), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 4, 8)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'AEC': (24, 4, 30), 'ATE': (188, 34, 248), 'CTX': (50, 12, 72), 'KTA_BRASIL': (140, 30, 188)},
            'Gestiones Operativas': {'AEC': (14, 0, 16), 'ATE': (48, 8, 64), 'CTX': (8, 2, 10), 'KTA_BRASIL': (24, 6, 32)},
            'Reputación ME': {'AEC': (196, 8, 214), 'ATE': (84, 6, 92), 'CTX': (26, 4, 32), 'KTA_BRASIL': (134, 8, 146)},
            'Reversa': {'AEC': (6, 2, 8), 'ATE': (26, 6, 34), 'KTA_BRASIL': (30, 10, 42), 'MELICIDADE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (8, 2, 10), 'ATE': (28, 10, 40), 'CTX': (4, 0, 4), 'KTA_BRASIL': (18, 0, 24)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'AEC': (26, 8, 38), 'ATE': (288, 34, 352), 'CTX': (54, 6, 62), 'KTA_BRASIL': (168, 24, 220), 'MELICIDADE': (2, 0, 2)},
            'Gestiones Operativas': {'AEC': (2, 0, 2), 'ATE': (54, 0, 56), 'CTX': (10, 4, 16), 'KTA_BRASIL': (16, 8, 26)},
            'Reputación ME': {'AEC': (184, 6, 200), 'ATE': (86, 8, 102), 'CTX': (12, 0, 14), 'KTA_BRASIL': (136, 12, 162)},
            'Reversa': {'AEC': (8, 6, 16), 'ATE': (38, 8, 48), 'KTA_BRASIL': (32, 4, 42)},
            'Viaje del paquete - Vendedor': {'AEC': (2, 0, 4), 'ATE': (22, 4, 28), 'CTX': (4, 0, 4), 'KTA_BRASIL': (22, 2, 26)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (14, 5, 25), 'ATE': (33, 10, 46), 'CTX': (5, 3, 10), 'KTA_BRASIL': (28, 11, 45), 'MELICIDADE': (2, 1, 3)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (30, 10, 43), 'ATE': (21, 6, 31), 'CTX': (5, 4, 9), 'KTA_BRASIL': (22, 6, 33), 'MELICIDADE': (3, 0, 3)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'AEC': (23, 7, 35), 'ATE': (240, 29, 290), 'CTX': (35, 8, 49), 'KTA_BRASIL': (190, 32, 251)},
            'Places Kangu': {'AEC': (2, 0, 2), 'ATE': (46, 4, 54), 'CTX': (7, 1, 9), 'KTA_BRASIL': (23, 4, 28)},
        },
        'S1': {
            'Drivers': {'AEC': (16, 7, 24), 'ATE': (228, 35, 287), 'CTX': (34, 8, 51), 'KTA_BRASIL': (197, 40, 262)},
            'Places Kangu': {'AEC': (4, 1, 6), 'ATE': (35, 3, 42), 'CTX': (5, 4, 11), 'KTA_BRASIL': (28, 1, 33)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'AEC': (1, 1, 2), 'ATE': (1, 0, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Reputación': {'AEC': (71, 7, 81), 'ATE': (33, 3, 39), 'CTX': (6, 2, 9), 'KTA_BRASIL': (61, 4, 72)},
        },
        'S1': {
            'Anulación de Venta': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 0, 1)},
            'Reputación': {'AEC': (70, 9, 85), 'ATE': (29, 4, 41), 'CTX': (8, 0, 8), 'KTA_BRASIL': (65, 6, 80)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'AEC': (146, 11, 173), 'CTX': (6, 3, 9), 'KTA_BRASIL': (13, 18, 32)},
            'Antes de publicar': {'AEC': (15, 1, 17), 'CTX': (4, 0, 5), 'KTA_BRASIL': (15, 0, 16)},
            'Calidad de foto': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'Denuncia de usuario': {'AEC': (5, 2, 8), 'CTX': (3, 0, 3), 'KTA_BRASIL': (0, 1, 1)},
            'Gestión de Publicación': {'AEC': (24, 3, 30), 'CTX': (6, 1, 7), 'KTA_BRASIL': (16, 4, 25)},
            'PR - Artículos prohibidos': {'AEC': (7, 5, 12), 'KTA_BRASIL': (15, 4, 22)},
            'PR - Datos Personales': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'PR - Propiedad intelectual': {'AEC': (22, 0, 22), 'KTA_BRASIL': (16, 4, 22)},
            'PR - Técnica prohibida': {'AEC': (16, 6, 22), 'KTA_BRASIL': (27, 1, 28)},
            'Potenciar Ventas': {'AEC': (8, 6, 15), 'CTX': (4, 2, 6), 'KTA_BRASIL': (17, 4, 24)},
        },
        'S1': {
            'Afiliados ML': {'AEC': (166, 14, 199), 'CTX': (3, 1, 5), 'KTA_BRASIL': (20, 20, 42)},
            'Antes de publicar': {'AEC': (6, 2, 8), 'CTX': (2, 0, 2), 'KTA_BRASIL': (18, 1, 22)},
            'Calidad de foto': {'AEC': (3, 1, 5), 'KTA_BRASIL': (9, 2, 12)},
            'Denuncia de usuario': {'AEC': (4, 2, 6), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Gestión de Publicación': {'AEC': (11, 3, 16), 'CTX': (3, 0, 3), 'KTA_BRASIL': (20, 7, 30)},
            'PR - Artículos prohibidos': {'AEC': (4, 3, 9), 'KTA_BRASIL': (18, 3, 23)},
            'PR - Datos Personales': {'AEC': (0, 1, 1), 'KTA_BRASIL': (5, 0, 6)},
            'PR - Propiedad intelectual': {'AEC': (10, 3, 13), 'KTA_BRASIL': (17, 7, 27)},
            'PR - Técnica prohibida': {'AEC': (21, 3, 24), 'ATE': (0, 0, 1), 'KTA_BRASIL': (18, 4, 25)},
            'Potenciar Ventas': {'AEC': (5, 6, 12), 'CTX': (2, 1, 4), 'KTA_BRASIL': (11, 1, 14), 'MELICIDADE': (1, 0, 1)},
        },
    },
}
p_o_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'AEC': (28, 3, 35), 'CTX': (4, 1, 5), 'KTA_BRASIL': (4, 3, 8)},
            'Emision de Nota Fiscal': {'AEC': (180, 23, 227), 'CTX': (29, 9, 39), 'KTA_BRASIL': (31, 29, 65)},
            'Facturación': {'AEC': (105, 18, 141), 'CTX': (9, 3, 12), 'KTA_BRASIL': (14, 22, 38)},
        },
        'M1': {
            'Datos fiscales': {'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (6, 0, 7), 'KTA_BRASIL': (1, 2, 3)},
            'Facturación': {'AEC': (1, 1, 2), 'KTA_BRASIL': (1, 2, 3)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'AEC': (146, 36, 196), 'ATE': (1214, 212, 1618), 'CTX': (302, 56, 386), 'KTA_BRASIL': (598, 116, 804), 'MELICIDADE': (6, 0, 6)},
            'Gestiones Operativas': {'AEC': (34, 8, 46), 'ATE': (244, 32, 306), 'CTX': (54, 12, 74), 'KTA_BRASIL': (80, 22, 114), 'MELICIDADE': (2, 0, 2)},
            'Reputación ME': {'AEC': (996, 28, 1084), 'ATE': (426, 30, 490), 'CTX': (134, 10, 160), 'KTA_BRASIL': (584, 64, 686), 'MELICIDADE': (2, 2, 4)},
            'Reversa': {'AEC': (34, 10, 46), 'ATE': (178, 30, 222), 'KTA_BRASIL': (152, 32, 212), 'MELICIDADE': (2, 0, 2)},
            'Suspensiones ME': {'ATE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (24, 4, 32), 'ATE': (120, 26, 170), 'CTX': (24, 0, 24), 'KTA_BRASIL': (60, 10, 86)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'AEC': (4, 2, 6), 'ATE': (86, 6, 96), 'KTA_BRASIL': (58, 2, 64)},
            'Gestiones Operativas': {'ATE': (16, 0, 16), 'KTA_BRASIL': (4, 0, 4)},
            'Reputación ME': {'AEC': (18, 2, 24), 'ATE': (26, 0, 26), 'KTA_BRASIL': (26, 4, 32)},
            'Reversa': {'ATE': (2, 6, 8), 'KTA_BRASIL': (6, 2, 10)},
            'Viaje del paquete - Vendedor': {'ATE': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (93, 35, 144), 'ATE': (166, 37, 225), 'CTX': (28, 13, 44), 'KTA_BRASIL': (79, 28, 118), 'MELICIDADE': (28, 5, 37)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (4, 0, 5), 'ATE': (2, 1, 4), 'KTA_BRASIL': (4, 0, 7)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'AEC': (74, 23, 110), 'ATE': (987, 137, 1223), 'CTX': (180, 36, 241), 'KTA_BRASIL': (577, 105, 763)},
            'Places Kangu': {'AEC': (21, 3, 25), 'ATE': (215, 27, 262), 'CTX': (64, 9, 81), 'KTA_BRASIL': (110, 19, 140)},
        },
        'M1': {
            'Drivers': {'AEC': (8, 1, 10), 'ATE': (93, 8, 112), 'KTA_BRASIL': (70, 17, 100)},
            'Places Kangu': {'ATE': (7, 0, 8), 'KTA_BRASIL': (7, 0, 8)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'AEC': (16, 2, 18), 'ATE': (6, 1, 7), 'CTX': (3, 0, 4), 'KTA_BRASIL': (5, 2, 7)},
            'Reputación': {'AEC': (310, 46, 382), 'ATE': (177, 17, 220), 'CTX': (70, 12, 90), 'KTA_BRASIL': (265, 36, 326), 'MELICIDADE': (5, 0, 5)},
        },
        'M1': {
            'Reputación': {'AEC': (8, 1, 9), 'ATE': (8, 1, 10), 'KTA_BRASIL': (11, 0, 13)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'AEC': (871, 87, 1044), 'CTX': (30, 11, 44), 'KTA_BRASIL': (57, 68, 138), 'MELICIDADE': (1, 0, 1)},
            'Antes de publicar': {'AEC': (70, 5, 84), 'CTX': (17, 2, 21), 'KTA_BRASIL': (75, 6, 89)},
            'Calidad de foto': {'AEC': (3, 2, 7), 'KTA_BRASIL': (15, 3, 18)},
            'Denuncia de usuario': {'AEC': (38, 7, 49), 'CTX': (7, 2, 10), 'KTA_BRASIL': (8, 3, 11)},
            'Gestión de Publicación': {'AEC': (62, 18, 88), 'CTX': (23, 8, 31), 'KTA_BRASIL': (111, 15, 150)},
            'PR - Artículos prohibidos': {'AEC': (31, 15, 48), 'CTX': (1, 0, 1), 'KTA_BRASIL': (66, 16, 87)},
            'PR - Datos Personales': {'AEC': (3, 1, 4), 'KTA_BRASIL': (8, 5, 14)},
            'PR - Propiedad intelectual': {'AEC': (65, 10, 79), 'KTA_BRASIL': (99, 21, 128)},
            'PR - Técnica prohibida': {'AEC': (95, 15, 116), 'ATE': (0, 0, 1), 'KTA_BRASIL': (105, 13, 134), 'MELICIDADE': (3, 0, 3)},
            'Potenciar Ventas': {'AEC': (44, 17, 66), 'CTX': (16, 6, 27), 'KTA_BRASIL': (74, 16, 102), 'MELICIDADE': (1, 0, 1)},
        },
        'M1': {
            'Afiliados ML': {'AEC': (77, 5, 89), 'KTA_BRASIL': (9, 3, 12)},
            'Antes de publicar': {'AEC': (0, 1, 1), 'KTA_BRASIL': (3, 0, 3)},
            'Calidad de foto': {'AEC': (3, 0, 4), 'KTA_BRASIL': (8, 1, 10)},
            'Denuncia de usuario': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 1, 2)},
            'Gestión de Publicación': {'AEC': (6, 1, 7), 'KTA_BRASIL': (4, 1, 5)},
            'PR - Artículos prohibidos': {'AEC': (1, 0, 2), 'KTA_BRASIL': (7, 1, 10)},
            'PR - Datos Personales': {'KTA_BRASIL': (4, 0, 4)},
            'PR - Propiedad intelectual': {'AEC': (3, 1, 4), 'KTA_BRASIL': (5, 4, 10)},
            'PR - Técnica prohibida': {'AEC': (5, 0, 5), 'KTA_BRASIL': (4, 2, 7)},
            'Potenciar Ventas': {'AEC': (2, 3, 5), 'KTA_BRASIL': (2, 1, 3)},
        },
    },
}


# ════════════════════════════════════════════════════════════════
# SECTION 2G: P×CANAL DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_TEAM_CHANNEL)
# ════════════════════════════════════════════════════════════════
p_c_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (5, 0, 6)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (7, 10, 18), 'MULTICANAL CHAT': (24, 4, 31)},
            'Facturación': {'MULTICANAL C2C': (1, 7, 8), 'MULTICANAL CHAT': (18, 2, 23)},
        },
        'S1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 4)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (10, 4, 16), 'MULTICANAL CHAT': (19, 1, 22)},
            'Facturación': {'MULTICANAL C2C': (4, 5, 9), 'MULTICANAL CHAT': (14, 2, 17)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (70, 12, 92), 'MULTICANAL CHAT': (332, 68, 446)},
            'Gestiones Operativas': {'MULTICANAL C2C': (26, 4, 32), 'MULTICANAL CHAT': (68, 12, 90)},
            'Reputación ME': {'MULTICANAL C2C': (64, 8, 72), 'MULTICANAL CHAT': (376, 18, 412)},
            'Reversa': {'MULTICANAL C2C': (12, 4, 16), 'MULTICANAL CHAT': (52, 14, 70)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (48, 10, 66)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (92, 22, 126), 'MULTICANAL CHAT': (446, 50, 548)},
            'Gestiones Operativas': {'MULTICANAL C2C': (16, 0, 16), 'MULTICANAL CHAT': (66, 12, 84)},
            'Reputación ME': {'MULTICANAL C2C': (66, 12, 82), 'MULTICANAL CHAT': (352, 14, 396)},
            'Reversa': {'MULTICANAL C2C': (12, 10, 24), 'MULTICANAL CHAT': (66, 8, 82)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (10, 0, 14), 'MULTICANAL CHAT': (40, 6, 48)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (30, 18, 50), 'MULTICANAL CHAT': (52, 12, 79)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (22, 14, 41), 'MULTICANAL CHAT': (59, 12, 78)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'MULTICANAL C2C': (60, 19, 93), 'MULTICANAL CHAT': (428, 57, 532)},
            'Places Kangu': {'MULTICANAL C2C': (7, 1, 9), 'MULTICANAL CHAT': (71, 8, 84)},
        },
        'S1': {
            'Drivers': {'MULTICANAL C2C': (55, 21, 81), 'MULTICANAL CHAT': (420, 69, 543)},
            'Places Kangu': {'MULTICANAL C2C': (13, 3, 19), 'MULTICANAL CHAT': (59, 6, 73)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'MULTICANAL C2C': (2, 1, 3), 'MULTICANAL CHAT': (4, 1, 5)},
            'Reputación': {'MULTICANAL C2C': (30, 8, 40), 'MULTICANAL CHAT': (141, 8, 161)},
        },
        'S1': {
            'Anulación de Venta': {'MULTICANAL CHAT': (3, 0, 3)},
            'Reputación': {'MULTICANAL C2C': (41, 4, 48), 'MULTICANAL CHAT': (131, 15, 166)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'MULTICANAL C2C': (19, 21, 41), 'MULTICANAL CHAT': (146, 11, 173)},
            'Antes de publicar': {'MULTICANAL C2C': (6, 1, 8), 'MULTICANAL CHAT': (28, 0, 30)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 0, 1), 'MULTICANAL CHAT': (5, 0, 5)},
            'Denuncia de usuario': {'MULTICANAL C2C': (3, 1, 4), 'MULTICANAL CHAT': (5, 2, 8)},
            'Gestión de Publicación': {'MULTICANAL C2C': (14, 3, 17), 'MULTICANAL CHAT': (32, 5, 45)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (21, 8, 32)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (6, 0, 6)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (38, 4, 44)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (5, 2, 7), 'MULTICANAL CHAT': (38, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 9), 'MULTICANAL CHAT': (24, 8, 36)},
        },
        'S1': {
            'Afiliados ML': {'MULTICANAL C2C': (23, 21, 47), 'MULTICANAL CHAT': (166, 14, 199)},
            'Antes de publicar': {'MULTICANAL C2C': (5, 1, 6), 'MULTICANAL CHAT': (21, 2, 26)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 1, 2), 'MULTICANAL CHAT': (12, 2, 15)},
            'Denuncia de usuario': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (4, 2, 6)},
            'Gestión de Publicación': {'MULTICANAL C2C': (5, 3, 9), 'MULTICANAL CHAT': (29, 7, 40)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (22, 5, 31)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (5, 1, 7)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (27, 10, 40)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (4, 2, 7), 'MULTICANAL CHAT': (35, 5, 43)},
            'Potenciar Ventas': {'MULTICANAL C2C': (5, 4, 11), 'MULTICANAL CHAT': (14, 4, 20)},
        },
    },
}
p_c_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'MULTICANAL C2C': (8, 4, 13), 'MULTICANAL CHAT': (28, 3, 35)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (60, 37, 103), 'MULTICANAL CHAT': (180, 24, 228)},
            'Facturación': {'MULTICANAL C2C': (23, 25, 50), 'MULTICANAL CHAT': (105, 18, 141)},
        },
        'M1': {
            'Datos fiscales': {'MULTICANAL C2C': (1, 1, 2)},
            'Emision de Nota Fiscal': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (6, 0, 7)},
            'Facturación': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (1, 1, 2)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (370, 110, 532), 'MULTICANAL CHAT': (1894, 308, 2472)},
            'Gestiones Operativas': {'MULTICANAL C2C': (98, 22, 126), 'MULTICANAL CHAT': (312, 52, 412)},
            'Reputación ME': {'MULTICANAL C2C': (356, 46, 422), 'MULTICANAL CHAT': (1784, 88, 2000)},
            'Reversa': {'MULTICANAL C2C': (70, 18, 92), 'MULTICANAL CHAT': (294, 54, 388)},
            'Suspensiones ME': {'MULTICANAL C2C': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'MULTICANAL C2C': (44, 8, 68), 'MULTICANAL CHAT': (184, 32, 244)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'MULTICANAL C2C': (30, 6, 36), 'MULTICANAL CHAT': (118, 4, 130)},
            'Gestiones Operativas': {'MULTICANAL CHAT': (20, 0, 20)},
            'Reputación ME': {'MULTICANAL C2C': (10, 2, 12), 'MULTICANAL CHAT': (60, 4, 70)},
            'Reversa': {'MULTICANAL C2C': (0, 4, 4), 'MULTICANAL CHAT': (8, 4, 14)},
            'Viaje del paquete - Vendedor': {'MULTICANAL CHAT': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (112, 51, 172), 'MULTICANAL CHAT': (280, 66, 393)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'MULTICANAL C2C': (1, 1, 4), 'MULTICANAL CHAT': (9, 0, 12)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'MULTICANAL C2C': (222, 65, 328), 'MULTICANAL CHAT': (1592, 236, 2004)},
            'Places Kangu': {'MULTICANAL C2C': (55, 13, 72), 'MULTICANAL CHAT': (355, 45, 436)},
        },
        'M1': {
            'Drivers': {'MULTICANAL C2C': (23, 4, 29), 'MULTICANAL CHAT': (148, 22, 193)},
            'Places Kangu': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (14, 0, 15)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'MULTICANAL C2C': (6, 2, 9), 'MULTICANAL CHAT': (24, 3, 27)},
            'Reputación': {'MULTICANAL C2C': (193, 33, 242), 'MULTICANAL CHAT': (633, 78, 780)},
        },
        'M1': {
            'Reputación': {'MULTICANAL C2C': (3, 1, 5), 'MULTICANAL CHAT': (24, 1, 27)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'MULTICANAL C2C': (87, 79, 182), 'MULTICANAL CHAT': (872, 87, 1045)},
            'Antes de publicar': {'MULTICANAL C2C': (28, 4, 35), 'MULTICANAL CHAT': (134, 9, 159)},
            'Calidad de foto': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (17, 4, 23)},
            'Denuncia de usuario': {'MULTICANAL C2C': (15, 5, 21), 'MULTICANAL CHAT': (38, 7, 49)},
            'Gestión de Publicación': {'MULTICANAL C2C': (34, 17, 53), 'MULTICANAL CHAT': (162, 24, 216)},
            'PR - Artículos prohibidos': {'MULTICANAL C2C': (7, 4, 11), 'MULTICANAL CHAT': (91, 27, 125)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (11, 6, 18)},
            'PR - Propiedad intelectual': {'MULTICANAL C2C': (4, 2, 6), 'MULTICANAL CHAT': (160, 29, 201)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (14, 6, 21), 'MULTICANAL CHAT': (189, 22, 233)},
            'Potenciar Ventas': {'MULTICANAL C2C': (23, 12, 41), 'MULTICANAL CHAT': (112, 27, 155)},
        },
        'M1': {
            'Afiliados ML': {'MULTICANAL C2C': (9, 3, 12), 'MULTICANAL CHAT': (77, 5, 89)},
            'Antes de publicar': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (3, 0, 3)},
            'Calidad de foto': {'MULTICANAL C2C': (0, 0, 1), 'MULTICANAL CHAT': (11, 1, 13)},
            'Denuncia de usuario': {'MULTICANAL C2C': (1, 1, 2), 'MULTICANAL CHAT': (2, 0, 2)},
            'Gestión de Publicación': {'MULTICANAL C2C': (0, 1, 1), 'MULTICANAL CHAT': (10, 1, 11)},
            'PR - Artículos prohibidos': {'MULTICANAL CHAT': (8, 1, 12)},
            'PR - Datos Personales': {'MULTICANAL CHAT': (4, 0, 4)},
            'PR - Propiedad intelectual': {'MULTICANAL CHAT': (8, 5, 14)},
            'PR - Técnica prohibida': {'MULTICANAL C2C': (2, 0, 2), 'MULTICANAL CHAT': (7, 2, 10)},
            'Potenciar Ventas': {'MULTICANAL C2C': (1, 2, 3), 'MULTICANAL CHAT': (3, 2, 5)},
        },
    },
}

# ════════════════════════════════════════════════════════════════
# SECTION 2H: P×OFICINA DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_OFFICE)
# ════════════════════════════════════════════════════════════════
p_o_weekly = {
    'Experiencia Impositiva Seller Dev': {
        'S2': {
            'Datos fiscales': {'AEC': (5, 0, 6), 'CTX': (1, 0, 1), 'KTA_BRASIL': (1, 0, 1)},
            'Emision de Nota Fiscal': {'AEC': (24, 4, 31), 'CTX': (4, 3, 7), 'KTA_BRASIL': (3, 7, 11)},
            'Facturación': {'AEC': (18, 2, 23), 'KTA_BRASIL': (1, 7, 8)},
        },
        'S1': {
            'Datos fiscales': {'AEC': (2, 0, 4), 'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (19, 1, 22), 'CTX': (2, 1, 3), 'KTA_BRASIL': (8, 3, 13)},
            'Facturación': {'AEC': (14, 2, 17), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 4, 8)},
        },
    },
    'ME Vendedor Seller Dev': {
        'S2': {
            'Despacho Ventas y Publicaciones': {'AEC': (24, 4, 30), 'ATE': (188, 34, 248), 'CTX': (50, 12, 72), 'KTA_BRASIL': (140, 30, 188)},
            'Gestiones Operativas': {'AEC': (14, 0, 16), 'ATE': (48, 8, 64), 'CTX': (8, 2, 10), 'KTA_BRASIL': (24, 6, 32)},
            'Reputación ME': {'AEC': (196, 8, 214), 'ATE': (84, 6, 92), 'CTX': (26, 4, 32), 'KTA_BRASIL': (134, 8, 146)},
            'Reversa': {'AEC': (6, 2, 8), 'ATE': (26, 6, 34), 'KTA_BRASIL': (30, 10, 42), 'MELICIDADE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (8, 2, 10), 'ATE': (28, 10, 40), 'CTX': (4, 0, 4), 'KTA_BRASIL': (18, 0, 24)},
        },
        'S1': {
            'Despacho Ventas y Publicaciones': {'AEC': (26, 8, 38), 'ATE': (288, 34, 352), 'CTX': (54, 6, 62), 'KTA_BRASIL': (168, 24, 220), 'MELICIDADE': (2, 0, 2)},
            'Gestiones Operativas': {'AEC': (2, 0, 2), 'ATE': (54, 0, 56), 'CTX': (10, 4, 16), 'KTA_BRASIL': (16, 8, 26)},
            'Reputación ME': {'AEC': (184, 6, 200), 'ATE': (86, 8, 102), 'CTX': (12, 0, 14), 'KTA_BRASIL': (136, 12, 162)},
            'Reversa': {'AEC': (8, 6, 16), 'ATE': (38, 8, 48), 'KTA_BRASIL': (32, 4, 42)},
            'Viaje del paquete - Vendedor': {'AEC': (2, 0, 4), 'ATE': (22, 4, 28), 'CTX': (4, 0, 4), 'KTA_BRASIL': (22, 2, 26)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'S2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (14, 5, 25), 'ATE': (33, 10, 46), 'CTX': (5, 3, 10), 'KTA_BRASIL': (28, 11, 45), 'MELICIDADE': (2, 1, 3)},
        },
        'S1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (30, 10, 43), 'ATE': (21, 6, 31), 'CTX': (5, 4, 9), 'KTA_BRASIL': (22, 6, 33), 'MELICIDADE': (3, 0, 3)},
        },
    },
    'Partners': {
        'S2': {
            'Drivers': {'AEC': (23, 7, 35), 'ATE': (240, 29, 290), 'CTX': (35, 8, 49), 'KTA_BRASIL': (190, 32, 251)},
            'Places Kangu': {'AEC': (2, 0, 2), 'ATE': (46, 4, 54), 'CTX': (7, 1, 9), 'KTA_BRASIL': (23, 4, 28)},
        },
        'S1': {
            'Drivers': {'AEC': (16, 7, 24), 'ATE': (228, 35, 287), 'CTX': (34, 8, 51), 'KTA_BRASIL': (197, 40, 262)},
            'Places Kangu': {'AEC': (4, 1, 6), 'ATE': (35, 3, 42), 'CTX': (5, 4, 11), 'KTA_BRASIL': (28, 1, 33)},
        },
    },
    'Post Venta Seller Dev': {
        'S2': {
            'Anulación de Venta': {'AEC': (1, 1, 2), 'ATE': (1, 0, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Reputación': {'AEC': (71, 7, 81), 'ATE': (33, 3, 39), 'CTX': (6, 2, 9), 'KTA_BRASIL': (61, 4, 72)},
        },
        'S1': {
            'Anulación de Venta': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 0, 1)},
            'Reputación': {'AEC': (70, 9, 85), 'ATE': (29, 4, 41), 'CTX': (8, 0, 8), 'KTA_BRASIL': (65, 6, 80)},
        },
    },
    'Publicaciones Seller Dev': {
        'S2': {
            'Afiliados ML': {'AEC': (146, 11, 173), 'CTX': (6, 3, 9), 'KTA_BRASIL': (13, 18, 32)},
            'Antes de publicar': {'AEC': (15, 1, 17), 'CTX': (4, 0, 5), 'KTA_BRASIL': (15, 0, 16)},
            'Calidad de foto': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'Denuncia de usuario': {'AEC': (5, 2, 8), 'CTX': (3, 0, 3), 'KTA_BRASIL': (0, 1, 1)},
            'Gestión de Publicación': {'AEC': (24, 3, 30), 'CTX': (6, 1, 7), 'KTA_BRASIL': (16, 4, 25)},
            'PR - Artículos prohibidos': {'AEC': (7, 5, 12), 'KTA_BRASIL': (15, 4, 22)},
            'PR - Datos Personales': {'AEC': (1, 0, 1), 'KTA_BRASIL': (5, 0, 5)},
            'PR - Propiedad intelectual': {'AEC': (22, 0, 22), 'KTA_BRASIL': (16, 4, 22)},
            'PR - Técnica prohibida': {'AEC': (16, 6, 22), 'KTA_BRASIL': (27, 1, 28)},
            'Potenciar Ventas': {'AEC': (8, 6, 15), 'CTX': (4, 2, 6), 'KTA_BRASIL': (17, 4, 24)},
        },
        'S1': {
            'Afiliados ML': {'AEC': (166, 14, 199), 'CTX': (3, 1, 5), 'KTA_BRASIL': (20, 20, 42)},
            'Antes de publicar': {'AEC': (6, 2, 8), 'CTX': (2, 0, 2), 'KTA_BRASIL': (18, 1, 22)},
            'Calidad de foto': {'AEC': (3, 1, 5), 'KTA_BRASIL': (9, 2, 12)},
            'Denuncia de usuario': {'AEC': (4, 2, 6), 'CTX': (0, 1, 1), 'KTA_BRASIL': (4, 1, 5)},
            'Gestión de Publicación': {'AEC': (11, 3, 16), 'CTX': (3, 0, 3), 'KTA_BRASIL': (20, 7, 30)},
            'PR - Artículos prohibidos': {'AEC': (4, 3, 9), 'KTA_BRASIL': (18, 3, 23)},
            'PR - Datos Personales': {'AEC': (0, 1, 1), 'KTA_BRASIL': (5, 0, 6)},
            'PR - Propiedad intelectual': {'AEC': (10, 3, 13), 'KTA_BRASIL': (17, 7, 27)},
            'PR - Técnica prohibida': {'AEC': (21, 3, 24), 'ATE': (0, 0, 1), 'KTA_BRASIL': (18, 4, 25)},
            'Potenciar Ventas': {'AEC': (5, 6, 12), 'CTX': (2, 1, 4), 'KTA_BRASIL': (11, 1, 14), 'MELICIDADE': (1, 0, 1)},
        },
    },
}
p_o_monthly = {
    'Experiencia Impositiva Seller Dev': {
        'M2': {
            'Datos fiscales': {'AEC': (28, 3, 35), 'CTX': (4, 1, 5), 'KTA_BRASIL': (4, 3, 8)},
            'Emision de Nota Fiscal': {'AEC': (180, 23, 227), 'CTX': (29, 9, 39), 'KTA_BRASIL': (31, 29, 65)},
            'Facturación': {'AEC': (105, 18, 141), 'CTX': (9, 3, 12), 'KTA_BRASIL': (14, 22, 38)},
        },
        'M1': {
            'Datos fiscales': {'KTA_BRASIL': (1, 1, 2)},
            'Emision de Nota Fiscal': {'AEC': (6, 0, 7), 'KTA_BRASIL': (1, 2, 3)},
            'Facturación': {'AEC': (1, 1, 2), 'KTA_BRASIL': (1, 2, 3)},
        },
    },
    'ME Vendedor Seller Dev': {
        'M2': {
            'Despacho Ventas y Publicaciones': {'AEC': (146, 36, 196), 'ATE': (1214, 212, 1618), 'CTX': (302, 56, 386), 'KTA_BRASIL': (598, 116, 804), 'MELICIDADE': (6, 0, 6)},
            'Gestiones Operativas': {'AEC': (34, 8, 46), 'ATE': (244, 32, 306), 'CTX': (54, 12, 74), 'KTA_BRASIL': (80, 22, 114), 'MELICIDADE': (2, 0, 2)},
            'Reputación ME': {'AEC': (996, 28, 1084), 'ATE': (426, 30, 490), 'CTX': (134, 10, 160), 'KTA_BRASIL': (584, 64, 686), 'MELICIDADE': (2, 2, 4)},
            'Reversa': {'AEC': (34, 10, 46), 'ATE': (178, 30, 222), 'KTA_BRASIL': (152, 32, 212), 'MELICIDADE': (2, 0, 2)},
            'Suspensiones ME': {'ATE': (2, 0, 2)},
            'Viaje del paquete - Vendedor': {'AEC': (24, 4, 32), 'ATE': (120, 26, 170), 'CTX': (24, 0, 24), 'KTA_BRASIL': (60, 10, 86)},
        },
        'M1': {
            'Despacho Ventas y Publicaciones': {'AEC': (4, 2, 6), 'ATE': (86, 6, 96), 'KTA_BRASIL': (58, 2, 64)},
            'Gestiones Operativas': {'ATE': (16, 0, 16), 'KTA_BRASIL': (4, 0, 4)},
            'Reputación ME': {'AEC': (18, 2, 24), 'ATE': (26, 0, 26), 'KTA_BRASIL': (26, 4, 32)},
            'Reversa': {'ATE': (2, 6, 8), 'KTA_BRASIL': (6, 2, 10)},
            'Viaje del paquete - Vendedor': {'ATE': (2, 2, 4)},
        },
    },
    'PCF Vendedor Seller Dev': {
        'M2': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (93, 35, 144), 'ATE': (166, 37, 225), 'CTX': (28, 13, 44), 'KTA_BRASIL': (79, 28, 118), 'MELICIDADE': (28, 5, 37)},
        },
        'M1': {
            'Post Compra Funcionalidades Vendedor': {'AEC': (4, 0, 5), 'ATE': (2, 1, 4), 'KTA_BRASIL': (4, 0, 7)},
        },
    },
    'Partners': {
        'M2': {
            'Drivers': {'AEC': (74, 23, 110), 'ATE': (987, 137, 1223), 'CTX': (180, 36, 241), 'KTA_BRASIL': (577, 105, 763)},
            'Places Kangu': {'AEC': (21, 3, 25), 'ATE': (215, 27, 262), 'CTX': (64, 9, 81), 'KTA_BRASIL': (110, 19, 140)},
        },
        'M1': {
            'Drivers': {'AEC': (8, 1, 10), 'ATE': (93, 8, 112), 'KTA_BRASIL': (70, 17, 100)},
            'Places Kangu': {'ATE': (7, 0, 8), 'KTA_BRASIL': (7, 0, 8)},
        },
    },
    'Post Venta Seller Dev': {
        'M2': {
            'Anulación de Venta': {'AEC': (16, 2, 18), 'ATE': (6, 1, 7), 'CTX': (3, 0, 4), 'KTA_BRASIL': (5, 2, 7)},
            'Reputación': {'AEC': (310, 46, 382), 'ATE': (177, 17, 220), 'CTX': (70, 12, 90), 'KTA_BRASIL': (265, 36, 326), 'MELICIDADE': (5, 0, 5)},
        },
        'M1': {
            'Reputación': {'AEC': (8, 1, 9), 'ATE': (8, 1, 10), 'KTA_BRASIL': (11, 0, 13)},
        },
    },
    'Publicaciones Seller Dev': {
        'M2': {
            'Afiliados ML': {'AEC': (871, 87, 1044), 'CTX': (30, 11, 44), 'KTA_BRASIL': (57, 68, 138), 'MELICIDADE': (1, 0, 1)},
            'Antes de publicar': {'AEC': (70, 5, 84), 'CTX': (17, 2, 21), 'KTA_BRASIL': (75, 6, 89)},
            'Calidad de foto': {'AEC': (3, 2, 7), 'KTA_BRASIL': (15, 3, 18)},
            'Denuncia de usuario': {'AEC': (38, 7, 49), 'CTX': (7, 2, 10), 'KTA_BRASIL': (8, 3, 11)},
            'Gestión de Publicación': {'AEC': (62, 18, 88), 'CTX': (23, 8, 31), 'KTA_BRASIL': (111, 15, 150)},
            'PR - Artículos prohibidos': {'AEC': (31, 15, 48), 'CTX': (1, 0, 1), 'KTA_BRASIL': (66, 16, 87)},
            'PR - Datos Personales': {'AEC': (3, 1, 4), 'KTA_BRASIL': (8, 5, 14)},
            'PR - Propiedad intelectual': {'AEC': (65, 10, 79), 'KTA_BRASIL': (99, 21, 128)},
            'PR - Técnica prohibida': {'AEC': (95, 15, 116), 'ATE': (0, 0, 1), 'KTA_BRASIL': (105, 13, 134), 'MELICIDADE': (3, 0, 3)},
            'Potenciar Ventas': {'AEC': (44, 17, 66), 'CTX': (16, 6, 27), 'KTA_BRASIL': (74, 16, 102), 'MELICIDADE': (1, 0, 1)},
        },
        'M1': {
            'Afiliados ML': {'AEC': (77, 5, 89), 'KTA_BRASIL': (9, 3, 12)},
            'Antes de publicar': {'AEC': (0, 1, 1), 'KTA_BRASIL': (3, 0, 3)},
            'Calidad de foto': {'AEC': (3, 0, 4), 'KTA_BRASIL': (8, 1, 10)},
            'Denuncia de usuario': {'AEC': (2, 0, 2), 'KTA_BRASIL': (1, 1, 2)},
            'Gestión de Publicación': {'AEC': (6, 1, 7), 'KTA_BRASIL': (4, 1, 5)},
            'PR - Artículos prohibidos': {'AEC': (1, 0, 2), 'KTA_BRASIL': (7, 1, 10)},
            'PR - Datos Personales': {'KTA_BRASIL': (4, 0, 4)},
            'PR - Propiedad intelectual': {'AEC': (3, 1, 4), 'KTA_BRASIL': (5, 4, 10)},
            'PR - Técnica prohibida': {'AEC': (5, 0, 5), 'KTA_BRASIL': (4, 2, 7)},
            'Potenciar Ventas': {'AEC': (2, 3, 5), 'KTA_BRASIL': (2, 1, 3)},
        },
    },
}

# ═══════════════════════════════════════════════════════════════
# SECTION 3: CALCULATIONS
# ═══════════════════════════════════════════════════════════════
def nps(p,d,s): return round(100.0*(p-d)/s,2) if s>0 else 0.0

def mix_neto(data, pa, pb, surv_a_tot, surv_b_tot, nps_b_tot):
    out={}
    for drv,periods in data.items():
        a=periods.get(pa,(0,0,0)); b=periods.get(pb,(0,0,0))
        na=nps(*a); nb=nps(*b)
        sha=a[2]/surv_a_tot if surv_a_tot else 0
        shb=b[2]/surv_b_tot if surv_b_tot else 0
        nt=round(sha*(nb-na),2); mx=round((shb-sha)*(nb-nps_b_tot),2)
        out[drv]={"surv_a":a[2],"nps_a":na,"share_a":round(sha*100,1),
                  "surv_b":b[2],"nps_b":nb,"share_b":round(shb*100,1),
                  "neto":nt,"mix":mx,"var":round(nt+mx,2)}
    return out

def proc_var(proc_data, pa, pb, nps_b_drv, sa_tot, sb_tot):
    out={}
    all_p=set(proc_data.get(pa,{}))|set(proc_data.get(pb,{}))
    for proc in all_p:
        a=proc_data.get(pa,{}).get(proc,(0,0,0)); b=proc_data.get(pb,{}).get(proc,(0,0,0))
        na=nps(*a); nb=nps(*b)
        sha=a[2]/sa_tot if sa_tot else 0; shb=b[2]/sb_tot if sb_tot else 0
        nt=round(sha*(nb-na),2); mx=round((shb-sha)*(nb-nps_b_drv),2)
        out[proc]={"surv_a":a[2],"nps_a":na,"share_a":round(sha*100,1),
                   "surv_b":b[2],"nps_b":nb,"share_b":round(shb*100,1),
                   "neto":nt,"mix":mx,"var":round(nt+mx,2)}
    return out

# Semana Fechada (S2 → S1)
sS2=sum(v["S2"][2] for v in weekly_driver.values())
sS1=sum(v["S1"][2] for v in weekly_driver.values())
pS2=sum(v["S2"][0] for v in weekly_driver.values()); dS2=sum(v["S2"][1] for v in weekly_driver.values())
pS1=sum(v["S1"][0] for v in weekly_driver.values()); dS1=sum(v["S1"][1] for v in weekly_driver.values())
nS2=nps(pS2,dS2,sS2); nS1=nps(pS1,dS1,sS1); dW=round(nS1-nS2,2)
wD=mix_neto(weekly_driver,"S2","S1",sS2,sS1,nS1)
wP={}
for drv in weekly_driver:
    s2p=weekly_proc[drv]["S2"]; s1p=weekly_proc[drv]["S1"]
    sa=sum(v[2] for v in s2p.values()); sb=sum(v[2] for v in s1p.values())
    wP[drv]=proc_var({"S2":s2p,"S1":s1p},"S2","S1",wD[drv]['nps_b'],sa,sb)

# Mensal (M2 → M1)
sM2=sum(v["M2"][2] for v in monthly_driver.values())
sM1=sum(v["M1"][2] for v in monthly_driver.values())
pM2=sum(v["M2"][0] for v in monthly_driver.values()); dM2x=sum(v["M2"][1] for v in monthly_driver.values())
pM1=sum(v["M1"][0] for v in monthly_driver.values()); dM1x=sum(v["M1"][1] for v in monthly_driver.values())
nM2=nps(pM2,dM2x,sM2); nM1=nps(pM1,dM1x,sM1); dM=round(nM1-nM2,2)
mD=mix_neto(monthly_driver,"M2","M1",sM2,sM1,nM1)
mP={}
for drv in monthly_driver:
    m2p=monthly_proc[drv]["M2"]; m1p=monthly_proc[drv]["M1"]
    sa=sum(v[2] for v in m2p.values()); sb=sum(v[2] for v in m1p.values())
    mP[drv]=proc_var({"M2":m2p,"M1":m1p},"M2","M1",mD[drv]['nps_b'],sa,sb)

# Semana Atual / Vigente (S1 → Vig)
sVig=sum(v[2] for v in drivers_vigente.values())
pVig=sum(v[0] for v in drivers_vigente.values()); dVig_s=sum(v[1] for v in drivers_vigente.values())
nVig=nps(pVig,dVig_s,sVig); dVW=round(nVig-nS1,2)
wDv={drv:{"S1":weekly_driver[drv]["S1"],"Vig":drivers_vigente.get(drv,(0,0,0))} for drv in weekly_driver}
vD=mix_neto(wDv,"S1","Vig",sS1,sVig,nVig)
vP={}
for drv in weekly_driver:
    s1p=weekly_proc[drv]["S1"]; vigp=proc_vigente.get(drv,{})
    sa=sum(v[2] for v in s1p.values()) or 1; sb=sum(v[2] for v in vigp.values()) or 1
    vP[drv]=proc_var({"S1":s1p,"Vig":vigp},"S1","Vig",vD[drv]['nps_b'],sa,sb)

# ═══════════════════════════════════════════════════════════════
# SECTION 4: HELPERS
# ═══════════════════════════════════════════════════════════════
import json as _json

DRIVER_COLORS = {
    "Experiencia Impositiva Seller Dev": "#3483FA",
    "ME Vendedor Seller Dev":            "#00A650",
    "PCF Vendedor Seller Dev":           "#FF7733",
    "Partners":                          "#9B59B6",
    "Post Venta Seller Dev":             "#E84142",
    "Publicaciones Seller Dev":          "#F39C12",
}
DRIVER_SHORT = {
    "Experiencia Impositiva Seller Dev": "Exp Imp",
    "ME Vendedor Seller Dev":            "ME Vendedor",
    "PCF Vendedor Seller Dev":           "PCF",
    "Partners":                          "Partners",
    "Post Venta Seller Dev":             "Post Venta",
    "Publicaciones Seller Dev":          "Publicaciones",
}

def _nps_series(history, labels):
    """Retorna {driver: [nps_por_periodo]}"""
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

def chart_block(chart_id, labels, history, target):
    series = _nps_series(history, labels)
    consolidated = _consolidated_series(history, labels)
    lbl_cfg = {
        "display": True,
        "anchor": "end",
        "align": "end",
        "offset": 2,
        "color": "#444",
        "font": {"size": 8, "weight": "600"},
        "formatter": "__FMT__",
    }
    datasets = []
    for drv in series:
        c = DRIVER_COLORS[drv]
        datasets.append({
            "type": "bar",
            "label": DRIVER_SHORT[drv],
            "data": series[drv],
            "backgroundColor": c + "cc",
            "borderColor": c,
            "borderWidth": 1,
            "borderRadius": 3,
            "borderSkipped": False,
            "datalabels": lbl_cfg,
        })
    datasets.append({
        "type": "line",
        "label": f"Target ({target:.2f}%)".replace(".", ","),
        "data": [target] * len(labels),
        "borderColor": "#e84142",
        "borderDash": [6, 3],
        "borderWidth": 2,
        "pointRadius": 0,
        "fill": False,
        "order": -1,
        "datalabels": {"display": False},
    })
    cfg = {
        "type": "bar",
        "data": {"labels": labels, "datasets": datasets},
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "layout": {"padding": {"top": 20, "bottom": 4}},
            "interaction": {"mode": "nearest", "intersect": True},
            "plugins": {
                "legend": {"position": "bottom", "labels": {"boxWidth": 12, "padding": 14, "font": {"size": 11}}},
                "tooltip": {"backgroundColor": "#fff", "borderColor": "#ddd", "borderWidth": 1,
                            "titleColor": "#333", "bodyColor": "#555"},
                "datalabels": {},
            },
            "scales": {
                "y": {"min": 25, "max": 90,
                      "ticks": {"stepSize": 5},
                      "grid": {"color": "#f0f0f0"}},
                "x": {"grid": {"display": False}}
            }
        }
    }
    cfg_json = _json.dumps(cfg).replace('"__FMT__"', 'function(v){return v!=null?v.toFixed(1)+"%":""}')
    return (
        f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);padding:20px 24px;margin-bottom:14px;position:relative;height:360px;">'
        f'<canvas id="{chart_id}"></canvas>'
        f'</div>'
        f'<script>new Chart(document.getElementById("{chart_id}"),{cfg_json});</script>'
    )

def fn(v): return f"{v:.2f}".replace(".", ",")
def fi(v): return f"{v:,}".replace(",", ".")
def arrow(v): return "▲" if v >= 0 else "▼"
def dc(v): return "pos" if v >= 0 else "neg"

def chip(v):
    sign = "+" if v > 0 else ""
    cls = "chip-pos" if v > 0 else ("chip-neg" if v < 0 else "chip-neu")
    return f'<span class="chip {cls}">{sign}{fn(v)}</span>'

def kpi_cards(nps_b, surv_b, label_b, delta, nps_a, surv_a, label_a, target=NPS_TARGET):
    vol_delta = surv_b - surv_a
    vol_pct = round(100*vol_delta/surv_a,1) if surv_a else 0
    gap = round(nps_b - target, 2)
    gap_cls = "var(--green)" if gap >= 0 else "var(--red)"
    gap_sign = "+" if gap >= 0 else ""
    gap_label = "acima do target" if gap >= 0 else "abaixo do target"
    pct_ating = round(nps_b / target * 100, 1) if target else 0
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
        f'</div>'
        f'</div>'
    )

def waterfall_block(chart_id, label_a, nps_a, label_b, nps_b, d_dict):
    sorted_drvs = sorted(d_dict.keys(), key=lambda d: -d_dict[d]['var'])
    y_min = 25
    labels, bars, bg_colors, deltas_js = [label_a], [], [], [None]

    # Opening bar
    bars.append([y_min, round(nps_a, 2)])
    bg_colors.append('#3483FAcc')

    # Delta bars
    running = nps_a
    for drv in sorted_drvs:
        v = round(d_dict[drv]['var'], 2)
        labels.append(DRIVER_SHORT[drv])
        lo, hi = round(min(running, running + v), 2), round(max(running, running + v), 2)
        bars.append([lo, hi])
        bg_colors.append('#00a650cc' if v >= 0 else '#e84142cc')
        deltas_js.append(v)
        running += v

    # Closing bar
    labels.append(label_b)
    bars.append([y_min, round(nps_b, 2)])
    bg_colors.append('#3483FAcc')
    deltas_js.append(None)

    nps_a_str = f'{nps_a:.1f}'.replace('.', ',') + '%'
    nps_b_str = f'{nps_b:.1f}'.replace('.', ',') + '%'
    n_last    = len(labels) - 1
    deltas_arr = _json.dumps(deltas_js)

    lbl_cfg = {"display": True, "anchor": "end", "align": "end", "offset": 3,
               "color": "#333", "font": {"size": 9, "weight": "600"},
               "formatter": "__WF_FMT__"}

    dataset = {"type": "bar", "data": bars, "backgroundColor": bg_colors,
               "borderRadius": 3, "borderSkipped": False, "datalabels": lbl_cfg}

    cfg = {
        "type": "bar",
        "data": {"labels": labels, "datasets": [dataset]},
        "options": {
            "responsive": True, "maintainAspectRatio": False,
            "layout": {"padding": {"top": 24, "bottom": 4}},
            "plugins": {
                "legend": {"display": False},
                "datalabels": {},
                "title": {"display": True, "text": f"Impacto WoW — Abertura Driver  ({label_a} → {label_b})",
                          "align": "start", "color": "#555", "font": {"size": 12, "weight": "600"},
                          "padding": {"bottom": 10}},
            },
            "scales": {
                "y": {"min": y_min, "max": 90, "ticks": {"stepSize": 5}, "grid": {"color": "#f0f0f0"}},
                "x": {"grid": {"display": False}, "ticks": {"maxRotation": 35, "font": {"size": 10}}},
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

    # Tabela lateral com variação por driver (mesma ordem do waterfall)
    tbl_rows = ""
    for drv in sorted_drvs:
        v   = d_dict[drv]['var']
        na  = d_dict[drv]['nps_a']
        nb  = d_dict[drv]['nps_b']
        clr = "var(--green)" if v >= 0 else "var(--red)"
        bgc = "var(--light-green)" if v >= 0 else "var(--light-red)"
        sign = "+" if v >= 0 else ""
        tbl_rows += (
            f'<tr>'
            f'<td style="font-size:11px;font-weight:600;padding:5px 8px;border-bottom:1px solid #f5f5f5;">{DRIVER_SHORT[drv]}</td>'
            f'<td style="font-size:11px;text-align:right;padding:5px 8px;border-bottom:1px solid #f5f5f5;color:#888;">{fn(na)}</td>'
            f'<td style="font-size:11px;text-align:right;padding:5px 8px;border-bottom:1px solid #f5f5f5;color:#888;">{fn(nb)}</td>'
            f'<td style="text-align:right;padding:5px 8px;border-bottom:1px solid #f5f5f5;">'
            f'<span style="background:{bgc};color:{clr};font-size:10px;font-weight:700;padding:2px 6px;border-radius:8px;">{sign}{fn(v)}</span>'
            f'</td>'
            f'</tr>'
        )

    side_table = (
        f'<div style="display:flex;flex-direction:column;justify-content:center;'
        f'background:#fff;border-radius:10px;border:1px solid var(--border);padding:12px 16px;">'
        f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;'
        f'color:#888;margin-bottom:8px;">Variação por Driver</div>'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<thead><tr>'
        f'<th style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;text-align:left;border-bottom:2px solid #f0f0f0;">Driver</th>'
        f'<th style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;text-align:right;border-bottom:2px solid #f0f0f0;">Ant.</th>'
        f'<th style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;text-align:right;border-bottom:2px solid #f0f0f0;">Atual</th>'
        f'<th style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:4px 8px;text-align:right;border-bottom:2px solid #f0f0f0;">VAR</th>'
        f'</tr></thead>'
        f'<tbody>{tbl_rows}</tbody>'
        f'</table></div>'
    )

    return (
        f'<div style="background:#fff;border-radius:8px;border:1px solid var(--border);padding:14px 16px;">'
        f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#888;margin-bottom:4px;">Impacto por Driver</div>'
        f'<div style="position:relative;height:230px;">'
        f'<canvas id="{chart_id}"></canvas></div>'
        f'</div>'
        f'<script>new Chart(document.getElementById("{chart_id}"),{cfg_json});</script>'
    )

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
                      "scales":{"y":{"min":25,"max":90,"ticks":{"stepSize":5},"grid":{"color":"#f0f0f0"}},
                                "x":{"grid":{"display":False}}}}}
    cfg_json = _json.dumps(cfg).replace('"__FMT__"', fmt_js)
    return (
        f'<div style="position:relative;height:210px;">'
        f'<canvas id="{chart_id}"></canvas></div>'
        f'<script>new Chart(document.getElementById("{chart_id}"),{cfg_json});</script>'
    )

def _forecast(vals):
    """Regressão linear sobre os períodos disponíveis → slope = variação esperada no próximo período."""
    nv = [(i, v) for i, v in enumerate(vals) if v is not None]
    if len(nv) < 2:
        return None
    n  = len(nv)
    xs = [p[0] for p in nv]; ys = [p[1] for p in nv]
    sx = sum(xs); sy = sum(ys)
    sxy = sum(x*y for x, y in zip(xs, ys))
    sx2 = sum(x*x for x in xs)
    den = n*sx2 - sx*sx
    if den == 0:
        return None
    return round((n*sxy - sx*sy) / den, 2)

def _trend(vals):
    """Retorna (label, color, bg) baseado nos últimos 2-3 períodos."""
    nv = [v for v in vals if v is not None]
    if len(nv) < 2:
        return "— Sem dados", "#888", "#f5f5f5"
    d1 = nv[-1] - nv[-2]
    d2 = nv[-2] - nv[-3] if len(nv) >= 3 else None
    both_up   = d2 is not None and d1 > 0 and d2 > 0
    both_down = d2 is not None and d1 < 0 and d2 < 0
    if both_up and d1 > 1.5:
        return "↑↑ Em alta",    "var(--green)", "var(--light-green)"
    elif d1 > 0.5:
        return "↑ Evolução",    "var(--green)", "var(--light-green)"
    elif abs(d1) <= 0.5:
        return "→ Estável",     "#666",         "#f0f0f0"
    elif both_down and d1 < -1.5:
        return "↓↓ Em queda",   "var(--red)",   "var(--light-red)"
    else:
        return "↓ Queda",       "var(--red)",   "var(--light-red)"

def driver_history_table(history, labels, drv_targets, delta_label="ΔMoM"):
    cell   = 'style="font-size:11px;padding:5px 8px;text-align:right;border-bottom:1px solid #f5f5f5;"'
    cell_l = 'style="font-size:11px;padding:5px 8px;font-weight:600;border-bottom:1px solid #f5f5f5;white-space:nowrap;"'
    th     = 'style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:5px 8px;text-align:right;border-bottom:2px solid #f0f0f0;white-space:nowrap;"'
    th_l   = 'style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:5px 8px;text-align:left;border-bottom:2px solid #f0f0f0;"'

    def nps_from(drv, lbl):
        d = history[drv].get(lbl, (0,0,0))
        return round(100*(d[0]-d[1])/d[2], 2) if d[2] > 0 else None

    def chip_cell(v):
        if v is None: return f'<td {cell}>—</td>'
        clr = "var(--green)" if v >= 0 else "var(--red)"
        bg  = "var(--light-green)" if v >= 0 else "var(--light-red)"
        s   = "+" if v >= 0 else ""
        return (f'<td {cell}><span style="background:{bg};color:{clr};font-size:10px;'
                f'font-weight:700;padding:2px 6px;border-radius:8px;">{s}{fn(v)}</span></td>')

    header = (f'<tr><th {th_l}>Driver</th>'
              + ''.join(f'<th {th}>{l}</th>' for l in labels)
              + f'<th {th}>{delta_label}</th><th {th}>vs Target</th>'
              + f'<th {th}>Tendência</th><th {th}>Forecast (pp)</th></tr>')

    rows = ""
    for drv in history:
        vals    = [nps_from(drv, l) for l in labels]
        cur     = vals[-1]
        prev    = vals[-2] if len(vals) >= 2 else None
        delta_v = round(cur - prev, 2) if cur is not None and prev is not None else None
        tgt_v   = round(cur - drv_targets.get(drv, 0), 2) if cur is not None else None
        tlabel, tclr, tbg = _trend(vals)

        trend_cell = (f'<td {cell}><span style="background:{tbg};color:{tclr};font-size:10px;'
                      f'font-weight:700;padding:2px 8px;border-radius:8px;white-space:nowrap;">'
                      f'{tlabel}</span></td>')

        fc = _forecast(vals)
        if fc is not None:
            fc_clr = "var(--green)" if fc >= 0 else "var(--red)"
            fc_bg  = "var(--light-green)" if fc >= 0 else "var(--light-red)"
            fc_s   = "+" if fc >= 0 else ""
            forecast_cell = (f'<td {cell}><span style="background:{fc_bg};color:{fc_clr};'
                             f'font-size:10px;font-weight:700;padding:2px 8px;border-radius:8px;">'
                             f'{fc_s}{fn(fc)} pp</span></td>')
        else:
            forecast_cell = f'<td {cell}>—</td>'

        val_cells = "".join(
            f'<td {cell}>{fn(v) if v is not None else "—"}</td>' for v in vals
        )
        rows += (f'<tr><td {cell_l}>{DRIVER_SHORT[drv]}</td>'
                 + val_cells + chip_cell(delta_v) + chip_cell(tgt_v)
                 + trend_cell + forecast_cell + '</tr>')

    return (
        f'<div style="margin-top:16px;overflow-x:auto;">'
        f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;'
        f'color:#888;margin-bottom:6px;">NPS por Driver — Histórico</div>'
        f'<table style="width:100%;border-collapse:collapse;background:#fff;">'
        f'<thead>{header}</thead><tbody>{rows}</tbody></table></div>'
    )

def summary_box(period_label, nps_b, nps_a, delta, surv_b, surv_a, d_dict, p_dict,
                wf_html="", cons_html="", hist_table=""):
    charts_grid = ""
    if cons_html or wf_html:
        charts_grid = (
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px;">'
            f'<div style="background:#fff;border-radius:8px;border:1px solid var(--border);padding:14px 16px;">'
            f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#888;margin-bottom:4px;">NPS Consolidado vs Target</div>'
            + cons_html +
            f'</div>'
            + (wf_html if wf_html else '') +
            f'</div>'
        )
    return (
        f'<div class="summary-box">'
        f'<div class="summary-header">'
        f'<div><div class="summary-title">Resumo Executivo</div>'
        f'<div class="summary-sub">{period_label}</div></div>'
        f'<span class="nps-badge" style="background:{"var(--light-green)" if delta>=0 else "var(--light-red)"};color:{"var(--green)" if delta>=0 else "var(--red)"};">'
        f'NPS {fn(nps_b)} {arrow(delta)} {("+" if delta>=0 else "")}{fn(delta)} pp</span>'
        f'</div><hr class="divider">'
        f'<p class="summary-text">{period_label} encerrou em <strong>NPS {fn(nps_b)} ({("+" if delta>=0 else "")}{fn(delta)} pp)</strong> '
        f'vs período anterior ({fn(nps_a)}, {fi(surv_a)} pesquisas). Atual: {fi(surv_b)} pesquisas.</p>'
        + charts_grid
        + hist_table +
        f'</div>'
    )

def driver_table(d_dict, surv_a, nps_a, surv_b, nps_b, delta, lbl_a, lbl_b):
    rows = ""
    for drv,v in sorted(d_dict.items(), key=lambda x: -abs(x[1]['var'])):
        rows += (
            f'<tr><td>{drv}</td>'
            f'<td>{fi(v["surv_a"])}</td><td>{fn(v["nps_a"])}</td>'
            f'<td>{fi(v["surv_b"])}</td><td>{fn(v["nps_b"])}</td>'
            f'<td>{v["share_a"]}%</td><td>{v["share_b"]}%</td>'
            f'<td>{chip(v["mix"])}</td><td>{chip(v["neto"])}</td>'
            f'<td>{chip(v["var"])}</td></tr>'
        )
    sm=round(sum(v['mix'] for v in d_dict.values()),2)
    sn=round(sum(v['neto'] for v in d_dict.values()),2)
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

def proc_blocks(d_dict, p_dict, lbl_a, lbl_b):
    blocks = ""
    for drv in sorted(d_dict, key=lambda d: -abs(d_dict[d]['var'])):
        v_drv = d_dict[drv]
        top = sorted(p_dict[drv].items(), key=lambda x: -abs(x[1]['var']))[:3]
        rows = "".join(
            f'<tr><td>{p}</td><td>{fn(v["nps_a"])}</td><td>{fn(v["nps_b"])}</td>'
            f'<td>{fi(v["surv_b"])}</td><td>{chip(v["var"])}</td></tr>'
            for p,v in top
        )
        dv = v_drv['var']
        sign = "+" if dv >= 0 else ""
        cls = "chip-pos" if dv >= 0 else "chip-neg"
        blocks += (
            f'<div class="driver-block">'
            f'<div class="driver-block-header">'
            f'<div><div class="driver-name">{drv}</div>'
            f'<div class="driver-meta">NPS {lbl_a}: {fn(v_drv["nps_a"])} → {lbl_b}: {fn(v_drv["nps_b"])} · {fi(v_drv["surv_b"])} pesquisas</div></div>'
            f'<span class="chip {cls}">VAR {sign}{fn(dv)} pp</span>'
            f'</div>'
            f'<table><thead><tr><th>Processo</th><th>NPS {lbl_a}</th><th>NPS {lbl_b}</th><th>Pesq.</th><th>VAR</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
        )
    return f'<div class="driver-grid">{blocks}</div>'

def tab_content(tab_id, nps_b, surv_b, label_b, delta, nps_a, surv_a, label_a,
                d_dict, p_dict, extra_html="",
                wf_html="", cons_html="", hist_table="", bullets_html=""):
    return (
        f'<div id="tab-{tab_id}" class="tab-content">'
        + f'<div class="section-title">KPIs</div>'
        + kpi_cards(nps_b, surv_b, label_b, delta, nps_a, surv_a, label_a)
        + (bullets_html if bullets_html else "")
        + summary_box(label_b, nps_b, nps_a, delta, surv_b, surv_a, d_dict, p_dict,
                    wf_html=wf_html, cons_html=cons_html, hist_table=hist_table) +
        extra_html +
        f'<div class="section-title">Drilldown por Processo — Top 3 por Driver</div>'
        + proc_blocks(d_dict, p_dict, label_a, label_b) +
        f'</div>'
    )

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
    """Segundo deep dive: drivers negativos vs target com tendência de queda + análise quantitativa."""
    if not alerts:
        return ""

    def _quant_section(drv_key):
        aq = ALERT_ANALYSIS.get(drv_key, {})
        if not aq:
            return ""
        # CDU table
        cdu_rows = ""
        for row in aq.get("cdu_breakdown", []):
            cdu_rows += (
                f'<tr>'
                f'<td style="font-size:10px;padding:4px 8px;border-bottom:1px solid #f5f5f5;">{row["cdu"]}</td>'
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
        # USER vs REP themes
        user_html = "".join(f'<li style="font-size:11px;padding:4px 0 4px 14px;border-bottom:1px solid #f5f5f5;position:relative;line-height:1.5;">'
                            f'<span style="position:absolute;left:0;color:var(--blue);font-weight:700;">U</span>{t}</li>'
                            for t in aq.get("user_themes", []))
        rep_html  = "".join(f'<li style="font-size:11px;padding:4px 0 4px 14px;border-bottom:1px solid #f5f5f5;position:relative;line-height:1.5;">'
                            f'<span style="position:absolute;left:0;color:#888;font-weight:700;">R</span>{t}</li>'
                            for t in aq.get("rep_themes", []))
        themes = (
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px;">'
            f'<div>'
            f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--blue);margin-bottom:6px;">Temas recorrentes — USER</div>'
            f'<ul style="list-style:none;padding:0;">{user_html}</ul></div>'
            f'<div>'
            f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#888;margin-bottom:6px;">Padrão de resposta — REP</div>'
            f'<ul style="list-style:none;padding:0;">{rep_html}</ul></div>'
            f'</div>'
        )
        return cdu_table + themes

    cards = ""
    for a in alerts:
        gap_str       = f'{a["delta_tgt"]:+.2f}'.replace(".", ",")
        insights_html = "".join(f'<li class="neg-li">{i}</li>' for i in a["insights"])
        acoes_html    = "".join(f'<li style="color:var(--blue);" class="neg-li">{ac}</li>' for ac in a.get("acoes", []))
        quant_html    = _quant_section(a["drv"])
        cards += (
            f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);border-top:4px solid #FF7733;overflow:hidden;">'
            f'<div style="padding:14px 18px;border-bottom:1px solid var(--border);background:#fff8f0;">'
            f'<div style="font-weight:800;font-size:14px;color:#FF7733;">&#9888; {a["drv"]}</div>'
            f'<div style="font-size:12px;color:#666;margin-top:3px;">{a["proc"]} · NPS {str(a["nps_cur"]).replace(".",",")}% vs Target {str(a["nps_tgt"]).replace(".",",")}% '
            f'({gap_str} pp) · {a["trend"]}</div>'
            f'</div>'
            f'<div style="padding:14px 18px;">'
            + quant_html +
            f'<div style="margin-top:12px;border-top:1px solid #f0f0f0;padding-top:10px;">'
            f'<div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:var(--red);margin-bottom:8px;">Insights — Comentários Detratores</div>'
            + (f'<div style="font-size:12px;background:#fff8f0;border-left:3px solid #FF7733;'
               f'padding:8px 12px;border-radius:0 4px 4px 0;margin-bottom:10px;color:#444;line-height:1.55;">'
               f'<span style="font-weight:800;color:#FF7733;">Por que está abaixo do target: </span>{a["why"]}</div>'
               if a.get("why") else "")
            + f'<ul class="deep-dive-body" style="padding:0;list-style:none;">{insights_html}</ul></div>'
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

def seniority_block(seniority_data, period_label, lbl_a=None, lbl_b=None, drv_targets=None):
    """Tabela Expert vs Newbie por driver. Aceita dict mensal {EXPERT:(p,d,s)} ou semanal {S1:{EXPERT:...}}."""
    def _nps(t): return round(100.0*(t[0]-t[1])/t[2], 2) if t[2]>0 else None

    # Normaliza: se weekly (tem S1/S2), usa S1 (mais recente); se mensal, usa direto
    def _get(drv_data):
        if lbl_b and lbl_b in drv_data:
            return drv_data[lbl_b]
        return drv_data

    rows = []
    for drv, data in seniority_data.items():
        d = _get(data)
        e = d.get("EXPERT", (0,0,0)); n = d.get("NEWBIE", (0,0,0))
        ne = _nps(e); nn = _nps(n)
        if ne is None or nn is None: continue
        gap = round(ne - nn, 2)
        rows.append((drv, ne, e[2], nn, n[2], gap))

    rows.sort(key=lambda r: r[5])  # pior gap primeiro

    def gap_chip(g):
        if g <= -20:
            clr, bg, lbl = "var(--red)", "var(--light-red)", f"{g:+.2f}".replace(".",",")
        elif g <= -8:
            clr, bg, lbl = "#FF7733", "#FF773322", f"{g:+.2f}".replace(".",",")
        elif g < 5:
            clr, bg, lbl = "#666", "#f0f0f0", f"{g:+.2f}".replace(".",",")
        else:
            clr, bg, lbl = "var(--blue)", "#e8f0fe", f"{g:+.2f}".replace(".",",")
        return (f'<span style="background:{bg};color:{clr};font-size:11px;font-weight:700;'
                f'padding:3px 8px;border-radius:8px;white-space:nowrap;">{lbl} pp</span>')

    th = 'style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:8px 12px;text-align:right;border-bottom:2px solid #f0f0f0;"'
    th_l = 'style="font-size:10px;font-weight:700;color:#aaa;text-transform:uppercase;padding:8px 12px;text-align:left;border-bottom:2px solid #f0f0f0;"'
    cell = 'style="font-size:12px;padding:8px 12px;text-align:right;border-bottom:1px solid #f5f5f5;"'
    cell_l = 'style="font-size:12px;font-weight:600;padding:8px 12px;border-bottom:1px solid #f5f5f5;"'

    def vs_tgt_chip(nps_val, tgt):
        if tgt is None: return ""
        diff = round(nps_val - tgt, 2)
        sign = "+" if diff >= 0 else ""
        clr  = "var(--green)" if diff >= 0 else "var(--red)"
        bg   = "var(--light-green)" if diff >= 0 else "var(--light-red)"
        arrow = "▲" if diff >= 0 else "▼"
        return (f'<br><span style="background:{bg};color:{clr};font-size:9px;font-weight:700;'
                f'padding:1px 5px;border-radius:4px;white-space:nowrap;">'
                f'{arrow} {sign}{str(diff).replace(".",",")} vs tgt</span>')

    tbody = ""
    for drv, ne, se, nn, sn, gap in rows:
        tgt = (drv_targets or {}).get(drv)
        e_clr = "var(--green)" if ne >= 60 else ("var(--red)" if ne < 40 else "#444")
        n_clr = "var(--green)" if nn >= 60 else ("var(--red)" if nn < 40 else "#444")
        tbody += (
            f'<tr>'
            f'<td {cell_l}>{DRIVER_SHORT[drv]}</td>'
            f'<td {cell}><span style="color:{e_clr};font-weight:700;">{fn(ne)}%</span>'
            f' <span style="color:#bbb;font-size:10px;">({fi(se)})</span>'
            f'{vs_tgt_chip(ne, tgt)}</td>'
            f'<td {cell}><span style="color:{n_clr};font-weight:700;">{fn(nn)}%</span>'
            f' <span style="color:#bbb;font-size:10px;">({fi(sn)})</span>'
            f'{vs_tgt_chip(nn, tgt)}</td>'
            f'<td {cell}>{gap_chip(gap)}</td>'
            f'</tr>'
        )

    return (
        f'<div class="section-title">Expert vs Newbie — {period_label}</div>'
        f'<div class="card" style="margin-bottom:14px;">'
        f'<div class="card-header">Seniority Gap por Driver'
        f'<span class="badge">Fonte: DM_CX_NPS_Y20_DETAIL · planejamento BR</span></div>'
        f'<table><thead><tr>'
        f'<th {th_l}>Driver</th>'
        f'<th {th}>Expert</th>'
        f'<th {th}>Newbie</th>'
        f'<th {th}>Gap (E − N)</th>'
        f'</tr></thead><tbody>{tbody}</tbody></table>'
        f'<div style="font-size:11px;color:#bbb;padding:8px 14px;">'
        f'<span style="background:var(--light-red);color:var(--red);padding:1px 6px;border-radius:4px;font-weight:700;font-size:10px;">≤ −20 pp</span> crítico &nbsp;'
        f'<span style="background:#FF773322;color:#FF7733;padding:1px 6px;border-radius:4px;font-weight:700;font-size:10px;">−8 a −20 pp</span> atenção &nbsp;'
        f'<span style="background:#f0f0f0;color:#666;padding:1px 6px;border-radius:4px;font-weight:700;font-size:10px;">&lt; 5 pp</span> equilibrado &nbsp;'
        f'<span style="background:#e8f0fe;color:var(--blue);padding:1px 6px;border-radius:4px;font-weight:700;font-size:10px;">+ pp</span> Newbie acima'
        f'</div></div>'
    )


def tab_bullets_block(period_label, nps_cur, delta, surv, target,
                      pos_drv, pos_var, pos_proc, pos_insights,
                      neg_drv, neg_var, neg_proc, neg_insights,
                      alerts, n_driver_insights=1,
                      seniority_data=None, drv_targets=None, seniority_period=None,
                      neg_why=""):
    """Resumo executivo com bullets qualitativos — inserido no topo de cada aba.
    n_driver_insights: quantos insights do deep dive mostrar por driver (1 para semanal, 2+ para mensal).
    Alertas sempre mostram 2 insights.
    """

    def insight_list(insights, n, color):
        """Renderiza n insights como mini lista com bullet colorido."""
        items = insights[:n] if insights else []
        if not items:
            return ""
        if len(items) == 1:
            return f'<div style="font-size:12px;color:#555;line-height:1.55;margin-top:4px;">{items[0]}</div>'
        li = "".join(
            f'<li style="font-size:12px;color:#555;line-height:1.55;padding:3px 0 3px 14px;'
            f'border-bottom:1px solid #fafafa;position:relative;">'
            f'<span style="position:absolute;left:0;color:{color};font-weight:700;">›</span>{i}</li>'
            for i in items
        )
        return f'<ul style="list-style:none;padding:0;margin-top:6px;">{li}</ul>'

    def row(badge, b_color, b_bg, title, proc_line, insights_html):
        return (
            f'<div style="display:grid;grid-template-columns:auto 1fr;gap:14px;'
            f'padding:12px 0;border-bottom:1px solid #f5f5f5;align-items:start;">'
            f'<span style="display:inline-flex;align-items:center;justify-content:center;'
            f'width:26px;height:26px;border-radius:50%;background:{b_bg};'
            f'color:{b_color};font-size:12px;font-weight:900;flex-shrink:0;margin-top:1px;">{badge}</span>'
            f'<div>'
            f'<div style="font-size:13px;font-weight:700;color:#1a1a2e;line-height:1.4;">{title}</div>'
            + (f'<div style="font-size:11px;color:#999;margin-top:3px;font-style:italic;">{proc_line}</div>' if proc_line else '')
            + insights_html
            + f'</div></div>'
        )

    # 1. Consolidated NPS
    d_sign = "+" if delta >= 0 else ""
    d_clr  = "var(--green)" if delta >= 0 else "var(--red)"
    gap    = round(nps_cur - target, 2)
    g_sign = "+" if gap >= 0 else ""
    g_clr  = "var(--green)" if gap >= 0 else "var(--red)"
    r1 = row(
        "↑" if delta >= 0 else "↓", d_clr, d_clr + "22",
        f'NPS <span style="color:{d_clr};">{fn(nps_cur)}%</span>'
        f'&nbsp;<span style="color:{d_clr};font-size:12px;font-weight:700;">({d_sign}{fn(delta)} pp)</span>'
        f'&nbsp;·&nbsp;<span style="color:{g_clr};font-size:12px;">{g_sign}{fn(gap)} pp vs target {fn(target)}%</span>'
        f'&nbsp;·&nbsp;<span style="color:#888;font-size:12px;">{fi(surv)} pesquisas</span>',
        "", ""
    )

    # 2. Best driver
    has_var_pos = pos_var not in ("sem dados", "")
    r2 = row(
        "↑", "var(--green)", "var(--light-green)",
        f'<span style="color:var(--green);">{pos_drv}</span>'
        + (f'&nbsp;<span style="font-size:12px;font-weight:700;color:var(--green);">({pos_var})</span>' if has_var_pos else ""),
        pos_proc if pos_proc not in ("sem dados", "") else "",
        insight_list(pos_insights, n_driver_insights, "var(--green)")
    )

    # 3. Worst driver
    has_var_neg = neg_var not in ("sem dados", "")
    _neg_why = neg_why
    _neg_why_html = (
        f'<div style="font-size:12px;background:#fdecea;border-left:3px solid var(--red);'
        f'padding:6px 10px;border-radius:0 4px 4px 0;margin-top:5px;color:#444;line-height:1.55;">'
        f'<span style="font-weight:700;color:var(--red);">Por que caiu: </span>{_neg_why}</div>'
    ) if _neg_why else ""
    r3 = row(
        "↓", "var(--red)", "var(--light-red)",
        f'<span style="color:var(--red);">{neg_drv}</span>'
        + (f'&nbsp;<span style="font-size:12px;font-weight:700;color:var(--red);">({neg_var})</span>' if has_var_neg else ""),
        neg_proc if neg_proc not in ("sem dados", "") else "",
        _neg_why_html + insight_list(neg_insights, n_driver_insights, "var(--red)")
    )

    # 4. Alerts — why (causa raiz em destaque) + 2 insights
    alert_rows = ""
    for a in alerts:
        gap_a    = round(a["nps_cur"] - a["nps_tgt"], 2)
        g_sign_a = "+" if gap_a >= 0 else ""
        proc_a   = a.get("proc", "")
        why_a    = a.get("why", "")
        title_a  = (
            f'<span style="color:#FF7733;">{a["drv"]}</span>'
            f'&nbsp;<span style="font-size:11px;color:#888;">·&nbsp;NPS {str(a["nps_cur"]).replace(".",",")}%'
            f'&nbsp;vs target {str(a["nps_tgt"]).replace(".",",")}%'
            f'&nbsp;({g_sign_a}{fn(gap_a)} pp)&nbsp;·&nbsp;{a["trend"]}</span>'
        )
        why_html = (
            f'<div style="font-size:12px;background:#fff8f0;border-left:3px solid #FF7733;'
            f'padding:6px 10px;border-radius:0 4px 4px 0;margin-top:5px;color:#444;line-height:1.55;">'
            f'<span style="font-weight:700;color:#FF7733;">Por que está abaixo do target: </span>{why_a}</div>'
        ) if why_a else ""
        alert_rows += row(
            "⚠", "#FF7733", "#FF773322",
            title_a,
            proc_a,
            why_html + insight_list(a.get("insights", []), 2, "#FF7733")
        )

    # 5. Seniority bullet — auto-gerado dos dados
    seniority_row = ""
    if seniority_data:
        def _nps_s(t): return round(100.0*(t[0]-t[1])/t[2], 2) if t[2]>0 else None

        def _get_period(drv_data):
            if seniority_period and seniority_period in drv_data:
                return drv_data[seniority_period]
            return drv_data

        gaps = []
        for drv, data in seniority_data.items():
            d = _get_period(data)
            ne = _nps_s(d.get("EXPERT",(0,0,0)))
            nn = _nps_s(d.get("NEWBIE",(0,0,0)))
            if ne is None or nn is None: continue
            gaps.append((drv, ne, nn, round(ne - nn, 2)))

        if gaps:
            avg_gap = round(sum(g for _, _, _, g in gaps) / len(gaps), 2)
            maiores = sorted([(d, g) for d, _, _, g in gaps if abs(g) > 5], key=lambda x: x[1])
            menores = sorted([(d, g) for d, _, _, g in gaps if abs(g) <= 5], key=lambda x: x[1])

            def gap_fmt(g):
                sign = "+" if g >= 0 else ""
                clr  = "var(--red)" if g <= -10 else ("#FF7733" if g < 0 else "var(--green)")
                return f'<span style="color:{clr};font-weight:700;">{sign}{fn(g)} pp</span>'

            maiores_txt = ", ".join(f'{DRIVER_SHORT[d]} {gap_fmt(g)}' for d, g in maiores) or "—"
            menores_txt = ", ".join(f'{DRIVER_SHORT[d]} {gap_fmt(g)}' for d, g in menores) or "—"

            avg_clr = "var(--red)" if avg_gap < -10 else ("#FF7733" if avg_gap < -5 else "var(--green)")
            avg_chip = (f'<span style="font-size:12px;font-weight:700;color:{avg_clr};">'
                        f'{fn(avg_gap)} pp</span>')

            title_html = f'Newbies vs Experts &nbsp;—&nbsp; Gap médio {avg_chip}'
            body_html  = (
                f'<div style="font-size:12px;color:#555;line-height:1.7;margin-top:4px;">'
                f'<b>Maiores Gaps:</b> {maiores_txt}<br>'
                f'<b>Menores Gaps:</b> {menores_txt}'
                f'</div>'
            )

            seniority_row = row("◑", "#9B59B6", "#9B59B622", title_html, "", body_html)

    return (
        f'<div style="background:#fff;border-radius:10px;border:1px solid var(--border);'
        f'border-left:4px solid var(--yellow);padding:18px 24px;margin-bottom:20px;">'
        f'<div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;'
        f'color:#888;margin-bottom:4px;">Resumo Executivo</div>'
        f'<div style="font-size:12px;color:#bbb;margin-bottom:12px;">{period_label}</div>'
        + r1 + r2 + r3 + alert_rows + seniority_row +
        f'</div>'
    )


# Deep dive HTML (gerado após dd_block estar definida)
deep_dive_html = dd_block(
    DEEP_DIVE_DATE,
    DEEP_DIVE_POS_DRIVER, DEEP_DIVE_POS_VAR, DEEP_DIVE_POS_PROC, DEEP_DIVE_POS_INSIGHTS,
    DEEP_DIVE_NEG_DRIVER, DEEP_DIVE_NEG_VAR, DEEP_DIVE_NEG_PROC, DEEP_DIVE_NEG_INSIGHTS,
    DCEV_ACOES
) + alert_dd_block(ALERT_SF, DEEP_DIVE_DATE)

vigente_banner = (
    f'<div class="vigente-banner">'
    f'<div style="font-size:12px;font-weight:700;color:#FFE600;text-transform:uppercase;letter-spacing:.6px;">Semana em andamento</div>'
    f'<div style="font-size:15px;font-weight:800;margin-top:3px;">{VIG_LABEL} (seg–hoje)</div>'
    f'<div style="font-size:12px;color:#aaa;margin-top:2px;">Comparado com semana fechada: {S1_LABEL} · Dados parciais</div>'
    f'</div>'
    + dd_block(
        DD_VIG_DATE,
        DD_VIG_POS_DRIVER, DD_VIG_POS_VAR, DD_VIG_POS_PROC, DD_VIG_POS_INSIGHTS,
        DD_VIG_NEG_DRIVER, DD_VIG_NEG_VAR, DD_VIG_NEG_PROC, DD_VIG_NEG_INSIGHTS,
        DD_VIG_ACO
    )
    + alert_dd_block(ALERT_VA, DD_VIG_DATE)
)

deep_dive_mes_html = (
    dd_block(
        DD_MES_DATE,
        DD_MES_POS_DRIVER, DD_MES_POS_VAR, DD_MES_POS_PROC, DD_MES_POS_INSIGHTS,
        DD_MES_NEG_DRIVER, DD_MES_NEG_VAR, DD_MES_NEG_PROC, DD_MES_NEG_INSIGHTS,
        DD_MES_ACO
    )
    + alert_dd_block(ALERT_MES, DD_MES_DATE)
)

def driver_dd_tab(wD_data, wP_data, mD_data, mP_data):
    """Deep Dive por Driver — executive brief, tabelas P/C/O/Sr, filtro de processo (driver_impact.html style)."""
    # ── 1. DD_BK ─────────────────────────────────────────────────
    def _to_bk(t):
        p,d,s=t[0],t[1],t[2]
        return {"p":p,"d":d,"s":s,"nps":round(100*(p-d)/s,1) if s>0 else None}
    dd_bk={}
    for drv in DRIVER_COLORS:
        p_data={}
        for pk,pd in [("S2",weekly_proc[drv].get("S2",{})),
                       ("S1",weekly_proc[drv].get("S1",{})),
                       ("M2",monthly_proc[drv].get("M2",{})),
                       ("M1",monthly_proc[drv].get("M1",{}))]:
            p_data[pk]={proc:_to_bk(v) for proc,v in pd.items()}
        sr_data={}
        if drv in seniority_weekly:
            for pk in ["S1","S2"]:
                if pk in seniority_weekly[drv]:
                    sr_data[pk]={}
                    for stype,key in [("Expert","EXPERT"),("Newbie","NEWBIE")]:
                        t=seniority_weekly[drv][pk].get(key,(0,0,0))
                        sr_data[pk][stype]=_to_bk(t)
        if drv in seniority_monthly:
            sr_data["M1"]={}
            for stype,key in [("Expert","EXPERT"),("Newbie","NEWBIE")]:
                t=seniority_monthly[drv].get(key,(0,0,0))
                sr_data["M1"][stype]=_to_bk(t)
        # Canal (C) e Oficina (O) de canal_weekly/monthly e oficina_weekly/monthly
        c_data={}
        for pk,cd in [("S2",canal_weekly.get(drv,{}).get("S2",{})),
                       ("S1",canal_weekly.get(drv,{}).get("S1",{})),
                       ("M2",canal_monthly.get(drv,{}).get("M2",{})),
                       ("M1",canal_monthly.get(drv,{}).get("M1",{}))]:
            c_data[pk]={canal:_to_bk(v) for canal,v in cd.items()}
        o_data={}
        for pk,od in [("S2",oficina_weekly.get(drv,{}).get("S2",{})),
                       ("S1",oficina_weekly.get(drv,{}).get("S1",{})),
                       ("M2",oficina_monthly.get(drv,{}).get("M2",{})),
                       ("M1",oficina_monthly.get(drv,{}).get("M1",{}))]:
            o_data[pk]={of:_to_bk(v) for of,v in od.items()}
        # P_C (processo × canal) e P_O (processo × oficina)
        pc_data={}
        for pk,pc_dict in [("S2",p_c_weekly.get(drv,{}).get("S2",{})),
                            ("S1",p_c_weekly.get(drv,{}).get("S1",{})),
                            ("M2",p_c_monthly.get(drv,{}).get("M2",{})),
                            ("M1",p_c_monthly.get(drv,{}).get("M1",{}))]:
            pc_data[pk]={proc:{canal:_to_bk(v) for canal,v in canal_dict.items()}
                         for proc,canal_dict in pc_dict.items()}
        po_data={}
        for pk,po_dict in [("S2",p_o_weekly.get(drv,{}).get("S2",{})),
                            ("S1",p_o_weekly.get(drv,{}).get("S1",{})),
                            ("M2",p_o_monthly.get(drv,{}).get("M2",{})),
                            ("M1",p_o_monthly.get(drv,{}).get("M1",{}))]:
            po_data[pk]={proc:{ofic:_to_bk(v) for ofic,v in ofic_dict.items()}
                         for proc,ofic_dict in po_dict.items()}
        dd_bk[drv]={"P":p_data,"C":c_data,"O":o_data,"Sr":sr_data,"Sr_P":{},"P_C":pc_data,"P_O":po_data}
    # ── 2. DRV_HIST ──────────────────────────────────────────────
    def _he(lbl,t):
        p,d,s=t[0],t[1],t[2]
        return {"label":lbl,"nps":round(100*(p-d)/s,2) if s>0 else None,"s":s}
    drv_hist={}
    for drv in DRIVER_COLORS:
        drv_hist[drv]={
            "target":DRIVER_TARGETS[drv],"cat":"Sellers",
            "weekly": [_he(lbl,weekly_history[drv].get(lbl,(0,0,0)))  for lbl in WEEK_LABELS  if lbl in weekly_history[drv]],
            "monthly":[_he(lbl,monthly_history[drv].get(lbl,(0,0,0))) for lbl in MONTH_LABELS if lbl in monthly_history[drv]],
        }
    # ── 3. DD_SUM ────────────────────────────────────────────────
    dd_sum={}
    # Preencher todos os 6 drivers com análise executiva framework completo (Seção 1G)
    for drv,insights in DRIVER_INSIGHTS_WOW.items():
        if drv not in dd_sum: dd_sum[drv]={}
        dd_sum[drv]["wow"]="\n".join("▶ "+i for i in insights)
    for drv,insights in DRIVER_INSIGHTS_MOM.items():
        if drv not in dd_sum: dd_sum[drv]={}
        dd_sum[drv]["mom"]="\n".join("▶ "+i for i in insights)
    # Sobrescrever os drivers destacados com análise qualitativa aprofundada + VoC + ações
    for drv,insights,key in [
        (DEEP_DIVE_POS_DRIVER, DEEP_DIVE_POS_INSIGHTS+DCEV_PROMOTORES+DCEV_ACOES, "wow"),
        (DEEP_DIVE_NEG_DRIVER, DEEP_DIVE_NEG_INSIGHTS+DCEV_DETRATORES+DCEV_ACOES, "wow"),
        (DD_MES_POS_DRIVER,    DD_MES_POS_INSIGHTS+DD_MES_PRO+DD_MES_ACO,         "mom"),
        (DD_MES_NEG_DRIVER,    DD_MES_NEG_INSIGHTS+DD_MES_DET+DD_MES_ACO,         "mom"),
    ]:
        if drv not in dd_sum: dd_sum[drv]={}
        dd_sum[drv][key]="\n".join("▶ "+i for i in insights)
    # ── 4. Serialize ─────────────────────────────────────────────
    bk_json  =_json.dumps(dd_bk)
    hist_json=_json.dumps(drv_hist)
    sum_json =_json.dumps(dd_sum)
    cfg_json =_json.dumps({"M1L":M1_LABEL,"M2L":M2_LABEL,"S1L":S1_LABEL,
                             "S2L":S2_LABEL,"VIGL":VIG_LABEL,
                             "TGT":DRIVER_TARGETS,"COLORS":DRIVER_COLORS,"SHORT":DRIVER_SHORT})
    opts="".join(f'<option value="{d}">{DRIVER_SHORT[d]}</option>' for d in DRIVER_COLORS)
    # ── 5. CSS ───────────────────────────────────────────────────
    css=(
        ".pill{display:inline-block;padding:2px 9px;border-radius:12px;font-weight:700;font-size:11px;white-space:nowrap}"
        ".pill-pos-hi{background:#e8f5e9;color:#1b5e20}.pill-pos-lo{background:#f1f8e9;color:#33691e}"
        ".pill-neg-hi{background:#ffebee;color:#b71c1c}.pill-dn1{background:#fff3e0;color:#e65100}"
        ".pill-dn2{background:#ffebee;color:#b71c1c}.pill-up1{background:#f1f8e9;color:#33691e}"
        ".pill-up2{background:#e8f5e9;color:#1b5e20}.pill-flat{background:#f5f5f5;color:#777}"
        ".pill-neu{background:#f5f5f5;color:#9e9e9e}"
        ".exec-brief{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1);margin-bottom:20px}"
        ".exec-brief-hdr{background:#1a1e3c;color:#fff;padding:14px 18px}"
        ".exec-brief-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}"
        ".exec-brief-drv{font-size:14px;font-weight:700}.exec-brief-per{font-size:11px;color:#aab4d4}"
        ".exec-brief-kpis{display:flex;gap:8px;flex-wrap:wrap}"
        ".exec-brief-kpi{background:rgba(255,255,255,.12);border-radius:7px;padding:6px 12px;display:flex;flex-direction:column;gap:2px}"
        ".exec-brief-kpi-lbl{font-size:9px;color:#aab4d4;text-transform:uppercase;letter-spacing:.5px}"
        ".exec-brief-kpi-val{font-size:17px;font-weight:700;line-height:1}"
        ".exec-brief-kpi-val.pos{color:#69f0ae}.exec-brief-kpi-val.neg{color:#ff8a80}.exec-brief-kpi-val.neutral{color:#fff}"
        ".exec-brief-body{display:grid;grid-template-columns:1fr 1fr}"
        ".exec-sec{padding:13px 16px;border-bottom:1px solid #f0f2f5;border-right:1px solid #f0f2f5}"
        ".exec-sec:nth-child(even){border-right:none}"
        ".exec-sec.fw{grid-column:1/-1;border-right:none}"
        ".exec-sec:last-child,.exec-sec:nth-last-child(2){border-bottom:none}"
        ".exec-sec-title{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;margin-bottom:8px}"
        ".exec-narr{font-size:12px;color:#333;line-height:1.65;margin:0 0 5px 0}"
        ".exec-bul{font-size:12px;color:#333;line-height:1.6;margin-bottom:5px;padding-left:4px}"
        ".exec-bul strong{color:#1a1e3c}.exec-na{font-size:12px;color:#aaa;font-style:italic}"
        ".dd2-pbar{display:flex;gap:6px;margin-bottom:16px}"
        ".dd2-pbtn{padding:7px 16px;border:1px solid var(--border);border-radius:8px;font-size:12px;font-weight:700;cursor:pointer;background:#fff;color:#888;transition:all .15s}"
        ".dd2-pbtn.active{background:var(--dark);color:#fff;border-color:var(--dark)}"
        ".dd2-bar{display:flex;align-items:center;gap:12px;margin-bottom:18px;background:#fff;border:1px solid var(--border);border-radius:10px;padding:12px 16px}"
        ".dd2-bar label{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;color:#888;white-space:nowrap}"
        ".dd2-bar select{flex:1;padding:7px 12px;border:1px solid #d0d5e0;border-radius:7px;font-size:14px;font-weight:600;color:var(--dark);background:#fafbff}"
        ".dd2-sc-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:18px}"
        ".dd2-sc{background:#fff;border-radius:10px;border:1px solid var(--border);padding:14px 16px}"
        ".dd2-sc .sc-lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#999;margin-bottom:6px}"
        ".dd2-sc .sc-val{font-size:26px;font-weight:800;line-height:1.1}"
        ".dd2-chart-sec{background:#fff;border-radius:12px;padding:16px 20px;box-shadow:0 1px 4px rgba(0,0,0,.07);margin-bottom:16px}"
        ".dd2-chart-title{font-size:13px;font-weight:700;color:#1a1e3c;margin-bottom:3px}"
        ".dd2-chart-sub{font-size:11px;color:#888;margin-bottom:10px}"
        ".dd2-chart-wrap{position:relative;height:250px}"
        ".dd-sec-title{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.6px;margin:20px 0 8px;padding-bottom:6px;border-bottom:1px solid #eee}"
        ".bk-wrap2{overflow-x:auto;margin-bottom:10px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.06)}"
        ".bk-tbl2{width:100%;border-collapse:collapse;background:#fff;font-size:12px;table-layout:fixed}"
        ".bk-tbl2 thead tr{background:#f5f6fa;border-bottom:2px solid #e0e2ee}"
        ".bk-tbl2 thead th{color:#666;padding:7px 9px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;text-align:center}"
        ".bk-tbl2 thead th.cn{text-align:left;color:#1a1e3c}"
        ".bk-tbl2 tbody td{padding:6px 9px;border-bottom:1px solid #f2f2f5;vertical-align:middle;white-space:nowrap;text-align:center;color:#333}"
        ".bk-tbl2 tbody td.cn{text-align:left;white-space:normal;word-break:break-word;color:#1a1e3c;font-weight:500}"
        ".bk-tbl2 tbody tr:hover td{background:#fafbff}"
        ".bk-tbl2 tr.bkt td{background:#f0f2f8;font-weight:700;border-top:2px solid #dde0ea;color:#1a1e3c}"
        ".bk-sv2{color:#bbb!important;font-size:11px!important}"
        ".dd2-empty{background:#fff;border-radius:10px;border:1px solid var(--border);padding:40px;text-align:center;color:#bbb;font-size:14px}"
        ".dd2-fb{display:flex;align-items:center;gap:10px;margin:12px 0 6px;padding:7px 12px;background:#f5f7ff;border-radius:8px;border:1px solid #dde2f0}"
        ".dd2-fb span{font-size:12px;font-weight:600;color:#3a3f6b;white-space:nowrap}"
        ".dd2-fsel{flex:1;max-width:320px;padding:6px 10px;border:1px solid #d0d5e0;border-radius:6px;font-size:13px}"
    )
    # ── 6. JS ────────────────────────────────────────────────────
    js_data = (
        '<script id="_ddd_bk"   type="application/json">'+bk_json  +'</script>\n'
        +'<script id="_ddd_hist" type="application/json">'+hist_json+'</script>\n'
        +'<script id="_ddd_sum"  type="application/json">'+sum_json +'</script>\n'
        +'<script id="_ddd_cfg"  type="application/json">'+cfg_json +'</script>\n'
    )
    js_code = (
        "<script>\n(function(){\n"
        "var BK=JSON.parse(document.getElementById('_ddd_bk').textContent);\n"
        "var HST=JSON.parse(document.getElementById('_ddd_hist').textContent);\n"
        "var SUM=JSON.parse(document.getElementById('_ddd_sum').textContent);\n"
        "var CFG=JSON.parse(document.getElementById('_ddd_cfg').textContent);\n"
        "var M1L=CFG.M1L,M2L=CFG.M2L,S1L=CFG.S1L,S2L=CFG.S2L,VIGL=CFG.VIGL;\n"
        "var TGT=CFG.TGT,COLORS=CFG.COLORS,SHORT=CFG.SHORT;\n"
        "var _per='w',_ch2={};\n"
        "function _f2(v){return v==null?'—':v.toFixed(2).replace('.',',');}\n"
        "function _f1(v){return v==null?'—':v.toFixed(1)+'%';}\n"
        "function _lbl2(p){return p==='M2'?M2L:p==='M1'?M1L:p==='S2'?S2L:p==='S1'?S1L:p==='VIG'?VIGL+' &#9889;':p;}\n"
        "function _clr2(v){return v>=0?'#1a7a1a':'#c0321a';}\n"
        "function _tag2(v,d){var s=(v>=0?'+':'')+v.toFixed(d||2)+' pp';\n"
        "  return '<span style=\"font-weight:700;color:'+_clr2(v)+'\">' +s+'</span>';}\n"
        "function pill2(v){\n"
        "  if(v==null)return'<span class=\"pill pill-neu\">—</span>';\n"
        "  var s=(v>=0?'+':'')+v.toFixed(2)+' pp';\n"
        "  var c=v>=1?'pill-pos-hi':v>=0?'pill-pos-lo':v>=-1?'pill-dn1':'pill-neg-hi';\n"
        "  return'<span class=\"pill '+c+'\">'+s+'</span>';}\n"
        "function pillT2(v){\n"
        "  if(v==null)return'<span class=\"pill pill-neu\">—</span>';\n"
        "  if(v>=3)   return'<span class=\"pill pill-up2\">&#8679;&#8679; Em alta</span>';\n"
        "  if(v>=0.5) return'<span class=\"pill pill-up1\">&#8679; Evolução</span>';\n"
        "  if(v>-0.5) return'<span class=\"pill pill-flat\">&#8594; Estável</span>';\n"
        "  if(v>-3)   return'<span class=\"pill pill-dn1\">&#8681; Queda</span>';\n"
        "  return'<span class=\"pill pill-dn2\">&#8681;&#8681; Em queda</span>';}\n"
        "function pillVT2(nps,tgt2){\n"
        "  if(nps==null||!tgt2)return'<span class=\"pill pill-neu\">—</span>';\n"
        "  var g=nps-tgt2,s=(g>=0?'+':'')+g.toFixed(2)+' pp';\n"
        "  return'<span class=\"pill '+(g>=0?'pill-pos-hi':'pill-neg-hi')+'\">'+s+'</span>';}\n"
        "function pillImp2(v){\n"
        "  if(v==null||v===0)return'<span class=\"pill pill-neu\">0,00 pp</span>';\n"
        "  var s=(v>=0?'+':'')+v.toFixed(2)+' pp';\n"
        "  var c=v>=0.3?'pill-pos-hi':v>=0.05?'pill-pos-lo':v<=-0.3?'pill-neg-hi':v<=-0.05?'pill-dn1':'pill-neu';\n"
        "  return'<span class=\"pill '+c+'\">'+s+'</span>';}\n"
        "function sc2dd(lbl,val,delta,nps,tgt2){\n"
        "  var c=nps!=null&&tgt2?(nps>=tgt2?'#1a7a1a':'#c0321a'):delta!=null?(delta>=0?'#1a7a1a':'#c0321a'):'#bf5c00';\n"
        "  return'<div class=\"dd2-sc\"><div class=\"sc-lbl\">'+lbl+'</div>'\n"
        "        +'<div class=\"sc-val\" style=\"color:'+c+'\">'+val+'</div></div>';}\n"
        "function bkTbl2(bk,dim,pA,pB,tgt2,lbl){\n"
        "  var dd=(bk&&bk[dim])||{};\n"
        "  var dA=dd[pA]||{},dB=dd[pB]||{};\n"
        "  var keys=Array.from(new Set(Object.keys(dA).concat(Object.keys(dB))));\n"
        "  if(!keys.length)return'<div class=\"dd2-empty\" style=\"padding:16px;font-size:12px;color:#aaa\">Sem dados para esta abertura</div>';\n"
        "  var lA=_lbl2(pA),lB=_lbl2(pB);\n"
        "  var tA={p:0,d:0,s:0},tB={p:0,d:0,s:0};\n"
        "  keys.forEach(function(k){var a=dA[k]||{};var b=dB[k]||{};tA.p+=a.p||0;tA.d+=a.d||0;tA.s+=a.s||0;tB.p+=b.p||0;tB.d+=b.d||0;tB.s+=b.s||0;});\n"
        "  var nA=tA.s>0?(tA.p-tA.d)/tA.s*100:null,nB=tB.s>0?(tB.p-tB.d)/tB.s*100:null;\n"
        "  var items=keys.map(function(k){\n"
        "    var a=dA[k]||{p:0,d:0,s:0,nps:null},b=dB[k]||{p:0,d:0,s:0,nps:null};\n"
        "    var shA=tA.s>0?(a.s||0)/tA.s:0,shB=tB.s>0?(b.s||0)/tB.s:0;\n"
        "    var neto=shA>0&&a.nps!=null&&b.nps!=null?shA*(b.nps-a.nps):0;\n"
        "    var mix=b.nps!=null&&nB!=null?(shB-shA)*(b.nps-nB):0;\n"
        "    return{k:k,a:a,b:b,shB:shB,imp:Math.round((neto+mix)*100)/100};});\n"
        "  items.sort(function(x,y){return Math.abs(y.imp)-Math.abs(x.imp);});\n"
        "  var h='<div class=\"bk-wrap2\"><table class=\"bk-tbl2\"><colgroup>'\n"
        "        +'<col style=\"width:24%\"><col style=\"width:9%\"><col style=\"width:9%\">'\n"
        "        +'<col style=\"width:11%\"><col style=\"width:9%\"><col style=\"width:7%\">'\n"
        "        +'<col style=\"width:11%\"><col style=\"width:10%\"><col style=\"width:10%\"></colgroup>'\n"
        "        +'<thead><tr><th class=\"cn\">'+(lbl||'Dimensão')+'</th>'\n"
        "        +'<th>'+lA+'</th><th>'+lB+'</th><th>&#916;NPS</th>'\n"
        "        +'<th>Surveys</th><th>Share</th><th>Impacto</th><th>VS Target</th><th>Tend.</th>'\n"
        "        +'</tr></thead><tbody>';\n"
        "  var totI=0;\n"
        "  items.forEach(function(it){\n"
        "    var d2=it.a.nps!=null&&it.b.nps!=null?Math.round((it.b.nps-it.a.nps)*100)/100:null;\n"
        "    totI+=it.imp;\n"
        "    h+='<tr><td class=\"cn\">'+it.k+'</td>'\n"
        "      +'<td>'+_f1(it.a.nps)+'</td><td>'+_f1(it.b.nps)+'</td>'\n"
        "      +'<td>'+pill2(d2)+'</td>'\n"
        "      +'<td class=\"bk-sv2\">'+(it.b.s||0).toLocaleString('pt-BR')+'</td>'\n"
        "      +'<td class=\"bk-sv2\">'+(it.shB*100).toFixed(1)+'%</td>'\n"
        "      +'<td>'+pillImp2(it.imp)+'</td>'\n"
        "      +'<td>'+pillVT2(it.b.nps,tgt2)+'</td>'\n"
        "      +'<td>'+pillT2(d2)+'</td></tr>';});\n"
        "  totI=Math.round(totI*100)/100;\n"
        "  var dT=nA!=null&&nB!=null?Math.round((nB-nA)*100)/100:null;\n"
        "  h+='<tr class=\"bkt\"><td class=\"cn\">Total driver</td>'\n"
        "    +'<td>'+_f1(nA)+'</td><td>'+_f1(nB)+'</td>'\n"
        "    +'<td>'+pill2(dT)+'</td>'\n"
        "    +'<td class=\"bk-sv2\">'+(tB.s||0).toLocaleString('pt-BR')+'</td>'\n"
        "    +'<td class=\"bk-sv2\">100%</td>'\n"
        "    +'<td>'+pillImp2(totI)+'</td>'\n"
        "    +'<td>'+pillVT2(nB,tgt2)+'</td>'\n"
        "    +'<td>'+pillT2(dT)+'</td></tr>';\n"
        "  return h+'</tbody></table></div>';}\n"
        "function srTbl2(bk,pA,pB,tgt2){\n"
        "  var sr=(bk&&bk.Sr)||{};\n"
        "  var dA=sr[pA]||{},dB=sr[pB]||{};\n"
        "  var lA=_lbl2(pA),lB=_lbl2(pB);\n"
        "  function nS(v){return v!=null?v.toFixed(1)+'%':'—';}\n"
        "  function pG2(g){if(g==null)return'<span style=\"color:#888\">—</span>';\n"
        "    var ab=Math.abs(g),col=ab>10?'#b71c1c':ab>5?'#e65100':'#2e7d32';\n"
        "    return'<span style=\"font-weight:600;color:'+col+'\">'+(g>=0?'+':'')+g.toFixed(1)+'pp</span>';}\n"
        "  var rows=[{k:'&#127775; Expert',key:'Expert'},{k:'&#128164; Newbie',key:'Newbie'}];\n"
        "  var h='<div class=\"bk-wrap2\"><table class=\"bk-tbl2\"><colgroup>'\n"
        "        +'<col style=\"width:22%\"><col style=\"width:14%\"><col style=\"width:14%\">'\n"
        "        +'<col style=\"width:13%\"><col style=\"width:12%\"><col style=\"width:13%\"></colgroup>'\n"
        "        +'<thead><tr><th class=\"cn\">Senioridade</th><th>'+lA+'</th><th>'+lB+'</th>'\n"
        "        +'<th>&#916;NPS</th><th>Surveys</th><th>vs Target</th></tr></thead><tbody>';\n"
        "  var eNB=null,nNB=null;\n"
        "  rows.forEach(function(r){\n"
        "    var a=(dA[r.key]||{}),b=(dB[r.key]||{});\n"
        "    var nA2=a.nps,nB2=b.nps;\n"
        "    if(r.key==='Expert')eNB=nB2; else nNB=nB2;\n"
        "    var d2=nA2!=null&&nB2!=null?Math.round((nB2-nA2)*100)/100:null;\n"
        "    h+='<tr><td class=\"cn\">'+r.k+'</td>'\n"
        "      +'<td>'+nS(nA2)+'</td><td>'+nS(nB2)+'</td>'\n"
        "      +'<td>'+pill2(d2)+'</td>'\n"
        "      +'<td class=\"bk-sv2\">'+(b.s||0)+'</td>'\n"
        "      +'<td>'+pillVT2(nB2,tgt2)+'</td></tr>';});\n"
        "  var gap=eNB!=null&&nNB!=null?Math.round((eNB-nNB)*100)/100:null;\n"
        "  h+='<tr class=\"bkt\"><td class=\"cn\">Gap E−N ('+lB+')</td>'\n"
        "    +'<td colspan=\"2\" style=\"font-weight:600\">'+pG2(gap)+'</td><td colspan=\"3\"></td></tr>';\n"
        "  return h+'</tbody></table></div>';}\n"
        "function execBrief2(drv,pA,pB,bk){\n"
        "  var lA=_lbl2(pA),lB=_lbl2(pB),tgt2=TGT[drv];\n"
        "  var hist=HST[drv],histArr=pA==='M2'?hist.monthly:hist.weekly;\n"
        "  var nB2=histArr&&histArr.length>0?histArr[histArr.length-1].nps:null;\n"
        "  var nA2=histArr&&histArr.length>1?histArr[histArr.length-2].nps:null;\n"
        "  var delta=nA2!=null&&nB2!=null?Math.round((nB2-nA2)*100)/100:null;\n"
        "  var gapTgt=nB2!=null&&tgt2?Math.round((nB2-tgt2)*100)/100:null;\n"
        "  function kC(v){return v==null?'neutral':v>=0?'pos':'neg';}\n"
        "  var kpis='<div class=\"exec-brief-kpis\">'\n"
        "    +'<div class=\"exec-brief-kpi\"><div class=\"exec-brief-kpi-lbl\">NPS '+lB+'</div>'\n"
        "    +'<div class=\"exec-brief-kpi-val '+kC(gapTgt)+'\">'+(nB2!=null?nB2.toFixed(1)+'%':'—')+'</div></div>'\n"
        "    +'<div class=\"exec-brief-kpi\"><div class=\"exec-brief-kpi-lbl\">Var. '+(pA==='M2'?'MoM':'WoW')+'</div>'\n"
        "    +'<div class=\"exec-brief-kpi-val '+kC(delta)+'\">'+(delta!=null?(delta>=0?'+':'')+delta.toFixed(2)+' pp':'—')+'</div></div>'\n"
        "    +'<div class=\"exec-brief-kpi\"><div class=\"exec-brief-kpi-lbl\">Gap vs Target</div>'\n"
        "    +'<div class=\"exec-brief-kpi-val '+kC(gapTgt)+'\">'+(gapTgt!=null?(gapTgt>=0?'+':'')+gapTgt.toFixed(2)+' pp':'—')+'</div></div>'\n"
        "    +'</div>';\n"
        "  var pdP=(bk&&bk.P)||{};\n"
        "  var dPA=pdP[pA]||{},dPB=pdP[pB]||{};\n"
        "  var pKeys=Array.from(new Set(Object.keys(dPA).concat(Object.keys(dPB))));\n"
        "  var totSA=0,totSB=0,totPB=0,totDB=0;\n"
        "  pKeys.forEach(function(k){var a=dPA[k]||{s:0};var b=dPB[k]||{s:0,p:0,d:0};totSA+=a.s||0;totSB+=b.s||0;totPB+=b.p||0;totDB+=b.d||0;});\n"
        "  var npsAll=totSB>0?(totPB-totDB)/totSB*100:null;\n"
        "  var procs=pKeys.map(function(k){\n"
        "    var a=dPA[k]||{p:0,d:0,s:0,nps:null},b=dPB[k]||{p:0,d:0,s:0,nps:null};\n"
        "    var shA=totSA>0?(a.s||0)/totSA:0,shB=totSB>0?(b.s||0)/totSB:0;\n"
        "    var neto=shA>0&&a.nps!=null&&b.nps!=null?shA*(b.nps-a.nps):0;\n"
        "    var mix=b.nps!=null&&npsAll!=null?(shB-shA)*(b.nps-npsAll):0;\n"
        "    var imp=Math.round((neto+mix)*100)/100;\n"
        "    var gapT=tgt2!=null&&b.nps!=null?Math.round((b.nps-tgt2)*100)/100:null;\n"
        "    var dlt=a.nps!=null&&b.nps!=null?Math.round((b.nps-a.nps)*100)/100:null;\n"
        "    return{k:k,nA:a.nps,nB:b.nps,sB:b.s||0,imp:imp,gapT:gapT,dlt:dlt,shB:Math.round(shB*1000)/10};\n"
        "  }).filter(function(x){return x.sB>0||x.nB!=null;}).sort(function(a,b){return a.imp-b.imp;});\n"
        "  var top3neg=procs.filter(function(p){return p.imp<0;}).slice(0,3);\n"
        "  var top2pos=procs.filter(function(p){return p.imp>0;}).slice(-2).reverse();\n"
        "  var s1='<div class=\"exec-sec-title\" style=\"color:#1a73e8\">&#128201; Variação '+(pA==='M2'?'MoM':'WoW')+'</div>';\n"
        "  s1+='<p class=\"exec-narr\">NPS '+(delta!=null?(delta>=0?'subiu':'caiu')+' '+Math.abs(delta).toFixed(2)+'pp':'variou')\n"
        "      +' de '+(nA2!=null?nA2.toFixed(1)+'%':'—')+' ('+lA+') para '+(nB2!=null?nB2.toFixed(1)+'%':'—')+' ('+lB+')';\n"
        "  if(top3neg.length)s1+='. Pressiona: '+top3neg.map(function(p){return'<b>'+p.k.substring(0,28)+'</b> ('+_tag2(p.imp)+', NPS '+_f1(p.nB)+')';}).join('; ');\n"
        "  if(top2pos.length)s1+=' | Compensa: '+top2pos.map(function(p){return'<b>'+p.k.substring(0,22)+'</b> ('+_tag2(p.imp)+')';}).join(', ');\n"
        "  s1+='.</p>';\n"
        "  var s2='<div class=\"exec-sec-title\" style=\"color:#bf5c00\">&#127919; Análise vs Target</div>';\n"
        "  if(procs.length&&tgt2!=null){\n"
        "    var abT=procs.filter(function(p){return p.gapT!=null&&p.gapT<0;}).sort(function(a,b){return a.gapT-b.gapT;});\n"
        "    var acT=procs.filter(function(p){return p.gapT!=null&&p.gapT>=0;}).sort(function(a,b){return b.gapT-a.gapT;});\n"
        "    var gapStr=(gapTgt>=0?'+':'')+_f2(gapTgt)+'pp '+(gapTgt>=0?'acima':'abaixo');\n"
        "    var gapCl=gapTgt>=0?'#1a7a1a':'#c0321a';\n"
        "    s2+='<p class=\"exec-narr\">Driver <b style=\"color:'+gapCl+'\">'+gapStr+'</b> do target ('+tgt2.toFixed(1)+'%).';\n"
        "    if(abT.length)s2+=' Processos pressionando: '+abT.slice(0,3).map(function(p){return'<b>'+p.k.substring(0,26)+'</b> ('+p.gapT.toFixed(1)+'pp, NPS '+_f1(p.nB)+')';}).join('; ')+'.';\n"
        "    if(acT.length&&abT.length)s2+=' Positivos: '+acT.slice(0,2).map(function(p){return'<b>'+p.k.substring(0,20)+'</b> (+'+p.gapT.toFixed(1)+'pp)';}).join(', ')+'.';\n"
        "    if(abT.length===0)s2+=' Todos acima do target.';\n"
        "    s2+='</p>';\n"
        "  }else s2+='<p class=\"exec-narr exec-na\">Sem dados de processo.</p>';\n"
        "  var procsMix=pKeys.map(function(k){\n"
        "    var a=dPA[k]||{s:0,nps:null},b=dPB[k]||{s:0,nps:null};\n"
        "    var shA=totSA>0?(a.s||0)/totSA:0,shB=totSB>0?(b.s||0)/totSB:0;\n"
        "    var neto=shA>0&&a.nps!=null&&b.nps!=null?Math.round(shA*(b.nps-a.nps)*100)/100:0;\n"
        "    var mix=b.nps!=null&&npsAll!=null?Math.round((shB-shA)*(b.nps-npsAll)*100)/100:0;\n"
        "    return{k:k,neto:neto,mix:mix,dSha:Math.round((shB-shA)*1000)/10,nB:b.nps,sB:b.s||0,abvAvg:b.nps!=null&&npsAll!=null?b.nps>npsAll:null};\n"
        "  }).filter(function(x){return x.sB>0;});\n"
        "  var totN=Math.round(procsMix.reduce(function(s,p){return s+p.neto;},0)*100)/100;\n"
        "  var totM=Math.round(procsMix.reduce(function(s,p){return s+p.mix;},0)*100)/100;\n"
        "  var badMix=procsMix.filter(function(p){return p.dSha>0.5&&p.abvAvg===false&&p.mix<-0.05;}).sort(function(a,b){return a.mix-b.mix;}).slice(0,3);\n"
        "  var s3='<div class=\"exec-sec-title\" style=\"color:#546e7a\">&#128257; Mix de Pesquisas</div>';\n"
        "  s3+='<p class=\"exec-narr\">NETO (qualidade): <strong style=\"color:'+_clr2(totN)+'\">'+(totN>=0?'+':'')+totN.toFixed(2)+'pp</strong> &nbsp;|&nbsp; MIX (volume): <strong style=\"color:'+_clr2(totM)+'\">'+(totM>=0?'+':'')+totM.toFixed(2)+'pp</strong>.';\n"
        "  if(badMix.length)s3+=' Volume cresceu em processos abaixo da média: '+badMix.map(function(p){return'<b>'+p.k.substring(0,22)+'</b> (+'+p.dSha.toFixed(1)+'pp) → '+_tag2(p.mix);}).join('; ')+'.';\n"
        "  else s3+=' Sem redistribuição significativa de volume.';\n"
        "  s3+='</p>';\n"
        "  var srD=(bk&&bk.Sr)||{},srB2=srD[pB]||{},srA2=srD[pA]||{};\n"
        "  var expB2=srB2.Expert||{},nwbB2=srB2.Newbie||{};\n"
        "  var expA2=srA2.Expert||{},nwbA2=srA2.Newbie||{};\n"
        "  var eDlt=expA2.nps!=null&&expB2.nps!=null?Math.round((expB2.nps-expA2.nps)*100)/100:null;\n"
        "  var nDlt=nwbA2.nps!=null&&nwbB2.nps!=null?Math.round((nwbB2.nps-nwbA2.nps)*100)/100:null;\n"
        "  var gapE=expB2.nps!=null&&nwbB2.nps!=null?Math.round((expB2.nps-nwbB2.nps)*100)/100:null;\n"
        "  var s4='<div class=\"exec-sec-title\" style=\"color:#7b1fa2\">&#127891; Senioridade — Expert vs Newbie</div>';\n"
        "  if(expB2.nps!=null||nwbB2.nps!=null){\n"
        "    s4+='<p class=\"exec-narr\">&#127775; <b>Expert</b>: NPS '+(expB2.nps!=null?expB2.nps.toFixed(1)+'%':'—')\n"
        "       +(eDlt!=null?' ('+_tag2(eDlt,1)+' vs '+lA+')':'')\n"
        "       +' &bull; <span class=\"bk-sv2\">'+(expB2.s||0).toLocaleString('pt-BR')+' surveys</span></p>'\n"
        "      +'<p class=\"exec-narr\">&#128164; <b>Newbie</b>: NPS '+(nwbB2.nps!=null?nwbB2.nps.toFixed(1)+'%':'—')\n"
        "       +(nDlt!=null?' ('+_tag2(nDlt,1)+' vs '+lA+')':'')\n"
        "       +' &bull; <span class=\"bk-sv2\">'+(nwbB2.s||0).toLocaleString('pt-BR')+' surveys</span></p>'\n"
        "      +(gapE!=null?'<p class=\"exec-narr\">Gap E−N: <strong style=\"color:'+(Math.abs(gapE)>5?'#c0321a':'#1a7a1a')+'\">'+(gapE>=0?'+':'')+gapE.toFixed(1)+'pp</strong></p>':'');\n"
        "  }else s4+='<p class=\"exec-narr exec-na\">Sem dados de senioridade.</p>';\n"
        "  var isMes2=pA==='M2';\n"
        "  var sumObj=SUM[drv]||{};\n"
        "  var sumRaw=isMes2?(sumObj.mom||sumObj.wow):(sumObj.wow||sumObj.mom);\n"
        "  var bullets2=sumRaw?sumRaw.split('\\n').map(function(b){return b.replace(/^[\\s▶]+/,'').trim();}).filter(function(b){return b.length>10;}):[];\n"
        "  var s5='<div class=\"exec-sec-title fw\" style=\"color:#c0321a\">&#128139; Insights de Atendimento</div>';\n"
        "  if(bullets2.length){\n"
        "    s5+=bullets2.slice(0,6).map(function(b){\n"
        "      var ci=b.indexOf(':');\n"
        "      if(ci>0&&ci<50)b='<strong>'+b.substring(0,ci+1)+'</strong>'+b.substring(ci+1);\n"
        "      return'<div class=\"exec-bul\">&#9658; '+b+'</div>';}).join('');\n"
        "  }else s5+='<p class=\"exec-narr exec-na\">Análise qualitativa não disponível.</p>';\n"
        "  return'<div class=\"exec-brief\">'\n"
        "    +'<div class=\"exec-brief-hdr\">'\n"
        "      +'<div class=\"exec-brief-top\"><div><div class=\"exec-brief-drv\">Resumo Executivo — '+drv+'</div>'\n"
        "      +'<div class=\"exec-brief-per\">'+lA+' → '+lB+'</div></div>'\n"
        "      +kpis+'</div></div>'\n"
        "    +'<div class=\"exec-brief-body\">'\n"
        "      +'<div class=\"exec-sec\">'+s1+'</div>'\n"
        "      +'<div class=\"exec-sec\">'+s2+'</div>'\n"
        "      +'<div class=\"exec-sec\">'+s3+'</div>'\n"
        "      +'<div class=\"exec-sec\">'+s4+'</div>'\n"
        "      +'<div class=\"exec-sec fw\">'+s5+'</div>'\n"
        "    +'</div></div>';}\n"
        "function renderBkTbl2(el){\n"
        "  var drv=el.getAttribute('data-drv'),pA=el.getAttribute('data-pa'),pB=el.getAttribute('data-pb');\n"
        "  var tgt2=el.getAttribute('data-tgt');tgt2=tgt2?parseFloat(tgt2):null;\n"
        "  var proc=el.value,lsuf=el.getAttribute('data-lsuf');\n"
        "  var tblId='bk2-'+drv.replace(/ /g,'-');\n"
        "  var cont=document.getElementById(tblId);\n"
        "  if(!cont)return;\n"
        "  var bk=BK[drv],h='';\n"
        "  h+='<div class=\"dd-sec-title\">Processos — '+lsuf+'</div>';\n"
        "  h+=bkTbl2(bk,'P',pA,pB,tgt2,'Processo');\n"
        "  if(!proc){\n"
        "    h+='<div class=\"dd-sec-title\">Canal — '+lsuf+'</div>';\n"
        "    h+=bkTbl2(bk,'C',pA,pB,tgt2,'Canal');\n"
        "    h+='<div class=\"dd-sec-title\">Oficina — '+lsuf+'</div>';\n"
        "    h+=bkTbl2(bk,'O',pA,pB,tgt2,'Oficina');\n"
        "    h+='<div class=\"dd-sec-title\">Senioridade — '+lsuf+'</div>';\n"
        "    h+=srTbl2(bk,pA,pB,tgt2);\n"
        "  }else{\n"
        "    var pcA=(bk&&bk.P_C&&bk.P_C[pA]&&bk.P_C[pA][proc])||{};\n"
        "    var pcB=(bk&&bk.P_C&&bk.P_C[pB]&&bk.P_C[pB][proc])||{};\n"
        "    var poA=(bk&&bk.P_O&&bk.P_O[pA]&&bk.P_O[pA][proc])||{};\n"
        "    var poB=(bk&&bk.P_O&&bk.P_O[pB]&&bk.P_O[pB][proc])||{};\n"
        "    var mC={C:{}},mO={O:{}};\n"
        "    mC.C[pA]=pcA;mC.C[pB]=pcB;mO.O[pA]=poA;mO.O[pB]=poB;\n"
        "    h+='<div class=\"dd-sec-title\">Canal — '+proc+' ('+lsuf+')</div>';\n"
        "    h+=bkTbl2(mC,'C',pA,pB,tgt2,'Canal');\n"
        "    h+='<div class=\"dd-sec-title\">Oficina — '+proc+' ('+lsuf+')</div>';\n"
        "    h+=bkTbl2(mO,'O',pA,pB,tgt2,'Oficina');\n"
        "    var srPa=(bk&&bk.Sr_P&&bk.Sr_P[pA]&&bk.Sr_P[pA][proc])||{};\n"
        "    var srPb=(bk&&bk.Sr_P&&bk.Sr_P[pB]&&bk.Sr_P[pB][proc])||{};\n"
        "    var mSr={Sr:{}};mSr.Sr[pA]=srPa;mSr.Sr[pB]=srPb;\n"
        "    h+='<div class=\"dd-sec-title\">Senioridade — '+proc+' ('+lsuf+')</div>';\n"
        "    h+=srTbl2(mSr,pA,pB,tgt2);}\n"
        "  cont.innerHTML=h;}\n"
        "window.renderBkTbl2=renderBkTbl2;\n"
        "window.setDDPer2=function(btn,p){\n"
        "  _per=p;\n"
        "  document.querySelectorAll('.dd2-pbtn').forEach(function(b){b.classList.remove('active');});\n"
        "  btn.classList.add('active');\n"
        "  window.renderDDDrv2();};\n"
        "window.renderDDDrv2=function(){\n"
        "  var drv=document.getElementById('dd2-drv-sel').value;\n"
        "  var cont=document.getElementById('dd2-drv-cont');\n"
        "  if(!drv){cont.innerHTML='<div class=\"dd2-empty\">Selecione um driver acima para ver a análise detalhada</div>';return;}\n"
        "  var isW=_per==='w',pA=isW?'S2':'M2',pB=isW?'S1':'M1';\n"
        "  var bk=BK[drv],hist=HST[drv],tgt2=TGT[drv],color=COLORS[drv],short2=SHORT[drv];\n"
        "  var histArr=isW?hist.weekly:hist.monthly;\n"
        "  var cur=histArr[histArr.length-1],prev=histArr[histArr.length-2];\n"
        "  var nCur=cur?cur.nps:null,nPrev=prev?prev.nps:null;\n"
        "  var delta=nCur!=null&&nPrev!=null?+(nCur-nPrev).toFixed(2):null;\n"
        "  var gapTgt=nCur!=null&&tgt2?+(nCur-tgt2).toFixed(2):null;\n"
        "  var lA=_lbl2(pA),lB=_lbl2(pB);\n"
        "  var sc='<div class=\"dd2-sc-grid\">'\n"
        "    +sc2dd('NPS '+lB,nCur!=null?nCur.toFixed(1)+'%':'—',null,nCur,tgt2)\n"
        "    +sc2dd('NPS '+lA,nPrev!=null?nPrev.toFixed(1)+'%':'—',null,nPrev,tgt2)\n"
        "    +sc2dd(isW?'Var. WoW':'Var. MoM',delta!=null?(delta>=0?'+':'')+delta.toFixed(2)+' pp':'—',delta,null,null)\n"
        "    +sc2dd('Target',tgt2?tgt2.toFixed(1)+'%':'—',null,null,null)\n"
        "    +sc2dd('Gap vs Target',gapTgt!=null?(gapTgt>=0?'+':'')+gapTgt.toFixed(2)+' pp':'—',gapTgt,null,null)\n"
        "    +'</div>';\n"
        "  var brief=execBrief2(drv,pA,pB,bk);\n"
        "  var cid='ddc2_'+Date.now();\n"
        "  var hl=histArr.map(function(x){return x.label;}),hd=histArr.map(function(x){return x.nps;});\n"
        "  var clrs=hd.map(function(v){return tgt2&&v!=null&&v<tgt2?'rgba(210,45,45,0.82)':'rgba(30,65,150,0.82)';});\n"
        "  var chart='<div class=\"dd2-chart-sec\">'\n"
        "    +'<div class=\"dd2-chart-title\">Histórico '+(isW?'Semanal':'Mensal')+' — '+drv+'</div>'\n"
        "    +'<div class=\"dd2-chart-sub\">NPS vs target do driver</div>'\n"
        "    +'<div class=\"dd2-chart-wrap\"><canvas id=\"'+cid+'\"></canvas></div></div>';\n"
        "  var tblId='bk2-'+drv.replace(/ /g,'-');\n"
        "  var pKeys2=(BK[drv]&&BK[drv].P&&BK[drv].P[pB])?Object.keys(BK[drv].P[pB]).sort():[];\n"
        "  var fOpts='<option value=\"\">Todos os processos</option>'\n"
        "    +pKeys2.map(function(p){return'<option value=\"'+p.replace(/\"/g,'&quot;')+'\">'+p+'</option>';}).join('');\n"
        "  var lsuf2=(isW?lA+' vs '+lB:'MoM ('+lA+' vs '+lB+')');\n"
        "  var fb='<div class=\"dd2-fb\"><span>&#128269; Filtrar por processo:</span>'\n"
        "    +'<select class=\"dd2-fsel\" onchange=\"renderBkTbl2(this)\" data-drv=\"'+drv+'\" data-pa=\"'+pA+'\" data-pb=\"'+pB+'\" data-tgt=\"'+(tgt2||'')+'\" data-lsuf=\"'+lsuf2+'\">'\n"
        "    +fOpts+'</select></div>';\n"
        "  var initT='<div class=\"dd-sec-title\">Processos — '+lsuf2+'</div>'\n"
        "    +bkTbl2(BK[drv],'P',pA,pB,tgt2,'Processo')\n"
        "    +'<div class=\"dd-sec-title\">Canal — '+lsuf2+'</div>'\n"
        "    +bkTbl2(BK[drv],'C',pA,pB,tgt2,'Canal')\n"
        "    +'<div class=\"dd-sec-title\">Oficina — '+lsuf2+'</div>'\n"
        "    +bkTbl2(BK[drv],'O',pA,pB,tgt2,'Oficina')\n"
        "    +'<div class=\"dd-sec-title\">Senioridade — '+lsuf2+'</div>'\n"
        "    +srTbl2(BK[drv],pA,pB,tgt2);\n"
        "  cont.innerHTML=sc+brief+chart+fb+'<div id=\"'+tblId+'\">'+initT+'</div>';\n"
        "  Object.keys(_ch2).forEach(function(k){try{_ch2[k].destroy();}catch(e){}delete _ch2[k];});\n"
        "  var ctx=document.getElementById(cid);\n"
        "  if(ctx){\n"
        "    var allV=hd.filter(function(v){return v!=null;}).concat(tgt2?[tgt2]:[]);\n"
        "    var yMin=allV.length?Math.floor(Math.min.apply(null,allV))-5:0;\n"
        "    var yMax=allV.length?Math.ceil(Math.max.apply(null,allV))+5:100;\n"
        "    _ch2[cid]=new Chart(ctx,{type:'bar',plugins:[ChartDataLabels],\n"
        "      data:{labels:hl,datasets:[\n"
        "        {label:short2,data:hd,backgroundColor:clrs,borderWidth:0,borderRadius:3},\n"
        "        {type:'line',label:'Target',data:hl.map(function(){return tgt2;}),\n"
        "         borderColor:'rgba(191,92,0,0.9)',borderWidth:2,borderDash:[5,4],\n"
        "         pointRadius:0,fill:false,tension:0}]},\n"
        "      options:{responsive:true,maintainAspectRatio:false,animation:false,\n"
        "        plugins:{legend:{display:false},tooltip:{enabled:true},\n"
        "          datalabels:{display:function(ctx){return ctx.dataset.type!=='line';},\n"
        "            formatter:function(v){return v!=null?v.toFixed(1)+'%':'';},\n"
        "            anchor:'end',align:'top',font:{size:10,weight:'600'},color:'#333',padding:2}},\n"
        "        layout:{padding:{top:24}},\n"
        "        scales:{\n"
        "          y:{min:yMin,max:yMax,display:true,ticks:{callback:function(v){return v+'%';},font:{size:10}},grid:{color:'#f0f0f0'}},\n"
        "          x:{ticks:{font:{size:10},color:'#555'},grid:{display:false},border:{display:false}}}}});\n"
        "  }};\n"
        "})();\n"
        "</script>\n"
    )
    js = js_data + js_code
    tab_html = (
        f'<div id="tab-driver" class="tab-content">'
        f'<style>{css}</style>'
        f'<div class="section-title">Driver Deep Dive</div>'
        f'<div class="dd2-pbar">'
        f'<button class="dd2-pbtn active" onclick="setDDPer2(this,\'w\')">Semana Fechada (WoW)</button>'
        f'<button class="dd2-pbtn" onclick="setDDPer2(this,\'m\')">Mensal (MoM)</button>'
        f'</div>'
        f'<div class="dd2-bar"><label>Driver</label>'
        f'<select id="dd2-drv-sel" onchange="renderDDDrv2()">'
        f'<option value="">— Selecione um driver —</option>'
        f'{opts}</select></div>'
        f'<div id="dd2-drv-cont"><div class="dd2-empty">Selecione um driver acima para ver a análise detalhada</div></div>'
        f'</div>\n'
    )
    return tab_html + js




# ═══════════════════════════════════════════════════════════════
# SECTION 5: CSS + HTML
# ═══════════════════════════════════════════════════════════════
CSS = """:root{--yellow:#FFE600;--dark:#1a1a2e;--gray:#f5f5f5;--border:#e0e0e0;--green:#00a650;--red:#e84142;--blue:#3483fa;--text:#333;--light-green:#e6f7ee;--light-red:#fdecea;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Proxima Nova',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:var(--text);font-size:14px;}
.header{background:var(--dark);color:#fff;padding:24px 40px;display:flex;align-items:center;justify-content:space-between;}
.header-left h1{font-size:22px;font-weight:800;letter-spacing:-.3px;}
.header-left p{font-size:13px;color:#aaa;margin-top:4px;}
.header-badge{background:var(--yellow);color:#000;font-weight:700;font-size:12px;padding:6px 14px;border-radius:20px;}
.container{max-width:1200px;margin:0 auto;padding:28px 24px 60px;}
.tabs{display:flex;gap:4px;border-bottom:3px solid var(--border);margin-bottom:28px;}
.tab-btn{padding:13px 32px;border:none;background:#fff;font-size:14px;font-weight:700;color:#999;cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-3px;border-radius:8px 8px 0 0;transition:all .15s;border:1px solid var(--border);border-bottom:3px solid transparent;}
.tab-btn.active{color:var(--dark);border-bottom-color:var(--yellow);background:#fff;border-color:var(--border);border-bottom-color:var(--yellow);}
.tab-btn:hover:not(.active){color:var(--dark);background:#f5f5f5;}
.tab-badge{display:inline-block;margin-left:8px;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;}
.tab-content{display:none;}
.tab-content.active{display:block;}
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
.highlight-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
.hl-pos{padding:14px 16px;background:var(--light-green);border-radius:8px;border-left:4px solid var(--green);}
.hl-neg{padding:14px 16px;background:var(--light-red);border-radius:8px;border-left:4px solid var(--red);}
.hl-title{font-weight:700;font-size:13px;margin-bottom:6px;}
.hl-pos .hl-title{color:var(--green);}
.hl-neg .hl-title{color:var(--red);}
.hl-text{font-size:12px;color:#333;line-height:1.6;}
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
.driver-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
.driver-block{background:#fff;border-radius:10px;border:1px solid var(--border);overflow:hidden;}
.driver-block-header{padding:12px 16px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;}
.driver-name{font-weight:700;font-size:13px;}
.driver-meta{font-size:12px;color:#888;margin-top:2px;}
.driver-block table th{font-size:10px;padding:7px 12px;}
.driver-block table td{font-size:12px;padding:7px 12px;}
.info-note{font-size:12px;color:#999;padding:8px 14px;background:#fafafa;border-radius:6px;border-left:3px solid var(--yellow);margin-bottom:10px;}
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
.dcev-section{background:#fff;border-radius:10px;border:1px solid var(--border);overflow:hidden;margin-bottom:14px;}
.dcev-section-header{padding:14px 20px;border-bottom:1px solid var(--border);background:#fafafa;}
.dcev-title{font-size:13px;font-weight:800;color:var(--dark);}
.dcev-sub{font-size:12px;color:#888;margin-top:3px;}
.dcev-grid{display:grid;grid-template-columns:1fr 1fr 1fr;}
.dcev-col{padding:16px 18px;border-right:1px solid var(--border);}
.dcev-col:last-child{border-right:none;}
.dcev-col-title{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid;}
.dcev-col-det .dcev-col-title{color:var(--red);border-color:var(--red);}
.dcev-col-pro .dcev-col-title{color:var(--green);border-color:var(--green);}
.dcev-col-act .dcev-col-title{color:var(--blue);border-color:var(--blue);}
.dcev-col ul{list-style:none;padding:0;}
.dcev-col ul li{font-size:12px;color:#444;line-height:1.6;padding:6px 0 6px 16px;border-bottom:1px solid #f5f5f5;position:relative;}
.dcev-col ul li:last-child{border-bottom:none;}
.dcev-col ul li::before{content:"•";position:absolute;left:0;font-weight:700;}
.dcev-col-det ul li::before{color:var(--red);}
.dcev-col-pro ul li::before{color:var(--green);}
.dcev-col-act ul li::before{color:var(--blue);}
.vigente-banner{background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;border-radius:10px;padding:16px 22px;margin-bottom:20px;}
"""

# Construir abas
chart_sf  = chart_block("chart_sf",  WEEK_LABELS,     weekly_history,     NPS_TARGET)
chart_va  = chart_block("chart_va",  WEEK_LABELS_VIG, weekly_history_vig, NPS_TARGET)
chart_mes = chart_block("chart_mes", MONTH_LABELS,    monthly_history,    NPS_TARGET)

# Consolidated NPS series
_cons_w   = _consolidated_series(weekly_history,     WEEK_LABELS)
_cons_v   = _consolidated_series(weekly_history_vig, WEEK_LABELS_VIG)
_cons_m   = _consolidated_series(monthly_history,    MONTH_LABELS)

# Consolidated NPS bar+line charts
cons_sf  = consolidated_chart_block("cons_sf",  WEEK_LABELS,     _cons_w, NPS_TARGET)
cons_va  = consolidated_chart_block("cons_va",  WEEK_LABELS_VIG, _cons_v, NPS_TARGET)
cons_mes = consolidated_chart_block("cons_mes", MONTH_LABELS,    _cons_m, NPS_TARGET)

# Waterfall charts
wf_sf  = waterfall_block("wf_sf",  f"S2", nS2, f"S1", nS1, wD)
wf_va  = waterfall_block("wf_va",  f"S1", nS1, f"Vig", nVig, vD)
wf_mes = waterfall_block("wf_mes", M2_LABEL[:3], nM2, M1_LABEL[:3], nM1, mD)

# Driver history tables
htbl_sf  = driver_history_table(weekly_history,     WEEK_LABELS,     DRIVER_TARGETS, delta_label="ΔWoW")
htbl_va  = driver_history_table(weekly_history_vig, WEEK_LABELS_VIG, DRIVER_TARGETS, delta_label="ΔWoW")
htbl_mes = driver_history_table(monthly_history,    MONTH_LABELS,    DRIVER_TARGETS, delta_label="ΔMoM")

tab_sf = tab_content(
    "fechada",
    nS1, sS1, f"S1 ({S1_LABEL})", dW, nS2, sS2, f"S2 ({S2_LABEL})",
    wD, wP, extra_html=deep_dive_html + seniority_block(seniority_weekly, S1_LABEL, lbl_b="S1", drv_targets=DRIVER_TARGETS),
    wf_html=wf_sf, cons_html=cons_sf, hist_table=htbl_sf,
    bullets_html=tab_bullets_block(
        period_label=S1_LABEL, nps_cur=nS1, delta=dW, surv=sS1, target=NPS_TARGET,
        pos_drv=DEEP_DIVE_POS_DRIVER, pos_var=DEEP_DIVE_POS_VAR,
        pos_proc=DEEP_DIVE_POS_PROC,
        pos_insights=DEEP_DIVE_POS_INSIGHTS,
        neg_drv=DEEP_DIVE_NEG_DRIVER, neg_var=DEEP_DIVE_NEG_VAR,
        neg_proc=DEEP_DIVE_NEG_PROC,
        neg_insights=DEEP_DIVE_NEG_INSIGHTS,
        alerts=ALERT_SF, n_driver_insights=1,
        seniority_data=seniority_weekly, drv_targets=DRIVER_TARGETS, seniority_period="S1",
        neg_why=DEEP_DIVE_NEG_WHY
    )
)

tab_va = tab_content(
    "vigente",
    nVig, sVig, f"Vig ({VIG_LABEL})", dVW, nS1, sS1, f"S1 ({S1_LABEL})",
    vD, vP, extra_html=vigente_banner,
    wf_html=wf_va, cons_html=cons_va, hist_table=htbl_va,
    bullets_html=tab_bullets_block(
        period_label=VIG_LABEL, nps_cur=nVig if sVig > 0 else nS1,
        delta=dVW if sVig > 0 else 0, surv=sVig, target=NPS_TARGET,
        pos_drv=DD_VIG_POS_DRIVER, pos_var=DD_VIG_POS_VAR,
        pos_proc=DD_VIG_POS_PROC,
        pos_insights=DD_VIG_POS_INSIGHTS,
        neg_drv=DD_VIG_NEG_DRIVER, neg_var=DD_VIG_NEG_VAR,
        neg_proc=DD_VIG_NEG_PROC,
        neg_insights=DD_VIG_NEG_INSIGHTS,
        alerts=ALERT_VA, n_driver_insights=1,
        neg_why=DD_VIG_NEG_WHY
    )
)

tab_mes = tab_content(
    "mensal",
    nM1, sM1, M1_LABEL, dM, nM2, sM2, M2_LABEL,
    mD, mP, extra_html=deep_dive_mes_html + seniority_block(seniority_monthly, M1_LABEL, drv_targets=DRIVER_TARGETS),
    wf_html=wf_mes, cons_html=cons_mes, hist_table=htbl_mes,
    bullets_html=tab_bullets_block(
        period_label=M1_LABEL, nps_cur=nM1, delta=dM, surv=sM1, target=NPS_TARGET,
        pos_drv=DD_MES_POS_DRIVER, pos_var=DD_MES_POS_VAR,
        pos_proc=DD_MES_POS_PROC,
        pos_insights=DD_MES_POS_INSIGHTS,
        neg_drv=DD_MES_NEG_DRIVER, neg_var=DD_MES_NEG_VAR,
        neg_proc=DD_MES_NEG_PROC,
        neg_insights=DD_MES_NEG_INSIGHTS,
        alerts=ALERT_MES, n_driver_insights=2,
        seniority_data=seniority_monthly, drv_targets=DRIVER_TARGETS,
        neg_why=DD_MES_NEG_WHY
    )
)

def tab_btn(tab_id, label, delta):
    badge_cls = "background:var(--light-green);color:var(--green)" if delta>=0 else "background:var(--light-red);color:var(--red)"
    sign = "+" if delta>=0 else ""
    return (
        f'<button class="tab-btn" id="btn-{tab_id}" onclick="showTab(\'{tab_id}\')">'
        f'{label}'
        f'<span class="tab-badge" style="{badge_cls};">{sign}{fn(delta)} pp</span>'
        f'</button>'
    )

tab_driver_dd = driver_dd_tab(wD, wP, mD, mP)

tabs_nav = (
    f'<div class="tabs">'
    + tab_btn("fechada", "Semana Fechada", dW)
    + tab_btn("vigente", "Semana Atual", dVW)
    + tab_btn("mensal",  "Mensal", dM)
    + f'<button class="tab-btn" id="btn-driver" onclick="showTab(\'driver\')">Driver Deep Dive</button>'
    + f'</div>'
)

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>NPS Seller Dev BR — {REPORT_DATE}</title>
<style>{CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<script>Chart.register(ChartDataLabels);</script>
</head>
<body>
<div class="header">
  <div class="header-left">
    <h1>NPS Seller Dev — Brasil</h1>
    <p>Fechada: {S1_LABEL} · Vigente: {VIG_LABEL} · {M1_LABEL} · Centro: BR · Seller Dev</p>
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
{tab_driver_dd}
</div>
<script>
function showTab(name) {{
  document.querySelectorAll('.tab-content').forEach(function(el) {{ el.classList.remove('active'); }});
  document.querySelectorAll('.tab-btn').forEach(function(el) {{ el.classList.remove('active'); }});
  document.getElementById('tab-' + name).classList.add('active');
  document.getElementById('btn-' + name).classList.add('active');
}}
document.getElementById('btn-fechada').classList.add('active');
document.getElementById('tab-fechada').classList.add('active');
</script>
</body>
</html>"""

OUTPUT = r"C:\claudinho\nps_seller_dev_br_semanal.html"
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

# ═══════════════════════════════════════════════════════════════
# SECTION 6: GITHUB PAGES DEPLOY
# ═══════════════════════════════════════════════════════════════
import subprocess, shutil, os, tempfile

GITHUB_REPO = "https://github.com/allabriola/nps-driver-test.git"
try:
    tmp = tempfile.mkdtemp()
    subprocess.run(["git","clone","--depth=1",GITHUB_REPO,tmp], check=True, capture_output=True)
    shutil.copy(OUTPUT, os.path.join(tmp,"nps_seller_dev_br_semanal.html"))
    subprocess.run(["git","-C",tmp,"add","nps_seller_dev_br_semanal.html"], check=True)
    subprocess.run(["git","-C",tmp,"-c","user.email=andre.labriola@mercadolivre.com",
                    "-c","user.name=Andre Labriola",
                    "commit","-m",f"Atualiza NPS Seller Dev BR — {REPORT_DATE}"], check=True)
    subprocess.run(["git","-C",tmp,"push","origin","main"], check=True, capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"GitHub Pages: OK -> https://allabriola.github.io/nps-driver-test/nps_seller_dev_br_semanal.html")
except Exception as e:
    print(f"GitHub Pages: erro -> {e}")

print(f"HTML: {OUTPUT}")
print(f"S1={fn(nS1)} ({'+' if dW>=0 else ''}{fn(dW)}pp) | Vig={fn(nVig)} ({'+' if dVW>=0 else ''}{fn(dVW)}pp) | {M1_LABEL[:3]}={fn(nM1)} ({'+' if dM>=0 else ''}{fn(dM)}pp)")

# ═══════════════════════════════════════════════════════════════
# SECTION 7: GRID DEPLOY
# ═══════════════════════════════════════════════════════════════
import requests as _req

import json as _json_mod, base64 as _b64_mod, os as _os_mod

GRID_DOC_ID    = "01KQ7CTM8AKS44HJ8H1BZDQ8CB"
GRID_COOKIES_F = _os_mod.path.join(_os_mod.path.dirname(_os_mod.path.abspath(__file__)), "grid_cookies.json")
# ↑ Gerar via: python save_grid_cookies.py  (Cookie-Editor → Export no Chrome)
# Re-rodar quando expirar (geralmente em semanas) — script avisa automaticamente.

if _os_mod.path.exists(GRID_COOKIES_F):
    try:
        from playwright.sync_api import sync_playwright as _sync_pw

        with open(OUTPUT, "rb") as _f:
            _html_b64 = _b64_mod.b64encode(_f.read()).decode()
        with open(GRID_COOKIES_F, encoding="utf-8") as _fc:
            _raw_ck = _json_mod.load(_fc)

        _VALID_SS = {"Strict", "Lax", "None"}
        _pw_cookies = []
        for _c in _raw_ck:
            _d = _c.get("domain", "grid.adminml.com")
            # hostOnly=True = cookie exato de domínio; não adicionar ponto inicial
            if not _d.startswith(".") and not _c.get("hostOnly", False):
                _d = "." + _d
            _ss = _c.get("sameSite", "None")
            if _ss not in _VALID_SS: _ss = "None"
            _pw_cookies.append({
                "name": _c["name"], "value": _c["value"], "domain": _d,
                "path": _c.get("path", "/"), "secure": bool(_c.get("secure", True)),
                "httpOnly": bool(_c.get("httpOnly", False)), "sameSite": _ss,
            })

        with _sync_pw() as _pw:
            _browser = _pw.chromium.launch(headless=True)
            _ctx = _browser.new_context()
            _ctx.add_cookies(_pw_cookies)
            _page = _ctx.new_page()
            _page.goto("https://grid.adminml.com", wait_until="networkidle", timeout=30000)

            _csrf_val = next((_c["value"] for _c in _raw_ck if _c.get("name") == "_csrf"), "")
            _result = _page.evaluate(
                """async ({b64html, docId, csrfToken}) => {
                    const bin = atob(b64html);
                    const bytes = new Uint8Array(bin.length);
                    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
                    const fd = new FormData();
                    fd.append("file", new Blob([bytes], {type:"text/html;charset=utf-8"}),
                              "nps_seller_dev_br_semanal.html");
                    fd.append("title", "NPS Seller Dev BR");
                    const r = await fetch("/api/v1/documents/" + docId + "/versions",
                                          {method:"POST", body:fd, credentials:"include",
                                           headers: csrfToken ? {"X-CSRF-Token": csrfToken} : {}});
                    const txt = await r.text();
                    return {status: r.status, body: txt.substring(0, 200)};
                }""",
                {"b64html": _html_b64, "docId": GRID_DOC_ID, "csrfToken": _csrf_val},
            )
            _browser.close()

        _s = _result.get("status", 0)
        if _s in (200, 201):
            import re as _rr
            _vm = _rr.search(r'"version"\s*:\s*(\d+)', _result.get("body", ""))
            _v = _vm.group(1) if _vm else "?"
            print(f"Grid: OK (v{_v}) -> https://grid.adminml.com/d/{GRID_DOC_ID}/view")
        elif _s == 401:
            print("Grid: sessao expirada — rode: python save_grid_cookies.py")
        else:
            print(f"Grid: erro HTTP {_s} -> {_result.get('body','')[:120]}")

    except Exception as _e:
        print(f"Grid: erro -> {_e}")
else:
    print("Grid: grid_cookies.json nao encontrado — rode: python save_grid_cookies.py")
