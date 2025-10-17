import React, { useState, useRef, useEffect, useCallback } from 'react';
import { authAPI } from '../api/index';
import TypingIndicator from '../components/TypingIndicator';
import MarkdownRenderer from '../components/MarkdownRenderer';

// Memoized message bubble component to prevent unnecessary re-renders
const MessageBubble = React.memo(({ message }) => {
  return (
    <div
      className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          message.isUser
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-200 text-gray-900'
        }`}
      >
        <div className="text-sm">
          {message.isStreaming && message.text === '' ? (
            <TypingIndicator />
          ) : (
            <MarkdownRenderer
              content={message.text}
              isStreaming={message.isStreaming}
            />
          )}
        </div>
        <p className={`text-xs mt-1 ${
          message.isUser ? 'text-indigo-200' : 'text-gray-500'
        }`}>
          {message.timestamp}
        </p>
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function - only re-render if message content actually changed
  return prevProps.message.text === nextProps.message.text &&
         prevProps.message.isStreaming === nextProps.message.isStreaming;
});

MessageBubble.displayName = 'MessageBubble';

const Home = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [metadataFiltered, setMetadataFiltered] = useState(false);
  const messagesEndRef = useRef(null);
  const currentBotMessageRef = useRef(null);
  const streamingTextRef = useRef(''); // Store streaming text in ref to avoid re-renders
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const messagesContainerRef = useRef(null);

  // Автоскролл к последнему сообщению
  const scrollToBottom = useCallback((smooth = true) => {
    if (messagesEndRef.current && shouldAutoScroll) {
      messagesEndRef.current.scrollIntoView({
        behavior: smooth ? 'smooth' : 'auto',
        block: 'end'
      });
    }
  }, [shouldAutoScroll]);

  // Detect if user has scrolled up manually
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShouldAutoScroll(isNearBottom);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // Автоскролл при добавлении новых сообщений или обновлении во время стриминга
  useEffect(() => {
    if (shouldAutoScroll) {
      // Use requestAnimationFrame for smoother scroll during streaming
      requestAnimationFrame(() => {
        scrollToBottom(!isLoading);
      });
    }
  }, [messages, isLoading, scrollToBottom, shouldAutoScroll]);

  // Дополнительный автоскролл при изменении размера textarea
  useEffect(() => {
    const handleResize = () => {
      if (shouldAutoScroll) {
        requestAnimationFrame(() => scrollToBottom(false));
      }
    };

    const textarea = document.querySelector('textarea');
    if (textarea) {
      const observer = new ResizeObserver(handleResize);
      observer.observe(textarea);

      return () => observer.disconnect();
    }
  }, [shouldAutoScroll, scrollToBottom]);

  const clearChat = () => {
    setMessages([]);
    setError(null);
    setMetadataFiltered(false);
  };

  // Функция для декодирования base64 метаданных
  const decodeMetadata = (base64String) => {
    try {
      const decoded = atob(base64String);
      return JSON.parse(decoded);
    } catch (error) {
      console.warn('Не удалось декодировать метаданные:', error);
      return null;
    }
  };

  // Функция для форматирования источника
  const formatSource = (metadata) => {
    if (!metadata) return '';
    
    const filename = metadata.filename || 'Документ';
    const page = metadata.page;
    const totalPages = metadata.total_pages;
    
    // Убираем расширение из имени файла
    const cleanFilename = filename.replace(/\.(pdf|doc|docx)$/i, '');
    
    let source = cleanFilename;
    if (page) {
      source += ` (стр. ${page}`;
      if (totalPages) {
        source += ` из ${totalPages}`;
      }
      source += ')';
    }
    
    return source;
  };

  // Функция для улучшенной очистки ответов с красивыми источниками
  const cleanResponse = (text) => {
    if (!text) return text;
    
    const originalText = text;
    let cleanedText = text;
    const sources = new Set();
    
    // Находим и обрабатываем метаданные
    const metadataRegex = /Metadata:\s*([A-Za-z0-9+/=]+)/g;
    let match;
    
    while ((match = metadataRegex.exec(text)) !== null) {
      const base64Data = match[1];
      const metadata = decodeMetadata(base64Data);
      
      if (metadata) {
        const source = formatSource(metadata);
        if (source) {
          sources.add(source);
        }
      }
    }
    
    // Также ищем источники в тексте вида "Document 1:", "Document 2:" и извлекаем реальные названия
    const documentRegex = /Document \d+:\s*([^\n]+)/g;
    let docMatch;
    
    while ((docMatch = documentRegex.exec(text)) !== null) {
      const docTitle = docMatch[1].trim();
      if (docTitle && !docTitle.includes('Metadata:')) {
        // Очищаем название документа от лишних символов
        const cleanTitle = docTitle.replace(/[^\w\s\-.]/g, '').trim();
        if (cleanTitle.length > 3) {
          sources.add(cleanTitle);
        }
      }
    }
    
    // Удаляем блоки "Metadata:" с base64 данными
    cleanedText = cleanedText.replace(/Metadata:\s*[A-Za-z0-9+/=]+/g, '');
    
    // Удаляем оставшиеся "(Документ X, )" части
    cleanedText = cleanedText.replace(/\(Документ \d+,\s*\)/g, '');
    
    // Удаляем ссылки на документы в тексте (универсальное выражение)
    cleanedText = cleanedText.replace(/\([^)]*(?:Документ|Document)\s*\d+(?:,\s*(?:Документ|Document)\s*\d+)*\)/g, '');
    
    // Удаляем "Источники: Document X, Document Y" в конце
    cleanedText = cleanedText.replace(/\n\s*Источники:\s*Document \d+(?:,\s*Document \d+)*\.?\s*$/g, '');
    cleanedText = cleanedText.replace(/\n\s*Источники:\s*Документ \d+(?:,\s*Документ \d+)*\.?\s*$/g, '');
    
    // Удаляем оставшиеся base64 строки (длинные строки из букв, цифр и символов =, +, /)
    cleanedText = cleanedText.replace(/^[A-Za-z0-9+/=]{50,}$/gm, '');
    
    // Удаляем неполные base64 строки в тексте
    cleanedText = cleanedText.replace(/[A-Za-z0-9+/=]{30,}/g, (match) => {
      // Проверяем, является ли строка base64
      if (match.length > 30 && /^[A-Za-z0-9+/=]+$/.test(match)) {
        return '';
      }
      return match;
    });
    
    // Удаляем оставшиеся фрагменты base64 в скобках
    cleanedText = cleanedText.replace(/\([^)]*[A-Za-z0-9+/=]{20,}[^)]*\)/g, '');
    
    // Удаляем строки с техническими метаданными
    cleanedText = cleanedText.replace(/^\s*(page|filename|filetype|pos):\s*[^\n]*$/gm, '');
    
    // Удаляем заголовки "Document X:" из текста
    cleanedText = cleanedText.replace(/^Document \d+:\s*$/gm, '');
    cleanedText = cleanedText.replace(/^Документ \d+:\s*$/gm, '');
    
    // Удаляем множественные пустые строки
    cleanedText = cleanedText.replace(/\n\s*\n\s*\n/g, '\n\n');
    
    // Удаляем пустые строки в начале и конце
    cleanedText = cleanedText.trim();
    
    // Добавляем источники в конец, если они есть (только уникальные)
    if (sources.size > 0) {
      const sourcesArray = Array.from(sources);
      const sourcesText = sourcesArray.length === 1 
        ? `\n\n📄 Источник: ${sourcesArray[0]}`
        : `\n\n📄 Источники:\n${sourcesArray.map(s => `• ${s}`).join('\n')}`;
      
      cleanedText += sourcesText;
    }
    
    // Удаляем дублирующиеся источники из текста (если они уже есть в тексте)
    cleanedText = cleanedText.replace(/\n📄 Источник:\s*[^\n]+\n/g, '');
    cleanedText = cleanedText.replace(/\n📄 Источники:\s*[^\n]+(?:\n• [^\n]+)*\n/g, '');
    
    // Проверяем, были ли отфильтрованы метаданные (только если действительно добавлены источники)
    if (originalText !== cleanedText && originalText.includes('Metadata:') && sources.size > 0) {
      setMetadataFiltered(true);
    }
    
    return cleanedText;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const handleTextareaChange = (e) => {
    setInputMessage(e.target.value);

    // Автоматическое изменение размера textarea
    const textarea = e.target;
    const currentScrollTop = textarea.scrollTop;

    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 120);
    textarea.style.height = newHeight + 'px';

    // Сохраняем позицию скролла только если не достигнут максимум
    if (textarea.scrollHeight <= 120) {
      textarea.scrollTop = currentScrollTop;
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      isUser: true,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);
    streamingTextRef.current = ''; // Reset streaming text

    // Сброс размера textarea
    setTimeout(() => {
      const textarea = document.querySelector('textarea');
      if (textarea) {
        textarea.style.height = 'auto';
      }
    }, 100);

    // Создаем сообщение бота для стриминга
    const botMessage = {
      id: Date.now() + 1,
      text: '',
      isUser: false,
      timestamp: new Date().toLocaleTimeString(),
      isStreaming: true,
    };

    setMessages(prev => [...prev, botMessage]);
    currentBotMessageRef.current = botMessage.id;

    // Use a throttled update mechanism for streaming
    let updateTimeout = null;
    const THROTTLE_MS = 100; // Update UI every 100ms instead of every chunk

    try {
      await authAPI.askWithAI(
        userMessage.text,
        // onChunk - обработчик получения части ответа
        (chunk) => {
          // Accumulate text in ref (doesn't cause re-render)
          streamingTextRef.current += chunk;

          // Throttle UI updates to improve performance
          if (!updateTimeout) {
            updateTimeout = setTimeout(() => {
              setMessages(prev =>
                prev.map(msg =>
                  msg.id === currentBotMessageRef.current
                    ? { ...msg, text: streamingTextRef.current }
                    : msg
                )
              );
              updateTimeout = null;
            }, THROTTLE_MS);
          }
        },
        // onError - обработчик ошибки
        (error) => {
          console.error('Ошибка при запросе к AI:', error);
          setError(error.message || 'Произошла ошибка при получении ответа');

          // Clear any pending updates
          if (updateTimeout) {
            clearTimeout(updateTimeout);
            updateTimeout = null;
          }

          setMessages(prev =>
            prev.map(msg =>
              msg.id === currentBotMessageRef.current
                ? {
                    ...msg,
                    text: streamingTextRef.current + '\n\n❌ Ошибка: ' + (error.message || 'Неизвестная ошибка'),
                    isStreaming: false
                  }
                : msg
            )
          );
          setIsLoading(false);
          streamingTextRef.current = '';
        },
        // onComplete - обработчик завершения
        () => {
          // Clear any pending updates and do final update
          if (updateTimeout) {
            clearTimeout(updateTimeout);
            updateTimeout = null;
          }

          setMessages(prev =>
            prev.map(msg =>
              msg.id === currentBotMessageRef.current
                ? { ...msg, isStreaming: false, text: cleanResponse(streamingTextRef.current) }
                : msg
            )
          );
          setIsLoading(false);
          currentBotMessageRef.current = null;
          streamingTextRef.current = '';

          // Автоскролл при завершении
          requestAnimationFrame(() => scrollToBottom(true));
        }
      );
    } catch (error) {
      console.error('Ошибка при отправке запроса:', error);
      setError(error.message || 'Произошла ошибка при отправке запроса');
      setIsLoading(false);
      streamingTextRef.current = '';
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-lg h-[600px] flex flex-col">
          {/* Header */}
          <div className="border-b px-4 py-3 flex justify-between items-center flex-shrink-0">
            <h2 className="text-lg font-semibold text-gray-900">AI Чат-бот</h2>
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1 rounded-md hover:bg-gray-100 transition-colors"
              >
                Очистить чат
              </button>
            )}
          </div>

          {/* Messages Area */}
          <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-gray-400 text-6xl mb-4">🤖</div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Добро пожаловать в AI чат-бот!
                  </h3>
                  <p className="text-gray-500">
                    Задайте любой вопрос и получите ответ от AI ассистента.
                  </p>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                />
              ))
            )}
            {error && (
              <div className="flex justify-center">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              </div>
            )}
            {metadataFiltered && (
              <div className="flex justify-center">
                <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-2 rounded text-sm">
                  ℹ️ Источники информации автоматически добавлены в конец ответа
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t p-4 flex-shrink-0">
            <form onSubmit={handleSendMessage} className="flex space-x-4">
              <textarea
                value={inputMessage}
                onChange={handleTextareaChange}
                onKeyPress={handleKeyPress}
                placeholder={isLoading ? "AI отвечает..." : "Введите ваше сообщение... (Enter для отправки, Shift+Enter для новой строки)"}
                disabled={isLoading}
                rows={1}
                className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:cursor-not-allowed resize-none"
                style={{ minHeight: '40px', maxHeight: '120px' }}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-2 rounded-md font-medium transition-colors flex items-center space-x-2"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Отправка...</span>
                  </>
                ) : (
                  <span>Отправить</span>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
