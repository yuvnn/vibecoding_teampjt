import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.category import Category
from app.models.tour_item import TourItem
from app.models.tour_master import TourMaster

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"

DEFAULT_CATEGORIES = [
    {"name": "관광지", "slug": "tour"},
    {"name": "맛집", "slug": "food"},
    {"name": "축제·행사", "slug": "festival"},
]


def seed_categories(db: Session) -> int:
    """커뮤니티 게시판 카테고리 기본값을 없는 것만 골라 채운다 (idempotent)."""
    created = 0
    for entry in DEFAULT_CATEGORIES:
        exists = db.execute(
            select(Category).where(Category.slug == entry["slug"])
        ).scalar_one_or_none()
        if not exists:
            db.add(Category(**entry))
            created += 1
    db.commit()
    return created


def _find_json_files() -> list[Path]:
    """data/raw/ 아래 모든 권역 폴더의 *.json 파일을 수집한다.

    제공 데이터는 5개 권역(서울/대전_충청권/구미_경북권/광주_전라권/부산)별 하위 폴더로
    내려오며, 서버 시작 시 전 권역 데이터를 tour_masters/tour_items에 적재한다.
    """
    json_files = []
    for folder in sorted(DATA_DIR.iterdir()):
        if folder.is_dir():
            json_files.extend(sorted(folder.glob("*.json")))
    return json_files


def load_tour_data(db: Session) -> int:
    """선정 권역의 data/raw/<권역>/*.json (TourAPI 4.0 포맷)을 tour_masters/tour_items에 적재.

    파일 하나(권역 x 콘텐츠유형)당 tour_masters 1행, items[] 각각이 tour_items 1행이 된다.
    """
    loaded = 0
    for json_file in _find_json_files():
        payload = json.loads(json_file.read_text(encoding="utf-8"))
        region = payload.get("region", "")
        content_type = payload.get("contentType", "")
        content_type_id = int(payload.get("contentTypeId") or 0)

        master = db.execute(
            select(TourMaster).where(
                TourMaster.region == region,
                TourMaster.content_type_id == content_type_id,
            )
        ).scalar_one_or_none()
        if not master:
            master = TourMaster(
                region=region,
                content_type=content_type,
                content_type_id=content_type_id,
                total=int(payload.get("total") or 0),
            )
            db.add(master)
            db.flush()

        for item in payload.get("items", []):
            content_id = item.get("contentid")
            if not content_id:
                continue
            exists = db.execute(
                select(TourItem).where(TourItem.content_id == content_id)
            ).scalar_one_or_none()
            if exists:
                continue
            db.add(
                TourItem(
                    master_id=master.id,
                    content_id=content_id,
                    title=item.get("title", ""),
                    addr1=item.get("addr1", ""),
                    addr2=item.get("addr2", ""),
                    tel=item.get("tel", ""),
                    zipcode=item.get("zipcode", ""),
                    first_image=item.get("firstimage", ""),
                    first_image2=item.get("firstimage2", ""),
                    map_x=float(item["mapx"]) if item.get("mapx") else None,
                    map_y=float(item["mapy"]) if item.get("mapy") else None,
                    m_level=int(item["mlevel"]) if item.get("mlevel") else None,
                    area_code=item.get("areacode", ""),
                    sigungu_code=item.get("sigungucode", ""),
                    cat1=item.get("cat1", ""),
                    cat2=item.get("cat2", ""),
                    cat3=item.get("cat3", ""),
                    created_time=item.get("createdtime", ""),
                    modified_time=item.get("modifiedtime", ""),
                )
            )
            loaded += 1
    db.commit()
    return loaded
