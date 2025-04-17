from app.services.database import Base
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Unique identifier for the user.
        email (str): Email address of the user.
        password (str): Password for the user.
        name (str): Name of the user.
        role (str): Role of the user (employee or manager).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum("employee", "manager", name="user_role"), nullable=False)

    leave_requests = relationship("LeaveRequest", back_populates="user")
    pod_assignments = relationship("PodAssignment", back_populates="user")
    leave_approvals_as_manager = relationship("LeaveApproval", back_populates="manager")
    leave_approvals_as_requester = relationship("LeaveApproval", backref="leave_request.user")
    pod_recommendations_as_recommender = relationship("PodRecommendation", back_populates="recommender")
    pod_recommendations_as_recommended = relationship("PodRecommendation", back_populates="recommended_user")

    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
    )