import { Box, Button, Group, Loader, Alert, ScrollArea } from '@mantine/core'
import { IconAlertTriangle, IconCode } from '@tabler/icons-react'
import { useQuery } from '@tanstack/react-query'
import { Children, createContext, isValidElement, ReactNode, useContext, useState } from 'react'
import Markdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import 'katex/dist/katex.min.css'
import { getEditorial, openEditorialInEditor } from '../../api/problems'
import CodeTabs from './CodeTabs'

const InPreContext = createContext(false)

interface Props {
  slug: string
}

export default function EditorialTab({ slug }: Props) {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['editorial', slug],
    queryFn: () => getEditorial(slug),
    retry: false,
  })

  const status = (error as { response?: { status?: number } } | null)?.response?.status

  return (
    <Box p="xl">
      <Group mb="lg">
        <Button
          size="xs"
          variant="light"
          leftSection={<IconCode size={14} />}
          onClick={() => openEditorialInEditor(slug)}
        >
          Open in Cursor
        </Button>
      </Group>

      {isLoading && <Loader size="sm" />}

      {isError && (
        <Alert
          icon={<IconAlertTriangle size={16} />}
          color="orange"
          title="Editorial unavailable"
          maw={500}
        >
          {status === 404
            ? 'No editorial.md found for this problem.'
            : 'Failed to load editorial.'}
        </Alert>
      )}

      {data && (
        <ScrollArea>
          <Box
            style={{
              maxWidth: 900,
              margin: '0 auto',
              fontFamily: '"STIX Two Text", Georgia, serif',
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
                  return <img src={resolvedSrc} alt={alt} style={{ maxWidth: '100%' }} {...props} />
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
                div: ({ children, className, ...props }) =>
                  className === 'code-tabs' ? (
                    <CodeTabs>{children}</CodeTabs>
                  ) : (
                    <div className={className} {...props}>{children}</div>
                  ),
              }}
            >
              {data.raw}
            </Markdown>
          </Box>
        </ScrollArea>
      )}
    </Box>
  )
}

function Spoiler({ children }: { children: ReactNode }) {
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
