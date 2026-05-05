from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    skills: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(Text)
