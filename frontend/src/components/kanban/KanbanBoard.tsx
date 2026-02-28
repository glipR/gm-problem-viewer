import { useState } from 'react'
import { SimpleGrid } from '@mantine/core'
import type { Problem, ProblemState } from '../../types/problem'
import KanbanLane from './KanbanLane'
import CreateProblemModal from './CreateProblemModal'

const LANES: { id: ProblemState; label: string }[] = [
  { id: 'draft', label: 'Draft' },
  { id: 'in-progress', label: 'In Progress' },
  { id: 'review', label: 'Review' },
]

interface Props {
  problems: Problem[]
  onProblemClick: (slug: string) => void
}

export default function KanbanBoard({ problems, onProblemClick }: Props) {
  const [modalOpened, setModalOpened] = useState(false)
  const [modalState, setModalState] = useState<string>('draft')

  function handleCreateClick(state: string) {
    setModalState(state)
    setModalOpened(true)
  }

  return (
    <>
      <SimpleGrid cols={3} spacing="md">
        {LANES.map((lane) => (
          <KanbanLane
            key={lane.id}
            id={lane.id}
            label={lane.label}
            problems={problems.filter((p) => p.config.state === lane.id)}
            onProblemClick={onProblemClick}
            onCreateClick={() => handleCreateClick(lane.id)}
          />
        ))}
      </SimpleGrid>
      <CreateProblemModal
        opened={modalOpened}
        initialState={modalState}
        onClose={() => setModalOpened(false)}
        onCreated={(slug) => onProblemClick(slug)}
      />
    </>
  )
}
