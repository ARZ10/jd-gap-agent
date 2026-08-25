import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
# Base is not useless. It inherits from DeclarativeBase. DeclarativeBase(from SQLALchemy)
# is the class that contains all the real machinery. The code that knows how to turn a Python
# class with `Mapped[...]` type annotation into an actual SQL table definition.

