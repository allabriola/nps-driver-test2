#!/usr/bin/env python3
import json, re

with open('generate_html_gerencia.py', 'r', encoding='utf-8') as f:
    src = f.read()
stop = re.search(r'# SECTION 3', src)
ns = {}
exec(compile(src[:stop.start()], 'g', 'exec'), ns)
mh = ns['monthly_history']
dt = ns['DRIVER_TARGETS']
nt = ns['NPS_TARGET']
ml = ns['MONTH_LABELS']

with open('_monthly_result.json', encoding='utf-8') as f:
    mr = json.load(f)
for lbl, dm in mr.items():
    for drv, vals in dm.items():
        if drv not in mh: mh[drv] = {}
        mh[drv][lbl] = tuple(vals)

with open('_exec_data.json', encoding='utf-8') as f:
    ed = json.load(f)
qual = ed.get('qual', {})

GROUPS = {
    'Exp. Impositiva':  ['Experiencia Impositiva Seller Dev'],
    'ME Vendedor':      ['ME Vendedor Seller Dev'],
    'PCF Vendedor':     ['PCF Vendedor Seller Dev'],
    'Post Venta':       ['Post Venta Seller Dev'],
    'Publicaciones':    ['Publicaciones Seller Dev'],
    'Partners':         ['Partners'],
}
ALL_D = [d for drvs in GROUPS.values() for d in drvs]
lC = ml[-1]; lP = ml[-2]

def nps(p,d,s): return round(100*(p-d)/s,2) if s>0 else None
def fn(v): return (f'{v:.1f}').replace('.',',') if v is not None else u'—'

def cons(lbl):
    p=sum(mh[d].get(lbl,(0,0,0))[0] for d in ALL_D)
    det=sum(mh[d].get(lbl,(0,0,0))[1] for d in ALL_D)
    s=sum(mh[d].get(lbl,(0,0,0))[2] for d in ALL_D)
    return nps(p,det,s), s

nc_cons, sc_cons = cons(lC)
np_cons, sp_cons = cons(lP)
delta_cons = round(nc_cons - np_cons, 2)

sA_tot = sum(mh[d].get(lP,(0,0,0))[2] for d in ALL_D)
sB_tot = sum(mh[d].get(lC,(0,0,0))[2] for d in ALL_D)

rows = {}
for g, drvs in GROUPS.items():
    pA=sum(mh[d].get(lP,(0,0,0))[0] for d in drvs if d in mh)
    dA=sum(mh[d].get(lP,(0,0,0))[1] for d in drvs if d in mh)
    sA=sum(mh[d].get(lP,(0,0,0))[2] for d in drvs if d in mh)
    pB=sum(mh[d].get(lC,(0,0,0))[0] for d in drvs if d in mh)
    dB=sum(mh[d].get(lC,(0,0,0))[1] for d in drvs if d in mh)
    sB=sum(mh[d].get(lC,(0,0,0))[2] for d in drvs if d in mh)
    na=nps(pA,dA,sA) or 0; nb=nps(pB,dB,sB) or 0
    sha=sA/sA_tot if sA_tot else 0; shb=sB/sB_tot if sB_tot else 0
    var=round(sha*(nb-na)+(shb-sha)*(nb-(nc_cons or 0)),2)
    tgt_num=sum(mh[d].get(lC,(0,0,0))[2]*dt.get(d,nt) for d in drvs if d in mh)
    tgt_v=round(tgt_num/sB,2) if sB else nt
    rows[g]={'nc':nb,'np':na,'sc':sB,'var':var,'tgt':tgt_v,'gap':round(nb-tgt_v,2),'delta':round(nb-na,2)}

sorted_rows = sorted(rows.items(), key=lambda x: x[1]['var'])
top_neg = [g for g,v in sorted_rows if v['var'] < 0]
top_pos = [g for g,v in sorted_rows if v['var'] >= 0]

