from app.services.database import Base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

class PodAssignment(Base):
    """
    Represents a pod assignment.

    Attributes:
        id (int): Unique identifier for the pod assignment.
        pod_id (int): Foreign key referencing the pod.
        user_id (int): Foreign key referencing the user.
        role (str): Role of the user in the pod.
    """

    __tablename__ = "pod_assignments"

    id = Column(Integer, primary_key=True)
    pod_id = Column(Integer, ForeignKey("pods.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)

    pod = relationship("Pod", back_populates="pod_assignments")
    user = relationship("User", back_populates="pod_assignments")

    __table_args__ = (
        Index("ix_pod_assignments_pod_id", "pod_id"),
        Index("ix_pod_assignments_user_id", "user_id"),
    )