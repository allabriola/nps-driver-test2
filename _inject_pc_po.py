#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injeta SECTION 2G (p_c_weekly/monthly) e 2H (p_o_weekly/monthly) em generate_html.py."""
import collections

def make_nested(rows):
    """rows = [(drv, proc, dim_val, p, d, s)]; returns {drv: {proc: {dim_val: (p,d,s)}}}"""
    d = {}
    for drv, proc, dim, p, de, s in rows:
        d.setdefault(drv, {}).setdefault(proc, {})[dim] = (int(p), int(de), int(s))
    return d

# ── P_C S1 ─────────────────────────────────────────────────────
PC_S1 = make_nested([
("Experiencia Impositiva Seller Dev","Datos fiscales","MULTICANAL C2C",1,1,2),
("Experiencia Impositiva Seller Dev","Datos fiscales","MULTICANAL CHAT",2,0,4),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","MULTICANAL C2C",10,4,16),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","MULTICANAL CHAT",19,1,22),
("Experiencia Impositiva Seller Dev","Facturación","MULTICANAL C2C",4,5,9),
("Experiencia Impositiva Seller Dev","Facturación","MULTICANAL CHAT",14,2,17),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MULTICANAL C2C",92,22,126),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MULTICANAL CHAT",446,50,548),
("ME Vendedor Seller Dev","Gestiones Operativas","MULTICANAL C2C",16,0,16),
("ME Vendedor Seller Dev","Gestiones Operativas","MULTICANAL CHAT",66,12,84),
("ME Vendedor Seller Dev","Reputación ME","MULTICANAL C2C",66,12,82),
("ME Vendedor Seller Dev","Reputación ME","MULTICANAL CHAT",352,14,396),
("ME Vendedor Seller Dev","Reversa","MULTICANAL C2C",12,10,24),
("ME Vendedor Seller Dev","Reversa","MULTICANAL CHAT",66,8,82),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","MULTICANAL C2C",10,0,14),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","MULTICANAL CHAT",40,6,48),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MULTICANAL C2C",22,14,41),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MULTICANAL CHAT",59,12,78),
("Partners","Drivers","MULTICANAL C2C",55,21,81),
("Partners","Drivers","MULTICANAL CHAT",420,69,543),
("Partners","Places Kangu","MULTICANAL C2C",13,3,19),
("Partners","Places Kangu","MULTICANAL CHAT",59,6,73),
("Post Venta Seller Dev","Anulación de Venta","MULTICANAL CHAT",3,0,3),
("Post Venta Seller Dev","Reputación","MULTICANAL C2C",41,4,48),
("Post Venta Seller Dev","Reputación","MULTICANAL CHAT",131,15,166),
("Publicaciones Seller Dev","Afiliados ML","MULTICANAL C2C",23,21,47),
("Publicaciones Seller Dev","Afiliados ML","MULTICANAL CHAT",166,14,199),
("Publicaciones Seller Dev","Antes de publicar","MULTICANAL C2C",5,1,6),
("Publicaciones Seller Dev","Antes de publicar","MULTICANAL CHAT",21,2,26),
("Publicaciones Seller Dev","Calidad de foto","MULTICANAL C2C",0,1,2),
("Publicaciones Seller Dev","Calidad de foto","MULTICANAL CHAT",12,2,15),
("Publicaciones Seller Dev","Denuncia de usuario","MULTICANAL C2C",4,2,6),
("Publicaciones Seller Dev","Denuncia de usuario","MULTICANAL CHAT",4,2,6),
("Publicaciones Seller Dev","Gestión de Publicación","MULTICANAL C2C",5,3,9),
("Publicaciones Seller Dev","Gestión de Publicación","MULTICANAL CHAT",29,7,40),
("Publicaciones Seller Dev","PR - Artículos prohibidos","MULTICANAL C2C",0,1,1),
("Publicaciones Seller Dev","PR - Artículos prohibidos","MULTICANAL CHAT",22,5,31),
("Publicaciones Seller Dev","PR - Datos Personales","MULTICANAL CHAT",5,1,7),
("Publicaciones Seller Dev","PR - Propiedad intelectual","MULTICANAL CHAT",27,10,40),
("Publicaciones Seller Dev","PR - Técnica prohibida","MULTICANAL C2C",4,2,7),
("Publicaciones Seller Dev","PR - Técnica prohibida","MULTICANAL CHAT",35,5,43),
("Publicaciones Seller Dev","Potenciar Ventas","MULTICANAL C2C",5,4,11),
("Publicaciones Seller Dev","Potenciar Ventas","MULTICANAL CHAT",14,4,20),
])

