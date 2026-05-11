#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca TODOS os detratores (NPS=-1) do processo top ofensor por driver no mês,
cruza com BT_CX_TRANSCRIPT (USER+REP) e o comentário da pesquisa,
gera categorias e conclusões por padrão de contato.
Salva em _recurrence_cases.json.
"""
import json, time, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import bigquery
bq = bigquery.Client(project="meli-bi-data")

# ── Carrega contexto ──────────────────────────────────────────────────
with open('_process_analysis.json', encoding='utf-8') as f:
    PA = json.load(f)

with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)
S1_LABEL = ns.get('S1_LABEL', '')

MON_NUM = {"jan":"01","fev":"02","mar":"03","abr":"04","mai":"05",
           "jun":"06","jul":"07","ago":"08","set":"09","out":"10","nov":"11","dez":"12"}

def parse_date(lbl_part, year="2026"):
    lbl_part = lbl_part.strip().replace("‪","").replace("‎","").strip()
    parts = lbl_part.split("/")
    if len(parts) == 2:
        day, mon = parts[0].strip().zfill(2), parts[1].strip().lower()
        return f"{year}-{MON_NUM.get(mon,'05')}-{day}"
    return None

if S1_LABEL and "–" in S1_LABEL:
    parts = S1_LABEL.split("–")
    S1_START = parse_date(parts[0]) or "2026-05-04"
    S1_END   = parse_date(parts[1]) or "2026-05-10"
else:
    S1_START, S1_END = "2026-05-04", "2026-05-10"

MON_START, MON_END = "2026-05-01", "2026-05-11"
ABR_START, ABR_END = "2026-04-01", "2026-04-30"

print(f"S1: {S1_START} → {S1_END} | Mês: {MON_START} → {MON_END}")

DRIVER_GROUPS = {
    "ME Vendedor":     ["ME Vendedor Seller Dev","ME Vendedor Mature","ME Vendedor Meli Pro"],
    "Exp. Impositiva": ["Experiencia Impositiva Seller Dev","Experiencia Impositiva Mature","Experiencia Impositiva Meli Pro"],
    "PCF Vendedor":    ["PCF Vendedor Seller Dev","PCF Vendedor Mature","PCF Vendedor Meli Pro"],
    "Post Venta":      ["Post Venta Seller Dev","Post Venta Mature","Post Venta Meli Pro"],
    "Publicaciones":   ["Publicaciones Seller Dev","Publicaciones Mature","Publicaciones Meli Pro"],
    "Partners":        ["Partners"],
    "Otros CV":        ["Otros CV"],
}

# ── SQLs ──────────────────────────────────────────────────────────────
SQL_DETRACTORS = """
SELECT
  CAST(CAS_CASE_ID AS STRING)               AS case_id,
  COALESCE(NULLIF(TRIM(COMMENTS),''), '')   AS survey_comment,
  COALESCE(CDU, 'N/I')                      AS cdu,
  COALESCE(CX_SOL_NAME, 'N/I')             AS solucao,
  COALESCE(ANTIGUEDAD_REP, 'N/I')          AS seniority,
  COALESCE(SURVEY_CHANNEL, 'N/I')          AS canal
FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
WHERE SIT_SITE_ID = 'MLB'
  AND SURVEY_CENTER = 'BR'
  AND NPS = -1
  AND PRO_PROCESS_NAME = '{proc}'
  AND SURVEY_DATE_SURVEY BETWEEN '{start}' AND '{end}'
  AND CAS_CASE_ID IS NOT NULL
ORDER BY RAND()
LIMIT {lim}
"""

SQL_TRANSCRIPT = """
SELECT
  CAST(CAS_CASE_ID AS STRING)                                        AS cid,
  SPEAKER_ROLE,
  SUBSTR(COALESCE(OBFUSCATED_MESSAGE_CONTENT,''), 1, 400)            AS msg,
  INITIAL_DTTM
FROM `meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT`
WHERE CAS_CASE_ID IN ({ids})
  AND SPEAKER_ROLE IN ('USER','REP')
