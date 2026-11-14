import asyncio

from chain import process_text

EJEMPLOS = [
    "El servicio de pagos en Python/FastAPI cae con timeouts hacia PostgreSQL "
    "y Redis cada vez que hay picos de tráfico en producción.",
    "ERROR 2026-11-14 10:32:11 - Connection refused: Kafka broker no responde "
    "en el cluster de staging. El consumer en Node.js reintentó 5 veces.",
]


async def main():
    for texto in EJEMPLOS:
        resultado = await process_text(texto)
        print(resultado.model_dump())
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())