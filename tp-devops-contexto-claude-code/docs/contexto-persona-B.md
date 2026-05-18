# Contexto para Claude Code — PERSONA B

> Pegá este archivo al iniciar tu sesión de Claude Code, o decile
> "leé docs/contexto-persona-B.md y CLAUDE.md antes de empezar".

## Tu bloque: Dockerfile multi-stage + docker-compose (Fase 2)

Tu parte vale **3 puntos** (Dockerfile 1 + multi-stage 1 + buenas prácticas
Docker 0,5 + buenas prácticas compose 0,5). Es de lo más pesado del TP.

Dependés de que Persona A tenga la API funcionando. Coordiná para arrancar
cuando ya exista `app/main.py` y `requirements.txt`.

## Lo que más se evalúa: BUENAS PRÁCTICAS JUSTIFICADAS

Bonanni (Clase 5) fue muy claro: las buenas prácticas **dependen del
lenguaje/framework** y hay que **justificarlas con fuente oficial**
(documentación de Python, FastAPI, Docker o de las librerías). Por cada
buena práctica que apliques, dejá un comentario en el Dockerfile/compose
indicando la fuente. Eso es evidencia directa para el informe.

## Tareas

### 1. Dockerfile multi-stage (`Dockerfile`)

Bonanni mostró el patrón en Clase 5 con dos stages. Para Python:

**Stage `builder`:**
- Imagen base oficial de Python.
- Instalar dependencias (idealmente compilando wheels) sin dejar basura.
- Copiar `requirements.txt` ANTES del código para aprovechar cache de capas
  (buena práctica de Docker, justificable con docs oficiales de Docker).

**Stage `runtime`:**
- Imagen base **lo más chica posible**. Bonanni (Clase 5): "Debian 11 es
  demasiado grande, debería ser alpine o algo similar para que sea lo
  mínimo posible".
  - **Decisión a justificar en el informe:** para Python conviene
    `python:3.12-slim` por encima de `alpine`, porque alpine usa musl libc
    y rompe wheels nativos (psycopg2). Esto se justifica con la doc oficial
    de Python en Docker Hub y discusiones oficiales. Documentá esta decisión.
- Copiar solo lo necesario desde el stage builder (`COPY --from=builder`).
- Crear y usar **usuario no-root** (`USER appuser`) — buena práctica de
  seguridad, justificable con docs de Docker.
- `WORKDIR` explícito.
- Variables de entorno necesarias (no secretos).
- **HEALTHCHECK** apuntando a `/health`.
- **LABELS** con metadata (Bonanni Clase 5: "una de las buenas prácticas es
  ponerle los tags y labels, extrae toda esa metadata" — esto lo aprovecha
  el workflow de publicación de Persona C).
- `CMD` con uvicorn.

### 2. docker-compose.yml (`docker-compose.yml`)

Servicios:
- `api`: build del Dockerfile, puerto expuesto, env desde `.env`,
  `depends_on` la base de datos con condición de healthy.
- `db`: PostgreSQL oficial, credenciales por env, volumen nombrado para
  persistencia, healthcheck propio.

Buenas prácticas de compose a aplicar y justificar:
- No hardcodear credenciales (usar `.env`).
- Volumen nombrado para la BD (persistencia).
- Healthchecks y `depends_on: condition: service_healthy`.
- Red nombrada.
- `restart` policy.
- Versión de imágenes pineada (no `latest`).

### 3. `.dockerignore`
Ya existe uno base (Fase 0). Revisalo y completalo si hace falta para que
la imagen no copie tests, .git, venv, etc. (imagen mínima — Clase 5).

## Criterios de aceptación

- [ ] `docker build -t tp-devops .` construye sin errores.
- [ ] La imagen final es chica (comprobá con `docker images`).
- [ ] El contenedor corre como usuario no-root.
- [ ] `docker compose up` levanta API + Postgres y se comunican.
- [ ] El HEALTHCHECK pasa a healthy.
- [ ] Cada buena práctica tiene un comentario con su fuente.

## Tu flujo Git

```
git checkout -b feat/docker-multistage-compose
# ... trabajar ...
git commit -m "feat: Dockerfile multi-stage y docker-compose con buenas practicas"
git push -u origin feat/docker-multistage-compose
# abrir PR, que lo revise A o C
```

## Para el informe (anotá mientras trabajás)

- Por qué multi-stage (imagen final mínima, separa build de runtime).
- Por qué `slim` y no `alpine` (con la fuente oficial).
- Por qué usuario no-root (seguridad).
- Por qué el orden de los COPY (cache de capas).
- Por qué labels (metadata para el registry).
- Capturas: tamaño de imagen, `docker compose up` funcionando.
- Relación con teoría: inmutabilidad, infraestructura como código.
