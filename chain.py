
import logging

from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import ValidationError
from schemas import EntidadesTecnicas

# Carga las variables del .env (OPENAI_API_KEY)
load_dotenv()

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Cliente del modelo
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
logger.info("Modelo configurado: %s", model.model_name)

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Sos un asistente experto en análisis técnico de software. "
        "Tu tarea es extraer información estructurada del texto que te pasen.\n\n"
        "Reglas:\n"
        "- Identificá todas las tecnologías, lenguajes, frameworks, bases de datos "
        "y servicios que aparezcan explícitamente en el texto.\n"
        "- No inventes tecnologías que no estén mencionadas.\n"
        "- Evaluá la criticidad como 'baja', 'media' o 'alta' según el impacto "
        "descrito (por ejemplo, caídas en producción o pérdida de datos son 'alta').\n"
        "- Escribí un resumen técnico breve, de una o dos oraciones.",
    ),
    ("human", "Texto a analizar:\n\n{text}"),
])

# Cadena LCEL
structured_model = model.with_structured_output(EntidadesTecnicas)
chain = prompt | structured_model
logger.info("Cadena LCEL construida")

# Cadena con reintentos: hasta 3 intentos si la salida es inválida
chain_con_reintento = chain.with_retry(
    retry_if_exception_type=(OutputParserException, ValidationError),
    stop_after_attempt=3,
)
logger.info("Reintentos configurados: máximo 3 intentos")


class LogReintentos(BaseCallbackHandler):
    """Registra en los logs cada vez que la cadena se reintenta."""

    def on_retry(self, retry_state, **kwargs):
        error = retry_state.outcome.exception() if retry_state.outcome else None
        logger.warning(
            "Reintentando (falló el intento %d). Motivo: %s: %s",
            retry_state.attempt_number,
            type(error).__name__,
            error,
        )


async def process_text(text: str) -> EntidadesTecnicas:
    logger.info("Procesando texto (%d caracteres)", len(text))
    try:
        resultado = await chain_con_reintento.ainvoke(
            {"text": text},
            config={"callbacks": [LogReintentos()]},
        )
        logger.info(
            "Validación exitosa: criticidad=%s, %d tecnologías",
            resultado.nivel_de_criticidad.value,
            len(resultado.tecnologias),
        )
        return resultado
    except (OutputParserException, ValidationError):
        logger.error("La salida siguió siendo inválida tras agotar los reintentos", exc_info=True)
        raise
    except Exception:
        logger.exception("Error inesperado al procesar el texto")
        raise


