import React, { useMemo } from 'react';
import DOMPurify from 'dompurify';

const SafeMarkdownRenderer = React.memo(({ content, isStreaming = false }) => {
  // Простая функция для рендеринга Markdown без react-markdown
  const renderMarkdown = useMemo(() => {
    if (!content || typeof content !== 'string') {
      return <div className="text-sm text-gray-500">Нет контента для отображения</div>;
    }

    // Sanitize content first
    const sanitized = DOMPurify.sanitize(content, {
      ALLOWED_TAGS: [],
      ALLOWED_ATTR: [],
    });

    // Обрабатываем текст - добавляем переносы строк для лучшего отображения
    let processedText = sanitized
      // Добавляем переносы строк перед заголовками
      .replace(/(\n|^)(#{1,6}\s)/g, '\n\n$2')
      // Добавляем переносы строк после точек с цифрами (1. 2. 3.)
      .replace(/(\d+\.\s)/g, '\n$1')
      // Добавляем переносы строк после заголовков с **
      .replace(/(\*\*[^*]+\*\*)/g, '\n$1')
      // Добавляем переносы строк после "Таким образом"
      .replace(/(Таким образом)/g, '\n$1')
      // Добавляем переносы строк после "Источники:"
      .replace(/(Источники:)/g, '\n$1')
      // Добавляем переносы строк для списков
      .replace(/\n([-*]|\d+\.)\s/g, '\n$1 ')
      // Убираем множественные переносы строк
      .replace(/\n{3,}/g, '\n\n')
      .trim();

    // Обработка форматирования текста (жирный, курсив, inline код)
    const processInlineFormatting = (text) => {
      const parts = [];
      let currentIndex = 0;
      let partIndex = 0;

      // Regular expression to match bold, italic, and inline code
      const regex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
      let match;

      while ((match = regex.exec(text)) !== null) {
        // Add text before match
        if (match.index > currentIndex) {
          parts.push(text.slice(currentIndex, match.index));
        }

        const matched = match[0];
        // Bold text **text**
        if (matched.startsWith('**') && matched.endsWith('**')) {
          parts.push(
            <strong key={`bold-${partIndex++}`} className="font-semibold text-gray-900">
              {matched.slice(2, -2)}
            </strong>
          );
        }
        // Italic text *text*
        else if (matched.startsWith('*') && matched.endsWith('*')) {
          parts.push(
            <em key={`italic-${partIndex++}`} className="italic text-gray-700">
              {matched.slice(1, -1)}
            </em>
          );
        }
        // Inline code `code`
        else if (matched.startsWith('`') && matched.endsWith('`')) {
          parts.push(
            <code key={`code-${partIndex++}`} className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono text-gray-800">
              {matched.slice(1, -1)}
            </code>
          );
        }

        currentIndex = match.index + matched.length;
      }

      // Add remaining text
      if (currentIndex < text.length) {
        parts.push(text.slice(currentIndex));
      }

      return parts.length > 0 ? parts : text;
    };

    // Разбиваем на строки
    const lines = processedText.split('\n');

    return lines.map((line, index) => {
      // Пропускаем пустые строки
      if (!line.trim()) {
        return <br key={index} />;
      }

      // Заголовки
      if (line.startsWith('### ')) {
        return (
          <h3 key={index} className="text-sm font-semibold mb-1 text-gray-900">
            {processInlineFormatting(line.replace('### ', ''))}
          </h3>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h2 key={index} className="text-base font-semibold mb-2 text-gray-900">
            {processInlineFormatting(line.replace('## ', ''))}
          </h2>
        );
      }
      if (line.startsWith('# ')) {
        return (
          <h1 key={index} className="text-lg font-bold mb-2 text-gray-900">
            {processInlineFormatting(line.replace('# ', ''))}
          </h1>
        );
      }

      // Списки (bullets)
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return (
          <div key={index} className="ml-4 text-sm flex">
            <span className="mr-2">•</span>
            <span>{processInlineFormatting(line.replace(/^[-*] /, ''))}</span>
          </div>
        );
      }

      // Numbered lists
      if (/^\d+\. /.test(line)) {
        const match = line.match(/^(\d+)\.\s(.+)$/);
        if (match) {
          return (
            <div key={index} className="ml-4 text-sm flex">
              <span className="mr-2">{match[1]}.</span>
              <span>{processInlineFormatting(match[2])}</span>
            </div>
          );
        }
      }

      // Code blocks (```code```)
      if (line.startsWith('```')) {
        return (
          <pre key={index} className="bg-gray-100 p-2 rounded text-xs font-mono text-gray-800 overflow-x-auto my-2">
            <code>{line.replace(/^```|```$/g, '')}</code>
          </pre>
        );
      }

      // Blockquotes
      if (line.startsWith('> ')) {
        return (
          <blockquote key={index} className="border-l-4 border-gray-300 pl-3 italic text-gray-600 my-2">
            {processInlineFormatting(line.slice(2))}
          </blockquote>
        );
      }

      // Links [text](url)
      const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/;
      if (linkRegex.test(line)) {
        const parts = [];
        let lastIndex = 0;
        let linkMatch;
        const linkRegexExec = /\[([^\]]+)\]\(([^)]+)\)/g;

        while ((linkMatch = linkRegexExec.exec(line)) !== null) {
          if (linkMatch.index > lastIndex) {
            parts.push(processInlineFormatting(line.slice(lastIndex, linkMatch.index)));
          }
          parts.push(
            <a
              key={`link-${linkMatch.index}`}
              href={linkMatch[2]}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {linkMatch[1]}
            </a>
          );
          lastIndex = linkMatch.index + linkMatch[0].length;
        }

        if (lastIndex < line.length) {
          parts.push(processInlineFormatting(line.slice(lastIndex)));
        }

        return (
          <p key={index} className="mb-2 last:mb-0 text-sm">
            {parts}
          </p>
        );
      }

      // Обработка источников
      if (line.startsWith('Источники:') || line.startsWith('📄 Источник')) {
        return (
          <div key={index} className="mt-3 pt-2 border-t border-gray-300">
            <div className="text-xs text-gray-600 font-medium mb-1">
              {line.startsWith('📄') ? line.split(':')[0] + ':' : '📄 Источники:'}
            </div>
            <div className="text-xs text-gray-500">
              {line.replace(/^(📄\s*)?(Источник|Источники):/, '').split(',').map((source, sourceIndex) => (
                <span key={sourceIndex}>
                  {source.trim()}
                  {sourceIndex < line.replace(/^(📄\s*)?(Источник|Источники):/, '').split(',').length - 1 && ', '}
                </span>
              ))}
            </div>
          </div>
        );
      }

      // Обычный текст с обработкой форматирования
      return (
        <p key={index} className="mb-2 last:mb-0 text-sm">
          {processInlineFormatting(line)}
        </p>
      );
    });
  }, [content]);

  return (
    <div className="prose prose-sm max-w-none">
      {renderMarkdown}
      {isStreaming && (
        <span className="inline-block w-2 h-4 bg-gray-400 ml-1 animate-pulse"></span>
      )}
    </div>
  );
});

SafeMarkdownRenderer.displayName = 'SafeMarkdownRenderer';

export default SafeMarkdownRenderer;
