from app.services.database import Base
from sqlalchemy import Column, Integer, Date, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

class LeaveRequest(Base):
    """
    Represents a leave request.

    Attributes:
        id (int): Unique identifier for the leave request.
        user_id (int): Foreign key referencing the user who made the request.
        start_date (date): Start date of the leave.
        end_date (date): End date of the leave.
        reason (str): Reason for the leave.
        status (str): Status of the leave request (pending, approved, or rejected).
        category (str): Category of the leave (paid_leave or sick_leave).
    """

    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum("pending", "approved", "rejected", name="leave_request_status"), nullable=False)
    category = Column(Enum("paid_leave", "sick_leave", name="leave_request_category"), nullable=False)

    user = relationship("User", back_populates="leave_requests")
    leave_approval = relationship("LeaveApproval", back_populates="leave_request")

    __table_args__ = (
        Index("ix_leave_requests_user_id", "user_id"),
    )