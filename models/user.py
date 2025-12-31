import uuid as uuid_pkg
from models.base import BaseModel
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
    
class User(BaseModel):
    __tablename__ = "user"
    
    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), default_factory=lambda: str(uuid_pkg.uuid4()), primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    profile_image_url: Mapped[str] = mapped_column(String, default="https://profileimageurl.com")
    is_superuser: Mapped[bool] = mapped_column(default=False)