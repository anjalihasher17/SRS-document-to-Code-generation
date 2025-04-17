from app.services.database import Base
from sqlalchemy import Column, Integer, String, Text

class DashboardTile(Base):
    """
    Represents a dashboard tile.
    """
    __tablename__ = "dashboard_tiles"

    id: int = Column(Integer, primary_key=True)
    """
    Unique identifier for the dashboard tile.
    """

    title: str = Column(String(255), nullable=False)
    """
    Title of the dashboard tile.
    """

    content: str = Column(Text, nullable=False)
    """
    Content of the dashboard tile.
    """

    def __repr__(self) -> str:
        return f"DashboardTile(id={self.id}, title={self.title}, content={self.content})"