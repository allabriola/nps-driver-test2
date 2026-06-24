# Configuração do Task Scheduler — Atualização Diária NPS

## Criar a tarefa (rodar CMD como Administrador)

```cmd
schtasks /create /tn "NPS_MeLi_Atualizar_Diario" /tr "\"C:\Users\allabriola\PROJETO CLAUDINHO\atualizar_dashboards.bat\"" /sc daily /st 10:00 /ru "allabriola" /rl HIGHEST /f
```

## Verificar se foi criada

```cmd
schtasks /query /tn "NPS_MeLi_Atualizar_Diario"
```

## Testar manualmente

```cmd
schtasks /run /tn "NPS_MeLi_Atualizar_Diario"
```

## Ver logs

Os logs ficam em: `C:\Users\allabriola\PROJETO CLAUDINHO\logs\`
Formato do nome: `atualizar_AAAAMMDD.log`

## Remover a tarefa (quando não precisar mais)

```cmd
schtasks /delete /tn "NPS_MeLi_Atualizar_Diario" /f
```

## Alterar horário (ex: 08:00)

```cmd
schtasks /change /tn "NPS_MeLi_Atualizar_Diario" /st 08:00
```

## Configurar para rodar ao ligar (caso a máquina estivesse desligada)

No Task Scheduler gráfico (taskschd.msc):
1. Abrir "NPS_MeLi_Atualizar_Diario"
2. Aba "Settings" → marcar "Run task as soon as possible after a scheduled start is missed"
