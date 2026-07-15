import logging

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.models.chat_message import ChatMessage
from app.models.chat_room import ChatRoom
from app.models.tour_item import TourItem
from app.models.tour_master import TourMaster
from app.schemas.chatbot import ChatPlaceRef

settings = get_settings()

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI

        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


BASE_SYSTEM_PROMPT = (
    "당신은 지역 정보를 안내하는 LocalHub 챗봇입니다. "
    "관광지 추천, 축제 일정, 맛집 위치, 커뮤니티 게시글 검색 등 지역 생활 정보 질문에만 답변하세요. "
    "[가드레일] 인사말이나 가벼운 안부 인사(예: '안녕', '안녕하세요', '반가워', '고마워')에는 짧고 "
    "친근하게 인사로 답하면서 자연스럽게 지역 정보를 도와줄 수 있다고 안내하세요 — 이런 인사는 거절 대상이 "
    "아닙니다. 하지만 그 외에 질문이 지역 정보(관광지·맛집·축제·게시판 이용 등)와 무관하면(예: 일반 상식, "
    "코딩, 수학·과제 풀이, 시사, 개인 고민 상담, 다른 서비스 안내 등) 절대 답변을 시도하지 말고, "
    "다른 말 없이 정확히 다음과 같이만 답하세요: "
    "'죄송해요, 저는 지역 관광지·맛집·축제·게시판 관련 질문만 도와드릴 수 있어요. 다른 걸 여쭤봐 주시겠어요?' "
    "[참고 자료]가 주어지면 그 범위 안에서 구체적으로 답변하세요. "
    "[참고 자료]가 없더라도 질문이 지역 정보와 관련 있다면, 정확히 맞는 정보를 찾지 못했다고 먼저 솔직히 말하되 "
    "거기서 대화를 끝내지 말고, 당신이 알고 있는 일반적인 지역 정보나 다른 대안을 자연스럽게 추천하세요."
)

# LLM 검색어 추출이 고를 수 있는 어휘 — 실제 tour_masters 테이블에 존재하는 값만 나열한다.
# (region은 data/raw 폴더명, category는 TourAPI contentType 한글명과 동일해야 SQL 필터가 먹는다.)
REGION_KEYWORDS = ["대전_충청권", "서울", "구미_경북권", "광주_전라권", "부산"]
CATEGORY_KEYWORDS: dict[str, int] = {
    "관광지": 12,
    "문화시설": 14,
    "축제공연행사": 15,
    "여행코스": 25,
    "레포츠": 28,
    "숙박": 32,
    "쇼핑": 38,
    "맛집": 39,
    "음식점": 39,
}

# 헤더에서 선택한 권역에 맞춰 챗봇이 그 지역 사투리 톤으로 답하도록 하는 지시문.
# data/raw 폴더명(=tour_masters.region 값)과 동일한 키를 사용한다.
DIALECT_PROMPTS: dict[str, str] = {
    "부산": "부산/경상도 사투리를 섞어서 답변하세요 (예: ~하노, ~아이가, ~합니더). 어미는 자연스럽게, 정보 전달은 정확하게.",
    "구미_경북권": "경상북도 사투리를 섞어서 답변하세요 (예: ~하니껴, ~라예, ~아이가). 어미는 자연스럽게, 정보 전달은 정확하게.",
    "광주_전라권": "전라도 사투리를 섞어서 답변하세요 (예: ~잉, ~허구만, ~랑께요). 어미는 자연스럽게, 정보 전달은 정확하게.",
    "대전_충청권": "충청도 사투리를 섞어서 답변하세요 (예: ~유, ~혀유, 느긋하고 여유로운 말투). 어미는 자연스럽게, 정보 전달은 정확하게.",
    "서울": "표준어로 정중하게 답변하세요.",
}


def _build_system_prompt(region: str | None) -> str:
    prompt = BASE_SYSTEM_PROMPT
    dialect = DIALECT_PROMPTS.get(region or "")
    if dialect:
        prompt += f"\n\n[말투 지침] {dialect}"
    return prompt


