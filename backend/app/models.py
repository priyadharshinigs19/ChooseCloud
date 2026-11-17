
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from sqlalchemy import (
    Integer, String, ForeignKey, Numeric,
    DateTime, Boolean, JSON
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from decimal import Decimal


class CloudProvider(Base):
    __tablename__ = "cloud_providers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )


class CloudService(Base):
    __tablename__ = "cloud_services"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    provider_id: Mapped[int] = mapped_column(
        ForeignKey("cloud_providers.id"),
        nullable=False
    )

    service_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

class ServicePrice(Base):
    __tablename__ = "service_prices"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("cloud_services.id"),
        nullable=False
    )

    region: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    configuration: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    billing_unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 6),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False
    )

    exchange_rate_to_inr: Mapped[Decimal] = mapped_column(
        Numeric(14, 6),
        nullable=False
    )

    source_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ActivityHistory(Base):
    __tablename__ = "activity_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    activity_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    summary: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    input_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    result_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )