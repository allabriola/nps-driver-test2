#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csat_upload_grid.py — Faz upload do csat_dashboard.html para o Grid

Pré-requisito: cookies frescos em grid_cookies.json
  1. Abra grid.adminml.com no Chrome (logado)
  2. Exporte cookies via Cookie-Editor → Export
  3. Execute: python save_grid_cookies.py

Uso: python csat_upload_grid.py
"""
import json, sys, os, requests
sys.stdout.reconfigure(encoding='utf-8')

DOC_ID    = "01KQ3BMS9EGKTB3QHEZXXW4E46"
HTML_FILE = "csat_dashboard.html"
SKILL_VER = "3.6.5"

# ── Verifica arquivo ──────────────────────────────────────────────────────────
if not os.path.exists(HTML_FILE):
    print(f"ERRO: {HTML_FILE} não encontrado. Rode build_csat_dashboard.py primeiro.")
    sys.exit(1)

if not os.path.exists("grid_cookies.json"):
    print("ERRO: grid_cookies.json não encontrado.")
    print("Passos:")
    print("  1. Abra grid.adminml.com no Chrome (logado)")
    print("  2. Exporte cookies via Cookie-Editor → Export")
    print("  3. Execute: python save_grid_cookies.py")
    sys.exit(1)

# ── Carrega cookies ───────────────────────────────────────────────────────────
with open("grid_cookies.json", encoding="utf-8") as f:
    cookies_list = json.load(f)

session = requests.Session()
session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
for c in cookies_list:
    domain = c.get('domain', 'grid.adminml.com').lstrip('.')
    session.cookies.set(c['name'], c['value'], domain=domain)

# ── Testa autenticação ────────────────────────────────────────────────────────
print("Testando autenticação...")
r = session.get("https://grid.adminml.com/api/v1/me", timeout=15)
if r.status_code == 401:
    print("ERRO 401: Cookies expirados.")
    print("Passos para renovar:")
    print("  1. Abra grid.adminml.com no Chrome (logado)")
    print("  2. Cookie-Editor → Export → copia o JSON")
    print("  3. Execute: python save_grid_cookies.py")
    sys.exit(1)
elif not r.ok:
    print(f"ERRO {r.status_code}: {r.text[:200]}")
    sys.exit(1)

user_info = r.json()
print(f"  OK — autenticado como: {user_info.get('name') or user_info.get('email') or 'OK'}")

# ── Upload via engine ─────────────────────────────────────────────────────────
print(f"\nFazendo upload de {HTML_FILE} para Grid doc {DOC_ID}...")
config = json.dumps({
    "skill_version": SKILL_VER,
    "doc_id":        DOC_ID,
    "title":         "CSAT — BR Longtail + ExpImpo",
})

with open(HTML_FILE, "rb") as fh:
    resp = session.post(
        "https://grid.adminml.com/api/v1/engine/run",
        data={"config": config},
        files={"file": (HTML_FILE, fh, "text/html")},
        timeout=60,
    )

if not resp.ok:
    print(f"ERRO HTTP {resp.status_code}:")
    print(resp.text[:500])
    sys.exit(1)

result = resp.json()
if result.get("ok"):
    view_url = result.get("view_url", f"https://grid.adminml.com/d/{DOC_ID}/view")
    print(f"\n✅ Upload concluído!")
    print(f"   Link: {view_url}")
else:
    # Verifica steps para detalhe do erro
    for step in result.get("steps", []):
        status = step.get("status", "")
        label  = step.get("label", "")
        detail = step.get("detail", "")
        icon   = "✓" if status == "OK" else "✗"
        print(f"  {icon} {label}: {detail}")

    if result.get("next_actions"):
        print("\nPróximos passos sugeridos pelo Grid:")
        for act in result["next_actions"]:
            print(f"  • {act}")
    sys.exit(1)