# ── P_C S2 ─────────────────────────────────────────────────────
PC_S2 = make_nested([
("Experiencia Impositiva Seller Dev","Datos fiscales","MULTICANAL C2C",2,0,2),
("Experiencia Impositiva Seller Dev","Datos fiscales","MULTICANAL CHAT",5,0,6),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","MULTICANAL C2C",7,10,18),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","MULTICANAL CHAT",24,4,31),
("Experiencia Impositiva Seller Dev","Facturación","MULTICANAL C2C",1,7,8),
("Experiencia Impositiva Seller Dev","Facturación","MULTICANAL CHAT",18,2,23),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MULTICANAL C2C",70,12,92),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MULTICANAL CHAT",332,68,446),
("ME Vendedor Seller Dev","Gestiones Operativas","MULTICANAL C2C",26,4,32),
("ME Vendedor Seller Dev","Gestiones Operativas","MULTICANAL CHAT",68,12,90),
("ME Vendedor Seller Dev","Reputación ME","MULTICANAL C2C",64,8,72),
("ME Vendedor Seller Dev","Reputación ME","MULTICANAL CHAT",376,18,412),
("ME Vendedor Seller Dev","Reversa","MULTICANAL C2C",12,4,16),
("ME Vendedor Seller Dev","Reversa","MULTICANAL CHAT",52,14,70),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","MULTICANAL C2C",10,2,12),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","MULTICANAL CHAT",48,10,66),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MULTICANAL C2C",30,18,50),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MULTICANAL CHAT",52,12,79),
("Partners","Drivers","MULTICANAL C2C",60,19,93),
("Partners","Drivers","MULTICANAL CHAT",428,57,532),
("Partners","Places Kangu","MULTICANAL C2C",7,1,9),
("Partners","Places Kangu","MULTICANAL CHAT",71,8,84),
("Post Venta Seller Dev","Anulación de Venta","MULTICANAL C2C",2,1,3),
("Post Venta Seller Dev","Anulación de Venta","MULTICANAL CHAT",4,1,5),
("Post Venta Seller Dev","Reputación","MULTICANAL C2C",30,8,40),
("Post Venta Seller Dev","Reputación","MULTICANAL CHAT",141,8,161),
("Publicaciones Seller Dev","Afiliados ML","MULTICANAL C2C",19,21,41),
("Publicaciones Seller Dev","Afiliados ML","MULTICANAL CHAT",146,11,173),
("Publicaciones Seller Dev","Antes de publicar","MULTICANAL C2C",6,1,8),
("Publicaciones Seller Dev","Antes de publicar","MULTICANAL CHAT",28,0,30),
("Publicaciones Seller Dev","Calidad de foto","MULTICANAL C2C",1,0,1),
("Publicaciones Seller Dev","Calidad de foto","MULTICANAL CHAT",5,0,5),
("Publicaciones Seller Dev","Denuncia de usuario","MULTICANAL C2C",3,1,4),
("Publicaciones Seller Dev","Denuncia de usuario","MULTICANAL CHAT",5,2,8),
("Publicaciones Seller Dev","Gestión de Publicación","MULTICANAL C2C",14,3,17),
("Publicaciones Seller Dev","Gestión de Publicación","MULTICANAL CHAT",32,5,45),
("Publicaciones Seller Dev","PR - Artículos prohibidos","MULTICANAL C2C",1,1,2),
("Publicaciones Seller Dev","PR - Artículos prohibidos","MULTICANAL CHAT",21,8,32),
("Publicaciones Seller Dev","PR - Datos Personales","MULTICANAL CHAT",6,0,6),
("Publicaciones Seller Dev","PR - Propiedad intelectual","MULTICANAL CHAT",38,4,44),
("Publicaciones Seller Dev","PR - Técnica prohibida","MULTICANAL C2C",5,2,7),
("Publicaciones Seller Dev","PR - Técnica prohibida","MULTICANAL CHAT",38,5,43),
("Publicaciones Seller Dev","Potenciar Ventas","MULTICANAL C2C",5,4,9),
("Publicaciones Seller Dev","Potenciar Ventas","MULTICANAL CHAT",24,8,36),
])

# ── P_C M1 ─────────────────────────────────────────────────────
PC_M1 = make_nested([
("Experiencia Impositiva Seller Dev","Datos fiscales","MULTICANAL C2C",1,1,2),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","MULTICANAL C2C",1,2,3),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","MULTICANAL CHAT",6,0,7),
("Experiencia Impositiva Seller Dev","Facturación","MULTICANAL C2C",1,2,3),
("Experiencia Impositiva Seller Dev","Facturación","MULTICANAL CHAT",1,1,2),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MULTICANAL C2C",30,6,36),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MULTICANAL CHAT",118,4,130),
("ME Vendedor Seller Dev","Gestiones Operativas","MULTICANAL CHAT",20,0,20),
("ME Vendedor Seller Dev","Reputación ME","MULTICANAL C2C",10,2,12),
("ME Vendedor Seller Dev","Reputación ME","MULTICANAL CHAT",60,4,70),
("ME Vendedor Seller Dev","Reversa","MULTICANAL C2C",0,4,4),
("ME Vendedor Seller Dev","Reversa","MULTICANAL CHAT",8,4,14),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","MULTICANAL CHAT",2,2,4),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MULTICANAL C2C",1,1,4),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MULTICANAL CHAT",9,0,12),
("Partners","Drivers","MULTICANAL C2C",23,4,29),
("Partners","Drivers","MULTICANAL CHAT",148,22,193),
("Partners","Places Kangu","MULTICANAL C2C",0,0,1),
("Partners","Places Kangu","MULTICANAL CHAT",14,0,15),
("Post Venta Seller Dev","Reputación","MULTICANAL C2C",3,1,5),
("Post Venta Seller Dev","Reputación","MULTICANAL CHAT",24,1,27),
("Publicaciones Seller Dev","Afiliados ML","MULTICANAL C2C",9,3,12),
("Publicaciones Seller Dev","Afiliados ML","MULTICANAL CHAT",77,5,89),
("Publicaciones Seller Dev","Antes de publicar","MULTICANAL C2C",0,1,1),
("Publicaciones Seller Dev","Antes de publicar","MULTICANAL CHAT",3,0,3),
("Publicaciones Seller Dev","Calidad de foto","MULTICANAL C2C",0,0,1),
("Publicaciones Seller Dev","Calidad de foto","MULTICANAL CHAT",11,1,13),
("Publicaciones Seller Dev","Denuncia de usuario","MULTICANAL C2C",1,1,2),
("Publicaciones Seller Dev","Denuncia de usuario","MULTICANAL CHAT",2,0,2),
("Publicaciones Seller Dev","Gestión de Publicación","MULTICANAL C2C",0,1,1),
("Publicaciones Seller Dev","Gestión de Publicación","MULTICANAL CHAT",10,1,11),
("Publicaciones Seller Dev","PR - Artículos prohibidos","MULTICANAL CHAT",8,1,12),
("Publicaciones Seller Dev","PR - Datos Personales","MULTICANAL CHAT",4,0,4),
("Publicaciones Seller Dev","PR - Propiedad intelectual","MULTICANAL CHAT",8,5,14),
("Publicaciones Seller Dev","PR - Técnica prohibida","MULTICANAL C2C",2,0,2),
("Publicaciones Seller Dev","PR - Técnica prohibida","MULTICANAL CHAT",7,2,10),
("Publicaciones Seller Dev","Potenciar Ventas","MULTICANAL C2C",1,2,3),
("Publicaciones Seller Dev","Potenciar Ventas","MULTICANAL CHAT",3,2,5),
])

