from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.schemas import IncomingSeller, ReturnedSeller, ReturnedAllSellers, ReturnedSellerWithBook, IncomingUpdateSeller
from fastapi import status, Response, APIRouter, Depends
from icecream import ic
from src.configurations.database import get_async_session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.sellers import Seller

sellers_router = APIRouter(
    tags=["selers"],
    prefix="/seller"
)

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncomingSeller, session: DBSession):
    new_seller = Seller(first_name = seller.first_name, last_name = seller.last_name, email = seller.email, password = seller.password)
    session.add(new_seller)
    await session.flush()
    return new_seller

@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}

@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBook)
async def get_seller(seller_id: int, session: DBSession):
    seller = await session.execute(
        select(Seller).options(selectinload(Seller.books)).filter(Seller.id == seller_id)
    )
    
    seller = seller.scalar_one_or_none()
    return seller

@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    # Загружаем продавца с предварительной загрузкой связанных книг
    deleted_seller = await session.execute(
        select(Seller).options(selectinload(Seller.books)).filter(Seller.id == seller_id)
    )

    deleted_seller = deleted_seller.scalar_one_or_none()

    if deleted_seller:
        # Удаляем книги, связанные с продавцом
        for book in deleted_seller.books:
            await session.delete(book)

        # Теперь удаляем самого продавца
        await session.delete(deleted_seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: IncomingUpdateSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)