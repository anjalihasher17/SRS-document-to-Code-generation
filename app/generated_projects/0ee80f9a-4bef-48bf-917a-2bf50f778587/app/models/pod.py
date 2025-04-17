from app.services.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from typing import List

class Pod(Base):
    """
    Represents a pod.
    """
    __tablename__ = "pods"

    id: int = Column(Integer, primary_key=True)
    """
    Unique identifier for the pod.
    """

    name: str = Column(String(255), nullable=False)
    """
    Name of the pod.
    """

    pod_assignments: List["PodAssignment"] = relationship("PodAssignment", back_populates="pod")
    pod_recommendations: List["PodRecommendation"] = relationship("PodRecommendation", back_populates="pod")

    def __repr__(self) -> str:
        return f"Pod(id={self.id}, name={self.name})"