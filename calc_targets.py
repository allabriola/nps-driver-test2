import glob, openpyxl

f = glob.glob(r'C:/claudinho/*.xlsx')[0]
wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
ws = wb['Q226 Target por proceso']

def parse_tgt(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    s = str(v).strip().replace(',', '.').replace('%', '').replace(' ', '')
    try:
        n = float(s)
        return n / 100 if abs(n) > 1.5 else n
    except:
        return None

# Ler Excel: processo -> (num, den)
excel_proc = {}
rep_pv = {'n': 0, 'd': 0}   # Reputação Post Venta (BR_MLPostVenda)
rep_ot = {'n': 0, 'd': 0}   # Reputação outros

for row in ws.iter_rows(values_only=True):
    if row[0] != 'BR': continue
    proc   = str(row[2] or '').strip()
    equipo = str(row[7] or '').strip()
    enc    = row[16]
    tgt    = parse_tgt(row[22])
    if enc is None or tgt is None: continue
    try:
        enc_f = float(str(enc).replace('.', '').replace(',', '.'))
    except:
        continue
    if enc_f <= 0: continue

    if proc == 'Reputación':
        if 'PostVenda' in equipo or 'Postvenda' in equipo or 'PostVenda' in equipo:
            rep_pv['n'] += tgt * enc_f; rep_pv['d'] += enc_f
        else:
            rep_ot['n'] += tgt * enc_f; rep_ot['d'] += enc_f
        continue

    if proc not in excel_proc:
        excel_proc[proc] = {'n': 0, 'd': 0}
    excel_proc[proc]['n'] += tgt * enc_f
    excel_proc[proc]['d'] += enc_f

excel_proc['Reputacion_PV'] = rep_pv
excel_proc['Reputacion_OT'] = rep_ot

def proc_tgt(proc_name, is_post_venta=False):
    if proc_name == 'Reputacion_KEY':
        pass
    key = 'Reputacion_PV' if (proc_name == 'Reputación' and is_post_venta) else \
          ('Reputacion_OT' if proc_name == 'Reputación' else proc_name)
    d = excel_proc.get(key, {})
    if d.get('d', 0) > 0:
        return d['n'] / d['d']
    # fallback: tentar nome sem acento
    for k in excel_proc:
        if k.lower().replace('á','a').replace('ó','o').replace('é','e').replace('ú','u').replace('ñ','n') == \
           proc_name.lower().replace('á','a').replace('ó','o').replace('é','e').replace('ú','u').replace('ñ','n'):
            dd = excel_proc[k]
            if dd.get('d', 0) > 0:
                return dd['n'] / dd['d']
    return None

POST_VENTA_DRVS = {'Post Venta Mature', 'Post Venta Meli Pro', 'Post Venta Seller Dev'}

DRV_PROCS = {
    'CBT': [('CBT - Billing',3),('CBT - Boosters',6),('CBT - Dispatch, Sales and Listings',12),
            ('CBT - ME Reputation',100),('CBT - MP Withdrawals',45),('CBT - Moderations',14),
            ('CBT - My Account',35),('CBT - Operational Management',6),('CBT - Package journey',22),
            ('CBT - Publication Management',6),('CBT - Reputation',85),('CBT - Reverse',9)],
    'Experiencia Impositiva Mature':    [('Datos fiscales',2),('Emision de Nota Fiscal',24),('Facturacion',5)],
    'Experiencia Impositiva Meli Pro':  [('Emision de Nota Fiscal',4),('Facturacion',4)],
    'Experiencia Impositiva Seller Dev':[('Datos fiscales',36),('Emision de Nota Fiscal',254),('Facturacion',140)],
    'FBM-S Mature':    [('FBM - Devoluciones',3),('FBM - Funcionalidades',4),('FBM - Inventario',24),
                        ('FBM - Post Inbound',14),('FBM - Pre Inbound',37),('FBM - Retiro de Stock - Cx One',17)],
    'FBM-S Meli Pro':  [('FBM - Devoluciones',4),('FBM - Funcionalidades',2),('FBM - Inventario',13),
                        ('FBM - Post Inbound',2),('FBM - Pre Inbound',7),('FBM - Retiro de Stock - Cx One',4)],
    'FBM-S Seller Dev':[('FBM - Devoluciones',11),('FBM - Funcionalidades',18),('FBM - Inventario',59),
                        ('FBM - Post Inbound',59),('FBM - Pre Inbound',113),('FBM - Retiro de Stock - Cx One',29)],
    'ME Vendedor Mature':    [('Despacho Ventas y Publicaciones',266),('Gestiones Operativas',128),
                              ('Reputacion ME',402),('Reversa',138),('Viaje del paquete - Vendedor',52)],
    'ME Vendedor Meli Pro':  [('Despacho Ventas y Publicaciones',20),('Gestiones Operativas',11),
                              ('Reputacion ME',44),('Reversa',27),('Viaje del paquete - Vendedor',19)],
    'ME Vendedor Seller Dev':[('Despacho Ventas y Publicaciones',1972),('Gestiones Operativas',342),
                              ('Reputacion ME',1544),('Reversa',308),('Viaje del paquete - Vendedor',176)],
    'Otros CV': [('KYC Services',262),('Apelaciones retorno buyer XDDS',49),
                 ('Asignacion del contactanos Buyers Post',22),('Caja vacia - Flex',17),('KYC seg360',6)],
    'PCF Vendedor Mature':    [('Post Compra Funcionalidades Vendedor',260)],
    'PCF Vendedor Meli Pro':  [('Post Compra Funcionalidades Vendedor',109)],
    'PCF Vendedor Seller Dev':[('Post Compra Funcionalidades Vendedor',337)],
    'PDD DS&XD - Vendedor':  [('Arrepentimiento - DS',107),('Arrepentimiento - XD',131),
                               ('Defectuoso - DS',76),('Defectuoso - XD',99),
                               ('Diferente - DS',54),('Diferente - XD',102),
                               ('Incompleto - DS',38),('Incompleto - XD',57)],
    'PDD FBM - Vendedor':    [('Arrepentimiento - FBM',32),('Arrepentimiento - Super - FBM',8),
                               ('Defectuoso - FBM',58),('Diferente - FBM',25),('Incompleto - FBM',13)],
    'PDD Fotos - Vendedor':  [('PDD - Fotos',36)],
    'PDD MP,FLEX & CBT - Vendedor': [('Arrepentimiento - Flex',9),('Arrepentimiento - MP',21),
                                      ('Defectuoso - Flex',17),('Defectuoso - MP',12),
                                      ('Diferente - MP',6),('Incompleto - Flex',8)],
    'PNR ME - Vendedor': [('PNR - Contradictorio XD DS FBM',23),('PNR - Previo al despacho XD DS',65)],
    'PNR MP - Vendedor': [('PNR - MP',163)],
    'Partners':          [('Drivers',1311),('Places Kangu',339)],
    'Post Venta Mature':    [('Anulacion de Venta',6),('Reputacion',271)],
    'Post Venta Meli Pro':  [('Anulacion de Venta',1),('Reputacion',145)],
    'Post Venta Seller Dev':[('Anulacion de Venta',25),('Reputacion',640)],
    'Publicaciones Mature':    [('Antes de publicar',7),('Calidad de foto',9),('Denuncia de usuario',4),
                                ('Gestion de Publicacion',53),('PR - Articulos prohibidos',17),
                                ('PR - Datos Personales',5),('PR - Propiedad intelectual',32),
                                ('PR - Tecnica prohibida',51),('Potenciar Ventas',27)],
    'Publicaciones Meli Pro':  [('Antes de publicar',3),('Gestion de Publicacion',11),
                                ('PR - Propiedad intelectual',4),('PR - Tecnica prohibida',26),
                                ('Potenciar Ventas',8)],
    'Publicaciones Seller Dev':[('Afiliados ML',868),('Antes de publicar',129),('Calidad de foto',16),
                                ('Denuncia de usuario',50),('Gestion de Publicacion',170),
                                ('PR - Articulos prohibidos',83),('PR - Datos Personales',9),
                                ('PR - Propiedad intelectual',137),('PR - Tecnica prohibida',166),
                                ('Potenciar Ventas',128)],
}

print('=== Targets Q2 2026 Oficiais — 27 Drivers ===\n')
print(f'{"Driver":<40} {"Target":>8}   {"Surv Q1":>8}')
print('-' * 62)
total_n = total_d = 0
results = {}
for drv in sorted(DRV_PROCS.keys()):
    num = den = 0
    is_pv = drv in POST_VENTA_DRVS
    for (proc, surv) in DRV_PROCS[drv]:
        proc_key = 'Reputación' if proc.lower().replace('á','a').replace('ó','o') == 'reputacion' else proc
        t = proc_tgt(proc_key, is_pv)
        if t is not None:
            num += t * surv; den += surv
    tgt_drv = round(num / den * 100, 2) if den > 0 else None
    results[drv] = tgt_drv
    print(f'{drv:<40} {str(tgt_drv) + "%":>8}   {str(int(den)):>8}')
    if tgt_drv is not None:
        total_n += num; total_d += den

print('-' * 62)
print(f'{"CONSOLIDADO":<40} {round(total_n/total_d*100,2):.2f}%   {int(total_d):>8}')

print('\n\n=== Dicionário Python para colar nos scripts ===')
print('DRIVER_TARGETS = {')
for drv in sorted(results.keys()):
    t = results[drv]
    if t is not None:
        print(f'    "{drv}": {t},')
print('}')
print(f'NPS_TARGET = {round(total_n/total_d*100,2)}')
