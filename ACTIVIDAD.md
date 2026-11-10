# Actividad · Pruebas de la Unidad 2 y pipeline de CI/CD (Python)

**Modalidad:** individual
**Fecha de entrega:** [FECHA DE ENTREGA]
**Entrega:** enlace a su repositorio en GitHub, con la actividad completa y el pipeline en verde.

## Objetivo

Partir de este proyecto, que hoy solo tiene pruebas unitarias en su pipeline, y llevarlo a un pipeline completo: desarrollar una función nueva con **TDD**, ampliar las **pruebas unitarias**, escribir escenarios **BDD**, aplicar **análisis estático**, medir la **cobertura** y hacer que el **despliegue (simulado)** solo ocurra cuando todo eso pasa.

Antes de empezar, lean el [README.md](README.md): ahí están los conceptos y los comandos que se usan en cada paso.

---

## Paso 0. Tener el proyecto en su propio repositorio

**Por qué:** el pipeline corre en GitHub Actions, y para eso el código tiene que estar en un repositorio suyo.

1. Clonen el proyecto y entren a la carpeta:
   ```bash
   git clone <url-del-repositorio-del-curso>
   cd pronosticos-python
   ```
2. Quiten el remoto del curso, para no intentar subir cambios a él:
   ```bash
   git remote remove origin
   ```
3. En GitHub, creen un repositorio **vacío** (sin README, sin `.gitignore`, sin licencia) con el nombre `pronosticos-python-<su-apellido>`.
4. Conecten su repositorio y suban el código:
   ```bash
   git remote add origin https://github.com/<su-usuario>/pronosticos-python-<su-apellido>.git
   git branch -M main
   git push -u origin main
   ```
5. En GitHub, abran la pestaña **Actions**.

**Qué deben observar:** el workflow **CI/CD** corriendo con dos jobs: *Pruebas unitarias* y *Despliegue (simulado)*. Abran el job de despliegue: la última línea dice `Desplegado`.

---

## Paso 1. Conocer el punto de partida

**Por qué:** antes de cambiar algo hay que saber que el punto de partida está en verde. Si después algo se pone en rojo, sabemos que fue por nuestros cambios.

```bash
uv sync
uv run pronosticos
uv run pytest tests/unit -v
```

**Qué deben observar:** la demostración imprime MAD 11.00 y MAPE 7.62 %, y las 10 pruebas pasan.

Abran `src/pronosticos/pronosticos.py` y `tests/unit/test_mad.py`. Fíjense en tres cosas que deben repetir en sus pruebas: cada prueba verifica un solo comportamiento, los nombres dicen qué se espera, y los decimales se comparan con `pytest.approx`.

---

## Paso 2. Desarrollar una función nueva con TDD

Van a construir `suavizacion_exponencial(serie, alfa)`, que pronostica el siguiente periodo con suavización exponencial simple:

> F<sub>t+1</sub> = F<sub>t</sub> + α · (D<sub>t</sub> − F<sub>t</sub>), empezando con F<sub>2</sub> = D<sub>1</sub>

Donde F es el pronóstico, D la demanda real y α (alfa) un número entre 0 y 1.

| Serie | Alfa | Resultado esperado |
|---|---|---|
| 120, 132, 128, 141, 138, 150 | 0.3 | 137.5546 |
| 120, 132, 128, 141, 138, 150 | 0 | 120.00 (con alfa 0 el pronóstico nunca cambia) |
| 120, 132, 128, 141, 138, 150 | 1 | 150.00 (con alfa 1 el pronóstico es la última demanda) |
| cualquiera | −0.1 o 1.5 | `ValueError` con el mensaje "Alfa debe estar entre 0 y 1" |

**Por qué:** en TDD la prueba se escribe primero. Si escriben el código primero, la prueba solo confirma lo que ya hicieron; si la escriben antes, la prueba define qué debe hacer el código.

### 2.1 Rojo

Creen `tests/unit/test_suavizacion_exponencial.py` con **solo** esta prueba:

```python
import pytest

from pronosticos import suavizacion_exponencial

SERIE = [120, 132, 128, 141, 138, 150]


def test_pronostica_el_siguiente_periodo_con_alfa_0_3():
    resultado = suavizacion_exponencial(SERIE, alfa=0.3)

    assert resultado == pytest.approx(137.5546, abs=0.01)
```

