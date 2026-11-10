# Pronósticos de demanda · Python con uv

Proyecto base del curso de Pruebas de Software. Calcula pronósticos de demanda y mide qué tan lejos quedaron de la demanda real, con las mismas reglas del proyecto nuclear "Sistema web para la predicción de la demanda en producción industrial".

No usa bases de datos, contenedores ni servicios externos: solo Python y uv. Todo lo demás lo instala uv.

La actividad que deben desarrollar está en [ACTIVIDAD.md](ACTIVIDAD.md).

---

## Qué hace

| Función | Qué calcula | Ejemplo con la serie 120, 132, 128, 141, 138, 150 |
|---|---|---|
| `promedio_movil(serie, ventana)` | Pronóstico del siguiente periodo con el promedio de los últimos `ventana` valores | Ventana 3: (141 + 138 + 150) / 3 = 143,00 |
| `mad(real, pronostico)` | Error absoluto medio, en unidades | 11,00 para los periodos 4 a 6 |
| `mape(real, pronostico)` | Error porcentual absoluto medio; excluye los periodos con demanda 0 | 7,62 % para los periodos 4 a 6 |
| `debe_generar_alerta(error, umbral)` | Si un error debe disparar una alerta; alerta cuando el error es mayor **o igual** al umbral | Error 10 % con umbral 10 %: sí alerta |

Todo el cálculo está en `src/pronosticos/pronosticos.py`. El archivo `src/pronosticos/cli.py` solo imprime una demostración en la terminal.

## Requisitos

