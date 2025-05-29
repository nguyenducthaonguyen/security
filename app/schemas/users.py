from pydantic import BaseModel, EmailStr, constr, field_validator
from app.models.users import GenderEnum, RoleEnum


class UserCreate(BaseModel):
    """
    Schema dùng để nhận dữ liệu tạo mới User từ client
    """
    username: constr(min_length=3, max_length=100)
    password: constr(min_length=8, max_length=32)
    email: EmailStr
    fullname: constr(min_length=3, max_length=100)
    gender: GenderEnum


class UserRead(BaseModel):
    """
    Schema dùng để trả dữ liệu User cơ bản (không bao gồm mật khẩu) cho client
    """
    id: int
    username: constr(min_length=3, max_length=100)
    email: EmailStr
    fullname: constr(min_length=3, max_length=100)
    gender: GenderEnum
    role: RoleEnum

    model_config = {
        "from_attributes": True,  # Cho phép tạo model từ object ORM (SQLAlchemy)
    }


class UserReadAdmin(UserRead):
    """
    Schema trả dữ liệu User dành cho admin,
    bao gồm thêm trường status để biết trạng thái tài khoản
    """
    status: bool


class TokenResponse(BaseModel):
    """
    Schema dùng để trả token xác thực khi đăng nhập thành công
    """
    access_token: str
    token_type: str
    id: int
    username: constr(min_length=3, max_length=100)


class UserUpdateRequest(BaseModel):
    """
    Schema dùng để nhận dữ liệu cập nhật thông tin User
    """
    email: EmailStr
    fullname: constr(min_length=3, max_length=100)
    gender: GenderEnum


class PasswordChangeRequest(BaseModel):
    """
    Schema dùng để nhận dữ liệu đổi mật khẩu,
    bao gồm mật khẩu cũ, mật khẩu mới và xác nhận mật khẩu mới
    """
    password_old: constr(min_length=8, max_length=32)
    password: constr(min_length=8, max_length=32)
    password_confirmation: constr(min_length=8, max_length=32)

    @field_validator("password_confirmation")
    def passwords_match(cls, v, info):
        """
        Validator kiểm tra password_confirmation phải trùng với password mới
        """
        password = info.data.get("password")
        if v != password:
            raise ValueError("Password confirmation does not match")
        return v


class MessageResponse(BaseModel):
    """
    Schema dùng để trả về thông báo đơn giản
    """
    detail: str
