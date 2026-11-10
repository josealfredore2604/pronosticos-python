# Análisis estático con Ruff

Guía de referencia para entender, ejecutar y modificar el análisis estático de este proyecto. Todas las salidas de consola que aparecen aquí se obtuvieron ejecutando los comandos en una copia del proyecto, con Ruff 0.17.4; los archivos de ejemplo (`ejemplos/…`, `cambios/…`) se crearon solo para provocar cada hallazgo y no forman parte del repositorio.

## 1. Qué es el análisis estático

El análisis estático revisa el código **sin ejecutarlo**. Lee el texto del programa y lo compara con un conjunto de reglas: nombres sin definir, importaciones que sobran, comparaciones que no hacen lo que parecen, funciones demasiado complejas.

Las pruebas (análisis dinámico) ejecutan el código y comparan el resultado con lo esperado. Por eso solo encuentran problemas en las líneas que recorren. El análisis estático encuentra lo que las pruebas no ven:

| Lo encuentra el análisis estático | Por qué las pruebas no lo ven |
|---|---|
| Un error en una rama que ninguna prueba recorre (por ejemplo, un nombre mal escrito dentro de un `except`) | La línea nunca se ejecuta durante las pruebas |
| Una variable calculada que nadie usa | El resultado es correcto; el problema es que sobra código |
| Una función con demasiadas decisiones | Funciona, pero es difícil de entender, de probar y de cambiar |
| Código que no sigue las convenciones del equipo | No cambia el comportamiento, cambia la mantenibilidad |

El temario ISTQB CTFL v4.0 (sección 3.1.3) lo resume así: el análisis estático encuentra defectos directamente, puede detectar defectos en caminos que se ejecutan rara vez y puede medir características que no dependen de ejecutar el código, como la mantenibilidad. Las dos técnicas se complementan; ninguna reemplaza a la otra.

## 2. La herramienta y su configuración

