#!/usr/bin/env python3
"""Replaces _recurrence_deep in both dashboard scripts to use pre-built categories."""

NEW_FUNC = r'''def _recurrence_deep(grp, trx_source=None, top_proc=None):
    """
    Usa categorias pré-construídas de _recurrence_cases.json (dados reais BQ).
    Retorna lista de dicts: {sub_pattern, s1_count, monthly_count, narrative, examples}
    """
    rc = _RC.get(grp, {})
    if not rc:
        return []

    # Prefere categorias mensais; fallback para semanais
    cats = rc.get("categories_mon") or rc.get("categories_wk") or []
    if not cats:
        return []

    # Garante compatibilidade com o formato esperado pelo renderizador
    result = []
    for c in cats[:4]:
        result.append({
            "categoria":     c.get("sub_pattern", ""),
            "sub_pattern":   c.get("sub_pattern", ""),
            "s1_count":      c.get("s1_count", 0),
            "monthly_count": c.get("monthly_count", c.get("s1_count", 0)),
            "examples":      c.get("examples", [])[:3],
            "narrative":     c.get("narrative", ""),
        })
    return result

'''

def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    start = content.find('def _recurrence_deep(grp')
    if start > 0 and content[start-1] == '\n':
        start -= 1

    end = content.find('\ndef _deep_trx_insights', start)
    if end == -1:
        end = content.find('\ndef _deep_trx', start)
    if end == -1:
        print(f"ERROR: end marker not found in {path}")
        return False

    new_content = content[:start] + '\n' + NEW_FUNC + '\n' + content[end+1:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Patched: {path}")
    return True

patch_file('generate_html_tendencias.py')
patch_file('generate_html_seller_dev.py')
print("Done.")
