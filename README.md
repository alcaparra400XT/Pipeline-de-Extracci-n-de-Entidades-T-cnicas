# Pipeline de Extracción de Entidades Técnicas

Pipeline asíncrono que recibe un párrafo de texto sin procesar (una descripción de arquitectura, un log de error, etc.) y devuelve un objeto **validado con Pydantic** con las entidades técnicas extraídas.

Construido con **LangChain (LCEL)**, **Pydantic** y **OpenAI**.

## ¿Qué extrae?

Dado un texto, devuelve un objeto `EntidadesTecnicas` con:

| Campo | Tipo | Descripción |
|---|---|---|
| `tecnologias` | `list[str]` | Tecnologías, lenguajes, frameworks, bases de datos o servicios mencionados |
| `nivel_de_criticidad` | `baja` \| `media` \| `alta` | Criticidad del problema o sistema descrito |
| `resumen_tecnico` | `str` | Resumen técnico breve del texto |

## Estructura del proyecto

```
.
├── schemas.py          # Modelo Pydantic (EntidadesTecnicas y enum NivelCriticidad)
├── chain.py            # Prompt, cadena LCEL, reintentos y process_text()
├── main.py             # Mini-script de prueba con ejemplos
├── requirements.txt    # Dependencias
├── .env                # Variables de entorno (NO se sube al repositorio)
└── README.md
```

## Cómo funciona

1. **Esquema (`schemas.py`)**: define la estructura de salida con Pydantic. El campo `nivel_de_criticidad` es un `Enum`, así que cualquier valor distinto de `baja`, `media` o `alta` se rechaza.
2. **Prompt (`chain.py`)**: un `ChatPromptTemplate` con un mensaje de sistema (instrucciones de extracción) y un mensaje humano con la variable `{text}`.
3. **Cadena LCEL**: `prompt | model.with_structured_output(EntidadesTecnicas)`. El modelo devuelve directamente un objeto `EntidadesTecnicas` ya validado.
4. **Resiliencia**: la cadena se envuelve con `.with_retry()` y reintenta hasta 3 veces (el intento original más 2 reintentos) si la salida es un JSON mal formado (`OutputParserException`) o no cumple el esquema (`ValidationError`). No se reintenta ante otros errores, como falta de créditos o de red.
5. **Función asíncrona**: `process_text(text: str)` ejecuta la cadena con `.ainvoke()` y registra en los logs el inicio, la validación exitosa, los reintentos y los errores.

## Requisitos

- Python 3.10 o superior
- Una API key de OpenAI con crédito disponible

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/alcaparra400XT/https://github.com/alcaparra400XT/Pipeline-de-Extracci-n-de-Entidades-T-cnicas.git
cd TU_REPO
```

2. Crear y activar un entorno virtual:

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Mac / Linux
source .venv/bin/activate
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

4. Crear un archivo `.env` en la raíz del proyecto con tu API key:

```
OPENAI_API_KEY=tu_api_key_aqui
```

## Uso

### Ejecutar el script de prueba

```bash
python main.py
```

Procesa dos textos de ejemplo e imprime el resultado de cada uno.

### Usar `process_text` desde tu propio código

```python
import asyncio
from chain import process_text

async def ejemplo():
    resultado = await process_text(
        "El servicio en FastAPI no conecta con Redis."
    )
    print(resultado.tecnologias)
    print(resultado.nivel_de_criticidad)
    print(resultado.resumen_tecnico)

asyncio.run(ejemplo())
```

## Ejemplo de salida

Ejemplo ilustrativo (el texto exacto puede variar según el modelo):

```python
{
    "tecnologias": ["FastAPI", "Redis"],
    "nivel_de_criticidad": "alta",
    "resumen_tecnico": "El servicio en FastAPI no logra conectar con Redis."
}
```

## Logs

El proyecto usa el módulo `logging` de Python. Durante la ejecución se pueden observar:

- `INFO`: configuración del modelo, construcción de la cadena, inicio del procesamiento y validación exitosa.
- `WARNING`: cada reintento automático, con el número de intento y el motivo del fallo.
- `ERROR`: cuando la salida sigue siendo inválida tras agotar los reintentos, o ante un error inesperado.

## Cambiar de modelo o de proveedor

- **Otro modelo de OpenAI**: modificar el parámetro `model` en `chain.py`.
- **Anthropic**: instalar `langchain-anthropic`, reemplazar `ChatOpenAI` por `ChatAnthropic` en `chain.py` y definir `ANTHROPIC_API_KEY` en el `.env`. El resto de la cadena no cambia.

## Seguridad

El archivo `.env` contiene credenciales y está excluido del repositorio mediante `.gitignore`. Nunca subas tu API key a GitHub.
