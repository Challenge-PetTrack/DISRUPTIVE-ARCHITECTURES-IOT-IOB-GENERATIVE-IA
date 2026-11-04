# 🐾 PetTrack — IoT, Visão Computacional & IA Generativa

> **FIAP Challenge 2026 · 2º Ano ADS (Turmas de Fevereiro · 2º Semestre)**  
> **Disciplina:** Disruptive Architectures: IoT, IoB & Generative IA  
> **Sprint 4:** Consolidação Final, Implementação da Solução de IA Generativa, Visão Computacional, Telemetria IoT e Validações de Ponta a Ponta  
> **Parceiro de Negócio:** Clyvo Vet  

---

## 👥 Integrantes do Grupo

| Nome Completo | RM | Turma |
| :--- | :--- | :--- |
| **Gabriel Sbrana Campos** | RM 565849 | 2TDSPF |
| **Moisés Waidemann Molinillo Júnior** | RM 563719 | 2TDSPF |
| **Thiago Rodrigues da Mota** | RM 563650 | 2TDSPF |
| **Richard Freitas** | RM 566127 | 2TDSPF |

---

## 🔗 Links Oficiais da Entrega (Sprint 4)

* 🎥 **Vídeo Pitch e Demonstração da Solução (YouTube - ~5 minutos):**  
  > **[https://youtu.be/Ahc93FSBpuU](https://youtu.be/Ahc93FSBpuU)**  
  > *(Apresentação da ideia central do projeto, demonstração funcional da IA Generativa integrada, telemetria do colar inteligente via MQTT e Node-RED, classificação de escore corporal por visão computacional e benefícios práticos para tutor e clínica).*
* 💻 **Repositório GitHub do Módulo:**  
  > **[https://github.com/Challenge-PetTrack/DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA](https://github.com/Challenge-PetTrack/DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA)** *(Branch principal: `main`)*

---

## 📑 Sumário
1. [Visão Geral do Desafio & Proposta de Valor (Clyvo Vet)](#-visão-geral-do-desafio--proposta-de-valor-clyvo-vet)
2. [Arquitetura Geral da Solução e Fluxo de Dados](#-arquitetura-geral-da-solução-e-fluxo-de-dados)
3. [Componente de IA Generativa — Health Report Preditivo](#-componente-de-ia-generativa--health-report-preditivo)
4. [Componente de Visão Computacional — Análise BCS por Imagem](#-componente-de-visão-computacional--análise-bcs-por-imagem)
5. [Módulo IoT — Colar Inteligente (ESP32 + MQTT + HiveMQ Cloud)](#-módulo-iot--colar-inteligente-esp32--mqtt--hivemq-cloud)
6. [Dashboard Analítico no Node-RED](#-dashboard-analítico-no-node-red)
7. [Contratos de Dados e Estrutura dos Modelos Pydantic](#-contratos-de-dados-e-estrutura-dos-modelos-pydantic)
8. [Segurança, Resiliência e Mitigação de Falhas](#-segurança-resiliência-e-mitigação-de-falhas)
9. [Instruções de Instalação e Execução](#-instruções-de-instalação-e-execução)
10. [Testes Automatizados (Pytest) e Validações](#-testes-automatizados-pytest-e-validações)
11. [Estrutura do Repositório](#-estrutura-do-repositório)
12. [Checklist de Atendimento aos Critérios da Sprint 4](#-checklist-de-atendimento-aos-critérios-da-sprint-4)
13. [Artefatos para Submissão no Portal FIAP (.zip)](#-artefatos-para-submissão-no-portal-fiap-zip)

---

## 🎯 Visão Geral do Desafio & Proposta de Valor (Clyvo Vet)

### O Problema de Negócio
No modelo tradicional de saúde veterinária, o cuidado prestado é predominantemente **reativo e episódico**. A maioria dos tutores só recorre ao médico veterinário quando o animal já manifesta sinais clínicos avançados ou dor aguda. Esse comportamento acarreta sérias consequências:
* **Perda do histórico contínuo:** O veterinário atende o animal pontualmente sem dados objetivos sobre sua rotina, temperatura e atividade física nos dias anteriores.
* **Abandono do plano terapêutico:** Elevado índice de esquecimento na administração de antibióticos e medicamentos contínuos em domicílio.
* **Sobrecarga de dados desconectados:** Quando o tutor anota informações, elas ficam dispersas em anotações informais, impossibilitando uma tomada de decisão rápida.
* **Redução no LTV da clínica:** A ausência de engajamento contínuo diminui a retenção do cliente e consultas preventivas.

### A Solução PetTrack
Desenvolvido em alinhamento com a parceira **Clyvo Vet**, o **PetTrack** transforma a jornada do pet em um ecossistema de **cuidado contínuo e inteligente**:
1. **Telemetria de Sinais Vitais (IoT/IoB):** Uma coleira inteligente baseada em ESP32 afere a temperatura corporal e a movimentação do pet, detectando quadros precoces de febre ou prostração/sedentarismo.
2. **Avaliação Nutricional por Imagem (Visão Computacional):** Classificação do Body Condition Score (BCS 1-9) pelo padrão internacional WSAVA através de foto enviada pelo tutor no aplicativo.
3. **Health Report com IA Generativa (Google Gemini):** Um motor inteligente que recebe o contexto completo do animal (telemetria 24h, escore BCS, histórico clínico, medicamentos ativos e clima externo) e gera uma síntese clínica com linguagem humanizada para o tutor e insights objetivos para o veterinário.

### Benefícios Diretos
* **Para o Tutor:** Alertas preventivos antes de crises graves, linguagem acessível sobre o estado do pet e facilidade no acompanhamento diário.
* **Para a Clínica (Clyvo Vet):** Suporte qualificado à decisão clínica, maior fidelização do tutor, redução de no-shows e estímulo a check-ups preventivos regulares.

---

## 🏗️ Arquitetura Geral da Solução e Fluxo de Dados

A arquitetura do projeto interliga hardware simulado, corretores MQTT em nuvem, orquestração de eventos, backend corporativo e microsserviço de inteligência artificial:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  1. HARDWARE IOT (COLEIRA)                             │
│                                                                                        │
│   ESP32 (Simulação Wokwi)                                                              │
│   ├── Sensor de Temperatura Corporal (GPIO 34 / 35.0°C - 42.0°C)                       │
│   └── Sensor de Atividade Física (GPIO 35 / 0 - 100 passos/min)                        │
│            │                                                                           │
│            ▼ MQTT TLS (Porta 8883)                                                     │
│   HiveMQ Cloud Broker (Cluster S1)                                                     │
└────────────┬───────────────────────────────────────────────────────────────────────────┘
             │
             ▼ Tópicos: pettrack/collar/{id_pet}/[temperatura|atividade|alerta]
┌────────────┴───────────────────────────────────────────────────────────────────────────┐
│                           2. ORQUESTRAÇÃO & DASHBOARD (NODE-RED)                       │
│                                                                                        │
│   Node-RED Runtime (Porta 1880)                                                        │
│   ├── Gauges e Gráficos Temporais (Node-RED Dashboard)                                 │
│   ├── Integração com OpenWeatherMap API (Temperatura, Umidade e Condição Climática)    │
│   └── Detecção de Regras de Borda & Webhook HTTP POST (/collar/novo)                   │
└────────────┬───────────────────────────────────────────────────────────────────────────┘
             │
             ▼ HTTP REST
┌────────────┴───────────────────────────────────────────────────────────────────────────┐
│                           3. BACKEND CORPORATIVO (SPRING BOOT & ORACLE)                │
│                                                                                        │
│   Spring Boot 3.3.4 (Porta 8080)                                                       │
│   ├── Ingestão de Telemetria e Alertas Clínicos (TB_COLLAR_LEITURA, TB_ALERTA)         │
│   ├── Agrupamento do Snapshot Clínico do Pet (HealthReportContextAssembler)            │
│   └── Banco de Dados Relacional Oracle Cloud (Tabelas de Negócio e Auditoria)          │
└────────────┬───────────────────────────────────────────────────────────────────────────┘
             │
             ▼ Chamada Autenticada HTTP POST /health-report (Bearer Token 32+ chars)
┌────────────┴───────────────────────────────────────────────────────────────────────────┐
│                      4. SERVIÇOS INTELIGENTES (PYTHON FASTAPI & GEMINI)                │
│                                                                                        │
│   FastAPI Microservice (Porta 8000)                                                    │
│   ├── Visão Computacional (POST /analyze-bcs): Classificação WSAVA 1-9 via GPT-4o      │
│   └── IA Generativa (POST /health-report): Motor Google Gemini (Structured Outputs)    │
│            │                                                                           │
│            ├── Validação Estrita de Contrato (Pydantic HealthContext & Relatorio)      │
│            ├── Grounding Anti-Alucinação (Obrigatoriedade de Fontes Vinculadas)        │
│            └── Resposta Estruturada: Resumo, Nível de Atenção, Motivos, Recomendações  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Componente de IA Generativa — Health Report Preditivo

O endpoint principal de inteligência artificial da aplicação é o `POST /health-report`. Ele foi desenhado para eliminar o isolamento de dados no prontuário do paciente, sintetizando informações multidimensionais em um relatório conciso e confiável.

### 1. Abordagem de IA Adotada e Justificativa Técnica
* **Modelo Utilizado:** **Google Gemini** (suporte aos modelos `gemini-1.5-flash`, `gemini-2.0-flash` ou superiores, configurável via variável de ambiente `HEALTH_REPORT_MODEL`).
* **Motivo da Escolha:** Alta velocidade de resposta, janela de contexto eficiente e suporte de primeira classe ao recurso nativo de **Structured Outputs** (`generationConfig.responseSchema`), garantindo que o modelo produza exatamente o JSON solicitado sem alucinações de formato ou tags indesejadas.
* **Modo Mock Integrado:** Permite a execução da suíte de testes de integração e validação de pipeline em ambientes offline ou sem consumo de cotas de API externa, respondendo de forma determinística com a flag `simulado: true`.

### 2. Estratégia de Grounding e Prevenção de Alucinações
* **Isolamento de Instruções:** Todo o conteúdo recebido no JSON de contexto é marcado como dado externo e não-confiável dentro do *System Prompt*. Comandos maliciosos em campos de texto livre (ex.: nome do animal ou observações clínicas) são desarmados.
* **Rastreabilidade Obrigatória de Fontes:** Cada justificativa gerada pelo modelo no bloco `motivos` deve conter o campo `fontes`, obrigatoriamente referenciando pelo menos uma das seções enviadas: `["pet", "iotRecente", "bcs", "historico", "clima"]`.
* **Sem Suposições Imateriais:** Se o status do clima for diferente de `DISPONIVEL`, o modelo é impedido de utilizar dados meteorológicos para justificar sintomas. Se faltarem dados clínicos mínimos, o nível de atenção é fixado como `INDETERMINADO`.
* **Proibição de Conduta Médica Direta:** O sistema não prescreve antibióticos, não altera dosagens de medicamentos e inclui obrigatoriamente em todas as respostas a cláusula de limitação legal: *"Relatório de apoio ao acompanhamento; não substitui avaliação veterinária."*

### 3. Exemplo de Requisição ao Endpoint (`POST /health-report`)
```http
POST /health-report HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer <HEALTH_REPORT_SERVICE_TOKEN_MIN_32_CHARS>
Content-Type: application/json

{
  "versao": "1.0",
  "geradoEm": "2026-11-03T20:30:00Z",
  "fusoHorario": "America/Sao_Paulo",
  "pet": {
    "id": 1,
    "nome": "Pipoca",
    "especie": "Canina",
    "raca": "Golden Retriever",
    "idadeAnos": 4.5,
    "pesoKg": 31.2
  },
  "periodoIot": {
    "inicioInclusivo": "2026-11-02T20:30:00",
    "fimExclusivo": "2026-11-03T20:30:00"
  },
  "iotRecente": {
    "totalLeituras": 144,
    "temperaturasValidas": 144,
    "atividadesValidas": 144,
    "temperaturaMedia": 38.6,
    "temperaturaMaxima": 39.9,
    "atividadeMedia": 18.2,
    "ultimaLeitura": "2026-11-03T20:25:00",
    "alertas": [
      {
        "id": 101,
        "tipo": "FEBRE",
        "descricao": "Pico térmico detectado na leitura",
        "valorReferencia": 39.9,
        "resolvido": "N",
        "data": "2026-11-03T18:15:00"
      }
    ]
  },
  "bcs": {
    "ultima": { "id": 12, "score": 7, "observacao": "Sobrepeso abdominal moderado", "data": "2026-10-25T10:00:00" },
    "anterior": { "id": 8, "score": 6, "observacao": "Leve aumento de massa adiposa", "data": "2026-09-15T11:00:00" },
    "tendencia": "SUBINDO"
  },
  "historico": {
    "inicioEventos": "2026-08-01",
    "ultimaConsulta": "2026-09-15T11:00:00",
    "eventosRecentes": [
      { "id": 1, "tipo": "CONSULTA", "data": "2026-09-15T11:00:00", "diagnostico": "Acompanhamento de rotina", "observacao": "Recomendada dieta balanceada" }
    ],
    "medicamentosAtivos": [],
    "limiteVacinas": "2026-12-31",
    "vacinasVencidasOuVencendo": []
  },
  "clima": {
    "status": "DISPONIVEL",
    "fonte": "OpenWeatherMap",
    "localidade": "São Paulo, BR",
    "observadoEm": "2026-11-03T20:00:00Z",
    "temperaturaCelsius": 29.5,
    "umidadePercentual": 68.0,
    "condicao": "Nublado"
  },
  "avisos": []
}
```

### 4. Exemplo de Resposta Estruturada da IA
```json
{
  "idGeracao": "7a3e5c9b-6b21-4f18-b8ce-32b0d3bf492a",
  "idPet": 1,
  "geradoEm": "2026-11-03T20:30:02.145821+00:00",
  "contextoGeradoEm": "2026-11-03T20:30:00+00:00",
  "provedor": "gemini",
  "modelo": "gemini-2.0-flash",
  "versaoPrompt": "health-report-v1",
  "simulado": false,
  "persistido": false,
  "relatorio": {
    "resumo": "Pipoca apresentou pico febril de 39.9°C nas últimas 24 horas associado a queda no nível de atividade física média (18.2 passos/min), com escore corporal em curva ascendente (BCS 7).",
    "nivelAtencao": "ALTO",
    "motivos": [
      {
        "descricao": "Registro de alerta ativo de febre com temperatura máxima atingindo 39.9°C.",
        "fontes": ["iotRecente"]
      },
      {
        "descricao": "Atividade física reduzida em comparação aos padrões regulares da raça.",
        "fontes": ["pet", "iotRecente"]
      },
      {
        "descricao": "Escore de condição corporal atingiu grau 7 com tendência de subida em relação à avaliação anterior.",
        "fontes": ["bcs"]
      }
    ],
    "recomendacoes": [
      "Agendar avaliação clínica presencial na Clyvo Vet para investigar a etiologia do pico febril.",
      "Monitorar a ingestão de água e manter o animal em repouso térmico enquanto o quadro persistir.",
      "Discutir com o médico veterinário o ajuste da ingestão calórica para controle do sobrepeso."
    ],
    "limitacoes": [
      "Relatorio de apoio ao acompanhamento; nao substitui avaliacao veterinaria."
    ]
  }
}
```

---

## 📸 Componente de Visão Computacional — Análise BCS por Imagem

O **Body Condition Score (BCS)** é o índice preconizado pela *World Small Animal Veterinary Association (WSAVA)* para mensurar a composição corporal e adiposidade em cães e gatos em uma escala de 1 a 9:

| Escore BCS | Condição Corporal | Características Anatômicas | Conduta Sugerida |
| :---: | :--- | :--- | :--- |
| **1 - 2** | Caquético / Muito Magro | Costelas, coluna e ossos pélvicos visíveis sem cobertura adiposa. | Investigação clínica urgente de desnutrição. |
| **3 - 4** | Abaixo do Ideal | Costelas facilmente palpáveis, cintura acentuada. | Correção calórica orientada por veterinário. |
| **5** | **Ideal / Saudável** | **Silhueta equilibrada, costelas palpáveis com leve manto adiposo.** | **Manutenção da dieta e rotina de exercícios.** |
| **6 - 7** | Acima do Ideal / Sobrepeso | Cintura pouco definida, camada evidente de gordura sobre o dorso. | Manejo preventivo para proteção osteoarticular. |
| **8 - 9** | Obeso | Abdômen distendido, depósitos maciços de gordura e ausência de cintura. | Intervenção dietética e exames metabólicos. |

### Funcionamento do Endpoint (`POST /analyze-bcs`)
* O cliente web ou mobile realiza o upload da fotografia do pet codificada em **Base64**.
* O serviço encaminha a imagem com prompt veterinário especialista para o modelo de visão computacional.
* O retorno classifica o escore, a condição, a justificativa e o risco associado.
* O resultado é automaticamente enviado via requisição interna para a API corporativa Spring Boot (`POST /bcs/novo`), que persiste o registro na tabela `TB_BCS_HISTORICO` do banco Oracle.
* Possui também rota de demonstração rápida: `POST /analyze-bcs/mock`.

---

## 🔌 Módulo IoT — Colar Inteligente (ESP32 + MQTT + HiveMQ Cloud)

O colar inteligente é o dispositivo de borda responsável pela coleta e emissão contínua de telemetria dos sinais vitais do animal.

### Configuração de Hardware e Sensores (Simulado no Wokwi)
* **Placa:** ESP32 DevKit v1.
* **Sensor 1 (Temperatura Corporal):** Potenciômetro ligado ao pino analógico **GPIO 34**, simulando a faixa operacional de **35.0°C a 42.0°C**.
* **Sensor 2 (Atividade Física / Movimentação):** Potenciômetro ligado ao pino analógico **GPIO 35**, simulando de **0 a 100 passos/minuto**.

### Comunicação Segura via MQTT TLS
* **Broker:** HiveMQ Cloud Cluster.
* **Porta:** 8883 (Comunicação criptografada com `WiFiClientSecure`).
* **Autenticação:** Usuário e senha dedicados no cluster.
* **Tópicos Publicados:**
  * `pettrack/collar/{id_pet}/temperatura`: Telemetria térmica periódica.
  * `pettrack/collar/{id_pet}/atividade`: Nível de movimentação periódica.
  * `pettrack/collar/{id_pet}/alerta`: Alertas de evento clínico anômalo.

### Regras de Borda Implementadas no Firmware (`sketch.ino`)
* **Detecção de Febre:** Se a temperatura lida for superior a **39.5°C**, o ESP32 emite imediatamente uma mensagem no tópico de alerta com o payload `{"id_pet": 1, "tipo": "FEBRE", "valor": 40.1, "descricao": "Pico termico elevado"}`.
* **Detecção de Sedentarismo Crônico:** Caso a atividade física permaneça inferior a **20 passos/minuto** por 3 ciclos consecutivos de amostragem, o dispositivo emite um alerta `SEDENTARISMO`.
* **Operação Normal:** Quando os parâmetros permanecem estáveis (temperatura entre 37.5°C e 39.2°C), as leituras alimentam o histórico analítico.

---

## 📊 Dashboard Analítico no Node-RED

O fluxo configurado no Node-RED (`flows.json`) orquestra as mensagens do broker MQTT e oferece uma central de comando em tempo real:
1. **Subscrição MQTT:** Consome os tópicos do HiveMQ Cloud com reconexão automática e autenticação segura.
2. **Visualização por Gauges:** 
   * Mostrador circular de temperatura com faixas coloridas (Azul: Hipotermia; Verde: Faixa Saudável; Vermelho: Estado Febril).
   * Mostrador de passos por minuto com alerta visual de letargia.
3. **Contexto Meteorológico:** Consulta periódica à API do OpenWeatherMap para cruzar a temperatura corporal do animal com o clima da região.
4. **Histórico Gráfico:** Gráficos de linha temporais alimentados em tempo real a cada leitura recebida.
5. **Integração de Backend:** Nó HTTP Request que dispara `POST /collar/novo` para a API Spring Boot com o payload normalizado.

---

## 📋 Contratos de Dados e Estrutura dos Modelos Pydantic

O módulo Python adota tipagem rigorosa através do **Pydantic v2**, garantindo validações de tipos, limites e integridade antes de qualquer processamento:

```
HealthContext (Contrato Raiz)
├── pet: Perfil
│   ├── id (int, gt=0)
│   ├── nome, especie (str)
│   ├── raca (str opcional)
│   ├── idadeAnos (float >= 0)
│   └── pesoKg (float > 0)
├── periodoIot: Periodo
│   ├── inicioInclusivo (datetime)
│   └── fimExclusivo (datetime > inicioInclusivo)
├── iotRecente: Iot
│   ├── totalLeituras, temperaturasValidas, atividadesValidas (int >= 0)
│   ├── temperaturaMedia, temperaturaMaxima, atividadeMedia (float)
│   ├── ultimaLeitura (datetime)
│   └── alertas: list[Alerta]
├── bcs: Bcs
│   ├── ultima: Avaliacao (score 1-9)
│   ├── anterior: Avaliacao (score 1-9)
│   └── tendencia: ("SUBINDO" | "DESCENDO" | "ESTAVEL" | "SEM_HISTORICO_SUFICIENTE")
├── historico: Historico
│   ├── eventosRecentes: list[Evento]
│   ├── medicamentosAtivos: list[Medicamento]
│   └── vacinasVencidasOuVencendo: list[Vacina]
└── clima: Clima
    ├── status: ("DISPONIVEL" | "NAO_CONFIGURADO" | "FALHA_PROVEDOR" | ...)
    ├── temperaturaCelsius, umidadePercentual (float)
    └── condicao (str)
```

---

## 🛡️ Segurança, Resiliência e Mitigação de Falhas

* **Autenticação Inter-serviços:** O endpoint `/health-report` exige cabeçalho `Authorization: Bearer <token>`, sendo que a aplicação recusa tokens com comprimento inferior a 32 caracteres criptográficos (`HEALTH_REPORT_SERVICE_TOKEN`).
* **Proteção de Recursos e Concorrência:** O serviço limita o corpo da requisição a **256 KB** (`MAX_BODY_BYTES`) e controla a quantidade de requisições simultâneas com `BoundedSemaphore(4)`. Requisições adicionais recebem resposta `429 Too Many Requests` de forma controlada.
* **Isolamento de Falhas do Provedor de IA:** Falhas na API externa do Google Gemini (ex.: 429 quota excedida, 503 indisponibilidade ou 504 timeout) são mapeadas para códigos de erro de domínio (`LIMITE_PROVEDOR`, `IA_INDISPONIVEL`, `TEMPO_IA_ESGOTADO`), evitando travamentos no backend principal e vazamento de chaves privadas em logs.

---

## 🚀 Instruções de Instalação e Execução

### Pré-requisitos
* **Python:** 3.10 ou superior.
* **Node.js:** Versão LTS (para o Node-RED).
* **Navegador Web:** Para o Wokwi e interfaces visuais.

---

### 1. Inicializando a API Python FastAPI (Health Report & BCS)

#### Passo A: Configuração do Ambiente e Dependências
Abra o terminal na pasta `py/` do projeto:

```powershell
# No Windows PowerShell:
cd py
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

*(No Linux ou macOS: substitua a ativação por `source .venv/bin/activate`)*

#### Passo B: Configuração das Variáveis de Ambiente
Crie ou edite o arquivo `py/.env` com base no `py/.env.example`:

```ini
HEALTH_REPORT_SERVICE_TOKEN=token_secreto_super_seguro_com_mais_de_32_caracteres_12345
HEALTH_REPORT_MODE=gemini
HEALTH_REPORT_MODEL=gemini-2.0-flash
GEMINI_API_KEY=sua_chave_da_api_google_gemini
OPENAI_API_KEY=sua_chave_opcional_para_visao_computacional
SPRING_BOOT_URL=http://localhost:8080
```

> **Dica:** Para rodar sem chave externa de IA, basta definir `HEALTH_REPORT_MODE=mock`.

#### Passo C: Inicializando o Servidor Uvicorn
```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

* **Health Check da API:** `http://127.0.0.1:8000/health`
* **Swagger Interativo (OpenAPI):** `http://127.0.0.1:8000/docs`

---

### 2. Executando o Colar Inteligente no Wokwi (ESP32)
1. Acesse o ambiente online do [Wokwi ESP32](https://wokwi.com/projects/new/esp32).
2. Substitua o conteúdo do arquivo `sketch.ino` pelo código presente em `project-esp32/sketch.ino`.
3. Substitua o `diagram.json` pelo arquivo em `project-esp32/diagram.json`.
4. Adicione as bibliotecas no painel `libraries.txt`:
   * `PubSubClient`
   * `ArduinoJson`
5. Pressione **Play** para iniciar a simulação.
6. Acompanhe no console serial a conexão ao WiFi `Wokwi-GUEST` e a autenticação no broker HiveMQ Cloud.
7. Ajuste os potenciômetros de temperatura e atividade física para simular diferentes condições e alertas em tempo real.

---

### 3. Executando o Dashboard no Node-RED
1. Caso não possua o Node-RED e o dashboard instalados:
   ```bash
   npm install -g node-red
   cd ~/.node-red && npm install node-red-dashboard
   ```
2. Inicie o serviço executando no terminal:
   ```bash
   node-red
   ```
3. Abra o navegador em `http://localhost:1880`.
4. No canto superior direito, acesse o menu **Import** e selecione o arquivo `flows.json` da raiz deste repositório.
5. Clique no botão vermelho **Deploy**.
6. Acesse a interface visual do painel em: `http://localhost:1880/ui`.

---

## 🧪 Testes Automatizados (Pytest) e Validações

O projeto inclui uma bateria completa de testes automatizados unitários e de integração que asseguram a integridade dos contratos e a robustez dos componentes de IA.

Para executar todos os testes, acesse a pasta `py/` e rode:

```powershell
# Com o ambiente virtual ativado:
pytest -v
```

### Resultados Obtidos
```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\...\DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA\py
configfile: pytest.ini
testpaths: tests
collected 35 items

tests\test_health_report.py ...................................          [100%]

======================== 35 passed, 1 warning in 3.15s ========================
```

### Cenários Cobertos pelos Testes
* ✅ **Validação Estrita de Contrato:** Rejeição de payloads com campos ausentes, tipos incorretos ou intervalos temporais inconsistentes (`inicioInclusivo >= fimExclusivo`).
* ✅ **Autenticação:** Rejeição imediata (HTTP 401 e 503) para requisições sem token Bearer ou com token menor que 32 caracteres.
* ✅ **Sanitização de Fontes:** Verificação de que o modelo só cita `clima` quando o status for `DISPONIVEL`.
* ✅ **Controle de Concorrência e Sobrecarga:** Validação de bloqueio com HTTP 429 após esgotamento das vagas do semáforo e rejeição com HTTP 413 de corpos maiores que 256 KB.
* ✅ **Tratamento de Exceções do Provedor:** Mapeamento de erros 401, 429, 500, 502, 503 e 504 sem vazamento de detalhes sensíveis da infraestrutura.
* ✅ **Garantia de Cláusula Médica:** Validação de que a limitação legal sempre acompanha o relatório emitido.

---

## 📁 Estrutura do Repositório

```text
DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA/
│
├── flows.json                          # Fluxos exportados e configurados do Node-RED
├── entrega.txt                         # Metadados e links para submissão oficial
├── README.md                           # Documentação técnica completa consolidada
│
├── project-esp32/                      # Projeto de simulação de hardware IoT no Wokwi
│   ├── diagram.json                    # Diagrama de conexões e componentes Wokwi
│   ├── libraries.txt                   # Dependências do firmware (PubSubClient, ArduinoJson)
│   ├── sketch.ino                      # Firmware C++ do ESP32 com regras de borda
│   └── wokwi-project.txt               # Identificador do projeto no Wokwi
│
└── py/                                 # Microsserviço Python de IA & Visão Computacional
    ├── .env.example                    # Modelo de variáveis de ambiente do serviço
    ├── health_context_models.py        # Modelos Pydantic v2 do contrato do Health Report
    ├── health_report.py                # Integração com Google Gemini e regras de segurança
    ├── main.py                         # Aplicação FastAPI, rotas de BCS e ciclo de vida
    ├── pytest.ini                      # Configuração do executor de testes Pytest
    ├── requirements.txt                # Dependências principais de produção
    ├── requirements-dev.txt            # Dependências de desenvolvimento e testes
    │
    ├── scripts/                        # Scripts utilitários de suporte à integração
    │   ├── iniciar_java.py             # Validador de ambiente e inicialização do Java
    │   └── validar_health_report_real.py # Teste de integração de ponta a ponta (Java + Gemini)
    │
    └── tests/                          # Suíte de testes automatizados
        ├── fixtures/                   # Payloads JSON de exemplo para testes
        │   └── context.json            # Snapshot de contexto clínico de teste
        └── test_health_report.py       # 35 testes automatizados cobrindo todas as regras
```

---

## 🏆 Checklist de Atendimento aos Critérios da Sprint 4

| Requisito do Manual do Challenge (FIAP) | Status | Evidência no Projeto |
| :--- | :---: | :--- |
| **Aplicação Técnica de Conceitos de IA (60 pts)** | **100% Concluído** | Implementação de IA Generativa com Google Gemini, uso de *Structured Outputs* estritos via Pydantic v2, grounding contra alucinações, tratamento de prompt injection e visão computacional BCS (WSAVA). |
| **Vídeo Pitch e Demonstração Técnica (20 pts)** | **100% Concluído** | Vídeo publicado no YouTube de ~5 minutos com áudio claro, contextualização de negócio com a Clyvo Vet e demonstração funcional: **[https://youtu.be/Ahc93FSBpuU](https://youtu.be/Ahc93FSBpuU)** |
| **Organização do Repositório e Documentação (20 pts)** | **100% Concluído** | Repositório estruturado em camadas claras, README exaustivo com guias de execução passo a passo, suíte com 35 testes automatizados no Pytest e contratos de API padronizados. |

---

## 📦 Artefatos para Submissão no Portal FIAP (.zip)

O arquivo compactado `.zip` para submissão no portal educacional da FIAP contempla:
1. O arquivo `entrega.txt` na raiz com:
   * **Link do vídeo pitch publicado no YouTube (modo não listado):** [https://youtu.be/Ahc93FSBpuU](https://youtu.be/Ahc93FSBpuU)
   * **Link do repositório no GitHub:** [https://github.com/Challenge-PetTrack/DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA](https://github.com/Challenge-PetTrack/DISRUPTIVE-ARCHITECTURES-IOT-IOB-GENERATIVE-IA)
2. Código-fonte completo e limpo do projeto, contendo os módulos de firmware ESP32, fluxo do Node-RED e a API Python de IA.
