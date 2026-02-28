export interface ProblemLimits {
  time: number
  memory: number
}

export type ProblemState = 'draft' | 'in-progress' | 'review' | 'complete' | 'archive'

export interface ProblemConfig {
  name: string
  type: 'standard' | 'interactive' | 'multi'
  tags: string[]
  difficulty?: number
  state: ProblemState
  limits: ProblemLimits
  author: string
}

export interface Solution {
  path: string
  language?: string
  name: string
  expectation: string | Record<string, string>
  description?: string
}

export interface Validator {
  path: string
  name: string
  checks?: string[]
  description?: string
}

export interface OutputValidator {
  path: string
  type: string
  name?: string
  description?: string
}

export interface Problem {
  slug: string
  config: ProblemConfig
  test_sets: string[]
  solutions: Solution[]
  validators: {
    input: Validator[],
    output: OutputValidator,
  }
}

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

export interface Verdict {
  test_case: string
  test_set: string
  verdict: string
  time_ms?: number
  comment: string
}

export interface SolutionRunResult {
  solution_path: string
  verdicts: Verdict[]
  overall: string
}

export interface SolutionsRunResult {
  solutions: SolutionRunResult[]
  status?: string
}

export interface ValidatorResult {
  validator: string
  test_case: string
  test_set: string
  passed: boolean
  error: string
}

export interface ValidatorsRunResult {
  results: ValidatorResult[]
}

export interface CheckResult {
  name: string
  passed: boolean
  detail: string
}

export interface PhaseResult {
  num_tests: number
  passed: number
  issues: string[]
}

export interface CategoryResult {
  num_tests: number
  passed: number
  issues: string[]
  color: 'green' | 'yellow' | 'red'
}

export interface ReviewJobResult {
  phase1?: PhaseResult
  phase2?: PhaseResult
  by_category?: Record<string, CategoryResult>
}

export interface AiReviewCheck {
  name: string
  summary: string
}

export interface AiReviewResult {
  checks: AiReviewCheck[]
}
