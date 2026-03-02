import { Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import { Box, Tabs } from '@mantine/core'
import KanbanPage from './pages/KanbanPage'
import ProblemDetailPage from './pages/ProblemDetailPage'
import SearchPage from './pages/SearchPage'

function MainLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const view = location.pathname === '/search' ? 'search' : 'kanban'

  return (
    <Box>
      <Tabs value={view} onChange={(v) => navigate(v === 'search' ? '/search' : '/')}>
        <Tabs.List px="xl" pt="sm">
          <Tabs.Tab value="kanban">Board</Tabs.Tab>
          <Tabs.Tab value="search">Search</Tabs.Tab>
        </Tabs.List>
      </Tabs>
      {view === 'kanban' && <KanbanPage />}
      {view === 'search' && <SearchPage />}
    </Box>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/problems/:slug" element={<ProblemDetailPage />} />
      <Route path="*" element={<MainLayout />} />
    </Routes>
  )
}
