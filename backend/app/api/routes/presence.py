from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/api/presence", tags=["presence"])

_connections: set[WebSocket] = set()


async def _broadcast_count() -> None:
    count = len(_connections)
    dead = []
    for ws in _connections:
        try:
            await ws.send_json({"count": count})
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.discard(ws)


@router.websocket("/ws")
async def presence_ws(websocket: WebSocket) -> None:
    """접속 중인 클라이언트를 WebSocket 연결로 직접 추적한다.

    연결/해제 이벤트가 곧 접속자 수 변화이므로 폴링이나 타임아웃 추정이 필요 없다.
    """
    await websocket.accept()
    _connections.add(websocket)
    await _broadcast_count()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _connections.discard(websocket)
        await _broadcast_count()
