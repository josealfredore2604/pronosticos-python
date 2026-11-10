# Ejemplo de TDD: así se habría construido `mad`

La función `mad` (error absoluto medio) ya existe en `src/pronosticos/pronosticos.py`. Este documento reconstruye, paso a paso, cómo se habría escrito con TDD: primero la prueba, después el código mínimo para que pase y al final la mejora del diseño. Es el mismo ciclo que van a seguir en la actividad, aplicado a una función que ya conocen.

**De dónde salen las salidas.** Cada salida de consola de este documento se obtuvo de verdad, en una copia del proyecto (`/tmp/pronosticos-copia/pronosticos-python`) de la que se quitaron `mad` y sus pruebas. Se copiaron tal cual; en su equipo solo cambian la ruta de la carpeta y los tiempos. El código del proyecto no se modificó para escribir este documento.

## El requisito

Antes de escribir una sola línea hay que saber qué se espera. Producción lo describió así:

| Regla | Ejemplo |
|---|---|
| El MAD es el promedio de las diferencias absolutas entre la demanda real y el pronóstico, en unidades | real `[141, 138, 150]`, pronóstico `[126.67, 133.67, 135.67]` → (14.33 + 4.33 + 14.33) / 3 = 11.00 |
| Si el pronóstico es exacto, el MAD es 0 | real `[100, 100]`, pronóstico `[100, 100]` → 0 |
| Las dos series deben tener el mismo número de periodos | `[100, 110]` y `[100]` → `ValueError` "Las series deben tener el mismo número de periodos" |
| Se necesita al menos un periodo | `[]` y `[]` → `ValueError` "Se necesita al menos un periodo" |

Cada fila de la tabla se convierte en un ciclo rojo-verde-refactor.

---

## Ciclo 1. El cálculo con el ejemplo de Producción

### Rojo

La prueba describe el primer comportamiento con el ejemplo calculado a mano:

```python
"""Pruebas unitarias del error absoluto medio (MAD)."""

import pytest

from pronosticos import mad

REAL = [141, 138, 150]
PRONOSTICO = [126.67, 133.67, 135.67]


def test_calcula_el_error_absoluto_medio():
    resultado = mad(REAL, PRONOSTICO)

    # (14.33 + 4.33 + 14.33) / 3 = 11.00, calculado de forma independiente.
    assert resultado == pytest.approx(11.00, abs=0.01)
```

```bash
uv run pytest tests/unit/test_mad.py
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0
rootdir: /private/tmp/pronosticos-copia/pronosticos-python
configfile: pyproject.toml
plugins: cov-7.1.0, bdd-9.0.1
collected 0 items / 1 error

==================================== ERRORS ====================================
___________________ ERROR collecting tests/unit/test_mad.py ____________________
ImportError while importing test module '/private/tmp/pronosticos-copia/pronosticos-python/tests/unit/test_mad.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
tests/unit/test_mad.py:5: in <module>
    from pronosticos import mad
E   ImportError: cannot import name 'mad' from 'pronosticos' (/private/tmp/pronosticos-copia/pronosticos-python/src/pronosticos/__init__.py)
=========================== short test summary info ============================
ERROR tests/unit/test_mad.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.03s ===============================
```

La prueba no llega a ejecutarse: pytest no puede importar `mad` porque no existe. Es un rojo legítimo. pytest termina con código de salida 2 (error al recolectar las pruebas), distinto del 1 que usa cuando una prueba se ejecuta y falla.

### Verde

El código **mínimo** para que esa prueba pase es devolver el valor esperado. Se agrega en `pronosticos.py` y se exporta en `__init__.py`:

```python
def mad(real, pronostico):
    return 11.0
```

```python
from pronosticos.pronosticos import debe_generar_alerta, mad, mape, promedio_movil

__all__ = ["debe_generar_alerta", "mad", "mape", "promedio_movil"]
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0
rootdir: /private/tmp/pronosticos-copia/pronosticos-python
configfile: pyproject.toml
plugins: cov-7.1.0, bdd-9.0.1
collected 1 item

tests/unit/test_mad.py .                                                 [100%]

============================== 1 passed in 0.00s ===============================
```

### Refactor

Todavía no hay nada que mejorar: el código es una sola línea y no repite nada.

### Qué se aprende

