from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, ForeignKey, Boolean

from backend.core.database.engine import Base


class BusinessElement(Base):
    __tablename__ = "business_elements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


class AccessRule(Base):
    """Правила доступа: определяет, какие права есть у роли на ресурс"""

    __tablename__ = "access_rules"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    business_element_id: Mapped[int] = mapped_column(
        ForeignKey("business_elements.id"), nullable=False
    )
    business_element: Mapped[BusinessElement] = relationship(backref="access_rules")
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role = relationship("Role")

    policies: Mapped[dict] = mapped_column(JSONB, default=dict, server_default='{}')