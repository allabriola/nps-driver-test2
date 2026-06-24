#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza generate_html.py para fechamento de Abril 2026.
   S1=20/abr, S2=13/abr, M1=Abril, M2=Março."""

with open(r'C:\claudinho\generate_html.py', encoding='utf-8') as f:
    content = f.read()

def replace_block(old, new):
    global content
    if old not in content:
        print(f'WARNING: block not found: {old[:60]!r}')
        return False
    content = content.replace(old, new, 1)
    return True

# ── 1D: Deep Dive Vigente ──────────────────────────────────────
replace_block(
'DD_VIG_DATE = "04/05/2026"\nDD_VIG_POS_DRIVER = "ME Vendedor Seller Dev"\nDD_VIG_POS_VAR = "+1,58 pp"',
'DD_VIG_DATE = "04/05/2026"\nDD_VIG_POS_DRIVER = "ME Vendedor Seller Dev"\nDD_VIG_POS_VAR = "+1,42 pp"'
)
replace_block(
'"Despacho Ventas y Publicaciones: NPS 59,85% (S2) → 69,14% (S1) (+9,29 pp) | 674 surveys | semana 04/mai sem dados ainda — exibindo referência da S1 fechada"',
'"Gestiones Operativas: 53,03% → 63,93% (+10,90 pp) | Reputación ME: 82,94% → 85,54% (+2,60 pp) | referência semana fechada S1 (20/abr–26/abr)"'
)
replace_block(
'"Semana 04/mai iniciando sem dados disponíveis (primeiro dia da semana, pipeline com lag normal) — referência baseada na S1 fechada (27/abr – 03/mai)."',
'"Semana vigente (27/abr+) sem dados — exibindo referência da semana fechada S1 (20/abr–26/abr). ME Vendedor foi o maior driver positivo no fechamento de Abril (+1,42 pp MIX+NETO)."'
)
replace_block(
'"ME Vendedor foi o maior driver positivo da semana fechada (+1,58 pp MIX+NETO, NPS 72,68%) impulsionado pelo processo Despacho (+9,29 pp com FCR e atendimento humanizado via WhatsApp e chat)."',
'"Gestiones Operativas liderou a alta: +10,90 pp em 122 surveys — CDUs de onboarding logístico (ME, ME Flex, ME Places) com atendimento consultivo gerando NPS 10 sistemático."'
)
replace_block(
'"A monitorar ao longo da semana: se Despacho mantiver NPS >65% com volume crescente, confirma tendência de melhora operacional em logística de despacho."',
'"Reputación ME é o processo âncora: NPS 85,54% em 484 surveys — consistência histórica acima de 82% por múltiplas semanas seguidas."'
)
replace_block(
'"Reputación ME permanece acima de 82% há múltiplas semanas — processo âncora de ME Vendedor com estabilidade estrutural."',
'"A monitorar na abertura de Maio: se ME Vendedor mantiver NPS >68% com Gestiones acima de 60%, confirma tendência de melhora operacional."'
)
replace_block(
'DD_VIG_NEG_DRIVER = "Partners"\nDD_VIG_NEG_VAR = "-1,08 pp"',
'DD_VIG_NEG_DRIVER = "PCF Vendedor Seller Dev"\nDD_VIG_NEG_VAR = "-0,42 pp"'
)
replace_block(
'DD_VIG_NEG_WHY = "Partners é o driver de maior pressão negativa: NPS caiu de 67,04% (S2) para 62,62% (S1) (-4,42 pp) e está 7,99 pp abaixo do target de 70,61%. CDUs de suspensão sem ferramenta e métricas sem transparência persistem como causas estruturais."',
'DD_VIG_NEG_WHY = "PCF Vendedor caiu de 49,09% (13/abr) para 40,31% (20/abr), -8,78 pp: único processo (Post Compra Funcionalidades) com padrão recorrente de devolução falha e mediação sem ferramenta de encerramento para o atendente."'
)
replace_block(
'DD_VIG_NEG_PROC = "Drivers: NPS 65,97% (S2) → 61,76% (S1) (-4,21 pp) | 625 surveys | 2ª semana consecutiva abaixo do target de 70,61%"',
'DD_VIG_NEG_PROC = "Post Compra Funcionalidades Vendedor: NPS 49,09% (S2) → 40,31% (S1) (-8,78 pp) | 137 → 129 surveys"'
)
replace_block(
'"Semana atual iniciando sem dados — exibindo referência S1. Partners é prioridade de monitoramento para a semana de 04/mai."',
'"PCF Vendedor abaixo do target de 39,93%: NPS atual 40,31% vs 49,09% anterior — queda de -8,78 pp em volume estável (~130 surveys/semana)."'
)
replace_block(
'"2ª semana consecutiva de queda em Partners/Drivers: NPS 62,62% vs target 70,61% (-7,99 pp) — bug de rotas e suspensão sem ferramenta de reversão como CDUs dominantes sem solução técnica disponível."',
'"Devolução falha é a causa raiz dominante: produto não chegou após retorno ou chegou danificado — atendente orienta reclamação mas não pode resolver a mediação nem liberar o pagamento."'
)
replace_block(
'"Target de 70,61% requer melhora de +7,99 pp vs NPS atual de 62,62% — meta agressiva que depende de solução técnica, não só de atendimento."',
'"Transferências em cadeia sem owner (Pablo → Jennifer → Kelly → Lucas) — cada atendente herda o problema mas não tem ferramenta para fechar a mediação."'
)
replace_block(
'"Places Kangu também em queda (-5,71 pp vs S2): ambos os processos deteriorando simultaneamente sugere problema estrutural do driver."',
'"Ação prioritária: criar owner fixo para mediações com prazo expirado com ferramenta de encerramento — CDU de maior impacto negativo em PCF há múltiplas semanas."'
)

# ── 1E: Deep Dive Mensal ──────────────────────────────────────
replace_block(
'DD_MES_DATE = "04/05/2026"\nDD_MES_POS_DRIVER = "ME Vendedor Seller Dev"\nDD_MES_POS_VAR = "+3,31 pp"',
'DD_MES_DATE = "04/05/2026"\nDD_MES_POS_DRIVER = "ME Vendedor Seller Dev"\nDD_MES_POS_VAR = "+0,91 pp"'
)
replace_block(
'"Despacho Ventas y Publicaciones: NPS 55,96% (Abr) → 83,13% (Mai, 4 dias) (+27,17 pp) | 3.020 → 166 surveys | Reputación ME estável em 82,84% (Abr) | 2.424 surveys"',
'"Despacho Ventas y Publicaciones: NPS 56,25% (Mar) → 59,91% (Abr) (+3,66 pp) | 2.062 → 3.020 surveys | Reversa: 50,90% → 60,28% (+9,38 pp) | Reputación ME estável em 82,39% | 2.226 surveys"'
)
replace_block(
'"ME Vendedor é o maior driver positivo do mês (+3,31 pp MIX+NETO): NPS subiu de 68,84% (Abr) para 76,55% (Mai, primeiros 4 dias, 290 surveys) — sinal inicial positivo, monitorar ao longo do mês."',
'"ME Vendedor é o maior driver positivo do mês (+0,91 pp MIX+NETO): NPS subiu de 67,05% (Mar) para 68,84% (Abr) em 6.784 surveys — maior volume absoluto do portfólio, melhora distribuída entre processos de logística."'
)
replace_block(
'"Despacho Ventas lidera a melhora: NPS 55,96% (Abr, 3.020 surveys) → 83,13% (Mai, 166 surveys) — amostra parcial muito favorável, confirma tendência já observada na semana fechada S1 (+9,29 pp em 27/abr-03/mai com FCR e atendimento humanizado)."',
'"Despacho Ventas y Publicaciones lidera a melhora: +3,66 pp em 3.020 surveys (Mar: 2.062) — maior processo do driver, subiu de 56,25% para 59,91% — sinal de melhora operacional em despachos e publicações vendedores."'
)
replace_block(
'"Atenção: M1 (Maio) tem apenas 290 surveys para ME Vendedor vs 6.784 em Abril — NPS de mai/26 reflete apenas os primeiros 4 dias úteis, deve ser monitorado ao longo do mês."',
'"Reputación ME mantém alta consistente em 82,39% (2.226 surveys) — processo âncora do driver, com NPS estável acima de 80% pelo 2º mês consecutivo."'
)
replace_block(
'DD_MES_NEG_DRIVER = "Experiencia Impositiva Seller Dev"\nDD_MES_NEG_VAR = "-0,82 pp"',
'DD_MES_NEG_DRIVER = "Publicaciones Seller Dev"\nDD_MES_NEG_VAR = "-1,19 pp"'
)
replace_block(
'DD_MES_NEG_WHY = "Exp. Impositiva despencou de 50,87% (Abr) para 23,53% (Mai, 17 surveys) — MIX+NETO -0,82 pp. Base muito parcial mas com padrão de problemas recorrentes confirmado: SLA ausente, encerramento sem resolução e IA com informação errada são causas estruturais sem correção."',
'DD_MES_NEG_WHY = "Publicaciones caiu de 68,45% (Mar) para 62,54% (Abr), MIX+NETO -1,19 pp em 2.600 surveys. Afiliados ML (-5,44 pp, 1.227 surveys) e Potenciar Ventas (-22,96 pp, 196 surveys) puxam a queda. IA de detecção de PI comete erros de classificação e atendentes passam informações contraditórias."'
)
replace_block(
'"Emision de Nota Fiscal: NPS 53,61% (Abr) → 50,00% (Mai, 10 surveys) | Facturación: 43,75% (Abr) → -20,00% (Mai, 5 surveys) | base parcial — monitorar ao longo do mês"',
'"Afiliados ML: NPS 70,07% (Mar) → 64,63% (Abr) (-5,44 pp) | 1.687 → 1.227 surveys (maior volume do driver) | Potenciar Ventas: 72,45% → 49,49% (-22,96 pp) | 265 → 196 surveys"'
)
replace_block(
'"Exp. Impositiva com NPS 23,53% nos primeiros dias de Maio (17 surveys) — queda de -27,34 pp vs Abril (50,87%) — amostra pequena mas consistente com padrão semanal recente: 52,86% na S1 vs 38,64% na S2."',
'"Afiliados ML com maior impacto absoluto em Publicaciones: MIX+NETO -2,85 pp — NPS caiu de 70,07% (Mar) para 64,63% (Abr) em 1.227 surveys (47% do volume do driver)."'
)
replace_block(
'"Padrão recorrente de Abril confirmado: encerramento sem resolução e reabertura de ticket sem contexto (#450867735, #447992026), IA passa informação errada por dias antes do humano corrigir com impacto na reputação (#450184747), \'responderam nada a ver com o que mandei\' (#452023484)."',
'"Potenciar Ventas com maior queda percentual: NPS 72,45% (Mar) → 49,49% (Abr), -22,96 pp em 196 surveys — abaixo do target de 52,87% — processo que precisa de atenção imediata."'
)
replace_block(
'"SLA ausente como raiz comum: NF pendente bloqueia anúncios FULL por 4+ dias sem previsão — \'#451516035: 3 chamados abertos, 4 dias sem resolução, FULL inativo com perda de vendas\' — atendente só \'registra e aguarda\' sem owner fixo."',
'"PR - Propiedad intelectual com queda relevante: NPS 73,62% (Mar) → 64,25% (Abr) em 207 surveys — IA de detecção de PI com erros de classificação, atendentes passam informações contraditórias entre si."'
)
replace_block(
'"Certificado digital expirado bloqueando emissão de NF: suporte não consegue resolver casos fora dos \'padrões\' — \'os problemas não respeitam os padrões\' (#454075257) — CDU crescente sem solução disponível."',
'"PR - Artículos prohibidos e Gestión de Publicación também em queda — múltiplos processos deteriorando simultaneamente sustentam o MIX+NETO -1,19 pp do driver."'
)
replace_block(
'DD_MES_DET = [\n    "Certificado digital não renovado bloqueando emissão de NF: fora dos padrões do suporte — \'os problemas não respeitam os padrões\' (#454075257).",\n    "Encerramento sem resolução e reabertura sem contexto: vendedor retorna do zero a cada novo atendente (#450867735, #447992026).",\n    "IA de 1ª linha repete informação incorreta até humano corrigir — impacto na reputação do seller já registrado antes da correção (#450184747).",\n    "NF pendente com FULL inativo: \'#451516035 — 3 chamados, 4 dias de bloqueio, perda mensurável de vendas\' — SLA ausente.",\n]',
'DD_MES_DET = [\n    "Afiliados ML — maior volume e impacto: NPS caindo de 70,07% → 64,63% (-5,44 pp) — 47% do volume do driver, queda sustentada em 1.227 surveys de Abril.",\n    "Potenciar Ventas — maior queda percentual: NPS -22,96 pp; abaixo do target de 52,87% — processo prioritário para ação.",\n    "PR - Propiedad intelectual — IA acusa falsamente de violação — vendedor com NF da fabricante sem recurso eficiente; informações contraditórias entre analistas.",\n    "PR-Técnica prohibida e Gestión de Publicación: queda de -4,88 pp e -4,23 pp respectivamente — múltiplos processos em queda simultânea.",\n]'
)
replace_block(
'DD_MES_PRO = [\n    "ME Vendedor: atendentes humanos com FCR e menção nominal gerando NPS 10 sistematicamente (Josi, Kenia, Ana Paula, Marcio) — replicar treinamento para outros drivers.",\n    "Post Venta/Reputación estável: exclusão de impacto no 1º contato com empatia gera NPS 70%+ há múltiplos meses.",\n    "Partners/Places Kangu com NPS 87,5% nos primeiros dias de Maio (16 surveys) — amostra parcial mas positiva vs S1.",\n]',
'DD_MES_PRO = [\n    "Atendentes nomeados em Reputação (Post Venta): Lidiane, Lucas, Daiane, Cicera, Mariana, Yasmin — resolução no 1º contato com exclusão de impacto gera NPS 10 consistente.",\n    "Gestão humanizada de resposta negativa em Reputação: \'mesmo não podendo remover o impacto, foi ótimo atendimento\' — empatia mantém NPS alto mesmo sem solução favorável.",\n    "Afiliados ML e Antes de publicar mantêm Publicaciones com NPS > target de 52,87% apesar das quedas em outros processos.",\n]'
)
replace_block(
'DD_MES_ACO = [\n    "Criar SLA de 24h para casos de NF pendente com anúncio FULL ativo — bloqueio de anúncios é impacto financeiro direto e mensurável (#451516035).",\n    "Implementar histórico obrigatório no contexto do atendente antes de responder — eliminar informações desconexas e encerramento sem resolução.",\n    "Revisar processo de certificado digital expirado: criar fast track de renovação com SLA de 4h — CDU crescente sem solução padrão disponível.",\n    "Replicar modelo de atendimento de Reputação (Post Venta) para Exp. Impositiva: owner fixo + empatia + SLA definido.",\n]',
'DD_MES_ACO = [\n    "Revisão do motor de IA de detecção de PI: criar processo de recurso com análise humana obrigatória antes do bloqueio — erro de classificação em Propiedad intelectual gera NPS 0 e perda de vendedor.",\n    "Padronizar resposta de atendentes para casos de PI com trilhas de decisão — eliminar informações contraditórias entre analistas.",\n    "Para Afiliados ML e Potenciar Ventas: investigar causa da queda progressiva de NPS em Abril — se sazonalidade ou mudança de produto, tratar antes de virar tendência em Maio.",\n    "Expandir atendimento humanizado de Reputação (Post Venta) como modelo: escuta ativa + exclusão de impacto no 1º contato é o padrão que gera NPS 70%+ — replicar para outros drivers.",\n]'
)

# ── 1F: Alertas ───────────────────────────────────────────────
replace_block(
'ALERT_SF = [\n    {\n        "drv": "Partners", "proc": "Drivers",\n        "nps_cur": 62.62, "nps_tgt": 70.61, "delta_tgt": -7.99, "trend": "↓↓ Em queda",\n        "why": "Partners/Drivers com NPS 62,62% (S1) vs target 70,61% (-7,99 pp): 2ª semana consecutiva abaixo do target com queda acelerada (-4,42 pp vs S2). Métricas sem transparência + suspensão sem ferramenta de reversão são CDUs dominantes — atendente só registra, não resolve.",',
'ALERT_SF = [\n    {\n        "drv": "Experiencia Impositiva Seller Dev", "proc": "Emision de Nota Fiscal",\n        "nps_cur": 38.64, "nps_tgt": 59.03, "delta_tgt": -20.39, "trend": "↓↓ Em queda",\n        "why": "Exp. Impositiva despencou de 49,38% (S2=13/abr) para 38,64% (S1=20/abr), -10,74 pp. KTA Newbie no canal C2C concentra a queda: Emissão NF KTA NPS negativo. SLA ausente e encerramento sem resolução como causas estruturais.",',
)
replace_block(
'        "insights": [\n            "Partners/Drivers com NPS 62,62% vs target 70,61% (-7,99 pp) — 2ª semana consecutiva em queda: 67,59% (W3) → 67,04% (S2) → 62,62% (S1), tendência \'em queda\' confirmada.",\n            "Métricas caindo sem acesso a detalhes: \'se houve reclamação, só o centro logístico tem acesso\' (#452936125) — atendente sem visibilidade dos dados, motor de NPS 0.",\n            "Suspensão preventiva sem justificativa e sem ferramenta: \'não fiz nada de errado, tenho tudo registrado e mesmo assim fui penalizado\' (#452908085) — atendente confirma mas não reverte.",\n            "Múltiplos atendentes sem owner: case técnico passou por 4 atendentes sem resolução (#452921370) — each um recomeça do zero pedindo as mesmas informações.",\n        ],\n        "acoes": [\n            "Dar ao atendente acesso ao log de métricas que gerou queda de nível — eliminar \'só o centro logístico tem acesso\' que gera NPS 0 mesmo com atendente empático.",\n            "Criar ferramenta de reversão de suspensão preventiva com aprovação de supervisor — CDU crescente sem resolução no 1º contato.",\n            "Criar owner fixo para casos técnicos (desafio/percurso/métricas): após 2 transferências, atribuir owner com SLA de 24h.",\n            "Criar canal de comunicação proativa para mudanças de nível e suspensão — motoristas não devem descobrir pela abertura do app.",\n        ],\n    },\n]',
'        "insights": [\n            "Exp. Impositiva com NPS 38,64% vs target 59,03% (-20,39 pp) — queda acelerada: 49,38% (13/abr) → 38,64% (20/abr), tendência \'em queda\' confirmada.",\n            "Ligação caindo sem retorno é causa estrutural recorrente: canal C2C com instabilidade persistente sem callback automático.",\n            "NF pendente por 4+ dias com anúncios FULL inativos: impacto financeiro direto mensurável — SLA ausente.",\n            "Respostas desconexas e encerramento sem resolução: IA repete informação incorreta antes do humano corrigir.",\n        ],\n        "acoes": [\n            "Corrigir instabilidade do canal telefônico de Emissão NF — callback obrigatório em até 5 minutos após queda de ligação.",\n            "Criar SLA de 24h para NF pendente com anúncio FULL ativo — prioridade máxima de resolução.",\n            "Implementar histórico obrigatório no contexto do atendente antes de responder.",\n            "Habilitar DCe no app mobile — canal desktop-only bloqueante para sellers mobile.",\n        ],\n    },\n    {\n        "drv": "Partners", "proc": "Drivers",\n        "nps_cur": 67.04, "nps_tgt": 70.19, "delta_tgt": -3.15, "trend": "↓ Queda",\n        "why": "Partners/Drivers com NPS 67,04% (S1=20/abr) vs target 70,19% (-3,15 pp). Contas pausadas sem ferramenta de reversão + bug de notificação de rotas dominam os detratores.",\n        "insights": [\n            "Partners/Drivers NPS 67,04% vs target 70,19% — tendência de queda: 67,59% (13/abr) → 67,04% (20/abr).",\n            "Conta pausada sem justificativa: motorista inativado sem explicação — atendente registra mas não reativa.",\n            "Bug de rotas: app mostra notificação mas ao abrir nenhuma rota aparece — problema sistêmico sem correção.",\n            "Atendentes sem ferramentas: padrão \'aguardar análise interna\' sem SLA — NPS 0 sistematicamente.",\n        ],\n        "acoes": [\n            "Criar ferramenta para atendente reativar conta pausada por Digital Account.",\n            "Corrigir bug de notificação de rotas no app — problema persistente há múltiplas semanas.",\n            "Capacitar atendentes Drivers com acesso ao sistema de conta e rotas.",\n            "Revisar política de pausa com contestação de SLA de 24h.",\n        ],\n    },\n]'
)

replace_block('ALERT_VA = []', 'ALERT_VA = []')  # keep

replace_block(
'ALERT_MES = [\n    {\n        "drv": "Experiencia Impositiva Seller Dev", "proc": "Emision de Nota Fiscal",\n        "nps_cur": 23.53, "nps_tgt": 59.67, "delta_tgt": -36.14, "trend": "↓ Queda",\n        "why": "Exp. Impositiva com NPS 23,53% (Mai, 17 surveys) vs target 59,67% (-36,14 pp) — base muito parcial (primeiros 4 dias) mas consistente com padrão recorrente de Abril: SLA ausente, encerramento sem resolução e IA com informação errada como causas estruturais sem correção.",\n        "insights": [\n            "Exp. Impositiva com NPS 23,53% nos primeiros dias de Maio (17 surveys) — queda de -27,34 pp vs Abril (50,87%); amostra parcial, mas padrão de problemas estruturais recorrentes confirmado.",\n            "SLA ausente é raiz comum: NF pendente bloqueia anúncios FULL por 4+ dias — \'#451516035: 3 chamados abertos, 4 dias bloqueado, perda mensurável de vendas\' — atendente só \'registra e aguarda\' sem owner.",\n            "Encerramento sem resolução e reabertura sem contexto: vendedor retorna do zero a cada novo atendente — \'#450867735, #447992026\' — ticket fechado por timeout sem confirmação do cliente.",\n            "Certificado digital expirado bloqueando emissão: CDU sem solução padrão — \'os problemas não respeitam os padrões\' (#454075257) — suporte não consegue resolver casos atípicos.",\n        ],\n        "acoes": [\n            "Criar SLA de 24h para NF pendente com anúncio FULL ativo — bloqueio de FULL é impacto financeiro direto e mensurável.",\n            "Implementar histórico obrigatório no contexto do atendente antes de responder — eliminar encerramento sem resolução e retrabalho.",\n            "Criar fast track de renovação de certificado digital com SLA de 4h — CDU crescente sem solução padrão disponível.",\n            "Monitorar Exp. Impositiva ao longo de Maio: base de 17 surveys é muito parcial — se NPS não recuperar para 50%+ até fim do mês, escalar para revisão de produto.",\n        ],\n    },\n]',
'ALERT_MES = [\n    {\n        "drv": "Partners", "proc": "Drivers",\n        "nps_cur": 65.65, "nps_tgt": 70.19, "delta_tgt": -4.54, "trend": "↓ Queda",\n        "why": "Partners NPS 65,65% (Abril) vs target 70,19% (-4,54 pp) — 2º mês consecutivo abaixo do target: Fev 72,38% → Mar 67,39% → Abr 65,65%. Conta pausada por Digital Account e bug de rotas como CDUs dominantes sem solução técnica.",\n        "insights": [\n            "Partners NPS 65,65% vs target 70,19% (-4,54 pp) — queda de Mar 67,39% → Abr 65,65% (-1,74 pp), abaixo do target pelo segundo mês consecutivo.",\n            "Conta pausada sem justificativa é CDU dominante em Drivers: motoristas com conta desativada por Digital Account sem ferramenta de reativação pelo atendente.",\n            "Bug de rotas persiste: app mostra notificação disponível mas rota não aparece — problema sistêmico sem correção há múltiplas semanas.",\n            "Atendentes sem ferramentas: padrão de \'aguardar análise interna\' sem SLA — NPS 0 sistematicamente.",\n        ],\n        "acoes": [\n            "Criar ferramenta para atendente reativar conta pausada por Digital Account — causa raiz do CDU dominante.",\n            "Corrigir bug de notificação de rotas no app com prioridade — problema sistêmico presente há mais de 2 semanas.",\n            "Criar canal de suporte dedicado para Partners/Drivers com ferramentas de acesso.",\n            "Monitorar NPS Drivers mensalmente — 2º mês abaixo do target, escalar para revisão de produto antes do M3.",\n        ],\n    },\n]'
)

# ── Section 2: weekly/monthly data ────────────────────────────
# weekly_driver
replace_block(
'weekly_driver = {\n    "Experiencia Impositiva Seller Dev": {"S2":(57,23,88),     "S1":(50,13,70)},\n    "ME Vendedor Seller Dev":            {"S2":(1058,152,1308),"S1":(1166,134,1420)},\n    "PCF Vendedor Seller Dev":           {"S2":(82,30,129),    "S1":(81,26,119)},\n    "Partners":                          {"S2":(567,85,719),   "S1":(548,99,717)},\n    "Post Venta Seller Dev":             {"S2":(177,18,209),   "S1":(175,19,217)},\n    "Publicaciones Seller Dev":          {"S2":(398,76,512),   "S1":(381,88,517)},\n}',
'weekly_driver = {\n    "Experiencia Impositiva Seller Dev": {"S2":(112,33,160),    "S1":(57,23,88)},\n    "ME Vendedor Seller Dev":            {"S2":(1154,178,1482), "S1":(1058,152,1308)},\n    "PCF Vendedor Seller Dev":           {"S2":(95,28,137),     "S1":(82,30,129)},\n    "Partners":                          {"S2":(575,85,725),    "S1":(567,85,719)},\n    "Post Venta Seller Dev":             {"S2":(194,23,233),    "S1":(177,18,209)},\n    "Publicaciones Seller Dev":          {"S2":(453,80,587),    "S1":(398,76,512)},\n}'
)

# monthly_driver
replace_block(
'monthly_driver = {\n    "Experiencia Impositiva Seller Dev": {"M2":(404,113,572),  "M1":(10,6,17)},\n    "ME Vendedor Seller Dev":            {"M2":(5420,750,6784),"M1":(248,26,290)},\n    "PCF Vendedor Seller Dev":           {"M2":(395,118,569),  "M1":(10,1,16)},\n    "Partners":                          {"M2":(2229,360,2847),"M1":(186,26,239)},\n    "Post Venta Seller Dev":             {"M2":(857,116,1059), "M1":(27,2,32)},\n    "Publicaciones Seller Dev":          {"M2":(2000,374,2600),"M1":(146,25,185)},\n}',
'monthly_driver = {\n    "Experiencia Impositiva Seller Dev": {"M2":(312,108,469),   "M1":(404,113,572)},\n    "ME Vendedor Seller Dev":            {"M2":(4958,754,6266), "M1":(5420,750,6784)},\n    "PCF Vendedor Seller Dev":           {"M2":(536,166,790),   "M1":(395,118,569)},\n    "Partners":                          {"M2":(2228,337,2806), "M1":(2229,360,2847)},\n    "Post Venta Seller Dev":             {"M2":(929,178,1186),  "M1":(857,116,1059)},\n    "Publicaciones Seller Dev":          {"M2":(2639,374,3309), "M1":(2000,374,2600)},\n}'
)

# weekly_proc
replace_block(
'weekly_proc = {\n    "Experiencia Impositiva Seller Dev":{\n        "S2":{"Datos fiscales":(7,0,8),"Emision de Nota Fiscal":(31,14,49),"Facturación":(19,9,31)},\n        "S1":{"Datos fiscales":(3,1,6),"Emision de Nota Fiscal":(29,5,38),"Facturación":(18,7,26)},\n    },\n    "ME Vendedor Seller Dev":{\n        "S2":{"Despacho Ventas y Publicaciones":(402,80,538),"Gestiones Operativas":(94,16,122),"Reputación ME":(440,26,484),"Reversa":(64,18,86),"Viaje del paquete - Vendedor":(58,12,78)},\n        "S1":{"Despacho Ventas y Publicaciones":(538,72,674),"Gestiones Operativas":(82,12,100),"Reputación ME":(418,26,478),"Reversa":(78,18,106),"Viaje del paquete - Vendedor":(50,6,62)},\n    },\n    "PCF Vendedor Seller Dev":{\n        "S2":{"Post Compra Funcionalidades Vendedor":(82,30,129)},\n        "S1":{"Post Compra Funcionalidades Vendedor":(81,26,119)},\n    },\n    "Partners":{\n        "S2":{"Drivers":(489,76,626),"Places Kangu":(78,9,93)},\n        "S1":{"Drivers":(476,90,625),"Places Kangu":(72,9,92)},\n    },\n    "Post Venta Seller Dev":{\n        "S2":{"Anulación de Venta":(6,2,8),"Reputación":(171,16,201)},\n        "S1":{"Anulación de Venta":(3,0,3),"Reputación":(172,19,214)},\n    },\n    "Publicaciones Seller Dev":{\n        "S2":{"Afiliados ML":(165,32,214),"Antes de publicar":(34,1,38),"Calidad de foto":(6,0,6),"Denuncia de usuario":(9,3,13),"Gestión de Publicación":(46,8,62),"PR - Artículos prohibidos":(22,9,34),"PR - Datos Personales":(6,0,6),"PR - Propiedad intelectual":(38,4,44),"PR - Técnica prohibida":(43,7,50),"Potenciar Ventas":(29,12,45)},\n        "S1":{"Afiliados ML":(189,35,246),"Antes de publicar":(26,3,32),"Calidad de foto":(12,3,17),"Denuncia de usuario":(8,4,12),"Gestión de Publicación":(34,11,50),"PR - Artículos prohibidos":(22,6,32),"PR - Datos Personales":(5,1,7),"PR - Propiedad intelectual":(27,10,40),"PR - Técnica prohibida":(39,7,50),"Potenciar Ventas":(19,8,31)},\n    },\n}',
'weekly_proc = {\n    "Experiencia Impositiva Seller Dev":{\n        "S2":{"Datos fiscales":(12,2,14),"Emision de Nota Fiscal":(61,19,88),"Facturación":(39,12,58)},\n        "S1":{"Datos fiscales":(7,0,8),"Emision de Nota Fiscal":(31,14,49),"Facturación":(19,9,31)},\n    },\n    "ME Vendedor Seller Dev":{\n        "S2":{"Despacho Ventas y Publicaciones":(476,90,654),"Gestiones Operativas":(96,26,132),"Reputación ME":(454,26,516),"Reversa":(78,28,114),"Viaje del paquete - Vendedor":(50,8,66)},\n        "S1":{"Despacho Ventas y Publicaciones":(402,80,538),"Gestiones Operativas":(94,16,122),"Reputación ME":(440,26,484),"Reversa":(64,18,86),"Viaje del paquete - Vendedor":(58,12,78)},\n    },\n    "PCF Vendedor Seller Dev":{\n        "S2":{"Post Compra Funcionalidades Vendedor":(95,28,137)},\n        "S1":{"Post Compra Funcionalidades Vendedor":(82,30,129)},\n    },\n    "Partners":{\n        "S2":{"Drivers":(478,74,608),"Places Kangu":(97,11,117)},\n        "S1":{"Drivers":(489,76,626),"Places Kangu":(78,9,93)},\n    },\n    "Post Venta Seller Dev":{\n        "S2":{"Anulación de Venta":(7,0,7),"Reputación":(187,23,226)},\n        "S1":{"Anulación de Venta":(6,2,8),"Reputación":(171,16,201)},\n    },\n    "Publicaciones Seller Dev":{\n        "S2":{"Afiliados ML":(220,43,284),"Antes de publicar":(44,3,50),"Calidad de foto":(5,0,6),"Denuncia de usuario":(10,1,12),"Gestión de Publicación":(37,10,57),"PR - Artículos prohibidos":(20,7,29),"PR - Datos Personales":(1,0,1),"PR - Propiedad intelectual":(41,5,51),"PR - Técnica prohibida":(39,5,54),"Potenciar Ventas":(36,6,43)},\n        "S1":{"Afiliados ML":(165,32,214),"Antes de publicar":(34,1,38),"Calidad de foto":(6,0,6),"Denuncia de usuario":(9,3,13),"Gestión de Publicación":(46,8,62),"PR - Artículos prohibidos":(22,9,34),"PR - Datos Personales":(6,0,6),"PR - Propiedad intelectual":(38,4,44),"PR - Técnica prohibida":(43,7,50),"Potenciar Ventas":(29,12,45)},\n    },\n}'
)

# monthly_proc
replace_block(
'monthly_proc = {\n    "Experiencia Impositiva Seller Dev":{\n        "M2":{"Datos fiscales":(36,7,48),"Emision de Nota Fiscal":(240,62,332),"Facturación":(128,44,192)},\n        "M1":{"Datos fiscales":(1,1,2),"Emision de Nota Fiscal":(7,2,10),"Facturación":(2,3,5)},\n    },\n    "ME Vendedor Seller Dev":{\n        "M2":{"Despacho Ventas y Publicaciones":(2268,428,3020),"Gestiones Operativas":(414,76,544),"Reputación ME":(2142,134,2424),"Reversa":(366,72,482),"Suspensiones ME":(2,0,2),"Viaje del paquete - Vendedor":(228,40,312)},\n        "M1":{"Despacho Ventas y Publicaciones":(148,10,166),"Gestiones Operativas":(20,0,20),"Reputación ME":(70,6,82),"Reversa":(8,8,18),"Viaje del paquete - Vendedor":(2,2,4)},\n    },\n    "PCF Vendedor Seller Dev":{\n        "M2":{"Post Compra Funcionalidades Vendedor":(395,118,569)},\n        "M1":{"Post Compra Funcionalidades Vendedor":(10,1,16)},\n    },\n    "Partners":{\n        "M2":{"Drivers":(1819,302,2339),"Places Kangu":(410,58,508)},\n        "M1":{"Drivers":(172,26,223),"Places Kangu":(14,0,16)},\n    },\n    "Post Venta Seller Dev":{\n        "M2":{"Anulación de Venta":(30,5,36),"Reputación":(827,111,1023)},\n        "M1":{"Reputación":(27,2,32)},\n    },\n    "Publicaciones Seller Dev":{\n        "M2":{"Afiliados ML":(959,166,1227),"Antes de publicar":(162,14,195),"Calidad de foto":(18,5,25),"Denuncia de usuario":(54,12,71),"Gestión de Publicación":(196,42,270),"PR - Artículos prohibidos":(98,31,137),"PR - Datos Personales":(11,6,18),"PR - Propiedad intelectual":(164,31,207),"PR - Técnica prohibida":(203,28,254),"Potenciar Ventas":(135,39,196)},\n        "M1":{"Afiliados ML":(86,8,101),"Antes de publicar":(3,1,4),"Calidad de foto":(11,1,14),"Denuncia de usuario":(3,1,4),"Gestión de Publicación":(10,2,12),"PR - Artículos prohibidos":(8,1,12),"PR - Datos Personales":(4,0,4),"PR - Propiedad intelectual":(8,5,14),"PR - Técnica prohibida":(9,2,12),"Potenciar Ventas":(4,4,8)},\n    },\n}',
'monthly_proc = {\n    "Experiencia Impositiva Seller Dev":{\n        "M2":{"Datos fiscales":(39,7,50),"Emision de Nota Fiscal":(129,26,177),"Facturación":(144,75,242)},\n        "M1":{"Datos fiscales":(36,7,48),"Emision de Nota Fiscal":(240,62,332),"Facturación":(128,44,192)},\n    },\n    "ME Vendedor Seller Dev":{\n        "M2":{"Despacho Ventas y Publicaciones":(1520,360,2062),"Gestiones Operativas":(546,74,692),"Reputación ME":(2080,148,2402),"Reversa":(468,128,668),"Suspensiones ME":(0,2,4),"Viaje del paquete - Vendedor":(344,42,438)},\n        "M1":{"Despacho Ventas y Publicaciones":(2268,428,3020),"Gestiones Operativas":(414,76,544),"Reputación ME":(2142,134,2424),"Reversa":(366,72,482),"Suspensiones ME":(2,0,2),"Viaje del paquete - Vendedor":(228,40,312)},\n    },\n    "PCF Vendedor Seller Dev":{\n        "M2":{"Post Compra Funcionalidades Vendedor":(536,166,790)},\n        "M1":{"Post Compra Funcionalidades Vendedor":(395,118,569)},\n    },\n    "Partners":{\n        "M2":{"Drivers":(1797,278,2277),"Places Kangu":(431,59,529)},\n        "M1":{"Drivers":(1819,302,2339),"Places Kangu":(410,58,508)},\n    },\n    "Post Venta Seller Dev":{\n        "M2":{"Anulación de Venta":(30,11,46),"Reputación":(899,167,1140)},\n        "M1":{"Anulación de Venta":(30,5,36),"Reputación":(827,111,1023)},\n    },\n    "Publicaciones Seller Dev":{\n        "M2":{"Afiliados ML":(1362,180,1687),"Antes de publicar":(219,19,267),"Asignación del Contáctanos - Prustomer":(0,0,1),"Calidad de foto":(43,2,47),"Denuncia de usuario":(85,12,109),"Gestión de Publicación":(213,39,284),"PR - Artículos prohibidos":(77,25,113),"PR - Datos Personales":(11,4,15),"PR - Propiedad intelectual":(198,25,235),"PR - Técnica prohibida":(235,25,286),"Potenciar Ventas":(196,43,265)},\n        "M1":{"Afiliados ML":(959,166,1227),"Antes de publicar":(162,14,195),"Calidad de foto":(18,5,25),"Denuncia de usuario":(54,12,71),"Gestión de Publicación":(196,42,270),"PR - Artículos prohibidos":(98,31,137),"PR - Datos Personales":(11,6,18),"PR - Propiedad intelectual":(164,31,207),"PR - Técnica prohibida":(203,28,254),"Potenciar Ventas":(135,39,196)},\n    },\n}'
)

# Section 2C: MONTH_LABELS, WEEK_LABELS, monthly_history, weekly_history
replace_block(
'MONTH_LABELS = ["Fev", "Mar", "Abr", "Mai"]\nWEEK_LABELS  = ["23/mar", "30/mar", "06/abr", "13/abr", "20/abr", "27/abr"]',
'MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr"]\nWEEK_LABELS  = ["16/mar", "23/mar", "30/mar", "06/abr", "13/abr", "20/abr"]'
)
replace_block(
'    "Experiencia Impositiva Seller Dev": {"Fev":(350,86,477),   "Mar":(312,108,469),  "Abr":(404,113,572),  "Mai":(10,6,17)},\n    "ME Vendedor Seller Dev":            {"Fev":(5136,734,6390),"Mar":(4958,754,6266),"Abr":(5420,750,6784),"Mai":(248,26,290)},\n    "PCF Vendedor Seller Dev":           {"Fev":(529,173,768),  "Mar":(536,166,790),  "Abr":(395,118,569),  "Mai":(10,1,16)},\n    "Partners":                          {"Fev":(1808,217,2198),"Mar":(2228,337,2806),"Abr":(2229,360,2847),"Mai":(186,26,239)},\n    "Post Venta Seller Dev":             {"Fev":(983,209,1291), "Mar":(929,178,1186), "Abr":(857,116,1059), "Mai":(27,2,32)},\n    "Publicaciones Seller Dev":          {"Fev":(2581,381,3231),"Mar":(2639,374,3309),"Abr":(2000,374,2600),"Mai":(146,25,185)},',
'    "Experiencia Impositiva Seller Dev": {"Jan":(574,111,744),  "Fev":(350,86,477),   "Mar":(312,108,469),  "Abr":(404,113,572)},\n    "ME Vendedor Seller Dev":            {"Jan":(8138,1110,9984),"Fev":(5136,734,6390),"Mar":(4958,754,6266),"Abr":(5420,750,6784)},\n    "PCF Vendedor Seller Dev":           {"Jan":(697,244,1059),  "Fev":(529,173,768),  "Mar":(536,166,790),  "Abr":(395,118,569)},\n    "Partners":                          {"Jan":(1793,251,2254), "Fev":(1808,217,2198),"Mar":(2228,337,2806),"Abr":(2229,360,2847)},\n    "Post Venta Seller Dev":             {"Jan":(1206,265,1585), "Fev":(983,209,1291), "Mar":(929,178,1186), "Abr":(857,116,1059)},\n    "Publicaciones Seller Dev":          {"Jan":(3396,475,4216), "Fev":(2581,381,3231),"Mar":(2639,374,3309),"Abr":(2000,374,2600)},',
)
replace_block(
'    "Experiencia Impositiva Seller Dev": {"23/mar":(60,19,90),   "30/mar":(66,25,100),  "06/abr":(150,36,208), "13/abr":(112,33,160), "20/abr":(57,23,88),   "27/abr":(50,13,70)},\n    "ME Vendedor Seller Dev":            {"23/mar":(1088,164,1358),"30/mar":(1016,158,1270),"06/abr":(1676,224,2106),"13/abr":(1154,178,1482),"20/abr":(1058,152,1308),"27/abr":(1166,134,1420)},\n    "PCF Vendedor Seller Dev":           {"23/mar":(113,38,167), "30/mar":(84,23,125),  "06/abr":(98,29,136),  "13/abr":(95,28,137),  "20/abr":(82,30,129),  "27/abr":(81,26,119)},\n    "Partners":                          {"23/mar":(450,75,573), "30/mar":(448,77,574), "06/abr":(460,76,587),  "13/abr":(575,85,725), "20/abr":(567,85,719), "27/abr":(548,99,717)},\n    "Post Venta Seller Dev":             {"23/mar":(214,41,280), "30/mar":(176,39,233), "06/abr":(239,39,301),  "13/abr":(194,23,233), "20/abr":(177,18,209), "27/abr":(175,19,217)},\n    "Publicaciones Seller Dev":          {"23/mar":(574,74,718), "30/mar":(502,88,653), "06/abr":(607,103,769), "13/abr":(453,80,587), "20/abr":(398,76,512), "27/abr":(381,88,517)},',
'    "Experiencia Impositiva Seller Dev": {"16/mar":(82,20,113),  "23/mar":(60,19,90),   "30/mar":(66,25,100),  "06/abr":(150,36,208), "13/abr":(112,33,160), "20/abr":(57,23,88)},\n    "ME Vendedor Seller Dev":            {"16/mar":(1130,152,1420),"23/mar":(1088,164,1358),"30/mar":(1016,158,1270),"06/abr":(1676,224,2106),"13/abr":(1154,178,1482),"20/abr":(1058,152,1308)},\n    "PCF Vendedor Seller Dev":           {"16/mar":(121,31,168), "23/mar":(113,38,167), "30/mar":(84,23,125),  "06/abr":(98,29,136),  "13/abr":(95,28,137),  "20/abr":(82,30,129)},\n    "Partners":                          {"16/mar":(528,69,659), "23/mar":(450,75,573), "30/mar":(448,77,574), "06/abr":(460,76,587),  "13/abr":(575,85,725), "20/abr":(567,85,719)},\n    "Post Venta Seller Dev":             {"16/mar":(215,28,261), "23/mar":(214,41,280), "30/mar":(176,39,233), "06/abr":(239,39,301),  "13/abr":(194,23,233), "20/abr":(177,18,209)},\n    "Publicaciones Seller Dev":          {"16/mar":(591,92,748), "23/mar":(574,74,718), "30/mar":(502,88,653), "06/abr":(607,103,769), "13/abr":(453,80,587), "20/abr":(398,76,512)},',
)
replace_block(
'weekly_history_vig = {drv: {**weekly_history[drv], "04/mai ⚡": drivers_vigente[drv]} for drv in weekly_history}\nWEEK_LABELS_VIG = WEEK_LABELS + ["04/mai ⚡"]',
'weekly_history_vig = {drv: {**weekly_history[drv], "27/abr ⚡": drivers_vigente[drv]} for drv in weekly_history}\nWEEK_LABELS_VIG = WEEK_LABELS + ["27/abr ⚡"]'
)

# ── Section 2E: Canal ─────────────────────────────────────────
# Update canal_weekly S2 (was 20/abr, now 13/abr) and S1 (was 27/abr, now 20/abr)
replace_block(
'"Experiencia Impositiva Seller Dev": {\n        "S2": {"MULTICANAL C2C":(10,17,28), "MULTICANAL CHAT":(47,6,60)},\n        "S1": {"MULTICANAL C2C":(15,10,27), "MULTICANAL CHAT":(35,3,43)},\n    },',
'"Experiencia Impositiva Seller Dev": {\n        "S2": {"MULTICANAL C2C":(31,17,49), "MULTICANAL CHAT":(81,15,110)},\n        "S1": {"MULTICANAL C2C":(10,17,28), "MULTICANAL CHAT":(47,6,60)},\n    },'
)
replace_block(
'"ME Vendedor Seller Dev": {\n        "S2": {"MULTICANAL C2C":(182,30,224), "MULTICANAL CHAT":(876,122,1084)},\n        "S1": {"MULTICANAL C2C":(196,44,262), "MULTICANAL CHAT":(970,90,1158)},\n    },\n    "PCF Vendedor Seller Dev": {\n        "S2": {"MULTICANAL C2C":(30,18,50),  "MULTICANAL CHAT":(52,12,79)},\n        "S1": {"MULTICANAL C2C":(22,14,41),  "MULTICANAL CHAT":(59,12,78)},\n    },\n    "Partners": {\n        "S2": {"MULTICANAL C2C":(67,20,102), "MULTICANAL CHAT":(499,65,616)},\n        "S1": {"MULTICANAL C2C":(68,24,100), "MULTICANAL CHAT":(479,75,616)},\n    },\n    "Post Venta Seller Dev": {\n        "S2": {"MULTICANAL C2C":(32,9,43),   "MULTICANAL CHAT":(145,9,166)},\n        "S1": {"MULTICANAL C2C":(41,4,48),   "MULTICANAL CHAT":(134,15,169)},\n    },\n    "Publicaciones Seller Dev": {\n        "S2": {"MULTICANAL C2C":(54,33,89),  "MULTICANAL CHAT":(343,43,422)},\n        "S1": {"MULTICANAL C2C":(46,35,89),  "MULTICANAL CHAT":(335,52,427)},\n    },\n}\ncanal_monthly',
'"ME Vendedor Seller Dev": {\n        "S2": {"MULTICANAL C2C":(212,36,272), "MULTICANAL CHAT":(932,138,1194)},\n        "S1": {"MULTICANAL C2C":(182,30,224), "MULTICANAL CHAT":(876,122,1084)},\n    },\n    "PCF Vendedor Seller Dev": {\n        "S2": {"MULTICANAL C2C":(23,9,33),  "MULTICANAL CHAT":(69,18,100)},\n        "S1": {"MULTICANAL C2C":(30,18,50),  "MULTICANAL CHAT":(52,12,79)},\n    },\n    "Partners": {\n        "S2": {"MULTICANAL C2C":(61,16,83), "MULTICANAL CHAT":(510,69,637)},\n        "S1": {"MULTICANAL C2C":(67,20,102), "MULTICANAL CHAT":(499,65,616)},\n    },\n    "Post Venta Seller Dev": {\n        "S2": {"MULTICANAL C2C":(60,8,70),   "MULTICANAL CHAT":(133,15,162)},\n        "S1": {"MULTICANAL C2C":(32,9,43),   "MULTICANAL CHAT":(145,9,166)},\n    },\n    "Publicaciones Seller Dev": {\n        "S2": {"MULTICANAL C2C":(49,29,83),  "MULTICANAL CHAT":(404,51,503)},\n        "S1": {"MULTICANAL C2C":(54,33,89),  "MULTICANAL CHAT":(343,43,422)},\n    },\n}\ncanal_monthly'
)

# canal_monthly: M2=Março, M1=Abril (was M2=Abril, M1=Maio)
replace_block(
'    "Experiencia Impositiva Seller Dev": {\n        "M2": {"MULTICANAL C2C":(91,66,166),   "MULTICANAL CHAT":(313,45,404)},\n        "M1": {"MULTICANAL C2C":(3,5,8),       "MULTICANAL CHAT":(7,1,9)},\n    },',
'    "Experiencia Impositiva Seller Dev": {\n        "M2": {"MULTICANAL C2C":(55,31,96),    "MULTICANAL CHAT":(232,64,333)},\n        "M1": {"MULTICANAL C2C":(91,66,166),   "MULTICANAL CHAT":(313,45,404)},\n    },'
)
replace_block(
'    "ME Vendedor Seller Dev": {\n        "M2": {"MULTICANAL C2C":(940,204,1242),"MULTICANAL CHAT":(4468,534,5516)},\n        "M1": {"MULTICANAL C2C":(40,12,52),    "MULTICANAL CHAT":(208,14,238)},\n    },\n    "PCF Vendedor Seller Dev": {\n        "M2": {"MULTICANAL C2C":(112,51,172),  "MULTICANAL CHAT":(280,66,393)},\n        "M1": {"MULTICANAL C2C":(1,1,4),       "MULTICANAL CHAT":(9,0,12)},\n    },\n    "Partners": {\n        "M2": {"MULTICANAL C2C":(277,78,400),  "MULTICANAL CHAT":(1947,281,2440)},\n        "M1": {"MULTICANAL C2C":(23,4,30),     "MULTICANAL CHAT":(162,22,208)},\n    },\n    "Post Venta Seller Dev": {\n        "M2": {"MULTICANAL C2C":(199,35,251),  "MULTICANAL CHAT":(657,81,807)},\n        "M1": {"MULTICANAL C2C":(3,1,5),       "MULTICANAL CHAT":(24,1,27)},\n    },\n    "Publicaciones Seller Dev": {\n        "M2": {"MULTICANAL C2C":(213,130,372), "MULTICANAL CHAT":(1786,242,2224)},\n        "M1": {"MULTICANAL C2C":(13,8,22),     "MULTICANAL CHAT":(133,17,163)},\n    },\n}',
'    "ME Vendedor Seller Dev": {\n        "M2": {"MULTICANAL C2C":(734,210,1030), "MULTICANAL CHAT":(3808,472,4694)},\n        "M1": {"MULTICANAL C2C":(940,204,1242),"MULTICANAL CHAT":(4468,534,5516)},\n    },\n    "PCF Vendedor Seller Dev": {\n        "M2": {"MULTICANAL C2C":(121,52,194),  "MULTICANAL CHAT":(378,100,537)},\n        "M1": {"MULTICANAL C2C":(112,51,172),  "MULTICANAL CHAT":(280,66,393)},\n    },\n    "Partners": {\n        "M2": {"MULTICANAL C2C":(305,89,435),  "MULTICANAL CHAT":(1712,218,2108)},\n        "M1": {"MULTICANAL C2C":(277,78,400),  "MULTICANAL CHAT":(1947,281,2440)},\n    },\n    "Post Venta Seller Dev": {\n        "M2": {"MULTICANAL C2C":(150,49,216),  "MULTICANAL CHAT":(703,115,875)},\n        "M1": {"MULTICANAL C2C":(199,35,251),  "MULTICANAL CHAT":(657,81,807)},\n    },\n    "Publicaciones Seller Dev": {\n        "M2": {"MULTICANAL C2C":(283,86,405),  "MULTICANAL CHAT":(2115,254,2596)},\n        "M1": {"MULTICANAL C2C":(213,130,372), "MULTICANAL CHAT":(1786,242,2224)},\n    },\n}'
)

# ── Section 2F: Oficina ───────────────────────────────────────
# oficina_weekly: S2 now 13/abr, S1 now 20/abr
replace_block(
'    "Experiencia Impositiva Seller Dev": {\n        "S2": {"AEC":(47,6,60), "CTX":(5,3,8), "KTA_BRASIL":(5,14,20)},\n        "S1": {"AEC":(35,3,43), "CTX":(2,2,4), "KTA_BRASIL":(13,8,23)},\n    },\n    "ME Vendedor Seller Dev": {\n        "S2": {"AEC":(248,16,278),"ATE":(374,64,478),"CTX":(88,18,118),"KTA_BRASIL":(346,54,432),"MELICIDADE":(2,0,2)},\n        "S1": {"AEC":(222,20,260),"ATE":(488,54,586),"CTX":(80,10,96), "KTA_BRASIL":(374,50,476),"MELICIDADE":(2,0,2)},\n    },\n    "PCF Vendedor Seller Dev": {\n        "S2": {"AEC":(14,5,25), "ATE":(33,10,46),"CTX":(5,3,10), "KTA_BRASIL":(28,11,45),"MELICIDADE":(2,1,3)},\n        "S1": {"AEC":(30,10,43),"ATE":(21,6,31), "CTX":(5,4,9),  "KTA_BRASIL":(22,6,33), "MELICIDADE":(3,0,3)},\n    },\n    "Partners": {\n        "S2": {"AEC":(25,7,37),  "ATE":(286,33,344),"CTX":(42,9,58), "KTA_BRASIL":(213,36,279)},\n        "S1": {"AEC":(20,8,30),  "ATE":(263,38,329),"CTX":(39,12,62),"KTA_BRASIL":(225,41,295)},\n    },\n    "Post Venta Seller Dev": {\n        "S2": {"AEC":(72,8,83),  "ATE":(34,3,40), "CTX":(6,2,9),  "KTA_BRASIL":(65,5,77)},\n        "S1": {"AEC":(72,9,87),  "ATE":(29,4,41), "CTX":(8,0,8),  "KTA_BRASIL":(66,6,81)},\n    },\n    "Publicaciones Seller Dev": {\n        "S2": {"AEC":(245,34,301),"CTX":(23,6,30), "KTA_BRASIL":(129,36,180)},\n        "S1": {"AEC":(230,38,293),"CTX":(10,3,15), "KTA_BRASIL":(140,46,206),"MELICIDADE":(1,0,1)},\n    },\n}',
'    "Experiencia Impositiva Seller Dev": {\n        "S2": {"AEC":(81,15,110), "CTX":(17,2,19), "KTA_BRASIL":(14,15,30)},\n        "S1": {"AEC":(47,6,60), "CTX":(5,3,8), "KTA_BRASIL":(5,14,20)},\n    },\n    "ME Vendedor Seller Dev": {\n        "S2": {"AEC":(224,20,264),"ATE":(484,58,614),"CTX":(144,18,176),"KTA_BRASIL":(300,78,422),"MELICIDADE":(2,0,2)},\n        "S1": {"AEC":(248,16,278),"ATE":(374,64,478),"CTX":(88,18,118),"KTA_BRASIL":(346,54,432),"MELICIDADE":(2,0,2)},\n    },\n    "PCF Vendedor Seller Dev": {\n        "S2": {"AEC":(20,7,30), "ATE":(46,10,65),"CTX":(5,2,8),  "KTA_BRASIL":(13,7,21), "MELICIDADE":(10,2,12)},\n        "S1": {"AEC":(14,5,25), "ATE":(33,10,46),"CTX":(5,3,10), "KTA_BRASIL":(28,11,45),"MELICIDADE":(2,1,3)},\n    },\n    "Partners": {\n        "S2": {"AEC":(27,4,32),  "ATE":(317,46,389),"CTX":(75,9,95), "KTA_BRASIL":(156,26,209)},\n        "S1": {"AEC":(25,7,37),  "ATE":(286,33,344),"CTX":(42,9,58), "KTA_BRASIL":(213,36,279)},\n    },\n    "Post Venta Seller Dev": {\n        "S2": {"AEC":(67,10,79),  "ATE":(48,5,61), "CTX":(24,2,29), "KTA_BRASIL":(55,6,64)},\n        "S1": {"AEC":(72,8,83),  "ATE":(34,3,40), "CTX":(6,2,9),  "KTA_BRASIL":(65,5,77)},\n    },\n    "Publicaciones Seller Dev": {\n        "S2": {"AEC":(294,38,363),"CTX":(23,8,33), "KTA_BRASIL":(134,34,188),"MELICIDADE":(2,0,2)},\n        "S1": {"AEC":(245,34,301),"CTX":(23,6,30), "KTA_BRASIL":(129,36,180)},\n    },\n}'
)

# oficina_monthly: M2=Março, M1=Abril
replace_block(
'    "Experiencia Impositiva Seller Dev": {\n        "M2": {"AEC":(313,44,403),"CTX":(42,13,56), "KTA_BRASIL":(49,54,111)},\n        "M1": {"AEC":(7,1,9),     "KTA_BRASIL":(3,5,8)},\n    },\n    "ME Vendedor Seller Dev": {\n        "M2": {"AEC":(1234,86,1404),"ATE":(2184,330,2808),"CTX":(514,78,644),"KTA_BRASIL":(1474,244,1902),"MELICIDADE":(12,2,14)},\n        "M1": {"AEC":(22,4,30),     "ATE":(132,14,150),   "KTA_BRASIL":(94,8,110)},\n    },\n    "PCF Vendedor Seller Dev": {\n        "M2": {"AEC":(93,35,144),"ATE":(166,37,225),"CTX":(28,13,44),"KTA_BRASIL":(79,28,118),"MELICIDADE":(28,5,37)},\n        "M1": {"AEC":(4,0,5),    "ATE":(2,1,4),     "KTA_BRASIL":(4,0,7)},\n    },\n    "Partners": {\n        "M2": {"AEC":(95,26,135),  "ATE":(1202,164,1485),"CTX":(244,45,322),"KTA_BRASIL":(687,124,903)},\n        "M1": {"AEC":(8,1,10),     "ATE":(100,8,120),    "KTA_BRASIL":(77,17,108)},\n    },\n    "Post Venta Seller Dev": {\n        "M2": {"AEC":(326,48,400),"ATE":(183,18,227),"CTX":(73,12,94),"KTA_BRASIL":(270,38,333),"MELICIDADE":(5,0,5)},\n        "M1": {"AEC":(8,1,9),     "ATE":(8,1,10),   "KTA_BRASIL":(11,0,13)},\n    },\n    "Publicaciones Seller Dev": {\n        "M2": {"AEC":(1282,177,1585),"CTX":(94,29,134),"KTA_BRASIL":(618,166,871),"MELICIDADE":(5,0,5)},\n        "M1": {"AEC":(99,11,119),    "KTA_BRASIL":(47,14,66)},\n    },\n}',
'    "Experiencia Impositiva Seller Dev": {\n        "M2": {"AEC":(252,68,359),"CTX":(36,16,57),"KTA_BRASIL":(23,20,48),"MELICIDADE":(1,2,3)},\n        "M1": {"AEC":(313,44,403),"CTX":(42,13,56),"KTA_BRASIL":(49,54,111)},\n    },\n    "ME Vendedor Seller Dev": {\n        "M2": {"AEC":(1196,112,1414),"ATE":(2376,380,3012),"CTX":(534,80,684),"KTA_BRASIL":(780,168,1052),"MELICIDADE":(70,12,98)},\n        "M1": {"AEC":(1234,86,1404),"ATE":(2184,330,2808),"CTX":(514,78,644),"KTA_BRASIL":(1474,244,1902),"MELICIDADE":(12,2,14)},\n    },\n    "PCF Vendedor Seller Dev": {\n        "M2": {"AEC":(177,40,242),"ATE":(195,67,305),"CTX":(49,20,77),"KTA_BRASIL":(55,22,79),"MELICIDADE":(60,16,86)},\n        "M1": {"AEC":(93,35,144),"ATE":(166,37,225),"CTX":(28,13,44),"KTA_BRASIL":(79,28,118),"MELICIDADE":(28,5,37)},\n    },\n    "Partners": {\n        "M2": {"AEC":(137,35,189),"ATE":(1400,193,1741),"CTX":(382,45,465),"KTA_BRASIL":(309,63,409)},\n        "M1": {"AEC":(95,26,135),"ATE":(1202,164,1485),"CTX":(244,45,322),"KTA_BRASIL":(687,124,903)},\n    },\n    "Post Venta Seller Dev": {\n        "M2": {"AEC":(337,74,436),"ATE":(308,44,378),"CTX":(106,29,148),"KTA_BRASIL":(154,24,192),"MELICIDADE":(23,6,30)},\n        "M1": {"AEC":(326,48,400),"ATE":(183,18,227),"CTX":(73,12,94),"KTA_BRASIL":(270,38,333),"MELICIDADE":(5,0,5)},\n    },\n    "Publicaciones Seller Dev": {\n        "M2": {"AEC":(1406,181,1746),"CTX":(830,118,1023),"KTA_BRASIL":(377,66,500),"MELICIDADE":(25,4,33)},\n        "M1": {"AEC":(1282,177,1585),"CTX":(94,29,134),"KTA_BRASIL":(618,166,871),"MELICIDADE":(5,0,5)},\n    },\n}'
)

# ── Section 2G: p_c_weekly shift ─────────────────────────────
# S2 becomes 13/abr data (currently empty for 13/abr), S1 becomes old S2 (20/abr)
# The 13/abr P_C data was not collected, so keep S2 as empty; S1 = old S2 data
# Just swap the keys: new S1 = old S2, new S2 = empty (no data for 13/abr)
# replace_block p_c_weekly removido — renaming quebrado, deixar p_c/p_o como estão
# This approach is getting too complex. Let me handle P_C/P_O differently.

# Write the file
with open(r'C:\claudinho\generate_html.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("File written. Checking for issues...")

# Verify key replacements
import re
checks = [
    ('S1_LABEL', '"20/abr'),
    ('M1_LABEL', '"Abril 2026"'),
    ('NPS_TARGET', '59.19'),
    ('weekly_driver.*S2.*112,33', None),
    ('monthly_driver.*M2.*312,108', None),
    ('WEEK_LABELS.*16/mar', None),
    ('MONTH_LABELS.*Jan', None),
]
with open(r'C:\claudinho\generate_html.py', encoding='utf-8') as f:
    txt = f.read()
for label, val in checks:
    found = bool(re.search(label, txt)) if val is None else (val in txt)
    print(f'  {label}: {"OK" if found else "MISSING"}')
