# Semanas: S2=30/mar-05/abr  S1=06/abr-12/abr (atual, parcial até 10/abr)
# Meses:   M2=Março 2026     M1=Abril 2026 (parcial)
# Tuplas: (promoters, detractors, surveys)

weekly_driver = {
    "Experiencia Impositiva Seller Dev": {"S2":(66,25,100),   "S1":(118,31,164)},
    "ME Vendedor Seller Dev":            {"S2":(1016,158,1270),"S1":(1326,186,1690)},
    "PCF Vendedor Seller Dev":           {"S2":(84,23,125),    "S1":(69,21,98)},
    "Partners":                          {"S2":(448,77,574),   "S1":(328,57,427)},
    "Post Venta Seller Dev":             {"S2":(176,39,233),   "S1":(172,35,223)},
    "Publicaciones Seller Dev":          {"S2":(502,88,653),   "S1":(405,67,511)},
}
monthly_driver = {
    "Experiencia Impositiva Seller Dev": {"M2":(312,108,469),  "M1":(163,45,227)},
    "ME Vendedor Seller Dev":            {"M2":(4958,754,6266),"M1":(1940,274,2448)},
    "PCF Vendedor Seller Dev":           {"M2":(536,166,790),  "M1":(118,27,162)},
    "Partners":                          {"M2":(2228,337,2806),"M1":(593,98,765)},
    "Post Venta Seller Dev":             {"M2":(929,178,1186), "M1":(271,54,354)},
    "Publicaciones Seller Dev":          {"M2":(2639,374,3309),"M1":(712,119,911)},
}
weekly_proc = {
    "Experiencia Impositiva Seller Dev":{
        "S2":{"Datos fiscales":(5,3,9),"Emision de Nota Fiscal":(37,8,50),"Facturacion":(24,14,41)},
        "S1":{"Datos fiscales":(10,2,14),"Emision de Nota Fiscal":(75,21,105),"Facturacion":(33,8,45)},
    },
    "ME Vendedor Seller Dev":{
        "S2":{"Despacho VP":(340,102,476),"Gestiones Oper.":(98,12,124),"Reputacion ME":(444,14,478),"Reversa":(86,18,122),"Suspensiones ME":(2,0,2),"Viaje paquete Vend.":(46,12,68)},
        "S1":{"Despacho VP":(630,112,834),"Gestiones Oper.":(88,10,112),"Reputacion ME":(504,48,608),"Reversa":(72,8,90),"Viaje paquete Vend.":(32,8,46)},
    },
    "PCF Vendedor Seller Dev":{
        "S2":{"Post Compra Func. Vendedor":(84,23,125)},
        "S1":{"Post Compra Func. Vendedor":(69,21,98)},
    },
    "Partners":{
        "S2":{"Drivers":(357,66,466),"Places Kangu":(91,11,108)},
        "S1":{"Drivers":(224,41,299),"Places Kangu":(104,16,128)},
    },
    "Post Venta Seller Dev":{
        "S2":{"Anulacion de Venta":(6,2,8),"Reputacion":(170,37,225)},
        "S1":{"Anulacion de Venta":(8,2,11),"Reputacion":(164,33,212)},
    },
    "Publicaciones Seller Dev":{
        "S2":{"Afiliados ML":(225,39,293),"Antes de publicar":(45,4,56),"Calidad de foto":(7,1,9),"Denuncia usuario":(18,3,22),"Gestion Publicacion":(53,9,69),"PR - Art. prohibidos":(21,6,29),"PR - Datos Personales":(3,0,3),"PR - Prop. intelectual":(38,7,47),"PR - Tecnica prohibida":(59,9,76),"Potenciar Ventas":(33,10,49)},
        "S1":{"Afiliados ML":(193,22,233),"Antes de publicar":(29,3,37),"Calidad de foto":(4,2,6),"Denuncia usuario":(11,1,14),"Gestion Publicacion":(46,8,59),"PR - Art. prohibidos":(25,6,33),"PR - Datos Personales":(0,4,4),"PR - Prop. intelectual":(36,12,49),"PR - Tecnica prohibida":(36,3,40),"Potenciar Ventas":(25,6,36)},
    },
}
monthly_proc = {
    "Experiencia Impositiva Seller Dev":{
        "M2":{"Datos fiscales":(39,7,50),"Emision de Nota Fiscal":(129,26,177),"Facturacion":(144,75,242)},
        "M1":{"Datos fiscales":(12,5,19),"Emision de Nota Fiscal":(106,24,142),"Facturacion":(45,16,66)},
    },
    "ME Vendedor Seller Dev":{
        "M2":{"Despacho VP":(1520,360,2062),"Gestiones Oper.":(546,74,692),"Reputacion ME":(2080,148,2402),"Reversa":(468,128,668),"Suspensiones ME":(0,2,4),"Viaje paquete Vend.":(344,42,438)},
        "M1":{"Despacho VP":(852,174,1140),"Gestiones Oper.":(128,16,168),"Reputacion ME":(772,54,886),"Reversa":(124,16,160),"Suspensiones ME":(2,0,2),"Viaje paquete Vend.":(62,14,92)},
    },
    "PCF Vendedor Seller Dev":{
        "M2":{"Post Compra Func. Vendedor":(536,166,790)},
        "M1":{"Post Compra Func. Vendedor":(118,27,162)},
    },
    "Partners":{
        "M2":{"Drivers":(1797,278,2277),"Places Kangu":(431,59,529)},
        "M1":{"Drivers":(440,73,573),"Places Kangu":(153,25,192)},
    },
    "Post Venta Seller Dev":{
        "M2":{"Anulacion de Venta":(30,11,46),"Reputacion":(899,167,1140)},
        "M1":{"Anulacion de Venta":(12,3,16),"Reputacion":(259,51,338)},
    },
    "Publicaciones Seller Dev":{
        "M2":{"Afiliados ML":(1362,180,1687),"Antes de publicar":(219,19,267),"Calidad de foto":(43,2,47),"Denuncia usuario":(85,12,109),"Gestion Publicacion":(213,39,284),"PR - Art. prohibidos":(77,25,113),"PR - Datos Personales":(11,4,15),"PR - Prop. intelectual":(198,25,235),"PR - Tecnica prohibida":(235,25,286),"Potenciar Ventas":(196,43,265)},
        "M1":{"Afiliados ML":(343,47,429),"Antes de publicar":(47,4,60),"Calidad de foto":(6,3,10),"Denuncia usuario":(24,3,30),"Gestion Publicacion":(73,11,92),"PR - Art. prohibidos":(36,10,48),"PR - Datos Personales":(3,4,7),"PR - Prop. intelectual":(58,16,76),"PR - Tecnica prohibida":(75,9,90),"Potenciar Ventas":(47,12,69)},
    },
}

