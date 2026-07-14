from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.chat_message import ChatMessage
from app.models.chat_room import ChatRoom
from app.models.post import Post
from app.models.tour_item import TourItem

settings = get_settings()

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI

        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


SYSTEM_PROMPT = (
    f"당신은 {settings.region} 지역 정보를 안내하는 LocalHub 챗봇입니다. "
    "관광지 추천, 축제 일정, 맛집 위치, 커뮤니티 게시글 검색 질의에 답변하세요. "
    "아래 [참고 자료]가 주어지면 그 범위 안에서 구체적으로 답변하고, 근거가 없으면 모른다고 답하세요."
)


def _search_context(db: Session, message: str) -> str:
    """tour_items / posts 제목·주소를 키워드로 검색해 간단한 근거 자료를 구성한다."""
    keywords = [w for w in message.replace(",", " ").split() if len(w) >= 2][:5]
    if not keywords:
        return ""

    tour_conditions = []
    for word in keywords:
        like = f"%{word}%"
        tour_conditions.append(TourItem.title.ilike(like))
        tour_conditions.append(TourItem.addr1.ilike(like))
    tour_matches = (
        db.execute(select(TourItem).where(or_(*tour_conditions)).limit(5)).scalars().all()
    )

    post_conditions = [Post.title.ilike(f"%{word}%") for word in keywords]
    post_matches = db.execute(select(Post).where(or_(*post_conditions)).limit(3)).scalars().all()

    lines = [f"- [장소] {item.title} / {item.addr1} / {item.tel or '연락처 미제공'}" for item in tour_matches]
    lines += [f"- [게시글] {post.title}" for post in post_matches]
    return "\n".join(lines)


def send_message(db: Session, room: ChatRoom, message: str) -> tuple[ChatMessage, ChatMessage]:
    """사용자 메시지를 저장하고, 최근 대화 이력 + 검색 근거를 컨텍스트로 OpenAI에 질의한 뒤
    봇 응답도 저장한다. (user_message, bot_message) 튜플을 반환."""
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

    context = _search_context(db, message)
    system_content = SYSTEM_PROMPT
    if context:
        system_content += f"\n\n[참고 자료]\n{context}"

    chat_history = [{"role": "system", "content": system_content}]
    chat_history += [
        {"role": "user" if item.sender == "user" else "assistant", "content": item.message}
        for item in history
    ]

    try:
        client = _get_client()
        response = client.chat.completions.create(model="gpt-4o-mini", messages=chat_history)
        reply = response.choices[0].message.content or ""
    except Exception:
        # OPENAI_API_KEY 미설정 등으로 호출이 실패해도 대화방 자체는 끊기지 않도록
        # 안내 메시지를 봇 응답으로 남긴다.
        reply = "죄송합니다. 챗봇 응답을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요."

    bot_message = ChatMessage(room_id=room.id, sender="bot", message=reply)
    db.add(bot_message)
    db.commit()
    db.refresh(bot_message)

    return user_message, bot_message
