import axios from 'axios'
import type { Problem } from '../types/problem'

const client = axios.create({ baseURL: '/api' })

export async function getProblems(): Promise<Problem[]> {
  const { data } = await client.get<Problem[]>('/problems/')
  return data
}

export async function patchProblemState(slug: string, state: string): Promise<Problem> {
  const { data } = await client.patch<Problem>(`/problems/${slug}`, { state })
  return data
}
