from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, HttpUrl
from pydantic.generics import GenericModel

from app.schemas.users import UserWithPostsResponse, UserRead


class PaginationSchema(BaseModel):
    total: int
    limit: int
    offset: int

class LinkSchema(BaseModel):
    self: HttpUrl
    next: Optional[HttpUrl] = None
    last: HttpUrl

class DataResponseSchema(BaseModel):
    items: List[UserWithPostsResponse]
    pagination: PaginationSchema
    link: LinkSchema

class StandardResponseSchema(BaseModel):
    status_code: int
    message: str
    data: List[UserWithPostsResponse]
    pagination: PaginationSchema
    link: LinkSchema

class MessageResponse(BaseModel):
    detail: str

T = TypeVar("T")

class StandardResponse(GenericModel, Generic[T]):
    status_code: int
    message: str
    data: T