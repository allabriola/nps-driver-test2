#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera copiloto_usabilidade.html — dashboard de usabilidade do CX Copilot.
Input:  _copilot_reps.json, _copilot_by_process.json, _copilot_categories.json
Output: copiloto_usabilidade.html
"""
import sys, json, math
from collections import defaultdict
from datetime import date
sys.stdout.reconfigure(encoding='utf-8')

OUT_FILE  = "copiloto_usabilidade.html"
DAYS_BACK = 30
LOW_ADOPT = 30.0   # limiar adoção baixa (%)
MIN_NPS   = 3      # n_nps mínimo para considerar no Q4
MIN_QM    = 1      # n_qm mínimo

# ══════════════════════════════════════════════════════════════════════
# CARREGA DADOS
# ══════════════════════════════════════════════════════════════════════
print("Carregando JSONs...")
def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  ! {path} não encontrado — usando dados vazios")
        return default

REPS    = load_json("_copilot_reps.json",       [])
BY_PROC = load_json("_copilot_by_process.json", [])
CATS    = load_json("_copilot_categories.json", {})

# Converte campos numéricos que possam ter vindo como string do BQ
NUM_FIELDS = ["pct_adopcion","outgoing_total","outgoing_copilot","dias_uso",
              "tmo_com_copilot","tmo_sem_copilot","nps_copilot","n_nps","estilo_meli","n_qm"]
for r in REPS:
    for f in NUM_FIELDS:
        v = r.get(f)
        if v is None or v == "None": r[f] = None; continue
        try: r[f] = float(v)
        except (ValueError, TypeError): r[f] = None
PROC_NUM = ["outgoing_total","outgoing_copilot","pct_adopcion"]
for r in BY_PROC:
    for f in PROC_NUM:
        v = r.get(f)
        if v is None or v == "None": r[f] = 0; continue
        try: r[f] = float(v)
        except (ValueError, TypeError): r[f] = 0

print(f"  {len(REPS)} reps | {len(BY_PROC)} linhas proc | {len(CATS)} processos categorizados")

# ══════════════════════════════════════════════════════════════════════
# CÁLCULO Q4
# ══════════════════════════════════════════════════════════════════════
def percentile(vals, p):
    if not vals: return None
    s = sorted(v for v in vals if v is not None)
    if not s: return None
    idx = (len(s) - 1) * p / 100
    lo, hi = int(idx), min(int(idx) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (idx - lo)

nps_vals   = [r["nps_copilot"]   for r in REPS if r.get("nps_copilot")   is not None and r.get("n_nps", 0)  >= MIN_NPS]
tmo_vals   = [r["tmo_com_copilot"] for r in REPS if r.get("tmo_com_copilot") is not None]
estilo_vals= [r["estilo_meli"]   for r in REPS if r.get("estilo_meli")   is not None and r.get("n_qm", 0)   >= MIN_QM]

q4_nps    = percentile(nps_vals,    25)   # abaixo = Q4
q4_tmo    = percentile(tmo_vals,    75)   # acima  = Q4
q4_estilo = percentile(estilo_vals, 25)   # abaixo = Q4

print(f"  Limiares Q4 → NPS < {q4_nps} | TMO > {q4_tmo} | Estilo < {q4_estilo}")

for r in REPS:
    r["q4_nps"]    = (r.get("nps_copilot")     is not None and r.get("n_nps",  0) >= MIN_NPS  and q4_nps    is not None and r["nps_copilot"]     <= q4_nps)
    r["q4_tmo"]    = (r.get("tmo_com_copilot") is not None and q4_tmo    is not None and r["tmo_com_copilot"]   >= q4_tmo)
    r["q4_estilo"] = (r.get("estilo_meli")     is not None and r.get("n_qm",   0) >= MIN_QM  and q4_estilo  is not None and r["estilo_meli"]     <= q4_estilo)
    r["n_q4"]      = sum([r["q4_nps"], r["q4_tmo"], r["q4_estilo"]])
    r["low_adopt"] = r.get("pct_adopcion", 0) < LOW_ADOPT
    r["critico"]   = r["low_adopt"] and r["n_q4"] >= 1

# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════
def fmt(v, dec=1, suffix=""):
    if v is None: return "—"
    return f"{v:.{dec}f}{suffix}"

def color_adopt(v):
    if v is None: return ""
    if v >= 60: return "gc"
    if v >= 30: return "yc"
    return "rc"

def color_nps(v, is_q4):
    if v is None: return ""
    return "rc" if is_q4 else ("gc" if v >= 70 else "")

def color_tmo(v, is_q4):
    if v is None: return ""
    return "rc" if is_q4 else ("gc" if v < 300 else "")

def color_estilo(v, is_q4):
    if v is None: return ""
    return "rc" if is_q4 else ("gc" if v >= 80 else "")

def badge_q4(rep):
    badges = []
    if rep["q4_nps"]:    badges.append('<span class="bdg red">Q4 NPS</span>')
    if rep["q4_tmo"]:    badges.append('<span class="bdg red">Q4 TMO</span>')
    if rep["q4_estilo"]: badges.append('<span class="bdg red">Q4 Estilo</span>')
    return " ".join(badges) if badges else '<span class="bdg neu">OK</span>'

# ══════════════════════════════════════════════════════════════════════
# KPIs GERAIS
# ══════════════════════════════════════════════════════════════════════
n_total     = len(REPS)
n_expert    = sum(1 for r in REPS if r.get("senioridade") == "Expert")
n_newbie    = sum(1 for r in REPS if r.get("senioridade") == "Newbie")
adopt_vals  = [r["pct_adopcion"] for r in REPS if r.get("pct_adopcion") is not None]
adopt_media = round(sum(adopt_vals)/len(adopt_vals), 1) if adopt_vals else 0
n_low       = sum(1 for r in REPS if r["low_adopt"])
n_critico   = sum(1 for r in REPS if r["critico"])
n_q4_any    = sum(1 for r in REPS if r["n_q4"] >= 1)

# Distribuição de adoção
buckets = {"0-20%": 0, "20-40%": 0, "40-60%": 0, "60-80%": 0, "80-100%": 0}
for r in REPS:
    v = r.get("pct_adopcion", 0) or 0
    if v < 20:   buckets["0-20%"]    += 1
    elif v < 40: buckets["20-40%"]   += 1
    elif v < 60: buckets["40-60%"]   += 1
    elif v < 80: buckets["60-80%"]   += 1
    else:        buckets["80-100%"]  += 1

# ══════════════════════════════════════════════════════════════════════
# TABELAS HTML
# ── Tooltip helper ────────────────────────────────────────────────────
TIPS = {
    "Adoção%":     "% dos outgoings (respostas ao cliente) em que o rep efetivamente usou o Copilot. Denominador = Copilot habilitado; numerador = rep interagiu com o Copilot naquele outgoing.",
    "NPS":         "NPS médio dos casos atendidos com Copilot. Promotor (+1), Passivo (0), Detrator (−1), exibido em %. Requer mínimo de 3 pesquisas para ser calculado.",
    "TMO(s)":      "Tempo Médio de Operação em segundos nos casos onde o rep usou o Copilot (FLAG_COPILOT=1). Valores altos indicam atendimentos mais demorados.",
    "Estilo Meli": "Nota de qualidade do QM (form Estilo Meli IA). Escala de 0 a 1 — avalia start contact, exploração, orientação e encerramento do atendimento.",
    "Status Q4":   "Métricas em que o rep está no pior quartil (25% piores da equipe). Q4 NPS = NPS baixo | Q4 TMO = tempo alto | Q4 Estilo = nota QM baixa.",
    "Métricas Q4": "Métricas em que o rep está no pior quartil (25% piores da equipe). Q4 NPS = NPS baixo | Q4 TMO = tempo alto | Q4 Estilo = nota QM baixa.",
    "Adoção% (processo)": "% dos outgoings neste processo em que os reps usaram o Copilot.",
}

def th(label, tip_key=None, cls=""):
    tip = TIPS.get(tip_key or label, "")
    cls_attr = f' class="{cls}"' if cls else ""
    if not tip:
        return f"<th{cls_attr}>{label}</th>"
    return (f'<th{cls_attr}>{label}'
            f'<span class="th-tip-icon">?</span>'
            f'<span class="th-tip-box">{tip}</span>'
            f'</th>')

# ══════════════════════════════════════════════════════════════════════
def reps_table(reps_list, show_q4_only=False, extra_cols=True):
    """Gera <table> de reps com métricas."""
    filtered = [r for r in reps_list if not show_q4_only or r["n_q4"] >= 1]
    if not filtered:
        return '<p class="sd" style="padding:12px">Nenhum rep encontrado.</p>'
    rows = ""
    for r in filtered:
        adopt_cls = color_adopt(r.get("pct_adopcion"))
        nps_cls   = color_nps(r.get("nps_copilot"), r["q4_nps"])
        tmo_cls   = color_tmo(r.get("tmo_com_copilot"), r["q4_tmo"])
        em_cls    = color_estilo(r.get("estilo_meli"), r["q4_estilo"])
        sen_cls   = "exp-badge" if r.get("senioridade") == "Expert" else "new-badge"
        rows += f"""<tr>
          <td class="rep-name" data-office="{r['USER_OFFICE']}" data-canal="{r['USER_TEAM_CHANNEL']}">{r['USER_LDAP']}</td>
          <td><span class="{sen_cls}">{r.get('senioridade','N/D')}</span></td>
          <td>{r.get('USER_OFFICE','—')}</td>
          <td>{r.get('USER_TEAM_CHANNEL','—')}</td>
          <td class="{adopt_cls}">{fmt(r.get('pct_adopcion'))}%</td>
          <td class="{nps_cls}">{fmt(r.get('nps_copilot'))}%</td>
          <td class="{tmo_cls}">{fmt(r.get('tmo_com_copilot'),0,'s')}</td>
          <td class="{em_cls}">{fmt(r.get('estilo_meli'))}</td>
          {'<td>' + badge_q4(r) + '</td>' if extra_cols else ''}
        </tr>"""
    header_q4 = th("Status Q4") if extra_cols else ""
    return f"""
    <table class="rt" data-table>
      <thead><tr>
        <th class="left">Rep</th><th>Senioridade</th><th>Oficina</th><th>Canal</th>
        {th("Adoção%")}{th("NPS")}{th("TMO(s)")}{th("Estilo Meli")}{header_q4}
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""