# ── P_C M2 ─────────────────────────────────────────────────────
PC_M2 = make_nested([
("Experiencia Impositiva Seller Dev","Datos fiscales","MULTICANAL C2C",8,4,13),
("Experiencia Impositiva Seller Dev","Datos fiscales","MULTICANAL CHAT",28,3,35),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","MULTICANAL C2C",60,37,103),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","MULTICANAL CHAT",180,24,228),
("Experiencia Impositiva Seller Dev","Facturación","MULTICANAL C2C",23,25,50),
("Experiencia Impositiva Seller Dev","Facturación","MULTICANAL CHAT",105,18,141),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MULTICANAL C2C",370,110,532),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MULTICANAL CHAT",1894,308,2472),
("ME Vendedor Seller Dev","Gestiones Operativas","MULTICANAL C2C",98,22,126),
("ME Vendedor Seller Dev","Gestiones Operativas","MULTICANAL CHAT",312,52,412),
("ME Vendedor Seller Dev","Reputación ME","MULTICANAL C2C",356,46,422),
("ME Vendedor Seller Dev","Reputación ME","MULTICANAL CHAT",1784,88,2000),
("ME Vendedor Seller Dev","Reversa","MULTICANAL C2C",70,18,92),
("ME Vendedor Seller Dev","Reversa","MULTICANAL CHAT",294,54,388),
("ME Vendedor Seller Dev","Suspensiones ME","MULTICANAL C2C",2,0,2),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","MULTICANAL C2C",44,8,68),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","MULTICANAL CHAT",184,32,244),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MULTICANAL C2C",112,51,172),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MULTICANAL CHAT",280,66,393),
("Partners","Drivers","MULTICANAL C2C",222,65,328),
("Partners","Drivers","MULTICANAL CHAT",1592,236,2004),
("Partners","Places Kangu","MULTICANAL C2C",55,13,72),
("Partners","Places Kangu","MULTICANAL CHAT",355,45,436),
("Post Venta Seller Dev","Anulación de Venta","MULTICANAL C2C",6,2,9),
("Post Venta Seller Dev","Anulación de Venta","MULTICANAL CHAT",24,3,27),
("Post Venta Seller Dev","Reputación","MULTICANAL C2C",193,33,242),
("Post Venta Seller Dev","Reputación","MULTICANAL CHAT",633,78,780),
("Publicaciones Seller Dev","Afiliados ML","MULTICANAL C2C",87,79,182),
("Publicaciones Seller Dev","Afiliados ML","MULTICANAL CHAT",872,87,1045),
("Publicaciones Seller Dev","Antes de publicar","MULTICANAL C2C",28,4,35),
("Publicaciones Seller Dev","Antes de publicar","MULTICANAL CHAT",134,9,159),
("Publicaciones Seller Dev","Calidad de foto","MULTICANAL C2C",1,1,2),
("Publicaciones Seller Dev","Calidad de foto","MULTICANAL CHAT",17,4,23),
("Publicaciones Seller Dev","Denuncia de usuario","MULTICANAL C2C",15,5,21),
("Publicaciones Seller Dev","Denuncia de usuario","MULTICANAL CHAT",38,7,49),
("Publicaciones Seller Dev","Gestión de Publicación","MULTICANAL C2C",34,17,53),
("Publicaciones Seller Dev","Gestión de Publicación","MULTICANAL CHAT",162,24,216),
("Publicaciones Seller Dev","PR - Artículos prohibidos","MULTICANAL C2C",7,4,11),
("Publicaciones Seller Dev","PR - Artículos prohibidos","MULTICANAL CHAT",91,27,125),
("Publicaciones Seller Dev","PR - Datos Personales","MULTICANAL CHAT",11,6,18),
("Publicaciones Seller Dev","PR - Propiedad intelectual","MULTICANAL C2C",4,2,6),
("Publicaciones Seller Dev","PR - Propiedad intelectual","MULTICANAL CHAT",160,29,201),
("Publicaciones Seller Dev","PR - Técnica prohibida","MULTICANAL C2C",14,6,21),
("Publicaciones Seller Dev","PR - Técnica prohibida","MULTICANAL CHAT",189,22,233),
("Publicaciones Seller Dev","Potenciar Ventas","MULTICANAL C2C",23,12,41),
("Publicaciones Seller Dev","Potenciar Ventas","MULTICANAL CHAT",112,27,155),
])

