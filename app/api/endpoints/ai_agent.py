from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.schemas.ai_response import AskWithAIResponse
from app.services.agent.ai_agent import build_agent
from app.services.agent.mcp_client import McpClient


router = APIRouter()


@router.post('/ask_with_ai')
async def ask_with_ai(
    query: AskWithAIResponse,
):

    try:
        async with McpClient(
            settings.mcp_server_url,
            transport=settings.mcp_transport
        ) as mcp:
            agent, astream_answer = build_agent(
                mcp=mcp,
                rag_tool_name=settings.mcp_rag_tool_name,
                model_name=settings.gigachat_model,
                temperature=settings.gigachat_temperature,
                scope=settings.gigachat_scope,
                credentials=settings.gigachat_credentials,
                verify_ssl=settings.gigachat_verify_ssl,
            )

            async def stream_response():
                async for chunk in astream_answer(query):
                    yield chunk
            return await StreamingResponse(
                stream_response(),
                media_type='text/plain',
                headers={
                    'Content-Type': 'text/plain',
                    'Transfer-Encoding': 'chunked',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                },
            )

    except Exception as e:
        return {'response': f'Ничего не найдено, ошибка: {e}'}
