from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Field(Base):
    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    soil_type: Mapped[str] = mapped_column(String(50), nullable=False)
    area_hectares: Mapped[float] = mapped_column(Float, nullable=False)
    irrigation_method: Mapped[str] = mapped_column(String(20), default="drip")

    owner: Mapped["User"] = relationship(back_populates="fields")
    crops: Mapped[list["FieldCrop"]] = relationship(back_populates="field", cascade="all, delete-orphan")