sign = '+' if delta_cons >= 0 else ''
neg_str = ' e '.join(top_neg[:2]) if top_neg else 'sem quedas'
pos_str = ' e '.join(top_pos[-2:]) if top_pos else 'estavel'

def narr(g, r):
    texts = {
        'Exp. Impositiva': (
            u'\U0001f534 <strong>Exp. Impositiva</strong>'
            u' (impacto {var:+.2f}pp, NPS {nc}% vs {np}% ant, {sc:,} enc)'
            u' — Queda de {delta:+.1f}pp WTD com gap crítico de {gap:+.1f}pp vs target ({tgt}%).'
            u' Dois problemas estruturais distintos: <em>(1) CDU "Dudas sobre cargos facturados" (7 detratores)</em>'
            u' — sellers relatam cobranças não autorizadas sem resolução no 1º atendimento,'
            u' com múltiplas transferências; <em>(2) Faturador MeLi (6 detratores)</em>'
            u' — bloqueio para emissão de NF-e por certificado digital expirado ou CNPJ restrito,'
            u' travando operação Full. Comentário recorrente:'
            u' <em>“repassam de atendente em atendente e não dão solução.”</em>'
            u' Driver estruturalmente abaixo do target — exige intervenção de produto, não de CX.'
        ),
        'Publicaciones': (
            u'\U0001f534 <strong>Publicaciones</strong>'
            u' (impacto {var:+.2f}pp, NPS {nc}% vs {np}% ant, {sc:,} enc)'
            u' — Queda de {delta:+.1f}pp MoM.'
            u' CDU dominante entre detratores: <em>Métricas y Comisiones (4)</em> com padrão de'
            u' atendimento que não resolve na 1ª interação — sellers relatam'
            u' “chamado em andamento” sem retorno efetivo.'
            u' CDU Activar/desactivar (2) e Configuração (2) surgem como novos vetores.'
            u' Apesar de {gap:+.1f}pp acima do target, a trajetória de queda em 3 dos últimos 4 meses'
            u' requer atenção antes que cruze o target.'
        ),
        'Partners': (
            u'\U0001f7e1 <strong>Partners</strong>'
            u' (impacto {var:+.2f}pp, NPS {nc}% vs {np}% ant, {sc:,} enc)'
            u' — Gap de {gap:+.1f}pp vs target ({tgt}%).'
            u' CDU dominante: inativação de conta (3 det) — sellers sem retorno sobre o motivo.'
            u' <em>Nivel de Lealtad</em> surge como fonte de frustração:'
            u' <em>“rebaixado de nível mesmo atendendo todos os requisitos.”</em>'
            u' 71 de 80 comentários são promotores — o problema é de produto/regra, não de qualidade de CX.'
        ),
        'PCF Vendedor': (
            u'\U0001f7e2 <strong>PCF Vendedor</strong>'
            u' (impacto {var:+.2f}pp, NPS {nc}% vs {np}% ant, {sc:,} enc)'
            u' — Estável, {gap:+.1f}pp acima do target.'
            u' CDUs de detratores: Mediação aberta (3), Antes del reclamo (2), Mediação fechada (2).'
            u' Atrito com bot identificado nos comentários:'
            u' <em>“atendimento gerado por IA é péssimo, não consegue resolver nada.”</em>'
            u' Triagem humana para mediações poderia elevar o NPS com ajuste pontual de fluxo.'
        ),
        'ME Vendedor': (
            u'\U0001f7e2 <strong>ME Vendedor</strong>'
            u' (impacto {var:+.2f}pp, NPS {nc}% vs {np}% ant, {sc:,} enc)'
            u' — Driver de maior volume do segmento, estável e {gap:+.1f}pp acima do target.'
            u' 75% dos detratores (12/16) têm CDU <em>“estado do envio”</em>'
            u' — causa logística estrutural, não de qualidade de atendimento.'
            u' Comentário típico: <em>“não vem entregando no prazo — o atendente é avaliado pelo problema da plataforma.”</em>'
            u' Tendência positiva consolidada no segmento.'
        ),
        'Post Venta': (
            u'\U0001f7e2 <strong>Post Venta</strong>'
            u' (impacto {var:+.2f}pp, NPS {nc}% vs {np}% ant, {sc:,} enc)'
            u' — Maior alta do segmento: {delta:+.1f}pp MoM, {gap:+.1f}pp acima do target.'
            u' 73 de 80 comentários são promotores.'
            u' Detratores concentrados em Reclamos (3) e Reputação (2)'
            u' — sellers discordam da <em>decisão da plataforma</em>, não do atendimento.'
            u' Modelo consultivo e individualizado é referência: deve ser replicado em outros drivers.'
        ),
    }
    tmpl = texts.get(g, u'{g}: NPS {nc}% var {var:+.2f}pp')
    return tmpl.format(
        g=g, var=r['var'], nc=fn(r['nc']), np=fn(r['np']),
        sc=r['sc'], delta=r['delta'], gap=r['gap'], tgt=fn(r['tgt'])
    )

