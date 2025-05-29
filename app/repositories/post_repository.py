from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.posts import Post
from app.models.users import User

class PostRepository:
    def __init__(self, db: Session):
        """
        Khởi tạo repository với một phiên làm việc DB (Session).
        """
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Lấy user theo user_id.
        Trả về User hoặc None nếu không tìm thấy.
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """
        Lấy bài post theo post_id.
        Trả về Post hoặc None nếu không tìm thấy.
        """
        return self.db.query(Post).filter(Post.id == post_id).first()

    def create_post(self, post: Post) -> Post:
        """
        Tạo mới bài post trong DB.
        """
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_posts_by_user_id(self, user_id: int) -> List[Post]:
        """
        Lấy danh sách tất cả bài post của user có user_id.
        """
        return self.db.query(Post).filter(Post.user_id == user_id).all()

    def get_all_posts(self) -> List[Post]:
        """
        Lấy tất cả bài post trong DB.
        """
        return self.db.query(Post).all()

    def get_all_posts_active_users(self) -> List[Post]:
        """
        Lấy tất cả bài post của các user đang hoạt động (User.status == True).
        """
        return (
            self.db.query(Post)
            .join(User, Post.user_id == User.id)
            .filter(User.status.is_(True))
            .all()
        )

    def update_post(self, post: Post) -> Post:
        """
        Commit và refresh post đã được cập nhật thuộc tính bên ngoài.
        """
        self.db.commit()
        self.db.refresh(post)
        return post


    def delete_post(self, post: Post):
        """
        Xóa bài post khỏi DB.
        """
        self.db.delete(post)
        self.db.commit()
