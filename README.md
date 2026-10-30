# 🐾 PetTrack — IoT, Visão Computacional & IA Generativa

> **FIAP Challenge 2026 · 2º Ano ADS (Turmas de Fevereiro · 2º Semestre)**  
> **Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA — **Sprint 4: Implementação e Integração da Solução de IA, Visão Computacional, Telemetria IoT e Validações**  
> **Parceiro de Negócio:** Clyvo Vet  

---

## 👥 Integrantes do Grupo

| Nome Completo | RM |
| :--- | :--- |
| **Gabriel Sbrana Campos** | RM 565849 |
| **Moisés Waidemann Molinillo Júnior** | RM 563719 |
| **Thiago Rodrigues da Mota** | RM 563650 |
| **Richard Freitas** | RM 566127 |

---

## 🔗 Links Oficiais da Entrega (Sprint 4)

* 🎥 **Vídeo Pitch e Demonstração da Solução (YouTube - ~5 minutos):**  
  > **[https://youtu.be/C591dfs1aLc](https://youtu.be/C591dfs1aLc)**  
  > *(Vídeo demonstrando a ideia central, o funcionamento da IA integrada, a telemetria do colar inteligente com Node-RED, a visão computacional e o impacto para tutor e clínica parceira)*  
* 💻 **Repositório GitHub do Módulo:**  
  > **[https://github.com/Challenge-PetTrack/DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA.git](https://github.com/Challenge-PetTrack/DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA.git)**  

---

## 📋 Descrição do Desafio e Solução Proposta

Em parceria com a **Clyvo Vet**, o **PetTrack** ataca a principal dor do mercado veterinário: o **cuidado episódico e reativo**. Na rotina convencional, o tutor só procura a clínica diante de sintomas graves ou emergências, causando perda de vínculo longitudinal, abandono de tratamentos preventivos e queda no LTV da clínica.

Para solucionar essa dor, este módulo implementa um ecossistema integrado em três frentes de tecnologia disruptiva:
1. **Colar Inteligente Simulado (IoT):** Monitoramento contínuo em tempo real de temperatura corporal e nível de atividade física do animal via ESP32, protocolo MQTT TLS e dashboard analítico no Node-RED.
2. **Visão Computacional para Escore Corporal (BCS 1-9):** Classificação do estado nutricional do pet através de foto enviada pelo tutor ou veterinário, orientando intervenções antes que o animal atinja sobrepeso ou desnutrição.
3. **Health Report Estruturado com IA Generativa (Google Gemini):** Consolidação de todo o histórico clínico, telemetria das últimas 24h, evolução do BCS, medicamentos ativos e clima externo para gerar relatórios preditivos de saúde com linguagem humanizada, alertas e recomendações de acompanhamento clínico.

---

## 🏗️ Arquitetura Completa de Integração

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             1. COLLAR IOT                                   │
│                                                                             │
│  ESP32 (Wokwi)                                                              │
│  Temperatura (GPIO 34) + Atividade Física (GPIO 35)                         │
│       │ MQTT TLS (Porta 8883)                                               │
│       ▼                                                                     │
│  HiveMQ Cloud Broker ────────────────► Node-RED Dashboard                   │
│                                            │ OpenWeatherMap API (Clima)     │
│                                            │ Alertas Visuais (Gauges/Charts)│
│                                            │ HTTP POST /collar/novo         │
│                                            ▼                                │
│                                    Spring Boot API ──► Oracle DB            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    2. VISÃO COMPUTACIONAL — BCS POR FOTO                    │
│                                                                             │
│  Portal Web / App Tutor                                                     │
│  Upload da foto do animal                                                   │
│       │ HTTP POST (Base64)                                                  │
│       ▼                                                                     │
│  Python FastAPI — POST /analyze-bcs                                         │
│       ▼                                                                     │
│  Classificação BCS 1-9 + Condição + Tendência + Risco                       │
│       │ Persistência via Spring Boot                                        │
│       ▼                                                                     │
│  Oracle DB (TB_BCS_HISTORICO)                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│              3. HEALTH REPORT COM IA GENERATIVA (GEMINI)                    │
│                                                                             │
│  Portal Web / Backend Spring Boot                                           │
│  Consolida contexto snapshot (IoT 24h + BCS + Clínico + Clima)              │
│       │ HTTP POST /health-report (Bearer Token 32+ chars)                   │
│       ▼                                                                     │
│  Python FastAPI + Google Gemini (com Structured Outputs / Pydantic)         │
│       ▼                                                                     │
│  Spring Boot valida contrato e persiste no Oracle (TB_HEALTH_REPORT)        │
│       ▼                                                                     │
│  Visualização interativa e amigável no Portal do Tutor e Painel da Clínica  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Parte 1 — Colar IoT (ESP32 + MQTT + Node-RED)

### Sensores Simulados no Wokwi

| Sensor | Pino | Simulação | Faixa de Operação |
| :--- | :--- | :--- | :--- |
| **Temperatura Corporal** | GPIO 34 | Potenciômetro analógico | 35.0°C a 42.0°C |
| **Atividade Física** | GPIO 35 | Potenciômetro analógico | 0 a 100 passos/minuto |

### Tópicos MQTT no HiveMQ Cloud
* `pettrack/collar/{id_pet}/temperatura`: `{"id_pet":1,"sensor":"temperatura","valor":38.5,"unidade":"C"}`
* `pettrack/collar/{id_pet}/atividade`: `{"id_pet":1,"sensor":"atividade","valor":72,"unidade":"passos/min"}`
* `pettrack/collar/{id_pet}/alerta`: `{"tipo":"FEBRE","valor":40.1}`

### Regras de Negócio e Disparo de Alertas
* **Febre:** Se temperatura > 39.5°C $\rightarrow$ Dispara alerta `FEBRE`, publica no tópico MQTT e salva alerta clínico no banco.
* **Sedentarismo Crônico:** Se atividade < 20 passos/min por 3 leituras consecutivas $\rightarrow$ Dispara alerta `SEDENTARISMO`.
* **Faixa Normal:** Temperatura entre 37.5°C e 39.2°C e atividade regular $\rightarrow$ Registro de telemetria histórica e recálculo do Health Score.

---

## 📸 Parte 2 — Visão Computacional: Body Condition Score (BCS)

O **Body Condition Score (BCS)** é o padrão internacional da *World Small Animal Veterinary Association (WSAVA)* para avaliar a silhueta e adiposidade de cães e gatos em uma escala de 1 a 9:

| Escore BCS | Condição Corporal | Classificação de Risco |
| :---: | :--- | :--- |
| **1 - 2** | Muito Abaixo do Peso / Caquético | Desnutrição severa |
| **3 - 4** | Abaixo do Ideal | Déficit calórico |
| **5** | **Ideal / Saudável** | Condição ótima de saúde |
| **6 - 7** | Acima do Ideal / Sobrepeso | Risco de sobrecarga articular |
| **8 - 9** | Obeso | Alto risco para cardiopatias e diabetes |

### Endpoint de Análise (`POST /analyze-bcs`)
Recebe a imagem do animal em base64 com metadados (espécie, raça) e retorna o escore classificado, condição, recomendação nutricional e risco associado, gravando o histórico para posterior correlação no Health Report.

---

## 🧠 Parte 3 — Health Report Consolidado com IA Generativa (`POST /health-report`)

### 1. Papel da IA no Negócio (Clyvo Vet)
O Health Report resolve a sobrecarga cognitiva do tutor e do veterinário:
* Em vez de analisar múltiplos gráficos desconectados (leituras do colar, vacinas vencidas, anotações de consultas e peso), a IA Generativa analisa o **contexto clínico unificado**.
* Produz um resumo objetivo, nível de atenção classificado (`BAIXO`, `MODERADO`, `ALTO`, `INDETERMINADO`), motivos fundamentados exclusivamente nos dados reais fornecidos, recomendações e limitações explícitas.

### 2. Contrato de Entrada: Snapshot de Contexto (`HealthContext`)
O backend Spring Boot autentica o solicitante, monta o snapshot no servidor e envia um JSON estruturado contendo:
* **`pet`:** Identificação, nome, espécie, raça, idade e sexo.
* **`iotRecente`:** Leituras de temperatura corporal e atividade das últimas 24h com média, máxima, mínima e alertas disparados.
* **`bcs`:** Último escore corporal registrado, data da análise e tendência (subindo/estável/descendo).
* **`historico`:** Consultas clínicas recentes, diagnósticos, medicações em uso, taxa de adesão medicamentosa e vacinas.
* **`clima`:** Temperatura, umidade e condição meteorológica local obtidas via OpenWeatherMap.

### 3. Medidas de Segurança e Robustez da IA
* **Proteção contra Prompt Injection:** O System Prompt isola estritamente as instruções do modelo dos dados do JSON, tratando todo o conteúdo recebido como dados não-confiáveis.
* **Structured Outputs Estrito:** Resposta formatada via schema Pydantic (`resumo`, `nivelAtencao`, `motivos` com lista de `fontes`, `recomendacoes`, `limitacoes`), impedindo saídas com alucinações de formato ou HTML.
* **Autenticação Segura entre Serviços:** Comunicação Java $\leftrightarrow$ Python protegida por token Bearer com no mínimo 32 caracteres criptográficos (`HEALTH_REPORT_SERVICE_TOKEN`).
* **Proteção de Recursos:** Semáforo de controle de concorrência (`BoundedSemaphore(4)`) e limite máximo de corpo de requisição (256 KB).
* **Identificação de Simulação:** Modo mock explicitamente sinalizado (`simulado=true`, `provedor=mock`), nunca servindo como fallback silencioso para erros de IA.

---

## 🚀 Como Executar o Módulo

### 1. Colar Inteligente no Wokwi (ESP32)
1. Acesse o [Wokwi](https://wokwi.com) e crie um projeto com placa ESP32.
2. Copie os arquivos da pasta `project-esp32/`: `sketch.ino` e `diagram.json`.
3. Inicie a simulação (Play). O monitor serial exibirá a conexão WiFi (`Wokwi-GUEST`) e a conexão TLS com o HiveMQ Cloud.
4. Ajuste os potenciômetros de temperatura e atividade física para gerar telemetria e simular alertas de febre e sedentarismo.

### 2. Dashboard no Node-RED
1. Instale o Node-RED e a biblioteca de dashboard:
   ```bash
   npm install -g node-red
   cd ~/.node-red && npm install node-red-dashboard
   ```
2. Inicie o Node-RED executando: `node-red`.
3. Acesse `http://localhost:1880`, vá no menu superior direito $\rightarrow$ **Import** e selecione o arquivo `flows.json`.
4. Clique em **Deploy**.
5. Acesse a interface visual do dashboard em: `http://localhost:1880/ui`.

### 3. API Python FastAPI (BCS & Health Report)

#### No macOS / Linux:
```bash
cd py
# 1. Criação do ambiente virtual (se ainda não existir):
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalação das dependências:
pip install -r requirements-dev.txt

# 3. Inicialização da API FastAPI:
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### No Windows PowerShell:
```powershell
cd py
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

A documentação interativa Swagger da API estará disponível em: **`http://127.0.0.1:8000/docs`**.

---

## 🧪 Testes Automatizados (Pytest)

A suíte de testes unitários e de integração valida exaustivamente os contratos de entrada, resposta da IA, proteção de endpoints e tratamento de falhas.

Execute os testes com:
```bash
# Dentro da pasta py:
pytest -v
```

**Cobertura validada (35 testes aprovados):**
* Validação do contrato estruturado Pydantic (`HealthContext` e `Relatorio`).
* Autenticação por token Bearer (rejeição de tokens ausentes ou com menos de 32 caracteres).
* Validação de fontes obrigatórias para os motivos (`pet`, `iotRecente`, `bcs`, `historico`, `clima`).
* Rejeição de clima quando o status não for `DISPONIVEL`.
* Proteção contra vazamento de erros de provedores externos (401, 429, 500, 503, 504).
* Limite de concorrência e limite de tamanho de payload (256 KB).
* Preservação de avisos de limitações médicas obrigatórias.

---

## 📊 Dashboard Node-RED — Recursos Implementados

* **Gauge de Temperatura Corporal:** Faixa de 35°C a 42°C, com sinalização visual de alerta para valores $> 39.5°C$.
* **Gauge de Atividade Física:** Faixa de 0 a 100 passos/min, com sinalização de sedentarismo para valores $< 20$.
* **Widget Meteorológico:** Integração com OpenWeatherMap exibindo temperatura, umidade e condição climática de São Paulo.
* **Histórico Gráfico:** Gráficos de linha temporais com as últimas medições recebidas via MQTT.
* **Painel de Eventos e Alertas:** Tabela em tempo real com alertas de `FEBRE`, `SEDENTARISMO` e `NORMAL` com timestamp.

---

## 📦 Artefatos para Entrega no Portal FIAP (.zip)

O arquivo `.zip` para envio no portal FIAP deve conter o arquivo `entrega.txt` com:
1. **Link do vídeo pitch publicado no YouTube (modo não listado):** `https://youtu.be/C591dfs1aLc`
2. **Link do repositório no GitHub:** `https://github.com/Challenge-PetTrack/DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA.git`
