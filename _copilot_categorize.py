#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Categoriza transcrições rep↔Copilot por processo usando Claude API.
Input:  _copilot_transcripts_raw.json
Output: _copilot_categories.json
"""
import sys, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
import anthropic

client = anthropic.Anthropic()

SAMPLE_PER_PROC  = 50   # máx transcrições enviadas ao Claude por processo
MAX_TR_CHARS     = 800  # máx chars por transcrição (evita tokens excessivos)
MIN_TR_PER_PROC  = 5    # processos com menos transcrições são ignorados


def categorize_process(processo, transcripts):
    sample = transcripts[:SAMPLE_PER_PROC]
    bloco = "\n\n---\n\n".join([
        f"[CONVERSA {i+1}]\n{t['copilot_transcript'][:MAX_TR_CHARS]}"
        for i, t in enumerate(sample)
    ])

    prompt = f"""Você analisará transcrições de conversas entre representantes de atendimento (reps) \
e o assistente de IA Copilot, no processo: "{processo}".

OBJETIVO: Identificar as principais CATEGORIAS DE CONSULTAS que os reps fazem ao Copilot \
para orientar reforços de treinamento em sala.

TRANSCRIÇÕES:
{bloco}

INSTRUÇÕES:
- Identifique entre 4 e 7 categorias distintas de consultas dos reps
- Seja específico e orientado à ação (ex: "Como emitir NF de devolução", não "Documentos")
- Para cada categoria extraia 2 exemplos reais de frases/perguntas do rep
- pct_estimado deve somar ~100 entre todas as categorias
- Retorne SOMENTE JSON válido, sem texto fora do JSON:

{{
  "categorias": [
    {{
      "nome": "Nome curto da categoria",
      "descricao": "Uma linha explicando o tipo de consulta",
      "pct_estimado": 25,
      "exemplos": ["frase exata rep 1", "frase exata rep 2"]
    }}
  ]
}}"""

    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1800,
            messages=[{"role": "user", "content": prompt}]
        )
        text = msg.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.lower().startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"    ! Erro: {e}")
        return {"categorias": []}


# ── MAIN ──────────────────────────────────────────────────────────────
print("=== CX Copilot — Categorização de Consultas ===\n")

try:
    with open("_copilot_transcripts_raw.json", encoding="utf-8") as f:
        all_tr = json.load(f)
except FileNotFoundError:
    print("! _copilot_transcripts_raw.json não encontrado — nada para categorizar.")
    sys.exit(0)

# Agrupa por processo
by_proc = defaultdict(list)
for t in all_tr:
    proc = (t.get("processo") or "Outros").strip()
    if proc:
        by_proc[proc].append(t)

print(f"Processos com transcrições: {len(by_proc)}")
for proc, items in sorted(by_proc.items(), key=lambda x: -len(x[1])):
    print(f"  {proc}: {len(items)}")

results = {}
procs_sorted = sorted(by_proc.items(), key=lambda x: -len(x[1]))

for proc, items in procs_sorted:
    n = len(items)
    if n < MIN_TR_PER_PROC:
        print(f"\n  Pulando '{proc}' ({n} transcrições — mínimo {MIN_TR_PER_PROC})")
        continue

    print(f"\n  [{proc}] {n} transcrições → categorizando...")
    result = categorize_process(proc, items)
    cats = result.get("categorias", [])

    results[proc] = {
        "n_transcricoes": n,
        "categorias": cats
    }

    print(f"  → {len(cats)} categorias:")
    for c in cats:
        print(f"     • {c.get('nome','?')} ({c.get('pct_estimado',0)}%)")

with open("_copilot_categories.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n=== Categorização concluída! ({len(results)} processos) ===")
print("Próximo: python _build_copilot_dashboard.py")
