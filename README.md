# TP Integrador DevOps

API integradora desarrollada para la materia DevOps (Prof. Lucas Bonanni).
El objetivo no es la complejidad de la API sino aplicar de forma incremental
cada etapa del ciclo DevOps vista en clase.

## Integrantes

- Francisco Daurat — Fase 1 (API + tests + base de datos)
- Pedro Livschitz — Fase 2 (Dockerfile multi-stage + docker-compose)
- Teodoro Welyczko — Fases 3-5 (CI/CD + Docker Hub + Render + monitoreo)

## Stack

- **Lenguaje:** Python 3.12
- **Framework:** FastAPI
- **Base de datos:** SQLite (local) / PostgreSQL (docker-compose)
- **Tests:** pytest
- **Contenedor:** Docker (multi-stage)
- **Orquestación:** docker-compose
- **CI/CD:** GitHub Actions
- **Registry:** Docker Hub
- **Deploy:** Render
- **Monitoreo:** New Relic (APM + Dashboard)

## Estructura del proyecto

```
app/
  routers/    -> endpoints (capa controller)
  services/   -> lógica de negocio (capa service)
  clients/    -> cliente HTTP a API externa (PokeAPI)
  models/     -> esquemas Pydantic
  db/         -> modelo y sesión SQLAlchemy
  main.py     -> punto de entrada FastAPI
tests/        -> pruebas unitarias
```

> La separación en capas (controller -> service -> client/db) responde a la
> recomendación de la Clase 4: tener varias capas y una llamada a una API
> externa para poder observar trazas encadenadas en el monitoreo.

## Cómo correr en local

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API disponible en: http://localhost:8000
Documentación interactiva (Swagger): http://localhost:8000/docs

## Cómo correr los tests

```bash
pytest --cov=app
```

## Estado de avance (checklist de evaluación)

| Módulo | Ítem | Puntaje | Estado |
|---|---|---|---|
| Dockerfile | Dockerfile (requerido) | 1 | ⬜ |
| Dockerfile | Multi-stage | 1 | ⬜ |
| Dockerfile | Buenas prácticas | 0,5 | ⬜ |
| Docker compose | Buenas prácticas | 0,5 | ⬜ |
| CI/CD | Checks (build + unit test) | 0,5 | ⬜ |
| CI/CD | Flujo de mergeo | 1 | ⬜ |
| CI/CD | Publicación dockerfile | 2 | ⬜ |
| CI/CD | Despliegue a Render | 1 | ⬜ |
| Monitoreo | Dashboard (Hits, etc) | 1,5 | ⬜ |
| Monitoreo | APM / Trazas | 1 | ⬜ |
| | **TOTAL** | **10** | |

## Relación con la teoría

- **Three Ways:** Flujo (CI/CD), Feedback (monitoreo), Aprendizaje continuo (iteración).
- **Andon Cords:** El pipeline se detiene ante un test fallido; alertas de monitoreo.
- **Lean:** Producto mínimo viable, eliminación de desperdicio, entrega rápida.
- **Build-Measure-Learn:** Ciclo de mejora continua sobre la API.
