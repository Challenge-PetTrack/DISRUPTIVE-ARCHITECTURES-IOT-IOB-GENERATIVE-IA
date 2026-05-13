#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ===== WIFI =====
const char* ssid     = "Wokwi-GUEST";
const char* password = "";

// ===== MQTT =====
const char* mqtt_server = "c9d03d6e4bf24b29b2a8b4fa3572a6b3.s1.eu.hivemq.cloud";
const int   mqtt_port   = 8883;
const char* mqtt_user   = "rm563719";
const char* mqtt_pass   = "Fiapinhos12@";
const char* client_id   = "pettrack-collar-001";

// ===== ID DO PET (fixo para simulacao) =====
const int ID_PET = 1;

// ===== TOPICOS =====
char topic_temp[60];
char topic_atv[60];
char topic_alerta[60];

// ===== PINOS =====
#define PIN_TEMP 34   // Potenciometro simulando temperatura
#define PIN_ATV  35   // Potenciometro simulando atividade

// ===== CONTROLE DE SEDENTARISMO =====
int leituras_baixas = 0;
const int LIMITE_SEDENTARISMO = 3;

// ===== CLIENTES =====
WiFiClientSecure espClient;
PubSubClient client(espClient);

// ===== WIFI =====
void setup_wifi() {
  Serial.print("Conectando WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi OK — IP: " + WiFi.localIP().toString());
}

// ===== MQTT =====
void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando MQTT...");
    if (client.connect(client_id, mqtt_user, mqtt_pass)) {
      Serial.println(" conectado!");
    } else {
      Serial.print(" falha rc=");
      Serial.print(client.state());
      Serial.println(" tentando em 3s");
      delay(3000);
    }
  }
}

// ===== LER TEMPERATURA =====
// Potenciometro 0-4095 mapeado para 35.0 a 42.0 graus Celsius
float lerTemperatura() {
  int raw = analogRead(PIN_TEMP);
  float temp = 35.0 + (raw / 4095.0) * 7.0;
  return temp;
}

// ===== LER ATIVIDADE =====
// Potenciometro 0-4095 mapeado para 0 a 100 passos/min
float lerAtividade() {
  int raw = analogRead(PIN_ATV);
  float atv = (raw / 4095.0) * 100.0;
  return atv;
}

// ===== PUBLICAR TEMPERATURA =====
void publicarTemperatura(float temp) {
  StaticJsonDocument<200> doc;
  doc["id_pet"]  = ID_PET;
  doc["sensor"]  = "temperatura";
  doc["valor"]   = serialized(String(temp, 1));
  doc["unidade"] = "C";

  char buffer[200];
  serializeJson(doc, buffer);
  client.publish(topic_temp, buffer);

  Serial.println("[TEMP] " + String(buffer));
}

// ===== PUBLICAR ATIVIDADE =====
void publicarAtividade(float atv) {
  StaticJsonDocument<200> doc;
  doc["id_pet"]  = ID_PET;
  doc["sensor"]  = "atividade";
  doc["valor"]   = serialized(String(atv, 0));
  doc["unidade"] = "passos/min";

  char buffer[200];
  serializeJson(doc, buffer);
  client.publish(topic_atv, buffer);

  Serial.println("[ATV]  " + String(buffer));
}

// ===== PUBLICAR ALERTA =====
void publicarAlerta(const char* tipo, float valor, const char* descricao) {
  StaticJsonDocument<256> doc;
  doc["id_pet"]    = ID_PET;
  doc["tipo"]      = tipo;
  doc["valor"]     = serialized(String(valor, 1));
  doc["descricao"] = descricao;

  char buffer[256];
  serializeJson(doc, buffer);
  client.publish(topic_alerta, buffer);

  Serial.println("[ALERTA] " + String(buffer));
}

// ===== VERIFICAR ALERTAS =====
void verificarAlertas(float temp, float atv) {

  // Alerta de FEBRE
  if (temp > 39.5) {
    publicarAlerta("FEBRE", temp, "Temperatura corporal acima do normal. Consulte um veterinario.");
  }

  // Controle de SEDENTARISMO (3 leituras consecutivas abaixo de 20)
  if (atv < 20.0) {
    leituras_baixas++;
    if (leituras_baixas >= LIMITE_SEDENTARISMO) {
      publicarAlerta("SEDENTARISMO", atv, "Atividade fisica muito baixa por periodo prolongado.");
      leituras_baixas = 0; // reset para nao ficar spamando
    }
  } else {
    leituras_baixas = 0; // reset se voltou a se mexer
  }
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  delay(500);

  // Monta os topicos com id_pet
  sprintf(topic_temp,   "pettrack/collar/%d/temperatura", ID_PET);
  sprintf(topic_atv,    "pettrack/collar/%d/atividade",   ID_PET);
  sprintf(topic_alerta, "pettrack/collar/%d/alerta",      ID_PET);

  Serial.println("=== PetTrack Collar IoT ===");
  Serial.println("Topicos:");
  Serial.println("  " + String(topic_temp));
  Serial.println("  " + String(topic_atv));
  Serial.println("  " + String(topic_alerta));

  setup_wifi();

  espClient.setInsecure(); // TLS sem verificacao de certificado (ok para dev)
  client.setServer(mqtt_server, mqtt_port);
}

// ===== LOOP =====
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  float temp = lerTemperatura();
  float atv  = lerAtividade();

  Serial.println("-----");
  publicarTemperatura(temp);
  publicarAtividade(atv);
  verificarAlertas(temp, atv);

  delay(3000); // publica a cada 3 segundos
}
