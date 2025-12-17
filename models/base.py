import uuid as uuid_pkg
from datetime import UTC, datetime

from core.db import Base
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

default_uuid_factory=lambda: str(uuid_pkg.uuid4())
    
class BaseModel(Base):
    __abstract__ = True
    id: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), default_factory=default_uuid_factory, unique=True, init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC), init=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, init=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, init=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True, init=False)
    
    
