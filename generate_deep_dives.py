#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_deep_dives.py
Gera resumos executivos (bullets) por driver para o Deep Dive.
Analisa: CDU, Solucao, Senioridade, Motivos + Transcricoes USER/REP via Claude.
Output: dd_summaries.json  (lido por build_driver_impact.py)

Uso: python generate_deep_dives.py
"""
import json, subprocess, io, csv, sys, os, time
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
M1_START = "2026-04-01"
M1_END   = "2026-04-27"
M2_START = "2026-03-01"
M2_END   = "2026-03-31"
S1_START = "2026-04-20"
S1_END   = "2026-04-26"
S2_START = "2026-04-13"
S2_END   = "2026-04-19"

MIN_SURVEYS_FOR_ANALYSIS = 15   # drivers com menos surveys: sem analise
MAX_TRANSCRIPTS          = 15   # amostras por periodo

try:
    import anthropic
    CLAUDE_CLIENT = anthropic.Anthropic()
except ImportError:
    print("AVISO: anthropic nao instalado. Instale com: pip install anthropic")
    CLAUDE_CLIENT = None

# ── DADOS DE APOIO ────────────────────────────────────────────────────────────
with open("dd_breakdown.json", encoding="utf-8") as f:
    DD_BREAKDOWN = json.load(f)

def escape_sq(s):
    return s.replace("'", "''")

# ── BIGQUERY ──────────────────────────────────────────────────────────────────
def bq(sql, max_rows=500):
    cmd = f'bq query --use_legacy_sql=false --format=csv --max_rows={max_rows} "{sql}"'
    # No Windows, bq e um .cmd; usar shell=True e passar SQL como arquivo temporario
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(sql)
        sql_file = tf.name
    try:
        result = subprocess.run(
            f'type "{sql_file}" | bq query --use_legacy_sql=false --format=csv --max_rows={max_rows}',
            shell=True, capture_output=True
        )
    finally:
        try:
            os.unlink(sql_file)
        except Exception:
            pass

    out  = result.stdout.decode("utf-8", errors="replace")
    err  = result.stderr.decode("utf-8", errors="replace")
    if result.returncode != 0 or ("Error" in err and "Waiting" not in err):
        clean_err = "\n".join(l for l in err.split("\n") if "Error" in l or "error" in l)
        print(f"  BQ erro (rc={result.returncode}): {clean_err[:200]}")
        return []
    lines = out.split("\n")
    header_idx = next(
        (i for i, l in enumerate(lines)
         if "," in l and not l.startswith("Waiting") and not l.startswith("bq")),
        -1
    )
    if header_idx < 0:
        return []
    csv_text = "\n".join(lines[header_idx:])
    return list(csv.DictReader(io.StringIO(csv_text)))

def get_processes(driver):
    """Retorna lista de processos do driver com dados em M1."""
    p = DD_BREAKDOWN.get(driver, {}).get("P", {}).get("M1", {})
    return [k for k, v in p.items() if v.get("s", 0) >= MIN_SURVEYS_FOR_ANALYSIS]

def worst_best_process(driver):
    """Pior e melhor processo por delta NPS MoM."""
    p_m1 = DD_BREAKDOWN.get(driver, {}).get("P", {}).get("M1", {})
    p_m2 = DD_BREAKDOWN.get(driver, {}).get("P", {}).get("M2", {})
    items = []
    for proc in p_m1:
        n1 = p_m1[proc].get("nps"); n2 = p_m2.get(proc, {}).get("nps")
        s1 = p_m1[proc].get("s", 0)
        if n1 is not None and n2 is not None and s1 >= MIN_SURVEYS_FOR_ANALYSIS:
            items.append({"proc": proc, "delta": n1 - n2, "nps": n1, "s": s1})
    items.sort(key=lambda x: x["delta"])
    return (items[0] if items else None), (items[-1] if items else None)

# ── QUERY QUANTITATIVA ────────────────────────────────────────────────────────
def quant_query(processes, date_start, date_end):
    if not processes:
        return []
    proc_in = "'" + "','".join(escape_sq(p) for p in processes[:10]) + "'"
    sql = f"""
    SELECT
      PRO_PROCESS_NAME as processo,
      CDU,
      CX_SOL_NAME as solucao,
      ANTIGUEDAD_REP as senioridade,
      USER_TEAM_CHANNEL as canal,
      COUNT(*) as surveys,
      SUM(PROMOTER) as promoters,
      SUM(DETRACTOR) as detractors,
      ROUND(100*(SUM(PROMOTER)-SUM(DETRACTOR))/COUNT(*),1) as nps,
      STRING_AGG(DISTINCT RES_DETRACTION_REASON LIMIT 8) as motivos_det,
      STRING_AGG(DISTINCT RES_PROMOTION_REASON  LIMIT 8) as motivos_pro
    FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL`
    WHERE SIT_SITE_ID = 'MLB'
      AND SURVEY_CENTER = 'BR'
      AND SURVEY_DATE_SURVEY BETWEEN '{date_start}' AND '{date_end}'
      AND PRO_PROCESS_NAME IN ({proc_in})
    GROUP BY 1,2,3,4,5
    HAVING COUNT(*) >= 3
    ORDER BY surveys DESC
    """
    return bq(sql, max_rows=300)

# ── QUERY TRANSCRICOES ────────────────────────────────────────────────────────
def transcript_query(processes, date_start, date_end, is_detractor=True):
    if not processes:
        return []
    proc_in = "'" + "','".join(escape_sq(p) for p in processes[:5]) + "'"
    role_filter = "n.DETRACTOR = 1" if is_detractor else "n.PROMOTER = 1"
    sql = f"""
    SELECT
      n.CAS_CASE_ID,
      n.PRO_PROCESS_NAME as processo,
      n.CDU,
      n.ANTIGUEDAD_REP as senioridade,
      SUBSTR(COALESCE(n.COMMENTS,''),1,200) as comentario,
      n.RES_DETRACTION_REASON as motivo,
      STRING_AGG(
        CASE WHEN t.SPEAKER_ROLE IN ('USER','REP')
          THEN '[' || t.SPEAKER_ROLE || '] ' || SUBSTR(COALESCE(t.OBFUSCATED_MESSAGE_CONTENT,''),1,250)
        END,
        ' || '
        ORDER BY t.INITIAL_DTTM
        LIMIT 8
      ) as transcript
    FROM `meli-bi-data.WHOWNER.DM_CX_NPS_Y20_DETAIL` n
    INNER JOIN `meli-bi-data.WHOWNER.BT_CX_TRANSCRIPT` t
      ON t.CAS_CASE_ID = n.CAS_CASE_ID
      AND DATE(t.INITIAL_DTTM) BETWEEN DATE('{date_start}') AND DATE('{date_end}')
    WHERE n.SIT_SITE_ID = 'MLB'
      AND n.SURVEY_CENTER = 'BR'
      AND n.SURVEY_DATE_SURVEY BETWEEN '{date_start}' AND '{date_end}'
      AND n.PRO_PROCESS_NAME IN ({proc_in})
      AND {role_filter}
      AND t.SPEAKER_ROLE IN ('USER','REP')
    GROUP BY 1,2,3,4,5,6
    ORDER BY RAND()
    LIMIT {MAX_TRANSCRIPTS}
    """
    return bq(sql, max_rows=MAX_TRANSCRIPTS + 5)

# ── CLAUDE PROMPT ─────────────────────────────────────────────────────────────
def build_prompt(driver, period_label, quant_m1, quant_m2, transcripts_det, transcripts_pro):
    def fmt_quant(rows, title):
        if not rows:
            return f"\n{title}: sem dados\n"
        txt = f"\n{title}:\n"
        # CDU breakdown
        cdus = {}
        for r in rows:
            c = r.get("CDU") or "(sem CDU)"
            if c not in cdus:
                cdus[c] = {"surveys": 0, "promoters": 0, "detractors": 0}
            cdus[c]["surveys"]    += int(r.get("surveys", 0) or 0)
            cdus[c]["promoters"]  += int(r.get("promoters", 0) or 0)
            cdus[c]["detractors"] += int(r.get("detractors", 0) or 0)
        txt += "  CDUs:\n"
        for c, d in sorted(cdus.items(), key=lambda x: -x[1]["surveys"])[:6]:
            if d["surveys"] > 0:
                n = round(100 * (d["promoters"] - d["detractors"]) / d["surveys"], 1)
                txt += f"    {c}: NPS {n} ({d['surveys']} pesquisas)\n"
        # Senioridade
        senior = {}
        for r in rows:
            s = r.get("senioridade") or "(sem info)"
            if s not in senior:
                senior[s] = {"surveys": 0, "promoters": 0, "detractors": 0}
            senior[s]["surveys"]    += int(r.get("surveys", 0) or 0)
            senior[s]["promoters"]  += int(r.get("promoters", 0) or 0)
            senior[s]["detractors"] += int(r.get("detractors", 0) or 0)
        if len(senior) > 1:
            txt += "  Senioridade:\n"
            for s, d in senior.items():
                if d["surveys"] > 0:
                    n = round(100 * (d["promoters"] - d["detractors"]) / d["surveys"], 1)
                    txt += f"    {s}: NPS {n} ({d['surveys']} pesquisas)\n"
        # Motivos de detraction/promotion
        motivos = {}
        for r in rows:
            for m in (r.get("motivos_det") or "").split(","):
                m = m.strip()
                if m:
                    motivos[m] = motivos.get(m, 0) + 1
        if motivos:
            txt += "  Motivos detratores:\n"
            for m, c in sorted(motivos.items(), key=lambda x: -x[1])[:5]:
                txt += f"    - {m} ({c}x)\n"
        return txt

    def fmt_transcripts(rows, titulo):
        if not rows:
            return f"\n{titulo}: sem transcricoes\n"
        txt = f"\n{titulo} (amostra de {len(rows)} casos):\n"
        for i, r in enumerate(rows[:8], 1):
            proc = r.get("processo", "")
            cdu  = r.get("CDU", "")
            sen  = r.get("senioridade", "")
            com  = r.get("comentario", "")
            tr   = r.get("transcript", "")
            txt += f"\n  Caso {i} | {proc} | CDU: {cdu} | Rep: {sen}\n"
            if com:
                txt += f"  Comentario: {com}\n"
            if tr:
                txt += f"  Trecho: {tr[:500]}\n"
        return txt

    return f"""Voce e um analista senior de Customer Experience (CX), NPS e Qualidade Operacional da MercadoLibre Brasil, com foco executivo e visao estrategica para lideranca.

Driver em analise: {driver}
Periodo: {period_label}

{fmt_quant(quant_m1, 'Periodo atual')}
{fmt_quant(quant_m2, 'Periodo anterior')}
{fmt_transcripts(transcripts_det, 'Transcricoes DETRATORES')}
{fmt_transcripts(transcripts_pro, 'Transcricoes PROMOTORES')}

Analise os dados acima e retorne EXCLUSIVAMENTE um JSON valido (sem markdown, sem texto fora do JSON) com a seguinte estrutura:

{{
  "resumo_executivo": "Paragrafo executivo (3-4 frases) com panorama do periodo, evolucao do NPS, principais movimentos e impacto para o negocio. Tom consultivo, orientado a decisao.",

  "top_detratores": [
    {{"causa": "...", "impacto": "...", "frequencia": "alta/media/baixa", "sugestao": "...", "prioridade": "Alta/Media/Baixa"}},
    {{"causa": "...", "impacto": "...", "frequencia": "...", "sugestao": "...", "prioridade": "..."}}
  ],

  "top_promotores": [
    {{"causa": "...", "impacto": "..."}},
    {{"causa": "...", "impacto": "..."}}
  ],

  "padroes_operacionais": "Falhas ou padroes identificados nas transcricoes: comportamento do atendente, gaps de comunicacao, padroes emocionais (frustracao, confianca, urgencia). Exemplos anonimizados.",

  "senioridade_insight": "Diferenca de performance Expert vs Newbie identificada. Mencionar processo/CDU especifico se relevante.",

  "sumario_diretoria": "Resumo de exatamente 5 linhas para diretoria. Cada linha separada por \\n. Foco em: resultado, causa, risco, oportunidade, proximos passos.",

  "conclusao_estrategica": "Uma conclusao estrategica de 2-3 frases indicando a posicao competitiva/operacional do driver e o que ela significa para os proximos 30-60 dias.",

  "acoes_30_dias": [
    {{"acao": "...", "prioridade": "Alta/Media/Baixa", "responsavel": "Operacao/Produto/Gestao"}},
    {{"acao": "...", "prioridade": "...", "responsavel": "..."}},
    {{"acao": "...", "prioridade": "...", "responsavel": "..."}}
  ],

  "alertas_criticos": ["Alerta 1 se existir", "Alerta 2 se existir"],

  "bullets_legado": "▶ Bullet 1\\n▶ Bullet 2\\n▶ Bullet 3\\n▶ Bullet 4\\n▶ Bullet 5"
}}

Regras obrigatorias:
- Cruze dados quantitativos (NPS/notas) com qualitativos (comentarios e transcricoes)
- Nao apenas descreva dados — interprete causas e consequencias
- Use linguagem executiva, objetiva e orientada para lideranca (tom McKinsey/Bain)
- Baseie cada afirmacao em evidencia dos dados apresentados
- Se nao houver dados suficientes para um campo, use string vazia ""
- bullets_legado deve manter o formato anterior com 5 bullets comecando com "▶"
- Retorne APENAS o JSON, sem texto adicional"""

def call_claude(prompt, max_tokens=2000):
    if CLAUDE_CLIENT is None:
        return None
    try:
        msg = CLAUDE_CLIENT.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = msg.content[0].text.strip()
        # Tentar parsear como JSON
        import json as _json
        try:
            return _json.loads(raw)
        except Exception:
            # Fallback: extrair JSON do texto se houver markdown
            import re as _re
            m = _re.search(r'\{.*\}', raw, _re.DOTALL)
            if m:
                try:
                    return _json.loads(m.group(0))
                except Exception:
                    pass
            # Fallback final: retornar como bullets_legado
            return {"bullets_legado": raw, "resumo_executivo": "", "top_detratores": [],
                    "top_promotores": [], "padroes_operacionais": "", "senioridade_insight": "",
                    "sumario_diretoria": "", "conclusao_estrategica": "",
                    "acoes_30_dias": [], "alertas_criticos": []}
    except Exception as e:
        return {"bullets_legado": f"(Erro Claude: {str(e)[:100]})", "resumo_executivo": "",
                "top_detratores": [], "top_promotores": [], "padroes_operacionais": "",
                "senioridade_insight": "", "sumario_diretoria": "", "conclusao_estrategica": "",
                "acoes_30_dias": [], "alertas_criticos": []}

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    summaries = {}
    drivers = sorted(DD_BREAKDOWN.keys())
    print(f"Gerando deep dives para {len(drivers)} drivers...")
    print(f"Periodos: M1={M1_START}/{M1_END}  M2={M2_START}/{M2_END}")
    print()

    for i, driver in enumerate(drivers, 1):
        print(f"[{i:02d}/{len(drivers)}] {driver}")
        processes = get_processes(driver)

        if not processes:
            print(f"  Sem processos com >= {MIN_SURVEYS_FOR_ANALYSIS} surveys, pulando.")
            summaries[driver] = {"mom": None, "wow": None, "skip": True}
            continue

        # ── MoM (Abril vs Marco) ──
        print(f"  Processos: {processes}")
        print(f"  Buscando dados quant M1...")
        q_m1 = quant_query(processes, M1_START, M1_END)
        print(f"  Buscando dados quant M2...")
        q_m2 = quant_query(processes, M2_START, M2_END)

        print(f"  Buscando transcricoes detratores M1...")
        worst, best = worst_best_process(driver)
        procs_focus = [worst["proc"]] if worst else processes[:2]
        t_det = transcript_query(procs_focus, M1_START, M1_END, is_detractor=True)
        print(f"  Buscando transcricoes promotores M1...")
        procs_best = [best["proc"]] if best else processes[:2]
        t_pro = transcript_query(procs_best, M1_START, M1_END, is_detractor=False)

        total_surveys = sum(int(r.get("surveys", 0) or 0) for r in q_m1)
        if total_surveys < MIN_SURVEYS_FOR_ANALYSIS:
            print(f"  Surveys insuficientes ({total_surveys}), pulando analise.")
            summaries[driver] = {"mom": None, "wow": None, "skip": True}
            continue

        print(f"  Gerando bullets MoM ({total_surveys} surveys, {len(t_det)} transcr det, {len(t_pro)} transcr pro)...")
        prompt_mom = build_prompt(driver, "Abril 2026 vs Marco 2026", q_m1, q_m2, t_det, t_pro)
        bullets_mom = call_claude(prompt_mom)
        print(f"  MoM OK")

        # ── WoW (S1 vs S2) ──
        print(f"  Buscando dados quant S1...")
        q_s1 = quant_query(processes, S1_START, S1_END)
        print(f"  Buscando dados quant S2...")
        q_s2 = quant_query(processes, S2_START, S2_END)

        print(f"  Buscando transcricoes detratores S1...")
        t_det_w = transcript_query(procs_focus, S1_START, S1_END, is_detractor=True)
        print(f"  Buscando transcricoes promotores S1...")
        t_pro_w = transcript_query(procs_best, S1_START, S1_END, is_detractor=False)

        total_surveys_w = sum(int(r.get("surveys", 0) or 0) for r in q_s1)
        if total_surveys_w >= MIN_SURVEYS_FOR_ANALYSIS:
            print(f"  Gerando bullets WoW ({total_surveys_w} surveys)...")
            prompt_wow = build_prompt(driver, "Semana 20-26/abr vs 13-19/abr", q_s1, q_s2, t_det_w, t_pro_w)
            bullets_wow = call_claude(prompt_wow)
            print(f"  WoW OK")
        else:
            bullets_wow = None
            print(f"  WoW: surveys insuficientes ({total_surveys_w})")

        summaries[driver] = {
            "mom": bullets_mom,
            "wow": bullets_wow,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        # Pausa pequena para nao saturar APIs
        time.sleep(1)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dd_summaries.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    ok = sum(1 for v in summaries.values() if v.get("mom"))
    print(f"\nSalvo: {out_path}")
    print(f"Drivers com resumo gerado: {ok}/{len(drivers)}")

if __name__ == "__main__":
    main()
