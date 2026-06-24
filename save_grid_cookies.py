#!/usr/bin/env python3
"""
Lê os cookies do Cookie-Editor da área de transferência e salva em grid_cookies.json.

Como usar:
  1. Abra grid.adminml.com no Chrome (logado)
  2. Clique no ícone do Cookie-Editor na barra de extensões
  3. No painel que abre, clique em Export (ícone { } ou botão "Export All")
  4. Execute este script: python save_grid_cookies.py
"""

import subprocess, json, os, sys

def get_clipboard():
    r = subprocess.run(
        ["powershell", "-command", "Get-Clipboard"],
        capture_output=True, text=True, encoding="utf-8"
    )
    return r.stdout.strip()

def main():
    print("Lendo área de transferência...")
    text = get_clipboard()

    if not text:
        print("ERRO  Área de transferência vazia.")
        print("   Clique em Export no Cookie-Editor e tente novamente.")
        sys.exit(1)

    try:
        cookies = json.loads(text)
    except json.JSONDecodeError:
        print("ERRO  Conteúdo copiado não é JSON válido.")
        print("   Certifique-se de clicar em Export no Cookie-Editor (não em Copy).")
        sys.exit(1)

    if not isinstance(cookies, list):
        print("ERRO  Formato inesperado — esperado uma lista de cookies.")
        sys.exit(1)

    # Filtra apenas cookies do grid.adminml.com
    grid_cookies = [c for c in cookies if "adminml" in c.get("domain", "")]
    if not grid_cookies:
        # Aceita todos se não houver filtro de domínio
        grid_cookies = cookies

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grid_cookies.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(grid_cookies, f, indent=2, ensure_ascii=False)

    print(f"OK  {len(grid_cookies)} cookies salvos em:")
    print(f"   {out}")
    print()
    print("Testando conexão com o Grid...")

    import requests, re
    sess = requests.Session()
    sess.headers.update({
        "X-Caller-Id": "andre.labriola@mercadolivre.com",
        "X-Requested-With": "XMLHttpRequest",
    })
    for c in grid_cookies:
        name  = c.get("name", "")
        value = c.get("value", "")
        domain = c.get("domain", "grid.adminml.com").lstrip(".")
        if name and value:
            sess.cookies.set(name, value, domain=domain)

    r = sess.get("https://grid.adminml.com/api/v1/me", timeout=10)
    if r.ok:
        user = r.json().get("name") or r.json().get("email") or "OK"
        print(f"OK  Sessão autenticada como: {user}")
        print()
        print("Tudo certo! O próximo 'weekly-report-semanal' já vai atualizar o Grid.")
    elif r.status_code == 401:
        print("ERRO  Sessão inválida ou expirada.")
        print("   Certifique-se de estar logado em grid.adminml.com e tente novamente.")
        os.remove(out)
    else:
        print(f"?  HTTP {r.status_code} — os cookies foram salvos mas não foi possível confirmar o login.")
        print("   Tente rodar o weekly-report-semanal para ver se funciona.")

if __name__ == "__main__":
    main()