# ── P_O S1 ─────────────────────────────────────────────────────
PO_S1 = make_nested([
("Experiencia Impositiva Seller Dev","Datos fiscales","AEC",2,0,4),
("Experiencia Impositiva Seller Dev","Datos fiscales","KTA_BRASIL",1,1,2),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","AEC",19,1,22),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","CTX",2,1,3),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","KTA_BRASIL",8,3,13),
("Experiencia Impositiva Seller Dev","Facturación","AEC",14,2,17),
("Experiencia Impositiva Seller Dev","Facturación","CTX",0,1,1),
("Experiencia Impositiva Seller Dev","Facturación","KTA_BRASIL",4,4,8),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","AEC",26,8,38),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","ATE",288,34,352),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","CTX",54,6,62),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","KTA_BRASIL",168,24,220),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MELICIDADE",2,0,2),
("ME Vendedor Seller Dev","Gestiones Operativas","AEC",2,0,2),
("ME Vendedor Seller Dev","Gestiones Operativas","ATE",54,0,56),
("ME Vendedor Seller Dev","Gestiones Operativas","CTX",10,4,16),
("ME Vendedor Seller Dev","Gestiones Operativas","KTA_BRASIL",16,8,26),
("ME Vendedor Seller Dev","Reputación ME","AEC",184,6,200),
("ME Vendedor Seller Dev","Reputación ME","ATE",86,8,102),
("ME Vendedor Seller Dev","Reputación ME","CTX",12,0,14),
("ME Vendedor Seller Dev","Reputación ME","KTA_BRASIL",136,12,162),
("ME Vendedor Seller Dev","Reversa","AEC",8,6,16),
("ME Vendedor Seller Dev","Reversa","ATE",38,8,48),
("ME Vendedor Seller Dev","Reversa","KTA_BRASIL",32,4,42),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","AEC",2,0,4),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","ATE",22,4,28),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","CTX",4,0,4),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","KTA_BRASIL",22,2,26),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","AEC",30,10,43),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","ATE",21,6,31),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","CTX",5,4,9),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","KTA_BRASIL",22,6,33),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MELICIDADE",3,0,3),
("Partners","Drivers","AEC",16,7,24),
("Partners","Drivers","ATE",228,35,287),
("Partners","Drivers","CTX",34,8,51),
("Partners","Drivers","KTA_BRASIL",197,40,262),
("Partners","Places Kangu","AEC",4,1,6),
("Partners","Places Kangu","ATE",35,3,42),
("Partners","Places Kangu","CTX",5,4,11),
("Partners","Places Kangu","KTA_BRASIL",28,1,33),
("Post Venta Seller Dev","Anulación de Venta","AEC",2,0,2),
("Post Venta Seller Dev","Anulación de Venta","KTA_BRASIL",1,0,1),
("Post Venta Seller Dev","Reputación","AEC",70,9,85),
("Post Venta Seller Dev","Reputación","ATE",29,4,41),
("Post Venta Seller Dev","Reputación","CTX",8,0,8),
("Post Venta Seller Dev","Reputación","KTA_BRASIL",65,6,80),
("Publicaciones Seller Dev","Afiliados ML","AEC",166,14,199),
("Publicaciones Seller Dev","Afiliados ML","CTX",3,1,5),
("Publicaciones Seller Dev","Afiliados ML","KTA_BRASIL",20,20,42),
("Publicaciones Seller Dev","Antes de publicar","AEC",6,2,8),
("Publicaciones Seller Dev","Antes de publicar","CTX",2,0,2),
("Publicaciones Seller Dev","Antes de publicar","KTA_BRASIL",18,1,22),
("Publicaciones Seller Dev","Calidad de foto","AEC",3,1,5),
("Publicaciones Seller Dev","Calidad de foto","KTA_BRASIL",9,2,12),
("Publicaciones Seller Dev","Denuncia de usuario","AEC",4,2,6),
("Publicaciones Seller Dev","Denuncia de usuario","CTX",0,1,1),
("Publicaciones Seller Dev","Denuncia de usuario","KTA_BRASIL",4,1,5),
("Publicaciones Seller Dev","Gestión de Publicación","AEC",11,3,16),
("Publicaciones Seller Dev","Gestión de Publicación","CTX",3,0,3),
("Publicaciones Seller Dev","Gestión de Publicación","KTA_BRASIL",20,7,30),
("Publicaciones Seller Dev","PR - Artículos prohibidos","AEC",4,3,9),
("Publicaciones Seller Dev","PR - Artículos prohibidos","KTA_BRASIL",18,3,23),
("Publicaciones Seller Dev","PR - Datos Personales","AEC",0,1,1),
("Publicaciones Seller Dev","PR - Datos Personales","KTA_BRASIL",5,0,6),
("Publicaciones Seller Dev","PR - Propiedad intelectual","AEC",10,3,13),
("Publicaciones Seller Dev","PR - Propiedad intelectual","KTA_BRASIL",17,7,27),
("Publicaciones Seller Dev","PR - Técnica prohibida","AEC",21,3,24),
("Publicaciones Seller Dev","PR - Técnica prohibida","ATE",0,0,1),
("Publicaciones Seller Dev","PR - Técnica prohibida","KTA_BRASIL",18,4,25),
("Publicaciones Seller Dev","Potenciar Ventas","AEC",5,6,12),
("Publicaciones Seller Dev","Potenciar Ventas","CTX",2,1,4),
("Publicaciones Seller Dev","Potenciar Ventas","KTA_BRASIL",11,1,14),
("Publicaciones Seller Dev","Potenciar Ventas","MELICIDADE",1,0,1),
])

