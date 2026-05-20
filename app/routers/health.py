from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    # DEMO: bug intencional para mostrar que el CI (test_health) frena el merge.
    # NO mergear — esta branch es solo para demostrar el Andon Cord.
    return {"status": "broken"}


@router.get("/error-test")
def error_test():
    raise RuntimeError("Error intencional para demostrar visibilidad en monitoreo")
