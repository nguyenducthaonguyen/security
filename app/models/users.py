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
    __tablename__ = "users"  # Tên bảng trong cơ sở dữ liệu

    # ID người dùng, khóa chính, có chỉ mục để tối ưu truy vấn
    id = Column(Integer, primary_key=True, index=True)

    # Tên đăng nhập, phải duy nhất, có chỉ mục
    username = Column(String(255), unique=True, index=True)

    # Email, phải duy nhất, có chỉ mục
    email = Column(String(255), unique=True, index=True)

    # Mật khẩu đã mã hóa, không được để trống
    password = Column(String(255), nullable=False)

    # Họ và tên đầy đủ của người dùng
    fullname = Column(String(255), nullable=False)

    # Giới tính: male / female / other (sử dụng Enum)
    gender = Column(Enum(GenderEnum), nullable=False)

    # Trạng thái tài khoản: True (hoạt động), False (bị khóa)
    status = Column(Boolean, default=True, nullable=False)

    # Vai trò của người dùng: admin / user (mặc định là user)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)

    # Mối quan hệ với các bài viết (1 người dùng có thể có nhiều bài viết)
    posts = relationship("Post", back_populates="user")
