from app.services.database import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class LeaveBalance(Base):
    """
    Represents a leave balance for a user.
    """
    __tablename__ = "leave_balances"

    id: int = Column(Integer, primary_key=True)
    """
    Unique identifier for the leave balance.
    """

    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    """
    Foreign key referencing the user.
    """

    leave_type_id: int = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    """
    Foreign key referencing the leave type.
    """

    balance: int = Column(Integer, nullable=False)
    """
    Leave balance.
    """

    user = relationship("User", back_populates="leave_balances")
    leave_type = relationship("LeaveType", back_populates="leave_balances")

    def __repr__(self) -> str:
        return f"LeaveBalance(id={self.id}, user_id={self.user_id}, leave_type_id={self.leave_type_id}, balance={self.balance})"