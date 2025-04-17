from app.services.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Pod(Base):
    """
    Represents a pod.

    Attributes:
        id (int): Unique identifier for the pod.
        name (str): Name of the pod.
    """

    __tablename__ = "pods"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    pod_assignments = relationship("PodAssignment", back_populates="pod")
    pod_recommendations = relationship("PodRecommendation", back_populates="pod")

    __table_args__ = (
        Index("ix_pods_name", "name", unique=True),
    )