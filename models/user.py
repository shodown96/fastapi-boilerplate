from models.base import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
    
class User(BaseModel):
    __tablename__ = "user"
    
    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    profile_image_url: Mapped[str] = mapped_column(String, default="https://profileimageurl.com")
    is_superuser: Mapped[bool] = mapped_column(default=False)