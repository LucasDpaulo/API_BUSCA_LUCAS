"""Modelo SQLAlchemy para histórico de testes."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class TestHistory(Base):
    __tablename__ = "test_history"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    sucesso: Mapped[bool] = mapped_column(Boolean, default=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    logs: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
