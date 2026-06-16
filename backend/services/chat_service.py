from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.query_agent import run_query
from agents.web_search import format_search_results, web_search
from core.config import settings
from models.rag_config import RAGDataSource
from rag.generator import get_llm_generator
from rag.prompts import RAG_SYSTEM_PROMPT, WEB_SEARCH_SYSTEM_PROMPT
from rag.retriever import RAGRetriever
from repositories.chat_repo import ChatRepository

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ChatRepository(db)

    async def list_sessions(self, user_id: str):
        sessions = await self.repo.list_sessions(user_id)
        result = []
        for s in sessions:
            count = await self.repo.get_session_message_count(s.id)
            result.append((s, count))
        return result

    async def create_session(self, user_id: str, title: str = "New Chat"):
        return await self.repo.create_session(user_id=str(user_id), title=title)

    async def get_session(self, session_id: str, user_id: str):
        return await self.repo.get_session(session_id, user_id)

    async def rename_session(self, session_id: str, user_id: str, title: str):
        return await self.repo.update_session_title(session_id, user_id, title)

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        return await self.repo.delete_session(session_id, user_id)

    async def _get_enabled_sources(self, db: AsyncSession) -> dict[str, bool]:
        """Load enabled RAG data sources from the database."""
        try:
            result = await db.execute(select(RAGDataSource))
            sources = result.scalars().all()
            return {s.source_type: s.enabled for s in sources}
        except Exception:
            # Default: both enabled
            return {"tickets": True, "documents": True}

    async def stream_response(
        self,
        session_id: str,
        user_id: str,
        user_message: str,
        db: AsyncSession,
    ) -> AsyncIterator[str]:
        """
        Main chat handler:
        1. Save user message
        2. Build conversation history
        3. Run RAG retrieval + confidence check
        4. Stream LLM response tokens as SSE events
        5. Save assistant message after streaming completes
        """
        repo = ChatRepository(db)
        session = await repo.get_session(str(session_id), str(user_id))
        if not session:
            yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
            return

        # Save user message
        await repo.add_message(session_id=str(session_id), role="user", content=user_message)

        # Build history for context (last 10 messages)
        messages = await repo.get_session_messages(str(session_id))
        history = [
            {"role": m.role, "content": m.content}
            for m in messages[-10:]
            if m.role in ("user", "assistant")
        ]
        # Don't include the just-saved user msg in history again
        if history and history[-1]["content"] == user_message:
            history = history[:-1]

        # Load enabled data sources from admin config
        source_map = await self._get_enabled_sources(db)
        use_tickets = source_map.get("tickets", True)
        use_documents = source_map.get("documents", True)

        # RAG retrieval with enabled sources
        retriever = RAGRetriever(use_tickets=use_tickets, use_documents=use_documents)
        chunks = retriever.retrieve(user_message)
        confident_chunks = [c for c in chunks if c.is_confident]
        needs_web = not confident_chunks or retriever.is_knowledge_base_empty()

        citations = []
        full_response = ""

        llm = get_llm_generator()

        # Signal start
        yield f"data: {json.dumps({'type': 'start', 'using_web': needs_web})}\n\n"

        if needs_web:
            # Web search fallback
            logger.info(f"Using web search fallback for: {user_message[:60]}...")
            yield f"data: {json.dumps({'type': 'status', 'message': 'Searching the web...'})}\n\n"

            # Run web search in executor to not block event loop
            loop = asyncio.get_event_loop()
            web_results = await loop.run_in_executor(None, web_search, user_message)

            citations = [
                {"title": r["title"], "url": r["url"], "snippet": r["snippet"][:200]}
                for r in web_results
            ]
            context = format_search_results(web_results)
            system_prompt = WEB_SEARCH_SYSTEM_PROMPT.format(context=context)
        else:
            context = "\n\n---\n\n".join(
                [f"[{c.metadata.get('ticket_number', c.metadata.get('filename', 'ref'))}]\n{c.text}"
                 for c in confident_chunks]
            )
            system_prompt = RAG_SYSTEM_PROMPT.format(context=context)

        # Stream tokens
        try:
            if settings.run_local_llm:
                from rag.generator import is_local_model_loaded
                if not is_local_model_loaded():
                    import sys
                    import queue
                    import threading
                    
                    class QueueWriter:
                        def __init__(self, q: queue.Queue, original_stream, thread_id):
                            self.q = q
                            self.original_stream = original_stream
                            self.thread_id = thread_id

                        def write(self, data):
                            try:
                                self.original_stream.write(data)
                                self.original_stream.flush()
                            except Exception:
                                pass
                            if threading.get_ident() == self.thread_id and data:
                                self.q.put(data)

                        def flush(self):
                            self.original_stream.flush()

                        def __getattr__(self, name):
                            return getattr(self.original_stream, name)
                    
                    q = queue.Queue()
                    loading_thread_id = None
                    
                    def thread_target():
                        nonlocal loading_thread_id
                        loading_thread_id = threading.get_ident()
                        
                        orig_stdout = sys.stdout
                        orig_stderr = sys.stderr
                        sys.stdout = QueueWriter(q, orig_stdout, loading_thread_id)
                        sys.stderr = QueueWriter(q, orig_stderr, loading_thread_id)
                        try:
                            from rag.generator import load_local_pipeline
                            load_local_pipeline()
                        except Exception as e:
                            logger.exception("Error loading local model in thread")
                            q.put(f"ERROR: {str(e)}")
                        finally:
                            sys.stdout = orig_stdout
                            sys.stderr = orig_stderr
                            q.put(None)
                    
                    t = threading.Thread(target=thread_target)
                    t.start()
                    
                    # Yield initial status
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Initializing model loading...'})}\n\n"
                    
                    buffer = ""
                    while True:
                        try:
                            data = q.get_nowait()
                            if data is None:
                                break
                            buffer += data
                            while True:
                                nl_idx = buffer.find("\n")
                                cr_idx = buffer.find("\r")
                                if nl_idx == -1 and cr_idx == -1:
                                    break
                                if nl_idx != -1 and (cr_idx == -1 or nl_idx < cr_idx):
                                    line = buffer[:nl_idx].strip()
                                    buffer = buffer[nl_idx + 1:]
                                    if line:
                                        yield f"data: {json.dumps({'type': 'status', 'message': line})}\n\n"
                                else:
                                    line = buffer[:cr_idx].strip()
                                    buffer = buffer[cr_idx + 1:]
                                    if line:
                                        yield f"data: {json.dumps({'type': 'status', 'message': line})}\n\n"
                        except queue.Empty:
                            await asyncio.sleep(0.05)
                        
                        if not t.is_alive() and q.empty():
                            break
                    
                    # Read any remaining output in buffer
                    remaining = buffer.strip()
                    if remaining:
                        yield f"data: {json.dumps({'type': 'status', 'message': remaining})}\n\n"
                    
                    t.join()
                    
            for token in llm.generate_stream(
                system_prompt=system_prompt,
                user_message=user_message,
                history=history,
            ):
                full_response += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as e:
            logger.exception(f"Streaming error: {e}")
            full_response = "I encountered an error. Please try again."
            yield f"data: {json.dumps({'type': 'token', 'content': full_response})}\n\n"

        # Save assistant message
        try:
            await repo.add_message(
                session_id=str(session_id),
                role="assistant",
                content=full_response,
                citations=citations,
                confidence_score=min((c.distance for c in chunks), default=1.0),
            )
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to save assistant message: {e}")

        # Signal done with citations
        yield f"data: {json.dumps({'type': 'done', 'citations': citations})}\n\n"
