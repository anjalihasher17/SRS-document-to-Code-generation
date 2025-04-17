from app.services.database import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class PodRecommendation(Base):
    """
    Represents a pod recommendation.

    Attributes:
        id (int): Unique identifier for the pod recommendation.
        pod_id (int): Foreign key referencing the pod.
        recommended_user_id (int): Foreign key referencing the recommended user.
    """

    __tablename__ = "pod_recommendations"

    id = Column(Integer, primary_key=True)
    pod_id = Column(Integer, ForeignKey("pods.id"), nullable=False)
    recommended_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    pod = relationship("Pod", back_populates="pod_recommendations")
    recommender = relationship("User", foreign_keys=[recommended_user_id], back_populates="pod_recommendations_as_recommender")
    recommended_user = relationship("User", back_populates="pod_recommendations_as_recommended")

    __table_args__ = (
        Index("ix_pod_recommendations_pod_id", "pod_id"),
        Index("ix_pod_recommendations_recommended_user_id", "recommended_user_id"),
    )