#!/usr/bin/env python3
"""Replaces _recurrence_deep in both dashboard scripts with BQ-based version."""
import re

NEW_FUNC = r'''def _recurrence_deep(grp, trx_source=None, top_proc=None):
    """
    Identifica padrões recorrentes de detratores usando dados reais do BQ
    (_recurrence_cases.json). Se não disponível, retorna lista vazia.
    """
    rc = _RC.get(grp, {})
    top_proc_name = rc.get("top_proc") or (top_proc or {}).get("proc") or ""

    if not rc or (not rc.get("weekly") and not rc.get("monthly")):
        return []

    weekly_cases  = rc.get("weekly",  {})
    monthly_cases = rc.get("monthly", {})

    def _complaint(d):
        return (d.get("complaint") or "").lower()

    all_wk  = {cid: _complaint(d) for cid, d in weekly_cases.items()}
    all_mon = {cid: _complaint(d) for cid, d in monthly_cases.items()}

    SUB_PATTERNS = {
        "envio e logistica": {
            "atraso de entrega sem atualizacao de status":
                ["atraso","atrasado","nao chegou","prazo","data","entrega"],
            "coleta nao realizada":
                ["coleta","inbound","agendar coleta","nao foi coletado"],
            "entregador nao compareceu":
                ["entregador","motorista","nao entregou","portao"],
            "envio Full parado no CD":
                ["full","centro de distribuicao","inbound","estoque parado"],
        },
        "cobranca e faturamento": {
            "cobranca de ADS nao autorizada":
                ["ads","publicidade","campanha","tarifa","ativei"],
            "bloqueio do Faturador / certificado digital":
                ["faturador","certificado","nf-e","nota fiscal","emiss","cnpj"],
            "cobranca indevida sem resolucao":
                ["cobrado indevid","cobranca errada","nao reconh","nao devo","desconto indevido"],
            "fatura ou debito automatico nao reconhecido":
                ["fatura","debito","automatico","debit","descontou"],
        },
        "mediacao e disputa": {
            "reclamo afetando reputacao indevidamente":
                ["reputacao","reclamo","afetou","impactou","penalizado"],
            "mediacao aberta sem prazo claro":
                ["mediacao","sem resposta","aguardando","sem prazo","em analise"],
            "decisao considerada injusta":
                ["injusto","erro do ml","nao e minha culpa","arbitrario"],
        },
        "publicacao e conta": {
            "comissao ou afiliado nao pago":
                ["afiliado","comissao","nao aprovada","invalidada"],
            "suspensao ou remocao de publicacao":
                ["suspensa","pausada","removida","publicacao","anuncio"],
            "atendimento automatico sem analise do caso":
                ["robotico","automatico","frases prontas","nao leu"],
        },
        "devolucao e reembolso": {
            "devolucao impactando reputacao":
                ["devolucao","impactou","reputacao","cancelamento"],
            "reembolso pendente sem atualizacao":
                ["reembolso","estorno","nao recebi","pendente"],
        },
        "outros": {
            "problema nao resolvido apos multiplos contatos":
                ["ja tentei","ja abri","segunda vez","terceira","semanas","meses tentando","varias vezes"],
            "urgencia operacional sem canal de resolucao":
                ["urgente","hoje","amanha","vence","nao consigo","bloqueado"],
        },
    }

    def _best_pattern(txt):
        best_score, best_key = 0, None
        for cat, sub_dict in SUB_PATTERNS.items():
            for sub, kws in sub_dict.items():
                s = sum(1 for k in kws if k in txt)
                if s > best_score:
                    best_score, best_key = s, (cat, sub)
        return best_key if best_score >= 1 else None

    cid_best     = {c: p for c, t in all_wk.items()  if (p := _best_pattern(t))}
    cid_best_mon = {c: p for c, t in all_mon.items() if (p := _best_pattern(t))}

    results = []
    seen = set()
    for cat, sub_dict in SUB_PATTERNS.items():
        for sub, kws in sub_dict.items():
            key = (cat, sub)
            if key in seen:
                continue
            ex_cids  = [c for c, k in cid_best.items()     if k == key][:3]
            mon_hits = sum(1 for k in cid_best_mon.values() if k == key)
            if len(ex_cids) >= 1 and mon_hits >= 1:
                seen.add(key)
                complaints_real = [weekly_cases[c].get("complaint", "")
                                   for c in ex_cids if c in weekly_cases]
                unique = list(dict.fromkeys(c[:160] for c in complaints_real if c))[:2]
                relatos = "; ".join(f'"{r}"' for r in unique) if unique else ""
                narrative = f"Processo: {top_proc_name}. Padrão em {len(ex_cids)} caso{'s' if len(ex_cids)>1 else ''} S1."
                if relatos:
                    narrative += f" Relatos: {relatos}."
                results.append({
                    "categoria":     cat,
                    "sub_pattern":   sub,
                    "s1_count":      len(ex_cids),
                    "monthly_count": mon_hits,
                    "examples":      ex_cids,
                    "narrative":     narrative,
                })

    if not results and weekly_cases and monthly_cases:
        # Sem padrão identificado — mostra casos mais ricos diretamente
        top_cids = sorted(
            weekly_cases.items(),
            key=lambda x: len(x[1].get("complaint", "")),
            reverse=True
        )[:3]
        complaints_txt = [d.get("complaint", "") for _, d in top_cids if d.get("complaint")]
        unique = list(dict.fromkeys(c[:160] for c in complaints_txt))[:2]
        relatos = "; ".join(f'"{r}"' for r in unique) if unique else ""
        narrative = f"Processo: {top_proc_name}. Padrão recorrente em S1 e mensal."
        if relatos:
            narrative += f" Relatos: {relatos}."
        results.append({
            "categoria":     "recorrencia geral",
            "sub_pattern":   f"Detratores em {top_proc_name}",
            "s1_count":      len(weekly_cases),
            "monthly_count": len(monthly_cases),
            "examples":      [c for c, _ in top_cids],
            "narrative":     narrative,
        })

    results.sort(key=lambda x: -(x["s1_count"] + x["monthly_count"]))
    return results[:4]

'''

def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find start and end of _recurrence_deep
    start = content.find('\ndef _recurrence_deep(grp')
    if start == -1:
        start = content.find('def _recurrence_deep(grp')
    else:
        start += 1  # skip the leading \n

    end = content.find('\ndef _deep_trx_insights', start)
    if end == -1:
        end = content.find('\ndef _deep_trx', start)
    if end == -1:
        print(f"ERROR: could not find end marker in {path}")
        return False

    new_content = content[:start] + NEW_FUNC + '\n' + content[end+1:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Patched: {path}")
    return True

patch_file('generate_html_tendencias.py')
patch_file('generate_html_seller_dev.py')
print("Done.")
