from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
import uuid

from models.database import async_session_maker
from models.report_run import ReportRun
from schemas.report import ReportStatus
from sqlalchemy import select
import redis.asyncio as aioredis
import os

router = APIRouter(prefix="/api", tags=["streams"])

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


@router.get("/runs/{run_id}/stream")
async def stream_report_status(run_id: uuid.UUID):
    """
    Server-Sent Events endpoint for real-time report status updates.
    Client subscribes to Redis Pub/Sub channel and receives status changes.
    """
    # Verify run exists
    async with async_session_maker() as session:
        result = await session.execute(select(ReportRun).where(ReportRun.id == run_id))
        run = result.scalar_one_or_none()
        
        if not run:
            raise HTTPException(status_code=404, detail="Report run not found")
        
        # If already completed or failed, send final event immediately
        if run.status in [ReportStatus.COMPLETED.value, ReportStatus.FAILED.value]:
            async def completed_event():
                yield {
                    "event": "status_update",
                    "data": json.dumps({
                        "run_id": str(run_id),
                        "status": run.status,
                        "completed_at": str(run.completed_at) if run.completed_at else None,
                        "file_path": run.file_path,
                        "error_message": run.error_message,
                    })
                }
                await asyncio.sleep(0)
            return EventSourceResponse(completed_event())
    
    # Subscribe to Redis Pub/Sub for status updates
    redis_client = aioredis.from_url(REDIS_URL)
    channel_name = f"report_status:{run_id}"
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel_name)
    
    async def event_generator():
        try:
            # Send initial status
            yield {
                "event": "status_update",
                "data": json.dumps({
                    "run_id": str(run_id),
                    "status": run.status,
                })
            }
            
            # Listen for status changes
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30.0)
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    yield {
                        "event": "status_update",
                        "data": json.dumps(data)
                    }
                    
                    # Stop streaming if terminal state
                    if data.get("status") in ["completed", "failed"]:
                        break
                else:
                    # Send keep-alive
                    yield {
                        "event": "keepalive",
                        "data": json.dumps({"run_id": str(run_id)})
                    }
        finally:
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()
            await redis_client.close()
    
    return EventSourceResponse(event_generator())
