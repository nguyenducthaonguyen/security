# app/services/post_service.py
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.post_repository import PostRepository
from app.schemas.posts import PostCreate, PostUpdate, MessageResponse
from app.models.posts import Post
from app.models.users import User

class PostService:
    def __init__(self, db: Session):
        """
        Khởi tạo PostService với một phiên làm việc database.
        Tạo một instance PostRepository để tương tác với DB.
        """
        self.repository = PostRepository(db)

    def _get_user_and_check_status(self, user_id: int) -> User:
        """
        Lấy user theo user_id và kiểm tra trạng thái hoạt động.
        Nếu không tìm thấy hoặc user bị block, raise HTTPException.
        """
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.status:
            raise HTTPException(status_code=403, detail="User is blocked")
        return user

    def create_post(self, post_data: PostCreate, user_id: int) -> Post:
        """
        Tạo mới một bài post cho user có user_id.
        Kiểm tra trạng thái user trước khi tạo.
        """
        self._get_user_and_check_status(user_id)

        new_post = Post(**post_data.dict(), user_id=user_id)
        return self.repository.create_post(new_post)

    def get_posts_by_user_id(self, user_id: int) -> List[Post]:
        """
        Lấy tất cả bài post của user theo user_id.
        Kiểm tra trạng thái user trước khi truy vấn.
        """
        self._get_user_and_check_status(user_id)
        return self.repository.get_posts_by_user_id(user_id)

    def get_post_by_id(self, post_id: int) -> Post:
        """
        Lấy bài post theo post_id.
        Kiểm tra trạng thái user sở hữu bài post.
        Nếu không tìm thấy post hoặc user không hợp lệ, raise HTTPException.
        """
        post = self.repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        self._get_user_and_check_status(post.user_id)
        return post

    def get_all_posts(self) -> List[Post]:
        """
        Lấy tất cả bài post (bất kể trạng thái user).
        """
        return self.repository.get_all_posts()

    def get_all_posts_active_users(self) -> List[Post]:
        """
        Lấy tất cả bài post của những user đang hoạt động (status=True).
        """
        return self.repository.get_all_posts_active_users()

    def update_post(self, post_id: int, post_update: PostUpdate, user_id: int) -> MessageResponse:
        """
        Cập nhật bài post theo post_id nếu user_id là chủ bài.
        Nếu không tìm thấy bài hoặc user không đúng quyền, raise HTTPException.
        """
        post = self.repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

            # Cập nhật thuộc tính ở đây
        post.title = post_update.title
        post.content = post_update.content

        # Gọi repository commit và refresh
        self.repository.update_post(post)

        return MessageResponse(detail="Post updated")


    def delete_post(self, post_id: int, user_id: int) -> MessageResponse:
        """
        Xóa bài post theo post_id nếu user_id là chủ bài.
        Nếu không tìm thấy bài hoặc user không đúng quyền, raise HTTPException.
        """
        post = self.repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        self.repository.delete_post(post)

        return MessageResponse(detail="Post deleted")
