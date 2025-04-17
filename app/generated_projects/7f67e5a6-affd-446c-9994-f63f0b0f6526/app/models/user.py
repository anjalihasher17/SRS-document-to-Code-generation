from app.services.database import Base
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from typing import List

class User(Base):
    """
    Represents a user in the system.
    """
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    """
    Unique identifier for the user.
    """

    email: str = Column(String(255), unique=True, nullable=False)
    """
    Email address of the user.
    """

    password: str = Column(String(255), nullable=False)
    """
    Password for the user.
    """

    name: str = Column(String(255), nullable=False)
    """
    Name of the user.
    """

    role: str = Column(Enum("manager", "employee", name="user_roles"), nullable=False)
    """
    Role of the user (either 'manager' or 'employee').
    """

    leave_requests: List["LeaveRequest"] = relationship("LeaveRequest", back_populates="user")
    pod_assignments: List["PodAssignment"] = relationship("PodAssignment", back_populates="user")
    pod_recommendations: List["PodRecommendation"] = relationship("PodRecommendation", back_populates="user")
    leave_balances: List["LeaveBalance"] = relationship("LeaveBalance", back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, name={self.name}, role={self.role})"