# ─── Tab 2: Reps Q4 ────────────────────────────────────────────────
def build_q4_tab():
    all_html     = reps_table(sorted(REPS, key=lambda r: (r["n_q4"]==0, -r.get("pct_adopcion",0))), show_q4_only=True)
    expert_html  = reps_table([r for r in REPS if r.get("senioridade")=="Expert"], show_q4_only=True)
    newbie_html  = reps_table([r for r in REPS if r.get("senioridade")=="Newbie"], show_q4_only=True)
    return f"""
    <div class="ptabs">
      <button class="ptab active" onclick="setPtab('q4','todos',this)">Todos ({sum(1 for r in REPS if r['n_q4']>=1)})</button>
      <button class="ptab" onclick="setPtab('q4','expert',this)">Expert ({sum(1 for r in REPS if r['n_q4']>=1 and r.get('senioridade')=='Expert')})</button>
      <button class="ptab" onclick="setPtab('q4','newbie',this)">Newbie ({sum(1 for r in REPS if r['n_q4']>=1 and r.get('senioridade')=='Newbie')})</button>
    </div>
    <div id="q4-todos"   class="period-pane active">{all_html}</div>
    <div id="q4-expert"  class="period-pane">{expert_html}</div>
    <div id="q4-newbie"  class="period-pane">{newbie_html}</div>
    <div class="note">
      <strong>Q4</strong> = pior quartil: NPS abaixo de {fmt(q4_nps)}% | TMO acima de {fmt(q4_tmo,0)}s | Estilo Meli abaixo de {fmt(q4_estilo)}.
      Reps com poucos dados (&lt;{MIN_NPS} pesquisas NPS ou &lt;{MIN_QM} análise QM) não são marcados Q4 para aquela métrica.
    </div>"""

