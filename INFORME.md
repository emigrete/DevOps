# Informe — Trabajo Práctico Integrador DevOps

**Materia:** DevOps — Prof. Lucas Bonanni
**Integrantes:**
- Francisco Daurat — Fase 1 (API + tests + base de datos)
- Pedro Livschitz — Fase 2 (Dockerfile multi-stage + docker-compose)
- Teodoro Welyczko — Fases 3-5 (CI/CD + Docker Hub + Render + monitoreo)

**Repositorio:** `https://github.com/emigrete/tp-devops`

---

## 1. Objetivo del trabajo

Aplicar de forma incremental cada etapa del ciclo DevOps sobre una API. El foco
**no es la complejidad de la aplicación** sino que cada etapa esté implementada
correctamente y justificada. La API es deliberadamente mínima: existe para tener
algo que testear, dockerizar, publicar, deployar y monitorear.

Cada decisión técnica relevante lleva en el código un **comentario citando la
fuente oficial** (Docker / Python / FastAPI / New Relic docs) que la respalda.

---

## 2. Resumen de cumplimiento (rúbrica)

| Módulo | Ítem | Puntaje | Estado | Evidencia (archivo) |
|---|---|---|:---:|---|
| Dockerfile | Dockerfile (requerido) | 1 | ✅ | `Dockerfile` |
| Dockerfile | Multi-stage | 1 | ✅ | `Dockerfile` (builder + runtime) |
| Dockerfile | Buenas prácticas | 0,5 | ✅ | `Dockerfile` |
| Docker compose | Buenas prácticas | 0,5 | ✅ | `docker-compose.yml` |
| CI | Checks (build + unit test) | 0,5 | ✅ | `.github/workflows/ci.yml` |
| CD | Flujo de mergeo (PRs) | 1 | ✅ | `GIT_WORKFLOW.md` + PRs en GitHub |
| CD | Publicación de imagen | 2 | ✅ | `.github/workflows/publish.yml` |
| CD | Despliegue a Render | 1 | ✅ | `publish.yml` (paso Render) |
| Monitoreo | Dashboard (Hits, etc.) | 1,5 | ✅ | New Relic + instrumentación |
| Monitoreo | APM / Trazas | 1 | ✅ | `function_trace` en service + client |
| | **Total** | **10** | **10/10** | |

---

## 3. Stack tecnológico

| Capa | Herramienta | Versión |
|---|---|---|
| Lenguaje | Python | 3.12 |
| Framework API | FastAPI | 0.115.6 |
| Validación de datos | Pydantic | 2.10.4 |
| ORM / base de datos | SQLAlchemy | 2.0.36 |
| Base de datos | SQLite (local) / PostgreSQL (compose) | 16.3 |
| Cliente HTTP | httpx | 0.28.1 |
| Tests | pytest + pytest-cov | 8.3.4 / 6.0.0 |
| Contenedor | Docker (multi-stage) | — |
| Orquestación | docker-compose | — |
| CI/CD | GitHub Actions | — |
| Registry | Docker Hub | — |
| Deploy | Render | — |
| Monitoreo | New Relic (agente APM) | 10.4.0 |

Todas las versiones están **pineadas** en `requirements.txt` para garantizar
reproducibilidad (que el build sea idéntico hoy y dentro de seis meses).

---

## 4. Fase 1 — API, base de datos y tests

### 4.1 Arquitectura en capas

La API está dividida en cuatro capas con una única responsabilidad cada una.
Esta separación es **el requisito que habilita las trazas encadenadas** del
monitoreo (Fase 6):

```
HTTP request
   → app/routers/   (controller: parsea request, llama al service, devuelve response)
   → app/services/  (lógica de negocio: CRUD contra DB, orquesta llamadas externas)
   → app/clients/   (cliente httpx hacia la API externa PokeAPI)
   → app/db/        (sesión SQLAlchemy + modelo Item)
app/models/          (esquemas Pydantic: ItemCreate, ItemUpdate, ItemOut)
app/main.py          (app FastAPI, include de routers, creación de tablas)
```

### 4.2 Endpoints

| Método | Ruta | Propósito |
|---|---|---|
| `GET` | `/health` | Healthcheck (usado por Docker y Render) |
| `GET` | `/items` | Listar items (DB) |
| `POST` | `/items` | Crear item (DB) |
| `GET` | `/items/{id}` | Obtener item (404 si no existe) |
| `PATCH` | `/items/{id}` | Actualizar item parcialmente (404 si no existe) |
| `DELETE` | `/items/{id}` | Borrar item (404 si no existe) |
| `GET` | `/pokemon/{name}` | Proxy a la API externa PokeAPI |
| `GET` | `/error-test` | Lanza un error a propósito → demuestra visibilidad en monitoreo |