- Ver el rojo primero demuestra que la prueba es capaz de fallar. Una prueba que nunca se vio fallar puede estar pasando por accidente (por ejemplo, porque no se ejecuta).
- Devolver una constante parece hacer trampa, pero es deliberado: obliga a que **otra prueba** exija el cálculo real. Si con una sola prueba se escribe la fórmula completa, nada garantiza que cada parte de la fórmula esté verificada.

---

## Ciclo 2. Un segundo caso obliga a calcular de verdad

### Rojo

```python
def test_es_cero_cuando_el_pronostico_es_exacto():
    assert mad([100, 100], [100, 100]) == 0
```

```bash
uv run pytest tests/unit/test_mad.py
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0
rootdir: /private/tmp/pronosticos-copia/pronosticos-python
configfile: pyproject.toml
plugins: cov-7.1.0, bdd-9.0.1
collected 2 items

tests/unit/test_mad.py .F                                                [100%]

=================================== FAILURES ===================================
_________________ test_es_cero_cuando_el_pronostico_es_exacto __________________

    def test_es_cero_cuando_el_pronostico_es_exacto():
>       assert mad([100, 100], [100, 100]) == 0
E       assert 11.0 == 0
E        +  where 11.0 = mad([100, 100], [100, 100])

tests/unit/test_mad.py:19: AssertionError
=========================== short test summary info ============================
FAILED tests/unit/test_mad.py::test_es_cero_cuando_el_pronostico_es_exacto - ...
========================= 1 failed, 1 passed in 0.01s ==========================
```

Ahora sí la prueba se ejecuta y falla: la constante 11.0 no sirve para este caso.

### Verde

Con dos ejemplos distintos, el único código que pasa los dos es el cálculo real:

```python
def mad(real, pronostico):
    errores = [abs(r - p) for r, p in zip(real, pronostico)]
    return sum(errores) / len(errores)
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0
rootdir: /private/tmp/pronosticos-copia/pronosticos-python
configfile: pyproject.toml
plugins: cov-7.1.0, bdd-9.0.1
collected 2 items

tests/unit/test_mad.py ..                                                [100%]

============================== 2 passed in 0.00s ===============================
```

### Refactor

El código es corto y claro. Se deja como está hasta tener las validaciones.

### Qué se aprende

- Esta técnica se llama **triangulación**: cada ejemplo nuevo descarta una implementación falsa. Dos ejemplos que no pueden resolverse con la misma constante obligan a escribir la fórmula.
- La salida de pytest muestra el valor obtenido (`11.0`) y el esperado (`0`). Por eso conviene que cada prueba verifique un solo comportamiento: el mensaje dice exactamente qué falló.

---

## Ciclo 3. Series de distinta longitud

### Rojo

```python
def test_rechaza_series_de_distinta_longitud():
    with pytest.raises(ValueError, match="mismo número de periodos"):
        mad([100, 110], [100])
```

```bash
uv run pytest tests/unit/test_mad.py
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0
rootdir: /private/tmp/pronosticos-copia/pronosticos-python
configfile: pyproject.toml
plugins: cov-7.1.0, bdd-9.0.1
collected 3 items

tests/unit/test_mad.py ..F                                               [100%]

=================================== FAILURES ===================================
___________________ test_rechaza_series_de_distinta_longitud ___________________

    def test_rechaza_series_de_distinta_longitud():
>       with pytest.raises(ValueError, match="mismo número de periodos"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/unit/test_mad.py:23: Failed
=========================== short test summary info ============================
FAILED tests/unit/test_mad.py::test_rechaza_series_de_distinta_longitud - Fai...
========================= 1 failed, 2 passed in 0.01s ==========================
```

`DID NOT RAISE` significa que la función terminó sin error. ¿Qué devolvió? Basta con llamarla:

```bash
uv run python -c "from pronosticos import mad; print(mad([100, 110], [100]))"
```

```
0.0
```

`zip` se detiene en la serie más corta: la función ignoró en silencio el segundo periodo y respondió que el pronóstico era perfecto. Es el peor tipo de defecto, porque no se nota.

### Verde

```python
def mad(real, pronostico):
    if len(real) != len(pronostico):
        raise ValueError("Las series deben tener el mismo número de periodos")
    errores = [abs(r - p) for r, p in zip(real, pronostico)]
    return sum(errores) / len(errores)
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0
rootdir: /private/tmp/pronosticos-copia/pronosticos-python
configfile: pyproject.toml
plugins: cov-7.1.0, bdd-9.0.1
collected 3 items

tests/unit/test_mad.py ...                                               [100%]

============================== 3 passed in 0.00s ===============================
```