# ── P_O S2 ─────────────────────────────────────────────────────
PO_S2 = make_nested([
("Experiencia Impositiva Seller Dev","Datos fiscales","AEC",5,0,6),
("Experiencia Impositiva Seller Dev","Datos fiscales","CTX",1,0,1),
("Experiencia Impositiva Seller Dev","Datos fiscales","KTA_BRASIL",1,0,1),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","AEC",24,4,31),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","CTX",4,3,7),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","KTA_BRASIL",3,7,11),
("Experiencia Impositiva Seller Dev","Facturación","AEC",18,2,23),
("Experiencia Impositiva Seller Dev","Facturación","KTA_BRASIL",1,7,8),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","AEC",24,4,30),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","ATE",188,34,248),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","CTX",50,12,72),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","KTA_BRASIL",140,30,188),
("ME Vendedor Seller Dev","Gestiones Operativas","AEC",14,0,16),
("ME Vendedor Seller Dev","Gestiones Operativas","ATE",48,8,64),
("ME Vendedor Seller Dev","Gestiones Operativas","CTX",8,2,10),
("ME Vendedor Seller Dev","Gestiones Operativas","KTA_BRASIL",24,6,32),
("ME Vendedor Seller Dev","Reputación ME","AEC",196,8,214),
("ME Vendedor Seller Dev","Reputación ME","ATE",84,6,92),
("ME Vendedor Seller Dev","Reputación ME","CTX",26,4,32),
("ME Vendedor Seller Dev","Reputación ME","KTA_BRASIL",134,8,146),
("ME Vendedor Seller Dev","Reversa","AEC",6,2,8),
("ME Vendedor Seller Dev","Reversa","ATE",26,6,34),
("ME Vendedor Seller Dev","Reversa","KTA_BRASIL",30,10,42),
("ME Vendedor Seller Dev","Reversa","MELICIDADE",2,0,2),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","AEC",8,2,10),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","ATE",28,10,40),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","CTX",4,0,4),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","KTA_BRASIL",18,0,24),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","AEC",14,5,25),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","ATE",33,10,46),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","CTX",5,3,10),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","KTA_BRASIL",28,11,45),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MELICIDADE",2,1,3),
("Partners","Drivers","AEC",23,7,35),
("Partners","Drivers","ATE",240,29,290),
("Partners","Drivers","CTX",35,8,49),
("Partners","Drivers","KTA_BRASIL",190,32,251),
("Partners","Places Kangu","AEC",2,0,2),
("Partners","Places Kangu","ATE",46,4,54),
("Partners","Places Kangu","CTX",7,1,9),
("Partners","Places Kangu","KTA_BRASIL",23,4,28),
("Post Venta Seller Dev","Anulación de Venta","AEC",1,1,2),
("Post Venta Seller Dev","Anulación de Venta","ATE",1,0,1),
("Post Venta Seller Dev","Anulación de Venta","KTA_BRASIL",4,1,5),
("Post Venta Seller Dev","Reputación","AEC",71,7,81),
("Post Venta Seller Dev","Reputación","ATE",33,3,39),
("Post Venta Seller Dev","Reputación","CTX",6,2,9),
("Post Venta Seller Dev","Reputación","KTA_BRASIL",61,4,72),
("Publicaciones Seller Dev","Afiliados ML","AEC",146,11,173),
("Publicaciones Seller Dev","Afiliados ML","CTX",6,3,9),
("Publicaciones Seller Dev","Afiliados ML","KTA_BRASIL",13,18,32),
("Publicaciones Seller Dev","Antes de publicar","AEC",15,1,17),
("Publicaciones Seller Dev","Antes de publicar","CTX",4,0,5),
("Publicaciones Seller Dev","Antes de publicar","KTA_BRASIL",15,0,16),
("Publicaciones Seller Dev","Calidad de foto","AEC",1,0,1),
("Publicaciones Seller Dev","Calidad de foto","KTA_BRASIL",5,0,5),
("Publicaciones Seller Dev","Denuncia de usuario","AEC",5,2,8),
("Publicaciones Seller Dev","Denuncia de usuario","CTX",3,0,3),
("Publicaciones Seller Dev","Denuncia de usuario","KTA_BRASIL",0,1,1),
("Publicaciones Seller Dev","Gestión de Publicación","AEC",24,3,30),
("Publicaciones Seller Dev","Gestión de Publicación","CTX",6,1,7),
("Publicaciones Seller Dev","Gestión de Publicación","KTA_BRASIL",16,4,25),
("Publicaciones Seller Dev","PR - Artículos prohibidos","AEC",7,5,12),
("Publicaciones Seller Dev","PR - Artículos prohibidos","KTA_BRASIL",15,4,22),
("Publicaciones Seller Dev","PR - Datos Personales","AEC",1,0,1),
("Publicaciones Seller Dev","PR - Datos Personales","KTA_BRASIL",5,0,5),
("Publicaciones Seller Dev","PR - Propiedad intelectual","AEC",22,0,22),
("Publicaciones Seller Dev","PR - Propiedad intelectual","KTA_BRASIL",16,4,22),
("Publicaciones Seller Dev","PR - Técnica prohibida","AEC",16,6,22),
("Publicaciones Seller Dev","PR - Técnica prohibida","KTA_BRASIL",27,1,28),
("Publicaciones Seller Dev","Potenciar Ventas","AEC",8,6,15),
("Publicaciones Seller Dev","Potenciar Ventas","CTX",4,2,6),
("Publicaciones Seller Dev","Potenciar Ventas","KTA_BRASIL",17,4,24),
])

