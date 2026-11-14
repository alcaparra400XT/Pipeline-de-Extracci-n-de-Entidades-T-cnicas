from enum import Enum
from pydantic import BaseModel, Field


class NivelCriticidad(str, Enum):
    baja = "baja"
    media = "media"
    alta = "alta"


class EntidadesTecnicas(BaseModel):
    tecnologias: list[str] = Field(
        description="Tecnologías, lenguajes, frameworks, bases de datos o servicios mencionados en el texto"
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        description="Nivel de criticidad del problema o sistema descrito: baja, media o alta"
    )
    resumen_tecnico: str = Field(
        description="Resumen técnico breve del texto, en una o dos oraciones"
    )