[Ruff](https://docs.astral.sh/ruff/) es un analizador estático (*linter*) y un formateador de Python. Se instala como dependencia de desarrollo (`[dependency-groups] dev` en `pyproject.toml`) y se ejecuta con `uv run ruff`.

Toda la configuración está en `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "C90"]

[tool.ruff.lint.mccabe]
max-complexity = 5
```

| Sección | Opción | Qué hace |
|---|---|---|
| `[tool.ruff]` | `line-length = 100` | Largo máximo de línea que exige la regla E501 y que usa el formateador para partir líneas. El valor por defecto de Ruff es 88 |
| `[tool.ruff.lint]` | `select = [...]` | Qué familias de reglas se activan. Cada código es un prefijo: `"E"` activa todas las reglas que empiezan por E |
| `[tool.ruff.lint.mccabe]` | `max-complexity = 5` | Complejidad ciclomática máxima por función para la regla C901. El valor por defecto es 10 |

Con `select` se reemplaza el conjunto por defecto de Ruff: solo quedan activas las familias de la lista. Para ver exactamente qué reglas quedaron activas:

```bash
uv run ruff check --show-settings src/pronosticos/pronosticos.py
```

En este proyecto son 64 reglas (la tabla completa está en la sección 3.6).

## 3. Las reglas configuradas

Los ejemplos de esta sección se crearon en archivos sueltos y se confirmó que Ruff reporta cada uno. Al lado de cada ejemplo está la línea que imprimió `uv run ruff check ejemplos/ --output-format concise` (formato de una línea por hallazgo: `archivo:línea:columna: CÓDIGO mensaje`). `[*]` indica que el hallazgo tiene corrección automática.

### 3.1 `line-length = 100` y la regla E501

**E501 · line-too-long.** Una línea más larga que `line-length`. Las líneas largas obligan a desplazarse en el editor y dificultan comparar versiones en una revisión.

```python
MENSAJE = "El pronóstico del periodo 7 se calcula con el promedio de los últimos tres periodos de la serie"
```

```
ejemplos/e501.py:1:101: E501 Line too long (107 > 100)
```

Corrección: partir el texto. En Python dos cadenas seguidas dentro de paréntesis se unen solas.

```python
MENSAJE = (
    "El pronóstico del periodo 7 se calcula con el promedio "
    "de los últimos tres periodos de la serie"
)
```

E501 no reporta una línea cuyo exceso es una URL (una URL no se puede partir) ni el exceso que corresponde a un comentario `# noqa`.

### 3.2 `"E"`: errores de estilo de pycodestyle

La familia E aplica la guía de estilo oficial de Python (PEP 8). Además de E501, estos son los casos que más aparecen:

**E711 · none-comparison.** Comparar con `None` usando `==`. `==` puede redefinirse en una clase; `is` compara identidad y no se puede redefinir.

```python
def describir(pronostico):
    if pronostico == None:
        return "sin pronóstico"
    return f"{pronostico:.2f}"
```

```
ejemplos/e711.py:2:22: E711 Comparison to `None` should be `cond is None`
```

Corrección: `if pronostico is None:`.

**E712 · true-false-comparison.** Comparar con `True` o `False`. La condición ya es un booleano.

```python
def mensaje(hay_alerta):
    if hay_alerta == True:
        return "Revisar el plan de producción"
    return "Sin novedades"
```

```
ejemplos/e712.py:2:8: E712 Avoid equality comparisons to `True`; use `hay_alerta:` for truth checks
```

Corrección: `if hay_alerta:`.

**E722 · bare-except.** Un `except:` sin tipo atrapa cualquier error, incluso los que nadie esperaba (y hasta `Ctrl + C`). Esconde defectos.

```python
def leer_ventana(texto):
    try:
        return int(texto)
    except:
        return 3
```

```
ejemplos/e722.py:4:5: E722 Do not use bare `except`
```

Corrección: atrapar solo el error previsto, `except ValueError:`.

**E741 · ambiguous-variable-name.** Variables llamadas `l`, `O` o `I`, que en muchas fuentes se confunden con `1` y `0`.

```python
def total(serie):
    l = len(serie)
    return sum(serie) / l
```

```
ejemplos/e741.py:2:5: E741 Ambiguous variable name: `l`
```

Corrección: un nombre que explique el contenido, `periodos = len(serie)`.

**E401 · multiple-imports-on-one-line.** Varias importaciones en una línea.

```python
import math, statistics
```

```
ejemplos/e401.py:1:1: E401 [*] Multiple imports on one line
```

Corrección: una importación por línea (`import math` y debajo `import statistics`).

**E731 · lambda-assignment.** Guardar una `lambda` en una variable. Si la función necesita nombre, se define con `def`: así aparece con su nombre en los errores y puede llevar docstring.

```python
error_absoluto = lambda real, pronostico: abs(real - pronostico)
```

```
ejemplos/e731.py:1:1: E731 Do not assign a `lambda` expression, use a `def`
```

Corrección:

```python
def error_absoluto(real, pronostico):
    return abs(real - pronostico)
```

### 3.3 `"F"`: defectos probables de Pyflakes

La familia F no revisa estilo: busca código que casi seguro es un error.

**F401 · unused-import.** Una importación que no se usa.

```python
import math


def promedio(serie):
    return sum(serie) / len(serie)
```

```
ejemplos/f401.py:1:8: F401 [*] `math` imported but unused
```

Corrección: borrar la importación.

**F841 · unused-variable.** Una variable local que se asigna y nunca se usa. Casi siempre indica que el código no hace lo que se pensó.

```python
def promedio(serie):
    total_periodos = len(serie)
    return sum(serie) / 3
```

```
ejemplos/f841.py:2:5: F841 Local variable `total_periodos` is assigned to but never used
```

Aquí el hallazgo revela un defecto real: la función divide entre 3 en lugar de entre el número de periodos. Corrección: `return sum(serie) / total_periodos`.

**F821 · undefined-name.** Un nombre que no existe, normalmente por un error al escribirlo. Si esa línea está en una rama que ninguna prueba recorre, solo el análisis estático lo detecta antes de producción.

```python
def promedio(serie):
    return sum(seire) / len(serie)
```

```
ejemplos/f821.py:2:16: F821 Undefined name `seire`
```

Corrección: `sum(serie)`.

**F811 · redefined-while-unused.** Una función (o importación) definida dos veces: la segunda reemplaza a la primera sin aviso.

```python
def promedio(serie):
    return sum(serie) / len(serie)


def promedio(serie):
    return sum(serie[-3:]) / 3
```

```
ejemplos/f811.py:5:5: F811 Redefinition of unused `promedio` from line 1: `promedio` redefined here
```

Corrección: dar a cada función su propio nombre (`promedio` y `promedio_ultimos_tres`) o borrar la que sobra.

**F541 · f-string-missing-placeholders.** Un f-string sin ninguna variable dentro: la `f` sobra o falta la variable.

```python
print(f"Pronóstico del periodo 7")
```

```
ejemplos/f541.py:1:7: F541 [*] f-string without any placeholders
```

Corrección: `print("Pronóstico del periodo 7")`.

**F632 · is-literal.** Usar `is` para comparar con un número o texto. `is` compara identidad, no valor; puede funcionar en una versión de Python y fallar en otra.

```python
def es_trimestral(ventana):
    return ventana is 3
```

```
ejemplos/f632.py:2:12: F632 [*] Use `==` to compare constant literals
```

Corrección: `return ventana == 3`.

### 3.4 `"I"`: orden de las importaciones

**I001 · unsorted-imports.** Las importaciones no siguen el orden de isort: primero la biblioteca estándar, luego las dependencias externas, luego el propio proyecto, cada grupo en orden alfabético. Un orden fijo evita conflictos de fusión y muestra de un vistazo qué usa el módulo.

```python
import statistics
import math
```

```
ejemplos/i001.py:1:1: I001 [*] Import block is un-sorted or un-formatted
```

Corrección: `import math` antes de `import statistics`. Ruff la hace solo con `--fix`.

### 3.5 `"C90"` y `max-complexity = 5`: complejidad ciclomática

**C901 · complex-structure.** La complejidad ciclomática (McCabe) cuenta los caminos independientes de una función: 1 más cada decisión (`if`, `elif`, `for`, `while`, `except`…). Con más de 5 caminos una función necesita más pruebas para cubrirse y cuesta más entenderla.

```python
def clasificar_error(error, umbral):
    if error < 0:
        return "inválido"
    if umbral <= 0:
        return "sin umbral"
    if error >= umbral * 2:
        return "crítico"
    if error >= umbral:
        return "alerta"
    if error >= umbral / 2:
        return "vigilar"
    return "normal"
```

```
ejemplos/c901.py:1:5: C901 `clasificar_error` is too complex (6 > 5)
```

Cinco `if` más uno: complejidad 6. Corrección: convertir la cadena de decisiones en datos. El comportamiento no cambia (se comprobó con 27 combinaciones de error y umbral), pero agregar un nivel ya no agrega una rama:

```python
# Cada nivel es una fila de datos y no una rama de código: agregar un nivel
# no aumenta la complejidad de la función.
NIVELES = [(2, "crítico"), (1, "alerta"), (0.5, "vigilar")]


def clasificar_error(error, umbral):
    if error < 0:
        return "inválido"
    if umbral <= 0:
        return "sin umbral"
    for proporcion, nivel in NIVELES:
        if error >= umbral * proporcion:
            return nivel
    return "normal"
```

Ruff no tiene corrección automática para C901: reducir la complejidad es una decisión de diseño.

### 3.6 Las 64 reglas activas

Esta es la lista que imprime `--show-settings` con la configuración del proyecto. El nombre en inglés es el identificador de la regla en la documentación de Ruff (`https://docs.astral.sh/ruff/rules/<nombre>/`). La última columna indica si Ruff ofrece corrección automática: *siempre*, *a veces* (según el caso) o *no*.

| Código | Nombre | Qué detecta | Corrección automática |
|---|---|---|---|
| C901 | complex-structure | Función con complejidad ciclomática mayor que `max-complexity` | no |
| E101 | mixed-spaces-and-tabs | Indentación que mezcla espacios y tabulaciones | no |
| E401 | multiple-imports-on-one-line | Varias importaciones en una sola línea | siempre |
| E402 | module-import-not-at-top-of-file | Importación que no está al inicio del módulo | a veces |
| E501 | line-too-long | Línea más larga que `line-length` | no |
| E701 | multiple-statements-on-one-line-colon | Varias sentencias en una línea con `:` (por ejemplo `if x: return`) | no |
| E702 | multiple-statements-on-one-line-semicolon | Varias sentencias en una línea separadas por `;` | no |
| E703 | useless-semicolon | Punto y coma innecesario al final de la línea | siempre |
| E711 | none-comparison | Comparación con `None` usando `==` o `!=` | siempre |
| E712 | true-false-comparison | Comparación con `True` o `False` | siempre |
| E713 | not-in-test | `not x in y` en lugar de `x not in y` | siempre |
| E714 | not-is-test | `not x is y` en lugar de `x is not y` | siempre |
| E721 | type-comparison | Comparar tipos con `==` en lugar de `isinstance` o `is` | no |
| E722 | bare-except | `except:` sin tipo de excepción | no |
| E731 | lambda-assignment | `lambda` guardada en una variable | a veces |
| E741 | ambiguous-variable-name | Variable llamada `l`, `O` o `I` | no |
| E742 | ambiguous-class-name | Clase llamada `l`, `O` o `I` | no |
| E743 | ambiguous-function-name | Función llamada `l`, `O` o `I` | no |
| E902 | io-error | Archivo que Ruff no pudo leer | no |
| F401 | unused-import | Importación sin usar | a veces |
| F402 | import-shadowed-by-loop-var | Variable de un `for` que oculta una importación | no |
| F403 | undefined-local-with-import-star | `from módulo import *`: no se sabe qué nombres llegan | no |
| F404 | late-future-import | `from __future__` que no está al inicio | no |
| F405 | undefined-local-with-import-star-usage | Nombre que podría venir de un `import *` | no |
| F406 | undefined-local-with-nested-import-star-usage | `import *` dentro de una función | no |
| F407 | future-feature-not-defined | Característica de `__future__` que no existe | no |
| F501 | percent-format-invalid-format | Formato `%` con sintaxis inválida | no |
| F502 | percent-format-expected-mapping | Formato `%` con nombres que recibe algo que no es un diccionario | no |
| F503 | percent-format-expected-sequence | Formato `%` posicional que recibe un diccionario | no |
| F504 | percent-format-extra-named-arguments | Formato `%` con nombres que sobran | siempre |
| F505 | percent-format-missing-argument | Formato `%` al que le faltan valores con nombre | no |
| F506 | percent-format-mixed-positional-and-named | Formato `%` que mezcla posiciones y nombres | no |
| F507 | percent-format-positional-count-mismatch | Formato `%` con un número de valores que no coincide | no |
| F508 | percent-format-star-requires-sequence | Formato `%` con `*` que no recibe una secuencia | no |
| F509 | percent-format-unsupported-format-character | Formato `%` con un carácter de conversión desconocido | no |
| F521 | string-dot-format-invalid-format | `.format()` con sintaxis inválida | no |
| F522 | string-dot-format-extra-named-arguments | `.format()` con argumentos con nombre que sobran | a veces |
| F523 | string-dot-format-extra-positional-arguments | `.format()` con argumentos posicionales que sobran | a veces |
| F524 | string-dot-format-missing-arguments | `.format()` al que le faltan argumentos | no |
| F525 | string-dot-format-mixing-automatic | `.format()` que mezcla `{}` y `{0}` | no |
| F541 | f-string-missing-placeholders | f-string sin variables | siempre |
| F601 | multi-value-repeated-key-literal | Diccionario con la misma clave escrita dos veces | a veces |
| F602 | multi-value-repeated-key-variable | Diccionario con la misma variable como clave dos veces | a veces |
| F621 | expressions-in-star-assignment | Demasiadas expresiones en una asignación con `*` | no |
| F622 | multiple-starred-expressions | Dos expresiones con `*` en la misma asignación | no |
| F631 | assert-tuple | `assert (condición, "mensaje")`: una tupla siempre es verdadera | no |
| F632 | is-literal | `is` o `is not` para comparar con un literal | siempre |
| F633 | invalid-print-syntax | Sintaxis de `print` de Python 2 (`print >> archivo`) | no |
| F634 | if-tuple | `if (a, b):`: una tupla no vacía siempre es verdadera | no |
| F701 | break-outside-loop | `break` fuera de un ciclo | no |
| F702 | continue-outside-loop | `continue` fuera de un ciclo | no |
| F704 | yield-outside-function | `yield` fuera de una función | no |
| F706 | return-outside-function | `return` fuera de una función | no |
| F707 | default-except-not-last | `except:` sin tipo antes de otros `except` | no |
| F722 | forward-annotation-syntax-error | Anotación de tipo entre comillas con sintaxis inválida | no |
| F811 | redefined-while-unused | Función o importación redefinida sin haberse usado | a veces |
| F821 | undefined-name | Nombre que no está definido | no |
| F822 | undefined-export | Nombre en `__all__` que el módulo no define | no |
| F823 | undefined-local | Variable local usada antes de asignarla | no |
| F841 | unused-variable | Variable local asignada y nunca usada | a veces |
| F842 | unused-annotation | Variable local anotada con un tipo y nunca usada | no |
| F901 | raise-not-implemented | `raise NotImplemented` en lugar de `NotImplementedError` | a veces |
| I001 | unsorted-imports | Bloque de importaciones desordenado | a veces |
| I002 | missing-required-import | Falta una importación obligatoria (solo si se configura `required-imports`) | siempre |

## 4. Cómo se ejecuta y cómo se lee un hallazgo

```bash
uv run ruff check .                  # analiza todo el proyecto
uv run ruff check src/pronosticos/   # solo una carpeta o un archivo
uv run ruff format --check .         # verifica el formato sin modificar archivos
```

Un hallazgo en el formato por defecto:

```
F841 Local variable `total_periodos` is assigned to but never used
 --> ejemplos/f841.py:2:5
  |
1 | def promedio(serie):
2 |     total_periodos = len(serie)
  |     ^^^^^^^^^^^^^^
3 |     return sum(serie) / 3
  |
help: Remove assignment to unused variable `total_periodos`
  |
1 | def promedio(serie):
  -     total_periodos = len(serie)
2 +     len(serie)
3 |     return sum(serie) / 3
  |
note: This is an unsafe fix and may change runtime behavior

Found 1 error.
1 unsafe fix available with `--fix --unsafe-fixes`.
```

| Parte | En el ejemplo | Qué significa |
|---|---|---|
| Regla | `F841` | Código de la regla. Se busca en https://docs.astral.sh/ruff/rules/ |
| Mensaje | `Local variable … never used` | Qué encontró, con el nombre concreto |
| Ubicación | `ejemplos/f841.py:2:5` | Archivo, línea y columna |
| Contexto | Las líneas con `^^^^` | El código señalado |
| `help` | `Remove assignment…` | La corrección que propone Ruff, si tiene |
| `note` | `unsafe fix` | La corrección podría cambiar el comportamiento: Ruff no la aplica sin permiso |

Para ver muchos hallazgos a la vez, `--output-format concise` imprime uno por línea (es el formato usado en la sección 3).

### El código de salida

El pipeline no lee los mensajes: decide con el **código de salida** del comando.

| Comando | Código | Significado |
|---|---|---|
| `ruff check` | 0 | No hay hallazgos (o todos se corrigieron con `--fix`) |
| `ruff check` | 1 | Hay al menos un hallazgo |
| `ruff check` | 2 | Ruff terminó de forma anormal: configuración inválida, opción desconocida o error interno |
| `ruff format --check` | 0 | Ningún archivo necesita formato |
| `ruff format --check` | 1 | Al menos un archivo se reformatearía |
| `ruff format --check` | 2 | Terminación anormal |

En GitHub Actions, un paso cuyo comando termina con un código distinto de 0 falla, el job queda en rojo y los jobs que dependen de él (`needs`) no se ejecutan. Por eso basta con poner `uv run ruff check .` en un paso para que un hallazgo detenga el despliegue.

## 5. Cómo corregir

### Lo que Ruff corrige solo

`--fix` aplica las correcciones **seguras**, las que no pueden cambiar el comportamiento. Con este archivo:

```python
import statistics
import math
import os


def resumen(serie, pronostico):
    diferencias = [abs(r - p) for r, p in zip(serie, pronostico)]
    if pronostico == None:
        return "sin pronóstico"
    return f"Desviación típica: {statistics.stdev(serie):.2f}, raíz de 2: {math.sqrt(2):.2f}"
```

```bash
uv run ruff check arreglo/reporte.py --output-format concise
```

```
arreglo/reporte.py:1:1: I001 [*] Import block is un-sorted or un-formatted
arreglo/reporte.py:3:8: F401 [*] `os` imported but unused
arreglo/reporte.py:7:5: F841 Local variable `diferencias` is assigned to but never used
arreglo/reporte.py:8:22: E711 Comparison to `None` should be `cond is None`
Found 4 errors.
[*] 2 fixable with `--fix` (2 unsafe fixes available with `--fix --unsafe-fixes`).
```

```bash
uv run ruff check arreglo/reporte.py --fix
```

Ruff ordenó las importaciones y borró `import os`, y terminó con `Found 4 errors (2 fixed, 2 remaining).` (código de salida 1, porque quedan hallazgos). Los dos que quedan tienen corrección **insegura**:

- **E711**: cambiar `==` por `is` es lo correcto casi siempre, pero si `pronostico` fuera un objeto que redefine `==`, el resultado podría cambiar. Ruff no lo decide por ustedes.
- **F841**: la corrección propuesta dejaría `[abs(r - p) for r, p in zip(serie, pronostico)]` como una expresión suelta. Elimina el aviso, pero no responde la pregunta importante: ¿para qué se calcularon las diferencias? Quizá faltaba usarlas.

`--fix --unsafe-fixes` aplica también las inseguras. Úsenlo solo después de leer qué va a cambiar.

### El formateador

`ruff format` reescribe el código con un estilo uniforme (espacios, saltos de línea, comillas). Ruff también formatea los bloques de código Python de los archivos Markdown (`.md`); por eso, en esta guía, el ejemplo mal formateado se muestra como texto. Con este archivo:

```text
def promedio( serie ):
    return sum( serie )/len( serie )
```

```bash
uv run ruff format --check formato/
```

```
unformatted: File would be reformatted
 --> formato/promedio.py:1:14
  |
  - def promedio( serie ):
  -     return sum( serie )/len( serie )
1 + def promedio(serie):
2 +     return sum(serie) / len(serie)
  |

1 file would be reformatted
```

```bash
uv run ruff format formato/
```

```
1 file reformatted
```

### Lo que hay que corregir a mano

Las reglas sin corrección automática (C901, E501, E722, E741, F821, entre otras) exigen una decisión: qué nombre poner, qué excepción atrapar, cómo dividir una función. Esas correcciones se hacen a mano y se verifican corriendo de nuevo las pruebas y el análisis.

## 6. Cómo cambiar la configuración

Todos los cambios de esta sección se probaron en una copia del proyecto y después se revirtieron.

### Agregar reglas

Para agregar una familia se suma su prefijo a `select`. Por ejemplo, `B` (flake8-bugbear) detecta errores de diseño frecuentes:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "C90", "B"]
```

Con un archivo de ejemplo que usa una lista como valor por defecto (la misma lista se comparte entre todas las llamadas):

```python
def agregar_periodo(valor, serie=[]):
    serie.append(valor)
    return serie