lines = []
lines.append(
    u'<div style="border-left:4px solid #F39C12;padding-left:14px;margin-bottom:20px">\n'
    u'  <div style="font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">Highlights &amp; Análise</div>\n'
    u'  <p style="font-size:15px;font-weight:700;color:#222;margin-bottom:16px">\n'
    u'    ' + sign + fn(delta_cons) + u'pp | ' + pos_str + u' sustentam o consolidado — alerta crítico em Exp. Impositiva e queda acumulada em Publicaciones\n'
    u'  </p>\n'
    u'  <p style="font-size:13px;font-weight:700;color:#333;margin-bottom:10px">Causas identificadas:</p>'
)

for g, r in sorted_rows:
    lines.append(
        u'  <p style="font-size:13px;line-height:1.8;margin-bottom:10px">\n'
        u'    ' + narr(g, r) + u'\n'
        u'  </p>'
    )

lines.append(
    u'  <p style="font-size:13px;font-weight:700;color:#333;margin-bottom:10px">Next steps:</p>\n'
    u'  <p style="font-size:13px;line-height:1.9;color:#444">\n'
    u'    Escalar a Produto o fluxo de cobranças automáticas em <strong>Exp. Impositiva</strong>'
    u' — documentar cases de “Dudas sobre cargos facturados” e Faturador MeLi bloqueado;'
    u' o atendimento de 1º nível não tem autonomia para resolver nenhum dos dois problemas.<br><br>\n'
    u'    Implementar triagem especializada para <strong>Métricas/Comissões em Publicaciones</strong>'
    u' — chatbot não resolve; escalonamento direto para especialista reduziria transferências'
    u' e interromperia a queda estrutural.<br><br>\n'
    u'    Comunicar proativamente as regras de <strong>Nivel de Lealtad para base Partners</strong>'
    u' — sellers rebaixados sem compreender o critério é causa direta de detração com solução de baixo custo.<br><br>\n'
    u'    Revisar fluxo de <strong>Mediação em PCF Vendedor</strong>'
    u' — substituir bot por triagem humana nas CDUs de Mediação aberta/fechada; impacto direto identificado em comentários.<br><br>\n'
    u'    Expandir o modelo consultivo de <strong>Post Venta</strong> como protocolo replicável'
    u' — análise individualizada de Reclamos e Reputação como referência para Publicaciones e PCF Vendedor.\n'
    u'  </p>\n'
    u'</div>'
)

html = u'\n'.join(lines)
with open('_exec_summary_sd.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Salvo _exec_summary_sd.html', len(html), 'chars')
for g, r in sorted_rows:
    print(f'  {g:<20} {fn(r["np"])}% -> {fn(r["nc"])}% var={r["var"]:+.2f}pp gap={r["gap"]:+.1f}pp sc={r["sc"]}')
