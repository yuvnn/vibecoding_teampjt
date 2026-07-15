from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.services.data_loader import backfill_post_relations, load_tour_data, seed_categories

settings = get_settings()

app = FastAPI(title="LocalHub API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_categories(db)
        loaded = load_tour_data(db)
        if loaded:
            print(f"[startup] tour data {loaded}건 적재 완료")
        migrated = backfill_post_relations(db)
        if migrated:
            print(f"[startup] {migrated}개 게시글의 카테고리/장소를 새 테이블로 이관 완료")
    finally:
        db.close()


@app.get("/")
def health_check():
    return {"status": "ok", "service": "LocalHub API", "region": settings.region}
