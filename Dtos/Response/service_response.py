from typing import Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ServiceResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