# ── P_O M1 ─────────────────────────────────────────────────────
PO_M1 = make_nested([
("Experiencia Impositiva Seller Dev","Datos fiscales","KTA_BRASIL",1,1,2),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","AEC",6,0,7),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","KTA_BRASIL",1,2,3),
("Experiencia Impositiva Seller Dev","Facturación","AEC",1,1,2),
("Experiencia Impositiva Seller Dev","Facturación","KTA_BRASIL",1,2,3),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","AEC",4,2,6),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","ATE",86,6,96),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","KTA_BRASIL",58,2,64),
("ME Vendedor Seller Dev","Gestiones Operativas","ATE",16,0,16),
("ME Vendedor Seller Dev","Gestiones Operativas","KTA_BRASIL",4,0,4),
("ME Vendedor Seller Dev","Reputación ME","AEC",18,2,24),
("ME Vendedor Seller Dev","Reputación ME","ATE",26,0,26),
("ME Vendedor Seller Dev","Reputación ME","KTA_BRASIL",26,4,32),
("ME Vendedor Seller Dev","Reversa","ATE",2,6,8),
("ME Vendedor Seller Dev","Reversa","KTA_BRASIL",6,2,10),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","ATE",2,2,4),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","AEC",4,0,5),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","ATE",2,1,4),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","KTA_BRASIL",4,0,7),
("Partners","Drivers","AEC",8,1,10),
("Partners","Drivers","ATE",93,8,112),
("Partners","Drivers","KTA_BRASIL",70,17,100),
("Partners","Places Kangu","ATE",7,0,8),
("Partners","Places Kangu","KTA_BRASIL",7,0,8),
("Post Venta Seller Dev","Reputación","AEC",8,1,9),
("Post Venta Seller Dev","Reputación","ATE",8,1,10),
("Post Venta Seller Dev","Reputación","KTA_BRASIL",11,0,13),
("Publicaciones Seller Dev","Afiliados ML","AEC",77,5,89),
("Publicaciones Seller Dev","Afiliados ML","KTA_BRASIL",9,3,12),
("Publicaciones Seller Dev","Antes de publicar","AEC",0,1,1),
("Publicaciones Seller Dev","Antes de publicar","KTA_BRASIL",3,0,3),
("Publicaciones Seller Dev","Calidad de foto","AEC",3,0,4),
("Publicaciones Seller Dev","Calidad de foto","KTA_BRASIL",8,1,10),
("Publicaciones Seller Dev","Denuncia de usuario","AEC",2,0,2),
("Publicaciones Seller Dev","Denuncia de usuario","KTA_BRASIL",1,1,2),
("Publicaciones Seller Dev","Gestión de Publicación","AEC",6,1,7),
("Publicaciones Seller Dev","Gestión de Publicación","KTA_BRASIL",4,1,5),
("Publicaciones Seller Dev","PR - Artículos prohibidos","AEC",1,0,2),
("Publicaciones Seller Dev","PR - Artículos prohibidos","KTA_BRASIL",7,1,10),
("Publicaciones Seller Dev","PR - Datos Personales","KTA_BRASIL",4,0,4),
("Publicaciones Seller Dev","PR - Propiedad intelectual","AEC",3,1,4),
("Publicaciones Seller Dev","PR - Propiedad intelectual","KTA_BRASIL",5,4,10),
("Publicaciones Seller Dev","PR - Técnica prohibida","AEC",5,0,5),
("Publicaciones Seller Dev","PR - Técnica prohibida","KTA_BRASIL",4,2,7),
("Publicaciones Seller Dev","Potenciar Ventas","AEC",2,3,5),
("Publicaciones Seller Dev","Potenciar Ventas","KTA_BRASIL",2,1,3),
])