```

```bash
uv run ruff check . --output-format concise
```

```
cambios/b006.py:1:34: B006 Do not use mutable data structures for argument defaults
src/pronosticos/pronosticos.py:31:49: B905 `zip()` without an explicit `strict=` parameter
src/pronosticos/pronosticos.py:44:62: B905 `zip()` without an explicit `strict=` parameter
Found 3 errors.
3 unsafe fixes available with `--fix --unsafe-fixes`.
```

Además del ejemplo, la regla nueva encontró dos hallazgos en el código del proyecto: B905 pide indicar qué hace `zip()` si las series tienen distinto largo. Esto pasa siempre que se agrega una regla: hay que decidir qué hacer con el código que ya existe (corregirlo, o no activar esa regla) **antes** de subir el cambio, o el pipeline quedará en rojo.

También existe `extend-select`, que agrega reglas sin reemplazar la lista de `select`. Es útil para probar una regla desde la terminal sin editar el archivo:

```bash
uv run ruff check . --extend-select B
```

### Subir o bajar un umbral

La complejidad máxima está en `[tool.ruff.lint.mccabe]`. Bajarla de 5 a 2:

```toml
[tool.ruff.lint.mccabe]
max-complexity = 2
```

```bash
uv run ruff check src --output-format concise
```

```
src/pronosticos/pronosticos.py:12:5: C901 `promedio_movil` is too complex (3 > 2)
src/pronosticos/pronosticos.py:63:5: C901 `_validar_series` is too complex (3 > 2)
Found 2 errors.
```

Las dos funciones tienen dos `if`, complejidad 3. Un umbral más bajo obliga a funciones más pequeñas; uno más alto (por ejemplo 10, el valor por defecto de Ruff) tolera funciones más complejas. El umbral es una decisión del equipo y conviene anotarla en el README.

Lo mismo vale para `line-length`: cambiarlo afecta tanto a E501 como al formateador.

### Desactivar una regla en una línea concreta

Cuando un hallazgo no se va a corregir, se suprime **solo en esa línea** con `# noqa: CÓDIGO` y se deja escrito el porqué. Sin justificación, la supresión parece un descuido; con ella, quien revise el código entiende la decisión.

