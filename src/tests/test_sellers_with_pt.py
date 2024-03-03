import pytest
from fastapi import status
from sqlalchemy import select
from json import loads
from src.models import books, sellers

# Тест на ручку создающую продавца. Тест может ложиться, если другие тесты были запущены вместе с ним (даже для теста books), 
# так как id не будет 1 (Не знаю, как исправить, поэтому не проверяю, что id=1)
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Wrong Code", "last_name": "Robert Martin", "email": "bad@mail.ru", "password": "12345"}
    response = await async_client.post("/api/v1/seller/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": result_data["id"],
        "first_name": "Wrong Code",
        "last_name": "Robert Martin", 
        "email": "bad@mail.ru",
    }

#тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):

    seller = sellers.Seller(first_name="Pushkin", last_name="Eugeny Onegin", email="bad@mail.ru", password="12345")

    seller2 = sellers.Seller(first_name="Pushkin2", last_name="Eugeny Onegin2", email="bad2@mail.ru", password="123456")

    db_session.add_all([seller, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "Pushkin", "last_name": "Eugeny Onegin", "email": "bad@mail.ru", "id": seller.id},
            {"first_name": "Pushkin2", "last_name": "Eugeny Onegin2", "email": "bad2@mail.ru", "id": seller2.id},
        ]
    }

# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):

    seller = sellers.Seller(first_name="Pushkin", last_name="Eugeny Onegin", email="bad@mail.ru", password="12345")

    seller2 = sellers.Seller(first_name="Pushkin2", last_name="Eugeny Onegin2", email="bad2@mail.ru", password="123456")

    db_session.add_all([seller, seller2])
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)
    book_3 = books.Book(author="Lermontov2", title="Mziri2", year=1997, count_pages=104, seller_id=seller2.id)
    db_session.add_all([book, book_2, book_3])
    await db_session.flush()
    books_list = []
    books_list.append(book)
    books_list.append(book_2)
    response = await async_client.get(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    response_data = loads(response.text)

    expected_data = {
        "first_name": "Pushkin",
        "last_name": "Eugeny Onegin",
        "email": "bad@mail.ru",
        "id": seller.id,
        "books": [
            dict(id=book.id, title=book.title, author=book.author, year=book.year, count_pages=book.count_pages)
            for book in books_list
        ]
    }

    assert response_data == expected_data

@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):

    seller = sellers.Seller(first_name="Pushkin", last_name="Eugeny Onegin", email="bad@mail.ru", password="12345")
    db_session.add_all([seller])
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Pushkin2", title="Eugeny Onegin2", year=2001, count_pages=104, seller_id=seller.id)
    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res1 = all_books.scalars().all()
    assert len(res1) == 0
    all_sellers = await db_session.execute(select(sellers.Seller))
    res2 = all_sellers.scalars().all()
    assert len(res2) == 0

# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):

    seller = sellers.Seller(first_name="Pushkin", last_name="Eugeny Onegin", email="bad@mail.ru", password="12345")
    db_session.add(seller)
    await db_session.flush()


    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{seller.id}",
        json={ "first_name": "Clean Code",
                "last_name": "Robert Martin",
                "email": "norm@mail.ru",
                "id": 3
                },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == "Clean Code"
    assert res.last_name == "Robert Martin"
    assert res.email == "norm@mail.ru"
    assert res.id == seller.id