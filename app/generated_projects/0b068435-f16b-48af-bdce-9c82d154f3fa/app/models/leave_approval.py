from app.services.database import Base
from sqlalchemy import Column, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

class LeaveApproval(Base):
    """
    Represents a leave approval.

    Attributes:
        id (int): Unique identifier for the leave approval.
        leave_request_id (int): Foreign key referencing the leave request.
        manager_id (int): Foreign key referencing the manager who approved/rejected the request.
        approval_status (str): Status of the leave approval (approved or rejected).
        comments (str): Comments from the manager.
    """

    __tablename__ = "leave_approvals"

    id = Column(Integer, primary_key=True)
    leave_request_id = Column(Integer, ForeignKey("leave_requests.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approval_status = Column(Enum("approved", "rejected", name="leave_approval_status"), nullable=False)
    comments = Column(Text)

    leave_request = relationship("LeaveRequest", back_populates="leave_approval")
    manager = relationship("User", back_populates="leave_approvals_as_manager")

    __table_args__ = (
        Index("ix_leave_approvals_leave_request_id", "leave_request_id"),
        Index("ix_leave_approvals_manager_id", "manager_id"),
    )