```python
# Los cinco niveles son la tabla que acordó Producción y se leen mejor juntos.
# Se acepta la complejidad 6 hasta revisar la tabla en el sprint 4.
def clasificar_error(error, umbral):  # noqa: C901
    if error < 0:
        return "inválido"
    if umbral <= 0:
        return "sin umbral"
    if error >= umbral * 2:
        return "crítico"
    if error >= umbral:
        return "alerta"
    if error >= umbral / 2:
        return "vigilar"
    return "normal"
```

```bash
uv run ruff check cambios/noqa.py
```

```
All checks passed!
```

Sin el comentario `# noqa: C901`, la misma función se reporta como `C901 'clasificar_error' is too complex (6 > 5)`. Reglas para usar `noqa`:

- Siempre con el código de la regla (`# noqa: C901`), nunca solo `# noqa`, que apaga **todas** las reglas en esa línea.
- Siempre con la justificación en un comentario.
- Para encontrar supresiones que ya no hacen falta, la regla RUF100 (*unused-noqa*). Por ejemplo, E501 ya ignora las líneas que terminan en una URL, así que este `noqa` sobra:

```python
# Enlace al informe de Producción donde se acordó la regla del umbral.
INFORME = "https://intranet.ejemplo.edu/produccion/acuerdos/2026/regla-del-umbral-de-alerta-igual-o-mayor.pdf"  # noqa: E501
```