```bash
uv run pytest tests/unit/test_suavizacion_exponencial.py
```

**Qué deben observar:** la prueba falla con `ImportError: cannot import name 'suavizacion_exponencial'`. Ese es el rojo: la prueba existe y la función todavía no.

Guarden este momento en el historial:

```bash
git add .
git commit -m "test: prueba en rojo para suavizacion_exponencial"
```

### 2.2 Verde

Escriban en `src/pronosticos/pronosticos.py` el código **mínimo** para que esa prueba pase, y expórtenlo en `src/pronosticos/__init__.py` (agréguenlo al `import` y a `__all__`). Corran de nuevo la prueba hasta que pase.

```bash
git add .
git commit -m "feat: implementa suavizacion_exponencial"
```

### 2.3 Más casos y refactor

Agreguen, una por una, pruebas para las filas restantes de la tabla (alfa 0, alfa 1 y alfa fuera de rango). Con cada prueba nueva repitan el ciclo: primero la ven fallar, después ajustan el código.

Cuando todas pasen, mejoren el código sin cambiar su comportamiento: nombres claros, una docstring que explique la fórmula, la validación de alfa al inicio. Después de cada cambio corran `uv run pytest tests/unit`; nunca deben quedar en rojo.

```bash
git add .
git commit -m "refactor: mejora la legibilidad de suavizacion_exponencial"
```

---

## Paso 3. Ampliar las pruebas unitarias

**Por qué:** `mape` y `debe_generar_alerta` ya existen pero no tienen pruebas. Código sin pruebas puede romperse en cualquier cambio sin que nadie lo note.

Creen `tests/unit/test_mape.py` y `tests/unit/test_alertas.py` con al menos estos casos:

| Función | Entrada | Esperado | Qué comprueba |
|---|---|---|---|
| `mape` | real `[141, 138, 150]`, pronóstico `[126.67, 133.67, 135.67]` | 7.62 | El cálculo normal |
| `mape` | real `[80, 0, 95]`, pronóstico `[80, 0, 100]` | 2.63 | El periodo con demanda 0 se excluye |
| `mape` | real `[0, 0]`, pronóstico `[10, 20]` | `ValueError` | Sin periodos válidos el MAPE no existe |
| `debe_generar_alerta` | error 12, umbral 10 | `True` | Supera el umbral |
| `debe_generar_alerta` | error 10, umbral 10 | `True` | Caso límite: igual al umbral sí alerta |
| `debe_generar_alerta` | error 7, umbral 10 | `False` | No alcanza el umbral |
| `debe_generar_alerta` | umbral 150 | `ValueError` | Umbral fuera de rango |

Calculen a mano el 2.63 antes de escribir la prueba: ¿por qué el promedio se divide entre 2 y no entre 3?

```bash
uv run pytest tests/unit -v
git add .
git commit -m "test: pruebas unitarias de mape y debe_generar_alerta"
```

---

## Paso 4. Escribir escenarios BDD

**Por qué:** la regla "el error igual al umbral sí alerta" es una decisión de negocio. En BDD la escribimos de forma que Producción pueda leerla y confirmarla, y esa misma descripción se ejecuta como prueba.

### 4.1 El escenario

Creen `tests/bdd/features/alertas.feature`. La línea `# language: es` tiene que ser la **primera** del archivo:

```gherkin
# language: es
Característica: Alertas de desviación del pronóstico
  Como planeador de producción
  Quiero recibir una alerta cuando el error del pronóstico sea alto
  Para revisar el plan de producción a tiempo

  Escenario: El error supera el umbral
    Dado un umbral de alerta de 10 %
    Cuando el error del pronóstico es 12 %
    Entonces se genera una alerta
```

Agreguen ustedes dos escenarios más: el error **igual** al umbral (10 %) y el error **por debajo** del umbral (7 %).

### 4.2 Los pasos

Creen `tests/bdd/test_alertas.py`. Este archivo conecta cada frase del escenario con código. Les damos la estructura y uno de los pasos; completen los demás:

