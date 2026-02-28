import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getProblems, patchProblemState, searchProblems } from '../api/problems'

export function useProblems() {
  return useQuery({ queryKey: ['problems'], queryFn: getProblems })
}

export function useSearchProblems(q: string, tags: string[]) {
  return useQuery({
    queryKey: ['problems', 'search', q, tags],
    queryFn: () => searchProblems(q, tags),
  })
}

export function usePatchProblemState() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ slug, state }: { slug: string; state: string }) =>
      patchProblemState(slug, state),
    onSettled: (_data, _err, variables) => {
      queryClient.invalidateQueries({ queryKey: ['problems'] })
      queryClient.invalidateQueries({ queryKey: ['problem', variables.slug] })
    },
  })
}
