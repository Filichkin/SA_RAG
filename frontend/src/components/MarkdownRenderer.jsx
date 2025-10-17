import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import DOMPurify from 'dompurify';
import ErrorBoundary from './ErrorBoundary';
import SafeMarkdownRenderer from './SafeMarkdownRenderer';

// Memoized component for better performance
const MarkdownRenderer = React.memo(({ content, isStreaming = false }) => {
  // Memoize sanitization - only recompute when content changes
  const sanitizedContent = useMemo(() => {
    // Check if content is valid
    if (!content || typeof content !== 'string') {
      return '';
    }

    // First, sanitize with DOMPurify to prevent XSS
    const purified = DOMPurify.sanitize(content, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                     'ul', 'ol', 'li', 'code', 'pre', 'blockquote', 'a', 'table',
                     'thead', 'tbody', 'tr', 'th', 'td', 'span', 'div'],
      ALLOWED_ATTR: ['href', 'target', 'rel', 'class', 'id'],
      ALLOW_DATA_ATTR: false,
    });

    // Then clean up whitespace while preserving intentional line breaks
    return purified
      .replace(/[^\x20-\x7E\u00A0-\uFFFF\n\r\t]/g, '') // Remove non-printable characters except newlines
      .trim();
  }, [content]);

  // Memoize custom components to prevent recreation on every render
  const components = useMemo(() => ({
    // Стилизация для чата
    p: ({ children, ...props }) => (
      <p className="mb-2 last:mb-0" {...props}>{children}</p>
    ),
    strong: ({ children, ...props }) => (
      <strong className="font-semibold text-gray-900" {...props}>{children}</strong>
    ),
    em: ({ children, ...props }) => (
      <em className="italic text-gray-700" {...props}>{children}</em>
    ),
    ul: ({ children, ...props }) => (
      <ul className="list-disc list-inside mb-2 space-y-1" {...props}>{children}</ul>
    ),
    ol: ({ children, ...props }) => (
      <ol className="list-decimal list-inside mb-2 space-y-1" {...props}>{children}</ol>
    ),
    li: ({ children, ...props }) => (
      <li className="text-sm" {...props}>{children}</li>
    ),
    h1: ({ children, ...props }) => (
      <h1 className="text-lg font-bold mb-2 text-gray-900 mt-3" {...props}>{children}</h1>
    ),
    h2: ({ children, ...props }) => (
      <h2 className="text-base font-semibold mb-2 text-gray-900 mt-2" {...props}>{children}</h2>
    ),
    h3: ({ children, ...props }) => (
      <h3 className="text-sm font-semibold mb-1 text-gray-900 mt-2" {...props}>{children}</h3>
    ),
    code: ({ inline, children, ...props }) => {
      // Inline code
      if (inline) {
        return (
          <code
            className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono text-gray-800"
            {...props}
          >
            {children}
          </code>
        );
      }
      // Block code
      return (
        <code className="font-mono text-xs" {...props}>{children}</code>
      );
    },
    pre: ({ children, ...props }) => (
      <pre
        className="bg-gray-100 p-2 rounded text-xs font-mono text-gray-800 overflow-x-auto my-2 max-w-full"
        {...props}
      >
        {children}
      </pre>
    ),
    blockquote: ({ children, ...props }) => (
      <blockquote
        className="border-l-4 border-gray-300 pl-3 italic text-gray-600 my-2"
        {...props}
      >
        {children}
      </blockquote>
    ),
    a: ({ href, children, ...props }) => (
      <a
        href={href || '#'}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 underline"
        {...props}
      >
        {children}
      </a>
    ),
    table: ({ children, ...props }) => (
      <div className="overflow-x-auto my-2">
        <table className="min-w-full border border-gray-200 rounded" {...props}>
          {children}
        </table>
      </div>
    ),
    thead: ({ children, ...props }) => (
      <thead {...props}>{children}</thead>
    ),
    tbody: ({ children, ...props }) => (
      <tbody {...props}>{children}</tbody>
    ),
    tr: ({ children, ...props }) => (
      <tr {...props}>{children}</tr>
    ),
    th: ({ children, ...props }) => (
      <th
        className="border border-gray-200 px-2 py-1 bg-gray-50 text-left text-xs font-semibold"
        {...props}
      >
        {children}
      </th>
    ),
    td: ({ children, ...props }) => (
      <td className="border border-gray-200 px-2 py-1 text-xs" {...props}>
        {children}
      </td>
    ),
  }), []);

  // Early return if no content
  if (!sanitizedContent) {
    return (
      <div className="text-sm text-gray-500">
        {isStreaming && <span className="inline-block w-2 h-4 bg-gray-400 ml-1 animate-pulse"></span>}
      </div>
    );
  }

  try {
    return (
      <ErrorBoundary
        fallback={
          <SafeMarkdownRenderer content={sanitizedContent} isStreaming={isStreaming} />
        }
      >
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={components}
          >
            {sanitizedContent}
          </ReactMarkdown>
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-gray-400 ml-1 animate-pulse"></span>
          )}
        </div>
      </ErrorBoundary>
    );
  } catch (error) {
    console.error('Ошибка при рендеринге Markdown:', error);
    // Fallback к безопасному рендереру
    return (
      <SafeMarkdownRenderer content={sanitizedContent} isStreaming={isStreaming} />
    );
  }
});

MarkdownRenderer.displayName = 'MarkdownRenderer';

export default MarkdownRenderer;
