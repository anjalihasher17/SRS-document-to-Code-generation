from app.services.database import Base
from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

class LeaveBalance(Base):
    """
    Represents a leave balance.

    Attributes:
        id (int): Unique identifier for the leave balance.
        user_id (int): Foreign key referencing the user.
        balance (int): Current balance of leaves.
        category (str): Category of the leave (paid_leave or sick_leave).
    """

    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Integer, nullable=False)
    category = Column(Enum("paid_leave", "sick_leave", name="leave_balance_category"), nullable=False)

    user = relationship("User", back_populates="leave_balances")

    __table_args__ = (
        Index("ix_leave_balances_user_id", "user_id"),
    )