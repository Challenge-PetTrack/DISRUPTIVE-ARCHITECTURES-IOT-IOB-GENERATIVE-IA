from datetime import date, datetime
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, model_validator

Texto = Annotated[str, Field(max_length=4000)]
Numero = Annotated[float, Field(allow_inf_nan=False)]


class Contrato(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Perfil(Contrato):
    id: Annotated[int, Field(gt=0)]
    nome: Texto
    especie: Texto
    raca: Texto | None
    idadeAnos: Annotated[Numero, Field(ge=0)] | None
    pesoKg: Annotated[Numero, Field(gt=0)] | None


class Periodo(Contrato):
    inicioInclusivo: datetime
    fimExclusivo: datetime

    @model_validator(mode="after")
    def intervalo(self):
        if self.inicioInclusivo.tzinfo or self.fimExclusivo.tzinfo:
            raise ValueError("Periodo local deve usar o fuso informado no contexto")
        if self.inicioInclusivo >= self.fimExclusivo:
            raise ValueError("Periodo invalido")
        return self


class Alerta(Contrato):
    id: int
    tipo: Texto
    descricao: Texto | None
    valorReferencia: Numero | None
    resolvido: Literal["S", "N"]
    data: datetime


class Iot(Contrato):
    totalLeituras: Annotated[int, Field(ge=0)]
    temperaturasValidas: Annotated[int, Field(ge=0)]
    atividadesValidas: Annotated[int, Field(ge=0)]
    temperaturaMedia: Numero | None
    temperaturaMaxima: Numero | None
    atividadeMedia: Numero | None
    ultimaLeitura: datetime | None
    alertas: list[Alerta]

    @model_validator(mode="after")
    def amostras(self):
        if max(self.temperaturasValidas, self.atividadesValidas) > self.totalLeituras:
            raise ValueError("Contagens inconsistentes")
        if self.temperaturasValidas == 0 and (self.temperaturaMedia is not None or self.temperaturaMaxima is not None):
            raise ValueError("Temperatura sem amostras")
        if self.atividadesValidas == 0 and self.atividadeMedia is not None:
            raise ValueError("Atividade sem amostras")
        return self


class Avaliacao(Contrato):
    id: int
    score: Annotated[int, Field(ge=1, le=9)]
    observacao: Texto | None
    data: datetime


class Bcs(Contrato):
    ultima: Avaliacao | None
    anterior: Avaliacao | None
    tendencia: Literal["SUBINDO", "DESCENDO", "ESTAVEL", "SEM_HISTORICO_SUFICIENTE"]

    @model_validator(mode="after")
    def coerencia(self):
        if self.anterior and not self.ultima:
            raise ValueError("BCS anterior sem ultimo")
        esperado = "SEM_HISTORICO_SUFICIENTE"
        if self.ultima and self.anterior:
            esperado = "ESTAVEL" if self.ultima.score == self.anterior.score else (
                "SUBINDO" if self.ultima.score > self.anterior.score else "DESCENDO")
        if self.tendencia != esperado:
            raise ValueError("Tendencia BCS inconsistente")
        return self


class Evento(Contrato):
    id: int
    tipo: Texto
    data: datetime
    diagnostico: Texto | None
    observacao: Texto | None


class Medicamento(Contrato):
    id: int
    nome: Texto
    dosagem: Texto
    frequencia: Texto
    inicio: date
    fim: date | None


class Vacina(Contrato):
    id: int
    nome: Texto
    proximaAplicacao: date
    statusCadastro: Texto


class Historico(Contrato):
    inicioEventos: date
    ultimaConsulta: datetime | None
    eventosRecentes: list[Evento]
    medicamentosAtivos: list[Medicamento]
    limiteVacinas: date
    vacinasVencidasOuVencendo: list[Vacina]


class Clima(Contrato):
    status: Literal["DISPONIVEL", "NAO_CONFIGURADO", "FALHA_PROVEDOR", "RESPOSTA_INVALIDA", "DADO_DESATUALIZADO"]
    fonte: Texto
    localidade: Texto | None
    observadoEm: AwareDatetime | None
    temperaturaCelsius: Numero | None
    umidadePercentual: Numero | None
    condicao: Texto | None


class HealthContext(Contrato):
    versao: Literal["1.0"]
    geradoEm: AwareDatetime
    fusoHorario: Texto
    pet: Perfil
    periodoIot: Periodo
    iotRecente: Iot
    bcs: Bcs
    historico: Historico
    clima: Clima
    avisos: Annotated[list[Texto], Field(max_length=20)]