# ─── Tab 3: Usabilidade por processo ───────────────────────────────
def build_processo_tab():
    # Agrega por processo (todos os reps)
    proc_agg = defaultdict(lambda: {"outgoing_total":0,"outgoing_copilot":0,"reps":set()})
    for row in BY_PROC:
        p = row["processo"]
        proc_agg[p]["outgoing_total"]   += row.get("outgoing_total",   0) or 0
        proc_agg[p]["outgoing_copilot"] += row.get("outgoing_copilot", 0) or 0
        proc_agg[p]["reps"].add(row["USER_LDAP"])

    # Agrega por processo (apenas Q4 reps)
    q4_ldaps = {r["USER_LDAP"] for r in REPS if r["n_q4"] >= 1}
    proc_q4  = defaultdict(lambda: {"outgoing_total":0,"outgoing_copilot":0,"reps":set()})
    for row in BY_PROC:
        if row["USER_LDAP"] not in q4_ldaps: continue
        p = row["processo"]
        proc_q4[p]["outgoing_total"]   += row.get("outgoing_total",   0) or 0
        proc_q4[p]["outgoing_copilot"] += row.get("outgoing_copilot", 0) or 0
        proc_q4[p]["reps"].add(row["USER_LDAP"])

    def proc_table(agg):
        rows_data = []
        for proc, d in agg.items():
            tot = d["outgoing_total"] or 0
            cop = d["outgoing_copilot"] or 0
            pct = round(cop/tot*100, 1) if tot > 0 else 0
            rows_data.append((proc, len(d["reps"]), tot, cop, pct))
        rows_data.sort(key=lambda x: x[4])  # menor adoção primeiro
        rows = ""
        for proc, n_reps, tot, cop, pct in rows_data:
            cls = color_adopt(pct)
            rows += f"""<tr>
              <td class="rep-name">{proc}</td>
              <td>{n_reps}</td>
              <td>{tot:,}</td>
              <td>{cop:,}</td>
              <td class="{cls}">{pct}%</td>
            </tr>"""
        return f"""<table class="rt" data-table>
          <thead><tr>
            <th class="left">Processo</th><th>Reps</th>
            <th>Outgoing Total</th><th>Com Copilot</th><th>Adoção%</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>"""

    return f"""
    <div class="ptabs">
      <button class="ptab active" onclick="setPtab('proc','todos',this)">Todos os Reps</button>
      <button class="ptab" onclick="setPtab('proc','q4',this)">Apenas Reps Q4</button>
    </div>
    <div id="proc-todos" class="period-pane active">{proc_table(proc_agg)}</div>
    <div id="proc-q4"    class="period-pane">{proc_table(proc_q4)}</div>
    <div class="note">Ordenado do menor para maior % de adoção — processos no topo são prioridade de atenção.</div>"""

