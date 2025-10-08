from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String(20), nullable=False)
    payment_intent_id = Column(String, nullable=False)
    escrow_id = Column(Integer, ForeignKey("escrows.id"), nullable=False)

    escrow = relationship("Escrow", back_populates="payments")