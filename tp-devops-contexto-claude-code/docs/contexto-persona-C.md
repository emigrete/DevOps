# Contexto para Claude Code — PERSONA C

> Pegá este archivo al iniciar tu sesión de Claude Code, o decile
> "leé docs/contexto-persona-C.md y CLAUDE.md antes de empezar".

## Tu bloque: CI/CD + Docker Hub + Deploy Render (Fases 3, 4 y 5)

Tu parte vale **4,5 puntos**, el bloque más pesado del TP:
- Checks (build + unit test): 0,5
- Flujo de mergeo: 1
- Publicación dockerfile a registry: **2** (el ítem individual más alto)
- Despliegue a Render: 1 (NO requerido para aprobar, pero suma — Clase 1)

Dependés de Persona A (tests para correr en CI) y Persona B (Dockerfile
para buildear y publicar). Tu CI podés empezar a armarlo en paralelo con
los tests básicos y completarlo cuando A y B avancen.

## Tareas

### 1. Workflow de CI (`.github/workflows/ci.yml`)

Bonanni mostró el patrón en CI_CD.pdf (slide 11, Node.js) y dijo (Clase 5):
"esa parte de los checks no es muy difícil de integrar, bastante sencilla".
Adaptarlo a Python:

- Trigger: `on: [push, pull_request]`.
- Job `lint`: ruff o flake8.
- Job `test`: `pytest --cov=app` (los unit tests de Persona A).
- Job `build`: `docker build` (validar que la imagen de Persona B compila;
  sin push todavía).

Estos son los **checks** que después se exigen en la rama protegida.

### 2. Flujo de mergeo (rama protegida + PRs)

- En GitHub: Settings -> Branches -> proteger `main`:
  - Require PR before merging.
  - Require status checks (los jobs del `ci.yml`).
- Documentar el flujo: branch -> PR -> review cruzado (con 3 personas,
  un PR lo aprueba alguien que NO lo escribió) -> merge.
- **Por qué (Clase 4):** Bonanni pidió esto para grupos: "crear pull
  requests, crear ramas, para simular la realidad de un flujo en una
  empresa". Sacar screenshots de PRs con reviewers para el informe.

### 3. Workflow de publicación a Docker Hub (`.github/workflows/publish.yml`)

Vale 2 puntos. Bonanni lo explicó en detalle en Clase 5.

- Trigger: push a `main` (o por tag/release).
- Login a Docker Hub usando **secrets**:
  - `DOCKER_USER`
  - `DOCKER_API_KEY` (Bonanni Clase 5: aclaró que es la API Key / Access
    Token, NO la password del usuario).
- Usar `docker/metadata-action` para extraer tags y labels desde el
  Dockerfile (los LABELS que puso Persona B — Clase 5: "extrae toda esa
  metadata").
- Usar `docker/build-push-action` con `push: true`.
- Taggear con el **SHA del commit** + `latest` (Bonanni Clase 5: "como
  nombre va a aparecer el SHA del commit").
- El repo de imagen en Docker Hub es **público** (cuenta gratuita solo
  permite públicas — Clase 5).

### 4. Deploy a Render (en el mismo publish.yml o uno aparte)

Bonanni mostró el paso a paso en Clase 6:
1. Crear cuenta en Render.
2. Crear un Web Service tipo **"Deploy an existing image from a registry"**
   (NO usar `latest`, le vamos a pasar la imagen nosotros — Clase 5).
3. En Settings del servicio -> copiar el **Deploy Hook URL** (es un secret).
4. Guardarlo en GitHub Secrets como `RENDER_DEPLOY_HOOK`.
5. Al final del workflow, después del push a Docker Hub, hacer un `curl`
   al Deploy Hook **agregando como query param la imagen** que se va a
   deployar (Bonanni Clase 5: "le agregan este query param donde
   especifican la imagen de Docker, y le pasan el SHA de la imagen o la
   versión si están usando semver").

Ejemplo conceptual del paso final (ajustar a la doc de Render):
```
curl "$RENDER_DEPLOY_HOOK&imgURL=docker.io/USUARIO/tp-devops:${SHA}"
```

## Secrets a configurar en GitHub (Settings -> Secrets -> Actions)

- `DOCKER_USER`
- `DOCKER_API_KEY`
- `RENDER_DEPLOY_HOOK`

NUNCA hardcodear estos valores en los YAML.

## Criterios de aceptación

- [ ] `ci.yml` corre en cada push/PR y los jobs pasan.
- [ ] Rama `main` protegida exige los checks.
- [ ] `publish.yml` publica la imagen pública en Docker Hub con tag SHA + latest.
- [ ] Render recibe el deploy hook y levanta la imagen publicada.
- [ ] Cero secretos en el código.

## Tu flujo Git

```
git checkout -b ci/pipeline-publish-deploy
# ... trabajar ...
git commit -m "ci: workflows de CI, publicacion a Docker Hub y deploy a Render"
git push -u origin ci/pipeline-publish-deploy
# abrir PR, que lo revise A o B
```

## Para el informe (anotá mientras trabajás)

- Diferencia Continuous Delivery vs Continuous Deployment (Clase 4 entera
  trató esto — aclarar cuál de los dos están haciendo).
- Por qué taggear con SHA (trazabilidad).
- Por qué API Key y no password (seguridad — Clase 5).
- Capturas: pipeline verde, imagen en Docker Hub, deploy en Render,
  PRs con checks.
- Relación con teoría: CI = primera vía (Flujo); pipeline que frena ante
  fallo = Andon Cord.
