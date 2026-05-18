# =============================================================
# Multi-stage build — separa dependencias de compilación del
# runtime final, reduciendo el tamaño de la imagen.
# Ref: https://docs.docker.com/build/building/multi-stage/
# =============================================================

# ── Stage 1: builder ─────────────────────────────────────────
FROM python:3.12-slim AS builder

# python:3.12-slim sobre alpine: alpine usa musl libc, lo que
# rompe wheels nativos como psycopg2-binary al instalar desde PyPI.
# slim es Debian-based y mantiene glibc, asegurando compatibilidad.
# Ref: https://hub.docker.com/_/python (sección "slim vs alpine")

WORKDIR /build

# Copiar requirements ANTES del código fuente para aprovechar la
# caché de capas de Docker: si el código cambia pero requirements
# no, esta capa no se reconstruye.
# Ref: https://docs.docker.com/build/cache/
COPY requirements.txt .

RUN pip install --upgrade pip --no-cache-dir \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ─────────────────────────────────────────
FROM python:3.12-slim AS runtime

# LABELS con metadata del proyecto.
# Permiten que registries (Docker Hub, GitHub Packages) y
# herramientas de CI extraigan información de la imagen.
# Ref: https://docs.docker.com/reference/dockerfile/#label
# Ref: https://github.com/opencontainers/image-spec/blob/main/annotations.md
LABEL org.opencontainers.image.title="tp-devops-api" \
      org.opencontainers.image.description="FastAPI TP DevOps — UADE" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Persona B" \
      org.opencontainers.image.source="https://github.com/emigrete/tp-devops"

WORKDIR /app

# Variables de entorno de Python recomendadas para contenedores:
# PYTHONDONTWRITEBYTECODE=1 → no genera archivos .pyc (imagen más limpia)
# PYTHONUNBUFFERED=1       → stdout/stderr sin buffer (logs visibles en tiempo real)
# Ref: https://docs.python.org/3/using/cmdline.html#environment-variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copiar solo los paquetes instalados desde el stage builder.
# El código fuente NO se copia desde builder; se copia desde el
# contexto directamente para mantener la separación de capas.
COPY --from=builder /install /usr/local

# Copiar el código de la aplicación.
COPY app/ ./app/

# Crear usuario no-root y correr como él.
# Principio de mínimo privilegio: si el proceso es comprometido,
# el atacante no tiene acceso root al host.
# Ref: https://docs.docker.com/build/building/best-practices/#user
RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --no-create-home appuser

USER appuser

# HEALTHCHECK: Docker daemon verifica que la API responde.
# Usado por docker-compose (depends_on: condition: service_healthy)
# y por Render para saber si el contenedor está listo.
# Ref: https://docs.docker.com/reference/dockerfile/#healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000

# CMD con uvicorn. Se usa la forma exec (lista) en lugar de shell
# para que el proceso reciba señales SIGTERM correctamente.
# Ref: https://docs.docker.com/reference/dockerfile/#cmd
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
