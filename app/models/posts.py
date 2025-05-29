from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.cores.database import Base

class Post(Base):
    __tablename__ = "posts"  # Tên bảng trong cơ sở dữ liệu

    # Khóa chính, tự động tăng, có chỉ mục để truy vấn nhanh
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Tiêu đề bài viết, không được để trống, độ dài tối đa 255 ký tự
    title = Column(String(255), nullable=False)

    # Nội dung bài viết, không được để trống, độ dài tối đa 2000 ký tự
    content = Column(String(2000), nullable=False)

    # Khóa ngoại tham chiếu đến bảng users (cột id)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Thiết lập mối quan hệ với model User (1 User có nhiều Post)
    user = relationship("User", back_populates="posts")
