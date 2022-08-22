from sqlalchemy import Column, Integer, String, SmallInteger
from sqlalchemy.orm import relationship

from sql_alchemy_lambda.dbmodels.review import Review
from sql_alchemy_lambda.dbmodels.base import BaseModel


class Book(BaseModel):
    """
    Our Book class
    """
    __tablename__ = 'book'
    _serialize_columns_only = True

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    publisher = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)


# 1 Book <-> 0 or more Reviews
Book.reviews = relationship("Review", order_by=Review.id, back_populates="book")
