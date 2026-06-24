# Setup Claude Code — Stack CX MeLi

Guia para configurar o Claude Code com os plugins, MCPs e skills usados pelo time de CX.

---

## Pré-requisitos

- Claude Code instalado (`npm install -g @anthropic-ai/claude-code` ou via download oficial)
- Acesso à VPN MeLi (obrigatório para MCPs internos)
- `mcp-remote-proxy` instalado (ver seção abaixo)

---

## 1. Instalar o `mcp-remote-proxy`

O proxy é necessário para conectar MCPs internos da MeLi (Fury, RAGaaS etc.).

```bash
pipx install mcp-remote-proxy --index-url https://pypi.melioffice.com/simple/
```

Verifique onde foi instalado:

```bash
which mcp-remote-proxy   # Linux/macOS
where mcp-remote-proxy   # Windows
```

O caminho padrão no Windows é:
```
C:\Users\<seu-usuario>\.local\bin\mcp-remote-proxy.exe
```

---

## 2. Configurar os MCPs internos MeLi

### RAGaaS MCP (base de conhecimento CX)

O RAGaaS é a base de conhecimento interna usada pelas skills de NPS e TMO para buscar contexto relevante.

Execute no terminal:

```bash
claude mcp add ragaas-mcp mcp-remote-proxy https://ragaas-mcp.melioffice.com/mcp
```

### MCP Fury (documentação e apps Fury)

Execute no terminal:

```bash
claude mcp add MCPFury mcp-remote-proxy https://fury-mcp.melioffice.com/mcp/
```

---

**Alternativa manual** — edite `~/.claude/mcp.json` diretamente:

```json
{
  "mcpServers": {
    "ragaas-mcp": {
      "command": "C:\\Users\\<seu-usuario>\\.local\\bin\\mcp-remote-proxy.exe",
      "args": ["https://ragaas-mcp.melioffice.com/mcp"]
    },
    "MCPFury": {
      "command": "C:\\Users\\<seu-usuario>\\.local\\bin\\mcp-remote-proxy.exe",
      "args": ["https://fury-mcp.melioffice.com/mcp/"]
    }
  }
}
```

> **Windows**: troque `<seu-usuario>` pelo seu usuário real e use barras duplas `\\` no caminho.
> **macOS/Linux**: use `~/.local/bin/mcp-remote-proxy` como comando.
> **Pré-requisito**: acesso ao grupo `ragaas_mcp_remote_prod` no Fury para o RAGaaS funcionar.

---

## 3. Registrar o marketplace CX

Execute no terminal dentro do Claude Code para adicionar o marketplace de plugins do time CX:

```
/plugin marketplace add melisource/fury_cx-plugins-marketplace
```

Isso registra o repositório `melisource/fury_cx-plugins-marketplace` como fonte de plugins.

---

## 4. Instalar os plugins

Execute cada comando abaixo no terminal do Claude Code:

```
/plugin install skill-creator@claude-plugins-official
```

```
/plugin install slack@claude-plugins-official
```

```
/plugin install metrics-cx@fury_cx-plugins-marketplace
```

> O plugin `metrics-cx` instala as skills de NPS, TMO, Journey e ferramentas de análise CX.
> O plugin `slack` habilita envio de mensagens, leitura de canais e busca no Slack direto do Claude.

---

## 5. Conectar o Slack

O plugin Slack autentica via OAuth no browser. Após instalar o plugin, execute qualquer skill ou comando que use Slack — o Claude vai abrir automaticamente o fluxo de autorização.

Para forçar a autenticação manualmente:

```
/slack:summarize-channel
```

Na primeira execução, o Claude vai exibir um link de autorização. Acesse, autorize com sua conta Slack MeLi e pronto — a sessão fica salva.

**Skills disponíveis após conectar:**