# ─── Tab 4: Top Usuários ───────────────────────────────────────────
def build_top_tab():
    top = sorted(REPS, key=lambda r: -(r.get("pct_adopcion") or 0))[:20]
    return reps_table(top, show_q4_only=False, extra_cols=False) + """
    <div class="note">Top 20 reps por % de adoção. Verde = boa performance naquele indicador.</div>"""

# ─── Tab 5: Análise de Consultas ───────────────────────────────────
def build_consultas_tab():
    if not CATS:
        return '<p class="note">Execute _copilot_categorize.py para gerar a análise de consultas.</p>'

    options = "".join(f'<option value="{p}">{p} ({CATS[p]["n_transcricoes"]} transcrições)</option>'
                      for p in sorted(CATS.keys()))

    cards_js = {}
    for proc, data in CATS.items():
        cats_list = data.get("categorias", [])
        cards_js[proc] = cats_list

    cards_json = json.dumps(cards_js, ensure_ascii=False)

    return f"""
    <div style="margin-bottom:16px">
      <label style="font-size:12px;font-weight:700;color:#64748b;margin-right:8px">Processo:</label>
      <select id="proc-sel" onchange="renderCats()" style="font-size:13px;padding:6px 10px;border-radius:7px;border:1px solid #e2e8f0;background:white">
        {options}
      </select>
    </div>
    <div id="cats-wrap"></div>
    <script>
    const CATS_DATA = {cards_json};
    function renderCats() {{
      const proc  = document.getElementById('proc-sel').value;
      const cats  = CATS_DATA[proc] || [];
      const wrap  = document.getElementById('cats-wrap');
      if (!cats.length) {{ wrap.innerHTML='<p class="note">Sem dados para este processo.</p>'; return; }}
      const sorted = [...cats].sort((a,b) => (b.pct_estimado||0)-(a.pct_estimado||0));
      wrap.innerHTML = sorted.map(c => `
        <div class="cat-card">
          <div class="cat-header">
            <span class="cat-name">${{c.nome}}</span>
            <span class="cat-pct">${{c.pct_estimado||'?'}}%</span>
          </div>
          <div class="cat-bar-wrap"><div class="cat-bar" style="width:${{c.pct_estimado||0}}%"></div></div>
          <div class="cat-desc">${{c.descricao||''}}</div>
          <div class="cat-ex">${{(c.exemplos||[]).map(e=>`<div class="ex-item">"${{e}}"</div>`).join('')}}</div>
        </div>`).join('');
    }}
    document.addEventListener('DOMContentLoaded', renderCats);
    </script>"""

