import { useState } from 'react'
import KanbanPage from './pages/KanbanPage'
import ProblemDetailPage from './pages/ProblemDetailPage'

export default function App() {
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null)

  if (selectedSlug) {
    return <ProblemDetailPage slug={selectedSlug} onBack={() => setSelectedSlug(null)} />
  }

  return <KanbanPage onProblemClick={setSelectedSlug} />
}