def _extract_search_terms(message: str) -> list[str]:
    """사용자 메시지에서 DB에 실제 존재하는 지역/카테고리 키워드만 LLM으로 골라낸다.

    목록에 없는 단어를 모델이 지어내더라도, 우리가 아는 어휘(REGION_KEYWORDS +
    CATEGORY_KEYWORDS)에 포함된 것만 최종적으로 채택해 SQL 필터에 안전하게 쓴다.
    """
    vocabulary = REGION_KEYWORDS + list(CATEGORY_KEYWORDS.keys())
    prompt = (
        "다음은 검색에 사용할 수 있는 키워드 목록입니다:\n"
        f"{', '.join(vocabulary)}\n\n"
        "아래 사용자 질문과 관련 있는 키워드를 이 목록 중에서만 골라 쉼표로 구분해 답하세요. "
        "목록에 없는 단어는 절대 새로 만들지 마세요. 관련 있는 키워드가 하나도 없으면 "
        "다른 말 없이 정확히 `없음` 이라고만 답하세요.\n\n"
        f"사용자 질문: {message}"
    )
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-5-mini", messages=[{"role": "user", "content": prompt}]
        )
        raw = (response.choices[0].message.content or "").strip()
    except Exception:
        logging.exception("Search-term extraction failed")
        return []

    # comma-split을 신뢰하기보다, 모델 출력 안에 실제로 등장하는 어휘만 채택한다
    # (형식을 살짝 어겨도 안전하게 동작하도록).
    return [term for term in vocabulary if term in raw]


def _search_context(
    db: Session, message: str, region: str | None
) -> tuple[str, list[TourItem]]:
    """LLM이 뽑은 지역/카테고리 키워드로 tour_items를 검색해 근거 자료(RAG 컨텍스트)를 구성한다.

    관련 키워드가 하나도 없으면 검색 자체를 생략하고 빈 컨텍스트를 반환한다 — 이 경우
    시스템 프롬프트의 지침에 따라 "정보를 찾지 못했다"고 답하면서 다른 추천으로 넘어간다.
    반환하는 TourItem 목록은 프론트에서 '경로에 추가' 버튼을 그릴 수 있도록 응답에도 실어 보낸다.
    """
    terms = _extract_search_terms(message)
    if not terms:
        return "", []

    region_terms = [t for t in terms if t in REGION_KEYWORDS]
    category_terms = [t for t in terms if t in CATEGORY_KEYWORDS]

    conditions = []
    effective_region = region_terms[0] if region_terms else region
    if effective_region:
        conditions.append(TourItem.master.has(TourMaster.region == effective_region))
    if category_terms:
        type_ids = {CATEGORY_KEYWORDS[t] for t in category_terms}
        conditions.append(TourItem.master.has(TourMaster.content_type_id.in_(type_ids)))

    query = select(TourItem).options(joinedload(TourItem.master))
    if conditions:
        query = query.where(and_(*conditions))
    tour_matches = db.execute(query.limit(5)).scalars().all()
    if not tour_matches:
        return "", []

    lines = [f"- [장소] {item.title} / {item.addr1} / {item.tel or '연락처 미제공'}" for item in tour_matches]
    return "\n".join(lines), tour_matches


def _place_type(item: TourItem) -> str:
    return "food" if item.master and item.master.content_type_id == 39 else "tour"


def send_message(
    db: Session, room: ChatRoom, message: str, region: str | None = None
) -> tuple[ChatMessage, ChatMessage, list[ChatPlaceRef]]:
    """사용자 메시지를 저장하고, 최근 대화 이력 + RAG 검색 근거를 컨텍스트로 OpenAI에 질의한 뒤
    봇 응답도 저장한다. (user_message, bot_message, referenced_places) 튜플을 반환."""
    user_message = ChatMessage(room_id=room.id, sender="user", message=message)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    history = (
        db.execute(
            select(ChatMessage)
            .where(ChatMessage.room_id == room.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
        .scalars()
        .all()
    )
    history.reverse()

    context, matched_items = _search_context(db, message, region)
    system_content = _build_system_prompt(region)
    if context:
        system_content += f"\n\n[참고 자료]\n{context}"

    chat_history = [{"role": "system", "content": system_content}]
    chat_history += [
        {"role": "user" if item.sender == "user" else "assistant", "content": item.message}
        for item in history
    ]

    try:
        client = _get_client()
        response = client.chat.completions.create(model="gpt-5-mini", messages=chat_history)
        reply = response.choices[0].message.content or ""
    except Exception:
        # OPENAI_API_KEY 미설정/모델 접근 불가 등으로 호출이 실패해도 대화방 자체는
        # 끊기지 않도록 안내 메시지를 봇 응답으로 남긴다. 원인은 로그로 남겨 진단한다.
        logging.exception("OpenAI chat completion failed")
        reply = "죄송합니다. 챗봇 응답을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요."

    bot_message = ChatMessage(room_id=room.id, sender="bot", message=reply)
    db.add(bot_message)
    db.commit()
    db.refresh(bot_message)

    referenced_places = [
        ChatPlaceRef(
            content_id=item.content_id,
            title=item.title,
            addr1=item.addr1,
            map_x=item.map_x,
            map_y=item.map_y,
            place_type=_place_type(item),
        )
        for item in matched_items
        if item.map_x and item.map_y
    ]

    return user_message, bot_message, referenced_places
