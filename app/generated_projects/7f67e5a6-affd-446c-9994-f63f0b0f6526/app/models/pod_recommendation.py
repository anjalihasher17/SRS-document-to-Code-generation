from app.services.database import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class PodRecommendation(Base):
    """
    Represents a pod recommendation.
    """
    __tablename__ = "pod_recommendations"

    id: int = Column(Integer, primary_key=True)
    """
    Unique identifier for the pod recommendation.
    """

    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    """
    Foreign key referencing the User model.
    """

    user = relationship("User", back_populates="pod_recommendations")

    pod_id: int = Column(Integer, ForeignKey("pods.id"), nullable=False)
    """
    Foreign key referencing the Pod model.
    """

    pod = relationship("Pod", back_populates="pod_recommendations")

    recommended_user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    """
    Foreign key referencing the User model (recommended user).
    """

    recommended_user = relationship("User", foreign_keys=[recommended_user_id])

    def __repr__(self) -> str:
        return f"PodRecommendation(id={self.id}, user_id={self.user_id}, pod_id={self.pod_id}, recommended_user_id={self.recommended_user_id})"