Los endpoints de `/items` cubren el **CRUD completo**: Create (`POST`), Read
(`GET` lista y por id), Update (`PATCH`) y Delete (`DELETE`). Para la
actualización se eligió **`PATCH` y no `PUT`** porque la semántica es
*actualización parcial*: el cliente envía solo los campos que quiere cambiar y
el resto queda intacto. PUT, en cambio, implica reemplazar el recurso completo.
El schema `ItemUpdate` tiene todos los campos opcionales y el service aplica solo
los recibidos (`model_dump(exclude_unset=True)`).

### 4.3 Configuración por variables de entorno

Nada hardcodeado: `DATABASE_URL`, `POKEAPI_BASE_URL`, puerto y credenciales
vienen de variables de entorno (plantilla en `.env.example`, archivo `.env`
fuera de git). Esto permite usar SQLite en local y PostgreSQL en compose sin
tocar el código.

### 4.4 Tests

Suite con pytest (`tests/test_api.py`, **8 tests**): cubre health, error-test,
CRUD completo de items (incluida la actualización parcial con `PATCH` y su caso
404) y el endpoint pokemon (con la llamada externa **mockeada**, para que los
tests no dependan de la red). Aislamiento total: cada test usa una base SQLite en
memoria que se crea y destruye por test (`tests/conftest.py`).

```bash
pytest --cov=app
```

---

## 5. Fase 2 — Dockerfile y docker-compose

### 5.1 Dockerfile multi-stage

Dos etapas separadas:

- **Stage `builder`**: instala las dependencias.
- **Stage `runtime`**: copia solo las dependencias instaladas → imagen final
  más liviana, sin las herramientas de compilación.

**Buenas prácticas aplicadas (cada una con su fuente citada en el archivo):**

| Decisión | Justificación |
|---|---|
| Base `python:3.12-slim` (no `alpine`) | alpine usa musl libc → rompe wheels nativos como `psycopg2-binary`; slim es Debian/glibc y mantiene compatibilidad |
| Multi-stage | separa build del runtime → imagen final más chica |
| Copiar `requirements.txt` antes del código | aprovecha la caché de capas de Docker (si cambia el código pero no las deps, no reinstala) |
| Usuario **no-root** (`appuser`) | principio de mínimo privilegio: si el proceso es comprometido, el atacante no tiene root en el host |
| `HEALTHCHECK` a `/health` | Docker y Render saben si el contenedor está sano |
| `ENV PYTHONUNBUFFERED=1` | logs visibles en tiempo real |

### 5.2 docker-compose

Levanta el stack completo (API + PostgreSQL) con un comando: `docker compose up`.

**Buenas prácticas aplicadas:**

| Decisión | Justificación |
|---|---|
| `depends_on: condition: service_healthy` | la API espera a que Postgres esté listo → evita el race condition de arrancar antes que la DB |
| Healthchecks en ambos servicios | `pg_isready` para Postgres, `/health` para la API |
| Volumen nombrado `postgres_data` | persistencia de datos entre recreaciones del contenedor |
| Red nombrada aislada | los servicios se comunican por nombre (`db:5432`) sin exponer Postgres al host |
| Imagen de Postgres pineada (`16.3-alpine`) | reproducibilidad (no usar `latest`) |
| Credenciales vía `env_file` | nunca hardcodeadas en el compose |

---

## 6. Fases 3-5 — CI/CD

### 6.1 CI — `ci.yml` (checks en cada push y PR)

Tres jobs. Si alguno falla, el Pull Request no se puede mergear (esto es un
**Andon Cord**: el pipeline frena ante un defecto).

| Job | Qué hace |
|---|---|
| `lint` | `ruff check app tests` (chequeo de estilo/errores) |
| `test` | `pytest --cov=app` (los tests unitarios de Fase 1) |
| `build` | `docker build` **sin push** → valida que el Dockerfile compila |

### 6.2 CD — `publish.yml` (en cada merge a `main`)

1. **Login a Docker Hub** usando *secrets* de GitHub (`DOCKER_USER` /
   `DOCKER_API_KEY`). Se usa una **API Key / Access Token, nunca la contraseña**
   de la cuenta (buena práctica de seguridad).
