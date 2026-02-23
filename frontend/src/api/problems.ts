import axios from 'axios'
import type { Problem, JobStatus, CheckResult, TestSetDetail, SolutionsRunResult } from '../types/problem'

const client = axios.create({ baseURL: '/api' })

export async function getProblems(): Promise<Problem[]> {
  const { data } = await client.get<Problem[]>('/problems/')
  return data
}

export async function getProblem(slug: string): Promise<Problem> {
  const { data } = await client.get<Problem>(`/problems/${slug}`)
  return data
}

export async function patchProblemState(slug: string, state: string): Promise<Problem> {
  const { data } = await client.patch<Problem>(`/problems/${slug}`, { state })
  return data
}

export async function getStatement(slug: string): Promise<{ raw: string }> {
  const { data } = await client.get<{ raw: string }>(`/problems/${slug}/statement/`)
  return data
}

export async function getTestSets(slug: string): Promise<TestSetDetail[]> {
  const { data } = await client.get<TestSetDetail[]>(`/problems/${slug}/tests/`)
  return data
}

export async function getTestContent(
  slug: string,
  setName: string,
  testName: string,
): Promise<{ content: string }> {
  const { data } = await client.get<{ content: string }>(
    `/problems/${slug}/tests/${setName}/${testName}`,
  )
  return data
}

export async function generateTests(
  slug: string,
  testSet: string,
  generatorName = 'gen_tests.py',
): Promise<{ job_ids: string[] }> {
  const { data } = await client.post<{ job_ids: string[] }>(
    `/problems/${slug}/tests/generate`,
    { requests: [{ test_set: testSet, generator_name: generatorName }] },
  )
  return data
}

export async function generateAllTests(
  slug: string,
  requests: { test_set: string; generator_name: string }[],
): Promise<{ job_ids: string[] }> {
  const { data } = await client.post<{ job_ids: string[] }>(
    `/problems/${slug}/tests/generate`,
    { requests },
  )
  return data
}

export async function createTestSet(
  slug: string,
  req: { name: string; description?: string; points?: number; marking_style?: string },
): Promise<void> {
  await client.post(`/problems/${slug}/tests/`, req)
}

export async function createTestCase(
  slug: string,
  setName: string,
  req: { content: string; name?: string; description?: string },
): Promise<{ name: string }> {
  const { data } = await client.post<{ name: string }>(
    `/problems/${slug}/tests/${setName}`,
    req,
  )
  return data
}

export async function updateTestCaseDescription(
  slug: string,
  setName: string,
  testName: string,
  description: string,
): Promise<void> {
  await client.patch(`/problems/${slug}/tests/${setName}/${testName}`, { description })
}

export async function runProblem(slug: string): Promise<{ job_ids: string[] }> {
  const { data } = await client.post<{ job_ids: string[] }>(`/problems/${slug}/run`)
  return data
}

export async function reviewProblem(slug: string): Promise<{ checks: CheckResult[] }> {
  const { data } = await client.post<{ checks: CheckResult[] }>(`/problems/${slug}/review`)
  return data
}

export async function reviewProblemAI(slug: string): Promise<{ job_ids: string[] }> {
  const { data } = await client.post<{ job_ids: string[] }>(`/problems/${slug}/review/ai`)
  return data
}

/** Request body for POST /problems/{slug}/solutions/run — matches RunSolutionRequest in API */
export interface RunSolutionRequest {
  solution_paths: string[]
  test_set?: string | null
}

export async function runSolutions(
  slug: string,
  req: RunSolutionRequest,
): Promise<{ job_ids: string[] }> {
  const { data } = await client.post<{ job_ids: string[] }>(
    `/problems/${slug}/solutions/run`,
    req,
  )
  return data
}

export async function getJob(jobId: string): Promise<JobStatus> {
  const { data } = await client.get<JobStatus>(`/jobs/${jobId}`)
  return data
}

export async function getMergedResults(slug: string): Promise<SolutionsRunResult> {
  const { data } = await client.get<SolutionsRunResult>(`/problems/${slug}/solutions/merged-results`)
  return data
}
