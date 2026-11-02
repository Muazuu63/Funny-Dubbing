"""
WebSocket Manager and Event Streaming Endpoint for AI-VPS.
Master Architecture v2.2 & PRD v2.2 Aligned.

Streams real-time updates to UI:
1. Queue position and task lifecycle transitions
2. Current step progress percentage
3. Real-time audio level telemetry (masterLevelDb) & peak clipping alerts
4. Rate limit quota pause (HTTP 429) notifications
"""
import json
import logging
from typing import List, Dict, Any, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("ai_vps.websocket")

router = APIRouter(tags=["WebSocket Event Streaming"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcasts a structured JSON event to all connected UI clients."""
        payload = json.dumps({"event": event_type, "data": data})
        stale = set()
        for conn in self.active_connections:
            try:
                await conn.send_text(payload)
            except Exception:
                stale.add(conn)

        for s in stale:
            self.disconnect(s)


ws_manager = ConnectionManager()


@router.websocket("/ws/events")
@router.websocket("/ws/telemetry")
async def websocket_events_endpoint(websocket: WebSocket):
    """Real-time event streaming for dashboard queue, audio telemetry, and alerts."""
    await ws_manager.connect(websocket)
    try:
        # Send initial connection handshake
        await websocket.send_text(json.dumps({
            "event": "CONNECTED",
            "message": "AI-VPS Live Event Stream established.",
        }))
        while True:
            # Keep connection open & handle incoming pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        ws_manager.disconnect(websocket)
