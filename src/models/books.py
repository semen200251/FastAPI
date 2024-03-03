from .base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

class Book(BaseModel):
    __tablename__ = "books_table"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int]
    count_pages: Mapped[int]
    seller_fk: Mapped[int] = mapped_column(ForeignKey('selers_table.id'))
    seller_id: Mapped["Seller"] = relationship(back_populates="books", uselist=False)