2. **Build + push** de la imagen al registry, etiquetada con:
   - el **SHA del commit** (trazabilidad: cada imagen mapea a un commit exacto),
   - `latest` (conveniencia).
3. **Deploy a Render**: se llama al Deploy Hook pasando la imagen **SHA-tagged**
   por query param, para que Render deploye exactamente ese commit y no `latest`.

### 6.3 Flujo de mergeo (1 pt)

- Una rama por feature: `feat/...`, `fix/...`, `chore/...`, `docs/...`, `ci/...`.
- Conventional Commits (`feat:`, `fix:`, `ci:`, ...).
- Rama `main` **protegida**: requiere PR aprobado + checks de CI en verde.
- Cada PR es revisado por un compañero que **no** lo escribió (review cruzado).
- Detalle completo en `GIT_WORKFLOW.md`.

**Evidencia para la presentación:** lista de PRs mergeados, un PR con la
aprobación del compañero, la configuración de branch protection y un check de
CI corriendo dentro de un PR.

---

## 7. Fase 6 — Monitoreo (New Relic)

- El agente de New Relic se arranca envolviendo a uvicorn con
  `newrelic-admin run-program` (en el `CMD` del Dockerfile).
- **Configuración 100% por variables de entorno** (sin archivo `newrelic.ini`):
  `NEW_RELIC_LICENSE_KEY`, `NEW_RELIC_APP_NAME`, distributed tracing activado.

### 7.1 Dashboard (1,5 pts)

New Relic muestra hits (cantidad de requests), throughput, tiempos de respuesta
y tasa de error. El endpoint `/error-test` genera errores a propósito para que
se vean reflejados en el dashboard.

### 7.2 APM / Trazas encadenadas (1 pt)

Cada función de las capas service y client lleva el decorador
`@newrelic.agent.function_trace()`, que genera un **span** propio. El resultado
es una traza que muestra la cadena completa:

```
Transacción: GET /pokemon/{name}
└─ router
   └─ service  (fetch_pokemon)     ← span por function_trace
      └─ client (get_pokemon)      ← span por function_trace
         └─ llamada HTTP externa a PokeAPI  ← span automático del agente
```

Para los endpoints de DB, el span de SQL (datastore) queda anidado bajo el
service. Esta jerarquía de spans es **el motivo de la separación en capas**: sin
ella, New Relic mostraría un único span plano y no habría trazas que demostrar.

---

## 8. Relación con la teoría DevOps

| Concepto | Cómo se aplica en el TP |
|---|---|
| **The Three Ways** | *Flujo*: pipeline CI/CD automatizado. *Feedback*: monitoreo en New Relic. *Aprendizaje continuo*: iteración sobre la API vía PRs. |
| **Andon Cord** | El pipeline frena ante un test/lint/build fallido → el PR no se mergea, igual que detener la línea de producción ante un defecto. |
| **Metodologías ágiles** | Trabajo iterativo en ramas cortas con review cruzado, entregas incrementales por fase. |
| **Lean** | Producto mínimo viable, sin features de más (lo que no suma puntos no se agrega), entrega rápida y eliminación de desperdicio. |

---

## 9. Cómo ejecutar el proyecto

```bash
# --- Local ---
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload          # http://localhost:8000  (docs en /docs)
pytest --cov=app                       # tests

# --- Docker ---
docker build -t tp-devops .
docker compose up                      # API + PostgreSQL
```

---

## 10. Estructura del repositorio

```
.
├── app/                      # código de la API (en capas)
│   ├── main.py               # entrypoint FastAPI
│   ├── routers/              # capa controller (health, items, pokemon)
│   ├── services/             # lógica de negocio + spans New Relic
│   ├── clients/              # cliente HTTP a la API externa (PokeAPI)
│   ├── db/                   # engine, sesión y modelo Item (SQLAlchemy)
│   └── models/               # esquemas Pydantic
├── tests/                    # pytest (conftest + test_api)
├── .github/workflows/
│   ├── ci.yml                # lint + test + build (en PR/push)
│   └── publish.yml           # push a Docker Hub + deploy a Render (en main)
├── Dockerfile                # multi-stage, no-root, healthcheck
├── docker-compose.yml        # api + postgres + volumen + red
├── requirements.txt          # dependencias pineadas
├── .env.example              # plantilla de variables de entorno
├── GIT_WORKFLOW.md           # flujo de PRs y branch protection
└── README.md                 # checklist de avance y guía de uso
```
