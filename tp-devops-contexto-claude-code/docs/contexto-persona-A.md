# Contexto para Claude Code — PERSONA A

> Pegá este archivo al iniciar tu sesión de Claude Code, o decile
> "leé docs/contexto-persona-A.md y CLAUDE.md antes de empezar".

## Tu bloque: API + Tests unitarios + Base de datos (Fase 1)

Sos la base del proyecto. Sin tu parte nadie puede dockerizar, testear
ni monitorear. Tu código es el que después se va a ver en las trazas del
monitoreo, así que hacelo prolijo y en capas.

## Tu objetivo concreto

Construir una API FastAPI mínima pero con la estructura correcta para que
el resto del TP se pueda lucir. **No agregues funcionalidad de más** —
Bonanni no evalúa la complejidad de la API (Clase 4).

## Tareas (en orden)

### 1. Modelo y base de datos (`app/db/`)
- SQLAlchemy 2.x con un modelo simple: `Item` (id, name, description, created_at).
- Sesión configurable por `DATABASE_URL` (SQLite local / Postgres en compose).
- Función de creación de tablas al startup.

### 2. Esquemas Pydantic (`app/models/`)
- `ItemCreate`, `ItemOut`. Validación básica.

### 3. Capa de servicios (`app/services/`)
- `items_service.py`: lógica CRUD contra la BD (crear, listar, obtener, borrar).
- `pokemon_service.py`: orquesta la llamada a la API externa vía el client.
- IMPORTANTE: la lógica de negocio vive acá, NO en los routers.

### 4. Cliente HTTP externo (`app/clients/`)
- `pokeapi_client.py`: usa `httpx` para llamar a PokeAPI
  (`GET https://pokeapi.co/api/v2/pokemon/{name}`).
- URL base desde variable de entorno `POKEAPI_BASE_URL`.
- Manejar timeout y errores HTTP.
- **Por qué esto importa (Clase 4):** Bonanni pidió textual una llamada a
  una API gratuita (Pokemon o Star Wars) "para poder observar las trazas
  encadenadas en el monitoreo".

### 5. Routers / endpoints (`app/routers/`)
Endpoints mínimos:
- `GET  /health` -> healthcheck simple (lo usa Docker y Render).
- `GET  /items` -> lista items (toca la BD).
- `POST /items` -> crea item (toca la BD).
- `GET  /items/{id}` -> obtiene item (toca la BD).
- `DELETE /items/{id}` -> borra item (toca la BD).
- `GET  /pokemon/{name}` -> llama a PokeAPI vía service+client (traza externa).
- `GET  /error-test` -> lanza una excepción a propósito.
  - **Por qué (Clase 4):** Bonanni pidió "tener algún momento en que falle,
    que ustedes ya sepan que falle, para mostrar cómo se ven los errores en
    monitoreo".

Los routers solo orquestan: reciben request -> llaman al service -> devuelven
respuesta. Sin lógica de negocio adentro.

### 6. `app/main.py`
- Instancia FastAPI.
- Incluye los routers.
- Crea tablas al startup.
- Título/descripción para que Swagger (`/docs`) quede presentable.

### 7. Tests (`tests/`) con pytest
- 4-6 tests, suficiente. Bonanni (Clase 4): "pruebas unitarias lo
  suficientemente básicas como para que tengamos algo para correr dentro
  del proceso de CI/CD".
- Cubrir: health, CRUD de items (con BD de test en SQLite memoria),
  el endpoint de pokemon (mockeando el client httpx), y el error-test.
- Configurar `pytest-cov` para reportar cobertura (Bonanni habló de
  code coverage en Clase 4).

## Criterios de aceptación de tu parte

- [ ] `uvicorn app.main:app --reload` levanta sin errores.
- [ ] `http://localhost:8000/docs` muestra todos los endpoints.
- [ ] `pytest --cov=app` corre verde y muestra cobertura.
- [ ] Separación real en capas (router -> service -> client/db).
- [ ] Endpoint de PokeAPI funciona.
- [ ] Endpoint `/error-test` rompe a propósito.
- [ ] Nada hardcodeado: URLs y DB por variables de entorno.

## Tu flujo Git

```
git checkout -b feat/api-tests-db
# ... trabajar ...
git commit -m "feat: API con capas, BD y tests unitarios"
git push -u origin feat/api-tests-db
# abrir PR, que lo revise B o C
```

## Para el informe (anotá mientras trabajás)

- Por qué la separación en capas (mantenibilidad, testabilidad, prepara
  el terreno para trazas de monitoreo).
- Qué probaste en los tests y por qué.
- Relación con teoría: tests = feedback rápido (Three Ways), Andon Cord
  (un test rojo frena el pipeline).
