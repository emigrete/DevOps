from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/error-test")
def error_test():
    raise RuntimeError("Error intencional para demostrar visibilidad en monitoreo")
