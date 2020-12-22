from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel

router: APIRouter = APIRouter()


class CoreResponse(BaseModel):
    message: str


@router.get("/", response_model=CoreResponse)
async def root() -> Dict[str, str]:
    return {"message": "This is the open sim service api"}


@router.get("/health", response_model=CoreResponse)
async def health_check() -> Dict[str, str]:
    """
    a call to /health will run a health check against the open-sim-api and will
    return with 200 and an indicator of health if the api is up and operating normally
    """
    return {"message": "The open sim service is running and healthy"}
