import { useEffect, useMemo, useState } from 'react'
import { Box, Center, Group, Loader, MultiSelect, SimpleGrid, Text, TextInput, Title } from '@mantine/core'
import { IconSearch } from '@tabler/icons-react'
import { useProblems, useSearchProblems } from '../hooks/useProblems'
import StaticProblemCard from '../components/kanban/StaticProblemCard'

interface Props {
  onProblemClick: (slug: string) => void
}

export default function SearchPage({ onProblemClick }: Props) {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])

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

  const { data: results, isLoading, isError } = useSearchProblems(debouncedQuery, selectedTags)

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
          <Text size="sm" c="dimmed" mb="md">
            {results.length} result{results.length !== 1 ? 's' : ''}
          </Text>
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
