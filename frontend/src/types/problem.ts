export interface ProblemLimits {
  time: number
  memory: number
}

export interface ProblemConfig {
  name: string
  type: 'standard' | 'interactive'
  tags: string[]
  difficulty?: number
  state: 'draft' | 'in-progress' | 'review' | 'archive'
  limits: ProblemLimits
  author: string
}

export interface Solution {
  path: string
  name: string
  expectation: string | Record<string, string>[]
  description?: string
}

export interface Validator {
  path: string
  name: string
  checks?: string[]
  description?: string
}

export interface Problem {
  slug: string
  config: ProblemConfig
  test_sets: string[]
  solutions: Solution[]
  validators: Validator[]
}

export type ProblemState = 'draft' | 'in-progress' | 'review' | 'archive'
