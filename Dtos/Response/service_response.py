from pydantic import BaseModel
from typing import Optional, Generic, TypeVar

T = TypeVar("T")


class ServiceResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
