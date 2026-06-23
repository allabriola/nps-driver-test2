#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Categoriza transcrições rep↔Copilot por processo via análise de palavras-chave.
Input:  _copilot_transcripts_raw.json
Output: _copilot_categories.json
"""
import sys, json, re
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8')

MIN_TR_PER_PROC = 5

# ── Categorias e palavras-chave ──────────────────────────────────────────────
# Ordem importa: primeira categoria que fizer match ganha
CATEGORIAS = [
    {
        "nome": "Reputação / Métricas",
        "descricao": "Dúvidas sobre impacto na reputação, métricas, nível de lealdade e cancelamentos",
        "keywords": ["reputaci", "reputaç", "metrica", "métrica", "nivel de leal", "nivel lealt",
                     "cancelac", "cancelaç", "demora", "atraso", "thermômetro", "termometro",
                     "penalizac", "penalizaç", "afect", "afeta"]
    },
    {
        "nome": "Reclamo / Mediação",
        "descricao": "Gestão de reclamos abertos, mediações e disputas entre comprador e vendedor",
        "keywords": ["reclamo", "mediaci", "mediação", "disputa", "reclamac", "reclamaç",
                     "abrió recl", "abriu recl", "reclama"]
    },
    {
        "nome": "Devolução / Reversa",
        "descricao": "Devoluções de produtos, reversas logísticas e reembolsos",
        "keywords": ["devoluci", "devoluç", "reversa", "reembolso", "reintegr", "retorno",
                     "produto devolvid", "entregó devoluc", "entregou devoluç"]
    },
    {
        "nome": "Despacho / Entrega / Logística",
        "descricao": "Problemas com envio, rastreio, etiqueta e status de entrega",
        "keywords": ["despacho", "entrega", "envio", "etiqueta", "flete", "transportadora",
                     "viaje del paquete", "viagem do pacote", "rastreo", "rastreio",
                     "operador logis", "correo", "shipment", "logistic"]
    },
    {
        "nome": "Publicação / Anúncio",
        "descricao": "Dúvidas sobre criação, edição, pausas e configurações de publicações",
        "keywords": ["publicaci", "publicaç", "anuncio", "anúncio", "listing", "pausad",
                     "activ", "desactiv", "ativar", "desativar", "foto", "descripci",
                     "descrição", "categoria", "atribut", "variaci", "variaç"]
    },
    {
        "nome": "Pagamentos / Acreditação",
        "descricao": "Liberação de pagamentos, acreditação de valores e questões financeiras",
        "keywords": ["pago", "pagament", "acreditac", "acreditaç", "dinero", "dinheiro",
                     "liberaci", "liberaç", "cobro", "cobrança", "transferencia", "transferência",
                     "saldo", "retenc", "retençã"]
    },
    {
        "nome": "Conta / Acesso / Segurança",
        "descricao": "Problemas de acesso à conta, verificação de identidade e segurança",
        "keywords": ["cuenta", "conta", "acceso", "acesso", "contrase", "senha", "verific",
                     "identidad", "identidade", "bloquead", "bloqueaç", "suspend",
                     "factor", "autenticac", "autenticaç"]
    },
    {
        "nome": "Potenciar Vendas / Ferramentas",
        "descricao": "Uso de ferramentas para aumentar vendas, promoções e visibilidade",
        "keywords": ["potenciar", "potencializ", "venta", "venda", "promoci", "promoç",
                     "descuento", "desconto", "visibilidad", "visibilidade", "product",
                     "mercado ads", "publicidad"]
    },
    {
        "nome": "Regulamento / Política (PR)",
        "descricao": "Infrações de políticas, artigos proibidos, propriedade intelectual",
        "keywords": ["prohibid", "proibid", "politica", "política", "regulament",
                     "propiedad intelectual", "propriedade intelectual", "infrac",
                     "baja", "baixa", "sancion", "sanção", "denunci"]
    },
    {
        "nome": "Outras Dúvidas Operacionais",
        "descricao": "Consultas diversas sobre processos e procedimentos de atendimento",
        "keywords": []   # fallback
    },
]

def classify(text):
    t = text.lower()
    for cat in CATEGORIAS[:-1]:
        for kw in cat["keywords"]:
            if kw in t:
                return cat["nome"]
    return CATEGORIAS[-1]["nome"]

def extract_examples(texts, category_name, n=2):
    """Extrai frases curtas relevantes como exemplos."""
    examples = []
    for text in texts:
        # Pega frases que contêm keywords da categoria
        sentences = re.split(r'[.\n]', text.lower())
        for s in sentences:
            s = s.strip()
            if 20 < len(s) < 150:
                cat_match = next((c for c in CATEGORIAS if c["nome"] == category_name), None)
                if cat_match:
                    if any(kw in s for kw in cat_match["keywords"]) or not cat_match["keywords"]:
                        # Limpa placeholders e capitaliza
                        clean = re.sub(r'%\w+', '…', s)
                        clean = re.sub(r'\[.*?\]', '', clean).strip()
                        if len(clean) > 20:
                            examples.append(clean[:120])
                if len(examples) >= n:
                    break
        if len(examples) >= n:
            break
    return examples[:n]


# ── MAIN ─────────────────────────────────────────────────────────────────────
print("=== CX Copilot — Categorização de Consultas (análise local) ===\n")

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

    print(f"\n  [{proc}] {n} transcrições → classificando...")

    # Classifica cada transcrição
    counts = Counter()
    texts_by_cat = defaultdict(list)
    for t in items:
        txt = t.get("copilot_transcript", "")
        cat = classify(txt)
        counts[cat] += 1
        texts_by_cat[cat].append(txt)

    total = sum(counts.values())
    cats_out = []
    for cat_name, cnt in counts.most_common():
        pct = round(cnt / total * 100)
        if pct < 3:
            continue
        cat_def = next((c for c in CATEGORIAS if c["nome"] == cat_name), {})
        exemplos = extract_examples(texts_by_cat[cat_name], cat_name, n=2)
        cats_out.append({
            "nome": cat_name,
            "descricao": cat_def.get("descricao", ""),
            "pct_estimado": pct,
            "exemplos": exemplos
        })

    results[proc] = {"n_transcricoes": n, "categorias": cats_out}
    print(f"  → {len(cats_out)} categorias:")
    for c in cats_out:
        print(f"     • {c['nome']} ({c['pct_estimado']}%)")

with open("_copilot_categories.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n=== Categorização concluída! ({len(results)} processos) ===")
print("Próximo: python _build_copilot_dashboard.py")
