from app.services.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from typing import List

class LeaveType(Base):
    """
    Represents a type of leave.
    """
    __tablename__ = "leave_types"

    id: int = Column(Integer, primary_key=True)
    """
    Unique identifier for the leave type.
    """

    name: str = Column(String(50), nullable=False)
    """
    Name of the leave type.
    """

    leave_balances: List["LeaveBalance"] = relationship("LeaveBalance", back_populates="leave_type")

    def __repr__(self) -> str:
        return f"LeaveType(id={self.id}, name={self.name})"