```bash
uv run ruff check cambios/url.py --extend-select RUF100
```

```
RUF100 [*] Unused `noqa` directive (unused: `E501`)
 --> cambios/url.py:2:113
  |
1 | # Enlace al informe de Producción donde se acordó la regla del umbral.
2 | INFORME = "https://intranet.ejemplo.edu/produccion/acuerdos/2026/regla-del-umbral-de-alerta-igual-o-mayor.pdf"  # noqa: E501
  |                                                                                                                 ^^^^^^^^^^^^
help: Remove unused `noqa` directive
  |
1 | # Enlace al informe de Producción donde se acordó la regla del umbral.
  - INFORME = "https://intranet.ejemplo.edu/produccion/acuerdos/2026/regla-del-umbral-de-alerta-igual-o-mayor.pdf"  # noqa: E501
2 + INFORME = "https://intranet.ejemplo.edu/produccion/acuerdos/2026/regla-del-umbral-de-alerta-igual-o-mayor.pdf"
  |

Found 1 error.
[*] 1 fixable with `--fix`.
```

## 7. Integración en el editor y en Git (referencia)

Esta sección es solo de referencia: el proyecto no la necesita para funcionar y la actividad no la exige.

**Editor.** La extensión oficial para Visual Studio Code es **Ruff**, publicada por Astral (identificador `charliermarsh.ruff`). Usa la configuración de `pyproject.toml` y marca los hallazgos mientras se escribe, con las mismas reglas que el pipeline. Hay instrucciones para otros editores en https://docs.astral.sh/ruff/editors/setup/.

**Hook de Git.** Con la herramienta [pre-commit](https://pre-commit.com/), Ruff puede correr antes de cada commit y bloquearlo si hay hallazgos. La documentación de Ruff propone este `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  # Versión de Ruff.
  rev: v0.17.4
  hooks:
    # Analizador estático.
    - id: ruff-check
    # Formateador.
    - id: ruff-format
```

El hook da retroalimentación antes de subir el cambio, pero no reemplaza al pipeline: un hook se puede saltar (`git commit --no-verify`) y el pipeline no.

## 8. Documentación oficial

- Ruff: https://docs.astral.sh/ruff/
- Configuración (`select`, `line-length`, `max-complexity`): https://docs.astral.sh/ruff/settings/
- Analizador, correcciones, `noqa` y códigos de salida: https://docs.astral.sh/ruff/linter/
- Formateador: https://docs.astral.sh/ruff/formatter/
- Lista de reglas: https://docs.astral.sh/ruff/rules/
- Integración con editores: https://docs.astral.sh/ruff/editors/
- Integración con pre-commit: https://docs.astral.sh/ruff/integrations/
- PEP 8, guía de estilo de Python: https://peps.python.org/pep-0008/