```python
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pronosticos import debe_generar_alerta

# Genera una prueba por cada escenario del archivo.
scenarios("features/alertas.feature")


@pytest.fixture
def contexto():
    # Diccionario compartido entre los pasos de un mismo escenario.
    return {}


@given(parsers.parse("un umbral de alerta de {umbral:d} %"))
def umbral_configurado(contexto, umbral):
    contexto["umbral"] = umbral


# Completen: @when para "el error del pronóstico es {error:d} %"
# Completen: @then para "se genera una alerta"
# Completen: @then para "no se genera una alerta"
```

`parsers.parse` toma el número de la frase y lo entrega como parámetro: así un mismo paso sirve para 10 %, 12 % o 7 %.

```bash
uv run pytest tests/bdd -v
```

**Qué deben observar:** tres pruebas que pasan, una por escenario, con el nombre del escenario.

```bash
git add .
git commit -m "test: escenarios BDD de alertas de desviación"
```

---

## Paso 5. Análisis estático con Ruff

**Por qué:** el análisis estático encuentra problemas sin ejecutar el código, incluso en líneas que ninguna prueba recorre.

```bash
uv run ruff check .
uv run ruff format --check .
```

Si aparecen hallazgos en su código, corríjanlos. `uv run ruff format .` arregla el formato automáticamente; los demás hallazgos los corrigen ustedes.

Ahora provoquen un hallazgo a propósito para ver cómo se reporta. En cualquier función de `pronosticos.py` agreguen una línea `sin_usar = 1` y corran `uv run ruff check .`. Lean el mensaje: archivo, línea, código de la regla (`F841`) y descripción. Después borren la línea.

```bash
git add .
git commit -m "style: código sin hallazgos de Ruff"
```

---

## Paso 6. Cobertura de código

**Por qué:** la cobertura muestra qué partes del código ninguna prueba ejecuta.

```bash
uv run pytest tests/unit tests/bdd --cov --cov-report=term-missing
```

**Qué deben observar:** una tabla con el porcentaje por archivo y, en la columna `Missing`, las líneas sin ejecutar. Si alguna línea de `pronosticos.py` aparece ahí, escriban la prueba que la recorre (pista: revisen las validaciones que lanzan `ValueError`).

Cuando estén por encima del 90 %, comprueben el umbral:

```bash
uv run pytest tests/unit tests/bdd --cov --cov-fail-under=90
```

Con `--cov-fail-under=90`, el comando termina con error si la cobertura baja de 90 %. Eso es lo que va a usar el pipeline.

```bash
git add .
git commit -m "test: cobertura superior al 90 %"
```

---

## Paso 7. Llevar todo al pipeline

**Por qué:** hasta ahora todo depende de que alguien corra los comandos. En el pipeline se ejecutan solos en cada push, y el despliegue solo ocurre si todo pasa.

Abran `.github/workflows/ci-cd.yml`.

### 7.1 Job de análisis estático

Agreguen este job debajo de `jobs:`, al mismo nivel que `pruebas-unitarias`:

```yaml
  analisis-estatico:
    name: Análisis estático
    runs-on: ubuntu-latest
    steps:
      - name: Descargar el código
        uses: actions/checkout@v6

      - name: Instalar uv
        uses: astral-sh/setup-uv@v8.1.0
        with:
          enable-cache: true

      - name: Instalar dependencias
        run: uv sync --locked

      # Revisa errores probables, estilo y complejidad sin ejecutar el código.
      - name: Revisar el código con Ruff
        run: uv run ruff check .

      # --check solo verifica; no modifica archivos en el runner.
      - name: Verificar el formato
        run: uv run ruff format --check .
```

En YAML la indentación es parte de la sintaxis: el job tiene que quedar con dos espacios, igual que `pruebas-unitarias`.

### 7.2 Jobs de BDD y de cobertura

Siguiendo el mismo modelo, agreguen ustedes dos jobs más:

- `pruebas-bdd` (nombre: "Pruebas BDD"), que corra `uv run pytest tests/bdd -v`.
- `cobertura` (nombre: "Cobertura"), que corra `uv run pytest tests/unit tests/bdd --cov --cov-report=term-missing --cov-fail-under=90`.

