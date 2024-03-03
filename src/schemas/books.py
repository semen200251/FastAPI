from pydantic import BaseModel, field_validator, ValidationError, Field
from pydantic_core import PydanticCustomError


__all__ = ["IncomingBook", "ReturnedBook", "ReturnedAllBooks"]

class BaseBook(BaseModel):
    title: str
    author: str
    year: int

class IncomingBook(BaseBook):
    year: int = 2024
    count_pages: int = Field(alias="pages", default=300)
    seller_fk: int
    @field_validator("year")
    @staticmethod
    def validate_year(val: int):
        if val < 1000:
            raise PydanticCustomError("The answer error", "Year is wrong")
        return val

class ReturnedBook(BaseBook):
    seller_fk: int
    id: int
    count_pages: int

class ReturnedBookForSeller(BaseBook):
    id: int
    count_pages: int
    
class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]