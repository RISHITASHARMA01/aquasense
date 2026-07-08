from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models.crop import Crop
from app.schemas.crop import CropRead

router = APIRouter(prefix="/crops", tags=["crops"])


@router.get("", response_model=list[CropRead])
def list_crops(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return db.query(Crop).order_by(Crop.name).all()
