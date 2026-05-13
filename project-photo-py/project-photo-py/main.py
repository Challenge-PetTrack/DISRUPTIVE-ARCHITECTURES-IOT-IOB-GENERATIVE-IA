from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

# ===== CONFIG =====
app = FastAPI(
    title="PetTrack BCS API",
    description="Analise de Body Condition Score do pet via foto usando GPT-4 Vision",
    version="1.0.0"
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SPRING_BOOT_URL = os.getenv("SPRING_BOOT_URL")

# FIX: client nao estava instanciado
client = OpenAI(api_key=OPENAI_API_KEY)

# ===== MODELS =====
class BCSRequest(BaseModel):
    id_pet: int
    foto: str
    especie: str
    raca: str = ""

class BCSResponse(BaseModel):
    id_pet: int
    bcs: int
    condicao: str
    recomendacao: str
    tendencia: str
    risco: str
    salvo_no_banco: bool = False

# ===== SALVAR NO ORACLE VIA SPRING BOOT =====
def salvar_bcs(id_pet: int, bcs: int, condicao: str):
    """
    Envia para o Spring Boot apenas os campos que existem em TB_BCS_HISTORICO:
    ID_BCS (sequence), NR_BCS, DS_FOTO_URL, DS_OBSERVACAO, DT_ANALISE (sysdate), ID_PET
    """
    try:
        payload = {
            "nr_bcs":        bcs,
            "ds_foto_url":   None,      # mobile envia base64, nao URL
            "ds_observacao": condicao,  # ex: "Ideal", "Acima do ideal"
            "id_pet":        id_pet
        }
        response = requests.post(
            f"{SPRING_BOOT_URL}/api/v1/bcs",
            json=payload,
            timeout=5
        )
        if response.status_code in [200, 201]:
            print(f"[BCS] Salvo no Oracle — id_pet={id_pet} bcs={bcs}")
            return True
        else:
            print(f"[BCS] Spring Boot retornou {response.status_code}: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[BCS] Spring Boot offline — nao foi possivel salvar. id_pet={id_pet} bcs={bcs}")
        return False
    except requests.exceptions.Timeout:
        print(f"[BCS] Spring Boot timeout. id_pet={id_pet} bcs={bcs}")
        return False
    except Exception as e:
        print(f"[BCS] Erro ao salvar: {str(e)}")
        return False

# ===== PROMPT VETERINARIO =====
def montar_prompt(especie: str, raca: str) -> str:
    raca_info = f" da raca {raca}" if raca else ""
    return f"""Voce e um veterinario especialista em nutricao animal.
Analise a foto deste {especie}{raca_info} e avalie o Body Condition Score (BCS) seguindo o padrao veterinario internacional de 1 a 9:

- BCS 1-2: Caquético / Muito magro — costelas, coluna e ossos muito proeminentes, sem gordura
- BCS 3-4: Abaixo do ideal — costelas facilmente palpáveis, cintura visível
- BCS 4-5: Ideal — costelas palpáveis com leve cobertura, cintura definida
- BCS 6-7: Acima do ideal — costelas com cobertura de gordura, cintura pouco visível
- BCS 8-9: Obeso — costelas difíceis de palpar, abdômen arredondado

Responda EXATAMENTE neste formato JSON, sem markdown, sem explicacoes extras:
{{
  "bcs": <numero de 1 a 9>,
  "condicao": "<Caquético|Muito magro|Abaixo do ideal|Ideal|Acima do ideal|Obeso>",
  "recomendacao": "<recomendacao nutricional especifica em portugues, max 200 caracteres>",
  "tendencia": "<estavel|subindo|descendo>",
  "risco": "<baixo|moderado|alto>"
}}"""

# ===== ENDPOINTS =====
@app.get("/")
def root():
    return {
        "projeto":     "PetTrack",
        "servico":     "BCS Analysis API",
        "versao":      "1.0.0",
        "status":      "online",
        "spring_boot": SPRING_BOOT_URL
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze-bcs", response_model=BCSResponse)
async def analyze_bcs(request: BCSRequest):
    try:
        image_data = request.foto
        if "," in image_data:
            image_data = image_data.split(",")[1]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": montar_prompt(request.especie, request.raca)
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )

        resposta_texto = response.choices[0].message.content.strip()

        if "```" in resposta_texto:
            resposta_texto = resposta_texto.split("```")[1]
            if resposta_texto.startswith("json"):
                resposta_texto = resposta_texto[4:]

        dados = json.loads(resposta_texto)

        bcs          = int(dados["bcs"])
        condicao     = dados["condicao"]
        recomendacao = dados["recomendacao"]
        tendencia    = dados.get("tendencia", "estavel")
        risco        = dados.get("risco", "baixo")

        # FIX: salvar_bcs agora recebe apenas os campos da TB_BCS_HISTORICO
        salvo = salvar_bcs(
            id_pet=request.id_pet,
            bcs=bcs,
            condicao=condicao
        )

        return BCSResponse(
            id_pet=request.id_pet,
            bcs=bcs,
            condicao=condicao,
            recomendacao=recomendacao,
            tendencia=tendencia,
            risco=risco,
            salvo_no_banco=salvo
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parsear resposta da IA: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na analise BCS: {str(e)}")

# ===== MOCK — testa sem foto e sem gastar credito =====
@app.post("/analyze-bcs/mock")
async def analyze_bcs_mock(id_pet: int = 1, especie: str = "cachorro"):
    salvo = salvar_bcs(
        id_pet=id_pet,
        bcs=5,
        condicao="Ideal"
    )
    return BCSResponse(
        id_pet=id_pet,
        bcs=5,
        condicao="Ideal",
        recomendacao="Manter dieta atual. Peso e condicao corporal adequados para a especie e raca.",
        tendencia="estavel",
        risco="baixo",
        salvo_no_banco=salvo
    )
