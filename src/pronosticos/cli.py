"""Punto de entrada de la línea de comandos.

Permite ver el sistema funcionando sin configurar nada: calcula el pronóstico y las
medidas de error para una serie de ejemplo y lo imprime en la terminal.
Se ejecuta con `uv run pronosticos`.
"""

from pronosticos.pronosticos import debe_generar_alerta, mad, mape, promedio_movil

SERIE_EJEMPLO = [120, 132, 128, 141, 138, 150]
VENTANA = 3
UMBRAL_ALERTA = 10


def main() -> None:
    reales = SERIE_EJEMPLO[VENTANA:]
    pronosticos = [
        promedio_movil(SERIE_EJEMPLO[:periodo], VENTANA)
        for periodo in range(VENTANA, len(SERIE_EJEMPLO))
    ]

    error_mape = mape(reales, pronosticos)
    hay_alerta = debe_generar_alerta(error_mape, UMBRAL_ALERTA)

    print(f"Serie de demanda: {SERIE_EJEMPLO}")
    print(f"Promedio móvil de {VENTANA} periodos")
    print(f"Pronóstico del periodo 7: {promedio_movil(SERIE_EJEMPLO, VENTANA):.2f}")
    print(f"MAD: {mad(reales, pronosticos):.2f}")
    print(f"MAPE: {error_mape:.2f} %")
    print(f"¿Genera alerta con umbral de {UMBRAL_ALERTA} %?: {hay_alerta}")
