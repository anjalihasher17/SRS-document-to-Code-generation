
            from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
            from sqlalchemy.orm import relationship
            from datetime import datetime
            from app.services.database import Base

            class TimestampMixin:
                """Mixin for adding timestamp fields to models"""
                created_at = Column(DateTime, default=datetime.utcnow)
                updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            