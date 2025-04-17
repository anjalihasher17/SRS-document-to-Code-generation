from app.services.database import Base
from sqlalchemy import Column, Integer, Date, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from typing import List

class LeaveRequest(Base):
    """
    Represents a leave request.
    """
    __tablename__ = "leave_requests"

    id: int = Column(Integer, primary_key=True)
    """
    Unique identifier for the leave request.
    """

    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    """
    Foreign key referencing the user who made the leave request.
    """

    start_date: date = Column(Date, nullable=False)
    """
    Start date of the leave.
    """

    end_date: date = Column(Date, nullable=False)
    """
    End date of the leave.
    """

    reason: str = Column(Text, nullable=False)
    """
    Reason for the leave.
    """

    status: str = Column(Enum("pending", "approved", "rejected", name="leave_request_statuses"), nullable=False)
    """
    Status of the leave request (pending, approved, or rejected).
    """

    user = relationship("User", back_populates="leave_requests")

    def __repr__(self) -> str:
        return f"LeaveRequest(id={self.id}, user_id={self.user_id}, start_date={self.start_date}, end_date={self.end_date}, status={self.status})"