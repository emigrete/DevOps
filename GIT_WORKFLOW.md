# Guía de Git y flujo de trabajo en equipo

Esta guía cubre el setup inicial del repo y el flujo de PRs.
El "flujo de mergeo" vale **1 punto** y Bonanni lo pidió explícitamente
para grupos (Clase 4): *"si están en equipo, se puede sumar esto de crear
pull requests, de crear ramas, para simular la realidad de lo que sería un
flujo en una empresa"*.

---

## 1. Inicializar el repositorio (una sola vez, persona A)

```bash
cd tp-devops
git init
git add .
git commit -m "chore: setup inicial del proyecto (Fase 0)"
git branch -M main
git remote add origin https://github.com/USUARIO/tp-devops.git
git push -u origin main
```

Luego en GitHub: **Settings -> Collaborators** -> agregar a la persona B.

## 2. Persona B clona el repo

```bash
git clone https://github.com/USUARIO/tp-devops.git
cd tp-devops
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 3. Proteger la rama main (suma puntos)

En GitHub: **Settings -> Branches -> Add branch protection rule**
- Branch name pattern: `main`
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
  (esto se activa una vez que exista el workflow de CI - Fase 3)

> Bonanni aclaró que la rama protegida con los checks **no es requerida**
> para aprobar, pero el **flujo de mergeo con PRs sí suma 1 punto**.

## 4. Flujo de trabajo por feature (cada cambio)

```bash
# 1. Partir siempre de main actualizado
git checkout main
git pull origin main

# 2. Crear branch descriptiva
git checkout -b feat/api-endpoints

# 3. Trabajar, commitear
git add .
git commit -m "feat: agrega endpoints CRUD de items"

# 4. Subir la branch
git push -u origin feat/api-endpoints

# 5. En GitHub: abrir Pull Request -> pedir review al compañero
# 6. El compañero revisa y aprueba
# 7. Merge a main (Squash and merge recomendado)
# 8. Borrar la branch
```

## 5. Convención de nombres de branches y commits

**Branches:**
- `feat/...`   nueva funcionalidad
- `fix/...`    corrección de bug
- `chore/...`  configuración / tooling
- `docs/...`   documentación

**Commits (Conventional Commits, opcional pero prolijo):**
- `feat:`  nueva funcionalidad
- `fix:`   corrección
- `chore:` config
- `docs:`  documentación
- `test:`  tests
- `ci:`    pipeline

## 6. Recomendación para el TP

Hagan **al menos 3-4 PRs reales con review cruzado** entre ustedes.
Para la presentación/informe, sacar screenshots de:
- La lista de PRs mergeados
- Un PR con el review/aprobación del compañero
- La configuración de branch protection
- El check de CI corriendo dentro del PR

Esto es la evidencia que pide Bonanni para el punto de "flujo de mergeo".
