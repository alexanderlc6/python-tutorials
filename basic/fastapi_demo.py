from typing import Dict

import fastapi
from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy import DateTime, func, String, Float, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
import datetime
from contextlib import asynccontextmanager

from unstructured_client.utils import retry

DB_URL = 'mysql+asyncmy://root:602231903@localhost:3306/py_tutorial?charset=utf8mb4'
async_engine = create_async_engine(DB_URL, echo=True, pool_size=10, max_overflow=20)

class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), insert_default=func.now, comment='Create Time')
    update_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), insert_default=func.now, onupdate=func.now, comment='Update Time')

class Book(Base):
    __tablename__='book'
    id: Mapped[int] = mapped_column(primary_key=True, comment='Book ID')
    book_name: Mapped[str] = mapped_column(String(255), comment='Book Name')
    author: Mapped[str] = mapped_column(String(255), comment='Author')
    price: Mapped[float] = mapped_column(comment='Price')
    publisher: Mapped[str] = mapped_column(String(255), comment='Publisher')

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Initializing database...')
    await create_tables()
    print('Database Initialized!')
    yield
    await async_engine.dispose()

app = FastAPI(lifespan=lifespan)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

# Dependency function
async def get_database():
   async with AsyncSessionLocal() as session:
       try:
           yield session
           await session.commit()
       except Exception:
           await session.rollback()
           raise
       finally:
           await session.close()


# @app.on_event("startup")
# async def startup_event():
#     await create_tables()

@app.get('/')
async def root():
    return {'message': 'Hello World'}

@app.get('/book/count')
async def get_book_count(db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(func.count(Book.id)))
    count = result.scalar()
    return count

@app.get('/book/list')
async def get_book_list(db: AsyncSession = Depends(get_database)):
    # Get ORM objects
    # & | ~ match mode
    # result = await db.execute(select(Book).where((Book.author.like('df%')) & (Book.price < 10)))
    id_list = [1,3]
    result = await db.execute(select(Book).where(Book.id.in_(id_list)))

    # Query all records
    books = result.scalars().all()

    # Query first record
    # books = result.scalars().first()

    # Query record by ID key field
    # books = await db.get(Book, 1)
    return books

@app.get('/book/{book_id}')
async def get_book_info(book_id: int, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    return book

@app.get('/book/search')
async def search_books(db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Book).where(Book.price >= 200))
    book = result.scalars().all()
    return book