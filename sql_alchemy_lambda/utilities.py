import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def get_db_session():
    """
    Creates a session to the database after creating a connection
    :return: Session()
    """
    Session = sessionmaker(
        bind=create_engine(
            os.environ.get("SQLALCHEMY_DATABASE_URI"), poolclass=NullPool
        )
    )
    return Session()

