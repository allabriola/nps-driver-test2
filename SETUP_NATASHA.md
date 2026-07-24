# Setup para atualização diária dos dashboards

Feito por: Andre Labriola  
Para: Natasha

---

## O que você vai fazer todo dia

Abrir o Claude Code nessa pasta e rodar um comando. Ele faz tudo automaticamente:
consulta o BigQuery, gera os HTMLs e publica no Grid.

Os dashboards atualizados ficam em:
- [Outgoing Drivers](https://grid.adminml.com/d/01KX12R63S5G2VZXXH7J5QDSZN/view)
- [NPS Tendências Seller Dev](https://grid.adminml.com/d/01KRBESTYE6P7M3FG2FS4KVES2/view)
- [Copiloto Usabilidade](https://grid.adminml.com/d/01KX131TPRN818YPAJZKY21DHE/view)
- [Async Longtail](https://grid.adminml.com/d/01KX12PSQHT8NHA128X1CYN2EN/view)

---

## Setup (só uma vez)

### 1. Clonar o repositório

Abra um terminal (PowerShell ou Git Bash) e rode:

```bash
git clone https://github.com/allabriola/nps-driver-test2.git C:\claudinho
```

### 2. Instalar o Python

Baixe e instale o Python 3.12: https://www.python.org/downloads/  
Durante a instalação, marque **"Add Python to PATH"**.

### 3. Instalar as dependências

```bash
cd C:\claudinho
pip install -r requirements.txt
```

### 4. Autenticar no Google Cloud (BigQuery)

Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install  
Depois rode:

```bash
gcloud auth application-default login
```

Vai abrir o browser — faça login com sua conta `@mercadolivre.com`.

### 5. Instalar o Claude Code

Se ainda não tiver: https://claude.ai/code  
Abra o Claude Code e aponte para a pasta `C:\claudinho`.

---

## Uso diário

1. Abra o Claude Code na pasta `C:\claudinho`
2. Digite o comando:

```
/atualizar-dashboard-grid
```

3. Aguarde — o processo leva ~20-30 minutos no total (BigQuery pode demorar)
4. No final, o Claude entrega uma tabela confirmando quais dashboards subiram no Grid

### Dicas

- **Rodar de manhã** é melhor — os dados do dia anterior já estão disponíveis
- **Segunda-feira** o processo é mais longo (tem etapas extras de virada de semana) — pode levar até 40 min
- Se um dashboard falhar, o Claude registra o erro e continua com os demais — não precisa recomeçar tudo
- O erro `Grid: No module named 'playwright'` no NPS Seller Dev é esperado e não afeta nada

---

## Atualizar o código

Se o Andre fizer mudanças no repositório durante as férias, rode:

```bash
cd C:\claudinho
git pull
```

---

## Dúvidas

Falar com Andre no retorno ou abrir issue no repositório.