# ─── Tab 6: Reps Críticos ──────────────────────────────────────────
def build_criticos_tab():
    criticos = sorted(
        [r for r in REPS if r["critico"]],
        key=lambda r: (-r["n_q4"], r.get("pct_adopcion") or 0)
    )
    n = len(criticos)
    if not n:
        return '<p class="note">Nenhum rep crítico encontrado (baixa adoção + Q4 em alguma métrica).</p>'

    rows = ""
    for r in criticos:
        adopt_cls = color_adopt(r.get("pct_adopcion"))
        sen_cls   = "exp-badge" if r.get("senioridade") == "Expert" else "new-badge"
        rows += f"""<tr>
          <td class="rep-name" data-office="{r['USER_OFFICE']}" data-canal="{r['USER_TEAM_CHANNEL']}">{r['USER_LDAP']}</td>
          <td><span class="{sen_cls}">{r.get('senioridade','N/D')}</span></td>
          <td class="{adopt_cls}">{fmt(r.get('pct_adopcion'))}%</td>
          <td>{fmt(r.get('nps_copilot'))}%</td>
          <td>{fmt(r.get('tmo_com_copilot'),0,'s')}</td>
          <td>{fmt(r.get('estilo_meli'))}</td>
          <td>{badge_q4(r)}</td>
          <td>{r.get('USER_OFFICE','—')}</td>
          <td>{r.get('USER_TEAM_CHANNEL','—')}</td>
        </tr>"""

    return f"""
    <div class="sc-grid" style="grid-template-columns:repeat(3,1fr);margin-bottom:20px">
      <div class="kc"><div class="lbl">Reps Críticos</div><div class="val" style="color:#dc2626">{n}</div><div class="cmp">Baixa adoção + Q4 ≥1 métrica</div></div>
      <div class="kc"><div class="lbl">Adoção &lt; {int(LOW_ADOPT)}%</div><div class="val" style="color:#d97706">{n_low}</div><div class="cmp">De {n_total} reps totais</div></div>
      <div class="kc"><div class="lbl">Q4 ≥1 métrica</div><div class="val" style="color:#7c3aed">{n_q4_any}</div><div class="cmp">NPS, TMO ou Estilo Meli</div></div>
    </div>
    <table class="rt" data-table>
      <thead><tr>
        <th class="left">Rep</th><th>Senioridade</th>
        {th("Adoção%")}{th("NPS")}{th("TMO(s)")}{th("Estilo Meli")}
        {th("Métricas Q4")}<th>Oficina</th><th>Canal</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <div class="note warn"><strong>Ação recomendada:</strong> priorizar esses reps para acompanhamento individualizado — combinar baixo uso com performance crítica nos KPIs.</div>"""

# ══════════════════════════════════════════════════════════════════════
# DADOS JS (para filtros client-side)
# ══════════════════════════════════════════════════════════════════════
offices  = sorted({r.get("USER_OFFICE","N/D") for r in REPS})
canais   = sorted({r.get("USER_TEAM_CHANNEL","N/D") for r in REPS})
offices_opts  = '<option value="ALL">Todas as Oficinas</option>' + "".join(f'<option value="{o}">{o}</option>' for o in offices if o != "N/D")
canais_opts   = '<option value="ALL">Todos os Canais</option>'   + "".join(f'<option value="{c}">{c}</option>' for c in canais  if c != "N/D")

today = date.today().strftime("%d/%m/%Y")

