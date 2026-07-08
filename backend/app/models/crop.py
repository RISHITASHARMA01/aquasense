from sqlalchemy import String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Crop(Base):
    """A crop reference entry with FAO-56 style Kc values per growth stage.

    stage_lengths_days / kc_values are aligned lists, e.g.
    stages = ["initial", "development", "mid", "late"]
    stage_lengths_days = [20, 30, 40, 15]
    kc_values = [0.35, 0.7, 1.15, 0.7]
    """

    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    root_depth_m: Mapped[float] = mapped_column(Float, nullable=False)
    depletion_fraction_p: Mapped[float] = mapped_column(Float, nullable=False)
    stages: Mapped[list] = mapped_column(JSON, nullable=False)
    stage_lengths_days: Mapped[list] = mapped_column(JSON, nullable=False)
    kc_values: Mapped[list] = mapped_column(JSON, nullable=False)

    field_crops: Mapped[list["FieldCrop"]] = relationship(back_populates="crop")
