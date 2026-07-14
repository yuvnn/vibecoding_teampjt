"""초기 데이터 적재 스크립트.

사용법 (backend/ 디렉터리에서 실행):
    python -m scripts.seed_db
"""

from app.core.database import Base, SessionLocal, engine
from app.services.data_loader import load_tour_data, seed_categories


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        created = seed_categories(db)
        print(f"categories {created}건 생성")
        loaded = load_tour_data(db)
        print(f"tour_items {loaded}건 적재 완료")
    finally:
        db.close()


if __name__ == "__main__":
    main()