# ── P_O M2 ─────────────────────────────────────────────────────
PO_M2 = make_nested([
("Experiencia Impositiva Seller Dev","Datos fiscales","AEC",28,3,35),
("Experiencia Impositiva Seller Dev","Datos fiscales","CTX",4,1,5),
("Experiencia Impositiva Seller Dev","Datos fiscales","KTA_BRASIL",4,3,8),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","AEC",180,23,227),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","CTX",29,9,39),
("Experiencia Impositiva Seller Dev","Emision de Nota Fiscal","KTA_BRASIL",31,29,65),
("Experiencia Impositiva Seller Dev","Facturación","AEC",105,18,141),
("Experiencia Impositiva Seller Dev","Facturación","CTX",9,3,12),
("Experiencia Impositiva Seller Dev","Facturación","KTA_BRASIL",14,22,38),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","AEC",146,36,196),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","ATE",1214,212,1618),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","CTX",302,56,386),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","KTA_BRASIL",598,116,804),
("ME Vendedor Seller Dev","Despacho Ventas y Publicaciones","MELICIDADE",6,0,6),
("ME Vendedor Seller Dev","Gestiones Operativas","AEC",34,8,46),
("ME Vendedor Seller Dev","Gestiones Operativas","ATE",244,32,306),
("ME Vendedor Seller Dev","Gestiones Operativas","CTX",54,12,74),
("ME Vendedor Seller Dev","Gestiones Operativas","KTA_BRASIL",80,22,114),
("ME Vendedor Seller Dev","Gestiones Operativas","MELICIDADE",2,0,2),
("ME Vendedor Seller Dev","Reputación ME","AEC",996,28,1084),
("ME Vendedor Seller Dev","Reputación ME","ATE",426,30,490),
("ME Vendedor Seller Dev","Reputación ME","CTX",134,10,160),
("ME Vendedor Seller Dev","Reputación ME","KTA_BRASIL",584,64,686),
("ME Vendedor Seller Dev","Reputación ME","MELICIDADE",2,2,4),
("ME Vendedor Seller Dev","Reversa","AEC",34,10,46),
("ME Vendedor Seller Dev","Reversa","ATE",178,30,222),
("ME Vendedor Seller Dev","Reversa","KTA_BRASIL",152,32,212),
("ME Vendedor Seller Dev","Reversa","MELICIDADE",2,0,2),
("ME Vendedor Seller Dev","Suspensiones ME","ATE",2,0,2),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","AEC",24,4,32),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","ATE",120,26,170),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","CTX",24,0,24),
("ME Vendedor Seller Dev","Viaje del paquete - Vendedor","KTA_BRASIL",60,10,86),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","AEC",93,35,144),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","ATE",166,37,225),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","CTX",28,13,44),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","KTA_BRASIL",79,28,118),
("PCF Vendedor Seller Dev","Post Compra Funcionalidades Vendedor","MELICIDADE",28,5,37),
("Partners","Drivers","AEC",74,23,110),
("Partners","Drivers","ATE",987,137,1223),
("Partners","Drivers","CTX",180,36,241),
("Partners","Drivers","KTA_BRASIL",577,105,763),
("Partners","Places Kangu","AEC",21,3,25),
("Partners","Places Kangu","ATE",215,27,262),
("Partners","Places Kangu","CTX",64,9,81),
("Partners","Places Kangu","KTA_BRASIL",110,19,140),
("Post Venta Seller Dev","Anulación de Venta","AEC",16,2,18),
("Post Venta Seller Dev","Anulación de Venta","ATE",6,1,7),
("Post Venta Seller Dev","Anulación de Venta","CTX",3,0,4),
("Post Venta Seller Dev","Anulación de Venta","KTA_BRASIL",5,2,7),
("Post Venta Seller Dev","Reputación","AEC",310,46,382),
("Post Venta Seller Dev","Reputación","ATE",177,17,220),
("Post Venta Seller Dev","Reputación","CTX",70,12,90),
("Post Venta Seller Dev","Reputación","KTA_BRASIL",265,36,326),
("Post Venta Seller Dev","Reputación","MELICIDADE",5,0,5),
("Publicaciones Seller Dev","Afiliados ML","AEC",871,87,1044),
("Publicaciones Seller Dev","Afiliados ML","CTX",30,11,44),
("Publicaciones Seller Dev","Afiliados ML","KTA_BRASIL",57,68,138),
("Publicaciones Seller Dev","Afiliados ML","MELICIDADE",1,0,1),
("Publicaciones Seller Dev","Antes de publicar","AEC",70,5,84),
("Publicaciones Seller Dev","Antes de publicar","CTX",17,2,21),
("Publicaciones Seller Dev","Antes de publicar","KTA_BRASIL",75,6,89),
("Publicaciones Seller Dev","Calidad de foto","AEC",3,2,7),
("Publicaciones Seller Dev","Calidad de foto","KTA_BRASIL",15,3,18),
("Publicaciones Seller Dev","Denuncia de usuario","AEC",38,7,49),
("Publicaciones Seller Dev","Denuncia de usuario","CTX",7,2,10),
("Publicaciones Seller Dev","Denuncia de usuario","KTA_BRASIL",8,3,11),
("Publicaciones Seller Dev","Gestión de Publicación","AEC",62,18,88),
("Publicaciones Seller Dev","Gestión de Publicación","CTX",23,8,31),
("Publicaciones Seller Dev","Gestión de Publicación","KTA_BRASIL",111,15,150),
("Publicaciones Seller Dev","PR - Artículos prohibidos","AEC",31,15,48),
("Publicaciones Seller Dev","PR - Artículos prohibidos","CTX",1,0,1),
("Publicaciones Seller Dev","PR - Artículos prohibidos","KTA_BRASIL",66,16,87),
("Publicaciones Seller Dev","PR - Datos Personales","AEC",3,1,4),
("Publicaciones Seller Dev","PR - Datos Personales","KTA_BRASIL",8,5,14),
("Publicaciones Seller Dev","PR - Propiedad intelectual","AEC",65,10,79),
("Publicaciones Seller Dev","PR - Propiedad intelectual","KTA_BRASIL",99,21,128),
("Publicaciones Seller Dev","PR - Técnica prohibida","AEC",95,15,116),
("Publicaciones Seller Dev","PR - Técnica prohibida","ATE",0,0,1),
("Publicaciones Seller Dev","PR - Técnica prohibida","KTA_BRASIL",105,13,134),
("Publicaciones Seller Dev","PR - Técnica prohibida","MELICIDADE",3,0,3),
("Publicaciones Seller Dev","Potenciar Ventas","AEC",44,17,66),
("Publicaciones Seller Dev","Potenciar Ventas","CTX",16,6,27),
("Publicaciones Seller Dev","Potenciar Ventas","KTA_BRASIL",74,16,102),
("Publicaciones Seller Dev","Potenciar Ventas","MELICIDADE",1,0,1),
])

