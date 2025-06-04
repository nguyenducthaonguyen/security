from pydantic import BaseModel, constr

# Schema cơ bản cho bài viết
class PostBase(BaseModel):
    title: constr(min_length=3, max_length=255)     # Tiêu đề bài viết
    content: constr(min_length=3, max_length=2000)  # Nội dung bài viết

# Schema dùng để tạo bài viết
class PostCreate(PostBase):
    pass

# Schema dùng để cập nhật bài viết
class PostUpdate(PostBase):
    pass

# Schema dùng để đọc dữ liệu bài viết trả về client
class PostRead(PostBase):
    id: int
    user_id: int

    # Cấu hình theo chuẩn Pydantic v2 để hỗ trợ ORM
    model_config = {
        "from_attributes": True  # Thay cho orm_mode = True trong Pydantic v1
    }

# Schema dùng để trả về thông báo dạng text
class MessageResponse(BaseModel):
    detail: str


class PostResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True