import newrelic.agent
from app.clients.pokeapi_client import get_pokemon


# function_trace → span propio de la capa service en la traza de New Relic,
# para visualizar la cadena router -> service -> client -> API externa.
# Ref: https://docs.newrelic.com/docs/apm/agents/python-agent/python-agent-api/functiontrace-python-agent-api/
@newrelic.agent.function_trace()
async def fetch_pokemon(name: str) -> dict:
    return await get_pokemon(name)
