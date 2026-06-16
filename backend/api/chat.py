from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from core.dependencies import CurrentUser, DB
from schemas.chat import (
    ChatSessionCreate,
    ChatSessionDetail,
    ChatSessionOut,
    ChatSessionUpdate,
    SendMessageRequest,
)
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/sessions", response_model=list[ChatSessionOut])
async def list_sessions(current_user: CurrentUser, db: DB):
    svc = ChatService(db)
    sessions_with_counts = await svc.list_sessions(str(current_user.id))
    result = []
    for session, count in sessions_with_counts:
        out = ChatSessionOut.model_validate(session)
        out.message_count = count
        result.append(out)
    return result


@router.post("/sessions", response_model=ChatSessionOut, status_code=201)
async def create_session(body: ChatSessionCreate, current_user: CurrentUser, db: DB):
    svc = ChatService(db)
    session = await svc.create_session(user_id=str(current_user.id), title=body.title)
    return session


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
async def get_session(session_id: str, current_user: CurrentUser, db: DB):
    svc = ChatService(db)
    session = await svc.get_session(session_id, str(current_user.id))
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.patch("/sessions/{session_id}", response_model=ChatSessionOut)
async def rename_session(
    session_id: str, body: ChatSessionUpdate, current_user: CurrentUser, db: DB
):
    svc = ChatService(db)
    session = await svc.rename_session(session_id, str(current_user.id), body.title)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str, current_user: CurrentUser, db: DB):
    svc = ChatService(db)
    deleted = await svc.delete_session(session_id, str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    body: SendMessageRequest,
    current_user: CurrentUser,
    db: DB,
):
    """
    Send a message and receive a streaming SSE response.
    Content-Type: text/event-stream
    """
    svc = ChatService(db)

    async def event_generator():
        async for chunk in svc.stream_response(
            session_id=session_id,
            user_id=str(current_user.id),
            user_message=body.content,
            db=db,
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
