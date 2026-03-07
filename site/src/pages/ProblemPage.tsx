import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Container, Title, Group, Badge, Text, Tabs, Loader, Alert, Button, Anchor, Box,
  Tooltip,
} from '@mantine/core'
import { IconArrowLeft, IconAlertTriangle, IconExternalLink, IconEye } from '@tabler/icons-react'
import type { ProblemData } from '../types'
import { fetchProblem } from '../data'
import ProblemMarkdown, { editorialComponents } from '../components/ProblemMarkdown'

function RevealBadges({ tooltip, labels, color, variant }: { tooltip: string, labels: string[]; color: string; variant: string }) {
  const [revealed, setRevealed] = useState(false)

  if (labels.length === 0) return null

  if (!revealed) {
    return (
      <Tooltip label={tooltip}>
        <Badge
          size="sm"
          variant="outline"
          color="gray"
          style={{ cursor: 'pointer' }}
          leftSection={<IconEye size={12} />}
          onClick={() => setRevealed(true)}
        >
          Reveal
        </Badge>
      </Tooltip>
    )
  }

  return (
    <>
      {labels.map((l) => (
        <Badge key={l} size="sm" variant={variant} color={color}>{l}</Badge>
      ))}
    </>
  )
}

export default function ProblemPage() {
  const { slug } = useParams<{ slug: string }>()
  const [problem, setProblem] = useState<ProblemData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return
    setLoading(true)
    fetchProblem(slug)
      .then(setProblem)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return <Container py="xl"><Loader size="sm" /></Container>
  if (error || !problem) {
    return (
      <Container py="xl">
        <Alert icon={<IconAlertTriangle size={16} />} color="red" title="Error">
          {error || 'Problem not found'}
        </Alert>
      </Container>
    )
  }

  const hasEditorial = !!problem.editorial
  const defaultTab = problem.statement ? 'statement' : hasEditorial ? 'editorial' : 'statement'

  return (
    <Container size="md" py="xl">
      <Button
        component={Link}
        to="/"
        variant="subtle"
        size="xs"
        leftSection={<IconArrowLeft size={14} />}
        mb="md"
      >
        All Problems
      </Button>

      <Group>
        <Group justify="space-between" align="flex-start" wrap="nowrap" style={{flexGrow: 1}}>
          <Title order={1} mb="0">{problem.name}</Title>
          {(problem.external_judge_url && (
            <Anchor href={problem.external_judge_url} target="_blank" rel="noopener noreferrer">
              <Button
                variant="light"
                color="orange"
                size="xs"
                leftSection={<IconExternalLink size={14} />}
              >
                Try on Judge
              </Button>
            </Anchor>
          ))}
        </Group>
        <Group justify="space-between" align="flex-start" wrap="nowrap" style={{flexGrow: 1}}>
          <Group gap="xs">
            <Badge variant="outline">{problem.type}</Badge>
            {problem.quality != null && (
              <Badge size="sm" variant="light" color="yellow">
                {'★'.repeat(problem.quality) + '☆'.repeat(5 - problem.quality)}
              </Badge>
            )}
            {problem.difficulty && (
              <RevealBadges tooltip="Click to reveal problem difficulty" labels={[String(problem.difficulty)]} color="blue" variant="light" />
            )}
            {problem.tags.length > 0 && (
              <RevealBadges tooltip="Click to reveal problem tags" labels={problem.tags} color="teal" variant="light" />
            )}
          </Group>
          <Group gap="md" justify="flex-end" mb="xs">
            {problem.author && <Text size="sm" c="dimmed">by {problem.author}</Text>}
            <Text size="sm" c="dimmed">
              Time: {problem.limits.time}s | Memory: {Math.round(problem.limits.memory / 1024)}KB
            </Text>
          </Group>
        </Group>
      </Group>

      <Tabs defaultValue={defaultTab}>
        <Tabs.List mb="md">
          <Tabs.Tab value="statement">Statement</Tabs.Tab>
          {hasEditorial && <Tabs.Tab value="editorial">Editorial</Tabs.Tab>}
        </Tabs.List>

        <Tabs.Panel value="statement">
          <Box style={{ maxWidth: 900, margin: '0 auto' }}>
            {problem.statement ? (
              <ProblemMarkdown slug={problem.slug}>{problem.statement}</ProblemMarkdown>
            ) : (
              <Text c="dimmed">No statement available.</Text>
            )}
          </Box>
        </Tabs.Panel>

        {hasEditorial && (
          <Tabs.Panel value="editorial">
            <Box style={{ maxWidth: 900, margin: '0 auto' }}>
              <ProblemMarkdown slug={problem.slug} extraComponents={editorialComponents}>
                {problem.editorial!}
              </ProblemMarkdown>
            </Box>
          </Tabs.Panel>
        )}
      </Tabs>
    </Container>
  )
}
