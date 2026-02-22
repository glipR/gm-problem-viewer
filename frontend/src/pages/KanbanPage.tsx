import { Box, Center, Loader, Text, Title } from '@mantine/core'
import { DndContext, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import { useProblems, usePatchProblemState } from '../hooks/useProblems'
import { useProblemsStore } from '../store/problemsStore'
import KanbanBoard from '../components/kanban/KanbanBoard'
import type { Problem } from '../types/problem'

interface Props {
  onProblemClick: (slug: string) => void
}

export default function KanbanPage({ onProblemClick }: Props) {
  const { data: problems, isLoading, isError } = useProblems()
  const { mutate: patchState } = usePatchProblemState()
  const { overrides, setOverride, clearOverride } = useProblemsStore()

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
  )

  function handleDragEnd(event: DragEndEvent) {
    const slug = event.active.id as string
    const newState = event.over?.id as string | undefined
    if (!newState || !slug) return

    setOverride(slug, newState)
    patchState(
      { slug, state: newState },
      { onSettled: () => clearOverride(slug) },
    )
  }

  if (isLoading) {
    return (
      <Center h="100vh">
        <Loader />
      </Center>
    )
  }

  if (isError || !problems) {
    return (
      <Center h="100vh">
        <Text c="red">Failed to load problems. Is the API running?</Text>
      </Center>
    )
  }

  // Apply optimistic overrides
  const displayProblems: Problem[] = problems.map((p) =>
    overrides[p.slug]
      ? { ...p, config: { ...p.config, state: overrides[p.slug] as Problem['config']['state'] } }
      : p,
  )

  return (
    <Box p="xl">
      <Title order={2} mb="lg">
        Problems
      </Title>
      <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
        <KanbanBoard problems={displayProblems} onProblemClick={onProblemClick} />
      </DndContext>
    </Box>
  )
}
