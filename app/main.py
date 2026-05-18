from fastapi import FastAPI
from app.db.database import create_tables
from app.routers import health, items, pokemon

app = FastAPI(
    title="TP DevOps API",
    description="API de ejemplo para demostrar CI/CD, dockerización y monitoreo con New Relic.",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    create_tables()


app.include_router(health.router)
app.include_router(items.router)
app.include_router(pokemon.router)
