import re, shutil

with open('C:/claudinho/reputacion_longtail_abr_mai_2026.html', encoding='utf-8') as f:
    html = f.read()

changes = 0

# 1. Mecanismo no exec summary
old = '49% exclusão + 61% experiência &nbsp;·&nbsp; <strong>Rep ME</strong> = 19% exclusão + 89% experiência'
new = '49% exclusão + 51% experiência &nbsp;·&nbsp; <strong>Rep ME</strong> = 19% exclusão + 79% experiência'
if old in html: html = html.replace(old, new, 1); changes += 1

# 2. Insight Rep ME %
old = '89% do ganho vem do NPS melhorando dentro de cada grupo'
new = '79% do ganho vem do NPS melhorando dentro de cada grupo'
if old in html: html = html.replace(old, new, 1); changes += 1

# 3. Insight frase Reputación 61%->51%
old = '61% de experiência. O dado mais relevante'
new = '51% de experiência. O dado mais relevante'
if old in html: html = html.replace(old, new, 1); changes += 1

# 4. Gráfico chartDecomp — NETO values [3.0,4.6] -> [2.5,4.1]
old = 'data: [3.0, 4.6],'
new = 'data: [2.5, 4.1],'
if old in html: html = html.replace(old, new, 1); changes += 1

# 5. NETO total na tabela
old = '<td class="pos"><strong>+3,0pp</strong></td><td class="pos"><strong>+4,6pp</strong></td>'
new = '<td class="pos"><strong>+2,5pp</strong></td><td class="pos"><strong>+4,1pp</strong></td>'
if old in html: html = html.replace(old, new, 1); changes += 1

# 6. Não Excluímos Rep NETO: +2,7pp -> +2,1pp
old = '>+2,7pp ★</td><td class="pos">+0,4pp</td>'
new = '>+2,1pp ★</td><td class="pos">+0,4pp</td>'
if old in html: html = html.replace(old, new, 1); changes += 1

# 7. Outros Rep ME NETO: +0,8pp -> +0,4pp
old = '<td class="pos">+0,8pp</td><td class="pos">+0,4pp</td>'
new = '<td class="pos">+0,4pp</td><td class="pos">+0,4pp</td>'
if old in html: html = html.replace(old, new, 1); changes += 1

# 8. Não Afeta Rep ME NETO: -0,3pp -> -0,5pp
old = '<td class="neg">-0,3pp</td>'
new = '<td class="neg">-0,5pp</td>'
if old in html: html = html.replace(old, new, 1); changes += 1

# 9. Seção ① cards de decomposição — texto nota
old = 'Rep ME: Excluímos subiu 86%↑91% — NPS melhorou mesmo dentro dos casos já excluídos'
new = 'MIX + NETO* = +5,2pp exato ✓ (NETO* usa share de Maio)'
# Try plain text
old2 = 'Rep ME: Excluímos subiu 86%↑91% — NPS melhorou mesmo dentro dos casos já excluídos'
new2 = 'MIX + NETO* = +5,2pp exato ✓ (NETO* usa share de Maio)'
if old2 in html: html = html.replace(old2, new2, 1); changes += 1

# 10. Nota Reputacion card
old3 = 'Reputación: mix de grupos mudou (+3,3pp em Excluímos, −3,0pp em Não Excluímos)'
new3 = 'MIX + NETO* = +4,9pp exato ✓ (NETO* usa share de Maio)'
if old3 in html: html = html.replace(old3, new3, 1); changes += 1

# 11. Card notas com rep ME +4,6pp -> +4,1pp
old4 = '+4,6pp de +5,2pp'
new4 = '+4,1pp de +5,2pp'
if old4 in html: html = html.replace(old4, new4, 1); changes += 1

# 12. Subtitle NETO -> NETO* nas colunas da tabela
old5 = '<th>Rep NETO</th><th>Rep ME NETO</th>'
new5 = '<th>Rep NETO*</th><th>Rep ME NETO*</th>'
if old5 in html: html = html.replace(old5, new5, 1); changes += 1

# 13. Seção ① title da decomposição
old6 = 'Efeito Exclusão × Efeito Experiência (Abr → Mai)'
new6 = 'Efeito Exclusão (MIX) × Efeito Experiência (NETO*) — fórmula exata: MIX + NETO* = Δ Total'
if old6 in html: html = html.replace(old6, new6, 1); changes += 1

print(f'Changes: {changes}')

# Ajustar cards na seção de decomposição (NETO label)
html = html.replace('Efeito Experiência (NETO): +3,0pp</div>', 'Efeito Experiência (NETO*): +2,5pp</div>')
html = html.replace('Efeito Experiência (NETO): +4,6pp</div>', 'Efeito Experiência (NETO*): +4,1pp</div>')
html = html.replace('>+3,0pp</div>', '>+2,5pp</div>', 1)
html = html.replace('>+4,6pp</div>', '>+4,1pp</div>', 1)

# Find and fix the card values using regex
def fix_neto_card(html, old_neto, new_neto, old_pct, new_pct):
    return html.replace(f'>{old_neto}</div>', f'>{new_neto}</div>', 1).replace(
        f'Efeito Experiência (NETO) · {old_pct}%', f'Efeito Experiência (NETO*) · {new_pct}%', 1)

# Direct replacements for specific values
for old_v, new_v in [('+3,0pp','+2,5pp'), ('+4,6pp','+4,1pp')]:
    # Only in the card section (first 2 occurrences)
    count = html.count(old_v)
    html = html.replace(old_v, new_v)
    print(f'Replaced {old_v} -> {new_v}: {count} times')

for old_p, new_p in [('(NETO) · 61%','(NETO*) · 51%'), ('(NETO) · 89%','(NETO*) · 79%')]:
    html = html.replace(old_p, new_p)

with open('C:/claudinho/reputacion_longtail_abr_mai_2026.html', 'w', encoding='utf-8') as f:
    f.write(html)
shutil.copy('C:/claudinho/reputacion_longtail_abr_mai_2026.html',
            'C:/claudinho/reputacion_lt_v2.html')
print(f'Salvo: {len(html)} chars')
