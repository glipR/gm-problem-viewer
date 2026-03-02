import { Box, ScrollArea } from '@mantine/core'
import { Children, createContext, type ComponentProps, type ReactNode, useContext, useState } from 'react'
import Markdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import 'katex/dist/katex.min.css'
import './markdown.css'
import CodeTabs from './CodeTabs'

const InPreContext = createContext(false)

type Components = ComponentProps<typeof Markdown>['components']

interface Props {
  /** Raw markdown string */
  children: string
  /** Problem slug, used to resolve relative image paths */
  slug: string
  /** Extra component overrides merged on top of the defaults */
  extraComponents?: Components
}

export default function ProblemMarkdown({ children, slug, extraComponents }: Props) {
  return (
    <ScrollArea>
      <Box
        style={{
          fontFamily: '"Helvetica Neue", Georgia, serif',
          lineHeight: 1.75,
          fontSize: 15,
        }}
      >
        <Markdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeRaw, rehypeKatex]}
          components={{
            h1: ({ children }) => (
              <h1 style={{ fontSize: 22, marginBottom: 8, fontFamily: 'system-ui, sans-serif' }}>
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 style={{ fontSize: 18, marginTop: 20, marginBottom: 6, fontFamily: 'system-ui, sans-serif' }}>
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 style={{ fontSize: 15, marginTop: 16, marginBottom: 4, fontFamily: 'system-ui, sans-serif' }}>
                {children}
              </h3>
            ),
            pre: ({ children }) => (
              <InPreContext.Provider value={true}>
                <pre
                  style={{
                    background: 'var(--mantine-color-gray-1)',
                    padding: '10px 14px',
                    borderRadius: 6,
                    fontFamily: 'monospace',
                    fontSize: 13,
                    overflowX: 'auto',
                    margin: '8px 0',
                  }}
                >
                  {children}
                </pre>
              </InPreContext.Provider>
            ),
            code: ({ children }) => {
              const inPre = useContext(InPreContext)
              return inPre ? (
                <code>{children}</code>
              ) : (
                <code
                  style={{
                    background: 'var(--mantine-color-gray-1)',
                    padding: '1px 5px',
                    borderRadius: 3,
                    fontFamily: 'monospace',
                    fontSize: 13,
                  }}
                >
                  {children}
                </code>
              )
            },
            img: ({ src, alt, ...props }) => {
              const resolvedSrc =
                src && !src.startsWith('http') && !src.startsWith('/')
                  ? `/api/problems/${slug}/files/${src}`
                  : src
              let displayAlt = alt || ''
              let width: string | undefined
              const widthMatch = displayAlt.match(/\|width=([^\]|]+)$/)
              if (widthMatch) {
                width = widthMatch[1].trim()
                displayAlt = displayAlt.slice(0, widthMatch.index).trim()
              }
              return <img src={resolvedSrc} alt={displayAlt} style={{ maxWidth: '100%', width }} {...props} />
            },
            table: ({ children }) => (
              <table
                style={{
                  borderCollapse: 'collapse',
                  marginBottom: 12,
                  fontFamily: 'system-ui, sans-serif',
                  fontSize: 14,
                }}
              >
                {children}
              </table>
            ),
            th: ({ children, ...props }) => (
              <th
                {...props}
                style={{
                  border: '1px solid var(--mantine-color-gray-3)',
                  padding: '4px 10px',
                  background: 'var(--mantine-color-gray-1)',
                  ...(props.style ?? {})
                }}
              >
                {children}
              </th>
            ),
            td: ({ children, ...props }) => (
              <td
                {...props}
                style={{
                  border: '1px solid var(--mantine-color-gray-3)',
                  padding: '4px 10px',
                  fontFamily: 'monospace',
                  ...(props.style ?? {})
                }}
              >
                {children}
              </td>
            ),
            div: ({ children, className, ...props }) =>
              className === 'code-tabs' ? (
                <CodeTabs>{children}</CodeTabs>
              ) : (
                <div className={className} {...props}>{children}</div>
              ),
            ...extraComponents,
          }}
        >
          {children}
        </Markdown>
      </Box>
    </ScrollArea>
  )
}

/** Inline spoiler text — click to reveal/hide. */
export function Spoiler({ children }: { children: ReactNode }) {
  const [revealed, setRevealed] = useState(false)
  return (
    <span
      role="button"
      tabIndex={0}
      onClick={() => setRevealed((r) => !r)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') setRevealed((r) => !r)
      }}
      style={{
        cursor: 'pointer',
        borderRadius: 4,
        padding: '1px 4px',
        transition: 'all 0.2s ease',
        ...(revealed
          ? { background: 'var(--mantine-color-blue-1)', color: 'inherit' }
          : { background: 'var(--mantine-color-dark-6)', color: 'transparent' }),
      }}
      title={revealed ? 'Click to hide' : 'Click to reveal'}
    >
      {children}
    </span>
  )
}

/** Styled <details>/<summary> for editorial hint blocks. */
export const editorialComponents: Components = {
  details: ({ children, ...props }) => {
    const childArray = Children.toArray(children) as ReactNode[]
    const summaryChild = childArray[0]
    const rest = childArray.slice(1)
    return (
      <details
        {...props}
        style={{
          background: 'var(--mantine-color-blue-6)',
          borderRadius: 8,
          marginBottom: 12,
          paddingBottom: 2,
        }}
      >
        {summaryChild}
        <div
          style={{
            background: 'var(--mantine-color-blue-1)',
            borderRadius: 6,
            padding: '10px 14px',
            margin: '0 4px 4px 4px',
          }}
        >
          {rest}
        </div>
      </details>
    )
  },
  summary: ({ children, ...props }) => (
    <summary
      {...props}
      style={{
        padding: '8px 14px',
        cursor: 'pointer',
        fontFamily: 'system-ui, sans-serif',
        fontWeight: 600,
        fontSize: 14,
        color: 'white',
      }}
    >
      {children}
    </summary>
  ),
  span: ({ children, className, ...props }) =>
    className === 'spoiler' ? (
      <Spoiler>{children}</Spoiler>
    ) : (
      <span className={className} {...props}>{children}</span>
    ),
}
