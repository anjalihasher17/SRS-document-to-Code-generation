from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    name = Column(String)
    role = Column(String)

    leave_requests = relationship("LeaveRequest", backref="user")
    pod_assignments = relationship("PodAssignment", backref="user")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    reason = Column(Text)
    status = Column(String)

class Pod(Base):
    __tablename__ = "pods"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    pod_assignments = relationship("PodAssignment", backref="pod")

class PodAssignment(Base):
    __tablename__ = "pod_assignments"
    id = Column(Integer, primary_key=True)
    pod_id = Column(Integer, ForeignKey("pods.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)

class Tile(Base):
    __tablename__ = "tiles"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)