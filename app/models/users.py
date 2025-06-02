from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from app.cores.database import Base

# Enum định nghĩa các vai trò người dùng
class RoleEnum(enum.Enum):
    admin = "admin"
    user = "user"

# Enum định nghĩa giới tính
class GenderEnum(enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255), nullable=False)
    fullname = Column(String(255), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)

    posts = relationship("Post", back_populates="user")

    sessions = relationship("Session", back_populates="user", cascade="all, delete")

    active_access_tokens = relationship("ActiveAccessToken", back_populates="user")