Solo [uv](https://docs.astral.sh/uv/getting-started/installation/). Si no tienen la versión de Python que pide el proyecto (archivo `.python-version`), uv la descarga sola.

```bash
uv --version
```

## Cómo levantarlo

```bash
git clone <url-de-este-repositorio>
cd pronosticos-python

uv sync
uv run pronosticos
```

`uv sync` crea el entorno virtual (`.venv/`) e instala exactamente las versiones de `uv.lock`. `uv run` ejecuta un comando dentro de ese entorno, sin tener que activarlo.

Salida esperada:

```
Serie de demanda: [120, 132, 128, 141, 138, 150]
Promedio móvil de 3 periodos
Pronóstico del periodo 7: 143.00
MAD: 11.00
MAPE: 7.62 %
¿Genera alerta con umbral de 10 %?: False
```

## Cómo correr las pruebas

```bash
uv run pytest tests/unit -v
```

Al iniciar el proyecto hay 10 pruebas unitarias y todas pasan.

Comandos que van a usar en la actividad:

| Comando | Qué hace |
|---|---|
| `uv run pytest tests/unit -v` | Pruebas unitarias |
| `uv run pytest tests/bdd -v` | Pruebas BDD (las crean ustedes) |
| `uv run ruff check .` | Análisis estático: errores probables, estilo, complejidad |
| `uv run ruff format --check .` | Verifica el formato sin modificar archivos |
| `uv run pytest --cov --cov-report=term-missing` | Pruebas con reporte de cobertura de líneas y ramas |

## Estructura

```
pronosticos-python/
├── .github/workflows/ci-cd.yml   Pipeline de CI/CD de GitHub Actions
├── src/pronosticos/
│   ├── __init__.py               Funciones públicas del paquete
│   ├── pronosticos.py            Reglas de negocio
│   └── cli.py                    Demostración en la terminal
├── tests/
│   ├── unit/                     Pruebas unitarias
│   └── bdd/                      Pruebas BDD (vacía al iniciar)
├── pyproject.toml                Proyecto, dependencias y configuración de las herramientas
├── uv.lock                       Versiones exactas de todas las dependencias
├── .python-version               Versión de Python del proyecto
├── README.md
└── ACTIVIDAD.md
```

## Herramientas

| Herramienta | Para qué | Dónde se configura |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | Gestiona Python, el entorno virtual y las dependencias | `pyproject.toml`, `uv.lock` |
| [pytest](https://docs.pytest.org/) | Ejecuta las pruebas | `[tool.pytest.ini_options]` |
| [pytest-bdd](https://pytest-bdd.readthedocs.io/) | Ejecuta escenarios escritos en Gherkin | Archivos `.feature` y sus pasos |
| [pytest-cov](https://pytest-cov.readthedocs.io/) | Mide la cobertura de código | `[tool.coverage.run]` |
| [Ruff](https://docs.astral.sh/ruff/) | Analizador estático y formateador | `[tool.ruff]` |

Todas son dependencias de desarrollo (`[dependency-groups] dev`): se usan para construir y verificar el software, no viajan con él.

---

## Conceptos

### Prueba unitaria

Verifica una unidad pequeña de código (una función) de forma aislada, sin base de datos, red ni archivos. Por eso es rápida y su resultado no depende del entorno. Las pruebas de este proyecto siguen el patrón **Arrange-Act-Assert**: preparar los datos, ejecutar la función y verificar el resultado, con un solo comportamiento por prueba.

Una buena prueba unitaria cumple **FIRST**: rápida (*Fast*), independiente de las demás (*Independent*), repetible en cualquier máquina (*Repeatable*), que decide sola si pasa o falla (*Self-validating*) y escrita a tiempo, junto con el código (*Timely*).

### Tolerancia numérica

Los cálculos con decimales no dan resultados exactos: `0.1 + 0.2` no es exactamente `0.3`. Por eso los resultados numéricos se comparan con una tolerancia:

```python
assert resultado == pytest.approx(11.00, abs=0.01)
```

El valor esperado siempre sale de un cálculo independiente (a mano, o con la hoja de cálculo de Producción), nunca del mismo código que se está probando.

### TDD (desarrollo guiado por pruebas)

La prueba se escribe antes que el código, en ciclos cortos:

1. **Rojo**: se escribe una prueba para un comportamiento que todavía no existe. Falla.
2. **Verde**: se escribe el código mínimo para que pase.
3. **Refactor**: se mejora el código sin cambiar su comportamiento. Las pruebas siguen en verde.

### BDD (desarrollo guiado por comportamiento)

El comportamiento esperado se describe en lenguaje natural con el formato **Dado / Cuando / Entonces** (Gherkin), antes de programarlo. Una persona del negocio puede leer el escenario y confirmar si es lo que necesita. Cada línea del escenario se conecta con código mediante un "paso" (*step*).

La primera línea del archivo `.feature` debe ser `# language: es` para usar las palabras clave en español. Si esa línea no está de primera, el archivo se lee en inglés y "Característica", "Dado" o "Cuando" no se reconocen.

### Análisis estático

Revisa el código sin ejecutarlo: encuentra variables sin usar, importaciones sobrantes, código inalcanzable, problemas de estilo y funciones demasiado complejas. Ruff mide además la **complejidad ciclomática** (número de decisiones más uno). En este proyecto el máximo permitido por función es 5.

### Cobertura de código

Indica qué porcentaje del código ejecutaron las pruebas. La **cobertura de líneas** cuenta líneas ejecutadas; la **cobertura de ramas** comprueba que cada decisión se recorrió por el lado verdadero y por el falso. Una cobertura alta no garantiza que las pruebas sean buenas, pero una cobertura baja sí señala código que nadie está probando.

`cli.py` está excluido de la medición (`omit` en `pyproject.toml`) porque solo imprime una demostración y no contiene reglas de negocio.

### CI/CD y pipeline

- **Integración continua (CI)**: cada cambio se verifica automáticamente al llegar al repositorio.
- **Despliegue continuo (CD)**: si la verificación pasa, el cambio se publica sin intervención manual. Aquí el despliegue es simulado: imprime `Desplegado` en el runner.
- **Pipeline**: la secuencia de pasos automáticos que recorre un cambio. En GitHub Actions se llama **workflow** y se define en `.github/workflows/`.

| Término | Qué es |
|---|---|
| Workflow | El archivo YAML completo |
| Evento (`on`) | Lo que dispara el workflow: un push, un pull request |
| Job | Un grupo de pasos que corre en su propia máquina virtual |
| Runner | La máquina virtual donde corre un job (`ubuntu-latest`) |
| Step | Un paso dentro de un job: una acción (`uses`) o un comando (`run`) |
| `needs` | Hace que un job espere a que otros terminen bien |

## El pipeline al iniciar

`.github/workflows/ci-cd.yml` tiene dos jobs:

1. **Pruebas unitarias**: instala uv y las dependencias, y corre `pytest tests/unit`.
2. **Despliegue (simulado)**: corre solo si el job anterior pasó y solo en un push a `main`. Imprime `Desplegado`.

En la actividad agregan análisis estático, pruebas BDD y cobertura, y hacen que el despliegue dependa de todo.

## Documentación oficial

- uv: https://docs.astral.sh/uv/
- pytest: https://docs.pytest.org/
- pytest-bdd: https://pytest-bdd.readthedocs.io/
- pytest-cov: https://pytest-cov.readthedocs.io/
- Coverage.py: https://coverage.readthedocs.io/
- Ruff: https://docs.astral.sh/ruff/
- Gherkin: https://cucumber.io/docs/gherkin/reference/
- GitHub Actions: https://docs.github.com/actions
- Acción setup-uv: https://github.com/astral-sh/setup-uv
