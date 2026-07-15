import time

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/presence", tags=["presence"])

ACTIVE_WINDOW_SECONDS = 60
_last_seen: dict[str, float] = {}


class HeartbeatIn(BaseModel):
    session_id: str


class PresenceOut(BaseModel):
    count: int


def _active_count() -> int:
    now = time.time()
    stale = [sid for sid, seen_at in _last_seen.items() if now - seen_at > ACTIVE_WINDOW_SECONDS]
    for sid in stale:
        del _last_seen[sid]
    return len(_last_seen)


@router.post("/heartbeat", response_model=PresenceOut)
def heartbeat(payload: HeartbeatIn):
    """탭(세션)마다 주기적으로 호출해 접속을 갱신하고, 최근 ACTIVE_WINDOW_SECONDS 내 접속자 수를 반환한다.

    별도 DB 테이블 없이 프로세스 메모리에만 유지한다 — 동시접속자 수는 근사치로 충분하고,
    서버 재시작 시 초기화되어도 문제없는 성격의 데이터이기 때문이다.
    """
    _last_seen[payload.session_id] = time.time()
    return PresenceOut(count=_active_count())


@router.get("", response_model=PresenceOut)
def get_presence():
    return PresenceOut(count=_active_count())
