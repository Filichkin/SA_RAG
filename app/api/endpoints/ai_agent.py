from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.constants import Constants, Messages, Descriptions
from app.schemas.ai_response import AskWithAIResponse
from app.services.agent.ai_agent import build_agent
from app.services.agent.mcp_client import McpClient
from app.logging import logging_config


router = APIRouter()


@router.post(
    Constants.AI_ASK_PREFIX,
    summary=Descriptions.AI_ASK_SUMMARY,
    description=Descriptions.AI_ASK_DESCRIPTION,
    tags=Constants.AI_AGENT_TAGS
)
async def ask_with_ai(
    request: AskWithAIResponse,
):
    '''
    Эндпоинт для взаимодействия с AI ассистентом.

    Args:
        request: Объект с полем query, содержащим вопрос пользователя

    Returns:
        StreamingResponse: Потоковый ответ от AI ассистента
    '''
    logger = logging_config.get_endpoint_logger('ai_agent')

    # Валидация входных данных
    if not request.query or not request.query.strip():
        logger.warning('Получен пустой запрос')
        raise HTTPException(
            status_code=Constants.HTTP_400_BAD_REQUEST,
            detail=Messages.AI_EMPTY_QUERY_MSG
        )

    if len(request.query) > Constants.AI_QUERY_MAX_LENGTH:
        logger.warning(
            f'Запрос слишком длинный: {len(request.query)} символов'
        )
        raise HTTPException(
            status_code=Constants.HTTP_400_BAD_REQUEST,
            detail=Messages.AI_QUERY_TOO_LONG_MSG
        )

    logger.info(
        f'Получен запрос: '
        f'{request.query[:Constants.AI_QUERY_PREVIEW_LENGTH]}...'
    )

    async def stream_response():
        """Stream response with MCP client context managed properly."""
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

            try:
                async for chunk in astream_answer(request.query):
                    yield chunk
            except Exception as stream_error:
                logger.error(
                    f'Ошибка при стриминге ответа: {stream_error}'
                )
                yield f'{Messages.AI_STREAM_ERROR_MSG}: {stream_error}'

    try:
        return StreamingResponse(
            stream_response(),
            media_type='text/plain; charset=utf-8',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            },
        )

    except Exception as e:
        logger.error(f'Ошибка в ask_with_ai: {e}', exc_info=True)
        error_message = str(e)

        # Возвращаем StreamingResponse с ошибкой вместо обычного словаря
        def error_stream():
            async def _async_generator():
                yield f'{Messages.AI_GENERAL_ERROR_MSG}: {error_message}'

            return _async_generator()

        return StreamingResponse(
            error_stream(),
            media_type='text/plain; charset=utf-8',
            status_code=500,
            headers={
                'Cache-Control': 'no-cache',
            },
        )
