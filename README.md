# 🐾 PetTrack — IoT & Disruptive Architectures

**Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA  
**Curso:** 2TDS — FIAP 2026  
**Challenge:** Clyvo Vet  

---

## 📋 Descrição

Módulo de IoT e Visão Computacional do **PetTrack**, sistema operacional da saúde contínua do pet. Este módulo implementa dois pilares de tecnologia disruptiva:

1. **Collar inteligente simulado** — monitora temperatura corporal e atividade física do animal em tempo real via MQTT
2. **BCS por foto** — análise do Body Condition Score (escore de condição corporal 1-9) via foto enviada pelo tutor ou veterinário, usando IA generativa (Claude Vision API)

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
│       │ Claude Vision API                           │
│       ▼                                             │
│  BCS Score 1-9 + Recomendação nutricional           │
│       │ Salva via Spring Boot                       │
│       ▼                                             │
│  Oracle DB (tb_bcs_historico)                       │
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

### Fluxo da Análise

```
Tutor/Vet tira foto do pet no app
        │ HTTP POST /analyze-bcs
        ▼
Python FastAPI
        │ Claude Vision API analisa:
        │  - Silhueta do animal
        │  - Visibilidade de costelas e coluna
        │  - Depósitos de gordura
        │  - Proporção corporal
        ▼
Retorna BCS + condição + recomendação nutricional
        │ Spring Boot salva no Oracle
        ▼
App exibe resultado + tendência histórica
```

### Endpoint Python

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

## ⚙️ Tecnologias Utilizadas

| Tecnologia | Parte | Função |
|---|---|---|
| ESP32 (Wokwi) | Collar | Microcontrolador simulado |
| MQTT TLS porta 8883 | Collar | Protocolo IoT seguro |
| HiveMQ Cloud | Collar | Broker MQTT na nuvem |
| Node-RED | Collar | Processamento e dashboard |
| OpenWeatherMap API | Collar | Dados climáticos externos |
| Python FastAPI | BCS | API de visão computacional |
| Claude Vision API | BCS | Análise de foto do pet |
| ArduinoJson | Collar | Serialização JSON no ESP32 |
| PubSubClient | Collar | Cliente MQTT para ESP32 |
| Oracle Database | Ambos | Persistência de dados |

---

## 📁 Estrutura do Repositório

```
iot/
├── collar/
│   ├── sketch.ino        # Código do ESP32
│   └── diagram.json      # Circuito Wokwi
├── bcs/
│   ├── main.py           # FastAPI — endpoint /analyze-bcs
│   ├── requirements.txt  # Dependências Python
│   └── Dockerfile        # Container Python
├── nodered/
│   └── flows.json        # Flow Node-RED completo
├── sql/
│   └── ddl.sql           # Tabelas Oracle
└── README.md             # Este arquivo
```

---

## 🚀 Como Executar

### Collar — ESP32 no Wokwi

1. Acesse [wokwi.com](https://wokwi.com) e crie um projeto ESP32
2. Cole o `sketch.ino` e o `diagram.json`
3. Clique em **Play**
4. Serial Monitor deve exibir:
```
WiFi OK
MQTT conectado!
{"id_pet":1,"sensor":"temperatura","valor":38.5,"unidade":"C"}
{"id_pet":1,"sensor":"atividade","valor":72,"unidade":"passos/min"}
```

### BCS — Python FastAPI

```bash
cd bcs
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Documentação automática em `http://localhost:8000/docs`

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

## 🗄️ Banco de Dados Oracle

```sql
CREATE TABLE tb_alerta_collar (
    id_alerta    NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    id_pet       NUMBER NOT NULL,
    tp_alerta    VARCHAR2(20) NOT NULL,
    vl_sensor    NUMBER(5,2),
    ds_descricao VARCHAR2(255),
    dt_alerta    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tb_bcs_historico (
    id_bcs       NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    id_pet       NUMBER NOT NULL,
    nr_score     NUMBER(2) NOT NULL,
    ds_condicao  VARCHAR2(30),
    ds_recomend  VARCHAR2(500),
    ds_tendencia VARCHAR2(20),
    dt_analise   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📈 Critérios de Avaliação

| Critério | Peso | Entregável |
|---|---|---|
| Aplicação técnica de IoT e/ou Visão Computacional | 50pts | Collar ESP32 + BCS por foto |
| Clareza e didática do vídeo | 20pts | Vídeo ~5min YouTube |
| Organização do repositório e documentação | 20pts | Este README + estrutura de pastas |
| Disrupção e originalidade | 10pts | Health score + BCS veterinário por foto |

---

## 👥 Integrantes

Nome | RM
--- | ---
Thiago Rodrigues da Mota | 563650
Moisés Waidemann Molinillo Júnior | 563719
Gabriel Sbrana Campos | 565849
Richard Freitas | 566127

## 🎬 Vídeo Demonstrativo

> Link: _em breve_

Roteiro (~5 minutos):
1. ESP32 no Wokwi publicando temperatura e atividade
2. HiveMQ Cloud recebendo em tempo real
3. Node-RED processando e gerando alertas
4. Dashboard com todos os indicadores
5. Envio de foto pelo app e retorno do BCS score
6. Dados salvos no Oracle

---


## 📎 Links

- **Vídeo YouTube:**https://youtu.be/C591dfs1aLc **
- **Repositório IOT:** https://github.com/Challenge-PetTrack/DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA.git **
