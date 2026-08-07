#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csat_diagnostic.py — Gera diagnóstico por processo via Claude API

Lê:  _csat_data.json   (diagnóstico raw: comentários + transcrições)
Salva: _csat_diagnostic.json

Para cada (equipe × processo × período) com ≥ 5 detratores com texto:
  → Chama claude-sonnet-4-6 e gera 1-2 frases em português (Modo A)
Para < 5 detratores com texto:
  → Retorna mensagem padrão Modo B

Custo estimado: ~0,01 USD/execução (poucos processos por equipe)
"""
import json, os, re, sys, time
from datetime import date
sys.stdout.reconfigure(encoding='utf-8')

import anthropic

# ── Config ─────────────────────────────────────────────────────────────────────
CLAUDE_MODEL   = "claude-haiku-4-5-20251001"   # rápido e eficiente para sumarização
MIN_CASES_MODO_A = 5   # mínimo de detratores com texto para Modo A
MAX_CHARS_CTX    = 3000  # limite de chars de contexto por chamada

# ── Carrega dados ──────────────────────────────────────────────────────────────
print("Carregando _csat_data.json…")
with open("_csat_data.json", encoding="utf-8") as f:
    csat_data = json.load(f)

month_cur     = csat_data.get("month_cur", "")
week_label    = csat_data.get("week_label", "")
month_cur_lbl = csat_data.get("month_cur_label", "")
diag_raw      = csat_data.get("diagnostic_raw", {})

# ── Claude client ──────────────────────────────────────────────────────────────
ai = anthropic.Anthropic()   # usa ANTHROPIC_API_KEY do ambiente

# Aproveita cache reutilizando o mesmo system prompt
SYSTEM_PROMPT = """Você é um analista de qualidade de atendimento ao cliente da Mercado Livre.
Analise os comentários e transcrições de chats de detratores de CSAT (nota 1, 2 ou 3) e identifique o tema dominante de insatisfação.

Regras:
- Responda em português (BR), máximo 2 frases curtas.
- Formato: "X% dos casos mencionam [tema]. [Detalhe específico observado]."
- Seja específico: não use termos genéricos como "atendimento ruim".
- Se não houver padrão claro, diga: "Casos variados sem tema dominante (n=X)."
- Não invente dados. Use apenas o que está nos textos fornecidos."""

def build_prompt(team: str, process: str, period_label: str,
                 cases: list[dict]) -> str:
    """Monta prompt com até MAX_CHARS_CTX caracteres de contexto."""
    n = len(cases)
    linhas = []
    chars = 0
    for i, c in enumerate(cases, 1):
        txt = c.get("comentario", "").strip()
        tr  = c.get("transcricao", "").strip()
        nota = c.get("score", "?")
        partes = []
        if txt:
            partes.append(f"Comentário: {txt}")
        if tr:
            partes.append(f"Transcrição: {tr[:400]}")
        if partes:
            linha = f"Caso {i} (nota {nota}): {' | '.join(partes)}"
            if chars + len(linha) > MAX_CHARS_CTX:
                break
            linhas.append(linha)
            chars += len(linha)

    contexto = "\n".join(linhas)
    return (f"Equipe: {team}\nProcesso: {process}\nPeríodo: {period_label}\n"
            f"Total de detratores analisados: {n}\n\n"
            f"Textos:\n{contexto}\n\n"
            f"Qual é o tema dominante de insatisfação neste processo?")

def generate_diag(team: str, process: str, period_label: str,
                  cases: list[dict]) -> str:
    """Chama Claude API e retorna texto diagnóstico."""
    prompt = build_prompt(team, process, period_label, cases)
    try:
        resp = ai.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=150,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()
    except Exception as e:
        print(f"      ! API error ({team}/{process}): {e}")
        return f"Erro ao gerar diagnóstico: {e}"

def modo_b(n: int) -> str:
    return f"Sem evidência suficiente no período selecionado para narrativa (n={n})."

# ── Processa diagnósticos ──────────────────────────────────────────────────────
def process_period(diag_period: dict, period_label: str) -> dict:
    """
    diag_period: {team: {process: [cases]}}
    Retorna: {team: {process: "texto diagnóstico"}}
    """
    result = {}
    total_calls = 0

    for team, procs in sorted(diag_period.items()):
        result[team] = {}
        for proc, cases in sorted(procs.items()):
            # Conta casos com texto útil
            cases_with_text = [
                c for c in cases
                if len((c.get("comentario") or "").strip()) > 5
                or len((c.get("transcricao") or "").strip()) > 10
            ]
            n = len(cases_with_text)
            print(f"   {team[:25]:25s} | {proc[:35]:35s} | n={n:3d}", end="")

            if n >= MIN_CASES_MODO_A:
                print(" → Modo A (Claude API)…", end=" ", flush=True)
                diag_text = generate_diag(team, proc, period_label, cases_with_text)
                total_calls += 1
                # Rate limit: 1 req/s para evitar throttle
                time.sleep(1.1)
            else:
                diag_text = modo_b(n)
                print(" → Modo B")

            result[team][proc] = diag_text
            print()  # newline se Modo A

    print(f"   Total chamadas API: {total_calls}")
    return result

print(f"\n=== Diagnóstico MENSAL ({month_cur_lbl}) ===")
diag_monthly_result = process_period(
    diag_raw.get("monthly", {}),
    month_cur_lbl
)

print(f"\n=== Diagnóstico SEMANAL ({week_label}) ===")
diag_weekly_result = process_period(
    diag_raw.get("weekly", {}),
    f"semana {week_label}"
)

# ── Salva resultado ────────────────────────────────────────────────────────────
output = {
    "generated_at": date.today().isoformat(),
    "month_cur":    month_cur,
    "week_label":   week_label,
    "monthly":      diag_monthly_result,
    "weekly":       diag_weekly_result,
}

OUT = "_csat_diagnostic.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ Salvo: {OUT}")