| Skill | O que faz |
|---|---|
| `/slack:summarize-channel` | Resume atividade recente de um canal |
| `/slack:channel-digest` | Digest de múltiplos canais de uma vez |
| `/slack:find-discussions` | Busca discussões sobre um tema nos canais |
| `/slack:draft-announcement` | Rascunha um anúncio formatado e salva como draft |
| `/slack:standup` | Gera update de standup baseado na atividade recente |

> O Slack é também usado automaticamente pelas skills de NPS (`/nps-lineal-cs`) para enviar o reporte finalizado.

---

## 6. Instalar as skills individuais

Após instalar o plugin `metrics-cx`, ative as skills abaixo:

```
/tmo-standard-analysis-manager
```
Análise padronizada de TMO por equipe, canal, WoW e ofensores.

```
/nps-lineal-cs
```
Reporte executivo mensal de NPS por equipe CX (MoM, GAP vs target, dispersão).

```
/nps-impact-analysis
```
Análise de impacto em NPS por mudanças no volume de pesquisas (funnel, mix, root cause).

---

## 7. Verificar o `settings.json`

O arquivo `~/.claude/settings.json` deve conter os plugins habilitados e o marketplace registrado. Exemplo de configuração completa:

```json
{
  "enableAllProjectMcpServers": true,
  "enabledPlugins": {
    "skill-creator@claude-plugins-official": true,
    "slack@claude-plugins-official": true,
    "metrics-cx@cx-plugins-marketplace": true
  },
  "extraKnownMarketplaces": {
    "cx-plugins-marketplace": {
      "source": {
        "source": "github",
        "repo": "melisource/fury_cx-plugins-marketplace"
      }
    }
  },
  "autoUpdatesChannel": "latest"
}
```

> Se você também usa Figma, Code Review ou outros plugins oficiais, adicione-os no bloco `enabledPlugins` da mesma forma.

---

## 8. Validar a instalação

Abra o Claude Code e execute:

```
/skills
```

Você deve ver listadas: `tmo-standard-analysis-manager`, `nps-lineal-cs`, `nps-impact-analysis`, `slack:summarize-channel`, entre outras.

Para testar o MCPFury:

```
Busque a documentação de KVS no Fury
```

Claude deve responder chamando o tool `search_sdk_docs` automaticamente.

---

## Troubleshooting

| Problema | Solução |
|---|---|
| `mcp-remote-proxy` não encontrado | Verifique o PATH ou use o caminho absoluto no `mcp.json` |
| MCPFury não responde | Confirme que a VPN MeLi está conectada |
| RAGaaS retorna erro 403 | Solicite acesso ao grupo `ragaas_mcp_remote_prod` no Fury |
| Plugin não aparece | Execute `/plugin marketplace add melisource/fury_cx-plugins-marketplace` novamente |
| Skill não dispara | Reinstale o plugin com `/plugin install metrics-cx@fury_cx-plugins-marketplace` |
| Slack pede autenticação toda vez | Execute `/slack:summarize-channel` e complete o OAuth — a sessão persiste após autorizar |
| Slack não envia mensagem | Verifique se o plugin está habilitado em `settings.json` com `"slack@claude-plugins-official": true` |

---

## Resumo dos comandos

```bash
# 1. Instalar proxy
pipx install mcp-remote-proxy --index-url https://pypi.melioffice.com/simple/

# 2. Adicionar os MCPs internos MeLi
claude mcp add ragaas-mcp mcp-remote-proxy https://ragaas-mcp.melioffice.com/mcp
claude mcp add MCPFury mcp-remote-proxy https://fury-mcp.melioffice.com/mcp/

# 3. Registrar marketplace e instalar plugins
/plugin marketplace add melisource/fury_cx-plugins-marketplace
/plugin install skill-creator@claude-plugins-official
/plugin install slack@claude-plugins-official
/plugin install metrics-cx@fury_cx-plugins-marketplace

# 4. Autenticar o Slack (abre fluxo OAuth no browser)
/slack:summarize-channel
```
