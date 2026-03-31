"""Modelo SQLAlchemy do Tenant (RF01 + RNF01)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.security.crypto import decrypt


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    hinova_token: Mapped[str] = mapped_column(Text, nullable=False)
    hinova_usuario: Mapped[str] = mapped_column(String(255), nullable=False)
    hinova_senha: Mapped[str] = mapped_column(Text, nullable=False)
    quepasa_token: Mapped[str] = mapped_column(Text, nullable=False)
    quepasa_base_url: Mapped[str] = mapped_column(
        String(500), nullable=False, default="http://localhost:31000"
    )
    whatsapp_destino: Mapped[str] = mapped_column(String(20), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_envio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ultimo_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def get_hinova_token(self) -> str:
        """Retorna o token Hinova decifrado."""
        return decrypt(self.hinova_token)

    def get_hinova_senha(self) -> str:
        """Retorna a senha Hinova decifrada."""
        return decrypt(self.hinova_senha)

    def get_quepasa_token(self) -> str:
        """Retorna o token Quepasa decifrado."""
        return decrypt(self.quepasa_token)