def nps(p,d,s): return round(100.0*(p-d)/s,2) if s>0 else 0.0

def mix_neto(data, pa, pb, surv_a_tot, surv_b_tot, nps_b_tot):
    out={}
    for drv,periods in data.items():
        a=periods.get(pa,(0,0,0)); b=periods.get(pb,(0,0,0))
        na=nps(*a); nb=nps(*b)
        sha=a[2]/surv_a_tot if surv_a_tot else 0
        shb=b[2]/surv_b_tot if surv_b_tot else 0
        nt=round(sha*(nb-na),2); mx=round((shb-sha)*(nb-nps_b_tot),2)
        out[drv]={"surv_a":a[2],"nps_a":na,"share_a":round(sha*100,1),
                  "surv_b":b[2],"nps_b":nb,"share_b":round(shb*100,1),
                  "neto":nt,"mix":mx,"var":round(nt+mx,2)}
    return out

def proc_var(proc_data, pa, pb, nps_b_drv, sa_tot, sb_tot):
    out={}
    all_p=set(proc_data.get(pa,{}))|set(proc_data.get(pb,{}))
    for proc in all_p:
        a=proc_data.get(pa,{}).get(proc,(0,0,0)); b=proc_data.get(pb,{}).get(proc,(0,0,0))
        na=nps(*a); nb=nps(*b)
        sha=a[2]/sa_tot if sa_tot else 0; shb=b[2]/sb_tot if sb_tot else 0
        nt=round(sha*(nb-na),2); mx=round((shb-sha)*(nb-nps_b_drv),2)
        out[proc]={"surv_a":a[2],"nps_a":na,"share_a":round(sha*100,1),
                   "surv_b":b[2],"nps_b":nb,"share_b":round(shb*100,1),
                   "neto":nt,"mix":mx,"var":round(nt+mx,2)}
    return out

