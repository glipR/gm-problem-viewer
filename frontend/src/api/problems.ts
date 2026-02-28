import axios from 'axios'
import type { Problem, JobStatus, CheckResult, TestSetDetail, SolutionsRunResult } from '../types/problem'

const client = axios.create({ baseURL: '/api' })

export async function createProblem(req: {
  name: string
  slug: string
  state?: string
  type?: string
}): Promise<Problem> {
  const { data } = await client.post<Problem>('/problems/', req)
  return data
}

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

export async function getLatestGenerateJob(slug: string): Promise<JobStatus | null> {
  const { data } = await client.get<JobStatus | null>(`/problems/${slug}/tests/generate/latest`)
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

export async function reviewProblem(slug: string): Promise<{ job_ids: string[] }> {
  const { data } = await client.post<{ job_ids: string[] }>(`/problems/${slug}/review`)
  return data
}

export async function getLatestReviewJob(slug: string): Promise<JobStatus | null> {
  const { data } = await client.get<JobStatus | null>(`/problems/${slug}/review/latest`)
  return data
}

export async function reviewProblemAI(slug: string): Promise<{ job_ids: string[] }> {
  const { data } = await client.post<{ job_ids: string[] }>(`/problems/${slug}/review/ai`)
  return data
}

export async function getLatestValidatorJob(slug: string): Promise<JobStatus | null> {
  const { data } = await client.get<JobStatus | null>(`/problems/${slug}/validators/latest`)
  return data
}

export async function runValidators(
  slug: string,
  req: { test_set?: string | null } = {},
): Promise<{ job_ids: string[] }> {
  const { data } = await client.post<{ job_ids: string[] }>(
    `/problems/${slug}/validators/run`,
    req,
  )
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

export async function searchProblems(q: string, tags: string[]): Promise<Problem[]> {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  tags.forEach((tag) => params.append('tags', tag))
  const { data } = await client.get<Problem[]>(`/problems/search?${params}`)
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

export async function openSolutionInEditor(slug: string, solutionPath: string): Promise<void> {
  await client.post(`/problems/${slug}/solutions/open`, { solution_path: solutionPath })
}

export async function openStatementInEditor(slug: string): Promise<void> {
  await client.post(`/problems/${slug}/statement/open`)
}

export async function openGeneratorInEditor(slug: string, setName: string, genName: string): Promise<void> {
  await client.post(`/problems/${slug}/tests/open-generator`, { set_name: setName, gen_name: genName })
}

export async function openTestCaseInEditor(slug: string, setName: string, testName: string): Promise<void> {
  await client.post(`/problems/${slug}/tests/open-test`, { set_name: setName, test_name: testName })
}

export async function getTodo(slug: string): Promise<{ raw: string | null }> {
  const { data } = await client.get<{ raw: string | null }>(`/problems/${slug}/todo/`)
  return data
}

export async function updateTodo(slug: string, content: string): Promise<void> {
  await client.put(`/problems/${slug}/todo/`, { content })
}

export async function getEditorial(slug: string): Promise<{ raw: string }> {
  const { data } = await client.get<{ raw: string }>(`/problems/${slug}/editorial/`)
  return data
}

export async function openEditorialInEditor(slug: string): Promise<void> {
  await client.post(`/problems/${slug}/editorial/open`)
}