### Refactor

Aún nada: hay una sola validación.

### Qué se aprende

- Las pruebas de los casos inválidos no son un trámite. Esta encontró un defecto real del código del ciclo anterior: un resultado equivocado sin ningún aviso.
- `match` compara el mensaje de la excepción. Así la prueba distingue este error de cualquier otro `ValueError`.

---

## Ciclo 4. Series vacías

### Rojo

```python
def test_rechaza_series_vacias():
    with pytest.raises(ValueError, match="al menos un periodo"):
        mad([], [])
```

```bash
uv run pytest tests/unit/test_mad.py
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0
rootdir: /private/tmp/pronosticos-copia/pronosticos-python
configfile: pyproject.toml
plugins: cov-7.1.0, bdd-9.0.1
collected 4 items

tests/unit/test_mad.py ...F                                              [100%]

=================================== FAILURES ===================================
__________________________ test_rechaza_series_vacias __________________________

    def test_rechaza_series_vacias():
        with pytest.raises(ValueError, match="al menos un periodo"):
>           mad([], [])

tests/unit/test_mad.py:29:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

real = [], pronostico = []

    def mad(real, pronostico):
        if len(real) != len(pronostico):
            raise ValueError("Las series deben tener el mismo número de periodos")
        errores = [abs(r - p) for r, p in zip(real, pronostico)]
>       return sum(errores) / len(errores)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       ZeroDivisionError: division by zero

src/pronosticos/pronosticos.py:31: ZeroDivisionError
=========================== short test summary info ============================
FAILED tests/unit/test_mad.py::test_rechaza_series_vacias - ZeroDivisionError...
========================= 1 failed, 3 passed in 0.01s ==========================
```

Esta vez sí hubo una excepción, pero no la acordada: `ZeroDivisionError` en lugar de `ValueError`. Para quien llama a la función, un `ZeroDivisionError` no explica qué hizo mal; el mensaje acordado sí.

### Verde

```python
def mad(real, pronostico):
    if len(real) != len(pronostico):
        raise ValueError("Las series deben tener el mismo número de periodos")
    if len(real) == 0:
        raise ValueError("Se necesita al menos un periodo")
    errores = [abs(r - p) for r, p in zip(real, pronostico)]
    return sum(errores) / len(errores)


def mape(real: Sequence[float], pronostico: Sequence[float]) -> float:
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0
rootdir: /private/tmp/pronosticos-copia/pronosticos-python
configfile: pyproject.toml
plugins: cov-7.1.0, bdd-9.0.1
collected 4 items

tests/unit/test_mad.py ....                                              [100%]

============================== 4 passed in 0.00s ===============================
```

### Qué se aprende

- La prueba no solo exige que haya un error: exige **el** error acordado, con su tipo y su mensaje. Eso es parte del contrato de la función.
- Con este ciclo la tabla del requisito queda cubierta. Ahora se puede mejorar el diseño con la tranquilidad de que cuatro pruebas vigilan el comportamiento.

---

## Refactor final

Con todas las pruebas en verde se mejora el código **sin cambiar lo que hace**:

1. **Quitar la duplicación.** Las dos validaciones son idénticas a las que necesita `mape`, que ya las tiene en `_validar_series`. Se reutiliza esa función en lugar de mantener dos copias de la misma regla.
2. **Nombres que explican.** `errores` pasa a ser `errores_absolutos`: el nombre dice qué contiene.
3. **Tipos y docstring.** Las anotaciones (`Sequence[float]`) documentan qué recibe y qué devuelve, y la docstring explica qué es el MAD.

Antes:

```python
def mad(real, pronostico):
    if len(real) != len(pronostico):
        raise ValueError("Las series deben tener el mismo número de periodos")
    if len(real) == 0:
        raise ValueError("Se necesita al menos un periodo")
    errores = [abs(r - p) for r, p in zip(real, pronostico)]
    return sum(errores) / len(errores)


def mape(real: Sequence[float], pronostico: Sequence[float]) -> float:
```

Después (es exactamente el código que hoy tiene el proyecto):

