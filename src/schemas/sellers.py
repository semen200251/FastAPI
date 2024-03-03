from typing import List, Dict, Union
from pydantic import BaseModel
from .books import ReturnedBookForSeller

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers", "ReturnedSellerWithBook", "IncomingUpdateSeller"]

class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str

class IncomingSeller(BaseSeller):
    password: str

class IncomingUpdateSeller(IncomingSeller):
    id: int

class ReturnedSeller(BaseSeller):
    id:int

class ReturnedSellerWithBook(ReturnedSeller):
    books: list[ReturnedBookForSeller]

    
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]