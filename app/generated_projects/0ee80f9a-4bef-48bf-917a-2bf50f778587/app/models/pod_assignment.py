from app.services.database import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class PodAssignment(Base):
    """
    Represents an assignment of a user to a pod.
    """
    __tablename__ = "pod_assignments"

    id: int = Column(Integer, primary_key=True)
    """
    Unique identifier for the pod assignment.
    """

    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    """
    Foreign key referencing the user assigned to the pod.
    """

    pod_id: int = Column(Integer, ForeignKey("pods.id"), nullable=False)
    """
    Foreign key referencing the pod.
    """

    user = relationship("User", back_populates="pod_assignments")
    pod = relationship("Pod", back_populates="pod_assignments")

    def __repr__(self) -> str:
        return f"PodAssignment(id={self.id}, user_id={self.user_id}, pod_id={self.pod_id})"