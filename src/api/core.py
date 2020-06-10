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
    return {"message": "The open sim service is running and healthy"}
