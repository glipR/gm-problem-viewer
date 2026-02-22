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
  language?: string
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

export interface TestCase {
  name: string
  set_name: string
  description?: string
}

export interface TestSetConfig {
  name: string
  description?: string
  points: number
  marking_style: string
}

export interface TestGenerator {
  name: string
  test_set: string
  description: string
}

export interface TestSetDetail {
  name: string
  config?: TestSetConfig
  test_cases: TestCase[]
  generators: TestGenerator[]
}

export interface JobStatus {
  id: string
  status: 'pending' | 'running' | 'done' | 'failed'
  result: unknown
  error?: string
}

export interface CheckResult {
  name: string
  passed: boolean
  detail: string
}
