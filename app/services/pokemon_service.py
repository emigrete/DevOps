from app.clients.pokeapi_client import get_pokemon


async def fetch_pokemon(name: str) -> dict:
    return await get_pokemon(name)
