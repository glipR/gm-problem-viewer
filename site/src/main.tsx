import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { MantineProvider } from '@mantine/core'
import { BrowserRouter } from 'react-router-dom'
import '@mantine/core/styles.css'
import 'katex/dist/katex.min.css'
import App from './App'

// GitHub Pages SPA: restore path from ?p= query param (set by 404.html redirect)
const params = new URLSearchParams(window.location.search)
const redirectPath = params.get('p')
if (redirectPath) {
  const cleanUrl = window.location.pathname + window.location.hash
  window.history.replaceState(null, '', cleanUrl.replace(/\/$/, '') + redirectPath)
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MantineProvider>
      <BrowserRouter basename={import.meta.env.BASE_URL}>
        <App />
      </BrowserRouter>
    </MantineProvider>
  </StrictMode>,
)
