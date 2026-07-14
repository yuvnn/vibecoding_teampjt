from pydantic import BaseModel, ConfigDict


class TourItemListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_id: str
    title: str
    addr1: str
    tel: str
    first_image: str
    map_x: float | None
    map_y: float | None


class TourItemDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_id: str
    title: str
    addr1: str
    addr2: str
    tel: str
    zipcode: str
    first_image: str
    first_image2: str
    map_x: float | None
    map_y: float | None
    area_code: str
    sigungu_code: str
    cat1: str
    cat2: str
    cat3: str
