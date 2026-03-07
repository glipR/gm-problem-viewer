import { Routes, Route } from 'react-router-dom'
import ProblemListPage from './pages/ProblemListPage'
import ProblemPage from './pages/ProblemPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ProblemListPage />} />
      <Route path="/problem/:slug" element={<ProblemPage />} />
    </Routes>
  )
}
