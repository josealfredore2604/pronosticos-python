"""Pronósticos de demanda y medidas de error.

Este módulo reúne las reglas de negocio del sistema de predicción de demanda:
cómo se calcula un pronóstico y cómo se mide qué tan lejos quedó de la demanda real.
No depende de bases de datos ni de servicios externos, por eso se puede probar
con pruebas unitarias rápidas y aisladas.
"""

from collections.abc import Sequence


def promedio_movil(serie: Sequence[float], ventana: int) -> float:
    """Pronostica el siguiente periodo con el promedio de los últimos `ventana` valores.

    Ejemplo: con la serie [120, 132, 128, 141, 138, 150] y ventana 3, el pronóstico
    del periodo 7 es (141 + 138 + 150) / 3 = 143.
    """
    if ventana <= 0:
        raise ValueError("La ventana debe ser un entero positivo")
    if len(serie) < ventana:
        raise ValueError("La serie tiene menos periodos que la ventana configurada")

    ultimos = serie[-ventana:]
    return sum(ultimos) / ventana


def mad(real: Sequence[float], pronostico: Sequence[float]) -> float:
    """Error absoluto medio (MAD): promedio de las diferencias absolutas, en unidades."""
    _validar_series(real, pronostico)

    errores_absolutos = [abs(r - p) for r, p in zip(real, pronostico)]
    return sum(errores_absolutos) / len(errores_absolutos)


def mape(real: Sequence[float], pronostico: Sequence[float]) -> float:
    """Error porcentual absoluto medio (MAPE), expresado en porcentaje.

    Un periodo con demanda real igual a 0 no se puede expresar en porcentaje
    (dividiría entre cero), así que se excluye del cálculo. Si todos los periodos
    tienen demanda 0, el MAPE no está definido y se informa con una excepción.
    """
    _validar_series(real, pronostico)

    errores_porcentuales = [abs(r - p) / r * 100 for r, p in zip(real, pronostico) if r != 0]
    if not errores_porcentuales:
        raise ValueError("El MAPE no está definido: todos los periodos tienen demanda 0")

    return sum(errores_porcentuales) / len(errores_porcentuales)


def debe_generar_alerta(error_porcentual: float, umbral: float) -> bool:
    """Indica si un error de pronóstico debe disparar una alerta.

    Regla acordada con Producción: la alerta se activa cuando el error es mayor
    o igual al umbral. Un error exactamente igual al umbral sí alerta.
    """
    if not 0 <= umbral <= 100:
        raise ValueError("El umbral debe estar entre 0 y 100")

    return error_porcentual >= umbral


def _validar_series(real: Sequence[float], pronostico: Sequence[float]) -> None:
    if len(real) != len(pronostico):
        raise ValueError("Las series deben tener el mismo número de periodos")
    if len(real) == 0:
        raise ValueError("Se necesita al menos un periodo")
