from datetime import datetime

from sqlalchemy import ForeignKey, CheckConstraint, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database.engine import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(
        CheckConstraint(
            "value >= 1 AND value <= 5", name="check_valid_evaluation_value"
        )
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), unique=True
    )
    evaluator_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