# ══════════════════════════════════════════════════════════════════════
# GERA HTML
# ══════════════════════════════════════════════════════════════════════
html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CX Copilot — Usabilidade dos Reps</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f7;color:#1a1a2e}}
.header{{background:#1a1a2e;color:white;padding:20px 32px;display:flex;justify-content:space-between;align-items:flex-start}}
.header h1{{font-size:18px;font-weight:700}}
.header .sub{{font-size:12px;color:#94a3b8;margin-top:4px}}
.filter-bar{{background:white;padding:10px 32px;display:flex;align-items:center;gap:16px;border-bottom:1px solid #e2e8f0;flex-wrap:wrap}}
.filter-bar label{{font-size:12px;font-weight:600;color:#64748b}}
.filter-bar select{{font-size:12px;padding:5px 10px;border-radius:7px;border:1px solid #e2e8f0;background:white;color:#1e293b}}
.container{{max-width:1350px;margin:0 auto;padding:20px 16px 40px}}
.tabs{{display:flex;gap:4px;margin-bottom:16px;background:white;padding:6px;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.07);width:fit-content;flex-wrap:wrap}}
.tab-btn{{padding:7px 18px;border-radius:7px;border:none;cursor:pointer;font-size:13px;font-weight:600;background:transparent;color:#64748b;transition:.15s}}
.tab-btn.active{{background:#1d4ed8;color:white}}
.tab-pane{{display:none}}.tab-pane.active{{display:block}}
.ptabs{{display:flex;gap:3px;margin-bottom:16px;background:#e2e8f0;padding:4px;border-radius:8px;width:fit-content}}
.ptab{{padding:6px 18px;border-radius:6px;border:none;cursor:pointer;font-size:12px;font-weight:600;background:transparent;color:#64748b}}
.ptab.active{{background:white;color:#1d4ed8;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
.period-pane{{display:none}}.period-pane.active{{display:block}}
.sc-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:16px}}
.kc{{background:white;border-radius:10px;padding:12px 14px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.kc .lbl{{font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:#94a3b8;font-weight:600;margin-bottom:7px}}
.kc .val{{font-size:22px;font-weight:800;color:#1d4ed8;line-height:1}}
.kc .cmp{{font-size:11px;color:#94a3b8;margin-top:4px}}
.ch-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:10px}}
.cc{{background:white;border-radius:10px;padding:16px 20px 14px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.cc h3{{font-size:12px;font-weight:700;color:#1e293b}}
.cc p{{font-size:10.5px;color:#94a3b8;margin:2px 0 10px}}
.rep-table-wrap{{margin-top:10px;overflow-x:auto}}
table.rt{{width:100%;border-collapse:collapse;font-size:11.5px}}
table.rt th{{background:#1a1a2e;color:white;padding:7px 10px;text-align:center;font-size:10.5px;font-weight:600;letter-spacing:.3px;white-space:nowrap}}
table.rt th.left{{text-align:left}}
table.rt td{{padding:5px 9px;border-bottom:1px solid #f1f5f9;text-align:center;white-space:nowrap}}
table.rt td.rep-name{{text-align:left;font-weight:600;font-size:11px;color:#1e293b}}
table.rt tr:hover td{{filter:brightness(.97)}}
.gc{{background:#dcfce7!important;color:#15803d;font-weight:700}}
.yc{{background:#fef9c3!important;color:#854d0e;font-weight:700}}
.rc{{background:#fee2e2!important;color:#dc2626;font-weight:700}}
.sd{{color:#cbd5e1;font-style:italic}}
.note{{font-size:11px;color:#94a3b8;background:white;padding:9px 14px;border-radius:8px;border-left:3px solid #e2e8f0;margin-top:10px;line-height:1.6}}
.note strong{{color:#64748b}}
.note.warn{{border-left-color:#f59e0b;background:#fffbeb}}.note.warn strong{{color:#92400e}}
.bdg{{font-size:10px;font-weight:700;padding:2px 7px;border-radius:5px;display:inline-block;margin:1px}}
.bdg.red{{background:#fee2e2;color:#dc2626}}
.bdg.neu{{background:#f1f5f9;color:#64748b}}
.exp-badge{{background:#dbeafe;color:#1d4ed8;font-size:10px;font-weight:700;padding:2px 7px;border-radius:5px}}
.new-badge{{background:#f3e8ff;color:#7c3aed;font-size:10px;font-weight:700;padding:2px 7px;border-radius:5px}}
th{{position:relative}}
.th-tip-icon{{display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;border-radius:50%;background:#94a3b8;color:#fff;font-size:9px;font-weight:700;margin-left:5px;cursor:help;vertical-align:middle;line-height:1}}
.th-tip-box{{display:none;position:absolute;top:100%;left:50%;transform:translateX(-50%);background:#1e293b;color:#f1f5f9;font-size:12px;font-weight:400;line-height:1.5;padding:8px 12px;border-radius:7px;width:240px;z-index:999;box-shadow:0 4px 12px rgba(0,0,0,.3);white-space:normal;text-align:left}}
th:hover .th-tip-box{{display:block}}
.section-lbl{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#94a3b8;margin:20px 0 10px;padding-top:8px;border-top:1px solid #e2e8f0}}
.cat-card{{background:white;border-radius:10px;padding:14px 16px;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.cat-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}}
.cat-name{{font-size:13px;font-weight:700;color:#1e293b}}
.cat-pct{{font-size:13px;font-weight:800;color:#1d4ed8}}
.cat-bar-wrap{{background:#e2e8f0;border-radius:4px;height:6px;margin-bottom:8px}}
.cat-bar{{background:#1d4ed8;border-radius:4px;height:6px;transition:.3s}}
.cat-desc{{font-size:11.5px;color:#64748b;margin-bottom:8px}}
.ex-item{{font-size:11px;color:#374151;background:#f8fafc;border-left:3px solid #93c5fd;padding:5px 10px;margin-bottom:4px;border-radius:0 5px 5px 0;font-style:italic}}
.footer{{font-size:11px;color:#94a3b8;text-align:center;margin-top:28px}}
.hidden{{display:none!important}}
@media(max-width:900px){{.sc-grid{{grid-template-columns:repeat(3,1fr)}}.ch-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>CX Copilot — Usabilidade dos Reps · BR</h1>
    <div class="sub">Últimos {DAYS_BACK} dias · {n_total} reps ativos · Gerado em {today}</div>
  </div>
</div>

<div class="filter-bar">
  <label>Oficina:</label>
  <select id="f-office" onchange="applyFilters()">{offices_opts}</select>
  <label>Canal:</label>
  <select id="f-canal" onchange="applyFilters()">{canais_opts}</select>
  <span id="filter-count" style="font-size:11px;color:#94a3b8;margin-left:8px"></span>
</div>

<div class="container">
  <div class="tabs">
    <button class="tab-btn active" onclick="setTab('geral',this)">Visão Geral</button>
    <button class="tab-btn" onclick="setTab('q4',this)">Reps Q4</button>
    <button class="tab-btn" onclick="setTab('proc',this)">Por Processo</button>
    <button class="tab-btn" onclick="setTab('top',this)">Top Usuários</button>
    <button class="tab-btn" onclick="setTab('consul',this)">Análise de Consultas</button>
    <button class="tab-btn" onclick="setTab('crit',this)">Reps Críticos</button>
  </div>

  <!-- ══ TAB 1: VISÃO GERAL ══ -->
  <div id="tab-geral" class="tab-pane active">
    <div class="sc-grid">
      <div class="kc"><div class="lbl">Reps Ativos Copilot</div><div class="val">{n_total}</div><div class="cmp">Expert: {n_expert} | Newbie: {n_newbie}</div></div>
      <div class="kc"><div class="lbl">Adoção Média</div><div class="val" style="color:{'#15803d' if adopt_media>=50 else '#d97706' if adopt_media>=30 else '#dc2626'}">{adopt_media}%</div><div class="cmp">% outgoing com Copilot</div></div>
      <div class="kc"><div class="lbl">Adoção &lt; {int(LOW_ADOPT)}%</div><div class="val" style="color:#d97706">{n_low}</div><div class="cmp">{round(n_low/n_total*100) if n_total else 0}% dos reps</div></div>
      <div class="kc"><div class="lbl">Q4 ≥1 Métrica</div><div class="val" style="color:#7c3aed">{n_q4_any}</div><div class="cmp">NPS, TMO ou Estilo Meli</div></div>
      <div class="kc"><div class="lbl">Críticos</div><div class="val" style="color:#dc2626">{n_critico}</div><div class="cmp">Baixa adoção + Q4</div></div>
    </div>
    <div class="ch-grid">
      <div class="cc">
        <h3>Distribuição de Adoção</h3>
        <p>N° de reps por faixa de % adoção Copilot</p>
        <canvas id="ch-dist"></canvas>
      </div>
      <div class="cc">
        <h3>Expert vs Newbie — Adoção Média</h3>
        <p>Comparação de adoção por senioridade</p>
        <canvas id="ch-sen"></canvas>
      </div>
    </div>
    <div class="section-lbl">Todos os Reps — Visão Geral</div>
    {reps_table(sorted(REPS, key=lambda r: -(r.get('pct_adopcion') or 0)), show_q4_only=False)}
  </div>

  <!-- ══ TAB 2: REPS Q4 ══ -->
  <div id="tab-q4" class="tab-pane">
    {build_q4_tab()}
  </div>

  <!-- ══ TAB 3: POR PROCESSO ══ -->
  <div id="tab-proc" class="tab-pane">
    {build_processo_tab()}
  </div>

  <!-- ══ TAB 4: TOP USUÁRIOS ══ -->
  <div id="tab-top" class="tab-pane">
    <div class="section-lbl">Top 20 Reps por Adoção Copilot</div>
    {build_top_tab()}
  </div>

  <!-- ══ TAB 5: ANÁLISE DE CONSULTAS ══ -->
  <div id="tab-consul" class="tab-pane">
    <div class="section-lbl">O que os reps pedem ao Copilot — por processo</div>
    {build_consultas_tab()}
  </div>

  <!-- ══ TAB 6: REPS CRÍTICOS ══ -->
  <div id="tab-crit" class="tab-pane">
    <div class="section-lbl">Reps com Baixa Adoção + Performance Crítica</div>
    {build_criticos_tab()}
  </div>

  <div class="footer">CX Copilot · Usabilidade · {today} · Dados: últimos {DAYS_BACK} dias</div>
</div>

<script>
// ── TABS ──────────────────────────────────────────────────────────────
function setTab(id, btn) {{
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  btn.classList.add('active');
}}
function setPtab(group, id, btn) {{
  document.querySelectorAll('[id^="' + group + '-"]').forEach(p => p.classList.remove('active'));
  btn.closest('.ptabs').querySelectorAll('.ptab').forEach(b => b.classList.remove('active'));
  document.getElementById(group + '-' + id).classList.add('active');
  btn.classList.add('active');
}}

// ── FILTROS ───────────────────────────────────────────────────────────
function applyFilters() {{
  const office = document.getElementById('f-office').value;
  const canal  = document.getElementById('f-canal').value;
  let vis = 0, tot = 0;
  document.querySelectorAll('table[data-table] tbody tr').forEach(tr => {{
    const td = tr.querySelector('td[data-office]');
    if (!td) {{ tr.classList.remove('hidden'); return; }}
    const ro = td.dataset.office || '';
    const rc = td.dataset.canal  || '';
    const show = (office === 'ALL' || ro === office) && (canal === 'ALL' || rc === canal);
    tr.classList.toggle('hidden', !show);
    tot++; if (show) vis++;
  }});
  const el = document.getElementById('filter-count');
  if (office !== 'ALL' || canal !== 'ALL') el.textContent = `${{vis}} de ${{tot}} reps visíveis`;
  else el.textContent = '';
}}

// ── CHARTS ────────────────────────────────────────────────────────────
const DIST_DATA = {json.dumps(list(buckets.values()))};
const DIST_LBLS = {json.dumps(list(buckets.keys()))};

const adopt_expert = {round(sum(r.get('pct_adopcion',0) or 0 for r in REPS if r.get('senioridade')=='Expert') / max(sum(1 for r in REPS if r.get('senioridade')=='Expert'),1), 1)};
const adopt_newbie = {round(sum(r.get('pct_adopcion',0) or 0 for r in REPS if r.get('senioridade')=='Newbie') / max(sum(1 for r in REPS if r.get('senioridade')=='Newbie'),1), 1)};

window.addEventListener('DOMContentLoaded', () => {{
  new Chart(document.getElementById('ch-dist'), {{
    type: 'bar',
    data: {{
      labels: DIST_LBLS,
      datasets: [{{
        label: 'Reps',
        data: DIST_DATA,
        backgroundColor: ['#dc2626','#f59e0b','#f59e0b','#22c55e','#15803d'],
        borderRadius: 5
      }}]
    }},
    options: {{
      plugins: {{
        legend: {{ display: false }},
        datalabels: {{
          anchor: 'center', align: 'center',
          color: '#fff', font: {{ weight: 'bold', size: 13 }},
          formatter: v => v
        }}
      }},
      scales: {{ y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }} }}
    }}
  }});

  new Chart(document.getElementById('ch-sen'), {{
    type: 'bar',
    data: {{
      labels: ['Expert', 'Newbie'],
      datasets: [{{
        label: 'Adoção Média %',
        data: [adopt_expert, adopt_newbie],
        backgroundColor: ['#1d4ed8','#7c3aed'],
        borderRadius: 5
      }}]
    }},
    options: {{
      plugins: {{
        legend: {{ display: false }},
        datalabels: {{
          anchor: 'center', align: 'center',
          color: '#fff', font: {{ weight: 'bold', size: 13 }},
          formatter: v => v + '%'
        }}
      }},
      scales: {{ y: {{ beginAtZero: true, max: 100, ticks: {{ callback: v => v+'%' }} }} }}
    }}
  }});
}});
</script>
</body>
</html>"""

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"=== Dashboard gerado: {OUT_FILE} ===")
print(f"    {n_total} reps | {n_critico} críticos | {n_q4_any} com Q4")