Cada job corre en su propia máquina, así que cada uno necesita sus tres primeros pasos: descargar el código, instalar uv e instalar dependencias.

### 7.3 Que el despliegue dependa de todo

Cambien la línea `needs` del job `despliegue`:

```yaml
    needs: [analisis-estatico, pruebas-unitarias, pruebas-bdd, cobertura]
```

Ahora el despliegue espera a los cuatro jobs y solo corre si los cuatro terminan bien.

### 7.4 Subir y comprobar

```bash
git add .
git commit -m "ci: análisis estático, BDD y cobertura en el pipeline"
git push
```

**Qué deben observar en Actions:** los cuatro jobs de verificación corren en paralelo y, cuando todos pasan, corre el despliegue e imprime `Desplegado`. En la vista del workflow se ve el diagrama con las flechas de `needs`.

### 7.5 Comprobar que el pipeline los protege

1. Rompan algo a propósito: cambien en `pronosticos.py` el `>=` de `debe_generar_alerta` por `>`.
2. Suban el cambio:
   ```bash
   git add .
   git commit -m "prueba: cambio que rompe la regla del umbral"
   git push
   ```
3. En Actions, el pipeline queda en rojo: fallan las pruebas que verifican el caso límite y el despliegue **no corre**.
4. Reviertan el cambio y suban de nuevo:
   ```bash
   git revert HEAD --no-edit
   git push
   ```
5. El pipeline vuelve a verde y el despliegue corre.

Tomen captura de las dos ejecuciones (la roja y la verde) para el informe.

---

## Paso 8. Informe

Creen en la raíz del repositorio el archivo `INFORME_<Nombre>_<Apellido>.md` con:

1. El enlace a su repositorio.
2. Las capturas del pipeline en rojo (Paso 7.5) y en verde.
3. La salida de `uv run pytest tests/unit tests/bdd --cov --cov-report=term-missing`.
4. Respuestas breves, con sus palabras:
   - ¿Qué vieron en el rojo del Paso 2.1 y por qué es importante verlo antes de escribir el código?
   - ¿Por qué el MAPE del caso `[80, 0, 95]` se divide entre 2?
   - ¿Qué diferencia hay entre una prueba unitaria y un escenario BDD en este proyecto?
   - En el Paso 7.5, ¿qué pruebas fallaron y por qué el despliegue no corrió?

```bash
git add .
git commit -m "docs: informe de la actividad"
git push
```

---

## Checklist de entrega

- [ ] El repositorio es suyo y el último pipeline está en verde.
- [ ] `suavizacion_exponencial` existe y el historial muestra los commits de rojo, verde y refactor.
- [ ] Hay pruebas unitarias de `suavizacion_exponencial`, `mape` y `debe_generar_alerta`, con los casos de las tablas.
- [ ] `tests/bdd/features/alertas.feature` tiene `# language: es` en la primera línea y tres escenarios.
- [ ] `uv run ruff check .` y `uv run ruff format --check .` no reportan nada.
- [ ] La cobertura es de 90 % o más.
- [ ] El workflow tiene los jobs de análisis estático, pruebas unitarias, BDD, cobertura y despliegue, y el despliegue depende de los cuatro.
- [ ] El informe tiene las capturas, la salida de cobertura y las respuestas.

## Rúbrica

| Criterio | Peso |
|---|---|
| TDD: función correcta y commits de rojo, verde y refactor | 20 % |
| Pruebas unitarias: casos completos, nombres claros, tolerancia numérica | 20 % |
| BDD: escenarios correctos en español y pasos que los ejecutan | 15 % |
| Análisis estático y cobertura | 15 % |
| Pipeline: jobs correctos, `needs` del despliegue y evidencia del rojo y el verde | 20 % |
| Informe: respuestas razonadas con sus palabras | 10 % |

## Documentación oficial

- pytest: https://docs.pytest.org/
- pytest-bdd: https://pytest-bdd.readthedocs.io/
- pytest-cov: https://pytest-cov.readthedocs.io/
- Ruff, reglas: https://docs.astral.sh/ruff/rules/
- uv en GitHub Actions: https://docs.astral.sh/uv/guides/integration/github/
- Sintaxis de workflows: https://docs.github.com/actions/reference/workflow-syntax-for-github-actions
