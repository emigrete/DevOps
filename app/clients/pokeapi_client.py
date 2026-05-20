import os
import httpx
import newrelic.agent

POKEAPI_BASE_URL = os.getenv("POKEAPI_BASE_URL", "https://pokeapi.co/api/v2")


# function_trace → span de la capa client; dentro queda anidada la llamada
# HTTP externa a PokeAPI (que el agente instrumenta automáticamente).
@newrelic.agent.function_trace()
async def get_pokemon(name: str) -> dict:
    url = f"{POKEAPI_BASE_URL}/pokemon/{name}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "id": data["id"],
            "name": data["name"],
            "height": data["height"],
            "weight": data["weight"],
        }