ORDER BY CAS_CASE_ID, INITIAL_DTTM
"""

def fetch_detractors(proc, start, end, lim=80):
    sql = SQL_DETRACTORS.format(
        proc=proc.replace("'","''"), start=start, end=end, lim=lim)
    try:
        rows = list(bq.query(sql).result())
        return [{
            "case_id":        r.case_id,
            "survey_comment": r.survey_comment or "",
            "cdu":            r.cdu,
            "solucao":        r.solucao,
            "seniority":      r.seniority,
            "canal":          r.canal,
        } for r in rows if r.case_id]
    except Exception as e:
        print(f"    WARN detractors: {e}")
        return []

def fetch_transcripts(case_ids, batch=900):
    result = {}
    for i in range(0, len(case_ids), batch):
        chunk = case_ids[i:i+batch]
        sql = SQL_TRANSCRIPT.format(ids=",".join(chunk))
        try:
            rows = list(bq.query(sql).result())
            for r in rows:
                cid = r.cid
                if cid not in result:
                    result[cid] = []
                result[cid].append({"role": r.SPEAKER_ROLE, "msg": (r.msg or "").strip()})
        except Exception as e:
            print(f"    WARN transcript batch {i}: {e}")
        time.sleep(0.3)
    return result

# Palavras de saudação/genéricas para ignorar
SKIP_PHRASES = [
    "tudo bem","bom dia","boa tarde","boa noite","olá","ola","quero falar",
    "falar com","assistente","atendente","preciso falar","queria falar",
    "pode me ajudar","obrigado","obrigada","aguardo","ok","sim","não","nao",
    "hola","buenos","gracias","por favor",
]

def is_meaningful(msg, min_len=30):
    if len(msg) < min_len:
        return False
    ml = msg.lower()
    return not any(ml.strip().startswith(p) for p in SKIP_PHRASES)

def summarize_case(case_meta, msgs):
    """
    Gera resumo estruturado de um caso:
    - motivo: o que o seller descreveu (primeiro msg USER substantivo)
    - desfecho: o que o atendente fez no encerramento
    - transferido: se houve transferência
    - resolvido: se o atendente confirmou resolução
    - comentario_pesquisa: comentário do seller na pesquisa NPS
    """
    user_msgs = [m["msg"] for m in msgs if m["role"] == "USER" and len(m["msg"]) > 15]
    rep_msgs  = [m["msg"] for m in msgs if m["role"] == "REP"  and len(m["msg"]) > 15]

    # Motivo: primeiro msg USER substantivo
    motivo = ""
    for m in user_msgs:
        if is_meaningful(m):
            motivo = m[:250]
            break
    if not motivo and user_msgs:
        motivo = user_msgs[0][:250]

    # Desfecho: última msg REP
    desfecho = rep_msgs[-1][:200] if rep_msgs else ""

    # Detecção de padrões operacionais
    all_text = " ".join(m["msg"].lower() for m in msgs)
    transferido = any(w in all_text for w in
        ["transfer","encaminhar","encaminhando","vou te passar","outro setor","supervisao","supervisor"])
    resolvido = any(w in all_text for w in
        ["resolvido","solucionado","concluido","concluído","pronto","feito","finalizado"])
    escalacao = any(w in all_text for w in
        ["procon","judicial","advogado","reclamacao formal","registro de ocorrencia"])

    return {
        "motivo":             motivo,
        "desfecho":           desfecho,
        "transferido":        transferido,
        "resolvido":          resolvido,
        "escalacao":          escalacao,
        "survey_comment":     case_meta.get("survey_comment",""),
        "cdu":                case_meta.get("cdu",""),
        "solucao":            case_meta.get("solucao",""),
        "seniority":          case_meta.get("seniority",""),
        "canal":              case_meta.get("canal",""),
        "n_msgs":             len(msgs),
    }

def _synthesize_theme(motivos, survey_comments, cdu, n, n_transf, n_resol, n_escal):
    """
    Gera síntese analítica do tema de contato a partir dos padrões identificados.
    Sem citações diretas — descreve o padrão dominante com evidências quantitativas.
    """
    all_text = " ".join(motivos + survey_comments).lower()

    THEMES = {
        "atraso na entrega / prazo não cumprido":
            ["atraso","atrasado","nao chegou","não chegou","prazo","data","entrega","reagendando","reaagendado"],
        "cobrança não reconhecida / não autorizada":
            ["cobranca","cobranc","cobrado","tarifa","nao autorizei","não autorizei","indevido","nao reconh","nao deve"],
        "produto com defeito / embalagem danificada":
            ["defeito","quebrado","danificado","avariado","embalagem","lacre"],
        "cancelamento de venda / pedido":
            ["cancelar","cancelamento","desistir","nao quero","não quero"],
        "devolução sem resolução":
            ["devoluc","devolveu","produto devolvido","retorno","estorno devoluc"],
        "mediação / reclamo afetando reputação":
            ["mediacao","mediação","reclamo","reclamacao","reputacao","reputação","penalizado","impactou"],
        "conta suspensa ou bloqueada":
            ["suspensa","bloqueada","restrita","sem acesso","inativada","inativou"],
        "certificado digital / Faturador bloqueado":
            ["certificado","faturador","nf-e","nota fiscal","emissao","cnpj","sefaz"],
        "pagamento retido / reembolso pendente":
            ["pagamento","estorno","reembolso","nao recebi","não recebi","liberar","retido","liberacao"],
        "publicação suspensa ou removida":
            ["publicacao","publicação","anuncio","anúncio","removida","pausada","suspensa publicac"],
        "comissão ou afiliado não pago":
            ["comissao","comissão","afiliado","nao pago","não pago","invalidado","nao aprovada"],
        "métricas / nível de lealdade contestado":
            ["metricas","métricas","nivel","nível","lealtad","pontuacao","pontuação","rebaixado"],
        "entregador não compareceu / falha logística":
            ["entregador","motorista","nao compareceu","não compareceu","nao entregou","nao foi coletado"],
        "envio Full parado / problema no CD":
            ["full","centro de distribuicao","inbound","cd parado","estoque parado"],
        "atendimento sem resolução / múltiplos contatos":
            ["nao resolveu","não resolveu","varios atendentes","vários atendentes","ja tentei","já tentei",
             "segunda vez","terceira","semanas","sem retorno","continua"],
    }

    theme_hits = {}
    for theme, kws in THEMES.items():
        hits = sum(1 for kw in kws if kw in all_text)
        if hits > 0:
            theme_hits[theme] = hits

    top = sorted(theme_hits.items(), key=lambda x: -x[1])[:2]

    # Constrói síntese
    if top:
        main = top[0][0]
        sec  = top[1][0] if len(top) > 1 else None
        if sec and top[1][1] >= 2:
            synthesis = f"Sellers contactaram principalmente sobre {main}, com ocorrências de {sec}."
        else:
            synthesis = f"Sellers contactaram sobre {main}."
    else:
        synthesis = f"Sellers reportaram problemas relacionados a {cdu} ({n} casos no período)."

    # Adiciona padrão operacional como contexto
    ops_parts = []
    if n_transf > 0:
        pct = round(100*n_transf/n)
        ops_parts.append(f"{pct}% foram transferidos para outro setor sem resolução no 1º contato")
    if n_resol < n // 2:
        ops_parts.append(f"apenas {round(100*n_resol/n)}% tiveram resolução confirmada")
    elif n_resol > 0:
        ops_parts.append(f"{round(100*n_resol/n)}% com resolução confirmada")
    if n_escal > 0:
        ops_parts.append(f"{n_escal} caso{'s' if n_escal>1 else ''} com risco de escalação (PROCON/judicial)")

    if ops_parts:
        synthesis += " " + "; ".join(ops_parts[:2]).capitalize() + "."

    return synthesis


def build_categories(cases_summary):
    """
    Agrupa os casos por CDU, sintetiza o tema e gera conclusão analítica.
    """
    by_cdu = {}
    for cid, s in cases_summary.items():
        cdu = s.get("cdu","N/I")
        by_cdu.setdefault(cdu, []).append({"cid": cid, **s})

    categories = []
    for cdu, cases in sorted(by_cdu.items(), key=lambda x: -len(x[1])):
        n = len(cases)
        if n < 1:
            continue

        n_transf = sum(1 for c in cases if c.get("transferido"))
        n_resol  = sum(1 for c in cases if c.get("resolvido"))
        n_escal  = sum(1 for c in cases if c.get("escalacao"))

        motivos   = [c.get("motivo","")         for c in cases if c.get("motivo")         and len(c.get("motivo","")) > 20]
        comments  = [c.get("survey_comment","") for c in cases if c.get("survey_comment") and len(c.get("survey_comment","")) > 10]

        narrative = _synthesize_theme(motivos, comments, cdu, n, n_transf, n_resol, n_escal)

        categories.append({
            "sub_pattern":   cdu,
            "s1_count":      n,
            "monthly_count": n,
            "examples":      [c["cid"] for c in cases[:3]],
            "narrative":     narrative,
            "n_transfer":    n_transf,
            "n_resolved":    n_resol,
            "n_escalation":  n_escal,
        })

    return sorted(categories, key=lambda x: -x["s1_count"])[:4]

# ── Principal ──────────────────────────────────────────────────────────
result = {}

for grp, drvs in DRIVER_GROUPS.items():
    neg = PA.get(grp, {}).get("top_neg", {})
    top_proc = neg.get("proc")
    if not top_proc:
        print(f"\n[{grp}] sem top_neg — pulando")
        continue

    print(f"\n{'='*60}")
    print(f"[{grp}] Processo: {top_proc}")
    result[grp] = {"top_proc": top_proc, "weekly": {}, "monthly": {}, "categories_mon": [], "categories_wk": []}

    # ── Mês atual (Mai) ──────────────────────────────────────────────
    print(f"  [Mai] buscando detratores...")
    mon_cases = fetch_detractors(top_proc, MON_START, MON_END, lim=80)
    print(f"    {len(mon_cases)} detratores encontrados")
    time.sleep(0.5)

    if mon_cases:
        mon_ids = [c["case_id"] for c in mon_cases]
        mon_trx = fetch_transcripts(mon_ids)
        print(f"    {len(mon_trx)} transcrições obtidas")

        mon_meta = {c["case_id"]: c for c in mon_cases}
        for cid, msgs in mon_trx.items():
            result[grp]["monthly"][cid] = summarize_case(mon_meta.get(cid,{}), msgs)

        # Casos sem transcrição — registra só metadados
        for c in mon_cases:
            if c["case_id"] not in result[grp]["monthly"]:
                result[grp]["monthly"][c["case_id"]] = {
                    "motivo": "", "desfecho": "", "transferido": False,
                    "resolvido": False, "escalacao": False,
                    "survey_comment": c.get("survey_comment",""),
                    "cdu": c.get("cdu",""), "solucao": c.get("solucao",""),
                    "seniority": c.get("seniority",""), "canal": c.get("canal",""),
                    "n_msgs": 0,
                }

        result[grp]["categories_mon"] = build_categories(result[grp]["monthly"])
        print(f"    {len(result[grp]['categories_mon'])} categorias geradas (mensal)")
        for cat in result[grp]["categories_mon"]:
            print(f"      · {cat['sub_pattern']} ({cat['s1_count']} casos)")

    # ── S1 semanal ───────────────────────────────────────────────────
    print(f"  [S1] buscando detratores...")
    wk_cases = fetch_detractors(top_proc, S1_START, S1_END, lim=40)
    print(f"    {len(wk_cases)} detratores encontrados")
    time.sleep(0.5)

    if wk_cases:
        wk_ids = [c["case_id"] for c in wk_cases]
        wk_trx = fetch_transcripts(wk_ids)
        print(f"    {len(wk_trx)} transcrições obtidas")

        wk_meta = {c["case_id"]: c for c in wk_cases}
        for cid, msgs in wk_trx.items():
            result[grp]["weekly"][cid] = summarize_case(wk_meta.get(cid,{}), msgs)
        for c in wk_cases:
            if c["case_id"] not in result[grp]["weekly"]:
                result[grp]["weekly"][c["case_id"]] = {
                    "motivo": "", "survey_comment": c.get("survey_comment",""),
                    "cdu": c.get("cdu",""), "n_msgs": 0,
                    "transferido": False, "resolvido": False, "escalacao": False,
                }

        result[grp]["categories_wk"] = build_categories(result[grp]["weekly"])
        print(f"    {len(result[grp]['categories_wk'])} categorias geradas (S1)")

with open("_recurrence_cases.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n\nSalvo em _recurrence_cases.json")
print("\nResumo:")
for grp, data in result.items():
    print(f"  {grp}: proc={data['top_proc']} | "
          f"S1={len(data['weekly'])} casos | Mai={len(data['monthly'])} casos | "
          f"cats={len(data['categories_mon'])}")
