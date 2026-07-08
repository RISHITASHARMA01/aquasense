import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models.crop import Crop
from app.seed_data.crop_coefficients import CROP_COEFFICIENTS


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
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
    db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Not used as a context manager so the real startup event (which touches
    # the production engine/db file) doesn't fire during tests.
    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
