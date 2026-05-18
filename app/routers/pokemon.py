from fastapi import APIRouter, HTTPException
import httpx
from app.services import pokemon_service

router = APIRouter(prefix="/pokemon")


@router.get("/{name}")
async def get_pokemon(name: str):
    try:
        return await pokemon_service.fetch_pokemon(name)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"PokeAPI error: {e.response.status_code}")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="PokeAPI unreachable")
