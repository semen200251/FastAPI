from sqlalchemy import select
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook, ReturnedBookForSeller
from fastapi import status, Response, APIRouter, Depends
from icecream import ic
from src.configurations.database import get_async_session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.books import Book

books_router = APIRouter(
    tags=["books"],
    prefix="/books"
)

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

@books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(book: IncomingBook, session: DBSession):
    new_book = Book(title = book.title, author = book.author, year = book.year, count_pages = book.count_pages, seller_id = book.seller_id)
    session.add(new_book)
    await session.flush()
    return new_book

@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):
    query = select(Book)
    res = await session.execute(query)
    books = res.scalars().all()
    return {"books": books}

@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    res = await session.get(Book, book_id)
    return res

@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await session.get(Book, book_id)
    ic(deleted_book)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_book:
        await session.delete(deleted_book)

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.


@books_router.put("/{book_id}")
async def update_book(book_id: int, new_data: ReturnedBookForSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if updated_book := await session.get(Book, book_id):
        updated_book.author = new_data.author
        updated_book.title = new_data.title
        updated_book.year = new_data.year
        updated_book.count_pages = new_data.count_pages

        await session.flush()

        return updated_book

    return Response(status_code=status.HTTP_404_NOT_FOUND)