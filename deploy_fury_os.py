#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload do nps_seller_dev_br_semanal.html para o Fury Object Storage.

Pré-requisitos:
  1. Fury app com Object Storage provisionado (fury new + provisionar OS no portal)
  2. Pacote instalado: poetry add melitk-objectstorage
  3. Variáveis de ambiente configuradas pelo Fury runtime:
       OBJECT_STORAGE_<STORAGE_NAME>_END_POINT_READ
       OBJECT_STORAGE_<STORAGE_NAME>_END_POINT_WRITE

Uso:
  python deploy_fury_os.py
"""

import os
import sys

try:
    from melitk.objectstorage import Client, OSType
    from melitk.objectstorage import exceptions as os_exceptions
except ImportError:
    print("Pacote nao instalado. Execute: poetry add melitk-objectstorage")
    sys.exit(1)

# ──────────────────────────────────────────────
# CONFIGURACAO  ← ajuste STORAGE_NAME para o
# nome do Object Storage provisionado no Fury
# ──────────────────────────────────────────────
STORAGE_NAME = "NPS-SELLER-DEV-BR"
REMOTE_PATH  = "nps_seller_dev_br_semanal.html"
LOCAL_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), REMOTE_PATH)


def main():
    print(f"Storage : {STORAGE_NAME}")
    print(f"Arquivo : {LOCAL_FILE}")

    if not os.path.exists(LOCAL_FILE):
        print(f"Arquivo nao encontrado: {LOCAL_FILE}")
        sys.exit(1)

    client = Client(storage_name=STORAGE_NAME, os_type=OSType.STANDARD)

    with open(LOCAL_FILE, "rb") as f:
        content = f.read()

    print(f"Fazendo upload ({len(content):,} bytes)...")
    try:
        client.upload(REMOTE_PATH, content, "text/html; charset=utf-8")
    except os_exceptions.UnableToSendFile as e:
        print(f"Falha no upload: {e}")
        sys.exit(1)

    print("Upload concluido.")

    # URL assinada valida por 60 minutos (util para compartilhar rapidamente)
    try:
        signed_url = client.make_download_url(REMOTE_PATH)
        print(f"\nURL temporaria (60 min):\n  {signed_url}")
    except os_exceptions.FailedToGetSignedURL as e:
        print(f"Nao foi possivel gerar URL assinada: {e}")

    print("\nPara URL permanente, acesse via Fury app:")
    print("  https://<seu-app>.furyapps.io/nps-report")
    print("  (requer fury_host/app.py deployado — veja fury_host/)")


if __name__ == "__main__":
    main()