```python
def mad(real: Sequence[float], pronostico: Sequence[float]) -> float:
    """Error absoluto medio (MAD): promedio de las diferencias absolutas, en unidades."""
    _validar_series(real, pronostico)

    errores_absolutos = [abs(r - p) for r, p in zip(real, pronostico)]
    return sum(errores_absolutos) / len(errores_absolutos)
```

Después del refactor se corren **todas** las pruebas unitarias, no solo las de `mad`, porque `_validar_series` también la usa `mape`:

```bash
uv run pytest tests/unit -v
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.2.0, pluggy-1.7.0 -- /private/tmp/pronosticos-copia/pronosticos-python/.venv/bin/python
cachedir: .pytest_cache
rootdir: /private/tmp/pronosticos-copia/pronosticos-python
configfile: pyproject.toml
plugins: cov-7.1.0, bdd-9.0.1
collecting ... collected 10 items

tests/unit/test_mad.py::test_calcula_el_error_absoluto_medio PASSED      [ 10%]
tests/unit/test_mad.py::test_es_cero_cuando_el_pronostico_es_exacto PASSED [ 20%]
tests/unit/test_mad.py::test_rechaza_series_de_distinta_longitud PASSED  [ 30%]
tests/unit/test_mad.py::test_rechaza_series_vacias PASSED                [ 40%]
tests/unit/test_promedio_movil.py::test_pronostica_con_el_promedio_de_los_ultimos_periodos PASSED [ 50%]
tests/unit/test_promedio_movil.py::test_con_ventana_igual_a_la_serie_usa_todos_los_periodos PASSED [ 60%]
tests/unit/test_promedio_movil.py::test_con_ventana_de_un_periodo_repite_el_ultimo_valor PASSED [ 70%]
tests/unit/test_promedio_movil.py::test_rechaza_una_ventana_mayor_que_la_serie PASSED [ 80%]
tests/unit/test_promedio_movil.py::test_rechaza_una_ventana_que_no_es_positiva[0] PASSED [ 90%]
tests/unit/test_promedio_movil.py::test_rechaza_una_ventana_que_no_es_positiva[-1] PASSED [100%]

============================== 10 passed in 0.01s ==============================
```

Y el análisis estático, para confirmar que el refactor no introdujo problemas de estilo:

```bash
uv run ruff check .
```

```
All checks passed!
```

### Qué se aprende

- El refactor es seguro **porque** hay pruebas. Sin ellas, cambiar las validaciones por `_validar_series` sería una apuesta.
- Refactorizar no es agregar funciones nuevas. Si durante el refactor aparece un comportamiento nuevo, se vuelve al rojo con una prueba para ese comportamiento.

---

## El historial que deja el ciclo

En la actividad se pide que el historial de commits muestre las tres fases. Para `mad`, un historial razonable sería:

| Commit | Fase | Estado de las pruebas |
|---|---|---|
| `test: prueba en rojo para mad` | Rojo del ciclo 1 | 1 falla |
| `feat: mad devuelve el resultado del ejemplo` | Verde del ciclo 1 | todas pasan |
| `test: mad es cero con un pronóstico exacto` | Rojo del ciclo 2 | 1 falla |
| `feat: mad calcula el promedio de los errores absolutos` | Verde del ciclo 2 | todas pasan |
| `test: mad rechaza series de distinta longitud` | Rojo del ciclo 3 | 1 falla |
| `feat: mad valida la longitud de las series` | Verde del ciclo 3 | todas pasan |
| `test: mad rechaza series vacías` | Rojo del ciclo 4 | 1 falla |
| `feat: mad exige al menos un periodo` | Verde del ciclo 4 | todas pasan |
| `refactor: mad reutiliza _validar_series` | Refactor | todas pasan |

No es obligatorio un commit por fase de cada ciclo; lo importante es que el historial permita ver que la prueba existió antes que el código.

## Resumen

| Fase | Qué se hace | Cómo se sabe que terminó |
|---|---|---|
| Rojo | Se escribe una prueba para un comportamiento que todavía no existe | La prueba falla, y falla por la razón esperada |
| Verde | Se escribe el código mínimo para que pase | Todas las pruebas pasan |
| Refactor | Se mejora el diseño sin cambiar el comportamiento | Todas las pruebas siguen pasando y el análisis estático no reporta nada |
