import { create } from 'zustand'

interface ProblemsStore {
  overrides: Record<string, string>
  setOverride: (slug: string, state: string) => void
  clearOverride: (slug: string) => void
}

export const useProblemsStore = create<ProblemsStore>((set) => ({
  overrides: {},
  setOverride: (slug, state) =>
    set((s) => ({ overrides: { ...s.overrides, [slug]: state } })),
  clearOverride: (slug) =>
    set((s) => {
      const next = { ...s.overrides }
      delete next[slug]
      return { overrides: next }
    }),
}))
