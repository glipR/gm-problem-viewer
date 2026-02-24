import { useState } from 'react'
import { Box, Tabs } from '@mantine/core'
import KanbanPage from './pages/KanbanPage'
import ProblemDetailPage from './pages/ProblemDetailPage'
import SearchPage from './pages/SearchPage'

type View = 'kanban' | 'search'

export default function App() {
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null)
  const [view, setView] = useState<View>('kanban')

  if (selectedSlug) {
    return <ProblemDetailPage slug={selectedSlug} onBack={() => setSelectedSlug(null)} />
  }

  return (
    <Box>
      <Tabs value={view} onChange={(v) => setView(v as View)}>
        <Tabs.List px="xl" pt="sm">
          <Tabs.Tab value="kanban">Board</Tabs.Tab>
          <Tabs.Tab value="search">Search</Tabs.Tab>
        </Tabs.List>
      </Tabs>
      {view === 'kanban' && <KanbanPage onProblemClick={setSelectedSlug} />}
      {view === 'search' && <SearchPage onProblemClick={setSelectedSlug} />}
    </Box>
  )
}
