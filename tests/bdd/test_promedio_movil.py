"""Pasos BDD del pronóstico con promedio móvil.

Este archivo conecta cada frase de features/promedio_movil.feature con código.
El escenario describe el comportamiento con las palabras de Producción; aquí solo
se traduce cada frase a una llamada a la función y a una verificación.
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pronosticos import promedio_movil

# Crea una prueba de pytest por cada escenario del archivo, y una por cada fila
# de Ejemplos en los esquemas. La ruta es relativa a la carpeta de este archivo.
scenarios("features/promedio_movil.feature")


@pytest.fixture
def contexto():
    # Estado compartido entre los pasos de un mismo escenario. Cada escenario
    # recibe un diccionario nuevo, así ningún escenario depende de otro.
    return {}


# "Dada" y "Dado" son la misma palabra clave en Gherkin (Given): se escribe la que
# concuerde con la frase. El paso recibe la serie como texto y la convierte en números.
@given(parsers.parse("la serie de demanda {serie}"))
def serie_de_demanda(contexto, serie):
    contexto["serie"] = [float(valor) for valor in serie.split(",")]


# {ventana:d} captura un entero de la frase. En el esquema, <ventana> ya fue
# reemplazado por el valor de la fila (7 o 0), así que este mismo paso sirve para todas.
@when(parsers.parse("calculo el promedio móvil con una ventana de {ventana:d} periodos"))
def calcular_promedio_movil(contexto, ventana):
    # El paso "Cuando" solo ejecuta la acción y guarda lo que pasó: el resultado o
    # el error. Decidir si eso es correcto le corresponde al paso "Entonces".
    try:
        contexto["pronostico"] = promedio_movil(contexto["serie"], ventana)
    except ValueError as error:
        contexto["error"] = error


@then(parsers.parse("el pronóstico del siguiente periodo es {esperado:g} unidades"))
def pronostico_esperado(contexto, esperado):
    assert "error" not in contexto, f"Hubo un error inesperado: {contexto.get('error')}"
    assert contexto["pronostico"] == pytest.approx(esperado, abs=0.01)


@then(parsers.parse('se informa el error "{mensaje}"'))
def error_esperado(contexto, mensaje):
    assert "pronostico" not in contexto, "Se esperaba un error y la función devolvió un pronóstico"
    assert str(contexto["error"]) == mensaje
