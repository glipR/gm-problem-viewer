import { Box, Button, Group, Loader, Alert, ScrollArea } from '@mantine/core'
import { IconBrain, IconAlertTriangle } from '@tabler/icons-react'
import { useQuery } from '@tanstack/react-query'
import Markdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import { getStatement } from '../../api/problems'

interface Props {
  slug: string
}

export default function StatementTab({ slug }: Props) {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['statement', slug],
    queryFn: () => getStatement(slug),
    retry: false,
  })

  const status = (error as { response?: { status?: number } } | null)?.response?.status

  return (
    <Box p="xl">
      <Group mb="lg">
        <Button
          size="xs"
          variant="light"
          color="violet"
          leftSection={<IconBrain size={14} />}
          onClick={() => {
            // TODO: POST /problems/{slug}/statement/review
          }}
        >
          Review with Claude
        </Button>
      </Group>

      {isLoading && <Loader size="sm" />}

      {isError && (
        <Alert
          icon={<IconAlertTriangle size={16} />}
          color="orange"
          title="Statement unavailable"
          maw={500}
        >
          {status === 501
            ? 'Statement endpoint not yet implemented.'
            : status === 404
              ? 'No statement.md found for this problem.'
              : 'Failed to load statement.'}
        </Alert>
      )}

      {data && (
        <ScrollArea>
          <Box
            style={{
              maxWidth: 740,
              fontFamily: '"STIX Two Text", Georgia, serif',
              lineHeight: 1.75,
              fontSize: 15,
            }}
          >
            <Markdown
              remarkPlugins={[remarkMath]}
              rehypePlugins={[rehypeKatex]}
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
                code: ({ children, className }) => {
                  const isBlock = className != null
                  return isBlock ? (
                    <pre
                      style={{
                        background: 'var(--mantine-color-gray-1)',
                        padding: '10px 14px',
                        borderRadius: 6,
                        fontFamily: 'monospace',
                        fontSize: 13,
                        overflowX: 'auto',
                      }}
                    >
                      <code>{children}</code>
                    </pre>
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
                th: ({ children }) => (
                  <th
                    style={{
                      border: '1px solid var(--mantine-color-gray-3)',
                      padding: '4px 10px',
                      background: 'var(--mantine-color-gray-1)',
                    }}
                  >
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td
                    style={{
                      border: '1px solid var(--mantine-color-gray-3)',
                      padding: '4px 10px',
                      fontFamily: 'monospace',
                    }}
                  >
                    {children}
                  </td>
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