# WEEKLY
sS2=sum(v["S2"][2] for v in weekly_driver.values())
sS1=sum(v["S1"][2] for v in weekly_driver.values())
pS2=sum(v["S2"][0] for v in weekly_driver.values()); dS2=sum(v["S2"][1] for v in weekly_driver.values())
pS1=sum(v["S1"][0] for v in weekly_driver.values()); dS1=sum(v["S1"][1] for v in weekly_driver.values())
nS2=nps(pS2,dS2,sS2); nS1=nps(pS1,dS1,sS1); dW=round(nS1-nS2,2)
print(f"WEEKLY: S2={nS2:.2f}  S1={nS1:.2f}  delta={dW:+.2f}  survS2={sS2} survS1={sS1}")

wD=mix_neto(weekly_driver,"S2","S1",sS2,sS1,nS1)
print("\n--- WEEKLY DRIVERS ---")
for d,v in sorted(wD.items(),key=lambda x:-abs(x[1]['var'])):
    print(f"  {d:<45} NPS_S2={v['nps_a']:6.2f} NPS_S1={v['nps_b']:6.2f} MIX={v['mix']:+.2f} NETO={v['neto']:+.2f} VAR={v['var']:+.2f}")
print(f"  SUM VAR = {sum(v['var'] for v in wD.values()):.4f}  (delta={dW})")

print("\n--- WEEKLY PROCESSES (top impact per driver) ---")
for drv in weekly_driver:
    s2p=weekly_proc[drv]["S2"]; s1p=weekly_proc[drv]["S1"]
    sa=sum(v[2] for v in s2p.values()); sb=sum(v[2] for v in s1p.values())
    pr=proc_var({"S2":s2p,"S1":s1p},"S2","S1",wD[drv]['nps_b'],sa,sb)
    top=sorted(pr.items(),key=lambda x:-abs(x[1]['var']))[:3]
    print(f"\n  [{drv}] drv_VAR={wD[drv]['var']:+.2f}")
    for p,v in top:
        print(f"    {p:<40} NPS_S2={v['nps_a']:6.2f} NPS_S1={v['nps_b']:6.2f} VAR={v['var']:+.2f}  surv_S1={v['surv_b']}")

# MONTHLY
sM2=sum(v["M2"][2] for v in monthly_driver.values())
sM1=sum(v["M1"][2] for v in monthly_driver.values())
pM2=sum(v["M2"][0] for v in monthly_driver.values()); dM2x=sum(v["M2"][1] for v in monthly_driver.values())
pM1=sum(v["M1"][0] for v in monthly_driver.values()); dM1x=sum(v["M1"][1] for v in monthly_driver.values())
nM2=nps(pM2,dM2x,sM2); nM1=nps(pM1,dM1x,sM1); dM=round(nM1-nM2,2)
print(f"\n\nMONTHLY: M2(Mar)={nM2:.2f}  M1(Abr)={nM1:.2f}  delta={dM:+.2f}  survM2={sM2} survM1={sM1}")

mD=mix_neto(monthly_driver,"M2","M1",sM2,sM1,nM1)
print("\n--- MONTHLY DRIVERS ---")
for d,v in sorted(mD.items(),key=lambda x:-abs(x[1]['var'])):
    print(f"  {d:<45} NPS_Mar={v['nps_a']:6.2f} NPS_Abr={v['nps_b']:6.2f} MIX={v['mix']:+.2f} NETO={v['neto']:+.2f} VAR={v['var']:+.2f}")
print(f"  SUM VAR = {sum(v['var'] for v in mD.values()):.4f}  (delta={dM})")

print("\n--- MONTHLY PROCESSES (top impact per driver) ---")
for drv in monthly_driver:
    m2p=monthly_proc[drv]["M2"]; m1p=monthly_proc[drv]["M1"]
    sa=sum(v[2] for v in m2p.values()); sb=sum(v[2] for v in m1p.values())
    pr=proc_var({"M2":m2p,"M1":m1p},"M2","M1",mD[drv]['nps_b'],sa,sb)
    top=sorted(pr.items(),key=lambda x:-abs(x[1]['var']))[:3]
    print(f"\n  [{drv}] drv_VAR={mD[drv]['var']:+.2f}")
    for p,v in top:
        print(f"    {p:<40} NPS_Mar={v['nps_a']:6.2f} NPS_Abr={v['nps_b']:6.2f} VAR={v['var']:+.2f}  surv_M1={v['surv_b']}")
