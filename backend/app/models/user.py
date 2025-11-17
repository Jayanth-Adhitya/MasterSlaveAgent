from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # employee, manager, tenant, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    sent_notifications = relationship(
        "Notification",
        foreign_keys="Notification.from_user_id",
        back_populates="from_user",
        cascade="all, delete-orphan",
    )
    received_notifications = relationship(
        "Notification",
        foreign_keys="Notification.to_user_id",
        back_populates="to_user",
        cascade="all, delete-orphan",
    )
