import { Tabs } from '@mantine/core'
import Editor from '@monaco-editor/react'
import { useState, Children, isValidElement, type ReactNode, type ReactElement } from 'react'

interface CodeTabsProps {
  children: ReactNode
}

interface TabInfo {
  lang: string
  label: string
  syntax: string
  code: string
}

const MONACO_LANG: Record<string, string> = {
  python: 'python',
  cpp: 'cpp',
  c: 'c',
  java: 'java',
  javascript: 'javascript',
  rust: 'rust',
  go: 'go',
}

const BG = '#1e1e1e'
const ACTIVE_TAB_BG = 'var(--mantine-primary-color-filled)'
const TAB_TEXT = '#ccc'
const ACTIVE_TAB_TEXT = '#fff'

export default function CodeTabs({ children }: CodeTabsProps) {
  const tabs: TabInfo[] = []

  Children.forEach(children, (child) => {
    if (!isValidElement(child)) return
    const el = child as ReactElement<Record<string, unknown>>
    const lang = (el.props['data-lang'] ?? el.props['dataLang'] ?? '') as string
    const label = (el.props['data-label'] ?? el.props['dataLabel'] ?? lang) as string
    const syntax = (el.props['data-syntax'] ?? el.props['dataSyntax'] ?? '') as string
    const b64 = (el.props['data-code'] ?? el.props['dataCode'] ?? '') as string
    if (lang && b64) {
      tabs.push({ lang, label, syntax, code: atob(b64) })
    }
  })

  const [active, setActive] = useState(tabs[0]?.lang ?? '')

  if (tabs.length === 0) return <>{children}</>

  return (
    <div style={{ background: BG, borderRadius: 8, overflow: 'hidden', margin: '8px 0' }}>
      <Tabs
        value={active}
        onChange={(v) => setActive(v ?? active)}
        styles={{
          list: {
            background: BG,
            borderBottom: 'none',
            gap: 0,
          },
          tab: {
            color: TAB_TEXT,
            fontFamily: 'system-ui, sans-serif',
            fontSize: 13,
            fontWeight: 500,
            border: 'none',
            borderRadius: '8px 8px 0 0',
            padding: '6px 16px',
            '&:hover': { background: '#333' },
            '&[dataActive]': {
              background: ACTIVE_TAB_BG,
              color: ACTIVE_TAB_TEXT,
            },
          },
        }}
      >
        <Tabs.List>
          {tabs.map((t) => (
            <Tabs.Tab
              key={t.lang}
              value={t.lang}
              style={
                active === t.lang
                  ? { background: ACTIVE_TAB_BG, color: ACTIVE_TAB_TEXT }
                  : { background: 'transparent', color: TAB_TEXT }
              }
            >
              {t.label}
            </Tabs.Tab>
          ))}
        </Tabs.List>
        {tabs.map((t) => {
          const lines = t.code.split('\n').length
          const height = Math.min(Math.max(lines * 19 + 16, 100), 600)
          return (
            <Tabs.Panel key={t.lang} value={t.lang}>
              <Editor
                height={height}
                language={MONACO_LANG[t.syntax] ?? t.syntax}
                value={t.code}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  domReadOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  lineNumbers: 'on',
                  fontSize: 13,
                  fontFamily: 'monospace',
                  renderLineHighlight: 'none',
                  overviewRulerLanes: 0,
                  hideCursorInOverviewRuler: true,
                  scrollbar: { vertical: 'auto', horizontal: 'auto' },
                }}
              />
            </Tabs.Panel>
          )
        })}
      </Tabs>
    </div>
  )
}
