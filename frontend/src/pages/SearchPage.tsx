import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Button, Center, Group, Loader, MultiSelect, Select, SimpleGrid, Text, TextInput, Title } from '@mantine/core'
import { IconSearch, IconListCheck } from '@tabler/icons-react'
import { notifications } from '@mantine/notifications'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { reviewProblem } from '../api/problems'
import { useProblems, useSearchProblems } from '../hooks/useProblems'
import StaticProblemCard from '../components/kanban/StaticProblemCard'

export default function SearchPage() {
  const navigate = useNavigate()
  const onProblemClick = (slug: string) => navigate(`/problems/${slug}`)
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [selectedContests, setSelectedContests] = useState<string[]>([])
  const [difficultySort, setDifficultySort] = useState<string | null>(null)

  // Debounce the text query to avoid a request per keystroke
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300)
    return () => clearTimeout(timer)
  }, [query])

  // Fetch all problems once to populate the tag list
  const { data: allProblems } = useProblems()
  const allTags = useMemo(() => {
    if (!allProblems) return []
    const tags = new Set<string>()
    allProblems.forEach((p) => p.config.tags.forEach((t) => tags.add(t)))
    return Array.from(tags).sort()
  }, [allProblems])

  const allContests = useMemo(() => {
    if (!allProblems) return []
    const contests = new Set<string>()
    allProblems.forEach((p) => p.config.contests?.forEach((c) => contests.add(c)))
    return Array.from(contests).sort()
  }, [allProblems])

  const { data: rawResults, isLoading, isError } = useSearchProblems(debouncedQuery, selectedTags)

  const results = useMemo(() => {
    if (!rawResults) return rawResults
    let filtered = rawResults
    // Client-side contest filter (AND logic)
    if (selectedContests.length > 0) {
      filtered = filtered.filter((p) =>
        selectedContests.every((c) => p.config.contests?.includes(c))
      )
    }
    // Difficulty sort
    if (difficultySort === 'asc' || difficultySort === 'desc') {
      const dir = difficultySort === 'asc' ? 1 : -1
      filtered = [...filtered].sort((a, b) => {
        const da = a.config.difficulty
        const db = b.config.difficulty
        if (da == null && db == null) return 0
        if (da == null) return 1
        if (db == null) return -1
        return (da - db) * dir
      })
    }
    return filtered
  }, [rawResults, selectedContests, difficultySort])

  const qc = useQueryClient()
  const { mutate: reviewAll, isPending: reviewAllPending } = useMutation({
    mutationFn: () => Promise.all((results ?? []).map((p) => reviewProblem(p.slug))),
    onSuccess: (responses) => {
      // Invalidate the latest-review-job cache for each slug so cards start polling
      responses.forEach((_, i) => {
        const slug = (results ?? [])[i].slug
        qc.invalidateQueries({ queryKey: ['latest-review-job', slug] })
      })
      notifications.show({
        message: `Review started for ${responses.length} problem${responses.length !== 1 ? 's' : ''}`,
        color: 'blue',
      })
    },
    onError: () => notifications.show({ message: 'Failed to start review', color: 'red' }),
  })

  return (
    <Box p="xl">
      <Title order={2} mb="lg">
        Search
      </Title>

      <Group mb="lg" grow>
        <TextInput
          placeholder="Search by title or statement content…"
          leftSection={<IconSearch size={16} />}
          value={query}
          onChange={(e) => setQuery(e.currentTarget.value)}
        />
        <MultiSelect
          placeholder="Filter by tags"
          data={allTags}
          value={selectedTags}
          onChange={setSelectedTags}
          clearable
        />
      </Group>

      <Group mb="lg" grow>
        <MultiSelect
          placeholder="Filter by contest"
          data={allContests}
          value={selectedContests}
          onChange={setSelectedContests}
          clearable
        />
        <Select
          placeholder="Sort by difficulty"
          data={[
            { value: 'asc', label: 'Difficulty ↑' },
            { value: 'desc', label: 'Difficulty ↓' },
          ]}
          value={difficultySort}
          onChange={setDifficultySort}
          clearable
        />
      </Group>

      {isLoading && (
        <Center mt="xl">
          <Loader />
        </Center>
      )}

      {isError && (
        <Text c="red" mt="md">
          Search failed. Is the API running?
        </Text>
      )}

      {results && (
        <>
          <Group justify="space-between" mb="md">
            <Text size="sm" c="dimmed">
              {results.length} result{results.length !== 1 ? 's' : ''}
            </Text>
            {results.length > 0 && (
              <Button
                size="xs"
                variant="light"
                leftSection={<IconListCheck size={14} />}
                loading={reviewAllPending}
                onClick={() => reviewAll()}
              >
                Review all ({results.length})
              </Button>
            )}
          </Group>
          <SimpleGrid cols={3} spacing="md">
            {results.map((p) => (
              <StaticProblemCard key={p.slug} problem={p} onSelect={onProblemClick} />
            ))}
          </SimpleGrid>
          {results.length === 0 && (
            <Center mt="xl">
              <Text c="dimmed">No problems match your search.</Text>
            </Center>
          )}
        </>
      )}
    </Box>
  )
}
