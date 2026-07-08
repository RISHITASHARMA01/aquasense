from datetime import date

from sqlalchemy import ForeignKey, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class FieldCrop(Base):
    """A crop instance planted in a field, tracked from planting date."""

    __tablename__ = "field_crops"

    id: Mapped[int] = mapped_column(primary_key=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id"), nullable=False)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), nullable=False)
    planting_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Running soil water depletion tracked in mm, updated by the water balance service daily.
    current_depletion_mm: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(default=True)

    field: Mapped["Field"] = relationship(back_populates="crops")
    crop: Mapped["Crop"] = relationship(back_populates="field_crops")
