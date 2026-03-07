import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Container, Title, Card, Group, Badge, Text, SimpleGrid, Loader, Alert, TextInput, Switch, MultiSelect } from '@mantine/core'
import { IconSearch, IconAlertTriangle } from '@tabler/icons-react'
import type { ProblemSummary } from '../types'
import { fetchIndex } from '../data'

const DIFFICULTY_COLORS: Record<string, string> = {
  '800': 'gray',
  '900': 'gray',
  '1000': 'green',
  '1100': 'green',
  '1200': 'teal',
  '1300': 'teal',
  '1400': 'blue',
  '1500': 'blue',
  '1600': 'violet',
  '1700': 'violet',
  '1800': 'orange',
  '1900': 'orange',
  '2000': 'red',
}

function difficultyColor(d?: number): string {
  if (!d) return 'gray'
  const key = String(Math.floor(d / 100) * 100)
  return DIFFICULTY_COLORS[key] || (d >= 2000 ? 'red' : 'gray')
}

export default function ProblemListPage() {
  const [problems, setProblems] = useState<ProblemSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [selectedContests, setSelectedContests] = useState<string[]>([])
  const [showTags, setShowTags] = useState(false)
  const [showDifficulty, setShowDifficulty] = useState(false)

  useEffect(() => {
    fetchIndex()
      .then(setProblems)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const allContests = useMemo(() => {
    const contests = new Set<string>()
    problems.forEach((p) => p.contests?.forEach((c) => contests.add(c)))
    return Array.from(contests).sort()
  }, [problems])

  const filtered = problems.filter((p) => {
    const q = search.toLowerCase()
    const matchesSearch =
      p.name.toLowerCase().includes(q) ||
      p.slug.toLowerCase().includes(q) ||
      p.tags.some((t) => t.toLowerCase().includes(q)) ||
      (p.author && p.author.toLowerCase().includes(q))
    const matchesContests =
      selectedContests.length === 0 ||
      selectedContests.every((c) => p.contests?.includes(c))
    return matchesSearch && matchesContests
  }).sort((a, b) => (b.quality ?? 0) - (a.quality ?? 0))

  return (
    <Container size="md" py="xl">
      <Title order={1} mb="lg">Problems</Title>

      {loading && <Loader size="sm" />}
      {error && (
        <Alert icon={<IconAlertTriangle size={16} />} color="red" title="Error">
          {error}
        </Alert>
      )}

      {!loading && !error && (
        <>
          <Group grow mb="sm">
            <TextInput
              placeholder="Search problems..."
              leftSection={<IconSearch size={16} />}
              value={search}
              onChange={(e) => setSearch(e.currentTarget.value)}
            />
            <MultiSelect
              placeholder="Filter by contest"
              data={allContests}
              value={selectedContests}
              onChange={setSelectedContests}
              clearable
            />
          </Group>
          <Group gap="lg" mb="lg">
            <Switch
              label="Show difficulty"
              checked={showDifficulty}
              onChange={(e) => setShowDifficulty(e.currentTarget.checked)}
              size="sm"
            />
            <Switch
              label="Show tags"
              checked={showTags}
              onChange={(e) => setShowTags(e.currentTarget.checked)}
              size="sm"
            />
          </Group>
          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
            {filtered.map((p) => (
              <Card
                key={p.slug}
                component={Link}
                to={`/problem/${p.slug}`}
                shadow="sm"
                padding="lg"
                radius="md"
                withBorder
                style={{ textDecoration: 'none', color: 'inherit' }}
              >
                <Group justify="space-between" mb="xs">
                  <Text fw={600} size="lg">{p.name}</Text>
                  {p.quality != null && (
                    <Badge color="yellow" variant="light">
                      {'★'.repeat(p.quality) + '☆'.repeat(5 - p.quality)}
                    </Badge>
                  )}
                  {showDifficulty && p.difficulty && (
                    <Badge color={difficultyColor(p.difficulty)} variant="light">
                      {p.difficulty}
                    </Badge>
                  )}
                </Group>
                <Group gap="xs" mb="xs">
                  <Badge size="sm" variant="outline">{p.type}</Badge>
                  {showTags && p.tags.map((t) => (
                    <Badge key={t} size="sm" variant="light" color="blue">{t}</Badge>
                  ))}
                </Group>
                {p.author && <Text size="sm" c="dimmed">by {p.author}</Text>}
                <Group justify="space-between" gap="xs" mt="xs">
                  {p.contests && <div>
                    {p.contests.map((c) => (
                      <Badge size="xs" color="green">{c}</Badge>
                    ))}
                  </div>}
                  {p.external_judge_url && <Badge size="xs" color="orange">Judge</Badge>}
                </Group>
              </Card>
            ))}
          </SimpleGrid>
          {filtered.length === 0 && (
            <Text c="dimmed" ta="center" mt="xl">No problems found.</Text>
          )}
        </>
      )}
    </Container>
  )
}
