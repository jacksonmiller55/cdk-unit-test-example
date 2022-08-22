from sqlalchemy import Column, Integer, String, SmallInteger
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sql_alchemy_lambda.dbmodels import BaseModel


class Review(BaseModel):
    """
    Our Review class
    """
    __tablename__ = 'review'
    _serialize_columns_only = True

    id = Column(Integer, primary_key=True)
    reviewer = Column(String(100), nullable=False)
    rate = Column(SmallInteger, nullable=False)  # 1-5 stars
    review = Column(String(500), nullable=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship("Book", back_populates="reviews")



