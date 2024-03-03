from .base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

class Seller(BaseModel):
    __tablename__ = "selers_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)

    books: Mapped[list["Book"]] = relationship(back_populates="seller", uselist=True)
