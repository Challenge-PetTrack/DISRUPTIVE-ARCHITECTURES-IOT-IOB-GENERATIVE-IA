# 🐾 PetTrack — IoT & Disruptive Architectures

**Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA  
**Curso:** 2TDS — FIAP 2026  
**Challenge:** Clyvo Vet  

---

## 📋 Descrição

Módulo de IoT, Visão Computacional e Relatórios Inteligentes do **PetTrack**, sistema operacional da saúde contínua do pet. Este módulo implementa três frentes de tecnologia disruptiva:

1. **Collar inteligente simulado** — monitora temperatura corporal e atividade física do animal em tempo real via MQTT
2. **BCS por foto** — análise do Body Condition Score (escore de condição corporal 1-9) via foto enviada pelo tutor ou veterinário
3. **Health Report estruturado** — geração de relatórios consolidados de acompanhamento a partir da telemetria IoT, histórico clínico, evolução do BCS e dados climáticos, integrado ao portal Java e persistido no Oracle DB

A proposta transforma o cuidado veterinário de **reativo para preventivo** — detectando febre, sedentarismo e má nutrição antes que se tornem emergências clínicas.

---

## 🏗️ Arquitetura Completa do Módulo

```
┌─────────────────────────────────────────────────────┐
│                    COLLAR IOT                       │
│                                                     │
│  ESP32 (Wokwi)                                      │
│  Temp (GPIO 34) + Atividade (GPIO 35)               │
│       │ MQTT TLS porta 8883                         │
│       ▼                                             │
│  HiveMQ Cloud ──────► Node-RED                      │
│                           │ OpenWeatherMap API      │
│                           │ Dashboard em tempo real │
│                           │ HTTP POST               │
│                           ▼                         │
│                      Spring Boot ──► Oracle DB      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              VISÃO COMPUTACIONAL — BCS              │
│                                                     │
│  App Tutor/Vet                                      │
│  Envia foto do pet                                  │
│       │ HTTP POST (base64)                          │
│       ▼                                             │
│  Python FastAPI — /analyze-bcs                      │
│       ▼                                             │
│  BCS Score 1-9 + Recomendação nutricional           │
│       │ Salva via Spring Boot                       │
│       ▼                                             │
│  Oracle DB (tb_bcs_historico)                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│            HEALTH REPORT CONSOLIDADO                │
│                                                     │
│  Portal Web / API Spring Boot                       │
│  Consolida contexto (IoT 24h + BCS + Clínico + Clima)│
│       │ HTTP POST /health-report (Bearer Token)     │
│       ▼                                             │
│  Python FastAPI + Gemini Structured Outputs         │
│       ▼                                             │
│  Spring Boot valida e persiste (TB_HEALTH_REPORT)   │
└─────────────────────────────────────────────────────┘
```

---

## 🔌 Parte 1 — Collar IoT (ESP32 + MQTT)

### Sensores Simulados (Wokwi)

| Sensor | Pino | Simulação | Faixa |
|---|---|---|---|
| Temperatura corporal | GPIO 34 | Potenciômetro | 35°C a 42°C |
| Atividade física | GPIO 35 | Potenciômetro | 0 a 100 passos/min |

### Tópicos MQTT

| Tópico | Descrição | Payload |
|---|---|---|
| `pettrack/collar/{id_pet}/temperatura` | Temperatura corporal | `{"id_pet":1,"sensor":"temperatura","valor":38.5,"unidade":"C"}` |
| `pettrack/collar/{id_pet}/atividade` | Atividade física | `{"id_pet":1,"sensor":"atividade","valor":72,"unidade":"passos/min"}` |
| `pettrack/collar/{id_pet}/alerta` | Alertas automáticos | `{"tipo":"FEBRE","valor":40.1}` |

### Regras de Alerta

| Condição | Alerta | Ação |
|---|---|---|
| Temperatura > 39.5°C | FEBRE | Publica no tópico de alerta + salva no Oracle |
| Atividade < 20 por 3 leituras seguidas | SEDENTARISMO | Publica no tópico de alerta + salva no Oracle |
| Temperatura OK + Atividade OK | NORMAL | Registra histórico |

---

## 📸 Parte 2 — Visão Computacional BCS por Foto

### O que é o BCS

O **Body Condition Score (BCS)** é um padrão veterinário internacional que avalia a condição corporal do animal em uma escala de **1 a 9**:

| Score | Condição | Risco |
|---|---|---|
| 1 - 2 | Caquético / Muito magro | Desnutrição severa |
| 3 - 4 | Abaixo do ideal | Necessita ganho de peso |
| 4 - 5 | Ideal | Condição saudável |
| 6 - 7 | Acima do ideal | Risco de sobrepeso |
| 8 - 9 | Obeso | Doenças metabólicas |

### Endpoint Python (`/analyze-bcs`)

```json
POST /analyze-bcs

Request:
{
  "id_pet": 1,
  "foto": "<base64>",
  "especie": "cachorro",
  "raca": "Golden Retriever"
}

Response:
{
  "bcs": 6,
  "condicao": "Acima do ideal",
  "recomendacao": "Reduzir porção em 15% e aumentar atividade física.",
  "tendencia": "subindo",
  "risco": "sobrepeso"
}
```

---

## 📄 Parte 3 — Health Report Consolidado (`/health-report`)

O endpoint `POST /health-report` recebe o contexto consolidado autenticado pelo backend Spring Boot (`HealthContext`), valida os dados com Pydantic e retorna um relatório estruturado contendo resumo, nível de atenção (`BAIXO`, `MODERADO`, `ALTO`, `INDETERMINADO`), motivos vinculados às fontes (`pet`, `iotRecente`, `bcs`, `historico`, `clima`), recomendações e limitações.

---

## 🚀 Como Executar

### Collar — ESP32 no Wokwi

1. Acesse [wokwi.com](https://wokwi.com) e crie um projeto ESP32
2. Cole o `project-esp32/sketch.ino` e o `project-esp32/diagram.json`
3. Clique em **Play**
4. Serial Monitor deve exibir:
```
WiFi OK
MQTT conectado!
{"id_pet":1,"sensor":"temperatura","valor":38.5,"unidade":"C"}
{"id_pet":1,"sensor":"atividade","valor":72,"unidade":"passos/min"}
```

### API Python FastAPI (BCS & Health Report)

```powershell
cd py
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Documentação automática em `http://127.0.0.1:8000/docs`

Execução dos testes automatizados:
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Node-RED

```bash
npm install -g node-red
cd ~/.node-red && npm install node-red-dashboard
node-red
```

1. Acesse `http://localhost:1880`
2. Importe o `flows.json`
3. Clique **Deploy**
4. Dashboard em `http://localhost:1880/ui`

---

## 📊 Dashboard Node-RED

| Widget | Dados exibidos |
|---|---|
| Gauge temperatura | 35°C a 42°C — alerta acima de 39.5°C |
| Gauge atividade | 0 a 100 passos/min — alerta abaixo de 20 |
| Clima externo | Temperatura, umidade e condição de SP |
| Painel de alertas | FEBRE / SEDENTARISMO / NORMAL com timestamp |
| Gráfico histórico | Últimas leituras de temperatura e atividade |

---

## 👥 Integrantes

Nome | RM
--- | ---
Thiago Rodrigues da Mota | 563650
Moisés Waidemann Molinillo Júnior | 563719
Gabriel Sbrana Campos | 565849
Richard Freitas | 566127

---

## 📎 Links

- **Vídeo YouTube:** https://youtu.be/C591dfs1aLc
- **Repositório IOT:** https://github.com/Challenge-PetTrack/DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA.git
