from models.base import BaseModel
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Post(BaseModel):
    __tablename__ = "post"

    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String(30))
    body: Mapped[str] = mapped_column(String(63206))
    media_url: Mapped[str | None] = mapped_column(String, default=None)