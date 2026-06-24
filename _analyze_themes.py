"""
Agrupa mensagens USER por CDU em temas recorrentes usando TF-IDF + KMeans.
Seleciona 3 case_ids representativos por tema (mais próximos do centroide).
"""
import json, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# ── Carrega dados ─────────────────────────────────────────────────────────────
with open('_lt_tr_wide.json', encoding='utf-8') as f:
    transcripts = json.load(f)  # [{case_id, msg, SPEAKER_ROLE}]

with open('_lt_cases_wide.json', encoding='utf-8') as f:
    cases = json.load(f)        # [{CDU, case_id}]

case_to_cdu = {r['case_id']: r['CDU'] for r in cases}

# Agrupa todas as msgs USER por case_id (concatena)
case_msgs = defaultdict(list)
for t in transcripts:
    cid = t.get('case_id','')
    msg = (t.get('msg') or '').strip()
    if len(msg) > 20:
        case_msgs[cid].append(msg)

# Monta doc por case_id = todas as msgs USER concatenadas
docs_by_cdu = defaultdict(list)  # CDU -> [(case_id, texto_completo)]
for cid, msgs in case_msgs.items():
    cdu = case_to_cdu.get(cid)
    if not cdu: continue
    texto = ' '.join(msgs)
    if len(texto) > 40:
        docs_by_cdu[cdu].append((cid, texto))

# ── Stopwords BR ──────────────────────────────────────────────────────────────
SW = set("""
de da do que em para com um uma os as o a e é se não por mais ele ela nao na
no ao dos das me você oi ola sim bom dia boa tarde noite obrigado obrigada ok
isso este esta esse essa meu minha seu sua foi ser ter estou esta tenho preciso
posso pode como quando onde qual aqui ja mas ou ate sobre mesmo tambem agora
ainda depois antes entao porque pelo pela mercado livre meli vendedor seller
entregador motorista representante atendimento boa tarde noite bom dia num date
hour url silence seconds email percent numero silencio gostaria precisava queria
null true false poderia adoraria queremos ficou ficaria nosso nossa eles elas
sim nao eh eh pois vai vem vou temos voce vc pro pra entre dentro desde
""".split())

def clean(text):
    t = re.sub(r'%\w+', ' ', text.lower())
    t = re.sub(r'[^\w\s]', ' ', t)
    tokens = [w for w in t.split() if len(w) > 3 and w not in SW]
    return ' '.join(tokens)

# ── Análise por CDU ───────────────────────────────────────────────────────────
CDU_LABELS = {
    'Tiene un inconviente con sus metricas de Nivel de Lealtad': 'Métricas / Nível Lealtad',
    'Quiere reclamar por inconvenientes en el recorrido o en el service center': 'Inconvenientes / SC',
    'Tiene problemas durante la creacion de la cuenta': 'Criação de Conta',
    'Quiere saber porque no le pagaron una ruta': 'Rota Não Paga',
}

N_THEMES = 3  # temas por CDU

results = {}

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import normalize
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print('sklearn não disponível — usando análise por keywords')

for cdu, docs in docs_by_cdu.items():
    label = CDU_LABELS.get(cdu, cdu[:40])
    print(f'\n{"="*70}')
    print(f'CDU: {label} ({len(docs)} casos)')
    print('='*70)

    if len(docs) < 6:
        print('  Poucos casos para análise temática.')
        continue

    case_ids = [d[0] for d in docs]
    textos   = [clean(d[1]) for d in docs]
    raw_txts = [d[1] for d in docs]

    if HAS_SKLEARN:
        k = min(N_THEMES, len(docs) // 3)
        vec = TfidfVectorizer(max_features=200, min_df=2, max_df=0.85, ngram_range=(1,2))
        try:
            X = vec.fit_transform(textos)
        except ValueError:
            print('  TF-IDF falhou (vocabulário vazio).')
            continue

        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X)
        labels = km.labels_

        # Nomes dos clusters: top 4 termos do centroide
        terms = vec.get_feature_names_out()
        theme_data = {}
        for ci in range(k):
            order = km.cluster_centers_[ci].argsort()[::-1][:6]
            top_terms = [terms[i] for i in order if terms[i] not in SW][:4]
            name = ' · '.join(top_terms)

            # Casos nesse cluster
            cluster_cases = [(case_ids[i], raw_txts[i]) for i in range(len(labels)) if labels[i] == ci]

            # 3 cases mais próximos do centroide
            if len(cluster_cases) >= 3:
                Xc = normalize(vec.transform([clean(c[1]) for c in cluster_cases]))
                center = normalize(km.cluster_centers_[ci].reshape(1,-1))
                prod = Xc @ center.T
                dists = (prod.toarray() if hasattr(prod,'toarray') else prod).flatten()
                top3_idx = dists.argsort()[::-1][:3]
                rep_cases = [cluster_cases[i] for i in top3_idx]
            else:
                rep_cases = cluster_cases[:3]

            theme_data[ci] = {
                'name': name,
                'count': len(cluster_cases),
                'pct': round(len(cluster_cases)/len(docs)*100),
                'cases': [(c[0], c[1][:250]) for c in rep_cases],
            }

            print(f'\n  Tema {ci+1}: [{theme_data[ci]["count"]} casos | {theme_data[ci]["pct"]}%] "{name}"')
            for j, (cid, txt) in enumerate(rep_cases):
                preview = txt[:180].replace('\n',' ')
                print(f'    Case {cid}: "{preview}..."')

        results[cdu] = {'label': label, 'n': len(docs), 'themes': theme_data}

    else:
        # Fallback: análise por keywords manuais
        pass

# Salva resultado
with open('_lt_themes.json', 'w', encoding='utf-8') as f:
    # Serializa themes com case IDs
    out = {}
    for cdu, val in results.items():
        themes_list = []
        for ti, td in val['themes'].items():
            themes_list.append({
                'name': td['name'],
                'count': td['count'],
                'pct': td['pct'],
                'cases': [{'id': c[0], 'preview': c[1][:200]} for c in td['cases']],
            })
        out[cdu] = {'label': val['label'], 'n': val['n'], 'themes': themes_list}
    json.dump(out, f, ensure_ascii=False, indent=2)

print('\n\nSalvo em _lt_themes.json')
