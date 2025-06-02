from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# Chỉ load .env nếu không ở production
if os.getenv("ENV", "development") != "production":
    from dotenv import load_dotenv
    load_dotenv()

# Lấy URL kết nối database từ biến môi trường, nếu không có thì dùng giá trị mặc định
DATABASE_CONNECTION = os.environ["DATABASE_CONNECTION"]


# Tạo engine để kết nối với cơ sở dữ liệu
engine = create_engine(DATABASE_CONNECTION)

# Tạo lớp SessionLocal để quản lý phiên làm việc với database
# autocommit=False: không tự động commit sau mỗi câu lệnh
# autoflush=False: không tự động flush dữ liệu về database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Tạo lớp cơ sở để khai báo các model (bảng dữ liệu)
Base = declarative_base()
