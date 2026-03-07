export interface ProblemSummary {
  slug: string
  name: string
  type: string
  tags: string[]
  difficulty?: number
  quality?: number
  author: string
  contests?: string[]
  external_judge_url?: string
  has_editorial: boolean
}

export interface ProblemData extends ProblemSummary {
  limits: { time: number; memory: number }
  statement: string | null
  editorial: string | null
}
