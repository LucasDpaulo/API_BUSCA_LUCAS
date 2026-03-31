"""Conexão e setup do banco de dados SQLite."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./data.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Cria todas as tabelas no banco."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency do FastAPI — abre e fecha sessão automaticamente."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
