def driver_dd_tab(wD_data, wP_data, mD_data, mP_data):
    """Deep Dive por Driver — executive brief, tabelas P/C/O/Sr, filtro de processo (driver_impact.html style)."""
    # ── 1. DD_BK ─────────────────────────────────────────────────
    def _to_bk(t):
        p,d,s=t[0],t[1],t[2]
        return {"p":p,"d":d,"s":s,"nps":round(100*(p-d)/s,1) if s>0 else None}
    dd_bk={}
    for drv in DRIVER_COLORS:
        p_data={}
        for pk,pd in [("S2",weekly_proc[drv].get("S2",{})),
                       ("S1",weekly_proc[drv].get("S1",{})),
                       ("M2",monthly_proc[drv].get("M2",{})),
                       ("M1",monthly_proc[drv].get("M1",{}))]:
            p_data[pk]={proc:_to_bk(v) for proc,v in pd.items()}
        sr_data={}
        if drv in seniority_weekly:
            for pk in ["S1","S2"]:
                if pk in seniority_weekly[drv]:
                    sr_data[pk]={}
                    for stype,key in [("Expert","EXPERT"),("Newbie","NEWBIE")]:
                        t=seniority_weekly[drv][pk].get(key,(0,0,0))
                        sr_data[pk][stype]=_to_bk(t)
        if drv in seniority_monthly:
            sr_data["M1"]={}
            for stype,key in [("Expert","EXPERT"),("Newbie","NEWBIE")]:
                t=seniority_monthly[drv].get(key,(0,0,0))
                sr_data["M1"][stype]=_to_bk(t)
        # Canal (C) e Oficina (O) de canal_weekly/monthly e oficina_weekly/monthly
        c_data={}
        for pk,cd in [("S2",canal_weekly.get(drv,{}).get("S2",{})),
                       ("S1",canal_weekly.get(drv,{}).get("S1",{})),
                       ("M2",canal_monthly.get(drv,{}).get("M2",{})),
                       ("M1",canal_monthly.get(drv,{}).get("M1",{}))]:
            c_data[pk]={canal:_to_bk(v) for canal,v in cd.items()}
        o_data={}
        for pk,od in [("S2",oficina_weekly.get(drv,{}).get("S2",{})),
                       ("S1",oficina_weekly.get(drv,{}).get("S1",{})),
                       ("M2",oficina_monthly.get(drv,{}).get("M2",{})),
                       ("M1",oficina_monthly.get(drv,{}).get("M1",{}))]:
            o_data[pk]={of:_to_bk(v) for of,v in od.items()}
        # P_C (processo × canal) e P_O (processo × oficina)
        # S1=20/abr (old S2 key), S2=13/abr (sem dados), M1=Abril (old M2 key), M2=Março (sem dados)
        pc_data={}
        for pk,pc_dict in [("S2",{}),
                            ("S1",p_c_weekly.get(drv,{}).get("S2",{})),
                            ("M2",{}),
                            ("M1",p_c_monthly.get(drv,{}).get("M2",{}))]:
            pc_data[pk]={proc:{canal:_to_bk(v) for canal,v in canal_dict.items()}
                         for proc,canal_dict in pc_dict.items()}
        po_data={}
        for pk,po_dict in [("S2",{}),
                            ("S1",p_o_weekly.get(drv,{}).get("S2",{})),
                            ("M2",{}),
                            ("M1",p_o_monthly.get(drv,{}).get("M2",{}))]:
            po_data[pk]={proc:{ofic:_to_bk(v) for ofic,v in ofic_dict.items()}
                         for proc,ofic_dict in po_dict.items()}
        dd_bk[drv]={"P":p_data,"C":c_data,"O":o_data,"Sr":sr_data,"Sr_P":{},"P_C":pc_data,"P_O":po_data}
    # ── 2. DRV_HIST ──────────────────────────────────────────────
    def _he(lbl,t):
        p,d,s=t[0],t[1],t[2]
        return {"label":lbl,"nps":round(100*(p-d)/s,2) if s>0 else None,"s":s}
    drv_hist={}
    for drv in DRIVER_COLORS:
        drv_hist[drv]={
            "target":DRIVER_TARGETS[drv],"cat":"Sellers",
            "weekly": [_he(lbl,weekly_history[drv].get(lbl,(0,0,0)))  for lbl in WEEK_LABELS  if lbl in weekly_history[drv]],
            "monthly":[_he(lbl,monthly_history[drv].get(lbl,(0,0,0))) for lbl in MONTH_LABELS if lbl in monthly_history[drv]],
        }
    # ── 3. DD_SUM ────────────────────────────────────────────────
    dd_sum={}
    for drv,insights,key in [
        (DEEP_DIVE_POS_DRIVER, DEEP_DIVE_POS_INSIGHTS+DCEV_ACOES,    "wow"),
        (DEEP_DIVE_NEG_DRIVER, DEEP_DIVE_NEG_INSIGHTS+DCEV_ACOES,    "wow"),
        (DD_MES_POS_DRIVER,    DD_MES_POS_INSIGHTS+DD_MES_ACO,       "mom"),
        (DD_MES_NEG_DRIVER,    DD_MES_NEG_INSIGHTS+DD_MES_ACO,       "mom"),
    ]:
        if drv not in dd_sum: dd_sum[drv]={}
        if key not in dd_sum[drv]:
            dd_sum[drv][key]="\n".join("▶ "+i for i in insights)
    # ── 4. Serialize ─────────────────────────────────────────────
    bk_json  =_json.dumps(dd_bk)
    hist_json=_json.dumps(drv_hist)
    sum_json =_json.dumps(dd_sum)
    cfg_json =_json.dumps({"M1L":M1_LABEL,"M2L":M2_LABEL,"S1L":S1_LABEL,
                             "S2L":S2_LABEL,"VIGL":VIG_LABEL,
                             "TGT":DRIVER_TARGETS,"COLORS":DRIVER_COLORS,"SHORT":DRIVER_SHORT})
    opts="".join(f'<option value="{d}">{DRIVER_SHORT[d]}</option>' for d in DRIVER_COLORS)
    # ── 5. CSS ───────────────────────────────────────────────────
    css=(
        ".pill{display:inline-block;padding:2px 9px;border-radius:12px;font-weight:700;font-size:11px;white-space:nowrap}"
        ".pill-pos-hi{background:#e8f5e9;color:#1b5e20}.pill-pos-lo{background:#f1f8e9;color:#33691e}"
        ".pill-neg-hi{background:#ffebee;color:#b71c1c}.pill-dn1{background:#fff3e0;color:#e65100}"
        ".pill-dn2{background:#ffebee;color:#b71c1c}.pill-up1{background:#f1f8e9;color:#33691e}"
        ".pill-up2{background:#e8f5e9;color:#1b5e20}.pill-flat{background:#f5f5f5;color:#777}"
        ".pill-neu{background:#f5f5f5;color:#9e9e9e}"
        ".exec-brief{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1);margin-bottom:20px}"
        ".exec-brief-hdr{background:#1a1e3c;color:#fff;padding:14px 18px}"
        ".exec-brief-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}"
        ".exec-brief-drv{font-size:14px;font-weight:700}.exec-brief-per{font-size:11px;color:#aab4d4}"
        ".exec-brief-kpis{display:flex;gap:8px;flex-wrap:wrap}"
        ".exec-brief-kpi{background:rgba(255,255,255,.12);border-radius:7px;padding:6px 12px;display:flex;flex-direction:column;gap:2px}"
        ".exec-brief-kpi-lbl{font-size:9px;color:#aab4d4;text-transform:uppercase;letter-spacing:.5px}"
        ".exec-brief-kpi-val{font-size:17px;font-weight:700;line-height:1}"
        ".exec-brief-kpi-val.pos{color:#69f0ae}.exec-brief-kpi-val.neg{color:#ff8a80}.exec-brief-kpi-val.neutral{color:#fff}"
        ".exec-brief-body{display:grid;grid-template-columns:1fr 1fr}"
        ".exec-sec{padding:13px 16px;border-bottom:1px solid #f0f2f5;border-right:1px solid #f0f2f5}"
        ".exec-sec:nth-child(even){border-right:none}"
        ".exec-sec.fw{grid-column:1/-1;border-right:none}"
        ".exec-sec:last-child,.exec-sec:nth-last-child(2){border-bottom:none}"
        ".exec-sec-title{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;margin-bottom:8px}"
        ".exec-narr{font-size:12px;color:#333;line-height:1.65;margin:0 0 5px 0}"
        ".exec-bul{font-size:12px;color:#333;line-height:1.6;margin-bottom:5px;padding-left:4px}"
        ".exec-bul strong{color:#1a1e3c}.exec-na{font-size:12px;color:#aaa;font-style:italic}"
        ".dd2-pbar{display:flex;gap:6px;margin-bottom:16px}"
        ".dd2-pbtn{padding:7px 16px;border:1px solid var(--border);border-radius:8px;font-size:12px;font-weight:700;cursor:pointer;background:#fff;color:#888;transition:all .15s}"
        ".dd2-pbtn.active{background:var(--dark);color:#fff;border-color:var(--dark)}"
        ".dd2-bar{display:flex;align-items:center;gap:12px;margin-bottom:18px;background:#fff;border:1px solid var(--border);border-radius:10px;padding:12px 16px}"
        ".dd2-bar label{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;color:#888;white-space:nowrap}"
        ".dd2-bar select{flex:1;padding:7px 12px;border:1px solid #d0d5e0;border-radius:7px;font-size:14px;font-weight:600;color:var(--dark);background:#fafbff}"
        ".dd2-sc-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:18px}"
        ".dd2-sc{background:#fff;border-radius:10px;border:1px solid var(--border);padding:14px 16px}"
        ".dd2-sc .sc-lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#999;margin-bottom:6px}"
        ".dd2-sc .sc-val{font-size:26px;font-weight:800;line-height:1.1}"
        ".dd2-chart-sec{background:#fff;border-radius:12px;padding:16px 20px;box-shadow:0 1px 4px rgba(0,0,0,.07);margin-bottom:16px}"
        ".dd2-chart-title{font-size:13px;font-weight:700;color:#1a1e3c;margin-bottom:3px}"
        ".dd2-chart-sub{font-size:11px;color:#888;margin-bottom:10px}"
        ".dd2-chart-wrap{position:relative;height:250px}"
        ".dd-sec-title{font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.6px;margin:20px 0 8px;padding-bottom:6px;border-bottom:1px solid #eee}"
        ".bk-wrap2{overflow-x:auto;margin-bottom:10px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.06)}"
        ".bk-tbl2{width:100%;border-collapse:collapse;background:#fff;font-size:12px;table-layout:fixed}"
        ".bk-tbl2 thead tr{background:#f5f6fa;border-bottom:2px solid #e0e2ee}"
        ".bk-tbl2 thead th{color:#666;padding:7px 9px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;text-align:center}"
        ".bk-tbl2 thead th.cn{text-align:left;color:#1a1e3c}"
        ".bk-tbl2 tbody td{padding:6px 9px;border-bottom:1px solid #f2f2f5;vertical-align:middle;white-space:nowrap;text-align:center;color:#333}"
        ".bk-tbl2 tbody td.cn{text-align:left;white-space:normal;word-break:break-word;color:#1a1e3c;font-weight:500}"
        ".bk-tbl2 tbody tr:hover td{background:#fafbff}"
        ".bk-tbl2 tr.bkt td{background:#f0f2f8;font-weight:700;border-top:2px solid #dde0ea;color:#1a1e3c}"
        ".bk-sv2{color:#bbb!important;font-size:11px!important}"
        ".dd2-empty{background:#fff;border-radius:10px;border:1px solid var(--border);padding:40px;text-align:center;color:#bbb;font-size:14px}"
        ".dd2-fb{display:flex;align-items:center;gap:10px;margin:12px 0 6px;padding:7px 12px;background:#f5f7ff;border-radius:8px;border:1px solid #dde2f0}"
        ".dd2-fb span{font-size:12px;font-weight:600;color:#3a3f6b;white-space:nowrap}"
        ".dd2-fsel{flex:1;max-width:320px;padding:6px 10px;border:1px solid #d0d5e0;border-radius:6px;font-size:13px}"
    )
    # ── 6. JS ────────────────────────────────────────────────────
    js_data = (
        '<script id="_ddd_bk"   type="application/json">'+bk_json  +'</script>\n'
        +'<script id="_ddd_hist" type="application/json">'+hist_json+'</script>\n'
        +'<script id="_ddd_sum"  type="application/json">'+sum_json +'</script>\n'
        +'<script id="_ddd_cfg"  type="application/json">'+cfg_json +'</script>\n'
    )
    js_code = (
        "<script>\n(function(){\n"
        "var BK=JSON.parse(document.getElementById('_ddd_bk').textContent);\n"
        "var HST=JSON.parse(document.getElementById('_ddd_hist').textContent);\n"
        "var SUM=JSON.parse(document.getElementById('_ddd_sum').textContent);\n"
        "var CFG=JSON.parse(document.getElementById('_ddd_cfg').textContent);\n"
        "var M1L=CFG.M1L,M2L=CFG.M2L,S1L=CFG.S1L,S2L=CFG.S2L,VIGL=CFG.VIGL;\n"
        "var TGT=CFG.TGT,COLORS=CFG.COLORS,SHORT=CFG.SHORT;\n"
        "var _per='w',_ch2={};\n"
        "function _f2(v){return v==null?'—':v.toFixed(2).replace('.',',');}\n"
        "function _f1(v){return v==null?'—':v.toFixed(1)+'%';}\n"
        "function _lbl2(p){return p==='M2'?M2L:p==='M1'?M1L:p==='S2'?S2L:p==='S1'?S1L:p==='VIG'?VIGL+' &#9889;':p;}\n"
        "function _clr2(v){return v>=0?'#1a7a1a':'#c0321a';}\n"
        "function _tag2(v,d){var s=(v>=0?'+':'')+v.toFixed(d||2)+' pp';\n"
        "  return '<span style=\"font-weight:700;color:'+_clr2(v)+'\">' +s+'</span>';}\n"
        "function pill2(v){\n"
        "  if(v==null)return'<span class=\"pill pill-neu\">—</span>';\n"
        "  var s=(v>=0?'+':'')+v.toFixed(2)+' pp';\n"
        "  var c=v>=1?'pill-pos-hi':v>=0?'pill-pos-lo':v>=-1?'pill-dn1':'pill-neg-hi';\n"
        "  return'<span class=\"pill '+c+'\">'+s+'</span>';}\n"
        "function pillT2(v){\n"
        "  if(v==null)return'<span class=\"pill pill-neu\">—</span>';\n"
        "  if(v>=3)   return'<span class=\"pill pill-up2\">&#8679;&#8679; Em alta</span>';\n"
        "  if(v>=0.5) return'<span class=\"pill pill-up1\">&#8679; Evolução</span>';\n"
        "  if(v>-0.5) return'<span class=\"pill pill-flat\">&#8594; Estável</span>';\n"
        "  if(v>-3)   return'<span class=\"pill pill-dn1\">&#8681; Queda</span>';\n"
        "  return'<span class=\"pill pill-dn2\">&#8681;&#8681; Em queda</span>';}\n"
        "function pillVT2(nps,tgt2){\n"
        "  if(nps==null||!tgt2)return'<span class=\"pill pill-neu\">—</span>';\n"
        "  var g=nps-tgt2,s=(g>=0?'+':'')+g.toFixed(2)+' pp';\n"
        "  return'<span class=\"pill '+(g>=0?'pill-pos-hi':'pill-neg-hi')+'\">'+s+'</span>';}\n"
        "function pillImp2(v){\n"
        "  if(v==null||v===0)return'<span class=\"pill pill-neu\">0,00 pp</span>';\n"
        "  var s=(v>=0?'+':'')+v.toFixed(2)+' pp';\n"
        "  var c=v>=0.3?'pill-pos-hi':v>=0.05?'pill-pos-lo':v<=-0.3?'pill-neg-hi':v<=-0.05?'pill-dn1':'pill-neu';\n"
        "  return'<span class=\"pill '+c+'\">'+s+'</span>';}\n"
        "function sc2dd(lbl,val,delta,nps,tgt2){\n"
        "  var c=nps!=null&&tgt2?(nps>=tgt2?'#1a7a1a':'#c0321a'):delta!=null?(delta>=0?'#1a7a1a':'#c0321a'):'#bf5c00';\n"
        "  return'<div class=\"dd2-sc\"><div class=\"sc-lbl\">'+lbl+'</div>'\n"
        "        +'<div class=\"sc-val\" style=\"color:'+c+'\">'+val+'</div></div>';}\n"
        "function bkTbl2(bk,dim,pA,pB,tgt2,lbl){\n"
        "  var dd=(bk&&bk[dim])||{};\n"
        "  var dA=dd[pA]||{},dB=dd[pB]||{};\n"
        "  var keys=Array.from(new Set(Object.keys(dA).concat(Object.keys(dB))));\n"
        "  if(!keys.length)return'<div class=\"dd2-empty\" style=\"padding:16px;font-size:12px;color:#aaa\">Sem dados para esta abertura</div>';\n"
        "  var lA=_lbl2(pA),lB=_lbl2(pB);\n"
        "  var tA={p:0,d:0,s:0},tB={p:0,d:0,s:0};\n"
        "  keys.forEach(function(k){var a=dA[k]||{};var b=dB[k]||{};tA.p+=a.p||0;tA.d+=a.d||0;tA.s+=a.s||0;tB.p+=b.p||0;tB.d+=b.d||0;tB.s+=b.s||0;});\n"
        "  var nA=tA.s>0?(tA.p-tA.d)/tA.s*100:null,nB=tB.s>0?(tB.p-tB.d)/tB.s*100:null;\n"
        "  var items=keys.map(function(k){\n"
        "    var a=dA[k]||{p:0,d:0,s:0,nps:null},b=dB[k]||{p:0,d:0,s:0,nps:null};\n"
        "    var shA=tA.s>0?(a.s||0)/tA.s:0,shB=tB.s>0?(b.s||0)/tB.s:0;\n"
        "    var neto=shA>0&&a.nps!=null&&b.nps!=null?shA*(b.nps-a.nps):0;\n"
        "    var mix=b.nps!=null&&nB!=null?(shB-shA)*(b.nps-nB):0;\n"
        "    return{k:k,a:a,b:b,shB:shB,imp:Math.round((neto+mix)*100)/100};});\n"
        "  items.sort(function(x,y){return Math.abs(y.imp)-Math.abs(x.imp);});\n"
        "  var h='<div class=\"bk-wrap2\"><table class=\"bk-tbl2\"><colgroup>'\n"
        "        +'<col style=\"width:24%\"><col style=\"width:9%\"><col style=\"width:9%\">'\n"
        "        +'<col style=\"width:11%\"><col style=\"width:9%\"><col style=\"width:7%\">'\n"
        "        +'<col style=\"width:11%\"><col style=\"width:10%\"><col style=\"width:10%\"></colgroup>'\n"
        "        +'<thead><tr><th class=\"cn\">'+(lbl||'Dimensão')+'</th>'\n"
        "        +'<th>'+lA+'</th><th>'+lB+'</th><th>&#916;NPS</th>'\n"
        "        +'<th>Surveys</th><th>Share</th><th>Impacto</th><th>VS Target</th><th>Tend.</th>'\n"
        "        +'</tr></thead><tbody>';\n"
        "  var totI=0;\n"
        "  items.forEach(function(it){\n"
        "    var d2=it.a.nps!=null&&it.b.nps!=null?Math.round((it.b.nps-it.a.nps)*100)/100:null;\n"
        "    totI+=it.imp;\n"
        "    h+='<tr><td class=\"cn\">'+it.k+'</td>'\n"
        "      +'<td>'+_f1(it.a.nps)+'</td><td>'+_f1(it.b.nps)+'</td>'\n"
        "      +'<td>'+pill2(d2)+'</td>'\n"
        "      +'<td class=\"bk-sv2\">'+(it.b.s||0).toLocaleString('pt-BR')+'</td>'\n"
        "      +'<td class=\"bk-sv2\">'+(it.shB*100).toFixed(1)+'%</td>'\n"
        "      +'<td>'+pillImp2(it.imp)+'</td>'\n"
        "      +'<td>'+pillVT2(it.b.nps,tgt2)+'</td>'\n"
        "      +'<td>'+pillT2(d2)+'</td></tr>';});\n"
        "  totI=Math.round(totI*100)/100;\n"
        "  var dT=nA!=null&&nB!=null?Math.round((nB-nA)*100)/100:null;\n"
        "  h+='<tr class=\"bkt\"><td class=\"cn\">Total driver</td>'\n"
        "    +'<td>'+_f1(nA)+'</td><td>'+_f1(nB)+'</td>'\n"
        "    +'<td>'+pill2(dT)+'</td>'\n"
        "    +'<td class=\"bk-sv2\">'+(tB.s||0).toLocaleString('pt-BR')+'</td>'\n"
        "    +'<td class=\"bk-sv2\">100%</td>'\n"
        "    +'<td>'+pillImp2(totI)+'</td>'\n"
        "    +'<td>'+pillVT2(nB,tgt2)+'</td>'\n"
        "    +'<td>'+pillT2(dT)+'</td></tr>';\n"
        "  return h+'</tbody></table></div>';}\n"
        "function srTbl2(bk,pA,pB,tgt2){\n"
        "  var sr=(bk&&bk.Sr)||{};\n"
        "  var dA=sr[pA]||{},dB=sr[pB]||{};\n"
        "  var lA=_lbl2(pA),lB=_lbl2(pB);\n"
        "  function nS(v){return v!=null?v.toFixed(1)+'%':'—';}\n"
        "  function pG2(g){if(g==null)return'<span style=\"color:#888\">—</span>';\n"
        "    var ab=Math.abs(g),col=ab>10?'#b71c1c':ab>5?'#e65100':'#2e7d32';\n"
        "    return'<span style=\"font-weight:600;color:'+col+'\">'+(g>=0?'+':'')+g.toFixed(1)+'pp</span>';}\n"
        "  var rows=[{k:'&#127775; Expert',key:'Expert'},{k:'&#128164; Newbie',key:'Newbie'}];\n"
        "  var h='<div class=\"bk-wrap2\"><table class=\"bk-tbl2\"><colgroup>'\n"
        "        +'<col style=\"width:22%\"><col style=\"width:14%\"><col style=\"width:14%\">'\n"
        "        +'<col style=\"width:13%\"><col style=\"width:12%\"><col style=\"width:13%\"></colgroup>'\n"
        "        +'<thead><tr><th class=\"cn\">Senioridade</th><th>'+lA+'</th><th>'+lB+'</th>'\n"
        "        +'<th>&#916;NPS</th><th>Surveys</th><th>vs Target</th></tr></thead><tbody>';\n"
        "  var eNB=null,nNB=null;\n"
        "  rows.forEach(function(r){\n"
        "    var a=(dA[r.key]||{}),b=(dB[r.key]||{});\n"
        "    var nA2=a.nps,nB2=b.nps;\n"
        "    if(r.key==='Expert')eNB=nB2; else nNB=nB2;\n"
        "    var d2=nA2!=null&&nB2!=null?Math.round((nB2-nA2)*100)/100:null;\n"
        "    h+='<tr><td class=\"cn\">'+r.k+'</td>'\n"
        "      +'<td>'+nS(nA2)+'</td><td>'+nS(nB2)+'</td>'\n"
        "      +'<td>'+pill2(d2)+'</td>'\n"
        "      +'<td class=\"bk-sv2\">'+(b.s||0)+'</td>'\n"
        "      +'<td>'+pillVT2(nB2,tgt2)+'</td></tr>';});\n"
        "  var gap=eNB!=null&&nNB!=null?Math.round((eNB-nNB)*100)/100:null;\n"
        "  h+='<tr class=\"bkt\"><td class=\"cn\">Gap E−N ('+lB+')</td>'\n"
        "    +'<td colspan=\"2\" style=\"font-weight:600\">'+pG2(gap)+'</td><td colspan=\"3\"></td></tr>';\n"
        "  return h+'</tbody></table></div>';}\n"
        "function execBrief2(drv,pA,pB,bk){\n"
        "  var lA=_lbl2(pA),lB=_lbl2(pB),tgt2=TGT[drv];\n"
        "  var hist=HST[drv],histArr=pA==='M2'?hist.monthly:hist.weekly;\n"
        "  var nB2=histArr&&histArr.length>0?histArr[histArr.length-1].nps:null;\n"
        "  var nA2=histArr&&histArr.length>1?histArr[histArr.length-2].nps:null;\n"
        "  var delta=nA2!=null&&nB2!=null?Math.round((nB2-nA2)*100)/100:null;\n"
        "  var gapTgt=nB2!=null&&tgt2?Math.round((nB2-tgt2)*100)/100:null;\n"
        "  function kC(v){return v==null?'neutral':v>=0?'pos':'neg';}\n"
        "  var kpis='<div class=\"exec-brief-kpis\">'\n"
        "    +'<div class=\"exec-brief-kpi\"><div class=\"exec-brief-kpi-lbl\">NPS '+lB+'</div>'\n"
        "    +'<div class=\"exec-brief-kpi-val '+kC(gapTgt)+'\">'+(nB2!=null?nB2.toFixed(1)+'%':'—')+'</div></div>'\n"
        "    +'<div class=\"exec-brief-kpi\"><div class=\"exec-brief-kpi-lbl\">Var. '+(pA==='M2'?'MoM':'WoW')+'</div>'\n"
        "    +'<div class=\"exec-brief-kpi-val '+kC(delta)+'\">'+(delta!=null?(delta>=0?'+':'')+delta.toFixed(2)+' pp':'—')+'</div></div>'\n"
        "    +'<div class=\"exec-brief-kpi\"><div class=\"exec-brief-kpi-lbl\">Gap vs Target</div>'\n"
        "    +'<div class=\"exec-brief-kpi-val '+kC(gapTgt)+'\">'+(gapTgt!=null?(gapTgt>=0?'+':'')+gapTgt.toFixed(2)+' pp':'—')+'</div></div>'\n"
        "    +'</div>';\n"
        "  var pdP=(bk&&bk.P)||{};\n"
        "  var dPA=pdP[pA]||{},dPB=pdP[pB]||{};\n"
        "  var pKeys=Array.from(new Set(Object.keys(dPA).concat(Object.keys(dPB))));\n"
        "  var totSA=0,totSB=0,totPB=0,totDB=0;\n"
        "  pKeys.forEach(function(k){var a=dPA[k]||{s:0};var b=dPB[k]||{s:0,p:0,d:0};totSA+=a.s||0;totSB+=b.s||0;totPB+=b.p||0;totDB+=b.d||0;});\n"
        "  var npsAll=totSB>0?(totPB-totDB)/totSB*100:null;\n"
        "  var procs=pKeys.map(function(k){\n"
        "    var a=dPA[k]||{p:0,d:0,s:0,nps:null},b=dPB[k]||{p:0,d:0,s:0,nps:null};\n"
        "    var shA=totSA>0?(a.s||0)/totSA:0,shB=totSB>0?(b.s||0)/totSB:0;\n"
        "    var neto=shA>0&&a.nps!=null&&b.nps!=null?shA*(b.nps-a.nps):0;\n"
        "    var mix=b.nps!=null&&npsAll!=null?(shB-shA)*(b.nps-npsAll):0;\n"
        "    var imp=Math.round((neto+mix)*100)/100;\n"
        "    var gapT=tgt2!=null&&b.nps!=null?Math.round((b.nps-tgt2)*100)/100:null;\n"
        "    var dlt=a.nps!=null&&b.nps!=null?Math.round((b.nps-a.nps)*100)/100:null;\n"
        "    return{k:k,nA:a.nps,nB:b.nps,sB:b.s||0,imp:imp,gapT:gapT,dlt:dlt,shB:Math.round(shB*1000)/10};\n"
        "  }).filter(function(x){return x.sB>0||x.nB!=null;}).sort(function(a,b){return a.imp-b.imp;});\n"
        "  var top3neg=procs.filter(function(p){return p.imp<0;}).slice(0,3);\n"
        "  var top2pos=procs.filter(function(p){return p.imp>0;}).slice(-2).reverse();\n"
        "  var s1='<div class=\"exec-sec-title\" style=\"color:#1a73e8\">&#128201; Variação '+(pA==='M2'?'MoM':'WoW')+'</div>';\n"
        "  s1+='<p class=\"exec-narr\">NPS '+(delta!=null?(delta>=0?'subiu':'caiu')+' '+Math.abs(delta).toFixed(2)+'pp':'variou')\n"
        "      +' de '+(nA2!=null?nA2.toFixed(1)+'%':'—')+' ('+lA+') para '+(nB2!=null?nB2.toFixed(1)+'%':'—')+' ('+lB+')';\n"
        "  if(top3neg.length)s1+='. Pressiona: '+top3neg.map(function(p){return'<b>'+p.k.substring(0,28)+'</b> ('+_tag2(p.imp)+', NPS '+_f1(p.nB)+')';}).join('; ');\n"
        "  if(top2pos.length)s1+=' | Compensa: '+top2pos.map(function(p){return'<b>'+p.k.substring(0,22)+'</b> ('+_tag2(p.imp)+')';}).join(', ');\n"
        "  s1+='.</p>';\n"
        "  var s2='<div class=\"exec-sec-title\" style=\"color:#bf5c00\">&#127919; Análise vs Target</div>';\n"
        "  if(procs.length&&tgt2!=null){\n"
        "    var abT=procs.filter(function(p){return p.gapT!=null&&p.gapT<0;}).sort(function(a,b){return a.gapT-b.gapT;});\n"
        "    var acT=procs.filter(function(p){return p.gapT!=null&&p.gapT>=0;}).sort(function(a,b){return b.gapT-a.gapT;});\n"
        "    var gapStr=(gapTgt>=0?'+':'')+_f2(gapTgt)+'pp '+(gapTgt>=0?'acima':'abaixo');\n"
        "    var gapCl=gapTgt>=0?'#1a7a1a':'#c0321a';\n"
        "    s2+='<p class=\"exec-narr\">Driver <b style=\"color:'+gapCl+'\">'+gapStr+'</b> do target ('+tgt2.toFixed(1)+'%).';\n"
        "    if(abT.length)s2+=' Processos pressionando: '+abT.slice(0,3).map(function(p){return'<b>'+p.k.substring(0,26)+'</b> ('+p.gapT.toFixed(1)+'pp, NPS '+_f1(p.nB)+')';}).join('; ')+'.';\n"
        "    if(acT.length&&abT.length)s2+=' Positivos: '+acT.slice(0,2).map(function(p){return'<b>'+p.k.substring(0,20)+'</b> (+'+p.gapT.toFixed(1)+'pp)';}).join(', ')+'.';\n"
        "    if(abT.length===0)s2+=' Todos acima do target.';\n"
        "    s2+='</p>';\n"
        "  }else s2+='<p class=\"exec-narr exec-na\">Sem dados de processo.</p>';\n"
        "  var procsMix=pKeys.map(function(k){\n"
        "    var a=dPA[k]||{s:0,nps:null},b=dPB[k]||{s:0,nps:null};\n"
        "    var shA=totSA>0?(a.s||0)/totSA:0,shB=totSB>0?(b.s||0)/totSB:0;\n"
        "    var neto=shA>0&&a.nps!=null&&b.nps!=null?Math.round(shA*(b.nps-a.nps)*100)/100:0;\n"
        "    var mix=b.nps!=null&&npsAll!=null?Math.round((shB-shA)*(b.nps-npsAll)*100)/100:0;\n"
        "    return{k:k,neto:neto,mix:mix,dSha:Math.round((shB-shA)*1000)/10,nB:b.nps,sB:b.s||0,abvAvg:b.nps!=null&&npsAll!=null?b.nps>npsAll:null};\n"
        "  }).filter(function(x){return x.sB>0;});\n"
        "  var totN=Math.round(procsMix.reduce(function(s,p){return s+p.neto;},0)*100)/100;\n"
        "  var totM=Math.round(procsMix.reduce(function(s,p){return s+p.mix;},0)*100)/100;\n"
        "  var badMix=procsMix.filter(function(p){return p.dSha>0.5&&p.abvAvg===false&&p.mix<-0.05;}).sort(function(a,b){return a.mix-b.mix;}).slice(0,3);\n"
        "  var s3='<div class=\"exec-sec-title\" style=\"color:#546e7a\">&#128257; Mix de Pesquisas</div>';\n"
        "  s3+='<p class=\"exec-narr\">NETO (qualidade): <strong style=\"color:'+_clr2(totN)+'\">'+(totN>=0?'+':'')+totN.toFixed(2)+'pp</strong> &nbsp;|&nbsp; MIX (volume): <strong style=\"color:'+_clr2(totM)+'\">'+(totM>=0?'+':'')+totM.toFixed(2)+'pp</strong>.';\n"
        "  if(badMix.length)s3+=' Volume cresceu em processos abaixo da média: '+badMix.map(function(p){return'<b>'+p.k.substring(0,22)+'</b> (+'+p.dSha.toFixed(1)+'pp) → '+_tag2(p.mix);}).join('; ')+'.';\n"
        "  else s3+=' Sem redistribuição significativa de volume.';\n"
        "  s3+='</p>';\n"
        "  var srD=(bk&&bk.Sr)||{},srB2=srD[pB]||{},srA2=srD[pA]||{};\n"
        "  var expB2=srB2.Expert||{},nwbB2=srB2.Newbie||{};\n"
        "  var expA2=srA2.Expert||{},nwbA2=srA2.Newbie||{};\n"
        "  var eDlt=expA2.nps!=null&&expB2.nps!=null?Math.round((expB2.nps-expA2.nps)*100)/100:null;\n"
        "  var nDlt=nwbA2.nps!=null&&nwbB2.nps!=null?Math.round((nwbB2.nps-nwbA2.nps)*100)/100:null;\n"
        "  var gapE=expB2.nps!=null&&nwbB2.nps!=null?Math.round((expB2.nps-nwbB2.nps)*100)/100:null;\n"
        "  var s4='<div class=\"exec-sec-title\" style=\"color:#7b1fa2\">&#127891; Senioridade — Expert vs Newbie</div>';\n"
        "  if(expB2.nps!=null||nwbB2.nps!=null){\n"
        "    s4+='<p class=\"exec-narr\">&#127775; <b>Expert</b>: NPS '+(expB2.nps!=null?expB2.nps.toFixed(1)+'%':'—')\n"
        "       +(eDlt!=null?' ('+_tag2(eDlt,1)+' vs '+lA+')':'')\n"
        "       +' &bull; <span class=\"bk-sv2\">'+(expB2.s||0).toLocaleString('pt-BR')+' surveys</span></p>'\n"
        "      +'<p class=\"exec-narr\">&#128164; <b>Newbie</b>: NPS '+(nwbB2.nps!=null?nwbB2.nps.toFixed(1)+'%':'—')\n"
        "       +(nDlt!=null?' ('+_tag2(nDlt,1)+' vs '+lA+')':'')\n"
        "       +' &bull; <span class=\"bk-sv2\">'+(nwbB2.s||0).toLocaleString('pt-BR')+' surveys</span></p>'\n"
        "      +(gapE!=null?'<p class=\"exec-narr\">Gap E−N: <strong style=\"color:'+(Math.abs(gapE)>5?'#c0321a':'#1a7a1a')+'\">'+(gapE>=0?'+':'')+gapE.toFixed(1)+'pp</strong></p>':'');\n"
        "  }else s4+='<p class=\"exec-narr exec-na\">Sem dados de senioridade.</p>';\n"
        "  var isMes2=pA==='M2';\n"
        "  var sumObj=SUM[drv]||{};\n"
        "  var sumRaw=isMes2?(sumObj.mom||sumObj.wow):(sumObj.wow||sumObj.mom);\n"
        "  var bullets2=sumRaw?sumRaw.split('\\n').map(function(b){return b.replace(/^[\\s▶]+/,'').trim();}).filter(function(b){return b.length>10;}):[];\n"
        "  var s5='<div class=\"exec-sec-title fw\" style=\"color:#c0321a\">&#128139; Insights de Atendimento</div>';\n"
        "  if(bullets2.length){\n"
        "    s5+=bullets2.slice(0,6).map(function(b){\n"
        "      var ci=b.indexOf(':');\n"
        "      if(ci>0&&ci<50)b='<strong>'+b.substring(0,ci+1)+'</strong>'+b.substring(ci+1);\n"
        "      return'<div class=\"exec-bul\">&#9658; '+b+'</div>';}).join('');\n"
        "  }else s5+='<p class=\"exec-narr exec-na\">Análise qualitativa não disponível.</p>';\n"
        "  return'<div class=\"exec-brief\">'\n"
        "    +'<div class=\"exec-brief-hdr\">'\n"
        "      +'<div class=\"exec-brief-top\"><div><div class=\"exec-brief-drv\">Resumo Executivo — '+drv+'</div>'\n"
        "      +'<div class=\"exec-brief-per\">'+lA+' → '+lB+'</div></div>'\n"
        "      +kpis+'</div></div>'\n"
        "    +'<div class=\"exec-brief-body\">'\n"
        "      +'<div class=\"exec-sec\">'+s1+'</div>'\n"
        "      +'<div class=\"exec-sec\">'+s2+'</div>'\n"
        "      +'<div class=\"exec-sec\">'+s3+'</div>'\n"
        "      +'<div class=\"exec-sec\">'+s4+'</div>'\n"
        "      +'<div class=\"exec-sec fw\">'+s5+'</div>'\n"
        "    +'</div></div>';}\n"
        "function renderBkTbl2(el){\n"
        "  var drv=el.getAttribute('data-drv'),pA=el.getAttribute('data-pa'),pB=el.getAttribute('data-pb');\n"
        "  var tgt2=el.getAttribute('data-tgt');tgt2=tgt2?parseFloat(tgt2):null;\n"
        "  var proc=el.value,lsuf=el.getAttribute('data-lsuf');\n"
        "  var tblId='bk2-'+drv.replace(/ /g,'-');\n"
        "  var cont=document.getElementById(tblId);\n"
        "  if(!cont)return;\n"
        "  var bk=BK[drv],h='';\n"
        "  h+='<div class=\"dd-sec-title\">Processos — '+lsuf+'</div>';\n"
        "  h+=bkTbl2(bk,'P',pA,pB,tgt2,'Processo');\n"
        "  if(!proc){\n"
        "    h+='<div class=\"dd-sec-title\">Canal — '+lsuf+'</div>';\n"
        "    h+=bkTbl2(bk,'C',pA,pB,tgt2,'Canal');\n"
        "    h+='<div class=\"dd-sec-title\">Oficina — '+lsuf+'</div>';\n"
        "    h+=bkTbl2(bk,'O',pA,pB,tgt2,'Oficina');\n"
        "    h+='<div class=\"dd-sec-title\">Senioridade — '+lsuf+'</div>';\n"
        "    h+=srTbl2(bk,pA,pB,tgt2);\n"
        "  }else{\n"
        "    var pcA=(bk&&bk.P_C&&bk.P_C[pA]&&bk.P_C[pA][proc])||{};\n"
        "    var pcB=(bk&&bk.P_C&&bk.P_C[pB]&&bk.P_C[pB][proc])||{};\n"
        "    var poA=(bk&&bk.P_O&&bk.P_O[pA]&&bk.P_O[pA][proc])||{};\n"
        "    var poB=(bk&&bk.P_O&&bk.P_O[pB]&&bk.P_O[pB][proc])||{};\n"
        "    var mC={C:{}},mO={O:{}};\n"
        "    mC.C[pA]=pcA;mC.C[pB]=pcB;mO.O[pA]=poA;mO.O[pB]=poB;\n"
        "    h+='<div class=\"dd-sec-title\">Canal — '+proc+' ('+lsuf+')</div>';\n"
        "    h+=bkTbl2(mC,'C',pA,pB,tgt2,'Canal');\n"
        "    h+='<div class=\"dd-sec-title\">Oficina — '+proc+' ('+lsuf+')</div>';\n"
        "    h+=bkTbl2(mO,'O',pA,pB,tgt2,'Oficina');\n"
        "    var srPa=(bk&&bk.Sr_P&&bk.Sr_P[pA]&&bk.Sr_P[pA][proc])||{};\n"
        "    var srPb=(bk&&bk.Sr_P&&bk.Sr_P[pB]&&bk.Sr_P[pB][proc])||{};\n"
        "    var mSr={Sr:{}};mSr.Sr[pA]=srPa;mSr.Sr[pB]=srPb;\n"
        "    h+='<div class=\"dd-sec-title\">Senioridade — '+proc+' ('+lsuf+')</div>';\n"
        "    h+=srTbl2(mSr,pA,pB,tgt2);}\n"
        "  cont.innerHTML=h;}\n"
        "window.renderBkTbl2=renderBkTbl2;\n"
        "window.setDDPer2=function(btn,p){\n"
        "  _per=p;\n"
        "  document.querySelectorAll('.dd2-pbtn').forEach(function(b){b.classList.remove('active');});\n"
        "  btn.classList.add('active');\n"
        "  window.renderDDDrv2();};\n"
        "window.renderDDDrv2=function(){\n"
        "  var drv=document.getElementById('dd2-drv-sel').value;\n"
        "  var cont=document.getElementById('dd2-drv-cont');\n"
        "  if(!drv){cont.innerHTML='<div class=\"dd2-empty\">Selecione um driver acima para ver a análise detalhada</div>';return;}\n"
        "  var isW=_per==='w',pA=isW?'S2':'M2',pB=isW?'S1':'M1';\n"
        "  var bk=BK[drv],hist=HST[drv],tgt2=TGT[drv],color=COLORS[drv],short2=SHORT[drv];\n"
        "  var histArr=isW?hist.weekly:hist.monthly;\n"
        "  var cur=histArr[histArr.length-1],prev=histArr[histArr.length-2];\n"
        "  var nCur=cur?cur.nps:null,nPrev=prev?prev.nps:null;\n"
        "  var delta=nCur!=null&&nPrev!=null?+(nCur-nPrev).toFixed(2):null;\n"
        "  var gapTgt=nCur!=null&&tgt2?+(nCur-tgt2).toFixed(2):null;\n"
        "  var lA=_lbl2(pA),lB=_lbl2(pB);\n"
        "  var sc='<div class=\"dd2-sc-grid\">'\n"
        "    +sc2dd('NPS '+lB,nCur!=null?nCur.toFixed(1)+'%':'—',null,nCur,tgt2)\n"
        "    +sc2dd('NPS '+lA,nPrev!=null?nPrev.toFixed(1)+'%':'—',null,nPrev,tgt2)\n"
        "    +sc2dd(isW?'Var. WoW':'Var. MoM',delta!=null?(delta>=0?'+':'')+delta.toFixed(2)+' pp':'—',delta,null,null)\n"
        "    +sc2dd('Target',tgt2?tgt2.toFixed(1)+'%':'—',null,null,null)\n"
        "    +sc2dd('Gap vs Target',gapTgt!=null?(gapTgt>=0?'+':'')+gapTgt.toFixed(2)+' pp':'—',gapTgt,null,null)\n"
        "    +'</div>';\n"
        "  var brief=execBrief2(drv,pA,pB,bk);\n"
        "  var cid='ddc2_'+Date.now();\n"
        "  var hl=histArr.map(function(x){return x.label;}),hd=histArr.map(function(x){return x.nps;});\n"
        "  var clrs=hd.map(function(v){return tgt2&&v!=null&&v<tgt2?'rgba(210,45,45,0.82)':'rgba(30,65,150,0.82)';});\n"
        "  var chart='<div class=\"dd2-chart-sec\">'\n"
        "    +'<div class=\"dd2-chart-title\">Histórico '+(isW?'Semanal':'Mensal')+' — '+drv+'</div>'\n"
        "    +'<div class=\"dd2-chart-sub\">NPS vs target do driver</div>'\n"
        "    +'<div class=\"dd2-chart-wrap\"><canvas id=\"'+cid+'\"></canvas></div></div>';\n"
        "  var tblId='bk2-'+drv.replace(/ /g,'-');\n"
        "  var pKeys2=(BK[drv]&&BK[drv].P&&BK[drv].P[pB])?Object.keys(BK[drv].P[pB]).sort():[];\n"
        "  var fOpts='<option value=\"\">Todos os processos</option>'\n"
        "    +pKeys2.map(function(p){return'<option value=\"'+p.replace(/\"/g,'&quot;')+'\">'+p+'</option>';}).join('');\n"
        "  var lsuf2=(isW?lA+' vs '+lB:'MoM ('+lA+' vs '+lB+')');\n"
        "  var fb='<div class=\"dd2-fb\"><span>&#128269; Filtrar por processo:</span>'\n"
        "    +'<select class=\"dd2-fsel\" onchange=\"renderBkTbl2(this)\" data-drv=\"'+drv+'\" data-pa=\"'+pA+'\" data-pb=\"'+pB+'\" data-tgt=\"'+(tgt2||'')+'\" data-lsuf=\"'+lsuf2+'\">'\n"
        "    +fOpts+'</select></div>';\n"
        "  var initT='<div class=\"dd-sec-title\">Processos — '+lsuf2+'</div>'\n"
        "    +bkTbl2(BK[drv],'P',pA,pB,tgt2,'Processo')\n"
        "    +'<div class=\"dd-sec-title\">Canal — '+lsuf2+'</div>'\n"
        "    +bkTbl2(BK[drv],'C',pA,pB,tgt2,'Canal')\n"
        "    +'<div class=\"dd-sec-title\">Oficina — '+lsuf2+'</div>'\n"
        "    +bkTbl2(BK[drv],'O',pA,pB,tgt2,'Oficina')\n"
        "    +'<div class=\"dd-sec-title\">Senioridade — '+lsuf2+'</div>'\n"
        "    +srTbl2(BK[drv],pA,pB,tgt2);\n"
        "  cont.innerHTML=sc+brief+chart+fb+'<div id=\"'+tblId+'\">'+initT+'</div>';\n"
        "  Object.keys(_ch2).forEach(function(k){try{_ch2[k].destroy();}catch(e){}delete _ch2[k];});\n"
        "  var ctx=document.getElementById(cid);\n"
        "  if(ctx){\n"
        "    var allV=hd.filter(function(v){return v!=null;}).concat(tgt2?[tgt2]:[]);\n"
        "    var yMin=allV.length?Math.floor(Math.min.apply(null,allV))-5:0;\n"
        "    var yMax=allV.length?Math.ceil(Math.max.apply(null,allV))+5:100;\n"
        "    _ch2[cid]=new Chart(ctx,{type:'bar',plugins:[ChartDataLabels],\n"
        "      data:{labels:hl,datasets:[\n"
        "        {label:short2,data:hd,backgroundColor:clrs,borderWidth:0,borderRadius:3},\n"
        "        {type:'line',label:'Target',data:hl.map(function(){return tgt2;}),\n"
        "         borderColor:'rgba(191,92,0,0.9)',borderWidth:2,borderDash:[5,4],\n"
        "         pointRadius:0,fill:false,tension:0}]},\n"
        "      options:{responsive:true,maintainAspectRatio:false,animation:false,\n"
        "        plugins:{legend:{display:false},tooltip:{enabled:true},\n"
        "          datalabels:{display:function(ctx){return ctx.dataset.type!=='line';},\n"
        "            formatter:function(v){return v!=null?v.toFixed(1)+'%':'';},\n"
        "            anchor:'end',align:'top',font:{size:10,weight:'600'},color:'#333',padding:2}},\n"
        "        layout:{padding:{top:24}},\n"
        "        scales:{\n"
        "          y:{min:yMin,max:yMax,display:true,ticks:{callback:function(v){return v+'%';},font:{size:10}},grid:{color:'#f0f0f0'}},\n"
        "          x:{ticks:{font:{size:10},color:'#555'},grid:{display:false},border:{display:false}}}}});\n"
        "  }};\n"
        "})();\n"
        "</script>\n"
    )
    js = js_data + js_code
    tab_html = (
        f'<div id="tab-driver" class="tab-content">'
        f'<style>{css}</style>'
        f'<div class="section-title">Driver Deep Dive</div>'
        f'<div class="dd2-pbar">'
        f'<button class="dd2-pbtn active" onclick="setDDPer2(this,\'w\')">Semana Fechada (WoW)</button>'
        f'<button class="dd2-pbtn" onclick="setDDPer2(this,\'m\')">Mensal (MoM)</button>'
        f'</div>'
        f'<div class="dd2-bar"><label>Driver</label>'
        f'<select id="dd2-drv-sel" onchange="renderDDDrv2()">'
        f'<option value="">— Selecione um driver —</option>'
        f'{opts}</select></div>'
        f'<div id="dd2-drv-cont"><div class="dd2-empty">Selecione um driver acima para ver a análise detalhada</div></div>'
        f'</div>\n'
    )
    return tab_html + js
