import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getProblems, patchProblemState } from '../api/problems'

export function useProblems() {
  return useQuery({ queryKey: ['problems'], queryFn: getProblems })
}

export function usePatchProblemState() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ slug, state }: { slug: string; state: string }) =>
      patchProblemState(slug, state),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['problems'] })
    },
  })
}
