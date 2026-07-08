from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, SessionLocal, engine
from app.models.crop import Crop
from app.routers import auth, crops, fields, recommendations
from app.seed_data.crop_coefficients import CROP_COEFFICIENTS


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_crops()
    yield


app = FastAPI(
    title="AquaSense API",
    description="Smart Irrigation Advisory System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_crops() -> None:
    db = SessionLocal()
    try:
        if db.query(Crop).count() > 0:
            return
        for entry in CROP_COEFFICIENTS:
            db.add(
                Crop(
                    name=entry["name"],
                    root_depth_m=entry["root_depth_m"],
                    depletion_fraction_p=entry["depletion_fraction_p"],
                    stages=entry["stages"],
                    stage_lengths_days=entry["stage_lengths_days"],
                    kc_values=entry["kc"],
                )
            )
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(fields.router)
app.include_router(crops.router)
app.include_router(recommendations.router)