# ── Generate Python code for new sections ──────────────────────
def fmt_dict(name_w, name_m, weekly_s1, weekly_s2, monthly_m1, monthly_m2):
    """Generate Python code for p_c_weekly / p_c_monthly style sections."""
    drivers = ["Experiencia Impositiva Seller Dev","ME Vendedor Seller Dev",
               "PCF Vendedor Seller Dev","Partners","Post Venta Seller Dev",
               "Publicaciones Seller Dev"]
    lines = []
    # Weekly
    lines.append(f'{name_w} = {{')
    for drv in drivers:
        lines.append(f'    {repr(drv)}: {{')
        for period, data in [('S2', weekly_s2), ('S1', weekly_s1)]:
            proc_data = data.get(drv, {})
            if not proc_data:
                lines.append(f'        {repr(period)}: {{}},')
                continue
            lines.append(f'        {repr(period)}: {{')
            for proc, dim_dict in sorted(proc_data.items()):
                inner = ', '.join(f'{repr(k)}: {v}' for k,v in sorted(dim_dict.items()))
                lines.append(f'            {repr(proc)}: {{{inner}}},')
            lines.append('        },')
        lines.append('    },')
    lines.append('}')
    lines.append(f'{name_m} = {{')
    for drv in drivers:
        lines.append(f'    {repr(drv)}: {{')
        for period, data in [('M2', monthly_m2), ('M1', monthly_m1)]:
            proc_data = data.get(drv, {})
            if not proc_data:
                lines.append(f'        {repr(period)}: {{}},')
                continue
            lines.append(f'        {repr(period)}: {{')
            for proc, dim_dict in sorted(proc_data.items()):
                inner = ', '.join(f'{repr(k)}: {v}' for k,v in sorted(dim_dict.items()))
                lines.append(f'            {repr(proc)}: {{{inner}}},')
            lines.append('        },')
        lines.append('    },')
    lines.append('}')
    return '\n'.join(lines)

pc_code = fmt_dict('p_c_weekly', 'p_c_monthly', PC_S1, PC_S2, PC_M1, PC_M2)
po_code = fmt_dict('p_o_weekly', 'p_o_monthly', PO_S1, PO_S2, PO_M1, PO_M2)

section = (
    "\n# ═" * 1 + "═" * 63 + "\n"
    "# SECTION 2G: P×CANAL DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_TEAM_CHANNEL)\n"
    "# ═" + "═" * 63 + "\n"
    + pc_code + "\n\n"
    "# ═" + "═" * 63 + "\n"
    "# SECTION 2H: P×OFICINA DATA  ← skill atualiza (PRO_PROCESS_NAME × CX_USER_OFFICE)\n"
    "# ═" + "═" * 63 + "\n"
    + po_code + "\n"
)

# Inject into generate_html.py after SECTION 2F
TARGET = r'C:\claudinho\generate_html.py'
with open(TARGET, encoding='utf-8') as f:
    content = f.read()

ANCHOR = '\n# ═' * 1 + '═' * 63 + '\n# SECTION 3: CALCULATIONS'
pos = content.find(ANCHOR)
if pos == -1:
    # Try simpler anchor
    ANCHOR = '\n# ═══════════════════════════════════════════════════════════════\n# SECTION 3: CALCULATIONS'
    pos = content.find(ANCHOR)

if pos == -1:
    print('ERROR: SECTION 3 anchor not found')
    exit(1)

new_content = content[:pos] + '\n' + section + content[pos:]
with open(TARGET, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'OK: injected {len(section)} chars at pos {pos}')
print(f'New file size: {len(new_content)} chars')
