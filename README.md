# Pronósticos de demanda · Python con uv

Proyecto base del curso de Pruebas de Software. Calcula pronósticos de demanda y mide qué tan lejos quedaron de la demanda real, con las mismas reglas del proyecto nuclear "Sistema web para la predicción de la demanda en producción industrial".

No usa bases de datos, contenedores ni servicios externos: solo Python y uv. Todo lo demás lo instala uv.

La actividad que deben desarrollar está en [ACTIVIDAD.md](ACTIVIDAD.md) (en GitHub: https://github.com/josealfredore2604/pronosticos-python/blob/main/ACTIVIDAD.md).

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
git clone https://github.com/josealfredore2604/pronosticos-python
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

Al iniciar el proyecto hay 10 pruebas unitarias y 3 pruebas BDD (los escenarios del ejemplo de promedio móvil), y todas pasan.

Comandos que van a usar en la actividad:

| Comando | Qué hace |
|---|---|
| `uv run pytest tests/unit -v` | Pruebas unitarias |
| `uv run pytest tests/bdd -v` | Pruebas BDD: el ejemplo de promedio móvil y los escenarios que ustedes agreguen |
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
│   └── bdd/                      Pruebas BDD
│       ├── features/             Escenarios en Gherkin (promedio_movil.feature)
│       └── test_promedio_movil.py  Pasos del ejemplo de promedio móvil
├── docs/
│   ├── EJEMPLO_TDD.md            Ciclo rojo-verde-refactor de mad, con salidas reales
│   └── ANALISIS_ESTATICO.md      Guía de Ruff: reglas, ejecución y configuración
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

El ciclo completo, reconstruido paso a paso con `mad` y con las salidas reales de la consola, está en [docs/EJEMPLO_TDD.md](docs/EJEMPLO_TDD.md).

### BDD (desarrollo guiado por comportamiento)

El comportamiento esperado se describe en lenguaje natural con el formato **Dado / Cuando / Entonces** (Gherkin), antes de programarlo. Una persona del negocio puede leer el escenario y confirmar si es lo que necesita. Cada línea del escenario se conecta con código mediante un "paso" (*step*).

La primera línea del archivo `.feature` debe ser `# language: es` para usar las palabras clave en español. Si esa línea no está de primera, el archivo se lee en inglés y "Característica", "Dado" o "Cuando" no se reconocen.

El proyecto trae un ejemplo funcionando: `tests/bdd/features/promedio_movil.feature` describe el pronóstico con promedio móvil y `tests/bdd/test_promedio_movil.py` conecta cada frase con el código. Tiene tres casos: el cálculo con la serie 120, 132, 128, 141, 138, 150 y ventana 3 (resultado 143), una ventana mayor que la serie y una ventana de 0, estos dos con error. Se ejecuta con `uv run pytest tests/bdd -v`.

Los dos casos de error están escritos como un **Esquema del escenario**: un solo escenario con marcadores (`<ventana>`, `<mensaje>`) y una tabla de **Ejemplos**. Gherkin lo ejecuta una vez por cada fila de la tabla, con los valores de esa fila. Sirve cuando varios casos siguen los mismos pasos y solo cambian los datos. pytest-bdd convierte cada fila en una prueba aparte; por eso `uv run pytest tests/bdd -v` muestra tres pruebas para dos escenarios.

### Pruebas funcionales

Una prueba funcional verifica **qué** hace el sistema: compara su comportamiento con el requisito, sin mirar cómo está programado. Es una prueba de **caja negra**. Quien la diseña parte del requisito ("con la serie 120, 132, 128, 141, 138, 150 y una ventana de 3 periodos, el pronóstico del periodo 7 es 143"), elige las entradas y los resultados esperados, y no necesita leer el código.

Los escenarios BDD de este proyecto son pruebas funcionales: cada escenario es un requisito de Producción, escrito en Gherkin y ejecutado contra el sistema. El ejemplo está en `tests/bdd/features/promedio_movil.feature`.

| | Prueba unitaria | Prueba funcional (escenario BDD) |
|---|---|---|
| Pregunta que responde | ¿Esta función hace bien su trabajo? | ¿El sistema cumple el requisito? |
| Se diseña a partir de | El código: quien la escribe conoce la función, sus ramas y sus validaciones | El requisito: no hace falta mirar el código |
| Quién la puede leer | El equipo de desarrollo | Desarrollo, pruebas y Producción |
| Lenguaje | Python | Gherkin, en español |
| Si falla, indica | Qué función y qué línea fallaron | Qué regla del negocio dejó de cumplirse |

Las dos pueden verificar la misma regla. En `tests/unit/test_promedio_movil.py`, `test_con_ventana_de_un_periodo_repite_el_ultimo_valor` comprueba un caso límite que sale de conocer cómo está escrita la función (el corte `serie[-ventana:]` con ventana 1). El escenario de promedio móvil, en cambio, verifica la regla tal como la dijo Producción y seguiría siendo válido aunque `promedio_movil` se reescribiera por completo.

En este proyecto los escenarios llaman directamente a las funciones de cálculo. Verificar la misma regla a través de la aplicación completa (en este proyecto, la demostración de `uv run pronosticos`; en los proyectos del curso que tienen API, una petición HTTP) también es una prueba funcional, pero además comprueba que las piezas del sistema funcionan juntas: es una **prueba de integración**, y las pruebas de integración, incluidas las de una API HTTP, se ven en la Unidad 3. Por eso este proyecto no las incluye.

### Análisis estático

Revisa el código sin ejecutarlo: encuentra variables sin usar, importaciones sobrantes, código inalcanzable, problemas de estilo y funciones demasiado complejas. Ruff mide además la **complejidad ciclomática** (número de decisiones más uno). En este proyecto el máximo permitido por función es 5.

Qué reglas están activas, qué detecta cada una, cómo se lee un hallazgo y cómo se cambia la configuración: [docs/ANALISIS_ESTATICO.md](docs/ANALISIS_ESTATICO.md).

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

`.github/workflows/ci-cd.yml` tiene tres jobs:

1. **Pruebas unitarias**: instala uv y las dependencias, y corre `pytest tests/unit`.
2. **Pruebas BDD**: instala uv y las dependencias, y corre `pytest tests/bdd -v`. Ejecuta el ejemplo de promedio móvil y, cuando los agreguen, sus escenarios de alertas.
3. **Despliegue (simulado)**: corre solo si los dos jobs anteriores pasaron y solo en un push a `main`. Imprime `Desplegado`.

Los dos jobs de pruebas corren en paralelo, cada uno en su propia máquina. En la actividad agregan análisis estático y cobertura, y hacen que el despliegue dependa de los cuatro jobs de verificación.

## Clean Code

*Clean Code* (código limpio) es código que otra persona puede leer, entender y cambiar sin miedo. No es una herramienta: es un conjunto de principios que el análisis estático ayuda a vigilar y que las revisiones estáticas comprueban.

| Principio | Qué significa | Dónde se ve en este proyecto |
|---|---|---|
| Nombres que explican | El nombre dice qué es o qué hace, sin necesidad de un comentario | `errores_absolutos` dice qué contiene la lista; `debe_generar_alerta` se lee como una pregunta y devuelve `True` o `False` |
| Una sola responsabilidad | Cada función hace una cosa; si hace dos, se divide | `promedio_movil` solo calcula; `_validar_series` solo valida; `cli.py` solo imprime. Ninguna función de `pronosticos.py` imprime ni lee archivos |
| Sin duplicación | Cada regla está escrita en un solo lugar | `mad` y `mape` necesitan las mismas validaciones y las toman de `_validar_series`, en lugar de repetirlas |
| Sin números mágicos | Un número que significa algo para el negocio lleva nombre | `cli.py` no escribe `3` ni `10` sueltos: usa `VENTANA = 3` y `UMBRAL_ALERTA = 10`. El `100` de `mape` se deja escrito porque es la definición de porcentaje, no un parámetro del negocio |
| Comentarios que explican el porqué | El código ya dice qué hace; el comentario dice por qué se decidió así | la docstring de `debe_generar_alerta` no repite que compara con `>=`: explica que es una regla acordada con Producción y que un error igual al umbral sí alerta |
| Manejo explícito de errores | Un dato inválido produce un error con un mensaje claro, no un resultado silencioso ni un error genérico | con series vacías, `mad` lanza `ValueError("Se necesita al menos un periodo")` en lugar de dejar escapar un `ZeroDivisionError` que no explica nada (ver el ciclo 4 de `docs/EJEMPLO_TDD.md`) |

Un ejemplo tomado del propio código:

```python
def mad(real: Sequence[float], pronostico: Sequence[float]) -> float:
    """Error absoluto medio (MAD): promedio de las diferencias absolutas, en unidades."""
    _validar_series(real, pronostico)

    errores_absolutos = [abs(r - p) for r, p in zip(real, pronostico)]
    return sum(errores_absolutos) / len(errores_absolutos)


def debe_generar_alerta(error_porcentual: float, umbral: float) -> bool:
    """Indica si un error de pronóstico debe disparar una alerta.

    Regla acordada con Producción: la alerta se activa cuando el error es mayor
    o igual al umbral. Un error exactamente igual al umbral sí alerta.
    """
    if not 0 <= umbral <= 100:
        raise ValueError("El umbral debe estar entre 0 y 100")

    return error_porcentual >= umbral
```

En estas dos funciones se ven cinco de los seis principios: nombres que explican (`errores_absolutos`, `debe_generar_alerta`), una sola responsabilidad (calcular, sin imprimir), ninguna duplicación (`_validar_series`), un comentario que explica el porqué (la regla acordada) y errores explícitos con un mensaje que dice qué está mal.

## Revisiones estáticas

Una **revisión** es el examen de un producto de trabajo (código, requisitos, escenarios, un plan de pruebas) hecho **por personas**, sin ejecutarlo. Es estática, como el análisis estático, pero no la hace una herramienta:

| | Análisis estático automatizado | Revisión estática |
|---|---|---|
| Quién revisa | Una herramienta (Ruff, en este proyecto) | Personas |
| Qué revisa | Solo código, contra reglas fijas | Cualquier producto de trabajo: código, requisitos, escenarios, documentos |
| Qué encuentra | Defectos que se pueden describir con una regla: variables sin usar, complejidad, nombres | Además, lo que una regla no ve: un requisito ambiguo, un caso que falta, un nombre que confunde, un diseño difícil de cambiar |
| Cuándo | En cada cambio, en segundos (en el pipeline) | Cuando el equipo lo planifica; cuesta tiempo de personas |

Las dos se complementan: la herramienta revisa lo mecánico en cada cambio y deja a las personas lo que requiere criterio.

**Tipos de revisión** (adaptación del temario ISTQB CTFL v4.0, sección 3.2.4). Van de la menos a la más formal:

| Tipo | Cómo es | Objetivo principal | Ejemplo en este proyecto |
|---|---|---|---|
| Revisión informal | No sigue un proceso definido ni exige dejar registro | Detectar anomalías | Pedirle a un compañero que lea la función nueva antes del commit |
| *Walkthrough* (recorrido) | La dirige el autor, que recorre el producto con los revisores; la revisión individual previa es opcional | Evaluar la calidad, generar confianza, enseñar, llegar a acuerdos, generar ideas y detectar anomalías | El autor recorre con Producción, línea por línea, el `.feature` de alertas para confirmar que dice lo que se acordó |
| Revisión técnica | La hacen revisores con conocimiento técnico y la dirige un moderador | Llegar a un acuerdo y tomar decisiones sobre un problema técnico; también detectar anomalías | El equipo decide si la complejidad máxima debe seguir en 5 |
| Inspección | La más formal: sigue el proceso completo, con roles definidos y métricas; el autor no puede ser líder ni secretario de la revisión | Encontrar el mayor número posible de anomalías | Inspeccionar el cálculo del MAPE con un checklist antes de entregarlo a Producción |

El temario describe un proceso genérico (sección 3.2.2): **planificación** (alcance, criterios de salida), **inicio** (que cada participante tenga el material y sepa su rol), **revisión individual** (cada revisor anota anomalías, por ejemplo con un checklist), **comunicación y análisis** (se discute cada anomalía y se decide qué hacer) y **corrección e informe**. Los roles principales (sección 3.2.3) son gerente, autor, moderador, secretario (quien registra), revisor y líder de la revisión. Cuanto más formal es la revisión, más de ese proceso se cumple.

En la actividad (Paso 8.5) hacen una revisión con el checklist de Clean Code.

## Testing en metodologías ágiles

En un equipo ágil las pruebas no son una fase al final: ocurren durante todo el sprint y son responsabilidad de todo el equipo (el temario ISTQB lo llama *whole team approach*, sección 1.5.2). Así encaja este proyecto en un sprint:

| Momento del sprint | Qué pasa | Qué parte del proyecto lo representa |
|---|---|---|
| Refinamiento de la historia | Producción, desarrollo y quien prueba escriben juntos la historia ("Como planeador de producción quiero una alerta…") y sus criterios de aceptación. Quien prueba pregunta por los casos límite: ¿un error igual al umbral alerta? | Los escenarios de `tests/bdd/features/` |
| Desarrollo | Cada función se construye con TDD; los escenarios se automatizan | `docs/EJEMPLO_TDD.md`, `tests/unit/`, los pasos BDD |
| Integración continua | Cada push ejecuta el pipeline | `.github/workflows/ci-cd.yml` |
| Revisión del sprint | Se muestra lo terminado; los escenarios en verde son la evidencia de que se cumplieron los criterios | El job *Pruebas BDD* del pipeline |
| Retrospectiva | El equipo revisa qué mejorar: por ejemplo, ajustar una regla del análisis estático | `docs/ANALISIS_ESTATICO.md` |

Tres ideas que conviene recordar:

- **Quien prueba participa desde la definición de la historia.** Encontrar la ambigüedad de "¿igual al umbral alerta o no?" cuando se escribe la historia cuesta una conversación; encontrarla en producción cuesta un defecto. Es el principio de probar temprano (*shift left*, sección 2.1.5 del temario).
- **Los escenarios BDD son criterios de aceptación ejecutables.** El temario (sección 4.5.2) describe el formato Dado/Cuando/Entonces como una de las dos formas habituales de escribir criterios de aceptación. Aquí, además, se ejecutan: si el código deja de cumplir el criterio, el pipeline lo dice.
- **El pipeline en verde es parte de la *Definition of Done*.** Una historia está terminada cuando, además de funcionar, cumple lo que el equipo acordó. Para este proyecto, una *Definition of Done* razonable sería: pruebas unitarias y escenarios BDD en verde, análisis estático sin hallazgos, cobertura de 90 % o más, código revisado por otra persona y el pipeline en verde en `main`. Si una de esas condiciones falla, la historia no está terminada, aunque "funcione en mi equipo".

Este es también el sentido de las **pruebas continuas en DevOps** (sección 2.1.4 del temario): el pipeline da retroalimentación rápida en cada cambio y reduce el riesgo de regresión, pero no elimina las pruebas manuales ni las revisiones desde el punto de vista de quien usa el sistema.

## Tipos de prueba de la Unidad 2 en este proyecto

| Tema de la unidad | Dónde está en el proyecto | Cómo se practica |
|---|---|---|
| TDD | `docs/EJEMPLO_TDD.md` (ciclo completo de `mad`) | ACTIVIDAD, Paso 2 (suavización exponencial) y Paso 8.1 (`mse`) |
| BDD | `tests/bdd/features/promedio_movil.feature` y `tests/bdd/test_promedio_movil.py` | `uv run pytest tests/bdd -v`; ACTIVIDAD, Pasos 4 y 8.3 |
| Pruebas unitarias | `tests/unit/` | `uv run pytest tests/unit -v`; ACTIVIDAD, Pasos 3 y 8.2 |
| Pruebas funcionales | Los escenarios BDD (sección "Pruebas funcionales" de este README) | `uv run pytest tests/bdd -v`; ACTIVIDAD, Pasos 4 y 8.3 |
| Análisis estático | `[tool.ruff]` en `pyproject.toml`; guía en `docs/ANALISIS_ESTATICO.md` | `uv run ruff check .`; ACTIVIDAD, Pasos 5 y 8.4 |
| Revisiones estáticas | Sección "Revisiones estáticas" de este README y checklist de la ACTIVIDAD | ACTIVIDAD, Paso 8.5 |
| Clean Code | Sección "Clean Code" de este README y el código de las reglas de negocio | ACTIVIDAD, refactor del Paso 2.3 y Paso 8.5 |
| Pruebas continuas en DevOps | `.github/workflows/ci-cd.yml` | ACTIVIDAD, Paso 7 |
| Testing en ágil | Sección "Testing en metodologías ágiles" de este README | ACTIVIDAD, Paso 7.5 y preguntas del informe (Paso 9) |

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
