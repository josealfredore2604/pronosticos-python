"""Pruebas unitarias de promedio_movil.

Cada prueba sigue el patrón Arrange-Act-Assert (preparar, ejecutar, verificar)
y revisa un solo comportamiento. Los valores esperados salen de un cálculo
independiente hecho a mano, nunca del propio código que se está probando.
"""

import pytest

from pronosticos import promedio_movil

SERIE = [120, 132, 128, 141, 138, 150]


def test_pronostica_con_el_promedio_de_los_ultimos_periodos():
    resultado = promedio_movil(SERIE, ventana=3)

    # (141 + 138 + 150) / 3 = 143
    assert resultado == pytest.approx(143.00, abs=0.01)


def test_con_ventana_igual_a_la_serie_usa_todos_los_periodos():
    resultado = promedio_movil([100, 110, 120], ventana=3)

    assert resultado == pytest.approx(110.00, abs=0.01)


def test_con_ventana_de_un_periodo_repite_el_ultimo_valor():
    resultado = promedio_movil(SERIE, ventana=1)

    assert resultado == pytest.approx(150.00, abs=0.01)


def test_rechaza_una_ventana_mayor_que_la_serie():
    with pytest.raises(ValueError, match="menos periodos que la ventana"):
        promedio_movil([100, 110], ventana=3)


@pytest.mark.parametrize("ventana", [0, -1])
def test_rechaza_una_ventana_que_no_es_positiva(ventana):
    with pytest.raises(ValueError, match="entero positivo"):
        promedio_movil(SERIE, ventana=ventana)
