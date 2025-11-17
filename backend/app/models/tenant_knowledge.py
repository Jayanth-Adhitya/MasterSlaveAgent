from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class TenantKnowledge(Base):
    __tablename__ = "tenant_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # Gemini embedding dimension
    category = Column(String(100), nullable=False)  # schedule, roster, rules, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="knowledge")
